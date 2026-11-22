"""Trader: turns the Research Manager's investment plan into a concrete transaction proposal."""

from __future__ import annotations

from langchain_core.messages import AIMessage

from tradingagents import prompts
from tradingagents.agents.context import (
    get_instrument_context_from_state,
    get_language_instruction,
    get_portfolio_context_from_state,
)
from tradingagents.agents.schemas import TraderProposal, render_trader_proposal
from tradingagents.agents.structured import (
    bind_structured,
    invoke_structured_or_freetext,
    no_external_tools,
)
from tradingagents.context import assemble_context, make_layers
from tradingagents.context.agent_layers import (
    constraints_block,
    history_block,
    identity_block,
    portfolio_block,
    resumable_block,
    retrieved_block,
    task_block,
)


def create_trader(llm):
    structured_llm = bind_structured(llm, TraderProposal, "Trader")

    def trader_node(state):
        company_name = state["company_of_interest"]
        instrument_context = get_instrument_context_from_state(state)
        investment_plan = state["investment_plan"]
        # The research plan digests the debate but loses exact price structure;
        # give the Trader the technical market report so entry/stop levels are
        # grounded in real ATR / support-resistance / current price (#1167). The
        # report is empty when the user did not select the market analyst, so
        # only offer it (and the grounding instruction) when it has content.
        market_report = (state["market_report"] or "").strip()
        portfolio_context = get_portfolio_context_from_state(state)

        if market_report:
            grounding = (
                "Ground concrete price levels (entry, stop-loss, position sizing) in the technical "
                "market report's price structure -- current price, support/resistance, ATR, and "
                "volatility -- and use the research plan for direction and strategy. "
            )
            report_section = f"Technical Market Report:\n{market_report}\n\n"
        else:
            grounding = ""
            report_section = ""

        # Entry/stop are numeric price fields. Asking for concrete levels
        # invites a percentage ("15%"), which is not a price and fails the
        # structured parse (#1288).
        role = prompts.load_prompt("trader.role").text.format(
            grounding=grounding,
            no_external_tools=no_external_tools(),
            language_instruction=get_language_instruction(),
        )
        task_text = prompts.load_prompt("trader.task").text.format(
            company_name=company_name,
            instrument_context=instrument_context,
            report_section=report_section,
            portfolio_context=portfolio_context,
            investment_plan=investment_plan,
        )
        original = role + "\n\n" + task_text

        layers = make_layers(
            identity=[
                identity_block(instrument_context),
                portfolio_block(portfolio_context),
            ],
            constraints=[constraints_block(role)],
            retrieved=[
                retrieved_block(
                    "state.market_report",
                    report_section.strip() or "(No technical market report in this run.)",
                    render=bool(report_section),
                ),
                retrieved_block(
                    "state.investment_plan", f"Proposed Investment Plan:\n{investment_plan}"
                ),
            ],
            history=[
                history_block(state.get("messages", ()), render=False)
            ],
            resumable=[resumable_block(state)],
            task=[task_block(task_text)],
        )
        assembled = assemble_context(layers, original=original, agent="Trader")

        if assembled.compacted:
            messages = [{"role": "system", "content": assembled.text}]
        else:
            messages = [
                {"role": "system", "content": role},
                {"role": "user", "content": task_text},
            ]

        trader_plan = invoke_structured_or_freetext(
            structured_llm,
            llm,
            messages,
            render_trader_proposal,
            "Trader",
        )

        return {
            "messages": [AIMessage(content=trader_plan)],
            "trader_investment_plan": trader_plan,
        }

    return trader_node
