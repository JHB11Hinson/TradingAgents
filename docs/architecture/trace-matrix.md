# Requirements trace matrix (D2.4)

- **Why this file exists:** the brief requires a trace matrix that maps **every requirement** to its
  **executing component**, its **test / evidence** and its **runtime monitor**
  (deliverable D2.4; requirement `D1-REQ-GOV-004`).
- **Requirement source of truth:** `docs/req/requirements.yaml` is the machine-readable registry.
  It registers all **40** requirements: 21 `must` (CHG-004), 12 `should` + 1 `could` (CHG-018), and
  6 `should` entries deferred to `wont` by CHG-032.
- **How to read it:** one row per requirement id. `Executing component` is the module that will
  carry the behaviour; `Test / evidence` is the artifact that makes the `fit_criterion` machine
  checkable; `Runtime monitor` is what is watched once the code is live.
- **Status:** baseline. Components marked *(planned)* do not exist yet; their tests/monitors are the
  planned evidence. Monitors marked *(via OBS-001)* depend on the telemetry event seam.
- **Maintenance:** whoever changes a requirement updates its row (team decision); the admin leads.

| REQ ID | Prio | Requirement (short) | Executing component | Test / evidence | Runtime monitor |
|---|---|---|---|---|---|
| D1-REQ-DEBATE-001 | must | Structured debate turns: claim, evidence, rebuttal, confidence | `src/tradingagents/agents/researchers`, `src/tradingagents/agents/schemas` | Schema-validator pass rate is 100% on the fixed set | `debate.turn` span + invalid-turn counter *(via OBS-001)* |
| D1-REQ-DEBATE-002 | should | Osborn-style diverge-then-converge per round | `src/tradingagents/agents/researchers` *(planned; round fields shared with DEBATE-001)* | Structural fields present + a round case | `debate.round` span with diverge/converge flags *(via OBS-001)* |
| D1-REQ-DEBATE-003 | wont | Debate evidence-citation rate >= baseline | none — deferred | Deferred (CHG-032); the registry carries a `deferred_reason` | none — deferred |
| D1-REQ-DEBATE-004 | must | Rounds configurable with a hard upper bound; converge at the bound | `src/tradingagents/graph/conditional_logic` | Round upper-bound case | Round counter vs `max_debate_rounds` *(via OBS-001)* |
| D1-REQ-TERM-001 | must | Loop self-stops on oscillation, stall or budget exhaustion | `src/tradingagents/graph/conditional_logic` | Oscillation/stall cases self-terminate; detector-removal negative test turns red | Termination reason event; alert on unbounded loop |
| D1-REQ-TERM-002 | should | Analyst tool loop detects repeated identical calls | `src/tradingagents/graph/setup` | Repeated-tool-call case | `tool.repeat` counter *(via OBS-001)* |
| D1-REQ-CTX-001 | must | Layered context assembly (six layers) for every model call | `src/tradingagents/context/assembler.py` | Assembler unit test asserts each layer's presence and source | `context.assemble` span with layer-presence flags *(via OBS-001)* |
| D1-REQ-CTX-002 | should | Assembly pipeline dedupe -> prioritize -> budget -> compact -> assemble | `src/tradingagents/context/assembler.py` | Pipeline unit test shows stage order and drops | `context.pipeline` span per stage *(via OBS-001)* |
| D1-REQ-CTX-003 | must | Assembled context <= budget; constraints re-injected after compaction | `src/tradingagents/context/assembler.py` | Unit test asserts `assembled_tokens <= budget` and byte-identical re-injection | Budget-ceiling breach event + alert |
| D1-REQ-CTX-004 | should | Layered structure and pipeline recorded in an ADR | `docs/architecture/adr` | ADR review | Review checklist per ADR |
| D1-REQ-MEM-001 | wont | Layered memory (working/episodic/semantic) survives sessions/versions | none — deferred | Deferred (CHG-032); the registry carries a `deferred_reason` | none — deferred |
| D1-REQ-MEM-002 | wont | Prior reflections retrieved by semantic similarity | none — deferred | Deferred (CHG-032); the registry carries a `deferred_reason` | none — deferred |
| D1-REQ-MEM-003 | should | Memory items source-attributable; no future leakage | `src/tradingagents/memory/log`, `date_window` | Point-in-time case | Future-dated item blocked event |
| D1-REQ-MEM-004 | could | Retention / rotation / size caps configurable | `src/tradingagents/memory/log` | Rotation case | Memory entry count vs cap *(via OBS-001)* |
| D1-REQ-COST-001 | must | Single analysis <= 50% of baseline tokens and cost | `src/tradingagents/evaluation/`, `eval/` | `python -m eval.run` over the fixed set: `total_tokens_ratio` and `est_cost_ratio` <= 0.5, plus the same-condition `capped_tokens_ratio` <= 0.98 (`test/offline/test_eval_report.py`, `test_eval_same_condition.py`, `test_eval_cli.py`) | `eval/results/report.json` metrics vs the recorded baseline; capped/uncapped ratio |
| D1-REQ-COST-002 | wont | Semantic cache with quantified savings | none — deferred | Deferred (CHG-032); the registry carries a `deferred_reason` | none — deferred |
| D1-REQ-COST-003 | must | Single analysis <= configured token budget (default 50000), else compaction | `src/tradingagents/default_config.py`, `src/tradingagents/context/assembler.py`, `src/tradingagents/graph/trading_graph.py` | Over-budget compaction case (`test_token_budget.py`); whole-request ledger and reserve (`test_context_ledger_reserve.py`); degradation on every entry point, including a real one-token run and a handler-removal negative test (`test_budget_degradation.py`) | Run manifest `context_usage.total_tokens <= budget`; compaction count; state log `termination_reason` and checkpoint presence |
| D1-REQ-PERF-001 | wont | Wall-clock <= 60% of baseline | none — deferred | Deferred (CHG-032); the registry carries a `deferred_reason` | none — deferred |
| D1-REQ-OBS-001 | should | Machine-parsable run trace (span / phase / duration) | `src/tradingagents/telemetry/trace.py`, `src/tradingagents/graph/setup.py` | `test/offline/test_telemetry_trace.py`: parses, one span per step, attribute allowlist | `<results>/<ticker>/TradingAgentsStrategy_logs/telemetry/trace_<date>.json` |
| D1-REQ-OBS-002 | should | Token / cost / latency aggregated per phase (run manifest) | `src/tradingagents/telemetry/manifest.py`, `src/tradingagents/telemetry/pricing.py` | `test/offline/test_telemetry_manifest.py`: per-phase tokens, cost, wall-clock; unknown model warns | `<results>/<ticker>/TradingAgentsStrategy_logs/telemetry/manifest_<date>.json` |
| D1-REQ-OBS-003 | should | Structured step events; a failing subscriber must not block the run | `src/tradingagents/telemetry/events.py`, `src/tradingagents/telemetry/spans.py` | `test/offline/test_telemetry_seam.py` + `test/offline/test_telemetry_integration.py`: subscriber raises, run stays green | `Telemetry.warnings` count |
| D1-REQ-EVAL-001 | must | Fixed set + thresholds + regression runnable locally | `src/tradingagents/evaluation/`, `eval/run.py` | `python -m eval.run` exit codes (`test_eval_cli.py`), loaders and aggregation (`test_eval_fixed_set.py`, `test_eval_thresholds.py`, `test_eval_report.py`), same-condition ratio (`test_eval_same_condition.py`) | `gate-4-semantic-eval` on every pull request; `eval/results/report.json` |
| D1-REQ-EVAL-002 | wont | Prompt/model change triggers evaluation; failure blocks | none — deferred | Deferred (CHG-032); the registry carries a `deferred_reason` | none — deferred |
| D1-REQ-SAFE-001 | must | External/retrieved text scrubbed; hostile samples blocked | `guardrails/` *(planned)* | Injection corpus blocked 100%; scrubbing-off negative test turns red | Blocked-injection event + alert |
| D1-REQ-SAFE-002 | must | Invalid-schema decision rejected and degraded | `src/tradingagents/agents/structured`, `guardrails/` | Malformed-decision negative test | REVIEW/degrade event |
| D1-REQ-SAFE-003 | must | Deterministic position ceiling; model cannot bypass it | `guardrails/`, `src/tradingagents/agents/managers` | Bypass-attempt negative test | Ceiling-clip event |
| D1-REQ-QUAL-001 | should | Structured-output pass rate 100%; REVIEW rate not rising | `src/tradingagents/agents/*` | `eval.run` summary | Evaluation logbook |
| D1-REQ-GOV-001 | must | Repository layout satisfies the required structure | `src/`, `test/` | Inherited suite + `pip install -e ".[dev]"` | gate-5-regression on `main` |
| D1-REQ-GOV-002 | must | `AGENTS.md` covers the six required sections | `AGENTS.md` | Review checklist | Sprint review checklist |
| D1-REQ-GOV-003 | must | Six blocking gates online; each failed on a deliberate violation | `.github`, `docs/code-governance/protection.json` | Deliberate-violation probes: gate-1 PR #45, gate-2 PR #12/#26, gate-3 PR #4, gate-4 PR #44, gate-5 PR #6, gate-6 PR #5 | Weekly branch-protection check (manual 8.2) |
| D1-REQ-GOV-004 | must | Trace matrix maps every requirement to component, test, monitor | `docs/architecture/trace-matrix.md` | Trace check: one row per REQ id | Sprint trace check (manual 8.3) |
| D1-REQ-GOV-005 | must | Agent tools x roles in `mcp-tool-manifest.md` | `docs/code-governance/mcp-tool-manifest.md` | Manifest vs permission-model consistency | Review checklist |
| D1-REQ-GOV-006 | must | Default-deny, per-path whitelist, consistent in three places | `.opencode/permissions.jsonc`, `docs/architecture/permission-model.md`, `AGENTS.md` | Three-way whitelist comparison | Review checklist |
| D1-REQ-GOV-007 | should | `structural-constraints.md`: element <-> module, extend not replace | `docs/code-governance/structural-constraints.md` | Structural (import/boundary) test | gate-2-static-analysis / structural test |
| D1-REQ-GOV-008 | must | `verification-constraints.md` + `invariants.md`: every rule has a test and fallback | `docs/code-governance/verification-constraints.md`, `docs/architecture/invariants.md` | Missing-entry check | Sprint review checklist |
| D1-REQ-GOV-009 | should | D2 architecture artifact set complete and consistent | `docs/architecture`, repo root | `test/offline/test_d2_artifacts.py`: every artifact exists and is non-empty, every blueprint component exists | Sprint review checklist |
| D1-REQ-GOV-010 | must | QA records: `docs/review-memo/PR-<n>.md` per PR, `debt-register.md`, `bug-diary.md` | `docs/` | Missing-entry check | Per-PR + weekly check (manual 8.1/8.2) |
| D1-REQ-GOV-011 | must | >=5 annotated transcripts over six stages; AI-use log current | `transcripts/`, `docs/ai-use-log/<member>.yaml` | gate-6 + coverage check | gate-6-ai-use-log + weekly check |
| D1-REQ-GOV-012 | should | Runtime prompts versioned as files, no in-place edits | `prompts/` | Versioned-file existence | Review checklist |
| D1-REQ-GOV-013 | must | Always-on rules + project covenant exist and agree | `.opencode/`, `.agent/` | File-existence + five covenant clauses | Sprint covenant check |

