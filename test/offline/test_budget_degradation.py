"""Budget exhaustion ends every entry point in a deterministic REVIEW (DEBT-012).

Covers ``D1-REQ-COST-003`` (the run cap is enforced) and ``D1-REQ-TERM-001``
(the run records why it stopped). The policy: a ``ContextBudgetExceeded`` that
reaches a run boundary returns ``final_rating == "REVIEW"`` with
``termination_reason == "budget_exhausted"``; the state log is written, the
memory log is skipped, and the checkpoint is kept. Any other exception still
propagates. The Portfolio Manager keeps its own catch and can still decide on
the reserve; that run is recorded normally.
"""

from __future__ import annotations

import copy
import json
from typing import TypedDict

import pytest
from langgraph.graph import END, START, StateGraph

import tradingagents.graph.trading_graph as trading_graph
from tradingagents.context import ContextBudgetExceeded
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.checkpointer import (
    checkpoint_step,
    get_checkpointer,
    thread_id,
)

TRADE_DATE = "2026-01-09"
TICKER = "NVDA"


class _Model:
    """No provider call: every test raises before the model would answer."""

    def bind_tools(self, tools, **kwargs):
        return self

    def with_structured_output(self, schema, **kwargs):
        raise NotImplementedError

    def invoke(self, *args, **kwargs):  # pragma: no cover - a call is the bug
        raise AssertionError("the degraded path must not call the model")


class _Client:
    def __init__(self, model):
        self.model = model

    def get_llm(self):
        return self.model


def _graph(tmp_path, monkeypatch, *, debug=False, selected_analysts=None, **config):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg.update(
        results_dir=str(tmp_path / "results"),
        data_cache_dir=str(tmp_path / "cache"),
        memory_log_path=str(tmp_path / "memory.md"),
        checkpoint_enabled=False,
    )
    cfg.update(config)
    monkeypatch.setattr(
        trading_graph, "create_tier_client", lambda config, tier, **k: _Client(_Model())
    )
    # Identity resolution is a live vendor lookup; the boundary tests do not need it.
    monkeypatch.setattr(trading_graph, "resolve_instrument_identity", lambda ticker: {})
    kwargs = {"config": cfg, "debug": debug}
    if selected_analysts is not None:
        kwargs["selected_analysts"] = selected_analysts
    return trading_graph.TradingAgentsGraph(**kwargs)


def _raise(exc_type, message="run cap"):
    def raiser(*args, **kwargs):
        raise exc_type(message)

    return raiser


def _degraded_state(tmp_path, monkeypatch):
    graph = _graph(tmp_path, monkeypatch)
    monkeypatch.setattr(graph.graph, "invoke", _raise(ContextBudgetExceeded))
    return graph.propagate(TICKER, TRADE_DATE)


@pytest.mark.unit
def test_the_initial_state_names_no_termination(tmp_path, monkeypatch):
    """A normal run starts with an empty reason (D1-REQ-TERM-001)."""
    graph = _graph(tmp_path, monkeypatch)

    assert graph.create_run_state(TICKER, TRADE_DATE)["termination_reason"] == ""


@pytest.mark.unit
def test_a_tiny_budget_returns_review_instead_of_raising(tmp_path, monkeypatch):
    """The normal ``propagate()`` path degrades instead of failing (D1-REQ-COST-003).

    D1-REQ-CTX-003 owns the budget itself; this asserts its run-boundary fallback, where
    the assembled context would exceed the cap and the run ends in REVIEW instead.
    """
    graph = _graph(tmp_path, monkeypatch)
    statuses: list[str] = []
    monkeypatch.setattr(graph, "_write_telemetry", lambda *a, **k: statuses.append(a[3]))
    monkeypatch.setattr(graph.graph, "invoke", _raise(ContextBudgetExceeded))

    state, signal = graph.propagate(TICKER, TRADE_DATE)

    assert signal == state["final_rating"] == "REVIEW"
    assert state["termination_reason"] == "budget_exhausted"
    assert statuses == ["degraded"]


