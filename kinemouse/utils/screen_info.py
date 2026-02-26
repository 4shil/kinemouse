"""
ScreenInfo — cross-platform primary and multi-monitor resolution detection.

Provides a unified way to get screen resolution without importing
OS-specific code in the core logic.

Usage:
    info = ScreenInfo.detect()
    print(info.primary)          # (1920, 1080)
    print(info.all_monitors)     # [(0,0,1920,1080), (1920,0,2560,1440)]
"""

import sys
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class Monitor:
    x: int
    y: int
    width: int
    height: int

    @property
    def resolution(self) -> Tuple[int, int]:
        return (self.width, self.height)

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)


@dataclass
class ScreenInfo:
    primary: Tuple[int, int]
    monitors: List[Monitor] = field(default_factory=list)

    @staticmethod
    def detect() -> "ScreenInfo":
        """Auto-detect screen resolution for the current platform."""
        try:
            if sys.platform == "win32":
                return ScreenInfo._detect_windows()
            elif sys.platform == "darwin":
                return ScreenInfo._detect_macos()
            else:
                if os.environ.get("WAYLAND_DISPLAY"):
                    return ScreenInfo._detect_wayland()
                return ScreenInfo._detect_x11()
        except Exception:
            return ScreenInfo(primary=(1920, 1080))

    @staticmethod
    def _detect_windows() -> "ScreenInfo":
        import ctypes
        user32 = ctypes.windll.user32  # type: ignore
        user32.SetProcessDPIAware()
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        return ScreenInfo(primary=(w, h), monitors=[Monitor(0, 0, w, h)])

    @staticmethod
    def _detect_macos() -> "ScreenInfo":
        import subprocess
        out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True)
        for line in out.splitlines():
            if "Resolution" in line:
                parts = line.split(":")[-1].strip().split(" x ")
                if len(parts) == 2:
                    w = int(parts[0].strip())
                    h = int(parts[1].strip().split(" ")[0])
                    return ScreenInfo(primary=(w, h), monitors=[Monitor(0, 0, w, h)])
        return ScreenInfo(primary=(1920, 1080))

    @staticmethod
    def _detect_x11() -> "ScreenInfo":
        import subprocess
        monitors = []
        primary = (1920, 1080)
        try:
            out = subprocess.check_output(["xrandr", "--query"], text=True)
            for line in out.splitlines():
                if " connected" in line:
                    for token in line.split():
                        if "x" in token and "+" in token and token[0].isdigit():
                            try:
                                w_h, ox, oy = token.split("+")
                                w, h = w_h.split("x")
                                mon = Monitor(int(ox), int(oy), int(w), int(h))
                                monitors.append(mon)
                                if not monitors or "primary" in line:
                                    primary = (int(w), int(h))
                            except Exception:
                                pass
        except Exception:
            pass
        if not monitors:
            monitors.append(Monitor(0, 0, *primary))
        return ScreenInfo(primary=primary, monitors=monitors)

    @staticmethod
    def _detect_wayland() -> "ScreenInfo":
        import subprocess
        try:
            out = subprocess.check_output(["wlr-randr"], text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                if "current" in line.lower() and "x" in line:
                    parts = line.split()
                    for p in parts:
                        if "x" in p and p[0].isdigit():
                            w, h = p.split("x")
                            h = h.split("@")[0]
                            return ScreenInfo(primary=(int(w), int(h)))
        except Exception:
            pass
        return ScreenInfo._detect_x11()
