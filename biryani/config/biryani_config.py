import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
MODELS_DIR = BASE_DIR / "models"
CHECKPOINT_PATH = MODELS_DIR / "biryani_classifier.pth"
METADATA_PATH = MODELS_DIR / "biryani_model_metadata.json"

# Classes
CLASS_NAMES = ["not_biryani", "biryani"]
LABEL_MAP = {"not_biryani": 0, "biryani": 1}
INV_LABEL_MAP = {0: "not_biryani", 1: "biryani"}

# Image specifications
IMAGE_SIZE = (224, 224)
NORMALIZATION_MEAN = [0.485, 0.456, 0.406]
NORMALIZATION_STD = [0.229, 0.224, 0.225]

# Decision Thresholds
# High confidence required to claim Biryani
BIRYANI_CONFIDENCE_THRESHOLD = 0.65
# Low confidence below which it is definitely Other
OTHER_CONFIDENCE_THRESHOLD = 0.35

# Training Hyperparameters
BATCH_SIZE = 16
NUM_EPOCHS = 8
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
RANDOM_SEED = 42

# Pretrained Architecture
ARCHITECTURE = "mobilenet_v3_small" # Lightweight, fast CPU inference, highly accurate
