### PR-55 — CHG-047 remove completed planning scratch files

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: `94bb259` (the eight deletions, the transcript and the AI-use entry). The commit
  that carries this record is docs-only, so the tree the gates run on is unchanged.
- Scope: repository housekeeping and D5 record keeping. No `src/`, test, prompt, model, gate or
  branch-protection change.
- Specification: delete the four implementation plans and four design specs under
  `docs/superpowers/` for CHG-039 and CHG-042 to CHG-045. Every change they planned has merged;
  their outcomes are in the ADRs, the trace matrix and the code. The historical transcripts that
  cite the old paths stay append-only and keep their text; the deleted files remain readable at
  the commits that introduced them.
- Architecture: no runtime component and no interface change. The only active references were the
  historical transcripts, so `grep -rn "docs/superpowers"` outside `transcripts/` is empty. The
  local cleanup (stale tracking ref, caches, `.superpowers/` scratch, no worktree) is described in
  the commit and the session record, but deliberately not part of the repository diff.
- Code and tests: `pytest -q` -> 1543 passed, 1 skipped, 1 deselected, 99 subtests passed in 14.66 s;
  `check-jsonschema` -> validation done. The two cited tests cover the D2 artifact set and the
  transcript index/part layout, which are the evidence areas this change leaves in place.
- Runtime metadata: none. No configuration key, dependency, permission or gate changed.
- Safety and efficiency: the diff removes 1,301 lines of completed planning text and adds the
  cleanup record; it introduces no secret or new personal data. The deleted content is not lost:
  it is recoverable from `9a7f20f` and the merge commits of the changes it planned.
- Record truth: `AI-2026-11-22-001` names the exact cleanup and points at the annotated session
  record; the PR body states which parts were local-only. No transcript is rewritten.

**Findings (non-blocking).**

1. The CHG-039 and CHG-041 transcripts still name `docs/superpowers/...` paths. They are historical
   citations, not live links; the files remain available at the commits that introduced and deleted
   them. Rewriting the transcripts would violate the append-only rule.
2. Removing the design specs also removes a short in-tree rationale. The authoritative record is
   the ADR set plus the trace matrix, and the full text stays in Git history, so no decision is
   lost.
3. The local `.superpowers/` ledger and caches are not represented in the commit. They are ignored
   scratch, and the session record captures that they were removed.

- Tests: test/offline/test_d2_artifacts.py, test/offline/test_transcripts_split.py
- Verdict: APPROVE

The change removes only completed planning scratch, keeps the evidence chain through Git history,
and leaves the transcript and AI-use records current. It is not on a safety-critical path; the
author still does not self-approve.
