# ADR-011: Structured debate turns with a prose adapter

- **Status:** accepted (CHG-043, 2026-11-21). Approved by the owner's standing instruction; the
  coding agent applied the edit and did not approve or merge.
- **Requirements:** `D1-REQ-DEBATE-001`, `D1-REQ-DEBATE-002`.
- **Related:** ADR-001, ADR-009 (termination), `agents/state.py`.

## Context

The five debate nodes emitted free prose. The course asks for a structured turn
(`claim`, `evidence`, `rebuttal`, `confidence`) and for Osborn's diverge-then-converge method. The
framework also supports providers without native structured output, and the inherited tests use
simple text doubles, so a hard "JSON or fail" rule would be an outage for those providers and a
regression for the suite.

## Decision

Add one `DebateTurn` schema and one adapter in `agents/debate.py`.

- Every turn carries `claim`, a non-empty `evidence` list of `(source, quote)`, `rebuttal`,
  `confidence` (`low|medium|high`), `diverge` and `converge`. All are required; the validators reject
  empty strings and an empty evidence list.
- `invoke_debate_turn` uses native structured output only when it returns an actual `DebateTurn`.
  Otherwise it calls the model normally and `parse_debate_turn` adapts the answer.
- The adapter tries a bare JSON object, then a fenced JSON block, then prose. A **prose** answer
  becomes a valid turn with the prose as its claim/evidence, the opponent as its rebuttal, and an
  explicit "no convergence stated" marker. An answer that **claims to be JSON** but fails validation
  raises `DebateTurnError`: a malformed structured turn is not silently re-read as prose.
- The rendered turn is what enters the shared debate history. `turn_records` keeps the raw dict per
  turn; `turn_digests` keeps the existing termination detector unchanged.

## Alternatives rejected

- **Fail on every non-JSON answer.** Rejected: it breaks every provider without structured output and
  the inherited debate tests; the adapter preserves the contract without pretending the prose had
  fields it did not.
- **A separate debate agent.** Rejected: duplicates five prompts and adds cost without new evidence.
- **Changing the termination digest to the rendered turn.** Rejected: it would change `TERM-001`'s
  tested behaviour for no benefit; the raw text is still the honest unit to compare.

## Consequences

- A structured provider is asked for the schema directly; a prose provider still produces a valid
  record. The distinction is visible in the record (`converge == "no convergence stated"`).
- An invalid JSON turn aborts the run instead of entering the debate as a fabricated complete turn.
- The risk debate's three-speaker cycle and the round bound are unchanged.
