"""
replay_session.py — replay a recorded gesture session without a webcam.

Loads a JSON file saved by record_session.py and runs it through the FSM,
printing events and optionally dispatching them to the OS backend.

Usage:
    python tools/replay_session.py session.json
    python tools/replay_session.py session.json --dispatch   # actually moves mouse
    python tools/replay_session.py session.json --speed 2.0  # 2x speed
"""

import sys
import json
import time
import argparse
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinemouse.utils.config import KineMouseConfig
from kinemouse.state.gesture_fsm import GestureFSM
from kinemouse.state.events import EventType
from kinemouse.utils.logger import init_logging, get_logger

log = get_logger("replay")


def dict_to_landmarks(frame_lm: list):
    """Convert list of dicts back to SimpleNamespace objects (mimics MediaPipe)."""
    return [SimpleNamespace(x=lm["x"], y=lm["y"], z=lm["z"]) for lm in frame_lm]


def main():
    parser = argparse.ArgumentParser(description="Replay a recorded gesture session")
    parser.add_argument("file", help="Path to session JSON file")
    parser.add_argument("--dispatch", action="store_true", help="Dispatch events to OS (moves real cursor)")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    args = parser.parse_args()

    init_logging("INFO")

    path = Path(args.file)
    if not path.exists():
        log.error("File not found: %s", path)
        sys.exit(1)

    data = json.loads(path.read_text())
    frames = data["frames"]
    cfg_data = data.get("config", {})
    screen_res = tuple(cfg_data.get("screen_res", [1920, 1080]))

    config = KineMouseConfig()
    fsm = GestureFSM(config, screen_res)

    backend = None
    if args.dispatch:
        from kinemouse.backends import get_backend
        backend = get_backend(config)
        log.info("Dispatching events to OS backend")

    log.info("Replaying %d frames from %s at %.1fx speed", len(frames), path.name, args.speed)

    prev_t = 0.0
    for i, frame in enumerate(frames):
        # Maintain original timing
        gap = (frame["t"] - prev_t) / args.speed
        if gap > 0:
            time.sleep(gap)
        prev_t = frame["t"]

        lm = dict_to_landmarks(frame["landmarks"]) if frame["found"] else None
        event = fsm.process(lm)

        if event.type != EventType.IDLE:
            log.info("[%05.2fs] frame=%d  event=%-12s  pos=%s",
                     frame["t"], i, event.type.name, event.position)

        if backend and event.type != EventType.IDLE:
            backend.dispatch(event)

    log.info("Replay complete.")


if __name__ == "__main__":
    main()
