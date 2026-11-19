"""Write a run's trace and manifest next to its saved state log (OBS-001/002).

The caller opens the telemetry scope; this module turns the finished hub into
two files. Any I/O error is the caller's to downgrade to a warning: losing a
trace must never lose a decision.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from tradingagents.dataflows.symbols import safe_ticker_component

from .events import TelemetryEvent
from .manifest import build_manifest, write_manifest
from .trace import write_trace


def run_output_dir(config: Mapping[str, Any], ticker: str) -> Path:
    """The directory where a run keeps its trace and manifest.

    A ``telemetry`` subdirectory keeps the state log's directory stable: the
    inherited ``test_a_graph_reused_across_runs_keeps_no_run_state`` counts the
    state logs with ``*.json`` and must keep seeing one file per run.
    """
    return (
        Path(config["results_dir"])
        / safe_ticker_component(ticker)
        / "TradingAgentsStrategy_logs"
        / "telemetry"
    )


def write_run_telemetry(
    config: Mapping[str, Any],
    ticker: str,
    trade_date: str,
    events: Iterable[TelemetryEvent],
    warnings: Iterable[str] | None = None,
    status: str = "complete",
) -> tuple[Path, Path]:
    """Write ``trace_<date>.json`` and ``manifest_<date>.json``."""
    items = list(events)
    directory = run_output_dir(config, ticker)
    trace_path = write_trace(directory / f"trace_{trade_date}.json", items, status=status)
    manifest = build_manifest(items, config.get("telemetry_pricing"), status=status)
    for warning in warnings or ():
        if warning not in manifest["warnings"]:
            manifest["warnings"].append(warning)
    manifest_path = write_manifest(directory / f"manifest_{trade_date}.json", manifest)
    return trace_path, manifest_path
