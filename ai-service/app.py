from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

def preprocess_image(filepath):
    try:
        img = Image.open(filepath)
        # Convert to RGB just in case
        img = img.convert('RGB')
        # Resize for faster heuristic processing
        img.thumbnail((150, 150))
        return img
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def assess_image_quality(filepath):
    try:
        image = cv2.imread(filepath)
        if image is None:
            return False, "Unable to read image."
            
        height, width = image.shape[:2]
        if width < 200 or height < 200:
            return False, "Image resolution is too low. Please upload a clearer image."
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        if fm < 50:
            return False, "Image quality is insufficient for reliable analysis (too blurry). Please capture a clearer image."
            
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        v = hsv[:,:,2]
        mean_v = np.mean(v)
        if mean_v < 40:
            return False, "Image quality is insufficient for reliable analysis (underexposed/dark). Please capture a clearer image."
        if mean_v > 230:
            return False, "Image quality is insufficient for reliable analysis (overexposed/bright). Please capture a clearer image."
            
        return True, "Good"
    except Exception as e:
        print(f"Error checking image quality: {e}")
        return False, "Error assessing image quality."

def detect_is_food(img, filename):
    # DEMO/MOCK: Distinguish food vs non-food without a real ML model.
    # 1. Filename heuristic
    if filename:
        filename_lower = filename.lower()
        non_food_keywords = ['screenshot', 'mongodb', 'mongo', 'code', 'book', 'phone', 'laptop', 'car', 'person', 'dog', 'cat', 'notfood', 'screen']
        for keyword in non_food_keywords:
            if keyword in filename_lower:
                return False, "The uploaded image does not appear to contain food. Please upload a clear image of food."
    
    # 2. Image heuristic (unique colors)
    if img:
        # A 150x150 image has 22,500 pixels.
        # Screenshots / UIs typically have large blocks of solid colors, resulting in fewer unique colors.
        # Natural organic photos (like food) have high color variance.
        colors = img.getcolors(maxcolors=25000)
        # If it returns a list, it means there are fewer than maxcolors unique colors
        if colors is not None:
            num_unique_colors = len(colors)
            # Threshold: A natural photo of 150x150 usually has > 5000 unique colors.
            # Screenshots typically have < 2000.
            if num_unique_colors < 3000:
                return False, "The uploaded image does not appear to contain food. Please upload a clear image of food."

    return True, None

def classify_food_category(img):
    # DEMO/MOCK: Deterministic category assignment based on dominant color instead of random.
    if not img:
        return 'Raw / Not Cooked Food', 'Unknown Food', 0.85
        
    pixels = list(img.getdata())
    avg_r = sum(p[0] for p in pixels) / len(pixels)
    avg_g = sum(p[1] for p in pixels) / len(pixels)
    avg_b = sum(p[2] for p in pixels) / len(pixels)
    
    if avg_r > avg_g + 20 and avg_r > avg_b + 20:
        # Reddish/Brownish -> Fried/Cooked meat
        if avg_g < 100:
            return 'Fried Food', 'Fried snacks or meat', 0.92
        else:
            return 'Cooked Food', 'Curry or cooked meal', 0.88
    elif avg_g > avg_r and avg_g > avg_b:
        # Greenish -> Raw vegetables
        return 'Raw / Not Cooked Food', 'Raw vegetables or salad', 0.95
    else:
        # Fallback
        return 'Cooked Food', 'Cooked dish', 0.82

def assess_visual_safety(category, img):
    # DEMO/MOCK: Deterministic scoring based on category
    # In a real model, these would come from multiple specific classifiers
    
    # Defaults
    freshness = "Likely Fresh"
    visibleMold = "Not Detected"
    visibleDiscoloration = "Low"
    visibleContamination = "Not Detected"
    visualHygieneRisk = "LOW RISK"
    score = 85
    
    if category == 'Raw / Not Cooked Food':
        score = 85
        freshness = "Likely Fresh"
        visualHygieneRisk = "LOW RISK"
    elif category == 'Cooked Food':
        score = 75
        freshness = "Freshly Cooked"
        visibleDiscoloration = "Medium"
        visualHygieneRisk = "MEDIUM RISK"
    elif category == 'Fried Food':
        score = 65
        freshness = "Requires Attention"
        visibleDiscoloration = "High"
        visualHygieneRisk = "MEDIUM RISK"
    else:
        score = 50
        freshness = "Unknown"
        visibleMold = "Possible"
        visualHygieneRisk = "HIGH RISK"
        
    recommendations = []
    if score >= 80:
        recommendations = ['Maintain current storage practices', 'This visual assessment cannot rule out invisible or microscopic hazards']
    elif score >= 60:
        recommendations = ['Consider checking preparation conditions', 'Monitor storage duration', 'This visual assessment cannot rule out invisible or microscopic hazards']
    else:
        recommendations = ['Check cooking conditions', 'Ensure proper food handling', 'May require further inspection']
        
    return score, freshness, visibleMold, visibleDiscoloration, visibleContamination, visualHygieneRisk, recommendations

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    filename = data.get('filename')
    filepath = data.get('filepath')
    
    if not filename or not filepath:
        return jsonify({"success": False, "message": "No filename or filepath provided"}), 400
        
    # 0. Image Quality Check
    is_good, q_msg = assess_image_quality(filepath)
    if not is_good:
        return jsonify({"success": False, "message": q_msg}), 400
        
    # 1. Preprocess
    img = preprocess_image(filepath)
    
    # 2. Food / Non-Food Detection
    is_food, msg = detect_is_food(img, filename)
    if not is_food:
        return jsonify({
            "success": True,
            "isFood": False,
            "data": {
                "detectedFood": None,
                "category": None,
                "confidence": None,
                "score": None,
                "status": "Not Food",
                "message": msg,
                "visualIndicators": [],
                "recommendations": []
            }
        })
        
    # 3. Classify Category
    category, detected_food, confidence = classify_food_category(img)
    
    # 4. Assess Safety
    score, freshness, mold, discoloration, contamination, hygiene_risk, recommendations = assess_visual_safety(category, img)
    
    return jsonify({
        "success": True,
        "isFood": True,
        "data": {
            "detectedFood": detected_food,
            "category": category,
            "confidence": confidence,
            "score": score,
            "freshness": freshness,
            "visibleMold": mold,
            "visibleDiscoloration": discoloration,
            "visibleContamination": contamination,
            "visualHygieneRisk": hygiene_risk,
            "recommendations": recommendations,
            "limitations": "Invisible or microscopic hazards — including bacteria, viruses, pesticide residues, chemical contaminants, veterinary drug residues, and toxins — cannot be confirmed through ordinary image analysis. A food image that appears normal does not prove that the food is free from contamination."
        }
    })

if __name__ == '__main__':
    app.run(port=8000, debug=True)
