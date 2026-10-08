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

def preprocess_image(cv_image):
    try:
        if cv_image is None:
            return None
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

def assess_image_quality(image):
    try:
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

FOOD_HYGIENE_MODEL = None
def load_food_hygiene_model():
    global FOOD_HYGIENE_MODEL
    try:
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            import tensorflow as tf
            tflite = tf.lite
        logger.info("Loading Food Hygiene TFLite model...")
        FOOD_HYGIENE_MODEL = tflite.Interpreter(model_path="food_hygiene_model.tflite")
        FOOD_HYGIENE_MODEL.allocate_tensors()
        logger.info("Food Hygiene model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load Food Hygiene model: {e}")
        FOOD_HYGIENE_MODEL = None

FOOD_TYPE_MODEL = None
FOOD_TYPE_CLASSES = {}

def load_food_type_model():
    global FOOD_TYPE_MODEL, FOOD_TYPE_CLASSES
    try:
        try:
            import tflite_runtime.interpreter as tflite
        except ImportError:
            import tensorflow as tf
            tflite = tf.lite
        import json
        logger.info("Loading Food Type TFLite model...")
        FOOD_TYPE_MODEL = tflite.Interpreter(model_path="food_type_model.tflite")
        FOOD_TYPE_MODEL.allocate_tensors()
        with open("food_type_classes.json", "r") as f:
            FOOD_TYPE_CLASSES = json.load(f)
        logger.info("Food Type model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load Food Type model: {e}")
        FOOD_TYPE_MODEL = None

load_models()
load_food_hygiene_model()
load_food_type_model()

from food_analyzers.biryani_analyzer import analyze_biryani_visual_quality
from food_analyzers.biryani_adapter import run_biryani_identification
from microbial.microbial_detector import analyze_microbial_image

def get_food_type(cv_image):
    if not FOOD_TYPE_MODEL:
        return 'unknown', 0.0
    
    try:
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb_image, (224, 224))
        img_array = resized.astype(np.float32)
        img_array = (img_array / 127.5) - 1.0
        img_array = np.expand_dims(img_array, axis=0)
        
        input_details = FOOD_TYPE_MODEL.get_input_details()
        output_details = FOOD_TYPE_MODEL.get_output_details()
        
        FOOD_TYPE_MODEL.set_tensor(input_details[0]['index'], img_array)
        FOOD_TYPE_MODEL.invoke()
        
        output_data = FOOD_TYPE_MODEL.get_tensor(output_details[0]['index'])
        class_idx = np.argmax(output_data[0])
        confidence = float(output_data[0][class_idx])
        
        class_name = FOOD_TYPE_CLASSES.get(str(class_idx), "unknown")
        return class_name, confidence
    except Exception as e:
        logger.error(f"Error predicting food type: {e}")
        return 'unknown', 0.0

