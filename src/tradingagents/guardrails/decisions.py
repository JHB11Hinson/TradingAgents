"""Strict free-text decision contract for the Portfolio Manager (D1-REQ-SAFE-002).

A provider without native structured output may still answer in prose. That
answer is not a schema-validated decision, so it is accepted only when it carries
exactly one explicit decision line and no conflicting rating label. Everything
else degrades to the non-tradeable REVIEW sentinel.
"""

from __future__ import annotations

import re
import unicodedata

_RATING_SET = {
    "buy": "Buy",
    "overweight": "Overweight",
    "hold": "Hold",
    "underweight": "Underweight",
    "sell": "Sell",
}
_SCALE_RE = re.compile(r"rating\s*(?:scale|options|legend)", re.IGNORECASE)
_OWN_LINE_RE = re.compile(
    r"(?im)^\s*(?:[-*+]\s+)?(?:\*\*)?(?:final\s+|our\s+|overall\s+)?rating(?:\*\*)?"
    r"\s*[:\-\u2010-\u2015]\s*(?:\*\*)?\s*(buy|overweight|hold|underweight|sell)\b"
)
_ANY_LABEL_RE = re.compile(
    r"(?i)(?<![a-z])rating\b[^:\-\u2010-\u2015\n]{0,40}?[:\-\u2010-\u2015]\s*\**\s*"
    r"(buy|overweight|hold|underweight|sell)\b"
)


def validate_free_text_decision(text: str) -> str | None:
    """The tier in a text with one explicit call, or ``None``.

    A rating scale echoed from the prompt, a list of other parties' ratings, and
    two different decision lines are all rejected. A single ``Rating: Hold`` is
    accepted: it is an explicit call, not an inference from prose.
    """
    if not text:
        return None
    normalized = unicodedata.normalize("NFKC", text)
    lines = [
        line for line in normalized.splitlines() if not _SCALE_RE.search(line)
    ]
    kept = "\n".join(lines)

    own = _OWN_LINE_RE.findall(kept)
    if len(own) != 1:
        return None

    labels = [value.lower() for value in _ANY_LABEL_RE.findall(kept)]
    distinct = {value for value in labels if value in _RATING_SET}
    if len(distinct) != 1:
        return None
    if own[0].lower() != next(iter(distinct)):
        return None
    return _RATING_SET[own[0].lower()]


def review_decision(reason: str) -> str:
    """The canonical REVIEW decision text used when no valid decision exists."""
    return (
        "Rating: REVIEW\n\n"
        "No tradeable decision was produced: the Portfolio Manager's answer failed the "
        f"deterministic decision contract ({reason})."
    )
