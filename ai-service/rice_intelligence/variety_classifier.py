import os
import sys
import logging
from pathlib import Path
from .config import (
    BASMATI_MIN_ASPECT_RATIO,
    SONA_MASURI_MIN_ASPECT_RATIO,
    SONA_MASURI_MAX_ASPECT_RATIO,
    SHORT_GRAIN_MAX_ASPECT_RATIO
)

logger = logging.getLogger(__name__)

# Search paths for trained PyTorch rice classifier checkpoint
CHECKPOINT_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "models" / "rice_classifier.pth",
    Path(__file__).resolve().parent.parent.parent / "rice-classification" / "export" / "rice_classifier.pth"
]

_NEURAL_ENGINE = None

def get_neural_engine():
    global _NEURAL_ENGINE
    if _NEURAL_ENGINE is not None:
        return _NEURAL_ENGINE
    for ckpt in CHECKPOINT_CANDIDATES:
        if ckpt.exists():
            try:
                rice_mod_path = Path(__file__).resolve().parent.parent.parent / "rice-classification"
                if str(rice_mod_path) not in sys.path:
                    sys.path.insert(0, str(rice_mod_path))
                from inference.rice_inference import RiceClassifierInferenceEngine
                _NEURAL_ENGINE = RiceClassifierInferenceEngine(checkpoint_path=ckpt)
                if _NEURAL_ENGINE.is_loaded:
                    logger.info(f"Loaded Neural Rice Classifier from {ckpt}")
                    return _NEURAL_ENGINE
            except Exception as e:
                logger.warning(f"Could not load neural rice classifier: {e}")
    return None

