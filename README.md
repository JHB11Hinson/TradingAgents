# TradingAgents — CS5351 Agentic Software Engineering Project

A three-member CS5351 project that extends the Tauric Research **TradingAgents** multi-agent LLM
framework. For one instrument on one trade date the system runs analysts, a structured bull/bear
debate, a research manager, a trader, a risk discussion and a portfolio manager, then returns a
researched rating and a written decision.

The product is an **analysis and decision-quality system**, not an order executor. Deterministic
code constrains what the model output may become; the model is advisory.

## 1. Purpose

The course names two pain points in the inherited prototype:

1. a single analysis is slow and token-burning;
2. the sub-agent debate is free-form.

This project extends the inherited baseline incrementally (it does not rewrite the LangGraph
orchestration) to address those points: structured debate turns, termination discipline, layered
context assembly, a token budget, observability, evaluation, and safety guardrails. The requirements
registry is the source of truth for what is in scope and what is still planned.

## 2. Architecture

The orchestration is a LangGraph state machine. Its public contract is
`TradingAgentsGraph(config=...).propagate(ticker, date) -> (final_state, decision)` and the console
script `tradingagents = cli.main:app`.

### 2.1 Agent workflow

```text
four analysts (fundamentals, sentiment, news, market)
        │
        ▼
bull/bear research debate
        │
        ▼
research manager ──► trader ──► risk discussion ──► portfolio manager
```

The analysts run in parallel. The debate and the risk discussion are bounded by
`max_debate_rounds` and `max_risk_discuss_rounds`; an analyst tool loop is bounded by
`max_tool_rounds` and ends in `wrap_up`.

### 2.2 Components

| Element | Module | Responsibility |
|---|---|---|
| Analysts | `src/tradingagents/agents/analysts/` | fundamentals, sentiment, news and market reports |
| Researcher debate | `src/tradingagents/agents/researchers/` | bull/bear debate |
| Research manager | `src/tradingagents/agents/managers/` | synthesis and the manager rating |
| Trader | `src/tradingagents/agents/trader/` | trade proposal |
| Risk management | `src/tradingagents/agents/risk_mgmt/` | aggressive/conservative/neutral risk discussion |
| Agent contracts | `src/tradingagents/agents/` (`state.py`, `schemas.py`, `structured.py`, `rating.py`, `context.py`, `tools.py`, `post_screen.py`) | state shape, structured output, `REVIEW` sentinel, context helpers, tool surface |
| Data access | `src/tradingagents/dataflows/` | provider chain, point-in-time rules, vendor errors |
| Orchestration | `src/tradingagents/graph/` | graph wiring, routing, checkpoints, propagation |
| LLM access | `src/tradingagents/llm_clients/` | provider clients, model catalog, key handling |
| Memory | `src/tradingagents/memory/` | decision log, reflection, settlement |
| Configuration | `src/tradingagents/default_config.py` | defaults and `TRADINGAGENTS_*` overrides |
| CLI | `src/cli/` | interactive and headless entry points, display, preferences |

### 2.3 Authority boundary

Model output — analyst reports, debate turns, the trader proposal, manager ratings — is
**advisory**. Deterministic code is **authoritative**:

- `agents/structured.py` binds a Pydantic schema;
- `agents/rating.py` turns an unparseable rating into `REVIEW`, which is not a tradeable position;
- a malformed final decision must be rejected or degraded, never emitted as a tradeable action.

**Current gap, stated honestly:** the deterministic position ceiling (`D1-REQ-SAFE-003`) is not
implemented yet, and the portfolio-manager path still has a free-text fallback that can parse a
rating after a structured-output failure. The invariant register
(`docs/architecture/invariants.md`) records both the rule and the fallback; the debt register
records the gap. Do not describe the boundary as fully enforced until those tests exist.

## 3. Repository organization

