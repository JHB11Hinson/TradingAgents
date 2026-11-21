# Evaluation logbook (D2.9)

**Status:** accepted 2026-11-20. **Owner:** `@JHB11Hinson`.
**Requirement:** `D1-REQ-GOV-009` (D2.9). **This artifact is optional** in the course; it is kept
because the project's cost and quality claims need a dated record, not a memory.

One entry per evaluation run that mattered. An entry that is not reproducible from its command is
not evidence; every entry names the command, the date and the result.

## E-001 — The ledger under-count, measured (2026-11-20)

- **Question:** does the run ledger record the tokens the model actually receives?
- **Method:** an offline full-graph run of NVDA 2026-01-09 with a scripted model and fixed vendor
  payloads; compare `context_usage["total_tokens"]` with the whole request (`request_tokens`).
- **Result:** the ledger reported **43,616** for a **56,861**-token request (the history layer was
  budgeted but not recorded). With the counter fixed, the default 50,000 cap made the Portfolio
  Manager return `REVIEW`; with the 2,500-token decision reserve it decided `Overweight` at 49,912
  tokens.
- **Interpretation:** the ledger was measuring its own bookkeeping, not the spend. Recorded as
  `BUG-005`, fixed by CHG-036 (`request_tokens` + reserve).

## E-002 — The fixed set, first measured run (2026-11-20)

- **Command:** `python -m eval.run --set eval/fixed-set.json --thresholds eval/thresholds.yaml`
- **Result:** 2 cases, 0 failed; `total_tokens_ratio 0.374408`, `est_cost_ratio 0.374408`,
  `budget_respected_rate 1.0`, `review_rate 0.0`, `cases_failed 0`; exit 0.
  NVDA 49,912/50,000 (2 compactions), BABA 39,946/50,000 (0).
- **Interpretation:** `COST-001` is satisfied on the fixed set (half of the 120,000 recorded
  baseline); the 50,000 cap binds on the full-analyst case. `DEBT-011` still says this is not a
  production cost claim.

## E-003 — gate-4 on a normal pull request (2026-11-20)

- **Context:** PR #43, the pull request that introduced the gate.
- **Result:** `gate-4-semantic-eval` **pass** in 33 s (run 44726451349).
- **Interpretation:** the gate runs the evaluator in CI without a key and within the job's timeout.

## E-004 — The deliberate-violation probe (2026-11-20)

- **Context:** PR #44 (throwaway), `eval/thresholds.yaml` with `total_tokens_ratio: {max: 0.0}`.
- **Command:** the gate itself; `gh run view 44726856524 --log-failed`.
- **Result:** `total_tokens_ratio: 0.374408 (FAIL; required <= 0)` → `verdict: FAIL` → exit 1;
  `gate-4-semantic-eval` **fail** in 42 s. `gate-5-regression` also failed, because the CLI test
  replays the shipped thresholds (the probe changes them).
- **Interpretation:** the gate blocks. The probe was closed without merging and its branch deleted;
  the evidence is the run log and PR #44.

## E-005 — The evaluation-set thresholds themselves (2026-11-20)

- **Question:** are the thresholds tight enough to catch a regression but loose enough for the
  shipped set?
- **Result:** the shipped values are token/cost ratio 0.5, budget-respected 1.0, review rate 0,
  cases-failed 0. The measured values sit at 0.374, 1.0, 0.0, 0 — margin on cost, none on review.
- **Interpretation:** a quality regression that turns one case into `REVIEW` fails immediately; a
  40% cost regression would still pass. Tightening the ratio is a decision for the next set version,
  not a silent edit.

## E-006 — The same-condition measurement (2026-11-21)

- **Question:** does the token budget actually reduce the request on the shipped set, or does the
  synthetic replay simply cost less than the inherited production analysis?
- **Command:** `.venv/bin/python -m eval.run --results-dir /tmp/opencode/eval-a`
- **Result:** capped **89,858** tokens (NVDA 49,912, BABA 39,946); the same cases with the run and
  call caps lifted **96,820** tokens (NVDA 56,874, BABA 39,946); `capped_tokens_ratio 0.928093`.
  The uncapped total is **0.403417** of the 120,000×2 baseline.
- **Interpretation:** the cap binds (NVDA compacts twice), but the `COST-001` ratio of 0.374 is
  **not** a production saving claim: the uncapped synthetic run already passes the 0.5 threshold
  against the inherited estimate. The new `capped_tokens_ratio` is the mechanism check; a live
  release run remains the only way to quote a production number (`DEBT-011`).
