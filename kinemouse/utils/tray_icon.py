"""
TrayIcon — optional system tray icon for KineMouse.

Shows current state (running/paused) in the system tray with a
context menu to pause, calibrate, or quit.

Requires: pystray + PIL/Pillow
Install: pip install pystray pillow

If pystray is not installed, this module gracefully does nothing
and KineMouse continues without a tray icon.

Usage:
    tray = TrayIcon(state)
    tray.start()   # non-blocking, runs in background thread
    ...
    tray.stop()
"""

from __future__ import annotations
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kinemouse.utils.hotkeys import HotkeyState


def _make_icon_image(color: tuple):
    """Create a simple 64x64 colored icon image."""
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (64, 64), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        draw.ellipse([8, 8, 56, 56], fill=color)
        return img
    except ImportError:
        return None


class TrayIcon:
    """
    System tray icon with pause/resume, calibrate, and quit actions.
    Gracefully no-ops if pystray or pillow not installed.
    """

    def __init__(self, state: "HotkeyState"):
        self._state = state
        self._icon = None
        self._thread: threading.Thread = None

    def start(self):
        """Start tray icon in background thread. No-op if dependencies missing."""
        try:
            import pystray
            icon_img = _make_icon_image((0, 200, 100))
            if icon_img is None:
                return

            menu = pystray.Menu(
                pystray.MenuItem(
                    "Pause / Resume",
                    lambda icon, item: self._toggle_pause(),
                ),
                pystray.MenuItem(
                    "Calibrate",
                    lambda icon, item: self._trigger_calibrate(),
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "Quit KineMouse",
                    lambda icon, item: self._quit(icon),
                ),
            )

            self._icon = pystray.Icon("KineMouse", icon_img, "KineMouse", menu)
            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
        except ImportError:
            pass   # pystray not installed — silent no-op

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _toggle_pause(self):
        self._state.paused = not self._state.paused
        self._update_icon()

    def _trigger_calibrate(self):
        self._state.run_calibration = True

    def _quit(self, icon):
        self._state.should_quit = True
        icon.stop()

    def _update_icon(self):
        if self._icon is None:
            return
        try:
            color = (200, 80, 80) if self._state.paused else (0, 200, 100)
            self._icon.icon = _make_icon_image(color)
        except Exception:
            pass
