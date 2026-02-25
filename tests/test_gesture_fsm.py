"""
Unit tests for GestureFSM — state machine logic using mock landmarks.
"""

import time
import pytest
from unittest.mock import MagicMock

from kinemouse.utils.config import KineMouseConfig
from kinemouse.state.gesture_fsm import GestureFSM, FSMState
from kinemouse.state.events import EventType


SCREEN_RES = (1920, 1080)


def make_landmarks(thumb_x=0.5, thumb_y=0.5, index_x=0.5, index_y=0.5,
                   middle_x=0.6, middle_y=0.6, wrist_x=0.5, wrist_y=0.8,
                   knuckle_x=0.5, knuckle_y=0.6):
    """Create mock landmark list matching MediaPipe layout."""
    lm = [MagicMock() for _ in range(21)]
    # Wrist (0)
    lm[0].x, lm[0].y = wrist_x, wrist_y
    # Index knuckle (5)
    lm[5].x, lm[5].y = knuckle_x, knuckle_y
    # Thumb tip (4)
    lm[4].x, lm[4].y = thumb_x, thumb_y
    # Index tip (8)
    lm[8].x, lm[8].y = index_x, index_y
    # Middle tip (12)
    lm[12].x, lm[12].y = middle_x, middle_y
    return lm


def test_idle_on_no_landmarks():
    fsm = GestureFSM(KineMouseConfig(), SCREEN_RES)
    event = fsm.process(None)
    assert event.type == EventType.IDLE


def test_move_when_pinching_index():
    cfg = KineMouseConfig()
    fsm = GestureFSM(cfg, SCREEN_RES)
    # Pinching: thumb and index very close, well within 15% of dref
    lm = make_landmarks(thumb_x=0.5, thumb_y=0.5, index_x=0.501, index_y=0.5,
                        wrist_x=0.5, wrist_y=0.8, knuckle_x=0.5, knuckle_y=0.6)
    event = fsm.process(lm)
    assert event.type == EventType.MOVE


def test_right_click_on_middle_pinch():
    cfg = KineMouseConfig()
    fsm = GestureFSM(cfg, SCREEN_RES)
    # Middle finger pinch: thumb close to middle, far from index
    lm = make_landmarks(thumb_x=0.5, thumb_y=0.5,
                        index_x=0.7, index_y=0.7,       # far — not pinching index
                        middle_x=0.501, middle_y=0.5,   # close — pinching middle
                        wrist_x=0.5, wrist_y=0.8, knuckle_x=0.5, knuckle_y=0.6)
    event = fsm.process(lm)
    assert event.type == EventType.RIGHT_CLICK


def test_fsm_state_starts_idle():
    fsm = GestureFSM(KineMouseConfig(), SCREEN_RES)
    assert fsm._state == FSMState.IDLE
