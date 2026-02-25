# KineMouse Setup Guide

## Quick Start

```bash
git clone https://github.com/4shil/kinemouse
cd kinemouse
pip install -r requirements.txt
python main.py
```

## Linux Wayland Setup

Wayland restricts direct input access. KineMouse uses a kernel-level `uinput` device to bypass this:

```bash
# Add user to input group
sudo usermod -aG input $USER

# Create udev rule for uinput access
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | \
  sudo tee /etc/udev/rules.d/99-kinemouse.rules

sudo udevadm control --reload-rules && sudo udevadm trigger

# Log out and log back in for group change to take effect
```

## macOS Setup

Grant Accessibility permissions:
- System Settings → Privacy & Security → Accessibility
- Add Terminal (or your Python interpreter) to the list

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```
