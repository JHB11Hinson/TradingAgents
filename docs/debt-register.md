# Technical debt register

**Deliverable:** D4. **Requirement:** `D1-REQ-GOV-010`.
**Owner:** the whole team (rotating maintenance). **Status values:** `open`, `mitigated`, `accepted`.

The course names eight AI-era debt categories. Every entry below belongs to exactly one of them, and
an entry that does not fit a category is a sign the category list or the entry is wrong — ask before
inventing a ninth.

| # | Category | One line |
|---|---|---|
| 1 | Prompt rot | prompts drift until nobody dares touch them |
| 2 | Hallucinated dependencies | a library or API that does not exist |
| 3 | Untouchable code | nobody understands it, everyone fears it |
| 4 | Hidden dependencies | used but not declared |
| 5 | Agent-induced bloat | lines grow, capability does not |
| 6 | Evaluation debt | no reliable way to tell whether quality dropped |
| 7 | Guardrail debt | a check that should exist does not |
| 8 | Human/cognitive debt | the team does not understand what the code does |

**How to add an entry:** copy the block, give it the next `DEBT-NNN` id, and fill every field. A
`none observed` entry still needs a **watch trigger** — the condition that would make it real.

---

## DEBT-001 — Runtime prompts are embedded and unversioned

- **Category:** 1. Prompt rot
- **What:** the product's prompts still live inside `src/tradingagents/agents/**`; `prompts/` is
  empty, so there is no `prompt_vX.Y.yaml` history and no way to diff a prompt change.
- **Impact:** a prompt edit is an invisible code edit; the semantic-evaluation gate (gate-4) has
  nothing versioned to evaluate.
- **Owner:** Member 1 (prompt versioning).
- **Trigger to revisit:** before the first change to a runtime prompt.
- **Linked requirement:** `D1-REQ-GOV-012` (versioned runtime prompts), `D1-REQ-EVAL-002`.
- **Status:** open

## DEBT-002 — Two safety guardrails are documented but not implemented

- **Category:** 7. Guardrail debt
- **What:** `D1-REQ-SAFE-001` (external/retrieved text scrubbing) and `D1-REQ-SAFE-003` (deterministic
  position ceiling) have no module yet; there is no `src/tradingagents/guardrails/`.
- **Impact:** the authority boundary is enforced only by schema validation and the `REVIEW` sentinel
  (`docs/code-governance/structural-constraints.md` §4). Model output is not yet ceiling-limited.
- **Owner:** Member 3 (safety).
- **Trigger to revisit:** before Sprint 3 safety work; do not describe the boundary as fully
  enforced until both look-tests exist.
- **Linked requirement:** `D1-REQ-SAFE-001`, `D1-REQ-SAFE-003`.
- **Status:** open

## DEBT-003 — No evaluation set, thresholds or runner

- **Category:** 6. Evaluation debt
- **What:** `eval/` is empty. There is no fixed set, no `thresholds.yaml`, no `python -m eval.run`.
- **Impact:** claim quality cannot be measured, and gate-4 cannot come online; every "the change is
  better" statement is opinion.
- **Owner:** Member 3.
- **Trigger to revisit:** before gate-4 is scheduled; before any COST/PERF/QUAL claim in the report.
- **Linked requirement:** `D1-REQ-EVAL-001`, `D1-REQ-EVAL-002`, `D1-REQ-COST-001`, `D1-REQ-PERF-001`.
- **Status:** open

## DEBT-004 — Environment-only dependencies

- **Category:** 4. Hidden dependencies
- **What:** `langchain_aws` is optional (one inherited test skips without it), and a machine behind a
  SOCKS proxy needs `httpx[socks]`. Neither is a runtime requirement, but both change test results.
- **Impact:** `pytest -q` can differ across machines (1 skipped vs 0), which weakens "zero
  regressions" as evidence.
- **Owner:** Admin (environment), all members when reporting results.
- **Trigger to revisit:** a clean install that fails, or a skip count that changes between machines.
- **Linked requirement:** `D1-REQ-GOV-001`, `D1-REQ-GOV-011`.
- **Status:** open

## DEBT-005 — The graph wiring has no team walkthrough

- **Category:** 3. Untouchable code
- **What:** `src/tradingagents/graph/` (`setup.py`, `conditional_logic.py`, `trading_graph.py`) is
  understood mainly through ADR-001/ADR-002; no walkthrough is recorded.
- **Impact:** the first change to the graph risks being made by trial and error, and a single member
  becomes a bottleneck.
- **Owner:** Admin.
- **Trigger to revisit:** before the first change to `graph/setup.py` or `conditional_logic.py`;
  ideally one recorded walkthrough added to `transcripts/`.
- **Linked requirement:** `D1-REQ-TERM-001`, `D1-REQ-DEBATE-004`.
- **Status:** open

## DEBT-006 — Supervision evidence is incomplete

- **Category:** 8. Human/cognitive debt
- **What:** the course requires at least five annotated transcripts covering the six supervised
  stages; `transcripts/` holds one file, and the stages are not all covered.
- **Impact:** the "authentic human authorship" evidence is thin, and reviewers cannot see how
  decisions were made.
- **Owner:** all members (at least one transcript each).
- **Trigger to revisit:** at the end of every sprint; the count is checked weekly (admin manual 8.2).
- **Linked requirement:** `D1-REQ-GOV-011`.
- **Status:** open

## DEBT-007 — Hallucinated dependencies

- **Category:** 2. Hallucinated dependencies
- **What:** none observed.
- **Watch trigger:** an import that is not in `pyproject.toml` / `requirements.txt`, or a vendor call
  outside `src/tradingagents/dataflows/` (the inherited structural test catches the second).
- **Owner:** reviewer of the affected pull request.
- **Linked requirement:** `D1-REQ-GOV-007`.
- **Status:** none observed

## DEBT-008 — Agent-induced bloat

- **Category:** 5. Agent-induced bloat
- **What:** none observed.
- **Watch trigger:** a pull request that adds code without a test, or a change whose diff is much
  larger than its change card explains.
- **Owner:** reviewer of the affected pull request.
- **Linked requirement:** `D1-REQ-GOV-010`.
- **Status:** none observed
