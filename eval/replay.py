"""Deterministic, offline backend for ``python -m eval.run`` (D1-REQ-EVAL-001).

The evaluation must be reproducible and must run without an API key, so this
backend replaces two boundaries only:

- the model, with a scripted chat model that calls every tool once and then
  writes a fixed report (so the graph, the prompts, the assembler and the budget
  are the real ones);
- the data vendors, with fixed payloads through the existing router hooks.

Everything between those two boundaries is the shipped pipeline, including the
token ledger the COST-001 check reads. The scripted report is deliberately the
same length as an analyst's, so the prompt growth the budget controls is real
rather than a toy string.
"""

from __future__ import annotations

import copy
import time
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from tradingagents.agents import context
from tradingagents.agents.analysts import sentiment_analyst
from tradingagents.dataflows import router
from tradingagents.dataflows.vendors.yahoo import market as yahoo_market, snapshot
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.evaluation import CaseObservation, EvaluationCase
from tradingagents.graph import trading_graph

# One fixed date for every fixture payload; the cases carry their own trade date.
FIXTURE_DATE = "2026-01-09"

REPORT = (
    "# Analysis\n\n"
    + (
        "The desk sees a constructive tape: breadth is positive, the 50-day sits above the "
        "200-day, and the last four sessions closed above the prior range. Volume confirms the "
        "move on two of the four sessions. Sentiment is neutral-to-positive with no crowding "
        "signal. News flow is dominated by a product cycle and a modest guidance raise; the "
        "fundamental picture shows revenue growth in line with consensus and stable margins. "
        "Risks: a hot CPI print and a crowded options expiry. Position sizing should respect "
        "the volatility regime. "
    )
    * 6
    + "\n\n**Rating**: Overweight\n\nFINAL TRANSACTION PROPOSAL: **BUY**"
)

# Arguments a tool call may need; each tool keeps the subset its schema declares.
TOOL_ARGUMENTS = {
    "symbol": "NVDA",
    "ticker": "NVDA",
    "curr_date": FIXTURE_DATE,
    "start_date": "2026-01-02",
    "end_date": FIXTURE_DATE,
    "indicator": "rsi",
    "topic": "Fed rate cut",
    "freq": "quarterly",
}


class ScriptedModel(BaseChatModel):
    """Calls every bound tool once, then answers with the fixed report."""

    tools: tuple = ()
    calls: list = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "eval-scripted"

    def bind_tools(self, tools, **kwargs):
        return self.model_copy(update={"tools": tuple(tools)})

    def with_structured_output(self, schema, **kwargs):
        return _ScriptedStructured(schema)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls.append(1)
        if self.tools and not isinstance(messages[-1], ToolMessage):
            calls = [
                {
                    "name": tool.name,
                    "id": f"call_{index}",
                    "args": {
                        key: value
                        for key, value in TOOL_ARGUMENTS.items()
                        if key in tool.tool_call_schema.model_json_schema()["properties"]
                    },
                }
                for index, tool in enumerate(self.tools)
            ]
            message = AIMessage(content="", tool_calls=calls)
        else:
            message = AIMessage(content=REPORT)
        return ChatResult(generations=[ChatGeneration(message=message)])


class _ScriptedStructured:
    """A deterministic structured-output binding for the replay model."""

    def __init__(self, schema) -> None:
        self.schema = schema

    def invoke(self, prompt, **kwargs):
        return _structured_value(self.schema)


def _structured_value(schema):
    """A schema-valid canned value for the replay model.

    The replay exercises the shipped structured path rather than the free-text
    fallback, so QUAL-001 can measure it. A schema added later must either be
    listed here or raise: a silent generic object would measure nothing.
    """
    name = getattr(schema, "__name__", "")
    if name == "SentimentReport":
        return schema(
            overall_band="Neutral",
            overall_score=5.0,
            confidence="medium",
            narrative=REPORT,
        )
    if name == "ResearchPlan":
        return schema(
            recommendation="Overweight",
            rationale="The bull case carried on the supplied evidence.",
            strategic_actions="Build the position gradually; respect the ceiling.",
        )
    if name == "TraderProposal":
        return schema(
            action="Buy",
            reasoning="The research plan and the price structure support a long.",
            position_pct=5.0,
        )
    if name == "PortfolioDecision":
        return schema(
            rating="Overweight",
            executive_summary="Build the position gradually within the ceiling.",
            investment_thesis="The analysts' evidence favours the bull case.",
            position_pct=5.0,
        )
    if name == "DebateTurn":
        return schema(
            claim="The evidence supports a constructive position.",
            evidence=[{"source": "analyst reports", "quote": "Breadth and guidance are positive."}],
            rebuttal="The bear case is acknowledged but the evidence is stronger here.",
            confidence="medium",
            diverge="Weighed the bear case and the volatility regime.",
            converge="A moderate long is the best-supported position.",
        )
    raise NotImplementedError(f"the replay model has no structured value for {name}")


