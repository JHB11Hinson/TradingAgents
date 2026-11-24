# TradingAgents — CS5351 Agentic Software Engineering Project: Process Report

<!--
DRAFT v2 — produced for team review. Every factual claim cites repository evidence.
Markers:
  [OWNER TO CONFIRM]  — a human decision or fact only the team can supply.
  [MEMBER TO WRITE]   — a personal reflection only that student may write.
  [NEEDS VERIFICATION]— a claim this review could not re-derive from repository evidence.
Do not remove a marker by guessing. See Report-Review.md for the full audit.
-->

> **STATUS: NOT SUBMISSION-READY.** Three mandatory items are still outstanding and cannot be completed
> by editing this file: the agreed **contribution hours/story points**, the three **student-written
> reflections**, and either **transcripts from two members or an explicit disclosure**. See Appendix B.
> Student names and student numbers are now in the title block. Every other D6 requirement is met or
> honestly marked.

**Team** (relative contribution is reported in §10):

| Student | Student number | GitHub handle |
|---|---|---|
| JIANG Haobin | 60198818 | `@JHB11Hinson` |
| ZHONG Junqiong | 60907770 | `@AKAScarlett` |
| WANG Songyan | 60847491 | `@SY1433` |

> `[OWNER TO CONFIRM]` The names and student numbers above were supplied by the team. The handle-to-person
> mapping was chosen by the team, not derived from the repository.

