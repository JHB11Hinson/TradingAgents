# Memory and state design (D2.5)

**Status:** accepted 2026-11-20. **Owner:** `@JHB11Hinson` (context/cost area), reviewed by the team.
**Requirement:** `D1-REQ-GOV-009` (D2.5); carries `D1-REQ-MEM-003` and `D1-REQ-MEM-004`.
**Related:** ADR-001, ADR-004, ADR-005; `src/tradingagents/memory/`, `src/tradingagents/graph/checkpointer.py`.

This document says what state survives a run, an interruption and a version change; how it is
written and retrieved; who owns it; how long it is kept; and what is deliberately **not** stored.
It describes the shipped code, not an aspiration: where a capability is deferred, the deferral is
named with its requirement id.

---

## 1. What persists, and where

| Store | Path (default) | Written by | Survives a session | Survives an interruption | Survives a version change |
|---|---|---|---|---|---|
| Decision log ("memory log") | `~/.tradingagents/memory/trading_memory.md` | `memory/log.py` | yes | yes (append-only) | yes — plain Markdown, no schema |
| Reflection | inside the memory log, under the settled entry | `memory/reflection.py` | yes | yes | yes |
| Checkpoint | `~/.tradingagents/cache/checkpoints/<TICKER>.db` (SQLite) | `graph/checkpointer.py` | yes | yes — this is its purpose | **no** by default: the thread id folds in a run signature, so different settings start fresh |
| State log | `<results>/<TICKER>/TradingAgentsStrategy_logs/full_states_log_<date>.json` | `graph/trading_graph.py` | yes | no (written when the run ends) | yes — JSON of the run's output |
| Trace and manifest | `<results>/<TICKER>/TradingAgentsStrategy_logs/telemetry/` | `telemetry/` | yes | failed leg written as `status: failed` | yes |
| Market-data cache | `~/.tradingagents/cache/` | `dataflows/` | yes | yes | best-effort; staleness is checked on read |
| In-run working state | LangGraph state | the graph | no | only through the checkpoint | no |

The base directory is `TRADINGAGENTS_DATA_DIR` / `TRADINGAGENTS_CACHE_DIR` when set
(`default_config.py`). Every store is **local files**; nothing is uploaded.

## 2. Layers: working, episodic, semantic

The course asks for a layered memory design. The shipped system realises three layers with two
mechanisms, and it does **not** claim the fourth (semantic/embedding retrieval):

| Layer | Realisation | Lifetime |
|---|---|---|
| Working | the LangGraph state of the current run (messages, reports, debates) | one run |
| Episodic | the memory log: one entry per decision with its outcome and a reflection | across runs |
| Semantic | the reflection text itself, retrieved by ticker and trade date | across runs |
| (Deferred) embedding index | not implemented | — |

`D1-REQ-MEM-001` (a three-layer persistence subsystem) and `D1-REQ-MEM-002` (embedding similarity)
are `wont`: the registry carries their `deferred_reason`. The product keeps one honest episodic store
instead of a second system that would duplicate it.

## 3. Write policy

- **One entry per (ticker, trade date).** `TradingMemoryLog.store_decision` scans the raw file for a
  line starting `[<date> | <ticker> |` and returns if one exists, so a re-run after the outcome
  landed cannot count the same decision twice. The log is opened append-only under a file lock
  (`dataflows/files.py:locked`) so two runs cannot interleave.
- **Entry shape.** `[date | ticker | rating | pending]`, then `DECISION:`, then the final decision
  text; entries are separated by the HTML comment `<!-- ENTRY_END -->`, which cannot occur in model
  prose. Settlement rewrites the tag to `resolved` and appends `REFLECTION:`.
- **Settlement.** `memory/settlement.py` settles a decision once its holding period has traded:
  it fetches the price, computes raw and alpha return, and asks `Reflector` for 2–4 sentences. A
  settlement failure is recorded and the entry stays pending; it is retried by a later run.
- **Reflection prompt.** The reflector is told the window length and to say plainly when the window
  is too short to judge the thesis (`memory/reflection.py`). The output is stored verbatim.
- **Idempotency over cleverness.** No update-in-place of decision text, no merging of entries: the
  log is evidence.

## 4. Retrieval policy