class _Client:
    def __init__(self, model: BaseChatModel) -> None:
        self.model = model

    def get_llm(self) -> BaseChatModel:
        return self.model


@contextmanager
def _scripted_clients(model: BaseChatModel):
    """Replace the provider factory for the duration of graph construction."""
    original = trading_graph.create_tier_client
    trading_graph.create_tier_client = lambda config, tier, **kwargs: _Client(model)
    try:
        yield
    finally:
        trading_graph.create_tier_client = original


def _vendor_payload(method: str) -> str:
    """A payload shaped like a vendor response: a header, a table and notes."""
    rows = "\n".join(
        f"2026-01-{day:02d},100.{day},101.{day},99.{day},100.{day},1{day}00000"
        for day in range(1, 29)
    )
    return f"{method}\nDate,Open,High,Low,Close,Volume\n{rows}\n" + ("Source note. " * 250)


def _install_vendor_stubs() -> None:
    """Answer every routed vendor call and the direct fetches the agents make."""
    for method, vendors in router.VENDOR_METHODS.items():
        for vendor in vendors:
            vendors[vendor] = lambda *args, _method=method, **kwargs: _vendor_payload(_method)
    prices = pd.DataFrame(
        {
            "Date": pd.bdate_range(end=FIXTURE_DATE, periods=60),
            "Open": 100.0,
            "High": 101.0,
            "Low": 99.0,
            "Close": 100.5,
            "Volume": 1_000_000,
        }
    )
    snapshot.load_ohlcv = lambda *args, **kwargs: prices.copy()
    sentiment_analyst.fetch_stocktwits_messages = lambda *args, **kwargs: "no posts"
    sentiment_analyst.fetch_reddit_posts = lambda *args, **kwargs: "no posts"
    yahoo_market.yf.Ticker = lambda symbol: type(
        "Ticker", (), {"info": {"longName": f"{symbol} Inc."}}
    )()
    context._identity.cache_clear()


def _replay_config(
    results_dir: str | Path,
    overrides: Mapping[str, Any] | None,
    case_id: str,
) -> dict[str, Any]:
    """Per-case config: a fresh results and memory directory, so cases stay independent."""
    base = Path(results_dir) / case_id
    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(
        results_dir=str(base / "runs"),
        data_cache_dir=str(base / "cache"),
        memory_log_path=str(base / "memory.md"),
        checkpoint_enabled=False,
    )
    config.update(dict(overrides or {}))
    return config


def build_replay_analyzer(
    results_dir: str | Path,
    overrides: Mapping[str, Any] | None = None,
) -> Callable[[EvaluationCase], CaseObservation]:
    """Return a ``case -> CaseObservation`` callable backed by the replay fixtures.

    ``results_dir`` must be specific to this analyzer pass: the memory log, cache
    and trace live under it, so two passes that share one directory read each
    other's state and the same-condition comparison becomes false.
    """
    _install_vendor_stubs()
    graphs: dict[str, tuple[trading_graph.TradingAgentsGraph, dict[str, Any]]] = {}

    def graph_for(case: EvaluationCase) -> tuple[trading_graph.TradingAgentsGraph, dict[str, Any]]:
        entry = graphs.get(case.id)
        if entry is None:
            config = _replay_config(results_dir, overrides, case.id)
            with _scripted_clients(ScriptedModel()):
                graph = trading_graph.TradingAgentsGraph(
                    selected_analysts=case.analysts, config=config
                )
            entry = (graph, config)
            graphs[case.id] = entry
        return entry

    def analyze(case: EvaluationCase) -> CaseObservation:
        graph, config = graph_for(case)
        started = time.perf_counter()
        final_state, rating = graph.propagate(case.ticker, case.trade_date)
        elapsed = time.perf_counter() - started
        usage = dict(getattr(graph, "_context_usage", {}) or {})
        return CaseObservation(
            total_tokens=int(usage.get("total_tokens", 0)),
            budget=int(usage.get("budget", config["context_budget_tokens"])),
            compacted_calls=int(usage.get("compacted_calls", 0)),
            wall_clock_s=round(elapsed, 3),
            rating=str(rating),
            structured_output_ok=(
                final_state.get("final_decision_source") == "structured"
            ),
        )

    return analyze
