"""D1-REQ-TERM-002: repeated identical tool calls end an analyst's loop early.

Two identical consecutive calls are not progress. The pure detector canonicalises
each call by ``(name, json.dumps(args, sort_keys=True))`` so a dict's key order
and a fresh tool-call id cannot hide a repeat, while different arguments or a
different call in between reset the streak. The analyst graph wraps up when the
detector fires and keeps ``max_tool_rounds`` as the backstop.
"""

from __future__ import annotations

import logging

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from tradingagents.agents.analysts.turn import WRAP_UP
from tradingagents.graph import setup as graph_setup
from tradingagents.graph.analyst_execution import AnalystNodeSpec
from tradingagents.graph.setup import _analyst_graph, identical_call_repeat


def _call(name: str = "get_stock_data", args: dict | None = None, call_id: str = "call_1") -> dict:
    return {"name": name, "args": {"symbol": "NVDA"} if args is None else args, "id": call_id}


def _round(*calls: dict) -> AIMessage:
    return AIMessage(content="", tool_calls=list(calls))


@pytest.mark.unit
def test_two_identical_calls_are_detected():
    messages = [_round(_call(call_id="call_1")), _round(_call(call_id="call_2"))]

    assert identical_call_repeat(messages) == "get_stock_data"


@pytest.mark.unit
def test_argument_dict_order_does_not_hide_a_repeat():
    messages = [
        _round(_call(args={"symbol": "NVDA", "period": "1y"})),
        _round(_call(args={"period": "1y", "symbol": "NVDA"}, call_id="call_2")),
    ]

    assert identical_call_repeat(messages) == "get_stock_data"


@pytest.mark.unit
def test_different_arguments_are_not_detected():
    messages = [
        _round(_call(args={"symbol": "NVDA"})),
        _round(_call(args={"symbol": "MSFT"}, call_id="call_2")),
    ]

    assert identical_call_repeat(messages) is None


@pytest.mark.unit
def test_a_different_call_between_repeats_is_not_detected():
    messages = [
        _round(_call(args={"symbol": "NVDA"})),
        _round(_call(name="get_news", args={"ticker": "NVDA"}, call_id="call_2")),
        _round(_call(args={"symbol": "NVDA"}, call_id="call_3")),
    ]

    assert identical_call_repeat(messages) is None


@tool
def get_stock_data(symbol: str) -> str:
    """Return the daily prices for a symbol."""
    return f"{symbol} prices"


SPEC = AnalystNodeSpec(
    key="market",
    agent_node="Market Analyst",
    report_key="market_report",
    tools=(get_stock_data,),
)


class RepeatingAnalyst:
    """A scripted node that makes the same call every round until told to wrap up."""

    def __init__(self):
        self.tool_rounds = 0
        self.wrap_up_messages = None

    def __call__(self, state):
        messages = state["messages"]
        if isinstance(messages[-1], HumanMessage) and messages[-1].content == WRAP_UP:
            self.wrap_up_messages = messages
            return {"market_report": "report from tool results"}
        self.tool_rounds += 1
        call = _call(call_id=f"call_{self.tool_rounds}")
        return {"messages": [AIMessage(content="", tool_calls=[call])]}


def _run(graph):
    return graph.invoke(
        {"messages": [HumanMessage("Analyse NVDA")], "company_of_interest": "NVDA",
         "trade_date": "2026-01-09"},
        config={"recursion_limit": 100},
    )


@pytest.mark.unit
def test_the_graph_wraps_up_on_the_second_repeat_not_at_the_round_bound(caplog):
    analyst = RepeatingAnalyst()
    graph = _analyst_graph(SPEC, analyst, max_tool_rounds=20)

    with caplog.at_level(logging.WARNING, logger=graph_setup.__name__):
        result = _run(graph)

    assert analyst.tool_rounds == 2          # the second call repeats the first
    assert analyst.wrap_up_messages is not None
    assert result["market_report"] == "report from tool results"
    assert "get_stock_data" in caplog.text
    assert "repeat" in caplog.text.lower()


@pytest.mark.unit
def test_without_the_detector_the_same_model_runs_to_the_round_bound(monkeypatch):
    """The negative test: a missing detector must let the loop reach the bound."""
    monkeypatch.setattr(graph_setup, "identical_call_repeat", lambda messages, limit=2: None)
    analyst = RepeatingAnalyst()
    graph = _analyst_graph(SPEC, analyst, max_tool_rounds=20)

    result = _run(graph)

    assert analyst.tool_rounds == 20
    assert result["market_report"] == "report from tool results"
