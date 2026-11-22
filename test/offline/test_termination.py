"""Termination discipline for both debate loops (D1-REQ-TERM-001).

A pure detector decides whether a debate has oscillated, stalled or run out of
budget. The router checks the configured hard bound first and only then the
detector, so the shipped replay's bound-terminated debates keep
``termination_reason == ""``. The terminal manager records the earliest reason
and emits a safe ``loop.terminated`` span.
"""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage

from tradingagents.agents.managers.portfolio_manager import create_portfolio_manager
from tradingagents.agents.managers.research_manager import create_research_manager
from tradingagents.agents.researchers.bear_researcher import create_bear_researcher
from tradingagents.agents.researchers.bull_researcher import create_bull_researcher
from tradingagents.agents.risk_mgmt.aggressive_debator import create_aggressive_debator
from tradingagents.agents.risk_mgmt.conservative_debator import create_conservative_debator
from tradingagents.agents.risk_mgmt.neutral_debator import create_neutral_debator
from tradingagents.agents.termination import (
    STALL_REPEATS,
    detect_termination,
    turn_digest,
)
from tradingagents.context import run_budget_scope
from tradingagents.graph.conditional_logic import ConditionalLogic
from tradingagents.graph.propagation import Propagator
from tradingagents.telemetry import telemetry_scope


class _FakeLLM:
    """Free text only; every call returns the same report."""

    def __init__(self, text: str = "Rating: Hold") -> None:
        self.text = text
        self.calls = 0

    def bind_tools(self, tools, **kwargs):
        return self

    def with_structured_output(self, schema, **kwargs):
        raise NotImplementedError

    def invoke(self, prompt):
        self.calls += 1
        return AIMessage(content=self.text)


def _investment(count=0, digests=(), current_response="Bull Analyst: a", history=""):
    return {
        "bull_history": "",
        "bear_history": "",
        "history": history,
        "current_response": current_response,
        "count": count,
        "turn_digests": list(digests),
    }


def _risk(count=0, digests=(), latest_speaker="Aggressive", history=""):
    return {
        "aggressive_history": "",
        "conservative_history": "",
        "neutral_history": "",
        "history": history,
        "latest_speaker": latest_speaker,
        "current_aggressive_response": "",
        "current_conservative_response": "",
        "current_neutral_response": "",
        "count": count,
        "turn_digests": list(digests),
    }


def _state(*, investment=None, risk=None, termination_reason=""):
    return {
        "messages": [],
        "company_of_interest": "NVDA",
        "asset_type": "stock",
        "instrument_context": "Instrument: NVDA",
        "trade_date": "2026-01-09",
        "past_context": "",
        "memory_note": "",
        "portfolio_context": "",
        "market_report": "M",
        "sentiment_report": "S",
        "news_report": "N",
        "fundamentals_report": "F",
        "investment_plan": "P",
        "trader_investment_plan": "T",
        "final_trade_decision": "",
        "final_rating": "",
        "termination_reason": termination_reason,
        "investment_debate_state": investment or _investment(),
        "risk_debate_state": risk or _risk(),
    }


def _digests(text: str) -> list[str]:
    return [turn_digest(ch) for ch in text]


# --- the pure detector -----------------------------------------------------------


@pytest.mark.unit
def test_investment_oscillation_is_period_two():
    assert detect_termination(_digests("abab"), cycle=2) == "oscillation"


@pytest.mark.unit
def test_risk_oscillation_is_period_three():
    assert detect_termination(_digests("abcabc"), cycle=3) == "oscillation"


@pytest.mark.unit
def test_a_one_digest_cycle_is_not_oscillation():
    """Four identical turns are a stall, never a two-turn 'cycle'."""
    assert detect_termination(_digests("aaaa"), cycle=2) == "stall"


@pytest.mark.unit
def test_stall_is_three_identical_turns():
    assert STALL_REPEATS == 3
    assert detect_termination(_digests("aaa"), cycle=2) == "stall"


@pytest.mark.unit
def test_progress_is_not_termination():
    assert detect_termination(_digests("abcd"), cycle=2) is None
    assert detect_termination(_digests("abcde"), cycle=3) is None


