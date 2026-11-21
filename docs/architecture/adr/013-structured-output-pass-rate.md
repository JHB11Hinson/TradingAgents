# ADR-013: Structured-output pass rate

- **Status:** accepted (CHG-045, 2026-11-21). Approved by the owner's standing instruction; the
  coding agent applied the edit and did not approve or merge.
- **Requirement:** `D1-REQ-QUAL-001`.
- **Related:** ADR-007 (evaluation harness), ADR-010 (`final_decision_source`).

## Context

`QUAL-001` asks for a 100% structured-output pass rate on the fixed set and a `review_rate` that does
not rise. The harness reported only `review_rate`; it could not tell a schema-validated decision from
a free-text answer. The offline replay also left `with_structured_output` unimplemented, so every
replay decision came through the free-text path.

## Decision

- The Portfolio Manager already records `final_decision_source` (`structured`, `free_text`,
  `review`) for SAFE-002. `eval/replay.py` reads that field from the final state and sets
  `CaseObservation.structured_output_ok`.
- `aggregate` reports `structured_output_pass_rate` = share of **successful** cases with a
  schema-validated decision. A failed case is already counted by `cases_failed`; it is not a silent
  pass in the denominator.
- `CaseResult` carries the per-case flag into the JSON report.
- `eval/thresholds.yaml` adds `structured_output_pass_rate: {min: 1.0}`.
- The replay model returns deterministic schema instances from `with_structured_output` for the
  schemas the pipeline binds: `SentimentReport`, `ResearchPlan`, `TraderProposal`,
  `PortfolioDecision`, and (after CHG-043) `DebateTurn`. An unknown schema raises rather than
  returning a meaningless object.

## Alternatives rejected

- **Infer the pass from the rating text.** The rating is deliberately readable from prose; that is
  exactly the ambiguity SAFE-002 removed.
- **Count a failed case as a pass.** It would make the rate look better when a case crashes.
- **Keep the replay on the free-text path.** It would measure the fallback, not the shipped primary
  path, and the threshold could never be honestly evaluated.

## Consequences

- The fixed set now exercises the structured path end to end and reports `1.0`.
- A provider or prompt change that sends a decision through free text lowers the metric and fails
  gate-4.
- `review_rate` remains as a separate guard against a decision degrading to `REVIEW`.
