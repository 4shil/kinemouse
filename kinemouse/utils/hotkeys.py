"""
HotkeyListener — global keyboard hotkeys to control KineMouse at runtime.

Supported keys (configurable):
    ESC / 'q'   — quit KineMouse
    'p'         — pause / resume gesture tracking
    'c'         — run calibration wizard
    'd'         — toggle debug overlay

Usage:
    listener = HotkeyListener()
    listener.start()
    while True:
        if listener.should_quit:
            break
        if listener.paused:
            continue
        ...
    listener.stop()
"""

import threading
from dataclasses import dataclass, field


@dataclass
class HotkeyState:
    should_quit:      bool = False
    paused:           bool = False
    run_calibration:  bool = False
    debug_overlay:    bool = False


class HotkeyListener:
    """
    Listens for keyboard events in a background thread.
    Uses pynput so it works without a focused window.
    """

    def __init__(self):
        self.state = HotkeyState()
        self._thread: threading.Thread = None
        self._listener = None

    def start(self):
        """Start background keyboard listener."""
        try:
            from pynput import keyboard

            def on_press(key):
                try:
                    k = key.char
                except AttributeError:
                    k = str(key)

                if k in ('q', '\x1b') or 'esc' in k.lower():
                    self.state.should_quit = True
                elif k == 'p':
                    self.state.paused = not self.state.paused
                elif k == 'c':
                    self.state.run_calibration = True
                elif k == 'd':
                    self.state.debug_overlay = not self.state.debug_overlay

            self._listener = keyboard.Listener(on_press=on_press)
            self._listener.start()
        except Exception:
            pass  # Graceful degradation if pynput keyboard unavailable

    def stop(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass

    @property
    def should_quit(self) -> bool:
        return self.state.should_quit

    @property
    def paused(self) -> bool:
        return self.state.paused
