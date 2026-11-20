# Option ledger (D2.11)

**Status:** accepted 2026-11-20. **Owner:** `@JHB11Hinson`, reviewed by the team.
**Requirement:** `D1-REQ-GOV-009` (D2.11). **This artifact is optional** in the course; it is kept
because a rejected option with no reopen condition is re-litigated every sprint.

Each entry is an architectural option this project considered and did not take. The evaluation scores
behind the decisions are in `docs/architecture/evaluation-table.md`; this file records only **why the
option is parked and what would bring it back**.

## O-01 — Replace LangGraph with an event bus or actors

- **Rejected:** 2026-10-30 (ADR-001). A rewrite of the inherited orchestration.
- **Why:** `AGENTS.md` §2 declares it a non-goal; it would scramble the graded baseline and put the
  inherited suite at risk for no named requirement.
- **Reopen if:** the course changes the baseline, or a requirement cannot be met without it (none is
  registered).

## O-02 — Per-agent prompt trimming instead of a shared assembler

- **Rejected:** 2026-10-30 (ADR-004).
- **Why:** no shared ceiling, and every agent re-implements the truncation; the constraints could be
  the tokens a trimmer drops.
- **Reopen if:** the assembler's layer contract blocks an agent whose prompt genuinely needs a
  different shape — then extend the contract, not bypass it.

## O-03 — Provider truncation as the budget

- **Rejected:** 2026-10-30 (ADR-004).
- **Why:** providers drop the oldest tokens, which can be the standing constraints; the failure is
  silent and invisible to the ledger.
- **Reopen if:** a provider exposes a constraints-preserving truncation contract (none today).

## O-04 — Three-layer memory with embeddings

- **Deferred:** 2026-11-17 (CHG-032). `MEM-001`/`MEM-002` are `wont` in the registry.
- **Why:** an embedding dependency, an index file and offline stubs for no graded behaviour; the
  append-only log already carries the lesson text.
- **Reopen if:** a cross-ticker lesson is shown to change a decision on the fixed set, or the course
  requires semantic retrieval.

## O-05 — A semantic cache for repeated work

- **Deferred:** 2026-11-17 (CHG-032). `COST-002` is `wont`.
- **Why:** a near-identical query can receive a stale answer; the token budget and compaction already
  deliver the cost target.
- **Reopen if:** the fixed set shows repeated identical work that the budget cannot remove, and a
  cache key can be made exact.

## O-06 — Parallel phases for wall-clock

- **Deferred:** 2026-11-17 (CHG-032). `PERF-001` is `wont`.
- **Why:** raises peak token spend and provider rate-limit pressure, working against `COST-001`; the
  analysts are already parallel.
- **Reopen if:** a measured p50 exceeds the target after the cost work lands.

## O-07 — A live-provider evaluation gate

- **Rejected:** 2026-11-20 (ADR-007).
- **Why:** a key in CI, a cost per pull request, and a model update changes the number without
  changing the code.
- **Reopen if:** a key is available with a budget, and the replay is compared against the live run on
  the same fixed set.

## O-08 — Raising the token budget instead of reserving a decision slice

- **Rejected:** 2026-11-20 (ADR-004 amendment).
- **Why:** it changes the requirement's stated 50,000 default and sits exactly on the 0.5 cost
  boundary.
- **Reopen if:** the reserve proves too tight across several cases, and the requirement's default is
  the thing that should change (a requirements change, not a code tweak).

## O-09 — OTel / Langfuse exporter for telemetry

- **Rejected:** 2026-11-20 (ADR-005).
- **Why:** a network dependency and a second service for a demo-scale run; the manifest already
  answers the cost question locally.
- **Reopen if:** a reviewer needs cross-run dashboards, or the course requires an external trace.
