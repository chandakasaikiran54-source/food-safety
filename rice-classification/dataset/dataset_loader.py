"""
Dataset acquisition, quality control, duplicate prevention, and leakage-free splitting
for the Rice Classification module.
"""

import os
import sys
import shutil
import hashlib
import urllib.request
from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader

# Ensure package imports work
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from config.rice_config import (
    DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR,
    MENDELEY_DOWNLOAD_URL, ARCHIVE_FILENAME, RAW_TO_TARGET_MAP,
    TARGET_CLASSES, CLASS_TO_IDX, RANDOM_SEED,
    TRAIN_RATIO, VAL_RATIO, TEST_RATIO
)
from preprocessing.rice_preprocessor import get_train_transforms, get_eval_transforms

def compute_file_hash(filepath, block_size=65536):
    """Computes MD5 hash to identify duplicate images."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        buf = f.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(block_size)
    return hasher.hexdigest()

def download_dataset(download_url=MENDELEY_DOWNLOAD_URL, target_dir=RAW_DATA_DIR):
    """Downloads the verified Mendeley Data 7z archive."""
    target_dir.mkdir(parents=True, exist_ok=True)
    archive_path = target_dir / ARCHIVE_FILENAME
    
    if archive_path.exists() and archive_path.stat().st_size > 100 * 1024 * 1024:
        print(f"[Dataset] Archive already exists: {archive_path} ({archive_path.stat().st_size / 1e6:.1f} MB)")
        return archive_path
        
    print(f"[Dataset] Downloading Mendeley Data archive from: {download_url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FoodSafe-AI/1.0"}
    req = urllib.request.Request(download_url, headers=headers)
    
    with urllib.request.urlopen(req) as response, open(archive_path, "wb") as out_file:
        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB chunks
        
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"\rDownloading: {downloaded / 1e6:.1f}MB / {total_size / 1e6:.1f}MB ({percent:.1f}%)", end="", flush=True)
            else:
                print(f"\rDownloading: {downloaded / 1e6:.1f}MB", end="", flush=True)
                
    print(f"\n[Dataset] Download complete: {archive_path}")
    return archive_path

def extract_archive(archive_path, extract_dir=RAW_DATA_DIR / "extracted"):
    """Extracts .7z archive using py7zr or system 7z."""
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if already extracted
    existing_subdirs = [p for p in extract_dir.glob("*") if p.is_dir()]
    if existing_subdirs:
        print(f"[Dataset] Archive already extracted at {extract_dir} ({len(existing_subdirs)} folders found)")
        return extract_dir

    print(f"[Dataset] Extracting {archive_path} to {extract_dir}...")
    try:
        import py7zr
        with py7zr.SevenZipFile(archive_path, mode="r") as z:
            z.extractall(path=extract_dir)
        print("[Dataset] Extraction successful with py7zr.")
    except ImportError:
        # Fallback to system 7z command
        res = os.system(f'7z x "{archive_path}" -o"{extract_dir}" -y')
        if res != 0:
            raise RuntimeError("py7zr is not installed and system 7z failed. Run: pip install py7zr")
            
    return extract_dir

def prepare_and_split_dataset(raw_extracted_dir, processed_dir=PROCESSED_DATA_DIR, max_samples_per_class=3000):
    """
    Quality Control & Leakage-Free Dataset Split:
    1. Scan all raw folders and map to target classes (basmati, sona_masuri, other_rice, unknown)
    2. Check image readability / corruptions
    3. Filter exact duplicates via MD5 hash
    4. Stratify into Train (75%), Val (12.5%), Test (12.5%)
    """
    import random
    random.seed(RANDOM_SEED)

    train_dir = processed_dir / "train"
    val_dir = processed_dir / "val"
    test_dir = processed_dir / "test"

    if (train_dir / "basmati").exists() and any((train_dir / "basmati").iterdir()):
        print(f"[Dataset] Processed dataset already prepared at {processed_dir}")
        return train_dir, val_dir, test_dir

    for d in [train_dir, val_dir, test_dir]:
        for cls_name in TARGET_CLASSES:
            (d / cls_name).mkdir(parents=True, exist_ok=True)

    print("[Dataset] Scanning raw images and performing Quality Control...")
    image_paths_by_class = {cls_name: [] for cls_name in TARGET_CLASSES}
    seen_hashes = set()
    corrupt_count = 0
    duplicate_count = 0

    # Locate image directories recursively
    all_image_files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"):
        all_image_files.extend(list(raw_extracted_dir.rglob(ext)))

    print(f"[Dataset] Found {len(all_image_files)} raw candidate image files.")

    for img_path in all_image_files:
        parent_folder = img_path.parent.name.lower()
        target_class = RAW_TO_TARGET_MAP.get(parent_folder)
        if not target_class:
            continue

        # 1. Quality & Readability check
        try:
            with Image.open(img_path) as im:
                im.verify()
        except Exception:
            corrupt_count += 1
            continue

        # 2. Duplicate check
        file_hash = compute_file_hash(img_path)
        if file_hash in seen_hashes:
            duplicate_count += 1
            continue
        seen_hashes.add(file_hash)

        image_paths_by_class[target_class].append(img_path)

    print(f"[Dataset QC] Corrupted filtered: {corrupt_count}, Duplicates filtered: {duplicate_count}")
    print("[Dataset QC] Clean unique images found per target class:")
    for cls_name, paths in image_paths_by_class.items():
        print(f"  - {cls_name}: {len(paths)} images")

    # Limit per class to balance dataset if necessary
    for cls_name in TARGET_CLASSES:
        paths = image_paths_by_class[cls_name]
        random.shuffle(paths)
        if len(paths) > max_samples_per_class:
            paths = paths[:max_samples_per_class]

        n = len(paths)
        n_train = int(n * TRAIN_RATIO)
        n_val = int(n * VAL_RATIO)

        train_paths = paths[:n_train]
        val_paths = paths[n_train:n_train + n_val]
        test_paths = paths[n_train + n_val:]

        for split_name, split_paths in [("train", train_paths), ("val", val_paths), ("test", test_paths)]:
            target_sub = processed_dir / split_name / cls_name
            for p in split_paths:
                dest = target_sub / p.name
                shutil.copy2(p, dest)

    return train_dir, val_dir, test_dir

class RiceImageDataset(Dataset):
    """PyTorch Dataset for Rice Variety Classification."""
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples = []
        
        for cls_name in TARGET_CLASSES:
            cls_dir = self.root_dir / cls_name
            if not cls_dir.exists():
                continue
            cls_idx = CLASS_TO_IDX[cls_name]
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"):
                for p in cls_dir.glob(ext):
                    self.samples.append((str(p), cls_idx))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label

def get_dataloaders(processed_dir=PROCESSED_DATA_DIR, batch_size=32, num_workers=2):
    """Constructs train, validation, and test PyTorch DataLoaders."""
    train_ds = RiceImageDataset(processed_dir / "train", transform=get_train_transforms())
    val_ds = RiceImageDataset(processed_dir / "val", transform=get_eval_transforms())
    test_ds = RiceImageDataset(processed_dir / "test", transform=get_eval_transforms())

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)

    return train_loader, val_loader, test_loader, train_ds, val_ds, test_ds
