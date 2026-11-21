### PR-53 — CHG-045 structured-output pass rate (test approval)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated test approval**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: tests-only head `c26d063` (no `src/` or `eval/` implementation yet).
- Review stage: test approval, before the first implementation commit. This pull request is stacked
  on `feat/CHG-042-guardrails` (PR #52) because it reads `final_decision_source`.
- Specification: `D1-REQ-QUAL-001` asks for a 100% structured-output pass rate and a non-rising
  `review_rate`. The tests pin the aggregate rate over successful cases (`2/3 -> 0.666667`), the
  per-case JSON flag, and the shipped fixed-set CLI report at `structured_output_pass_rate == 1.0`.
- Architecture: one metric in `evaluation/metrics.py`, one per-case field in
  `evaluation/report.py`, one replay binding in `eval/replay.py`, one threshold in
  `eval/thresholds.yaml`; ADR-013 records the choice.
- Code and tests: this head changes `test/` and `docs/` only; the two new assertions are red because
  the metric and replay binding do not exist yet. No inherited test is weakened.
- Runtime metadata: the implementation adds `structured_output_pass_rate: {min: 1.0}` to gate-4; no
  permission or dependency change.
- Safety and efficiency: the metric is deterministic and offline; a failed case remains in
  `cases_failed` and is not silently counted as a pass.
- Record truth at the test-only head: the two new tests fail on the missing metric; the final
  decision is recorded after the gates are green.
- Tests: test/offline/test_eval_report.py, test/offline/test_eval_cli.py
- Verdict: APPROVE

Approval scope: this record approves the **test contract only**. The implementation head needs a
second decision in this same file after the gates are green.

### PR-53 — CHG-045 implementation head (review)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label.
- Head reviewed: implementation head `6ee4f25`; this docs/AI-use commit follows it. Base:
  `feat/CHG-042-guardrails` (PR #52), which supplies `final_decision_source`.
- Specification: `structured_output_pass_rate` is the share of successful cases whose final decision
  came from a validated schema; it is `0.666667` for two of three, and the shipped fixed set reports
  `1.0`. A failed case stays in `cases_failed` and is not counted as a pass.
- Architecture: one metric, one per-case field, one replay binding and one threshold; ADR-013
  records the choice. The replay model's `with_structured_output` raises for an unknown schema
  rather than returning a meaningless object.
- Code and tests: `PYTHONPATH=src pytest -q` -> 1491 passed, 1 skipped, 1 deselected; `ruff` clean;
  `mypy` clean on the changed evaluation modules. `python -m eval.run` -> 2 cases, 0 failed,
  `structured_output_pass_rate 1.0`, `review_rate 0.0`.
- Runtime metadata: `gate-4-semantic-eval` now reads the new threshold; no permission or dependency
  change.
- Safety and efficiency: deterministic and offline; no model call or key is added.
- Record truth: the CLI report and the per-case JSON flag are both pinned; the metric is defined over
  successful cases, not the whole set.
- Tests: test/offline/test_eval_report.py, test/offline/test_eval_cli.py
- Verdict: APPROVE
