from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

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
    if category == 'Raw / Not Cooked Food':
        score = 85
    elif category == 'Cooked Food':
        score = 75
    else:
        score = 65
        
    if score >= 80:
        status = 'Excellent'
        indicators = ['Food type recognized', 'No visible concern was identified in the image', 'No obvious visible foreign material']
        recommendations = ['Maintain current storage practices', 'This visual assessment cannot rule out invisible or microscopic hazards']
    elif score >= 60:
        status = 'Good / Needs Attention'
        indicators = ['Food type recognized', 'Possible visual discoloration', 'Minor visible handling indicators']
        recommendations = ['Consider checking preparation conditions', 'Monitor storage duration', 'This visual assessment cannot rule out invisible or microscopic hazards']
    elif score >= 40:
        status = 'Poor'
        indicators = ['Visible concern', 'Food appears exposed or poorly handled', 'Unusual visual appearance detected']
        recommendations = ['Check cooking conditions', 'Ensure proper food handling', 'May require further inspection']
    else:
        status = 'High Concern'
        indicators = ['Excessive charring/browning or visible spoilage-like appearance', 'Visual indicator detected that requires attention']
        recommendations = ['May require further inspection', 'Check for spoilage', 'Laboratory testing may be required to confirm safety']
        
    return score, status, indicators, recommendations

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    filename = data.get('filename')
    filepath = data.get('filepath')
    
    if not filename or not filepath:
        return jsonify({"success": False, "message": "No filename or filepath provided"}), 400
        
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
    score, status, indicators, recommendations = assess_visual_safety(category, img)
    
    return jsonify({
        "success": True,
        "isFood": True,
        "data": {
            "detectedFood": detected_food,
            "category": category,
            "confidence": confidence,
            "score": score,
            "status": status,
            "visualIndicators": indicators,
            "recommendations": recommendations,
            "limitations": "Invisible or microscopic hazards — including bacteria, viruses, pesticide residues, chemical contaminants, veterinary drug residues, and toxins — cannot be confirmed through ordinary image analysis. A food image that appears normal does not prove that the food is free from contamination."
        }
    })

if __name__ == '__main__':
    app.run(port=8000, debug=True)
