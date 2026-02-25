"""Layer 3: OS Abstraction — platform-specific mouse backends."""

import sys
from kinemouse.utils.config import KineMouseConfig


def get_backend(config: KineMouseConfig):
    """
    Factory: auto-detect OS and return the correct mouse backend.
    """
    platform = sys.platform

    if platform == "win32":
        from kinemouse.backends.windows_backend import WindowsBackend
        return WindowsBackend(config)
    elif platform == "darwin":
        from kinemouse.backends.macos_backend import MacOSBackend
        return MacOSBackend(config)
    elif platform.startswith("linux"):
        # Detect Wayland vs X11
        import os
        if os.environ.get("WAYLAND_DISPLAY"):
            from kinemouse.backends.linux_wayland_backend import LinuxWaylandBackend
            return LinuxWaylandBackend(config)
        else:
            from kinemouse.backends.linux_x11_backend import LinuxX11Backend
            return LinuxX11Backend(config)
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")
