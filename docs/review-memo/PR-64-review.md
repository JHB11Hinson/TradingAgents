### PR-64 — CHG-053 demo scripts as repository evidence

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated non-author
  review**, requested by the owner with the `bot-review` label; the record names the reviewer as
  automated. The author does not self-approve.
- Head reviewed: the head that carries `docs/demo/` plus the `Report.md` measurement section from
  CHG-052.
- Scope: D6 evidence. `docs/demo/` holds the demo runner, the real live-run script, the debate
  and guardrail demos, and a README. The `Report.md` section records the same-config measurement
  the demo quotes.
- Specification: the runner resolves the repository from `docs/demo/../..`; the live script prints
  each phase, tool call, model call and token count and finishes with the rating and totals; OHLCV
  is served from the run cache by default (`DEMO_OHLCV=live` forces Yahoo); the debate and
  guardrail scripts keep their existing demonstrations and add `src/` to `sys.path`.
- Architecture: no module, schema, permission, prompt or gate-name change. `docs/demo/` is
  evidence and is not imported by the application or the test suite.
- Code and tests: no `src/`/`test/` change. The demos exercise code already covered by
  `test/offline/test_debate_turns.py`, `test/offline/test_guardrails.py`,
  `test/offline/test_eval_same_condition.py` and `test/offline/test_token_budget.py`. The live
  run reproduced locally: 16 model calls, 12 tool calls, 155,064 provider tokens, rating
  `Underweight`.
- Safety and efficiency: no secret, token or personal data; the cache removes a flaky network
  dependency; the live calls are explicit and interruptible.
- Tests: test/offline/test_debate_turns.py, test/offline/test_guardrails.py,
  test/offline/test_eval_same_condition.py, test/offline/test_token_budget.py
- Verdict: APPROVE

Evidence-only: the scripts move under `docs/demo/`, their paths become repository-relative, and
the live process and cache policy are recorded. No runtime, test, schema or gate file changes, so
the six gates keep their meaning.
