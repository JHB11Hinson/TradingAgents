# AGENTS.md

**Repository:** `JHB11Hinson/TradingAgents` (a graded fork of `TauricResearch/TradingAgents`, Apache-2.0).
**Deliverable:** D3 — coding governance. **Requirement:** `D1-REQ-GOV-002`.
**Owner:** `@JHB11Hinson`. **Reviewers:** any of the four team members (`*` in `CODEOWNERS`).

---

## 1. Purpose and how to use this file

This is the **single entry point** for the coding agent. Read this file first, then `Prompt.md`,
then the artifacts in the order given in §3.

- **Language.** Every repository file is English: code, comments, docs, YAML/JSON, prompts, gate
  names, commit messages, branch names, PR titles. The Chinese course manuals and the requirements
  draft are local and untracked.
- **Ownership.** Four members share every path (`.github/CODEOWNERS`): `@JHB11Hinson`,
  `@AKAScarlett`, `@zihao9462-creator`, `@SY1433`. GitHub does not allow self-approval, so every
  change needs an approving review from someone other than its author.
- **Protected path.** This file is the agent's single entry point; like every repository path it
  changes only through a reviewed pull request. The one file the course marks human-only is
  `.opencode/rules.md` (see §11).

---

## 2. Build target

**Extend the inherited TradingAgents framework incrementally. Do not rewrite the LangGraph
orchestration.** The system is a multi-agent LLM trading framework: analysts → bull/bear research
debate → research manager → trader → risk discussion → portfolio manager.

The work targets the two pain points named by the course:

