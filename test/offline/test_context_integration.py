"""Runtime integration: every report-producing agent declares the six layers.

The assembler unit tests cover the layer contract; these tests prove the agents
actually use it, and that the inherited prompt guarantees survive the change:
the research team stays blind to the portfolio, and analysts keep their tool
rounds.
"""

from __future__ import annotations

import importlib

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from tradingagents.context import Layer

AGENTS = [
    ("tradingagents.agents.analysts.market_analyst", "create_market_analyst"),
    ("tradingagents.agents.analysts.news_analyst", "create_news_analyst"),
    ("tradingagents.agents.analysts.fundamentals_analyst", "create_fundamentals_analyst"),
    ("tradingagents.agents.analysts.sentiment_analyst", "create_sentiment_analyst"),
    ("tradingagents.agents.researchers.bull_researcher", "create_bull_researcher"),
    ("tradingagents.agents.researchers.bear_researcher", "create_bear_researcher"),
    ("tradingagents.agents.managers.research_manager", "create_research_manager"),
    ("tradingagents.agents.trader.trader", "create_trader"),
    ("tradingagents.agents.risk_mgmt.aggressive_debator", "create_aggressive_debator"),
    ("tradingagents.agents.risk_mgmt.conservative_debator", "create_conservative_debator"),
    ("tradingagents.agents.risk_mgmt.neutral_debator", "create_neutral_debator"),
    ("tradingagents.agents.managers.portfolio_manager", "create_portfolio_manager"),
]


class _FakeLLM:
    """A provider stand-in: records prompts, never reaches the network."""

    def __init__(self) -> None:
        self.calls = 0

    def bind_tools(self, tools):
        return RunnableLambda(self._call)

    def _call(self, messages):
        self.calls += 1
        return AIMessage(content="Report.")

    def invoke(self, prompt):
        self.calls += 1
        return AIMessage(content="Rating: Hold")

    def with_structured_output(self, schema):
        raise NotImplementedError


def _state(**overrides):
    state = {
        "company_of_interest": "NVDA",
        "trade_date": "2026-01-15",
        "asset_type": "stock",
        "instrument_context": "",
        "portfolio_context": "",
        "messages": [],
        "market_report": "Market report.",
        "sentiment_report": "Sentiment report.",
        "news_report": "News report.",
        "fundamentals_report": "Fundamentals report.",
        "investment_plan": "Plan.",
        "trader_investment_plan": "Trader plan.",
        "past_context": "",
        "investment_debate_state": {
            "bull_history": "",
            "bear_history": "",
            "history": "Debate.",
            "current_response": "",
            "count": 1,
        },
        "risk_debate_state": {
            "aggressive_history": "",
            "conservative_history": "",
            "neutral_history": "",
            "history": "Risk debate.",
            "latest_speaker": "",
            "current_aggressive_response": "",
            "current_conservative_response": "",
            "current_neutral_response": "",
            "count": 1,
        },
    }
    state.update(overrides)
    return state


def _capture_layers(monkeypatch, module):
    real = module.assemble_context
    seen = []

    def wrapper(layers, **kwargs):
        seen.append(layers)
        return real(layers, **kwargs)

    monkeypatch.setattr(module, "assemble_context", wrapper)
    return seen


def _prepare_sentiment(monkeypatch, module):
    monkeypatch.setattr(module, "fetch_stocktwits_messages", lambda *a, **k: "st")
    monkeypatch.setattr(module, "fetch_reddit_posts", lambda *a, **k: "rd")
    monkeypatch.setattr(module.get_news, "func", lambda *a, **k: "news", raising=False)


@pytest.mark.unit
@pytest.mark.parametrize("module_name,factory", AGENTS)
def test_every_report_agent_declares_all_six_layers(monkeypatch, module_name, factory):
    module = importlib.import_module(module_name)
    if module_name.endswith("sentiment_analyst"):
        _prepare_sentiment(monkeypatch, module)
    seen = _capture_layers(monkeypatch, module)

    getattr(module, factory)(_FakeLLM())(_state())

    assert seen, f"{factory} did not call the assembler"
    declared = seen[0]
    assert declared.missing() == ()
    assert set(declared.sources()) == set(Layer)
    assert all(declared.sources()[layer] for layer in Layer)


@pytest.mark.unit
@pytest.mark.parametrize(
    "module_name,factory",
    [
        ("tradingagents.agents.researchers.bull_researcher", "create_bull_researcher"),
        ("tradingagents.agents.researchers.bear_researcher", "create_bear_researcher"),
    ],
)
def test_researchers_declare_no_portfolio_identity(monkeypatch, module_name, factory):
    module = importlib.import_module(module_name)
    seen = _capture_layers(monkeypatch, module)

    getattr(module, factory)(_FakeLLM())(
        _state(portfolio_context="PORTFOLIO_BLOCK_MARKER")
    )

    sources = seen[0].sources()
    assert all("portfolio" not in source for source in sources[Layer.IDENTITY])


@pytest.mark.unit
def test_every_prompt_source_uses_the_assembler():
    """Source-level guard: a new report agent must not bypass the assembler."""
    for module_name, _ in AGENTS:
        source = importlib.import_module(module_name).__file__
        assert source is not None
        with open(source, encoding="utf-8") as handle:
            text = handle.read()
        assert "assemble_context(" in text, module_name


@pytest.mark.unit
def test_an_analyst_declares_its_message_history_as_the_history_layer(monkeypatch):
    module = importlib.import_module("tradingagents.agents.analysts.market_analyst")
    seen = _capture_layers(monkeypatch, module)
    history = [("human", "x" * 1600)] * 4

    module.create_market_analyst(_FakeLLM())(_state(messages=history))

    assert seen[0].sources()[Layer.HISTORY] == ("state.messages",)
