### PR-47 — CHG-039 DEBT-011 same-condition evaluation (implementation head)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated non-author
  review**, requested by the owner with the `bot-review` label.
- Head reviewed: implementation head `4fad750`; the docs/AI-use commit follows it.
- Specification: the shipped run reports `total_tokens_ratio 0.374408` against the inherited
  120,000 estimate and `capped_tokens_ratio 0.928093` against the same-condition uncapped run
  (threshold 0.98). The uncapped total is 96,820, already 0.403 of the inherited baseline, so the
  headline is mechanism evidence, not a production saving claim.
- Architecture: two isolated replay passes (`capped/`, `uncapped/`); both caps lifted in the second.
  `CaseObservation` gains one optional field; no graph, prompt or authority change.
- Code and tests: `pytest -q` -> 1411 passed, 1 skipped, 1 deselected; `ruff` and `mypy` clean;
  `python -m eval.run` -> 2 cases, 0 failed, exit 0.
- Safety and efficiency: no safety-critical path; deterministic and offline; the second pass is
  sub-second.
- Record truth: `E-006` and the rewritten `DEBT-011` state the caveat; a live release check remains
  a trigger, not CI work.
- Fix pass after the fresh whole-branch review: any unmeasured or zero-token uncapped case forces
  the aggregate ratio to 1.0; pass isolation, uncapped-failure, default-report-path and artifact
  layout are now pinned by tests. `pytest -q` -> 1416 passed, 1 skipped, 1 deselected.
- Tests: test/offline/test_eval_same_condition.py, test/offline/test_eval_report.py, test/offline/test_eval_cli.py
- Verdict: APPROVE
