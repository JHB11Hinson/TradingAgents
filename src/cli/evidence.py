"""Collect and render a finished run's evidence (D1-REQ-OBS-001/002/003).

A run already writes a state log, a telemetry trace and a manifest. This module
reads them back into one :class:`Evidence` record and renders it as a compact
Rich panel in the inherited style. It is purely additive: the live layout, the
graph and the report-save flow are untouched, and a missing or malformed file
degrades to ``not written`` / ``not recorded`` rather than raising, so evidence
can never fail a run.

The same collector serves the post-run panel (``collect_evidence`` on the
in-memory final state) and the ``inspect`` command (``collect_from_log`` on a
saved state log).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cli.display import format_tokens
from tradingagents.agents.rating import run_rating
from tradingagents.dataflows.symbols import safe_ticker_component
from tradingagents.telemetry import TelemetryEvent, load_trace, run_output_dir

# Memory lessons cite their origin as ``src:<date>/<ticker>`` (D1-REQ-MEM-003).
_SRC_RE = re.compile(r"src:([^\s|]+)")

# Human-readable names for the advisory guardrail spans (D1-REQ-SAFE-001/002/003).
_GUARDRAIL_LABELS = {
    "guardrail.instruction_blocked": "Instruction blocked",
    "guardrail.position_clipped": "Position clipped",
    "guardrail.decision_review": "Decision review",
    "guardrail.budget_review": "Budget review",
}

_DEBATE_EXCERPT = 80
_GUARDRAIL_DETAIL = 120
_PHASE_ROWS = 6


@dataclass(frozen=True)
class StateLogRef:
    """A located state log: its path and the run it belongs to."""

    path: Path
    ticker: str
    trade_date: str


@dataclass(frozen=True)
class Evidence:
    """Everything the Run Evidence panel shows about one finished run."""

    ticker: str
    trade_date: str
    rating: str
    decision_source: str
    termination_reason: str
    context: dict
    research_turns: list | tuple
    risk_turns: list | tuple
    guardrails: list | tuple
    memory_note: str
    memory_sources: tuple[str, ...]
    phases: dict
    manifest_totals: dict
    trace_path: Path | None
    manifest_path: Path | None
    telemetry_status: str


# --- small defensive helpers -------------------------------------------------


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _tokens(value: Any) -> str:
    return format_tokens(_int(value))


def _short(text: Any, limit: int) -> str:
    """Collapse whitespace to one line and truncate to ``limit`` chars with …."""
    collapsed = " ".join(str(text or "").split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[:limit].rstrip() + "…"


def _read_json(path: str | Path) -> Any:
    """Read a JSON file; a missing or malformed file is ``None``, never a raise."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _turn_records(debate_state: Any) -> list:
    if isinstance(debate_state, dict):
        records = debate_state.get("turn_records", [])
        if isinstance(records, (list, tuple)):
            return list(records)
    return []


def _parse_sources(past_context: Any) -> list[str]:
    return sorted(set(_SRC_RE.findall(str(past_context or ""))))


def _load_events(path: Path) -> list[TelemetryEvent]:
    try:
        return load_trace(path)
    except (OSError, ValueError, KeyError, TypeError):
        return []


def _trace_status(path: Path) -> str:
    data = _read_json(path)
    if isinstance(data, dict):
        return str(data.get("status") or "complete")
    return "complete"


