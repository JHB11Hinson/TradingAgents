### PR-39 — CHG-034 non-author review (implementation head)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated review.** The
  owner (@JHB11Hinson) asked the bot to act as the non-author reviewer because the other two
  `CODEOWNERS` members (@AKAScarlett, @SY1433) did not review this change. The bot is not a team
  member: this is an automated approval and it is labelled as one, so the record is not read as a
  human second signature.
- Head reviewed: `fc0dfc5` (the head the record cites). The branch has since gained docs-only
  commits — `84a6ae5` attaches the annotated transcript and the commit that records this review —
  while `src/` and `test/` are unchanged since `d8c7524`. The tree this verdict applies to is therefore
  the tree the gates ran on.
- Scope: `D1-REQ-OBS-001` (span trace), `D1-REQ-OBS-002` (per-phase manifest) and
  `D1-REQ-OBS-003` (in-process event seam), reviewed against `AGENTS.md` §2/§8/§9 and ADR-005.
- Gates at the reviewed head: `gate-1`, `gate-2`, `gate-3`, `gate-5`, `gate-6` pass; `gate-4` is
  planned and out of scope. Reproduced locally: `pytest -q` -> 1348 passed, 1 skipped, 1 deselected,
  99 subtests, 11.85 s; `ruff check` on the 11 changed `src/**/*.py` files -> all checks passed.

**Specification coverage.** Each fit criterion has a test that fails when the behaviour is removed.
`OBS-001`: `test_trace_is_json_parsable_and_has_one_span_per_step`, `test_span_records_phase_start_end_and_duration`,
`test_an_exception_closes_the_span_before_it_propagates`, plus the end-to-end
`test_a_run_writes_a_trace_and_a_manifest`, which runs the real graph offline and finds
`market.agent`, `market.tools` and `Bull Researcher` spans. `OBS-002`:
`test_manifest_aggregates_tokens_cost_and_wall_clock_per_phase`,
`test_manifest_totals_equal_the_sum_of_the_phases`, `test_unknown_model_costs_zero_and_warns`,
`test_run_output_uses_a_configured_price_table`. `OBS-003`: `test_raising_subscriber_does_not_block_and_is_recorded`,
`test_keyboard_interrupt_is_never_swallowed`, and the run-level
`test_a_broken_subscriber_leaves_the_run_green`. Negative paths are present and the trace allowlist
is proven by `test_trace_contains_no_secret_or_path_attributes`.

**Architecture.** Additive and in-process: a new `tradingagents.telemetry` package, node wrappers in
`graph/setup.py` and one run scope in `graph/trading_graph.py`. It does not turn the orchestration
into an event-driven system, the `AGENTS.md` §8 contracts are unchanged, and the authority boundary
is untouched — the trace and manifest are written after the decision and can never change it.
`INV-07` is implemented with a concrete fallback: `_write_telemetry` catches, logs and continues, and
`Telemetry.emit` re-raises `KeyboardInterrupt`/`SystemExit` but downgrades any other subscriber
failure to a warning. `telemetry_enabled=false` is a true no-op and is tested.

**Findings (non-blocking).**

1. A resumed run merges two legs into one artifact whose top-level `run_id` is the *first* leg's,
   while the spans carry both legs' ids — reproduced: top-level `leg-1`, span ids
   `['leg-1', 'leg-2']`, and the manifest inherits the same id. The totals then describe a mixed run
   under one identity. A `legs` list, or the final leg's id plus a per-span leg marker, would keep
   the artifact honest.
2. `telemetry_pricing` **replaces** the built-in table instead of merging over it
   (`DEFAULT_PRICING if pricing is None else pricing`), so a caller who overrides one model silently
   degrades every default-catalog model to zero cost plus a warning. `{**DEFAULT_PRICING, **override}`
   matches the ADR's "overrides it" wording and fails less quietly.
3. With the shipped table no model the default catalog can create is priced, so an ordinary run
   reports `est_cost: 0` with a warning. `OBS-002`'s fit criterion only requires the field to exist
   and parse, so this passes, but the manifest is not yet useful for cost control. Follow-up: price
   the `llm_clients` catalog, or map those ids onto the table.
4. `self.callbacks = list(callbacks or [])` replaces the caller's list object, so a caller that
   mutates its own list after construction no longer reaches the graph. Not a §8 contract, but it is
   a quiet behaviour change worth one docstring or ADR line.
5. `stream_run` closed early by its consumer writes a `failed` trace, because `GeneratorExit`
   reaches the `finally`. Defensible, but the status conflates "the caller stopped watching" with
   "the run failed"; a third status would read better.

Accepted as-is, restated as follow-ups from the author's own record: wall-clock is the sum of a
phase's spans rather than critical-path time; span order follows completion; writes are not atomic;
subscriber warning text can carry a local path; `telemetry_enabled` is absent from
`_NOT_IN_SIGNATURE`; `test/offline/test_telemetry_*.py` are not ruff-clean (gate-2 lints `src/`
only).

- Tests: test/offline/test_telemetry_seam.py, test/offline/test_telemetry_trace.py, test/offline/test_telemetry_manifest.py, test/offline/test_telemetry_integration.py
- Verdict: APPROVE

None of the findings changes a decision, a public contract, the authority boundary or the gate set;
findings 1-3 belong in the debt register, not in this pull request. The test contract was approved
before the first `src/` commit and the implementation honours it.