**Repository:** `JHB11Hinson/TradingAgents` — a graded fork of `TauricResearch/TradingAgents` (Apache-2.0).
**Baseline commit:** `1394a3f` ("Merge pull request #1478 … v0.6.0", 2026-10-03).
**Repository state described:** `origin/main` at `b3e0d93` (PR #65).

---

## Abstract

We extended an inherited, open-source multi-agent LLM trading framework. Our work did not rewrite its orchestration; it specified what the system must do, turned those specifications into executable gates, and made deterministic code — not model prose — hold authority wherever the course requires it.

The report is organised around the process, not the artifact list. Section 1 explains how the project frame was set. Sections 2–4 follow the course's six supervised stages: requirements classification, architecture candidate evaluation, plan approval, build, verification, and architecture revision. Sections 5–7 present the two pain points the course names, the verification method, the process-quality evidence, and the measurements with their limits. Sections 8–9 record the failures and the human–agent division of responsibility. Sections 10–11 are the contribution table and the individual reflections.

**Project size at submission** (each figure re-verified against the repository at `b3e0d93`):

| Measure | Value | Source |
|---|---|---|
| Pull requests merged | 55 (of 65 opened; 10 closed without merge) | `gh pr list --state merged` |
| Deliberate-violation probes, one per gate | 6 (all six target gates turned red) | closed PRs #45, #26, #4, #44, #6, #5 |
| Recorded change ids (`CHG-xxx`) | 50 | `git log` + review memos |
| Registered requirements | 40 (21 must / 12 should / 1 could / 6 wont) | `docs/req/requirements.yaml` |
| Architecture decision records | 18 written; 15 `accepted`, 3 `proposed` | `docs/architecture/adr/` |
| Offline tests | 1,672 passed, 1 skipped, 1 deselected | `pytest -q -m "not integration"` |
| Annotated session transcripts | 27 files, 27 recorded interventions, six stages covered | `transcripts/` |
| Blocking gates | 6 | `.github/workflows/ci.yml` |

> `[OWNER TO CONFIRM]` If you prefer a different opening (e.g. a single paragraph rather than a table), the facts are identical; the table is easy to remove.

---

## 1. Problem, context, and framing decision

### 1.1 The inherited system and the two named weaknesses

The inherited framework wires four analysts into a bull/bear research debate, a research manager, a trader, a risk discussion and a portfolio manager, orchestrated by LangGraph. It works. But the course names two pain points, and both are visible in the inherited behaviour:

1. **A single analysis is slow and token-burning.** The inherited pipeline assembles a large free-form context for each agent turn and re-reads it every round; nothing bounds the prompt.
2. **The sub-agent debate is too free-form.** Bull and bear argue in prose until a round limit stops them. There is no schema for a turn, no explicit divergence/convergence, and no detector for a debate that is looping or stalling.

### 1.2 Alternatives considered for the project frame

| Option | Why considered | Why rejected |
|---|---|---|
| Rewrite the orchestration (event bus, actors, async queue) | Would make cost and control explicit | The brief says extend, not replace; a rewrite would discard the inherited tests and the baseline commit the project is graded against |
| Add features without constraints | Matches "AI generates code fast" energy | The course grades *supervised* engineering, not volume of features |
| **Specify, then constrain, then verify** — the chosen path | Turns the two weaknesses into named requirements with machine-checkable fit criteria, enforced by gates | — |

**Decision.** We adopted the inherited architecture as the baseline (ADR-001), moved the code under `src/` to make the layout match the module contracts (ADR-002), and fixed the authority boundary between advisory model output and authoritative deterministic code (ADR-003). Every later change extends this baseline.

**Why this matters for the course.** The brief asks for an AI-enabled application built *under auditable human supervision*. Choosing to constrain rather than rewrite means every subsequent change is small, reviewable, and traceable to a requirement — which is what makes supervision auditable.

---

## 2. Requirements: from a brief to a registry

*(Course stage: requirements classification.)*

### 2.1 Problem

A statement like "make the analysis cheaper" is not a requirement. It has no metric, no threshold, and no way to verify it. Three members cannot act on it consistently, and a coding agent cannot be held to it.

### 2.2 What we decided

We made the course brief machine-readable. `docs/req/requirements.yaml` holds every requirement as an entry with:

- an `id` (stable, never reused — `D1-REQ-…`);
- a `type` (functional, invariant, quality, performance, cost, governance, security);
- a `statement` in plain language;
- a **machine-checkable `fit_criterion`** — the verification is part of the requirement, not a later addition;
- a `priority` in MoSCoW terms, with the trade-off stated explicitly;
- a `source` — the course text, the inherited behaviour, or a specific analysis.

`docs/req/req-schema.json` validates the registry, and gate-3 runs that validation on every pull request. This means a malformed or incomplete requirement cannot merge.

### 2.3 The classification result

| Priority | Count | How it is treated in the delivery |
|---|---:|---|
| `must` | 21 | delivered and traced to at least one test |
| `should` | 12 | delivered, or explicitly deferred |
| `could` | 1 | delivered if low cost and low risk |
| `wont` | 6 | registered with a `deferred_reason`; not counted as a gap |

| Type | Count |
|---|---:|
| governance | 14 |
| functional | 10 |
| invariant | 5 |
| cost | 4 |
| quality | 4 |
| security | 2 |
| performance | 1 |
| **total** | **40** |

### 2.4 Why some requirements were deferred

The six `wont` decisions are the clearest evidence of judgement, because each names a cost we declined to pay — not an item we forgot:

| Requirement | Deferred because |
|---|---|
| `DEBATE-003` evidence-citation rate | Needs a citation extractor plus a live baseline; no extractor exists, and building one is a project of its own |
| `MEM-001` three-layer memory | Duplicates what `memory/log.py` already does; a second subsystem would need its own tests and offline stubs |
| `MEM-002` semantic recall | Embeddings add a runtime dependency and an index file, and need offline stubs — cost without a demonstrated benefit here |
| `COST-002` semantic cache | A cache can serve a stale answer for a near-identical query. That is a *safety* cost, not just a cost saving |
| `PERF-001` wall-clock | Parallelising the phases raises peak token spend and hits provider rate limits — it trades one pain point for another |
| `EVAL-002` gate-4 on prompt PRs | Would force live model calls on every prompt pull request, making the gate slow, flaky and expensive |

**Lesson.** A `wont` with a written reason is a *decision*; a missing requirement is an omission. The registry records which, and the report can therefore claim completeness honestly.

> `[OWNER TO CONFIRM]` Were the six `wont` calls reached in team discussion, or decided by one member? The registry records the reasons but not who agreed to them. Say which, because the report otherwise implies a team decision the evidence cannot show.

### 2.5 Fit criteria as the design tool

Every `must` has a fit criterion a test can check. Examples:

- `D1-REQ-SAFE-003` (position ceiling): a model claim of 50% is clipped to 10% on both the structured and the free-text path.
- `D1-REQ-SAFE-002` (decision validity): a malformed or ambiguous final answer becomes `REVIEW`, never a tradeable rating.
- `D1-REQ-DEBATE-001` (structured turn): every debate turn is a schema-valid `DebateTurn` with a non-empty claim, evidence, rebuttal, confidence, divergence and convergence.

These criteria *are* the design. Writing them first forced the implementation to expose the right seams (a place to clip, a place to reject, a place to validate), which is why later test-writing was mechanical rather than exploratory.

---

## 3. Architecture: candidate evaluation and ADRs

*(Course stages: architecture candidate generation and evaluation; architecture revision.)*

### 3.1 Problems the architecture had to solve

Beyond the two pain points, three structural problems had to be settled before code:

1. **Where does authority sit?** Model output is advisory; a deterministic check must be able to override it. (ADR-003)
2. **What does the model see on every turn, and how big may it be?** (ADR-004)
3. **How do we observe cost without risking the run?** (ADR-005)

### 3.2 Alternatives and decisions

| ADR | Decision | Alternatives considered | Why chosen |
|---|---|---|---|
| 001 | Adopt the inherited architecture as the baseline | rewrite | keeps the baseline commit gradable; keeps 86 inherited test files as a regression net |
| 002 | Move code under `src/` | leave flat | one module per architectural element, no ambiguity about what is the package |
| 003 | Deterministic guardrails are authoritative; model output is advisory | trust the model's numbers | the course requires zero-tolerance safety; a model cannot be trusted to clip its own output |
| 004 | Layered context assembly with a token budget and compaction | cap only; summarise mid-run | a cap alone truncates; compaction keeps the constraints |
| 005 | Telemetry is advisory — it observes, never decides | telemetry that can fail a run | a cost measurement that can break a trade is worse than no measurement |
| 006 | Only a schema-valid decision may set the final rating | accept any parseable prose | closes a real hole: arbitrary prose could become a trade |
| 011 | Structured debate turns with explicit diverge/converge | keep free-form prose | directly attacks pain point 2; makes the debate testable |
| 014 | Explicit memory source attribution | implicit memory | stops future data leaking into a past run |
| 016 | A one-way ratchet on the `mypy` quarantine | allow it to grow | stops type-check coverage decaying |
| 018 | Gate-2 also needs a safety-path guard and a dependency check | trust reviewers to notice | turns a review convention into an enforced check |

`Full ADR set:` 18 files in `docs/architecture/adr/`. **Fifteen are `accepted`; three (ADR-016, ADR-017, ADR-018) are `proposed`** — awaiting the non-author review that turns them into accepted decisions.

### 3.3 The layered context structure (ADR-004)

This is the direct answer to pain point 1, and it is worth stating concretely because D2 asks for it:

- **Layers** the model receives on each turn: identity, standing constraints, retrieved knowledge, conversation history, resumable state, current task.
- **Assembly pipeline**: deduplicate → prioritise → budget → compact → assemble.
- **Budget**: a 50,000-token cap (`D1-REQ-COST-003`).
- **Compaction threshold**: **80 % of the cap** (`DEFAULT_COMPACTION_THRESHOLD = 0.8` in
  `src/tradingagents/context/assembler.py`, configurable as `context_compaction_threshold`); the five
  stages are named in the code as `("dedupe", "prioritize", "budget", "compact", "assemble")`.
- **Re-injection**: after compaction the standing constraints are re-injected so a compaction cannot drop
  a safety rule.

The effect is measured in §7, and the measurement is deliberately separated from the live before/after comparison.

### 3.4 Architecture revision that actually happened

Architecture revision is a course stage, and we have a real instance. ADR-016 was recorded citing "PR-3" — an unrelated pull request from 2026-10-12. A later change (CHG-055) added an automated validator for ADR status and PR references; it caught the wrong citation, and it was corrected to `PR #60`.

This is useful evidence for two reasons. First, it shows the ADR set is *maintained*, not written once. Second, it shows that an automated check found a human mistake — a theme the course's "what did oversight catch" question rewards.

> `[OWNER TO CONFIRM]` Which ADR most changed a member's thinking? A one-line answer here makes the "architecture revision" stage concrete rather than procedural.

---

## 4. Governance and human–agent collaboration

*(Course stage: plan approval before code.)*

### 4.1 Problem

A coding agent will produce plausible, buildable code very quickly. Left unsupervised, that speed becomes a liability: the agent can silently change contracts, widen a gate to make a red build green, or edit a document it should not touch. The course's supervision requirement is therefore not a formality; it is the actual engineering discipline of the project.

### 4.2 How supervision was structured

`AGENTS.md` is the agent's single entry point. It states the protocol explicitly:

1. **Plan first.** Before writing any implementation code, the agent produces an execution plan covering traceability, the interface contract, scope boundaries, the testing strategy and the steps.
2. **Human approval.** The plan stops for a human to approve before code is generated.
3. **Tests before implementation.** The tests are committed before the implementation, so a test cannot be written to fit whatever the code happened to do.
4. **Stop at every surprise.** If the baseline is not green, if a file outside scope would change, or if the plan is wrong, the agent stops and asks.
5. **The agent never approves or merges.** A human decides after somebody else has approved.

Around this protocol sit:

- a **default-deny permission model** (`.opencode/permissions.jsonc`, `docs/architecture/permission-model.md`), so an unknown path is denied by default;
- a **project covenant** (`.agent/rules.md`) stating abstraction limits, dependency constraints, the "at least one negative test per feature" rule, and the requirement that changing safety-critical code needs an architecture decision and human approval;
- a **human-only file** (`.opencode/rules.md`) that the agent must not write.

### 4.3 The division of responsibility — stated precisely

The honest description is narrower than "humans wrote nothing and the agent wrote everything". What the evidence supports is:

- **The agent executed every recorded change.** The relationship between agent work and human direction is recorded per change in `docs/ai-use-log/<member>.yaml`. We did not find a change in the history that bypassed this protocol.
- **Humans made the decisions the protocol reserves to humans**: approving plans, approving the test-first sequence, and merging. Every one of the 55 merges was performed by a human account.
- **Review was *not* uniformly human, and the report must not imply it was.** See §4.4.

> **Correction to an earlier claim.** An earlier draft said "every change was written by an AI coding agent" and "every merge was a human decision" and let the reader infer human *review*. The evidence refines that. The two statements are true as written, but 36 of 48 review memos record an **automated** review, so the report states the review position separately rather than relying on the inference.

### 4.4 Review capacity: an honest constraint

GitHub does not allow self-approval, and the team had one dominant author. Requiring a human non-author review for every PR would therefore have stalled the project. We addressed this with a **recorded, auditable automated review** rather than by removing the requirement:

- A maintainer commits the review text as `docs/review-memo/PR-<n>-review.md` and applies the `bot-review` label.
- `.github/workflows/bot-review.yml` posts that committed text as an approving review authored by `github-actions[bot]`.
- The **reviewer field says "automated"**, so the record never pretends a human reviewed it.

The numbers, from the review memos and the GitHub API:

| Reviewer | Review memos authored | GitHub reviews submitted |
|---|---:|---:|
| `github-actions[bot]` (automated) | 36 | 25 |
| `@AKAScarlett` | 4 | 15 |
| `@JHB11Hinson` | 2 | 4 |
| `@SY1433` | 0 | 5 |

So the automated review is the *majority* path, not an exception. That is a genuine limitation of a one-author-dominant project, and the report states it as one. It is also why the AI-use log matters: the log is where *human* direction is evidenced, independent of who approved the review.

**Lesson.** An approval mechanism is only as good as its reviewers. Automating the approval keeps the pipeline moving but does not replace human judgement; the useful question is not "was there an approval?" but "where is the evidence that a human constrained the work?" — which is what the AI-use log records (§9).

### 4.4a Role assignment and rotation

The course asks teams to "rotate roles so that students can experience different responsibilities"
(project.pdf p. 4). We assigned fixed **primary** responsibilities instead — repository governance and
gates; structured debate and quality; memory, safety and evaluation (README §10) — while every member
shared review and every path in `CODEOWNERS`. We did not rotate those primaries.

We report this rather than claim rotation happened. The dimension matrix in §10.2 shows the boundaries
were not absolute: for example, `@AKAScarlett` contributed to gate-1 and to gate-2's safety checks, and
`@SY1433` to gate-2's promotion and ADR hygiene, so members did cross into one another's areas on
specific changes. But a structured rotation is not evidenced, and the report does not assert one.

> `[OWNER TO CONFIRM]` Did the team agree fixed primaries deliberately (e.g. to match members' existing
> strengths), or rotate informally? An honest one-line answer here is better than silence.

### 4.5 The AI-use log

`docs/ai-use-log/` holds one file per member. Each entry records an intervention and why it happened, classified as `approve`, `constrain` or `correct`. Across the log: **45 approve, 43 constrain, 12 correct** entries.

The distribution is informative: the largest category after approvals is **constrain** — cases where a human refused something that would have crossed a boundary. That is the supervision the course asks to see.

> `[OWNER TO CONFIRM]` `docs/ai-use-log/SY1433.yaml` currently contains only its header comment and no entries, although `@SY1433` authored five merged PRs and submitted five reviews. Is that file incomplete, or were those changes logged in `JHB11Hinson.yaml`? The report should not describe a per-member log as maintained when one member's file is empty.

---

## 5. Gates: making the rules executable

### 5.1 Problem

A rule written in a document is a suggestion. "Tests before implementation", "the private key never enters a commit", "every requirement validates against its schema" are worth nothing if a hurried pull request can bypass them. The point of a blocking gate is that the rule executes whether or not anyone remembers it.

### 5.2 The six gates

All six are jobs in `.github/workflows/ci.yml` (workflow name `gates`), and their names match the branch-protection contexts character for character.

| Gate | Risk it addresses | How it is enforced |
|---|---|---|
| `gate-1-test-approval` | implementation without a prior, approved test | a `src/` change must carry a `Test-Approval:` reference to a review record whose verdict is `APPROVE` and whose `Tests:` line lists existing paths; test and `src/` changes cannot share a commit (`gate1_check.py`) |
| `gate-2-static-analysis` | lint and type debt decaying invisibly; a safety path changing without an ADR; an undeclared dependency | `pip check`; `ruff` on changed `src` files; scoped `mypy` with a shrink-only quarantine (`gate2_check.py`, ADR-016); a safety-path guard (`gate2_safety_check.py`, ADR-018); a dependency-declaration check (`gate2_deps_check.py`, ADR-018) |
| `gate-3-schema` | a malformed requirement entering the registry | `check-jsonschema` over `requirements.yaml` against `req-schema.json` |
| `gate-4-semantic-eval` | a change silently breaking quality or cost | the fixed evaluation set replays against `eval/thresholds.yaml`; any missed bound exits non-zero |
| `gate-5-regression` | breaking inherited behaviour | the full offline suite (`pytest -q`) |
| `gate-6-ai-use-log` | code or prompt changes with no AI-use record | a PR touching `src/`, `test/` or `prompts/` must also change `docs/ai-use-log/**` |

**Branch protection.** `docs/code-governance/protection.json` is the committed baseline: the six gate names as required contexts, `strict: true`, `enforce_admins: true`, at least one approving review, `dismiss_stale_reviews: true`, no force pushes, no deletions. The live `main` branch reports `protected: true`.

> `[NEEDS VERIFICATION]` The live rule *details* could not be re-read for this draft: the available token lacks admin rights, so the branch-protection API returns 404 (and no repository rulesets exist). A member with admin access should confirm the live settings match `protection.json` and record the check in this section.

### 5.3 Demonstrating that a gate works

A gate that has never failed is not known to work. For **every one of the six gates** we opened a pull
request designed to violate it and required the gate to turn red, then closed the pull request. The
check runs are still visible on the closed pull requests:

| Gate | Probe PR | Result on the probe |
|---|---|---|
| `gate-1-test-approval` | #45 "`[probe]` deliberate violation for gate-1 (must turn red)" | **FAILURE** |
| `gate-2-static-analysis` | #26 "deliberate violation probe for gate-2" (also #12) | **FAILURE** |
| `gate-3-schema` | #4 "deliberate-violation probe … gate-3-schema" | **FAILURE** |
| `gate-4-semantic-eval` | #44 "`[probe]` deliberate violation for gate-4 (must turn red)" | **FAILURE** |
| `gate-5-regression` | #6 "deliberate-violation probe … gate-5-regression" | **FAILURE** |
| `gate-6-ai-use-log` | #5 "deliberate-violation probe … gate-6-ai-use-log" | **FAILURE** |

In each run the *other* gates passed, so the failure is attributable to the targeted gate rather than to
a broken workflow. This is the strongest single piece of evidence that the gates are real.

Two probes also produced a bug entry: BUG-002 records that the first gate-2 probe was **inconclusive**
because the probe was ordered wrongly in the workflow — the lesson stored was that "a gate is not real
until its name has appeared on a pull request".

Further behavioural tests guard the gates themselves: CHG-051 adds tests that fail if the mypy
quarantine list grows, and CHG-054 adds tests that fail if a safety-path change arrives without an ADR
(ADR-018). The evaluation logbook records the gate-4 probe as E-004.

### 5.4 Gate-2 grew in three stages — a process optimisation

This is the clearest example in the project of a process being *optimised in response to evidence*, which is exactly what D6 asks the report to present.

| Stage | Change | Trigger | What it bought |
|---|---|---|---|
| 1 | `ruff` only (ADR-003) | initial gate set | lint discipline, nothing more |
| 2 | scoped `mypy` with a shrink-only quarantine (CHG-021, ADR-016) | type errors were quarantined with no way to stop the list growing | type coverage can only improve |
| 3 | safety-path guard + dependency check (CHG-054, ADR-018) | a safety-critical path could change without an ADR; imports could drift from the declared dependencies | a convention became an enforced check |

Each stage was a *recorded debt being paid* (`DEBT-007`, `DEBT-009`, `DEBT-010` in `docs/debt-register.md`), not a new feature. The gate kept its name and its protection context throughout, so growth did not disturb branch protection.

**Lesson.** Growing a gate in place, under a stable name, is safer than adding new gates: the protection configuration does not churn, and the failure attribution stays clear.

---

## 6. Implementation: the two pain points

This section distinguishes **what is implemented** from **what is intended or partially achieved**, as the task requires.

### 6.1 Pain point 1 — cost and speed

**Implemented:**

- the layered context assembler with a token budget, compaction, and constraint re-injection after compaction (ADR-004);
- telemetry that records token use per request without ever failing the run (ADR-005);
- a fixed evaluation set with thresholds that gate a change (gate-4).

**Measured:** on the fixed set, the capped run is 64,950 tokens against 70,061 uncapped (−7.3%), with `capped_tokens_ratio` 0.927 — a ratio below 1.0 means the cap actually binds. See §7 for why this is a different quantity from the live comparison.

**Partially achieved / not claimed:** wall-clock time was **not** measured. `PERF-001` is deferred as `wont` precisely because parallelising the phases trades speed for peak token spend. The report therefore makes **no speed claim** — only a cost claim, and a narrow one.

### 6.2 Pain point 2 — structured debate

**Implemented:**

- `agents/schemas.py` defines `DebateTurn`: a non-empty claim, an evidence list, a rebuttal, a confidence, an explicit divergence and an explicit convergence.
- `agents/debate.py` (`parse_debate_turn`, `invoke_debate_turn`) adapts prose with an explicit "no convergence stated" marker, and **aborts** on a claimed-JSON answer that fails validation rather than inventing a complete turn.
- **Termination discipline**: oscillation and stall detectors stop a debate that is looping or stagnating, instead of letting it run to the round limit.

**Evidence:** `test/offline/test_debate_turns.py` rejects missing and empty fields, rejects an empty convergence, parses both JSON and prose, and records exactly one turn per node.

**Partially achieved:** the *quality* of the structured debate (whether structured turns produce better decisions) is **not** measured. The evaluation thresholds check that the decision remains schema-valid and that no case degrades to `REVIEW`; they do not compare debate quality against the prosaic baseline. The report says so rather than implying a quality win.

### 6.3 Safety

Three mechanisms, each with an invariant and a negative test:

| Mechanism | Invariant | Negative test (exists) |
|---|---|---|
| Instruction scrubbing of external and retrieved text | `INV-04` (`D1-REQ-SAFE-001`) | `test_removing_the_detector_leaves_the_hostile_text` |
| Schema-valid decision or `REVIEW`; never a tradeable malformed answer | `INV-05` (`D1-REQ-SAFE-002`) | malformed / ambiguous PM answer drives to `REVIEW` |
| Deterministic position ceiling | `INV-06` (`D1-REQ-SAFE-003`) | a 50% claim is clipped to 10% on both paths |

**Partially achieved:** `DEBT-002` records that the scrubbing patterns are pattern-bounded — they catch a fixed corpus at 100%, but not every paraphrase. The invariant states this instead of hiding it.

### 6.4 Technical debt

Twelve debts are registered in `docs/debt-register.md`. Their true status at `b3e0d93`:

| Status | Count | Debts |
|---|---:|---|
| closed / mitigated | 8 | DEBT-001, 002 (mitigated, bounded), 003, 004, 006, 010, 011, 012 |
| "none observed" (a watch item, not a repaid debt) | 2 | DEBT-007, DEBT-008 |
| open | 2 | DEBT-005 (no graph-wiring walkthrough), DEBT-009 (26 inherited modules quarantined from `mypy`) |
| **total** | **12** | |

> The headline "10 closed or mitigated" in an earlier draft counted DEBT-007/008 ("none observed") as closed. They are not paid debts; they are categories where no instance was found. The report should use the table above.

`DEBT-009` stays open and honest: 26 inherited modules remain outside the type check, but the list may only shrink (ADR-016). `DEBT-005` is open because the graph wiring is understood through its ADRs but has no recorded walkthrough — the report lists it as a gap.

---

## 7. Verification and measurements

### 7.1 Three tiers

`AGENTS.md` §9 and `docs/code-governance/verification-constraints.md` define three tiers:

- **structural** — imports, module boundaries, permissions, architectural fitness functions;
- **regression** — every prior test suite passes with zero regressions;
- **behavioural** — quality thresholds (a schema-valid decision, no `REVIEW` under a tight budget) and zero safety escapes.

### 7.2 Traceability

`docs/architecture/trace-matrix.md` maps each of the 40 requirements to a component, a test/evidence and a runtime monitor; a test checks the mapping has no gaps. `docs/architecture/invariants.md` registers eight invariants (`INV-01`…`INV-08`), each with a statement, a source requirement, an enforcing component, a **verification test and a negative test**, and a concrete operational fallback.

**Caveat, stated precisely:** the invariant tests cite the *requirement* ids (`D1-REQ-SAFE-*`, `D1-REQ-OBS-003`, `D1-REQ-DEBATE-001/2`) rather than the `INV-0x` labels. Only `INV-01`–`INV-03` appear by invariant id in the test tree. So the accurate claim is "every invariant maps to a requirement, and every such requirement has a test that fails when the behaviour is violated", not "every `INV-0x` string appears in a test".

### 7.3 The suite

- **119 test files** in `test/offline/`, **1,672 passed, 1 skipped, 1 deselected** (31.4 s).
- The skip is `test/offline/test_bedrock_provider.py:74` because the optional `langchain_aws` package is not installed. It is not a failure.
- **The inherited tests are never modified.** A diff from the baseline `1394a3f` to `b3e0d93` over `test/` shows **121 entries, all additions** — no inherited test file was edited or deleted.

### 7.4 Measurement 1 — live analysis, inherited vs current

The 120,000-token figure in `eval/baseline.json` is an **estimate** copied from an early requirements example, never a measurement. To replace it with evidence we ran the inherited code and the current tree once each, with the same inputs and configuration.

| | Inherited (`1394a3f`) | Current | Change |
|---|---:|---:|---:|
| Provider tokens (input + output) | 206,694 | 160,833 | **−22.2%** |
| Input tokens | 156,321 | 100,643 | −35.6% |
| Output tokens | 50,373 | 60,190 | **+19.5%** |
| LLM calls | 13 | 10 | −3 |
| Rating | Underweight | Underweight | unchanged |

**What this does not show.** One run per side; the model is stochastic; one analyst and one round; the current run started with one memory-log entry. **Output tokens rose.** Cost was not reported because the gateway has no price entry for the model, so `est_cost` is 0. The report therefore makes **no general "cheaper" claim** — only that cost is now measured rather than estimated.

### 7.5 Measurement 2 — the 50,000-token budget on the fixed set

On the fixed evaluation set (which has **two cases**: NVDA-2026-01-09 and BABA-2026-01-09), the uncapped run is 70,061 tokens and the `--budget 40000` run is 64,950 tokens (−7.3%), with zero `REVIEW` decisions and `capped_tokens_ratio` of 0.927.

**Why this is a separate experiment.** Measurement 2 uses *replay fixtures*, not live vendor payloads, and varies *only the budget*. It proves the budget **compacts**; it does not prove what a live analysis costs. Measurement 1 varies the *code* and proves the current configuration's live use is measured; it does not isolate the budget.

A third data point, from `DEBT-011`'s history: an earlier capped/uncapped comparison was **not like-for-like** (89,858 / 96,820), and CHG-039 corrected the method — a recorded evidence defect, not a silent revision.

### 7.6 What cannot be claimed

- Approximate wall-clock speed.
- Dollar cost.
- That the debate is *better*, only that it is structured and testable.
- A production saving from a single pair of live runs.
- That the evaluation set is representative: two fixtures are a method check, not a benchmark.

> `[OWNER TO CONFIRM]` Should the report add an explicit "two cases only" caveat to the abstract, or is it enough to state it here? Recommend the abstract line in §7.5's form.

### 7.7 Process quality: requirement volatility, defect trends, ambiguity resolution

D6 asks the report to provide *evidence about the process itself*, not only about the product. This
section does that from three records the team maintains: the requirements history, the bug diary and
review memos, and the ADR revision histories. Every figure below states its calculation and its limit;
none is extrapolated into a trend the data cannot carry.

#### Requirement volatility

`docs/req/requirements.yaml` has **six commits**. Comparing consecutive versions by requirement id:

| Measure | Value | How it is counted |
|---|---:|---|
| Requirements ever registered | 40 | final parse of the registry |
| Requirements **deleted** | **0** | no id present in an earlier version is absent later |
| Requirements whose **priority changed** | **6** | the six `must`/`should` → `wont` flips in CHG-032, each with a written `deferred_reason` |
| Requirements whose **fit criterion changed** | **2** | `GOV-010` and `GOV-011` in CHG-029, where the AI-use-log path moved |

So **32 of 40 requirements never changed priority after registration**, and the only priority change
was one deliberate decision (CHG-032) that recorded why each requirement was deferred. The internal
requirement set was therefore stable once written.

Two honest qualifications. First, the sample is small: six commits is not a trend. Second, the registry
grew in two large batches (21, then 19 more) rather than incrementally, so the volatility is
*concentrated in a few decisions* rather than spread smoothly — which is a fact about how we worked, not
a defect.

#### Defect trends

Five significant bugs are recorded in `docs/bug-diary.md`. Their classification:

| Classification | Count | Bugs |
|---|---:|---|
| code (accounting, with a safety consequence) | 1 | BUG-005: the run ledger under-counted the request it was capping |
| documentation (reference integrity) | 1 | BUG-001: the blueprint named an ADR that did not exist |
| process (probe ordering) | 1 | BUG-002: the gate-2 violation probe was inconclusive |
| environment | 2 | BUG-003 (proxy disagreement), BUG-004 (Actions stopped on the fork) |

**Three of the five exposed a missing check, and each produced a concrete change**: a reference that is
now validated, a probe-ordering rule, and a budget the code actually enforces. That is the useful
defect narrative — each bug that mattered became a permanent check.

**What we will not claim.** We will not give a defect *rate* or say defects *fell*. The diary is small,
and the review records use two formats: the legacy archive has **11 `CHANGES REQUIRED`** verdicts out of
23 entries, while the later per-PR memos show **zero** out of 48. That zero is an artefact of the
pre-committed review-text workflow, not evidence that later changes were cleaner.

#### Ambiguity resolution

The clearest example is **ADR-006**, which went through **five revisions (r1 → r5)**. Its header
records what each round changed: r3 added four failure identifiers and split the test roles; r4
corrected a repository-state premise, moved a debt id, and made the context quote verbatim. The ADR also
carries an explicit **"Reconsider if"** section with four written reopen conditions — for example, if the
evaluation set showed that turning free-text decisions into `REVIEW` lost material quality, then a
stricter structured re-ask would deserve its own ADR.

Ambiguity was usually resolved by **escalating it rather than guessing**. Two early review memos are
marked `PENDING TEAM RULING`; a session transcript records a human rejecting the agent's over-broad
claim that several files were "human-only", after checking the course PDF, because only one file is. The
AI-use log mirrors this at scale: **43 `constrain`** and **12 `correct`** entries against 45 `approve`.
Human time went mostly into *preventing* wrong directions and *correcting* wrong findings.

**What we cannot count:** there is no field recording which requirements were perceived as *ambiguous*, so
no rate is reported.

### 7.8 Keeping artifacts co-evolving

When one artifact changes, the others must follow. These are three cases where that happened and is
recorded:

| Trigger | What had to change together | Evidence |
|---|---|---|
| A log file exceeded GitHub's 1 MB render limit | the AI-use log was split per member, gate-6's path was taught the new layout, and the `GOV-010`/`GOV-011` fit criteria were rewritten to match | CHG-029 diff on `requirements.yaml` |
| Cost/benefit at the end of the build | six requirements gained `wont` status *and* a `deferred_reason`; the trace matrix and this report follow them | CHG-032 |
| ADR-016 cited the wrong pull request | the citation was corrected **and** a validator was added so the class of error is detectable | CHG-055; ADR-016 header |

**And the counter-example, which belongs here too.** Three documentation values were *not* kept
co-evolving: the test baseline in `AGENTS.md`, the `TERM-001` row in `verification-constraints.md`, and
the gate-1 state in `README.md` (§8.1). Keeping artifacts co-evolving worked when a gate or a check
compelled it; it failed where only prose was involved. That is the honest summary.

---

## 8. Failures, corrections, and lessons learned

We keep these because the course grades *supervised* engineering, and supervision is visible mainly in what changed after a human noticed something.

| Failure | How it was caught | What changed | Process improvement |
|---|---|---|---|
| An ADR cited "PR-3", an unrelated pull request | an automated ADR/PR-reference validator added in CHG-055 | citation corrected to PR #60 | a new validator makes the class of error detectable, not just the instance fixable |
| ADR-006's retry budget was miscounted in its first revision | owner review before implementation | revised (see the ADR's revision history) | the plan-approval gate caught a design error before code |
| The capped/uncapped evaluation was not like-for-like | DEBT-011 audit | CHG-039 corrected the method | behavioural evidence is now compared on the same footing |
| `AGENTS.md` quoted a stale test baseline (1,262) | documentation audit | **still open at `b3e0d93`** | see below |
| `verification-constraints.md` marked termination "partial" after the detectors shipped | documentation audit | **still open at `b3e0d93`** | see below |
| `README.md` still calls gate-1 "promotion pending" although it is online | documentation audit | **still open at `b3e0d93`** | see below |

