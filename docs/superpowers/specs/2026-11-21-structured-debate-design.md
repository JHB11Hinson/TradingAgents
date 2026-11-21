# Design: structured debate turns and diverge-then-converge (CHG-043)

- **Status:** approved by the owner's standing instruction, 2026-11-21.
- **Scope:** `D1-REQ-DEBATE-001`, `D1-REQ-DEBATE-002`.
- **Out of scope:** the round bound (`DEBATE-004`, already done), termination (`TERM-001`), the
  risk debate's scoring.

## Intent

Every debate turn is currently free prose. The course asks for a requirements-engineering method
(Osborn's diverge-then-converge) and a structured object per turn. The change gives the five debate
nodes one schema and records it in state without adding a graph node.

## Approaches

1. **One `DebateTurn` schema plus a deterministic adapter (chosen).** The model is asked for a JSON
   object; providers with native structured output return it directly; a prose answer is adapted
   into the schema with the prose as its claim/evidence, so legacy providers and existing tests keep
   working. The rendered turn is what enters the debate history.
2. **Fail the run on any non-JSON turn.** Rejected: it would turn every non-structured provider into
   a total outage and would break the inherited debate tests.
3. **A separate debate agent.** Rejected: it duplicates prompts and adds cost.

## Design

- `agents/schemas.py`
  - `DebateEvidence(source: str, quote: str)` with both non-empty.
  - `DebateTurn(claim, evidence: list[DebateEvidence], rebuttal, confidence, diverge, converge)`.
    Every field is required and non-empty; `evidence` needs at least one item; `converge` and
    `diverge` are explicit (DEBATE-002). `confidence` is `low|medium|high`.
  - `parse_debate_turn(text, *, side, opponent="") -> DebateTurn`: try a JSON object, then a fenced
    JSON block, then adapt prose (`claim=text`, one evidence item quoting it, `rebuttal` = opponent
    or "no opponent spoke", `diverge=text`, `converge` = an explicit "no convergence stated"
    marker). Never returns a turn with an empty required field.
  - `render_debate_turn(turn, side) -> str`: markdown sections `**Claim**`, `**Evidence**`,
    `**Rebuttal**`, `**Confidence**`, `**Diverge**`, `**Converge**`, prefixed with the speaker.
- `agents/state.py`: `turn_records: list[dict]` in both debate states; one record per turn.
- The five debate nodes (bull, bear, aggressive, conservative, neutral):
  - ask for the schema in the task text;
  - call `invoke_debate_turn(llm, prompt, side, opponent)` (a new helper in
    `agents/structured.py` or `agents/debate.py`) that tries native structured output, then falls
    back to `llm.invoke` plus `parse_debate_turn`;
  - append the rendered turn to history and the `turn.model_dump()` to `turn_records`;
  - keep `turn_digest(response_text)` on the raw text for the termination detector.
- `graph/propagation.py` initialises `turn_records: []`.
- Managers copy `turn_records` through so a resumed state keeps them.
- `docs/architecture/invariants.md` gets an invariant for a structurally valid turn; the trace
  matrix and `structural-constraints.md` gain the schema reference.

## Acceptance

- `DebateTurn` rejects a turn missing any of claim/evidence/rebuttal/confidence and any turn with an
  empty `diverge` or `converge`.
- A structured response produces a rendered turn with all six sections; a prose response produces a
  schema-valid turn and still reaches the next speaker.
- All five nodes append exactly one `turn_record` and one digest.
- `pytest -q` green and the eval replay green.
