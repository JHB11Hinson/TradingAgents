"""The fixed-set report: run every case, aggregate, judge (EVAL-001, COST-001).

A case that raises is recorded as failed and the run continues: one broken case
must not hide the cost of the others, and ``cases_failed`` is itself a threshold
so a failure can never be mistaken for a pass. The report is plain JSON so a CI
job and a reader can consume the same artifact.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .baseline import Baseline
from .cases import EvaluationCase
from .metrics import CaseObservation, aggregate
from .thresholds import Threshold, ThresholdOutcome, check_thresholds


@dataclass(frozen=True)
class CaseResult:
    """One case's outcome, successful or not."""

    case_id: str
    ok: bool
    total_tokens: int = 0
    uncapped_tokens: int = 0
    budget: int = 0
    compacted_calls: int = 0
    wall_clock_s: float = 0.0
    rating: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "case": self.case_id,
            "ok": self.ok,
            "total_tokens": self.total_tokens,
            "uncapped_tokens": self.uncapped_tokens,
            "budget": self.budget,
            "compacted_calls": self.compacted_calls,
            "wall_clock_s": self.wall_clock_s,
            "rating": self.rating,
            "error": self.error,
        }


@dataclass(frozen=True)
class EvaluationReport:
    """The metrics, the per-case evidence and the threshold verdicts."""

    metrics: Mapping[str, float | int]
    cases: tuple[CaseResult, ...]
    thresholds: tuple[ThresholdOutcome, ...]
    set_path: str
    thresholds_path: str
    baseline: Baseline
    started_at: str

    @property
    def ok(self) -> bool:
        return all(outcome.ok for outcome in self.thresholds)

    def failed_thresholds(self) -> tuple[ThresholdOutcome, ...]:
        return tuple(outcome for outcome in self.thresholds if not outcome.ok)

    def summary(self) -> str:
        lines = [
            f"eval.run: {len(self.cases)} case(s), "
            f"{sum(1 for case in self.cases if not case.ok)} failed",
            f"  set: {self.set_path}",
            f"  baseline: {self.baseline.total_tokens} tokens / "
            f"${self.baseline.est_cost_usd:.2f} per analysis "
            f"({self.baseline.source})",
            f"  same condition: {self.metrics.get('total_tokens', 0)} capped / "
            f"{self.metrics.get('uncapped_tokens', 0)} uncapped "
            f"(ratio {self.metrics.get('capped_tokens_ratio', 1.0)})",
        ]
        for outcome in self.thresholds:
            lines.append(f"  {outcome.describe()}")
        for case in self.cases:
            if case.ok:
                lines.append(
                    f"  {case.case_id}: {case.total_tokens} tokens "
                    f"({case.uncapped_tokens} uncapped) / budget {case.budget} "
                    f"({case.compacted_calls} compacted), rating {case.rating or 'n/a'}, "
                    f"{case.wall_clock_s:.2f}s"
                )
            else:
                lines.append(f"  {case.case_id}: FAILED — {case.error}")
        lines.append("  verdict: " + ("pass" if self.ok else "FAIL"))
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "set": self.set_path,
            "thresholds_file": self.thresholds_path,
            "started_at": self.started_at,
            "baseline": {
                "recorded_at": self.baseline.recorded_at,
                "source": self.baseline.source,
                "total_tokens_per_analysis": self.baseline.total_tokens,
                "est_cost_usd_per_analysis": self.baseline.est_cost_usd,
                "usd_per_million_input_tokens": self.baseline.usd_per_million_input_tokens,
            },
            "metrics": dict(sorted(self.metrics.items())),
            "thresholds": [
                {
                    "metric": outcome.metric,
                    "value": outcome.value,
                    "min": outcome.minimum,
                    "max": outcome.maximum,
                    "ok": outcome.ok,
                }
                for outcome in self.thresholds
            ],
            "cases": [case.to_dict() for case in self.cases],
        }

    def write(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return target


def evaluate_cases(
    cases: Sequence[EvaluationCase],
    analyze: Callable[[EvaluationCase], CaseObservation],
    baseline: Baseline,
    thresholds: Sequence[Threshold],
    started_at: str | None = None,
    set_path: str = "",
    thresholds_path: str = "",
) -> EvaluationReport:
    """Run every case, aggregate the observations and judge the thresholds."""
    results: list[CaseResult] = []
    observations: list[CaseObservation] = []

    for case in cases:
        start = time.perf_counter()
        try:
            observation = analyze(case)
        except Exception as exc:  # noqa: BLE001 - a broken case is evidence, not a crash
            results.append(
                CaseResult(
                    case_id=case.id,
                    ok=False,
                    wall_clock_s=round(time.perf_counter() - start, 3),
                    error=f"{type(exc).__name__}: {exc}",
                )
            )
            continue
        elapsed = observation.wall_clock_s or (time.perf_counter() - start)
        results.append(
            CaseResult(
                case_id=case.id,
                ok=True,
                total_tokens=observation.total_tokens,
                uncapped_tokens=observation.uncapped_total_tokens or 0,
                budget=observation.budget,
                compacted_calls=observation.compacted_calls,
                wall_clock_s=round(elapsed, 3),
                rating=observation.rating,
            )
        )
        observations.append(observation)

    metrics = aggregate(observations, baseline, len(cases))
    outcomes = check_thresholds(tuple(thresholds), metrics)
    return EvaluationReport(
        metrics=metrics,
        cases=tuple(results),
        thresholds=outcomes,
        set_path=set_path,
        thresholds_path=thresholds_path,
        baseline=baseline,
        started_at=started_at or datetime.now(UTC).isoformat(timespec="seconds"),
    )
