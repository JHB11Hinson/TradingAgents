# Verification constraints (D4)

**Status:** accepted 2026-11-17. **Owner:** `@JHB11Hinson` (rules) with `@SY1433` (execution).
**Requirement:** `D1-REQ-GOV-008`; course D4.
**Related:** `docs/architecture/invariants.md`, `docs/architecture/trace-matrix.md`,
`docs/req/requirements.yaml`, `AGENTS.md` §9, `.github/workflows/ci.yml`.

These are the rules the verification agent applies to every change. They are short on purpose: each
one is checkable. The requirement-to-evidence mapping is the trace matrix; this file defines the
rules and the exceptions, not a second registry.

---

## 1. The four rules

### Rule 1 — Every fit criterion has at least one test or a planned-evidence entry

Every `fit_criterion` in `docs/req/requirements.yaml` must point at a test, a command or an explicit
evidence artifact. The authoritative mapping is `docs/architecture/trace-matrix.md`. A **must**
requirement without executable evidence must carry a `status: planned` (or equivalent) entry, an
owner and a target sprint; a must requirement with neither is a release blocker.

A new requirement is registered with its evidence in the same pull request. A requirement whose
evidence is only a review checklist is allowed for governance requirements, but not for a safety
invariant or a behavioral quality threshold.

### Rule 2 — Every invariant has a negative test and a concrete fallback

Every invariant in `docs/architecture/invariants.md` has:

1. at least one test that **fails when the invariant is violated** (not just a happy-path test);
2. a concrete fallback action to take when the invariant is violated (an action, not "fix the bug").

The negative test is part of the change that introduces or touches the invariant. Removing the
detector/check must turn the test red. A planned invariant is marked **planned** or **partial** in
the register; it is never described as enforced.

### Rule 3 — Every test references the requirement or invariant it verifies

A new test names the `D1-REQ-…` id or `INV-…` id in its module docstring or test name. The pattern is:

```python
"""Verifies D1-REQ-TERM-001: a stalled loop terminates within the bound."""
```

**Inherited-test exception.** The inherited suite (84 test modules / 86 Python files at the
baseline) predates the requirement registry and is **frozen** by `AGENTS.md` §5: it must not be
weakened, skipped or renamed without an ADR and human approval. Those tests are mapped to
requirements in `docs/architecture/trace-matrix.md`; the map is the reference. A change that
modifies an inherited test for an unrelated reason does **not** need to add an ID, but a change that
adds or replaces coverage must name the requirement it covers. Adding a docstring to an inherited
test is a change to a frozen test and needs the same review; it is not done as drive-by cleanup.

### Rule 4 — Every round runs all prior suites with zero regressions

Every change runs the full offline suite (`pytest -q`) before review. The inherited 1262-passed
baseline is the floor; new tests add to it. A regression blocks the merge; a test is never weakened,
skipped or deleted to make a change pass. Integration tests run only with `pytest -m integration`
when the environment has keys.

## 2. Three-tier verification

| Tier | What it covers | Evidence today |
|---|---|---|
| **Structural** | imports, module boundaries, permissions, architectural fitness functions | `test/offline/test_layering.py`; the module table in `docs/code-governance/structural-constraints.md`; the three-way permission check |
| **Regression** | all prior suites, zero regressions | `pytest -q` (gate-5); inherited 1262-passed baseline |
| **Behavioral** | quality thresholds, zero safety escapes | `eval/fixed-set.json`, `eval/thresholds.yaml`, `python -m eval.run`; **gate-4** runs it on every pull request (CHG-037) |

The behavioral tier is not optional in the course. CHG-036 brought it online as a local, runnable
check and CHG-037 made it the blocking `gate-4-semantic-eval`; the deliberate-violation probe is
recorded in the CHG-038 AI-use entry and the review memo.

## 3. Test layout and naming

```text
test/
├── offline/    deterministic; no network, no API keys; the default pytest testpath
└── live/       API-dependent; run only with keys and `-m integration`
```

- A deterministic test goes under `test/offline/`; a test that needs a provider or a live vendor goes
  under `test/live/`.
- A test file is named `test_<subject>.py`; a test names the requirement/invariant it covers.
- A feature carries at least one negative test (`.agent/rules.md` §3).
- A test may not depend on another test's fixtures or ordering.

## 4. Must requirements: current evidence and status

This table is a **status snapshot**, not a second registry. The IDs, statements and fit criteria are
in `docs/req/requirements.yaml`; the per-row mapping is `docs/architecture/trace-matrix.md`. Status
is as of 2026-11-17, with the COST/EVAL rows updated by CHG-036 on 2026-11-20.