### 8.1 Unresolved issues at submission

Three documentation inconsistencies remain, all in write-ask paths that were not corrected during this review:

1. `AGENTS.md` §4 quotes "86 files / 1262 passed" — the measured baseline is **119 files / 1,672 passed**.
2. `docs/code-governance/verification-constraints.md` still marks `TERM-001` **partial** although the termination detectors exist and are tested.
3. `README.md` §7 marks gate-1 "promotion to `main` pending" although it is an online job.
4. **ADR-006 cites a debt id, `DEBT-013`, that does not exist** in the twelve-entry `debt-register.md`,
   where the highest id is `DEBT-012`.

We report these rather than claim the repository is fully consistent. `docs/ai-use-log/SY1433.yaml` is also empty (see §4.5). A `[OWNER TO CONFIRM]` decision is needed: correct them in a follow-up change, or state in the final report that they are open.

> `[OWNER TO CONFIRM]` Which of the three to correct before submission? Leaving them is defensible (the report is honest about open items); correcting them would remove a section but is a governance change that needs its own review.

### 8.2 The most important lesson

The failures that reached `main` were **documentation drift**, not code drift. The gates caught code-level defects; nothing caught a stale number in `AGENTS.md` or a mislabelled status row, because no gate reads prose. If we repeated the project we would add one cheap check: a test that greps the documents for the values the code can compute (test count, gate names, ADR count) and fails when they disagree. That is the honest generalisation from our specific failures.

