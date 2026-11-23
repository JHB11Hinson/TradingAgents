### PR-63 — CHG-054 complete gate-2 with a safety-path guard and a dependency check

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated non-author
  review**, requested by the owner with the `bot-review` label; the record names the reviewer as
  automated. The author does not self-approve.
- Head reviewed: the test-stage head (two RED test modules + ADR-018 only); implementation follows.
- Scope: `D1-REQ-GOV-003` (resolves `DEBT-010`, overlaps `DEBT-004`). Gate change under `.github/**`,
  accompanied by `docs/architecture/adr/018-gate2-safety-path-and-deps.md` per AGENTS.md section 11.
- Specification: two new pure-stdlib CI-glue checkers inside `gate-2-static-analysis`. A safety-path
  guard fails a PR that changes a path in `docs/code-governance/safety-paths.txt` without an
  accompanying ADR; a dependency-declaration checker fails any `src/` import not backed by a
  `pyproject.toml` dependency, resolving module→distribution mismatches via a mapping (no `deptry`).
  The gate name and six contexts are unchanged.
- Architecture: ADR-018 (proposed). No new `src/` module, no schema, permission or gate-name change.
- Code and tests (test stage): `pytest test/offline/test_gate2_safety_check.py
  test/offline/test_gate2_deps_check.py` -> collection error (`FileNotFoundError`, RED by design).
- Safety and efficiency: read-only file reads and `ast` parsing; no network, no keys. Three
  transitive-only deps become declared in the implementation, closing the DEBT-004 class.
- Tests: test/offline/test_gate2_safety_check.py, test/offline/test_gate2_deps_check.py
- Verdict: APPROVE

Approving the test stage: the tests target one governance requirement, fail before the checkers
exist, and cover the negative (safety-path change without ADR, undeclared import) alongside the
positive (with ADR, declared import). The implementations and `ci.yml` steps are reviewed separately
at the final head.