1. a single analysis is **slow and token-burning**;
2. the sub-agent **debate is too free-form** (structure it with a requirements-engineering method,
   e.g. Osborn's diverge-then-converge).

**Deliverables:** D1 (requirements), D2 (architecture artifacts), D3 (coding governance),
D4 (verification and QA), D5 (session transcripts), D6 (`Report.md`), D7 (gates and branch
protection), D8 (`src/` and `test/`), D9 (`Prompt.md`).

**Non-goals** (guard against scope creep):

- do **not** replace LangGraph with an event bus, actors or an async queue;
- do **not** turn the project into a portfolio simulator or an order executor (`backtest.py` stays
  "decision-quality evaluation");
- do **not** add capability purely to inflate a score; every requirement must trace to the course
  material or to a named frontier practice.

---

## 3. Artifact reading order

Read in this order. The machine-readable source of truth wins over prose when they disagree.

| # | Artifact | What it holds |
|---|---|---|
| 1 | `AGENTS.md` (this file) | governance entry point |
| 2 | `Prompt.md` | the static startup prompt (D9); the launch instruction |
| 3 | `architecture-blueprint.md` | the master constraint document (D2.1) |
| 4 | `docs/req/requirements.yaml` + `docs/req/req-schema.json` | requirements registry and its schema (D1) |
| 5 | `docs/architecture/adr/` | architecture decisions (ADR-001 baseline, ADR-002 src layout) |
| 6 | `docs/architecture/trace-matrix.md` | requirement → component → test → runtime monitor |
| 7 | `docs/code-governance/protection.json` | the committed branch-protection baseline (D7) |
| 8 | `.github/workflows/ci.yml` | the real gate names and their steps |
| 9 | `docs/review-memo.md`, `docs/ai-use-log.yaml` | per-PR review records and the AI-use log |

> Other `docs/architecture/**` and `docs/code-governance/**` artifacts are planned but not written
> yet; when they exist they slot in after #6.

---

## 4. Code baseline

- **Upstream:** `TauricResearch/TradingAgents` (multi-agent LLM trading framework, Apache-2.0).
- **Fork point (baseline commit):** `1394a3f72aa4393e1a98f51b382434c4b4c2d972`
  ("Merge pull request #1478 from TauricResearch/v0.6.0", 2026-10-03).
- **Inherited packages:** `src/tradingagents/` (agents, dataflows, graph, llm_clients, memory) and
  `src/cli/`, moved under `src/` by ADR-002 / CHG-001.
- **Inherited test suite:** 86 files in `test/offline/`; measured on Python 3.12 in a clean venv:
  1262 passed, 1 skipped (optional `langchain_aws`), 1 deselected (`-m "not integration"`), ~12 s.
- **Inherited CI** (test matrix, smoke install, full-repo ruff) was **replaced** by our six blocking
  gates (see §10 and ADR-003 / CHG-002).
- **Never sync upstream into `main`.** It would scramble the recorded baseline. Handle upstream
  updates as their own reviewed change.

---

## 5. Readable / modifiable / frozen

| Class | Paths | Rule |
|---|---|---|
| **Readable** | everything in the repository | reading is always allowed |
| **Modifiable via PR** | `src/**`, `test/**`, `docs/**`, `README.md`, `architecture-blueprint.md` | change on a branch, open a PR, get a review |
| **Versioned-only** | `prompts/` | add a new `prompt_vX.Y.yaml`; **never edit an existing prompt file in place** (`D1-REQ-GOV-012`) |
| **Frozen** | the public entry points and contracts in §8; the inherited tests; the `[tool.ruff]` block in `pyproject.toml`; requirement `id`s; the gate names in branch protection | do not change without an ADR and human approval; never weaken, skip or rename an inherited test; never create a `ruff.toml` |
| **Human-only** | `.opencode/rules.md` (course D3) | the agent must not edit this file; every other path is a protected path (§11) |

New code goes under `src/`; new deterministic tests go under `test/offline/`; API-dependent tests go
under `test/live/`.

---

## 6. Module organization

```
src/
├── tradingagents/
│   ├── agents/       # analysts, researchers, managers, risk_mgmt, trader, schemas, state, rating
│   ├── dataflows/    # provider chain (router, vendors, symbols, date_window, net, files)
│   ├── graph/        # LangGraph wiring (setup, conditional_logic, trading_graph, propagation)
│   ├── llm_clients/  # provider clients and the model catalog
│   └── memory/       # decision log and reflection
└── cli/              # interactive CLI (main:app), config, display, selections
test/
├── offline/          # deterministic, no network / no keys
└── live/             # API-dependent
```

**Rules** (to be expanded in `docs/code-governance/structural-constraints.md`, not yet written):

- each architectural element maps to **exactly one module**;
- new work **extends** the existing baseline, it never replaces it;
- every module and function references the ADR and the invariant it implements;
- keep the **authority boundary**: model output is advisory, deterministic code is authoritative.

---

## 7. Plan before code — human gates (STOP points)

The agent does **not** run unattended to completion. At each stage a human gate applies.

The course expects the code to be **agent-generated** (intro P20: "AI-generated code is explicitly
permitted and expected"); the team's value is in specifying the control and supervising the output,
not in hand-editing generated code.

1. **Plan first.** Before generating any code, produce an execution plan covering traceability,
   the interface contract, scope boundaries, the testing strategy and the steps.
2. **STOP for approval.** Wait for the human to approve the plan before writing implementation code.
3. **Tests before implementation.** Commit the tests first, then the implementation that makes them
   pass (gate 1; the test-independence covenant in `D1-REQ-GOV-013`). Each feature carries at least
   one negative test.
4. **STOP at every surprise.** If the baseline suite is not green, if a file beyond the agreed scope
   would change, or if the plan is wrong, stop and ask.
5. **The agent never merges.** After the PR is open, a human decides: the human author may merge once
   someone else has approved (GitHub forbids self-approval, not self-merge). The agent never approves
   or merges a change.

---

## 8. Integration contracts between modules

These are the stable interfaces. Changing one is a safety-critical change: it needs an ADR and human
approval (§7, §11).

| Contract | Detail |
|---|---|
| Package import | `import tradingagents`, `import cli.main` |
| Console script | `tradingagents = cli.main:app` (`[project.scripts]`) |
| Python API | `TradingAgentsGraph(config=...).propagate(ticker, date) -> (final_state, decision)`; `save_reports(state, ticker, html=...)` |
| Configuration | `DEFAULT_CONFIG` mapping; `TRADINGAGENTS_*` env overrides come from the single source `_ENV_OVERRIDES` in `src/tradingagents/default_config.py` |
| Graph state and wiring | `agents/state.py` (state shape), `graph/setup.py` (nodes/edges), `graph/conditional_logic.py` (routing) |
| Data access | `dataflows/router.py` provider chain; point-in-time rules (SEC EDGAR as filed; Yahoo past dates withheld) |
| Persistence | `~/.tradingagents/memory/trading_memory.md`; `~/.tradingagents/cache/checkpoints/<TICKER>.db`; override base via `TRADINGAGENTS_DATA_DIR` / `TRADINGAGENTS_CACHE_DIR` |
| Authority boundary | position ceiling and schema validation are deterministic and **authoritative**; model output is **advisory** (`D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`) |

Planned additions (the telemetry "event seam", the context assembler) must be **additive** and must
not break the contracts above.

---

## 9. Verification requirements

Generated code must satisfy all of the following before it is offered for review.

- **Lint.** `ruff` uses the config already in `pyproject.toml` (`line-length = 100`,
  `target-version = "py311"`, `select = ["E","W","F","I","B","UP","C4","SIM"]`, `ignore = ["E501"]`).
  Never create a `ruff.toml`; never edit `[tool.ruff]`. Changed `src/**/*.py` must be clean.
- **Regression.** `pytest -q` (the full offline suite) must stay green with **zero regressions**;
  the inherited suite is the baseline. Integration tests run with `pytest -m integration`.
- **Schema.** `check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml`
  must pass whenever requirements change.
- **Traceability.** Every `fit_criterion` has at least one test; every invariant has a test that
  fails when violated **and** a concrete fallback action; every test names the requirement or
  invariant it covers.
- **AI-use log.** The gate enforces the course floor: a PR that changes code or prompts (`src/`,
  `test/`, `prompts/`) without updating `docs/ai-use-log.yaml` is blocked. By team policy the log is
  updated whenever the AI materially contributed to a change, including governance documents.
- **Three-tier verification:** structural (imports, module boundaries, permissions, architectural
  functions) / regression / behavioral (quality thresholds, zero safety escapes).
- **Secrets.** No API key or secret may enter any commit.

---

## 10. Blocking gates and branch protection

`.github/workflows/ci.yml` is `name: gates` and defines six jobs. The gate name must match the
branch-protection `contexts` **character for character**.

| Gate | Checks | State |
|---|---|---|
| `gate-1-test-approval` | the change is covered by tests committed before the implementation, pointed at by `Test-Approval:` | planned |
| `gate-2-static-analysis` | `ruff` on the `src/**/*.py` files this PR touches (plus `mypy src`, soft) | planned |
| `gate-3-schema` | `requirements.yaml` validates against `req-schema.json` | **online** |
| `gate-4-semantic-eval` | prompt/model changes run the semantic evaluation | planned |
| `gate-5-regression` | full inherited + new suite, `pytest -q` | **online** |
| `gate-6-ai-use-log` | a PR that changes code or prompts (`src/`, `test/`, `prompts/`) must update the AI-use log | **online** |

**Branch protection on `main`:** at least 1 approving review, `dismiss_stale_reviews: true`,
`enforce_admins: true`, no force pushes, no deletions. **Nobody pushes to `main` directly,
including the admin.** The committed baseline is `docs/code-governance/protection.json`.

---

## 11. Human-only and protected paths

The course marks exactly **one** repository file as human-only (D3):

- `.opencode/rules.md` — "the project-level always-on behavioral rules for the coding agent.
  **Human-only file.**" The agent must not write it.

Every other path is governed by two rules, not by a human-only label:

- **Protected paths** — change them only through a reviewed pull request, like any other path:
  `AGENTS.md`, `Prompt.md`, `.opencode/**`, `.agent/**`, `.github/**`, `docs/**`.
- **Safety-critical paths** — a change needs a human review **and** an accompanying architecture
  decision record (D7: "changes to safety-critical paths must require human review with an
  accompanying architecture decision"; the `.agent/rules.md` covenant says the same). This covers the
  module contracts in §8, the permission model, and the safety guardrails.

The agent is expected to write code (§2, §7). What these rules protect is traceability: every change
cites the requirement it serves, the test that covers it, and the review that approved it.

---

## 12. Change registration and records

**Workflow:** requirement first → tests before implementation → branch → PR → review → merge.

- **Branch prefixes.** `feat/`, `fix/`, `refactor/`, `test/` (code), `req/CHG-xxx` (requirements),
  `arch/` (architecture artifacts), `docs/` (documentation), `gov/CHG-xxx` (governance files),
  `ci/CHG-xxx` (gates). The branch name carries the change id; a branch lives at most 3 days and 5
  commits before it is split or rebuilt.
- **Commit trailers** (one per line, after a blank line):
  `Refs:` (deliverables / requirement ids), `Agent-Session:` (transcript file + line range),
  `AI-Use-Log:` (`docs/ai-use-log.yaml`), `Test-Approval:` (`docs/review-memo.md#<change id>`).
- **Records.** Every PR gets one `docs/review-memo.md` entry; the author appends one
  `docs/ai-use-log.yaml` entry whenever the AI materially contributed to the change (any path,
  governance included); annotated session transcripts live in `transcripts/` (append-only).
- **Merge.** `gh pr merge <n> --squash --delete-branch`, then `git switch main && git pull --ff-only`
  and delete the local branch. Only after an approving review.

---

## 13. Permission model (default deny)

The machine-readable source is `.opencode/permissions.jsonc`; the prose is
`docs/architecture/permission-model.md`; this section is the summary. **All three list the same
whitelist and must agree.** Precedence: **deny > ask > allow**; an unknown path or command is denied.

| Mode | Paths |
|---|---|
| **Read — allow** | `AGENTS.md`, `Prompt.md`, `README.md`, `architecture-blueprint.md`, `Report.md`, `CHANGELOG.md`, `docs/**`, `src/**`, `test/**`, `prompts/**`, `eval/**`, `transcripts/**`, `.github/**`, `.agent/**`, `.opencode/rules.md`, `.opencode/tasks/**`, `pyproject.toml`, `requirements.txt`, `mypy.ini`, `Dockerfile`, `docker-compose.yml` |
| **Read — deny** | `.env`, `.env.*`, `*.key`, `*.pem`, `*.p12`, `~/.ssh/**`, `~/.aws/**`, `~/.config/gh/**` |
| **Write — allow** | `src/**`, `test/**`, `docs/**`, `transcripts/**` (append-only), `prompts/**` (new versioned files only), `README.md`, `architecture-blueprint.md` |
| **Write — ask** | `AGENTS.md`, `Prompt.md`, `.github/**`, `.agent/**`, `.opencode/**`, `pyproject.toml`, `requirements.txt`, `docs/req/req-schema.json`, `docs/code-governance/**`, `docs/architecture/permission-model.md` |
| **Write — deny** | `.opencode/rules.md`, `.opencode/tasks/**`, `.opencode/git-gh-rules/**`, `.env*`, `*.key`, `*.pem`, `.git/**`, `.venv/**` |

Commands follow the same three tiers: read-only commands and work on your own branch are allowed;
history changes, `gh pr review` / `gh pr comment`, tags and `--force` require asking; pushes to
`main` or `upstream`, `gh pr merge`, `gh api` writes, `reset --hard`, `clean -fdx`, `filter-repo` and
`-X ours|theirs` are denied.