def _filter_phases(phases: Any, events: list[TelemetryEvent]) -> dict:
    """Per-phase buckets with the guardrail spans' contribution removed.

    Guardrail spans carry no tokens or cost, so only their span count and
    wall-clock are subtracted; a phase left with nothing is dropped, keeping the
    table the run's own work rather than its advisory guardrails.
    """
    if not isinstance(phases, dict):
        return {}
    guard: dict[str, dict[str, float]] = {}
    for event in events:
        if event.kind != "guardrail":
            continue
        bucket = guard.setdefault(event.phase, {"spans": 0, "ms": 0.0})
        bucket["spans"] += 1
        bucket["ms"] += event.duration_ms
    result: dict[str, dict] = {}
    for name, raw in phases.items():
        if not isinstance(raw, dict):
            continue
        bucket = dict(raw)
        removed = guard.get(name)
        if removed:
            bucket["spans"] = max(0, _int(bucket.get("spans")) - _int(removed["spans"]))
            bucket["wall_clock_ms"] = max(
                0.0, _float(bucket.get("wall_clock_ms")) - removed["ms"]
            )
        if _int(bucket.get("spans")) <= 0 and _int(bucket.get("tokens")) <= 0:
            continue
        result[name] = bucket
    return result


def _guardrail_label(name: str) -> str:
    if name in _GUARDRAIL_LABELS:
        return _GUARDRAIL_LABELS[name]
    bare = name.removeprefix("guardrail.").replace("_", " ")
    return bare[:1].upper() + bare[1:] if bare else name


def _validate_date(value: Any) -> str:
    text = str(value)
    try:
        canonical = datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d") == text
    except ValueError:
        canonical = False
    if not canonical:
        raise ValueError(f"date must be a day in YYYY-MM-DD format, got {value!r}")
    return text


# --- collectors --------------------------------------------------------------


def collect_evidence(
    final_state: dict, config: dict, ticker: str, trade_date: str
) -> Evidence:
    """Build the evidence record from a finished run's state and its files."""
    final_state = final_state or {}
    context = final_state.get("context_usage") or {}
    if not isinstance(context, dict):
        context = {}
    sources = final_state.get("memory_sources") or _parse_sources(
        final_state.get("past_context", "")
    )
    base: dict[str, Any] = {
        "ticker": ticker,
        "trade_date": trade_date,
        "rating": run_rating(final_state),
        "decision_source": str(final_state.get("final_decision_source") or ""),
        "termination_reason": str(final_state.get("termination_reason") or ""),
        "context": context,
        "research_turns": _turn_records(final_state.get("investment_debate_state")),
        "risk_turns": _turn_records(final_state.get("risk_debate_state")),
        "memory_note": str(final_state.get("memory_note") or ""),
        "memory_sources": tuple(sorted({str(s) for s in sources})),
    }

    if not config.get("telemetry_enabled", True):
        return Evidence(
            **base,
            guardrails=(),
            phases={},
            manifest_totals={},
            trace_path=None,
            manifest_path=None,
            telemetry_status="disabled",
        )

    events: list[TelemetryEvent] = []
    trace_path: Path | None = None
    manifest_path: Path | None = None
    status = "not written"
    phases: dict = {}
    totals: dict = {}
    if config.get("results_dir"):
        directory = run_output_dir(config, ticker)
        candidate_trace = directory / f"trace_{trade_date}.json"
        candidate_manifest = directory / f"manifest_{trade_date}.json"
        if candidate_trace.exists():
            trace_path = candidate_trace
            events = _load_events(candidate_trace)
            status = _trace_status(candidate_trace)
        if candidate_manifest.exists():
            manifest_path = candidate_manifest
            manifest = _read_json(candidate_manifest)
            if isinstance(manifest, dict):
                phases = _filter_phases(manifest.get("phases"), events)
                totals = manifest.get("totals") or {}

    return Evidence(
        **base,
        guardrails=tuple(e for e in events if e.kind == "guardrail"),
        phases=phases,
        manifest_totals=totals,
        trace_path=trace_path,
        manifest_path=manifest_path,
        telemetry_status=status,
    )