```text
.
├── AGENTS.md                     coding-agent governance (D3), the single entry point
├── Prompt.md                     static startup prompt (D9)
├── architecture-blueprint.md     master constraint document (D2.1)
├── README.md                     this file
├── Report.md                     process report and reflections (D6)
├── docs/
│   ├── req/                      requirements.yaml + req-schema.json (D1)
│   ├── architecture/             ADRs, invariants, trace matrix, permission model (D2);
│   │                             memory design, runtime policy catalog, evaluation table planned
│   ├── code-governance/          structural and verification constraints, MCP manifest (D3/D4)
│   ├── ai-use-log/               one AI-use log per active member (legacy file is an archive)
│   ├── review-memo/              one review record per pull request (legacy file is an archive)
│   ├── debt-register.md          technical debt (D4)
│   └── bug-diary.md              significant bugs and the invariant gap they exposed (D4)
├── .github/
│   ├── CODEOWNERS                path ownership
│   ├── PULL_REQUEST_TEMPLATE.md  change card and gate self-check
│   └── workflows/ci.yml          the blocking gates (D7)
├── .opencode/                    permissions.jsonc + human-only rules.md (D3)
├── .agent/rules.md               the project covenant (D3)
├── prompts/                      versioned runtime prompts (new files only)
├── src/                          application source (D8)
│   ├── tradingagents/
│   └── cli/
├── test/
│   ├── offline/                  deterministic tests, no network or keys
│   └── live/                     API-dependent tests
└── transcripts/                  annotated agent-session transcripts (D5)
```

## 4. Install

Python 3.11 or newer is required; the measured baseline is Python 3.12.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## 5. Run the tests

```bash
# Offline suite: deterministic, no network and no API keys
pytest -q test/offline

# Full suite (the same offline testpaths today; test/live is the API-dependent location)
pytest -q

# Live/integration tests, only when keys are configured
pytest -q -m integration test/live
```

`test/live/` currently holds no API-dependent tests; it is the reserved location for them. The
default `pytest` configuration excludes the `integration` marker.

Static checks used by the gates:

```bash
ruff check src
check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml
```

## 6. Blocking gates

The workflow `.github/workflows/ci.yml` is named `gates`. The gate name must match the
branch-protection `contexts` character for character.

| Gate | What it enforces | State |
|---|---|---|
| `gate-1-test-approval` | a `src/` change carries a `Test-Approval:` record approved before the first `src/` commit; test and implementation commits are separate | implemented on the CHG-030 branch; promotion to `main` pending |
| `gate-2-static-analysis` | `pip check`, `ruff`, and scoped `mypy` on the `src/**/*.py` files a PR touches; inherited errors are quarantined in `mypy-legacy.txt` | online |
| `gate-3-schema` | `requirements.yaml` validates against `req-schema.json` | online |
| `gate-4-semantic-eval` | a prompt or model change replays a fixed evaluation set against thresholds | planned (no evaluation set or runner yet; `DEBT-003`) |
| `gate-5-regression` | the full inherited and new offline suite (`pytest -q`); a regression blocks | online |
| `gate-6-ai-use-log` | a PR that changes `src/`, `test/` or `prompts/` updates the AI-use log | online |

Branch protection on `main`:

- at least one approving review from someone other than the author;
- `dismiss_stale_reviews: true`;
- required status checks are strict (the branch must be up to date);
- `enforce_admins: true`, no force pushes, no deletions.

The committed baseline is `docs/code-governance/protection.json`. The live setting is the fact;
if this file and the live setting disagree, fix this file.

## 7. Documentation map

| Question | File |
|---|---|
| How must the coding agent work? | `AGENTS.md` |
| What is the launch instruction? | `Prompt.md` |
| What constrains the architecture? | `architecture-blueprint.md`, `docs/architecture/adr/` |
| What must the product do? | `docs/req/requirements.yaml`, `docs/req/req-schema.json` |
| Where is each requirement implemented and monitored? | `docs/architecture/trace-matrix.md` |
| Which invariants must never be violated, and what happens if they are? | `docs/architecture/invariants.md` |
| How is verification governed? | `docs/code-governance/verification-constraints.md` |
| What are the permissions? | `.opencode/permissions.jsonc`, `docs/architecture/permission-model.md`, `AGENTS.md` §13 |
| What was reviewed, and what did the AI do? | `docs/review-memo/`, `docs/ai-use-log/`, `transcripts/` |

## 8. Baseline and licence

This repository is a graded fork of `TauricResearch/TradingAgents` (Apache-2.0), baseline commit
`1394a3f72aa4393e1a98f51b382434c4b4c2d972` (v0.6.0, 2026-10-03). The inherited packages were moved
under `src/` and the inherited suite under `test/offline/` by ADR-002. The upstream project is not
synced into `main`; upstream updates are handled as separate reviewed changes.

The licence is Apache-2.0; see `LICENSE`.

## 9. Team

| Member | Primary responsibility |
|---|---|
| `@JHB11Hinson` | repository governance, gates, observability, context and cost |
| `@AKAScarlett` | structured debate, termination discipline, quality control |
| `@SY1433` | memory, safety and evaluation |

All three share every path in `.github/CODEOWNERS`; GitHub does not allow self-approval, so every
change needs an approving review from someone other than its author.
