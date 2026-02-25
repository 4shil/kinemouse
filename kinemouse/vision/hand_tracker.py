"""
HandTracker — Layer 1: Vision Engine.

Responsibilities:
- Capture webcam frames via OpenCV (30 FPS)
- Run MediaPipe Hands to extract 3D hand landmarks
- Expose a clean per-frame result object to Layer 2
"""

import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

from kinemouse.utils.config import KineMouseConfig


@dataclass
class HandFrame:
    """Result of processing one camera frame."""
    landmarks: Optional[List] = None   # MediaPipe NormalizedLandmarkList
    raw_frame: Optional[np.ndarray] = None
    annotated_frame: Optional[np.ndarray] = None
    found: bool = False


class HandTracker:
    """
    Captures webcam frames and extracts hand landmarks using MediaPipe.
    Designed to run in its own thread at ~30 FPS.
    """

    def __init__(self, config: KineMouseConfig):
        self.config = config
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.max_num_hands,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )
        self._cap: Optional[cv2.VideoCapture] = None

    def start(self) -> bool:
        """Open the webcam capture. Returns True if successful."""
        self._cap = cv2.VideoCapture(self.config.camera_index)
        if not self._cap.isOpened():
            return False
        self._cap.set(cv2.CAP_PROP_FPS, self.config.capture_fps)
        return True

    def stop(self):
        """Release webcam and MediaPipe resources."""
        if self._cap:
            self._cap.release()
        self._hands.close()

    def next_frame(self) -> HandFrame:
        """
        Capture and process one frame.
        Returns a HandFrame with landmarks if a hand is detected.
        """
        if not self._cap or not self._cap.isOpened():
            return HandFrame()

        ret, frame = self._cap.read()
        if not ret:
            return HandFrame()

        if self.config.flip_horizontal:
            frame = cv2.flip(frame, 1)

        # MediaPipe expects RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)
        rgb.flags.writeable = True

        annotated = frame.copy()
        landmarks = None
        found = False

        if results.multi_hand_landmarks:
            hand_lm = results.multi_hand_landmarks[0]
            self._mp_draw.draw_landmarks(
                annotated,
                hand_lm,
                self._mp_hands.HAND_CONNECTIONS,
            )
            landmarks = hand_lm.landmark
            found = True

        return HandFrame(
            landmarks=landmarks,
            raw_frame=frame,
            annotated_frame=annotated,
            found=found,
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
