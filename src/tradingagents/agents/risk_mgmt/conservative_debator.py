from tradingagents.agents.context import (
    get_instrument_context_from_state,
    get_language_instruction,
    get_portfolio_context_from_state,
    opponent_argument_or_opening,
    report_or_absent,
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


def create_conservative_debator(llm):
    def conservative_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        conservative_history = risk_debate_state.get("conservative_history", "")

        current_aggressive_response = opponent_argument_or_opening(
            risk_debate_state.get("current_aggressive_response", ""), "aggressive analyst"
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

        role = f"""As the Conservative Risk Analyst, your primary objective is to protect assets, minimize volatility, and ensure steady, reliable growth. You prioritize stability, security, and risk mitigation, carefully assessing potential losses, economic downturns, and market volatility. When evaluating the trader's decision or plan, critically examine high-risk elements, pointing out where the decision may expose the firm to undue risk and where more cautious alternatives could secure long-term gains. Here is the trader's decision:

{trader_decision}

Your task is to actively counter the arguments of the Aggressive and Neutral Analysts, highlighting where their views may overlook potential threats or fail to prioritize sustainability. Respond directly to their points, drawing from the following data sources to build a convincing case for a low-risk approach adjustment to the trader's decision:"""

        history_text = (
            f"Here is the current conversation history: {history} Here is the last response from "
            f"the aggressive analyst: {current_aggressive_response} Here is the last response "
            f"from the neutral analyst: {current_neutral_response}. If there are no responses "
            "from the other viewpoints yet, present your own argument based on the available data."
        )
        task_text = (
            "Engage by questioning their optimism and emphasizing the potential downsides they "
            "may have overlooked. Address each of their counterpoints to showcase why a "
            "conservative stance is ultimately the safest path for the firm's assets. Focus on "
            "debating and critiquing their arguments to demonstrate the strength of a low-risk "
            "strategy over their approaches. Output conversationally as if you are speaking "
            "without any special formatting."
        ) + get_language_instruction()

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
            layers, original=original, agent="Conservative Analyst"
        )

        response = llm.invoke(assembled.text)

        argument = f"Conservative Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "aggressive_history": risk_debate_state.get("aggressive_history", ""),
            "conservative_history": conservative_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Conservative",
            "current_aggressive_response": risk_debate_state.get(
                "current_aggressive_response", ""
            ),
            "current_conservative_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return conservative_node
