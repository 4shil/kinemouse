"""
run_demo.py — minimal KineMouse demo that prints live landmark data.

Usage:
    python examples/run_demo.py
    python examples/run_demo.py --camera 1
    python examples/run_demo.py --verbose

Press 'q' in the preview window or Ctrl+C to stop.
"""

import sys
import argparse
import time
from pathlib import Path

# Allow running from repo root without install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinemouse.vision.hand_tracker import HandTracker
from kinemouse.utils.config import KineMouseConfig
from kinemouse.utils.math_utils import compute_dref, is_pinching, midpoint
from kinemouse.utils.logger import init_logging, get_logger
import cv2

log = get_logger("demo")


def main():
    parser = argparse.ArgumentParser(description="KineMouse landmark demo")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    init_logging("DEBUG" if args.verbose else "INFO")
    config = KineMouseConfig(camera_index=args.camera)

    log.info("Starting demo on camera %d — press 'q' to quit", args.camera)

    frame_count = 0
    t0 = time.monotonic()

    with HandTracker(config) as tracker:
        while True:
            frame = tracker.next_frame()
            frame_count += 1

            if frame.found and frame.landmarks:
                lm = frame.landmarks
                dref = compute_dref(lm)
                pinching = is_pinching(lm, 4, 8, dref, config.pinch_threshold)
                mid = midpoint((lm[4].x, lm[4].y), (lm[8].x, lm[8].y))

                if args.verbose:
                    log.debug(
                        "frame=%d  dref=%.4f  pinch=%s  mid=(%.3f, %.3f)",
                        frame_count, dref, pinching, mid[0], mid[1]
                    )
                else:
                    status = "PINCH" if pinching else "open "
                    print(f"\r[{status}]  mid=({mid[0]:.3f}, {mid[1]:.3f})  dref={dref:.4f}  fps={frame_count / max(1, time.monotonic() - t0):.1f}  ", end="", flush=True)
            else:
                print(f"\r[no hand]  fps={frame_count / max(1, time.monotonic() - t0):.1f}  ", end="", flush=True)

            if frame.annotated_frame is not None:
                cv2.imshow("KineMouse Demo", frame.annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    print()
    elapsed = time.monotonic() - t0
    log.info("Demo ended — %d frames in %.1fs (avg %.1f fps)", frame_count, elapsed, frame_count / elapsed)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
