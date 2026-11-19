"""The in-process telemetry event seam (D1-REQ-OBS-003).

One run owns one :class:`Telemetry` hub. Nodes emit :class:`TelemetryEvent`
objects to it; subscribers may be added by a caller (the CLI, a test, an
exporter) without the graph knowing about them. A subscriber that raises is
recorded as a warning and skipped: telemetry is advisory and must never decide
whether a run succeeds. ``KeyboardInterrupt`` and ``SystemExit`` are not
subscriber failures and still stop the run.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

# Trace attributes are an allowlist. Prompts, provider endpoints, API keys and
# local paths must never reach a file that may be shared with a report.
SAFE_ATTRIBUTE_KEYS = frozenset({"node", "error", "model"})


def utc_now() -> str:
    """An ISO-8601 UTC timestamp with millisecond precision."""
    return datetime.now(UTC).isoformat(timespec="milliseconds")


@dataclass(frozen=True)
class TelemetryEvent:
    """One finished span: an agent or tool step, with its phase and timing."""

    run_id: str
    name: str
    phase: str
    kind: str
    started_at: str
    ended_at: str
    duration_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    model: str | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        """A JSON-safe record; only allowlisted attributes survive."""
        attributes = {
            key: value
            for key, value in self.attributes.items()
            if key in SAFE_ATTRIBUTE_KEYS and value is not None
        }
        return {
            "run_id": self.run_id,
            "name": self.name,
            "phase": self.phase,
            "kind": self.kind,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": round(self.duration_ms, 3),
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "model": self.model,
            "attributes": attributes,
        }


Subscriber = Callable[[TelemetryEvent], None]


class Telemetry:
    """The hub of one run: it records every event and fans it out."""

    def __init__(self, run_id: str | None = None) -> None:
        self.run_id = run_id or uuid.uuid4().hex
        self._subscribers: list[Subscriber] = []
        self._events: list[TelemetryEvent] = []
        self.warnings: list[str] = []

    @property
    def events(self) -> tuple[TelemetryEvent, ...]:
        """Every event this run emitted, in completion order."""
        return tuple(self._events)

    def subscribe(self, subscriber: Subscriber) -> Callable[[], None]:
        """Register a subscriber and return the function that removes it."""
        self._subscribers.append(subscriber)

        def unsubscribe() -> None:
            if subscriber in self._subscribers:
                self._subscribers.remove(subscriber)

        return unsubscribe

    def emit(self, event: TelemetryEvent) -> None:
        """Record ``event`` and hand it to every subscriber.

        A failing subscriber is a warning, not a run failure. Control-flow
        exceptions are re-raised so Ctrl-C still works.
        """
        self._events.append(event)
        for subscriber in list(self._subscribers):
            try:
                subscriber(event)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as exc:  # noqa: BLE001 - a subscriber is untrusted
                self.warnings.append(
                    f"telemetry subscriber failed: {type(exc).__name__}: {exc}"
                )
