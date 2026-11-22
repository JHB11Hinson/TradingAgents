# ADR-014: Explicit memory source attribution for injected lessons

- **Status:** proposed (CHG-050, 2026-11-22). Awaiting human review; the coding agent wrote
  the draft and does not approve or merge it.
- **Requirements:** `D1-REQ-MEM-003`.
- **Related:** ADR-001 (adopt inherited architecture), `docs/architecture/memory-design.md` §4,
  `DEBT-009` (mypy quarantine).
- **Safety-critical path:** `src/tradingagents/memory/log.py` is a retrieval path; this change needs
  human review with this ADR (`AGENTS.md` §11).

## Context

`D1-REQ-MEM-003` requires that **every retrieved memory item be source-attributable** and that a
historical run not read outcomes unknown as of its analysis date. The point-in-time half is already
implemented and tested (the `resolved:` tag and the `as_of` filter in `get_past_context`, #1251).

The attribution half is only implicit. An injected block's tag line carries the trade date and the
ticker (`[2026-01-05 | NVDA | Buy | …]`), and `docs/architecture/memory-design.md` §4 already claims
the entry "carries its source id by construction (the tag line)". But no exposed field names that
id, and no test asserts it. A caller cannot mechanically attribute an injected lesson to a specific
stored decision, so the fit criterion "each injected item carries its source id" is not checkable.

## Decision

Derive an explicit `source_id` of the form `<trade_date>/<ticker>` and carry it on every retrieved
item.

- `_parse_entry` adds `source_id = f"{date}/{ticker}"` to the entry dict, so `load_entries()` and
  `get_past_context()` expose a machine-readable id.
- A single helper `TradingMemoryLog._source_id(entry)` computes the id, so there is one seam to test
  and to remove in a negative test.
- `_format_full` and `_format_reflection_only` render `| src:<date>/<ticker>` into the block tag; that
  rendered text is what `get_past_context` injects into the Portfolio Manager's `retrieved` layer.
- The on-disk log format is **unchanged**: `store_decision`, `update_with_outcome` and `_resolved_tag`
  are not touched. The id is computed on read.
- The point-in-time filter semantics are unchanged.

## Alternatives rejected

- **UUID assigned at write time.** Rejected: it changes the on-disk schema and needs a migration for
  existing logs; legacy entries would have no id. The date+ticker pair is already unique per decision
  (the idempotency guard in `store_decision` rejects a second entry for the same ticker and date).
- **A hash of the whole entry.** Rejected: unreadable in the prompt, brittle for tests, and it changes
  when the reflection text changes even though the decision did not.
- **A separate source-index file.** Rejected: a second piece of state that can drift from the log; the
  log is the evidence record and should stay the single source.

## Consequences

- Every injected lesson is attributable with zero migration; legacy entries get a stable id on read.
- The id is stable and unique because the idempotency guard already forbids two entries for one
  ticker and date.
- The injected text grows by about ten tokens per item (up to eight items: five same-ticker, three
  cross-ticker). This is inside the context budget; `gate-4-semantic-eval` (run locally before the
  implementation) must confirm `COST-001`/`COST-003` thresholds still pass. If a threshold is tight,
  the tag may shorten to `@<date>/<ticker>` without changing the id.
- `src/tradingagents/memory/log.py` can be de-listed from `docs/code-governance/mypy-legacy.txt` once
  the change is type-clean, lowering the `DEBT-009` count; if it is not clean, it stays quarantined
  and the PR records why.
