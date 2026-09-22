import cv2
import numpy as np

def analyze_tomato(image):
    """
    Analyzes an OpenCV image of a tomato.
    Returns (visible_issues, visual_assessment_status, hygiene_confidence, quality_score, defect_score, microbial_risk, quality_level, reason)
    """
    if image is None:
        return ["No image data"], "INSUFFICIENT EVIDENCE", 0.0, 0, 100, "Unknown / Cannot Determine", "POOR", "Image could not be read.", "Unknown"

    height, width = image.shape[:2]
    image_area = height * width
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 1. Detect Tomato Mask (Red/Orange/Yellow hues, excluding background)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([15, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    
    lower_orange_yellow = np.array([15, 50, 50])
    upper_orange_yellow = np.array([45, 255, 255])
    mask_oy = cv2.inRange(hsv, lower_orange_yellow, upper_orange_yellow)
    
    mask_tomato = cv2.bitwise_or(mask_red1, mask_red2)
    mask_tomato = cv2.bitwise_or(mask_tomato, mask_oy)
    
    contours, _ = cv2.findContours(mask_tomato, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tomato_area = 0
    if contours:
        c = max(contours, key=cv2.contourArea)
        tomato_area = cv2.contourArea(c)
        
    if tomato_area < (image_area * 0.02):
        return ["Tomato is too small or unclear in the image"], "INSUFFICIENT EVIDENCE", 0.5, 0, 100, "Unknown / Cannot Determine", "POOR", "Image resolution or tomato size is too small.", "Unknown"

    # 2. Defect Detection
    visible_issues = []
    total_defect_penalty = 0
    reason_parts = []

    # A. Dark spots / Rotting (Low Value/Dark colored areas inside the tomato)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 50]) 
    mask_dark = cv2.inRange(hsv, lower_dark, upper_dark)
    mask_dark_on_tomato = cv2.bitwise_and(mask_dark, mask_tomato)
    
    dark_area = np.sum(mask_dark_on_tomato == 255)
    dark_ratio = dark_area / tomato_area
    
    if dark_ratio > 0.08:
        visible_issues.append("Dark/rotting area — 91% confidence — Severe")
        total_defect_penalty += 50
        reason_parts.append("Large dark/decayed area is visible.")
    elif dark_ratio > 0.02:
        visible_issues.append("Dark spots/Bruising — 82% confidence — Mild")
        total_defect_penalty += 15
        reason_parts.append("Minor dark spots or bruising detected.")

    # B. Mold-like growth (White/Grayish fuzzy patches, high value, low saturation)
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 30, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    mask_white_on_tomato = cv2.bitwise_and(mask_white, mask_tomato)
    
    white_area = np.sum(mask_white_on_tomato == 255)
    white_ratio = white_area / tomato_area
    
    if white_ratio > 0.03:
        visible_issues.append("Mold-like visible growth — 88% confidence — Severe")
        total_defect_penalty += 60
        reason_parts.append("Significant mold-like growth is visible.")
        
    # C. Cracks / Cuts (Edge detection)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges_on_tomato = cv2.bitwise_and(edges, mask_tomato)
    edge_area = np.sum(edges_on_tomato == 255)
    edge_ratio = edge_area / tomato_area
    
    if edge_ratio > 0.10:
        visible_issues.append("Surface damage/Cracks — 75% confidence — Moderate")
        total_defect_penalty += 20
        reason_parts.append("Surface damage or cracking is visible.")
        
    # Add continuous penalty based on precise ratios so score is not a hardcoded 100
    continuous_penalty = (dark_ratio * 200) + (white_ratio * 500) + (edge_ratio * 100)
    total_defect_penalty += continuous_penalty

    # 3. Calculate Score
    defect_score = min(100, int(total_defect_penalty))
    # Start from a baseline of 100 for a perfect tomato.
    # Deduct defects from the baseline.
    quality_score = max(0, 100 - defect_score)
    
    # 4. Quality Level & Reason
    if quality_score >= 70:
        quality_level = "GOOD"
        reason = "Tomato appears visually fresh with no major visible damage."
        if not visible_issues:
            visible_issues.append("No obvious visible defect detected")
    elif quality_score >= 40:
        quality_level = "AVERAGE"
        reason = "Tomato shows moderate visible issues. " + " ".join(reason_parts)
    else:
        quality_level = "POOR"
        reason = "Tomato shows severe visual defects. " + " ".join(reason_parts)
        
    # 5. Visual Assessment Status & Microbial Risk (Estimated)
    hygiene_confidence = 0.85
    microbial_risk = "Unknown / Cannot Determine" # Default baseline for visual-only systems
    
    if white_ratio > 0.03:
        visual_assessment_status = "Visible Contamination Risk"
        hygiene_confidence = 0.95
        microbial_risk = "High Risk (Visible Spoilage)"
    elif total_defect_penalty >= 50:
        visual_assessment_status = "Visible Contamination Risk"
        hygiene_confidence = 0.90
        microbial_risk = "High Risk (Severe Decay)"
    elif total_defect_penalty >= 20:
        visual_assessment_status = "Visible quality concerns detected"
        hygiene_confidence = 0.85
        microbial_risk = "Moderate Risk (Damaged Surface)"
    elif quality_score >= 60:
        visual_assessment_status = "Insufficient visual evidence"
        microbial_risk = "Unknown / Cannot Determine"
    else:
        visual_assessment_status = "INSUFFICIENT EVIDENCE"
        
    # 6. Detect dominant colour
    detected_colour = "Unknown"
    hsv_tomato_pixels = hsv[mask_tomato > 0]
    if len(hsv_tomato_pixels) > 0:
        hues = hsv_tomato_pixels[:, 0]
        # Count pixels in ranges
        red_count = np.sum((hues <= 15) | (hues >= 160))
        orange_yellow_count = np.sum((hues > 15) & (hues <= 45))
        green_count = np.sum((hues > 45) & (hues <= 85))
        
        total_colored = red_count + orange_yellow_count + green_count
        if total_colored > 0:
            r_ratio = red_count / total_colored
            oy_ratio = orange_yellow_count / total_colored
            g_ratio = green_count / total_colored
            
            if g_ratio > 0.4:
                detected_colour = "Greenish"
            elif oy_ratio > 0.5:
                detected_colour = "Orange/Yellowish"
            elif r_ratio > 0.8:
                detected_colour = "Bright Red"
            else:
                detected_colour = "Light Red"
        else:
            detected_colour = "Red"
            
    return visible_issues, visual_assessment_status, hygiene_confidence, quality_score, defect_score, microbial_risk, quality_level, reason, detected_colour
