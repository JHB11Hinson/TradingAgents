"""Verifies DEBT-011: the evaluation compares capped and uncapped runs.

The headline ``total_tokens_ratio`` is measured against the inherited 120,000
baseline. That comparison is not like-for-like on a synthetic replay, so the
run also reports ``capped_tokens_ratio``: the same fixtures, with and without
the run/call cap. A ratio of 1.0 means the cap did not bind.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from eval import run as eval_run
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


def _fake_analyzer(calls: list[tuple[Path, dict]] | None = None):
    def build(results_dir, overrides=None):
        if calls is not None:
            calls.append((Path(results_dir), dict(overrides or {})))
        total = 110 if Path(results_dir).name == "uncapped" else 100
        return lambda case: CaseObservation(
            total_tokens=total,
            budget=1000,
            rating="Hold",
        )

    return build


@pytest.mark.unit
def test_the_two_passes_use_isolated_directories(tmp_path, monkeypatch):
    calls: list[tuple[Path, dict]] = []
    monkeypatch.setattr("eval.replay.build_replay_analyzer", _fake_analyzer(calls))

    rc = eval_run.main(
        ["--results-dir", str(tmp_path), "--out", str(tmp_path / "report.json")]
    )

    assert rc == 0
    assert calls[0][0] == tmp_path / "capped"
    assert calls[1][0] == tmp_path / "uncapped"
    assert calls[0][0] != calls[1][0]
    assert calls[1][1]["context_budget_tokens"] == 10**9
    assert calls[1][1]["context_call_budget_tokens"] == 10**9
    assert calls[1][1]["context_decision_reserve_tokens"] == 0


@pytest.mark.unit
def test_an_uncapped_failure_is_a_failed_case_not_a_pass(tmp_path, monkeypatch):
    def build(results_dir, overrides=None):
        if Path(results_dir).name == "uncapped":
            def boom(case):
                raise RuntimeError("uncapped replay refused")

            return boom
        return lambda case: CaseObservation(
            total_tokens=100, budget=1000, rating="Hold"
        )

    monkeypatch.setattr("eval.replay.build_replay_analyzer", build)
    out = tmp_path / "report.json"

    rc = eval_run.main(["--results-dir", str(tmp_path), "--out", str(out)])

    assert rc == 1
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["metrics"]["cases_failed"] == 2
    assert report["ok"] is False
