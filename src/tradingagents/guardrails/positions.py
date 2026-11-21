"""Deterministic position ceiling (D1-REQ-SAFE-003).

The model may propose a position size; it may not decide that the ceiling does
not apply. The functions here clip a claimed size to the configured ceiling and
report what they changed, so the Portfolio Manager can log it.
"""

from __future__ import annotations

import math
import re
from typing import Any

DEFAULT_MAX_POSITION_PCT = 10.0

_PERCENT_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*%")
_POSITION_LINE_RE = re.compile(
    r"(?im)^(\s*(?:[-*+]\s+)?(?:\*\*)?position\s*(?:size|sizing)(?:\*\*)?\s*:\s*)"
    r"(\d+(?:\.\d+)?)\s*%"
)


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def claimed_position_pct(text: str | None) -> float | None:
    """The first percentage stated in a sizing string, or ``None``."""
    if not text:
        return None
    match = _PERCENT_RE.search(text)
    return _finite(match.group(1)) if match else None


def enforce_position_ceiling(decision: Any, ceiling_pct: float) -> tuple[Any, str | None]:
    """Return ``(clipped_decision, warning)`` for a structured decision.

    ``position_pct`` is authoritative when present. If it is absent, a percentage
    in ``executive_summary`` is treated as the claimed size, so a model cannot
    bypass the ceiling by leaving the typed field empty.
    """
    ceiling = _finite(ceiling_pct)
    if ceiling is None or ceiling < 0:
        raise ValueError("the position ceiling must be a finite non-negative percentage")

    claimed = _finite(getattr(decision, "position_pct", None))
    if claimed is None:
        claimed = claimed_position_pct(getattr(decision, "executive_summary", ""))
    if claimed is None:
        return decision, None

    if claimed < 0:
        claimed = 0.0
    clipped = min(claimed, ceiling)
    if clipped == claimed:
        return decision.model_copy(update={"position_pct": clipped}), None
    warning = f"position size {claimed:g}% exceeds the {ceiling:g}% ceiling; clipped to {clipped:g}%"
    return decision.model_copy(update={"position_pct": clipped}), warning


def clip_free_text_decision(text: str, ceiling_pct: float) -> tuple[str, str | None]:
    """Clip a free-text ``Position Size: X%`` line to the ceiling."""
    ceiling = _finite(ceiling_pct)
    if ceiling is None or ceiling < 0:
        raise ValueError("the position ceiling must be a finite non-negative percentage")
    match = _POSITION_LINE_RE.search(text or "")
    if not match:
        return text, None
    claimed = _finite(match.group(2))
    if claimed is None or claimed <= ceiling:
        return text, None
    replacement = f"{match.group(1)}{ceiling:g}%"
    clipped = text[: match.start()] + replacement + text[match.end() :]
    warning = f"position size {claimed:g}% exceeds the {ceiling:g}% ceiling; clipped to {ceiling:g}%"
    return clipped, warning
