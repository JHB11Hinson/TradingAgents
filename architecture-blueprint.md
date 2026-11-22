# Architecture blueprint (D2.1)

**Status:** accepted 2026-11-17. **Owner:** `@JHB11Hinson`. **Reviewers:** the active team.
**Requirement:** `D1-REQ-GOV-009`; course D2.1. **Reading order:** `AGENTS.md` first, then this file,
then `docs/req/requirements.yaml`, the ADRs and `docs/architecture/trace-matrix.md`.

This is the master constraint document the Plan agent reads. It states what the system is, where
its boundaries are, what is authoritative, how it is verified and what may change. It does not
replace the ADRs or the requirements registry; it constrains them.

---

## 1. Purpose and scope

The system analyses one instrument on one trade date and returns a researched rating plus a written
decision. It is an **analysis and decision-quality system**, not an order executor. The product
extends the inherited TradingAgents baseline incrementally; it does not rewrite the LangGraph
orchestration.

**In scope**

- the six-stage agent pipeline (analysts → debate → research manager → trader → risk → portfolio
  manager);
- a structured debate with a hard round bound and termination discipline;
- a layered context assembler with a token budget and constraint re-injection;
- a memory log and a reflection path;
- observability (trace and run manifest), evaluation, and deterministic safety guardrails.

**Non-goals** (guard against scope creep)

- do not replace LangGraph with an event bus, actors or an async queue;
- do not turn the project into a portfolio simulator or an order executor (`backtest.py` stays
  "decision-quality evaluation");
- do not add capability purely to inflate a score; every requirement must trace to the course
  material or a named frontier practice.

## 2. Architectural drivers

| # | Driver | Source |
|---|---|---|
| 1 | A single analysis is slow and token-burning | intro P20; `D1-REQ-COST-001/003`, `PERF-001` |
| 2 | The sub-agent debate is too free-form | intro P20; `D1-REQ-DEBATE-001/002/004` |
| 3 | Model output must not bypass deterministic code | course safety boundary; `SAFE-002/003` |
| 4 | The system must be auditable under human supervision | course core expectation; D5/D7 |
| 5 | The inherited baseline must stay green | `D1-REQ-GOV-001`; ADR-001 |

The primary tradeoff is **cost and latency vs analysis depth**. The context budget and the debate
bound are the two levers; both are configuration, not hard-coded constants.

## 3. System boundaries and components

| Element | Module | Boundary |
|---|---|---|
| Analysts | `src/tradingagents/agents/analysts/` | read vendor data through `dataflows/`, write a report; no vendor import |
| Researcher debate | `src/tradingagents/agents/researchers/` | consume analyst reports; emit debate turns |
| Research manager | `src/tradingagents/agents/managers/` | synthesise the debate into a research plan |
| Trader | `src/tradingagents/agents/trader/` | turn the plan into a trade proposal |
| Risk management | `src/tradingagents/agents/risk_mgmt/` | three-way risk discussion |
| Portfolio manager | `src/tradingagents/agents/managers/portfolio_manager.py` | final rating and decision |
| Agent contracts | `src/tradingagents/agents/` (`state.py`, `schemas.py`, `structured.py`, `rating.py`, `context.py`, `tools.py`, `post_screen.py`) | state shape, schemas, `REVIEW`, helpers, tool surface |
| Data access | `src/tradingagents/dataflows/` | the only layer that imports vendor libraries; point-in-time rules |
| Orchestration | `src/tradingagents/graph/` | graph wiring, routing, checkpoints, propagation |
| LLM access | `src/tradingagents/llm_clients/` | provider clients, model catalog, key handling |
| Memory | `src/tradingagents/memory/` | decision log, reflection, settlement |
| Versioned prompts | `src/tradingagents/prompts/` | read-only versioned prompt store; each entry is SHA-256 checked, a change adds a new version, and the twelve agent nodes load their role, preamble and task text from it at node call time (no second copy in `src/`) |
| Configuration | `src/tradingagents/default_config.py` | defaults and `TRADINGAGENTS_*` overrides |
| CLI | `src/cli/` | interactive and headless entry points, display, preferences |

**Boundary rules.** Each architectural element maps to exactly one module; a new element gets a new
module and a new row in `docs/code-governance/structural-constraints.md`. Vendor libraries are
imported only by `dataflows/` (enforced by `test/offline/test_layering.py`). New work extends the
baseline; a replacement needs an ADR and must keep the inherited tests green.

## 4. Agent workflow

```text
START
  │
  ├─ fundamentals analyst ─┐
  ├─ sentiment analyst    ─┤  (parallel)
  ├─ news analyst         ─┤
  └─ market analyst       ─┘
              │
              ▼
      bull/bear debate  ──►  research manager  ──►  trader
              │                                      │
              └──────────────►  risk discussion ◄─────┘
                                     │
                                     ▼
                              portfolio manager
                                     │
                                    END
```

