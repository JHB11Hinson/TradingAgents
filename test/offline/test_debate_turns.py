"""Structured debate turns (D1-REQ-DEBATE-001, D1-REQ-DEBATE-002).

Every debate turn is a :class:`DebateTurn`: claim, evidence, rebuttal,
confidence, diverge and converge.  A provider with native structured output
returns the object directly; a prose-only provider is adapted deterministically
so the debate never stalls.  Both debate states keep one ``turn_records`` entry
per turn, while ``turn_digests`` still covers the raw text for termination.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage
from pydantic import ValidationError

from tradingagents.agents.debate import (
    DebateTurnError,
    invoke_debate_turn,
    parse_debate_turn,
    render_debate_turn,
)
from tradingagents.agents.managers.portfolio_manager import create_portfolio_manager
from tradingagents.agents.managers.research_manager import create_research_manager
from tradingagents.agents.researchers.bear_researcher import create_bear_researcher
from tradingagents.agents.researchers.bull_researcher import create_bull_researcher
from tradingagents.agents.risk_mgmt.aggressive_debator import create_aggressive_debator
from tradingagents.agents.risk_mgmt.conservative_debator import create_conservative_debator
from tradingagents.agents.risk_mgmt.neutral_debator import create_neutral_debator
from tradingagents.agents.schemas import DebateEvidence, DebateTurn
from tradingagents.agents.termination import turn_digest
from tradingagents.graph.propagation import Propagator

SECTION_LABELS = ("Claim", "Evidence", "Rebuttal", "Confidence", "Diverge", "Converge")


def _turn(**over):
    base = {
        "claim": "growth is intact",
        "evidence": [DebateEvidence(source="earnings", quote="revenue grew 20%")],
        "rebuttal": "valuation is not stretched",
        "confidence": "high",
        "diverge": "growth versus valuation",
        "converge": "the growth case wins",
    }
    base.update(over)
    return DebateTurn(**base)


def _json_turn() -> str:
    return json.dumps(_turn().model_dump())


class _FakeLLM:
    """Prose/JSON test provider: no native structured output."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.calls = 0

    def with_structured_output(self, schema):
        raise NotImplementedError("provider has no structured output")

    def invoke(self, prompt):
        self.calls += 1
        return AIMessage(content=self.text)


# ---------------------------------------------------------------------------
# D1-REQ-DEBATE-001: the schema
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("claim", ""),
        ("claim", "   "),
        ("rebuttal", ""),
        ("confidence", ""),
        ("diverge", ""),
        ("converge", ""),
    ],
)
def test_a_turn_rejects_an_empty_required_field(field, value):
    """D1-REQ-DEBATE-001: every required field is non-empty."""
    with pytest.raises(ValidationError):
        _turn(**{field: value})


@pytest.mark.unit
@pytest.mark.parametrize(
    "missing", ["claim", "evidence", "rebuttal", "confidence", "diverge", "converge"]
)
def test_a_turn_rejects_a_missing_required_field(missing):
    """D1-REQ-DEBATE-001: a missing field is not silently defaulted."""
    payload = _turn().model_dump()
    payload.pop(missing)
    with pytest.raises(ValidationError):
        DebateTurn.model_validate(payload)


@pytest.mark.unit
def test_a_turn_rejects_empty_evidence():
    """D1-REQ-DEBATE-001: at least one evidence item is required."""
    with pytest.raises(ValidationError):
        _turn(evidence=[])


@pytest.mark.unit
@pytest.mark.parametrize(("source", "quote"), [("", "q"), ("s", ""), ("  ", "q")])
def test_evidence_fields_are_non_empty(source, quote):
    """D1-REQ-DEBATE-001: evidence carries a real source and quote."""
    with pytest.raises(ValidationError):
        DebateEvidence(source=source, quote=quote)


@pytest.mark.unit
def test_confidence_is_limited_to_low_medium_high():
    """D1-REQ-DEBATE-001: confidence is a closed three-value scale."""
    with pytest.raises(ValidationError):
        _turn(confidence="certain")


@pytest.mark.unit
def test_a_json_turn_with_empty_convergence_is_rejected():
    """D1-REQ-DEBATE-002: explicit convergence is mandatory, not optional."""
    payload = _turn().model_dump()
    payload["converge"] = ""
    with pytest.raises(ValidationError):
        DebateTurn.model_validate_json(json.dumps(payload))


