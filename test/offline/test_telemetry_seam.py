"""The in-process event seam (D1-REQ-OBS-003).

A subscriber that raises must never block the run; the failure is recorded as a
telemetry warning. ``KeyboardInterrupt``/``SystemExit`` are not subscriber
failures and must still stop the run.
"""

from __future__ import annotations

import pytest

from tradingagents.telemetry import (
    Telemetry,
    TelemetryEvent,
    current_telemetry,
    span,
    telemetry_scope,
)


def _event(**overrides) -> TelemetryEvent:
    values = {
        "run_id": "run-1",
        "name": "Market Analyst",
        "phase": "market",
        "kind": "agent",
        "started_at": "2026-01-09T00:00:00+00:00",
        "ended_at": "2026-01-09T00:00:01+00:00",
        "duration_ms": 1000.0,
    }
    values.update(overrides)
    return TelemetryEvent(**values)


@pytest.mark.unit
def test_event_reaches_every_subscriber():
    hub = Telemetry(run_id="run-1")
    first, second = [], []

    hub.subscribe(first.append)
    hub.subscribe(second.append)
    event = _event()
    hub.emit(event)

    assert first == [event]
    assert second == [event]
    assert hub.events == (event,)


@pytest.mark.unit
def test_raising_subscriber_does_not_block_and_is_recorded():
    hub = Telemetry(run_id="run-1")
    delivered = []

    def broken(_event):
        raise RuntimeError("subscriber exploded")

    hub.subscribe(broken)
    hub.subscribe(delivered.append)
    event = _event()

    hub.emit(event)  # must not raise

    assert delivered == [event]
    assert event in hub.events
    assert len(hub.warnings) == 1
    assert "subscriber exploded" in hub.warnings[0]


@pytest.mark.unit
def test_keyboard_interrupt_is_never_swallowed():
    hub = Telemetry(run_id="run-1")

    def interrupted(_event):
        raise KeyboardInterrupt

    hub.subscribe(interrupted)

    with pytest.raises(KeyboardInterrupt):
        hub.emit(_event())


@pytest.mark.unit
def test_unsubscribe_stops_delivery():
    hub = Telemetry(run_id="run-1")
    seen = []

    unsubscribe = hub.subscribe(seen.append)
    unsubscribe()
    hub.emit(_event())

    assert seen == []


@pytest.mark.unit
def test_disabled_scope_has_no_hub_and_span_is_a_noop():
    with telemetry_scope({"telemetry_enabled": False}) as hub:
        assert hub is None
        assert current_telemetry() is None
        with span("Market Analyst", phase="market") as recorded:
            assert recorded is None


@pytest.mark.unit
def test_nested_scope_reuses_the_open_hub():
    with telemetry_scope({"telemetry_enabled": True}, run_id="outer") as outer:
        with telemetry_scope({"telemetry_enabled": True}, run_id="inner") as inner:
            assert inner is outer
        assert current_telemetry() is outer