---

## 9. Human oversight: what it caught that the agent did not

*(Course D6 theme: "what human oversight caught that the agent did not".)*

Three concrete examples, all evidenced:

1. **The contract-shape rejection (ADR-006).** The agent's first design would have changed a node's return shape to expose a retry counter. Human review rejected it: the return shape is a frozen contract, and a convenience field is not a reason to break it. The counters were observed through the existing mock entry points instead. *(This is the clearest case of a human protecting an interface against a small optimisation.)*
2. **The environment-bug correction.** An agent-reported diagnosis claimed an environment bug affected every checkout. Re-testing in the owner's own tree showed it affected only one stale installed package. The false diagnosis was corrected in the README change and the AI-use log, rather than propagated.
3. **The unsupported-code mistake.** The agent described code it had only read summarily. Review caught the mismatch between the description and the actual source. The lesson recorded: read the file, then describe it.

> `[OWNER TO CONFIRM]` These three come from the AI-use log (`correct` and `constrain` entries). Please confirm the wording of example 1 matches what actually happened, since it is the strongest example and the most likely to be questioned.

Across the log there are **12 `correct`** and **43 `constrain`** interventions: the ratio suggests that most human time went into *preventing* wrong directions rather than *repairing* them. That is the process-quality point the course is looking for.