@pytest.mark.unit
def test_an_invalid_json_turn_aborts_instead_of_becoming_prose():
    """D1-REQ-DEBATE-002: a malformed JSON turn fails validation; prose adaptation
    is only for answers that never claimed to be JSON."""
    payload = _turn().model_dump()
    payload["converge"] = ""
    with pytest.raises(DebateTurnError):
        parse_debate_turn(json.dumps(payload), side="Bull Analyst")


# ---------------------------------------------------------------------------
# Rendering and the deterministic adapter
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_a_valid_turn_renders_all_six_sections_with_the_speaker():
    """D1-REQ-DEBATE-001: the rendered turn is complete and attributed."""
    text = render_debate_turn(_turn(), "Bull Analyst")
    assert text.startswith("Bull Analyst")
    for label in SECTION_LABELS:
        assert f"**{label}**" in text
    assert "revenue grew 20%" in text


@pytest.mark.unit
def test_a_prose_turn_is_adapted_into_a_valid_turn():
    """D1-REQ-DEBATE-002: a legacy provider still produces a valid turn."""
    text = "Bull Analyst: growth is intact"
    turn = parse_debate_turn(text, side="Bull Analyst")

    assert turn.claim == text
    assert turn.evidence and turn.evidence[0].quote == text
    assert turn.rebuttal == "no opponent spoke"
    assert turn.confidence in {"low", "medium", "high"}
    assert turn.diverge == text
    assert turn.converge


@pytest.mark.unit
def test_a_prose_turn_uses_the_opponent_as_its_rebuttal():
    """D1-REQ-DEBATE-002: the adapter records the actual opposing case."""
    turn = parse_debate_turn(
        "growth is intact",
        side="Bull Analyst",
        opponent="Bear Analyst: valuation is stretched",
    )
    assert turn.rebuttal == "Bear Analyst: valuation is stretched"


@pytest.mark.unit
def test_empty_prose_still_yields_no_empty_field():
    """D1-REQ-DEBATE-002: the adapter never returns an invalid turn."""
    turn = parse_debate_turn("   ", side="Bull Analyst")
    assert all(
        [turn.claim, turn.evidence, turn.rebuttal, turn.confidence, turn.diverge, turn.converge]
    )


@pytest.mark.unit
def test_a_json_turn_is_parsed():
    """D1-REQ-DEBATE-001: a JSON object is read as the schema, not prose."""
    turn = parse_debate_turn(_json_turn(), side="Bull Analyst")

    assert turn.claim == "growth is intact"
    assert turn.confidence == "high"
    assert turn.evidence[0].source == "earnings"
    assert turn.converge == "the growth case wins"


@pytest.mark.unit
def test_a_fenced_json_turn_is_parsed():
    """D1-REQ-DEBATE-001: a fenced JSON block is accepted."""
    text = f"Here is my turn:\n```json\n{_json_turn()}\n```\n"
    turn = parse_debate_turn(text, side="Bull Analyst")
    assert turn.claim == "growth is intact"


@pytest.mark.unit
def test_invoke_uses_a_native_structured_turn_when_it_is_a_debate_turn():
    """D1-REQ-DEBATE-001: a real structured result is not re-parsed."""
    expected = _turn()
    structured = MagicMock()
    structured.invoke.return_value = expected
    llm = MagicMock()
    llm.with_structured_output.return_value = structured

    turn, raw = invoke_debate_turn(llm, "prompt", side="Bull Analyst")

    assert turn is expected
    assert raw
    llm.invoke.assert_not_called()


@pytest.mark.unit
def test_invoke_falls_back_when_structured_output_is_not_a_debate_turn():
    """D1-REQ-DEBATE-001: a mock/unparsed structured result falls back."""
    structured = MagicMock()
    structured.invoke.return_value = MagicMock()
    llm = MagicMock()
    llm.with_structured_output.return_value = structured
    llm.invoke.return_value = AIMessage(content=_json_turn())

    turn, raw = invoke_debate_turn(llm, "prompt", side="Bull Analyst")

    assert isinstance(turn, DebateTurn)
    assert raw == _json_turn()
    llm.invoke.assert_called_once()


# ---------------------------------------------------------------------------
# D1-REQ-DEBATE-002: wiring the five debate nodes
# ---------------------------------------------------------------------------

_DEBATORS = [
    (create_bull_researcher, "investment_debate_state", "Bull Analyst"),
    (create_bear_researcher, "investment_debate_state", "Bear Analyst"),
    (create_aggressive_debator, "risk_debate_state", "Aggressive Analyst"),
    (create_conservative_debator, "risk_debate_state", "Conservative Analyst"),
    (create_neutral_debator, "risk_debate_state", "Neutral Analyst"),
]

