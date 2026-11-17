from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents.agents.analysts.turn import take_turn
from tradingagents.agents.context import get_instrument_context_from_state, get_language_instruction
from tradingagents.agents.tools import (
    get_balance_sheet,
    get_cashflow,
    get_fundamentals,
    get_income_statement,
    get_insider_transactions,
)
from tradingagents.context import Layer, assemble_context, make_layers
from tradingagents.context.agent_layers import (
    constraints_block,
    history_block,
    identity_block,
    resumable_block,
    retrieved_block,
    task_block,
    trim_messages,
)

# The tools this analyst is offered; its tool node is built from the same tuple.
TOOLS = (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    get_insider_transactions,
)

_PREAMBLE = (
    "You are a helpful AI assistant, collaborating with other assistants."
    " Use the provided tools to progress towards answering the question."
    " If you are unable to fully answer, that's OK; another assistant with different tools"
    " will help where you left off. Execute what you can to make progress."
    " Report what your tools support; another agent decides the trade."
    " You have access to the following tools: {tool_names}."
    " Today's date is {current_date}; treat it as 'now' for all analysis and tool-call date ranges. {instrument_context}"
)


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = get_instrument_context_from_state(state)

        system_message = (
            "You are a researcher tasked with analyzing fundamental information over the past week about a company. Please write a comprehensive report of the company's fundamental information such as financial documents, company profile, basic company financials, and company financial history to gain a full view of the company's fundamental information to inform traders. Make sure to include as much detail as possible. Provide specific, actionable insights with supporting evidence to help traders make informed decisions."
            + " Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
            + " Use the available tools: `get_fundamentals` for comprehensive company analysis, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` for specific financial statements, and `get_insider_transactions` for recent insider buying and selling."
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    _PREAMBLE + "\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        tool_names = ", ".join([tool.name for tool in TOOLS])
        original = _PREAMBLE.format(
            tool_names=tool_names,
            current_date=current_date,
            instrument_context=instrument_context,
        ) + "\n" + system_message
        layers = make_layers(
            identity=[identity_block(instrument_context)],
            constraints=[constraints_block(system_message)],
            retrieved=[
                retrieved_block("tools", f"Available tools: {tool_names}", render=False)
            ],
            history=[history_block(state["messages"], render=False)],
            resumable=[resumable_block(state)],
            task=[
                task_block(
                    "Use the tools as needed, then write the comprehensive fundamentals "
                    "report with the Markdown table."
                )
            ],
        )
        assembled = assemble_context(
            layers, original=original, agent="Fundamentals Analyst"
        )
        messages = (
            trim_messages(state["messages"], assembled.layer_tokens[Layer.HISTORY])
            if assembled.compacted
            else state["messages"]
        )

        prompt = prompt.partial(
            system_message=assembled.text if assembled.compacted else system_message
        )
        prompt = prompt.partial(tool_names=tool_names)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        result, report = take_turn(prompt, llm, TOOLS, messages)

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
