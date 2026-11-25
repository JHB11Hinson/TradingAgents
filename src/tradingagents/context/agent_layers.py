"""Helpers the report agents use to declare their six context layers.

The agents keep owning their prose; these helpers only make the layer
boundary explicit, so every call reports the same six sources to the
assembler (D1-REQ-CTX-001).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from tradingagents.guardrails.instructions import scrub_untrusted
from tradingagents.telemetry import guardrail_event

from .assembler import ContextBlock, Layer, estimate_tokens

DEFAULT_POINTER = (
    "Run state: the LangGraph checkpoint and the memory log are the resume "
    "pointers; this node received no explicit pointer in the state."
)


def identity_block(instrument_context: str) -> ContextBlock:
    """The instrument identity layer every report agent receives."""
    return ContextBlock(Layer.IDENTITY, "state.instrument_context", instrument_context)


def portfolio_block(portfolio_context: str) -> ContextBlock:
    """The caller's portfolio, for the agents that may size a position."""
    return ContextBlock(Layer.IDENTITY, "state.portfolio_context", portfolio_context)


def constraints_block(role: str) -> ContextBlock:
    """The agent's standing role prompt and output contract."""
    return ContextBlock(Layer.CONSTRAINTS, "role", role)


def retrieved_block(source: str, text: str, *, render: bool = True) -> ContextBlock:
    """One piece of retrieved knowledge with its state source.

    Retrieved text can be vendor or social content, so SAFE-001 scrubs
    instruction-like spans here, at the one seam every report, memory lesson and
    manager plan passes through. A blocked span is reported as an advisory
    guardrail event carrying only the pattern names (OBS-003).
    """
    scrubbed = scrub_untrusted(text)
    if scrubbed.blocked:
        guardrail_event("guardrail.instruction_blocked", ",".join(scrubbed.matches), node=source)
    return ContextBlock(Layer.RETRIEVED, source, scrubbed.text, render=render)


def history_block(
    messages: Iterable[Any] = (),
    *,
    text: str | None = None,
    source: str = "state.messages",
    render: bool = True,
) -> ContextBlock:
    """Conversation history (messages or a debate transcript)."""
    rendered = text if text is not None else messages_text(messages)
    if not rendered.strip():
        rendered = "(No conversation history in this run.)"
    return ContextBlock(Layer.HISTORY, source, rendered, render=render)


def resumable_block(state: Mapping[str, Any]) -> ContextBlock:
    """The resumable-state layer: checkpoint and memory-log pointers."""
    pointer = state.get("run_pointers") or state.get("checkpoint_thread_id")
    text = f"Run state: resume pointer {pointer}." if pointer else DEFAULT_POINTER
    return ContextBlock(Layer.RESUMABLE, "state.run_pointers", text)


def task_block(instruction: str) -> ContextBlock:
    """The current turn's instruction."""
    return ContextBlock(Layer.TASK, "task", instruction)


def messages_text(messages: Iterable[Any]) -> str:
    """Render a message list as text, for budget accounting only."""
    lines = []
    for message in messages or ():
        role, content = _message_parts(message)
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines)


def trim_messages(messages: Sequence[Any], token_cap: int | None) -> list[Any]:
    """Drop the oldest messages until the history fits its compacted ceiling.

    The assembler reports how many history tokens survived; the analyst passes
    the same messages it was given unless compaction actually trimmed history.
    """
    kept = list(messages or ())
    if token_cap is None:
        return kept
    while kept and estimate_tokens(messages_text(kept)) > token_cap:
        kept.pop(0)
    return kept


def _message_parts(message: Any) -> tuple[str, str]:
    if isinstance(message, tuple) and len(message) == 2:
        role, content = message
        return str(role), str(content)
    if isinstance(message, Mapping):
        return str(message.get("role", "message")), str(message.get("content", ""))
    role = getattr(message, "type", None) or getattr(message, "role", None) or "message"
    content = getattr(message, "content", "")
    return str(role), str(content)
