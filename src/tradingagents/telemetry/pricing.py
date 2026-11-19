"""Deterministic, offline price book for the run manifest (OBS-002).

Prices are USD per million tokens. The table is local on purpose: telemetry must
not call a provider, and an unknown model is a zero cost plus a warning rather
than a fabricated number.
"""

from __future__ import annotations

from collections.abc import Mapping

# Provider list prices at the time of writing; update when a provider changes
# them. A model absent here is reported as an unknown-cost warning.
DEFAULT_PRICING: Mapping[str, Mapping[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
}

_PER_MILLION = 1_000_000


def estimate_cost(
    model: str | None,
    tokens_in: int,
    tokens_out: int,
    pricing: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[float, str | None]:
    """Return ``(usd, warning)`` for one model call.

    ``model=None`` is a step with no model call (a tool, for example): zero
    cost and no warning. An unknown model is zero cost and a warning.
    """
    if model is None:
        return 0.0, None
    table = DEFAULT_PRICING if pricing is None else pricing
    prices = table.get(model)
    if prices is None:
        return 0.0, f"no price for model {model!r}; est_cost reported as 0"
    cost = (
        int(tokens_in) * float(prices.get("input", 0.0))
        + int(tokens_out) * float(prices.get("output", 0.0))
    ) / _PER_MILLION
    return round(cost, 8), None
