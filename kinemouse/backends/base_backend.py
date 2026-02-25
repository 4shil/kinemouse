"""
BaseBackend — Abstract interface all OS backends must implement.
Layer 3 contract.
"""

from abc import ABC, abstractmethod
from typing import Tuple
from kinemouse.state.events import MouseEvent, EventType
from kinemouse.utils.config import KineMouseConfig


class BaseBackend(ABC):
    """
    Abstract OS backend.
    Subclass this for each platform (Windows, macOS, Linux X11, Linux Wayland).
    """

    def __init__(self, config: KineMouseConfig):
        self.config = config

    @abstractmethod
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Return (width, height) of the primary display in pixels."""

    @abstractmethod
    def move(self, x: int, y: int) -> None:
        """Move the OS cursor to absolute screen position (x, y)."""

    @abstractmethod
    def click(self, x: int, y: int) -> None:
        """Perform a single left mouse click at (x, y)."""

    @abstractmethod
    def right_click(self, x: int, y: int) -> None:
        """Perform a right mouse click at (x, y)."""

    @abstractmethod
    def mouse_down(self, x: int, y: int) -> None:
        """Press and hold the left mouse button at (x, y) — begin drag."""

    @abstractmethod
    def mouse_up(self, x: int, y: int) -> None:
        """Release the left mouse button at (x, y) — end drag."""

    def dispatch(self, event: MouseEvent) -> None:
        """
        Dispatch a MouseEvent to the appropriate OS action.
        This is the single entry point called by the main loop.
        """
        if event.position is None and event.type not in (EventType.IDLE,):
            return

        pos = event.position or (0, 0)

        if event.type == EventType.MOVE:
            self.move(*pos)
        elif event.type == EventType.CLICK:
            self.click(*pos)
        elif event.type == EventType.RIGHT_CLICK:
            self.right_click(*pos)
        elif event.type == EventType.MOUSE_DOWN:
            self.mouse_down(*pos)
        elif event.type == EventType.MOUSE_UP:
            self.mouse_up(*pos)
        # IDLE → no-op
