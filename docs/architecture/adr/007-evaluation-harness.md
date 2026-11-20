# ADR-007: A deterministic evaluation harness, and an honest run ledger

- Status: accepted, implemented in CHG-036 (`src/tradingagents/evaluation/`, `eval/`)
- Date: 2026-11-20
- Deciders: the owner (`@JHB11Hinson`), on the record in the CHG-036 session transcript
- Related: ADR-004 (context assembly), ADR-005 (telemetry), `D1-REQ-EVAL-001`, `D1-REQ-COST-001`,
  `D1-REQ-COST-003`, `D1-REQ-QUAL-001`

## Context

`EVAL-001` (a fixed set, thresholds and a pass/fail runner) and `COST-001` (half of the recorded
baseline in tokens and cost) were the last open `must` requirements in the context/cost area, and
`eval/` was empty (`DEBT-003`). Gate-4 could not come online without them.

Building the harness exposed a defect in the ledger it was supposed to read. On an uncompacted call,
`assemble_context` recorded only the estimate of the prompt text the agent already built, while the
history layer (`state["messages"]`) is budgeted but passed to the model separately. Measured on an
offline full-graph run: `context_usage.total_tokens = 43,616` against a real request of 56,861.
With a one-line honest counter, the same run under the shipped `context_budget_tokens = 50,000`
compacted to the cap and the Portfolio Manager, with no budget left, returned `REVIEW` without a
model call. The cap therefore traded the decision away, which `QUAL-001` forbids.

## Decision

**1. The ledger counts the whole request.** `RunBudget.record` receives
`request_tokens = assembled text + the layers the prompt template carries separately`, and
`AssembledContext` exposes both `tokens` (the assembled text) and `request_tokens` (what the model
receives). The run cap bounds the second number, which is the one that costs money.

**2. A decision reserve.** `RunBudget` withholds `context_decision_reserve_tokens` (default 2,500)
from ordinary calls; `assemble_context(..., use_reserve=True)` — used by the Portfolio Manager only —
may spend it. Compaction can therefore shorten evidence, but it cannot remove the turn that produces
the decision. The default run cap stays at the requirement's 50,000.

**3. The harness is data, not code constants.** `eval/fixed-set.json` (versioned cases),
`eval/thresholds.yaml` (one bound per metric) and `eval/baseline.json` (the number, the price and its
provenance) are committed artifacts. `python -m eval.run` loads them, replays every case, aggregates
the metrics and exits `0` (pass), `1` (a threshold failed) or `2` (a file could not be read). The
rules live in `src/tradingagents/evaluation/`; the backend lives in `eval/replay.py`.

**4. The offline backend replaces two boundaries only.** A scripted chat model (it calls every tool
once, then writes a fixed analyst-length report) and fixed vendor payloads. The graph, the prompts,
the assembler, the budget and the ledger are the shipped ones, so the token count is the product's
number rather than a mock's.

**5. Cost is derived from the measured tokens at the baseline's recorded price.** The replay makes no
paid call, so a provider-reported cost would be zero and the cost check would pass for the wrong
reason. Live runs keep the telemetry manifest (ADR-005) as the authoritative cost record.

## Alternatives considered

- **Live-provider evaluation.** Rejected for CI and for this repository: there is no key in the
  environment, a run costs money on every pull request, and a model update changes the number without
  changing the code. It remains the right mode for a release check once keys exist.
- **Thresholds in code.** Rejected: changing a threshold would be a code change and would need a
  review for a number that is a project decision; a YAML file makes the change visible.
- **Recording real runs and replaying their metrics.** Rejected: it measures last week's analysis,
  never fails when the code regresses, and needs a key to refresh.
- **Raising the default budget instead of reserving.** Rejected: it changes the requirement's stated
  default and sits exactly on the 0.5 cost boundary.
- **Leaving the ledger as it was and documenting the under-count.** Rejected: `COST-001` would rest on
  a number known to be 20% low.

## Consequences

- `COST-001` is measured: two cases, `total_tokens_ratio 0.374`, `review_rate 0`, `budget_respected_rate
  1.0` on the shipped set; the 50,000 cap binds on the NVDA case (49,912 tokens, 2 compactions).
- `EVAL-001` is runnable: `python -m eval.run --set eval/fixed-set.json --thresholds eval/thresholds.yaml`
  exits on the verdict. Gate-4 can consume that exit code when it is scheduled.
- The ledger change alters CHG-033's behaviour: a run that needs more than the cap now compacts
  sooner, and a run that needs far more may still exhaust the analysis budget mid-flight. That
  residual risk is `DEBT-011`, not a silent success.
- The replay payloads are synthetic but fixed; the fixed set is small (two cases) and must grow
  before the thresholds can carry a quality claim.

## Reconsider if

- A key is available in CI: add a live mode and compare it with the replay, keeping the exit-code
  contract.
- A provider tokenizer replaces the `characters / 4` estimate: the estimator is part of the
  comparison, so both sides change together.
- The fixed set grows enough that its runtime stops being negligible in gate-5.
- Compaction is shown to change decision quality on the fixed set: the reserve and the threshold are
  the first two knobs.
