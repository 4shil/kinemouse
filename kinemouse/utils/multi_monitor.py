"""
MultiMonitorRouter — maps normalized cursor position across multiple monitors.

For Phase 2 multi-monitor support. Instead of mapping to a single screen,
this router maps the active_box to the full virtual desktop spanning all monitors.

Usage:
    router = MultiMonitorRouter(screen_info)
    abs_x, abs_y = router.map(norm_x, norm_y, active_box)
"""

from typing import Tuple, List
from kinemouse.utils.screen_info import ScreenInfo, Monitor
from kinemouse.utils.math_utils import map_to_screen


class MultiMonitorRouter:
    """
    Maps a normalized hand position to absolute pixel coordinates
    across a virtual desktop that spans multiple monitors.

    Virtual desktop = bounding box of all monitor rectangles.
    """

    def __init__(self, screen_info: ScreenInfo):
        self._monitors: List[Monitor] = screen_info.monitors or [
            Monitor(0, 0, *screen_info.primary)
        ]
        self._vdesk = self._compute_virtual_desktop()

    def _compute_virtual_desktop(self) -> Tuple[int, int, int, int]:
        """Compute bounding rect of all monitors: (x_min, y_min, x_max, y_max)."""
        x_min = min(m.x for m in self._monitors)
        y_min = min(m.y for m in self._monitors)
        x_max = max(m.x + m.width for m in self._monitors)
        y_max = max(m.y + m.height for m in self._monitors)
        return (x_min, y_min, x_max, y_max)

    @property
    def virtual_resolution(self) -> Tuple[int, int]:
        """Total pixel dimensions of the virtual desktop."""
        vd = self._vdesk
        return (vd[2] - vd[0], vd[3] - vd[1])

    def map(
        self,
        norm_point: Tuple[float, float],
        active_box: Tuple[float, float, float, float],
    ) -> Tuple[int, int]:
        """
        Map a normalized hand position through active_box to virtual desktop coords.
        Returns absolute (x, y) pixel position valid for the OS cursor API.
        """
        vres = self.virtual_resolution
        sx, sy = map_to_screen(norm_point, active_box, vres)
        # Offset by virtual desktop origin (handles negative coords on some setups)
        vd = self._vdesk
        return (sx + vd[0], sy + vd[1])

    def which_monitor(self, x: int, y: int) -> Monitor:
        """Return which monitor a given absolute position falls on."""
        for m in self._monitors:
            if m.x <= x < m.x + m.width and m.y <= y < m.y + m.height:
                return m
        return self._monitors[0]

    def monitor_count(self) -> int:
        return len(self._monitors)
