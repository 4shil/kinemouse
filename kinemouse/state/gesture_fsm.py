"""
GestureFSM — Layer 2: State Machine.

Translates raw hand landmarks into MouseEvents using:
- Dynamic thresholding (D_ref normalization)
- EMA smoothing
- Double-pinch state machine (400ms window)
- Right-click detection (Thumb + Middle)
"""

import time
from enum import Enum, auto
from typing import Optional, Tuple

from kinemouse.utils.config import KineMouseConfig
from kinemouse.utils.math_utils import (
    compute_dref, is_pinching, midpoint, ema_smooth, map_to_screen
)
from kinemouse.state.events import (
    MouseEvent, EventType,
    idle_event, move_event, click_event,
    mouse_down_event, mouse_up_event, right_click_event
)


class FSMState(Enum):
    """Internal states of the double-pinch state machine."""
    IDLE         = auto()   # Waiting — hand open
    PINCH_1      = auto()   # First pinch detected — cursor moves
    RELEASE_WAIT = auto()   # Pinch released — waiting for 2nd within 400ms
    DRAG_MODE    = auto()   # Drag active — mouse button held


class GestureFSM:
    """
    Core state machine that processes one HandFrame worth of landmarks
    and returns a MouseEvent for the OS backend to execute.
    """

    def __init__(self, config: KineMouseConfig, screen_resolution: Tuple[int, int]):
        self.config = config
        self.screen_res = screen_resolution

        # FSM internals
        self._state = FSMState.IDLE
        self._release_time: Optional[float] = None   # Timestamp of first pinch release

        # EMA state
        self._smoothed: Optional[Tuple[float, float]] = None

    def process(self, landmarks) -> MouseEvent:
        """
        Process one frame of landmarks and return the appropriate MouseEvent.
        Call this once per captured frame.
        """
        if landmarks is None:
            self._state = FSMState.IDLE
            self._smoothed = None
            return idle_event()

        cfg = self.config

        # --- Layer 1 math ---
        dref = compute_dref(landmarks)
        if dref == 0:
            return idle_event()

        pinching_index = is_pinching(landmarks, cfg.THUMB_TIP, cfg.INDEX_TIP, dref, cfg.pinch_threshold)
        pinching_middle = is_pinching(landmarks, cfg.THUMB_TIP, cfg.MIDDLE_TIP, dref, cfg.pinch_threshold)

        # Raw pinch midpoint
        thumb = (landmarks[cfg.THUMB_TIP].x, landmarks[cfg.THUMB_TIP].y)
        index = (landmarks[cfg.INDEX_TIP].x, landmarks[cfg.INDEX_TIP].y)
        raw_mid = midpoint(thumb, index)

        # EMA smoothing
        if self._smoothed is None:
            self._smoothed = raw_mid
        else:
            self._smoothed = ema_smooth(raw_mid, self._smoothed, cfg.ema_alpha)

        screen_pos = map_to_screen(self._smoothed, cfg.active_box, self.screen_res)

        # --- Right click (Thumb + Middle) — checked in any state ---
        if pinching_middle and not pinching_index:
            self._state = FSMState.IDLE
            return right_click_event(*screen_pos)

        # --- Double-pinch FSM ---
        now = time.monotonic()

        if self._state == FSMState.IDLE:
            if pinching_index:
                self._state = FSMState.PINCH_1
                return move_event(*screen_pos)
            return idle_event()

        elif self._state == FSMState.PINCH_1:
            if pinching_index:
                return move_event(*screen_pos)
            else:
                # Pinch released — start 400ms countdown
                self._state = FSMState.RELEASE_WAIT
                self._release_time = now
                return move_event(*screen_pos)

        elif self._state == FSMState.RELEASE_WAIT:
            elapsed_ms = (now - self._release_time) * 1000  # type: ignore
            if pinching_index:
                # Second pinch before 400ms → enter DRAG
                self._state = FSMState.DRAG_MODE
                return mouse_down_event(*screen_pos)
            elif elapsed_ms > cfg.double_pinch_window_ms:
                # 400ms expired → single click
                self._state = FSMState.IDLE
                self._release_time = None
                return click_event(*screen_pos)
            else:
                return move_event(*screen_pos)

        elif self._state == FSMState.DRAG_MODE:
            if pinching_index:
                return move_event(*screen_pos)
            else:
                # Released during drag → mouse up
                self._state = FSMState.IDLE
                return mouse_up_event(*screen_pos)

        return idle_event()

    def reset(self):
        """Reset FSM to IDLE (e.g., on hand lost)."""
        self._state = FSMState.IDLE
        self._release_time = None
        self._smoothed = None
