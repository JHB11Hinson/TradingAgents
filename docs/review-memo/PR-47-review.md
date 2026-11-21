### PR-47 — CHG-039 DEBT-011 same-condition evaluation (test approval)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated test approval**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: `33febf5` (tests-only head; no `src/` or `eval/` commit yet).
- Specification: the tests pin the same-condition contract for `D1-REQ-EVAL-001` and
  `D1-REQ-COST-001`: `CaseObservation.uncapped_total_tokens`, `uncapped_tokens`,
  `capped_tokens_ratio`, a 1.0 fallback for a missing measurement, and a 0.98 threshold that fails
  when the cap does not bind.
- Code and tests: the branch's only commit touches `test/offline/`; the suite is red for the
  intended reason. No inherited test is weakened.
- Safety and efficiency: additive and offline; no safety-critical path.
- Record truth: `gate-1/2/3` pass; `gate-5/6` are red by design at this test-only head.
- Tests: test/offline/test_eval_same_condition.py, test/offline/test_eval_report.py, test/offline/test_eval_cli.py
- Verdict: APPROVE
