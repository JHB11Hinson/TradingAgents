"""Memory-log lessons are point-in-time safe and source-attributable (#1251).

Verifies ``D1-REQ-MEM-003``: every retrieved memory item is source-attributable
and a historical run must not read outcomes unknown as of its analysis date.

get_past_context previously returned every resolved lesson regardless of the run
date, so a historical run could learn from an outcome that had not happened yet.
Resolved entries now record the date their outcome became known (``resolved:``),
and get_past_context(as_of=...) filters on it. Legacy entries without a
resolution date are excluded from a point-in-time query (conservative migration).

Every injected item also carries its ``source_id`` (``<trade_date>/<ticker>``),
derived from the tag line so legacy entries are attributed without a migration
(ADR-014).
"""
from __future__ import annotations

import pytest

from tradingagents.memory import TradingMemoryLog


def _log(tmp_path):
    return TradingMemoryLog({"memory_log_path": str(tmp_path / "mem.md")})


def _resolve(log, ticker, date, resolution_date, reflection):
    log.store_decision(ticker, date, f"Rating: Buy\n{reflection}")
    log.update_with_outcome(
        ticker, date, 0.05, 0.02, 5, reflection, resolution_date=resolution_date,
    )


@pytest.mark.unit
def test_resolution_date_is_stored_and_parsed(tmp_path):
    """D1-REQ-MEM-003: a resolved entry records the date its outcome became known."""
    log = _log(tmp_path)
    _resolve(log, "NVDA", "2026-01-05", "2026-01-10", "outcome known 01-10")
    entry = log.load_entries()[0]
    assert entry["resolved"] == "2026-01-10"
    assert "resolved:2026-01-10" in (tmp_path / "mem.md").read_text()


@pytest.mark.unit
def test_as_of_excludes_lessons_resolved_after_the_run_date(tmp_path):
    """D1-REQ-MEM-003: a backdated run excludes outcomes resolved after its date."""
    log = _log(tmp_path)
    # Decision on 01-05, outcome only known on 01-10.
    _resolve(log, "NVDA", "2026-01-05", "2026-01-10", "great trade")

    # A run as-of 01-07 must NOT see it (the outcome was still in the future).
    assert log.get_past_context("NVDA", as_of="2026-01-07") == ""
    # A run as-of 01-10 (and later) sees it.
    assert "great trade" in log.get_past_context("NVDA", as_of="2026-01-10")
    assert "great trade" in log.get_past_context("NVDA", as_of="2026-02-01")


@pytest.mark.unit
def test_no_as_of_is_unfiltered_live_behavior(tmp_path):
    log = _log(tmp_path)
    _resolve(log, "NVDA", "2026-01-05", "2026-01-10", "great trade")
    # Live run (no as_of): unchanged behavior, lesson is shown.
    assert "great trade" in log.get_past_context("NVDA")


@pytest.mark.unit
def test_legacy_entry_without_resolution_date_excluded_in_backtest(tmp_path):
    """D1-REQ-MEM-003: a legacy entry with no known-by date is withheld from a backtest."""
    log = _log(tmp_path)
    # Simulate a pre-migration resolved entry: no resolution_date recorded.
    log.store_decision("NVDA", "2026-01-05", "Rating: Buy\nlegacy lesson")
    log.update_with_outcome("NVDA", "2026-01-05", 0.05, 0.02, 5, "legacy lesson")
    entry = log.load_entries()[0]
    assert entry["resolved"] is None

    # Conservative: excluded from a point-in-time query (can't prove it was known)...
    assert log.get_past_context("NVDA", as_of="2026-06-01") == ""
    # ...but still available on a live (unfiltered) run.
    assert "legacy lesson" in log.get_past_context("NVDA")


@pytest.mark.unit
def test_cross_ticker_lessons_are_also_gated(tmp_path):
    """D1-REQ-MEM-003: cross-ticker lessons obey the same point-in-time cutoff."""
    log = _log(tmp_path)
    _resolve(log, "AAPL", "2026-01-05", "2026-01-10", "cross lesson")
    # Querying a different ticker as-of before resolution: no cross lesson leaks.
    assert log.get_past_context("NVDA", as_of="2026-01-07") == ""
    assert "cross lesson" in log.get_past_context("NVDA", as_of="2026-01-10")


@pytest.mark.unit
def test_memory_as_of_gates_historical_but_not_live():
    # The graph filters only for a past trade date; a current-date run passes
    # None so live behavior and legacy entries are unaffected (#1251).
    from datetime import datetime, timedelta

    from tradingagents.graph.trading_graph import TradingAgentsGraph

    g = object.__new__(TradingAgentsGraph)
    past = "2024-01-01"
    today = datetime.now().strftime("%Y-%m-%d")
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    assert g._memory_as_of(past) == past       # backtest -> filter on the trade date
    assert g._memory_as_of(today) is None      # live -> no filter
    assert g._memory_as_of(future) is None     # future-dated run -> no filter


# --- source attribution (D1-REQ-MEM-003) -----------------------------------------


@pytest.mark.unit
def test_every_injected_item_carries_its_source_id(tmp_path):
    """D1-REQ-MEM-003: each injected block is tagged with its ``src:<date>/<ticker>``."""
    log = _log(tmp_path)
    _resolve(log, "NVDA", "2026-01-05", "2026-01-10", "first NVDA lesson")
    _resolve(log, "NVDA", "2026-01-06", "2026-01-11", "second NVDA lesson")
    _resolve(log, "AAPL", "2026-01-07", "2026-01-12", "cross AAPL lesson")

    ctx = log.get_past_context("NVDA")

    for source_id in ("2026-01-05/NVDA", "2026-01-06/NVDA", "2026-01-07/AAPL"):
        assert f"src:{source_id}" in ctx
    # One source id per injected item: 2 same-ticker + 1 cross-ticker.
    assert ctx.count("src:") == 3


@pytest.mark.unit
def test_source_id_is_derived_from_the_tag_line(tmp_path):
    """D1-REQ-MEM-003: source_id is derived, so legacy logs need no migration."""
    log = _log(tmp_path)
    _resolve(log, "NVDA", "2026-01-05", "2026-01-10", "derived id")

    entry = log.load_entries()[0]
    assert entry["source_id"] == "2026-01-05/NVDA"
    # The id is computed on read; the on-disk tag line is unchanged.
    assert "src:" not in (tmp_path / "mem.md").read_text()


@pytest.mark.unit
def test_source_ids_are_unique_per_decision(tmp_path):
    """D1-REQ-MEM-003: two decisions get distinct source ids."""
    log = _log(tmp_path)
    _resolve(log, "NVDA", "2026-01-05", "2026-01-10", "a")
    _resolve(log, "NVDA", "2026-01-06", "2026-01-11", "b")

    ids = [e["source_id"] for e in log.load_entries()]
    assert ids == ["2026-01-05/NVDA", "2026-01-06/NVDA"]
    assert len(set(ids)) == len(ids)


@pytest.mark.unit
def test_without_the_source_id_seam_attribution_is_lost(tmp_path, monkeypatch):
    """Negative test: the attribution comes from ``_source_id``, not from luck.

    Removing the seam (a helper that returns the entry's id) must make the
    positive invariant fail, proving the test exercises the attribution code.
    """
    import tradingagents.memory.log as memory_log

    monkeypatch.setattr(memory_log.TradingMemoryLog, "_source_id",
                        staticmethod(lambda e: ""))
    log = _log(tmp_path)
    _resolve(log, "NVDA", "2026-01-05", "2026-01-10", "no id")

    ctx = log.get_past_context("NVDA")
    assert "src:2026-01-05/NVDA" not in ctx
