# Design: clear DEBT-011, DEBT-012 and TERM-001 (batch B)

- **Status:** draft for human approval
- **Date:** 2026-11-21
- **Owner:** `@JHB11Hinson`
- **Scope:** `DEBT-011`, `DEBT-012`, `D1-REQ-TERM-001`
- **Out of scope:** the other open debts (`DEBT-001/002/004/005/006/009/010`), a live evaluation
  mode, prompt versioning, and routing the reflection call through the context assembler.

## Intent

Three gaps remain in the context/cost and termination area:

1. `DEBT-011` — the evaluation harness is deterministic and offline, but its headline ratio compares
   a synthetic replay with a recorded 120,000-token production estimate. The debt is not that the
   harness is offline; it is that the number does not isolate the budget's effect.
2. `DEBT-012` — when the run budget is exhausted, only the Portfolio Manager degrades to `REVIEW`.
   Every other agent raises and the whole run fails.
3. `D1-REQ-TERM-001` — the debate loops have round bounds but no oscillation, stall or budget
   detector. `docs/architecture/trace-matrix.md` claims a detector test that does not exist.

The goal is to close these three with evidence the course accepts (D2.3, D2.7, D4, D7 gate 4),
without turning any of them into a new subsystem.

## Constraints

- `AGENTS.md` §7: plan approval before code; tests before implementation; stop at surprises.
- `AGENTS.md` §8: `agents/state.py`, `graph/setup.py` and `graph/conditional_logic.py` are contracts.
  The two graph changes need an ADR and human review.
- `AGENTS.md` §9: `pytest -q` stays green; changed `src/**/*.py` passes `ruff`; a negative test per
  feature; every test names its requirement.
- `AGENTS.md` §12: one feature per pull request, tests-only commit first, review memo before the first
  `src/` commit, AI-use log updated, transcripts annotated.
- No live provider call in CI: `ADR-007` rejects a key, a cost per pull request and model drift.

---

## 1. DEBT-011 — make the cost evidence comparable

### Problem

`eval/baseline.json` records 120,000 tokens from an inherited production analysis. The shipped
replay measures 89,858 capped tokens (ratio 0.374 against two baseline analyses). The same replay
with the budget lifted measures 96,820 tokens (ratio 0.403 against the same baseline). Therefore the
0.374 already passes without the budget; the ratio proves the replay is smaller than the inherited
analysis, not that the cap saved half the tokens. The 50,000 cap does bind (89,858 vs 96,820), but
no metric says so.

### Approaches considered

- **Documentation only.** Cheapest, but it leaves the harness blind to a regression that stops
  compaction from binding. Rejected as the only action.
- **Live provider mode.** The right release check, but rejected for CI by `ADR-007`; it is not
  required by D7 gate 4 and would add a key and cost to every pull request. Not built.
- **Same-condition measurement.** Run every fixed-set case twice — once capped, once with the budget
  lifted — and report both numbers. Chosen. It is deterministic, offline, cheap (the set runs in
  under a second) and directly tests the mechanism.

### Design

- `CaseObservation` gains `uncapped_total_tokens: int | None`.
- `aggregate()` reports two new metrics:
  - `uncapped_tokens` — sum of the uncapped totals;
  - `capped_tokens_ratio` — `total_tokens / uncapped_tokens`, or `1.0` when a case has no uncapped
    measurement (so a missing measurement can never look like a saving).
- `eval/run.py` builds two replay analyzers: the shipped one and an uncapped one
  (`context_budget_tokens` very large, `context_decision_reserve_tokens = 0`), then combines their
  observations per case. Both use the same fixtures, model and graph.
- `eval/thresholds.yaml` adds `capped_tokens_ratio: {max: 0.98}`. Measured: 0.928. The bound is
  deliberately about the **mechanism** (the cap must bind) rather than a savings target: 1.0 means
  no compaction at all and fails, while benign fixture/report drift keeps the ratio well below 0.98.
  `total_tokens_ratio` and `est_cost_ratio` against the 120,000 baseline stay unchanged: they are the
  `COST-001` contract.
