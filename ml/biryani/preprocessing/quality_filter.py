"""
FoodSafe AI — Automated Frame Quality & Relevance Filter
Implements Phase 7: Automated rejection of blurry, duplicate, non-food, and low-quality frames.
"""

import cv2
import numpy as np
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# Initialize OpenCV Haar Cascade for face detection if available
face_cascade = None
try:
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
except Exception:
    pass

class FrameQualityFilter:
    def __init__(self,
                 blur_threshold=20.0,
                 min_brightness=30.0,
                 max_brightness=240.0,
                 min_contrast=18.0,
                 min_food_ratio=0.18,
                 max_face_area_ratio=0.20,
                 dup_hash_dist_threshold=5):
        self.blur_threshold = blur_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_contrast = min_contrast
        self.min_food_ratio = min_food_ratio
        self.max_face_area_ratio = max_face_area_ratio
        self.dup_hash_dist_threshold = dup_hash_dist_threshold
        self.seen_hashes = []

    def compute_dhash(self, cv_image, hash_size=8):
        """Compute difference hash (dHash) for near-duplicate detection."""
        resized = cv2.resize(cv_image, (hash_size + 1, hash_size), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        diff = gray[:, 1:] > gray[:, :-1]
        return diff.flatten()

    def is_duplicate(self, current_hash):
        """Checks if current frame is a near-duplicate of previously accepted frames."""
        for prev_hash in self.seen_hashes:
            hamming_dist = np.count_nonzero(current_hash != prev_hash)
            if hamming_dist <= self.dup_hash_dist_threshold:
                return True, hamming_dist
        return False, 999

    def evaluate_frame(self, cv_image):
        """
        Assesses whether a frame is suitable for the Biryani classification dataset.
        Returns: (keep: bool, reason: str, metrics: dict)
        """
        if cv_image is None or cv_image.size == 0:
            return False, "empty_image", {}

        h, w = cv_image.shape[:2]
        if w < 160 or h < 160:
            return False, "resolution_too_low", {"w": w, "h": h}

        # 1. Blur Detection (Laplacian variance)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        blur_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if blur_var < self.blur_threshold:
            return False, f"too_blurry (var={blur_var:.1f})", {"blur_var": blur_var}

        # 2. Illumination & Contrast
        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]
        mean_v = float(np.mean(v_channel))
        contrast = float(np.std(gray))

        if mean_v < self.min_brightness:
            return False, f"too_dark (v={mean_v:.1f})", {"mean_v": mean_v}
        if mean_v > self.max_brightness:
            return False, f"overexposed (v={mean_v:.1f})", {"mean_v": mean_v}
        if contrast < self.min_contrast:
            return False, f"low_contrast_or_blank (std={contrast:.1f})", {"contrast": contrast}

        # 3. Human Face Dominance Check
        if face_cascade is not None and not face_cascade.empty():
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(40, 40))
            if len(faces) > 0:
                total_face_area = sum(fw * fh for (fx, fy, fw, fh) in faces)
                face_area_ratio = total_face_area / float(w * h)
                if face_area_ratio > self.max_face_area_ratio:
                    return False, f"human_face_dominated (ratio={face_area_ratio:.2f})", {"face_ratio": face_area_ratio}

        # 4. Food / Biryani Color Distribution Check
        # Warm tones (saffron/yellow/orange/red): H in [5, 35], S > 40
        # Dark brown / fried onions: H in [8, 25], S in [50, 200], V in [25, 120]
        # Green garnish / herbs (for Donne etc): H in [35, 85], S > 40
        # White / pale dum rice: S < 45, V > 140
        mask_warm = cv2.inRange(hsv, np.array([5, 40, 50]), np.array([35, 255, 255]))
        mask_brown = cv2.inRange(hsv, np.array([8, 50, 25]), np.array([25, 200, 120]))
        mask_green = cv2.inRange(hsv, np.array([35, 40, 35]), np.array([85, 255, 220]))
        mask_white = cv2.inRange(hsv, np.array([0, 0, 140]), np.array([180, 45, 255]))

        food_pixels = cv2.countNonZero(mask_warm) + cv2.countNonZero(mask_brown) + \
                      cv2.countNonZero(mask_green) + cv2.countNonZero(mask_white)
        food_ratio = food_pixels / float(w * h)

        if food_ratio < self.min_food_ratio:
            return False, f"insufficient_food_content (ratio={food_ratio:.2f})", {"food_ratio": food_ratio}

        # 5. Near-Duplicate Check
        dhash = self.compute_dhash(cv_image)
        is_dup, dist = self.is_duplicate(dhash)
        if is_dup:
            return False, f"near_duplicate (hamming_dist={dist})", {"dup_dist": dist}

        # Passed all filters
        self.seen_hashes.append(dhash)
        return True, "accepted", {
            "blur_var": round(blur_var, 1),
            "mean_v": round(mean_v, 1),
            "contrast": round(contrast, 1),
            "food_ratio": round(food_ratio, 2)
        }

    def reset_video_session(self):
        """Clears seen hashes when moving to a new video."""
        self.seen_hashes.clear()