---

## 10. Team contributions

### 10.1 How we measured contribution

The course suggests a measure such as **productive hours or story points**, and states that marks
are pro-rated by relative contribution using `member total ÷ team mean`. It also fixes the scale: "The
average contribution is **1.0**", so the three weights must average to 1.0. We follow that method rather
than counting pull requests, for a reason: in this project the agent executed the code, so the number of
pull requests a member opened reflects *who was directing the agent on which days*, not the size of the
contribution. Counting PRs would overstate the most active co-ordinator and understate the reviewers and
designers. The course also warns that hours claimed "without tangible output" count as no contribution,
which is why §10.2 records output by dimension alongside any hours.

**The measure:** agreed productive hours per member, summed over five sprints, using the course's worked
form `total ÷ mean` (the course's own example turns totals 60 / 55 / 35 into weights 1.2 / 1.1 / 0.7).
`[OWNER TO CONFIRM]` — each member supplies their own hours. **This table is the one required number in
the report that cannot come from the repository.** Do not fill it by inference.

| Member | S1 | S2 | S3 | S4 | S5 | Total | Relative weight (total ÷ mean) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `@JHB11Hinson` | `[OWNER TO CONFIRM]` | | | | | — | — |
| `@AKAScarlett` | `[OWNER TO CONFIRM]` | | | | | — | — |
| `@SY1433` | `[OWNER TO CONFIRM]` | | | | | — | — |
| **Mean** | | | | | | — | |

### 10.2 Contribution by dimension (evidence-based)

This table describes *what each member's record shows*, by dimension. It is not an hours claim, and it deliberately does not add up to a workload.

| Dimension | `@JHB11Hinson` | `@AKAScarlett` | `@SY1433` |
|---|---|---|---|
| **Requirements and planning** | authored the requirements registry and schema; the six `wont` deferrals | test-approval rule and gate-1 scope | merge-train runbook; team-record correction (CHG-026) |
| **Architecture and design** | ADR-001/002/003 baseline, ADR-004 context, ADR-005 telemetry, ADR-006 decision validity, debate ADRs | ADR-014 memory source attribution | ADR numbering correction; ADR status/PR-reference validator |
| **Implementation** | context assembler, telemetry, evaluation harness, runtime prompt store, structured-debate turns | gate-1, mypy quarantine ratchet, gate-2 safety/deps checks | gate-2 promotion; ADR renumbering; validator |
| **Testing and verification** | evaluation set, gate-4, structured-output metric, debate tests | RED tests for gate-2 safety and dependency checks; the quarantine test | tests guarding ADR format and numbering |
| **Code and document review** | 2 review memos; 4 GitHub reviews | **4 review memos; 15 GitHub reviews — the most of any human** | 5 GitHub reviews |
| **Documentation and governance** | `AGENTS.md`, every gate, the 11-session transcript series | review-memo entries for its changes | README evaluator note, merge-train runbook, ADR set hygiene |

> `[OWNER TO CONFIRM]` Each member should correct their own column. The rows are drawn from `git log`, the review memos and the AI-use log; they describe artifacts, not effort, and may miss work done in discussion.

### 10.3 Review load

Because GitHub forbids self-approval and one member authored most pull requests, the **review** contribution concentrated on the other two members and on the automated reviewer:

- `@AKAScarlett`: 4 review memos, 15 GitHub reviews (most of any human);
- `@SY1433`: 5 GitHub reviews;
- `@JHB11Hinson`: 2 review memos, 4 GitHub reviews;
- `github-actions[bot]`: 36 review memos (see §4.4).

Review was a real, uneven load; the contribution table should reflect it rather than hide it under PR counts.

> `[OWNER TO CONFIRM]` **`zihao9462-creator`** merged PRs #7, #8 and #9 and submitted four reviews, and is not in `CODEOWNERS`. Before this report claims a three-person team, explain this account (for example, a collaborator removed by CHG-026, PR #30). If it was a former member or a course instructor, say so here; an unexplained fourth merger in the history is a question an assessor will ask.

---

## 11. Individual reflections

> **These sections must be written by each student.** What follows is an evidence summary and a set of questions — not a draft. A reflection written by the coding agent would undercut the very thing the course uses reflections to show. Each block is preceded by its header; the student writes the paragraph (target 300–500 words) and keeps the header with name and student number.
>
> Each member has a matching worksheet — `docs/report/Reflection-JHB11Hinson.md`,
> `docs/report/Reflection-AKAScarlett.md`, `docs/report/Reflection-SY1433.md` — that repeats this
> evidence, adds two or three specific incidents with the file or commit that proves them, and leaves
> space for the text. The worksheet is the working copy; this section is where the finished paragraph
> is pasted.

### 11.1 Reflection — JIANG Haobin (60198818), `@JHB11Hinson`

**What the repository evidence shows** (for the student to check and then reflect on, not to quote):

- Set the project frame: adopted the inherited baseline, fixed the authority boundary, and wrote `AGENTS.md` as the single agent entry point.
- Built and grew the gates, including the three-stage growth of gate-2 under a stable name (§5.4).
- Defended a frozen interface against an agent optimisation in the ADR-006 review (§9, example 1), and corrected several agent-reported findings that did not survive re-testing (§9, examples 2–3).
- Produced the 11-session annotated transcript series and the AI-use log entries (28 in `docs/ai-use-log/JHB11Hinson.yaml`).
- Orchestrated a very high share of the merged work (45 of 55 merged PRs were opened by this account), which is itself worth reflecting on: how much was co-ordination, and how much would have been better distributed?

**Questions to answer in your own words:**

1. Which single intervention changed the project's direction, and what would have happened without it?
2. Where did you *approve a plan you later wished you had rejected*, and what did that teach you about plan review?
3. You were both the dominant author and a co-ordinator. Looking back, where did that concentration of work weaken the project — in review, in shared understanding, or in documentation?
4. The gates caught code defects; documentation drift survived (§8.2). Why do you think prose went unguarded?
5. With hindsight, would you have specified the requirements differently — earlier, with more members, with different fit criteria?

### 11.2 Reflection — ZHONG Junqiong (60907770), `@AKAScarlett`

**What the repository evidence shows:**

- Designed and implemented gate-1 (the test-before-implementation gate, CHG-030) and the mypy quarantine ratchet test (CHG-051).
- Wrote the RED tests for the gate-2 safety-path and dependency checks (CHG-054), i.e. designed *how the new checks should fail* before they existed.
- Contributed ADR-014, memory source attribution (MEM-003), which prevents future data leaking into a past run.
- Carried the largest human review load: 4 review memos and 15 GitHub reviews (§10.3).

**Questions to answer in your own words:**

1. Gate-1 is hard to get right: what is the boundary between "a test exists" and "a test was approved before the code"? How did you decide, and what did you have to reject?
2. You wrote RED tests for checks you had not yet built. What did that force you to decide earlier than you otherwise would have?
3. ADR-014 (memory source attribution) protects a subtle invariant — that a past run never sees future data. What made this worth an ADR rather than a small fix, and where did the difficulty lie?
4. You reviewed more than anyone else on the team. What did you find hardest to judge: correctness, scope, or the honesty of the PR description? Give one review you would do differently.
5. Was there an agent suggestion that looked reasonable until you inspected it closely? What did inspection find?

### 11.3 Reflection — WANG Songyan (60847491), `@SY1433`

**What the repository evidence shows:**

- Promoted gate-2 to a blocking scoped type check (CHG-021) — a change that had to keep the gate name and protection context stable (§5.4).
- Wrote the merge-train runbook (CHG-028), which arose from observed friction in integrating changes.
- Corrected the team record by removing an inactive collaborator (CHG-026, PR #30) — relevant to the `zihao9462-creator` question in §10.3.
- Renumbered a duplicate ADR-014 to ADR-017 (CHG-053) and added the ADR status/PR-reference validator (CHG-055) that later caught the ADR-016 citation error.
- Documented the evaluator's installed-package trap in the README (CHG-052).

**Questions to answer in your own words:**

1. What exactly was breaking in the merge train, and why did a written runbook help beyond fixing the individual problems?
2. You added a validator for ADR status and PR references rather than fixing one wrong citation. How did you decide that a class of error was worth automating?
3. Renumbering an ADR while other documents cite it is disruptive. How did you sequence the change so it did not break references?
4. The team used an automated reviewer for most PRs (§4.4). As someone who also reviewed manually, how did you find the two differ — and where did automation miss something a human would catch?
5. `docs/ai-use-log/SY1433.yaml` is currently empty. If you contributed to the changes listed above, this reflection is a good place to explain your role in them; the log can then be completed from your account.

> `[OWNER TO CONFIRM]` Whether at least one annotated transcript from each member can be added to `transcripts/` (currently all 30 files belong to `60198818-HaobinJiang`). This is the one course-evidence gap the report cannot close by editing.

---

## 12. Conclusion

We took an inherited framework with two named weaknesses and made both of them **specified, implemented and verifiable**. A forty-entry requirements registry says what must be true; eighteen ADRs (fifteen accepted) say why the design is what it is; six gates make the rules executable; a trace matrix and an invariant register prove coverage; and the AI-use log, with 43 `constrain` and 12 `correct` interventions, is the evidence that a human was directing the work rather than merely receiving it.

The process improved in observable steps: gate-2 grew from lint to type checking to safety and dependency enforcement, each growth triggered by a recorded debt; the evaluation method was corrected when its baseline turned out not to be like-for-like.

What we do not claim is equally important. The cost figure is one pair of live runs, and output tokens rose, so it is not a benchmark. The budget's effect is measured separately and only on two fixtures. Wall-clock time was not measured. Review was automated for 36 of 48 merged pull requests, and the report says so. Three documentation inconsistencies and one empty AI-use log remain, and the transcript evidence is currently single-author. A process report that hides these would not be evidence of a process; this one records them as open items with owners.

> `[OWNER TO CONFIRM]` The conclusion deliberately restates the open items. If any are fixed before submission (see §8.1), move them out of the list and into §8's resolved column rather than deleting the mention.

---

## Appendix A — Deliverable map

| Code | Deliverable | Location | Status |
|---|---|---|---|
| D1 | Requirements (machine-readable) | `docs/req/requirements.yaml`, `docs/req/req-schema.json` | present |
| D2 | Architecture artifacts | `architecture-blueprint.md`, `docs/architecture/**` (blueprint, 18 ADRs, invariants, trace matrix, memory design, permission model, runtime policy catalog, candidate evaluation table, + 3 optional) | present |
| D3 | Coding governance | `AGENTS.md`, `.agent/rules.md`, `.opencode/rules.md`, `.opencode/permissions.jsonc`, `docs/code-governance/**` | present |
| D4 | Verification governance | `docs/code-governance/verification-constraints.md`, `docs/review-memo/` (48 memos), `docs/debt-register.md`, `docs/bug-diary.md` | present |
| D5 | Session transcripts | `transcripts/` (30 files; 27 annotated sessions) | **present — 27 annotated files, all six stages covered; single author** (§11, `Transcript-Compliance.md`) |
| D6 | This report | `Report.md` | this document |
| D7 | GitHub repository, gates, protection | `.github/workflows/ci.yml`, `docs/code-governance/protection.json` | present; six gates each proven red by a probe; live settings `[NEEDS VERIFICATION]` |
| D8 | Source and tests | `src/` (118 modules), `test/offline/` (119 files), `test/live/` | present |
| D9 | Static prompt | `Prompt.md` | present |
| — | Demo video (intro p. 23, excluded from the zip) | — | `[NEEDS VERIFICATION]`: `docs/demo/` has scripts; no video is tracked |

## Appendix B — Open items before submission

| Item | Owner | Status |
|---|---|---|
| Student names and numbers in the title block | each member | **done** — supplied by the team |
| Relative-contribution hours table, weights averaging 1.0 (§10.1) | each member | **required (D6)** — blocker |
| Three reflections (300–500 words, with name + ID) | each member | **not written** — blocker |
| Every `[OWNER TO CONFIRM]` marker resolved | `@JHB11Hinson` + members | open |
| `zihao9462-creator` explained (§10.3) | `@JHB11Hinson` | open |
| At least one transcript per member, or disclosure (§11) | `@AKAScarlett`, `@SY1433` | open — D5 gap |
| `docs/ai-use-log/SY1433.yaml` completed (§4.5) | `@SY1433` | open |
| Live branch protection confirmed against `protection.json` (§5.2) | a member with admin | open |
| Four documentation inconsistencies fixed or disclosed (§8.1) | `@JHB11Hinson` (write-ask) | open |
| Role rotation stated or confirmed (§4.4a) | all members | open |
| Render to PDF and confirm > 15 pages at 12 pt | `@JHB11Hinson` | open |
| Demo video recorded (intro p. 23) | any | `[NEEDS VERIFICATION]` |
