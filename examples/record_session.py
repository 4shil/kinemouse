"""
record_session.py — records a live gesture session to a JSON file.

Captures landmark data + FSM events frame by frame and saves to disk.
Useful for:
  - Replaying sessions offline without a webcam
  - Debugging gesture recognition
  - Building test fixtures

Usage:
    python examples/record_session.py --out session.json --duration 30
    python examples/record_session.py --camera 1 --out my_session.json
"""

import sys
import json
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinemouse.vision.hand_tracker import HandTracker
from kinemouse.state.gesture_fsm import GestureFSM
from kinemouse.utils.config import KineMouseConfig
from kinemouse.utils.screen_info import ScreenInfo
from kinemouse.utils.logger import init_logging, get_logger
import cv2

log = get_logger("record")


def landmark_to_dict(lm) -> dict:
    return {"x": round(lm.x, 5), "y": round(lm.y, 5), "z": round(lm.z, 5)}


def main():
    parser = argparse.ArgumentParser(description="Record gesture session to JSON")
    parser.add_argument("--out", default="session.json", help="Output JSON file path")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--duration", type=float, default=None, help="Max recording duration in seconds")
    parser.add_argument("--no-preview", action="store_true")
    args = parser.parse_args()

    init_logging("INFO")
    config = KineMouseConfig(camera_index=args.camera)
    screen_res = ScreenInfo.detect().primary
    fsm = GestureFSM(config, screen_res)

    frames = []
    t_start = time.monotonic()
    log.info("Recording to %s (Ctrl+C or 'q' to stop)", args.out)

    with HandTracker(config) as tracker:
        while True:
            hf = tracker.next_frame()
            elapsed = time.monotonic() - t_start

            if args.duration and elapsed > args.duration:
                break

            record = {
                "t": round(elapsed, 4),
                "found": hf.found,
                "landmarks": [landmark_to_dict(lm) for lm in hf.landmarks] if hf.found and hf.landmarks else [],
            }

            if hf.found:
                event = fsm.process(hf.landmarks)
                record["event"] = event.type.name
                record["pos"] = list(event.position) if event.position else None
            else:
                fsm.process(None)
                record["event"] = "IDLE"
                record["pos"] = None

            frames.append(record)

            if not args.no_preview and hf.annotated_frame is not None:
                cv2.putText(hf.annotated_frame, f"REC {len(frames)} frames", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.imshow("Recording", hf.annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cv2.destroyAllWindows()
    out_path = Path(args.out)
    out_path.write_text(json.dumps({"frames": frames, "config": {
        "camera": args.camera,
        "screen_res": list(screen_res),
        "fps": config.capture_fps,
    }}, indent=2))

    log.info("Saved %d frames to %s", len(frames), out_path)


if __name__ == "__main__":
    main()
