"""Verifies D1-REQ-GOV-012 at runtime: every agent prompt comes from the versioned store.

A store that no agent reads is documentation, not a versioned prompt. These tests
pin the twelve agent nodes to named entries, prove a missing entry fails the node
closed instead of falling back to a literal, and fail when a migrated prompt
reappears in `src/tradingagents/agents/**`.
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from tradingagents import prompts
from tradingagents.dataflows.config import set_config
from tradingagents.prompts import PromptError, load_all

REPO = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO / "src" / "tradingagents" / "agents"

# Every prompt a node must load from the store, keyed by the module that owns it.
# The guard test also checks the three shared-fragment modules.
AGENT_PROMPTS = {
    "tradingagents.agents.analysts.market_analyst": (
        "analyst.tool_preamble",
        "analyst.market.system",
    ),
    "tradingagents.agents.analysts.news_analyst": (
        "analyst.tool_preamble",
        "analyst.news.system",
    ),
    "tradingagents.agents.analysts.fundamentals_analyst": (
        "analyst.tool_preamble",
        "analyst.fundamentals.system",
    ),
    "tradingagents.agents.analysts.sentiment_analyst": (
        "analyst.sentiment_preamble",
        "analyst.sentiment.system",
    ),
    "tradingagents.agents.researchers.bull_researcher": (
        "researcher.bull.role",
        "researcher.bull.task",
        "shared.debate_turn_instruction",
    ),
    "tradingagents.agents.researchers.bear_researcher": (
        "researcher.bear.role",
        "researcher.bear.task",
        "shared.debate_turn_instruction",
    ),
    "tradingagents.agents.risk_mgmt.aggressive_debator": (
        "risk.aggressive.role",
        "risk.aggressive.task",
        "shared.debate_turn_instruction",
    ),
    "tradingagents.agents.risk_mgmt.conservative_debator": (
        "risk.conservative.role",
        "risk.conservative.task",
        "shared.debate_turn_instruction",
    ),
    "tradingagents.agents.risk_mgmt.neutral_debator": (
        "risk.neutral.role",
        "risk.neutral.task",
        "shared.debate_turn_instruction",
    ),
    "tradingagents.agents.managers.research_manager": (
        "manager.research.role",
        "manager.research.task",
        "shared.no_external_tools",
    ),
    "tradingagents.agents.managers.portfolio_manager": (
        "manager.portfolio.role",
        "manager.portfolio.task",
        "shared.no_external_tools",
    ),
    "tradingagents.agents.trader.trader": (
        "trader.role",
        "trader.task",
        "shared.no_external_tools",
    ),
    "tradingagents.agents.debate": ("shared.debate_turn_instruction",),
    "tradingagents.agents.structured": ("shared.no_external_tools",),
    "tradingagents.agents.context": ("shared.language_instruction",),
}

AGENT_FACTORIES = {
    "tradingagents.agents.analysts.market_analyst": "create_market_analyst",
    "tradingagents.agents.analysts.news_analyst": "create_news_analyst",
    "tradingagents.agents.analysts.fundamentals_analyst": "create_fundamentals_analyst",
    "tradingagents.agents.analysts.sentiment_analyst": "create_sentiment_analyst",
    "tradingagents.agents.researchers.bull_researcher": "create_bull_researcher",
    "tradingagents.agents.researchers.bear_researcher": "create_bear_researcher",
    "tradingagents.agents.managers.research_manager": "create_research_manager",
    "tradingagents.agents.trader.trader": "create_trader",
    "tradingagents.agents.risk_mgmt.aggressive_debator": "create_aggressive_debator",
    "tradingagents.agents.risk_mgmt.conservative_debator": "create_conservative_debator",
    "tradingagents.agents.risk_mgmt.neutral_debator": "create_neutral_debator",
    "tradingagents.agents.managers.portfolio_manager": "create_portfolio_manager",
}


class _RecordingLLM:
    """A provider stand-in that records the exact prompt it receives."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def bind_tools(self, tools):
        return RunnableLambda(self._call)

    def _call(self, messages):
        self.prompts.append(_flatten(messages))
        return AIMessage(content="Report.")

    def invoke(self, prompt):
        self.prompts.append(_flatten(prompt))
        return AIMessage(content="Rating: Hold")

    def with_structured_output(self, schema):
        raise NotImplementedError


def _flatten(prompt) -> str:
    if isinstance(prompt, str):
        return prompt
    parts = []
    for item in prompt:
        if isinstance(item, dict):
            parts.append(str(item.get("content", "")))
        else:
            parts.append(str(getattr(item, "content", item)))
    return "\n".join(parts)


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


