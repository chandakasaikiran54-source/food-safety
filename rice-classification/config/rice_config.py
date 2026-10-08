"""
Configuration file for Rice Variety Classification (FoodSafe AI).
Target Classes:
1. basmati: Basmati extra-long slender rice
2. sona_masuri: Sona Masuri / HMT medium slender rice
3. other_rice: Other rice varieties (Arborio, Jasmine, Ipsala, Karacadag, Masuri)
4. unknown: Low-confidence / Out-of-distribution / Non-rice samples
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORT_DIR = BASE_DIR / "export"
MODELS_DIR = BASE_DIR / "models"
CHECKPOINT_PATH = EXPORT_DIR / "rice_classifier.pth"
CLASS_NAMES_PATH = EXPORT_DIR / "class_names.json"
CONFIG_PATH = EXPORT_DIR / "preprocessing_config.json"
METRICS_PATH = EXPORT_DIR / "metrics.json"

# Dataset Specs (Prabira Sethy / Mendeley Data DOI: 10.17632/c5y6gjwdzh.1)
MENDELEY_DATASET_ID = "c5y6gjwdzh"
MENDELEY_FILE_ID = "86367406-086b-4e6d-a959-b6ffa63b3324"
MENDELEY_DOWNLOAD_URL = (
    "https://data.mendeley.com/public-files/datasets/c5y6gjwdzh/files/"
    "86367406-086b-4e6d-a959-b6ffa63b3324/file_downloaded"
)
ARCHIVE_FILENAME = "Milled_Rice_Dataset.7z"

# Class Mapping
RAW_TO_TARGET_MAP = {
    "basmati": "basmati",
    "hmt": "sona_masuri",
    "arborio": "other_rice",
    "ipsala": "other_rice",
    "jasmine": "other_rice",
    "karacadag": "other_rice",
    "masuri": "other_rice",
    "jhili": "other_rice",
    "unknown": "unknown"
}

TARGET_CLASSES = ["basmati", "sona_masuri", "other_rice", "unknown"]
NUM_CLASSES = len(TARGET_CLASSES)

CLASS_TO_IDX = {cls_name: idx for idx, cls_name in enumerate(TARGET_CLASSES)}
IDX_TO_CLASS = {idx: cls_name for idx, cls_name in enumerate(TARGET_CLASSES)}

# Model Hyperparameters
ARCHITECTURE = "efficientnet_b0"  # Supported: efficientnet_b0, mobilenet_v3_large, resnet18
IMAGE_SIZE = 224
BATCH_SIZE = 32
NUM_WORKERS = 2
EPOCHS = 15
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
DROPOUT_RATE = 0.3
LABEL_SMOOTHING = 0.1

# Normalization parameters (ImageNet default)
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]

# Decision Thresholds
CONFIDENCE_THRESHOLD = 0.65  # Predictions below 0.65 are routed to 'unknown'
RANDOM_SEED = 42

# Split ratios
TRAIN_RATIO = 0.75
VAL_RATIO = 0.125
TEST_RATIO = 0.125
