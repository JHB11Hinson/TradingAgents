# Design: input and decision guardrails (CHG-042)

- **Status:** approved by the owner's standing instruction ("all decisions yours except merge"),
  2026-11-21.
- **Scope:** `D1-REQ-SAFE-001`, `D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`.
- **Out of scope:** the debate schema (`CHG-043`), the token budget, the evaluation metrics.

## Intent

The three `must` safety requirements are the only remaining unimplemented musts. The framework
already refuses an unparseable rating (`REVIEW`), but it does not clean external text before a model
sees it, it still reads a rating out of an arbitrary free-text Portfolio Manager answer, and no
deterministic code constrains the position size a model claims.

The change adds one small `guardrails/` module and wires it into the existing seams. It does not
rewrite an agent or add a graph node.

## Approaches

1. **Guardrail module at the context and decision seams (chosen).** A pure `scrub_untrusted`
   neutralises instruction-like spans in retrieved text and tool output; a pure
   `enforce_position_ceiling` clips a claimed size; a strict free-text decision contract replaces
   `parse_rating` in the Portfolio Manager fallback. Pure functions are testable, deterministic and
   cheap.
2. **A model-based guard (LLM classifier).** Rejected: it adds a paid call, is nondeterministic,
   and can itself be injected.
3. **Per-vendor scrubbing.** Rejected: every new vendor would have to remember it; the context and
   tool seams already cover all retrieved text.

## Design

### `src/tradingagents/guardrails/`

- `instructions.py`
  - `ScrubResult(text: str, blocked: bool, matches: tuple[str, ...])`.
  - `scrub_untrusted(text: str, *, enabled: bool = True) -> ScrubResult`.
  - Detects a fixed corpus of instruction patterns (ignore/disregard previous instructions,
    system/developer/assistant role markers, "you are now", "new instructions", "reveal the system
    prompt", "call the tool", jailbreak markers, encoded zero-width separators).
  - Replaces each matched span with `[blocked instruction]` and leaves the evidence around it.
  - `enabled=False` is the negative-test switch; the shipped callers use the default.
- `positions.py`
  - `DEFAULT_MAX_POSITION_PCT = 10.0`.
  - `claimed_position_pct(text: str | None) -> float | None` parses "5%", "5 % of portfolio",
    "position size: 5". Returns `None` when no number is stated.
  - `enforce_position_ceiling(decision: PortfolioDecision, ceiling_pct: float) -> tuple[PortfolioDecision, str | None]`
    clips `decision.position_pct` (or a percentage in `executive_summary`) to the ceiling and
    returns a warning string when it clipped. Non-finite/negative values become 0.
  - `clip_free_text_decision(text: str, ceiling_pct: float) -> tuple[str, str | None]` does the
    same for the free-text fallback's `**Position Size**: X%` line.
- `decisions.py`
  - `validate_free_text_decision(text: str) -> str | None`: accepts only a text with exactly one
    explicit decision line (`Rating: <tier>` / `**Rating**: <tier>`, not a scale legend, not two
    conflicting labels). Returns the tier or `None`.
  - `review_decision(reason: str) -> str`: the canonical `Rating: REVIEW` markdown.

### Wiring

- `context/agent_layers.py`: `retrieved_block` scrubs its text (the one seam every report, memory
  lesson and manager plan passes through). `history_block` is model-generated and is not scrubbed.
- `agents/analysts/turn.py`: before the model call, every `ToolMessage` is replaced by its scrubbed
  copy. Tool call ids and the message order are preserved.
- `agents/analysts/sentiment_analyst.py`: the pre-fetched news, StockTwits and Reddit blocks are
  scrubbed before they enter the prompt.
- `agents/schemas.py`: `TraderProposal.position_pct` and `PortfolioDecision.position_pct` are new
  optional `float` fields (0-100), rendered as `**Position Size**: X%`.
- `agents/managers/portfolio_manager.py`:
  - the structured path applies `enforce_position_ceiling` before rendering;
  - the free-text path uses `validate_free_text_decision`; an answer without one explicit rating
    becomes the canonical `REVIEW` text and `final_rating = "REVIEW"`;
  - `final_decision_source` is added to the returned state (`structured`, `free_text`, `review`).
- `agents/trader/trader.py`: the structured proposal records `position_pct`; no ceiling is applied
  there because the trader is advisory. The Portfolio Manager remains the authoritative decision.
- `default_config.py`: `max_position_pct` (default `10.0`) and
  `TRADINGAGENTS_MAX_POSITION_PCT`; `graph/setup.py` passes it to the Portfolio Manager.

## Goals

- Every retrieved block and every tool result is scrubbed before a model sees it.
- A decision with no explicit rating, or with conflicting ratings, is `REVIEW`.
- A claimed position above the configured ceiling is clipped deterministically.
- The inherited PM fallback test still passes because its text carries one explicit `**Rating**`
  line.

## Non-goals

- No LLM-based guard, no network dependency, no new graph node.
- No change to the rating vocabulary or the `REVIEW` sentinel.
- No position sizing recommendation; the ceiling clips, it does not choose a size.

## Acceptance

- An adversarial corpus is blocked at 100%; disabling scrubbing makes the corpus test red.
- A malformed/ambiguous PM answer yields `REVIEW`; a clean free-text answer still yields its tier.
- A 50% claim under a 10% ceiling renders as 10%; a 10% claim is unchanged.
- `pytest -q` green, `ruff` clean, `python -m eval.run` green.
