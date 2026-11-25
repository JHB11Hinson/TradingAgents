"""The Run Evidence panel and the state-log finder (D1-REQ-OBS-001/002/003).

A finished run already writes a state log, a telemetry trace and a manifest.
These tests fix what the panel must show from them: the decision and its source,
the context budget, the structured debate, the guardrail events, the memory
attribution and the paths to the two telemetry files. A run whose evidence is
missing or disabled must still render, saying so, rather than raise.
"""

from __future__ import annotations

import json
import os
from io import StringIO
from pathlib import Path

import pytest
from cli.evidence import (
    Evidence,
    collect_evidence,
    collect_from_log,
    find_state_log,
    render_evidence,
)
from rich.console import Console

from tradingagents.telemetry import (
    TelemetryEvent,
    run_output_dir,
    span,
    telemetry_scope,
    write_trace,
)


def _render(evidence: Evidence) -> str:
    buffer = StringIO()
    console = Console(file=buffer, width=120)
    console.print(render_evidence(evidence))
    return buffer.getvalue()


def _guardrail_event() -> TelemetryEvent:
    return TelemetryEvent(
        run_id="run-1",
        name="guardrail.position_clipped",
        phase="Portfolio Manager",
        kind="guardrail",
        started_at="2026-11-20T10:00:00.000+00:00",
        ended_at="2026-11-20T10:00:00.010+00:00",
        duration_ms=10.0,
        attributes={
            "node": "Portfolio Manager",
            "reason": "position size 50% exceeds the 10% ceiling; clipped to 10%",
        },
    )


def _evidence(**overrides) -> Evidence:
    values = {
        "ticker": "NVDA",
        "trade_date": "2026-11-20",
        "rating": "Hold",
        "decision_source": "structured",
        "termination_reason": "",
        "context": {
            "budget": 0,
            "total_tokens": 0,
            "compacted_calls": 0,
            "max_call_tokens": 0,
        },
        "research_turns": [],
        "risk_turns": [],
        "guardrails": [],
        "memory_note": "",
        "memory_sources": (),
        "phases": {},
        "manifest_totals": {
            "tokens_in": 0,
            "tokens_out": 0,
            "tokens": 0,
            "est_cost": 0.0,
            "wall_clock_ms": 0.0,
            "spans": 0,
        },
        "trace_path": Path("/runs/NVDA/telemetry/trace_2026-11-20.json"),
        "manifest_path": Path("/runs/NVDA/telemetry/manifest_2026-11-20.json"),
        "telemetry_status": "complete",
    }
    values.update(overrides)
    return Evidence(**values)


def _state(**overrides) -> dict:
    values = {
        "company_of_interest": "NVDA",
        "trade_date": "2026-11-20",
        "final_rating": "Hold",
        "final_trade_decision": "**Rating**: Hold",
        "final_decision_source": "structured",
        "termination_reason": "",
        "context_usage": {
            "budget": 0,
            "total_tokens": 0,
            "compacted_calls": 0,
            "max_call_tokens": 0,
        },
        "memory_note": "",
        "past_context": "",
        "investment_debate_state": {"turn_records": []},
        "risk_debate_state": {"turn_records": []},
    }
    values.update(overrides)
    return values


@pytest.mark.unit
def test_render_evidence_shows_decision_context_debate_memory_and_paths():
    evidence = _evidence(
        rating="Overweight",
        decision_source="structured",
        context={
            "budget": 50000,
            "total_tokens": 43500,
            "compacted_calls": 2,
            "max_call_tokens": 12100,
        },
        memory_note="1 past decision could not be settled",
        memory_sources=("2026-10-01/NVDA",),
        research_turns=[
            {
                "claim": "Guidance raised 8%",
                "evidence": "Q3 filing",
                "converge": "Demand is strong",
            }
        ],
        risk_turns=[
            {
                "claim": "Valuation is stretched",
                "evidence": "Forward P/E",
                "converge": "Trim into strength",
            }
        ],
        guardrails=[_guardrail_event()],
        phases={
            "market": {
                "tokens": 21400,
                "est_cost": 0.031,
                "wall_clock_ms": 18200.0,
                "spans": 3,
            }
        },
    )

    output = _render(evidence)

    assert "Run Evidence" in output
    assert "Overweight" in output
    assert "structured" in output
    assert "43.5k" in output
    assert "50.0k" in output
    assert "compacted 2" in output
    assert "Research" in output
    assert "Risk" in output
    assert "src:2026-10-01/NVDA" in output
    assert "trace_2026-11-20.json" in output
    assert "manifest_2026-11-20.json" in output


