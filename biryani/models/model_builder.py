import torch
import torch.nn as nn
from torchvision import models

def build_biryani_model(arch="mobilenet_v3_small", pretrained=True, num_classes=2, dropout_p=0.3):
    """
    Constructs a transfer-learning model tailored for Biryani vs Not-Biryani classification.
    Supports lightweight, CPU-efficient architectures:
    - mobilenet_v3_small (Recommended: ~9.3 MB, ultra-fast CPU latency < 15ms)
    - mobilenet_v3_large (~21 MB)
    - resnet18 (~44 MB)
    - efficientnet_b0 (~20 MB)
    """
    arch = arch.lower()
    
    if arch == "mobilenet_v3_small":
        weights = models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v3_small(weights=weights)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Sequential(
            nn.Dropout(p=dropout_p),
            nn.Linear(in_features, num_classes)
        )
    elif arch == "mobilenet_v3_large":
        weights = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v3_large(weights=weights)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Sequential(
            nn.Dropout(p=dropout_p),
            nn.Linear(in_features, num_classes)
        )
    elif arch == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=dropout_p),
            nn.Linear(in_features, num_classes)
        )
    elif arch == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Sequential(
            nn.Dropout(p=dropout_p),
            nn.Linear(in_features, num_classes)
        )
    else:
        raise ValueError(f"Unsupported architecture: {arch}")
        
    return model
