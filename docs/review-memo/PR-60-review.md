### PR-60 — CHG-051 gate-2 mypy quarantine guard

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated non-author
  review**, requested by the owner with the `bot-review` label; the record names the reviewer as
  automated. The author does not self-approve.
- Head reviewed: the test-stage head (tests + ADR-016 only); implementation follows in C2/C3.
- Scope: `D1-REQ-GOV-003`, `D1-REQ-GOV-007`. Gate change under `.github/**`, accompanied by
  `docs/architecture/adr/016-gate2-mypy-quarantine-guard.md` per AGENTS.md section 11.
- Specification: add `.github/scripts/gate2_check.py` that compares
  `docs/code-governance/mypy-legacy.txt` between the base branch and HEAD and fails when a path was
  added (the list may shrink but never grow); wire one extra step into `gate-2-static-analysis`
  without changing the job name or the six protection contexts. Tests: new line fails, deletion
  passes, no change passes, comment-only passes, missing base passes.
- Architecture: ADR-016 (proposed). No new module, no schema, permission or gate-name change.
- Code and tests (test stage): `pytest test/offline/test_gate2_check.py` -> collection error
  (`FileNotFoundError`, RED by design until the checker exists).
- Safety and efficiency: read-only comparison of two git blobs; it cannot widen or narrow the
  type-check scope, only guard the exemption boundary. No secret or personal data.
- Tests: test/offline/test_gate2_check.py
- Verdict: APPROVE

Approving the test stage: the tests target one governance requirement, fail before the checker exists,
and include the negative (added line reds the gate) alongside the positive (removal passes). The
implementation and the `ci.yml` step are reviewed separately at the final head.
