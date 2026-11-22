### PR-59 — CHG-050 memory source attribution for injected lessons

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated non-author
  review**, requested by the owner with the `bot-review` label; the record names the reviewer as
  automated. The author does not self-approve.
- Head reviewed: the test-stage head `607332b` (tests + ADR only; implementation follows in C3).
- Scope: `D1-REQ-MEM-003`. Safety-critical path (`src/tradingagents/memory/log.py`), accompanied by
  `docs/architecture/adr/014-memory-source-attribution.md` per AGENTS.md section 11.
- Specification: add an explicit `source_id = "<trade_date>/<ticker>"` to every injected memory item
  (derived from the tag line, no on-disk change, no migration), rendered as `| src:<date>/<ticker>`
  and exposed on the parsed entry. The point-in-time filter is unchanged. Tests: three positives (each
  block tagged, derived-and-migration-free, ids unique) and one negative (removing the `_source_id`
  seam drops the attribution).
- Architecture: ADR-014 (proposed). No new module, no schema, permission or gate change.
- Code and tests (test stage): `pytest test/offline/test_memory_pointintime.py` -> 4 failed, 6 passed
  (RED by design until the implementation). `pytest -q` -> 4 failed, 1577 passed. `ruff` clean.
- Safety and efficiency: read-only derived id; injected text grows by about ten tokens per item, to be
  confirmed against `COST-001`/`COST-003` in C3's eval run. No secret or personal data.
- Tests: test/offline/test_memory_pointintime.py
- Verdict: APPROVE

Approving the test stage: the tests are focused on one requirement, fail before the code exists, and
include a negative case, so gate-1 sees tests before implementation. The implementation and the
`mypy` de-list are reviewed separately at the final head.
