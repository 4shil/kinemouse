"""
FrameAnnotator — draws gesture state, FPS, active box, and debug info
onto the preview frame without polluting HandTracker logic.

Usage:
    annotator = FrameAnnotator(config)
    display_frame = annotator.draw(frame, event, fps)
"""

import cv2
import numpy as np
from typing import Tuple, Optional

from kinemouse.utils.config import KineMouseConfig
from kinemouse.state.events import MouseEvent, EventType


# Color palette (BGR)
_COLORS = {
    "idle":        (180, 180, 180),
    "move":        (0,   220, 100),
    "click":       (0,   200, 255),
    "right_click": (50,  50,  255),
    "drag":        (255, 120, 0),
    "mouse_up":    (200, 200, 0),
    "box":         (0,   255, 100),
    "fps":         (200, 200, 200),
    "crosshair":   (0,   255, 200),
}

_STATE_LABELS = {
    EventType.IDLE:        "IDLE",
    EventType.MOVE:        "MOVING",
    EventType.CLICK:       "CLICK",
    EventType.RIGHT_CLICK: "RIGHT CLICK",
    EventType.MOUSE_DOWN:  "DRAG START",
    EventType.MOUSE_UP:    "DRAG END",
}


class FrameAnnotator:
    """
    Draws HUD elements on top of the annotated webcam frame:
    - Active box boundary
    - Current gesture state (colored label)
    - FPS counter
    - Pinch midpoint crosshair (when MOVE/DRAG)
    - Screen coordinate being sent to OS
    """

    def __init__(self, config: KineMouseConfig):
        self.config = config

    def draw(
        self,
        frame: np.ndarray,
        event: MouseEvent,
        fps: float,
        smoothed_norm: Optional[Tuple[float, float]] = None,
    ) -> np.ndarray:
        """
        Draw all HUD elements onto frame (copy, non-destructive).
        smoothed_norm: optional normalized (0..1) smoothed pinch midpoint
        """
        out = frame.copy()
        h, w = out.shape[:2]

        self._draw_active_box(out, w, h)
        self._draw_state_label(out, event)
        self._draw_fps(out, fps)

        if smoothed_norm is not None and event.type in (
            EventType.MOVE, EventType.MOUSE_DOWN, EventType.MOUSE_UP
        ):
            self._draw_crosshair(out, smoothed_norm, w, h)

        if event.position is not None:
            self._draw_screen_coord(out, event.position)

        return out

    def _draw_active_box(self, frame, w, h):
        ab = self.config.active_box
        x1, y1 = int(ab[0] * w), int(ab[1] * h)
        x2, y2 = int(ab[2] * w), int(ab[3] * h)
        cv2.rectangle(frame, (x1, y1), (x2, y2), _COLORS["box"], 2)
        cv2.putText(frame, "active zone", (x1 + 4, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, _COLORS["box"], 1, cv2.LINE_AA)

    def _draw_state_label(self, frame, event: MouseEvent):
        label = _STATE_LABELS.get(event.type, event.type.name)
        color = _COLORS.get(event.type.name.lower(), (200, 200, 200))
        cv2.putText(frame, label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)

    def _draw_fps(self, frame, fps: float):
        text = f"{fps:.1f} fps"
        h = frame.shape[0]
        cv2.putText(frame, text, (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, _COLORS["fps"], 1, cv2.LINE_AA)

    def _draw_crosshair(self, frame, norm: Tuple[float, float], w: int, h: int):
        cx = int(norm[0] * w)
        cy = int(norm[1] * h)
        size = 12
        cv2.line(frame, (cx - size, cy), (cx + size, cy), _COLORS["crosshair"], 2)
        cv2.line(frame, (cx, cy - size), (cx, cy + size), _COLORS["crosshair"], 2)
        cv2.circle(frame, (cx, cy), 4, _COLORS["crosshair"], -1)

    def _draw_screen_coord(self, frame, pos: Tuple[int, int]):
        text = f"screen ({pos[0]}, {pos[1]})"
        h = frame.shape[0]
        cv2.putText(frame, text, (10, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)
