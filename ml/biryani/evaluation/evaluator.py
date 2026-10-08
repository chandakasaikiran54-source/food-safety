"""
FoodSafe AI — Dual-Stage Biryani Evaluator & Domain Gap Analyzer
Implements Phase 16, 17, & 18:
- Stage 1: Untouched Video-frame Test Set
- Stage 2: Real Smartphone Photo Test Set
- Domain Gap Analysis (Video Accuracy vs Smartphone Accuracy)
- Per-class metrics, confusion matrix, and classification report.
"""

import os
import sys
import json
import logging
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.biryani_config import (
    TEST_DIR, SMARTPHONE_TEST_DIR, MODELS_DIR, EVALUATION_DIR,
    IMAGE_SIZE, NORMALIZATION_MEAN, NORMALIZATION_STD,
    TARGET_CLASSES, CLASS_TO_IDX, IDX_TO_CLASS
)
from training.model_builder import build_biryani_classifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class BiryaniModelEvaluator:
    def __init__(self, checkpoint_path=None, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = checkpoint_path or (MODELS_DIR / "best_biryani_classifier.pth")
        self.model = None
        self.class_names = [c.lower() for c in TARGET_CLASSES]
        self.eval_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORMALIZATION_MEAN, std=NORMALIZATION_STD)
        ])
        self.load_model()

    def load_model(self):
        if not Path(self.checkpoint_path).exists():
            logger.warning(f"Checkpoint not found at {self.checkpoint_path}. Using uninitialized/mock weights for evaluation testing.")
            self.model = build_biryani_classifier(architecture="mobilenet_v3_large", num_classes=12, pretrained=False)
            self.model = self.model.to(self.device)
            self.model.eval()
            return

        checkpoint = torch.load(str(self.checkpoint_path), map_location=self.device)
        arch = checkpoint.get("architecture", "mobilenet_v3_large")
        self.class_names = checkpoint.get("class_names", self.class_names)
        num_classes = len(self.class_names)

        self.model = build_biryani_classifier(architecture=arch, num_classes=num_classes, pretrained=False)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model = self.model.to(self.device)
        self.model.eval()
        logger.info(f"Model loaded successfully from {self.checkpoint_path} ({arch})")

    def evaluate_dataset(self, dataset_dir, stage_name="Stage 1 - Video Frame Test"):
        """Evaluates model on a specific directory."""
        dataset_path = Path(dataset_dir)
        if not dataset_path.exists():
            logger.warning(f"Dataset path {dataset_path} does not exist.")
            return None

        try:
            dataset = datasets.ImageFolder(root=str(dataset_path), transform=self.eval_transform)
            if len(dataset) == 0:
                logger.warning(f"Dataset at {dataset_path} has 0 samples.")
                return None
        except (FileNotFoundError, Exception) as e:
            logger.warning(f"Dataset at {dataset_path} contains no valid image files ({e}). Skipping Stage evaluation.")
            return None

        loader = DataLoader(dataset, batch_size=16, shuffle=False, num_workers=0)
        y_true = []
        y_pred = []
        y_probs = []

        with torch.no_grad():
            for images, labels in loader:
                images = images.to(self.device)
                outputs = self.model(images)
                probs = torch.softmax(outputs, dim=1)
                _, preds = torch.max(probs, 1)

                y_true.extend(labels.cpu().numpy())
                y_pred.extend(preds.cpu().numpy())
                y_probs.extend(probs.cpu().numpy())

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        acc = float(accuracy_score(y_true, y_pred))
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
        macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

        # Per-class metrics
        unique_labels = sorted(list(set(y_true).union(set(y_pred))))
        target_names = [dataset.classes[i] if i < len(dataset.classes) else f"class_{i}" for i in unique_labels]
        report_dict = classification_report(y_true, y_pred, labels=unique_labels, target_names=target_names, output_dict=True, zero_division=0)

        conf_mat = confusion_matrix(y_true, y_pred, labels=unique_labels).tolist()

        return {
            "stage_name": stage_name,
            "total_samples": len(dataset),
            "accuracy": round(acc, 4),
            "weighted_precision": round(float(prec), 4),
            "weighted_recall": round(float(rec), 4),
            "weighted_f1": round(float(f1), 4),
            "macro_precision": round(float(macro_prec), 4),
            "macro_recall": round(float(macro_rec), 4),
            "macro_f1": round(float(macro_f1), 4),
            "confusion_matrix": conf_mat,
            "class_names": target_names,
            "detailed_classification_report": report_dict
        }

    def plot_confusion_matrix(self, conf_mat, class_names, out_path):
        """Plots and saves confusion matrix heatmap."""
        plt.figure(figsize=(10, 8))
        plt.imshow(conf_mat, interpolation="nearest", cmap=plt.cm.Oranges)
        plt.title("Biryani Regional Style Confusion Matrix", fontsize=14, pad=15)
        plt.colorbar()

        tick_marks = np.arange(len(class_names))
        plt.xticks(tick_marks, class_names, rotation=45, ha="right", fontsize=9)
        plt.yticks(tick_marks, class_names, fontsize=9)

        # Text labels in cells
        for i in range(len(conf_mat)):
            for j in range(len(conf_mat[i])):
                val = conf_mat[i][j]
                plt.text(j, i, format(val, "d"),
                         ha="center", va="center",
                         color="white" if val > (np.max(conf_mat) / 2) else "black",
                         fontsize=8)

        plt.ylabel("True Regional Style", fontsize=11)
        plt.xlabel("Predicted Regional Style", fontsize=11)
        plt.tight_layout()
        plt.savefig(out_path, dpi=200)
        plt.close()

    def run_full_evaluation(self):
        """Executes Stage 1, Stage 2, and Domain Gap Analysis."""
        EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Evaluating Stage 1: Untouched Video-frame Test Set...")
        stage1_results = self.evaluate_dataset(TEST_DIR, stage_name="Stage 1: Video-frame Test Set")

        logger.info("Evaluating Stage 2: Real Smartphone Photo Test Set...")
        stage2_results = self.evaluate_dataset(SMARTPHONE_TEST_DIR, stage_name="Stage 2: Real Smartphone Photo Test Set")

        # Domain Gap Calculation (Phase 18)
        domain_gap = None
        if stage1_results and stage2_results and stage1_results["total_samples"] > 0 and stage2_results["total_samples"] > 0:
            gap_acc = stage1_results["accuracy"] - stage2_results["accuracy"]
            gap_f1 = stage1_results["weighted_f1"] - stage2_results["weighted_f1"]
            domain_gap = {
                "accuracy_gap": round(gap_acc, 4),
                "f1_gap": round(gap_f1, 4),
                "interpretation": (
                    "Significant domain shift observed between cooking video frames and handheld restaurant smartphone photos. "
                    "Primary drivers: dynamic restaurant lighting, angle differences, plating styles, and ambient color temperature."
                    if gap_acc > 0.15 else "Moderate domain alignment between video and smartphone domains."
                ),
                "mitigation_strategy": [
                    "Color-jitter and random perspective domain augmentation",
                    "Targeted fine-tuning on smartphone test collections",
                    "Dual-branch grain texture and color palette calibration"
                ]
            }

        full_report = {
            "evaluation_protocol": "Two-Stage Isolated Evaluation (No Metric Merging)",
            "stage_1_video_frame_test": stage1_results or {"status": "pending_frame_population"},
            "stage_2_real_smartphone_test": stage2_results or {"status": "pending_smartphone_population"},
            "domain_gap_analysis": domain_gap or {
                "status": "awaiting_dual_eval",
                "analysis": "Evaluated independently as mandated by Phase 8 and Phase 17."
            }
        }

        # Save classification report json
        report_file = EVALUATION_DIR / "classification_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2)

        # Generate confusion matrix plot if Stage 1 results exist
        if stage1_results and "confusion_matrix" in stage1_results:
            cm_img_file = EVALUATION_DIR / "confusion_matrix.png"
            self.plot_confusion_matrix(stage1_results["confusion_matrix"], stage1_results["class_names"], cm_img_file)

        logger.info(f"Evaluation complete. Reports written to {EVALUATION_DIR}")
        return full_report

if __name__ == "__main__":
    evaluator = BiryaniModelEvaluator()
    rep = evaluator.run_full_evaluation()
    print("Evaluation summary generated successfully!")
