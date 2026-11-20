"""Verifies D1-REQ-COST-003: the run ledger counts the whole request.

Before CHG-036 an uncompacted call recorded only the system-prompt estimate: the
history layer was budgeted but not counted, so the run log under-reported the
tokens the model received and a run could "fit" a cap it had already exceeded.
The ledger now records the whole request, and a slice of the run cap is withheld
from ordinary calls so the final decision still has room.
"""

from __future__ import annotations

import pytest
from tradingagents.context import (
    ContextBlock,
    ContextBudgetExceeded,
    Layer,
    RunBudget,
    assemble_context,
    estimate_tokens,
    make_layers,
    run_budget_scope,
)

HISTORY = "Earlier: hold. " * 10


def _block(layer: Layer, source: str, text: str, render: bool = True) -> ContextBlock:
    return ContextBlock(layer=layer, source=source, text=text, render=render)


def _layers() -> object:
    return make_layers(
        identity=[_block(Layer.IDENTITY, "state.instrument_context", "Instrument: NVDA")],
        constraints=[_block(Layer.CONSTRAINTS, "role", "Standing constraints.")],
        retrieved=[_block(Layer.RETRIEVED, "state.market_report", "Report evidence.")],
        history=[_block(Layer.HISTORY, "state.messages", HISTORY, render=False)],
        resumable=[_block(Layer.RESUMABLE, "state.run_pointers", "Run state: checkpoint.")],
        task=[_block(Layer.TASK, "task", "Write the report now.")],
    )


@pytest.mark.unit
def test_the_ledger_records_the_whole_request_including_non_rendered_layers():
    with run_budget_scope(
        {"context_budget_tokens": 10_000, "context_call_budget_tokens": 10_000}
    ) as budget:
        assembled = assemble_context(_layers(), original="a" * 400, budget=budget)

        assert budget.spent == assembled.request_tokens
        assert assembled.request_tokens == estimate_tokens("a" * 400) + estimate_tokens(HISTORY)
        assert assembled.request_tokens > assembled.tokens


@pytest.mark.unit
def test_a_compacted_call_records_the_whole_request_too():
    with run_budget_scope(
        {"context_budget_tokens": 400, "context_call_budget_tokens": 400}
    ) as budget:
        assembled = assemble_context(_layers(), original="a" * 4000, budget=budget)

        assert assembled.compacted is True
        assert budget.spent == assembled.request_tokens
        assert assembled.request_tokens <= 400


@pytest.mark.unit
def test_the_decision_reserve_is_withheld_from_ordinary_calls():
    budget = RunBudget(1000, reserve=300)

    assert budget.available() == 700
    assert budget.available(use_reserve=True) == 1000


@pytest.mark.unit
def test_a_reserve_larger_than_the_cap_is_clamped():
    budget = RunBudget(500, reserve=900)

    assert budget.reserve == 500
    assert budget.available() == 0
    assert budget.available(use_reserve=True) == 500


@pytest.mark.unit
def test_an_ordinary_call_cannot_spend_the_reserve():
    budget = RunBudget(1000, reserve=400)
    budget.record("Risk Analyst", 600, compacted=False)

    with pytest.raises(ContextBudgetExceeded):
        assemble_context(_layers(), original="x" * 100, budget=budget)

    assembled = assemble_context(_layers(), original="x" * 100, budget=budget, use_reserve=True)

    assert assembled.request_tokens <= 400
    assert budget.spent <= budget.cap


@pytest.mark.unit
def test_the_run_log_reports_the_reserve():
    with run_budget_scope(
        {
            "context_budget_tokens": 1000,
            "context_call_budget_tokens": 1000,
            "context_decision_reserve_tokens": 250,
        }
    ) as budget:
        snapshot = budget.snapshot()

    assert snapshot["reserve"] == 250
