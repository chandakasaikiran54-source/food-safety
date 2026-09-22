import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json
import os

CONFIDENCE_THRESHOLD = float(os.environ.get("DISEASE_CONFIDENCE_THRESHOLD", "0.50"))

def get_transforms():
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        normalize,
    ])

def load_class_mapping(model_name):
    with open(f"models/{model_name}/class_names.json", "r") as f:
        mapping = json.load(f)
    return mapping

def format_prediction(class_name):
    import re
    # Convert things like "Tomato___Bacterial_spot" or "Tomato_Bacterial_spot"
    # to "Tomato bacterial spot"
    clean_name = re.sub(r'_+', ' ', class_name).strip()
    
    if clean_name.lower().endswith("healthy"):
        return clean_name
    
    if not clean_name.lower().endswith("disease"):
        # Make the rest lowercase except the first word
        parts = clean_name.split(' ', 1)
        if len(parts) == 2:
            clean_name = f"{parts[0]} {parts[1].lower()}"
        return f"{clean_name} disease"
    return clean_name

def predict_image(model, model_name, image_path, class_mapping):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    
    transform = get_transforms()
    
    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        return {"error": str(e)}
        
    input_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)
        
    predicted_idx = str(predicted_idx.item())
    confidence = confidence.item()
    
    predicted_class_raw = class_mapping.get(predicted_idx, "Unknown")
    
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "model": model_name,
            "predicted_class": "LOW_CONFIDENCE",
            "confidence": round(confidence, 4)
        }
        
    formatted_class = format_prediction(predicted_class_raw)
    
    return {
        "model": model_name,
        "predicted_class": formatted_class,
        "raw_class": predicted_class_raw,
        "confidence": round(confidence, 4)
    }

def predict_resnet(image_path):
    class_mapping = load_class_mapping("resnet18")
    num_classes = len(class_mapping)
    
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load("models/resnet18/best_model.pth", map_location=device, weights_only=True))
    
    return predict_image(model, "ResNet18", image_path, class_mapping)

def predict_mobilenet(image_path):
    class_mapping = load_class_mapping("mobilenetv3")
    num_classes = len(class_mapping)
    
    model = models.mobilenet_v3_large(weights=None)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load("models/mobilenetv3/best_model.pth", map_location=device, weights_only=True))
    
    return predict_image(model, "MobileNetV3-Large", image_path, class_mapping)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        print("ResNet18:", predict_resnet(img_path))
        print("MobileNetV3:", predict_mobilenet(img_path))
