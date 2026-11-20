"""Deterministic evaluation of a fixed set (D1-REQ-EVAL-001, D1-REQ-COST-001).

The package is pure policy: a fixed set of cases, a threshold file, a recorded
baseline, and the aggregation that turns one run per case into a pass/fail
verdict. The backend that actually runs an analysis (offline replay or a live
provider) lives outside it, in ``eval/``, so the rules stay importable and
testable without a model, a key or a network.

The fit criteria this package makes checkable:

- ``EVAL-001``: ``python -m eval.run --set ... --thresholds ...`` exits non-zero
  when a threshold fails and zero when it passes.
- ``COST-001``: the run reports ``total_tokens`` and ``est_cost_usd`` at or below
  half of the recorded baseline, aggregated over the fixed set.
"""

from .baseline import Baseline, BaselineError, load_baseline
from .cases import ANALYSTS, EvaluationCase, FixedSetError, load_fixed_set
from .metrics import KNOWN_METRICS, CaseObservation, aggregate
from .report import CaseResult, EvaluationReport, evaluate_cases
from .thresholds import (
    Threshold,
    ThresholdError,
    ThresholdOutcome,
    check_thresholds,
    load_thresholds,
)

__all__ = [
    "ANALYSTS",
    "KNOWN_METRICS",
    "Baseline",
    "BaselineError",
    "CaseObservation",
    "CaseResult",
    "EvaluationCase",
    "EvaluationReport",
    "FixedSetError",
    "Threshold",
    "ThresholdError",
    "ThresholdOutcome",
    "aggregate",
    "check_thresholds",
    "evaluate_cases",
    "load_baseline",
    "load_fixed_set",
    "load_thresholds",
]
