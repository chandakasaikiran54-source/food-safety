from .preprocessing import validate_image_quality
from .model_loader import load_microbial_model
from .inference import run_inference

def analyze_microbial_image(image):
    """
    Main entry point for microscopic microbial analysis.
    """
    # 1. Image Quality Validation
    is_valid, quality_status = validate_image_quality(image)
    if not is_valid:
        return {
            "result": "image_quality_insufficient",
            "confidence": 0.0,
            "model_version": "Not Validated",
            "image_quality": quality_status,
            "detection_regions": []
        }
        
    # 2. Load Model
    model = load_microbial_model()
    
    # 3. Inference
    inference_data = run_inference(model, image)
    
    return {
        "result": inference_data["result"],
        "confidence": inference_data["confidence"],
        "model_version": "Not Validated",
        "image_quality": quality_status,
        "detection_regions": inference_data["detection_regions"]
    }
