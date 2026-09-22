import cv2
import numpy as np

def validate_image_quality(image):
    """
    Validates the quality of a microscopic image using Laplacian variance (blur)
    and basic resolution checks.
    """
    if image is None:
        return False, "insufficient"
        
    height, width = image.shape[:2]
    if height < 100 or width < 100:
        return False, "insufficient"
        
    # Check for blur
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # 50 is an arbitrary threshold for microscopy
    if variance < 50:
        return False, "insufficient"
        
    return True, "acceptable"
