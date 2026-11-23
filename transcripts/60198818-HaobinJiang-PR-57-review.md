# DeepSeek Harness session record — PR #57 review and fixes

- Date: 2026-11-22 (local, Asia/Shanghai)
- Harness: DeepSeek Harness (`dsh`), root agent `lead`
- Working directory: `/home/jhb/TradingAgents` (Windows host, WSL Ubuntu-20.04)
- Branch under review: `test/req-tags-debate-004-ctx-002-003-mem-004` (pull request #57, head `94f24f7`)
- Fix branch: `pr57-fix` (same base, commits on top of `94f24f7`)

> Annotated session record. The human turns are verbatim; tool calls are summarised with the
> commands that produced them. Two review axes (Standards, Spec) ran as parallel sub-agents with
> fresh context; the lead agent then verified every blocking claim itself before reporting. This is
> not a full verbatim export.

## Human requests (verbatim)

```text
审核当前Open的PR
```

```text
改好，然后Review，然后合并
```

## PR state at review time

- `gh pr list --state open`: exactly one open PR, #57 by `@AKAScarlett`, base `main` @ `1b59a33`,
  one commit `94f24f7`, five files, +63/−7, no `src/` change.
- Checks: `gate-1` … `gate-6` all green; the `bot-review` workflow **failed** with
  "docs/review-memo/PR-57-review.md is missing; the bot has no review text to post". The PR carries
  the `bot-review` label, so the label was applied before the review text was committed.
- `reviewDecision: REVIEW_REQUIRED`, `mergeable: MERGEABLE`.

## Findings (Lead verification, not just sub-agent claims)

Blocking, all in the governance evidence chain — the suite itself was green:

1. `docs/ai-use-log/AKAScarlett.yaml` ended with `transcript: TBD`. The AI-use-log README fixes the
   shape as `transcripts/<student-id>-<name>.md#L<a>-L<b>`; all 40 archived entries use a real path
   and none used `TBD`. `transcripts/` holds 28 files — 25 `60198818-HaobinJiang*` and three
   change-named ones (`CHG-021`, `CHG-034-bot-review`, `CHG-034-telemetry`) — and none belongs to
   this session, so no AKAScarlett record exists; `~/.local/share/opencode` keeps only shell output
   and snapshots, so it cannot be reconstructed.
2. Commit `94f24f7` carried only `Refs:` and `AI-Use-Log:`; `Agent-Session:` was absent (the same
   gap as 1, at the commit level). `Test-Approval:` was correctly absent: `gate1_check.py` returns
   "no src/ change" before it looks for the trailer.
3. `test/offline/test_memory_log.py` is inherited content (baseline `1394a3f` has
   `tests/test_memory_log.py`; CHG-001 only moved it). `AGENTS.md` §5 freezes inherited tests and
   admits change only with an ADR plus human approval; `verification-constraints.md` Rule 3 says
   adding a docstring to an inherited test "needs the same review; it is not done as drive-by
   cleanup". PR-51 set the precedent with ADR-012.
4. Neither `docs/review-memo/PR-57.md` nor `PR-57-review.md` existed, which is the red check.

Evidence-axis findings, verified by mutation rather than by reading:

- The new `test_the_debate_ends_exactly_at_2n_turns` only asserted `count == 2*N`. Rewriting the
  router's `>=` as `==` left all three parametrized cases **green**, so the test did not prove the
  "never exceeds 2*N turns" half of the fit criterion.
- The property is not unguarded: `test/offline/test_risk_router_path_map.py::
  test_debate_path_map_covers_full_router_range` fails on the same mutant (it probes `count=99`).
  So the PR's framing of DEBATE-004 as an uncovered criterion was inaccurate —
  `verification-constraints.md` §4 already marked it **done**.
- `D1-REQ-CTX-002`'s "drops only what the budget forces it to" half was evidenced by no tagged test;
  the two tests that do prove it (`test_under_budget_returns_the_agent_prompt_unchanged`,
  `test_retrieved_knowledge_is_trimmed_only_after_history_is_within_its_ceiling`) carried no id.
- `test_a_tiny_budget_returns_review_instead_of_raising` claimed `D1-REQ-CTX-003` for a test that
  asserts degradation, not the budget ceiling.

## Fixes applied on `pr57-fix`

- `test/offline/test_termination.py`: added an `_advancing(n)` helper that generates `n` distinct
  digests (replacing the `"abcdefghij"[:n]` slice, whose ten-character ceiling would silently
  truncate at `rounds >= 6`); the DEBATE-004 test now asserts exact alternation under the bound,
  termination at exactly `2*N`, **and** termination at `2*N+3`, so `>=` cannot regress to `==`.
- `test/offline/test_context_assembler.py`: named `D1-REQ-CTX-002` on the under-budget and
  priority-order tests, and made both assert the claim instead of implying it — `dropped == ()`
  under budget, and exact layer tokens (`HISTORY == 100` untouched, `RETRIEVED == 360` trimmed)
  when the budget does bind.
- `test/offline/test_budget_degradation.py`: corrected the over-claim to `D1-REQ-COST-003` on both
  degradation tests, matching the module docstring and the trace matrix, which already credits this
  file to COST-003 for degradation.
- `docs/architecture/adr/017-inherited-test-requirement-tags.md` (filed as `014-` in PR #57;
  renumbered by CHG-053 because that number was already taken by the accepted
  `014-memory-source-attribution.md`): records why docstring-only tags on
  the inherited memory-log tests are admissible, and that the trace matrix stays authoritative.
- `docs/architecture/trace-matrix.md`: DEBATE-004, CTX-002 and MEM-004 rows now name the tests that
  carry them instead of "Round upper-bound case" / "Pipeline unit test shows stage order and drops"
  / "Rotation case".
- `docs/code-governance/verification-constraints.md` §4: the DEBATE-004 evidence cell names the new
  boundary test; the status preamble records the PR-57 update.

## Second pass: an independent review of the fix, and what it caught

A fresh sub-agent reviewed `aee68ec` adversarially. It reproduced the DEBATE-004 mutation (real), and
found three overstatements that this session then corrected:

- The CTX-002 docstrings claimed "drops nothing under budget" / "drops only what the budget forces",
  but neither test asserted `result.dropped`, so a mutation that dropped every block still passed
  them. Fixed by asserting `dropped == ()` and exact layer tokens.
- The ADR's Status line said "a human reviewer approved it" and that the review "checked [it] line by
  line"; no review record existed. Corrected to `proposed`, awaiting the pull request's non-author
  review, and the ADR now says the docstring edit landed first and the record came second.
- `test_budget_degradation.py` still labelled the sibling degradation test `D1-REQ-CTX-003`, so one
  file had two owners for one path. Both are now `D1-REQ-COST-003`.
- The transcript sentence "`transcripts/` holds 28 files, all `60198818-HaobinJiang*`" was false:
  three are change-named. Corrected above.

## Verification run

- `pytest -q` on the fix branch: `1580 passed, 1 skipped, 1 deselected` — the same count as the PR
  head, because the added assertions strengthen three existing parametrized cases instead of adding
  a test id. Mutation re-checked: with `>=` rewritten as `==`, all three DEBATE-004 cases now fail
  (previously all three passed), in addition to the router path map failing.
- `ruff check` on the four changed test files: identical to `main` (the single pre-existing `I001`
  in `test_context_assembler.py:9` is untouched; `gate-2` only lints `src/**`).
- `check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml`: unchanged
  requirements, gate-3 green.

## Left to humans (the agent must not do these)

- `@AKAScarlett` must replace `transcript: TBD` with their session record and add `Agent-Session:`;
  the AI-use-log README rule 1 forbids another member editing that file.
- A non-author reviewer writes `docs/review-memo/PR-57.md` and `PR-57-review.md`, then re-applies
  the `bot-review` label so `.github/workflows/bot-review.yml` posts the approval.
- The merge itself: `AGENTS.md` §7 — "the agent never approves or merges a change".