def classify_rice_variety(morphology_result, color_result=None, cv_img=None):
    """
    Classifies rice variety combining Deep Learning computer vision (when trained weights are present)
    with empirical morphological evidence and verified standards:
    - Basmati (Extra Long Slender, aspect ratio >= 3.2)
    - Sona Masuri (Medium Slender, aspect ratio 2.4 - 3.1)
    - Other rice (Short, bold, round, or non-slender grains)
    - Unknown (When visual evidence is insufficient or confidence is low)
    """
    # 1. Attempt Deep Learning Classifier if image is provided and checkpoint exists
    if cv_img is not None:
        engine = get_neural_engine()
        if engine and engine.is_loaded:
            try:
                dl_res = engine.predict(cv_img)
                if dl_res.get("status") == "prediction_available" and dl_res.get("rice_type") in ("basmati", "sona_masuri", "other_rice"):
                    p_type = dl_res["rice_type"]
                    conf = dl_res["confidence"]
                    metrics = (morphology_result or {}).get("metrics") or {}
                    ar_str = f" Aspect ratio: {metrics.get('median_aspect_ratio'):.2f}." if metrics.get("median_aspect_ratio") else ""
                    
                    scientific_map = {
                        "basmati": "Oryza sativa L. (Basmati extra-long slender)",
                        "sona_masuri": "Oryza sativa L. (Sona Masuri / HMT medium slender)",
                        "other_rice": "Oryza sativa L. (Non-slender / other variety)"
                    }
                    return {
                        "type": p_type,
                        "confidence": conf,
                        "scientific_label": scientific_map.get(p_type, "Oryza sativa L."),
                        "model_source": "deep_learning_vision_classifier",
                        "notice": f"Deep-learning vision model confirmed {p_type.replace('_', ' ').title()}.",
                        "evidence": f"Deep visual feature extraction matched {p_type.replace('_', ' ').title()} with {conf*100:.1f}% confidence.{ar_str}",
                        "neural_details": dl_res.get("evidence", {})
                    }
            except Exception as e:
                logger.warning(f"Neural rice prediction error: {e}, falling back to morphology.")
    if not morphology_result or not morphology_result.get("success", False):
        return {
            "type": "unknown",
            "confidence": 0.0,
            "scientific_label": "Unidentified / Non-Rice",
            "notice": "Insufficient visual evidence to identify rice variety.",
            "evidence": "No clear rice grain segmentation possible."
        }

    metrics = morphology_result.get("metrics")
    if not metrics:
        return {
            "type": "unknown",
            "confidence": 0.0,
            "scientific_label": "Unknown",
            "notice": "Insufficient visual evidence.",
            "evidence": "Grain morphology metrics could not be extracted."
        }

    median_ar = metrics.get("median_aspect_ratio")
    seg_mode = morphology_result.get("grain_segmentation_mode", "individual_grains")
    grain_count = morphology_result.get("segmented_grains_count", 0)

    # If grains are in dense bulk cluster and no individual aspect ratio could be measured
    if median_ar is None:
        # Check if color/texture suggests cooked rice
        if morphology_result.get("rice_detected", False):
            return {
                "type": "unknown",
                "confidence": 0.50,
                "scientific_label": "Cooked Rice (Clustered)",
                "notice": "Individual grain boundaries cannot be isolated from the dense cooked cluster. Variety cannot be definitively confirmed without separate single grains.",
                "evidence": "Clustered cooked rice grains detected without individual grain boundary isolation."
            }
        return {
            "type": "unknown",
            "confidence": 0.0,
            "scientific_label": "Unknown",
            "notice": "Insufficient visual evidence.",
            "evidence": "Grain boundaries could not be resolved."
        }

    # High aspect ratio: Basmati (Extra-Long Slender)
    if median_ar >= BASMATI_MIN_ASPECT_RATIO:
        confidence = min(0.95, 0.70 + (grain_count * 0.01) + ((median_ar - 3.2) * 0.08))
        return {
            "type": "basmati",
            "confidence": round(float(confidence), 2),
            "scientific_label": "Oryza sativa L. (Basmati extra-long slender)",
            "notice": "Morphological slenderness ratio is consistent with certified Basmati grain standards (L/B >= 3.2).",
            "evidence": f"Measured median aspect ratio of {median_ar:.2f} satisfies extra-long slender Basmati morphological criteria."
        }

    # Medium aspect ratio: Sona Masuri candidate (Medium Slender)
    elif SONA_MASURI_MIN_ASPECT_RATIO <= median_ar <= SONA_MASURI_MAX_ASPECT_RATIO:
        confidence = 0.72  # Capped because benchmark datasets lack official verified Sona Masuri weights
        return {
            "type": "sona_masuri",
            "confidence": round(float(confidence), 2),
            "scientific_label": "Oryza sativa L. (Medium slender / BPT 5204 candidate)",
            "notice": "Sona Masuri classification requires additional verified labelled data. Identified provisionally based on medium-slender morphology.",
            "evidence": f"Measured median aspect ratio of {median_ar:.2f} aligns with medium-slender grain profiles (2.4 - 3.1)."
        }

    # Short / Bold grain: Other rice (Arborio, Ponni, IR64, short grain, etc.)
    elif median_ar < SHORT_GRAIN_MAX_ASPECT_RATIO:
        confidence = 0.85
        return {
            "type": "other_rice",
            "confidence": round(float(confidence), 2),
            "scientific_label": "Oryza sativa L. (Short / Bold / Round grain)",
            "notice": "Grain morphology indicates non-slender (short or bold) rice variety, unsuitable for traditional dum biryani.",
            "evidence": f"Measured median aspect ratio of {median_ar:.2f} indicates a short/plump grain rather than long-grain biryani rice."
        }

    # Ambiguous intermediate
    else:
        return {
            "type": "unknown",
            "confidence": 0.45,
            "scientific_label": "Undetermined Rice Variety",
            "notice": "Grain dimensions fall into an intermediate morphological band between slender and bold varieties.",
            "evidence": f"Aspect ratio {median_ar:.2f} is inconclusive without laboratory DNA or seed certification."
        }
