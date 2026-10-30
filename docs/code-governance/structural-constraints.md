# Structural constraints

**Deliverable:** D3. **Requirement:** `D1-REQ-GOV-007`.
**Related:** `AGENTS.md` §6 (module organization), `docs/architecture/trace-matrix.md` (per-requirement
mapping), ADR-001, ADR-002, ADR-003.

These constraints bind every change. They are short on purpose: each one is checkable.

---

## 1. One architectural element maps to exactly one module

A **module** is a package (a directory) or a single file under `src/`. An element must not be split
across two modules, and two elements must not own the same module.

| Architectural element | Module | What it owns |
|---|---|---|
| Analyst team | `src/tradingagents/agents/analysts/` | fundamentals, sentiment, news and market analysts |
| Researcher debate | `src/tradingagents/agents/researchers/` | the bull/bear debate |
| Research manager | `src/tradingagents/agents/managers/` | research synthesis and the manager ratings |
| Trader | `src/tradingagents/agents/trader/` | the trade proposal |
| Risk management | `src/tradingagents/agents/risk_mgmt/` | the risk discussion |
| Agent contracts | `src/tradingagents/agents/` (`state.py`, `schemas.py`, `structured.py`, `rating.py`, `context.py`, `tools.py`, `post_screen.py`) | state shape, structured output, the REVIEW sentinel, context assembly, tool surface, post screening |
| Data access | `src/tradingagents/dataflows/` (+ `vendors/`) | the provider chain, point-in-time rules, vendor errors |
| Orchestration | `src/tradingagents/graph/` | graph wiring, routing, checkpoints, propagation |
| LLM access | `src/tradingagents/llm_clients/` | provider clients, model catalog, key handling |
| Memory | `src/tradingagents/memory/` | decision log, reflection, settlement |
| Backtest evaluation | `src/tradingagents/backtest.py` | grid runs and decision scoring |
| Portfolio context | `src/tradingagents/portfolio.py` | holdings input |
| Reporting | `src/tradingagents/reporting.py`, `src/tradingagents/report_html.py` | report trees and the HTML page |
| Configuration | `src/tradingagents/default_config.py` | defaults and `TRADINGAGENTS_*` overrides |
| CLI | `src/cli/` | interactive and headless entry points, display, preferences |

Package data (`src/tradingagents/assets/`, `src/cli/static/`) is not a module and carries no element.
`src/tradingagents/` and `src/tradingagents/__init__.py` are the package root and its initializer;
they carry no element of their own.

The module list must match `src/`. When a module is added, split or removed, this table changes in the
same pull request.

## 2. New work extends the baseline; it never replaces it

- Extend an element by adding to its module or by adding a **new** module with its own row above.
- Do not rewrite an inherited module to "clean it up". Refactors are allowed only when they keep
  behaviour and are covered by the inherited tests.
- Do not move an element to a different module as a side effect of another change; a move is its own
  change with its own ADR (as ADR-002 did for the `src/` layout).
- A replacement needs an ADR that says what it replaces, why the baseline cannot be extended, and how
  the inherited tests keep passing.

## 3. Every module references the ADR and the invariant it implements

| Module | ADR | Requirement / invariant it carries |
|---|---|---|
| `agents/` | ADR-001 | `CTX-001`/`CTX-003` (layered context, budget), `DEBATE-001` (structured turns), `SAFE-002` (schema failure → REVIEW) |
| `agents/managers/`, `agents/trader/`, `agents/risk_mgmt/` | ADR-001, ADR-003 | `SAFE-002`, `SAFE-003` (authority boundary) |
| `dataflows/` | ADR-001 | `MEM-003` (point-in-time, no future leakage), `SAFE-001` (external text scrubbed) |
| `graph/` | ADR-001 | `TERM-001` (self-termination), `DEBATE-004` (round bound), `COST-003` (token budget) |
| `memory/` | ADR-001 | `MEM-001`–`MEM-004` |
| `llm_clients/` | ADR-001 | provider and model selection; no invariant of its own |
| `backtest.py`, `portfolio.py`, `reporting.py`, `report_html.py` | ADR-001 | reporting and evaluation; no invariant of their own |
| `default_config.py`, `cli/` | ADR-001, ADR-002 | `GOV-001` (layout), configuration surface |

The **authoritative** requirement-to-component mapping is `docs/architecture/trace-matrix.md`; this
table is the structural view. `docs/architecture/invariants.md` (GOV-008) will hold the invariant
statements and fallbacks; until it exists, the requirement ids above are the reference.

## 4. Authority boundary: advisory model output, authoritative deterministic code

- **Advisory:** everything a model produces — analyst reports, debate turns, the trader's proposal,
  manager ratings. It informs a decision; it does not become one by itself.
- **Authoritative:** the deterministic code that validates and constrains it.
  - `agents/structured.py` binds a schema; a response that does not match is not trusted.
  - `agents/rating.py` turns an unparseable rating into `REVIEW` (line 30, `RATING_REVIEW`), which is
    not a tradeable position.
- **No bypass:** a model output may not reach a tradeable decision by skipping that code. A change
  that lets model output set a final action directly is a safety-critical change (ADR + human review).

**Known gap, stated honestly:** the deterministic position ceiling (`D1-REQ-SAFE-003`) is **not
implemented yet**. Until it lands, the boundary is enforced only by schema validation and the REVIEW
sentinel. The gap is recorded in `docs/architecture/trace-matrix.md`; it must not be described as
enforced.

## 5. Enforcement

| Constraint | How it is checked |
|---|---|
| Vendor libraries are imported only by the data layer | `test/offline/test_layering.py` (inherited structural test; fails on a violation) |
| Changed `src/**/*.py` stay lint- and type-clean | `gate-2-static-analysis` (batch 2, PR #11) |
| No inherited test is weakened, skipped or renamed | review; `gate-5-regression` |
| Module list matches `src/` | the check below, run at review |
| Authority boundary is not bypassed | review; `SAFE-002`/`SAFE-003` tests once they land |

```bash
# packages and top-level modules; a file inside a listed package is covered by that package's row,
# and __init__.py is the package initializer
find src -mindepth 1 -maxdepth 2 -type d \
  -not -path '*__pycache__*' -not -path '*egg-info*' -not -path '*assets*' -not -path '*static*' | sort
ls src/tradingagents/*.py
```

An element without a row, a module without an element, or a module whose ADR/invariant column is
empty is a review blocker.