def collect_from_log(
    log_path: str | Path, config: dict, ticker: str, trade_date: str
) -> Evidence:
    """Rebuild the evidence record from a saved state log (for ``inspect``)."""
    path = Path(log_path)
    data = _read_json(path)
    if data is None:
        if not path.exists():
            raise FileNotFoundError(f"state log not found: {path}")
        raise ValueError(f"state log is not valid JSON: {path}")
    if not isinstance(data, dict):
        raise ValueError(f"state log is not a JSON object: {path}")

    final_state = {
        "company_of_interest": data.get("company_of_interest", ticker),
        "trade_date": data.get("trade_date", trade_date),
        "final_rating": data.get("final_rating", ""),
        "final_trade_decision": data.get("final_trade_decision", ""),
        "final_decision_source": data.get("final_decision_source", ""),
        "termination_reason": data.get("termination_reason", ""),
        "context_usage": data.get("context_usage", {}),
        "memory_note": data.get("memory_note", ""),
        "memory_sources": data.get("memory_sources", []),
        "past_context": "",
        "investment_debate_state": {
            "turn_records": _turn_records(data.get("investment_debate_state"))
        },
        "risk_debate_state": {"turn_records": _turn_records(data.get("risk_debate_state"))},
    }
    return collect_evidence(final_state, config, ticker, trade_date)


def find_state_log(ticker: str, date: str | None, results_dir: str | Path) -> StateLogRef:
    """Locate a ticker's state log: the named date, or the newest by mtime.

    The ticker is validated as a path component and the date as ``YYYY-MM-DD``,
    so neither can escape the results directory. A missing log raises
    ``FileNotFoundError`` naming the expected path.
    """
    safe_ticker = safe_ticker_component(ticker)
    directory = Path(results_dir) / safe_ticker / "TradingAgentsStrategy_logs"
    if date is not None:
        canonical = _validate_date(date)
        path = directory / f"full_states_log_{canonical}.json"
        if not path.exists():
            raise FileNotFoundError(f"no state log for {safe_ticker} on {canonical}: {path}")
        return StateLogRef(path, safe_ticker, canonical)

    candidates = list(directory.glob("full_states_log_*.json")) if directory.is_dir() else []
    if not candidates:
        raise FileNotFoundError(f"no state log found for {safe_ticker} under {directory}")
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    return StateLogRef(newest, safe_ticker, newest.stem.removeprefix("full_states_log_"))


# --- renderer ----------------------------------------------------------------


def _summary_grid(evidence: Evidence) -> Table:
    ctx = evidence.context
    budget = _int(ctx.get("budget"))
    total = _int(ctx.get("total_tokens"))
    pct = f"{round(100 * total / budget)}%" if budget > 0 else "n/a"
    context_line = (
        f"{_tokens(total)} / {_tokens(budget)} ({pct}) · "
        f"compacted {_int(ctx.get('compacted_calls'))} · max call {_tokens(ctx.get('max_call_tokens'))}"
    )

    source = evidence.decision_source or "not recorded"
    termination = evidence.termination_reason or "normal"
    decision_line = f"{evidence.rating or 'not recorded'} · {source} · termination {termination}"

    note = evidence.memory_note or "no note"
    if evidence.memory_sources:
        sources = " ".join(f"src:{s}" for s in evidence.memory_sources)
    else:
        sources = "not recorded"
    memory_line = f"{note} · {sources}"

    if evidence.telemetry_status == "disabled":
        telemetry_line = "telemetry disabled"
    else:
        telemetry_line = evidence.telemetry_status
        totals = evidence.manifest_totals
        if totals:
            telemetry_line += (
                f" · {_tokens(totals.get('tokens'))} tokens · {_int(totals.get('spans'))} spans"
            )

    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold cyan", no_wrap=True)
    grid.add_column()
    grid.add_row("Decision", decision_line)
    grid.add_row("Context", context_line)
    grid.add_row("Memory", memory_line)
    grid.add_row("Telemetry", telemetry_line)
    return grid


