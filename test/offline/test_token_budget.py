"""Token-budget tests named by the COST-003 fit criterion.

The budget has two levels: `context_budget_tokens` caps a whole run, and
`context_call_budget_tokens` caps one assembled call. Both default to 50000.
An over-budget context is compacted before the provider is called; the run log
records what was spent so the cap is auditable.
"""

from __future__ import annotations

import json

import pytest
from langchain_core.messages import AIMessage
from tradingagents.context import (
    ContextBlock,
    Layer,
    RunBudget,
    assemble_context,
    make_layers,
    run_budget_scope,
)

import tradingagents.default_config as default_config


def _block(layer: Layer, source: str, text: str) -> ContextBlock:
    return ContextBlock(layer=layer, source=source, text=text)


def _layers(text: str = "evidence") -> object:
    return make_layers(
        identity=[_block(Layer.IDENTITY, "state.instrument_context", "Instrument: NVDA")],
        constraints=[_block(Layer.CONSTRAINTS, "role", "Standing constraints.")],
        retrieved=[_block(Layer.RETRIEVED, "state.market_report", text)],
        history=[_block(Layer.HISTORY, "state.messages", "Earlier: hold.")],
        resumable=[_block(Layer.RESUMABLE, "state.run_pointers", "Run state: checkpoint.")],
        task=[_block(Layer.TASK, "task", "Write the report now.")],
    )


def _without_env(monkeypatch):
    for key in list(default_config._ENV_OVERRIDES):
        monkeypatch.delenv(key, raising=False)
    return default_config.build_default_config()


@pytest.mark.unit
def test_default_run_and_call_budgets_are_50000(monkeypatch):
    config = _without_env(monkeypatch)

    assert config["context_budget_tokens"] == 50_000
    assert config["context_call_budget_tokens"] == 50_000
    assert config["context_compaction_threshold"] == 0.8


@pytest.mark.unit
def test_budget_env_overrides_are_read(monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_CONTEXT_BUDGET_TOKENS", "1234")
    monkeypatch.setenv("TRADINGAGENTS_CONTEXT_CALL_BUDGET_TOKENS", "4321")
    monkeypatch.setenv("TRADINGAGENTS_CONTEXT_COMPACTION_THRESHOLD", "0.5")

    config = default_config.build_default_config()

    assert config["context_budget_tokens"] == 1234
    assert config["context_call_budget_tokens"] == 4321
    assert config["context_compaction_threshold"] == 0.5


@pytest.mark.unit
def test_invalid_budget_env_value_fails_loudly(monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_CONTEXT_BUDGET_TOKENS", "not-a-number")

    with pytest.raises(ValueError, match="TRADINGAGENTS_CONTEXT_BUDGET_TOKENS"):
        default_config.build_default_config()


@pytest.mark.unit
def test_over_budget_context_compacts_and_stays_under_the_cap():
    result = assemble_context(_layers("x" * 4000), budget=RunBudget(500))

    assert result.compacted is True
    assert result.tokens <= 500


@pytest.mark.unit
def test_a_run_never_spends_more_than_the_configured_budget():
    with run_budget_scope(
        {"context_budget_tokens": 1000, "context_call_budget_tokens": 1000}
    ) as budget:
        assemble_context(_layers(), original="a" * 1600, budget=budget)
        assemble_context(_layers(), original="b" * 1600, budget=budget)

        snapshot = budget.snapshot()

    assert snapshot["budget"] == 1000
    assert snapshot["total_tokens"] <= 1000
    assert snapshot["total_tokens"] == budget.spent
    assert len(snapshot["calls"]) == 2


def _state(ticker="NVDA"):
    return {
        "company_of_interest": ticker,
        "trade_date": "2026-09-01",
        "market_report": "M",
        "sentiment_report": "S",
        "news_report": "N",
        "fundamentals_report": "F",
        "investment_plan": "P",
        "trader_investment_plan": "T",
        "final_trade_decision": "Rating: Hold",
        "final_rating": "Hold",
        "investment_debate_state": {
            "bull_history": "",
            "bear_history": "",
            "history": "",
            "current_response": "",
            "count": 0,
        },
        "risk_debate_state": {
            "aggressive_history": "",
            "conservative_history": "",
            "neutral_history": "",
            "history": "",
            "latest_speaker": "",
            "current_aggressive_response": "",
            "current_conservative_response": "",
            "current_neutral_response": "",
            "count": 0,
        },
    }


def _bare_graph(tmp_path):
    from tradingagents.graph.trading_graph import TradingAgentsGraph

    graph = object.__new__(TradingAgentsGraph)
    graph.config = {
        "results_dir": str(tmp_path),
        "llm_provider": "openai",
        "deep_think_llm": "d",
        "quick_think_llm": "q",
        "max_debate_rounds": 1,
        "max_risk_discuss_rounds": 1,
        "output_language": "English",
        "data_vendors": {},
        "tool_vendors": {},
    }
    graph.selected_analysts = ("market",)
    graph._context_usage = {}
    return graph


@pytest.mark.unit
def test_the_graph_snapshots_the_run_budget_for_the_state_log(tmp_path):
    graph = _bare_graph(tmp_path)
    with run_budget_scope(
        {"context_budget_tokens": 1000, "context_call_budget_tokens": 1000}
    ):
        assemble_context(_layers(), original="a" * 400)
        graph._record_context_usage()

    assert graph._context_usage["budget"] == 1000
    assert graph._context_usage["total_tokens"] <= 1000


@pytest.mark.unit
def test_the_run_log_reports_context_usage_within_the_budget(tmp_path):
    graph = _bare_graph(tmp_path)
    graph._context_usage = {
        "budget": 50_000,
        "call_budget": 50_000,
        "total_tokens": 1234,
        "max_call_tokens": 800,
        "calls": [{"agent": "Market Analyst", "tokens": 800}],
        "compacted_calls": 1,
    }

    graph._log_state("2026-09-01", _state())

    logged = json.loads(
        next(tmp_path.rglob("full_states_log*.json")).read_text(encoding="utf-8")
    )
    usage = logged["context_usage"]
    assert usage["total_tokens"] <= usage["budget"]
    assert usage["calls"][0]["agent"] == "Market Analyst"


class _FakeLLM:
    """No structured output, no provider call; records every invocation."""

    def __init__(self) -> None:
        self.calls = 0

    def with_structured_output(self, schema):
        raise NotImplementedError

    def invoke(self, prompt):
        self.calls += 1
        return AIMessage(content="Rating: Hold")


@pytest.mark.unit
def test_portfolio_manager_returns_review_without_a_model_call_when_p0_exceeds_the_budget():
    from tradingagents.agents.managers.portfolio_manager import create_portfolio_manager

    llm = _FakeLLM()
    node = create_portfolio_manager(llm)
    with run_budget_scope(
        {"context_budget_tokens": 1, "context_call_budget_tokens": 1}
    ):
        result = node(_state())

    assert result["final_rating"] == "REVIEW"
    assert llm.calls == 0
