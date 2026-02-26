"""
Hot-reload gesture config from ~/.kinemouse/config.json at runtime.
Watches the file for changes and applies updates without restarting.

Usage:
    loader = GestureConfigLoader(config)
    loader.start()          # background watcher thread
    # config object is updated in-place when file changes
    loader.stop()
"""

import json
import time
import threading
from pathlib import Path
from kinemouse.utils.config import KineMouseConfig
from kinemouse.utils.logger import get_logger

log = get_logger(__name__)

CONFIG_PATH = Path.home() / ".kinemouse" / "config.json"
_WATCH_INTERVAL = 2.0  # seconds


class GestureConfigLoader:
    """
    Watches ~/.kinemouse/config.json and hot-reloads tuneable parameters
    (ema_alpha, pinch_threshold, double_pinch_window_ms, active_box)
    into the live KineMouseConfig object without restarting the app.
    """

    def __init__(self, config: KineMouseConfig):
        self._config = config
        self._last_mtime: float = 0.0
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        """Start the background file-watcher thread."""
        self._running = True
        self._thread = threading.Thread(target=self._watch, daemon=True)
        self._thread.start()
        log.info("Config hot-reload watching %s", CONFIG_PATH)

    def stop(self):
        self._running = False

    def _watch(self):
        while self._running:
            try:
                if CONFIG_PATH.exists():
                    mtime = CONFIG_PATH.stat().st_mtime
                    if mtime != self._last_mtime:
                        self._last_mtime = mtime
                        self._reload()
            except Exception as e:
                log.warning("Config reload error: %s", e)
            time.sleep(_WATCH_INTERVAL)

    def _reload(self):
        try:
            with open(CONFIG_PATH) as f:
                data = json.load(f)

            changed = []
            for key, value in data.items():
                if hasattr(self._config, key):
                    old = getattr(self._config, key)
                    if old != value:
                        setattr(self._config, key, value)
                        changed.append(f"{key}: {old} → {value}")

            if changed:
                log.info("Config hot-reloaded: %s", ", ".join(changed))
        except Exception as e:
            log.warning("Failed to parse config.json: %s", e)
