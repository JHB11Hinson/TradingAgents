"""Unit tests for the layered context assembler (D1-REQ-CTX-001/002/003).

The assembler owns the six-layer contract, the deterministic token estimate,
the run/call budget, priority compaction and P0 re-injection. These tests are
the fit criteria for INV-02 and INV-03; each negative test names the check it
removes.
"""

from __future__ import annotations

import hashlib

import pytest
import tradingagents.context.assembler as assembler
from tradingagents.context import (
    ContextBlock,
    ContextBudgetExceeded,
    ContextIncomplete,
    Layer,
    RunBudget,
    assemble_context,
    current_budget,
    estimate_tokens,
    make_layers,
    run_budget_scope,
)

P0 = frozenset({Layer.IDENTITY, Layer.CONSTRAINTS, Layer.TASK})


def block(layer: Layer, source: str, text: str, *, render: bool = True) -> ContextBlock:
    return ContextBlock(layer=layer, source=source, text=text, render=render)


def layers(**overrides):
    """A complete six-layer request; tests override one layer at a time."""
    base = {
        "identity": [block(Layer.IDENTITY, "state.instrument_context", "Instrument: NVDA")],
        "constraints": [
            block(Layer.CONSTRAINTS, "role", "Standing constraints: never trade after the date.")
        ],
        "retrieved": [block(Layer.RETRIEVED, "state.market_report", "Market report: RSI 61.")],
        "history": [block(Layer.HISTORY, "state.messages", "Earlier: hold.")],
        "resumable": [block(Layer.RESUMABLE, "state.run_pointers", "Run state: checkpoint.")],
        "task": [block(Layer.TASK, "task", "Write the report now.")],
    }
    base.update(overrides)
    return make_layers(**base)


@pytest.mark.unit
def test_assembler_emits_all_six_layers_in_order_with_sources():
    result = assemble_context(layers(), budget=RunBudget(10_000))

    assert result.layers == (
        Layer.IDENTITY,
        Layer.CONSTRAINTS,
        Layer.RETRIEVED,
        Layer.HISTORY,
        Layer.RESUMABLE,
        Layer.TASK,
    )
    assert set(result.sources) == set(result.layers)
    assert result.sources[Layer.RETRIEVED] == ("state.market_report",)
    assert all(result.sources[layer] for layer in result.layers)


@pytest.mark.unit
def test_missing_layer_is_rejected_before_rendering():
    incomplete = layers(history=[])

    with pytest.raises(ContextIncomplete, match="history"):
        assemble_context(incomplete, budget=RunBudget(10_000))


@pytest.mark.unit
def test_dedupe_keeps_one_copy_of_repeated_evidence():
    duplicate = "Same market evidence."
    request = layers(
        retrieved=[
            block(Layer.RETRIEVED, "state.market_report", duplicate),
            block(Layer.RETRIEVED, "state.news_report", duplicate),
        ]
    )

    result = assemble_context(request, budget=RunBudget(10_000))

    assert result.text.count(duplicate) == 1
    assert [drop.source for drop in result.dropped] == ["state.news_report"]


@pytest.mark.unit
def test_pipeline_records_each_stage_in_order():
    result = assemble_context(layers(), budget=RunBudget(10_000))

    assert result.stages == ("dedupe", "prioritize", "budget", "compact", "assemble")


@pytest.mark.unit
def test_under_budget_returns_the_agent_prompt_unchanged():
    original = "Legacy prompt built by the agent."
    result = assemble_context(layers(), original=original, budget=RunBudget(10_000))

    assert result.text == original
    assert result.compacted is False
    assert result.tokens == estimate_tokens(original)


@pytest.mark.unit
def test_over_budget_compacts_and_stays_within_the_cap():
    big = "x" * 4000  # 1000 estimated tokens
    request = layers(
        retrieved=[block(Layer.RETRIEVED, "state.market_report", big)],
        history=[block(Layer.HISTORY, "state.messages", big)],
        resumable=[block(Layer.RESUMABLE, "state.run_pointers", big)],
    )

    result = assemble_context(request, budget=RunBudget(500))

    assert result.compacted is True
    assert result.tokens <= 500
    assert result.tokens <= result.budget


@pytest.mark.unit
def test_p0_constraints_are_byte_identical_after_compaction():
    request = layers(
        constraints=[block(Layer.CONSTRAINTS, "role", "NEVER DROP THIS CONSTRAINT")],
        retrieved=[block(Layer.RETRIEVED, "state.market_report", "r" * 4000)],
        history=[block(Layer.HISTORY, "state.messages", "h" * 4000)],
        resumable=[block(Layer.RESUMABLE, "state.run_pointers", "p" * 4000)],
    )

    result = assemble_context(request, budget=RunBudget(500))

    assert result.p0_digest_before == result.p0_digest
    assert result.text.count("NEVER DROP THIS CONSTRAINT") == 1
    assert result.re_injected is True


