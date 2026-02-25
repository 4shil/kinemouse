# KineMouse 🖱️

> Zero-latency, cross-platform virtual mouse controlled entirely by hand gestures via a standard webcam.

## Overview

KineMouse lets you control your computer mouse using hand gestures detected through any standard webcam — no special hardware required.

## Features

- 🖐️ **Gesture-based control** — Move, click, right-click, and drag using natural hand gestures
- 🌍 **Cross-platform** — Windows 10/11, macOS 13+, Linux (Wayland & X11)
- ⚡ **Zero-latency design** — 30 FPS capture with async OS event dispatch
- 🎯 **Dynamic thresholding** — Works regardless of distance from camera
- 🧈 **Smooth cursor** — Exponential Moving Average (EMA) stabilization

## Tech Stack

- Python 3.10+
- OpenCV
- MediaPipe
- NumPy
- OS backends: pynput, evdev, pywin32, Quartz

## Gesture Map

| Action | Gesture |
|--------|---------|
| Idle / Freeze | Hand open/relaxed |
| Move Cursor | Pinch Thumb + Index, move hand |
| Single Click | Quick pinch + release |
| Drag | Double pinch within 400ms |
| Right Click | Pinch Thumb + Middle finger |

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## License

MIT
