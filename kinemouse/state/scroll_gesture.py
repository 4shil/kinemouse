"""
ScrollGesture — detects Ring+Thumb pinch and maps hand elevation to scroll events.

PRD Phase 2 feature: Pinching Ring Finger (16) + Thumb (4), then moving hand
up/down triggers scroll up/down.

Usage:
    scroller = ScrollGesture(config)
    result = scroller.process(landmarks, dref)
    # result is ScrollEvent or None
"""

import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List

from kinemouse.utils.config import KineMouseConfig
from kinemouse.utils.math_utils import is_pinching


class ScrollDirection(Enum):
    UP   = auto()
    DOWN = auto()


@dataclass
class ScrollEvent:
    direction: ScrollDirection
    magnitude: int = 1   # scroll ticks


class ScrollGesture:
    """
    Detects Ring+Thumb pinch and uses hand Y elevation to determine scroll direction.
    Fires scroll events at a fixed interval to prevent scroll spam.
    """

    def __init__(self, config: KineMouseConfig, scroll_interval_ms: int = 120):
        self.config = config
        self._interval = scroll_interval_ms / 1000.0
        self._last_fire = 0.0
        self._baseline_y: Optional[float] = None   # Y when pinch started
        self._pinching = False

    def process(self, landmarks: List, dref: float) -> Optional[ScrollEvent]:
        """
        Call each frame. Returns ScrollEvent if scrolling, else None.
        landmarks: MediaPipe landmark list
        dref: precomputed D_ref for this frame
        """
        if landmarks is None or dref == 0:
            self._reset()
            return None

        ring_pinch = is_pinching(
            landmarks,
            self.config.THUMB_TIP,
            self.config.RING_TIP,
            dref,
            self.config.pinch_threshold
        )

        # Also ensure index/middle are NOT pinching to avoid conflicts
        index_pinch = is_pinching(landmarks, self.config.THUMB_TIP, self.config.INDEX_TIP, dref, self.config.pinch_threshold)

        if ring_pinch and not index_pinch:
            thumb_y = landmarks[self.config.THUMB_TIP].y

            if not self._pinching:
                # Pinch just started — record baseline
                self._pinching = True
                self._baseline_y = thumb_y
                return None

            # Measure elevation delta from baseline (normalized 0..1, inverted: up = lower y)
            delta = (self._baseline_y or thumb_y) - thumb_y  # positive = moved up
            dead_zone = 0.02  # 2% of frame height, ignore tiny jitter

            if abs(delta) < dead_zone:
                return None

            now = time.monotonic()
            if now - self._last_fire < self._interval:
                return None

            self._last_fire = now
            direction = ScrollDirection.UP if delta > 0 else ScrollDirection.DOWN
            magnitude = max(1, int(abs(delta) / 0.04))  # scale: 4% per tick
            return ScrollEvent(direction=direction, magnitude=magnitude)

        else:
            self._reset()
            return None

    def _reset(self):
        self._pinching = False
        self._baseline_y = None
