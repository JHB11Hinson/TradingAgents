"""Research Manager: turns the bull/bear debate into a structured investment plan for the trader."""

from __future__ import annotations

from tradingagents import prompts
from tradingagents.agents.context import get_instrument_context_from_state, get_language_instruction
from tradingagents.agents.schemas import ResearchPlan, render_research_plan
from tradingagents.agents.structured import (
    bind_structured,
    invoke_structured_or_freetext,
    no_external_tools,
)
from tradingagents.agents.termination import detect_termination
from tradingagents.context import assemble_context, make_layers
from tradingagents.context.agent_layers import (
    constraints_block,
    history_block,
    identity_block,
    resumable_block,
    retrieved_block,
    task_block,
)
from tradingagents.telemetry import span


def create_research_manager(llm, max_turns: int = 2):
    structured_llm = bind_structured(llm, ResearchPlan, "Research Manager")

    def research_manager_node(state) -> dict:
        instrument_context = get_instrument_context_from_state(state)
        history = state["investment_debate_state"].get("history", "")

        investment_debate_state = state["investment_debate_state"]
        count = investment_debate_state["count"]
        existing_reason = state.get("termination_reason", "")
        reason = (
            detect_termination(investment_debate_state.get("turn_digests", []), cycle=2)
            if count < max_turns
            else None
        )
        if reason and not existing_reason:
            # The debate stopped before its configured bound; record why.
            with span(
                "loop.terminated",
                phase="termination",
                kind="termination",
                attributes={"node": "Research Manager", "reason": reason},
            ):
                pass
            termination_reason = reason
        else:
            termination_reason = existing_reason

        role = prompts.load_prompt("manager.research.role").text

        history_text = f"**Debate History:**\n{history}"
        task_text = prompts.load_prompt("manager.research.task").text.format(
            no_external_tools=no_external_tools(),
            language_instruction=get_language_instruction(),
        )

        original = (
            role
            + f"\n\n{instrument_context}\n\n"
            + history_text
            + f"\n\n{task_text}"
        )
        layers = make_layers(
            identity=[identity_block(instrument_context)],
            constraints=[constraints_block(role)],
            retrieved=[
                retrieved_block(
                    "state.investment_debate_state",
                    "Research digest: the bull/bear debate below.",
                    render=False,
                )
            ],
            history=[
                history_block(
                    text=history_text, source="state.investment_debate_state.history"
                )
            ],
            resumable=[resumable_block(state)],
            task=[task_block(task_text)],
        )
        assembled = assemble_context(
            layers, original=original, agent="Research Manager"
        )

        investment_plan = invoke_structured_or_freetext(
            structured_llm,
            llm,
            assembled.text,
            render_research_plan,
            "Research Manager",
        )

        new_investment_debate_state = {
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": investment_plan,
            "count": investment_debate_state["count"],
            "turn_digests": investment_debate_state.get("turn_digests", []),
            "turn_records": investment_debate_state.get("turn_records", []),
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": investment_plan,
            "termination_reason": termination_reason,
        }

    return research_manager_node
