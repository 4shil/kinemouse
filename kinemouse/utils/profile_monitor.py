"""
ProfileMonitor — lightweight runtime performance monitor.

Tracks per-frame processing time, rolling average FPS, and CPU/memory
usage. Prints periodic reports to stderr.

Usage:
    monitor = ProfileMonitor(report_every=300)  # report every 300 frames
    while True:
        with monitor.frame():
            ... process frame ...
        monitor.maybe_report()
"""

import time
import os
import threading
from contextlib import contextmanager
from collections import deque
from typing import Optional


class ProfileMonitor:
    """
    Lightweight per-frame profiler with optional psutil integration.
    Falls back gracefully if psutil is not installed.
    """

    def __init__(self, report_every: int = 300):
        self._report_every = report_every
        self._frame_times: deque = deque(maxlen=300)
        self._frame_count = 0
        self._start = time.monotonic()
        self._last_report = time.monotonic()
        self._has_psutil = self._check_psutil()

    def _check_psutil(self) -> bool:
        try:
            import psutil
            self._process = psutil.Process(os.getpid())
            return True
        except ImportError:
            return False

    @contextmanager
    def frame(self):
        """Context manager — wraps a single frame's processing."""
        t0 = time.perf_counter()
        yield
        self._frame_times.append(time.perf_counter() - t0)
        self._frame_count += 1

    @property
    def avg_frame_ms(self) -> float:
        if not self._frame_times:
            return 0.0
        return (sum(self._frame_times) / len(self._frame_times)) * 1000

    @property
    def fps(self) -> float:
        if len(self._frame_times) < 2:
            return 0.0
        window = sum(self._frame_times)
        return len(self._frame_times) / window if window > 0 else 0.0

    def cpu_percent(self) -> Optional[float]:
        if self._has_psutil:
            try:
                return self._process.cpu_percent(interval=None)
            except Exception:
                pass
        return None

    def memory_mb(self) -> Optional[float]:
        if self._has_psutil:
            try:
                return self._process.memory_info().rss / (1024 * 1024)
            except Exception:
                pass
        return None

    def maybe_report(self):
        """Print a performance report if enough frames have passed."""
        if self._frame_count % self._report_every == 0 and self._frame_count > 0:
            self._print_report()

    def _print_report(self):
        cpu = self.cpu_percent()
        mem = self.memory_mb()
        parts = [
            f"frame={self._frame_count}",
            f"avg={self.avg_frame_ms:.1f}ms",
            f"fps={self.fps:.1f}",
        ]
        if cpu is not None:
            parts.append(f"cpu={cpu:.1f}%")
        if mem is not None:
            parts.append(f"mem={mem:.0f}MB")
        import sys
        print(f"[perf] {' | '.join(parts)}", file=sys.stderr)
