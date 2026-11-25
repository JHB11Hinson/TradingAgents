"""Sentiment analyst: one sentiment report from three sources.

The node fetches its sources before calling the model and puts them in the
prompt, so the model reports on data it was given rather than inventing posts:

  1. News headlines: Yahoo Finance
  2. StockTwits messages: the cashtag stream, with Bullish/Bearish tags
  3. Reddit posts: r/wallstreetbets, r/stocks, r/investing, or crypto communities for a crypto pair

Each source is trimmed to the analysis window. With a TypeSafe key, the social
posts are screened by Jev first (see post_screen). These feeds serve recent items
and are not archived, so a historical run's sentiment inputs are not
point-in-time.

The report is a SentimentReport through structured output where the provider
supports it and free text otherwise, so the band, score and confidence header
reads the same across providers.
"""

from datetime import datetime, timedelta

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents import prompts
from tradingagents.agents.context import get_instrument_context_from_state, get_language_instruction
from tradingagents.agents.post_screen import jev_screen
from tradingagents.agents.schemas import SentimentReport, render_sentiment_report
from tradingagents.agents.structured import bind_structured, invoke_structured_or_freetext
from tradingagents.agents.tools import get_news
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
from tradingagents.dataflows.vendors.reddit import (
    CRYPTO_SUBREDDITS,
    DEFAULT_SUBREDDITS,
    fetch_reddit_posts,
    subreddits_for,
)
from tradingagents.dataflows.vendors.stocktwits import fetch_stocktwits_messages
from tradingagents.guardrails.instructions import scrub_untrusted
from tradingagents.telemetry import guardrail_event


def _seven_days_back(trade_date: str) -> str:
    return (datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")


def _scrub_source(name: str, text: str) -> str:
    """SAFE-001 scrub one pre-fetched feed; report blocked spans to telemetry.

    The event reason carries only the pattern names, never the feed text
    (D1-REQ-OBS-003).
    """
    scrubbed = scrub_untrusted(text)
    if scrubbed.blocked:
        guardrail_event("guardrail.instruction_blocked", ",".join(scrubbed.matches), node=name)
    return scrubbed.text


def create_sentiment_analyst(llm):
    """Create a sentiment analyst node for the trading graph.

    Pre-fetches news + StockTwits + Reddit data, injects them into the
    prompt as structured blocks, and produces a deterministic sentiment
    report via structured output (with a free-text fallback for providers
    that do not support it).
    """
    structured_llm = bind_structured(llm, SentimentReport, "Sentiment Analyst")

    def sentiment_analyst_node(state):
        ticker = state["company_of_interest"]
        end_date = state["trade_date"]
        start_date = _seven_days_back(end_date)
        instrument_context = get_instrument_context_from_state(state)

        # Pre-fetch all three sources. Each fetcher degrades gracefully and
        # returns a string (no exceptions surface from here), so the LLM
        # always sees something — either real data or a clear placeholder.
        news_block = get_news.func(ticker, start_date, end_date)
        # Pass the analysis window so a historical run trims social posts to it
        # instead of leaking today's chatter into a backtest (#1220).
        screen = jev_screen(ticker)
        stocktwits_block = fetch_stocktwits_messages(
            ticker, limit=30, start_date=start_date, end_date=end_date, screen=screen
        )
        subreddits = subreddits_for(ticker)
        reddit_block = fetch_reddit_posts(
            ticker, subreddits, start_date=start_date, end_date=end_date, screen=screen
        )
        # SAFE-001: these three blocks are external text embedded in the prompt
        # template, so they do not pass through the context assembler.
        news_block = _scrub_source("news", news_block)
        stocktwits_block = _scrub_source("stocktwits", stocktwits_block)
        reddit_block = _scrub_source("reddit", reddit_block)

        preamble = prompts.load_prompt("analyst.sentiment_preamble").text.format(
            current_date=end_date,
            instrument_context=instrument_context,
            no_external_tools=prompts.load_prompt("shared.no_external_tools").text,
        )
        system_message = _build_system_message(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            news_block=news_block,
            stocktwits_block=stocktwits_block,
            reddit_block=reddit_block,
            subreddits=subreddits,
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

        original = preamble.format(
            current_date=end_date,
            instrument_context=instrument_context,
        ) + "\n" + system_message
        layers = make_layers(
            identity=[identity_block(instrument_context)],
            constraints=[constraints_block(system_message)],
            retrieved=[
                retrieved_block(
                    "state.market_data",
                    "News, StockTwits and Reddit blocks are embedded in the role prompt.",
                    render=False,
                )
            ],
            history=[history_block(state["messages"], render=False)],
            resumable=[resumable_block(state)],
            task=[
                task_block(
                    "Produce the sentiment report with the overall band, score, "
                    "confidence and narrative fields."
                )
            ],
        )
        assembled = assemble_context(
            layers, original=original, agent="Sentiment Analyst"
        )
        messages = (
            trim_messages(state["messages"], assembled.layer_tokens[Layer.HISTORY])
            if assembled.compacted
            else state["messages"]
        )

        prompt = prompt.partial(
            system_message=assembled.text if assembled.compacted else system_message
        )
        prompt = prompt.partial(current_date=end_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        # Format the template into a concrete message list so the structured
        # and free-text paths receive the same input. No bind_tools — the
        # data is already in the prompt.
        formatted_messages = prompt.format_messages(messages=messages)

        report_text = invoke_structured_or_freetext(
            structured_llm,
            llm,
            formatted_messages,
            render_sentiment_report,
            "Sentiment Analyst",
        )

        return {
            "messages": [AIMessage(content=report_text)],
            "sentiment_report": report_text,
        }

    return sentiment_analyst_node


def _build_system_message(
    *,
    ticker: str,
    start_date: str,
    end_date: str,
    news_block: str,
    stocktwits_block: str,
    reddit_block: str,
    subreddits: tuple[str, ...] = DEFAULT_SUBREDDITS,
) -> str:
    """Assemble the sentiment-analyst system message with structured data blocks."""
    if subreddits == DEFAULT_SUBREDDITS:
        character = "r/wallstreetbets is often contrarian/exuberant; r/stocks more measured; r/investing longer-term"
    elif len(subreddits) > len(CRYPTO_SUBREDDITS):
        character = f"r/{subreddits[0]} leans toward the coin's holders; r/CryptoCurrency and r/CryptoMarkets are broader"
    else:
        character = "r/CryptoCurrency and r/CryptoMarkets are broad crypto communities"
    return prompts.load_prompt("analyst.sentiment.system").text.format(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        news_block=news_block,
        stocktwits_block=stocktwits_block,
        reddit_block=reddit_block,
        subreddits=", ".join(f"r/{sub}" for sub in subreddits),
        character=character,
        language_instruction=get_language_instruction(),
    )
