"""Unit tests for MouseEvent types."""

from kinemouse.state.events import (
    EventType, move_event, click_event, right_click_event,
    mouse_down_event, mouse_up_event, idle_event
)

def test_move_event():
    e = move_event(100, 200)
    assert e.type == EventType.MOVE
    assert e.position == (100, 200)

def test_click_event():
    e = click_event(50, 60)
    assert e.type == EventType.CLICK

def test_idle_event():
    e = idle_event()
    assert e.type == EventType.IDLE
    assert e.position is None

def test_right_click_event():
    e = right_click_event(300, 400)
    assert e.type == EventType.RIGHT_CLICK
    assert e.position == (300, 400)
