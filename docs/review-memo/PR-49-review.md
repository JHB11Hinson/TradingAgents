### PR-49 — CHG-041 TERM-001 termination discipline (implementation head)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label.
- Head reviewed: implementation head `c87da70`; the docs/AI-use commit follows it.
- Specification: both debate loops stop early on oscillation (cycle 2 investment / cycle 3 risk), a
  three-identical-turn stall or budget exhaustion. The hard bound is checked first, so the shipped
  replay keeps `termination_reason == ""`; the earliest manager reason survives; the PM's own budget
  catch still returns `budget_exhausted`.
- Architecture: a pure `agents/termination.py`, additive `turn_digests` fields, one digest per turn
  in the five debate nodes, detector checks in the existing router, and reason/span emission in the
  existing terminal managers. No new node, edge, prompt or dependency.
- Code and tests: `pytest -q` -> 1460 passed, 1 skipped, 1 deselected; `ruff` clean on the changed
  `src/**/*.py`; `mypy` clean on the changed non-quarantined modules; `eval.run` -> 2 cases, 0
  failed, exit 0 with unchanged ratings and ratios. The detector-removal negative test and the
  replay's empty-reason assertion are in place.
- Safety and efficiency: pure deterministic logic, no added model call, earlier stop for a repeating
  debate. `loop.terminated` carries only allowlisted `node` and fixed-vocabulary `reason`.
- Record truth: ADR-009 and INV-01/trace matrix/runtime catalog describe the shipped policy; the
  budget marker is tested without a fake successful manager.
- Tests: test/offline/test_termination.py, test/offline/test_graph_end_to_end.py
- Verdict: APPROVE
