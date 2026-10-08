"""
Image preprocessing and data augmentation pipeline for Rice Classification.
Includes image quality diagnostics and standard TorchVision transforms.
"""

import cv2
import numpy as np
from PIL import Image
import torchvision.transforms as transforms

def get_train_transforms(image_size=224, norm_mean=None, norm_std=None):
    if norm_mean is None:
        norm_mean = [0.485, 0.456, 0.406]
    if norm_std is None:
        norm_std = [0.229, 0.224, 0.225]
        
    return transforms.Compose([
        transforms.Resize((int(image_size * 1.15), int(image_size * 1.15))),
        transforms.RandomCrop(image_size),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=180),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=norm_mean, std=norm_std)
    ])

def get_eval_transforms(image_size=224, norm_mean=None, norm_std=None):
    if norm_mean is None:
        norm_mean = [0.485, 0.456, 0.406]
    if norm_std is None:
        norm_std = [0.229, 0.224, 0.225]
        
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=norm_mean, std=norm_std)
    ])

def assess_image_quality(cv_image):
    """
    Checks whether an input image meets minimum computer-vision standards:
    - Min resolution: 180x180
    - Sharpness: Laplacian variance >= 18
    - Lighting: Average HSV value between 25 and 245
    """
    if cv_image is None or cv_image.size == 0:
        return False, "Failed to read image data.", {}
        
    h, w = cv_image.shape[:2]
    if h < 180 or w < 180:
        return False, f"Image resolution ({w}x{h}) is too low for reliable grain inspection.", {"width": w, "height": h}
        
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    if fm < 18.0:
        return False, f"Image is blurry (sharpness score: {fm:.1f} < 18.0). Please provide a sharper photo.", {"sharpness": fm}
        
    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    brightness = float(np.mean(hsv[:, :, 2]))
    if brightness < 25.0:
        return False, f"Image is too dark (brightness: {brightness:.1f}). Ensure adequate lighting.", {"brightness": brightness}
    if brightness > 245.0:
        return False, f"Image is overexposed (brightness: {brightness:.1f}). Avoid glare and overexposure.", {"brightness": brightness}
        
    return True, "Quality check passed.", {"width": w, "height": h, "sharpness": round(fm, 1), "brightness": round(brightness, 1)}

def to_pil_image(image_input):
    """Converts numpy BGR image or file path to PIL RGB Image."""
    if isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    elif isinstance(image_input, np.ndarray):
        rgb = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
    elif isinstance(image_input, str):
        return Image.open(image_input).convert("RGB")
    else:
        raise ValueError("Unsupported input format for PIL conversion.")
