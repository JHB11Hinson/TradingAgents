"""The run scope and the span context manager (D1-REQ-OBS-001/003).

``telemetry_scope`` opens the run's hub; ``span`` measures one agent or tool
step and emits it when the step finishes, including when it raises. Outside an
enabled scope both are no-ops, so a caller that switches telemetry off pays
nothing and writes nothing.
"""

from __future__ import annotations

import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from .events import SAFE_ATTRIBUTE_KEYS, Telemetry, TelemetryEvent, utc_now

_CURRENT: ContextVar[Telemetry | None] = ContextVar("tradingagents_telemetry", default=None)
_ACTIVE: ContextVar[Span | None] = ContextVar("tradingagents_telemetry_span", default=None)


def current_telemetry() -> Telemetry | None:
    """The hub of the run in progress, or None outside a telemetry scope."""
    return _CURRENT.get()


def current_span() -> Span | None:
    """The span of the step in progress, or None outside a span."""
    return _ACTIVE.get()


@contextmanager
def telemetry_scope(
    config: Mapping[str, Any] | None = None,
    run_id: str | None = None,
) -> Iterator[Telemetry | None]:
    """Open the run's hub unless one is already open.

    ``telemetry_enabled`` (default True) decides whether a hub exists at all.
    A nested scope reuses the open hub, so a caller can subscribe before a run
    and still see the graph's events.
    """
    existing = _CURRENT.get()
    if existing is not None:
        yield existing
        return
    enabled = True if config is None else bool(config.get("telemetry_enabled", True))
    if not enabled:
        yield None
        return
    hub = Telemetry(run_id=run_id)
    token = _CURRENT.set(hub)
    try:
        yield hub
    finally:
        _CURRENT.reset(token)


class Span:
    """A mutable step record; the event is frozen when the span closes."""

    def __init__(
        self,
        hub: Telemetry,
        name: str,
        phase: str,
        kind: str,
        attributes: Mapping[str, Any] | None = None,
    ) -> None:
        self._hub = hub
        self.name = name
        self.phase = phase
        self.kind = kind
        self.started_at = utc_now()
        self.ended_at = self.started_at
        self.duration_ms = 0.0
        self.tokens_in = 0
        self.tokens_out = 0
        self.model: str | None = None
        self.attributes: dict[str, Any] = {
            key: value
            for key, value in (attributes or {}).items()
            if key in SAFE_ATTRIBUTE_KEYS
        }
        self.attributes.setdefault("model", None)

    def add_usage(self, tokens_in: int, tokens_out: int, model: str | None = None) -> None:
        """Add one model call's token usage to this step."""
        self.tokens_in += int(tokens_in or 0)
        self.tokens_out += int(tokens_out or 0)
        if model:
            self.model = model
            self.attributes["model"] = model

    def set_attribute(self, key: str, value: Any) -> None:
        """Record an attribute if the allowlist permits it."""
        if key in SAFE_ATTRIBUTE_KEYS:
            self.attributes[key] = value

    def to_event(self) -> TelemetryEvent:
        return TelemetryEvent(
            run_id=self._hub.run_id,
            name=self.name,
            phase=self.phase,
            kind=self.kind,
            started_at=self.started_at,
            ended_at=self.ended_at,
            duration_ms=self.duration_ms,
            tokens_in=self.tokens_in,
            tokens_out=self.tokens_out,
            model=self.model,
            attributes=dict(self.attributes),
        )


@contextmanager
def span(
    name: str,
    phase: str | None = None,
    kind: str = "agent",
    attributes: Mapping[str, Any] | None = None,
) -> Iterator[Span | None]:
    """Measure one agent or tool step and emit it when the step finishes."""
    hub = current_telemetry()
    if hub is None:
        yield None
        return
    record = Span(hub, name, phase or name, kind, attributes)
    started = time.perf_counter()
    token = _ACTIVE.set(record)
    try:
        yield record
    except BaseException as exc:
        record.set_attribute("error", type(exc).__name__)
        raise
    finally:
        record.duration_ms = (time.perf_counter() - started) * 1000.0
        record.ended_at = utc_now()
        _ACTIVE.reset(token)
        hub.emit(record.to_event())
