"""Unit tests for ScrollGesture — ring+thumb scroll detection."""

import pytest
from unittest.mock import MagicMock
from kinemouse.utils.config import KineMouseConfig
from kinemouse.state.scroll_gesture import ScrollGesture, ScrollDirection


def make_landmarks(thumb_x=0.5, thumb_y=0.5,
                   ring_x=0.6, ring_y=0.6,
                   index_x=0.8, index_y=0.8,
                   wrist_x=0.5, wrist_y=0.9,
                   knuckle_x=0.5, knuckle_y=0.65):
    lm = [MagicMock() for _ in range(21)]
    lm[0].x, lm[0].y = wrist_x, wrist_y
    lm[4].x, lm[4].y = thumb_x, thumb_y
    lm[5].x, lm[5].y = knuckle_x, knuckle_y
    lm[8].x, lm[8].y = index_x, index_y
    lm[12].x, lm[12].y = 0.7, 0.7
    lm[16].x, lm[16].y = ring_x, ring_y
    return lm


def test_no_scroll_when_no_landmarks():
    sg = ScrollGesture(KineMouseConfig())
    result = sg.process(None, 0.2)
    assert result is None


def test_no_scroll_when_not_pinching():
    sg = ScrollGesture(KineMouseConfig())
    lm = make_landmarks(thumb_x=0.5, ring_x=0.8)  # far apart
    result = sg.process(lm, 0.2)
    assert result is None


def test_scroll_up_detected():
    sg = ScrollGesture(KineMouseConfig(), scroll_interval_ms=0)
    # First frame: start pinch, set baseline
    lm = make_landmarks(thumb_x=0.5, thumb_y=0.5, ring_x=0.501, ring_y=0.5)
    sg.process(lm, 0.2)
    # Second frame: move hand up (lower y value)
    lm2 = make_landmarks(thumb_x=0.5, thumb_y=0.42, ring_x=0.501, ring_y=0.42)
    result = sg.process(lm2, 0.2)
    assert result is not None
    assert result.direction == ScrollDirection.UP
