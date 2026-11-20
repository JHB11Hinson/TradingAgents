"""Thresholds a fixed-set run must satisfy (D1-REQ-EVAL-001).

The file is a YAML mapping from a metric name to a single bound::

    metrics:
      total_tokens_ratio: {max: 0.5}
      review_rate: {max: 0.0}
      budget_respected_rate: {min: 1.0}

One bound per metric is deliberate. "At most" and "at least" are different
claims; a metric that needs both is a metric that needs splitting. An unknown
metric name is rejected, so a typo cannot quietly disable a check, and a missing
metric is an error rather than a pass.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .metrics import KNOWN_METRICS


class ThresholdError(ValueError):
    """The threshold file is missing, malformed or names an unknown metric."""


@dataclass(frozen=True)
class Threshold:
    """One metric and the bound it must not cross."""

    metric: str
    minimum: float | None = None
    maximum: float | None = None

    def evaluate(self, value: float | int) -> ThresholdOutcome:
        if self.maximum is not None:
            ok = float(value) <= self.maximum
        else:
            assert self.minimum is not None
            ok = float(value) >= self.minimum
        return ThresholdOutcome(
            metric=self.metric,
            minimum=self.minimum,
            maximum=self.maximum,
            value=value,
            ok=ok,
        )


@dataclass(frozen=True)
class ThresholdOutcome:
    """The measured value next to the bound it was judged against."""

    metric: str
    minimum: float | None
    maximum: float | None
    value: float | int
    ok: bool

    def describe(self) -> str:
        if self.maximum is not None:
            bound = f"<= {_format_bound(self.maximum)}"
        else:
            assert self.minimum is not None
            bound = f">= {_format_bound(self.minimum)}"
        verdict = "pass" if self.ok else "FAIL"
        return f"{self.metric}: {self.value} ({verdict}; required {bound})"


def load_thresholds(path: str | Path) -> tuple[Threshold, ...]:
    target = Path(path)
    try:
        data = yaml.safe_load(target.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ThresholdError(f"cannot read the thresholds {target}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ThresholdError(f"the thresholds {target} are not valid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ThresholdError("the threshold file must be a mapping")
    raw_metrics = data.get("metrics")
    if not isinstance(raw_metrics, dict) or not raw_metrics:
        raise ThresholdError("the threshold file must carry a non-empty 'metrics' mapping")

    thresholds = []
    for metric, raw in raw_metrics.items():
        if metric not in KNOWN_METRICS:
            raise ThresholdError(
                f"unknown metric {metric!r}; known metrics are {', '.join(KNOWN_METRICS)}"
            )
        if not isinstance(raw, dict):
            raise ThresholdError(f"the threshold for {metric} must be a mapping with min or max")
        unknown = set(raw) - {"min", "max"}
        if unknown:
            raise ThresholdError(f"the threshold for {metric} has unknown key(s): {', '.join(sorted(unknown))}")
        has_min, has_max = "min" in raw, "max" in raw
        if has_min == has_max:
            raise ThresholdError(f"the threshold for {metric} must set exactly one of min or max")
        bound = _number(raw["min"] if has_min else raw["max"], metric)
        if has_min:
            thresholds.append(Threshold(metric=metric, minimum=bound))
        else:
            thresholds.append(Threshold(metric=metric, maximum=bound))

    if not thresholds:
        raise ThresholdError("the threshold file has no thresholds")
    return tuple(thresholds)


def check_thresholds(
    thresholds: tuple[Threshold, ...] | list[Threshold],
    metrics: dict[str, float | int],
) -> tuple[ThresholdOutcome, ...]:
    """Judge every threshold; a metric missing from ``metrics`` is an error."""
    outcomes = []
    for threshold in thresholds:
        if threshold.metric not in metrics:
            raise ThresholdError(f"the report has no value for metric {threshold.metric!r}")
        outcomes.append(threshold.evaluate(metrics[threshold.metric]))
    return tuple(outcomes)


def _number(value: Any, metric: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ThresholdError(f"the threshold for {metric} must be a number")
    return float(value)


def _format_bound(value: float) -> str:
    """Print ``0`` rather than ``0.0`` for an integral bound."""
    return str(int(value)) if float(value).is_integer() else f"{value:g}"
