"""Write and read a run's spans as one parsable JSON trace (D1-REQ-OBS-001)."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .events import TelemetryEvent


def write_trace(
    path: str | Path,
    events: Iterable[TelemetryEvent],
    status: str = "complete",
) -> Path:
    """Write ``events`` as ``{"run_id", "status", "spans"}`` deterministic JSON."""
    items = list(events)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": items[0].run_id if items else None,
        "status": status,
        "spans": [event.as_dict() for event in items],
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def load_trace(path: str | Path) -> list[TelemetryEvent]:
    """Read a trace back; a missing file is an empty run, not an error."""
    target = Path(path)
    if not target.exists():
        return []
    payload = json.loads(target.read_text(encoding="utf-8"))
    return [
        TelemetryEvent(
            run_id=span.get("run_id", ""),
            name=span["name"],
            phase=span["phase"],
            kind=span["kind"],
            started_at=span["started_at"],
            ended_at=span["ended_at"],
            duration_ms=float(span["duration_ms"]),
            tokens_in=int(span.get("tokens_in", 0)),
            tokens_out=int(span.get("tokens_out", 0)),
            model=span.get("model"),
            attributes=span.get("attributes", {}),
        )
        for span in payload.get("spans", [])
    ]

