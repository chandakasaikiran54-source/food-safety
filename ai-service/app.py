from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import cv2
import numpy as np
import logging
import io
import torch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def preprocess_image(file_stream):
    try:
        file_stream.seek(0)
        img = Image.open(file_stream)
        img = img.convert('RGB')
        return img
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

def assess_image_quality(file_stream):
    try:
        file_stream.seek(0)
        file_bytes = np.asarray(bytearray(file_stream.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return False, "Unable to read image."
            
        height, width = image.shape[:2]
        if width < 200 or height < 200:
            return False, "Image resolution is too low. Please upload a clearer image."
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        if fm < 20: 
            return False, "Image quality is POOR (too blurry). Please capture a clearer image."
            
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        v = hsv[:,:,2]
        mean_v = np.mean(v)
        if mean_v < 30:
            return False, "Image quality is POOR (too dark). Please capture a clearer image in better lighting."
        if mean_v > 240:
            return False, "Image quality is POOR (too bright/overexposed). Please capture a clearer image."
            
        return True, "Good"
    except Exception as e:
        logger.error(f"Error checking image quality: {e}")
        return False, "Error assessing image quality."

FOOD_CLASSIFIER = None

def load_models():
    global FOOD_CLASSIFIER
    try:
        from transformers import pipeline
        logger.info("Loading zero-shot classification model...")
        device = 0 if torch.cuda.is_available() else -1
        FOOD_CLASSIFIER = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32", device=device)
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load transformers model: {e}")
        FOOD_CLASSIFIER = None

load_models()

from food_analyzers.tomato import analyze_tomato
from microbial.microbial_detector import analyze_microbial_image
try:
    from disease_recognition.predict import predict_resnet, predict_mobilenet
except ImportError:
    logger.warning("Could not import disease_recognition. Models might not be trained yet.")
    predict_resnet = None
    predict_mobilenet = None

def detect_is_tomato(img):
    if FOOD_CLASSIFIER is None:
        return False, "FoodSafe AI could not initialize the validation model.", 0.0
    try:
        # Check if it's a tomato vs other common things
        candidate_labels = ["a photo of a tomato", "a photo of a fruit or vegetable", "a photo of a person", "a photo of a random object", "a photo of an empty plate"]
        results = FOOD_CLASSIFIER(img, candidate_labels=candidate_labels)
        
        # results is a list of dicts with 'label' and 'score'
        top_label = results[0]['label']
        top_score = results[0]['score']
        
        if top_label == "a photo of a tomato":
            if top_score > 0.4:
                return True, None, top_score
            else:
                return False, "Confidence too low.", top_score
        
        # If it's not a tomato, return false
        return False, "Tomato not detected. Please upload a clear tomato image.", top_score
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return False, "Error during tomato validation.", 0.0

def detect_is_leaf(img):
    if FOOD_CLASSIFIER is None:
        return False, "FoodSafe AI could not initialize the validation model."
    try:
        candidate_labels = ["a photo of a tomato leaf", "a photo of a tomato fruit", "a photo of a person", "a photo of a random object"]
        results = FOOD_CLASSIFIER(img, candidate_labels=candidate_labels)
        top_label = results[0]['label']
        top_score = results[0]['score']
        
        if top_label == "a photo of a tomato leaf" and top_score > 0.3:
            return True, None
        return False, "Plant disease model requires a compatible plant/leaf image."
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return False, "Error during leaf validation."

@app.route('/', methods=['GET'])
def index():
    return jsonify({"success": True, "message": "FoodSafe AI Service is running"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"success": True, "service": "FoodSafe AI", "status": "running"})

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400
        
    file = request.files['image']
    filename = request.form.get('filename', getattr(file, 'filename', 'unknown'))
    
    logger.info(f"[AI Service] Received analyze request for file: {filename}")
    
    file_bytes = file.read()
    file_stream = io.BytesIO(file_bytes)
    
    # 0. Image Quality Check
    is_good, q_msg = assess_image_quality(file_stream)
    if not is_good:
        return jsonify({"success": False, "message": q_msg}), 400
        
    # 1. Preprocess
    img = preprocess_image(file_stream)
    if img is None:
        return jsonify({"success": False, "message": "Failed to process image"}), 400
    
    # 2. Detect if Tomato
    is_tomato, msg, confidence = detect_is_tomato(img)
    if not is_tomato:
        return jsonify({
            "success": True,
            "isFood": False,
            "data": {
                "foodName": "Uncertain",
                "foodConfidence": round(confidence, 2) if confidence else 0.0,
                "message": msg
            }
        })
        
    # 3. Analyze Tomato Defects using OpenCV
    file_stream.seek(0)
    cv_image = cv2.imdecode(np.asarray(bytearray(file_stream.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
    visible_issues, visual_assessment_status, hygiene_confidence, quality_score, defect_score, microbial_risk, quality_level, reason, detected_colour = analyze_tomato(cv_image)
    
    return jsonify({
        "success": True,
        "isFood": True,
        "data": {
            "foodName": "Tomato",
            "foodConfidence": round(confidence, 2) if confidence else 0.95,
            "visualAssessmentStatus": visual_assessment_status,
            "microbialSafetyRisk": microbial_risk,
            "hygieneConfidence": hygiene_confidence,
            "qualityScore": quality_score,
            "defectScore": defect_score,
            "qualityLevel": quality_level,
            "visibleIssues": visible_issues,
            "reason": reason,
            "detectedColour": detected_colour,
            "customerAssessment": {
                "quality": None,
                "taste": None,
                "comment": None
            },
            "finalQualityScore": None,
            "assessmentDifference": None,
            "howToEat": [
                "Raw in salads",
                "Sliced with meals",
                "Used in curries",
                "Used in sauces",
                "Used in sandwiches"
            ],
            "limitations": "This AI performs visual food-quality analysis. It cannot directly detect bacteria, viruses, toxins, pesticides, or other microscopic/chemical contaminants. Visual appearance does not guarantee microbiological safety."
        }
    })
# -------------------------------------------------------------
# Microbial Analysis Endpoint
# -------------------------------------------------------------
@app.route('/microbial-analyze', methods=['POST'])
def microbial_analyze():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "message": "Empty filename"}), 400

    try:
        # Load image via OpenCV
        file.seek(0)
        cv_image = cv2.imdecode(np.asarray(bytearray(file.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
        
        # Analyze
        result = analyze_microbial_image(cv_image)
        
        return jsonify({
            "success": True,
            "analysis_type": "microscopic_microbial_analysis",
            "result": result["result"],
            "confidence": result["confidence"],
            "model_version": result["model_version"],
            "image_quality": result["image_quality"],
            "detection_regions": result["detection_regions"]
        })
    except Exception as e:
        logger.error(f"Error in microbial_analyze: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

def classify_raw_food(img):
    if FOOD_CLASSIFIER is None:
        return 'Unknown', 0.0
    try:
        results = FOOD_CLASSIFIER(img, top_k=1)
        top = results[0]
        if top['score'] > 0.4:
            return top['label'].replace('_', ' ').title(), round(top['score'], 2)
        return 'Unknown', 0.0
    except Exception as e:
        logger.error(f"Error in classify_raw_food: {e}")
        return 'Unknown', 0.0

def assess_raw_quality(file_stream):
    try:
        file_stream.seek(0)
        file_bytes = np.asarray(bytearray(file_stream.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return "INSUFFICIENT EVIDENCE", 0.0, [], "Could not read image.", 3.0, "Low", []
            
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_brown = np.array([10, 20, 20])
        upper_brown = np.array([30, 255, 200])
        mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
        
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 30])
        mask_black = cv2.inRange(hsv, lower_black, upper_black)
        
        mask_combined = cv2.bitwise_or(mask_brown, mask_black)
        contours, _ = cv2.findContours(mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_defect_area = 0
        defect_boxes = []
        image_area = image.shape[0] * image.shape[1]
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > (image_area * 0.005): 
                total_defect_area += area
                x, y, w, h = cv2.boundingRect(cnt)
                defect_boxes.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})
        
        defect_ratio = total_defect_area / image_area
        
        indicators = []
        status = "FRESH"
        visual_quality_score = 5.0
        defect_severity = "None"
        explanation = "Food appears to be in good condition based on visual analysis."
        
        if defect_ratio > 0.15:
            status = "VISIBLY SPOILED"
            indicators = ["Extensive discoloration or spotting detected", "Significant damaged areas"]
            visual_quality_score = 1.0
            defect_severity = "High"
            explanation = "Extensive surface defects, discoloration, or potential rot detected covering a significant area."
        elif defect_ratio > 0.05:
            status = "POOR"
            indicators = ["Multiple bruised or discolored areas"]
            visual_quality_score = 2.5
            defect_severity = "Medium"
            explanation = "Moderate surface defects or bruising detected."
        elif defect_ratio > 0.01:
            status = "ACCEPTABLE"
            indicators = ["Minor surface imperfections or small spots"]
            visual_quality_score = 4.0
            defect_severity = "Low"
            explanation = "Minor surface imperfections detected, generally acceptable."
            
        return status, 0.85, indicators, explanation, visual_quality_score, defect_severity, defect_boxes
        
    except Exception as e:
        logger.error(f"Error in assess_raw_quality: {e}")
        return "INSUFFICIENT EVIDENCE", 0.0, [], "Error processing image for quality.", 3.0, "Low", []

@app.route('/raw-analyze', methods=['POST'])
def raw_analyze():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400
        
    file = request.files['image']
    filename = request.form.get('filename', getattr(file, 'filename', 'unknown'))
    
    logger.info(f"[AI Service - Raw] Received analyze request for file: {filename}")
    
    file_bytes = file.read()
    file_stream = io.BytesIO(file_bytes)
    
    # 0. Image Quality Check
    is_good, q_msg = assess_image_quality(file_stream)
    if not is_good:
        return jsonify({"success": False, "message": q_msg}), 400
        
    # 1. Preprocess
    img = preprocess_image(file_stream)
    
    # 2. Food Identification
    food_name, food_confidence = classify_raw_food(img)
    
    # 3. Quality Assessment
    quality_status, quality_confidence, detected_indicators, explanation, visual_quality_score, defect_severity, defect_boxes = assess_raw_quality(file_stream)
    
    return jsonify({
        "success": True,
        "foodName": food_name,
        "foodConfidence": food_confidence,
        "qualityStatus": quality_status,
        "qualityConfidence": quality_confidence,
        "detectedVisualIndicators": detected_indicators,
        "microbialAssessment": {
            "status": "NOT_DETERMINABLE_FROM_RGB",
            "confidence": None
        },
        "explanation": explanation,
        "visualQualityScore": visual_quality_score,
        "defectSeverity": defect_severity,
        "defectBoxes": defect_boxes,
        "assessmentType": "VISUAL_AI_ASSESSMENT",
        "modelVersion": "ML-CV-Food-v3.0",
        "limitations": "Visual AI assessment cannot confirm microbial, chemical, pesticide, or complete food safety."
    })

# -------------------------------------------------------------
# Disease Analysis Endpoint
# -------------------------------------------------------------
@app.route('/api/disease/analyze', methods=['POST'])
def disease_analyze():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "message": "Empty filename"}), 400
        
    if not predict_resnet or not predict_mobilenet:
         return jsonify({"success": False, "message": "Disease recognition models are not loaded or trained yet."}), 500

    try:
        file_bytes = file.read()
        file.seek(0) # Reset pointer to save it later
        file_stream = io.BytesIO(file_bytes)
        
        img = preprocess_image(file_stream)
        if img is None:
            return jsonify({"success": False, "message": "Failed to process image"}), 400
            
        is_leaf, msg = detect_is_leaf(img)
        if not is_leaf:
            return jsonify({
                "success": True,
                "is_compatible": False,
                "message": msg
            })
            
        # Save temporarily
        temp_path = f"temp_{file.filename}"
        file.save(temp_path)
        
        # Analyze
        res_resnet = predict_resnet(temp_path)
        res_mobilenet = predict_mobilenet(temp_path)
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if "error" in res_resnet:
            return jsonify({"success": False, "message": res_resnet["error"]}), 500
            
        return jsonify({
            "success": True,
            "is_compatible": True,
            "resnet18": {
                "predicted_class": res_resnet["predicted_class"],
                "confidence": res_resnet["confidence"]
            },
            "mobilenetv3": {
                "predicted_class": res_mobilenet["predicted_class"],
                "confidence": res_mobilenet["confidence"]
            }
        })
    except Exception as e:
        logger.error(f"Error in disease_analyze: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True)