def _prepare(monkeypatch, module_name, module):
    if module_name.endswith("sentiment_analyst"):
        monkeypatch.setattr(module, "fetch_stocktwits_messages", lambda *a, **k: "st")
        monkeypatch.setattr(module, "fetch_reddit_posts", lambda *a, **k: "rd")
        monkeypatch.setattr(module.get_news, "func", lambda *a, **k: "news")
        monkeypatch.setattr(module, "jev_screen", lambda *a, **k: None)


def _sentinel_loader(monkeypatch):
    real = prompts.load_prompt

    def fake(name, version=None):
        prompt = real(name, version)
        return prompts.Prompt(
            name=prompt.name,
            version=prompt.version,
            text=f"SENTINEL[{name}]\n{prompt.text}",
            description=prompt.description,
        )

    monkeypatch.setattr(prompts, "load_prompt", fake)


def _run_agent(monkeypatch, module_name, module, llm):
    _prepare(monkeypatch, module_name, module)
    factory = AGENT_FACTORIES[module_name]
    getattr(module, factory)(llm)(_state())
    return "\n".join(llm.prompts)


@pytest.mark.unit
def test_every_runtime_prompt_is_in_the_store():
    loaded = load_all()
    required = {name for names in AGENT_PROMPTS.values() for name in names}
    assert required - set(loaded) == set()


@pytest.mark.unit
@pytest.mark.parametrize("module_name", sorted(AGENT_FACTORIES))
def test_the_agent_loads_its_prompts_from_the_store(monkeypatch, module_name):
    _sentinel_loader(monkeypatch)
    module = importlib.import_module(module_name)
    text = _run_agent(monkeypatch, module_name, module, _RecordingLLM())

    for name in AGENT_PROMPTS[module_name]:
        assert f"SENTINEL[{name}]" in text, f"{module_name} did not load {name}"


@pytest.mark.unit
@pytest.mark.parametrize("module_name", sorted(AGENT_FACTORIES))
def test_a_missing_prompt_fails_the_node_closed(monkeypatch, module_name):
    def missing(name, version=None):
        raise PromptError(f"store unavailable for {name}")

    monkeypatch.setattr(prompts, "load_prompt", missing)
    module = importlib.import_module(module_name)
    _prepare(monkeypatch, module_name, module)

    with pytest.raises(PromptError):
        getattr(module, AGENT_FACTORIES[module_name])(_RecordingLLM())(_state())


@pytest.mark.unit
def test_no_agent_module_embeds_a_migrated_prompt():
    loaded = load_all()
    offenders: dict[str, list[str]] = {}
    for module_name, names in AGENT_PROMPTS.items():
        relative = module_name.removeprefix("tradingagents.agents.").replace(".", "/")
        source = (AGENTS_DIR / f"{relative}.py").read_text(encoding="utf-8")
        for name in names:
            if loaded[name].text[:60] in source:
                offenders.setdefault(f"{relative}.py", []).append(name)

    assert offenders == {}


@pytest.mark.unit
def test_a_braced_report_value_is_inserted_verbatim(monkeypatch):
    braced = '{"x": 1}'
    _sentinel_loader(monkeypatch)

    sentiment = importlib.import_module(
        "tradingagents.agents.analysts.sentiment_analyst"
    )
    monkeypatch.setattr(sentiment, "fetch_stocktwits_messages", lambda *a, **k: "st")
    monkeypatch.setattr(sentiment, "fetch_reddit_posts", lambda *a, **k: "rd")
    monkeypatch.setattr(sentiment.get_news, "func", lambda *a, **k: braced)
    monkeypatch.setattr(sentiment, "jev_screen", lambda *a, **k: None)
    llm = _RecordingLLM()
    sentiment.create_sentiment_analyst(llm)(_state())
    assert braced in "\n".join(llm.prompts)

    manager = importlib.import_module("tradingagents.agents.managers.research_manager")
    llm = _RecordingLLM()
    manager.create_research_manager(llm)(
        _state(investment_debate_state={"history": braced, "count": 1})
    )
    assert braced in "\n".join(llm.prompts)

    trader = importlib.import_module("tradingagents.agents.trader.trader")
    llm = _RecordingLLM()
    trader.create_trader(llm)(_state(investment_plan=braced))
    assert braced in "\n".join(llm.prompts)


@pytest.mark.unit
def test_the_language_instruction_comes_from_the_store(monkeypatch):
    _sentinel_loader(monkeypatch)
    set_config({"output_language": "中文"})
    try:
        from tradingagents.agents.context import get_language_instruction

        assert "SENTINEL[shared.language_instruction]" in get_language_instruction()
    finally:
        set_config({"output_language": "English"})


@pytest.mark.unit
def test_import_does_not_read_the_store(tmp_path):
    env = dict(os.environ)
    env["TRADINGAGENTS_PROMPTS_DIR"] = str(tmp_path)
    env["PYTHONPATH"] = str(REPO / "src")

    result = subprocess.run(
        [sys.executable, "-c", "import tradingagents; import cli.main"],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
