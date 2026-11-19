"""Aggregate a run's spans per phase (D1-REQ-OBS-002).

The manifest answers "what did each phase cost, in tokens, estimated dollars and
wall-clock time?". Wall-clock is the sum of that phase's span durations: spans
inside one phase are sequential steps. Prices come from a local table, so an
unknown model is a warning with a zero cost, never a network call.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .events import TelemetryEvent
from .pricing import estimate_cost


def build_manifest(
    events: Iterable[TelemetryEvent],
    pricing: Mapping[str, Mapping[str, float]] | None = None,
    status: str = "complete",
) -> dict[str, Any]:
    """Per-phase and total tokens, estimated cost and wall-clock."""
    items = list(events)
    phases: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []

    for event in items:
        bucket = phases.setdefault(
            event.phase,
            {
                "tokens_in": 0,
                "tokens_out": 0,
                "tokens": 0,
                "est_cost": 0.0,
                "wall_clock_ms": 0.0,
                "spans": 0,
                "models": [],
            },
        )
        cost, warning = estimate_cost(
            event.model, event.tokens_in, event.tokens_out, pricing
        )
        if warning and warning not in warnings:
            warnings.append(warning)
        bucket["tokens_in"] += event.tokens_in
        bucket["tokens_out"] += event.tokens_out
        bucket["tokens"] = bucket["tokens_in"] + bucket["tokens_out"]
        bucket["est_cost"] = round(bucket["est_cost"] + cost, 8)
        bucket["wall_clock_ms"] = round(bucket["wall_clock_ms"] + event.duration_ms, 3)
        bucket["spans"] += 1
        if event.model and event.model not in bucket["models"]:
            bucket["models"].append(event.model)

    totals = {
        "tokens_in": sum(phase["tokens_in"] for phase in phases.values()),
        "tokens_out": sum(phase["tokens_out"] for phase in phases.values()),
        "tokens": sum(phase["tokens"] for phase in phases.values()),
        "est_cost": round(sum(phase["est_cost"] for phase in phases.values()), 8),
        "wall_clock_ms": round(sum(phase["wall_clock_ms"] for phase in phases.values()), 3),
        "spans": sum(phase["spans"] for phase in phases.values()),
    }
    return {
        "run_id": items[0].run_id if items else None,
        "status": status,
        "phases": phases,
        "totals": totals,
        "warnings": warnings,
    }


def write_manifest(path: str | Path, manifest: Mapping[str, Any]) -> Path:
    """Write the manifest as deterministic JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return target
