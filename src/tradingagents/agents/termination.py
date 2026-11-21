"""Pure termination detectors for the two debate loops (D1-REQ-TERM-001, INV-01).

The graph asks this module whether a debate has stopped making progress. It is
deliberately free of graph and model state: the caller passes the turn digests
it already recorded, and the only ambient input is the run's token ledger.

Vocabulary: ``""`` (normal bound), ``oscillation``, ``stall`` and
``budget_exhausted``. The router checks its configured hard bound first; these
detectors only run while the debate is still below that bound, so a debate that
ends at its bound keeps an empty reason.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence

from tradingagents.context import current_budget

# Three identical consecutive turns is a stall. Two is not enough: a repeated
# opening or closing sentence is common and does not mean the debate is stuck.
STALL_REPEATS = 3


def turn_digest(text: str) -> str:
    """A stable short digest of one debate turn, ignoring case and spacing.

    The speaker label is not part of the digest, so the same argument from
    either side compares equal.
    """
    normalized = " ".join((text or "").lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def detect_termination(digests: Sequence[str], cycle: int) -> str | None:
    """Return why the debate must stop, or ``None`` while it still progresses.

    ``cycle`` is the debate's period: 2 for the bull/bear debate, 3 for the
    three-way risk debate. Budget exhaustion wins over either pattern because
    the next call cannot be made at all.
    """
    budget = current_budget()
    if budget is not None and budget.available(use_reserve=False) <= 0:
        return "budget_exhausted"

    turns = list(digests)
    if cycle > 0 and len(turns) >= 2 * cycle:
        previous, latest = turns[-2 * cycle : -cycle], turns[-cycle:]
        # A block of one repeated digest is a stall, not an oscillation.
        if latest == previous and len(set(latest)) > 1:
            return "oscillation"

    if len(turns) >= STALL_REPEATS and len(set(turns[-STALL_REPEATS:])) == 1:
        return "stall"
    return None
