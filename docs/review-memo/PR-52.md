### PR-52 — CHG-042 guardrails (test approval)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated test approval**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: tests-only head `dc8f614` (no `src/` commit yet).
- Review stage: test approval, before the first `src/` commit, so `gate-1-test-approval` reads this
  record at the parent of that commit.
- Specification: `test/offline/test_guardrails.py` covers `D1-REQ-SAFE-001` (hostile corpus blocked,
  zero-width evasion, detector-removal and seam-removal negative tests, tool-message scrubbing),
  `D1-REQ-SAFE-002` (one explicit rating accepted; ambiguous/absent answers become `REVIEW`) and
  `D1-REQ-SAFE-003` (50% -> 10%, free-text clip, configured 5% PM ceiling, negative size rejected,
  environment override). All three ids exist in `docs/req/requirements.yaml`.
- Architecture: one new pure `guardrails/` package wired into existing seams; no graph node, no model
  call, no dependency. ADR-010 records the decision and the pattern-corpus limit.
- Code and tests: this head changes `test/` and `docs/` only. The test file is red because
  `guardrails/` does not exist yet; no inherited test is weakened.
- Runtime metadata: the implementation adds `max_position_pct` (default 10%) and
  `final_decision_source`; this head has no runtime change.
- Safety and efficiency: the tests pin zero-tolerance blocking on the corpus and a deterministic
  ceiling; no model call or vendor request is added.
- Record truth at the test-only head: the suite is red by design for the guardrail module; the final
  decision is recorded after the gates are green.
- Tests: test/offline/test_guardrails.py
- Verdict: APPROVE

Approval scope: this record approves the **test contract only**. The implementation head needs a
second decision in this same file after the gates are green.

### PR-52 — CHG-042 implementation head (review)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label.
- Head reviewed: implementation head `7b2b3a4`; this docs/AI-use commit follows it.
- Specification: `D1-REQ-SAFE-001` blocks the hostile corpus and scrubs retrieved blocks and tool
  results; `D1-REQ-SAFE-002` accepts only one explicit free-text rating and degrades ambiguity to
  `REVIEW`; `D1-REQ-SAFE-003` clips a 50% structured or free-text claim to `max_position_pct`
  (default 10%, environment-overridable). The inherited clean-prose PM test still passes.
- Architecture: one pure `guardrails/` package wired into the existing context, tool and manager
  seams; no new graph node, dependency or model call. ADR-010 records the decision and the
  pattern-corpus limit; INV-04/05/06, the trace matrix, structural constraints, runtime catalogue and
  DEBT-002 are updated.
- Code and tests: `pytest -q` -> 1489 passed, 1 skipped, 1 deselected; `ruff` clean on every changed
  `src/**/*.py`; `mypy` clean on the changed non-quarantined modules (`graph/setup.py` and
  `trading_graph.py` remain in `mypy-legacy.txt`). `python -m eval.run` -> 2 cases, 0 failed, all
  thresholds pass.
- Runtime metadata: `max_position_pct` (default 10%) and `TRADINGAGENTS_MAX_POSITION_PCT`;
  `final_decision_source` records `structured`, `free_text` or `review`. No permission or gate change.
- Safety and efficiency: deterministic, offline, no added model call; the corpus is the maintenance
  surface and is stated as such rather than claimed complete.
- Record truth: the negative tests remove the detector/seam and the strict contract; the position
  bypass test drives the PM node with a 50% decision under a 5% ceiling.
- Tests: test/offline/test_guardrails.py
- Verdict: APPROVE
