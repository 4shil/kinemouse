"""
KineMouse — Zero-latency cross-platform gesture mouse.

Package structure:
    kinemouse/
        vision/     — Layer 1: Vision Engine (OpenCV + MediaPipe)
        state/      — Layer 2: State Machine (gesture → events)
        backends/   — Layer 3: OS Abstraction (platform adapters)
        utils/      — Shared utilities (math, config, logging)
"""

__version__ = "1.0.0"
__author__ = "4shil"
