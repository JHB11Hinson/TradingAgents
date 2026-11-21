# Runtime policy catalog (D2.7)

**Status:** accepted 2026-11-20. **Owner:** `@JHB11Hinson`, reviewed by the team.
**Requirement:** `D1-REQ-GOV-009` (D2.7); carries the degradation paths of `SAFE-001/002`,
`COST-003`, `OBS-001/003`, `MEM-003`.
**Related:** ADR-001 (baseline), ADR-003 (authority boundary), ADR-004 (context budget), ADR-005
(telemetry), ADR-007 (evaluation), ADR-008 (budget-exhaustion REVIEW), ADR-009 (debate termination).

This catalog answers one question for every degraded or failure path: **what does the running system
do, deterministically, when this happens?** A policy that is not in code is not a policy; each row
names the module that implements it. Rows marked *(planned)* are not implemented and must not be
described as if they were.

---

## 1. Data and vendors

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| A vendor is throttled or unreachable | `VendorUnavailableError` from the vendor | try the next vendor in the configured chain | nothing yet | `dataflows/router.py:route_to_vendor` | — |
| Every vendor that answered has no usable data | `NoMarketDataError` after the chain | return a `NO_DATA_AVAILABLE:` sentinel that tells the agent not to fabricate | the report says the data is unavailable for the symbol | `router.py:no_data_available` | — |
| Every vendor was throttled or errored | no success, last failure is unavailable | return a `DATA_UNAVAILABLE:` sentinel; do not end the run | the report says the vendor was the problem, not the instrument | `router.py:vendor_unavailable` | — |
| An optional enrichment category fails (e.g. prediction markets) | category in `OPTIONAL_CATEGORIES` | return a sentinel and proceed | the optional section is missing, the analysis continues | `router.py` | — |
| A required category fails on every vendor | first real error, no sentinel path | raise the vendor's error | the run fails with the provider's message | `router.py` | — |
| A request would look past the analysis date | `date_window` / vendor point-in-time rules | withhold the datum or mark it unavailable | no future information reaches the model | `dataflows/date_window.py`, vendor modules | `MEM-003` |
| An unsafe ticker (`../etc`) | `safe_ticker_component` | reject before any path is built | a validation error, no file access | `dataflows/symbols.py` | — |

## 2. Model output and the authority boundary

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| Provider lacks structured output | `with_structured_output` raises `NotImplementedError`/`AttributeError` | log a warning and use free-text generation for that agent | a warning in the run log | `agents/structured.py:bind_structured` | `SAFE-002` |
| Structured call fails (malformed JSON, transient) | exception from the structured invoke | retry once as free text and render the result | a warning; the run continues | `agents/structured.py:invoke_structured` | `SAFE-002` |
| Decision text has no parseable rating | `extract_rating` returns `None` | emit `REVIEW`, which is not a tradeable position | the report shows `REVIEW`, never a fabricated `Hold` | `agents/rating.py` | `SAFE-002` |
| Context budget exhausted before the Portfolio Manager | `ContextBudgetExceeded` in the PM | return a deterministic `REVIEW` decision that names the cause and sets `termination_reason = "budget_exhausted"`; do not call the model | `REVIEW` with an explanation, no trade | `agents/managers/portfolio_manager.py` | `SAFE-002`, `COST-003` |
| Context budget exhausted for any other agent | `ContextBudgetExceeded` at the run boundary | return a deterministic `REVIEW`; write the state log; skip the memory log; preserve the checkpoint | `REVIEW` with an explanation, no trade; the run can resume | `graph/trading_graph.py:_run_graph`, `_budget_exhausted_state`, `stream_run`; `cli/run.py` | `COST-003`, `TERM-001`; ADR-008 |
| A model output tries to set a position directly | the authority boundary | deterministic code owns the decision; the model's text is advisory | never bypassed | ADR-003 | `SAFE-003` *(ceiling planned)* |

### 2.1 Debate termination (`TERM-001`)

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| The investment debate repeats itself | the last 2 digests equal the previous 2 and contain more than one distinct turn | route to the Research Manager before the bound; set `termination_reason = "oscillation"`; emit `loop.terminated` | the debate ends early; the reason is in the state log | `agents/termination.py`, `graph/conditional_logic.py`, `agents/managers/research_manager.py` | `TERM-001` |
| The risk debate repeats itself | the last 3 digests equal the previous 3 (more than one distinct) | route to the Portfolio Manager; keep the earliest reason; emit `loop.terminated` | the debate ends early; the reason is in the state log | `agents/termination.py`, `graph/conditional_logic.py`, `agents/managers/portfolio_manager.py` | `TERM-001` |
| Three consecutive turns are identical | `detect_termination` stall check | route to the terminal manager; set `termination_reason = "stall"` | the debate ends early; the reason is in the state log | `agents/termination.py`, `graph/conditional_logic.py`, managers | `TERM-001` |
| The run budget is exhausted during a debate | `detect_termination` budget check (`available(use_reserve=False) <= 0`) | route to the terminal manager with `budget_exhausted`; if its own call then raises, the run boundary returns the deterministic REVIEW (ADR-008) | REVIEW, no trade; checkpoint kept | `agents/termination.py`, managers, `graph/trading_graph.py` | `TERM-001`, `COST-003` |
| The debate reaches its configured bound | hard-bound check runs first | route to the terminal manager; `termination_reason` stays empty | a normal, bound-terminated debate | `graph/conditional_logic.py`, managers | `TERM-001`, `DEBATE-004` |

