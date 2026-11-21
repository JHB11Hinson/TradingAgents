import json
import logging
from collections import Counter
from typing import Any, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from tradingagents.agents import (
    create_aggressive_debator,
    create_bear_researcher,
    create_bull_researcher,
    create_conservative_debator,
    create_fundamentals_analyst,
    create_market_analyst,
    create_neutral_debator,
    create_news_analyst,
    create_portfolio_manager,
    create_research_manager,
    create_sentiment_analyst,
    create_trader,
)
from tradingagents.agents.analysts.turn import WRAP_UP
from tradingagents.agents.state import AgentState
from tradingagents.telemetry import span

from .analyst_execution import build_analyst_execution_plan
from .conditional_logic import ConditionalLogic

logger = logging.getLogger(__name__)

# Every target a shared conditional router can return. Each edge driven by the
# router maps all of them, so a fall-through return (e.g. under prompt/i18n/
# refactor drift in the speaker labels) can never hit a missing path_map entry
# and crash LangGraph mid-run (#1088).
DEBATE_PATH_MAP = {
    "Bull Researcher": "Bull Researcher",
    "Bear Researcher": "Bear Researcher",
    "Research Manager": "Research Manager",
}
RISK_ANALYSIS_PATH_MAP = {
    "Aggressive Analyst": "Aggressive Analyst",
    "Conservative Analyst": "Conservative Analyst",
    "Neutral Analyst": "Neutral Analyst",
    "Portfolio Manager": "Portfolio Manager",
}


def _tools_or_done(state) -> str:
    """Route an analyst's turn: run its tool calls, or finish with its report."""
    return "tools" if state["messages"][-1].tool_calls else END


def identical_call_repeat(messages, limit: int = 2) -> str | None:
    """Name of the tool whose call repeats in ``limit`` consecutive rounds, or ``None``.

    Implements D1-REQ-TERM-002: a model that asks for the same call with the
    same arguments again is not making progress, so the analyst loop may wrap
    up instead of spending every remaining round on it.

    A call is canonicalised as ``(name, json.dumps(args, sort_keys=True))``, so
    a different key order or a fresh tool-call id cannot hide a repeat. The
    streak counts consecutive rounds (an ``AIMessage`` turn); tool results
    between them are ignored, while different arguments or a different call in
    between start it again. A round may hold several calls, in which case the
    repeated call's names are returned in sorted order.
    """
    if limit < 2:
        return None
    previous = None
    streak = 0
    for message in messages:
        if not isinstance(message, AIMessage):
            continue
        calls = message.tool_calls or []
        if not calls:
            previous, streak = None, 0
            continue
        signature = tuple(sorted(
            (call.get("name", ""), json.dumps(call.get("args", {}), sort_keys=True))
            for call in calls
        ))
        if signature == previous:
            streak += 1
        else:
            previous, streak = signature, 1
        if streak >= limit:
            return ", ".join(sorted({name for name, _ in signature}))
    return None


def _traced(name: str, node, phase: str | None = None, kind: str = "agent"):
    """Wrap one graph step so it emits a telemetry span (OBS-001).

    The wrapper keeps the ``(state)`` signature LangGraph inspects. Outside a
    telemetry scope ``span`` is a no-op, so the graph is unchanged when the
    feature is off.
    """

    def traced_node(state):
        with span(name, phase=phase or name, kind=kind):
            return node(state) if callable(node) else node.invoke(state)

    traced_node.__name__ = getattr(node, "__name__", name.replace(".", "_"))
    return traced_node


