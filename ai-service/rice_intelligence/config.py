# Configuration and constants for Rice Intelligence Engine

# Project Design Hypothesis:
# Rice quality may contribute approximately 20% to the overall Biryani assessment.
# Note: 20% is a configurable project design hypothesis, NOT an immutable physical constant or IIT Hyderabad mandate.
DEFAULT_RICE_CONTRIBUTION_WEIGHT = 0.20

# Morphological Thresholds (Dimensionless / Relative Aspect Ratio L/B):
# Standards reference: AGMARK, FSSAI, ICAR for Indian Rice Varieties
BASMATI_MIN_ASPECT_RATIO = 3.20      # Extra Long Slender (ELS) typically >= 3.2 - 3.5
SONA_MASURI_MIN_ASPECT_RATIO = 2.40  # Medium Slender (MS) typically 2.4 - 3.0
SONA_MASURI_MAX_ASPECT_RATIO = 3.10
SHORT_GRAIN_MAX_ASPECT_RATIO = 2.20  # Bold / Short grain < 2.2

# Broken grain threshold:
# A grain is categorized as broken if its major length is less than 75% of the median whole grain length
BROKEN_GRAIN_LENGTH_RATIO = 0.75

# Quality thresholds (broken grain percentage):
QUALITY_HIGH_BROKEN_MAX = 5.0        # Grade 1 / Premium: < 5% broken
QUALITY_MEDIUM_BROKEN_MAX = 15.0     # Grade 2: 5 - 15% broken

# Image Quality Minimums:
MIN_IMAGE_WIDTH = 150
MIN_IMAGE_HEIGHT = 150
MIN_LAPLACIAN_VARIANCE = 25.0        # Blur detection threshold
MIN_GRAINS_FOR_CONFIDENT_ASSESSMENT = 5
MIN_RICE_PIXEL_RATIO = 0.03          # Minimum percentage of image occupied by rice candidate pixels