@pytest.mark.unit
def test_a_real_tiny_budget_degrades_before_any_model_call(tmp_path, monkeypatch):
    """A genuine cap (not a patched exception) ends the analyse step in REVIEW (D1-REQ-CTX-003)."""
    graph = _graph(
        tmp_path,
        monkeypatch,
        selected_analysts=("market",),
        context_budget_tokens=1,
        context_call_budget_tokens=1,
        context_decision_reserve_tokens=0,
    )

    state, signal = graph.propagate(TICKER, TRADE_DATE)

    assert signal == state["final_rating"] == "REVIEW"
    assert state["termination_reason"] == "budget_exhausted"


@pytest.mark.unit
def test_a_debug_run_degrades_through_the_stream(tmp_path, monkeypatch):
    """``_run_graph(debug=True)`` goes through ``stream_run``; it degrades too."""
    graph = _graph(tmp_path, monkeypatch, debug=True)
    monkeypatch.setattr(graph, "_stream_run", _raise(ContextBudgetExceeded))

    state, signal = graph.propagate(TICKER, TRADE_DATE)

    assert signal == state["final_rating"] == "REVIEW"
    assert state["termination_reason"] == "budget_exhausted"


@pytest.mark.unit
def test_stream_run_yields_the_degraded_state(tmp_path, monkeypatch):
    """The CLI's stream path ends with the same REVIEW state (COST-003)."""
    graph = _graph(tmp_path, monkeypatch)
    monkeypatch.setattr(graph, "_stream_run", _raise(ContextBudgetExceeded))

    chunks = list(graph.stream_run(graph.create_run_state(TICKER, TRADE_DATE)))

    assert chunks[-1][1]["final_rating"] == "REVIEW"
    assert chunks[-1][1]["termination_reason"] == "budget_exhausted"


@pytest.mark.unit
def test_stream_run_reports_degraded_telemetry(tmp_path, monkeypatch):
    """The stream path records the run as degraded, not complete."""
    graph = _graph(tmp_path, monkeypatch)
    statuses: list[str] = []
    monkeypatch.setattr(
        graph, "_write_telemetry_identity", lambda *a, **k: statuses.append(a[3])
    )
    monkeypatch.setattr(graph, "_stream_run", _raise(ContextBudgetExceeded))

    list(graph.stream_run(graph.create_run_state(TICKER, TRADE_DATE)))

    assert statuses == ["degraded"]


@pytest.mark.unit
def test_stream_run_without_identity_reraises(tmp_path, monkeypatch):
    """A resume with no state yet carries no ticker; inventing one is worse."""
    graph = _graph(tmp_path, monkeypatch)
    monkeypatch.setattr(graph, "_stream_run", _raise(ContextBudgetExceeded))

    with pytest.raises(ContextBudgetExceeded):
        list(graph.stream_run(None))


@pytest.mark.unit
def test_a_different_exception_still_propagates(tmp_path, monkeypatch):
    """Only the budget exception degrades; a provider failure is still a failure."""
    graph = _graph(tmp_path, monkeypatch)
    monkeypatch.setattr(graph.graph, "invoke", _raise(RuntimeError, "boom"))

    with pytest.raises(RuntimeError, match="boom"):
        graph.propagate(TICKER, TRADE_DATE)


@pytest.mark.unit
def test_the_state_log_and_the_memory_log_disagree_on_review(tmp_path, monkeypatch):
    """A REVIEW non-decision is logged for a person, not recorded as a position.

    The log must carry the empty plan fields so the existing writer needs no
    special case (COST-003).
    """
    _degraded_state(tmp_path, monkeypatch)

    state_log = next((tmp_path / "results").rglob("full_states_log_2026-01-09.json"))
    logged = json.loads(state_log.read_text(encoding="utf-8"))
    assert logged["termination_reason"] == "budget_exhausted"
    assert logged["final_rating"] == "REVIEW"
    assert logged["investment_plan"] == ""
    assert logged["trader_investment_plan"] == ""
    assert not (tmp_path / "memory.md").exists()


