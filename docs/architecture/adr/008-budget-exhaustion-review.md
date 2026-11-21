# ADR-008: Budget exhaustion ends a run in a deterministic REVIEW

- Status: **accepted** by the non-author review on PR #48 (`github-actions`, the automated
  `bot-review` channel requested by the owner). The coding agent applied the edit; it did not
  approve or merge.
- Date: 2026-11-21
- Deciders: the owner (`@JHB11Hinson`) and the non-author review channel recorded on PR #48
- Change: `CHG-040` — `DEBT-012`
- Related: ADR-003 (authority boundary), ADR-004 (context assembly), `AGENTS.md` §8/§11/§12,
  `D1-REQ-COST-003`, `D1-REQ-TERM-001`, `INV-03`, `docs/architecture/runtime-policy-catalog.md`

## Context

`ContextBudgetExceeded` was caught only in the Portfolio Manager. An analyst, researcher, trader or
risk debator that exhausted the run cap raised through `_run_graph`, so the run ended with an
exception and no decision. `runtime-policy-catalog.md` documented that failure, while `INV-03`'s
fallback already promised "return `REVIEW`" — a promise only the PM kept. The debt entry is
`DEBT-012`.

The context budget is a safety and cost guardrail (`COST-003`): a call that cannot fit must not be
sent to the provider. The question was where the *run* turns that aborted call into a report.

## Decision

**1. One policy at the run boundary.** A `ContextBudgetExceeded` that reaches a run boundary produces
a deterministic `REVIEW` state with `termination_reason = "budget_exhausted"`. The boundary is
`TradingAgentsGraph._run_graph` for `propagate()` and its debug path, and `stream_run()` for the CLI.
The exception is never converted into a fabricated partial report.

**2. The degraded state is explicit and loggable.** `_budget_exhausted_state(base_state, exc)` copies
the run's initial state and sets:

- `final_trade_decision`: `Rating: REVIEW` plus a sentence naming the budget as the cause;
- `final_rating`: `REVIEW`;
- `termination_reason`: `budget_exhausted`;
- `memory_note`: a sentence for the report;
- `investment_plan` and `trader_investment_plan`: empty strings, so the existing `_log_state` writer
  needs no special case.

`AgentState` gains `termination_reason: str`; `create_initial_state()` sets it to `""`; `_log_state`
records it.

**3. Logging rule: state log always, memory log only for a decision.** `record_decision()` always
writes the state log. It appends to the memory log unless the run ended in a **non-decision**:
`final_rating == "REVIEW"` **and** `termination_reason == "budget_exhausted"`. A Portfolio Manager
that still decided on the reserve keeps its normal memory entry: the reason alone is not enough to
suppress a call.

**4. Checkpoint rule: a non-decision keeps its work.** `_run_graph` and `src/cli/run.py` skip
`clear_checkpoint_on_success()` under the same non-decision condition, so a later run with a larger
budget can resume. An ordinary completed run still clears it.

**5. The Portfolio Manager keeps its catch.** It can still decide with the decision reserve. Its
exception return now includes the same `termination_reason`, and telemetry status is derived from the
final state (`degraded` versus `complete`) rather than only from an uncaught exception. This leaves
two degradation sites — the PM's own call and the graph boundary — but one observable policy.

**6. Only the budget exception degrades.** Every other exception, including a plain `RuntimeError`,
still propagates. With no identity (a `stream_run` resume that failed before its first state), the
stream re-raises rather than inventing a ticker.

**7. The CLI says what happened.** The CLI renders the `REVIEW` decision and prints a budget-specific
message instead of the generic unparseable-rating message.

## Alternatives considered

- **Per-agent placeholder outputs.** Rejected: a partial report invented by each agent risks
  fabricated evidence and touches every agent, including prompts.
- **Keep PM-only degradation and document it.** Rejected: the debt stays open and a real run can
  lose all its work. This is the status quo the ADR replaces.
- **Retry automatically with a larger budget.** Rejected: that hides the cost the cap exists to
  bound and silently turns one run into another. A caller may rerun deliberately; the checkpoint is
  kept for exactly that.
- **Catch every exception at the boundary.** Rejected: a provider failure or a programming error is a
  failure, not a budget outcome. Degrading it would hide real defects.

## Consequences

- A budget-exhausted run is visible and reproducible: the state log carries the decision and reason,
  the trace/manifest carry `status = degraded`, and the checkpoint survives.
- Partial work can be resumed, but it is not presented as a finished analysis. A future
  partial-report policy would be a new decision, not this ADR.
- The memory log never quotes a budget non-decision as a past call; the lesson set stays honest.
- The policy is testable without a provider: `test/offline/test_budget_degradation.py` covers the
  normal, debug, stream and CLI paths, the state-log shape, the memory/checkpoint rules, the PM
  reserve, the non-budget exception, a real one-token budget, and a handler-removal negative test.
- Rollback is the reverted handler: agent code and the graph wiring are unchanged.

## Verification

- `.venv/bin/pytest -q` — full offline suite green.
- `.venv/bin/ruff check` on the changed `src/**/*.py` files.
- `.venv/bin/mypy` on the changed non-quarantined modules.
- A real one-token run returns `REVIEW`, writes the state log with empty plan fields, writes no
  memory entry and leaves the checkpoint in place.
