"""
Linux Wayland Backend — uses evdev/uinput to create a virtual kernel-level mouse device.
This bypasses Wayland's security restrictions by operating at the kernel level.

Requires:
    - evdev package (pip install evdev)
    - User must be in 'input' group OR run with uinput access:
        sudo usermod -aG input $USER
        echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | sudo tee /etc/udev/rules.d/99-kinemouse.rules
        sudo udevadm control --reload-rules && sudo udevadm trigger
"""

import os
from typing import Tuple

from kinemouse.backends.base_backend import BaseBackend
from kinemouse.utils.config import KineMouseConfig


class LinuxWaylandBackend(BaseBackend):
    """
    Mouse backend for Linux Wayland using evdev uinput virtual device.
    Creates a kernel-level virtual mouse, bypassing Wayland compositor restrictions.
    """

    def __init__(self, config: KineMouseConfig):
        super().__init__(config)
        self._screen_res = self._detect_resolution()
        self._device = self._create_uinput_device()

    def _detect_resolution(self) -> Tuple[int, int]:
        """Detect screen resolution using wayland tools or fallback."""
        try:
            import subprocess
            out = subprocess.check_output(
                ["wlr-randr"], text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                if "current" in line.lower() and "x" in line:
                    parts = line.split()
                    for p in parts:
                        if "x" in p:
                            w, h = p.split("x")
                            return (int(w), int(h.split("@")[0]))
        except Exception:
            pass
        return (1920, 1080)

    def _create_uinput_device(self):
        """Create a uinput virtual absolute mouse device."""
        try:
            import evdev
            from evdev import UInput, AbsInfo, ecodes as e

            cap = {
                e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE],
                e.EV_ABS: [
                    (e.ABS_X, AbsInfo(value=0, min=0, max=self._screen_res[0], fuzz=0, flat=0, resolution=1)),
                    (e.ABS_Y, AbsInfo(value=0, min=0, max=self._screen_res[1], fuzz=0, flat=0, resolution=1)),
                ],
                e.EV_SYN: [],
            }
            return UInput(cap, name="KineMouse Virtual Pointer", version=0x3)
        except Exception as ex:
            raise RuntimeError(
                f"Could not create uinput device: {ex}\n"
                "Ensure you are in the 'input' group and uinput rules are set."
            ) from ex

    def get_screen_resolution(self) -> Tuple[int, int]:
        return self._screen_res

    def _emit(self, x: int, y: int):
        """Move the virtual pointer to absolute position."""
        from evdev import ecodes as e
        self._device.write(e.EV_ABS, e.ABS_X, x)
        self._device.write(e.EV_ABS, e.ABS_Y, y)
        self._device.syn()

    def move(self, x: int, y: int) -> None:
        self._emit(x, y)

    def click(self, x: int, y: int) -> None:
        from evdev import ecodes as e
        self._emit(x, y)
        self._device.write(e.EV_KEY, e.BTN_LEFT, 1)
        self._device.syn()
        self._device.write(e.EV_KEY, e.BTN_LEFT, 0)
        self._device.syn()

    def right_click(self, x: int, y: int) -> None:
        from evdev import ecodes as e
        self._emit(x, y)
        self._device.write(e.EV_KEY, e.BTN_RIGHT, 1)
        self._device.syn()
        self._device.write(e.EV_KEY, e.BTN_RIGHT, 0)
        self._device.syn()

    def mouse_down(self, x: int, y: int) -> None:
        from evdev import ecodes as e
        self._emit(x, y)
        self._device.write(e.EV_KEY, e.BTN_LEFT, 1)
        self._device.syn()

    def mouse_up(self, x: int, y: int) -> None:
        from evdev import ecodes as e
        self._emit(x, y)
        self._device.write(e.EV_KEY, e.BTN_LEFT, 0)
        self._device.syn()
