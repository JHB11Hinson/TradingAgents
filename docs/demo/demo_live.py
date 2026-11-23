#!/usr/bin/env python3
"""One real TradingAgents run, with the process printed in the terminal.

This is the live path: a real model and the configured market vendors, not the
deterministic replay in `demo.sh b1/b2`. It uses one analyst and one round of
each debate by default so the demo finishes in a reasonable time. Override with
the environment variables below.

Endpoint selection, in order:
  1. DEMO_BASE_URL / DEMO_MODEL / DEMO_API_KEY
  2. CITYUCS_LLM_BASE_URL + CITYUCS_LLM_API_KEY, model CS5351/DeepSeek-V4-Flash
  3. http://127.0.0.1:8765/v1, model deepseek-v4.1-flash (local OpenCode Go proxy)
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import yfinance as yf
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import LLMResult

REPO_DIR = Path(
    os.environ.get("DEMO_REPO") or Path(__file__).resolve().parents[2]
)
if (REPO_DIR / "src").is_dir():
    sys.path.insert(0, str(REPO_DIR / "src"))

from tradingagents.agents.rating import run_rating  # noqa: E402
from tradingagents.dataflows.symbols import safe_ticker_component  # noqa: E402
from tradingagents.default_config import DEFAULT_CONFIG  # noqa: E402
from tradingagents.graph.trading_graph import TradingAgentsGraph  # noqa: E402

PRINT_LOCK = threading.Lock()


def say(line: str = "") -> None:
    with PRINT_LOCK:
        print(line, flush=True)


def _short(value: object, limit: int = 110) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _port_open(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.hostname not in {"127.0.0.1", "localhost"}:
        return True
    try:
        with socket.create_connection((parsed.hostname, parsed.port or 80), timeout=1):
            return True
    except OSError:
        return False


def install_cached_ohlcv(ticker: str, cache_dir: Path) -> Path | None:
    """Serve this ticker's OHLCV history from the run cache, not Yahoo.

    ``get_stock_data`` calls yfinance directly, while the indicator and snapshot
    tools already read the cache. When Yahoo rate-limits the direct call, the
    market analyst loses the CSV even though the data is on disk. Patching
    ``Ticker.history`` for this ticker makes the demo use the same cached frame
    the measured run used; other tickers still go live.
    """
    path = cache_dir / f"{safe_ticker_component(ticker.upper())}-YFin-data.csv"
    if not path.exists():
        return None

    frame = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
    original_history = yf.Ticker.history

    def cached_history(self, *args, **kwargs):
        if str(getattr(self, "ticker", "")).upper() != ticker.upper():
            return original_history(self, *args, **kwargs)
        data = frame.copy()
        start = kwargs.get("start") or (args[0] if len(args) > 0 else None)
        end = kwargs.get("end") or (args[1] if len(args) > 1 else None)
        if start:
            data = data[data.index >= pd.Timestamp(start)]
        if end:
            data = data[data.index < pd.Timestamp(end)]
        return data

    yf.Ticker.history = cached_history
    return path


def resolve_endpoint() -> tuple[str, str, str]:
    base = os.environ.get("DEMO_BASE_URL", "").strip()
    model = os.environ.get("DEMO_MODEL", "").strip()
    key = os.environ.get("DEMO_API_KEY", "").strip()

    if not base and os.environ.get("CITYUCS_LLM_BASE_URL") and os.environ.get(
        "CITYUCS_LLM_API_KEY"
    ):
        base = os.environ["CITYUCS_LLM_BASE_URL"].strip()
        key = key or os.environ["CITYUCS_LLM_API_KEY"].strip()
        model = model or "CS5351/DeepSeek-V4-Flash"

    if not base:
        base = "http://127.0.0.1:8765/v1"
    if not model:
        model = "CS5351/DeepSeek-V4-Flash" if "cityu" in base else "deepseek-v4.1-flash"
    if not key:
        key = os.environ.get("OPENAI_COMPATIBLE_API_KEY", "proxy")
    return base.rstrip("/"), model, key


class TerminalReporter(BaseCallbackHandler):
    """Print each model call, tool call and token increment as it happens."""

    def __init__(self) -> None:
        super().__init__()
        self.llm_calls = 0
        self.tool_calls = 0
        self.tokens_in = 0
        self.tokens_out = 0

    def on_llm_end(self, response: LLMResult, **kwargs: object) -> None:
        usage = None
        try:
            generation = response.generations[0][0]
            usage = getattr(getattr(generation, "message", None), "usage_metadata", None)
        except (IndexError, TypeError):
            pass
        if not isinstance(usage, dict):
            return
        tokens_in = int(usage.get("input_tokens", 0) or 0)
        tokens_out = int(usage.get("output_tokens", 0) or 0)
        with PRINT_LOCK:
            self.llm_calls += 1
            self.tokens_in += tokens_in
            self.tokens_out += tokens_out
            print(
                f"    [tokens] call {self.llm_calls}: "
                f"{tokens_in:,} in / {tokens_out:,} out "
                f"(running {self.tokens_in:,} / {self.tokens_out:,})",
                flush=True,
            )

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: object) -> None:
        name = (serialized or {}).get("name", "tool")
        with PRINT_LOCK:
            self.tool_calls += 1
            print(f"    [tool] {name}({_short(input_str)})", flush=True)


def main() -> int:
    ticker = os.environ.get("DEMO_TICKER", "NVDA")
    trade_date = os.environ.get("DEMO_DATE", "2026-11-20")
    analysts = [a.strip() for a in os.environ.get("DEMO_ANALYSTS", "market").split(",") if a.strip()]
    language = os.environ.get("DEMO_LANGUAGE", "English")
    rounds = int(os.environ.get("DEMO_ROUNDS", "1"))

    base_url, model, api_key = resolve_endpoint()
    os.environ["OPENAI_COMPATIBLE_API_KEY"] = api_key

    results_dir = Path(os.environ.get("DEMO_RESULTS_DIR", "/tmp/opencode/demo-live/results"))
    cache_dir = Path(os.environ.get("DEMO_CACHE_DIR", str(Path.home() / ".tradingagents/cache")))
    memory_path = Path(
        os.environ.get("DEMO_MEMORY", "/tmp/opencode/demo-live/memory/trading_memory.md")
    )
    for path in (results_dir, cache_dir, memory_path.parent):
        path.mkdir(parents=True, exist_ok=True)

    ohlcv_cache = None
    if os.environ.get("DEMO_OHLCV", "cache").lower() != "live":
        ohlcv_cache = install_cached_ohlcv(ticker, cache_dir)

    config = dict(DEFAULT_CONFIG)
    config.update(
        {
            "llm_provider": "openai_compatible",
            "backend_url": base_url,
            "deep_think_llm": model,
            "quick_think_llm": model,
            "output_language": language,
            "max_debate_rounds": rounds,
            "max_risk_discuss_rounds": rounds,
            "context_budget_tokens": int(os.environ.get("DEMO_CONTEXT_BUDGET", "250000")),
            "context_call_budget_tokens": 50000,
            "results_dir": str(results_dir),
            "data_cache_dir": str(cache_dir),
            "memory_log_path": str(memory_path),
            "checkpoint_enabled": False,
            "telemetry_enabled": True,
        }
    )

    if not _port_open(base_url):
        say(f"No endpoint at {base_url}.")
        say("Start the local proxy or set DEMO_BASE_URL / DEMO_MODEL / DEMO_API_KEY.")
        return 2

    say("CS5351 live run")
    say(f"  ticker={ticker}  date={trade_date}  analysts={','.join(analysts)}")
    say(f"  endpoint={base_url}  model={model}  language={language}")
    say(f"  rounds={rounds}  budget={config['context_budget_tokens']:,}")
    if ohlcv_cache is not None:
        say(f"  OHLCV: cache {ohlcv_cache} (set DEMO_OHLCV=live to force Yahoo)")
    else:
        say("  OHLCV: live (no cache for this ticker; Yahoo may rate-limit)")
    say("  This is a real run: it calls the model and market vendors. Expect several minutes.")
    say("  Ctrl-C stops it; the run is not recorded as a decision.")
    say()

    reporter = TerminalReporter()
    started = time.time()
    graph = TradingAgentsGraph(
        selected_analysts=analysts,
        debug=False,
        config=config,
        callbacks=[reporter],
    )

    init_state = graph.create_run_state(ticker, trade_date)
    args = graph.propagator.get_graph_args(callbacks=[reporter])
    final_state = dict(init_state)
    seen_phases: set[str] = set()
    seen_messages: set[object] = set()

    phases = [
        ("market_report", "Market Analyst report ready"),
        ("sentiment_report", "Sentiment Analyst report ready"),
        ("news_report", "News Analyst report ready"),
        ("fundamentals_report", "Fundamentals Analyst report ready"),
        ("investment_plan", "Research Manager decision ready"),
        ("trader_investment_plan", "Trader plan ready"),
        ("final_trade_decision", "Portfolio Manager decision ready"),
    ]

    try:
        for messages, chunk in graph.stream_run(graph.checkpoint_input(init_state), **args):
            for message in messages:
                message_id = getattr(message, "id", None)
                if message_id is not None:
                    if message_id in seen_messages:
                        continue
                    seen_messages.add(message_id)
                if isinstance(message, AIMessage):
                    calls = getattr(message, "tool_calls", None) or []
                    if not calls and getattr(message, "content", ""):
                        text = str(message.content)
                        say(f"    [agent] {len(text):,} chars: {_short(text, 100)}")
                elif isinstance(message, ToolMessage):
                    text = str(message.content)
                    say(f"    [data] {len(text):,} chars")

            if chunk is None:
                continue
            final_state.update(chunk)
            for key, label in phases:
                if key not in seen_phases and chunk.get(key):
                    seen_phases.add(key)
                    say(f"\n[phase] {label}")

        rating = run_rating(final_state)
        graph.record_decision(ticker, trade_date, final_state)
        report_path = graph.save_reports(final_state, ticker, html=False)
    except KeyboardInterrupt:
        say("\nInterrupted; no decision recorded.")
        return 130
    except Exception as exc:  # noqa: BLE001 - the demo should show the failure, not hide it
        say(f"\nRun failed: {type(exc).__name__}: {exc}")
        return 1

    elapsed = time.time() - started
    say()
    say("Done.")
    say(f"  rating: {rating}")
    say(f"  provider tokens: {reporter.tokens_in:,} in / {reporter.tokens_out:,} out "
        f"/ {reporter.tokens_in + reporter.tokens_out:,} total")
    say(f"  model calls: {reporter.llm_calls}  tool calls: {reporter.tool_calls}")
    say(f"  state log: {results_dir}")
    say(f"  report: {report_path}")
    say(f"  elapsed: {elapsed:,.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
