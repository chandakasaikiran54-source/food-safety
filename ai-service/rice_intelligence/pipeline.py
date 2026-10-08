import cv2
import numpy as np
import io
from PIL import Image

from .config import DEFAULT_RICE_CONTRIBUTION_WEIGHT
from .morphology_engine import check_image_quality, segment_and_analyze_grains
from .color_engine import analyze_rice_color
from .variety_classifier import classify_rice_variety
from .quality_engine import assess_rice_quality
from .culinary_engine import evaluate_culinary_profile
from .nutrition_engine import get_rice_nutrition_profile
from .hygiene_engine import evaluate_visual_hygiene

def analyze_rice_image(image_input, rice_contribution_weight=None):
    """
    Main entrypoint for Rice Intelligence Analysis.
    Combines Computer Vision (grain segmentation, morphology, color) with
    Verified Food Science & Nutrition Knowledge.
    
    Accepts:
    - numpy ndarray (OpenCV BGR image)
    - bytes / bytearray (image file bytes)
    - PIL Image
    - file path (str or Path)
    
    Returns structured JSON strictly adhering to Phase 19 specification.
    """
    if rice_contribution_weight is None:
        rice_contribution_weight = DEFAULT_RICE_CONTRIBUTION_WEIGHT

    # 1. Decode to CV2 BGR image
    cv_img = None
    try:
        if isinstance(image_input, np.ndarray):
            cv_img = image_input
        elif isinstance(image_input, (bytes, bytearray)):
            nparr = np.frombuffer(image_input, np.uint8)
            cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_input, Image.Image):
            rgb = np.array(image_input.convert("RGB"))
            cv_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, str):
            cv_img = cv2.imread(image_input)
    except Exception as e:
        return {
            "success": False,
            "food": "biryani",
            "message": f"Error decoding image: {str(e)}",
            "rice": None
        }

    if cv_img is None or cv_img.size == 0:
        return {
            "success": False,
            "food": "biryani",
            "message": "Unable to read or decode image file.",
            "rice": None
        }

    # 2. Image Quality Check
    is_good, quality_msg = check_image_quality(cv_img)
    if not is_good:
        return {
            "success": False,
            "food": "biryani",
            "message": quality_msg,
            "rice": None
        }

    # 3. Grain Morphology & Segmentation
    morphology = segment_and_analyze_grains(cv_img)
    if not morphology.get("success", False) or not morphology.get("rice_detected", False):
        return {
            "success": True,
            "food": "biryani",
            "message": morphology.get("reason", "No prominent rice grains detected in image."),
            "rice": {
                "type": "unknown",
                "confidence": 0.0,
                "visual_characteristics": {
                    "grain_length": None,
                    "grain_width": None,
                    "aspect_ratio": None,
                    "uniformity": "insufficient_evidence",
                    "colour": "Undetermined",
                    "visible_discoloration": False
                },
                "quality": {
                    "indicator": "insufficient_evidence",
                    "broken_grains": None,
                    "foreign_material": False,
                    "abnormal_grains": False,
                    "reason": "Insufficient visual evidence to resolve grains."
                },
                "biryani_suitability": {
                    "rating": "insufficient_evidence",
                    "reason": "Grain evidence absent or obscured."
                },
                "culinary_profile": {
                    "expected_texture": "Unknown",
                    "grain_separation": "undetermined",
                    "aroma_potential": "Undetermined",
                    "taste_prediction": "Expected culinary profile only; taste cannot be determined from image."
                },
                "nutrition": {
                    "protein": None,
                    "carbohydrates": None,
                    "fat": None,
                    "fiber": None,
                    "minerals": {}
                },
                "glycemic_information": {
                    "gi": None,
                    "interpretation": "GI cannot be determined from ambiguous image.",
                    "limitations": "Individual metabolic response requires confirmed variety and portion context."
                },
                "hygiene_indicator": {
                    "rating": "Insufficient evidence",
                    "visible_concerns": ["Rice grains could not be clearly resolved."],
                    "limitations": "Image-based visual assessment only."
                }
            }
        }

    # 4. Color & Discoloration Analysis
    color_res = analyze_rice_color(cv_img)

    # 5. Rice Variety Identification
    variety_res = classify_rice_variety(morphology, color_res, cv_img=cv_img)

    # 6. Quality Assessment
    quality_res = assess_rice_quality(morphology, color_res)

    # 7. Biryani Culinary Profile
    culinary_res = evaluate_culinary_profile(variety_res, morphology, quality_res)

    # 8. Verified Nutrition & Glycemic Layer
    nutrition_res = get_rice_nutrition_profile(variety_res.get("type", "unknown"))

    # 9. Rice-Based Visual Hygiene Indicator
    hygiene_res = evaluate_visual_hygiene(morphology, color_res, quality_res)

    # 10. Compile Structured JSON adhering to Phase 19
    metrics = morphology.get("metrics") or {}
    
    # Grain length / width: Report in pixels or null (no physical calibration assumed)
    grain_length = metrics.get("median_length_px")
    grain_width = metrics.get("median_width_px")
    aspect_ratio = metrics.get("median_aspect_ratio")
    uniformity = metrics.get("uniformity", "medium")
    broken_grains = metrics.get("broken_grain_percentage")

    final_report = {
        "success": True,
        "food": "biryani",
        "module": "rice_intelligence",
        "rice_contribution_weight": rice_contribution_weight,
        "design_hypothesis_note": f"Rice quality contributes a configurable {int(rice_contribution_weight * 100)}% to the overall Biryani assessment design hypothesis.",

        "rice": {
            "type": variety_res.get("type", "unknown"),
            "confidence": variety_res.get("confidence", 0.0),
            "scientific_label": variety_res.get("scientific_label", ""),
            "variety_notice": variety_res.get("notice", ""),

            "visual_characteristics": {
                "grain_length_px": grain_length,
                "grain_width_px": grain_width,
                "aspect_ratio": aspect_ratio,
                "uniformity": uniformity,
                "colour": color_res.get("dominant_color", "Normal"),
                "brightness_score": color_res.get("brightness_score"),
                "visible_discoloration": color_res.get("visible_discoloration", False),
                "discoloration_details": color_res.get("discoloration_details", []),
                "calibration_note": "Dimensions reported in pixels and dimensionless aspect ratio. Millimeter values require a physical calibration target."
            },

            "quality": {
                "indicator": quality_res.get("indicator", "medium"),
                "broken_grains": broken_grains,
                "foreign_material": quality_res.get("foreign_material", False),
                "abnormal_grains": quality_res.get("abnormal_grains", False),
                "reason": quality_res.get("reason", "")
            },

            "biryani_suitability": {
                "rating": culinary_res["biryani_suitability"]["rating"],
                "reason": culinary_res["biryani_suitability"]["reason"]
            },

            "culinary_profile": {
                "expected_texture": culinary_res["culinary_profile"]["expected_texture"],
                "grain_separation": culinary_res["culinary_profile"]["grain_separation"],
                "aroma_potential": culinary_res["culinary_profile"]["aroma_potential"],
                "cooking_characteristics": culinary_res["culinary_profile"]["cooking_characteristics"],
                "taste_prediction": culinary_res["culinary_profile"]["taste_prediction"]
            },

            "nutrition": {
                "variety_referenced": nutrition_res["nutrition"].get("variety_referenced"),
                "basis": nutrition_res["nutrition"].get("basis"),
                "calories_kcal": nutrition_res["nutrition"].get("calories_kcal"),
                "protein_g": nutrition_res["nutrition"].get("protein_g"),
                "carbohydrates_g": nutrition_res["nutrition"].get("carbohydrates_g"),
                "fat_g": nutrition_res["nutrition"].get("fat_g"),
                "fiber_g": nutrition_res["nutrition"].get("fiber_g"),
                "minerals_mg": nutrition_res["nutrition"].get("minerals_mg", {}),
                "reference_note": nutrition_res["nutrition"].get("reference_note")
            },

            "glycemic_information": {
                "gi": nutrition_res["glycemic_information"].get("gi"),
                "gi_category": nutrition_res["glycemic_information"].get("gi_category"),
                "glycemic_load": nutrition_res["glycemic_information"].get("glycemic_load"),
                "amylose_context": nutrition_res["glycemic_information"].get("amylose_context"),
                "interpretation": nutrition_res["glycemic_information"].get("interpretation"),
                "cooking_factors": nutrition_res["glycemic_information"].get("cooking_factors"),
                "limitations": nutrition_res["glycemic_information"].get("limitations")
            },

            "hygiene_indicator": {
                "rating": hygiene_res.get("rating", "Good visible condition"),
                "visible_concerns": hygiene_res.get("visible_concerns", []),
                "limitations": hygiene_res.get("limitations", "Image-based visual assessment only.")
            }
        }
    }

    return final_report
