import os
import sys
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.biryani_config import (
    DATASET_DIR, CHECKPOINT_PATH, IMAGE_SIZE, BATCH_SIZE,
    BIRYANI_CONFIDENCE_THRESHOLD, OTHER_CONFIDENCE_THRESHOLD, ARCHITECTURE
)
from preprocessing.preprocessor import get_inference_transforms
from models.model_builder import build_biryani_model

def evaluate_test_set():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Evaluation] Using device: {device}")

    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found at {CHECKPOINT_PATH}. Train the model first.")

    checkpoint = torch.load(str(CHECKPOINT_PATH), map_location=device)
    class_to_idx = checkpoint.get("class_to_idx", {"biryani": 0, "not_biryani": 1})
    classes = checkpoint.get("classes", ["biryani", "not_biryani"])
    
    # Identify index of 'biryani'
    biryani_idx = class_to_idx.get("biryani", 0)
    not_biryani_idx = class_to_idx.get("not_biryani", 1)

    test_dir = DATASET_DIR / "test"
    test_dataset = ImageFolder(root=str(test_dir), transform=get_inference_transforms(IMAGE_SIZE))
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    model = build_biryani_model(arch=checkpoint.get("architecture", ARCHITECTURE), pretrained=False, num_classes=2)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()

    all_labels = []
    all_preds = []
    all_probs = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = F.softmax(outputs, dim=1)
            
            _, preds = torch.max(outputs, 1)

            all_labels.extend(labels.numpy())
            all_preds.extend(preds.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)

    # Probability of being biryani
    biryani_probs = all_probs[:, biryani_idx]
    binary_labels = (all_labels == biryani_idx).astype(int)
    binary_preds = (all_preds == biryani_idx).astype(int)

    acc = float(accuracy_score(binary_labels, binary_preds))
    prec = float(precision_score(binary_labels, binary_preds, zero_division=0))
    rec = float(recall_score(binary_labels, binary_preds, zero_division=0))
    f1 = float(f1_score(binary_labels, binary_preds, zero_division=0))
    
    try:
        auc = float(roc_auc_score(binary_labels, biryani_probs))
    except Exception:
        auc = None

    cm = confusion_matrix(binary_labels, binary_preds).tolist()
    # cm: [[TN, FP], [FN, TP]] where 1 is biryani
    tn = cm[0][0] if len(cm) > 1 else 0
    fp = cm[0][1] if len(cm) > 1 else 0
    fn = cm[1][0] if len(cm) > 1 else 0
    tp = cm[1][1] if len(cm) > 1 else 0

    results = {
        "test_samples": len(test_dataset),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4) if auc is not None else "N/A",
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
            "raw_matrix": cm
        },
        "per_class": {
            "biryani": {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "support": int(np.sum(binary_labels == 1))
            },
            "not_biryani": {
                "precision": round(tn / (tn + fn) if (tn + fn) > 0 else 0, 4),
                "recall": round(tn / (tn + fp) if (tn + fp) > 0 else 0, 4),
                "support": int(np.sum(binary_labels == 0))
            }
        }
    }

    eval_out = BASE_DIR / "evaluation" / "test_evaluation_results.json"
    eval_out.parent.mkdir(parents=True, exist_ok=True)
    with open(eval_out, "w") as f:
        json.dump(results, f, indent=2)

    print("\n========== BIRYANI CLASSIFIER TEST EVALUATION ==========")
    print(f"Test Accuracy: {acc * 100:.2f}%")
    print(f"Precision:     {prec * 100:.2f}%")
    print(f"Recall:        {rec * 100:.2f}%")
    print(f"F1-Score:      {f1 * 100:.2f}%")
    if auc is not None:
        print(f"ROC-AUC:       {auc:.4f}")
    print(f"Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    print(f"Results saved to {eval_out}")
    print("========================================================\n")

    return results

if __name__ == "__main__":
    evaluate_test_set()
