"""
FPS counter utility for KineMouse.
Tracks real-time frame rate using a rolling window for smooth display.

Usage:
    counter = FPSCounter(window=30)
    while True:
        counter.tick()
        print(f"{counter.fps:.1f} fps")
"""

import time
from collections import deque


class FPSCounter:
    """
    Rolling-window FPS counter.
    More accurate than simple frame/elapsed because it adapts
    to recent performance rather than averaging over the whole run.
    """

    def __init__(self, window: int = 30):
        """
        window: number of recent frames to average over.
        Larger window = smoother number. Smaller = more reactive.
        """
        self._window = window
        self._timestamps: deque = deque(maxlen=window)

    def tick(self):
        """Call once per frame."""
        self._timestamps.append(time.monotonic())

    @property
    def fps(self) -> float:
        """Current rolling-average FPS."""
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        if elapsed <= 0:
            return 0.0
        return (len(self._timestamps) - 1) / elapsed

    def reset(self):
        self._timestamps.clear()

    def __str__(self) -> str:
        return f"{self.fps:.1f} fps"