| Requirement | Evidence today | Status |
|---|---|---|
| `DEBATE-001` structured turns | schema validator on a fixed set | **planned** — no debate schema/eval yet |
| `DEBATE-004` round bound | `graph/conditional_logic.py` bound; `test/offline/test_risk_router_path_map.py` reaches the terminal at the bound | **done** (existing bound + router case) |
| `TERM-001` self-termination | oscillation/stall cases + detector-removal negative test | **partial** — round bounds exist; detectors planned (INV-01) |
| `CTX-001` six layers | assembler unit test | **done** (CHG-033; `test/offline/test_context_assembler.py`) |
| `CTX-003` budget + re-injection | budget and byte-identical re-injection tests | **done** (CHG-033; `test/offline/test_token_budget.py`) |
| `COST-001` ≤50% baseline | `eval.run` fixed-set totals | **done** (CHG-036; `test/offline/test_eval_*.py`, `python -m eval.run` -> 0.374) |
| `COST-003` token budget | `test/offline/test_token_budget.py` | **done** (CHG-033/CHG-036; the ledger counts the whole request, `test/offline/test_context_ledger_reserve.py`) |
| `EVAL-001` fixed set + runner | `python -m eval.run` pass/fail | **done** (CHG-036; `test/offline/test_eval_cli.py`) |
| `QUAL-001` structured pass rate | `structured_output_pass_rate == 1.0` and `review_rate == 0.0` on the fixed set | **done** (CHG-045; `eval/thresholds.yaml`, `test/offline/test_eval_*.py`) |
| `SAFE-001` injection scrubbing | adversarial corpus + detector-removal and seam-removal negative tests | **done** (CHG-042; `test/offline/test_guardrails.py`) |
| `SAFE-002` schema rejection | malformed/ambiguous-decision negative test, including the PM free-text fallback | **done** (CHG-042; the fallback needs one explicit rating) |
| `SAFE-003` position ceiling | over-ceiling clip + bypass-negative test | **done** (CHG-042; `test/offline/test_guardrails.py`) |
| `GOV-001` layout | src/test present, install green, README states the test commands | **partial** — README reset in CHG-031; verify after merge |
| `GOV-002` AGENTS.md sections | review checklist | **partial** — the “six required sections” count is being corrected (P1-08) |
| `GOV-003` six gates | `protection.json` + deliberate-violation records | **done** — six contexts online (CHG-037); red evidence: gate-1 PR #45, gate-2 PR #12/#26, gate-3 PR #4, gate-4 PR #44, gate-5 PR #6, gate-6 PR #5 |
| `GOV-004` trace matrix | 40 rows for 40 requirements | **done** |
| `GOV-005` tool manifest | manifest vs permission model | **done** (review check) |
| `GOV-006` three-source whitelist | three-way comparison | **partial** — read paths/commands still need alignment (P1-07) |
| `GOV-008` verification + invariants | this file + `docs/architecture/invariants.md` | **partial** — both files exist; the negative tests for the planned invariants and a missing-entry check are still to land |
| `GOV-010` QA records | `docs/review-memo/PR-<n>.md`, `debt-register.md`, `bug-diary.md` | **partial** — per-PR records continue |
| `GOV-011` five transcripts | `transcripts/` coverage check | **partial** — 2 files today (P0-05) |
| `GOV-013` rules + covenant | file presence + five clauses | **done** |

A **must** row that is `planned` or `partial` is visible debt, not a completed claim. The owning
change updates this table and the trace matrix together.

## 5. How to run the verification

```bash
# Regression (the default gate-5 command)
pytest -q

# Structural boundary check (part of the offline suite)
pytest -q test/offline/test_layering.py

# Lint and types (gate-2)
ruff check src
mypy --follow-imports=silent <changed-src-files>

# Schema (gate-3)
check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml

# Behavioral (gate-4 runs this on every pull request)
python -m eval.run --set eval/fixed-set.json --thresholds eval/thresholds.yaml
```

## 6. Gate mapping

| Gate | Verification rule it enforces |
|---|---|
| `gate-1-test-approval` | tests exist and were approved before the implementation (Rule 1 + the human gate) |
| `gate-2-static-analysis` | structural hygiene: `pip check`, `ruff`, scoped `mypy` |
| `gate-3-schema` | the registry is valid |
| `gate-4-semantic-eval` | behavioral tier (Rule 1 for quality requirements): the fixed set replays and a failed threshold blocks (CHG-037) |
| `gate-5-regression` | Rule 4 |
| `gate-6-ai-use-log` | the AI-use log is current when code, tests or prompts change |

## 7. Review checklist

- [ ] Every changed requirement has a test or a planned-evidence entry.
- [ ] Every changed invariant has a negative test and a concrete fallback.
- [ ] Every new test names its `D1-REQ-…` or `INV-…` id.
- [ ] `pytest -q` is green; no inherited test was weakened, skipped or renamed.
- [ ] `ruff` and `check-jsonschema` pass.
- [ ] The trace matrix and the debt register agree with the status claimed in this file.
