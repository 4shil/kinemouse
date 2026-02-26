"""Unit tests for GestureClassifier — static hand pose recognition."""

import pytest
from unittest.mock import MagicMock
from kinemouse.state.gesture_classifier import classify_pose, HandPose


def make_lm(positions: dict) -> list:
    """Create 21 mock landmarks. positions = {idx: (x, y)}"""
    lm = [MagicMock() for _ in range(21)]
    for idx, (x, y) in positions.items():
        lm[idx].x = x
        lm[idx].y = y
    # default others
    for i in range(21):
        if not hasattr(lm[i], 'x') or lm[i].x is MagicMock:
            lm[i].x = 0.5
            lm[i].y = 0.5
    return lm


def make_fist():
    """All fingertips below their PIP joints (bent fingers)."""
    lm = [MagicMock() for _ in range(21)]
    for i in range(21):
        lm[i].x = 0.5
        lm[i].y = 0.5
    # tips below PIPs (y larger = lower in frame)
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        lm[tip].y = 0.8   # tip is lower
        lm[pip].y = 0.6   # pip is higher
    # thumb not extended
    lm[4].x = 0.5
    lm[2].x = 0.5
    return lm


def make_open_hand():
    """All fingertips above PIP joints (all fingers extended)."""
    lm = [MagicMock() for _ in range(21)]
    for i in range(21):
        lm[i].x = 0.5
        lm[i].y = 0.5
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        lm[tip].y = 0.2
        lm[pip].y = 0.5
    lm[4].x = 0.3   # thumb extended (far from MCP)
    lm[2].x = 0.5
    return lm


def test_none_returns_unknown():
    assert classify_pose(None) == HandPose.UNKNOWN


def test_fist_detection():
    lm = make_fist()
    pose = classify_pose(lm)
    assert pose == HandPose.FIST


def test_open_hand_detection():
    lm = make_open_hand()
    pose = classify_pose(lm)
    assert pose == HandPose.OPEN_HAND
