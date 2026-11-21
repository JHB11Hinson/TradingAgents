### PR-49 — CHG-041 TERM-001 termination discipline (test approval)

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated test approval**,
  requested by the owner with the `bot-review` label.
- Head reviewed: tests-only head `af765d1`; no `src/` commit yet.
- Specification: the tests pin `D1-REQ-TERM-001` and `D1-REQ-DEBATE-004`: oscillation period 2 for
  the investment debate, period 3 for the risk debate, a three-identical-turn stall, budget
  precedence, the hard bound first in the router, one digest per turn in all five debate nodes, the
  earliest reason in both managers, safe `loop.terminated` attributes, and a detector-removal
  negative test.
- Architecture: a pure detector module plus additive debate-state fields; no new node or edge, no
  prompt or dependency change. The shipped replay stays bound-terminated with an empty reason.
- Code and tests: the branch's only commit touches `test/offline/`; the suite is red for the missing
  detector, and no inherited test is weakened or skipped.
- Safety and efficiency: pure deterministic logic; the telemetry attributes are allowlisted `node`
  and a fixed-vocabulary `reason`.
- Record truth: this is a test-contract approval; `gate-5`/`gate-6` are red until the implementation
  and the AI-use entry land. The final approval is recorded after the gates are green.
- Tests: test/offline/test_termination.py
- Verdict: APPROVE
