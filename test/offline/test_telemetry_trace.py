"""The run trace (D1-REQ-OBS-001).

A run writes a JSON trace that parses and carries one span per agent/tool step,
with its phase, start, end and duration. Trace attributes are an allowlist: a
key, an endpoint or a local path must never reach the file.
"""

from __future__ import annotations

import json
import time

import pytest

from tradingagents.telemetry import span, telemetry_scope, write_trace


@pytest.mark.unit
def test_trace_is_json_parsable_and_has_one_span_per_step(tmp_path):
    with telemetry_scope({"telemetry_enabled": True}, run_id="run-1") as hub:
        with span("market.agent", phase="market", kind="agent"):
            pass
        with span("market.tools", phase="market", kind="tool"):
            pass
        with span("Bull Researcher", phase="Bull Researcher", kind="agent"):
            pass

    path = write_trace(tmp_path / "trace.json", hub.events)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["run_id"] == "run-1"
    assert [step["name"] for step in payload["spans"]] == [
        "market.agent",
        "market.tools",
        "Bull Researcher",
    ]


@pytest.mark.unit
def test_span_records_phase_start_end_and_duration():
    with telemetry_scope({"telemetry_enabled": True}, run_id="run-1") as hub:
        with span("market.tools", phase="market", kind="tool"):
            time.sleep(0.005)

    event = hub.events[0]

    assert event.phase == "market"
    assert event.kind == "tool"
    assert event.started_at <= event.ended_at
    assert event.duration_ms >= 5


@pytest.mark.unit
def test_trace_contains_no_secret_or_path_attributes(tmp_path):
    with telemetry_scope({"telemetry_enabled": True}, run_id="run-1") as hub:
        with span(
            "market.agent",
            phase="market",
            attributes={
                "node": "market.agent",
                "api_key": "sk-live-secret",
                "endpoint": "https://provider.example/v1",
                "path": "/home/alice/.tradingagents",
            },
        ):
            pass

    path = write_trace(tmp_path / "trace.json", hub.events)
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)

    assert "sk-live-secret" not in text
    assert "provider.example" not in text
    assert "/home/alice" not in text
    assert payload["spans"][0]["attributes"] == {"node": "market.agent"}


@pytest.mark.unit
def test_an_exception_closes_the_span_before_it_propagates():
    with telemetry_scope({"telemetry_enabled": True}, run_id="run-1") as hub:
        with pytest.raises(RuntimeError, match="model exploded"):
            with span("market.agent", phase="market"):
                raise RuntimeError("model exploded")

    event = hub.events[0]

    assert event.attributes["error"] == "RuntimeError"
    assert event.ended_at >= event.started_at
