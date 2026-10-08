"""
FoodSafe AI — High-Speed Partial Range Test Split Extractor
Extracts food frames directly from untouched Video 9 & Video 10 using range-download.
"""

import os
import sys
from pathlib import Path

# Add ffmpeg to PATH
scripts_dir = r'C:\Users\chand\Music\main project\foodsafe-ai\ai-service\venv\Scripts'
if scripts_dir not in os.environ['PATH']:
    os.environ['PATH'] = scripts_dir + os.pathsep + os.environ['PATH']

import json
import logging
import cv2
import yt_dlp

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.biryani_config import DATASETS_DIR, IIITH_TO_CANONICAL
from preprocessing.quality_filter import FrameQualityFilter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def extract_test_split(target_frames_per_class=4):
    manifest_file = DATASETS_DIR / "video_split_manifest.json"
    candidate_meta = [
        DATASETS_DIR / "all_videos_segmentation_metadata.json",
        Path(r"C:\Users\chand\.gemini\antigravity-ide\brain\4e4ca756-7ca8-4886-908c-ecc6a2823ecf\scratch\all_videos_segmentation_metadata.json")
    ]
    meta_file = next(p for p in candidate_meta if p.exists())

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    test_splits = manifest["splits"]["test"]
    q_filter = FrameQualityFilter()

    test_dir = DATASETS_DIR / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    temp_clip_path = Path("scratch/temp_test_clip.mp4")

    results = {}
    for cat_name, test_videos in test_splits.items():
        canonical_class = IIITH_TO_CANONICAL.get(cat_name, cat_name)
        class_dir = test_dir / canonical_class
        class_dir.mkdir(parents=True, exist_ok=True)

        existing = len(list(class_dir.glob("*.jpg")))
        if existing >= target_frames_per_class:
            logger.info(f"[{canonical_class}] already has {existing} test frames.")
            results[canonical_class] = existing
            continue

        logger.info(f"Populating test frames for {canonical_class} from {test_videos}...")
        retained_count = existing

        for v_key in test_videos:
            if retained_count >= target_frames_per_class:
                break

            v_info = meta.get(cat_name, {}).get(v_key, {})
            url = v_info.get("youtube_url")
            chunks = v_info.get("relevant_chunks", [])
            if not url or not chunks:
                continue

            # Pick serving/plating chunk
            sorted_chunks = sorted(
                chunks,
                key=lambda c: any(w in ' '.join(c.get('actions', [])).lower() for w in ['serving', 'plate', 'plating', 'garnish', 'bowl', 'finished']),
                reverse=True
            )

            for c in sorted_chunks[:2]:
                if retained_count >= target_frames_per_class:
                    break

                ts = c.get("timestamp", "")
                try:
                    parts = ts.split("-")
                    sec_start = float(parts[0])
                    sec_end = min(sec_start + 8.0, float(parts[1]))
                except Exception:
                    continue

                ydl_opts = {
                    'format': 'bestvideo[height<=360][ext=mp4]/best[height<=360]/best',
                    'download_ranges': yt_dlp.utils.download_range_func(None, [(sec_start, sec_end)]),
                    'outtmpl': str(temp_clip_path),
                    'quiet': True,
                    'js_runtimes': {'node': {}},
                    'force_overwrites': True
                }

                try:
                    if temp_clip_path.exists():
                        temp_clip_path.unlink()
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                except Exception as e:
                    logger.warning(f"Download range failed for {url}: {e}")
                    continue

                if not temp_clip_path.exists():
                    continue

                cap = cv2.VideoCapture(str(temp_clip_path))
                if not cap.isOpened():
                    continue

                q_filter.reset_video_session()
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                sample_indices = [int(frame_count * 0.3), int(frame_count * 0.7)]

                for f_idx in sample_indices:
                    if retained_count >= target_frames_per_class:
                        break
                    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        continue

                    keep, reason, metrics = q_filter.evaluate_frame(frame)
                    if keep:
                        out_path = class_dir / f"{canonical_class}_{v_key}_{int(sec_start)}_{f_idx}.jpg"
                        cv2.imwrite(str(out_path), frame)
                        retained_count += 1
                        logger.info(f"  Saved test frame: {out_path.name}")

                cap.release()

        results[canonical_class] = retained_count

    print("Test split population complete:", json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    extract_test_split()
