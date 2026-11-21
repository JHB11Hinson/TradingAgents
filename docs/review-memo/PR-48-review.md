### PR-48 — CHG-040 DEBT-012 budget exhaustion degrades to REVIEW (implementation head)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label.
- Head reviewed: implementation head `cb36980`; the docs/AI-use commit follows it.
- Specification: a budget-exhausted run ends in `REVIEW` with
  `termination_reason = "budget_exhausted"` on `propagate`, `_run_graph(debug=True)`, `stream_run`
  and the CLI. The state log is written with empty plan fields; the memory log is skipped only for
  that REVIEW non-decision; the checkpoint is preserved; a Portfolio Manager decision on the reserve
  is recorded and clears its checkpoint; a non-budget exception still propagates.
- Architecture: one graph-boundary handler plus the existing PM catch; `AgentState` gains one string
  field. No node, edge, prompt, dependency or default-cap change. ADR-008 records the decision and
  the runtime catalog, INV-03, trace matrix and debt register describe the shipped policy.
- Code and tests: `pytest -q` -> 1432 passed, 1 skipped, 1 deselected; `ruff` clean on the changed
  `src/**/*.py`; `mypy` clean on the changed non-quarantined modules; `python -m eval.run` -> 2 cases,
  0 failed, exit 0. The new test file covers every entry point, the real one-token budget, the shared
  logging/checkpoint rules and a handler-removal negative test.
- Safety and efficiency: deterministic fallback, no model call added, recoverable work kept. The
  resume-without-identity case re-raises rather than inventing identity.
- Record truth: the test-contract approval is superseded by this implementation-head approval; both
  are recorded in `docs/review-memo/PR-48.md`.
- Tests: test/offline/test_budget_degradation.py, test/offline/test_token_budget.py
- Verdict: APPROVE