- The uncapped analyzer uses its own directory (`<results-dir>/uncapped`; the capped one uses
  `<results-dir>/capped`) so the memory log, cache and trace of one pass cannot leak into the other.
  It lifts both `context_budget_tokens` and `context_call_budget_tokens` to a very large value and
  sets `context_decision_reserve_tokens = 0`.
- An exception in the uncapped pass is a **failed case** (`cases_failed`), not a silent missing
  measurement. A successful case without `uncapped_total_tokens` reports ratio 1.0, which fails the
  0.98 threshold.
- `EvaluationReport.summary()` and `to_dict()` carry the uncapped total and the ratio, per case and
  in aggregate.
- Documentation: `evaluation-logbook.md` gains E-006 with the two numbers and the explicit statement
  that 0.403 already passes against the inherited baseline; `evaluation-table.md` and `ADR-007`
  gain the same caveat. `DEBT-011` is rewritten to the real defect (the ratio did not isolate the
  budget) and becomes `mitigated`: the remaining live release check is named as a trigger, not as CI
  work.

### Acceptance and tests

- A same-condition test shows capped 900 / uncapped 1,000 -> ratio 0.9 passes, and capped 1,000 /
  uncapped 1,000 -> ratio 1.0 fails the 0.98 threshold.
- A missing uncapped measurement yields ratio 1.0, not a silent pass.
- The shipped `python -m eval.run` prints both ratios and still exits 0.
- `test_eval_report.py`, `test_eval_cli.py` and `test_eval_thresholds.py` stay green.

---

## 2. DEBT-012 — every agent degrades to a deterministic REVIEW

### Problem

`ContextBudgetExceeded` is caught only in `portfolio_manager.py`. An analyst, researcher, trader or
risk debator that exhausts the run cap raises; `_run_graph` has no handler, so the run fails with an
exception and no decision. `runtime-policy-catalog.md` documents that failure, but the invariant
fallback says “return REVIEW”, which only the PM does.

### Approaches considered

- **Per-agent placeholder outputs.** Each node would invent a partial report. This risks fabricated
  evidence and touches every agent. Rejected.
- **Keep PM-only degradation and document it.** Already the status quo; the debt stays open and a
  real run can lose all work. Rejected for this batch.
- **Graph-level degradation.** Catch `ContextBudgetExceeded` at the run boundary and return a
  deterministic `REVIEW` state. Chosen: one handler, no fabricated reports, the authority boundary
  stays in deterministic code.

### Design

**One policy, three entry points.** The policy is: budget exhaustion produces a deterministic
`REVIEW` state with `termination_reason = "budget_exhausted"`; the state log is written; the memory
log is not; the checkpoint is preserved; telemetry status is `degraded`. It must hold on
`propagate()`, `_run_graph(debug=True)`, `stream_run()` and the CLI path.

- `_run_graph` catches `ContextBudgetExceeded` around the graph invocation (normal path). It builds
  a degraded state from the initial state:
  - `final_trade_decision`: `Rating: REVIEW` plus a sentence naming the cause;
  - `final_rating`: `REVIEW`;
  - `termination_reason`: `budget_exhausted`;
  - `memory_note`: a sentence for the report;
  - `investment_plan` and `trader_investment_plan`: empty strings, so the existing `_log_state`
    writer (which indexes them) can write the state log without a special case.
- `stream_run()` catches the same exception, yields the degraded state as its final value and sets
  its telemetry status to `degraded`. It builds the state from the input state, or from the last
  value state already received when resuming. If neither carries the ticker, it re-raises: without
  identity there is no state to report.
- `record_decision()` always writes the state log. It appends to the memory log unless the run ended
  in a **non-decision**: `final_rating == "REVIEW"` and `termination_reason == "budget_exhausted"`.
  A PM that still decided on the reserve keeps its normal memory entry.
- `_run_graph` and `src/cli/run.py` skip `clear_checkpoint_on_success()` under the same
  non-decision condition, so a later run with a larger budget can resume. The CLI still renders the
  REVIEW decision and the message that the budget ended the run.
