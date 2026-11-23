# ADR-016: Enforce a one-way ratchet on the gate-2 mypy quarantine list

- **Status:** proposed (PR #60, 2026-11-23) — awaiting the non-author review of the pull request,
  which is what turns it into `accepted`. The coding agent applied the edit; the agent did not
  approve or merge.
- **Requirement:** `D1-REQ-GOV-003` (the blocking gates) and `D1-REQ-GOV-007` (guard against
  guardrail decay); traceability duty `D1-REQ-GOV-008`.
- **Related:** `AGENTS.md` §10 (`gate-2-static-analysis`), §11 (safety-critical paths need an ADR
  plus human review), `docs/code-governance/mypy-legacy.txt`, `DEBT-009`, ADR-001 (inherited
  baseline), CHG-021 (which promoted gate-2 to blocking and introduced the quarantine list).

## Context

Gate 2 type-checks only the changed `src/**/*.py` files, skipping any file still listed in
`docs/code-governance/mypy-legacy.txt`. That list exists because mypy 2.4.1 reports 156 errors across
26 inherited modules; blocking on the whole tree would red every pull request. The exemption is
recorded as `DEBT-009` and is meant to **shrink**, one module at a time, as modules are cleaned.

The design intent was a **one-way ratchet**: new code is always type-checked, and the quarantine list
only ever gets shorter. Nothing, however, enforced that intent. A pull request could quietly **add**
a line to `mypy-legacy.txt` and thereby silence the type check on a file the author could not make
clean — turning the visible debt into a growing blind spot. The comment in the file ("Remove a line
once that module is type-clean") is a convention, not a gate.

Because `mypy-legacy.txt` lives under `docs/` and `ci.yml` under `.github/`, both are protected
paths, and a change to how a blocking gate decides what to type-check is safety-critical under
`AGENTS.md` §11. It therefore needs this record and a human review, not a silent edit.

## Decision

- Add `.github/scripts/gate2_check.py`, a CI-glue checker (like `gate1_check.py`) that compares
  `docs/code-governance/mypy-legacy.txt` between the base branch and the head commit.
- Compare only the **quarantined path set**, ignoring blank lines and `#` comments. The checker
  **fails** when a path appears in the head file but not in the base (an added quarantine line =
  new hidden debt); it **passes** when paths are only removed or unchanged.
- A missing base file passes (first adoption), so introducing the guard on a branch that predates the
  list does not red itself.
- Wire the checker into `gate-2-static-analysis` as one extra step. The job name and the required
  status-check contexts are unchanged, so branch protection and the gate-6 contract keep matching.

## Consequences

- The ratchet is now enforced: a pull request can shrink the list (cleaning a module and lowering the
  `DEBT-009` count) but cannot add to it. A file that fails mypy must be fixed or left out of the
  change; it cannot be de-listed into the quarantine.
- `DEBT-009` stays open and honest — its remaining count can only go down.
- The checker is offline and deterministic: it reads two git blobs and compares sets, so its tests
  run with no network and no keys.
- This does not attempt to type-check the quarantined files themselves (that is the per-module
  cleanup work tracked by `DEBT-009`); it only guards the boundary of the exemption.
