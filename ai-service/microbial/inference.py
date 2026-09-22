def run_inference(model, image):
    """
    Runs the inference if a model exists.
    """
    if model is None:
        return {
            "result": "model_not_available",
            "confidence": 0.0,
            "detection_regions": []
        }
    
    # Placeholder for future inference
    return {
        "result": "inconclusive",
        "confidence": 0.0,
        "detection_regions": []
    }
