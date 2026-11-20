"""Verifies D1-REQ-COST-001: the baseline carries its number and its provenance.

A baseline without a source is an unfalsifiable claim, and a negative or
zero value would make the ratio meaningless, so both are rejected.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tradingagents.evaluation import BaselineError, load_baseline

REPO = Path(__file__).resolve().parents[2]
SHIPPED = REPO / "eval" / "baseline.json"


def _write(tmp_path: Path, payload: object) -> Path:
    target = tmp_path / "baseline.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def _valid() -> dict:
    return {
        "version": 1,
        "recorded_at": "2026-11-20",
        "source": "unit test",
        "per_analysis": {"total_tokens": 1000, "est_cost_usd": 0.01},
        "usd_per_million_input_tokens": 2.5,
    }


@pytest.mark.unit
def test_the_shipped_baseline_loads_and_names_its_source():
    baseline = load_baseline(SHIPPED)

    assert baseline.total_tokens > 0
    assert baseline.est_cost_usd > 0
    assert baseline.source
    assert baseline.recorded_at


@pytest.mark.unit
def test_the_shipped_baseline_carries_the_registry_recorded_number():
    baseline = load_baseline(SHIPPED)

    assert baseline.total_tokens == 120_000


@pytest.mark.unit
def test_a_baseline_without_a_source_is_rejected(tmp_path):
    payload = _valid()
    payload.pop("source")

    with pytest.raises(BaselineError, match="source"):
        load_baseline(_write(tmp_path, payload))


@pytest.mark.unit
def test_a_zero_or_negative_number_is_rejected(tmp_path):
    payload = _valid()
    payload["per_analysis"]["total_tokens"] = 0

    with pytest.raises(BaselineError, match="positive integer"):
        load_baseline(_write(tmp_path, payload))


@pytest.mark.unit
def test_an_unknown_version_is_rejected(tmp_path):
    payload = _valid()
    payload["version"] = 2

    with pytest.raises(BaselineError, match="version"):
        load_baseline(_write(tmp_path, payload))


@pytest.mark.unit
def test_a_missing_file_is_rejected(tmp_path):
    with pytest.raises(BaselineError, match="cannot read"):
        load_baseline(tmp_path / "missing.json")
