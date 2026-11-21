"""Verifies D1-REQ-COST-001 and D1-REQ-EVAL-001: aggregation and the verdict.

The ratios are what COST-001 is judged on, so they are pinned against a
hand-computed baseline. A broken case is evidence rather than a crash: it is
counted in ``cases_failed`` so the run can never pass with a case missing.
"""

from __future__ import annotations

import json

import pytest

from tradingagents.evaluation import (
    Baseline,
    CaseObservation,
    EvaluationCase,
    Threshold,
    aggregate,
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


def _case(case_id: str) -> EvaluationCase:
    return EvaluationCase(id=case_id, ticker="NVDA", trade_date="2026-01-09")


def _thresholds() -> tuple[Threshold, ...]:
    return (
        Threshold("total_tokens_ratio", maximum=0.5),
        Threshold("est_cost_ratio", maximum=0.5),
        Threshold("budget_respected_rate", minimum=1.0),
        Threshold("review_rate", maximum=0.0),
        Threshold("cases_failed", maximum=0),
    )


@pytest.mark.unit
def test_aggregate_reports_tokens_cost_and_ratios_against_the_baseline():
    observations = [
        CaseObservation(total_tokens=400, budget=500, rating="Buy"),
        CaseObservation(total_tokens=600, budget=1000, rating="Overweight"),
    ]

    metrics = aggregate(observations, _baseline(), 2)

    assert metrics["total_tokens"] == 1000
    assert metrics["baseline_tokens"] == 2000
    assert metrics["total_tokens_ratio"] == 0.5
    assert metrics["est_cost_usd"] == pytest.approx(0.0025)
    assert metrics["baseline_cost_usd"] == pytest.approx(0.005)
    assert metrics["est_cost_ratio"] == pytest.approx(0.5)
    assert metrics["budget_respected_rate"] == 1.0
    assert metrics["review_rate"] == 0.0


@pytest.mark.unit
def test_aggregate_reports_the_same_condition_ratio():
    observations = [
        CaseObservation(total_tokens=900, budget=1000, rating="Hold", uncapped_total_tokens=1000),
        CaseObservation(total_tokens=1000, budget=1000, rating="Hold", uncapped_total_tokens=1000),
    ]

    metrics = aggregate(observations, _baseline(), 2)

    assert metrics["uncapped_tokens"] == 2000
    assert metrics["capped_tokens_ratio"] == 0.95


@pytest.mark.unit
def test_a_missing_uncapped_measurement_reports_one():
    observations = [CaseObservation(total_tokens=100, budget=1000, rating="Hold")]

    metrics = aggregate(observations, _baseline(), 1)

    assert metrics["capped_tokens_ratio"] == 1.0


@pytest.mark.unit
@pytest.mark.parametrize("missing", [None, 0])
def test_one_missing_uncapped_measurement_forces_the_whole_ratio_to_one(missing):
    observations = [
        CaseObservation(total_tokens=100, budget=1000, rating="Hold", uncapped_total_tokens=1000),
        CaseObservation(
            total_tokens=1, budget=1000, rating="Hold", uncapped_total_tokens=missing
        ),
    ]

    metrics = aggregate(observations, _baseline(), 2)

    assert metrics["capped_tokens_ratio"] == 1.0


@pytest.mark.unit
def test_review_and_budget_breaches_are_counted():
    observations = [
        CaseObservation(total_tokens=600, budget=500, rating="REVIEW"),
        CaseObservation(total_tokens=100, budget=500, rating="Hold"),
    ]

    metrics = aggregate(observations, _baseline(), 2)

    assert metrics["review_rate"] == 0.5
    assert metrics["budget_respected_rate"] == 0.5


@pytest.mark.unit
def test_a_failed_case_is_counted_and_never_passes_the_run():
    def analyze(case: EvaluationCase) -> CaseObservation:
        if case.id == "broken":
            raise RuntimeError("provider unavailable")
        return CaseObservation(total_tokens=100, budget=1000, rating="Hold")

    report = evaluate_cases(
        [_case("ok"), _case("broken")], analyze, _baseline(), _thresholds()
    )

    assert report.metrics["cases_failed"] == 1
    assert report.metrics["total_tokens"] == 100
    assert report.ok is False
    assert [case.ok for case in report.cases] == [True, False]
    assert "provider unavailable" in (report.cases[1].error or "")
    assert "FAILED" in report.summary()


@pytest.mark.unit
def test_the_report_is_ok_only_when_every_threshold_passes():
    def analyze(case: EvaluationCase) -> CaseObservation:
        return CaseObservation(total_tokens=100, budget=1000, rating="Hold")

    report = evaluate_cases([_case("ok")], analyze, _baseline(), _thresholds())

    assert report.ok is True
    assert report.failed_thresholds() == ()


@pytest.mark.unit
def test_a_threshold_violation_makes_the_report_not_ok():
    def analyze(case: EvaluationCase) -> CaseObservation:
        return CaseObservation(total_tokens=900, budget=1000, rating="REVIEW")

    report = evaluate_cases([_case("hot")], analyze, _baseline(), _thresholds())

    assert report.ok is False
    assert {outcome.metric for outcome in report.failed_thresholds()} == {
        "total_tokens_ratio",
        "est_cost_ratio",
        "review_rate",
    }


@pytest.mark.unit
def test_the_report_json_round_trips(tmp_path):
    def analyze(case: EvaluationCase) -> CaseObservation:
        return CaseObservation(total_tokens=100, budget=1000, rating="Hold")

    report = evaluate_cases(
        [_case("ok")], analyze, _baseline(), _thresholds(),
        set_path="eval/fixed-set.json", thresholds_path="eval/thresholds.yaml",
    )
    target = report.write(tmp_path / "report.json")
    payload = json.loads(target.read_text(encoding="utf-8"))

    assert payload["ok"] is True
    assert payload["set"] == "eval/fixed-set.json"
    assert payload["metrics"]["total_tokens"] == 100
    assert payload["cases"][0]["case"] == "ok"
    assert payload["baseline"]["total_tokens_per_analysis"] == 1000


@pytest.mark.unit
def test_an_empty_set_is_refused_by_the_aggregator():
    with pytest.raises(ValueError, match="at least one case"):
        aggregate([], _baseline(), 0)


@pytest.mark.unit
def test_structured_output_pass_rate_is_the_share_of_successful_cases():
    """D1-REQ-QUAL-001: only a schema-validated final decision counts as a pass."""
    observations = [
        CaseObservation(total_tokens=100, budget=1000, rating="Buy"),
        CaseObservation(total_tokens=100, budget=1000, rating="Hold"),
        CaseObservation(total_tokens=100, budget=1000, rating="Hold", structured_output_ok=False),
    ]

    metrics = aggregate(observations, _baseline(), 3)

    assert metrics["structured_output_pass_rate"] == pytest.approx(0.666667)


@pytest.mark.unit
def test_the_report_carries_the_structured_flag_per_case():
    """D1-REQ-QUAL-001: the per-case evidence survives into the JSON report."""
    def analyze(case: EvaluationCase) -> CaseObservation:
        return CaseObservation(
            total_tokens=100,
            budget=1000,
            rating="Hold",
            structured_output_ok=case.id == "structured",
        )

    report = evaluate_cases(
        [_case("structured"), _case("free_text")],
        analyze,
        _baseline(),
        _thresholds(),
    )

    flags = {case.case_id: case.structured_output_ok for case in report.cases}
    assert flags == {"structured": True, "free_text": False}
    assert report.to_dict()["cases"][0]["structured_output_ok"] in {True, False}
