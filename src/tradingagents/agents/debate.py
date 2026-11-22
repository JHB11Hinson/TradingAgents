"""Structured debate turns with a deterministic prose fallback.

The five debate nodes (bull, bear, aggressive, conservative, neutral) all follow
the same contract (D1-REQ-DEBATE-001, D1-REQ-DEBATE-002):

1. Prefer the provider's native structured output, ``with_structured_output``,
   bound to :class:`~tradingagents.agents.schemas.DebateTurn`.
2. If the provider has no structured mode, or it returns something that is not a
   ``DebateTurn`` (a weak model, a thinking model, a test double), invoke the
   model normally and adapt the prose into a valid turn.
3. Render the turn into the debate history and return the raw text alongside it,
   because the termination detector still digests the text the model produced.

The adapter never returns an empty required field: a prose-only provider keeps
the debate moving instead of turning every non-JSON answer into an outage.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from tradingagents import prompts
from tradingagents.agents.schemas import DebateEvidence, DebateTurn

logger = logging.getLogger(__name__)


class DebateTurnError(ValueError):
    """A model returned JSON that does not satisfy the DebateTurn contract."""

# A model often wraps the JSON object in a markdown fence, optionally labelled.
_FENCED_JSON = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)

# Explicit non-empty marker for a prose turn that never stated a convergence.
_NO_CONVERGENCE = "no convergence stated"
_NO_OPPONENT = "no opponent spoke"
_NO_CLAIM = "(no claim provided)"

def debate_turn_instruction() -> str:
    """The JSON contract appended to every debate task, from the versioned store.

    Kept in one place so the five speakers ask for exactly the same shape
    (D1-REQ-DEBATE-001, D1-REQ-GOV-012).
    """
    return prompts.load_prompt("shared.debate_turn_instruction").text


def render_debate_turn(turn: DebateTurn, side: str) -> str:
    """Render a debate turn as markdown with the speaker prefix.

    The six labelled sections are what enters the shared debate history, so the
    next speaker and the managers read the same structure the schema records.
    """
    evidence = "\n".join(f"- {item.source}: {item.quote}" for item in turn.evidence)
    return "\n".join([
        f"{side}:",
        "",
        f"**Claim**: {turn.claim}",
        "",
        "**Evidence**:",
        evidence,
        "",
        f"**Rebuttal**: {turn.rebuttal}",
        "",
        f"**Confidence**: {turn.confidence}",
        "",
        f"**Diverge**: {turn.diverge}",
        "",
        f"**Converge**: {turn.converge}",
    ])


def _parse_json_turn(text: str) -> DebateTurn | None:
    """Return the turn encoded in ``text``, accepting a bare or fenced object."""
    try:
        return DebateTurn.model_validate_json(text)
    except ValueError:
        pass
    for match in _FENCED_JSON.finditer(text):
        try:
            return DebateTurn.model_validate_json(match.group(1))
        except ValueError:
            continue
    return None


def parse_debate_turn(text: str, *, side: str, opponent: str = "") -> DebateTurn:
    """Parse a model answer into a schema-valid turn.

    Tries a bare JSON object, then a fenced JSON block, then adapts prose. The
    prose path keeps the model's words as the claim and evidence, records the
    opponent it was answering, and states explicitly that no convergence was
    given, so no required field is ever empty.
    """
    raw = (text or "").strip()
    parsed = _parse_json_turn(raw)
    if parsed is not None:
        return parsed
    if raw.startswith("{") or _FENCED_JSON.search(raw):
        raise DebateTurnError(
            "the model returned JSON that does not satisfy the DebateTurn contract "
            "(claim/evidence/rebuttal/confidence/diverge/converge are required and non-empty)"
        )

    claim = raw or _NO_CLAIM
    source = (side or "speaker").strip() or "speaker"
    return DebateTurn(
        claim=claim,
        evidence=[DebateEvidence(source=source, quote=claim)],
        rebuttal=(opponent or "").strip() or _NO_OPPONENT,
        confidence="low",
        diverge=claim,
        converge=_NO_CONVERGENCE,
    )


def invoke_debate_turn(
    llm: Any,
    prompt: Any,
    *,
    side: str,
    opponent: str = "",
) -> tuple[DebateTurn, str]:
    """Invoke one debate turn, returning the parsed turn and its raw text.

    Native structured output is used only when it yields an actual
    ``DebateTurn``; anything else (unsupported provider, ``None``, a bare
    ``MagicMock``) falls back to a plain ``llm.invoke`` plus
    :func:`parse_debate_turn`. The raw text is returned so the caller can keep
    ``turn_digest(raw_text)`` for the termination detector.
    """
    structured = None
    try:
        structured = llm.with_structured_output(DebateTurn)
    except Exception as exc:  # noqa: BLE001 - provider support varies widely
        logger.debug("%s: native structured output unavailable (%s)", side, exc)

    if structured is not None:
        try:
            result = structured.invoke(prompt)
        except Exception as exc:  # noqa: BLE001 - fall back on any provider error
            logger.warning(
                "%s: structured debate turn failed (%s); retrying as free text",
                side, exc,
            )
        else:
            if isinstance(result, DebateTurn):
                return result, result.model_dump_json()

    response = llm.invoke(prompt)
    raw = getattr(response, "content", response)
    if not isinstance(raw, str):
        raw = str(raw)
    return parse_debate_turn(raw, side=side, opponent=opponent), raw