@app.route('/', methods=['GET'])
def index():
    return jsonify({"success": True, "message": "FoodSafe AI Service (Biryani Edition) is running"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"success": True, "service": "FoodSafe AI", "focus": "Biryani", "status": "running"})

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400
        
    file = request.files['image']
    filename = request.form.get('filename', getattr(file, 'filename', 'unknown'))
    
    logger.info(f"[AI Service - Biryani] Received analyze request for file: {filename}")
    
    file_bytes = file.read()
    
    logger.info(f"[AI Service - Biryani] Received analyze request for file: {filename} | size: {len(file_bytes)} bytes")
    
    # 0. Decode image once
    cv_image = cv2.imdecode(np.asarray(bytearray(file_bytes), dtype=np.uint8), cv2.IMREAD_COLOR)
    if cv_image is None:
        return jsonify({"success": False, "message": "Failed to read image"}), 400
        
    # 1. Image Quality Check
    is_good, q_msg = assess_image_quality(cv_image)
    if not is_good:
        return jsonify({"success": False, "message": q_msg}), 400
        
    # 2. Biryani Identification
    biryani_id_result = run_biryani_identification(cv_image)
    is_biryani = biryani_id_result.get("is_biryani", False)
    confidence = biryani_id_result.get("confidence", 0.0)
    detected_food = biryani_id_result.get("food", "other")
    
    if not is_biryani:
        msg = biryani_id_result.get("message", "Biryani not detected. Please upload a clear image of Biryani.")
        return jsonify({
            "success": True,
            "isFood": detected_food != "non_food",
            "data": {
                "foodName": "Not Biryani" if detected_food != "non_food" else "Non-Food",
                "foodConfidence": round(confidence, 2) if confidence else 0.0,
                "is_biryani": False,
                "message": msg
            }
        })
        
    # 3. Biryani Visual Quality & Food Safety Analysis
    logger.info(f"[AI Service - Biryani] cv_image shape: {cv_image.shape}")
    visual_analysis = analyze_biryani_visual_quality(cv_image)
    
    quality_score = visual_analysis.get("qualityScore", 85.0)
    defect_score = visual_analysis.get("defectScore", 0.0)
    visual_assessment_status = visual_analysis.get("visualAssessmentStatus", "FRESH & APPETIZING")
    quality_level = visual_analysis.get("qualityLevel", "HIGH")
    visible_issues = visual_analysis.get("visibleIssues", [])
    positive_indicators = visual_analysis.get("positiveIndicators", [])
    reason = visual_analysis.get("reason", "Biryani shows appealing visual characteristics.")
    how_to_eat = visual_analysis.get("howToEat", [])
    limitations = visual_analysis.get("limitations", "")
    
    logger.info(f"[AI Service - Biryani] Scores: quality={quality_score}, defect={defect_score}, status={visual_assessment_status}")
    
    return jsonify({
        "success": True,
        "isFood": True,
        "data": {
            "foodName": "Chicken Biryani",
            "foodConfidence": round(confidence, 2) if confidence else 0.95,
            "is_biryani": True,
            "visualAssessmentStatus": visual_assessment_status,
            "microbialSafetyRisk": "NOT_DETERMINABLE_FROM_RGB (See Scientific Disclaimer)",
            "hygieneConfidence": round(confidence, 2) if confidence else 0.95,
            "qualityScore": quality_score,
            "defectScore": defect_score,
            "qualityLevel": quality_level,
            "visibleIssues": visible_issues,
            "positiveIndicators": positive_indicators,
            "reason": reason,
            "customerAssessment": {
                "quality": None,
                "taste": None,
                "comment": None
            },
            "finalQualityScore": None,
            "assessmentDifference": None,
            "howToEat": how_to_eat,
            "limitations": limitations
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

def classify_raw_food(img, cv_image=None):
    if cv_image is not None:
        food_type, conf = get_food_type(cv_image)
        if food_type != 'unknown':
            return food_type.replace('_', ' ').title(), round(conf, 2)
            
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

def assess_raw_quality(image):
    try:
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
    
    cv_image = cv2.imdecode(np.asarray(bytearray(file_bytes), dtype=np.uint8), cv2.IMREAD_COLOR)
    if cv_image is None:
        return jsonify({"success": False, "message": "Failed to read image"}), 400
    
    # 0. Image Quality Check
    is_good, q_msg = assess_image_quality(cv_image)
    if not is_good:
        return jsonify({"success": False, "message": q_msg}), 400
        
    # 1. Preprocess
    img = preprocess_image(cv_image)
    if img is None:
        return jsonify({"success": False, "message": "Failed to process image"}), 400
    
    # 2. Food Identification
    food_name, food_confidence = classify_raw_food(img, cv_image)
    
    if food_name.lower() == 'non food':
        return jsonify({
            "success": True,
            "isFood": False,
            "data": {
                "foodName": "Unknown",
                "foodConfidence": food_confidence,
                "message": "Food Not Detected. Please upload a clear image of food."
            }
        })

    # 3. Quality Assessment
    if food_name.lower() == 'biryani':
        visual_analysis = analyze_biryani_visual_quality(cv_image)
        quality_status = visual_analysis.get("visualAssessmentStatus", "FRESH & APPETIZING")
        quality_confidence = food_confidence
        detected_indicators = visual_analysis.get("visibleIssues", [])
        explanation = visual_analysis.get("reason", "")
        visual_quality_score = visual_analysis.get("qualityScore", 85.0)
        defect_severity = "High" if visual_analysis.get("defectScore", 0) > 20 else "Low"
        defect_boxes = []
    else:
        # General freshness check (for Rice, Bread, etc.)
        # Using the new hygiene model if available, else fallback to openCV approach
        if FOOD_HYGIENE_MODEL:
            try:
                rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
                resized = cv2.resize(rgb_image, (224, 224))
                img_array = resized.astype(np.float32)
                img_array = (img_array / 127.5) - 1.0
                img_array = np.expand_dims(img_array, axis=0)
                
                input_details = FOOD_HYGIENE_MODEL.get_input_details()
                output_details = FOOD_HYGIENE_MODEL.get_output_details()
                
                FOOD_HYGIENE_MODEL.set_tensor(input_details[0]['index'], img_array)
                FOOD_HYGIENE_MODEL.invoke()
                
                output_data = FOOD_HYGIENE_MODEL.get_tensor(output_details[0]['index'])
                prediction_score = float(output_data[0][0])
                
                if prediction_score > 0.5:
                    quality_status = "VISIBLY SPOILED"
                    quality_confidence = prediction_score
                    detected_indicators = ["Visible spoilage or contamination detected"]
                    explanation = "The AI detected visual signs of spoilage or decay."
                    visual_quality_score = 1.0
                    defect_severity = "High"
                    defect_boxes = []
                else:
                    quality_status = "FRESH"
                    quality_confidence = 1.0 - prediction_score
                    detected_indicators = []
                    explanation = "Food appears fresh based on visual analysis."
                    visual_quality_score = 5.0
                    defect_severity = "Low"
                    defect_boxes = []
            except Exception as e:
                logger.error(f"Hygiene model error: {e}")
                quality_status, quality_confidence, detected_indicators, explanation, visual_quality_score, defect_severity, defect_boxes = assess_raw_quality(cv_image)
        else:
            quality_status, quality_confidence, detected_indicators, explanation, visual_quality_score, defect_severity, defect_boxes = assess_raw_quality(cv_image)
    
    return jsonify({
        "success": True,
        "isFood": True,
        "data": {
            "foodName": food_name,
            "foodConfidence": food_confidence,
            "qualityStatus": quality_status,
            "qualityConfidence": quality_confidence,
            "detectedVisualIndicators": detected_indicators,
            "explanation": explanation,
            "visualQualityScore": visual_quality_score,
            "defectSeverity": defect_severity,
            "defectBoxes": defect_boxes,
            "assessmentType": "VISUAL_AI_ASSESSMENT",
            "modelVersion": "ML-CV-Food-v3.0",
            "limitations": "Visual AI assessment cannot confirm microbial, chemical, pesticide, or complete food safety.",
            "defectScore": 10 if defect_severity == "High" else 0,
            "visualAssessmentStatus": quality_status
        }
    })

@app.route('/predict', methods=['POST'])
def predict_hygiene():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "message": "Empty filename"}), 400
        
    if not FOOD_HYGIENE_MODEL:
        return jsonify({"success": False, "message": "Food Hygiene model is not loaded."}), 500

    try:
        file_bytes = file.read()
        cv_image = cv2.imdecode(np.asarray(bytearray(file_bytes), dtype=np.uint8), cv2.IMREAD_COLOR)
        if cv_image is None:
            return jsonify({"success": False, "message": "Failed to read image"}), 400
            
        # Preprocess identically to training: 224x224, RGB, MobileNetV2 preprocess
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb_image, (224, 224))
        
        # We can either import tf for preprocess, or write it manually:
        # MobileNetV2 preprocess_input scales pixels to [-1, 1]
        img_array = resized.astype(np.float32)
        img_array = (img_array / 127.5) - 1.0
        img_array = np.expand_dims(img_array, axis=0)
        
        input_details = FOOD_HYGIENE_MODEL.get_input_details()
        output_details = FOOD_HYGIENE_MODEL.get_output_details()
        
        FOOD_HYGIENE_MODEL.set_tensor(input_details[0]['index'], img_array)
        FOOD_HYGIENE_MODEL.invoke()
        
        output_data = FOOD_HYGIENE_MODEL.get_tensor(output_details[0]['index'])
        prediction_score = float(output_data[0][0])
        
        # In our training: 0 = Hygienic, 1 = Not Hygienic
        # Wait, how were they mapped? flow_from_directory uses alphabetical order.
        # H comes before N. So Hygienic = 0, Not Hygienic = 1.
        # Sigmoid output > 0.5 means Not Hygienic.
        
        if prediction_score > 0.5:
            label = "Not Hygienic"
            confidence = prediction_score
        else:
            label = "Hygienic"
            confidence = 1.0 - prediction_score
            
        logger.info(f"Prediction: {label}, confidence: {confidence:.2f}, timestamp: {logging.Formatter('%(asctime)s').format(logging.LogRecord('', 0, '', 0, '', (), None))}")
        
        if confidence < 0.6:
            return jsonify({
                "result": "Uncertain, retake photo in better lighting",
                "confidence": confidence,
                "note": "Visual indicator only, not a lab test for pathogens"
            })
            
        return jsonify({
            "result": label,
            "confidence": confidence,
            "note": "Visual indicator only, not a lab test for pathogens"
        })
        
    except Exception as e:
        logger.error(f"Error in predict_hygiene: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------------------------------------
# Food Identification Endpoint (Isolated - First Food: Biryani)
# -------------------------------------------------------------
try:
    from food_analyzers.biryani_adapter import run_biryani_identification
except ImportError:
    run_biryani_identification = None

@app.route('/api/food-identification/biryani', methods=['POST'])
def api_identify_biryani():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400

    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({"success": False, "message": "Empty filename"}), 400

    try:
        file_bytes = file.read()
        if not run_biryani_identification:
            return jsonify({"success": False, "message": "Biryani identification adapter unavailable"}), 500

        result = run_biryani_identification(file_bytes)
        status_code = 200 if result.get("success", False) else (400 if not result.get("quality_passed", True) else 500)
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in api_identify_biryani: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------------------------------------
# Biryani 12-Class Regional Classifier Endpoint (Phase 25)
# -------------------------------------------------------------
try:
    import importlib.util
    from pathlib import Path
    _clf_file = Path(__file__).resolve().parent.parent / "ml" / "biryani" / "inference" / "biryani_classifier.py"
    _clf_spec = importlib.util.spec_from_file_location("regional_biryani_classifier", str(_clf_file))
    _clf_mod = importlib.util.module_from_spec(_clf_spec)
    _clf_spec.loader.exec_module(_clf_mod)
    biryani_classifier_engine = _clf_mod.BiryaniClassifier()
    logger.info("Successfully initialized 12-class BiryaniClassifier in Flask app.")
except Exception as e:
    logger.error(f"Could not initialize 12-class BiryaniClassifier: {e}")
    biryani_classifier_engine = None

@app.route('/api/biryani/classify', methods=['POST'])
def api_classify_biryani():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400

    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({"success": False, "message": "Empty filename"}), 400

    try:
        file_bytes = file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if cv_img is None:
            return jsonify({"success": False, "message": "Failed to decode image"}), 400

        # Assess basic quality
        quality_passed, quality_msg = assess_image_quality(cv_img)
        if not quality_passed:
            return jsonify({
                "success": False,
                "biryani_type": "Unknown",
                "confidence": 0.0,
                "evidence_quality": "low",
                "status": "poor_quality_image",
                "message": quality_msg
            }), 400

        # Optional Stage-1 Screening (Phase 22)
        is_biryani_confirmed = True
        if run_biryani_identification:
            try:
                screening = run_biryani_identification(cv_img)
                if screening.get("success") and not screening.get("is_biryani", True):
                    is_biryani_confirmed = False
            except Exception as e:
                logger.warning(f"Stage-1 screening skipped: {e}")

        # Stage-2: 12-Class Calibrated Regional Classification
        if biryani_classifier_engine:
            prediction_res = biryani_classifier_engine.predict(
                cv_img,
                is_confirmed_biryani=is_biryani_confirmed,
                generate_heatmap=True
            )
        else:
            prediction_res = {
                "biryani_type": "Unknown",
                "confidence": 0.0,
                "evidence_quality": "low",
                "status": "model_unavailable"
            }

        # Visible quality metrics from biryani_analyzer
        quality_analysis = {}
        try:
            from food_analyzers.biryani_analyzer import analyze_biryani_visual_quality
            quality_analysis = analyze_biryani_visual_quality(cv_img)
        except Exception as e:
            logger.warning(f"Visual quality analysis skipped: {e}")

        response_payload = {
            "success": True,
            **prediction_res,
            "visual_quality": quality_analysis
        }
        return jsonify(response_payload), 200

    except Exception as e:
        logger.error(f"Error in api_classify_biryani: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------------------------------------
# Rice Intelligence Endpoint (Biryani Rice Analysis)
# -------------------------------------------------------------
try:
    from rice_intelligence import analyze_rice_image
except ImportError as e:
    logger.error(f"Could not import rice_intelligence module: {e}")
    analyze_rice_image = None

@app.route('/api/rice-intelligence/analyze', methods=['POST'])
@app.route('/api/rice/analyze', methods=['POST'])
def api_rice_intelligence():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image provided"}), 400

    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({"success": False, "message": "Empty filename"}), 400

    try:
        if not analyze_rice_image:
            return jsonify({"success": False, "message": "Rice Intelligence module unavailable"}), 500

        file_bytes = file.read()
        weight_param = request.form.get('weight', None)
        weight = float(weight_param) if weight_param else None

        result = analyze_rice_image(file_bytes, rice_contribution_weight=weight)
        status_code = 200 if result.get("success", False) else 400
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Error in api_rice_intelligence: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True)

