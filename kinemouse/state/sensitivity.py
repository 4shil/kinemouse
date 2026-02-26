"""
SensitivityController — dynamic mouse sensitivity adjustment.

Allows users to fine-tune cursor speed:
- Slow mode (for precise work, e.g., Photoshop selections)
- Normal mode (default)
- Fast mode (for quick large movements)

Sensitivity is applied as a multiplier on the screen coordinate mapping,
effectively scaling the active_box to change how much hand movement
maps to screen movement.

Usage:
    sens = SensitivityController(config)
    sens.set_mode("slow")
    adjusted_box = sens.adjusted_active_box
"""

from enum import Enum, auto
from typing import Tuple

from kinemouse.utils.config import KineMouseConfig


class SensitivityMode(Enum):
    SLOW   = auto()   # Small movements = precise
    NORMAL = auto()   # Default
    FAST   = auto()   # Large range, less arm fatigue


_MODE_SCALE = {
    SensitivityMode.SLOW:   1.8,   # wider active box → same hand movement = smaller cursor movement
    SensitivityMode.NORMAL: 1.0,
    SensitivityMode.FAST:   0.6,   # narrower box → more cursor movement per gesture
}


class SensitivityController:
    """
    Adjusts the effective active_box size to control cursor sensitivity.
    Does not modify the base config — returns an adjusted box tuple.
    """

    def __init__(self, config: KineMouseConfig):
        self._config = config
        self._mode = SensitivityMode.NORMAL
        self._custom_scale: float = 1.0

    @property
    def mode(self) -> SensitivityMode:
        return self._mode

    def set_mode(self, mode: str):
        """Set mode by name: 'slow', 'normal', 'fast'."""
        mapping = {
            "slow":   SensitivityMode.SLOW,
            "normal": SensitivityMode.NORMAL,
            "fast":   SensitivityMode.FAST,
        }
        self._mode = mapping.get(mode.lower(), SensitivityMode.NORMAL)

    def set_custom_scale(self, scale: float):
        """Set a custom sensitivity scale factor (0.1 – 5.0)."""
        self._custom_scale = max(0.1, min(5.0, scale))
        self._mode = SensitivityMode.NORMAL   # Custom overrides named mode

    @property
    def scale(self) -> float:
        return _MODE_SCALE.get(self._mode, 1.0) * self._custom_scale

    @property
    def adjusted_active_box(self) -> Tuple[float, float, float, float]:
        """
        Return an active_box scaled around its center.
        Larger scale = wider box = slower (more precise) cursor.
        """
        x_min, y_min, x_max, y_max = self._config.active_box
        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2
        half_w = ((x_max - x_min) / 2) * self.scale
        half_h = ((y_max - y_min) / 2) * self.scale

        return (
            max(0.0, cx - half_w),
            max(0.0, cy - half_h),
            min(1.0, cx + half_w),
            min(1.0, cy + half_h),
        )
