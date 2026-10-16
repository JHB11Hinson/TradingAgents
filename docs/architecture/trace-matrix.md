# Requirements trace matrix (D2.4)

- **Why this file exists:** the brief requires a trace matrix that maps **every requirement** to its
  **executing component**, its **test / evidence** and its **runtime monitor**
  (deliverable D2.4; requirement `D1-REQ-GOV-004`).
- **Requirement source of truth:** `docs/req/requirements.yaml` is the machine-readable registry
  (it currently registers the `must` set). The `should` / `could` items are tracked here from the
  team requirements draft ahead of their own registration change.
- **How to read it:** one row per requirement id. `Executing component` is the module that will
  carry the behaviour; `Test / evidence` is the artifact that makes the `fit_criterion` machine
  checkable; `Runtime monitor` is what is watched once the code is live.
- **Status:** baseline. Components marked *(planned)* do not exist yet; their tests/monitors are the
  planned evidence. Monitors marked *(via OBS-001)* depend on the telemetry event seam.
- **Maintenance:** whoever changes a requirement updates its row (team decision); the admin leads.

| REQ ID | Prio | Requirement (short) | Executing component | Test / evidence | Runtime monitor |
|---|---|---|---|---|---|
| D1-REQ-DEBATE-001 | must | Structured debate turns: claim, evidence, rebuttal, confidence | `src/tradingagents/agents/researchers`, `src/tradingagents/agents/schemas` | Schema-validator pass rate is 100% on the fixed set | `debate.turn` span + invalid-turn counter *(via OBS-001)* |
| D1-REQ-DEBATE-002 | should | Osborn-style diverge-then-converge per round | `src/tradingagents/agents/researchers` | Structural fields present + a round case | `debate.round` span with diverge/converge flags *(via OBS-001)* |
| D1-REQ-DEBATE-003 | should | Debate evidence-citation rate >= baseline | `src/tradingagents/agents/researchers` | `eval.run` summary metric | Evaluation logbook, per run |
| D1-REQ-DEBATE-004 | must | Rounds configurable with a hard upper bound; converge at the bound | `src/tradingagents/graph/conditional_logic` | Round upper-bound case | Round counter vs `max_debate_rounds` *(via OBS-001)* |
| D1-REQ-TERM-001 | must | Loop self-stops on oscillation, stall or budget exhaustion | `src/tradingagents/graph/conditional_logic` | Oscillation/stall cases self-terminate; detector-removal negative test turns red | Termination reason event; alert on unbounded loop |
| D1-REQ-TERM-002 | should | Analyst tool loop detects repeated identical calls | `src/tradingagents/graph/setup` | Repeated-tool-call case | `tool.repeat` counter *(via OBS-001)* |
| D1-REQ-CTX-001 | must | Layered context assembly (six layers) for every model call | `src/tradingagents/agents/context` *(planned assembler)* | Assembler unit test asserts each layer's presence and source | `context.assemble` span with layer-presence flags *(via OBS-001)* |
| D1-REQ-CTX-002 | should | Assembly pipeline dedupe -> prioritize -> budget -> compact -> assemble | `context/` module *(planned)* | Pipeline unit test shows stage order and drops | `context.pipeline` span per stage *(via OBS-001)* |
| D1-REQ-CTX-003 | must | Assembled context <= budget; constraints re-injected after compaction | `context/` module *(planned)* | Unit test asserts `assembled_tokens <= budget` and byte-identical re-injection | Budget-ceiling breach event + alert |
| D1-REQ-CTX-004 | should | Layered structure and pipeline recorded in an ADR | `docs/architecture/adr` | ADR review | Review checklist per ADR |
| D1-REQ-MEM-001 | should | Layered memory (working/episodic/semantic) survives sessions/versions | `src/tradingagents/memory` | Unit test round-trips each layer across restart and version bump | `memory.read`/`memory.write` spans *(via OBS-001)* |
| D1-REQ-MEM-002 | should | Prior reflections retrieved by semantic similarity | `src/tradingagents/memory` *(planned retrieval)* | Positive and negative retrieval cases | `memory.retrieve` span + hit ratio *(via OBS-001)* |
| D1-REQ-MEM-003 | should | Memory items source-attributable; no future leakage | `src/tradingagents/memory/log`, `date_window` | Point-in-time case | Future-dated item blocked event |
| D1-REQ-MEM-004 | could | Retention / rotation / size caps configurable | `src/tradingagents/memory/log` | Rotation case | Memory entry count vs cap *(via OBS-001)* |
| D1-REQ-COST-001 | must | Single analysis <= 50% of baseline tokens and cost | `context/`, `src/tradingagents/graph` *(planned)* | `eval.run` fixed-set totals <= 0.5 * baseline | Run manifest total_tokens / est_cost vs baseline |
| D1-REQ-COST-002 | should | Semantic cache with quantified savings | `cache/` *(planned)* | Cache hit and miss cases | Run manifest `cache_hit_rate` |
| D1-REQ-COST-003 | must | Single analysis <= configured token budget (default 50000), else compaction | `src/tradingagents/default_config`, `context/` | Over-budget triggers compaction case (`test_token_budget.py`) | Run manifest total_tokens <= budget; compaction event |
| D1-REQ-PERF-001 | should | Wall-clock <= 60% of baseline | `src/tradingagents/graph`, `src/tradingagents/dataflows` | `eval.run` p50 wall-clock <= 0.6 * baseline | Run manifest p50 wall-clock |
| D1-REQ-OBS-001 | should | Machine-parsable run trace (span / phase / duration) | `telemetry/` *(planned event seam)* | Trace parses; one span per step | The trace file itself |
| D1-REQ-OBS-002 | should | Token / cost / latency aggregated per phase (run manifest) | `telemetry/` *(planned)* | Manifest parse case | The manifest file itself |
| D1-REQ-OBS-003 | should | Structured step events; a failing subscriber must not block the run | `telemetry/` *(planned)* | Subscriber-raises case still completes | Telemetry warning count |
| D1-REQ-EVAL-001 | must | Fixed set + thresholds + regression runnable locally | `eval/` *(planned)* | Local run + threshold pass/fail | Evaluation logbook |
| D1-REQ-EVAL-002 | should | Prompt/model change triggers evaluation; failure blocks | `.github`, `eval/` *(planned)* | gate-4 case | gate-4 status in branch protection |
| D1-REQ-SAFE-001 | must | External/retrieved text scrubbed; hostile samples blocked | `guardrails/` *(planned)* | Injection corpus blocked 100%; scrubbing-off negative test turns red | Blocked-injection event + alert |
| D1-REQ-SAFE-002 | must | Invalid-schema decision rejected and degraded | `src/tradingagents/agents/structured`, `guardrails/` | Malformed-decision negative test | REVIEW/degrade event |
| D1-REQ-SAFE-003 | must | Deterministic position ceiling; model cannot bypass it | `guardrails/`, `src/tradingagents/agents/managers` | Bypass-attempt negative test | Ceiling-clip event |
| D1-REQ-QUAL-001 | should | Structured-output pass rate 100%; REVIEW rate not rising | `src/tradingagents/agents/*` | `eval.run` summary | Evaluation logbook |
| D1-REQ-GOV-001 | must | Repository layout satisfies the required structure | `src/`, `test/` | Inherited suite + `pip install -e ".[dev]"` | gate-5-regression on `main` |
| D1-REQ-GOV-002 | must | `AGENTS.md` covers the six required sections | `AGENTS.md` | Review checklist | Sprint review checklist |
| D1-REQ-GOV-003 | must | Six blocking gates online; each failed on a deliberate violation | `.github`, `docs/code-governance/protection.json` | Deliberate-violation experiments | Weekly branch-protection check (manual 8.2) |
| D1-REQ-GOV-004 | must | Trace matrix maps every requirement to component, test, monitor | `docs/architecture/trace-matrix.md` | Trace check: one row per REQ id | Sprint trace check (manual 8.3) |
| D1-REQ-GOV-005 | must | Agent tools x roles in `mcp-tool-manifest.md` | `docs/code-governance/mcp-tool-manifest.md` | Manifest vs permission-model consistency | Review checklist |
| D1-REQ-GOV-006 | must | Default-deny, per-path whitelist, consistent in three places | `.opencode/permissions.jsonc`, `docs/architecture/permission-model.md`, `AGENTS.md` | Three-way whitelist comparison | Review checklist |
| D1-REQ-GOV-007 | should | `structural-constraints.md`: element <-> module, extend not replace | `docs/code-governance/structural-constraints.md` | Structural (import/boundary) test | gate-2-static-analysis / structural test |
| D1-REQ-GOV-008 | must | `verification-constraints.md` + `invariants.md`: every rule has a test and fallback | `docs/code-governance/verification-constraints.md`, `docs/architecture/invariants.md` | Missing-entry check | Sprint review checklist |
| D1-REQ-GOV-009 | should | D2 architecture artifact set complete and consistent | `docs/architecture`, repo root | File-existence + blueprint-to-module mapping | Sprint review checklist |
| D1-REQ-GOV-010 | must | QA records: `review-memo.md` per PR, `debt-register.md`, `bug-diary.md` | `docs/` | Missing-entry check | Per-PR + weekly check (manual 8.1/8.2) |
| D1-REQ-GOV-011 | must | >=5 annotated transcripts over six stages; AI-use log current | `transcripts/`, `docs/ai-use-log.yaml` | gate-6 + coverage check | gate-6-ai-use-log + weekly check |
| D1-REQ-GOV-012 | should | Runtime prompts versioned as files, no in-place edits | `prompts/` | Versioned-file existence | Review checklist |
| D1-REQ-GOV-013 | must | Always-on rules + project covenant exist and agree | `.opencode/`, `.agent/` | File-existence + five covenant clauses | Sprint covenant check |

## Notes

- **Registry vs matrix.** `docs/req/requirements.yaml` currently registers the 21 `must` requirements
  (CHG-004). The `should` / `could` rows above are traced here ahead of their registration change, so
  that no requirement is lost between the draft and the registry.
- **Planned components.** Rows whose component is marked *(planned)* have no module yet; their
  `fit_criterion` is not yet checkable, and their tests/monitors are the intended evidence once the
  owning change lands. This is recorded so the gap is visible rather than implied as done.
- **Invariant fallbacks** (the "what to do when violated" action for `TERM-001`, `CTX-003`,
  `SAFE-001/002/003`) live in `docs/architecture/invariants.md` (to be written under
  `D1-REQ-GOV-008`).
