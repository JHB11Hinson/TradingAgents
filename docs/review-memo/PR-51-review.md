### PR-51 — CHG-044 repeated tool calls (test approval)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated test approval**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: tests-only head `d0a271f` (no `src/` commit yet).
- Review stage: test approval, before the first `src/` commit.
- Specification: `test/offline/test_repeated_tool_calls.py` covers `D1-REQ-TERM-002`: identical
  calls detected, key order ignored, different arguments and an intervening different call not
  detected, graph wraps at the second repeat, and the detector-removal negative test runs to the
  round bound. The inherited `LoopingModel` is changed to vary a date each round so its `3 * 3`
  assertion still tests the hard bound rather than the new detector.
- Architecture: one pure helper in `graph/setup.py`; `more_or_wrap_up` consults it, the hard bound
  remains the backstop. ADR-012 records why the inherited test was adjusted and how its intent was
  preserved.
- Code and tests: this head changes `test/` and `docs/` only. The new test file is red because
  `identical_call_repeat` does not exist yet; the inherited test still passes.
- Runtime metadata: the implementation changes only the analyst router; no config, prompt or
  dependency.
- Safety and efficiency: the detector stops a repeating loop earlier than the bound; no model call
  is added.
- Record truth: the graph-level test and its negative twin are the evidence; the final decision is
  recorded after the gates are green.
- Tests: test/offline/test_repeated_tool_calls.py, test/offline/test_graph_end_to_end.py
- Verdict: APPROVE

Approval scope: this record approves the **test contract only**. The implementation head needs a
second decision in this same file after the gates are green.

### PR-51 — CHG-044 implementation head (review)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label.
- Head reviewed: implementation head `19d210e`; this docs/AI-use commit follows it.
- Specification: `D1-REQ-TERM-002` wraps up at the second consecutive identical `(name, args)` call;
  key order and call ids do not hide a repeat; different arguments or an intervening different call
  reset the streak; the round bound remains the backstop.
- Architecture: one pure helper in `graph/setup.py`; no new state key, model call or dependency.
  ADR-012 records the decision and why the inherited `LoopingModel` now varies its date argument.
- Code and tests: `pytest -q` -> 1466 passed, 1 skipped, 1 deselected; `ruff` clean. The graph-level
  test wraps at two rounds with `max_tool_rounds=20`; the negative twin removes the detector and runs
  to twenty, proving the test catches a missing guard. The inherited `3 * 3` assertion is unchanged
  and now genuinely exercises the hard bound.
- Runtime metadata: no config, prompt, permission or gate change.
- Safety and efficiency: the detector stops a repeating loop earlier than the bound and adds no
  model call.
- Record truth: the detector and its negative twin are separate tests; the inherited bound test is
  preserved in intent and assertion.
- Tests: test/offline/test_repeated_tool_calls.py, test/offline/test_graph_end_to_end.py
- Verdict: APPROVE
