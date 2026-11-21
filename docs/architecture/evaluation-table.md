# Candidate evaluation table (D2.8)

**Status:** accepted 2026-11-20. **Owner:** `@JHB11Hinson`, reviewed by the team.
**Requirement:** `D1-REQ-GOV-009` (D2.8). **Related:** ADR-001, ADR-003, ADR-004, ADR-005, ADR-007.

This is the comparison that justifies the architecture as chosen, one decision at a time. The scores
are **judgement on a 1–5 scale** (5 best) against the criteria below; they are not measurements. The
one decision with measured evidence is the evaluation harness, and its number is quoted.

## 1. Criteria and weights

| # | Criterion | What a 5 means |
|---|---|---|
| C1 | Fit to the inherited baseline | extends the baseline, inherited tests stay green |
| C2 | Cost and latency | reduces the token spend or wall-clock the course names as the pain |
| C3 | Quality evidence | the effect is measurable with the evaluation harness |
| C4 | Risk | failure is contained; the authority boundary is not weakened |
| C5 | Reversibility and effort | one module, revertable, no migration |

C2 and C3 carry the weight: the project exists because a single analysis is slow and token-burning,
and the course grades evidence, not opinion.

## 2. Decisions

### A. Orchestration — extend LangGraph

| Candidate | C1 | C2 | C3 | C4 | C5 | Total | Decision |
|---|---|---|---|---|---|---|---|
| Extend the inherited LangGraph graph (ADR-001) | 5 | 4 | 4 | 5 | 5 | **23** | **chosen** |
| Rewrite on an event bus / actors | 1 | 2 | 2 | 2 | 1 | 8 | rejected (`AGENTS.md` §2 non-goal) |
| Async queue with a worker per agent | 1 | 3 | 2 | 2 | 1 | 9 | rejected: same rewrite, more operations |

The inherited graph is the graded baseline; a rewrite would scramble it and put the inherited 1262
tests at risk. Reopen only if the course changes the baseline (it does not) — a non-goal.

### B. Context — layered assembler with a run budget

| Candidate | C1 | C2 | C3 | C4 | C5 | Total | Decision |
|---|---|---|---|---|---|---|---|
| Six-layer assembler + run budget + decision reserve (ADR-004) | 5 | 5 | 5 | 5 | 3 | **23** | **chosen** |
| Let each agent trim its own prompt | 3 | 2 | 1 | 2 | 4 | 12 | rejected: no shared ceiling, duplicated logic |
| Rely on provider truncation | 5 | 1 | 1 | 1 | 5 | 13 | rejected: providers drop the oldest tokens, which can be the constraints |
| Fixed message-count window | 4 | 3 | 2 | 2 | 4 | 15 | rejected: size varies by an order of magnitude |

Measured on the fixed set: 89,858 tokens capped vs 96,820 uncapped (`capped_tokens_ratio 0.928`);
NVDA alone is 49,912 against a 50,000 cap, and 56,874 uncapped. The `total_tokens_ratio` of 0.374 is
measured against the inherited 120,000 estimate; the uncapped replay is already 0.403 of that
baseline, so the headline is **not** a production saving claim (`DEBT-011`, `E-006`).

### C. Debate — structured, diverge-then-converge

| Candidate | C1 | C2 | C3 | C4 | C5 | Total | Decision |
|---|---|---|---|---|---|---|---|
| Structured turns + Osborn diverge/converge (`DEBATE-001/002`) | 4 | 3 | 4 | 5 | 3 | **19** | **chosen, partial** |
| Keep the free-form debate | 5 | 4 | 1 | 3 | 5 | 18 | rejected: the course names it as the second pain point |
| Free LLM-judge scoring of the debate | 3 | 2 | 2 | 2 | 3 | 12 | rejected: another model call and non-determinism where the budget is tight |

Round bound `DEBATE-004` is shipped; the structured turn contract is registered and its evidence is
still planned (`verification-constraints.md` §4). The table must not be read as "implemented".

### D. Memory — the existing episodic log

| Candidate | C1 | C2 | C3 | C4 | C5 | Total | Decision |
|---|---|---|---|---|---|---|---|
| Keep the append-only decision log + reflection (MEM-003/004) | 5 | 4 | 3 | 5 | 5 | **22** | **chosen** |
| Three-layer store with embeddings (MEM-001/002) | 3 | 1 | 2 | 3 | 2 | 11 | deferred (`wont`, registry reason) |
| External vector database | 1 | 1 | 2 | 2 | 1 | 7 | rejected: a service for a demo-scale log |

The log is markdown evidence; adding a second store would duplicate it and add a dependency the
graded behaviour does not need. Reopen if a cross-ticker lesson proves to change decisions.

### E. Observability — in-process seam + trace/manifest

| Candidate | C1 | C2 | C3 | C4 | C5 | Total | Decision |
|---|---|---|---|---|---|---|---|
| In-process event seam, trace and manifest (ADR-005) | 5 | 4 | 5 | 5 | 4 | **23** | **chosen** |
| Structured logs only | 5 | 5 | 2 | 5 | 5 | 22 | rejected: no per-phase tokens or cost |
| OTel/Langfuse exporter | 3 | 3 | 4 | 3 | 2 | 15 | rejected: a network dependency and a second service |

### F. Evaluation — deterministic replay

| Candidate | C1 | C2 | C3 | C4 | C5 | Total | Decision |
|---|---|---|---|---|---|---|---|
| Fixed set + thresholds + offline replay (ADR-007) | 5 | 5 | 5 | 5 | 4 | **24** | **chosen and measured** |
| Live provider replay | 4 | 1 | 5 | 3 | 4 | 17 | rejected for CI: a key, a cost per pull request, model drift |
| Replay recorded metrics | 5 | 5 | 1 | 2 | 4 | 17 | rejected: never fails when the code regresses |

Measured: two cases, `total_tokens_ratio 0.374`, `capped_tokens_ratio 0.928`, `review_rate 0`,
exit 0; the deliberate-violation probe (PR #44) failed the gate as designed. The same-condition
ratio is the mechanism check; the baseline ratio alone does not prove the cap caused the saving.

### G. Safety — deterministic guardrails

| Candidate | C1 | C2 | C3 | C4 | C5 | Total | Decision |
|---|---|---|---|---|---|---|---|
| Deterministic schemas, `REVIEW` sentinel, position ceiling (ADR-003) | 5 | 4 | 4 | 5 | 4 | **22** | **chosen, partial** |
| Prompt-only safety instructions | 5 | 4 | 1 | 1 | 5 | 16 | rejected: a model instruction is advisory |
| A third-party guardrails framework | 3 | 2 | 3 | 3 | 2 | 13 | rejected: a dependency for two checks |

Schema validation and the `REVIEW` sentinel are shipped; the position ceiling (`SAFE-003`) and
injection scrubbing (`SAFE-001`) are **not**, and `DEBT-002` records that. The table scores the
design, not the implementation status.

## 3. How to use this table

- A row is a **candidate**, not a commitment: the rejected candidates and their reopen conditions are
  in `docs/architecture/option-ledger.md`.
- A change that reverses a chosen row needs an ADR that cites the criteria here and updates this
  table in the same pull request.
- A score moves only with evidence (a measured run, a course requirement, or a named frontier
  practice); otherwise it is an opinion and belongs in the review discussion, not the table.
