# Report

## What one analysis burns: a live measurement (2026-11-23)

The 120,000-token figure in `eval/baseline.json` is an estimate copied from an early requirements example. It was never a measurement. To replace it with evidence, we ran the inherited code and the current tree once each with the same inputs and configuration.

| | Inherited (v0.6.0, `1394a3f`) | Current (`main`, `e0bafd9`) |
|---|---:|---:|
| Ticker and date | NVDA, 2026-11-20 | NVDA, 2026-11-20 |
| Analysts | market | market |
| Debate / risk rounds | 1 / 1 | 1 / 1 |
| Model | deepseek-v4.1-flash | deepseek-v4.1-flash |
| Provider tokens (input + output) | 206,694 (156,321 + 50,373) | 160,833 (100,643 + 60,190) |
| LLM calls | 13 | 10 |
| Rating | Underweight | Underweight |

"Provider tokens" are the gateway's `usage` counts for every request. This is the cost caliber. The current run's context ledger reports 36,595 tokens, not 100,643 input tokens, because the ledger estimates `ceil(characters / 4)` on the assembled prompt and that estimator undercounts Chinese text. The ledger is the budget caliber, not the bill.

The two runs differ in both directions: total tokens fell 22.2% and input tokens fell 35.6%, but output tokens rose 19.5%. The two runs also made 13 and 10 LLM calls; tool-call choices are model-driven. A single pair of runs cannot separate a code effect from model or tool-call variance, so this page reports the numbers and does not claim a precise production saving.

Yahoo rate-limited fresh NVDA downloads during the measurement, so both runs read the same cached NVDA OHLCV file. That removes vendor availability as a variable; it does not make the model deterministic.

The fixed-set replay is a third caliber. On the same two fixtures, the uncapped run is 70,061 tokens and the `--budget 40000` run is 64,950 tokens (−7.3%), with zero `REVIEW` decisions and `capped_tokens_ratio 0.927`. That comparison proves the budget compacts; it does not prove what a live analysis costs.

What the measurement does **not** show:

- It is one run per side. The model is stochastic and the vendor payloads are live, so the difference is not a benchmark.
- It uses one analyst and one round of each debate. The default four-analyst analysis is larger.
- The current run started with one memory-log entry; the baseline started with an empty log.
- Cost is not reported. The gateway has no price entry for `deepseek-v4.1-flash`, so `est_cost` is 0; tokens are the comparable quantity.
- The 120,000-token estimate stays in `eval/baseline.json` as the gate's historical threshold. It is not used as a headline.

**Reproduce.** Baseline: `git worktree add --detach /tmp/upstream 1394a3f`, then run `TradingAgentsGraph(selected_analysts=["market"], config=...)` with the table's settings and a `StatsCallbackHandler`. Current: run `python -m cli.main` with the same settings; the manifest is written next to the state log when telemetry is enabled.

The measurement supports one narrow claim: the current configuration's live token use is now measured, and the budget's effect is measured separately on the fixed set. It does not support a general "73% cheaper" claim, and this report does not make one.