@pytest.mark.unit
def test_removing_the_handler_lets_the_exception_escape(tmp_path, monkeypatch):
    """Negative test: the tiny-budget run exercises the handler, not luck."""
    graph = _graph(tmp_path, monkeypatch)
    monkeypatch.setattr(
        graph, "_budget_exhausted_state", _raise(ContextBudgetExceeded, "x")
    )
    monkeypatch.setattr(graph.graph, "invoke", _raise(ContextBudgetExceeded))

    with pytest.raises(ContextBudgetExceeded):
        graph.propagate(TICKER, TRADE_DATE)


@pytest.mark.unit
def test_record_decision_skips_the_memory_log_for_a_review_non_decision(
    tmp_path, monkeypatch
):
    """A REVIEW + budget_exhausted state is not a call the next run should quote."""
    graph = _graph(tmp_path, monkeypatch)
    state = graph.create_run_state(TICKER, TRADE_DATE)
    state.update(
        final_trade_decision="Rating: REVIEW\n\nThe context budget ended this run.",
        final_rating="REVIEW",
        termination_reason="budget_exhausted",
        investment_plan="",
        trader_investment_plan="",
    )

    graph.record_decision(TICKER, TRADE_DATE, state)

    assert not (tmp_path / "memory.md").exists()


@pytest.mark.unit
def test_a_budget_stopped_run_that_decided_is_recorded(tmp_path, monkeypatch):
    """The Portfolio Manager can still decide on the reserve; that call counts."""
    graph = _graph(tmp_path, monkeypatch)
    state = graph.create_run_state(TICKER, TRADE_DATE)
    state.update(
        final_rating="Overweight",
        final_trade_decision="Rating: Overweight\n\nDecided on the reserve.",
        termination_reason="budget_exhausted",
        investment_plan="",
        trader_investment_plan="",
    )

    graph.record_decision(TICKER, TRADE_DATE, state)

    assert "Overweight" in (tmp_path / "memory.md").read_text(encoding="utf-8")


class _TinyState(TypedDict):
    count: int


def _seed_checkpoint(cache_dir, ticker, trade_date, signature):
    """Write one real checkpoint under the run's thread id."""

    def step(state):
        return {"count": state["count"] + 1}

    workflow = StateGraph(_TinyState)
    workflow.add_node("step", step)
    workflow.add_edge(START, "step")
    workflow.add_edge("step", END)
    with get_checkpointer(cache_dir, ticker) as saver:
        tiny = workflow.compile(checkpointer=saver)
        tiny.invoke(
            {"count": 0},
            config={"configurable": {"thread_id": thread_id(ticker, trade_date, signature)}},
        )


@pytest.mark.unit
def test_the_degraded_run_keeps_its_checkpoint(tmp_path, monkeypatch):
    """A later run with a larger budget may resume the saved work (COST-003)."""
    graph = _graph(tmp_path, monkeypatch, checkpoint_enabled=True)
    cache = graph.config["data_cache_dir"]
    signature = graph._run_signature("stock")
    _seed_checkpoint(cache, TICKER, TRADE_DATE, signature)
    assert checkpoint_step(cache, TICKER, TRADE_DATE, signature) is not None
    monkeypatch.setattr(graph.graph, "invoke", _raise(ContextBudgetExceeded))

    graph._run_graph(TICKER, TRADE_DATE)

    assert checkpoint_step(cache, TICKER, TRADE_DATE, signature) is not None


@pytest.mark.unit
def test_a_completed_run_still_clears_its_checkpoint(tmp_path, monkeypatch):
    """Only the non-decision keeps the checkpoint; an ordinary run still clears."""
    graph = _graph(tmp_path, monkeypatch, checkpoint_enabled=True)
    cache = graph.config["data_cache_dir"]
    signature = graph._run_signature("stock")
    _seed_checkpoint(cache, TICKER, TRADE_DATE, signature)

    state = graph.create_run_state(TICKER, TRADE_DATE)
    state.update(
        final_rating="Hold",
        final_trade_decision="Rating: Hold\n\nDone.",
        investment_plan="P",
        trader_investment_plan="T",
    )
    monkeypatch.setattr(graph.graph, "invoke", lambda *a, **k: state)

    graph._run_graph(TICKER, TRADE_DATE)

    assert checkpoint_step(cache, TICKER, TRADE_DATE, signature) is None


# --- the CLI merge path ----------------------------------------------------------


