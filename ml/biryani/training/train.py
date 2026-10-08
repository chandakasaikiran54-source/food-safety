"""
FoodSafe AI — Biryani Regional Classifier Training Pipeline
Implements Phase 12 & 13: Hardware audit, transfer learning, checkpointing, and metrics tracking.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.biryani_config import (
    TRAIN_DIR, VAL_DIR, MODELS_DIR, IMAGE_SIZE,
    NORMALIZATION_MEAN, NORMALIZATION_STD,
    BATCH_SIZE, NUM_EPOCHS, LEARNING_RATE, WEIGHT_DECAY,
    TARGET_CLASSES, CLASS_TO_IDX, IDX_TO_CLASS
)
from training.model_builder import build_biryani_classifier, get_model_size_mb

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def check_hardware_environment():
    """
    Implements Phase 12: Rigorous hardware and accelerator audit.
    """
    print("=" * 60)
    print("HARDWARE & ACCELERATOR ENVIRONMENT AUDIT")
    print("=" * 60)
    cuda_available = torch.cuda.is_available()
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available:  {cuda_available}")

    if cuda_available:
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        cuda_version = torch.version.cuda
        print(f"GPU:             YES ({gpu_count} device(s) active)")
        print(f"GPU NAME:        {gpu_name}")
        print(f"CUDA Version:    {cuda_version}")
        print(f"VRAM:            {vram_gb:.2f} GB")
        device = torch.device("cuda:0")
    else:
        print("GPU:             NO (NVIDIA CUDA GPU not detected)")
        print("GPU NAME:        N/A (Host graphics: Intel Integrated Graphics)")
        print("CUDA:            N/A")
        print("VRAM:            N/A (Using Host System RAM)")
        print("Status:          Running on CPU mode.")
        print("Recommendation:  For long high-epoch training runs, execute via Google Colab GPU.")
        device = torch.device("cpu")

    print("=" * 60)
    return device, cuda_available

def get_data_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.75, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORMALIZATION_MEAN, std=NORMALIZATION_STD)
    ])

    val_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORMALIZATION_MEAN, std=NORMALIZATION_STD)
    ])

    return train_transform, val_transform

def train_biryani_model(architecture="mobilenet_v3_large",
                        epochs=NUM_EPOCHS,
                        batch_size=BATCH_SIZE,
                        lr=LEARNING_RATE,
                        patience=4):
    device, cuda_available = check_hardware_environment()
    train_tf, val_tf = get_data_transforms()

    # Load datasets
    train_dataset = datasets.ImageFolder(root=str(TRAIN_DIR), transform=train_tf)
    val_dataset = datasets.ImageFolder(root=str(VAL_DIR), transform=val_tf)

    num_classes = len(train_dataset.classes)
    class_names = train_dataset.classes
    logger.info(f"Loaded datasets: {len(train_dataset)} train samples, {len(val_dataset)} val samples across {num_classes} classes.")

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    model = build_biryani_classifier(architecture=architecture, num_classes=num_classes, pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    use_amp = cuda_available and hasattr(torch.cuda, "amp")
    scaler = torch.cuda.amp.GradScaler() if use_amp else None

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    best_val_acc = 0.0
    best_epoch = 0
    epochs_no_improve = 0
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}

    start_time = time.time()
    for epoch in range(1, epochs + 1):
        # Training Phase
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()

            if use_amp:
                with torch.cuda.amp.autocast():
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += labels.size(0)

        scheduler.step()
        epoch_train_loss = running_loss / max(1, total_train)
        epoch_train_acc = correct_train / max(1, total_train)

        # Validation Phase
        model.eval()
        running_val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                running_val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels.data).item()
                total_val += labels.size(0)

        epoch_val_loss = running_val_loss / max(1, total_val)
        epoch_val_acc = correct_val / max(1, total_val)

        history["train_loss"].append(epoch_train_loss)
        history["train_acc"].append(epoch_train_acc)
        history["val_loss"].append(epoch_val_loss)
        history["val_acc"].append(epoch_val_acc)

        logger.info(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.3f} | Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc:.3f}")

        # Checkpointing
        if epoch_val_acc >= best_val_acc:
            best_val_acc = epoch_val_acc
            best_epoch = epoch
            epochs_no_improve = 0
            best_path = MODELS_DIR / "best_biryani_classifier.pth"
            torch.save({
                "epoch": epoch,
                "architecture": architecture,
                "model_state_dict": model.state_dict(),
                "val_acc": best_val_acc,
                "class_names": class_names,
                "class_to_idx": train_dataset.class_to_idx,
                "normalization": {"mean": NORMALIZATION_MEAN, "std": NORMALIZATION_STD}
            }, str(best_path))
            logger.info(f"  >>> Best model saved (Val Acc: {best_val_acc:.4f})")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                logger.info(f"Early stopping triggered after {epoch} epochs (Best Val Acc: {best_val_acc:.4f})")
                break

    training_time = time.time() - start_time

    # Save final model
    final_path = MODELS_DIR / "final_biryani_classifier.pth"
    torch.save({
        "epoch": epoch,
        "architecture": architecture,
        "model_state_dict": model.state_dict(),
        "final_val_acc": epoch_val_acc,
        "class_names": class_names,
        "class_to_idx": train_dataset.class_to_idx
    }, str(final_path))

    # Save metadata files (Phase 13)
    with open(MODELS_DIR / "class_names.json", "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)

    training_config = {
        "architecture": architecture,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "optimizer": "AdamW",
        "scheduler": "CosineAnnealingLR",
        "training_time_seconds": round(training_time, 2),
        "device": str(device),
        "cuda_used": cuda_available,
        "best_epoch": best_epoch,
        "best_val_accuracy": round(best_val_acc, 4),
        "model_size_mb": round(get_model_size_mb(model), 2)
    }
    with open(MODELS_DIR / "training_config.json", "w", encoding="utf-8") as f:
        json.dump(training_config, f, indent=2)

    with open(MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    logger.info("Training complete and all artifacts successfully persisted.")
    return training_config

if __name__ == "__main__":
    train_biryani_model()
