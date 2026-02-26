"""
GestureClassifier — recognizes static hand shapes beyond pinch.

Detects:
- FIST         (all fingers closed) — for pause/freeze
- PEACE        (index + middle extended, others closed) — configurable action
- THUMBS_UP    (thumb up, all others closed)
- OPEN_HAND    (all fingers extended) — idle/release

These extend KineMouse beyond simple pinch gestures into richer pose detection.
"""

from enum import Enum, auto
from typing import List, Optional

from kinemouse.utils.math_utils import euclidean_distance


class HandPose(Enum):
    UNKNOWN    = auto()
    OPEN_HAND  = auto()
    FIST       = auto()
    PEACE      = auto()
    THUMBS_UP  = auto()
    PINCH      = auto()   # already handled by FSM but included for completeness


def _tip_above_pip(landmarks, tip_idx: int, pip_idx: int) -> bool:
    """Returns True if fingertip is above its PIP joint (finger extended)."""
    return landmarks[tip_idx].y < landmarks[pip_idx].y


def classify_pose(landmarks: List) -> HandPose:
    """
    Classify the current hand pose from MediaPipe landmarks.
    Returns a HandPose enum value.
    """
    if landmarks is None:
        return HandPose.UNKNOWN

    # Check which fingers are extended (tip above PIP joint in normalized coords)
    # MediaPipe y: 0 = top of frame, 1 = bottom
    index_ext  = _tip_above_pip(landmarks, 8,  6)
    middle_ext = _tip_above_pip(landmarks, 12, 10)
    ring_ext   = _tip_above_pip(landmarks, 16, 14)
    pinky_ext  = _tip_above_pip(landmarks, 20, 18)

    # Thumb: compare tip x to MCP x (for right hand, tip.x < mcp.x = extended)
    thumb_ext  = abs(landmarks[4].x - landmarks[2].x) > 0.04

    extended = [index_ext, middle_ext, ring_ext, pinky_ext]
    num_extended = sum(extended)

    if num_extended == 0 and not thumb_ext:
        return HandPose.FIST

    if num_extended == 4 and thumb_ext:
        return HandPose.OPEN_HAND

    if index_ext and middle_ext and not ring_ext and not pinky_ext and not thumb_ext:
        return HandPose.PEACE

    if thumb_ext and num_extended == 0:
        return HandPose.THUMBS_UP

    return HandPose.UNKNOWN
