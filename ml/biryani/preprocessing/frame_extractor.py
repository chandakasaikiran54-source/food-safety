"""
FoodSafe AI — Targeted Frame Extractor with Procedural Filtering
Implements Phase 5 & 7: Extracts food-relevant frames from IIIT-H videos using timestamp annotations.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
import cv2
import yt_dlp

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.biryani_config import (
    DATASETS_DIR, IIITH_TO_CANONICAL, TARGET_CLASSES
)
from preprocessing.quality_filter import FrameQualityFilter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class VideoFrameExtractor:
    def __init__(self,
                 manifest_path=None,
                 metadata_path=None,
                 frames_per_video_limit=15):
        self.manifest_path = manifest_path or DATASETS_DIR / "video_split_manifest.json"
        
        # Check candidate locations for metadata
        candidate_meta = [
            DATASETS_DIR / "all_videos_segmentation_metadata.json",
            Path(r"C:\Users\chand\.gemini\antigravity-ide\brain\4e4ca756-7ca8-4886-908c-ecc6a2823ecf\scratch\all_videos_segmentation_metadata.json")
        ]
        if metadata_path:
            self.metadata_path = Path(metadata_path)
        else:
            self.metadata_path = next((p for p in candidate_meta if p.exists()), candidate_meta[0])

        self.frames_per_video_limit = frames_per_video_limit
        self.quality_filter = FrameQualityFilter()
        self.stats = {
            "total_extracted": 0,
            "total_retained": 0,
            "total_rejected": 0,
            "rejection_reasons": {},
            "split_counts": {"train": 0, "validation": 0, "test": 0},
            "class_counts": {c.lower(): 0 for c in TARGET_CLASSES}
        }

    def parse_timestamp_range(self, ts_str):
        """Converts timestamp like '500-510' or '510-516' to start_sec, end_sec."""
        try:
            parts = str(ts_str).split("-")
            start = float(parts[0].strip())
            end = float(parts[1].strip())
            return start, end
        except Exception:
            return None, None

    def extract_from_video(self, url, relevant_chunks, out_dir, prefix, max_frames=12):
        """Streams video with yt-dlp and extracts frames at targeted timestamps."""
        self.quality_filter.reset_video_session()
        ydl_opts = {
            'format': '18/best[ext=mp4][height<=360]',
            'quiet': True,
            'no_warnings': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info.get('url')
        except Exception as e:
            logger.warning(f"Could not retrieve stream for {url}: {e}")
            return 0, 0

        if not stream_url:
            return 0, 0

        cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            logger.warning(f"Failed to open video capture for {url}")
            return 0, 0

        video_retained = 0
        video_rejected = 0

        # Prioritize chunks that mention serving, plating, or finished biryani
        sorted_chunks = sorted(
            relevant_chunks,
            key=lambda c: any(w in ' '.join(c.get('actions', [])).lower() for w in ['serving', 'plate', 'plating', 'garnish', 'bowl']),
            reverse=True
        )

        for chunk in sorted_chunks:
            if video_retained >= max_frames:
                break

            ts = chunk.get("timestamp")
            start_sec, end_sec = self.parse_timestamp_range(ts)
            if start_sec is None or end_sec is None:
                continue

            # Sample 1-2 points per chunk
            duration = max(1.0, end_sec - start_sec)
            sample_points = [start_sec + 0.5 * duration]
            if duration >= 5.0 and video_retained + 1 < max_frames:
                sample_points.append(start_sec + 0.8 * duration)

            for sec in sample_points:
                if video_retained >= max_frames:
                    break

                cap.set(cv2.CAP_PROP_POS_MSEC, int(sec * 1000))
                ret, frame = cap.read()
                self.stats["total_extracted"] += 1

                if not ret or frame is None:
                    video_rejected += 1
                    self.stats["total_rejected"] += 1
                    self.stats["rejection_reasons"]["read_failure"] = self.stats["rejection_reasons"].get("read_failure", 0) + 1
                    continue

                keep, reason, metrics = self.quality_filter.evaluate_frame(frame)
                if keep:
                    out_filename = f"{prefix}_{int(sec)}s.jpg"
                    out_path = out_dir / out_filename
                    cv2.imwrite(str(out_path), frame)
                    video_retained += 1
                    self.stats["total_retained"] += 1
                else:
                    video_rejected += 1
                    self.stats["total_rejected"] += 1
                    base_reason = reason.split()[0]
                    self.stats["rejection_reasons"][base_reason] = self.stats["rejection_reasons"].get(base_reason, 0) + 1

        cap.release()
        return video_retained, video_rejected

    def run_extraction(self, max_videos_per_class=None, frames_per_video=8):
        """Executes targeted frame extraction across splits and categories."""
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        splits = manifest["splits"]

        for split_name in ["train", "validation", "test"]:
            logger.info(f"=== Processing Split: {split_name.upper()} ===")
            split_dict = splits[split_name]

            for cat_name, video_list in split_dict.items():
                canonical_class = IIITH_TO_CANONICAL.get(cat_name, cat_name)
                target_dir = DATASETS_DIR / split_name / canonical_class
                target_dir.mkdir(parents=True, exist_ok=True)

                selected_videos = video_list[:max_videos_per_class] if max_videos_per_class else video_list

                for v_key in selected_videos:
                    v_meta = metadata.get(cat_name, {}).get(v_key, {})
                    url = v_meta.get("youtube_url")
                    relevant_chunks = v_meta.get("relevant_chunks", [])

                    if not url or not relevant_chunks:
                        continue

                    prefix = f"{canonical_class}_{v_key}"
                    logger.info(f"Extracting [{split_name}] {cat_name} -> {v_key} ({len(relevant_chunks)} chunks)...")
                    retained, rejected = self.extract_from_video(
                        url, relevant_chunks, target_dir, prefix, max_frames=frames_per_video
                    )
                    self.stats["split_counts"][split_name] += retained
                    self.stats["class_counts"][canonical_class] += retained
                    logger.info(f"  Result: {retained} retained, {rejected} rejected.")

        # Save extraction report
        report_path = DATASETS_DIR / "frame_extraction_manifest.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

        logger.info(f"Extraction completed! Report saved to {report_path}")
        return self.stats

if __name__ == "__main__":
    extractor = VideoFrameExtractor()
    # Run a test extraction with 1 video per class across splits to verify
    stats = extractor.run_extraction(max_videos_per_class=1, frames_per_video=6)
    print("Test extraction stats:", json.dumps(stats, indent=2))
