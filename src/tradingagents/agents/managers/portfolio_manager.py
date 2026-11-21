"""Portfolio Manager: synthesises the risk-analyst debate into the final decision.

Uses LangChain's ``with_structured_output`` so the LLM produces a typed
``PortfolioDecision`` directly, in a single call. Its rating is the run's
``final_rating``, and the decision is rendered to markdown as
``final_trade_decision`` for the memory log, CLI display and saved reports.
When a provider does not expose structured output, the agent falls back to
free-text generation and the rating is read from that text.
"""

from __future__ import annotations

import logging

from tradingagents.agents.context import (
    get_instrument_context_from_state,
    get_language_instruction,
    get_portfolio_context_from_state,
)
from tradingagents.agents.schemas import PortfolioDecision, render_pm_decision
from tradingagents.agents.structured import NO_EXTERNAL_TOOLS, bind_structured, invoke_structured
from tradingagents.agents.termination import detect_termination
from tradingagents.context import (
    ContextBudgetExceeded,
    assemble_context,
    make_layers,
)
from tradingagents.context.agent_layers import (
    constraints_block,
    history_block,
    identity_block,
    portfolio_block,
    resumable_block,
    retrieved_block,
    task_block,
)
from tradingagents.guardrails.decisions import review_decision, validate_free_text_decision
from tradingagents.guardrails.positions import (
    DEFAULT_MAX_POSITION_PCT,
    clip_free_text_decision,
    enforce_position_ceiling,
)
from tradingagents.telemetry import span

logger = logging.getLogger(__name__)


