"""Telemetry at run boundaries (D1-REQ-OBS-001/002/003).

The whole graph runs offline with scripted models: the trace and manifest land
next to the saved state log, a broken subscriber leaves the run green, and a
disabled switch writes nothing at all.
"""

from __future__ import annotations

import json

import pytest
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult

from test.offline.test_graph_end_to_end import TRADE_DATE, ScriptedModel, _graph, offline  # noqa: F401
from tradingagents.telemetry import TelemetryCallback, span, telemetry_scope


def _logs(tmp_path):
    return tmp_path / "results" / "NVDA" / "TradingAgentsStrategy_logs" / "telemetry"


@pytest.mark.unit
def test_a_run_writes_a_trace_and_a_manifest(tmp_path, monkeypatch, offline):  # noqa: F811
    graph = _graph(tmp_path, monkeypatch, ScriptedModel())

    graph.propagate("NVDA", TRADE_DATE)

    trace = json.loads((_logs(tmp_path) / f"trace_{TRADE_DATE}.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (_logs(tmp_path) / f"manifest_{TRADE_DATE}.json").read_text(encoding="utf-8")
    )
    names = {step["name"] for step in trace["spans"]}

    assert "market.agent" in names
    assert "market.tools" in names
    assert "Bull Researcher" in names
    assert {"market", "Bull Researcher"} <= set(manifest["phases"])
    assert manifest["totals"]["spans"] == len(trace["spans"])
    assert manifest["totals"]["wall_clock_ms"] >= 0


@pytest.mark.unit
def test_usage_metadata_is_attributed_to_the_active_span():
    message = AIMessage(
        content="Report.",
        usage_metadata={"input_tokens": 120, "output_tokens": 30, "total_tokens": 150},
    )
    response = LLMResult(generations=[[ChatGeneration(message=message)]])

    with telemetry_scope({"telemetry_enabled": True}, run_id="run-1") as hub:
        with span("market.agent", phase="market", kind="agent"):
            TelemetryCallback().on_llm_end(response)

    event = hub.events[0]

    assert (event.tokens_in, event.tokens_out) == (120, 30)
    assert event.attributes["model"] is None


@pytest.mark.unit
def test_a_broken_subscriber_leaves_the_run_green(tmp_path, monkeypatch, offline):  # noqa: F811
    graph = _graph(tmp_path, monkeypatch, ScriptedModel())

    def broken(_event):
        raise RuntimeError("subscriber down")

    with telemetry_scope({"telemetry_enabled": True}, run_id="outer") as hub:
        hub.subscribe(broken)
        _, signal = graph.propagate("NVDA", TRADE_DATE)

    assert signal == "Overweight"
    assert hub.warnings


@pytest.mark.unit
def test_an_outer_subscriber_still_gets_the_trace_and_manifest(tmp_path, monkeypatch, offline):  # noqa: F811
    graph = _graph(tmp_path, monkeypatch, ScriptedModel())

    with telemetry_scope({"telemetry_enabled": True}, run_id="outer") as hub:
        graph.propagate("NVDA", TRADE_DATE)

    assert hub.events
    assert (_logs(tmp_path) / f"trace_{TRADE_DATE}.json").exists()
    assert (_logs(tmp_path) / f"manifest_{TRADE_DATE}.json").exists()


@pytest.mark.unit
def test_a_failed_run_marks_the_trace_as_failed(tmp_path, monkeypatch, offline):  # noqa: F811
    graph = _graph(tmp_path, monkeypatch, ScriptedModel(fail_at=12), checkpoint_enabled=True)

    with pytest.raises(RuntimeError, match="provider unavailable"):
        graph.propagate("NVDA", TRADE_DATE)

    trace = json.loads((_logs(tmp_path) / f"trace_{TRADE_DATE}.json").read_text(encoding="utf-8"))
    assert trace["status"] == "failed"


@pytest.mark.unit
def test_a_resumed_run_merges_the_failed_leg(tmp_path, monkeypatch, offline):  # noqa: F811
    graph = _graph(tmp_path, monkeypatch, ScriptedModel(fail_at=12), checkpoint_enabled=True)
    with pytest.raises(RuntimeError, match="provider unavailable"):
        graph.propagate("NVDA", TRADE_DATE)
    failed = json.loads((_logs(tmp_path) / f"trace_{TRADE_DATE}.json").read_text(encoding="utf-8"))

    graph.propagate("NVDA", TRADE_DATE)

    resumed = json.loads(
        (_logs(tmp_path) / f"trace_{TRADE_DATE}.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (_logs(tmp_path) / f"manifest_{TRADE_DATE}.json").read_text(encoding="utf-8")
    )
    assert resumed["status"] == "complete"
    assert len(resumed["spans"]) > len(failed["spans"])
    assert manifest["totals"]["spans"] == len(resumed["spans"])


@pytest.mark.unit
def test_disabled_telemetry_writes_nothing(tmp_path, monkeypatch, offline):  # noqa: F811
    graph = _graph(tmp_path, monkeypatch, ScriptedModel(), telemetry_enabled=False)

    _, signal = graph.propagate("NVDA", TRADE_DATE)

    assert signal == "Overweight"
    assert not list(_logs(tmp_path).glob("trace_*.json"))
    assert not list(_logs(tmp_path).glob("manifest_*.json"))
