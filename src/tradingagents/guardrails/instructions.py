"""Instruction scrubbing for external and retrieved text (D1-REQ-SAFE-001).

Vendor payloads, social posts, news and retrieved reports reach a model as
evidence. A small, fixed set of instruction-like patterns is neutralised before
that happens: the evidence stays readable, but a span that tries to address the
model as a system or developer is replaced with a marker.

The scrubber is deliberately not an LLM guard. It is deterministic, offline and
cheap, and it does not depend on a provider.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ZERO_WIDTH = "\u200b\u200c\u200d\u2060\ufeff"
BLOCKED_MARKER = "[blocked instruction]"


@dataclass(frozen=True)
class ScrubResult:
    """The scrubbed text and the patterns that fired."""

    text: str
    blocked: bool
    matches: tuple[str, ...]


_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ignore_instructions",
        re.compile(
            r"\b(?:ignore|disregard|forget|override)\b[^\n.!?]{0,80}?"
            r"\b(?:previous|prior|above|earlier|all|the)\b[^\n.!?]{0,20}?"
            r"\b(?:instructions?|rules?|prompts?|directions?|guardrails?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "role_marker",
        re.compile(
            r"(?im)^\s*(?:system|developer|assistant|tool)\s*:",
        ),
    ),
    (
        "inline_role_marker",
        re.compile(
            r"\b(?:system|developer|assistant)\s+(?:prompt|message|instructions?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "new_instructions",
        re.compile(r"\b(?:new|updated|revised)\s+instructions?\b", re.IGNORECASE),
    ),
    (
        "you_are_now",
        re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
    ),
    (
        "do_anything_now",
        re.compile(r"\bdo\s+anything\s+now\b", re.IGNORECASE),
    ),
    (
        "reveal_prompt",
        re.compile(
            r"\b(?:reveal|print|show|repeat|leak)\b[^\n.!?]{0,40}?"
            r"\b(?:system|developer|hidden|initial)\b[^\n.!?]{0,20}?"
            r"\b(?:prompt|message|instructions?)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "call_tool",
        re.compile(r"\bcall\s+the\s+tool\b", re.IGNORECASE),
    ),
    (
        "jailbreak",
        re.compile(r"\b(?:jailbreak|DAN|developer\s+mode)\b"),
    ),
)


def detect(text: str) -> tuple[str, ...]:
    """Names of the instruction patterns the text contains."""
    if not text:
        return ()
    return tuple(name for name, pattern in _PATTERNS if pattern.search(text))


def _strip_zero_width(text: str) -> str:
    return text.translate({ord(char): None for char in _ZERO_WIDTH})


def scrub_untrusted(text: str, *, enabled: bool = True) -> ScrubResult:
    """Neutralise instruction-like spans in untrusted text.

    ``enabled=False`` exists for the negative test: it returns the input
    unchanged so a test can prove that the guard is what removed the span.
    """
    if not text or not enabled:
        return ScrubResult(text or "", False, ())

    cleaned = _strip_zero_width(text)
    names = set(detect(cleaned))
    matches = []
    for name, pattern in _PATTERNS:
        if name in names:
            matches.append(name)
            cleaned = pattern.sub(BLOCKED_MARKER, cleaned)
    return ScrubResult(cleaned, bool(matches), tuple(matches))