@pytest.mark.unit
def test_compaction_never_drops_p0():
    request = layers(
        retrieved=[block(Layer.RETRIEVED, "state.market_report", "r" * 4000)],
        history=[block(Layer.HISTORY, "state.messages", "h" * 4000)],
        resumable=[block(Layer.RESUMABLE, "state.run_pointers", "p" * 4000)],
    )

    result = assemble_context(request, budget=RunBudget(500))

    assert not any(drop.layer in P0 for drop in result.dropped)


@pytest.mark.unit
def test_history_is_compacted_to_its_ceiling_before_retrieved_knowledge():
    request = layers(
        retrieved=[block(Layer.RETRIEVED, "state.market_report", "r" * 1600)],  # 400 tokens
        history=[block(Layer.HISTORY, "state.messages", "h" * 1600)],  # 400 tokens
    )

    result = assemble_context(request, budget=RunBudget(800))

    assert result.compacted is True
    assert result.layer_tokens[Layer.HISTORY] <= 240  # 30% of 800
    assert result.layer_tokens[Layer.RETRIEVED] <= 360  # 45% of 800


@pytest.mark.unit
def test_retrieved_knowledge_is_trimmed_only_after_history_is_within_its_ceiling():
    request = layers(
        retrieved=[block(Layer.RETRIEVED, "state.market_report", "r" * 2400)],  # 600 tokens
        history=[block(Layer.HISTORY, "state.messages", "h" * 400)],  # 100 tokens
    )

    result = assemble_context(request, budget=RunBudget(800))

    assert result.layer_tokens[Layer.HISTORY] <= 100
    assert result.layer_tokens[Layer.RETRIEVED] <= 360


@pytest.mark.unit
def test_removing_the_budget_check_would_let_the_context_exceed_the_cap(monkeypatch):
    """Negative test: the ceiling is enforced by _within_budget, not by luck."""
    monkeypatch.setattr(assembler, "_within_budget", lambda *args, **kwargs: True)
    request = layers(retrieved=[block(Layer.RETRIEVED, "state.market_report", "r" * 4000)])

    result = assemble_context(request, budget=RunBudget(100))

    assert result.tokens > result.budget


@pytest.mark.unit
def test_p0_over_budget_aborts_before_a_model_call():
    request = layers(constraints=[block(Layer.CONSTRAINTS, "role", "c" * 4000)])

    with pytest.raises(ContextBudgetExceeded):
        assemble_context(request, budget=RunBudget(100))


@pytest.mark.unit
@pytest.mark.parametrize(
    "text,expected",
    [("", 0), ("a", 1), ("abcd", 1), ("abcde", 2), ("a" * 400, 100)],
)
def test_estimator_is_deterministic_characters_over_four(text, expected):
    assert estimate_tokens(text) == expected
    assert estimate_tokens(text) == estimate_tokens(text)


@pytest.mark.unit
def test_run_budget_never_spends_more_than_the_cap():
    with run_budget_scope(
        {"context_budget_tokens": 1000, "context_call_budget_tokens": 1000}
    ) as budget:
        first = assemble_context(layers(), original="a" * 1600, budget=budget)
        second = assemble_context(layers(), original="b" * 1600, budget=budget)

        assert budget.spent == first.tokens + second.tokens
        assert budget.spent <= 1000
        assert budget.snapshot()["total_tokens"] == budget.spent


@pytest.mark.unit
def test_exhausted_run_budget_aborts_before_another_call():
    large_p0 = layers(constraints=[block(Layer.CONSTRAINTS, "role", "c" * 300)])
    with run_budget_scope(
        {"context_budget_tokens": 100, "context_call_budget_tokens": 100}
    ) as budget:
        assemble_context(large_p0, original="a" * 400, budget=budget)

        with pytest.raises(ContextBudgetExceeded):
            assemble_context(large_p0, original="b" * 400, budget=budget)

        assert budget.spent <= 100


@pytest.mark.unit
def test_run_budget_scope_resets_after_the_run():
    assert current_budget() is None
    with run_budget_scope({"context_budget_tokens": 1000}):
        assert current_budget() is not None
    assert current_budget() is None


@pytest.mark.unit
def test_p0_digest_is_a_sha256_of_the_p0_block_text():
    result = assemble_context(layers(), budget=RunBudget(10_000))

    joined = "\n\n".join(
        [
            "Instrument: NVDA",
            "Standing constraints: never trade after the date.",
            "Write the report now.",
        ]
    )
    assert result.p0_digest == hashlib.sha256(joined.encode("utf-8")).hexdigest()
