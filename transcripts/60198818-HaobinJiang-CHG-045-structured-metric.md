# CHG-045 structured-output metric — annotated session record

- Session: `ses_e0273b64bffelE3KMr6t43Rehf`
- Date: 2026-11-21
- Agent: OpenCode / DeepSeek V4.1 Flash
- Change: CHG-045, `D1-REQ-QUAL-001`
- Stacked on: `feat/CHG-042-guardrails` (PR #52), which supplies `final_decision_source`.
- Format: human turns quoted verbatim; tool calls and results summarised.

## Human instruction

> 按优先级顺序开始实现，如果是可以并发的需求，则并发实现，敏捷开发，除了合并以外，所有决策由你自行决断，采用Bot Review

The safety, debate and repeated-call tracks were already in review; the agent continued with the
next priority item, QUAL-001, in a stacked worktree.

## What the agent did

1. Wrote the failing metric tests first: `(2 of 3) -> 0.666667`, the per-case flag in the JSON report,
   and the shipped CLI report at `1.0`. The CLI test failed with `KeyError`.
2. Added `structured_output_ok` to `CaseObservation` and `CaseResult`, computed the rate over
   successful cases only, and added `structured_output_pass_rate: {min: 1.0}`.
3. Read `final_decision_source` from the final state in `eval/replay.py`; this is why the branch is
   stacked on PR #52.
4. Implemented deterministic `with_structured_output` values for the schemas the pipeline binds, so
   the fixed set exercises the structured path instead of the fallback.
5. Ran `PYTHONPATH=src pytest -q` (`1491 passed, 1 skipped`), `python -m eval.run` (both cases
   structured, rate 1.0, review rate 0.0), ruff and mypy.

## Review channel

The owner asked for Bot Review. The test approval is `docs/review-memo/PR-53.md`; the implementation
review follows on the same pull request. The coding agent did not approve or merge.