## Notes

- **Registry vs matrix.** `docs/req/requirements.yaml` registers all 40 requirements: the 21 `must`
  (CHG-004), the 12 `should` + 1 `could` (CHG-018) still in scope, and the 6 `should` entries
  deferred to `wont` by CHG-032. Every row above has a registry entry with the same id.
- **Deferred requirements.** A row whose `Prio` is `wont` is out of this delivery. The requirement id
  and its `fit_criterion` stay in the registry (ids are frozen); the registry carries the
  `deferred_reason` and the schema rejects a `wont` entry without one. Deferred rows say
  `none — deferred` in the component and monitor columns and point at the registry reason instead of
  a test, so they are not counted as gaps.
- **Planned components.** Rows whose component is marked *(planned)* have no module yet; their
  `fit_criterion` is not yet checkable, and their tests/monitors are the intended evidence once the
  owning change lands. This is recorded so the gap is visible rather than implied as done.
- **Evaluation harness (CHG-036/CHG-037).** `COST-001` and `EVAL-001` are now measured with the same artifact:
  `python -m eval.run` replays `eval/fixed-set.json`, judges `eval/thresholds.yaml` against the
  `eval/baseline.json` record, and exits on the verdict (ADR-007). `gate-4-semantic-eval` runs that
  command on every pull request, so a failed threshold blocks the merge; the run's `context_usage` is
  the whole-request ledger.
- **Invariant fallbacks** (the "what to do when violated" action for `TERM-001`, `CTX-003`,
  `SAFE-001/002/003`) live in `docs/architecture/invariants.md`.
- **Verification rules** (fit-criterion coverage, negative tests, test-to-requirement references,
  zero-regression rounds, three-tier verification) live in
  `docs/code-governance/verification-constraints.md`.