- The Portfolio Manager keeps its existing catch (it can still decide with the reserve). It now sets
  `termination_reason = "budget_exhausted"` in its returned state; `_run_graph` derives telemetry
  status `degraded` from the final state rather than only from an exception. This keeps two
  degradation sites but one observable policy: the PM path and the graph path produce the same
  decision, reason and logging rule.
- `runtime-policy-catalog.md` and `invariants.md` (INV-03 fallback) are updated: budget exhaustion
  ends the run in `REVIEW`; it is not an uncaught failure.
- New ADR-008 records the decision, the alternatives and the consequences.

### Acceptance and tests

- With `context_budget_tokens=1`, `propagate()` returns a state whose `final_rating` is `REVIEW` and
  whose `termination_reason` is `budget_exhausted`; no exception escapes, and no memory entry is
  written.
- The state log contains the degraded decision, including the empty plan fields and the REVIEW
  reason; the checkpoint is preserved.
- A different exception (`RuntimeError`) still propagates: the handler is scoped to the budget
  exception.
- Negative test: removing the handler (monkeypatching it to re-raise) makes the tiny-budget run
  fail, proving the test exercises the handler.
- `stream_run()` with the same tiny budget yields a final state with `REVIEW`; the CLI merge path
  (`record_decision` + skip clear) leaves the checkpoint in place and writes no memory entry.
- A run whose debate stopped for budget but whose Portfolio Manager still decided on the reserve
  keeps its memory entry and clears its checkpoint: only a REVIEW non-decision is skipped.
- The existing PM budget test is updated to assert `termination_reason == "budget_exhausted"` and
  still returns `REVIEW`.

---

## 3. TERM-001 — oscillation, stall and budget detectors

### Problem

`ConditionalLogic` only checks `count` against the configured round bounds. The trace matrix claims
“oscillation/stall cases self-terminate; detector-removal negative test turns red”, but no detector,
no `termination_reason`, and no test exist. `INV-01` itself says “partial”.

### Detection contract

A pure module `src/tradingagents/agents/termination.py` provides:

- `turn_digest(text)` — lowercase, collapse whitespace, SHA-256, first 16 hex characters. The speaker
  label is not part of the digest, so the same argument from either side compares equal.
- `detect_termination(digests, cycle)`:
  - **budget** first: an active `RunBudget` with `available(use_reserve=False) <= 0` -> `budget_exhausted`;
  - **oscillation**: the last `cycle` digests equal the `cycle` before them, and the block contains
    more than one distinct digest -> `oscillation` (cycle 2 for the investment debate, 3 for the risk
    debate);
  - **stall**: the last three digests are identical -> `stall`;
  - otherwise `None`.
- The router keeps its existing hard-bound check **first**; the detector only runs while
  `count < max_turns`. That ordering is what keeps the shipped replay unchanged: its scripted model
  returns the same report, so a detector-only design would call the default three-turn risk debate a
  “stall”. At `count == max_turns` the debate has converged by bound, and
  `termination_reason` stays empty.
- **Reason precedence.** `termination_reason` is one field with the vocabulary `""`, `oscillation`,
  `stall`, `budget_exhausted`. The investment manager sets the reason only when the field is empty;
  the risk manager keeps an existing reason; the Portfolio Manager overrides with
  `budget_exhausted` only when its own call is the one that ran out of budget. If both debates
  terminate by detector, the earliest reason survives.

### Wiring

- `InvestDebateState` and `RiskDebateState` gain `turn_digests: list[str]`. The five debate nodes
  append `turn_digest(response.content)` to it. `AgentState` gains `termination_reason: str`.
- `ConditionalLogic` keeps the hard-bound check first, then calls `detect_termination`; a non-`None`
  reason routes to the debate's terminal node (`Research Manager` or `Portfolio Manager`).
- `create_research_manager` and `create_portfolio_manager` gain a `max_turns` argument (default 2 and
  3 so existing one-argument tests keep working). `GraphSetup` passes
  `2 * max_debate_rounds` and `3 * max_risk_discuss_rounds`. The manager recomputes the detector and
  sets `termination_reason` only when `count < max_turns`; at the bound it sets nothing.
