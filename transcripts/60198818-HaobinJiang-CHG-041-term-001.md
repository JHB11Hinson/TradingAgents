# CHG-041 — TERM-001 termination discipline

**Member:** 60198818 HaobinJiang (@JHB11Hinson) · **Agent:** DeepSeek Harness · **Date:** 2026-11-21
**Scope:** `D1-REQ-TERM-001`, `D1-REQ-DEBATE-004`

An annotated session record: human turns are quoted verbatim, tool calls and results are summarised,
and each intervention says what it changed.

---

## 1. The handoff (human turn 1, verbatim)

> 继续PR C 任务

**Annotation — intervention type: scope.** The human continued the batch-B sequence after PR B was
merged. PR C is the TERM-001 slice of the approved design
(`docs/superpowers/specs/2026-11-21-debt-batch-b-design.md` §3) and the plan
`docs/superpowers/plans/2026-11-21-term-001-termination.md`. The standing rules from PR B still
apply: native (inline) execution, tests first, separate test and `src/` commits, no
`Test-Approval` placeholder in the test commit, `bot-review` for the non-author decision, and the
agent never approves or merges.

## 2. Pre-flight

- PR #48 (CHG-040) was merged at `0ac1578`; `main` was clean and level with `origin/main`.
- Baseline `.venv/bin/pytest -q` → 1432 passed, 1 skipped, 1 deselected.
- Branch `feat/CHG-041-term-001-termination` created from that head.

## 3. Tests first

- Created `test/offline/test_termination.py`: detector periods 2 and 3, the three-identical-turn
  stall, progress, budget precedence, the hard-bound-first router, one digest per turn in all five
  debate nodes, the managers' earliest-reason rule, the safe `loop.terminated` attributes, and a
  detector-removal negative test.
- First run: `ModuleNotFoundError: tradingagents.agents.termination` — red for the intended reason.
- Tests-only commit `af765d1`; the review record `92cd6cc` was pushed and the `bot-review` label
  produced an APPROVE from `github-actions` on PR #49 before any `src/` commit.

## 4. What the implementation changed

- `src/tradingagents/agents/termination.py`: `turn_digest`, `detect_termination`, `STALL_REPEATS`.
- `src/tradingagents/agents/state.py`, `graph/propagation.py`: `turn_digests` in both debate states,
  empty in the initial state.
- The five debate nodes (`researchers/bull_researcher.py`, `bear_researcher.py`,
  `risk_mgmt/aggressive_debator.py`, `conservative_debator.py`, `neutral_debator.py`): one digest per
  turn.
- `src/tradingagents/graph/conditional_logic.py`: the hard bound first, then the detector (cycle 2
  and cycle 3).
- `src/tradingagents/agents/managers/research_manager.py`, `portfolio_manager.py`: `max_turns`, the
  earliest reason, the `loop.terminated` span, and the PM's existing `budget_exhausted` catch.
- `src/tradingagents/graph/setup.py`: passes `2 * max_debate_rounds` and
  `3 * max_risk_discuss_rounds`.
- `src/tradingagents/telemetry/events.py`: `reason` in `SAFE_ATTRIBUTE_KEYS`.
- `docs/architecture/adr/009-termination-discipline.md`: the decision record.
- `docs/architecture/invariants.md` (INV-01), `trace-matrix.md`, `runtime-policy-catalog.md`: the
  shipped policy.
- `test/offline/test_graph_end_to_end.py`: the shipped replay keeps `termination_reason == ""`.

## 5. Evidence

- Tests-only head `af765d1`: red for the missing detector module.
- After the detector: the pure detector cases pass; router and node cases pass after C3; manager and
  telemetry cases pass after C4.
- `pytest -q test/offline/test_termination.py test_risk_router_path_map.py test_graph_end_to_end.py
  test_context_integration.py` → 77 passed.
- Full suite → 1460 passed, 1 skipped, 1 deselected.
- `ruff` on every changed `src/**/*.py` → clean; `mypy` on the changed non-quarantined modules →
  clean; `python -m eval.run --results-dir /tmp/opencode/eval-c` → 2 cases, 0 failed, exit 0, same
  ratings and ratios as PR A.
- Bot approval: PR #49, `github-actions` APPROVED on the tests-only head, then re-requested for the
  final head.

## 6. Boundaries kept

- The hard bound remains first; the shipped replay's bound-terminated debates keep an empty reason.
- No new graph node, edge, prompt or dependency.
- The budget marker does not fabricate a successful manager call; PR B's boundary still owns the
  end-to-end REVIEW.
- The agent does not approve or merge.
