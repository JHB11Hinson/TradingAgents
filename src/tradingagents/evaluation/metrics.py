"""Aggregation of one run per case into the fixed-set metrics (EVAL-001, COST-001).

``total_tokens`` is what the run ledger recorded, i.e. the whole request each
model call received (see ``tradingagents.context.assembler``). ``est_cost_usd``
is only that number priced: the offline backend makes no paid calls, so a
provider-reported cost would be zero and the cost check would pass for the
wrong reason. ``usd_per_million_input_tokens`` comes from the baseline, so both
sides of the ratio are valued at the same price.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .baseline import Baseline

REVIEW = "REVIEW"

KNOWN_METRICS: tuple[str, ...] = (
    "cases",
    "cases_failed",
    "total_tokens",
    "uncapped_tokens",
    "baseline_tokens",
    "total_tokens_ratio",
    "capped_tokens_ratio",
    "est_cost_usd",
    "baseline_cost_usd",
    "est_cost_ratio",
    "budget_respected_rate",
    "review_rate",
    "wall_clock_s",
)


@dataclass(frozen=True)
class CaseObservation:
    """What one finished analysis reported about itself."""

    total_tokens: int
    budget: int
    compacted_calls: int = 0
    wall_clock_s: float = 0.0
    rating: str = ""
    est_cost_usd: float | None = None
    uncapped_total_tokens: int | None = None


def aggregate(
    observations: Sequence[CaseObservation],
    baseline: Baseline,
    case_count: int,
) -> dict[str, float | int]:
    """Turn the successful observations into the metric mapping thresholds read."""
    if case_count <= 0:
        raise ValueError("a fixed set needs at least one case")
    failed = case_count - len(observations)
    total_tokens = sum(observation.total_tokens for observation in observations)
    costs = [observation.est_cost_usd for observation in observations]
    if costs and all(cost is not None for cost in costs):
        est_cost: float = round(sum(float(cost) for cost in costs if cost is not None), 8)
    else:
        est_cost = round(total_tokens * baseline.usd_per_million_input_tokens / 1_000_000, 8)

    uncapped_complete = all(
        observation.uncapped_total_tokens is not None and observation.uncapped_total_tokens > 0
        for observation in observations
    )
    uncapped_tokens = sum(
        observation.uncapped_total_tokens
        if observation.uncapped_total_tokens is not None
        else observation.total_tokens
        for observation in observations
    )
    baseline_tokens = baseline.tokens_for(case_count)
    baseline_cost = baseline.cost_for(case_count)
    respected = sum(
        1 for observation in observations if observation.total_tokens <= observation.budget
    )
    reviews = sum(1 for observation in observations if observation.rating.strip().upper() == REVIEW)

    return {
        "cases": case_count,
        "cases_failed": failed,
        "total_tokens": total_tokens,
        "uncapped_tokens": uncapped_tokens,
        "baseline_tokens": baseline_tokens,
        "total_tokens_ratio": _ratio(total_tokens, baseline_tokens),
        "capped_tokens_ratio": (
            _ratio(total_tokens, uncapped_tokens)
            if uncapped_complete and uncapped_tokens
            else 1.0
        ),
        "est_cost_usd": est_cost,
        "baseline_cost_usd": baseline_cost,
        "est_cost_ratio": _ratio(est_cost, baseline_cost),
        "budget_respected_rate": round(respected / case_count, 6),
        "review_rate": round(reviews / case_count, 6),
        "wall_clock_s": round(sum(observation.wall_clock_s for observation in observations), 3),
    }


def _ratio(value: float | int, reference: float | int) -> float:
    if reference <= 0:
        raise ValueError("the baseline must be positive")
    return round(float(value) / float(reference), 6)


def metric_names() -> Mapping[str, str]:
    """A one-line description per metric, for the threshold file and the report."""
    return {
        "cases": "cases in the fixed set",
        "cases_failed": "cases whose analysis raised",
        "total_tokens": "whole-request tokens recorded by the run ledger",
        "uncapped_tokens": "whole-request tokens with the run and call caps lifted",
        "baseline_tokens": "recorded baseline tokens for the set",
        "total_tokens_ratio": "total_tokens / baseline_tokens",
        "capped_tokens_ratio": "total_tokens / uncapped_tokens; 1.0 means the cap did not bind",
        "est_cost_usd": "total_tokens priced at the baseline's reference price",
        "baseline_cost_usd": "recorded baseline cost for the set",
        "est_cost_ratio": "est_cost_usd / baseline_cost_usd",
        "budget_respected_rate": "share of cases within their token budget",
        "review_rate": "share of cases whose rating is REVIEW",
        "wall_clock_s": "summed analysis wall-clock",
    }
