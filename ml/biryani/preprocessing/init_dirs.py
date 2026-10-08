import os
from pathlib import Path

BASE_DIR = Path("ml/biryani/datasets")
CLASSES = [
    'ambur', 'bombay', 'dindigul', 'donne', 'hyderabadi', 'kashmiri',
    'kolkata', 'awadhi', 'malabar', 'mughlai', 'sindhi', 'thalassery'
]

splits = ['frames', 'train', 'validation', 'test', 'real_smartphone_test']
for s in splits:
    for c in CLASSES:
        os.makedirs(BASE_DIR / s / c, exist_ok=True)

os.makedirs(BASE_DIR / 'ood_test' / 'non_biryani', exist_ok=True)
print("Successfully initialized all dataset directory trees.")
