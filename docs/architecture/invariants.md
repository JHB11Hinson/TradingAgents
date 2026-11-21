# Invariant register (D2.3)

**Status:** accepted 2026-11-17. **Owner:** `@JHB11Hinson` (rules) with `@SY1433` (execution).
**Requirement:** `D1-REQ-GOV-008`; course D2.3.
**Related:** `docs/req/requirements.yaml`, `docs/architecture/trace-matrix.md`,
`docs/code-governance/structural-constraints.md`, `docs/code-governance/verification-constraints.md`.

An **invariant** is a non-negotiable rule with a zero-tolerance fit criterion. A violation is not a
quality regression; it is a defect that must stop the run and produce a concrete fallback. This
register is the authoritative list. It does not replace the requirements registry; it expands the
`type: invariant` entries and the zero-tolerance safety requirements.

**How to add an invariant.** Add a row to §1 and a block to §2. Every field is required: statement,
source requirement ID, enforcing component, verification method, and a concrete fallback (an action,
not "fix the bug"). A change to an invariant is a safety-critical change: it needs an ADR and human
approval (`AGENTS.md` §11).

---

## 1. Register at a glance

| ID | Invariant | Source | Enforcing component | Current status |
|---|---|---|---|---|
| `INV-01` | A loop must stop itself on oscillation, stalled progress or budget exhaustion | `D1-REQ-TERM-001` | `src/tradingagents/agents/termination.py`, `src/tradingagents/graph/conditional_logic.py`, `setup.py` | **implemented** (CHG-041) — hard bounds first, then the detector |
| `INV-02` | Every model call is assembled from the six context layers | `D1-REQ-CTX-001` | `src/tradingagents/context/` *(planned assembler)* | **planned** |
| `INV-03` | Assembled context stays within the token budget; critical constraints are re-injected verbatim | `D1-REQ-CTX-003` | `src/tradingagents/context/` *(planned assembler)*, `default_config.py` | **planned** |
| `INV-04` | External and retrieved text is scrubbed of instructions; hostile samples are blocked | `D1-REQ-SAFE-001` | `src/tradingagents/guardrails/instructions.py`, `context/agent_layers.py`, `agents/analysts/turn.py` | **implemented** (CHG-042) |
| `INV-05` | A decision that fails schema validation is rejected/degraded, never emitted as tradeable | `D1-REQ-SAFE-002` | `src/tradingagents/agents/structured.py`, `rating.py`, `guardrails/decisions.py`, `managers/portfolio_manager.py` | **implemented** (CHG-042) — the free-text path needs one explicit rating |
| `INV-06` | A deterministic position ceiling constrains the decision; model output cannot bypass it | `D1-REQ-SAFE-003` | `src/tradingagents/guardrails/positions.py`, `agents/managers/`, `default_config.py` | **implemented** (CHG-042) |
| `INV-07` | Telemetry is advisory: a failing subscriber or an unwritable trace must not fail or change a run | `D1-REQ-OBS-003` | `src/tradingagents/telemetry/`, `graph/trading_graph.py` | **implemented** (CHG-034) |
| `INV-08` | Every debate turn is a schema-valid `DebateTurn` with an explicit divergence and convergence | `D1-REQ-DEBATE-001`, `D1-REQ-DEBATE-002` | `src/tradingagents/agents/debate.py`, `agents/schemas.py`, the five debate nodes | **implemented** (CHG-043) — a JSON answer that fails validation aborts; prose is adapted |

## 2. Invariant details

### INV-01 — Bounded loops (`D1-REQ-TERM-001`)

- **Statement.** A loop must stop itself on oscillation, stalled progress or budget exhaustion; it
  must never run unbounded.
- **Source.** `D1-REQ-TERM-001`; course D2.3; intro P16–P17 (termination discipline).
- **Enforcing component.** `graph/conditional_logic.py` (`max_debate_rounds`,
  `max_risk_discuss_rounds`), `graph/setup.py` (`max_tool_rounds`, `wrap_up`) and
  `agents/termination.py` (`turn_digest`, `detect_termination`). The router checks the configured
  hard bound first; the detector only runs while the debate is below that bound.
- **Verification.** `test/offline/test_termination.py` covers oscillation (period 2 for the
  investment debate, period 3 for the risk debate), the three-identical-turn stall, budget
  precedence, the hard-bound-first ordering, one digest per turn in all five debate nodes, the
  managers' earliest-reason rule and the safe `loop.terminated` attributes. A negative test
  monkeypatches the detector away and proves the oscillating state falls through to the bound.
  `test_graph_end_to_end.py` pins the shipped replay to `termination_reason == ""`.
- **Operational fallback.** Stop the loop immediately; return the current best decision; set
  `termination_reason` to the detector reason (`oscillation`, `stall` or `budget_exhausted`); emit a
  `loop.terminated` span with `node` and `reason`; open a bug-diary entry with the oscillation/stall
  evidence. Never continue to a second unbounded loop.