The graph state and wiring are `agents/state.py`, `graph/setup.py` and
`graph/conditional_logic.py`. The debate is bounded by `max_debate_rounds`; an analyst tool loop is
bounded by `max_tool_rounds` and ends in `wrap_up`. The termination invariant (`TERM-001`) requires
oscillation, stall and budget detection; the round bounds are the current partial enforcement.

## 5. Authority boundary: advisory model output, authoritative deterministic code

- **Advisory:** everything a model produces — analyst reports, debate turns, the trader proposal,
  manager ratings. It informs a decision; it does not become one by itself.
- **Authoritative:** the deterministic code that validates and constrains it.
  - `agents/structured.py` binds a Pydantic schema;
  - `agents/rating.py` turns an unparseable rating into `REVIEW`;
  - a malformed final decision is rejected or degraded, never emitted as a tradeable action.

**Current enforcement, stated honestly**

- Schema validation and the `REVIEW` sentinel exist.
- The position ceiling (`SAFE-003`) is **not implemented**; it is a planned invariant.
- The portfolio-manager path still has a free-text fallback after a structured-output failure; the
  fallback can parse a rating. `SAFE-002` is therefore **partial**, not fully enforced.

The invariant register (`docs/architecture/invariants.md`) and the debt register record these gaps.
No change may describe the boundary as fully enforced until the negative tests exist.

## 6. Permissions

The permission model is **default deny, per-path whitelist**, with precedence `deny > ask > allow`.
The machine-readable source is `.opencode/permissions.jsonc`; the prose is
`docs/architecture/permission-model.md`; the summary is `AGENTS.md` §13. The three must list the same
whitelist.

Roles: `plan` (read-only), `build` (read + write + commands), `review` (read + drafts). The role
comes from the task, not from the `gh` account. `.opencode/rules.md` is human-only; the agent must
not write it. Secrets, `.env*`, keys and the home-directory credential stores are always denied.

## 7. Verification strategy

Three tiers, all required:

1. **Structural** — imports, module boundaries, permissions and architectural fitness functions.
   `test/offline/test_layering.py` enforces the data-layer boundary; review enforces the rest.
2. **Regression** — the full inherited and new offline suite. `pytest -q` must stay green; the
   inherited 1262-passed baseline is the floor.
3. **Behavioral** — quality thresholds and zero safety escapes. The fixed evaluation set and
   `python -m eval.run` are **planned** (`EVAL-001/002`, `DEBT-003`); until they land, the behavioral
   tier is a review checklist, not a gate.

The rules are in `docs/code-governance/verification-constraints.md`; the per-requirement mapping is
`docs/architecture/trace-matrix.md`. Every `fit_criterion` must have a test or an explicitly planned
evidence entry; every invariant must have a negative test and a concrete fallback.

## 8. Observability

A run must emit a machine-parsable trace (spans with phase, start/end and duration) and a run
manifest that aggregates tokens, estimated cost and wall-clock per phase (`OBS-001/002`). The
telemetry seam is an **in-process event seam**: a failing subscriber must not block the run
(`OBS-003`). It is additive; it does not turn the orchestration into an event-driven system.

The trace and manifest are implemented in CHG-034: `src/tradingagents/telemetry/` wraps every graph
step in a span and writes `telemetry/trace_<date>.json` plus `telemetry/manifest_<date>.json` next to
the state log. A subscriber failure is a warning, never a run failure. The event seam must not break
the public contracts in `AGENTS.md` §8.

## 9. Change policy

- **Requirement first.** Cite `D1-REQ-…` in the change card; register it first if it is missing.
- **Tests first.** Commit the tests before the implementation; each feature carries at least one
  negative test.
- **One change, one branch, one pull request.** Branch prefixes, commit trailers and review records
  follow `AGENTS.md` §12 and `docs/code-governance/merge-train.md`.
- **Safety-critical changes** (the contracts in `AGENTS.md` §8, the permission model, the guardrails)
  need an ADR and human approval.
- **Never weaken a gate or an inherited test** to make a change pass. A red gate is a finding, not a
  negotiation.
- **Docs co-evolve.** A requirement change updates this blueprint, the trace matrix, the invariant
  register and the affected governance files within one sprint.

## 10. Known gaps (must stay visible)

| Gap | Requirement | Where recorded |
|---|---|---|
| injection scrubbing is not implemented | `SAFE-001` | `DEBT-002`; invariants register |
| the position ceiling is not implemented | `SAFE-003` | `DEBT-002`; invariants register |
| the portfolio-manager free-text fallback can produce a rating after a schema failure | `SAFE-002` | invariants register; debt register |

A gap in this table is not permission to claim the capability. It is the opposite: it is the
evidence a reviewer uses to reject an overclaim.
