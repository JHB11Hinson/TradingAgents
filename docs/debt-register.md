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

## DEBT-002 — Safety guardrails are now implemented but pattern-bounded

- **Category:** 7. Guardrail debt
- **What:** `D1-REQ-SAFE-001` (external/retrieved text scrubbing), `D1-REQ-SAFE-002` (strict
  free-text decision) and `D1-REQ-SAFE-003` (deterministic position ceiling) are implemented in
  `src/tradingagents/guardrails/` (ADR-010). The scrubber is a fixed pattern corpus, so a paraphrase
  outside the corpus is not blocked.
- **Impact:** the authority boundary is enforced, but the corpus is the maintenance surface: a new
  injection style needs a new pattern and a corpus sample, not a new subsystem.
- **Owner:** Member 3 (safety).
- **Trigger to revisit:** a hostile sample that the corpus misses; before describing the guard as
  "complete protection".
- **Linked requirement:** `D1-REQ-SAFE-001`, `D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`.
- **Status:** mitigated by CHG-042 (2026-11-21); the pattern-corpus limit is recorded in `INV-04`.

## DEBT-003 — No evaluation set, thresholds or runner

- **Category:** 6. Evaluation debt
- **What:** `eval/` is empty. There is no fixed set, no `thresholds.yaml`, no `python -m eval.run`.
- **Impact:** claim quality cannot be measured, and gate-4 cannot come online; every "the change is
  better" statement is opinion.
- **Owner:** Member 3.
- **Trigger to revisit:** before gate-4 is scheduled; before any COST/PERF/QUAL claim in the report.
- **Linked requirement:** `D1-REQ-EVAL-001`, `D1-REQ-EVAL-002`, `D1-REQ-COST-001`, `D1-REQ-PERF-001`.
- **Status:** mitigated by CHG-036 (2026-11-20): the fixed set, thresholds, recorded baseline and
  `python -m eval.run` exist, and `COST-001` is measured on them (ADR-007); `gate-4-semantic-eval`
  runs the command on every pull request (CHG-037). The follow-ups are `DEBT-011`.

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

## DEBT-009 — Twenty-six inherited modules are quarantined from gate-2's type check

- **Category:** 7. Guardrail debt
- **What:** `mypy 2.4.1` reports **156 errors across 26 inherited modules** (mostly
  `llm_clients/` and `dataflows/`). Blocking on the whole `src/` tree would red every pull
  request, so `gate-2-static-analysis` skips a changed file only while it is listed in
  `docs/code-governance/mypy-legacy.txt`; new files and unlisted files are type-checked.
- **Impact:** a type regression inside a quarantined module is not caught by CI. The list is
  visible and shrinkable, but it is an exemption until each module is cleaned.
- **Owner:** the module owner who next changes a quarantined file.
- **Trigger to revisit:** any change to a quarantined module; clean and de-list at least one
  module per sprint; report the remaining count before the freeze review.
- **Linked requirement:** `D1-REQ-GOV-003`, `D1-REQ-GOV-007`.
- **Status:** open

## DEBT-010 — Gate 2 still lacks the safety-path and dependency-declaration halves

- **Category:** 7. Guardrail debt
- **What:** gate 2 now runs lint, type-checking and `pip check` (installed-metadata
  consistency). The course's gate-2 second half — contract, security, API-surface and permission
  checks on pull requests touching safety-relevant paths — and a dependency-**declaration** check
  are not implemented.
- **Impact:** a change to a safety-critical path (for example `agents/schemas.py`,
  `default_config.py`, `dataflows/router.py` or the permission files) still relies on human review
  alone for those checks.
- **Owner:** Member 3 (safety) with the administrator.
- **Trigger to revisit:** before the first change to a safety-critical path and before Sprint 3
  safety work; do not describe gate 2 as fully implementing the course gate until then.
- **Linked requirement:** `D1-REQ-GOV-003`, `D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`.
- **Status:** open

## DEBT-011 — The evaluation baseline was not like-for-like

- **Category:** 6. Evaluation debt
- **What:** `COST-001` compared a synthetic replay with a recorded 120,000-token production estimate.
  The same replay with the cap lifted is 96,820 tokens, already 0.403 of that baseline, so the 0.374
  headline did not isolate the budget's effect. The fixed set is still two synthetic cases and
  there is still no live mode; both are deliberate, not hidden.
- **Impact:** the capped/uncapped mechanism is now measured (`capped_tokens_ratio 0.928`, threshold
  0.98), but the number is not a production cost claim. A real analysis can still differ from the
  two fixtures.
- **Owner:** admin (context/cost), with member 3 for the evaluation set.
- **Trigger to revisit:** before quoting a cost figure in `Report.md`; before raising or lowering
  `context_budget_tokens`; when a key is available for a one-off live release check (not CI);
  **before growing the fixed set** — the aggregate ratio rises toward 1.0 as non-compacting cases
  are added, so revisit the mechanism metric (for example, a binding rate) at that point.
- **Linked requirement:** `D1-REQ-EVAL-001`, `D1-REQ-COST-001`, `D1-REQ-COST-003`, `D1-REQ-QUAL-001`.
- **Status:** mitigated by CHG-039 (2026-11-21): capped 89,858 / uncapped 96,820, ratio 0.928093;
  `eval/thresholds.yaml` fails when the cap stops binding. `E-006` records the numbers and the
  caveat. A live release check remains the trigger, not a CI requirement.

## DEBT-012 — Only the Portfolio Manager degrades when the budget is exhausted

- **Category:** 7. Guardrail debt
- **What:** `ContextBudgetExceeded` is caught by the Portfolio Manager (which returns `REVIEW`), but an
  analyst, researcher, trader or risk debator that hits the run cap mid-flight aborts the run with an
  exception. The honest whole-request ledger makes this reachable for a run whose analysis needs far
  more than the cap.
- **Impact:** a pathological input under a tight budget loses the run instead of producing a partial
  report. The default 50,000 cap plus the 2,500 decision reserve makes it unlikely on the fixed set,
  but it is not impossible.
- **Owner:** admin (context/cost).
- **Trigger to revisit:** the first real run that exhausts the analysis budget, or before
  `context_budget_tokens` is lowered.
- **Linked requirement:** `D1-REQ-COST-003`, `D1-REQ-TERM-001`.
- **Status:** mitigated by CHG-040 (2026-11-21): every entry point (`propagate`, debug,
  `stream_run`, CLI) now ends a budget-exhausted run in `REVIEW` with
  `termination_reason = "budget_exhausted"`; the state log is written, the memory log is skipped for
  that non-decision, and the checkpoint is preserved. `test/offline/test_budget_degradation.py`
  pins each path, the real one-token case and a handler-removal negative test. ADR-008 records the
  decision.
