# ADR-018: Complete gate-2 with a safety-path guard and a dependency-declaration check

- **Status:** proposed (CHG-054, 2026-11-23) — awaiting the non-author review of the pull request,
  which is what turns it into `accepted`. The coding agent applied the edit; the agent did not
  approve or merge.
- **Requirement:** `D1-REQ-GOV-003` (the six blocking gates); supports `D1-REQ-SAFE-002`,
  `D1-REQ-SAFE-003`. Resolves `DEBT-010` and overlaps `DEBT-004` (hidden dependencies).
- **Related:** `AGENTS.md` §8 (module contracts), §10 (`gate-2-static-analysis`), §11
  (safety-critical paths need an ADR plus human review); `docs/debt-register.md` `DEBT-010`,
  `DEBT-004`; `test/offline/test_permission_consistency.py` (`D1-REQ-GOV-006`); ADR-016 (the gate-2
  quarantine ratchet).

## Context

`DEBT-010` records that gate 2 implements only **half** of the course's `D1-REQ-GOV-003` gate: it runs
`ruff`, scoped `mypy` and `pip check` (installed-metadata consistency). The course gate's second half
covers **contract, security, API-surface and permission checks on pull requests that touch
safety-relevant paths**, plus a **dependency-declaration** check (an import must match a declared
dependency, not a transitive one). Today a change to a safety-critical path relies on human review
alone for those checks, and a hidden dependency — the `DEBT-004` class, e.g. an undeclared `httpx`
extra or `langchain_aws` — can ship unnoticed.

A naive dependency checker introduces its own contradiction: if the checker is `deptry` (or any
third-party tool) added only to CI, the tool that detects undeclared dependencies would itself be an
undeclared dependency. The check must therefore be **pure standard-library Python**.

Imports also do not match distribution names one-for-one: `import yaml` is `PyYAML`, `import PIL` is
`Pillow`, `import dotenv` is `python-dotenv`, `import dateutil` is `python-dateutil`, and
`import markdown_it` is `markdown-it-py`. A checker that compared module names to requirement names
directly would report false positives. A maintained **module → distribution** map is required.

Both checks are CI glue, so they live under `.github/scripts/` and run as extra steps inside the
existing `gate-2-static-analysis` job. The job name and the six branch-protection contexts stay
frozen (`test/offline/test_gate_contract.py` pins them).

## Decision

- **Safety-path guard** (`.github/scripts/gate2_safety_check.py`).
  - The safety-critical paths come from a reviewable **data file**,
    `docs/code-governance/safety-paths.txt` (blank lines and `#` comments ignored), so the team adds
    a path by editing text, not code.
  - On a pull request, if any changed file matches a safety path, the PR must also add or modify an
    ADR under `docs/architecture/adr/` in the same diff; otherwise the step **fails**. A PR that
    touches no safety path, or one that touches a safety path and carries an ADR, passes.
  - When the permission sources change (`.opencode/permissions.jsonc`,
    `docs/architecture/permission-model.md`, `AGENTS.md` §13), the guard requires them to remain
    mutually consistent by delegating to the `D1-REQ-GOV-006` check.
- **Dependency-declaration checker** (`.github/scripts/gate2_deps_check.py`).
  - Parses every top-level import in `src/**/*.py` with the stdlib `ast` module.
  - Classifies each root module as one of: standard library (`sys.stdlib_module_names`), first-party
    (`tradingagents`, `cli`), mapped third-party, or unknown.
  - A known **module → distribution** map (`yaml`→`PyYAML`, `dotenv`→`python-dotenv`,
    `dateutil`→`python-dateutil`, `markdown_it`→`markdown-it-py`, `PIL`→`Pillow`, `langchain_*`→the
    declared `langchain-*` packages, `langgraph*`→`langgraph`, and so on) resolves the mismatch.
    Pebble distribution names are compared case-insensitively with `-`/`_` folded.
  - An import that is neither stdlib, first-party, nor declared in `pyproject.toml`
    (`[project].dependencies` or an optional extra) **fails** the step with the offending module and
    its best-guess distribution.
  - No third-party dependency is added; the checker uses only the standard library.
- Both steps run only on `pull_request`; both are inside `gate-2-static-analysis` so no context
  changes.

## Consequences

- `DEBT-010` is closed: gate 2 now performs every check the course attributes to it, and a
  safety-path change without an ADR, or an undeclared dependency, reds the gate.
- The safety-path list and the module→distribution map are the two maintenance points, both visible
  and reviewable (one is a text file, the other a literal dict in the checker).
- The dependency checker is conservative: a genuinely transitive-only import (`pydantic` via
  `langchain-core`) is reported unless it is declared. That is the intended `DEBT-004` behaviour —
  hidden transitive reliance becomes visible — and the fix is a one-line `pyproject.toml` addition,
  not a checker change.
- The checker stays offline and deterministic: it reads files and parses imports; no network, no keys.
- This does not type-check the quarantined modules (`DEBT-009`) and does not run the checks on push
  to `main`; both remain as recorded.
