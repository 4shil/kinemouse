"""
Centralized logger for KineMouse.
Usage:
    from kinemouse.utils.logger import get_logger
    log = get_logger(__name__)
    log.info("started")
    log.debug("landmark count: %d", len(lm))
"""

import logging
import sys
from pathlib import Path


_LOG_FORMAT = "%(asctime)s  %(levelname)-7s  %(name)s — %(message)s"
_DATE_FORMAT = "%H:%M:%S"
_initialized = False


def init_logging(level: str = "INFO", log_file: str = None):
    """
    Call once at startup (main.py) to configure root logger.
    level: DEBUG, INFO, WARNING, ERROR
    log_file: optional path to write logs to file as well
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # Console handler
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # Optional file handler
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        root.addHandler(fh)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call init_logging() first."""
    return logging.getLogger(name)