@pytest.mark.unit
def test_long_debate_excerpts_are_truncated():
    claim = "x" * 500
    evidence = _evidence(research_turns=[{"claim": claim, "evidence": "", "converge": ""}])

    output = _render(evidence)

    assert claim not in output
    assert output.count("x") < 500
    assert "…" in output


@pytest.mark.unit
def test_missing_trace_and_manifest_renders_not_written(tmp_path):
    config = {"results_dir": str(tmp_path), "telemetry_enabled": True}

    output = _render(collect_evidence(_state(), config, "NVDA", "2026-11-20"))

    assert output.count("not written") >= 2


@pytest.mark.unit
def test_telemetry_disabled_says_so(tmp_path):
    config = {"results_dir": str(tmp_path), "telemetry_enabled": False}

    output = _render(collect_evidence(_state(), config, "NVDA", "2026-11-20"))

    assert "telemetry disabled" in output


@pytest.mark.unit
def test_collect_evidence_reads_guardrail_spans_from_trace(tmp_path):
    config = {"results_dir": str(tmp_path), "telemetry_enabled": True}
    with telemetry_scope({"telemetry_enabled": True}, run_id="run-1") as hub, span(
        "guardrail.position_clipped",
        phase="Portfolio Manager",
        kind="guardrail",
        attributes={
            "node": "Portfolio Manager",
            "reason": "position size 50% exceeds the 10% ceiling; clipped to 10%",
        },
    ):
        pass
    write_trace(
        run_output_dir(config, "NVDA") / "trace_2026-11-20.json",
        hub.events,
    )

    output = _render(collect_evidence(_state(), config, "NVDA", "2026-11-20"))

    assert "Position clipped" in output
    assert "50%" in output


@pytest.mark.unit
def test_find_state_log_uses_the_latest_file_and_rejects_a_bad_date(tmp_path):
    log_dir = tmp_path / "NVDA" / "TradingAgentsStrategy_logs"
    log_dir.mkdir(parents=True)
    older = log_dir / "full_states_log_2026-11-19.json"
    newer = log_dir / "full_states_log_2026-11-20.json"
    older.write_text("{}", encoding="utf-8")
    newer.write_text("{}", encoding="utf-8")
    os.utime(older, (1_700_000_000, 1_700_000_000))
    os.utime(newer, (1_700_100_000, 1_700_100_000))

    found = find_state_log("NVDA", None, tmp_path)
    assert Path(found.path) == newer

    with pytest.raises(ValueError):
        find_state_log("NVDA", "../etc/passwd", tmp_path)

    with pytest.raises(FileNotFoundError):
        find_state_log("NVDA", "2026-01-09", tmp_path)


@pytest.mark.unit
def test_an_old_state_log_without_the_new_fields_still_renders(tmp_path):
    log_dir = tmp_path / "NVDA" / "TradingAgentsStrategy_logs"
    log_dir.mkdir(parents=True)
    path = log_dir / "full_states_log_2026-11-20.json"
    path.write_text(
        json.dumps(
            {
                "company_of_interest": "NVDA",
                "trade_date": "2026-11-20",
                "final_trade_decision": "**Rating**: Hold",
                "final_rating": "Hold",
                "termination_reason": "",
                "context_usage": {},
            }
        ),
        encoding="utf-8",
    )

    evidence = collect_from_log(
        path, {"results_dir": str(tmp_path)}, "NVDA", "2026-11-20"
    )
    output = _render(evidence)

    assert "Hold" in output
    assert "not recorded" in output
