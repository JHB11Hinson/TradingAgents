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