- The manager also emits a zero-duration `loop.terminated` span with `node` and `reason`
  attributes. `reason` is added to `SAFE_ATTRIBUTE_KEYS`; the values are a fixed enum, not free text.
- `create_initial_state` sets `termination_reason=""` and both digest lists to `[]`; `_log_state`
  records `termination_reason`; body-less test states use `.get(..., [])`.
- **Budget reason is a marker, not a shortcut.** In the investment debate it routes to the Research
  Manager, whose ordinary call may then raise; PR B's handler turns that into the deterministic
  REVIEW. PR C is therefore merged after PR B for the end-to-end budget path, while the detector's
  unit cases run independently.
- New ADR-009 records the detector definitions, the graph wiring and the fallback: stop the loop,
  return the current best decision, set `termination_reason` to the detector reason, and emit
  `loop.terminated`. `INV-01` changes from “partial” to “implemented (CHG-xxx)” and its old
  `"unconverged"` wording is replaced by the vocabulary above; the trace matrix row loses its
  unbacked test claim and names the new tests.

### Acceptance and tests

- Detector unit cases: `a,b,a,b` -> oscillation; `a,b,c,a,b,c` -> oscillation; `a,a,a` -> stall;
  `a,b,c,d` -> `None`; exhausted budget -> `budget_exhausted`; no budget scope -> `None`.
- Router: an oscillating investment state with `max_debate_rounds=3` routes to `Research Manager`
  before the bound; a normal state keeps alternating; the existing path-map tests stay green.
- Manager: an oscillating state sets `termination_reason="oscillation"`; a state at the hard bound
  does not set a detector reason; an existing investment reason survives the risk manager; the PM's
  own budget exhaustion overrides it.
- Telemetry: a subscriber sees `loop.terminated` with the reason.
- Negative test: monkeypatching `detect_termination` to `None` makes the oscillating state run to
  the hard bound, proving the test exercises the detector.
- End-to-end with the shipped replay: metrics and ratings are unchanged; `termination_reason` is
  empty because both debates end at their default bounds (risk: three turns, three identical
  scripted reports, bound wins).

---

## 4. Pull-request plan

| PR | Scope | Safety-critical | ADR |
|---|---|---|---|
| PR A | DEBT-011: same-condition metric, threshold, report, docs | no | none (amend ADR-007) |
| PR B | DEBT-012: graph-level budget degradation, CLI/stream policy | yes | ADR-008 |
| PR C | TERM-001: termination detectors and wiring | yes | ADR-009 |

Merge order is A → B → C. PR B lands the run-level budget handler; PR C's budget-detector path
depends on it for the end-to-end REVIEW. Each PR follows the governance workflow: branch from
`main`; tests-only commit; test-approval review memo; implementation commit; docs and AI-use log;
full suite and six gates; non-author approval; no merge by the agent.

## 5. Risks and rollback

- **Double eval runtime and storage.** The fixed set is tiny; two passes stay well under a second.
  The two passes use separate result directories, so the report keeps only the capped pass's run
  artifacts plus the aggregate uncapped numbers. If the set grows, the uncapped pass becomes the
  first candidate for a cache.
- **False stall in real debates.** Three identical consecutive turns is a conservative signal; a
  legitimate repetition is unlikely. The detector can be tuned by a reviewed threshold change.
- **Degraded REVIEW hides partial work.** The state log and telemetry keep the trace; the decision is
  deliberately non-tradeable. A future change may add a partial-report policy, but that is a new
  decision, not this debt.
- **Rollback.** Each PR is additive and independently revertible. The `capped_tokens_ratio`
  threshold can be removed without touching the analyzer; the budget handler can be removed without
  touching agent code; the detectors can be disabled by reverting the router call.

## 6. Open decision

- Non-author review channel: the previous batches used `github-actions[bot]` via the `bot-review`
  label because the other members were unavailable. This design assumes the same channel unless the
  owner says otherwise. The agent still never approves or merges.
