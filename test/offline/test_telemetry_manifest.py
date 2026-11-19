"""The run manifest (D1-REQ-OBS-002).

Per phase it aggregates input/output tokens, estimated cost and wall-clock; the
totals equal the sum of the phases. A model with no price is a zero cost plus a
warning, never a crash.
"""

from __future__ import annotations

import json

import pytest

from tradingagents.telemetry import (
    TelemetryEvent,
    build_manifest,
    estimate_cost,
    write_manifest,
    write_run_telemetry,
)

PRICING = {"gpt-4o": {"input": 2.50, "output": 10.00}}


def _span(phase, tokens_in=0, tokens_out=0, duration_ms=0.0, model="gpt-4o", **overrides):
    values = {
        "run_id": "run-1",
        "name": phase,
        "phase": phase,
        "kind": "agent",
        "started_at": "2026-01-09T00:00:00+00:00",
        "ended_at": "2026-01-09T00:00:01+00:00",
        "duration_ms": duration_ms,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "model": model,
    }
    values.update(overrides)
    return TelemetryEvent(**values)


@pytest.mark.unit
def test_manifest_aggregates_tokens_cost_and_wall_clock_per_phase():
    events = [
        _span("market", 1_000, 500, 100.0),
        _span("market", 0, 0, 50.0, model=None, kind="tool"),
        _span("Bull Researcher", 2_000, 1_000, 200.0),
    ]

    manifest = build_manifest(events, PRICING)

    market = manifest["phases"]["market"]
    assert market["tokens_in"] == 1_000
    assert market["tokens_out"] == 500
    assert market["tokens"] == 1_500
    assert market["wall_clock_ms"] == pytest.approx(150.0)
    assert market["spans"] == 2
    assert market["est_cost"] == pytest.approx(0.0075)

    debate = manifest["phases"]["Bull Researcher"]
    assert debate["tokens"] == 3_000
    assert debate["est_cost"] == pytest.approx(0.015)


@pytest.mark.unit
def test_manifest_totals_equal_the_sum_of_the_phases():
    events = [_span("market", 1_000, 500, 100.0), _span("news", 500, 250, 40.0)]

    manifest = build_manifest(events, PRICING)

    assert manifest["totals"]["tokens_in"] == 1_500
    assert manifest["totals"]["tokens_out"] == 750
    assert manifest["totals"]["tokens"] == 2_250
    assert manifest["totals"]["wall_clock_ms"] == pytest.approx(140.0)
    assert manifest["totals"]["spans"] == 2
    assert manifest["totals"]["est_cost"] == pytest.approx(
        sum(phase["est_cost"] for phase in manifest["phases"].values())
    )


@pytest.mark.unit
def test_unknown_model_costs_zero_and_warns():
    cost, warning = estimate_cost("mystery-model", 1_000, 1_000, PRICING)

    assert cost == 0.0
    assert warning is not None
    assert "mystery-model" in warning


@pytest.mark.unit
def test_manifest_records_an_unknown_model_as_a_warning():
    manifest = build_manifest([_span("market", 10, 10, 5.0, model="mystery-model")], PRICING)

    assert manifest["phases"]["market"]["est_cost"] == 0.0
    assert any("mystery-model" in warning for warning in manifest["warnings"])


@pytest.mark.unit
def test_manifest_is_written_as_parsable_json(tmp_path):
    manifest = build_manifest([_span("market", 10, 10, 5.0)], PRICING)

    path = write_manifest(tmp_path / "manifest.json", manifest)

    assert json.loads(path.read_text(encoding="utf-8"))["totals"]["spans"] == 1


@pytest.mark.unit
def test_run_output_uses_a_configured_price_table(tmp_path):
    config = {
        "results_dir": str(tmp_path),
        "telemetry_pricing": {"mystery-model": {"input": 1.0, "output": 2.0}},
    }

    write_run_telemetry(
        config, "NVDA", "2026-01-09", [_span("market", 1_000_000, 0, 5.0, model="mystery-model")]
    )

    manifest = json.loads(
        (
            tmp_path / "NVDA" / "TradingAgentsStrategy_logs" / "telemetry"
            / "manifest_2026-01-09.json"
        ).read_text(encoding="utf-8")
    )
    assert manifest["phases"]["market"]["est_cost"] == pytest.approx(1.0)
