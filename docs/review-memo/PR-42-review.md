### PR-42 — CHG-036 non-author review (test contract)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated review.** The
  owner (@JHB11Hinson) asked the bot to act as the non-author reviewer; this is an automated approval
  and it is labelled as one, so the record is not read as a human second signature.
- Head reviewed: `42ff790` (tests-only head; no `src/` or `eval/` commit on the branch yet).
- Scope: `D1-REQ-EVAL-001`, `D1-REQ-COST-001`, `D1-REQ-COST-003`, and the test contract for the
  ledger change, reviewed against `AGENTS.md` §7/§9, `docs/code-governance/verification-constraints.md`
  and the CHG-036 change card.

**Specification coverage.** Each fit criterion has a test that fails when the behaviour is removed.
`EVAL-001`: `test_the_runner_exits_zero_when_every_threshold_passes`,
`test_the_runner_exits_non_zero_when_a_threshold_fails`,
`test_a_malformed_fixed_set_exits_with_a_configuration_error`, plus the strict loaders
(`test_eval_fixed_set.py`, `test_eval_thresholds.py`, `test_eval_baseline.py`). `COST-001`:
`test_aggregate_reports_tokens_cost_and_ratios_against_the_baseline` and
`test_a_failed_case_is_counted_and_never_passes_the_run`. `COST-003`:
`test_the_ledger_records_the_whole_request_including_non_rendered_layers`,
`test_an_ordinary_call_cannot_spend_the_reserve`, `test_the_run_log_reports_the_reserve`.

**Design of the tests.** The CLI test is a subprocess against the real command, so the fit criterion
("executes non-zero") is exercised as written rather than through an imported function. The
deterministic backend is the only mocked boundary — the model and the vendors — so the token numbers
come from the shipped graph, assembler and ledger. Every loader has its rejection cases: a silently
shrinking fixed set or a typo'd metric would weaken every threshold, and each is a negative test.

**Findings (non-blocking).**

1. `test_the_runner_exits_non_zero_when_a_threshold_fails` writes a one-metric threshold file. That is
   the cleanest way to force a failure, but it means the other four metrics' failure paths are only
   covered by the unit tests, not by a CLI run.
2. The shipped fixed set has two cases. The CLI test re-runs them on every suite run; it is fast now
   (about 3 s for the whole file) but the threshold should be revisited before the set grows
   (`DEBT-011`).
3. The ledger test asserts the whole request on an uncompacted call and on a compacted one. It does
   not pin the *combination* of a reserve and a compaction in the same run; the CLI run covers it
   end-to-end, but a focused unit test would localise a future regression faster.

None of these changes the test contract. The tests were committed before any `src/` change and no
inherited test is touched.

- Tests: test/offline/test_context_ledger_reserve.py, test/offline/test_eval_fixed_set.py, test/offline/test_eval_thresholds.py, test/offline/test_eval_report.py, test/offline/test_eval_baseline.py, test/offline/test_eval_cli.py
- Verdict: APPROVE
