"""
macOS Backend — uses pynput (Quartz CoreGraphics) for cursor control on macOS 13+.
"""

from typing import Tuple
from pynput.mouse import Button, Controller
from kinemouse.backends.base_backend import BaseBackend
from kinemouse.utils.config import KineMouseConfig

class MacOSBackend(BaseBackend):
    def __init__(self, config: KineMouseConfig):
        super().__init__(config)
        self._mouse = Controller()

    def get_screen_resolution(self) -> Tuple[int, int]:
        try:
            import subprocess
            out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True)
            for line in out.splitlines():
                if "Resolution" in line:
                    parts = line.split(":")[-1].strip().split(" x ")
                    if len(parts) == 2:
                        return (int(parts[0].strip()), int(parts[1].strip().split(" ")[0]))
        except Exception:
            pass
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
