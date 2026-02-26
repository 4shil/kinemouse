"""
GestureHistory — records gesture events with timestamps for analysis and replay.

Useful for:
- Debugging gesture detection timing
- Identifying accidental triggers
- Building gesture macros (future)
- Saving recorded sessions to JSON for deterministic testing

Usage:
    history = GestureHistory(max_entries=1000)
    history.record(event)
    history.save("session.json")
    history.print_summary()
"""

import json
import time
from collections import deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Deque

from kinemouse.state.events import MouseEvent, EventType


@dataclass
class GestureRecord:
    timestamp: float
    event_type: str
    position_x: Optional[int]
    position_y: Optional[int]

    @staticmethod
    def from_event(event: MouseEvent) -> "GestureRecord":
        return GestureRecord(
            timestamp=time.monotonic(),
            event_type=event.type.name,
            position_x=event.position[0] if event.position else None,
            position_y=event.position[1] if event.position else None,
        )


class GestureHistory:
    """
    Rolling buffer of recent gesture events with save/load and summary capabilities.
    """

    def __init__(self, max_entries: int = 1000):
        self._buffer: Deque[GestureRecord] = deque(maxlen=max_entries)
        self._counts: dict = {t.name: 0 for t in EventType}

    def record(self, event: MouseEvent):
        """Record a gesture event."""
        if event.type == EventType.IDLE:
            return  # Skip idle noise
        self._buffer.append(GestureRecord.from_event(event))
        self._counts[event.type.name] = self._counts.get(event.type.name, 0) + 1

    def save(self, path: str):
        """Save session history to a JSON file."""
        records = [asdict(r) for r in self._buffer]
        with open(path, "w") as f:
            json.dump({"records": records, "counts": self._counts}, f, indent=2)

    def load(self, path: str):
        """Load history from JSON file."""
        with open(path) as f:
            data = json.load(f)
        self._buffer.clear()
        for r in data.get("records", []):
            self._buffer.append(GestureRecord(**r))
        self._counts = data.get("counts", {})

    def print_summary(self):
        """Print event frequency summary to stdout."""
        total = sum(self._counts.values())
        print(f"\n--- Gesture Session Summary ({total} events) ---")
        for name, count in sorted(self._counts.items(), key=lambda x: -x[1]):
            if count > 0:
                pct = (count / total * 100) if total else 0
                print(f"  {name:<15} {count:>5}  ({pct:.1f}%)")
        print()

    def last_n(self, n: int) -> List[GestureRecord]:
        """Return last n recorded events."""
        items = list(self._buffer)
        return items[-n:]

    def clear(self):
        self._buffer.clear()
        self._counts = {t.name: 0 for t in EventType}
