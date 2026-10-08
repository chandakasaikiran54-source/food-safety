"""
Model architecture builder for Rice Classification (FoodSafe AI).
Supports transfer-learning vision backbones with customized multi-class classification heads.
"""

import torch
import torch.nn as nn
from torchvision import models

def build_rice_classifier(arch="efficientnet_b0", pretrained=True, num_classes=4, dropout_p=0.3):
    """
    Constructs a transfer-learning vision model for Rice Variety classification.
    
    Supported backbones:
    - efficientnet_b0: Optimal balance of parameter efficiency (~5.3M params) and top-1 accuracy
    - mobilenet_v3_large: Fast mobile backbone (~5.4M params)
    - resnet18: Robust residual architecture (~11.7M params)
    """
    arch = arch.lower()
    
    if arch == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=dropout_p),
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_p * 0.5),
            nn.Linear(256, num_classes)
        )
    elif arch == "mobilenet_v3_large":
        weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v3_large(weights=weights)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Sequential(
            nn.Dropout(p=dropout_p),
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_p * 0.5),
            nn.Linear(256, num_classes)
        )
    elif arch == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=dropout_p),
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_p * 0.5),
            nn.Linear(256, num_classes)
        )
    else:
        raise ValueError(f"Unsupported architecture: {arch}. Choose efficientnet_b0, mobilenet_v3_large, or resnet18.")
        
    return model
