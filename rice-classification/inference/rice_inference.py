"""
Production Inference Engine for Rice Classification (FoodSafe AI).
Loads the trained PyTorch checkpoint and performs real-time classification
with image quality validation and confidence thresholding.
"""

import os
import sys
import json
import logging
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import torch
import torch.nn.functional as F

CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from config.rice_config import (
    CHECKPOINT_PATH, CLASS_NAMES_PATH, CONFIG_PATH,
    IMAGE_SIZE, TARGET_CLASSES, CONFIDENCE_THRESHOLD, ARCHITECTURE
)
from preprocessing.rice_preprocessor import (
    get_eval_transforms, assess_image_quality, to_pil_image
)
from models.rice_model_builder import build_rice_classifier

logger = logging.getLogger(__name__)

class RiceClassifierInferenceEngine:
    """
    Inference Engine for Rice Variety Classification in FoodSafe AI.
    Integrates with both standalone testing and the live Flask/Express microservice.
    """
    def __init__(self, checkpoint_path=None, config_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else CHECKPOINT_PATH
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        self.model = None
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(TARGET_CLASSES)}
        self.idx_to_class = {i: cls_name for i, cls_name in enumerate(TARGET_CLASSES)}
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.transform = get_eval_transforms(IMAGE_SIZE)
        self.is_loaded = False
        self.load_model()

    def load_model(self):
        if not self.checkpoint_path.exists():
            logger.warning(f"Rice classifier checkpoint not found at {self.checkpoint_path}. Model uninitialized.")
            self.is_loaded = False
            return False

        try:
            checkpoint = torch.load(str(self.checkpoint_path), map_location=self.device)
            arch = checkpoint.get("architecture", ARCHITECTURE)
            self.class_to_idx = checkpoint.get("class_to_idx", self.class_to_idx)
            self.idx_to_class = {idx: name for name, idx in self.class_to_idx.items()}
            self.confidence_threshold = checkpoint.get("confidence_threshold", CONFIDENCE_THRESHOLD)

            num_classes = len(self.class_to_idx)
            self.model = build_rice_classifier(arch=arch, pretrained=False, num_classes=num_classes)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model = self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            logger.info(f"Rice classifier model ({arch}) loaded successfully on {self.device}")
            return True
        except Exception as e:
            logger.error(f"Error loading Rice classifier checkpoint: {e}", exc_info=True)
            self.model = None
            self.is_loaded = False
            return False

    def predict(self, image_input):
        """
        Runs the complete inference pipeline:
        1. Decode and Quality Validation
        2. Neural Inference
        3. Confidence Thresholding (unknown / insufficient evidence handling)
        """
        # 1. Decode Image
        cv_img = None
        pil_img = None

        try:
            if isinstance(image_input, (str, Path)):
                cv_img = cv2.imread(str(image_input))
                pil_img = Image.open(str(image_input)).convert("RGB")
            elif isinstance(image_input, (bytes, bytearray)):
                nparr = np.frombuffer(image_input, np.uint8)
                cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                import io
                pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
            elif isinstance(image_input, np.ndarray):
                cv_img = image_input
                pil_img = to_pil_image(image_input)
            elif isinstance(image_input, Image.Image):
                pil_img = image_input.convert("RGB")
                cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            else:
                return {
                    "success": False,
                    "rice_type": "unknown",
                    "confidence": 0.0,
                    "status": "unsupported_format",
                    "message": "Unsupported image format."
                }
        except Exception as e:
            return {
                "success": False,
                "rice_type": "unknown",
                "confidence": 0.0,
                "status": "decode_error",
                "message": f"Error decoding image: {str(e)}"
            }

        # 2. Quality Assessment
        is_good, q_msg, q_metrics = assess_image_quality(cv_img)
        if not is_good:
            return {
                "success": False,
                "rice_type": "unknown",
                "confidence": 0.0,
                "status": "quality_failed",
                "message": q_msg,
                "evidence": {
                    "grain_visibility": "poor",
                    "quality_metrics": q_metrics
                }
            }

        if not self.is_loaded:
            if not self.load_model():
                return {
                    "success": False,
                    "rice_type": "unknown",
                    "confidence": 0.0,
                    "status": "model_not_ready",
                    "message": "Rice classifier model checkpoint not loaded."
                }

        # 3. Model Inference
        try:
            tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.model(tensor)
                probs = F.softmax(logits, dim=1)[0]
                
                max_prob, max_idx = torch.max(probs, dim=0)
                confidence = float(max_prob.item())
                predicted_class = self.idx_to_class.get(int(max_idx.item()), "unknown")

            # 4. Confidence Thresholding
            if confidence < self.confidence_threshold:
                return {
                    "success": True,
                    "rice_type": "unknown",
                    "raw_prediction": predicted_class,
                    "confidence": round(confidence, 2),
                    "status": "insufficient_evidence",
                    "message": "Confidence below threshold. Visual evidence insufficient to confirm variety conclusively.",
                    "evidence": {
                        "grain_visibility": "adequate",
                        "quality_metrics": q_metrics
                    }
                }

            return {
                "success": True,
                "rice_type": predicted_class,
                "confidence": round(confidence, 2),
                "status": "prediction_available",
                "message": f"Rice variety identified as {predicted_class}.",
                "evidence": {
                    "grain_visibility": "good",
                    "quality_metrics": q_metrics,
                    "class_probabilities": {
                        self.idx_to_class[i]: round(float(probs[i].item()), 3)
                        for i in range(len(self.idx_to_class))
                    }
                }
            }
        except Exception as e:
            logger.error(f"Inference execution error: {e}", exc_info=True)
            return {
                "success": False,
                "rice_type": "unknown",
                "confidence": 0.0,
                "status": "inference_error",
                "message": f"Inference execution error: {str(e)}"
            }

# Singleton instance
_RICE_ENGINE = None

def get_rice_inference_engine():
    global _RICE_ENGINE
    if _RICE_ENGINE is None:
        _RICE_ENGINE = RiceClassifierInferenceEngine()
    return _RICE_ENGINE

def predict_rice_variety(image_input):
    engine = get_rice_inference_engine()
    return engine.predict(image_input)
