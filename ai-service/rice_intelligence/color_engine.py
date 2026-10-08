import cv2
import numpy as np

def analyze_rice_color(cv_image):
    """
    Performs color space analysis across RGB, HSV, and CIELAB.
    Detects dominant color, lightness, color uniformity, and visible discoloration.

    SCIENTIFIC SAFETY:
    Discoloration is reported as optical variance or visible spots,
    NEVER as 'chemical contamination', 'pathogen', or 'pesticide'.
    """
    if cv_image is None or cv_image.size == 0:
        return {
            "dominant_color": "unknown",
            "brightness": None,
            "color_uniformity": "insufficient evidence",
            "visible_discoloration": False,
            "discoloration_details": []
        }

    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
    total_pixels = cv_image.shape[0] * cv_image.shape[1]

    # CIELAB channels: L* (0..255 in OpenCV), a* (green-red), b* (blue-yellow)
    l_channel = lab[:, :, 0]
    mean_l = float(np.mean(l_channel))
    std_l = float(np.std(l_channel))

    # Brightness in HSV (V channel: 0..255)
    v_channel = hsv[:, :, 2]
    mean_v = float(np.mean(v_channel))

    # Saturation (S channel: 0..255)
    s_channel = hsv[:, :, 1]
    mean_s = float(np.mean(s_channel))

    # Detect dominant visual tone
    if mean_s < 35 and mean_v > 180:
        dominant_color = "Pearly White / Polished Raw"
    elif mean_s < 55 and mean_v > 150:
        dominant_color = "Ivory / Translucent Cream"
    elif mean_s >= 55 and mean_v > 130:
        dominant_color = "Golden / Saffron Tinted (Cooked Dum Style or Parboiled)"
    else:
        dominant_color = "Muted / Dull Grain Tone"

    # Color uniformity
    if std_l < 22:
        color_uniformity = "high"
    elif std_l < 38:
        color_uniformity = "medium"
    else:
        color_uniformity = "low"

    # Visible discoloration detection:
    # 1. Dark/blackish spots (V < 40)
    dark_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 40]))
    dark_pixels = cv2.countNonZero(dark_mask)
    dark_ratio = dark_pixels / float(total_pixels)

    # 2. Abnormal dull gray/brown spots in predominantly white rice
    dull_mask = cv2.inRange(hsv, np.array([10, 30, 40]), np.array([30, 180, 100]))
    dull_pixels = cv2.countNonZero(dull_mask)
    dull_ratio = dull_pixels / float(total_pixels)

    discoloration_details = []
    visible_discoloration = False

    if dark_ratio > 0.03:
        visible_discoloration = True
        discoloration_details.append("Visible dark speckles or surface spotting detected.")
    
    if dull_ratio > 0.08 and mean_s < 45:
        visible_discoloration = True
        discoloration_details.append("Noticeable localized brownish or dull discoloration observed.")

    return {
        "dominant_color": dominant_color,
        "brightness_score": round(mean_v / 2.55, 1), # 0-100 scale
        "cielab_lightness": round(mean_l, 1),
        "color_uniformity": color_uniformity,
        "visible_discoloration": visible_discoloration,
        "discoloration_details": discoloration_details
    }
