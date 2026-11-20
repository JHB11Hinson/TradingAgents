### PR-40 — CHG-035 non-author review (ADR-006 r4, head `d63d5a9`)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated review.** The
  owner (@JHB11Hinson) asked the bot to write the non-author decision for this ADR; this is an
  automated approval and it is labelled as one, so the record is not read as a human second
  signature.
- Scope: `D1-REQ-SAFE-002` (decision validity), reviewed against `AGENTS.md` §7/§8/§11, ADR-001,
  ADR-003 and the code the ADR quotes.
- Head: `d63d5a9` (r4), rebased onto `main`; the diff is `docs/architecture/adr/006-...md` and one
  appended AI-use entry.

**Specification coverage.** The ADR answers the registry's fit criterion for `SAFE-002`: a decision
that fails schema validation is rejected and degraded, and the negative test (removing the `REVIEW`
guard) is named in §8 as the proof the invariant fails when violated. The failure table in §2 maps
each of the six conditions to a call count, a reason identifier and a rating, which is what makes
the negative tests writable without ambiguity. The implementation and its tests are explicitly out
of scope for this PR and are listed in the change card.

**Accuracy.** The code quote in §Context was checked against
`src/tradingagents/agents/managers/portfolio_manager.py:152-158` and now matches verbatim, including
`render_pm_decision(decision)`. The inherited test the ADR says stays green
(`test/offline/test_memory_log.py:795`) really does assert only `final_trade_decision`. The
repository-state paragraph in §10 was corrected: all four records say `SAFE-002` is partial today,
and the implementation change flips three of them while the fourth follows under `DEBT-013`.

**Governance.** The change id `CHG-035`, the debt id `DEBT-013` and the AI-use id
`AI-2026-11-20-006` are unique on `main`. The entry sits in the file its own `members` field
declares. The transcript is `null` at the owner's explicit request and is recorded as a known gap
for the implementation change; that is a recorded decision, not an omission. `Status: proposed`
stays until the implementation change flips it, so this approval is not dismissed by a later push
(`dismiss_stale_reviews`).

**Findings (non-blocking).**

1. The ADR's four identifiers appear only in `final_trade_decision`; an operator who wants to count
   them from telemetry will need a structured field. That is a state-shape change and belongs to a
   later ADR, not this one.
2. The free-text explanation still costs one model call on a failure path. The cap is stated and
   tested; whether the explanation is worth the call is a product decision for `COST-003`'s owner.
3. The `SAFE-003` composition point is named but not designed; the implementation change must say
   where the ceiling sits relative to the retry.

None of these changes the decision, the authority boundary or the gate set.

- Tests: none — docs-only; gate-1 reports "no src/ change".
- Verdict: APPROVE
