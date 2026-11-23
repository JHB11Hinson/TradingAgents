### PR-62 — CHG-053 renumber the duplicate ADR-014 to ADR-017

- Reviewer: github-actions[bot]
- Head reviewed: e8a58e9
- Scope: D1-REQ-GOV-009. No src/ change.
- Specification: two files claimed ADR-014; the later proposed record is renumbered to 017.
  The accepted record keeps 014 because src/ and three documents cite it.
- Architecture: ADR numbering only; no module, schema, permission or gate change.
- Code and tests: 3 of 6 tests RED before the move; full suite 1637 passed.
- Tests: test/offline/test_adr_numbering.py
- Verdict: APPROVE
