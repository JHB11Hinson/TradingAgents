# The project covenant

This file binds every change in this repository. `AGENTS.md` says how the coding agent works,
`Prompt.md` is its launch instruction, and this covenant states the five promises the **work** must
keep. If a habit or a convenience conflicts with a clause here, the clause wins.

Enforcement: the blocking gates in `AGENTS.md` §10 cover the mechanical parts; human review covers
the rest. A change that cannot satisfy a clause stops and asks.

## 1. Abstraction limits

Each architectural element maps to exactly one module, and each module exposes the smallest interface
that carries its element. Do not reach across layers, re-export another module's internals, or add an
abstraction with a single caller. New behaviour extends the existing baseline; it never replaces it.

## 2. Dependency constraints

The runtime dependency set is the inherited one in `pyproject.toml`. Adding a third-party runtime
dependency requires an architecture decision and human approval; adding a dev-only dependency
requires a note in the change card. Solve with the standard library or an existing dependency first.
Never vendor a dependency or pin around a problem silently.

## 3. Test independence

Every feature carries at least one negative test — one that fails when the feature is removed or when
its invariant is violated. Each test names the requirement or invariant it covers. A test may not
depend on another test's fixtures or ordering. Never weaken, skip or rename an inherited test to make
a change pass.

## 4. Safety-critical changes need an ADR and human approval

A change to the module contracts in `AGENTS.md` §8, the permission model, or the safety guardrails
(position ceiling, schema validation, injection scrubbing) requires an architecture decision record
and a human review before it merges. This is the course's D7 rule: "changes to safety-critical paths
must require human review with an accompanying architecture decision."

Gate changes (`.github/workflows/**`) are **not** in this list: they follow the gate-change process —
a `ci/` pull request, the administrator, and a second team member's approval.

## 5. Context freshness

When a requirement changes, `AGENTS.md`, this covenant and the affected architecture and governance
artifacts are updated within one sprint. A change that contradicts them is not merged until they are
updated — the documents are the contract, not a description written after the fact.
