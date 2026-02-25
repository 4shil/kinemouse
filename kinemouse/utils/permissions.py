"""
Permissions Helper — first-run OS permission checks and guidance.
Prompts the user gracefully when required OS permissions are missing.
"""

import sys
import os
import platform


def check_and_prompt() -> bool:
    """
    Check OS-specific permissions required by KineMouse.
    Returns True if all permissions are satisfied (or not needed).
    Prints guidance and returns False if action is needed.
    """
    plat = sys.platform

    if plat == "darwin":
        return _check_macos()
    elif plat.startswith("linux"):
        if os.environ.get("WAYLAND_DISPLAY"):
            return _check_linux_wayland()
        else:
            return _check_linux_x11()
    # Windows: pynput works without special permissions in most cases
    return True


def _check_macos() -> bool:
    """Check macOS Accessibility permission."""
    try:
        from Quartz import AXIsProcessTrusted  # type: ignore
        trusted = AXIsProcessTrusted()
        if not trusted:
            print(
                "\n[KineMouse] ⚠️  macOS Accessibility permission required.\n"
                "Please grant access:\n"
                "  System Settings → Privacy & Security → Accessibility\n"
                "  → Add your Terminal / Python interpreter\n"
                "Then restart KineMouse."
            )
            return False
        return True
    except ImportError:
        # Quartz not available — pynput will handle accessibility request
        return True


def _check_linux_wayland() -> bool:
    """Check uinput access for Wayland backend."""
    uinput_path = "/dev/uinput"
    if not os.path.exists(uinput_path):
        print(
            "\n[KineMouse] ⚠️  /dev/uinput not found.\n"
            "Load the module: sudo modprobe uinput"
        )
        return False
    if not os.access(uinput_path, os.W_OK):
        print(
            "\n[KineMouse] ⚠️  No write access to /dev/uinput (Wayland backend).\n"
            "Run these once to fix permanently:\n\n"
            "  sudo usermod -aG input $USER\n"
            '  echo \'KERNEL=="uinput", GROUP="input", MODE="0660"\' | \\\n'
            "    sudo tee /etc/udev/rules.d/99-kinemouse.rules\n"
            "  sudo udevadm control --reload-rules && sudo udevadm trigger\n\n"
            "Log out and back in, then restart KineMouse."
        )
        return False
    return True


def _check_linux_x11() -> bool:
    """X11 — usually no special permission needed for pynput."""
    display = os.environ.get("DISPLAY")
    if not display:
        print(
            "\n[KineMouse] ⚠️  DISPLAY environment variable not set.\n"
            "Make sure you are running inside an X11 session."
        )
        return False
    return True
