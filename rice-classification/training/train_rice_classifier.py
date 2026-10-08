"""
GPU-accelerated training pipeline for FoodSafe AI Rice Variety Classifier.
Enforces CUDA hardware requirement, logs exact diagnostic metrics,
trains with early stopping & checkpointing, evaluates on untouched test set,
and exports all deployment artifacts.
"""

import os
import sys
import json
import time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import GradScaler, autocast
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from config.rice_config import (
    TARGET_CLASSES, NUM_CLASSES, CLASS_TO_IDX, IDX_TO_CLASS,
    ARCHITECTURE, EPOCHS, BATCH_SIZE, LEARNING_RATE, WEIGHT_DECAY,
    IMAGE_SIZE, NORM_MEAN, NORM_STD, CONFIDENCE_THRESHOLD,
    EXPORT_DIR, CHECKPOINT_PATH, CLASS_NAMES_PATH, CONFIG_PATH, METRICS_PATH,
    PROCESSED_DATA_DIR, RAW_DATA_DIR
)
from models.rice_model_builder import build_rice_classifier
from dataset.dataset_loader import (
    download_dataset, extract_archive, prepare_and_split_dataset, get_dataloaders
)

def run_training():
    # -------------------------------------------------------------
    # 1. HARDWARE DETECTION & STRICT CUDA CHECK (Phase 13)
    # -------------------------------------------------------------
    if not torch.cuda.is_available():
        print("\n========================================================")
        print("CRITICAL: Compatible GPU unavailable; training would run on CPU.")
        print("As per project specifications, training execution is halted.")
        print("Please enable a CUDA-compatible GPU (e.g. Google Colab T4/V100/A100).")
        print("========================================================\n")
        sys.exit(1)

    device = torch.device("cuda")
    gpu_name = torch.cuda.get_device_name(0)
    cuda_version = torch.version.cuda
    pytorch_version = torch.__version__

    # -------------------------------------------------------------
    # 2. DATASET ACQUISITION & VALIDATION (Phases 5-7)
    # -------------------------------------------------------------
    archive_path = download_dataset(target_dir=RAW_DATA_DIR)
    extracted_dir = extract_archive(archive_path, extract_dir=RAW_DATA_DIR / "extracted")
    train_dir, val_dir, test_dir = prepare_and_split_dataset(extracted_dir, processed_dir=PROCESSED_DATA_DIR)

    train_loader, val_loader, test_loader, train_ds, val_ds, test_ds = get_dataloaders(
        processed_dir=PROCESSED_DATA_DIR, batch_size=BATCH_SIZE, num_workers=2
    )

    # -------------------------------------------------------------
    # 3. MANDATORY PRE-TRAINING PRINT SPECIFICATION
    # -------------------------------------------------------------
    print("GPU:", gpu_name)
    print("CUDA:", cuda_version)
    print("PyTorch:", pytorch_version)
    print("Dataset: Mendeley Data (Milled Rice Grain - Prabira Sethy DOI: 10.17632/c5y6gjwdzh.1)")
    print("Classes:", TARGET_CLASSES)
    print("Train images:", len(train_ds))
    print("Validation images:", len(val_ds))
    print("Test images:", len(test_ds))
    print("--------------------------------------------------------\n")

    # -------------------------------------------------------------
    # 4. MODEL INITIALIZATION & TRAINING SETUP (Phase 11-12)
    # -------------------------------------------------------------
    model = build_rice_classifier(arch=ARCHITECTURE, pretrained=True, num_classes=NUM_CLASSES)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=1e-6)
    scaler = GradScaler()

    best_val_acc = 0.0
    best_model_state = None
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[Training] Starting training on {gpu_name} for {EPOCHS} epochs...")
    start_time = time.time()

    for epoch in range(1, EPOCHS + 1):
        # Training Phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            optimizer.zero_grad()
            with autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        scheduler.step()
        epoch_train_loss = running_loss / total
        epoch_train_acc = correct / total

        # Validation Phase
        model.eval()
        val_running_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)
                with autocast():
                    outputs = model(images)
                    loss = criterion(outputs, labels)

                val_running_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        epoch_val_loss = val_running_loss / val_total
        epoch_val_acc = val_correct / val_total

        history["train_loss"].append(round(epoch_train_loss, 4))
        history["val_loss"].append(round(epoch_val_loss, 4))
        history["train_acc"].append(round(epoch_train_acc, 4))
        history["val_acc"].append(round(epoch_val_acc, 4))

        print(f"Epoch [{epoch:02d}/{EPOCHS:02d}] "
              f"Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc*100:.2f}% | "
              f"Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc*100:.2f}%")

        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            best_model_state = model.state_dict().copy()
            # Save intermediate best checkpoint
            torch.save({
                "epoch": epoch,
                "architecture": ARCHITECTURE,
                "model_state_dict": best_model_state,
                "val_acc": best_val_acc,
                "class_to_idx": CLASS_TO_IDX,
                "classes": TARGET_CLASSES
            }, str(CHECKPOINT_PATH))

    total_training_time = time.time() - start_time
    print(f"\n[Training] Completed in {total_training_time/60:.2f} mins. Best Val Acc: {best_val_acc*100:.2f}%")

    # -------------------------------------------------------------
    # 5. TEST SET EVALUATION (Phase 16)
    # -------------------------------------------------------------
    print("\n[Evaluation] Evaluating best model on untouched test set...")
    model.load_state_dict(best_model_state)
    model.eval()

    y_true = []
    y_pred = []
    y_probs = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            with autocast():
                logits = model(images)
                probs = torch.softmax(logits, dim=1)

            preds = torch.argmax(probs, dim=1)
            y_true.extend(labels.cpu().numpy().tolist())
            y_pred.extend(preds.cpu().numpy().tolist())
            y_probs.extend(probs.cpu().numpy().tolist())

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    overall_acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    per_cls_prec, per_cls_rec, per_cls_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=list(range(NUM_CLASSES)), zero_division=0
    )
    conf_mat = confusion_matrix(y_true, y_pred, labels=list(range(NUM_CLASSES))).tolist()

    print(f"Overall Test Accuracy: {overall_acc*100:.2f}%")
    print(f"Weighted Precision:   {prec:.4f}")
    print(f"Weighted Recall:      {rec:.4f}")
    print(f"Weighted F1-score:    {f1:.4f}")
    print("\nPer-class Performance:")
    for idx, cls_name in enumerate(TARGET_CLASSES):
        print(f"  {cls_name.upper():<12} -> Precision: {per_cls_prec[idx]:.4f} | Recall: {per_cls_rec[idx]:.4f} | F1: {per_cls_f1[idx]:.4f}")

    print("\nConfusion Matrix:")
    print(" " * 14 + " ".join([f"{c[:6]:>8}" for c in TARGET_CLASSES]))
    for idx, row in enumerate(conf_mat):
        row_str = " ".join([f"{v:>8}" for v in row])
        print(f"{TARGET_CLASSES[idx][:12]:<12}: {row_str}")

    # -------------------------------------------------------------
    # 6. EXPORT ARTIFACTS (Phase 22-23)
    # -------------------------------------------------------------
    # 1. Final Best Model
    torch.save({
        "architecture": ARCHITECTURE,
        "model_state_dict": best_model_state,
        "test_accuracy": float(overall_acc),
        "test_f1": float(f1),
        "class_to_idx": CLASS_TO_IDX,
        "classes": TARGET_CLASSES,
        "image_size": IMAGE_SIZE,
        "norm_mean": NORM_MEAN,
        "norm_std": NORM_STD,
        "confidence_threshold": CONFIDENCE_THRESHOLD
    }, str(CHECKPOINT_PATH))
    print(f"[Export] Saved best model to: {CHECKPOINT_PATH}")

    # 2. class_names.json
    with open(CLASS_NAMES_PATH, "w") as f:
        json.dump({str(idx): name for idx, name in enumerate(TARGET_CLASSES)}, f, indent=2)
    print(f"[Export] Saved class names to: {CLASS_NAMES_PATH}")

    # 3. preprocessing_config.json
    config_data = {
        "architecture": ARCHITECTURE,
        "image_size": IMAGE_SIZE,
        "normalization": {"mean": NORM_MEAN, "std": NORM_STD},
        "classes": TARGET_CLASSES,
        "class_to_idx": CLASS_TO_IDX,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "hardware": {
            "gpu": gpu_name,
            "cuda": cuda_version,
            "pytorch": pytorch_version
        }
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"[Export] Saved preprocessing config to: {CONFIG_PATH}")

    # 4. metrics.json
    metrics_data = {
        "overall_accuracy": float(overall_acc),
        "weighted_precision": float(prec),
        "weighted_recall": float(rec),
        "weighted_f1": float(f1),
        "per_class": {
            cls_name: {
                "precision": float(per_cls_prec[idx]),
                "recall": float(per_cls_rec[idx]),
                "f1": float(per_cls_f1[idx])
            } for idx, cls_name in enumerate(TARGET_CLASSES)
        },
        "confusion_matrix": conf_mat,
        "history": history,
        "training_time_seconds": round(total_training_time, 1)
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"[Export] Saved evaluation metrics to: {METRICS_PATH}")

    print("\n========================================================")
    print("SUCCESS: Rice variety classifier training & evaluation completed!")
    print(f"Artifacts exported to: {EXPORT_DIR}")
    print("========================================================\n")

if __name__ == "__main__":
    run_training()
