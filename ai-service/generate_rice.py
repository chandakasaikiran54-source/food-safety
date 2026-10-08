import os
from PIL import Image
import numpy as np

def generate_rice_images():
    base_dir = "food_dataset/raw"
    hygienic_dir = os.path.join(base_dir, "Hygienic")
    not_hygienic_dir = os.path.join(base_dir, "Not Hygienic")
    
    os.makedirs(hygienic_dir, exist_ok=True)
    os.makedirs(not_hygienic_dir, exist_ok=True)
    
    print("Generating synthetic fresh rice images...")
    for i in range(10):
        # White-ish color for fresh rice
        img = Image.new('RGB', (224, 224), color=(240, 240, 245))
        img.save(os.path.join(hygienic_dir, f"rice_fresh_{i}.jpg"))
        
    print("Generating synthetic spoiled rice images...")
    for i in range(10):
        # Green/Brownish for moldy/spoiled rice
        img = Image.new('RGB', (224, 224), color=(100, 120, 80))
        img.save(os.path.join(not_hygienic_dir, f"rice_spoiled_{i}.jpg"))
        
if __name__ == "__main__":
    generate_rice_images()
