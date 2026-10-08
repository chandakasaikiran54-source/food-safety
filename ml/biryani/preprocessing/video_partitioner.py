"""
FoodSafe AI — Zero-Data-Leakage Video Partitioner
Implements Phase 6: Strict video-level and URL-level partitioning across Train, Val, and Test.
"""

import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def generate_video_splits(metadata_path, train_count=7, val_count=1, test_count=2):
    """
    Creates deterministic video-level partition mappings for each of the 12 categories.
    Guarantees: ZERO video or URL overlap between train, validation, and test splits.
    """
    with open(metadata_path, "r", encoding="utf-8") as f:
        all_metadata = json.load(f)

    splits = {
        "train": {},
        "validation": {},
        "test": {}
    }

    url_to_split = {}
    video_manifest = {}

    for cat_name, videos in all_metadata.items():
        v_keys = sorted(videos.keys(), key=lambda x: int(x.replace("video", "")))
        
        splits["train"][cat_name] = []
        splits["validation"][cat_name] = []
        splits["test"][cat_name] = []
        video_manifest[cat_name] = {}

        # Track category assignments
        assigned_train = []
        assigned_val = []
        assigned_test = []

        for idx, v_key in enumerate(v_keys):
            v_info = videos[v_key]
            v_url = v_info.get("youtube_url", "")

            # If this URL was already assigned to a split (e.g., duplicate URL in Bombay biryani)
            if v_url in url_to_split:
                target_split = url_to_split[v_url]
                splits[target_split][cat_name].append(v_key)
                video_manifest[cat_name][v_key] = {
                    "split": target_split,
                    "url": v_url,
                    "duplicate_of_assigned_url": True
                }
                continue

            # Standard video-level deterministic assignment:
            # First 7 videos -> train
            # Video 8 -> validation
            # Video 9, 10 -> test
            if len(assigned_train) < train_count:
                target_split = "train"
                assigned_train.append(v_key)
            elif len(assigned_val) < val_count:
                target_split = "validation"
                assigned_val.append(v_key)
            else:
                target_split = "test"
                assigned_test.append(v_key)

            splits[target_split][cat_name].append(v_key)
            url_to_split[v_url] = target_split
            video_manifest[cat_name][v_key] = {
                "split": target_split,
                "url": v_url,
                "duplicate_of_assigned_url": False
            }

    # Strict Zero-Leakage Verification Assertions
    train_urls = {v["youtube_url"] for cat in splits["train"] for vk in splits["train"][cat] for v in [all_metadata[cat][vk]]}
    val_urls = {v["youtube_url"] for cat in splits["validation"] for vk in splits["validation"][cat] for v in [all_metadata[cat][vk]]}
    test_urls = {v["youtube_url"] for cat in splits["test"] for vk in splits["test"][cat] for v in [all_metadata[cat][vk]]}

    overlap_train_val = train_urls.intersection(val_urls)
    overlap_train_test = train_urls.intersection(test_urls)
    overlap_val_test = val_urls.intersection(test_urls)

    assert len(overlap_train_val) == 0, f"DATA LEAKAGE DETECTED between Train and Val: {overlap_train_val}"
    assert len(overlap_train_test) == 0, f"DATA LEAKAGE DETECTED between Train and Test: {overlap_train_test}"
    assert len(overlap_val_test) == 0, f"DATA LEAKAGE DETECTED between Val and Test: {overlap_val_test}"

    summary = {
        "status": "ZERO_LEAKAGE_VERIFIED",
        "total_categories": len(all_metadata),
        "split_counts_per_category": {
            "train_videos": train_count,
            "validation_videos": val_count,
            "test_videos": test_count
        },
        "splits": splits,
        "video_manifest": video_manifest
    }

    return summary

if __name__ == "__main__":
    import os
    candidate_paths = [
        Path("scratch/all_videos_segmentation_metadata.json"),
        Path(r"C:\Users\chand\.gemini\antigravity-ide\brain\4e4ca756-7ca8-4886-908c-ecc6a2823ecf\scratch\all_videos_segmentation_metadata.json")
    ]
    metadata_file = None
    for p in candidate_paths:
        if p.exists():
            metadata_file = p
            break

    if metadata_file:
        res = generate_video_splits(metadata_file)
        out_path = Path("ml/biryani/datasets/video_split_manifest.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print("Video split manifest generated and zero-leakage verified successfully!")
        print(f"Manifest written to: {out_path}")
    else:
        print("Could not find all_videos_segmentation_metadata.json!")

