"""
Mouse event definitions for KineMouse.
Layer 2 emits these events; Layer 3 executes them.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Tuple, Optional


class EventType(Enum):
    """All possible mouse events emitted by the state machine."""
    IDLE        = auto()   # No action — hand open or not detected
    MOVE        = auto()   # Move cursor to (x, y)
    CLICK       = auto()   # Single left click
    MOUSE_DOWN  = auto()   # Begin drag (mouse button held)
    MOUSE_UP    = auto()   # End drag (mouse button released)
    RIGHT_CLICK = auto()   # Right click


@dataclass
class MouseEvent:
    """A single mouse event with optional screen coordinates."""
    type: EventType
    position: Optional[Tuple[int, int]] = None  # Screen (x, y) in pixels

    def __repr__(self):
        if self.position:
            return f"MouseEvent({self.type.name}, pos={self.position})"
        return f"MouseEvent({self.type.name})"


# Convenience constructors
def idle_event() -> MouseEvent:
    return MouseEvent(EventType.IDLE)

def move_event(x: int, y: int) -> MouseEvent:
    return MouseEvent(EventType.MOVE, position=(x, y))

def click_event(x: int, y: int) -> MouseEvent:
    return MouseEvent(EventType.CLICK, position=(x, y))

def mouse_down_event(x: int, y: int) -> MouseEvent:
    return MouseEvent(EventType.MOUSE_DOWN, position=(x, y))

def mouse_up_event(x: int, y: int) -> MouseEvent:
    return MouseEvent(EventType.MOUSE_UP, position=(x, y))

def right_click_event(x: int, y: int) -> MouseEvent:
    return MouseEvent(EventType.RIGHT_CLICK, position=(x, y))