def _debate_table(evidence: Evidence) -> Table:
    table = Table(
        title="Structured Debate",
        box=box.SIMPLE_HEAD,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold magenta",
    )
    table.add_column("Debate", style="cyan", no_wrap=True)
    table.add_column("Turns", justify="right")
    table.add_column("Claim", style="green", max_width=40, overflow="ellipsis")
    table.add_column("Converge", style="green", max_width=40, overflow="ellipsis")
    for label, turns in (("Research", evidence.research_turns), ("Risk", evidence.risk_turns)):
        last = turns[-1] if turns else {}
        claim = _short(last.get("claim", ""), _DEBATE_EXCERPT) if isinstance(last, dict) else ""
        converge = (
            _short(last.get("converge", ""), _DEBATE_EXCERPT) if isinstance(last, dict) else ""
        )
        table.add_row(label, str(len(turns)), claim or "—", converge or "—")
    return table


def _guardrails_block(evidence: Evidence) -> Any:
    if evidence.telemetry_status == "disabled":
        return Text("telemetry disabled", style="dim")
    if not evidence.guardrails:
        return Text("no guardrail actions recorded", style="dim")
    table = Table(
        title="Guardrails",
        box=box.SIMPLE_HEAD,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold magenta",
    )
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Node", style="green")
    table.add_column("Detail", max_width=60, overflow="ellipsis")
    for event in evidence.guardrails:
        node = str(event.attributes.get("node") or event.phase)
        detail = _short(event.attributes.get("reason", ""), _GUARDRAIL_DETAIL)
        table.add_row(_guardrail_label(event.name), node, detail or "—")
    return table


def _phases_block(evidence: Evidence) -> Any:
    if not evidence.phases:
        return Text("no phase data", style="dim")
    ordered = sorted(
        evidence.phases.items(),
        key=lambda item: _int(item[1].get("tokens")),
        reverse=True,
    )
    table = Table(
        title="Phases",
        box=box.SIMPLE_HEAD,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold magenta",
    )
    table.add_column("Phase", style="cyan")
    table.add_column("Tokens", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Time", justify="right")

    def add_row(name: str, bucket: dict) -> None:
        table.add_row(
            name,
            _tokens(bucket.get("tokens")),
            f"${_float(bucket.get('est_cost')):.3f}",
            f"{_float(bucket.get('wall_clock_ms')) / 1000:.1f}s",
        )

    for name, bucket in ordered[:_PHASE_ROWS]:
        add_row(name, bucket)
    rest = ordered[_PHASE_ROWS:]
    if rest:
        other = {
            "tokens": sum(_int(b.get("tokens")) for _, b in rest),
            "est_cost": sum(_float(b.get("est_cost")) for _, b in rest),
            "wall_clock_ms": sum(_float(b.get("wall_clock_ms")) for _, b in rest),
        }
        add_row("other", other)

    totals = evidence.manifest_totals
    if totals:
        footer = Text(
            f"total: {_tokens(totals.get('tokens'))} tokens · "
            f"${_float(totals.get('est_cost')):.3f} · "
            f"{_float(totals.get('wall_clock_ms')) / 1000:.1f}s",
            style="dim",
        )
        return Group(table, footer)
    return table


def _paths_block(evidence: Evidence) -> Text:
    trace = f"trace: {evidence.trace_path}" if evidence.trace_path else "trace: not written"
    manifest = (
        f"manifest: {evidence.manifest_path}" if evidence.manifest_path else "manifest: not written"
    )
    return Text(f"{trace}\n{manifest}", style="dim")


def render_evidence(evidence: Evidence) -> Panel:
    """Render the evidence as a compact panel in the inherited Rich style."""
    body = Group(
        _summary_grid(evidence),
        Text(""),
        _debate_table(evidence),
        Text(""),
        _guardrails_block(evidence),
        Text(""),
        _phases_block(evidence),
        Text(""),
        _paths_block(evidence),
    )
    return Panel(
        body,
        title=f"Run Evidence · {evidence.ticker} · {evidence.trade_date}",
        border_style="green",
        padding=(1, 2),
    )
