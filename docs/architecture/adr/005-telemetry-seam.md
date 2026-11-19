# ADR-005: In-process telemetry seam, run trace and run manifest

- Status: accepted, implemented in CHG-034 (`src/tradingagents/telemetry/`)
- Date: 2026-11-20
- Deciders: the three active team members
- Related: ADR-001, ADR-002, ADR-004, `D1-REQ-OBS-001`, `D1-REQ-OBS-002`,
  `D1-REQ-OBS-003`

## Context

The inherited pipeline reports progress through the CLI display and the saved state log. Neither is
machine-parsable per step: there is no record of which agent or tool ran, in which phase, for how
long, and at what token or dollar cost. The architecture blueprint (§8) requires a trace of spans, a
per-phase run manifest and an in-process event seam, and forbids turning the orchestration into an
event-driven system (`AGENTS.md` §2).

Two constraints shape the decision:

- **The graph is the orchestrator.** LangGraph still decides what runs; telemetry only observes.
- **Telemetry is advisory.** A trace that fails to write, or a subscriber that raises, must never
  change a decision or stop a run.

## Decision

**1. One hub per run, in a context variable.** `telemetry_scope(config)` opens a `Telemetry` hub for
the duration of a run. A nested scope reuses the open hub, so a caller can subscribe before calling
the graph and still see every event. `telemetry_enabled=false` yields no hub: `span()` is a no-op and
no file is written.

**2. One span per agent or tool step.** `graph/setup.py` wraps every node with `_traced`. An analyst's
private subgraph contributes `"<key>.agent"`, `"<key>.tools"` and `"<key>.wrap_up"` spans; a
top-level node contributes one span under its node name. A span records the phase, the kind
(`agent`, `tool`, `wrap_up`), start, end and duration.

**3. Token usage follows the call into its span.** `TelemetryCallback` is a LangChain callback
handler: `on_llm_end` reads `usage_metadata` and adds `input_tokens`/`output_tokens` to the span that
is active in the current context. LangGraph copies the context into each parallel branch, so two
analysts running side by side never share an active span.

**4. Two files, next to the state log.** At the end of a run the graph writes
`<results_dir>/<ticker>/TradingAgentsStrategy_logs/telemetry/trace_<date>.json` and
`manifest_<date>.json`.

- The **trace** is `{"run_id": ..., "status": ..., "spans": [...]}`: one record per step,
  deterministic key order. `status` is `complete` or `failed`, so a crashed leg is not mistaken for
  a finished run. Span attributes are an allowlist (`node`, `error`, `model`); prompts, endpoints,
  keys and local paths cannot reach the file.
- The **manifest** aggregates input/output tokens, estimated cost and wall-clock per phase, plus
  totals, status and warnings. Prices come from a local table (`pricing.py`), in USD per million
  tokens; an optional `telemetry_pricing` config mapping overrides it for a caller that knows its
  provider's prices. A model absent from the table costs zero and adds a warning; telemetry never
  calls a provider. Wall-clock is the sum of that phase's span durations: spans inside one phase are
  sequential steps.

A **resumed** run (`checkpoint_enabled`) continues a failed leg. When it finishes, it reads the
previous trace back and prepends those spans before writing the merged trace and manifest, so the
record describes the whole logical run rather than only the leg that happened to finish.

The `telemetry/` subdirectory is deliberate. The inherited
`test_a_graph_reused_across_runs_keeps_no_run_state` counts `*.json` in the state-log directory; a
subdirectory keeps that contract true without weakening the inherited test.

**5. Failures are warnings.** A subscriber that raises is caught and recorded in
`Telemetry.warnings`; the run continues. `KeyboardInterrupt` and `SystemExit` are not subscriber
failures and still stop the run. A trace or manifest write error is a logged warning; the decision is
already recorded.

**6. The seam is the extension point.** The hub accepts subscribers, so a future OTel exporter or a
dashboard is a subscriber, not a change to the graph. This ADR does not add such an exporter.

## Alternatives considered

- **Adopt the OTel SDK now.** Rejected: a new dependency and exporter configuration well beyond
  `OBS-001/002`; the in-process seam is the prerequisite, and an OTel subscriber can be added later.
- **Log only.** Rejected: free-text logs do not satisfy "machine-parsable trace with one span per
  step", and per-phase aggregation would parse strings.
- **Measure tokens only in the context assembler.** Rejected: tool spans and provider calls that
  bypass the assembler would be invisible; `usage_metadata` is the provider's own count.
- **Let a telemetry error fail the run.** Rejected: observability must not decide a trade. The
  authority boundary puts deterministic decisions first.
- **Write one trace file per node.** Rejected: partial files on a crash, and the trace would not be
  one parsable run record.
- **An event bus between nodes.** Rejected explicitly by `AGENTS.md` §2: the graph stays the
  orchestrator.

## Consequences

- A run gains two small JSON files; with telemetry off it gains nothing.
- Cost is an **estimate** from a static price table, not a provider invoice; an unknown model is
  visible as a warning rather than silently free.
- Wall-clock per phase is the sum of sequential spans, not a critical-path measurement.
- The trace attribute allowlist must be extended deliberately; that is the point.
- `OBS-001/002/003` are covered by `test/offline/test_telemetry_{seam,trace,manifest,integration}.py`,
  including the negative tests for a raising subscriber, an unknown model and a disabled switch.

## Reconsider if

- A collector (OTel, Langfuse) becomes a delivery requirement: implement it as a subscriber.
- Provider pricing changes often enough that the static table misleads: load prices from a reviewed
  data file, keeping the zero-plus-warning fallback.
- The graph gains steps that are not nodes (for example a background worker); they need an explicit
  span, not an implicit one.
