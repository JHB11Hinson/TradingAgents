from tradingagents.agents.context import (
    get_instrument_context_from_state,
    get_language_instruction,
    opponent_argument_or_opening,
    report_or_absent,
)
from tradingagents.agents.termination import turn_digest
from tradingagents.context import assemble_context, make_layers
from tradingagents.context.agent_layers import (
    constraints_block,
    history_block,
    identity_block,
    resumable_block,
    retrieved_block,
    task_block,
)


def create_bull_researcher(llm):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = opponent_argument_or_opening(
            investment_debate_state.get("current_response", ""), "bear analyst"
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

        role = f"""You are a Bull Analyst advocating for investing in the {target_label}. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the company's market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong branding, or dominant market positioning.
- Positive Indicators: Use financial health, industry trends, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data."""

        history_text = (
            f"Conversation history of the debate: {history}\n"
            f"Last bear argument: {current_response}"
        )
        task_text = """Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position.
""" + get_language_instruction()

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
        assembled = assemble_context(layers, original=original, agent="Bull Researcher")

        response = llm.invoke(assembled.text)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
            "turn_digests": [
                *investment_debate_state.get("turn_digests", []),
                turn_digest(response.content),
            ],
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
