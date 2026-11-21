"""Verifies DEBT-011: the evaluation compares capped and uncapped runs.

The headline ``total_tokens_ratio`` is measured against the inherited 120,000
baseline. That comparison is not like-for-like on a synthetic replay, so the
run also reports ``capped_tokens_ratio``: the same fixtures, with and without
the run/call cap. A ratio of 1.0 means the cap did not bind.
"""

from __future__ import annotations

import pytest
from tradingagents.evaluation import (
    Baseline,
    CaseObservation,
    EvaluationCase,
    EvaluationReport,
    Threshold,
    evaluate_cases,
)


def _baseline() -> Baseline:
    return Baseline(
        total_tokens=1000,
        est_cost_usd=0.0025,
        usd_per_million_input_tokens=2.5,
        source="unit-test baseline",
        recorded_at="2026-11-20",
    )


def _case(case_id: str = "NVDA") -> EvaluationCase:
    return EvaluationCase(id=case_id, ticker="NVDA", trade_date="2026-01-09")


def _report(uncapped: int) -> EvaluationReport:
    def analyze(case: EvaluationCase) -> CaseObservation:
        return CaseObservation(
            total_tokens=100,
            budget=1000,
            rating="Hold",
            uncapped_total_tokens=uncapped,
        )

    thresholds = (Threshold("capped_tokens_ratio", maximum=0.98),)
    return evaluate_cases([_case()], analyze, _baseline(), thresholds)


@pytest.mark.unit
def test_a_binding_cap_passes():
    assert _report(uncapped=110).ok is True


@pytest.mark.unit
def test_no_compaction_fails():
    report = _report(uncapped=100)

    assert report.ok is False
    assert report.failed_thresholds()[0].metric == "capped_tokens_ratio"
