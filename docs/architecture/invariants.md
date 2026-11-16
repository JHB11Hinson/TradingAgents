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
| `INV-01` | A loop must stop itself on oscillation, stalled progress or budget exhaustion | `D1-REQ-TERM-001` | `src/tradingagents/graph/conditional_logic.py`, `setup.py` | **partial** — round bounds exist; oscillation/stall/budget detectors do not |
| `INV-02` | Every model call is assembled from the six context layers | `D1-REQ-CTX-001` | `src/tradingagents/context/` *(planned assembler)* | **planned** |
| `INV-03` | Assembled context stays within the token budget; critical constraints are re-injected verbatim | `D1-REQ-CTX-003` | `src/tradingagents/context/` *(planned assembler)*, `default_config.py` | **planned** |
| `INV-04` | External and retrieved text is scrubbed of instructions; hostile samples are blocked | `D1-REQ-SAFE-001` | `src/tradingagents/guardrails/` *(planned)* | **not implemented** |
| `INV-05` | A decision that fails schema validation is rejected/degraded, never emitted as tradeable | `D1-REQ-SAFE-002` | `src/tradingagents/agents/structured.py`, `rating.py`, `managers/portfolio_manager.py` | **partial** — schema + `REVIEW` exist; the free-text fallback can still parse a rating |
| `INV-06` | A deterministic position ceiling constrains the decision; model output cannot bypass it | `D1-REQ-SAFE-003` | `src/tradingagents/guardrails/` *(planned)*, `agents/managers/` | **not implemented** |

## 2. Invariant details

### INV-01 — Bounded loops (`D1-REQ-TERM-001`)

- **Statement.** A loop must stop itself on oscillation, stalled progress or budget exhaustion; it
  must never run unbounded.
- **Source.** `D1-REQ-TERM-001`; course D2.3; intro P16–P17 (termination discipline).
- **Enforcing component.** `graph/conditional_logic.py` (`max_debate_rounds`,
  `max_risk_discuss_rounds`) and `graph/setup.py` (`max_tool_rounds`, `wrap_up`). The oscillation,
  stall and budget detectors are **not implemented**.
- **Verification.** Constructed oscillation and stall cases terminate within the configured bounds;
  a negative test that removes the detector must turn red. The test is planned with the detector.
- **Operational fallback.** Stop the loop immediately; return the current best decision with
  `termination_reason = "unconverged"`; emit a `loop.terminated` telemetry event; open a bug-diary
  entry with the oscillation/stall evidence. Never continue to a second unbounded loop.
- **Status.** Partial. The hard round bounds are the current safety net; they are not a substitute
  for the detector.

### INV-02 — Layered context (`D1-REQ-CTX-001`)

- **Statement.** Every model call is assembled from exactly six layers, in order: identity,
  standing constraints, retrieved knowledge, conversation history, resumable state, current task.
- **Source.** `D1-REQ-CTX-001`; ADR-004; course D2.2.
- **Enforcing component.** `src/tradingagents/context/` (planned assembler). Today the layers exist
  scattered across `agents/context.py`, `state.py`, the debate state and the checkpoint.
- **Verification.** An assembler unit test asserts each layer's presence and source; the negative
  test removes one layer and must fail.
- **Operational fallback.** Do not issue the model call. Return `context_incomplete` to the
  orchestrator, use the last approved prompt template for that agent only, record a warning, and
  require a human review before retrying.
- **Status.** Planned (ADR-004 accepted as design; assembler not implemented).

### INV-03 — Budget and re-injection (`D1-REQ-CTX-003`)

- **Statement.** Assembled context must stay within the token budget, and critical constraints must
  be re-injected **verbatim** after compaction.
- **Source.** `D1-REQ-CTX-003`, `D1-REQ-COST-003`; ADR-004.
- **Enforcing component.** The planned context assembler and `default_config.py`
  (`context_budget_tokens`, default 50,000).
- **Verification.** A unit test asserts `assembled_tokens <= budget`; a second test hashes the
  constraint block before and after compaction and asserts it is byte-identical; a negative test
  removes the budget check and must turn red.
- **Operational fallback.** Compact from the lowest priority upward (P3 → P2 → P1), re-inject P0
  verbatim, and if the result is still over budget, abort the call with `budget_exceeded` and return
  `REVIEW`. Never call the provider with an over-budget prompt.
- **Status.** Planned.

### INV-04 — Instruction scrubbing (`D1-REQ-SAFE-001`)

- **Statement.** External and retrieved text must be scrubbed of instructions before it reaches the
  model; hostile samples must be blocked at 100% (zero tolerance).
- **Source.** `D1-REQ-SAFE-001`; course safety boundary; D2.3.
- **Enforcing component.** `src/tradingagents/guardrails/` (planned). No guardrail module exists
  today.
- **Verification.** A fixed adversarial corpus is blocked at 100%; the negative test disables
  scrubbing and must turn red.
- **Operational fallback.** Discard the offending text block; continue with the remaining evidence;
  record a `security.injection_blocked` event and alert the operator. Never pass the block through
  "for analysis".
- **Status.** Not implemented. Recorded in `DEBT-002`.

### INV-05 — Decision validity (`D1-REQ-SAFE-002`)

- **Statement.** A decision that fails schema validation must be rejected and degraded; it must
  never be emitted as a tradeable action.
- **Source.** `D1-REQ-SAFE-002`; `agents/rating.py` (`REVIEW` sentinel); ADR-003.
- **Enforcing component.** `agents/structured.py` (schema binding), `agents/rating.py` (`REVIEW`),
  `agents/managers/portfolio_manager.py` (final rating).
- **Verification.** A malformed portfolio-manager decision is rejected and produces `REVIEW`, with
  no tradeable action. The test must cover the **free-text fallback** path, not only the structured
  happy path. The negative test removes the `REVIEW` guard and must turn red.
- **Operational fallback.** Set `final_rating = REVIEW`; emit no tradeable action; record
  `decision.invalid_schema` with the malformed payload; require a human or a fresh run.
- **Status.** Partial. The structured path is guarded; `portfolio_manager.py` falls back to
  `llm.invoke(prompt).content` and `parse_rating`, so a parseable free-text rating can still become
  `final_rating` after a structured failure. This is a known gap, not an accepted design; it must be
  fixed or the invariant must be reworded with human approval.

### INV-06 — Authority boundary and position ceiling (`D1-REQ-SAFE-003`)

- **Statement.** Position size must pass a deterministic ceiling; model output must never bypass
  deterministic code to take effect.
- **Source.** `D1-REQ-SAFE-003`; ADR-003; course safety boundary.
- **Enforcing component.** `src/tradingagents/guardrails/` (planned) and the deterministic manager
  path. No ceiling exists today; the model only writes "position sizing" prose.
- **Verification.** A decision over the ceiling is clipped or rejected by deterministic code; a
  bypass-attempt negative test proves the model cannot set the final action directly.
- **Operational fallback.** The deterministic layer clamps the position to the ceiling or forces
  `REVIEW`; it records `position.ceiling_clipped` with the requested and applied values. The raw
  model value never reaches the decision.
- **Status.** Not implemented. Recorded in `DEBT-002`; the blueprint and permission model must not
  describe the boundary as fully enforced.

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
