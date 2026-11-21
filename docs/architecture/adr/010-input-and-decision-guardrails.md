# ADR-010: Input and decision guardrails

- **Status:** accepted (CHG-042, 2026-11-21). Approved by the owner's standing instruction; the
  coding agent applied the edit and did not approve or merge the pull request.
- **Requirements:** `D1-REQ-SAFE-001`, `D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`.
- **Supersedes:** none. Extends ADR-003's authority boundary.

## Context

The framework already refuses an unparseable rating, but three `must` safety requirements were
unimplemented: external text reached models unchanged, the Portfolio Manager's free-text fallback
could turn an arbitrary answer into a rating, and no deterministic code constrained a claimed
position size. All three are authority-boundary gaps, not model-quality gaps.

## Decision

Add one pure `src/tradingagents/guardrails/` package and wire it into existing seams.

1. **Instruction scrubbing.** `scrub_untrusted` neutralises a fixed corpus of instruction patterns
   in retrieved blocks (`context/agent_layers.retrieved_block`), analyst tool results
   (`agents/analysts/turn.take_turn`) and the sentiment analyst's pre-fetched vendor blocks. The
   scrubber is deterministic and offline; it is not an LLM guard.
2. **Decision contract.** The Portfolio Manager's free-text fallback accepts only a text with one
   explicit decision line and no conflicting rating label. Anything else becomes the canonical
   `REVIEW` decision; no tradeable rating is emitted.
3. **Position ceiling.** `PortfolioDecision.position_pct` and `TraderProposal.position_pct` carry a
   claimed size. `enforce_position_ceiling` clips it to `max_position_pct` (default 10%) before the
   decision is rendered; a free-text `Position Size: X%` line is clipped the same way. The trader is
   advisory; the Portfolio Manager is the authoritative application point.

## Alternatives rejected

- **An LLM classifier as the guard.** Costs a model call, is nondeterministic and can be injected.
- **Per-vendor scrubbing.** Every new vendor would have to remember it; the context and tool seams
  already cover all retrieved text.
- **Rejecting every free-text answer.** The inherited provider-fallback contract and its test
  require a clean prose answer to keep working; the strict contract keeps that case without
  accepting ambiguity.

## Consequences

- A hostile instruction is replaced with `[blocked instruction]`; the surrounding evidence stays.
- `max_position_pct` is an environment-overridable configuration key; a claim above it is clipped
  and logged, never silently accepted.
- `final_decision_source` records `structured`, `free_text` or `review`, which the evaluation uses
  for `D1-REQ-QUAL-001`.
- The scrubber is pattern-based. A paraphrase outside the corpus is not blocked; the corpus and the
  tests are the maintenance point, and the gap is stated in `INV-04` rather than hidden.
