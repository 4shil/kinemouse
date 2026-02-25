"""
KineMouse — main entry point.

Orchestrates all 3 layers:
    Layer 1 (HandTracker) → Layer 2 (GestureFSM) → Layer 3 (OS Backend)

Runs at 30 FPS. OS dispatch runs on a separate async thread.
"""

import sys
import threading
import queue
import time

import cv2

from kinemouse.utils.config import KineMouseConfig
from kinemouse.vision.hand_tracker import HandTracker
from kinemouse.backends import get_backend
from kinemouse.state.gesture_fsm import GestureFSM
from kinemouse.state.events import EventType


def run(config: KineMouseConfig = None, show_preview: bool = True):
    if config is None:
        config = KineMouseConfig()

    # --- Layer 3: OS Backend (auto-detect) ---
    print("[KineMouse] Detecting OS backend...")
    backend = get_backend(config)
    screen_res = backend.get_screen_resolution()
    print(f"[KineMouse] Screen resolution: {screen_res[0]}x{screen_res[1]}")

    # --- Event queue for async OS dispatch ---
    event_queue: queue.Queue = queue.Queue(maxsize=4)

    def dispatcher_thread():
        """Consume events from queue and dispatch to OS backend."""
        while True:
            event = event_queue.get()
            if event is None:
                break  # Shutdown signal
            try:
                backend.dispatch(event)
            except Exception as e:
                print(f"[Dispatcher] Error: {e}", file=sys.stderr)
            event_queue.task_done()

    dispatcher = threading.Thread(target=dispatcher_thread, daemon=True)
    dispatcher.start()

    # --- Layer 2: State Machine ---
    fsm = GestureFSM(config, screen_res)

    # --- Layer 1: Hand Tracker ---
    print("[KineMouse] Starting webcam capture... Press 'q' to quit.")
    tracker = HandTracker(config)

    if not tracker.start():
        print("[KineMouse] ERROR: Could not open webcam.", file=sys.stderr)
        event_queue.put(None)
        return

    frame_delay = 1.0 / config.capture_fps

    try:
        while True:
            t_start = time.monotonic()

            # Layer 1: capture frame + extract landmarks
            hand_frame = tracker.next_frame()

            # Layer 2: translate landmarks → MouseEvent
            event = fsm.process(hand_frame.landmarks if hand_frame.found else None)

            # Layer 3: async dispatch
            if event.type != EventType.IDLE:
                try:
                    event_queue.put_nowait(event)
                except queue.Full:
                    pass  # Drop frame — OS busy, keep real-time feel

            # Optional preview window
            if show_preview and hand_frame.annotated_frame is not None:
                frame = hand_frame.annotated_frame
                # Draw active box overlay
                h_px, w_px = frame.shape[:2]
                ab = config.active_box
                x1 = int(ab[0] * w_px); y1 = int(ab[1] * h_px)
                x2 = int(ab[2] * w_px); y2 = int(ab[3] * h_px)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 100), 2)
                cv2.putText(frame, f"State: {event.type.name}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
                cv2.imshow("KineMouse Preview", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Maintain target FPS
            elapsed = time.monotonic() - t_start
            sleep = frame_delay - elapsed
            if sleep > 0:
                time.sleep(sleep)

    except KeyboardInterrupt:
        print("\n[KineMouse] Interrupted by user.")
    finally:
        tracker.stop()
        event_queue.put(None)
        cv2.destroyAllWindows()
        print("[KineMouse] Stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="KineMouse — gesture virtual mouse")
    parser.add_argument("--no-preview", action="store_true", help="Disable webcam preview window")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument("--alpha", type=float, default=0.25, help="EMA smoothing factor (default: 0.25)")
    args = parser.parse_args()

    cfg = KineMouseConfig(camera_index=args.camera, ema_alpha=args.alpha)
    run(config=cfg, show_preview=not args.no_preview)
