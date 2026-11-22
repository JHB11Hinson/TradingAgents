# ADR-014: Requirement tags on the inherited memory-log tests

- **Status:** accepted (PR-57, 2026-11-22). The coding agent applied the edit; a human reviewer
  approved it and the agent did not approve or merge.
- **Requirement:** `D1-REQ-MEM-004`; traceability duty `D1-REQ-GOV-008`.
- **Related:** `docs/code-governance/verification-constraints.md` Rule 3 (inherited-test exception),
  `AGENTS.md` §5 (frozen inherited tests), ADR-012 (the precedent for adjusting an inherited test).

## Context

`D1-REQ-MEM-004` is covered by the four rotation tests in `test/offline/test_memory_log.py`
(retention disabled by default, prune oldest resolved, never prune pending, no-op under the cap).
That module's **content is inherited**: the baseline commit `1394a3f` carries it as
`tests/test_memory_log.py`, and CHG-001 only moved it to `test/offline/`. The tests themselves were
never touched.

Rule 3 of the verification constraints asks a change that adds or replaces coverage to name the
requirement it covers, and its inherited-test exception states that adding a docstring to an
inherited test "is a change to a frozen test and needs the same review; it is not done as drive-by
cleanup". `AGENTS.md` §5 freezes inherited tests and admits a change only with an ADR and human
approval. Without this record the docstring tags would be an unrecorded edit to a frozen test.

## Decision

- Add one docstring line naming `D1-REQ-MEM-004` to each of the four rotation tests.
- Change **nothing else**: no assertion, test name, marker, fixture, import or line of setup is
  altered. The four hunks are docstring text only, which is what the review of PR-57 checked line by
  line.
- Tagging the other three files in the same pull request (`test_termination.py`,
  `test_context_assembler.py`, `test_budget_degradation.py`) needs no ADR: those modules were
  authored here (CHG-041, CHG-033, CHG-040), not inherited.

## Consequences

- `D1-REQ-MEM-004`'s fit criterion is now named at the test that proves it, without changing what
  the suite proves.
- The inherited test stays frozen **in substance**: a future behavioural edit to it still needs its
  own decision record.
- A docstring tag is documentation, not enforcement. It cannot fail a run, so
  `docs/architecture/trace-matrix.md` remains the authoritative requirement-to-evidence map and this
  record does not move that authority into the test file.