- **Status.** Implemented (CHG-041); the hard round bounds remain the outer guarantee and the
  detector is an early stop inside them.

### INV-02 — Layered context (`D1-REQ-CTX-001`)

- **Statement.** Every model call is assembled from exactly six layers, in order: identity,
  standing constraints, retrieved knowledge, conversation history, resumable state, current task.
- **Source.** `D1-REQ-CTX-001`; ADR-004; course D2.2.
- **Enforcing component.** `src/tradingagents/context/assembler.py` (`assemble_context`,
  `ContextLayers`, `Layer`) and the twelve report agents, which declare their layers through
  `src/tradingagents/context/agent_layers.py`. The identity, reports, history, checkpoint and task
  evidence still live in `agents/context.py`, `state.py`, the debate state and the checkpoint; the
  assembler is the single place that orders and budgets them.
- **Verification.** An assembler unit test asserts each layer's presence and source; the negative
  test removes one layer and must fail (`test_missing_layer_is_rejected_before_rendering`).
- **Operational fallback.** Do not issue the model call. Return `context_incomplete` to the
  orchestrator, use the last approved prompt template for that agent only, record a warning, and
  require a human review before retrying.
- **Status.** Implemented (CHG-033).

### INV-03 — Budget and re-injection (`D1-REQ-CTX-003`)

- **Statement.** Assembled context must stay within the token budget, and critical constraints must
  be re-injected **verbatim** after compaction.
- **Source.** `D1-REQ-CTX-003`, `D1-REQ-COST-003`; ADR-004.
- **Enforcing component.** `src/tradingagents/context/assembler.py` (`RunBudget`,
  `run_budget_scope`, `_within_budget`, `_compact`, `_enforce_total`), `default_config.py`
  (`context_budget_tokens`, `context_call_budget_tokens`, `context_compaction_threshold`) and
  `graph/trading_graph.py` (`_budget_exhausted_state`, `_run_graph`, `stream_run`).
- **Verification.** `test/offline/test_context_assembler.py` asserts `assembled_tokens <= budget`;
  a second test hashes the constraint block before and after compaction and asserts it is
  byte-identical; a negative test removes the budget check and turns red.
  `test/offline/test_budget_degradation.py` proves the fallback on every entry point, including a
  real one-token budget and a negative test that removes the handler.
- **Operational fallback.** Compact from the lowest priority upward (P3 → P2 → P1), re-inject P0
  verbatim; if the result is still over budget, abort the call and end the run in `REVIEW` with
  `termination_reason = "budget_exhausted"`, write the state log, skip the memory log and keep the
  checkpoint. Never call the provider with an over-budget prompt.
- **Status.** Implemented (CHG-033); the run-boundary fallback added in CHG-040 (ADR-008).

### INV-04 — Instruction scrubbing (`D1-REQ-SAFE-001`)

- **Statement.** External and retrieved text must be scrubbed of instructions before it reaches the
  model; hostile samples must be blocked at 100% (zero tolerance).
- **Source.** `D1-REQ-SAFE-001`; course safety boundary; D2.3.
- **Enforcing component.** `src/tradingagents/guardrails/instructions.py` (`scrub_untrusted`),
  called by `context/agent_layers.retrieved_block`, `agents/analysts/turn.take_turn` and the
  sentiment analyst's pre-fetched blocks.
- **Verification.** `test/offline/test_guardrails.py` blocks a fixed adversarial corpus at 100%; the
  negative test removes the detector (`monkeypatch.setattr(instructions, "detect", ...)`) or the
  seam (`agent_layers.scrub_untrusted`) and observes the hostile text survive.
- **Operational fallback.** Replace the offending span with `[blocked instruction]`; keep the
  surrounding evidence; log the warning; alert the operator. Never pass the block through "for
  analysis".
- **Status.** Implemented (CHG-042); the patterns are the maintenance point, not a claim that every
  paraphrase is caught.

### INV-05 — Decision validity (`D1-REQ-SAFE-002`)

- **Statement.** A decision that fails schema validation must be rejected and degraded; it must
  never be emitted as a tradeable action.
- **Source.** `D1-REQ-SAFE-002`; `agents/rating.py` (`REVIEW` sentinel); ADR-003.
- **Enforcing component.** `agents/structured.py` (schema binding), `agents/rating.py` (`REVIEW`),
  `guardrails/decisions.py` (`validate_free_text_decision`, `review_decision`) and
  `agents/managers/portfolio_manager.py` (final rating).
- **Verification.** `test/offline/test_guardrails.py` drives a malformed and an ambiguous PM answer
  to `REVIEW`, and a clean `**Rating**: Sell` answer to `Sell`. The negative test removes the
  strict contract and the ambiguity would be accepted.
