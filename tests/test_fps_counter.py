"""Unit tests for FPSCounter."""

import time
import pytest
from kinemouse.utils.fps_counter import FPSCounter


def test_fps_zero_at_start():
    c = FPSCounter()
    assert c.fps == 0.0


def test_fps_zero_single_tick():
    c = FPSCounter()
    c.tick()
    assert c.fps == 0.0


def test_fps_reasonable_after_ticks():
    c = FPSCounter(window=10)
    for _ in range(10):
        c.tick()
        time.sleep(0.01)
    fps = c.fps
    assert 50 < fps < 200  # ~100 fps with 10ms sleep


def test_fps_reset():
    c = FPSCounter()
    for _ in range(5):
        c.tick()
    c.reset()
    assert c.fps == 0.0


def test_fps_rolling_window():
    """Window size limits how many timestamps are kept."""
    c = FPSCounter(window=5)
    for _ in range(20):
        c.tick()
    assert len(c._timestamps) == 5


def test_fps_str():
    c = FPSCounter()
    assert "fps" in str(c)
