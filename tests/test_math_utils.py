"""Unit tests for math_utils — core geometry and EMA."""

import pytest
from kinemouse.utils.math_utils import (
    euclidean_distance, midpoint, ema_smooth, map_to_screen
)


def test_euclidean_distance_zero():
    assert euclidean_distance((0, 0), (0, 0)) == 0.0

def test_euclidean_distance_known():
    assert abs(euclidean_distance((0, 0), (3, 4)) - 5.0) < 1e-9

def test_midpoint():
    assert midpoint((0, 0), (4, 4)) == (2.0, 2.0)

def test_ema_smooth_alpha_1():
    """With alpha=1.0, smoothed == current."""
    result = ema_smooth((10, 20), (0, 0), alpha=1.0)
    assert result == (10.0, 20.0)

def test_ema_smooth_alpha_0():
    """With alpha=0.0, smoothed == previous."""
    result = ema_smooth((10, 20), (5, 7), alpha=0.0)
    assert result == (5.0, 7.0)

def test_ema_smooth_midpoint():
    result = ema_smooth((10, 10), (0, 0), alpha=0.5)
    assert result == (5.0, 5.0)

def test_map_to_screen_center():
    """Center of active box should map to center of screen."""
    box = (0.25, 0.20, 0.75, 0.80)
    res = (1920, 1080)
    x, y = map_to_screen((0.50, 0.50), box, res)
    assert x == 960
    assert y == 540

def test_map_to_screen_clamp():
    """Points outside active box should be clamped."""
    box = (0.25, 0.20, 0.75, 0.80)
    res = (1920, 1080)
    # Far outside box → should clamp to edge
    x, y = map_to_screen((0.0, 0.0), box, res)
    assert x == 0 and y == 0
