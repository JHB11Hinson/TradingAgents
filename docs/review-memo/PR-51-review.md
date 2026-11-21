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
