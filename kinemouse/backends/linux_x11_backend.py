"""
Linux X11 Backend — uses pynput for cursor control on X11/Xorg.
"""

import subprocess
from typing import Tuple
from pynput.mouse import Button, Controller

from kinemouse.backends.base_backend import BaseBackend
from kinemouse.utils.config import KineMouseConfig


class LinuxX11Backend(BaseBackend):
    """Mouse backend for Linux X11 (Xorg) using pynput."""

    def __init__(self, config: KineMouseConfig):
        super().__init__(config)
        self._mouse = Controller()

    def get_screen_resolution(self) -> Tuple[int, int]:
        """Read screen resolution using xrandr."""
        try:
            out = subprocess.check_output(
                ["xrandr", "--query"], text=True
            )
            for line in out.splitlines():
                if " connected" in line and "x" in line:
                    for token in line.split():
                        if "x" in token and "+" in token:
                            w, rest = token.split("x", 1)
                            h = rest.split("+")[0]
                            return (int(w), int(h))
        except Exception:
            pass
        return (1920, 1080)  # safe fallback

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
