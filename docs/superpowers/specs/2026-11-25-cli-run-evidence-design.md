# CLI Run Evidence — design

**Change:** CHG-057
**Status:** proposed, awaiting approval
**Related requirements:** `D1-REQ-OBS-001`, `D1-REQ-OBS-002`, `D1-REQ-OBS-003`,
`D1-REQ-COST-003`, `D1-REQ-TERM-001`, `D1-REQ-SAFE-001/002/003`,
`D1-REQ-DEBATE-001/002`, `D1-REQ-MEM-003`

## Intent

The inherited CLI still shows only the upstream live view: agent status, messages, the current
report and a provider-token footer. The project's distinguishing modules — context budget,
telemetry, structured debate, termination, guardrails and memory attribution — write machine-readable
artifacts but are invisible to someone running `tradingagents`.

This change makes the existing evidence visible without changing the live layout or the graph's
orchestration:

1. **A. Post-run panel.** After a run ends, print a compact `Run Evidence` panel in the same Rich
   style as the existing view.
2. **B. `tradingagents inspect`.** Read a finished run's state log, trace and manifest and print the
   same panel later, without re-running the analysis.

## Goals

- Show the decision, its source (`structured` / `free_text` / `review`) and the termination reason.
- Show context spend against the run budget, compaction count and the largest call.
- Show structured debate records with short excerpts of claim, evidence and convergence.
- Show guardrail actions: blocked instruction spans, clipped position sizes, REVIEW fallbacks and
  budget REVIEW.
- Show memory attribution: the memory note and the `src:` ids injected into the run.
- Show per-phase telemetry (tokens, estimated cost, wall-clock) and the trace/manifest paths.
- Keep the inherited live layout, colours, panels and tables unchanged.

## Non-goals

- No redesign of the live `Layout` or the progress/messages panels.
- No new evaluation command and no change to `python -m eval.run`.
- No change to prompt files, model routing or LangGraph wiring.
- No change to the behaviour of the pure guardrail functions (`scrub_untrusted`,
  `enforce_position_ceiling`, `clip_free_text_decision`, `validate_free_text_decision`).
- No network access, no API keys and no new dependency.

## Approaches considered

| Approach | Why chosen / rejected |
|---|---|
| **A + B (chosen)** | A gives immediate visibility at the end of a run; B makes the evidence reusable for demos and post-mortems. Both are additive and keep the front-end style. |
| A only | Lower cost, but a reviewer cannot inspect a run without re-running it; the demo loses replayability. |
| Rebuild the live layout | Rejected: large blast radius on inherited display tests and no requirement asks for it. |
| Parse `message_tool.log` for guardrails | Rejected: guardrails log through `logging`, not the CLI message buffer; the log does not carry structured events. |
| Add a new `run_evidence.json` artifact | Rejected for now: the state log, trace and manifest already carry the data; a fourth artifact is unnecessary. |

## Data flow

```text
run
 ├─ context assembler ──► state log: context_usage
 ├─ debate nodes ───────► state log: turn_records
 ├─ guardrail call sites ─► telemetry trace: kind=guardrail spans
 ├─ telemetry ──────────► trace_<date>.json + manifest_<date>.json
 └─ final state ────────► final_decision_source, termination_reason, memory_note
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
            post-run panel                  inspect command
          (in-memory state + files)      (state log + files)
```

### Guardrail events

Guardrail actions become telemetry spans with `kind="guardrail"`:

| Event | Emitted at | `reason` |
|---|---|---|
| `guardrail.instruction_blocked` | `retrieved_block`, analyst tool-result scrubbing, sentiment pre-fetch | pattern names, never the hostile text |
| `guardrail.position_clipped` | Portfolio Manager, structured and free-text paths | claimed and applied percentages |
| `guardrail.decision_review` | Portfolio Manager, invalid free-text fallback | the contract failure, e.g. "no single explicit rating" |
| `guardrail.budget_review` | Portfolio Manager, `ContextBudgetExceeded` | "context budget exhausted" |