_REPORTS = {
    "company_of_interest": "NVDA",
    "asset_type": "stock",
    "market_report": "market",
    "sentiment_report": "sentiment",
    "news_report": "news",
    "fundamentals_report": "fundamentals",
}


def _investment_state():
    return {
        **_REPORTS,
        "investment_debate_state": {
            "bull_history": "",
            "bear_history": "",
            "history": "",
            "current_response": "",
            "count": 0,
            "turn_digests": [],
            "turn_records": [],
        },
    }


def _risk_state():
    return {
        **_REPORTS,
        "trader_investment_plan": "plan",
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
            "turn_digests": [],
            "turn_records": [],
        },
    }


@pytest.mark.unit
@pytest.mark.parametrize(("factory", "debate_key", "speaker"), _DEBATORS)
def test_each_debate_node_appends_one_record_and_one_digest(factory, debate_key, speaker):
    """D1-REQ-DEBATE-002: one structured record and one digest per turn."""
    raw = _json_turn()
    state = _investment_state() if debate_key == "investment_debate_state" else _risk_state()

    debate = factory(_FakeLLM(raw))(state)[debate_key]

    assert len(debate["turn_records"]) == 1
    assert debate["turn_digests"] == [turn_digest(raw)]
    record = debate["turn_records"][0]
    assert set(record) == {
        "claim",
        "evidence",
        "rebuttal",
        "confidence",
        "diverge",
        "converge",
    }
    assert all(record[field] for field in record)
    assert debate["history"].lstrip().startswith(f"{speaker}:")
    for label in SECTION_LABELS:
        assert f"**{label}**" in debate["history"]


@pytest.mark.unit
@pytest.mark.parametrize(("factory", "debate_key", "speaker"), _DEBATORS)
def test_a_prose_only_provider_still_appends_one_record(factory, debate_key, speaker):
    """D1-REQ-DEBATE-002: legacy prose keeps the debate moving."""
    raw = "Rating: Hold"
    state = _investment_state() if debate_key == "investment_debate_state" else _risk_state()

    debate = factory(_FakeLLM(raw))(state)[debate_key]

    assert len(debate["turn_records"]) == 1
    assert debate["turn_digests"] == [turn_digest(raw)]
    assert debate["turn_records"][0]["claim"] == raw
    assert debate["history"].lstrip().startswith(f"{speaker}:")


@pytest.mark.unit
def test_initial_state_has_empty_turn_records():
    """D1-REQ-DEBATE-002: both debates start with no records."""
    state = Propagator().create_initial_state("NVDA", "2026-01-09")

    assert state["investment_debate_state"]["turn_records"] == []
    assert state["risk_debate_state"]["turn_records"] == []


@pytest.mark.unit
def test_research_manager_preserves_turn_records():
    """D1-REQ-DEBATE-002: the manager copies records on to the next state."""
    records = [{"claim": "c", "evidence": [], "rebuttal": "r",
                "confidence": "low", "diverge": "d", "converge": "v"}]
    state = {
        "company_of_interest": "NVDA",
        "instrument_context": "Instrument: NVDA",
        "investment_debate_state": {
            "history": "history",
            "bull_history": "",
            "bear_history": "",
            "current_response": "",
            "count": 0,
            "turn_digests": [],
            "turn_records": records,
        },
    }

    result = create_research_manager(_FakeLLM(_json_turn()))(state)

    assert result["investment_debate_state"]["turn_records"] == records


@pytest.mark.unit
def test_portfolio_manager_preserves_turn_records():
    """D1-REQ-DEBATE-002: the risk records survive the terminal manager."""
    records = [{"claim": "c", "evidence": [], "rebuttal": "r",
                "confidence": "low", "diverge": "d", "converge": "v"}]
    state = {
        "company_of_interest": "NVDA",
        "instrument_context": "Instrument: NVDA",
        "portfolio_context": "",
        "past_context": "",
        "investment_plan": "plan",
        "trader_investment_plan": "trader plan",
        "risk_debate_state": {
            "aggressive_history": "",
            "conservative_history": "",
            "neutral_history": "",
            "history": "risk history",
            "latest_speaker": "Neutral",
            "current_aggressive_response": "",
            "current_conservative_response": "",
            "current_neutral_response": "",
            "count": 0,
            "turn_digests": [],
            "turn_records": records,
        },
    }

    result = create_portfolio_manager(_FakeLLM(_json_turn()))(state)

    assert result["risk_debate_state"]["turn_records"] == records
