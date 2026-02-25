"""
Math utilities for KineMouse.

Provides:
- Distance calculations between hand landmarks
- Dynamic reference distance (D_ref) normalization
- Exponential Moving Average (EMA) smoothing
- Screen coordinate mapping
"""

import math
import numpy as np
from typing import Tuple, List


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Compute Euclidean distance between two 2D points."""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def compute_dref(landmarks: List) -> float:
    """
    Compute dynamic reference distance D_ref.
    Measures distance from Wrist (0) to Index Knuckle (5).
    Used to normalize pinch threshold to camera distance.
    """
    wrist = (landmarks[0].x, landmarks[0].y)
    index_knuckle = (landmarks[5].x, landmarks[5].y)
    return euclidean_distance(wrist, index_knuckle)


def is_pinching(landmarks: List, tip_a: int, tip_b: int, dref: float, threshold: float = 0.15) -> bool:
    """
    Check if two finger tips are pinching.
    Pinch activates when distance < threshold * D_ref (default 15%).
    """
    pt_a = (landmarks[tip_a].x, landmarks[tip_a].y)
    pt_b = (landmarks[tip_b].x, landmarks[tip_b].y)
    dist = euclidean_distance(pt_a, pt_b)
    return dist < (threshold * dref)


def midpoint(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    """Return midpoint between two 2D points."""
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)


def ema_smooth(current: Tuple[float, float], previous: Tuple[float, float], alpha: float = 0.25) -> Tuple[float, float]:
    """
    Apply Exponential Moving Average smoothing.
    S_t = alpha * X_t + (1 - alpha) * S_{t-1}
    """
    sx = alpha * current[0] + (1 - alpha) * previous[0]
    sy = alpha * current[1] + (1 - alpha) * previous[1]
    return (sx, sy)


def map_to_screen(
    point: Tuple[float, float],
    active_box: Tuple[float, float, float, float],
    screen_res: Tuple[int, int]
) -> Tuple[int, int]:
    """
    Map a normalized point (0..1) from active_box region to full screen resolution.
    active_box: (x_min, y_min, x_max, y_max) in normalized coords
    screen_res: (width, height) in pixels
    """
    x_min, y_min, x_max, y_max = active_box
    # Clamp to active box
    nx = max(x_min, min(x_max, point[0]))
    ny = max(y_min, min(y_max, point[1]))
    # Map to screen
    sx = int(((nx - x_min) / (x_max - x_min)) * screen_res[0])
    sy = int(((ny - y_min) / (y_max - y_min)) * screen_res[1])
    return (sx, sy)
