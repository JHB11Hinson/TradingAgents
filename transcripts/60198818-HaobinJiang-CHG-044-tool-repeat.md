# CHG-044 repeated tool calls — annotated session record

- Session: `ses_e0273b64bffelE3KMr6t43Rehf`
- Date: 2026-11-21
- Agent: OpenCode / DeepSeek V4.1 Flash, with one implementation subagent
- Change: CHG-044, `D1-REQ-TERM-002`
- Format: human turns quoted verbatim; tool calls and results summarised.

## Human instruction

> 按优先级顺序开始实现，如果是可以并发的需求，则并发实现，敏捷开发，除了合并以外，所有决策由你自行决断，采用Bot Review

The agent dispatched an independent subagent in `/tmp/opencode/wt-ops` for the repeated-call detector
while working on the safety track. The subagent wrote the tests first; collection failed because
`identical_call_repeat` did not exist.

## What the agent did

1. Added `identical_call_repeat(messages, limit=2)` to `graph/setup.py`: canonical
   `(name, json.dumps(args, sort_keys=True))`, consecutive-round comparison, call ids and key order
   ignored.
2. Wired the detector into `more_or_wrap_up`; the hard `max_tool_rounds` bound remains the backstop.
3. Added six tests, including the graph-level wrap at the second repeat and a detector-removal
   negative test that runs to the bound.
4. Found the inherited `LoopingModel` used one identical call every round, so the new detector
   changed its `3 * 3` assertion. The agent decided (owner authorised all decisions except merge) to
   vary a date argument in that fake model so the inherited assertion still tests the hard bound;
   ADR-012 records the reason and the unchanged assertion.
5. Ran the full suite (`1466 passed, 1 skipped`) and ruff.

## Review channel

The owner asked for Bot Review. The test approval is `docs/review-memo/PR-51.md`; the implementation
review follows on the same pull request. The coding agent did not approve or merge.
