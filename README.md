<div align="center">

# KineMouse

**A zero-latency, cross-platform virtual mouse controlled entirely by hand gestures via a standard webcam.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00897B?style=flat-square&logo=google&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

</div>

---

![KineMouse Demo]()

> **No special hardware. No drivers. Just a webcam and your hand.**

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Gesture Map](#gesture-map)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Platform Notes](#platform-notes)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

KineMouse translates raw webcam input into precise OS-level mouse events using a strict 3-layer pipeline:

1. **Vision Engine** — OpenCV captures frames; MediaPipe extracts 21 hand landmarks per frame
2. **State Machine** — Interprets landmark geometry into discrete gesture events with dynamic distance normalization and EMA smoothing
3. **OS Adapter** — Routes events to the correct native backend (pynput, evdev/uinput, Quartz)

The cursor only moves when the user actively pinches — a "clutch" mechanism — so resting or repositioning your hand has zero effect on the cursor.

---

## Architecture

```
                     +-----------------------------------------+
                     |   Layer 1: Vision Engine (Platform-Free) |
                     |   OpenCV capture @ 30 FPS                |
                     |   MediaPipe Hands — 21 landmarks/frame   |
                     +-----------------------------------------+
                                        |
                                        v  HandFrame
                     +-----------------------------------------+
                     |   Layer 2: Gesture State Machine         |
                     |   D_ref dynamic thresholding             |
                     |   EMA smoothing (alpha = 0.25)           |
                     |   Double-pinch FSM (400ms window)        |
                     +-----------------------------------------+
                                        |
                              (async queue)
                                        |
                                        v  MouseEvent
                     +-----------------------------------------+
                     |   Layer 3: OS Abstraction Adapter        |
                     |   Windows  →  pynput / ctypes            |
                     |   macOS    →  pynput / Quartz            |
                     |   Linux X11 →  pynput / Xlib             |
                     |   Linux Wayland →  evdev / uinput        |
                     +-----------------------------------------+
```

The core vision and state logic are fully platform-agnostic. Only Layer 3 touches OS APIs.

---

## Gesture Map

| Action | Physical Gesture | Landmarks Used |
|---|---|---|
| Idle | Hand open or relaxed | Distance(4, 8) > threshold |
| Move Cursor | Pinch Thumb + Index, move hand | Midpoint of (4, 8) mapped to screen |
| Single Click | Pinch and release quickly | FSM: PINCH_1 → RELEASE_WAIT → 400ms expires |
| Drag | Pinch, release, pinch again within 400ms | FSM: PINCH_1 → RELEASE_WAIT → DRAG_MODE → MOUSE_DOWN |
| Right Click | Pinch Thumb + Middle finger | Distance(4, 12) < threshold |

### Double-Pinch State Machine

```
    IDLE
     |
     | pinch detected
     v
   PINCH_1  ---------> cursor moves
     |
     | pinch released
     v
  RELEASE_WAIT  <-- 400ms countdown
     |            |
     |            | second pinch before 400ms
     |            v
     |         DRAG_MODE  --> MOUSE_DOWN held, cursor moves
     |            |
     |            | pinch released
     |            v
     |          MOUSE_UP --> back to IDLE
     |
     | 400ms expires, no second pinch
     v
  SINGLE_CLICK --> back to IDLE
```

---

## Installation

**Prerequisites:** Python 3.10+, a working webcam, pip

```bash
git clone https://github.com/4shil/kinemouse.git
cd kinemouse
pip install -r requirements.txt
```

For Linux Wayland (additional step — see [Platform Notes](#platform-notes)):

```bash
pip install evdev
```

---

## Usage

```bash
# Default — opens webcam 0 with preview window
python main.py

# Headless (no preview)
python main.py --no-preview

# Custom camera index
python main.py --camera 1

# Adjust smoothing (lower = smoother, more lag)
python main.py --alpha 0.15
```

### Preview Window

When running with preview, a live annotated feed shows:
- Hand skeleton overlay (MediaPipe landmarks)
- Green bounding box for the active control region
- Current FSM state (IDLE / MOVE / CLICK / DRAG)

Press `q` to quit.

---

## Configuration

All parameters live in `kinemouse/utils/config.py` as a dataclass:

```python
@dataclass
class KineMouseConfig:
    camera_index: int = 0
    capture_fps: int = 30
    flip_horizontal: bool = True
    active_box: Tuple[float, float, float, float] = (0.25, 0.20, 0.75, 0.80)
    pinch_threshold: float = 0.15      # % of D_ref
    double_pinch_window_ms: int = 400
    ema_alpha: float = 0.25
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.7
```

**`active_box`** defines the normalized region of the camera frame that maps to the full screen. Shrinking it reduces arm movement needed; enlarging it increases precision range.

**`ema_alpha`** controls smoothing. `0.1` = very smooth but laggy. `0.5` = snappy but jittery. Default `0.25` is a good starting point.

---

## Platform Notes

### Linux — Wayland

Wayland restricts userspace input injection. KineMouse creates a kernel-level `uinput` virtual device to bypass this:

```bash
# Add yourself to the input group
sudo usermod -aG input $USER

# Set udev rules so the device is accessible without sudo
echo 'KERNEL=="uinput", GROUP="input", MODE="0660"' | \
  sudo tee /etc/udev/rules.d/99-kinemouse.rules

sudo udevadm control --reload-rules
sudo udevadm trigger

# Log out and back in for group change to apply
```

### Linux — X11

No special setup needed. pynput works out of the box via Xlib.

### macOS

Grant Accessibility permissions to your terminal / Python interpreter:

```
System Settings > Privacy & Security > Accessibility > Add your app
```

### Windows

No setup required. pynput communicates with the Win32 mouse API directly.

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

Test coverage includes:
- `test_math_utils.py` — Euclidean distance, EMA, screen mapping, D_ref
- `test_events.py` — MouseEvent types and constructors
- `test_gesture_fsm.py` — FSM state transitions, pinch detection, right-click

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

Short version:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/scroll-gesture`)
3. Write tests for your changes
4. Submit a pull request against `main`

---

## License

MIT License. See [LICENSE](LICENSE) for details.
