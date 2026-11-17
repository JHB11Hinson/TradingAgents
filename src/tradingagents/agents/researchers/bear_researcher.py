from tradingagents.agents.context import (
    get_instrument_context_from_state,
    get_language_instruction,
    opponent_argument_or_opening,
    report_or_absent,
)
from tradingagents.context import assemble_context, make_layers
from tradingagents.context.agent_layers import (
    constraints_block,
    history_block,
    identity_block,
    resumable_block,
    retrieved_block,
    task_block,
)


def create_bear_researcher(llm):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = opponent_argument_or_opening(
            investment_debate_state.get("current_response", ""), "bull analyst"
        )
        market_research_report = report_or_absent(state["market_report"], "market")
        sentiment_report = report_or_absent(state["sentiment_report"], "sentiment")
        news_report = report_or_absent(state["news_report"], "news")
        fundamentals_report = report_or_absent(state["fundamentals_report"], "fundamentals")
        instrument_context = get_instrument_context_from_state(state)
        asset_type = state.get("asset_type", "stock")
        target_label = "stock" if asset_type == "stock" else "asset"
        fundamentals_label = (
            "Company fundamentals report"
            if asset_type == "stock"
            else "Asset fundamentals report (may be unavailable for crypto)"
        )

        role = f"""You are a Bear Analyst making the case against investing in the {target_label}. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:

- Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
- Negative Indicators: Use evidence from financial data, market trends, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts."""

        history_text = (
            f"Conversation history of the debate: {history}\n"
            f"Last bull argument: {current_response}"
        )
        task_text = (
            f"Use this information to deliver a compelling bear argument, refute the bull's "
            f"claims, and engage in a dynamic debate that demonstrates the risks and weaknesses "
            f"of investing in the {target_label}."
        ) + get_language_instruction()

        original = (
            role
            + f"\n\nResources available:\n\n{instrument_context}\n"
            f"Market research report: {market_research_report}\n"
            f"Social media sentiment report: {sentiment_report}\n"
            f"Latest world affairs news: {news_report}\n"
            f"{fundamentals_label}: {fundamentals_report}\n"
            f"{history_text}\n"
            f"{task_text}"
        )
        layers = make_layers(
            identity=[identity_block(instrument_context)],
            constraints=[constraints_block(role)],
            retrieved=[
                retrieved_block(
                    "state.market_report", f"Market research report: {market_research_report}"
                ),
                retrieved_block(
                    "state.sentiment_report", f"Social media sentiment report: {sentiment_report}"
                ),
                retrieved_block(
                    "state.news_report", f"Latest world affairs news: {news_report}"
                ),
                retrieved_block(
                    "state.fundamentals_report",
                    f"{fundamentals_label}: {fundamentals_report}",
                ),
            ],
            history=[history_block(text=history_text, source="state.investment_debate_state.history")],
            resumable=[resumable_block(state)],
            task=[task_block(task_text)],
        )
        assembled = assemble_context(layers, original=original, agent="Bear Researcher")

        response = llm.invoke(assembled.text)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