def create_portfolio_manager(
    llm, max_turns: int = 3, max_position_pct: float = DEFAULT_MAX_POSITION_PCT
):
    structured_llm = bind_structured(llm, PortfolioDecision, "Portfolio Manager")

    def portfolio_manager_node(state) -> dict:
        instrument_context = get_instrument_context_from_state(state)
        portfolio_context = get_portfolio_context_from_state(state)

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        research_plan = state["investment_plan"]
        trader_plan = state["trader_investment_plan"]
        count = risk_debate_state["count"]
        existing_reason = state.get("termination_reason", "")
        reason = (
            detect_termination(risk_debate_state.get("turn_digests", []), cycle=3)
            if count < max_turns
            else None
        )
        if reason and not existing_reason:
            # The debate stopped before its bound; keep the earliest reason.
            with span(
                "loop.terminated",
                phase="termination",
                kind="termination",
                attributes={"node": "Portfolio Manager", "reason": reason},
            ):
                pass
            termination_reason = reason
        else:
            termination_reason = existing_reason

        new_risk_debate_state = {
            "history": risk_debate_state["history"],
            "aggressive_history": risk_debate_state["aggressive_history"],
            "conservative_history": risk_debate_state["conservative_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_aggressive_response": risk_debate_state["current_aggressive_response"],
            "current_conservative_response": risk_debate_state["current_conservative_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
            "turn_digests": risk_debate_state.get("turn_digests", []),
            "turn_records": risk_debate_state.get("turn_records", []),
        }

        past_context = state.get("past_context", "")
        lessons_line = (
            f"- Lessons from prior decisions and outcomes:\n{past_context}\n"
            if past_context
            else ""
        )

        role = """As the Portfolio Manager, synthesize the risk analysts' debate and deliver the final trading decision.

---

**Rating Scale** (use exactly one):
- **Buy**: Strong conviction to enter or add to position
- **Overweight**: Favorable outlook, gradually increase exposure
- **Hold**: Maintain current position, no action needed
- **Underweight**: Reduce exposure, take partial profits
- **Sell**: Exit position or avoid entry

---

Ground every conclusion in specific evidence from the analysts. The risk debate always contains conflicting stances; deciding which is stronger is the job, so conflict alone is not a reason to Hold. Commit to the stronger case, sized by how decisively it wins. Choose Hold only when the evidence is still balanced after that weighing, or too thin to support a call; do not force a direction to appear decisive. Weigh the analysts on their merits, independent of speaking order."""

        task_text = (
            "## Output\n\n"
            "Write these sections, in this order, starting with the rating on its own line:\n\n"
            "- **Rating**: exactly one of Buy / Overweight / Hold / Underweight / Sell\n"
            "- **Executive Summary**: the call and how to act on it\n"
            "- **Investment Thesis**: the evidence that decided it, and what would change it\n\n"
            + NO_EXTERNAL_TOOLS
            + get_language_instruction()
        )

        original = (
            role
            + f"\n\n{instrument_context}\n\n{portfolio_context}\n\n"
            + f"**Context:**\n"
            f"- Research Manager's investment plan: **{research_plan}**\n"
            f"- Trader's transaction proposal: **{trader_plan}**\n"
            f"{lessons_line}\n"
            f"**Risk Analysts Debate History:**\n{history}\n\n"
            + task_text
        )
        layers = make_layers(
            identity=[identity_block(instrument_context), portfolio_block(portfolio_context)],
            constraints=[constraints_block(role)],
            retrieved=[
                retrieved_block(
                    "state.investment_plan",
                    f"Research Manager's investment plan: {research_plan}",
                ),
                retrieved_block(
                    "state.trader_investment_plan",
                    f"Trader's transaction proposal: {trader_plan}",
                ),
                retrieved_block(
                    "state.past_context",
                    lessons_line.strip() or "(No prior lessons in this run.)",
                    render=bool(lessons_line),
                ),
            ],
            history=[
                history_block(text=history, source="state.risk_debate_state.history")
            ],
            resumable=[resumable_block(state)],
            task=[task_block(task_text)],
        )

        try:
            assembled = assemble_context(
                layers, original=original, agent="Portfolio Manager", use_reserve=True
            )
        except ContextBudgetExceeded as exc:
            # SAFE-002: the decision is deterministic and authoritative; without
            # its full constraints no tradeable rating may be emitted.
            logger.warning("Portfolio Manager call aborted: %s", exc)
            return {
                "risk_debate_state": new_risk_debate_state,
                "final_trade_decision": (
                    "Rating: REVIEW\n\nThe context budget was exhausted before the "
                    "Portfolio Manager could see the full risk debate; no tradeable "
                    "decision was produced."
                ),
                "final_rating": "REVIEW",
                "final_decision_source": "review",
                "termination_reason": "budget_exhausted",
            }

        # The typed rating is the decision; the rendered text only carries it.
        # Read back from text, a rating the thesis quotes could replace it.
        decision = invoke_structured(structured_llm, assembled.text, "Portfolio Manager")
        if decision is not None:
            decision, ceiling_warning = enforce_position_ceiling(decision, max_position_pct)
            if ceiling_warning:
                logger.warning("Portfolio Manager: %s", ceiling_warning)
            final_trade_decision = render_pm_decision(decision)
            final_rating = decision.rating.value
            final_decision_source = "structured"
        else:
            # SAFE-002: prose is not a schema-validated decision. Accept it only
            # when it carries one explicit rating; otherwise degrade to REVIEW.
            free_text = llm.invoke(assembled.text).content
            rating = validate_free_text_decision(free_text)
            if rating is None:
                final_trade_decision = review_decision(
                    "the free-text answer had no single explicit rating"
                )
                final_rating = "REVIEW"
                final_decision_source = "review"
            else:
                final_trade_decision, ceiling_warning = clip_free_text_decision(
                    free_text, max_position_pct
                )
                if ceiling_warning:
                    logger.warning("Portfolio Manager: %s", ceiling_warning)
                final_rating = rating
                final_decision_source = "free_text"

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": final_trade_decision,
            "final_rating": final_rating,
            "final_decision_source": final_decision_source,
            "termination_reason": termination_reason,
        }

    return portfolio_manager_node
