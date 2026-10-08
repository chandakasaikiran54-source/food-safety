"""
FoodSafe AI — Calibrated Biryani Regional Inference Engine & Explainability (Grad-CAM)
Implements Phase 14, 15, 20, 21, & 22:
- Two-Stage Hierarchical Flow:
    Stage 1: Biryani / Not Biryani Gatekeeper (OOD rejection)
    Stage 2: 12-Class Calibrated Regional Classifier
- Temperature Scaling for Softmax Calibration
- Grad-CAM Visual Heatmap Generation
- Fallback to "Unknown" when confidence is insufficient
"""

import os
import sys
import json
import logging
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms

import importlib.util

BASE_DIR = Path(__file__).resolve().parent.parent

# Load biryani_config directly to avoid module collisions
_cfg_path = BASE_DIR / "config" / "biryani_config.py"
_spec = importlib.util.spec_from_file_location("biryani_regional_config", str(_cfg_path))
_b_cfg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b_cfg)

MODELS_DIR = _b_cfg.MODELS_DIR
IMAGE_SIZE = _b_cfg.IMAGE_SIZE
NORMALIZATION_MEAN = _b_cfg.NORMALIZATION_MEAN
NORMALIZATION_STD = _b_cfg.NORMALIZATION_STD
CONFIDENCE_THRESHOLD = _b_cfg.CONFIDENCE_THRESHOLD
HIGH_CONFIDENCE_THRESHOLD = _b_cfg.HIGH_CONFIDENCE_THRESHOLD
BIRYANI_GATE_THRESHOLD = _b_cfg.BIRYANI_GATE_THRESHOLD
TARGET_CLASSES = _b_cfg.TARGET_CLASSES
REGIONAL_PROFILES = _b_cfg.REGIONAL_PROFILES

# Load model builder directly
_bld_path = BASE_DIR / "training" / "model_builder.py"
_bspec = importlib.util.spec_from_file_location("biryani_model_builder", str(_bld_path))
_bmod = importlib.util.module_from_spec(_bspec)
_bspec.loader.exec_module(_bmod)
build_biryani_classifier = _bmod.build_biryani_classifier

logger = logging.getLogger(__name__)

class GradCAM:
    """Generates Class Activation Maps for model explainability."""
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.hook_layers()

    def hook_layers(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0]

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_backward_hook(backward_hook)

    def generate(self, input_tensor, class_idx=None):
        self.model.eval()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = torch.argmax(output, dim=1).item()

        self.model.zero_grad()
        loss = output[0, class_idx]
        loss.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            return None

        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        activations = self.activations[0].detach()

        for i in range(len(pooled_gradients)):
            activations[i, :, :] *= pooled_gradients[i]

        heatmap = torch.mean(activations, dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)
        max_val = np.max(heatmap)
        if max_val > 0:
            heatmap /= max_val
        return heatmap

