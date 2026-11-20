### PR-42 — CHG-036 non-author review (implementation head)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated review.** The
  owner (@JHB11Hinson) asked the bot to act as the non-author reviewer; this is an automated approval
  and it is labelled as one, so the record is not read as a human second signature.
- Head reviewed: the head this record cites — `c92f1a5` (implementation). The tree the verdict applies
  to is the tree the gates ran on; no `src/`, `test/` or `prompts/` change follows it.
- Scope: `D1-REQ-EVAL-001`, `D1-REQ-COST-001`, `D1-REQ-COST-003`, and the ledger change they depend
  on, reviewed against `AGENTS.md` §2/§8/§9, ADR-004 (amended) and ADR-007.
- Gates at the reviewed head: `gate-1`, `gate-2`, `gate-3`, `gate-5` and `gate-6` pass (run
  44711014534); `gate-4` is planned and out of scope. Reproduced locally: `pytest -q` -> 1389 passed,
  1 skipped, 1 deselected, 99 subtests, 13.25 s; `ruff check` on the changed `src/**/*.py` and `eval/`
  -> clean; scoped `mypy` clean on the new package and the two non-quarantined changed modules.

**Specification coverage.** `EVAL-001`: the CLI exits 0 on the shipped set, 1 when a threshold fails,
2 when a set cannot be read; the loaders reject a missing case, a duplicate id, a future date, an
unknown analyst, an unknown metric, both bounds, a non-numeric bound, a baseline without a source.
`COST-001`: `total_tokens_ratio` and `est_cost_ratio` are judged against the recorded 120,000-token
baseline and both are 0.374408 on the shipped set. `COST-003`: the ledger records the whole request
(`request_tokens` equals the assembled text plus the non-rendered history), an ordinary call cannot
spend the reserve, and the Portfolio Manager can. `QUAL-001`: `review_rate == 0` is a shipped
threshold, so a cap that turns the decision into `REVIEW` fails the run.

**Architecture.** Additive except for the measured ledger correction. `tradingagents.evaluation` is a
pure policy package (no graph import, no network); `eval/` is a development tool and is deliberately
not installed. The `AssembledContext` field is additive (`request_tokens` alongside `tokens`), and the
new configuration key travels through `_ENV_OVERRIDES` and `run_settings`. The `AGENTS.md` §8 public
contracts are unchanged: the reserve is an internal budget policy, and the authority boundary is
untouched.

**Findings (non-blocking).**

1. `est_cost_ratio` is the token ratio by construction in replay mode: both sides are the same token
   count priced at the baseline's reference rate. The cost threshold therefore adds no information
   until a live mode uses the telemetry manifest's provider-reported cost.
2. The replay vendor stubs duplicate the end-to-end test's fixtures (`test_graph_end_to_end.py`).
   They can drift; a shared fixture module would remove the copy but couples the tool to `test/`.
3. The 2,500-token reserve is a fixed number. A case with a much larger decision prompt (a bigger
   portfolio context) would need more, and a smaller analysis would waste it.
4. The fixed set is two cases with synthetic payloads. `COST-001` is reproducible and comparable on
   it, but the 0.374 figure is not a production cost claim (`DEBT-011`).
5. Only the Portfolio Manager degrades when the analysis budget is exhausted; every other agent raises
   (`DEBT-012`). The reserve makes this unlikely on the shipped set, not impossible.

Findings 1, 3 and 4 are recorded in the debt register; 2 and 5 are follow-ups with a named trigger.
None changes a decision, a public contract, the authority boundary or the gate set.

- Tests: test/offline/test_context_ledger_reserve.py, test/offline/test_eval_fixed_set.py, test/offline/test_eval_thresholds.py, test/offline/test_eval_report.py, test/offline/test_eval_baseline.py, test/offline/test_eval_cli.py
- Verdict: APPROVE
