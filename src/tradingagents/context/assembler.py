"""Layered context assembler (D1-REQ-CTX-001/002/003, D1-REQ-COST-003).

Every model call is assembled from six layers, in a fixed order, by this
module. The pipeline records ``dedupe -> prioritize -> budget -> compact ->
assemble``; under the budget it returns the agent's own prompt unchanged, so
the common case is a no-op (ADR-004). Over budget it compacts from the lowest
priority upward, never drops the P0 block, and re-injects P0 verbatim.

Token counts use the deterministic estimator ``ceil(characters / 4)`` so a run
is reproducible on any machine (ADR-004 section 3). ``context_budget_tokens``
caps a whole run; ``context_call_budget_tokens`` caps one call.

The run ledger records the **whole request** the model receives: the assembled
text plus the layers the prompt template carries separately (``render=False``,
such as ``state["messages"]``). ``context_decision_reserve_tokens`` keeps a
slice of the run cap for the final decision, so compaction can never spend the
Portfolio Manager's turn (ADR-004 amendment, 2026-11-20).
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any

TOKEN_CHARS = 4
DEFAULT_BUDGET = 50_000
DEFAULT_COMPACTION_THRESHOLD = 0.8

STAGES = ("dedupe", "prioritize", "budget", "compact", "assemble")


class Layer(StrEnum):
    """The six context layers, in emission order (ADR-004 section 1)."""

    IDENTITY = "identity"
    CONSTRAINTS = "constraints"
    RETRIEVED = "retrieved"
    HISTORY = "history"
    RESUMABLE = "resumable"
    TASK = "task"


LAYER_ORDER: tuple[Layer, ...] = (
    Layer.IDENTITY,
    Layer.CONSTRAINTS,
    Layer.RETRIEVED,
    Layer.HISTORY,
    Layer.RESUMABLE,
    Layer.TASK,
)

# P0 is never dropped or shortened; P1 is retrieved knowledge, P2 history and
# P3 resumable state. Compaction works P3 -> P2 -> P1.
P0_LAYERS = frozenset({Layer.IDENTITY, Layer.CONSTRAINTS, Layer.TASK})

# Per-layer ceilings as a fraction of the call budget (ADR-004 section 2).
CEILING_FRACTIONS: Mapping[Layer, float] = {
    Layer.IDENTITY: 0.05,
    Layer.CONSTRAINTS: 0.10,
    Layer.RETRIEVED: 0.45,
    Layer.HISTORY: 0.30,
    Layer.RESUMABLE: 0.05,
    Layer.TASK: 0.10,
}


class ContextIncomplete(ValueError):
    """A required layer is missing, so no prompt may be rendered."""


class ContextBudgetExceeded(RuntimeError):
    """The call cannot fit the budget even after compaction; do not call the model."""


@dataclass(frozen=True)
class ContextBlock:
    """One piece of evidence in one layer.

    ``render`` is False for evidence the prompt template already carries (for
    example ``state["messages"]``, passed to the model separately). Such a
    block is still budgeted, but it is not duplicated into the assembled text.
    """

    layer: Layer
    source: str
    text: str
    render: bool = True


@dataclass(frozen=True)
class Drop:
    """A block removed by dedupe or by the budget."""

    layer: Layer
    source: str
    reason: str


@dataclass(frozen=True)
class ContextLayers:
    """A complete request: every layer, its blocks and their sources."""

    blocks: Mapping[Layer, tuple[ContextBlock, ...]]

    def missing(self) -> tuple[Layer, ...]:
        """Layers with no non-empty block, in emission order."""
        return tuple(
            layer
            for layer in LAYER_ORDER
            if not any(block.text.strip() for block in self.blocks.get(layer, ()))
        )

    def sources(self) -> dict[Layer, tuple[str, ...]]:
        """Declared sources per layer, in emission order."""
        return {
            layer: tuple(block.source for block in self.blocks.get(layer, ()))
            for layer in LAYER_ORDER
        }


@dataclass(frozen=True)
class AssembledContext:
    """The result of one assembly pass, auditable after the call."""

    layers: tuple[Layer, ...]
    sources: Mapping[Layer, tuple[str, ...]]
    text: str
    tokens: int
    request_tokens: int
    budget: int
    compacted: bool
    re_injected: bool
    dropped: tuple[Drop, ...]
    stages: tuple[str, ...]
    p0_digest: str
    p0_digest_before: str
    layer_tokens: Mapping[Layer, int]


class RunBudget:
    """The token ledger shared by every call in one run."""

    def __init__(
        self,
        cap: int,
        call_budget: int | None = None,
        compaction_threshold: float = DEFAULT_COMPACTION_THRESHOLD,
        reserve: int = 0,
    ) -> None:
        self.cap = int(cap)
        self.call_budget = int(cap if call_budget is None else call_budget)
        self.compaction_threshold = float(compaction_threshold)
        # The slice ordinary calls may not touch; the final decision may.
        self.reserve = max(0, min(int(reserve), self.cap))
        self._calls: list[dict[str, Any]] = []
        self._max_call_tokens = 0
        self._compacted_calls = 0

    @property
    def spent(self) -> int:
        return sum(call["tokens"] for call in self._calls)

    @property
    def remaining(self) -> int:
        return max(0, self.cap - self.spent)

    def available(self, use_reserve: bool = False) -> int:
        """The cap for the next call: the per-call cap and what is left of the run.

        An ordinary call cannot reach into the decision reserve; the final
        decision call (``use_reserve=True``) may.
        """
        headroom = self.remaining if use_reserve else self.remaining - self.reserve
        return max(0, min(self.call_budget, headroom))

    def record(self, agent: str, tokens: int, compacted: bool) -> None:
        self._calls.append({"agent": agent, "tokens": int(tokens)})
        self._max_call_tokens = max(self._max_call_tokens, tokens)
        if compacted:
            self._compacted_calls += 1

    def snapshot(self) -> dict[str, Any]:
        """A JSON-safe summary for the run log (COST-003)."""
        return {
            "budget": self.cap,
            "call_budget": self.call_budget,
            "reserve": self.reserve,
            "total_tokens": self.spent,
            "max_call_tokens": self._max_call_tokens,
            "calls": [dict(call) for call in self._calls],
            "compacted_calls": self._compacted_calls,
        }


_CURRENT: ContextVar[RunBudget | None] = ContextVar("tradingagents_context_budget", default=None)


def current_budget() -> RunBudget | None:
    """The ledger of the run in progress, or None outside ``run_budget_scope``."""
    return _CURRENT.get()


@contextmanager
def run_budget_scope(config: Mapping[str, Any]):
    """Open a run-level budget from the run configuration.

    ``context_budget_tokens`` caps the run and ``context_call_budget_tokens``
    caps one call; both default to 50,000. ``context_decision_reserve_tokens``
    of the run cap is withheld from ordinary calls so the final decision can
    still be made (ADR-004 amendment). Agents read the ledger through
    :func:`assemble_context` and the graph snapshots it into the state log.
    """
    cap = int(config.get("context_budget_tokens", DEFAULT_BUDGET))
    call_budget = int(config.get("context_call_budget_tokens", cap))
    threshold = float(config.get("context_compaction_threshold", DEFAULT_COMPACTION_THRESHOLD))
    reserve = int(config.get("context_decision_reserve_tokens", 0))
    budget = RunBudget(cap, call_budget, threshold, reserve)
    token = _CURRENT.set(budget)
    try:
        yield budget
    finally:
        _CURRENT.reset(token)


def estimate_tokens(text: str) -> int:
    """Deterministic estimate: four characters per token, rounded up."""
    return (len(text) + TOKEN_CHARS - 1) // TOKEN_CHARS


def make_layers(**blocks_by_layer: Iterable[ContextBlock]) -> ContextLayers:
    """Build a request from six keyword arguments, one per layer."""
    unknown = set(blocks_by_layer) - {layer.value for layer in LAYER_ORDER}
    if unknown:
        raise TypeError(f"unknown context layer(s): {', '.join(sorted(unknown))}")
    blocks = {
        layer: tuple(blocks_by_layer.get(layer.value, ()))
        for layer in LAYER_ORDER
    }
    return ContextLayers(blocks=blocks)


def assemble_context(
    layers: ContextLayers,
    original: str | None = None,
    budget: RunBudget | None = None,
    agent: str = "context",
    use_reserve: bool = False,
) -> AssembledContext:
    """Run the assembly pipeline for one model call.

    ``original`` is the prompt the agent already builds; it is returned
    unchanged while the request is within budget (ADR-004 section 5).
    ``budget`` defaults to the ledger opened by :func:`run_budget_scope`.
    ``use_reserve`` lets the final decision call spend the withheld reserve.
    """
    missing = layers.missing()
    if missing:
        raise ContextIncomplete(
            "missing context layer(s): " + ", ".join(layer.value for layer in missing)
        )

    run = budget if budget is not None else current_budget()
    if run is None:
        run = RunBudget(DEFAULT_BUDGET)
    cap = run.available(use_reserve)
    if cap <= 0:
        raise ContextBudgetExceeded(
            f"run token budget exhausted before the {agent} call ({run.spent}/{run.cap})"
        )

    kept, dropped = _dedupe(layers)
    layer_tokens = _layer_tokens(kept)
    p0_text_before = _p0_text(kept)
    p0_digest_before = _digest(p0_text_before)
    p0_tokens = estimate_tokens(p0_text_before)
    original_tokens = estimate_tokens(original) if original is not None else None

    within = _within_budget(layer_tokens, cap, run.compaction_threshold)
    if original_tokens is not None and original_tokens > cap:
        within = False

    if within:
        text = original if original is not None else _render(kept)
        tokens = original_tokens if original_tokens is not None else estimate_tokens(text)
        # Layers the template carries separately are still part of the request.
        request_tokens = tokens + _non_rendered_tokens(kept)
        compacted = False
        re_injected = False
    else:
        if p0_tokens > cap:
            raise ContextBudgetExceeded(
                f"P0 constraints need {p0_tokens} tokens, above the {cap}-token cap; "
                f"refusing to call {agent}"
            )
        compacted_blocks = _compact(kept, cap, dropped)
        compacted_blocks = _enforce_total(compacted_blocks, cap, dropped)
        text = _render(compacted_blocks)
        tokens = estimate_tokens(text) + _non_rendered_tokens(compacted_blocks)
        if tokens > cap:
            raise ContextBudgetExceeded(
                f"assembled context needs {tokens} tokens, above the {cap}-token cap"
            )
        kept = compacted_blocks
        layer_tokens = _layer_tokens(kept)
        request_tokens = tokens
        compacted = True
        re_injected = True

    run.record(agent, request_tokens, compacted)

    return AssembledContext(
        layers=LAYER_ORDER,
        sources={layer: tuple(block.source for block in kept[layer]) for layer in LAYER_ORDER},
        text=text,
        tokens=tokens,
        request_tokens=request_tokens,
        budget=cap,
        compacted=compacted,
        re_injected=re_injected,
        dropped=tuple(dropped),
        stages=STAGES,
        p0_digest=_digest(_p0_text(kept)),
        p0_digest_before=p0_digest_before,
        layer_tokens=layer_tokens,
    )


def _within_budget(
    layer_tokens: Mapping[Layer, int],
    cap: int,
    threshold: float = DEFAULT_COMPACTION_THRESHOLD,
) -> bool:
    """True when the context needs no compaction.

    Two checks: the whole request must stay under the compaction threshold
    (headroom for the model's reply), and every non-P0 layer must stay under
    its ceiling. P0 may exceed its nominal share because it is never dropped.
    """
    total = sum(layer_tokens.values())
    if total > cap * threshold:
        return False
    for layer, fraction in CEILING_FRACTIONS.items():
        if layer in P0_LAYERS:
            continue
        if layer_tokens.get(layer, 0) > cap * fraction:
            return False
    return True


def _dedupe(layers: ContextLayers) -> tuple[dict[Layer, list[ContextBlock]], list[Drop]]:
    """Keep one copy of repeated evidence, first occurrence wins."""
    seen: set[str] = set()
    kept: dict[Layer, list[ContextBlock]] = {layer: [] for layer in LAYER_ORDER}
    dropped: list[Drop] = []
    for layer in LAYER_ORDER:
        for block in layers.blocks.get(layer, ()):
            key = " ".join(block.text.split())
            if key and key in seen:
                dropped.append(Drop(layer, block.source, "dedupe"))
                continue
            if key:
                seen.add(key)
            kept[layer].append(block)
    return kept, dropped


def _compact(
    blocks: dict[Layer, list[ContextBlock]],
    cap: int,
    dropped: list[Drop],
) -> dict[Layer, list[ContextBlock]]:
    """Trim every non-P0 layer to its ceiling, lowest priority first."""
    out = {layer: list(items) for layer, items in blocks.items()}
    for layer in (Layer.RESUMABLE, Layer.HISTORY, Layer.RETRIEVED):
        ceiling = int(cap * CEILING_FRACTIONS[layer])
        out[layer] = _fit(out[layer], ceiling, layer, dropped)
    return out


def _fit(
    blocks: list[ContextBlock],
    ceiling: int,
    layer: Layer,
    dropped: list[Drop],
) -> list[ContextBlock]:
    """Shorten a layer to ``ceiling`` tokens, removing its oldest evidence first."""
    total = sum(estimate_tokens(block.text) for block in blocks)
    if total <= ceiling:
        return list(blocks)
    kept, removed = _shrink(blocks, total - ceiling, layer)
    dropped.extend(removed)
    return kept


def _shrink(
    blocks: list[ContextBlock],
    amount: int,
    layer: Layer,
) -> tuple[list[ContextBlock], list[Drop]]:
    """Remove at least ``amount`` tokens from the end of a layer."""
    kept = list(blocks)
    removed: list[Drop] = []
    need = amount
    while need > 0 and kept:
        last = kept[-1]
        tokens = estimate_tokens(last.text)
        if tokens > need:
            kept[-1] = replace(last, text=last.text[: (tokens - need) * TOKEN_CHARS])
            need = 0
        else:
            kept.pop()
            removed.append(Drop(layer, last.source, "budget"))
            need -= tokens
    return kept, removed


def _enforce_total(
    blocks: dict[Layer, list[ContextBlock]],
    cap: int,
    dropped: list[Drop],
) -> dict[Layer, list[ContextBlock]]:
    """Shrink P3 -> P2 -> P1 until the rendered context fits the hard cap."""
    out = {layer: list(items) for layer, items in blocks.items()}
    while True:
        total = _assembled_tokens(out)
        if total <= cap:
            return out
        for layer in (Layer.RESUMABLE, Layer.HISTORY, Layer.RETRIEVED):
            if out[layer]:
                out[layer], removed = _shrink(out[layer], total - cap, layer)
                dropped.extend(removed)
                break
        else:
            raise ContextBudgetExceeded(
                f"assembled context needs {total} tokens, above the {cap}-token cap"
            )


def _assembled_tokens(blocks: Mapping[Layer, list[ContextBlock]]) -> int:
    return estimate_tokens(_render(blocks)) + _non_rendered_tokens(blocks)


def _non_rendered_tokens(blocks: Mapping[Layer, list[ContextBlock]]) -> int:
    return sum(
        estimate_tokens(block.text)
        for layer in LAYER_ORDER
        for block in blocks.get(layer, ())
        if not block.render
    )


def _render(blocks: Mapping[Layer, list[ContextBlock]]) -> str:
    """Join the rendered layers in emission order."""
    parts = [
        block.text.strip()
        for layer in LAYER_ORDER
        for block in blocks.get(layer, ())
        if block.render and block.text.strip()
    ]
    return "\n\n".join(parts)


def _p0_text(blocks: Mapping[Layer, list[ContextBlock]]) -> str:
    parts = [
        block.text.strip()
        for layer in LAYER_ORDER
        if layer in P0_LAYERS
        for block in blocks.get(layer, ())
        if block.text.strip()
    ]
    return "\n\n".join(parts)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _layer_tokens(blocks: Mapping[Layer, list[ContextBlock]]) -> dict[Layer, int]:
    return {
        layer: sum(estimate_tokens(block.text) for block in blocks.get(layer, ()))
        for layer in LAYER_ORDER
    }