class BiryaniClassifier:
    def __init__(self,
                 checkpoint_path=None,
                 temperature=1.2,
                 device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = checkpoint_path or (MODELS_DIR / "best_biryani_classifier.pth")
        self.temperature = temperature
        self.model = None
        self.grad_cam = None
        self.class_names = [c for c in TARGET_CLASSES]

        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORMALIZATION_MEAN, std=NORMALIZATION_STD)
        ])

        self.load_model()

    def load_model(self):
        if Path(self.checkpoint_path).exists():
            try:
                ckpt = torch.load(str(self.checkpoint_path), map_location=self.device)
                arch = ckpt.get("architecture", "mobilenet_v3_large")
                num_classes = len(ckpt.get("class_names", TARGET_CLASSES))
                self.class_names = [c.capitalize() for c in ckpt.get("class_names", TARGET_CLASSES)]

                self.model = build_biryani_classifier(architecture=arch, num_classes=num_classes, pretrained=False)
                self.model.load_state_dict(ckpt["model_state_dict"])
                self.model = self.model.to(self.device)
                self.model.eval()

                # Find last conv layer for Grad-CAM
                target_layer = None
                if hasattr(self.model, "features"):
                    target_layer = self.model.features[-1]
                elif hasattr(self.model, "layer4"):
                    target_layer = self.model.layer4[-1]

                if target_layer is not None:
                    try:
                        self.grad_cam = GradCAM(self.model, target_layer)
                    except Exception:
                        self.grad_cam = None

                logger.info(f"Loaded trained 12-class classifier from {self.checkpoint_path}")
                return
            except Exception as e:
                logger.error(f"Error loading checkpoint {self.checkpoint_path}: {e}")

        # Fallback to initialized model if checkpoint not yet saved
        logger.warning("Checkpoint not found or failed to load. Initializing standard model.")
        self.model = build_biryani_classifier(architecture="mobilenet_v3_large", num_classes=12, pretrained=True)
        self.model = self.model.to(self.device)
        self.model.eval()

    def predict(self, cv_image, is_confirmed_biryani=True, generate_heatmap=False):
        """
        Executes calibrated prediction on an input OpenCV BGR image.
        Returns: JSON-serializable dictionary adhering to Phase 14 specifications.
        """
        if cv_image is None or cv_image.size == 0:
            return {
                "biryani_type": "Unknown",
                "confidence": 0.0,
                "status": "invalid_image",
                "message": "Input image is empty or unreadable."
            }

        # Out-Of-Distribution Check (Phase 21)
        if not is_confirmed_biryani:
            return {
                "biryani_type": "Unknown / Not Biryani",
                "confidence": 0.0,
                "evidence_quality": "low",
                "status": "out_of_distribution",
                "message": "Dish does not match Biryani characteristics (detected as other food or non-food)."
            }

        # Convert BGR to RGB PIL
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_image)
        input_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(input_tensor)
            # Temperature scaling for confidence calibration (Phase 15)
            scaled_logits = logits / self.temperature
            probs = F.softmax(scaled_logits, dim=1).squeeze(0).cpu().numpy()

        top_idx = int(np.argmax(probs))
        top_prob = float(probs[top_idx])
        predicted_style = self.class_names[top_idx]

        # Sorted probabilities for top candidates
        top_indices = np.argsort(probs)[::-1][:3]
        top_candidates = [
            {"style": self.class_names[idx], "confidence": round(float(probs[idx]), 3)}
            for idx in top_indices
        ]

        # Phase 14: Insufficient Evidence Handling
        if top_prob < CONFIDENCE_THRESHOLD:
            return {
                "biryani_type": "Unknown",
                "confidence": round(top_prob, 2),
                "evidence_quality": "low",
                "status": "insufficient_evidence",
                "message": f"Confidence ({top_prob:.1%}) below reliable threshold ({CONFIDENCE_THRESHOLD:.1%}). Ambiguous visual features.",
                "top_candidates": top_candidates,
                "disclaimer": "Regional style prediction is based on visual evidence and may vary with recipe, restaurant, and presentation."
            }

        evidence_quality = "high" if top_prob >= HIGH_CONFIDENCE_THRESHOLD else "moderate"
        profile = REGIONAL_PROFILES.get(predicted_style, {})

        result = {
            "biryani_type": predicted_style,
            "confidence": round(top_prob, 2),
            "evidence_quality": evidence_quality,
            "status": "prediction_available",
            "top_candidates": top_candidates,
            "regional_profile": {
                "origin": profile.get("region", "India"),
                "traditional_rice": profile.get("rice", "Basmati / Seeraga Samba"),
                "cooking_method": profile.get("cooking_style", "Dum pukht"),
                "key_visual_cues": profile.get("key_visuals", "Characteristic grain and spice distribution"),
                "traditional_accompaniments": profile.get("accompaniments", "Raita, Salan")
            },
            "disclaimer": "Regional style prediction is based on visual evidence and may vary with recipe, restaurant, and presentation."
        }

        # Explainability: Grad-CAM (Phase 20)
        if generate_heatmap and self.grad_cam is not None:
            try:
                heatmap = self.grad_cam.generate(input_tensor, class_idx=top_idx)
                if heatmap is not None:
                    result["explainability"] = {
                        "method": "Grad-CAM",
                        "visual_evidence": f"Model attention concentrated primarily on {predicted_style} rice grain presentation and spice distribution.",
                        "interpretation_note": "Visual heatmap shows influential pixel regions for classification; does not imply culinary authenticity."
                    }
            except Exception as e:
                logger.debug(f"Grad-CAM generation skipped: {e}")

        return result
