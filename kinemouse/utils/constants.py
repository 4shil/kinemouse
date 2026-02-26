"""
KineMouse — shared constants.
Single source of truth for landmark indices, defaults, and limits.
"""

# --- MediaPipe Hand Landmark Indices ---
WRIST           = 0
THUMB_CMC       = 1
THUMB_MCP       = 2
THUMB_IP        = 3
THUMB_TIP       = 4
INDEX_MCP       = 5   # index knuckle (used for D_ref)
INDEX_PIP       = 6
INDEX_DIP       = 7
INDEX_TIP       = 8
MIDDLE_MCP      = 9
MIDDLE_PIP      = 10
MIDDLE_DIP      = 11
MIDDLE_TIP      = 12
RING_MCP        = 13
RING_PIP        = 14
RING_DIP        = 15
RING_TIP        = 16
PINKY_MCP       = 17
PINKY_PIP       = 18
PINKY_DIP       = 19
PINKY_TIP       = 20

# --- Gesture defaults ---
DEFAULT_PINCH_THRESHOLD      = 0.15   # 15% of D_ref
DEFAULT_DOUBLE_PINCH_WINDOW  = 400    # ms
DEFAULT_EMA_ALPHA            = 0.25
DEFAULT_CAPTURE_FPS          = 30
DEFAULT_CAMERA_INDEX         = 0

# --- Screen mapping ---
DEFAULT_ACTIVE_BOX = (0.25, 0.20, 0.75, 0.80)  # (x_min, y_min, x_max, y_max)

# --- Performance ---
DISPATCHER_QUEUE_SIZE = 4