def _analyst_graph(spec, agent, max_tool_rounds: int):
    """One analyst as a graph of its own: the model and its tools, on a private message history.

    It returns only its report, so analysts running side by side never write the
    same key, and its tool calls never reach the other analysts' messages. After
    ``max_tool_rounds`` rounds of tool calls it is told to write its report, and
    that turn ends it whatever it answers, so a model that keeps calling tools
    cannot run the graph into its recursion limit (#1420).
    """
    output = TypedDict(f"{spec.key.capitalize()}Report", {spec.report_key: str})
    graph = StateGraph(AgentState, output_schema=output)
    graph.add_node("agent", _traced(f"{spec.key}.agent", agent, phase=spec.key))
    graph.add_edge(START, "agent")
    if not spec.tools:
        graph.add_edge("agent", END)
        return graph.compile()

    def calls(messages):
        return [call["name"] for m in messages for call in (getattr(m, "tool_calls", None) or [])]

    def rounds(messages) -> int:
        return sum(1 for m in messages if getattr(m, "tool_calls", None))

    def more_or_wrap_up(state) -> str:
        if rounds(state["messages"]) >= max_tool_rounds:
            return "wrap_up"
        return "wrap_up" if identical_call_repeat(state["messages"]) else "agent"

    def wrap_up(state):
        repeated = ", ".join(f"{name} x{n}" for name, n in Counter(calls(state["messages"])).most_common())
        stalled_on = identical_call_repeat(state["messages"])
        if stalled_on is not None:
            logger.warning("%s repeated the same %s call; asking for its report (%s)",
                           spec.agent_node, stalled_on, repeated)
        else:
            logger.warning("%s used its %d tool rounds (%s); asking for its report",
                           spec.agent_node, max_tool_rounds, repeated)
        return agent({**state, "messages": [*state["messages"], HumanMessage(WRAP_UP)]})

    graph.add_node(
        "tools", _traced(f"{spec.key}.tools", ToolNode(list(spec.tools)), phase=spec.key, kind="tool")
    )
    graph.add_node(
        "wrap_up", _traced(f"{spec.key}.wrap_up", wrap_up, phase=spec.key, kind="wrap_up")
    )
    graph.add_conditional_edges("agent", _tools_or_done, ["tools", END])
    graph.add_conditional_edges("tools", more_or_wrap_up, ["agent", "wrap_up"])
    graph.add_edge("wrap_up", END)
    return graph.compile()


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm: Any,
        deep_thinking_llm: Any,
        conditional_logic: ConditionalLogic,
        max_tool_rounds: int,
    ):
        """Initialize with required components."""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.conditional_logic = conditional_logic
        self.max_tool_rounds = max_tool_rounds

    def setup_graph(
        self, selected_analysts=("market", "social", "news", "fundamentals"), memory_node=None
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "social": Sentiment analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
            memory_node: Node that settles past decisions and returns the run's
                ``past_context``. It runs alongside the analysts.
        """
        plan = build_analyst_execution_plan(selected_analysts)

        analyst_factories = {
            "market": lambda: create_market_analyst(self.quick_thinking_llm),
            "social": lambda: create_sentiment_analyst(self.quick_thinking_llm),
            "news": lambda: create_news_analyst(self.quick_thinking_llm),
            "fundamentals": lambda: create_fundamentals_analyst(self.quick_thinking_llm),
        }

        bull_researcher_node = create_bull_researcher(self.quick_thinking_llm)
        bear_researcher_node = create_bear_researcher(self.quick_thinking_llm)
        research_manager_node = create_research_manager(
            self.deep_thinking_llm,
            max_turns=2 * self.conditional_logic.max_debate_rounds,
        )
        trader_node = create_trader(self.quick_thinking_llm)

        aggressive_analyst = create_aggressive_debator(self.quick_thinking_llm)
        neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
        conservative_analyst = create_conservative_debator(self.quick_thinking_llm)
        portfolio_manager_node = create_portfolio_manager(
            self.deep_thinking_llm,
            max_turns=3 * self.conditional_logic.max_risk_discuss_rounds,
        )

        workflow = StateGraph(AgentState)

        for spec in plan.specs:
            workflow.add_node(spec.agent_node,
                              _analyst_graph(spec, analyst_factories[spec.key](), self.max_tool_rounds))

        workflow.add_node("Bull Researcher", _traced("Bull Researcher", bull_researcher_node))
        workflow.add_node("Bear Researcher", _traced("Bear Researcher", bear_researcher_node))
        workflow.add_node("Research Manager", _traced("Research Manager", research_manager_node))
        workflow.add_node("Trader", _traced("Trader", trader_node))
        workflow.add_node("Aggressive Analyst", _traced("Aggressive Analyst", aggressive_analyst))
        workflow.add_node("Neutral Analyst", _traced("Neutral Analyst", neutral_analyst))
        workflow.add_node(
            "Conservative Analyst", _traced("Conservative Analyst", conservative_analyst)
        )
        workflow.add_node("Portfolio Manager", _traced("Portfolio Manager", portfolio_manager_node))

        # The analysts work at the same time; the research debate starts once
        # every one of them has filed its report. The memory log settles past
        # decisions alongside them: only the Portfolio Manager reads its lessons.
        first_steps = [spec.agent_node for spec in plan.specs]
        if memory_node is not None:
            workflow.add_node("Memory Log", _traced("Memory Log", memory_node))
            first_steps.append("Memory Log")
        for node in first_steps:
            workflow.add_edge(START, node)
        workflow.add_edge(first_steps, "Bull Researcher")

        # Both research-debate edges share the complete DEBATE_PATH_MAP (#1088).
        for debate_node in ("Bull Researcher", "Bear Researcher"):
            workflow.add_conditional_edges(
                debate_node,
                self.conditional_logic.should_continue_debate,
                DEBATE_PATH_MAP,
            )
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Aggressive Analyst")
        # All three risk edges share the complete RISK_ANALYSIS_PATH_MAP (#1088).
        for risk_node in ("Aggressive Analyst", "Conservative Analyst", "Neutral Analyst"):
            workflow.add_conditional_edges(
                risk_node,
                self.conditional_logic.should_continue_risk_analysis,
                RISK_ANALYSIS_PATH_MAP,
            )

        workflow.add_edge("Portfolio Manager", END)

        return workflow
