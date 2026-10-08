import cv2
import numpy as np
import logging
from .config import (
    MIN_IMAGE_WIDTH, MIN_IMAGE_HEIGHT, MIN_LAPLACIAN_VARIANCE,
    MIN_GRAINS_FOR_CONFIDENT_ASSESSMENT, MIN_RICE_PIXEL_RATIO,
    BROKEN_GRAIN_LENGTH_RATIO
)

logger = logging.getLogger(__name__)

def check_image_quality(cv_image):
    """
    Evaluates basic optical quality: resolution, blur (Laplacian variance), and exposure.
    """
    if cv_image is None or cv_image.size == 0:
        return False, "Invalid or empty image file."

    h, w = cv_image.shape[:2]
    if w < MIN_IMAGE_WIDTH or h < MIN_IMAGE_HEIGHT:
        return False, f"Image resolution too low ({w}x{h}). Minimum required is {MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}."

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    if lap_var < MIN_LAPLACIAN_VARIANCE:
        return False, f"Image is too blurry (sharpness score: {lap_var:.1f}). Please capture a sharper image."

    mean_brightness = np.mean(gray)
    if mean_brightness < 25:
        return False, "Image is underexposed / too dark. Please capture with better lighting."
    if mean_brightness > 245:
        return False, "Image is overexposed / too bright. Please reduce glare or direct flash."

    return True, "Quality check passed."

def segment_and_analyze_grains(cv_image):
    """
    Segments visible rice grains and computes measurable morphology.
    Returns individual and aggregate metrics in pixels and relative aspect ratios.
    
    IMPORTANT:
    Does NOT fabricate millimeter values without a physical calibration reference.
    """
    h, w = cv_image.shape[:2]
    total_area = h * w

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # Multi-cue rice detection:
    # 1. Intensity threshold for pale/white/golden grains
    # 2. HSV mask for rice hues (white, ivory, saffron-yellow, light golden)
    _, otsu_thresh = cv2.threshold(enhanced_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Mask for rice hues (raw white/cream or cooked biryani rice)
    # Brightness > 70, Saturation usually < 180 (avoids dark curries/meat)
    hsv_mask = cv2.inRange(hsv, np.array([0, 0, 60]), np.array([180, 180, 255]))

    # Combine cues
    combined_mask = cv2.bitwise_and(otsu_thresh, hsv_mask)

    # Morphological cleaning to separate slightly touching grains
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    rice_pixel_count = cv2.countNonZero(cleaned_mask)
    rice_ratio = rice_pixel_count / float(total_area)

    if rice_ratio < MIN_RICE_PIXEL_RATIO:
        return {
            "success": False,
            "rice_detected": False,
            "reason": "No prominent rice grains detected in image.",
            "metrics": None
        }

    # Find contours of candidate grains
    contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_grain_area = max(50.0, total_area * 0.0003)
    max_grain_area = total_area * 0.05

    grains = []
    lengths = []
    widths = []
    aspect_ratios = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_grain_area <= area <= max_grain_area:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter <= 0:
                continue

            rect = cv2.minAreaRect(cnt)
            (cx, cy), (dim1, dim2), angle = rect

            if dim1 == 0 or dim2 == 0:
                continue

            major_len = max(dim1, dim2)
            minor_wid = min(dim1, dim2)
            aspect_ratio = major_len / float(minor_wid)

            # Rice grains have an aspect ratio >= 1.3 and length >= 14px
            if 1.3 <= aspect_ratio <= 7.0 and major_len >= 14 and minor_wid >= 4:
                circularity = (4 * np.pi * area) / (perimeter * perimeter)
                grains.append({
                    "length_px": round(float(major_len), 1),
                    "width_px": round(float(minor_wid), 1),
                    "aspect_ratio": round(float(aspect_ratio), 2),
                    "area_px": round(float(area), 1),
                    "perimeter_px": round(float(perimeter), 1),
                    "circularity": round(float(circularity), 3)
                })
                lengths.append(major_len)
                widths.append(minor_wid)
                aspect_ratios.append(aspect_ratio)

    total_grains = len(grains)
    if total_grains < MIN_GRAINS_FOR_CONFIDENT_ASSESSMENT:
        # Check if it's really rice in bulk cluster (requires rice_ratio >= 0.15)
        if rice_ratio >= 0.15:
            return {
                "success": True,
                "rice_detected": True,
                "grain_segmentation_mode": "bulk_cluster",
                "segmented_grains_count": total_grains,
                "reason": "Individual grains are densely packed or clustered in cooked state. Evaluated via aggregate optical analysis.",
                "metrics": {
                    "median_length_px": None,
                    "median_width_px": None,
                    "median_aspect_ratio": None,
                    "mean_aspect_ratio": None,
                    "uniformity": "moderate",
                    "broken_grain_percentage": None,
                    "calibration_note": "Pixel and dimensionless ratio measurements. Calibration reference required for physical millimeters."
                }
            }
        else:
            return {
                "success": False,
                "rice_detected": False,
                "reason": "Insufficient visual evidence. No prominent rice grains could be resolved in the image.",
                "metrics": None
            }

    # Statistical evaluation of segmented grains
    median_length = float(np.median(lengths))
    median_width = float(np.median(widths))
    median_ar = float(np.median(aspect_ratios))
    mean_ar = float(np.mean(aspect_ratios))

    # Broken grain calculation: grains with length < 75% of median whole-grain length
    broken_count = sum(1 for l in lengths if l < (median_length * BROKEN_GRAIN_LENGTH_RATIO))
    broken_percentage = (broken_count / float(total_grains)) * 100.0

    # Uniformity calculation (based on Length Coefficient of Variation: CV = std / mean)
    std_length = float(np.std(lengths))
    mean_length = float(np.mean(lengths))
    cv_length = (std_length / mean_length) if mean_length > 0 else 1.0

    if cv_length < 0.18:
        uniformity = "high"
    elif cv_length < 0.32:
        uniformity = "medium"
    else:
        uniformity = "low"

    return {
        "success": True,
        "rice_detected": True,
        "grain_segmentation_mode": "individual_grains",
        "segmented_grains_count": total_grains,
        "metrics": {
            "median_length_px": round(median_length, 1),
            "median_width_px": round(median_width, 1),
            "median_aspect_ratio": round(median_ar, 2),
            "mean_aspect_ratio": round(mean_ar, 2),
            "uniformity": uniformity,
            "broken_grain_percentage": round(broken_percentage, 1),
            "calibration_note": "Pixel and dimensionless ratio measurements. Calibration reference required for physical millimeters."
        }
    }
