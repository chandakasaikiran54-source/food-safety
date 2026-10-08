"""
FoodSafe AI — Biryani Regional Classifier Architecture Builder
Implements Phase 11: Multi-architecture support for EfficientNet, MobileNet, ResNet, and ConvNeXt.
"""

import torch
import torch.nn as nn
from torchvision import models
import logging

logger = logging.getLogger(__name__)

SUPPORTED_ARCHITECTURES = [
    "mobilenet_v3_large",
    "efficientnet_b0",
    "resnet50",
    "convnext_tiny"
]

def build_biryani_classifier(architecture="efficientnet_b0", num_classes=12, pretrained=True, dropout=0.3):
    """
    Builds a transfer-learning image classification model with custom classification head.
    """
    arch = architecture.lower()
    weights = "DEFAULT" if pretrained else None

    if arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT if pretrained else None)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=dropout, inplace=True),
            nn.Linear(in_features, 256),
            nn.SiLU(),
            nn.Dropout(p=dropout / 2.0),
            nn.Linear(256, num_classes)
        )

    elif arch == "mobilenet_v3_large":
        model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None)
        in_features = model.classifier[0].in_features
        model.classifier = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.Hardswish(),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_classes)
        )

    elif arch == "resnet50":
        model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT if pretrained else None)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(p=dropout / 2.0),
            nn.Linear(256, num_classes)
        )

    elif arch == "convnext_tiny":
        model = models.convnext_tiny(weights=models.ConvNeXt_Tiny_Weights.DEFAULT if pretrained else None)
        in_features = model.classifier[2].in_features
        model.classifier[2] = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes)
        )

    else:
        raise ValueError(f"Unsupported architecture '{architecture}'. Choose from: {SUPPORTED_ARCHITECTURES}")

    logger.info(f"Built model: {architecture} with {num_classes} target classes (Pretrained: {pretrained})")
    return model

def get_model_size_mb(model):
    """Calculates model parameter size in Megabytes."""
    param_size = sum(p.numel() * p.element_size() for p in model.parameters())
    buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
    return (param_size + buffer_size) / (1024 * 1024)
