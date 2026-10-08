import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_biryani_visual_quality(cv_image):
    """
    Analyzes an OpenCV image of Biryani for visible appearance, presentation,
    and visible quality indicators.

    Strict Scientific Safety Compliance:
    - Analyzes visible RGB color distributions, texture, charred areas, and garnish.
    - NEVER fabricates bacterial, pathogen, chemical, or microbial counts.
    - Explicitly marks non-visible safety limitations.
    """
    if cv_image is None or cv_image.size == 0:
        return {
            "success": False,
            "message": "Invalid or empty image"
        }

    height, width = cv_image.shape[:2]
    total_pixels = height * width

    # Convert to HSV & RGB
    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

    # 1. Color Palette Analysis (Biryani typically features golden, saffron, yellow, orange and white rice grains)
    # Yellow/Orange hues (Hue: 10 - 35)
    mask_saffron = cv2.inRange(hsv, np.array([10, 50, 70]), np.array([35, 255, 255]))
    saffron_pixels = cv2.countNonZero(mask_saffron)
    saffron_ratio = saffron_pixels / float(total_pixels)

    # White/pale rice grains (Low saturation, moderate-to-high value)
    mask_white = cv2.inRange(hsv, np.array([0, 0, 160]), np.array([180, 50, 255]))
    white_pixels = cv2.countNonZero(mask_white)
    white_ratio = white_pixels / float(total_pixels)

    # Green herbs / garnish (mint/coriander leaves) (Hue: 35 - 85, Saturation > 50)
    mask_green = cv2.inRange(hsv, np.array([35, 50, 40]), np.array([85, 255, 220]))
    green_pixels = cv2.countNonZero(mask_green)
    green_ratio = green_pixels / float(total_pixels)

    # Dark / Burnt / Charred patches (Very low Value < 35, moderate to any Saturation)
    # Note: Fried onions (birista) are dark brown, but excessive black indicate scorching/burn.
    mask_charred = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 30]))
    charred_pixels = cv2.countNonZero(mask_charred)
    charred_ratio = charred_pixels / float(total_pixels)

    # Brown / Caramelized fried onions (birista) (Hue 8-25, Low-mid brightness)
    mask_brown = cv2.inRange(hsv, np.array([8, 60, 30]), np.array([25, 220, 120]))
    brown_pixels = cv2.countNonZero(mask_brown)
    brown_ratio = brown_pixels / float(total_pixels)

    # Visible issues detection
    visible_issues = []
    positive_indicators = []

    # Check for excessive scorching
    if charred_ratio > 0.08:
        visible_issues.append("Excessive scorched or charred areas detected on dish surface.")
    elif charred_ratio > 0.04:
        visible_issues.append("Moderate dark / over-browned areas observed.")

    # Check for grey/dull discoloration (desaturated midtones)
    mask_grey = cv2.inRange(hsv, np.array([0, 0, 60]), np.array([180, 25, 140]))
    grey_ratio = cv2.countNonZero(mask_grey) / float(total_pixels)
    if grey_ratio > 0.18:
        visible_issues.append("Dull or grayish tone observed in rice portions.")

    # Positive presentation indicators
    if saffron_ratio > 0.10:
        positive_indicators.append("Rich saffron and turmeric rice coloration visible.")
    if white_ratio > 0.08 and saffron_ratio > 0.05:
        positive_indicators.append("Distinct multi-toned rice grain separation (dum style) observed.")
    if green_ratio > 0.01:
        positive_indicators.append("Fresh herb garnish (mint/coriander) detected.")
    if brown_ratio > 0.03:
        positive_indicators.append("Caramelized fried onions (birista) visible.")

    # Quality scoring based on visible indicators
    # Base quality: 85
    base_score = 85.0
    defect_penalty = 0.0

    if charred_ratio > 0.08:
        defect_penalty += 35.0
    elif charred_ratio > 0.04:
        defect_penalty += 15.0

    if grey_ratio > 0.18:
        defect_penalty += 20.0

    # Bonus for appealing garnish & color balance
    bonus = 0.0
    if len(positive_indicators) >= 3:
        bonus += 10.0
    elif len(positive_indicators) >= 2:
        bonus += 5.0

    quality_score = min(100.0, max(20.0, base_score - defect_penalty + bonus))
    defect_score = min(100.0, max(0.0, defect_penalty))

    if quality_score >= 80.0:
        visual_status = "FRESH & APPETIZING"
        quality_level = "HIGH"
        reason = "Biryani demonstrates excellent visible grain quality, rich characteristic coloration, and appealing presentation."
    elif quality_score >= 60.0:
        visual_status = "ACCEPTABLE"
        quality_level = "MODERATE"
        reason = "Biryani shows acceptable visual characteristics with standard coloration and presentation."
    else:
        visual_status = "POOR VISIBLE QUALITY"
        quality_level = "LOW"
        reason = "Biryani exhibits noticeable visible defects such as excessive scorching or irregular discoloration."

    how_to_eat = [
        "Enjoy hot with cooling cucumber or mint raita.",
        "Pair with traditional Mirchi ka Salan or rich baghara baingan gravy.",
        "Accompany with sliced onions, fresh lemon wedges, and mint leaves.",
        "Ensure biryani has been held at safe hot-holding temperatures (above 60°C / 140°F) before consumption."
    ]

    limitations = (
        "Scientific Note: This assessment evaluates visible presentation and RGB optical characteristics only. "
        "Ordinary smartphone or camera photography cannot measure microbial count, bacterial species "
        "(e.g., Bacillus cereus, Salmonella), toxins, or internal chemical safety. "
        "Always practice standard food safety and temperature control."
    )

    return {
        "success": True,
        "visualAssessmentStatus": visual_status,
        "qualityScore": round(quality_score, 1),
        "defectScore": round(defect_score, 1),
        "qualityLevel": quality_level,
        "visibleIssues": visible_issues,
        "positiveIndicators": positive_indicators,
        "reason": reason,
        "howToEat": how_to_eat,
        "limitations": limitations,
        "metrics": {
            "saffron_ratio": round(saffron_ratio, 3),
            "white_rice_ratio": round(white_ratio, 3),
            "garnish_ratio": round(green_ratio, 3),
            "charred_ratio": round(charred_ratio, 3),
            "birista_ratio": round(brown_ratio, 3)
        }
    }
