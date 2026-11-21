### PR-50 — CHG-043 structured debate (test approval)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated test approval**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: tests-only head `a822b4a` (no `src/` commit yet).
- Review stage: test approval, before the first `src/` commit.
- Specification: `test/offline/test_debate_turns.py` covers `D1-REQ-DEBATE-001` (claim, evidence,
  rebuttal, confidence; missing/empty fields rejected; JSON and prose paths; one record per turn) and
  `D1-REQ-DEBATE-002` (explicit diverge/converge; empty convergence rejected; invalid JSON aborts
  instead of being re-read as prose). Both ids exist in the registry.
- Architecture: one schema plus one adapter in `agents/`; additive `turn_records` in both debate
  states; no new graph node, edge, dependency or prompt file. ADR-011 records the adapter's limits.
- Code and tests: this head changes `test/` and `docs/` only. The test file is red because
  `agents/debate.py` and the schema do not exist yet; no inherited test is weakened.
- Runtime metadata: the implementation adds `turn_records` to the state; this head has no runtime
  change.
- Safety and efficiency: the adapter never fabricates an empty field; a claimed-JSON answer that
  fails validation aborts; prose adaptation is explicit in the record.
- Record truth: the adversarial path (JSON with empty `converge`) is pinned; the final decision is
  recorded after the gates are green.
- Tests: test/offline/test_debate_turns.py
- Verdict: APPROVE

Approval scope: this record approves the **test contract only**. The implementation head needs a
second decision in this same file after the gates are green.

### PR-50 — CHG-043 implementation head (review)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label.
- Head reviewed: implementation head `c6a7052`; this docs/AI-use commit follows it.
- Specification: `D1-REQ-DEBATE-001` gives every turn claim, evidence, rebuttal, confidence, diverge
  and converge; `D1-REQ-DEBATE-002` makes diverge/converge explicit and rejects an empty
  convergence. A claimed-JSON answer that fails validation raises `DebateTurnError`; prose is adapted
  with an explicit "no convergence stated" marker.
- Architecture: one schema plus one adapter; additive `turn_records` in both states; no new graph
  node, edge, dependency or prompt file. ADR-011 and INV-08, the trace matrix and structural
  constraints record it.
- Code and tests: `pytest -q` -> 1500 passed, 1 skipped, 1 deselected; `ruff` clean on every changed
  `src/**/*.py`; `mypy` clean on the 13 changed modules. The inherited `test_debate_opening.py` and
  `test_termination.py` stay green and the raw-text digest is unchanged.
- Runtime metadata: `turn_records` in the state log; `turn_digests` keeps the TERM-001 evidence. No
  config, prompt, permission or gate change.
- Safety and efficiency: no model call is added on the structured path; the prose adapter is
  deterministic and the invalid-JSON path aborts instead of fabricating a complete turn.
- Record truth: one record per turn in all five nodes; the graph and manager copies are tested.
- Tests: test/offline/test_debate_turns.py
- Verdict: APPROVE
