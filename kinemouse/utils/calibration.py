"""
Calibration — interactive first-run calibration wizard.

Guides the user to move their hand to the four corners of the active zone
to compute a personalized active_box that matches their natural range of motion.

Usage:
    from kinemouse.utils.calibration import run_calibration
    box = run_calibration(tracker, config)
    # returns (x_min, y_min, x_max, y_max) normalized coords
"""

import time
import cv2
import numpy as np
from typing import Tuple, List, Optional

from kinemouse.vision.hand_tracker import HandTracker
from kinemouse.utils.config import KineMouseConfig
from kinemouse.utils.math_utils import midpoint


_INSTRUCTIONS = [
    ("TOP-LEFT",     "Move your pinched hand to the TOP-LEFT of your comfortable range"),
    ("TOP-RIGHT",    "Move your pinched hand to the TOP-RIGHT of your comfortable range"),
    ("BOTTOM-RIGHT", "Move your pinched hand to the BOTTOM-RIGHT of your comfortable range"),
    ("BOTTOM-LEFT",  "Move your pinched hand to the BOTTOM-LEFT of your comfortable range"),
]

_HOLD_SECONDS = 2.0   # how long to hold each position
_COUNTDOWN_COLOR = (0, 200, 255)
_TEXT_COLOR = (255, 255, 255)


def run_calibration(
    tracker: HandTracker,
    config: KineMouseConfig,
) -> Optional[Tuple[float, float, float, float]]:
    """
    Run the interactive calibration wizard using the webcam feed.
    Returns a normalized active_box tuple, or None if cancelled.
    Press 'q' at any time to cancel.
    """
    corners: List[Tuple[float, float]] = []
    cv2.namedWindow("KineMouse Calibration", cv2.WINDOW_NORMAL)

    for label, instruction in _INSTRUCTIONS:
        collected: List[Tuple[float, float]] = []
        start_time: Optional[float] = None
        holding = False

        while True:
            hand_frame = tracker.next_frame()
            frame = hand_frame.annotated_frame
            if frame is None:
                continue

            h, w = frame.shape[:2]
            overlay = frame.copy()

            # Instruction text
            cv2.putText(overlay, instruction, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, _TEXT_COLOR, 2, cv2.LINE_AA)
            cv2.putText(overlay, f"Corner: {label}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, _COUNTDOWN_COLOR, 2, cv2.LINE_AA)
            cv2.putText(overlay, "Pinch and HOLD for 2 seconds", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, _TEXT_COLOR, 1, cv2.LINE_AA)
            cv2.putText(overlay, "Press 'q' to cancel calibration", (10, h - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1, cv2.LINE_AA)

            if hand_frame.found and hand_frame.landmarks:
                lm = hand_frame.landmarks
                thumb = (lm[4].x, lm[4].y)
                index = (lm[8].x, lm[8].y)
                mid = midpoint(thumb, index)

                # Check pinch
                dist = ((thumb[0] - index[0])**2 + (thumb[1] - index[1])**2) ** 0.5
                pinching = dist < 0.06

                if pinching:
                    if not holding:
                        holding = True
                        start_time = time.monotonic()
                        collected.clear()

                    elapsed = time.monotonic() - (start_time or 0)
                    collected.append(mid)

                    # Progress bar
                    progress = min(elapsed / _HOLD_SECONDS, 1.0)
                    bar_w = int(progress * (w - 20))
                    cv2.rectangle(overlay, (10, h - 35), (10 + bar_w, h - 20), _COUNTDOWN_COLOR, -1)
                    cv2.putText(overlay, f"Hold... {elapsed:.1f}s", (10, h - 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, _COUNTDOWN_COLOR, 1)

                    if elapsed >= _HOLD_SECONDS:
                        # Average of collected positions
                        avg_x = sum(p[0] for p in collected) / len(collected)
                        avg_y = sum(p[1] for p in collected) / len(collected)
                        corners.append((avg_x, avg_y))
                        cv2.putText(overlay, "CAPTURED!", (w // 2 - 60, h // 2),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 100), 3)
                        cv2.imshow("KineMouse Calibration", overlay)
                        cv2.waitKey(600)
                        break
                else:
                    holding = False
                    start_time = None

            cv2.imshow("KineMouse Calibration", overlay)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                return None

    cv2.destroyAllWindows()

    if len(corners) < 4:
        return None

    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    box = (min(xs), min(ys), max(xs), max(ys))
    return box
