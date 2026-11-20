### PR-46 — CHG-038 non-author review (the D2 artifacts)

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated review.** The
  owner (@JHB11Hinson) asked the bot to act as the non-author reviewer; this is an automated approval
  and it is labelled as one, so the record is not read as a human second signature.
- Scope: `D1-REQ-GOV-009` (the D2 artifact set) and `D1-REQ-GOV-003` (the deliberate-violation
  evidence), reviewed against the course's D2 requirement and against the code the artifacts
  describe.
- Head reviewed: the docs head of `arch/CHG-038-d2-artifacts`.

**Coverage against D2.** The course asks for eleven artifact types, of which 1–8 are required and
9–11 optional. The repository already had the blueprint, the ADR set, the invariant register, the
trace matrix and the permission model; this PR adds the memory/state design, the runtime policy
catalog and the candidate evaluation table, and the three optional artifacts. `GOV-009`'s registry
entry names six files rather than three, so all six are present; the optional ones say so in their
own text and the test asserts it.

**Accuracy check.** Each artifact was read against the code rather than the other way round:

1. `memory-design.md` — the stores (`memory/log.py`, `graph/checkpointer.py`, the state log, the
   telemetry directory), the entry format and the append-only lock, the point-in-time
   `get_past_context`, `memory_log_max_entries`, and the run signature that invalidates a checkpoint.
   The deferred embedding layer is named with its requirement id, not described as present.
2. `runtime-policy-catalog.md` — the vendor sentinels (`DATA_UNAVAILABLE`, `NO_DATA_AVAILABLE`), the
   optional-category path, the structured-output fallback, the `REVIEW` sentinel, the budget reserve,
   the telemetry subscriber isolation, the checkpoint resume and the memory degradation. The
   unimplemented paths (`SAFE-001`, `SAFE-003`, the analyst budget exhaustion) are in a "planned"
   section, which is the right shape: a reader cannot mistake them for policy.
3. `evaluation-table.md` — the scores are judgement, not measurement, and the file says so. The one
   measured row quotes the fixed-set result (0.374) and `BUG-005`.

**Gate evidence.** The `GOV-003` row now cites a red run for every gate: gate-1 PR #45 (this PR's
probe), gate-2 PR #12/#26, gate-3 PR #4, gate-4 PR #44, gate-5 PR #6, gate-6 PR #5. The gate-4 and
gate-1 probes are throwaway pull requests that were closed without merging; the run logs are the
evidence.

**Findings (non-blocking).**

1. `risk-list.md` and `option-ledger.md` overlap: a rejected option can also be a risk. The split is
   "a decision we did not take" vs "an assumption that could break"; if the lists drift, merge them.
2. The evaluation table's scores are not reproducible. They are explicitly judgement on a 1–5 scale;
   a later reviewer should move one only with evidence, and the file says that.
3. `runtime-policy-catalog.md` will need a row per new failure path; the test does not check the
   catalog against the code, only the file's existence. A structural check would be a follow-up.
4. The transcript and AI-use entries cite the probes by number; if a probe PR is ever deleted instead
   of closed, the citation breaks.

None of these changes a decision, a requirement or a gate.

- Tests: test/offline/test_d2_artifacts.py
- Verdict: APPROVE
