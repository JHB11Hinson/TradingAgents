"""Verifies D1-REQ-EVAL-001: thresholds are explicit, single-bounded and complete.

A typo in a metric name must fail the run instead of silently disabling a check,
and a metric that needs both "at most" and "at least" is really two metrics.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from tradingagents.evaluation import (
    Threshold,
    ThresholdError,
    check_thresholds,
    load_thresholds,
)

REPO = Path(__file__).resolve().parents[2]
SHIPPED = REPO / "eval" / "thresholds.yaml"


def _write(tmp_path: Path, metrics: object) -> Path:
    target = tmp_path / "thresholds.yaml"
    target.write_text(yaml.safe_dump({"metrics": metrics}), encoding="utf-8")
    return target


@pytest.mark.unit
def test_the_shipped_thresholds_load_and_each_is_a_single_bound():
    thresholds = load_thresholds(SHIPPED)

    assert thresholds
    assert {threshold.metric for threshold in thresholds} >= {
        "total_tokens_ratio",
        "est_cost_ratio",
        "budget_respected_rate",
        "review_rate",
    }
    for threshold in thresholds:
        assert (threshold.minimum is None) != (threshold.maximum is None)


@pytest.mark.unit
def test_an_unknown_metric_is_rejected(tmp_path):
    with pytest.raises(ThresholdError, match="unknown metric"):
        load_thresholds(_write(tmp_path, {"total_tokens_ration": {"max": 0.5}}))


@pytest.mark.unit
def test_a_threshold_with_both_bounds_is_rejected(tmp_path):
    with pytest.raises(ThresholdError, match="exactly one"):
        load_thresholds(_write(tmp_path, {"review_rate": {"min": 0.0, "max": 0.1}}))


@pytest.mark.unit
def test_a_threshold_without_a_bound_is_rejected(tmp_path):
    with pytest.raises(ThresholdError, match="exactly one"):
        load_thresholds(_write(tmp_path, {"review_rate": {}}))


@pytest.mark.unit
def test_a_non_numeric_bound_is_rejected(tmp_path):
    with pytest.raises(ThresholdError, match="must be a number"):
        load_thresholds(_write(tmp_path, {"review_rate": {"max": "low"}}))


@pytest.mark.unit
def test_a_truthy_boolean_is_not_a_number(tmp_path):
    with pytest.raises(ThresholdError, match="must be a number"):
        load_thresholds(_write(tmp_path, {"review_rate": {"max": True}}))


@pytest.mark.unit
def test_a_missing_metrics_mapping_is_rejected(tmp_path):
    target = tmp_path / "thresholds.yaml"
    target.write_text(yaml.safe_dump({"limits": {}}), encoding="utf-8")

    with pytest.raises(ThresholdError, match="metrics"):
        load_thresholds(target)


@pytest.mark.unit
def test_a_metric_inside_its_bound_passes_and_a_violation_fails():
    thresholds = (
        Threshold("total_tokens_ratio", maximum=0.5),
        Threshold("budget_respected_rate", minimum=1.0),
    )

    passed = check_thresholds(thresholds, {"total_tokens_ratio": 0.4, "budget_respected_rate": 1.0})
    failed = check_thresholds(thresholds, {"total_tokens_ratio": 0.9, "budget_respected_rate": 1.0})

    assert [outcome.ok for outcome in passed] == [True, True]
    assert [outcome.ok for outcome in failed] == [False, True]
    assert "FAIL" in failed[0].describe()


@pytest.mark.unit
def test_a_metric_the_report_did_not_produce_is_an_error():
    with pytest.raises(ThresholdError, match="no value"):
        check_thresholds((Threshold("review_rate", maximum=0.0),), {"cases": 1})