A new helper `guardrail_event(name, reason, node=None)` uses the existing telemetry `span` context
manager. It takes the phase of the active span when one exists, so the manifest phase table is not
polluted with a synthetic `guardrail` phase. Outside a telemetry scope it is a no-op; a disabled
telemetry run writes nothing and the CLI says so.

### State-log additions

`_log_state` records three additive fields so `inspect` can render the same evidence:

- `final_decision_source`
- `memory_note`
- `memory_sources` (distinct `src:` ids parsed from `past_context`)
- `turn_records` inside both debate states

The state log remains readable JSON; no existing field is removed or renamed.

## Display

The panel uses the existing `Panel`, `Table`, `box.SIMPLE_HEAD`, magenta headers and green/cyan
borders. It has four short blocks:

```text
╭─ Run Evidence ──────────────────────────────────────────────╮
│ Decision  Overweight · structured · termination normal      │
│ Context   43.5k / 50.0k (87%) · compacted 2 · max call 12k  │
│ Memory    1 prior lesson · src:2026-10-01/NVDA              │
│ Telemetry trace …/telemetry/trace_2026-11-20.json           │
│           manifest …/telemetry/manifest_2026-11-20.json     │
│                                                              │
│ Structured Debate                                           │
│ Debate    Turns  Claim                    Converge          │
│ Research  3      Guidance raised 8% …    Demand is strong … │
│ Risk      3      Valuation is stretched  Trim into strength │
│                                                              │
│ Guardrails                                                  │
│ Position clipped  50% exceeds the 10% ceiling; clipped …    │
│                                                              │
│ Phases                                                      │
│ Phase              Tokens   Cost     Time                   │
│ market             21.4k    $0.031   18.2s                  │
│ …                                                           │
╰──────────────────────────────────────────────────────────────╯
```

Text excerpts are collapsed to a single line and truncated (default 80 characters for debate
excerpts, 120 for guardrail details). Full reports remain in the saved report tree and the existing
`Current Report`/complete-report paths.

## Failure behaviour

- Missing trace or manifest: the panel says `not written` and still shows the in-memory evidence.
- Telemetry disabled: no trace/manifest; guardrail section says `telemetry disabled`.
- Malformed JSON in an old state log/trace: `inspect` prints one red line and exits 1; it does not
  raise a traceback.
- Unknown ticker/date: `inspect` prints the expected path and exits 1.
- Guardrail telemetry is advisory: a failing subscriber still cannot fail the run (`OBS-003`).

## Commands

```bash
# Post-run panel: automatic after every successful analysis
tradingagents

# Inspect a recorded run (date omitted = newest state log for the ticker)
tradingagents inspect NVDA 2026-11-20
tradingagents inspect NVDA --results-dir /path/to/results
```

## Requirement trace

No new runtime requirement is introduced. The change surfaces existing monitors:

| Requirement | What the panel shows |
|---|---|
| `OBS-001` | trace path and run status |
| `OBS-002` | per-phase tokens, cost, wall-clock |
| `OBS-003` | guardrail events, subscriber-safe advisory events |
| `COST-003` | `context_usage`: budget, spent, compacted calls, max call |
| `TERM-001` | `termination_reason` |
| `SAFE-001` | blocked-instruction events |
| `SAFE-002` | REVIEW fallback events and `final_decision_source` |
| `SAFE-003` | position-clip events |
| `DEBATE-001/002` | `turn_records` and claim/evidence/converge excerpts |
| `MEM-003` | `memory_note` and `src:` ids |

If the reviewer decides a display-specific `should` requirement is required, register it before the
first `src/` commit; the plan already keeps the implementation additive, so it can cite that id.

## Governance

- Branch: `feat/CHG-057-cli-run-evidence`.
- Tests first; no commit mixes `test/` and `src/`.
- A human reviewer supplies the test-approval record (`Verdict: APPROVE`, `Tests:` line) before the
  first `src/` commit; the agent never approves or merges.
- Update `docs/ai-use-log/<member>.yaml`; add `docs/review-memo/PR-<n>.md` after the PR number is
  known.
- The change does not touch `.opencode/rules.md`, prompts, secrets or the authority boundary.
