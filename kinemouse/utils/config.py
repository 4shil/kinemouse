"""
KineMouse Configuration.
All tuneable parameters in one place.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class KineMouseConfig:
    # --- Vision ---
    camera_index: int = 0
    capture_fps: int = 30
    flip_horizontal: bool = True  # Mirror image for natural feel

    # --- Active Box (normalized, center of frame) ---
    active_box: Tuple[float, float, float, float] = (0.25, 0.20, 0.75, 0.80)

    # --- Gesture Thresholds ---
    pinch_threshold: float = 0.15       # % of D_ref for pinch activation
    double_pinch_window_ms: int = 400   # ms window for double-pinch detection

    # --- Smoothing ---
    ema_alpha: float = 0.25             # EMA smoothing factor (lower = smoother, more lag)

    # --- Performance ---
    max_num_hands: int = 1
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.7

    # --- Landmarks (MediaPipe hand landmark indices) ---
    WRIST: int = 0
    INDEX_KNUCKLE: int = 5
    THUMB_TIP: int = 4
    INDEX_TIP: int = 8
    MIDDLE_TIP: int = 12
    RING_TIP: int = 16


# Default config singleton
DEFAULT_CONFIG = KineMouseConfig()
