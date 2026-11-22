from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents import prompts
from tradingagents.agents.analysts.turn import take_turn
from tradingagents.agents.context import get_instrument_context_from_state, get_language_instruction
from tradingagents.agents.tools import get_indicators, get_stock_data, get_verified_market_snapshot
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
    get_stock_data,
    get_indicators,
    get_verified_market_snapshot,
)

def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = get_instrument_context_from_state(state)

        # Identity, date and tool names stay in the template so the wrap-up turn
        # can re-bind `tool_names`; the assembler supplies the role-and-task block.
        preamble = prompts.load_prompt("analyst.tool_preamble").text
        system_message = prompts.load_prompt("analyst.market.system").text.format(
            language_instruction=get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    preamble + "\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        tool_names = ", ".join([tool.name for tool in TOOLS])
        original = preamble.format(
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
                    "Use the tools as needed, then write the detailed market report "
                    "with the Markdown table."
                )
            ],
        )
        assembled = assemble_context(
            layers, original=original, agent="Market Analyst"
        )
        messages = (
            trim_messages(state["messages"], assembled.layer_tokens[Layer.HISTORY])
            if assembled.compacted
            else state["messages"]
        )

        # Under budget the role text is unchanged; over budget the assembler's
        # compacted block replaces it.
        system_part = assembled.text if assembled.compacted else system_message
        prompt = prompt.partial(system_message=system_part)
        prompt = prompt.partial(tool_names=tool_names)
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        result, report = take_turn(prompt, llm, TOOLS, messages)

        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