class _FakeGraph:
    """Records the lifecycle calls ``run_analysis`` makes."""

    def __init__(self, final_state):
        self.calls = []
        self.propagator = self
        self._resuming = False
        self._final_state = {"messages": [], **final_state}

    def create_run_state(self, ticker, trade_date, asset_type="stock", portfolio=None):
        self.calls.append(("create_run_state", ticker, trade_date))
        return {"messages": [], "company_of_interest": ticker}

    def record_decision(self, ticker, trade_date, final_state):
        self.calls.append(
            ("record_decision", ticker, trade_date, final_state.get("final_rating"))
        )

    def get_graph_args(self, callbacks=None):
        return {}

    def begin_checkpoint(self, *a, **k):
        return None

    def checkpoint_input(self, state):
        return state

    def clear_checkpoint_on_success(self, *a, **k):
        self.calls.append(("clear_checkpoint",))

    def end_checkpoint(self):
        pass

    def stream_run(self, graph_input, **kwargs):
        yield [], {"messages": [], "market_report": "M"}
        yield [], self._final_state


class _NullLive:
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _FakeBuffer:
    def __init__(self):
        self.messages = []
        self.tool_calls = []
        self.report_sections = {}
        self.agent_status = {}
        self.selected_analysts = []
        self._processed_message_ids = set()

    def init_for_analysis(self, selected_analysts):
        self.selected_analysts = [a.lower() for a in selected_analysts]

    def add_message(self, kind, content):
        self.messages.append((0.0, kind, content))

    def add_tool_call(self, name, args):
        self.tool_calls.append((0.0, name, args))

    def update_report_section(self, *a):
        pass

    def update_agent_status(self, agent, status):
        self.agent_status[agent] = status


def _run_cli(monkeypatch, tmp_path, fake):
    import cli.main as m
    import cli.run as cli_run
    from cli.models import AnalystType

    monkeypatch.setattr(cli_run, "TradingAgentsGraph", lambda *a, **k: fake)
    monkeypatch.setattr(cli_run, "message_buffer", _FakeBuffer())
    monkeypatch.setattr(cli_run, "create_layout", lambda: None)
    monkeypatch.setattr(cli_run, "update_display", lambda *a, **k: None)
    monkeypatch.setattr(cli_run, "Live", _NullLive)
    monkeypatch.setattr(
        cli_run,
        "get_user_selections",
        lambda flags=None: {
            "ticker": TICKER,
            "analysis_date": "2026-01-10",
            "analysts": [AnalystType.MARKET],
            "asset_type": "stock",
        },
    )
    monkeypatch.setattr(
        cli_run,
        "_build_run_config",
        lambda selections, checkpoint: {
            "data_cache_dir": str(tmp_path / "cache"),
            "results_dir": str(tmp_path / "results"),
        },
    )
    monkeypatch.setattr(m.typer, "prompt", lambda *a, **k: "N")
    cli_run.run_analysis()


@pytest.mark.unit
def test_the_cli_records_but_does_not_clear_a_budget_review(tmp_path, monkeypatch, capsys):
    """The CLI write path follows the same REVIEW rule as ``propagate``."""
    fake = _FakeGraph(
        {
            "final_trade_decision": "Rating: REVIEW\n\nThe context budget ended this run.",
            "final_rating": "REVIEW",
            "termination_reason": "budget_exhausted",
        }
    )

    _run_cli(monkeypatch, tmp_path, fake)

    assert ("record_decision", TICKER, "2026-01-10", "REVIEW") in fake.calls
    assert ("clear_checkpoint",) not in fake.calls
    assert "budget" in capsys.readouterr().out.lower()


@pytest.mark.unit
def test_the_cli_clears_the_checkpoint_when_the_manager_still_decided(
    tmp_path, monkeypatch
):
    """A decision made on the reserve is an ordinary completed run."""
    fake = _FakeGraph(
        {
            "final_trade_decision": "Rating: Hold\n\nDecided on the reserve.",
            "final_rating": "Hold",
            "termination_reason": "budget_exhausted",
        }
    )

    _run_cli(monkeypatch, tmp_path, fake)

    assert ("clear_checkpoint",) in fake.calls
