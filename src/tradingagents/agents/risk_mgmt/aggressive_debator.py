from tradingagents.agents.context import (
    get_instrument_context_from_state,
    get_language_instruction,
    get_portfolio_context_from_state,
    opponent_argument_or_opening,
    report_or_absent,
)
from tradingagents.agents.debate import (
    DEBATE_TURN_INSTRUCTION,
    invoke_debate_turn,
    render_debate_turn,
)
from tradingagents.agents.termination import turn_digest
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


def create_aggressive_debator(llm):
    def aggressive_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        aggressive_history = risk_debate_state.get("aggressive_history", "")

        current_conservative_response = opponent_argument_or_opening(
            risk_debate_state.get("current_conservative_response", ""), "conservative analyst"
        )
        current_neutral_response = opponent_argument_or_opening(
            risk_debate_state.get("current_neutral_response", ""), "neutral analyst"
        )

        market_research_report = report_or_absent(state["market_report"], "market")
        sentiment_report = report_or_absent(state["sentiment_report"], "sentiment")
        news_report = report_or_absent(state["news_report"], "news")
        fundamentals_report = report_or_absent(state["fundamentals_report"], "fundamentals")
        instrument_context = get_instrument_context_from_state(state)
        portfolio_context = get_portfolio_context_from_state(state)

        trader_decision = state["trader_investment_plan"]

        role = f"""As the Aggressive Risk Analyst, your role is to actively champion high-reward, high-risk opportunities, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan, focus intently on the potential upside, growth potential, and innovative benefits—even when these come with elevated risk. Use the provided market data and sentiment analysis to strengthen your arguments and challenge the opposing views. Specifically, respond directly to each point made by the conservative and neutral analysts, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might miss critical opportunities or where their assumptions may be overly conservative. Here is the trader's decision:

{trader_decision}

Your task is to create a compelling case for the trader's decision by questioning and critiquing the conservative and neutral stances to demonstrate why your high-reward perspective offers the best path forward. Incorporate insights from the following sources into your arguments:"""

        history_text = (
            f"Here is the current conversation history: {history} Here are the last arguments "
            f"from the conservative analyst: {current_conservative_response} Here are the last "
            f"arguments from the neutral analyst: {current_neutral_response}. If there are no "
            "responses from the other viewpoints yet, present your own argument based on the "
            "available data."
        )
        task_text = (
            "Engage actively by addressing any specific concerns raised, refuting the weaknesses "
            "in their logic, and asserting the benefits of risk-taking to outpace market norms. "
            "Maintain a focus on debating and persuading, not just presenting data. Challenge "
            "each counterpoint to underscore why a high-risk approach is optimal.\n\n"
        ) + DEBATE_TURN_INSTRUCTION + get_language_instruction()

        original = (
            role
            + f"\n\n{instrument_context}\n{portfolio_context}\n"
            f"Market Research Report: {market_research_report}\n"
            f"Social Media Sentiment Report: {sentiment_report}\n"
            f"Latest World Affairs Report: {news_report}\n"
            f"Company Fundamentals Report: {fundamentals_report}\n"
            f"{history_text}\n\n{task_text}"
        )
        layers = make_layers(
            identity=[identity_block(instrument_context), portfolio_block(portfolio_context)],
            constraints=[constraints_block(role)],
            retrieved=[
                retrieved_block(
                    "state.market_report", f"Market Research Report: {market_research_report}"
                ),
                retrieved_block(
                    "state.sentiment_report",
                    f"Social Media Sentiment Report: {sentiment_report}",
                ),
                retrieved_block(
                    "state.news_report", f"Latest World Affairs Report: {news_report}"
                ),
                retrieved_block(
                    "state.fundamentals_report",
                    f"Company Fundamentals Report: {fundamentals_report}",
                ),
            ],
            history=[history_block(text=history_text, source="state.risk_debate_state.history")],
            resumable=[resumable_block(state)],
            task=[task_block(task_text)],
        )
        assembled = assemble_context(
            layers, original=original, agent="Aggressive Analyst"
        )

        opponent = "\n\n".join(
            part
            for part in (
                risk_debate_state.get("current_conservative_response", ""),
                risk_debate_state.get("current_neutral_response", ""),
            )
            if part.strip()
        )
        turn, raw_text = invoke_debate_turn(
            llm, assembled.text, side="Aggressive Analyst", opponent=opponent
        )

        argument = render_debate_turn(turn, "Aggressive Analyst")

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": aggressive_history + "\n" + argument,
            "conservative_history": risk_debate_state.get("conservative_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Aggressive",
            "current_aggressive_response": argument,
            "current_conservative_response": risk_debate_state.get("current_conservative_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
            "turn_digests": [
                *risk_debate_state.get("turn_digests", []),
                turn_digest(raw_text),
            ],
            "turn_records": [
                *risk_debate_state.get("turn_records", []),
                turn.model_dump(),
            ],
        }

        return {"risk_debate_state": new_risk_debate_state}

    return aggressive_node