@pytest.mark.unit
def test_budget_exhaustion_is_detected_first():
    with run_budget_scope(
        {"context_budget_tokens": 10, "context_call_budget_tokens": 10}
    ) as budget:
        budget.record("analyst", 10, False)
        assert detect_termination(_digests("abab"), cycle=2) == "budget_exhausted"


@pytest.mark.unit
def test_no_budget_scope_is_silent():
    assert detect_termination([turn_digest("a")], cycle=2) is None


@pytest.mark.unit
def test_turn_digest_ignores_speaker_labels_and_whitespace():
    assert turn_digest(" Hello   WORLD ") == turn_digest("hello world")
    digest = turn_digest("hello world")
    assert len(digest) == 16 and all(ch in "0123456789abcdef" for ch in digest)


# --- the router ------------------------------------------------------------------


@pytest.mark.unit
def test_oscillating_investment_debate_routes_to_the_manager_before_the_bound():
    logic = ConditionalLogic(max_debate_rounds=3)
    state = _state(investment=_investment(count=4, digests=_digests("abab")))

    assert logic.should_continue_debate(state) == "Research Manager"


@pytest.mark.unit
def test_a_normal_investment_debate_keeps_alternating():
    logic = ConditionalLogic(max_debate_rounds=3)
    state = _state(
        investment=_investment(
            count=2, digests=_digests("ab"), current_response="Bull Analyst: a"
        )
    )

    assert logic.should_continue_debate(state) == "Bear Researcher"


@pytest.mark.unit
@pytest.mark.parametrize("rounds", [1, 2, 3])
def test_the_debate_ends_exactly_at_2n_turns(rounds):
    """D1-REQ-DEBATE-004: with max_debate_rounds=N the debate ends at 2*N turns.

    ``max_debate_rounds`` is one turn each for bull and bear, so the router must
    keep alternating while ``count < 2*N`` and route to the manager at exactly
    ``count == 2*N``. The digests advance (no oscillation) so this isolates the
    configured bound from the termination detector.
    """
    logic = ConditionalLogic(max_debate_rounds=rounds)
    bound = 2 * rounds
    under = _state(investment=_investment(count=bound - 1, digests=_digests("abcdefghij"[:bound - 1])))
    at = _state(investment=_investment(count=bound, digests=_digests("abcdefghij"[:bound])))

    assert logic.should_continue_debate(under) in ("Bull Researcher", "Bear Researcher")
    assert logic.should_continue_debate(at) == "Research Manager"


@pytest.mark.unit
def test_an_oscillating_risk_debate_routes_to_the_portfolio_manager():
    logic = ConditionalLogic(max_risk_discuss_rounds=3)
    state = _state(
        risk=_risk(count=6, digests=_digests("abcabc"), latest_speaker="Neutral")
    )

    assert logic.should_continue_risk_analysis(state) == "Portfolio Manager"


@pytest.mark.unit
def test_a_normal_period_three_risk_debate_is_not_flagged():
    logic = ConditionalLogic(max_risk_discuss_rounds=3)
    state = _state(
        risk=_risk(count=6, digests=_digests("abcdef"), latest_speaker="Neutral")
    )

    assert logic.should_continue_risk_analysis(state) == "Aggressive Analyst"


@pytest.mark.unit
def test_the_hard_bound_wins_over_a_repeated_turn():
    logic = ConditionalLogic(max_risk_discuss_rounds=1)
    state = _state(
        risk=_risk(count=3, digests=_digests("aaa"), latest_speaker="Neutral")
    )

    assert logic.should_continue_risk_analysis(state) == "Portfolio Manager"


@pytest.mark.unit
def test_the_router_routes_budget_exhaustion_to_the_manager():
    logic = ConditionalLogic(max_debate_rounds=3)
    state = _state(investment=_investment(count=2, digests=_digests("ab")))
    with run_budget_scope({"context_budget_tokens": 10, "context_call_budget_tokens": 10}) as budget:
        budget.record("analyst", 10, False)
        assert logic.should_continue_debate(state) == "Research Manager"


