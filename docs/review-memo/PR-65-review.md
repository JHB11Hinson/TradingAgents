### PR-65 — CHG-055 ADR status and PR reference validator

- Reviewer: github-actions[bot]
- Head reviewed: 8513d12
- Scope: D1-REQ-GOV-009, D1-REQ-GOV-003. No src/ change.
- Specification: an accepted ADR that cites a pull request must cite one with a record
  under docs/review-memo/. Only accepted records are checked; an accepted record that
  cites nothing is exempt; proposed records are not verified; only `PR #<n>` and
  `PR-<n>` count as citations.
- Architecture: .github/scripts/adr_status_check.py beside gate1_check.py and gate2_check.py.
  Not wired into ci.yml, so no gate behaviour changes.
- Code and tests: 16 tests, loaded by path like test_gate2_check.py, PR predicate injected so
  no network. ADR-016's "PR-3" corrected to PR #60; decision text untouched.
- Tests: test/offline/test_adr_status.py
- Verdict: APPROVE
