"""Verifies D1-REQ-EVAL-001: the shipped fixed set is valid and the loader is strict.

A fixed set that silently shrinks (a typo, a dropped case, a future date) makes
every threshold easier to pass, so the loader rejects anything it cannot honour.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from tradingagents.evaluation import FixedSetError, load_fixed_set

REPO = Path(__file__).resolve().parents[2]
SHIPPED = REPO / "eval" / "fixed-set.json"


def _write(tmp_path: Path, payload: object) -> Path:
    target = tmp_path / "set.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


@pytest.mark.unit
def test_the_shipped_fixed_set_loads_and_every_case_is_well_formed():
    cases = load_fixed_set(SHIPPED)

    assert len(cases) >= 2
    assert len({case.id for case in cases}) == len(cases)
    for case in cases:
        assert case.ticker
        assert case.analysts
        assert case.trade_date < date.today().isoformat()


@pytest.mark.unit
def test_a_case_without_analysts_runs_the_default_four(tmp_path):
    cases = load_fixed_set(_write(tmp_path, {
        "version": 1,
        "cases": [{"id": "a", "ticker": "NVDA", "trade_date": "2026-01-09"}],
    }))

    assert cases[0].analysts == ("market", "social", "news", "fundamentals")


@pytest.mark.unit
def test_an_empty_case_list_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="non-empty"):
        load_fixed_set(_write(tmp_path, {"version": 1, "cases": []}))


@pytest.mark.unit
def test_an_unknown_case_key_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="unknown key"):
        load_fixed_set(_write(tmp_path, {
            "version": 1,
            "cases": [{"id": "a", "ticker": "NVDA", "trade_date": "2026-01-09", "tiker": "x"}],
        }))


@pytest.mark.unit
def test_a_duplicate_case_id_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="duplicate case id"):
        load_fixed_set(_write(tmp_path, {
            "version": 1,
            "cases": [
                {"id": "same", "ticker": "NVDA", "trade_date": "2026-01-09"},
                {"id": "same", "ticker": "BABA", "trade_date": "2026-01-09"},
            ],
        }))


@pytest.mark.unit
def test_a_future_trade_date_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="future"):
        load_fixed_set(
            _write(tmp_path, {
                "version": 1,
                "cases": [{"id": "a", "ticker": "NVDA", "trade_date": "2026-12-31"}],
            }),
            today=date(2026, 1, 1),
        )


@pytest.mark.unit
def test_a_bad_date_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="YYYY-MM-DD"):
        load_fixed_set(_write(tmp_path, {
            "version": 1,
            "cases": [{"id": "a", "ticker": "NVDA", "trade_date": "09/01/2026"}],
        }))


@pytest.mark.unit
def test_an_unknown_analyst_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="unknown analyst"):
        load_fixed_set(_write(tmp_path, {
            "version": 1,
            "cases": [{"id": "a", "ticker": "NVDA", "trade_date": "2026-01-09",
                       "analysts": ["market", "astrology"]}],
        }))


@pytest.mark.unit
def test_an_unknown_version_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="version"):
        load_fixed_set(_write(tmp_path, {"version": 99, "cases": []}))


@pytest.mark.unit
def test_a_missing_file_is_rejected(tmp_path):
    with pytest.raises(FixedSetError, match="cannot read"):
        load_fixed_set(tmp_path / "missing.json")
