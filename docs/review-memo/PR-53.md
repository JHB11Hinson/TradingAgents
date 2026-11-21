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
