"""
MultiHandTracker — extends HandTracker to track up to 2 hands simultaneously.

Right hand → primary mouse control (existing FSM)
Left hand  → secondary actions (scroll, modifier gestures)

Each hand is identified by MediaPipe's handedness label.
"""

import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from kinemouse.utils.config import KineMouseConfig


@dataclass
class MultiHandFrame:
    """Result of processing one camera frame with up to 2 hands."""
    right_landmarks: Optional[List] = None
    left_landmarks:  Optional[List] = None
    annotated_frame: Optional[np.ndarray] = None
    raw_frame:       Optional[np.ndarray] = None
    right_found:     bool = False
    left_found:      bool = False

    @property
    def any_found(self) -> bool:
        return self.right_found or self.left_found


class MultiHandTracker:
    """
    Tracks both hands separately, returning per-hand landmark lists.
    Right hand landmarks go to the primary gesture FSM.
    Left hand landmarks go to secondary gesture processing (scroll, etc.)
    """

    def __init__(self, config: KineMouseConfig):
        self.config = config
        self._mp_hands = mp.solutions.hands
        self._mp_draw  = mp.solutions.drawing_utils
        self._hands    = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )
        self._cap: Optional[cv2.VideoCapture] = None

    def start(self) -> bool:
        self._cap = cv2.VideoCapture(self.config.camera_index)
        if not self._cap.isOpened():
            return False
        self._cap.set(cv2.CAP_PROP_FPS, self.config.capture_fps)
        return True

    def stop(self):
        if self._cap:
            self._cap.release()
        self._hands.close()

    def next_frame(self) -> MultiHandFrame:
        if not self._cap or not self._cap.isOpened():
            return MultiHandFrame()

        ret, frame = self._cap.read()
        if not ret:
            return MultiHandFrame()

        if self.config.flip_horizontal:
            frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)
        rgb.flags.writeable = True

        annotated = frame.copy()
        result = MultiHandFrame(raw_frame=frame, annotated_frame=annotated)

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_lm, handedness in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                label = handedness.classification[0].label  # "Left" or "Right"
                self._mp_draw.draw_landmarks(
                    annotated, hand_lm, self._mp_hands.HAND_CONNECTIONS
                )
                # Note: MediaPipe labels are from camera POV; flip because we mirror
                if label == "Left":
                    result.right_landmarks = hand_lm.landmark
                    result.right_found = True
                else:
                    result.left_landmarks = hand_lm.landmark
                    result.left_found = True

        result.annotated_frame = annotated
        return result

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
