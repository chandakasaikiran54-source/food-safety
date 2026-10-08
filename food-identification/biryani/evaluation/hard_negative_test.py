import os
import sys
import json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.biryani_inference import BiryaniInferenceEngine

def run_hard_negative_tests():
    """
    Evaluates the Biryani identification model against difficult negative cases:
    - Blurry and low-light images (tests quality gate)
    - Various non-biryani foods (curries, breads, vegetables, mixed plates)
    - Confirms false positive resistance (preventing non-biryani -> biryani)
    """
    engine = BiryaniInferenceEngine()
    if engine.model is None:
        print("[Hard Negative Test] Error: Biryani model could not be loaded.")
        return

    test_dir = BASE_DIR / "dataset" / "test"
    not_biryani_test_dir = test_dir / "not_biryani"

    results = {
        "quality_gate_tests": [],
        "hard_negatives": [],
        "summary": {}
    }

    print("\n========== HARD NEGATIVE & EDGE CASE EVALUATION ==========")
    
    # 1. Test Quality Gate: Intentionally Blurry Image
    blurry_img = np.random.randint(50, 200, (300, 300, 3), dtype=np.uint8)
    blurry_img = cv2.GaussianBlur(blurry_img, (45, 45), 0)
    res_blur = engine.predict(blurry_img)
    results["quality_gate_tests"].append({
        "case": "Severely Blurry Image",
        "expected_quality_pass": False,
        "actual_result": res_blur
    })
    print(f"[Blur Test] Passed quality check? {res_blur.get('quality_passed')} | Message: {res_blur.get('message')}")

    # 2. Test Quality Gate: Low-light / Underexposed Image
    dark_img = np.full((300, 300, 3), 15, dtype=np.uint8)
    res_dark = engine.predict(dark_img)
    results["quality_gate_tests"].append({
        "case": "Severely Dark Image",
        "expected_quality_pass": False,
        "actual_result": res_dark
    })
    print(f"[Dark Test] Passed quality check? {res_dark.get('quality_passed')} | Message: {res_dark.get('message')}")

    # 3. Test Negative Indian Food Dishes from Test Split
    negative_images = list(not_biryani_test_dir.glob("*.jpg"))
    print(f"\nEvaluating {len(negative_images)} authentic non-biryani Indian food images...")

    false_positives = 0
    true_negatives = 0
    uncertain_count = 0
    negative_predictions = []

    for img_p in negative_images:
        res = engine.predict(str(img_p))
        is_false_pos = (res.get("food") == "biryani")
        if is_false_pos:
            false_positives += 1
        elif res.get("food") == "other":
            true_negatives += 1
        else:
            uncertain_count += 1

        negative_predictions.append({
            "image": img_p.name,
            "prediction": res.get("food"),
            "is_biryani": res.get("is_biryani"),
            "confidence": res.get("confidence")
        })

    total_neg = len(negative_images)
    fp_rate = (false_positives / total_neg) if total_neg > 0 else 0.0

    print(f"Total Negative Food Images Tested: {total_neg}")
    print(f"Correctly Classified as Other:    {true_negatives} ({(true_negatives/total_neg)*100:.1f}%)")
    print(f"Classified as Unknown/Uncertain:  {uncertain_count} ({(uncertain_count/total_neg)*100:.1f}%)")
    print(f"False Positives (Mistaken Biryani): {false_positives} ({fp_rate*100:.1f}%)")
    print(f"False Positive Rate:              {fp_rate * 100:.2f}%")

    results["hard_negatives"] = negative_predictions
    results["summary"] = {
        "total_negative_images": total_neg,
        "true_negatives": true_negatives,
        "uncertain": uncertain_count,
        "false_positives": false_positives,
        "false_positive_rate": round(fp_rate, 4),
        "rejection_rate": round((total_neg - false_positives) / total_neg if total_neg > 0 else 1.0, 4)
    }

    out_file = BASE_DIR / "evaluation" / "hard_negative_evaluation.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Hard negative test report saved to {out_file}")
    print("==========================================================\n")
    return results

if __name__ == "__main__":
    run_hard_negative_tests()
