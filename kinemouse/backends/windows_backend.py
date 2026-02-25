"""
Windows Backend — uses pynput for cursor control on Windows 10/11.
"""

from typing import Tuple
from pynput.mouse import Button, Controller
from kinemouse.backends.base_backend import BaseBackend
from kinemouse.utils.config import KineMouseConfig

class WindowsBackend(BaseBackend):
    def __init__(self, config: KineMouseConfig):
        super().__init__(config)
        self._mouse = Controller()

    def get_screen_resolution(self) -> Tuple[int, int]:
        try:
            import ctypes
            user32 = ctypes.windll.user32  # type: ignore
            user32.SetProcessDPIAware()
            return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
        except Exception:
            return (1920, 1080)

    def move(self, x: int, y: int) -> None:
        self._mouse.position = (x, y)

    def click(self, x: int, y: int) -> None:
        self._mouse.position = (x, y)
        self._mouse.click(Button.left, 1)

    def right_click(self, x: int, y: int) -> None:
        self._mouse.position = (x, y)
        self._mouse.click(Button.right, 1)

    def mouse_down(self, x: int, y: int) -> None:
        self._mouse.position = (x, y)
        self._mouse.press(Button.left)

    def mouse_up(self, x: int, y: int) -> None:
        self._mouse.position = (x, y)
        self._mouse.release(Button.left)
