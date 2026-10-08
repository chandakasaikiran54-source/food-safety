"""
FoodSafe AI — Biryani Regional Classification Configuration
Based on IIIT Hyderabad / CVIT Research: "How Does India Cook Biryani?" (ICVGIP 2025)
"""

import os
from pathlib import Path

# Base Paths
ML_BIRYANI_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = ML_BIRYANI_DIR / "datasets"
RAW_DATASET_DIR = DATASETS_DIR / "raw" / "iith_video_dataset"
FRAMES_DIR = DATASETS_DIR / "frames"
TRAIN_DIR = DATASETS_DIR / "train"
VAL_DIR = DATASETS_DIR / "validation"
TEST_DIR = DATASETS_DIR / "test"
SMARTPHONE_TEST_DIR = DATASETS_DIR / "real_smartphone_test"
OOD_TEST_DIR = DATASETS_DIR / "ood_test"
MODELS_DIR = ML_BIRYANI_DIR / "models"
EVALUATION_DIR = ML_BIRYANI_DIR / "evaluation"

# Target Classes (12 Regional Categories)
TARGET_CLASSES = [
    "Ambur",
    "Bombay",
    "Dindigul",
    "Donne",
    "Hyderabadi",
    "Kashmiri",
    "Kolkata",
    "Awadhi",
    "Malabar",
    "Mughlai",
    "Sindhi",
    "Thalassery"
]

CLASS_TO_IDX = {cls_name.lower(): idx for idx, cls_name in enumerate(TARGET_CLASSES)}
IDX_TO_CLASS = {idx: cls_name for idx, cls_name in enumerate(TARGET_CLASSES)}

# Canonical Research Mapping (from IIIT-H directory names to standard target keys)
IIITH_TO_CANONICAL = {
    "ambur_biryani": "ambur",
    "bombay_biryani": "bombay",
    "dindigul_biryani": "dindigul",
    "donne_biryani": "donne",
    "hyderabadi_biryani": "hyderabadi",
    "kashmiri_biryani": "kashmiri",
    "kolkata_biryani": "kolkata",
    "lucknow_awadhi_biryani": "awadhi",
    "malabar_biryani": "malabar",
    "mughlai_biryani": "mughlai",
    "sindhi_biryani": "sindhi",
    "thalassery_biryani": "thalassery"
}

