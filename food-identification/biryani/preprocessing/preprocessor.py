import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms

def get_train_transforms(image_size=(224, 224)):
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

def get_inference_transforms(image_size=(224, 224)):
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

def assess_image_quality(cv_image):
    """
    Validates image resolution, sharpness, and illumination.
    Returns: (is_good: bool, reason: str, metrics: dict)
    """
    if cv_image is None or not isinstance(cv_image, np.ndarray):
        return False, "Unable to read image or invalid image array.", {}

    height, width = cv_image.shape[:2]
    if width < 150 or height < 150:
        return False, f"Image resolution too low ({width}x{height}). Minimum required is 150x150.", {"width": width, "height": height}

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < 15.0:
        return False, "Image is too blurry. Please upload a sharper image.", {"blur_variance": laplacian_var}

    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    brightness = float(np.mean(hsv[:, :, 2]))
    if brightness < 25.0:
        return False, "Image is too dark. Please upload with better lighting.", {"brightness": brightness}
    if brightness > 245.0:
        return False, "Image is severely overexposed.", {"brightness": brightness}

    return True, "Quality check passed.", {
        "width": width,
        "height": height,
        "blur_variance": laplacian_var,
        "brightness": brightness
    }

def to_pil_image(image_input):
    """Convert file path, bytes, numpy array, or PIL image into RGB PIL Image."""
    if isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    elif isinstance(image_input, np.ndarray):
        if len(image_input.shape) == 2:
            return Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_GRAY2RGB))
        return Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
    elif isinstance(image_input, str):
        return Image.open(image_input).convert("RGB")
    elif isinstance(image_input, (bytes, bytearray)):
        import io
        return Image.open(io.BytesIO(image_input)).convert("RGB")
    else:
        raise ValueError(f"Unsupported image type: {type(image_input)}")