## 3. Context and cost

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| A call would exceed its cap | layer estimate vs the compaction threshold (80%) | compact P3 → P2 → P1, keep P0, re-inject P0 verbatim | the prompt is shorter; the constraints are intact | `context/assembler.py` | `CTX-003` |
| The run would spend the decision reserve | ordinary call's `available()` excludes the reserve | compact the call; the reserve is untouched | the analysis compacts sooner, the decision keeps room | `context/assembler.py`, `default_config.py` | `COST-003` |
| The run cap is exhausted | `available() <= 0` | raise `ContextBudgetExceeded`; the run boundary (or the PM on its reserve) turns it into `REVIEW` with `termination_reason = "budget_exhausted"` | `REVIEW`, no trade; the checkpoint is kept | `context/assembler.py`, `graph/trading_graph.py` | `COST-003`, `TERM-001` |
| A run exceeds the evaluated cost | `eval.run` threshold | exit `1`; gate-4 turns red; the merge is blocked | the pull request cannot merge | `eval/run.py`, `eval/thresholds.yaml` | `COST-001` |

## 4. Observability

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| A telemetry subscriber raises | exception from the subscriber | record a warning, keep the run green | a warning; the decision is unaffected | `telemetry/events.py:Telemetry.emit` | `OBS-003` |
| A subscriber raises `KeyboardInterrupt`/`SystemExit` | control-flow exception | re-raise so Ctrl-C still works | the run stops | `telemetry/events.py` | `OBS-003` |
| The trace/manifest write fails | exception in `write_run_telemetry` | log a warning; the run's decision is kept | a warning; no trace for that run | `graph/trading_graph.py:_write_telemetry` | `OBS-001/002` |
| The model is absent from the price table | `estimate_cost` returns `(0, warning)` | zero cost plus a warning in the manifest | the manifest says it could not price the model | `telemetry/pricing.py` | `OBS-002` |
| Telemetry is disabled | `telemetry_enabled = false` | no spans, no files | nothing written | `telemetry/spans.py` | `OBS-001/002` |

## 5. State, resume and memory

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| A run crashes mid-graph | checkpoint exists for the thread | the next run with the same signature resumes from the last successful node | the run continues, not restarts | `graph/checkpointer.py`, `graph/trading_graph.py` | — |
| The run signature changed (analysts, rounds, model, …) | signature mismatch in the thread id | start a fresh run instead of resuming | no mixed run | `graph/trading_graph.py:_run_signature` | — |
| A run completes | success | clear its checkpoint; store the decision in the memory log | the next run settles it when due | `graph/trading_graph.py` | — |
| A run ends in a `REVIEW` non-decision | `final_rating == "REVIEW"` and `termination_reason == "budget_exhausted"` | write the state log; do not append to the memory log; keep the checkpoint | the run is visible for review, not quoted as a call; a larger-budget run can resume | `graph/trading_graph.py:record_decision`, `_run_graph`; `cli/run.py` | `COST-003`, `TERM-001`; ADR-008 |
| The memory log cannot be read | exception in `get_past_context` | continue with `memory_note` set; the report says the log was unreadable | a note in the report | `graph/trading_graph.py:_memory_step` | `MEM-003` |
| Settlement cannot fetch a price | vendor sentinel / exception | leave the entry pending, note the count, continue | the lesson is not available yet | `memory/settlement.py` | `MEM-003` |

## 6. Configuration and input

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| An invalid `TRADINGAGENTS_*` value | `build_default_config` parsing | raise `ValueError` naming the variable, before the run | a clear startup error | `default_config.py` | — |
| A trade date that is malformed or in the future | `_validate_trade_date` | raise `ValueError`; the run does not start | a validation error | `graph/trading_graph.py` | — |
| An unknown context layer key | `make_layers` | raise `TypeError` | a programming error, caught in tests | `context/assembler.py` | — |
| A missing context layer | `ContextLayers.missing()` | raise `ContextIncomplete`; no prompt is rendered | an error, never a silently incomplete prompt | `context/assembler.py` | `CTX-001` |

## 7. Evaluation

| Trigger | Detection | Runtime action | User-visible effect | Code | Requirement |
|---|---|---|---|---|---|
| A fixed-set case fails | exception in the analyzer | record the case as failed, continue the set | `cases_failed >= 1` fails the run | `evaluation/report.py` | `EVAL-001` |
| A threshold is violated | metric vs bound | exit `1` | gate-4 red, merge blocked | `eval/run.py` | `EVAL-001`, `COST-001` |
| The set/thresholds/baseline are malformed | loader validation | exit `2`, no run | a configuration error, distinct from a quality failure | `evaluation/cases.py`, `thresholds.py`, `baseline.py` | `EVAL-001` |

## 8. Planned policies (not implemented)

| Path | Today | Required action | Requirement |
|---|---|---|---|
| Injection scrub before external text reaches a model | not implemented | a deterministic filter with a blocked-sample corpus; zero tolerance | `SAFE-001` |
| Deterministic position ceiling | not implemented | clip or reject a decision over the ceiling; a test proves the model cannot bypass it | `SAFE-003` |

A row in section 8 is a gap, not a policy. It is listed so a reader cannot mistake the intended
behaviour for the shipped one.