# Regional Culinary Knowledge Base (Extracted from IIIT-H recipes & papers)
REGIONAL_PROFILES = {
    "Ambur": {
        "region": "Tamil Nadu (Vellore region)",
        "rice": "Seeraga Samba (short-grain)",
        "cooking_style": "Dum pukht with curd, tomato, and red chili paste",
        "key_visuals": "Slightly reddish-orange hue, shorter plump rice grains, tender meat, mild sour curd notes.",
        "accompaniments": "Ennai Kathirikai (tangy brinjal gravy), Onion Pachadi"
    },
    "Bombay": {
        "region": "Maharashtra (Mumbai coastal)",
        "rice": "Long-grain Basmati",
        "cooking_style": "Sweet, sour and spicy layered dum",
        "key_visuals": "Distinctive fried potato chunks, dried plums (aloo bukhara), kewra essence, crispy fried onions.",
        "accompaniments": "Kachumber, Boondi Raita"
    },
    "Dindigul": {
        "region": "Tamil Nadu (Dindigul / Thalappakatti)",
        "rice": "Seeraga Samba (short-grain)",
        "cooking_style": "Thalappakatti dum with curd, lemon juice, whole spices",
        "key_visuals": "Small aromatic grains, uniform amber-brown appearance, visible black pepper and cloves.",
        "accompaniments": "Dalcha, Onion Pachadi"
    },
    "Donne": {
        "region": "Karnataka (Bengaluru / Military Hotels)",
        "rice": "Seeraga Samba / Jeerakasala",
        "cooking_style": "Spiced broth infused with ground fresh herbs",
        "key_visuals": "Prominent greenish-tinted rice from ground mint, coriander and green chilies; served in areca nut leaf bowls (donne).",
        "accompaniments": "Raita, spicy thin gravy"
    },
    "Hyderabadi": {
        "region": "Telangana (Nizami Hyderabad)",
        "rice": "Aged Long-grain Basmati",
        "cooking_style": "Kachchi Dum (raw marinated meat slow-cooked with parboiled rice layers)",
        "key_visuals": "Tri-colored rice grains (pearly white, saffron yellow, amber orange), caramelized fried onions (birista), fresh mint.",
        "accompaniments": "Mirchi ka Salan, Dahi ki Chutney"
    },
    "Kashmiri": {
        "region": "Jammu & Kashmir",
        "rice": "Long-grain Basmati",
        "cooking_style": "Gentle aromatic saffron infusion, asafoetida, dry ginger, fennel",
        "key_visuals": "Lustrous saffron-golden rice, sweet-savory garnish of cashews, almonds, raisins, dried fruits.",
        "accompaniments": "Walnut chutney, Muji Chetinn (radish raita)"
    },
    "Kolkata": {
        "region": "West Bengal (Kolkata / Wajid Ali Shah legacy)",
        "rice": "Long-grain Basmati",
        "cooking_style": "Subtle Awadhi derivative dum with meetha atar, kewra and rose water",
        "key_visuals": "Light golden-yellow and white rice, large tender yellow spiced potato halves, whole boiled egg.",
        "accompaniments": "Burhani, Shami Kabab, Salad"
    },
    "Awadhi": {
        "region": "Uttar Pradesh (Lucknow / Nawabi Awadh)",
        "rice": "Aged Long-grain Basmati",
        "cooking_style": "Pakki Dum (cooked meat simmered in yakhni broth, strained, then sealed in handi)",
        "key_visuals": "Subtle, non-greasy, delicate pale cream and light saffron grains, deeply infused bone-marrow essence.",
        "accompaniments": "Galouti Kabab, Boondi Raita"
    },
    "Malabar": {
        "region": "Kerala (Malabar Coast)",
        "rice": "Jeerakasala / Khyma or Basmati",
        "cooking_style": "Layered dum with ghee, green chilies, Malabar garam masala",
        "key_visuals": "Glistening ghee coating, fried golden cashews and sultanas, gentle spice masala layer distinct from mild rice.",
        "accompaniments": "Date pickle (Eenthapazham achar), Chammanthi, Pappadam, Raita"
    },
    "Mughlai": {
        "region": "Delhi / Northern India (Imperial Mughal courts)",
        "rice": "Aged Long-grain Basmati",
        "cooking_style": "Rich royal dum with dry fruit pastes, cream/curd, kewra and saffron",
        "key_visuals": "Opulent presentation, creamy texture, visible almond/cashew slivers, gentle golden-hued grains.",
        "accompaniments": "Raita, Shahi Paneer or rich mutton gravies"
    },
    "Sindhi": {
        "region": "Sindh / Western Subcontinent",
        "rice": "Long-grain Basmati",
        "cooking_style": "Tangy and heavily spiced layered dum",
        "key_visuals": "Richly spiced orange-red rice, halved potatoes, sour dried plums (aloo bukhara), mint leaves, green chilies.",
        "accompaniments": "Kachumber, Cucumber Raita"
    },
    "Thalassery": {
        "region": "Kerala (North Malabar / Kannur)",
        "rice": "Authentic Jeerakasala / Kaima (short, delicate grain)",
        "cooking_style": "Dum cooked with local Malabar spices, fennel, pure ghee",
        "key_visuals": "Tiny distinct Kaima rice grains, golden brown fried onion garnish, roasted cashews and raisins.",
        "accompaniments": "Beetroot pachadi, Lemon pickle, Coconut chutney"
    }
}

# Image Preprocessing & Normalization
IMAGE_SIZE = (224, 224)
NORMALIZATION_MEAN = [0.485, 0.456, 0.406]
NORMALIZATION_STD = [0.229, 0.224, 0.225]

# Strict Video-Level Partitioning
# 10 videos per category:
# Train: 7 videos (70%)
# Validation: 1-2 videos (15%)
# Test: 1-2 videos (15%)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Training Hyperparameters
BATCH_SIZE = 16
NUM_EPOCHS = 12
LEARNING_RATE = 3e-4
WEIGHT_DECAY = 1e-4
RANDOM_SEED = 42

# Decision & Calibration Thresholds
CONFIDENCE_THRESHOLD = 0.50       # Predictions below 50% are categorized as Unknown/Insufficient Evidence
HIGH_CONFIDENCE_THRESHOLD = 0.75  # Highly confident prediction
BIRYANI_GATE_THRESHOLD = 0.65     # Stage-1 Binary gatekeeper threshold
