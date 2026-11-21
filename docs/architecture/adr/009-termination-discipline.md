# ADR-009: Debate termination on oscillation, stall or budget exhaustion

- Status: **accepted** by the non-author review on PR #49 (`github-actions`, the automated
  `bot-review` channel requested by the owner). The coding agent applied the edit; it did not
  approve or merge.
- Date: 2026-11-21
- Deciders: the owner (`@JHB11Hinson`) and the non-author review channel recorded on PR #49
- Change: `CHG-041` — `D1-REQ-TERM-001`
- Related: ADR-003 (authority boundary), ADR-004 (context budget), ADR-008 (budget REVIEW),
  `AGENTS.md` §8/§11/§12, `D1-REQ-TERM-001`, `D1-REQ-DEBATE-004`, `INV-01`,
  `docs/architecture/runtime-policy-catalog.md`

## Context

Both debate loops had configurable round bounds and nothing else. `ConditionalLogic` compared the
turn count with `2 * max_debate_rounds` or `3 * max_risk_discuss_rounds`; a debate that repeats the
same argument, or one side stalling, still consumed every allowed round. `trace-matrix.md` claimed
oscillation/stall cases self-terminate and that a detector-removal negative test exists, but no
detector, no `termination_reason` and no test existed. `INV-01` said `partial`.

The budget path already existed after CHG-040: a `ContextBudgetExceeded` reaching the run boundary
becomes a deterministic `REVIEW`. The debate loops needed an early, deterministic stop signal; they
did not need a new graph node or an unbounded judge.

## Decision

**1. One pure module.** `src/tradingagents/agents/termination.py` exposes:

- `turn_digest(text)` — lowercase, collapse whitespace, SHA-256, first 16 hex characters. The
  speaker label is not part of the digest, so the same argument from either side compares equal.
- `detect_termination(digests, cycle)` — budget first, then oscillation, then stall.
- `STALL_REPEATS = 3`.

**2. The detector definitions.** With `turns = list(digests)`:

- **budget_exhausted** — an active `RunBudget` with `available(use_reserve=False) <= 0`;
- **oscillation** — at least `2 * cycle` turns, the last `cycle` equal to the `cycle` before them,
  and the block contains more than one distinct digest (`cycle` is 2 for the investment debate and 3
  for the risk debate);
- **stall** — the last three digests are identical;
- otherwise `None`.

Budget wins over either pattern because the next call cannot be made at all. A block of a single
repeated digest is a stall, not an oscillation.

**3. The hard bound stays first.** `ConditionalLogic` keeps its existing bound check before the
detector. The detector only runs while `count < max_turns`, so a debate that converged by bound
keeps an empty `termination_reason`. This ordering is what keeps the shipped replay unchanged: its
scripted model returns the same report, and the default risk debate's third identical turn is the
bound, not a stall.

**4. One digest per turn, in the state.** `InvestDebateState` and `RiskDebateState` gain
`turn_digests: list[str]`. The five debate nodes append `turn_digest(response.content)`; the
managers carry the list through when they rewrite their debate state. `create_initial_state()` sets
both lists to `[]`.

**5. The router routes; the manager records.** An oscillation, stall or budget reason routes to the
debate's terminal node (`Research Manager` or `Portfolio Manager`). The manager recomputes the
detector, sets the reason only when it fires before the bound and the field is still empty, and emits
a zero-duration `loop.terminated` span with `node` and `reason`. The earliest reason survives: the
Research Manager may set it first; the Portfolio Manager keeps it. The Portfolio Manager's own
budget catch overrides with `budget_exhausted` only when its own call is the one that ran out.

**6. The reason is observable.** `termination_reason` is already in `AgentState`, the initial state
and the state log (CHG-040). The vocabulary is fixed: `""`, `oscillation`, `stall`,
`budget_exhausted`. `reason` is added to `SAFE_ATTRIBUTE_KEYS`; the values are an enum, not free
text.

**7. Budget is a marker, not a shortcut.** The budget reason only routes the debate to its terminal
manager. That manager's ordinary call may then raise; CHG-040's run boundary turns it into the
deterministic `REVIEW`. The detector's unit cases and the router target are tested independently of
a fake successful manager.

## Alternatives considered

- **A model-as-judge termination check.** Rejected: it adds a paid, nondeterministic call to every
  debate turn and gives the model authority over stopping, which the authority boundary forbids.
- **A wall-clock or token-per-turn limit only.** Rejected as the sole mechanism: it is
  nondeterministic in CI and does not catch repetition that fits the budget. The cost ledger already
  covers the budget dimension.
- **Detector before the bound.** Rejected: the shipped scripted replay would classify a normal
  three-turn risk debate as a stall. The hard bound must win at the terminal turn.
- **A new graph node for termination.** Rejected: the router and the existing terminal managers
  already own the decision; a node would add an edge and a state merge for no new capability.

## Consequences

- A loop that repeats or stalls stops early, at a deterministic point, with a machine-readable
  reason in the state log and telemetry.
- The detector is conservative: three identical turns is not common in a real debate, and the
  threshold can be tuned by a reviewed change.
- The shipped replay is unchanged: both debates end at their default bounds and keep
  `termination_reason == ""`.
- The budget detector's end-to-end REVIEW depends on CHG-040; this PR is merged after it.
- Rollback is the reverted router call; the digest fields and the manager span are additive.

## Verification

- `test/offline/test_termination.py` covers the detector (both cycles, stall, progress, budget
  precedence), the hard-bound-first router, all five digest writers, both managers, the safe span,
  and a detector-removal negative test.
- `test/offline/test_graph_end_to_end.py` asserts the shipped replay's reason stays empty.
- Full offline suite, `ruff`, the non-quarantined `mypy` modules and `python -m eval.run` are green;
  the replay's ratings and token ratios are unchanged.
