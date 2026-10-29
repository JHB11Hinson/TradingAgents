# ADR-003: Authority boundary and the default-deny permission model

- Status: accepted
- Date: 2026-10-30
- Deciders: the four team members
- Related: ADR-001, ADR-002, `AGENTS.md` §8/§13, `D1-REQ-GOV-006`, `D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`

## Context

The course requires a **file-level permission model** for the coding agent: "default is no read, no
write; every path is explicitly whitelisted" (D2.6), in **machine-readable form with guard rules and
enforcement mechanisms** (D3). The inherited system also lets model output flow toward a tradeable
decision, so the **authority boundary** between advisory model output and authoritative deterministic
code has to be explicit.

Without a default-deny model, the agent can widen its own reach: a path is writable because nobody
said otherwise. That is exactly the failure mode the course's "human supervision" evidence is meant
to prevent. This is a safety-critical change, so it carries this ADR.

## Decision

1. Adopt a **default-deny, per-path whitelist** with three modes — `allow`, `ask`, `deny` — and the
   precedence **deny > ask > allow**. An unknown path or command is denied.
2. Use **one whitelist and three role modes**: `plan` (read-only), `build` (read + write + commands),
   `review` (read + `/tmp` drafts). The role comes from the task, not from the `gh` account.
3. Keep both layers explicit: **coding-agent permissions** (files and commands) and the **product
   authority boundary** (model output advisory, deterministic code authoritative).
4. Record the same whitelist in **three places that must agree**: `.opencode/permissions.jsonc`,
   `docs/architecture/permission-model.md`, and `AGENTS.md` §13.
5. Enforce it with four layers: OpenCode permission settings derived from the JSONC, the CI gates,
   branch protection, and human review.

## Alternatives considered

- **Allow everything, rely on review.** Rejected: the course asks for explicit whitelists, and a
  reviewer cannot see every path an agent touched.
- **Deny everything except `src/` and `test/`.** Rejected: the agent must read requirements, ADRs and
  gates, and must write records; an over-tight whitelist would be bypassed in practice.
- **A prose document only.** Rejected: D3 requires a machine-readable model.
- **Duplicate the whitelist per role.** Rejected: three lists drift immediately; one list interpreted
  by role modes keeps a single source.
- **Enforce only in CI.** Rejected: CI sees a pushed branch, not an unsafe local action; runtime
  settings close that gap.

## Consequences

- A new path must be added in three files; the consistency check fails otherwise.
- The agent stops more often at the `ask` tier. That is intended: the `ask` tier is where human
  oversight becomes auditable.
- `.opencode/rules.md` stays human-only and is denied to every role, including `build`.
- The model gains no path that bypasses the deterministic ceiling or schema validation.

## Reconsider if

- OpenCode ships a native permission format that can consume `.opencode/permissions.jsonc` directly.
- The team adopts a policy engine that enforces the whitelist at runtime (then the JSONC becomes its
  input, not documentation).
- The course changes the required permission artifact or its format.
