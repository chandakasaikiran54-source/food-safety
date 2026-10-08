import sys
import logging
from pathlib import Path

# Connect to the Biryani core module
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIRYANI_MODULE_PATH = REPO_ROOT / "biryani"
if not BIRYANI_MODULE_PATH.exists():
    BIRYANI_MODULE_PATH = REPO_ROOT / "food-identification" / "biryani"

if str(BIRYANI_MODULE_PATH) not in sys.path:
    sys.path.insert(0, str(BIRYANI_MODULE_PATH))

logger = logging.getLogger(__name__)

try:
    from inference.biryani_inference import identify_biryani, get_biryani_inference_engine
except ImportError as e:
    logger.error(f"Could not import biryani inference module: {e}")
    identify_biryani = None

def run_biryani_identification(image_bytes_or_cv):
    """
    Adapter function that invokes the Biryani identification engine.
    """
    if identify_biryani is None:
        return {
            "success": False,
            "food": "unknown",
            "is_biryani": False,
            "confidence": 0.0,
            "message": "Biryani identification service module not available."
        }
    return identify_biryani(image_bytes_or_cv)
