"""
ConfigIO — save and load KineMouseConfig from a JSON file.

Allows users to persist their calibration, alpha, thresholds etc.
without changing source code.

Default config path: ~/.kinemouse/config.json

Usage:
    from kinemouse.utils.config_io import load_config, save_config

    config = load_config()          # loads from default or creates defaults
    config.ema_alpha = 0.15
    save_config(config)             # persists to disk
"""

import json
import os
from pathlib import Path
from typing import Optional

from kinemouse.utils.config import KineMouseConfig


_DEFAULT_CONFIG_PATH = Path.home() / ".kinemouse" / "config.json"


def _config_to_dict(config: KineMouseConfig) -> dict:
    return {
        "camera_index":            config.camera_index,
        "capture_fps":             config.capture_fps,
        "flip_horizontal":         config.flip_horizontal,
        "active_box":              list(config.active_box),
        "pinch_threshold":         config.pinch_threshold,
        "double_pinch_window_ms":  config.double_pinch_window_ms,
        "ema_alpha":               config.ema_alpha,
        "max_num_hands":           config.max_num_hands,
        "min_detection_confidence": config.min_detection_confidence,
        "min_tracking_confidence":  config.min_tracking_confidence,
    }


def _dict_to_config(data: dict) -> KineMouseConfig:
    cfg = KineMouseConfig()
    cfg.camera_index            = data.get("camera_index",            cfg.camera_index)
    cfg.capture_fps             = data.get("capture_fps",             cfg.capture_fps)
    cfg.flip_horizontal         = data.get("flip_horizontal",         cfg.flip_horizontal)
    ab = data.get("active_box")
    if ab and len(ab) == 4:
        cfg.active_box = tuple(ab)
    cfg.pinch_threshold         = data.get("pinch_threshold",         cfg.pinch_threshold)
    cfg.double_pinch_window_ms  = data.get("double_pinch_window_ms",  cfg.double_pinch_window_ms)
    cfg.ema_alpha               = data.get("ema_alpha",               cfg.ema_alpha)
    cfg.max_num_hands           = data.get("max_num_hands",           cfg.max_num_hands)
    cfg.min_detection_confidence = data.get("min_detection_confidence", cfg.min_detection_confidence)
    cfg.min_tracking_confidence  = data.get("min_tracking_confidence",  cfg.min_tracking_confidence)
    return cfg


def load_config(path: Optional[Path] = None) -> KineMouseConfig:
    """Load config from JSON file. Returns defaults if file doesn't exist."""
    p = path or _DEFAULT_CONFIG_PATH
    if p.exists():
        try:
            with open(p) as f:
                data = json.load(f)
            return _dict_to_config(data)
        except Exception:
            pass
    return KineMouseConfig()


def save_config(config: KineMouseConfig, path: Optional[Path] = None):
    """Save config to JSON file. Creates directory if needed."""
    p = path or _DEFAULT_CONFIG_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(_config_to_dict(config), f, indent=2)