@pytest.mark.unit
def test_removing_the_detector_runs_to_the_bound(monkeypatch):
    """Negative test: the router case exercises the detector, not the bound."""
    import tradingagents.graph.conditional_logic as conditional_logic

    monkeypatch.setattr(conditional_logic, "detect_termination", lambda *a, **k: None)
    logic = conditional_logic.ConditionalLogic(max_debate_rounds=3)
    state = _state(investment=_investment(count=4, digests=_digests("abab")))

    assert logic.should_continue_debate(state) == "Bear Researcher"


# --- the five debate nodes record one digest per turn ----------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("factory", "debate_key"),
    [
        (create_bull_researcher, "investment_debate_state"),
        (create_bear_researcher, "investment_debate_state"),
        (create_aggressive_debator, "risk_debate_state"),
        (create_conservative_debator, "risk_debate_state"),
        (create_neutral_debator, "risk_debate_state"),
    ],
)
def test_each_debate_node_appends_one_digest(factory, debate_key):
    node = factory(_FakeLLM())
    state = _state()

    result = node(state)

    debate = result[debate_key]
    assert debate["turn_digests"] == [turn_digest("Rating: Hold")]
    assert debate["count"] == 1


@pytest.mark.unit
def test_the_initial_state_has_empty_digest_lists():
    state = Propagator().create_initial_state("NVDA", "2026-01-09")

    assert state["investment_debate_state"]["turn_digests"] == []
    assert state["risk_debate_state"]["turn_digests"] == []


# --- the terminal managers -------------------------------------------------------


@pytest.mark.unit
def test_research_manager_records_oscillation():
    node = create_research_manager(_FakeLLM(), max_turns=6)
    state = _state(investment=_investment(count=4, digests=_digests("abab")))

    assert node(state)["termination_reason"] == "oscillation"


@pytest.mark.unit
def test_research_manager_at_the_bound_sets_no_reason():
    node = create_research_manager(_FakeLLM(), max_turns=4)
    state = _state(investment=_investment(count=4, digests=_digests("abab")))

    assert node(state)["termination_reason"] == ""


@pytest.mark.unit
def test_research_manager_keeps_an_existing_reason():
    node = create_research_manager(_FakeLLM(), max_turns=9)
    state = _state(
        investment=_investment(count=4, digests=_digests("abab")),
        termination_reason="stall",
    )

    assert node(state)["termination_reason"] == "stall"


@pytest.mark.unit
def test_portfolio_manager_records_its_own_detector_reason():
    node = create_portfolio_manager(_FakeLLM(), max_turns=9)
    state = _state(risk=_risk(count=6, digests=_digests("abcabc")))

    assert node(state)["termination_reason"] == "oscillation"


@pytest.mark.unit
def test_portfolio_manager_keeps_an_existing_reason():
    node = create_portfolio_manager(_FakeLLM(), max_turns=9)
    state = _state(
        risk=_risk(count=6, digests=_digests("abcabc")),
        termination_reason="oscillation",
    )

    assert node(state)["termination_reason"] == "oscillation"


@pytest.mark.unit
def test_the_portfolio_manager_budget_catch_overrides_the_existing_reason():
    node = create_portfolio_manager(_FakeLLM(), max_turns=9)
    state = _state(
        risk=_risk(count=6, digests=_digests("abcabc")),
        termination_reason="oscillation",
    )
    with run_budget_scope(
        {"context_budget_tokens": 1, "context_call_budget_tokens": 1}
    ):
        assert node(state)["termination_reason"] == "budget_exhausted"


@pytest.mark.unit
def test_termination_emits_a_safe_span():
    with telemetry_scope({}) as hub:
        create_research_manager(_FakeLLM(), max_turns=6)(
            _state(investment=_investment(count=4, digests=_digests("abab")))
        )

    event = next(e for e in hub.events if e.name == "loop.terminated")
    assert event.as_dict()["attributes"] == {
        "node": "Research Manager",
        "reason": "oscillation",
    }
