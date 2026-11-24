# D5 Transcript Compliance Assessment

**Requirement** (project.pdf p. 6, p. 2, p. 9):

> "One full, raw transcript of an AI coding agent session to build the system implementation from
> scratch. Each transcript is annotated with the student team members' marked interventions and a
> rationale for each, showing where the team interrupted, redirected, approved, or rejected the
> agent's work. Collectively, the transcripts must demonstrate the entire supervised pipeline:
> requirements classification, architecture candidate generation and evaluation, plan approval before
> code, build, verification compliance, and architecture revision based on test evidence."

Plus (p. 2): "One repository plus **five annotated agent-session transcripts** and one process report."
Plus (p. 9, repository structure): `transcripts/<student-id>-<student-name>.md`.
Plus (intro p. 20): "The full session transcripts are the **primary evidence of authentic human
authorship**."

**Audited:** `transcripts/` at `b3e0d93`, 2026-11-25.

---

## 1. Correction to an earlier finding

The previous review noted "no standardized annotation markers" and reported that claims about
deliberate-violation probes were unverifiable. **Both were wrong.** Re-inspection found:

- **Annotations exist and are structured.** Each session file opens with a
  `### Human interventions` table with four columns: `#`, `Type`, `What`, `Why`. The `Type` values are
  `approve`, `constrain`, `redirect`, `correct`. The `Why` column is the **rationale the course asks
  for**.
- **Deliberate-violation probe pull requests exist** — eight of them, and each target gate turned red.

The earlier method (grep for `[INTERRUPT]`-style markers) missed the table format. This assessment
supersedes that finding.

---

## 2. Inventory — what is in `transcripts/`

| Group | Files | Convention | Author |
|---|---:|---|---|
| Index | 1 (`60198818-HaobinJiang.md`) | `<id>-<name>.md` ✓ | 60198818 Haobin Jiang |
| Session series | 11 (`S01`–`S11`) | `<id>-<name>-Sxx-...md` ✓ | 60198818 Haobin Jiang |
| Per-change records | 15 (`CHG-036`…`CHG-049`, `PR-57`) | `<id>-<name>-CHG-...md` ✓ | 60198818 Haobin Jiang |
| Legacy names | 3 (`CHG-021-gate-2-promotion.md`, `CHG-034-bot-review.md`, `CHG-034-telemetry.md`) | ✗ no student prefix | unclear from filename |
| **Total** | **30** | | **27 explicitly attributed to one student** |

**Authorship, verified:** every prefixed filename begins `60198818-HaobinJiang`, and the index header
states `Owner: 60198818 Haobin Jiang (@JHB11Hinson)`.

---

## 3. Do the transcripts qualify?

| Criterion | Verdict | Evidence |
|---|---|---|
| At least **five** transcripts | **Yes** — 27 | count above |
| `<student-id>-<student-name>.md` naming | **Mostly** — 27 of 30; 3 legacy names | `CHG-021-*`, `CHG-034-*` |
| Annotated with **marked interventions** | **Yes** | `### Human interventions` table per session |
| A **rationale** for each intervention | **Yes** — the `Why` column | e.g. S06 row 3: *"The draft over-claimed a course rule; the governance entry point must state the actual classification."* |
| Shows **interrupt / redirect / approve / reject** | **Yes** | `Type` values include `redirect`, `constrain`, `correct`, `approve` |
| Collectively cover the **six stages** | **Yes, per the index** | coverage map below |
| Authored by **team members** (plural) | **No** — one student only | all prefixed files are `60198818-HaobinJiang` |

### 3.1 Six-stage coverage (from the index's own D5 coverage map)

| D5 stage | Sessions covering it |
|---|---|
| Requirements classification | 03, 05 |
| Architecture candidate generation and evaluation | 03, 04 |
| Plan approval before code | 01, 04, 06, 07 |
| Build | 01, 02, 05, 06, 07 |
| Verification compliance | 01, 02, 04, 05, 06, 08, 09, 10 |
| Architecture revision from test evidence | 04, 06, 10 |

**All six stages are covered.** This is the strongest part of the transcript evidence.

### 3.2 Annotation density (interventions per session)

| Session | Interventions | Session | Interventions |
|---|---:|---|---:|
| S01 | 2 | S07 | 3 |
| S02 | 2 | S08 | 2 |
| S03 | 2 | S09 | 1 |
| S04 | 4 | S10 | 2 |
| S05 | 3 | S11 | **0** |
| S06 | 6 | **Total** | **27** |

S11 is 32 lines and records no intervention — it is a short audit session, not a supervised build.

---

## 4. Missing evidence, by member

| Member | Transcripts | Stages covered alone | Author-authorship evidence available instead |
|---|---:|---|---|
| `@JHB11Hinson` (60198818 Haobin Jiang) | **27 files** | all six | transcripts + 28 AI-use-log entries + 45 merged PRs |
| `@AKAScarlett` | **0** | none | 4 AI-use-log entries, 4 review memos, 15 GitHub reviews, 5 merged PRs |
| `@SY1433` | **0** | none | **0 AI-use-log entries** (file is header-only), 5 GitHub reviews, 5 merged PRs |

**Risk assessment.** The course calls transcripts the "primary evidence of authentic human authorship".
Two of three members have no transcript at all, and one of those (`@SY1433`) has an empty AI-use log.
If the assessor applies the wording literally, the evidence for two members' authorship is thin —
though not absent: review memos, GitHub reviews and merged PRs do show those members acted.

---

## 5. Additional work required

### Option A — add transcripts (recommended)

| Step | Owner | Detail |
|---|---|---|
| 1 | `@AKAScarlett` | Export at least one annotated session under `transcripts/<student-id>-<student-name>.md`, covering a stage their work actually touched (e.g. gate-1 design = **plan approval**; the RED tests for gate-2 = **verification compliance**) |
| 2 | `@SY1433` | Same, e.g. the gate-2 promotion = **verification compliance**; the ADR validator = **architecture revision** |
| 3 | both | Use the same `### Human interventions` table format with a real `Why` for each row |
| 4 | both | Add the new files to the index's part table |

One qualifying transcript each would make the set team-wide while the six-stage coverage (already
complete via `@JHB11Hinson`'s sessions) stays intact.

### Option B — disclose the gap

If no additional transcript exists, the report states in §11 and Appendix B that transcript evidence is
single-author, and points to each other member's review memos, GitHub reviews and merged PRs.

### Do not

**Do not** copy, split or relabel `@JHB11Hinson`'s transcripts under another member's name. A
misattributed transcript is academic-integrity risk; a disclosed gap is a limitation.

---

## 6. Verdict

| Question | Answer |
|---|---|
| Does the repository meet "five annotated transcripts"? | **Yes** — 27 annotated files, 27 interventions with rationales |
| Does it demonstrate the six-stage pipeline? | **Yes** — the index maps every stage to named sessions |
| Is it "the student team members' marked interventions"? | **Only one member's.** This is the gap. |
| Is the gap closeable by editing the report? | **No.** It needs two new transcripts, or a disclosure. |

**Status: partial — strong on annotation and coverage, weak on multi-member authorship.**
