import os
import sys
import time
import json
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Ensure root paths are in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.biryani_config import (
    DATASET_DIR, MODELS_DIR, CHECKPOINT_PATH, METADATA_PATH,
    IMAGE_SIZE, BATCH_SIZE, NUM_EPOCHS, LEARNING_RATE, WEIGHT_DECAY,
    RANDOM_SEED, ARCHITECTURE, CLASS_NAMES
)
from preprocessing.preprocessor import get_train_transforms, get_inference_transforms
from models.model_builder import build_biryani_model

def train():
    torch.manual_seed(RANDOM_SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Training] Using device: {device}")

    train_dir = DATASET_DIR / "train"
    val_dir = DATASET_DIR / "val"

    if not train_dir.exists() or not val_dir.exists():
        raise FileNotFoundError(f"Dataset directories not found in {DATASET_DIR}. Run dataset_builder first.")

    train_dataset = ImageFolder(root=str(train_dir), transform=get_train_transforms(IMAGE_SIZE))
    val_dataset = ImageFolder(root=str(val_dir), transform=get_inference_transforms(IMAGE_SIZE))

    print(f"[Training] Classes detected: {train_dataset.class_to_idx}")
    print(f"[Training] Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # Class weighting to handle any remaining imbalance
    class_counts = [0] * len(train_dataset.classes)
    for _, label in train_dataset.samples:
        class_counts[label] += 1
    total_samples = sum(class_counts)
    weights = [total_samples / (len(class_counts) * c) if c > 0 else 1.0 for c in class_counts]
    class_weights = torch.tensor(weights, dtype=torch.float).to(device)
    print(f"[Training] Class weights: {class_weights.tolist()}")

    # Build model
    model = build_biryani_model(arch=ARCHITECTURE, pretrained=True, num_classes=2)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    best_val_f1 = 0.0
    best_epoch = 0
    training_history = []

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n[Training] Starting training for {NUM_EPOCHS} epochs with {ARCHITECTURE}...")
    start_time = time.time()

    for epoch in range(1, NUM_EPOCHS + 1):
        # Training Phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / total if total > 0 else 0.0
        train_acc = correct / total if total > 0 else 0.0

        # Validation Phase
        model.eval()
        val_loss_sum = 0.0
        val_total = 0
        all_labels = []
        all_preds = []

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss_sum += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                
                val_total += labels.size(0)
                all_labels.extend(labels.cpu().numpy())
                all_preds.extend(preds.cpu().numpy())

        scheduler.step()

        val_loss = val_loss_sum / val_total if val_total > 0 else 0.0
        val_acc = accuracy_score(all_labels, all_preds)
        val_f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
        val_prec = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
        val_rec = recall_score(all_labels, all_preds, average='weighted', zero_division=0)

        epoch_stats = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 4),
            "val_precision": round(val_prec, 4),
            "val_recall": round(val_rec, 4),
            "val_f1": round(val_f1, 4),
        }
        training_history.append(epoch_stats)
        print(f"Epoch {epoch}/{NUM_EPOCHS} -> Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}, Val F1: {val_f1:.4f}")

        # Save checkpoint if best F1
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            torch.save({
                "model_state_dict": model.state_dict(),
                "architecture": ARCHITECTURE,
                "class_to_idx": train_dataset.class_to_idx,
                "classes": train_dataset.classes,
                "epoch": epoch,
                "val_f1": val_f1,
                "val_acc": val_acc
            }, str(CHECKPOINT_PATH))
            print(f"  -> Best model saved to {CHECKPOINT_PATH} (Epoch {epoch}, F1: {val_f1:.4f})")

    total_training_time = time.time() - start_time
    print(f"\n[Training] Completed in {total_training_time:.1f}s. Best Epoch: {best_epoch} with Val F1: {best_val_f1:.4f}")

    metadata = {
        "architecture": ARCHITECTURE,
        "input_resolution": list(IMAGE_SIZE),
        "best_epoch": best_epoch,
        "best_val_f1": best_val_f1,
        "training_time_seconds": round(total_training_time, 2),
        "class_mapping": train_dataset.class_to_idx,
        "history": training_history,
        "device": str(device),
        "checkpoint_file": str(CHECKPOINT_PATH.name)
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata

if __name__ == "__main__":
    train()
