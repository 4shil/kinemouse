# KineMouse Architecture

## 3-Layer Design

```
┌─────────────────────────────────────────────┐
│  Layer 1: Vision Engine (Platform Agnostic) │
│  ┌──────────────────────────────────────┐   │
│  │  HandTracker                         │   │
│  │  - OpenCV webcam capture @ 30 FPS    │   │
│  │  - MediaPipe Hands landmark extract  │   │
│  │  → Emits: HandFrame (21 landmarks)   │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  Layer 2: State Machine (Platform Agnostic) │
│  ┌──────────────────────────────────────┐   │
│  │  GestureFSM                          │   │
│  │  - D_ref dynamic thresholding        │   │
│  │  - EMA smoothing (α = 0.25)          │   │
│  │  - Double-pinch FSM (400ms window)   │   │
│  │  - Right-click detection             │   │
│  │  → Emits: MouseEvent                 │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                      │
                      ▼ (async queue)
┌─────────────────────────────────────────────┐
│  Layer 3: OS Abstraction (Adapter Layer)    │
│  ┌────────────┐  ┌────────────┐  ┌───────┐ │
│  │  Windows   │  │   macOS    │  │ Linux │ │
│  │  pynput/   │  │  pynput/   │  │ X11 / │ │
│  │  ctypes    │  │  Quartz    │  │Wayland│ │
│  └────────────┘  └────────────┘  └───────┘ │
└─────────────────────────────────────────────┘
```

## Gesture State Machine

```
       ┌──────────────────────────────────────────┐
       │                   IDLE                   │
       │        (hand open / not detected)        │
       └──────────────────┬───────────────────────┘
                          │ pinch detected
                          ▼
       ┌──────────────────────────────────────────┐
       │                 PINCH_1                  │
       │          (cursor follows hand)           │
       └──────────────────┬───────────────────────┘
                          │ pinch released
                          ▼
       ┌──────────────────────────────────────────┐
       │              RELEASE_WAIT                │
       │         (400ms countdown starts)         │
       └────────┬─────────────────────────────────┘
                │                │
       400ms    │                │ second pinch
      expires   │                │ < 400ms
                ▼                ▼
         SINGLE_CLICK       DRAG_MODE
         → return IDLE    (MOUSE_DOWN held)
                                 │
                                 │ pinch released
                                 ▼
                              MOUSE_UP
                           → return IDLE
```

## Math Models

### Dynamic Thresholding
```
D_ref = distance(Wrist[0], IndexKnuckle[5])
Pinch active when: distance(ThumbTip[4], FingerTip) < 0.15 × D_ref
```

### EMA Smoothing
```
S_t = α × X_t + (1 - α) × S_{t-1}   where α = 0.25
```