- **Operational fallback.** Set `final_rating = REVIEW` and `final_decision_source = "review"`; emit
  no tradeable action; record the reason in the decision text; require a human or a fresh run.
- **Status.** Implemented (CHG-042). The inheritance contract keeps a clean prose answer (one
  explicit rating) working, but an arbitrary parseable prose answer is no longer a decision.

### INV-06 — Authority boundary and position ceiling (`D1-REQ-SAFE-003`)

- **Statement.** Position size must pass a deterministic ceiling; model output must never bypass
  deterministic code to take effect.
- **Source.** `D1-REQ-SAFE-003`; ADR-003; course safety boundary.
- **Enforcing component.** `src/tradingagents/guardrails/positions.py`
  (`enforce_position_ceiling`, `clip_free_text_decision`, `claimed_position_pct`),
  `agents/managers/portfolio_manager.py` and `default_config.py` (`max_position_pct`, default 10%).
- **Verification.** `test/offline/test_guardrails.py` clips a 50% structured claim to 10%, clips a
  free-text `Position Size: 50%` line, leaves a 10% claim unchanged, and drives the PM node with a
  5% configured ceiling. The bypass attempt is a model that states 50% in either path; neither
  reaches the rendered decision.
- **Operational fallback.** Clip to the ceiling, log the requested and applied values, and keep the
  decision. A negative or non-finite claim becomes 0%.
- **Status.** Implemented (CHG-042).

### INV-07 — Telemetry never fails a run (`D1-REQ-OBS-003`)

- **Statement.** Telemetry observes a run; it never decides one. A subscriber that raises, a trace
  that cannot be written, or a price that is unknown must not stop the run or change its decision.
  `KeyboardInterrupt` and `SystemExit` are not subscriber failures and still stop the run.
- **Source.** `D1-REQ-OBS-003`; ADR-005.
- **Enforcing component.** `telemetry/events.py` (`Telemetry.emit` catches a subscriber and records a
  warning), `telemetry/spans.py` (the span still emits on an exception) and
  `graph/trading_graph.py` (`_write_telemetry` logs a failed write and returns).
- **Verification.** `test_raising_subscriber_does_not_block_and_is_recorded`,
  `test_keyboard_interrupt_is_never_swallowed`, `test_a_broken_subscriber_leaves_the_run_green` and
  `test_disabled_telemetry_writes_nothing`; the negative tests fail if the guard is removed.
- **Operational fallback.** Skip the trace/manifest write, log `Telemetry could not be written`,
  keep the decision and the state log, and report the failed subscriber in `manifest["warnings"]`.
- **Status.** Implemented (CHG-034).

### INV-08 — Structured debate turns (`D1-REQ-DEBATE-001`, `D1-REQ-DEBATE-002`)

- **Statement.** Every debate turn is a schema-valid `DebateTurn` containing a non-empty claim,
  evidence list, rebuttal, confidence, divergence and convergence; a malformed structured turn does
  not enter the debate.
- **Source.** `D1-REQ-DEBATE-001`, `D1-REQ-DEBATE-002`; ADR-011.
- **Enforcing component.** `agents/schemas.py` (`DebateTurn` validators),
  `agents/debate.py` (`parse_debate_turn`, `invoke_debate_turn`) and the five debate nodes.
- **Verification.** `test/offline/test_debate_turns.py` rejects missing/empty fields and an empty
  `converge`, parses JSON and prose, and records exactly one turn per node. The negative test sends a
  JSON object with an empty convergence and expects `DebateTurnError`.
- **Operational fallback.** A prose answer is adapted with an explicit "no convergence stated"
  marker; a claimed-JSON answer that fails validation aborts the run rather than entering a
  fabricated complete turn.
- **Status.** Implemented (CHG-043).

## 3. Relationship to the other artifacts

- **Requirements.** `docs/req/requirements.yaml` is the source of truth for the `D1-REQ-…` ids and
  the zero-tolerance fit criteria.
- **Trace matrix.** `docs/architecture/trace-matrix.md` maps each invariant to its component, test
  and runtime monitor.
- **Verification.** `docs/code-governance/verification-constraints.md` defines the negative-test and
  regression rules; this register names the tests.
- **Debt.** Gaps are recorded in `docs/debt-register.md`; an invariant may be *planned* but must not
  be described as enforced.
- **Change policy.** A change to an invariant, its enforcer or its fallback is a safety-critical
  change: ADR + human review.

## 4. Review checklist

- [ ] Every `type: invariant` requirement has a row in §1 and a block in §2.
- [ ] Every block names a source ID, an enforcer, a verification method and a concrete fallback.
- [ ] Every invariant has at least one negative test that fails when the invariant is violated.
- [ ] A planned invariant is marked **planned** or **partial**, never **done**.
- [ ] The trace matrix row and the debt register agree with the status here.
