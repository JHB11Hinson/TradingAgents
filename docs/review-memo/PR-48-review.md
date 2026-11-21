### PR-48 — CHG-040 DEBT-012 budget exhaustion degrades to REVIEW (test approval)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated test approval**,
  requested by the owner with the `bot-review` label.
- Head reviewed: tests-only head `c556c07`; no `src/` commit yet.
- Specification: the tests pin the DEBT-012 contract for `D1-REQ-COST-003` and
  `D1-REQ-TERM-001`: a budget-exhausted run ends in `REVIEW` with
  `termination_reason == "budget_exhausted"` on `propagate`, `_run_graph(debug=True)`, `stream_run`
  and the CLI; the state log is written with empty plan fields; the memory log is skipped only for a
  REVIEW non-decision; the checkpoint is preserved; a PM decision on the reserve is recorded; and a
  non-budget exception still propagates.
- Architecture: additive. One graph-boundary handler plus the existing Portfolio Manager catch;
  `AgentState` gains one string field. No node or edge change, no model call, no new dependency.
- Code and tests: the branch's only commit touches `test/offline/`; the suite is red for the
  intended missing handler/field, and no inherited test is weakened or skipped.
- Safety and efficiency: the fallback is deterministic and preserves work for a later run; the
  degraded state keeps the authority boundary in deterministic code.
- Record truth: this is a test-contract approval; `gate-5`/`gate-6` are red until the implementation
  and the AI-use entry land. The final approval is recorded after the gates are green.
- Tests: test/offline/test_budget_degradation.py, test/offline/test_token_budget.py
- Verdict: APPROVE
