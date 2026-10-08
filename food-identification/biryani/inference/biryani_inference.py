import os
import sys
import logging
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import torch
import torch.nn.functional as F

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.biryani_config import (
    CHECKPOINT_PATH, IMAGE_SIZE,
    BIRYANI_CONFIDENCE_THRESHOLD, OTHER_CONFIDENCE_THRESHOLD, ARCHITECTURE
)
from preprocessing.preprocessor import (
    get_inference_transforms, assess_image_quality, to_pil_image
)
from models.model_builder import build_biryani_model

logger = logging.getLogger(__name__)

class BiryaniInferenceEngine:
    """
    Dedicated, modular inference engine for Biryani identification and quality assessment.
    """
    def __init__(self, checkpoint_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else CHECKPOINT_PATH
        self.model = None
        self.class_to_idx = {"biryani": 0, "not_biryani": 1}
        self.biryani_idx = 0
        self.not_biryani_idx = 1
        self.transform = get_inference_transforms(IMAGE_SIZE)
        self.load_model()

    def load_model(self):
        if not self.checkpoint_path.exists():
            logger.warning(f"Biryani checkpoint not found at {self.checkpoint_path}. Model uninitialized.")
            return

        try:
            checkpoint = torch.load(str(self.checkpoint_path), map_location=self.device)
            arch = checkpoint.get("architecture", ARCHITECTURE)
            self.class_to_idx = checkpoint.get("class_to_idx", {"biryani": 0, "not_biryani": 1})
            self.biryani_idx = self.class_to_idx.get("biryani", 0)
            self.not_biryani_idx = self.class_to_idx.get("not_biryani", 1)

            self.model = build_biryani_model(arch=arch, pretrained=False, num_classes=2)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.info(f"Biryani model loaded successfully from {self.checkpoint_path}")
        except Exception as e:
            logger.error(f"Failed to load Biryani model: {e}")
            self.model = None

    def predict(self, image_input):
        """
        Runs the food identification pipeline:
        1. Decode and Quality Assessment
        2. Food Identifier (Biryani Classifier)
        3. Returns strictly formatted response with confidence thresholds
        """
        # 1. Decode to CV2 numpy for quality assessment
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
                    "food": "unknown",
                    "is_biryani": False,
                    "confidence": 0.0,
                    "message": "Unsupported image format."
                }
        except Exception as e:
            return {
                "success": False,
                "food": "unknown",
                "is_biryani": False,
                "confidence": 0.0,
                "message": f"Error decoding image: {str(e)}"
            }

        # 2. Quality Assessment
        is_good, q_msg, q_metrics = assess_image_quality(cv_img)
        if not is_good:
            return {
                "success": False,
                "food": "unknown",
                "is_biryani": False,
                "confidence": 0.0,
                "quality_passed": False,
                "message": q_msg,
                "quality_metrics": q_metrics
            }

        if self.model is None:
            self.load_model()
            if self.model is None:
                return {
                    "success": False,
                    "food": "unknown",
                    "is_biryani": False,
                    "confidence": 0.0,
                    "message": "Biryani classification model not initialized."
                }

        # 3. Model Inference
        try:
            tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.model(tensor)
                probs = F.softmax(logits, dim=1)[0]
                
                p_biryani = float(probs[self.biryani_idx].item())
                p_other = float(probs[self.not_biryani_idx].item())

            logger.info(f"[Biryani Inference] p_biryani: {p_biryani:.4f}, p_other: {p_other:.4f}")

            # 4. Threshold Logic
            if p_biryani >= BIRYANI_CONFIDENCE_THRESHOLD:
                return {
                    "success": True,
                    "food": "biryani",
                    "is_biryani": True,
                    "confidence": round(p_biryani, 2),
                    "quality_passed": True,
                    "message": "Biryani successfully identified.",
                    "biryani_specific_analysis": {
                        "food_category": "Biryani (Rice & Spiced Delicacy)",
                        "identification_confidence": round(p_biryani, 2),
                        "microbial_safety_note": "Visual AI identifies food types. Ordinary RGB food photos cannot directly prove bacteria, bacterial count, or microbial toxins. Follow food hygiene guidelines."
                    }
                }
            elif p_biryani < OTHER_CONFIDENCE_THRESHOLD:
                return {
                    "success": True,
                    "food": "other",
                    "is_biryani": False,
                    "confidence": round(p_other, 2),
                    "quality_passed": True,
                    "message": "Food identified as non-Biryani dish."
                }
            else:
                # Ambiguous / Low confidence zone (between 0.35 and 0.65)
                return {
                    "success": True,
                    "food": "unknown",
                    "is_biryani": False,
                    "confidence": round(max(p_biryani, p_other), 2),
                    "quality_passed": True,
                    "message": "Confidence insufficient to conclusively identify dish. Please upload a clearer photo."
                }
        except Exception as e:
            logger.error(f"Inference error: {e}", exc_info=True)
            return {
                "success": False,
                "food": "unknown",
                "is_biryani": False,
                "confidence": 0.0,
                "message": f"Inference execution error: {str(e)}"
            }

# Global singleton engine
_ENGINE_INSTANCE = None

def get_biryani_inference_engine():
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        _ENGINE_INSTANCE = BiryaniInferenceEngine()
    return _ENGINE_INSTANCE

def identify_biryani(image_input):
    """Stand-alone entrypoint for external callers."""
    engine = get_biryani_inference_engine()
    return engine.predict(image_input)