- `TradingMemoryLog.get_past_context(ticker, as_of)` reads the entries for the ticker and filters
  out anything resolved **after** `as_of`. A backdated run therefore sees only what was known on its
  date (`D1-REQ-MEM-003`, point-in-time). The filter is a string compare on the stored dates.
- Every injected block carries an explicit `source_id` of the form `<trade_date>/<ticker>`, derived
  on read from the tag line (`_source_id`; ADR-014) and rendered as `| src:<id>`. The id is stable and
  unique because the idempotency guard forbids two entries for one ticker and date, and it needs no
  migration: the on-disk log format is unchanged.
- The graph's Memory Log step runs beside the analysts (`graph/trading_graph.py:_memory_step`),
  settles every due decision, then injects the ticker's lessons into the Portfolio Manager's context
  as the `retrieved` layer, under the assembler's budget (ADR-004).
- Retrieval is **ticker + recency**, not similarity. A lesson learned on NVDA is not injected into a
  BABA run; `MEM-002` is the requirement that would change that, and it is deferred.

## 5. Ownership

`src/tradingagents/memory/` owns the log, the reflection and the settlement; `graph/checkpointer.py`
owns the checkpoints; `graph/trading_graph.py` owns the state log and the run scope. No agent module
writes a memory file directly. Configuration is read through `DEFAULT_CONFIG` /
`TRADINGAGENTS_*` overrides, so the persistence paths have one source of truth (`AGENTS.md` §8).

## 6. Retention and rotation

- **Memory log.** `memory_log_max_entries` caps the number of **resolved** entries; pending entries
  are never pruned (`D1-REQ-MEM-004`). `None` (the default) disables rotation. The file is small
  prose, so the cap is a hygiene knob, not a performance one.
- **Checkpoints.** Cleared on a successful run (`clear_checkpoint_on_success`); a crash leaves the
  last successful step, which is the resume point.
- **Results.** State logs, traces and manifests accumulate under `results_dir`; they are evidence and
  are deleted only by a human, deliberately.
- **Market-data cache.** Freshness is validated on read (stale bars are refused rather than served).

## 7. Privacy

- Everything is local; there is no telemetry upload. `run_settings` is an allowlist — provider,
  model names, analyst selection, limits, language, vendors — and never a URL, a key or a local path.
- The trace attribute allowlist is `node`, `error`, `model` (`telemetry/events.py`), so a key or a
  path cannot be written into a trace.
- The memory log contains the decision prose the model produced; it is analyst commentary, not user
  data. There is no PII collection path in the product.
- Secrets are supplied through environment variables only; `docs/code-governance/permission-model.md`
  denies reading `.env*` to the coding agent.

## 8. Degradation and failure

| Failure | Behaviour | Where |
|---|---|---|
| Memory log unreadable | the run continues with `memory_note` set; the report says the log could not be read | `graph/trading_graph.py:_memory_step` |
| Settlement fails (missing price) | the entry stays pending, the run continues, the note lists how many are unsettled | `memory/settlement.py` |
| Checkpoint corrupt | the resume fails; a fresh run is the fallback (the operator clears the DB) | `graph/checkpointer.py` |
| State-log write fails | the decision is still returned; the exception propagates only at the caller | `graph/trading_graph.py:_log_state` |
| Trace/manifest write fails | a warning; the run's decision is unaffected | `telemetry/wiring.py` |

## 9. Versioning and migration

- The memory log has **no schema**: entries are Markdown, so an older entry is readable by a newer
  build. The entry tag is the only parsed contract; a format change must keep the tag line and is a
  new ADR.
- A checkpoint is tied to the run's **signature** (analyst selection, debate depth, risk depth, asset
  mode, portfolio fingerprint, and the digest of the rest of the config). A changed signature starts
  a fresh run rather than resuming a incompatible graph (`graph/trading_graph.py:_run_signature`).
- The state log records `run_settings` so a later reader can tell which settings produced it.

## 10. Known gaps

| Gap | Requirement | Where recorded |
|---|---|---|
| no embedding/semantic retrieval | `D1-REQ-MEM-002` (wont) | registry `deferred_reason` |
| no three-layer persistence subsystem | `D1-REQ-MEM-001` (wont) | registry `deferred_reason` |
| a lesson is retrieved per ticker, not across tickers | `D1-REQ-MEM-002` | registry |
| the memory log is human-readable prose, not a queryable store | — | this file, section 2 |
