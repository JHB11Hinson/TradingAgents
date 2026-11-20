### PR-43 — CHG-037 non-author review (gate-4 online)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated review.** The
  owner (@JHB11Hinson) asked the bot to act as the non-author reviewer; this is an automated approval
  and it is labelled as one, so the record is not read as a human second signature.
- Scope: `D1-REQ-GOV-003` (six blocking gates) and `D1-REQ-EVAL-001` (the fixed set and runner),
  reviewed against `AGENTS.md` §9/§10, `docs/code-governance/verification-constraints.md` and
  ADR-007.
- Head reviewed: the implementation head of `ci/CHG-037-gate-4`. No `src/` file changes; the job and
  the protection baseline are the change.

**Specification coverage.** The five tests in `test/offline/test_gate_contract.py` assert that the
workflow defines exactly the six gate jobs with matching `name:` values, that `protection.json`
requires exactly the same six contexts in gate order, that the gate-4 job installs the package and
runs the evaluator on the shipped set and thresholds, that `pyyaml` is a declared dependency, and
that `enforce_admins`, `allow_force_pushes`, `allow_deletions` and `dismiss_stale_reviews` still hold
their values. The gate names are compared character for character, which is the failure mode that
leaves a pull request pending forever.

**Design.** Running the evaluator on every pull request rather than only prompt/model pull requests is
stricter than the course's wording and avoids the "skipped check" ambiguity: a required context that
does not run on a pull request is either pending or skipped, and a skipped job is not evidence. The
replay backend keeps the gate deterministic and key-free; a live evaluation would need a key in CI
and would cost money on every pull request.

**Findings (non-blocking).**

1. The gate adds roughly a minute (install + two replay cases). The fixed set is two cases; if it grows
   much larger, the job should shard or move to a scheduled run plus a threshold check
   (`DEBT-011` covers the set size).
2. The gate runs the evaluator even on documentation-only pull requests, where it cannot fail for the
   change's reason. It is cheap now; if the set grows, an `if:` on `paths` would need the same
   "skipped check" reasoning as above.
3. The deliberate-violation probe is not part of this pull request. It is a throwaway pull request
   after the merge, and the evidence lands in the CHG-038 record; until then `GOV-003` is "contexts
   done, probe recorded next".

No finding changes the gate set, the protection values or a public contract.

- Tests: test/offline/test_gate_contract.py
- Verdict: APPROVE
