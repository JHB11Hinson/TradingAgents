# CS5351 — Team Confirmation Sheet

**Purpose.** Every value in this sheet is filled in by the student it belongs to. The fields below feed
the report's D6 sections. Nothing here was inferred, estimated or copied from git history — where the
repository proves something, it is named as *evidence*; where it cannot, the field is left blank.

**How to use.** Each member fills their own block in §2 and confirms §3; the team agrees §5
together. Hand the completed sheet back; the values are copied verbatim into `Report.md` §10 and §11.

---

## 1. Identity block (D6 p. 6)

| Member | Full name | Student number | GitHub username | Course email |
|---|---|---|---|---|
| 1 | JIANG Haobin | 60198818 | `@JHB11Hinson` | |
| 2 | ZHONG Junqiong | 60907770 | `@AKAScarlett` | |
| 3 | WANG Songyan | 60847491 | `@SY1433` | |

> Names and student numbers were supplied by the team. The handle-to-person mapping was chosen by the
> team; the repository records only handles. **Course email is still blank.**

> The GitHub username column is pre-filled because it is the one identity fact the repository proves.
> **Full name and student number must match the course enrolment record** — the report is marked
> against it.

**Team size check.** The course describes "an N-student group project". Our repository: 3 accounts in
`.github/CODEOWNERS`. A **fourth account, `zihao9462-creator`, merged pull requests #7, #8 and #9 and
submitted four reviews**, and is not in `CODEOWNERS`.

- [ ] `zihao9462-creator` was **a member of this team** (name: ______________________; student number: ____________)
- [ ] `zihao9462-creator` was **a former collaborator**, removed before submission (removed in PR #30, CHG-026)
- [ ] `zihao9462-creator` was **the course instructor / a TA / other** (explain: ______________________)

*Who confirms:* `@JHB11Hinson`. *Why it matters:* if the assessor reads four contributors, a
three-person contribution table looks incomplete.

---

## 2. Contribution measure (D6 p. 7; intro p. 22)

The course lets the team choose the measure. **Tick one:**

- [ ] **Actual productive hours** per sprint
- [ ] **Story points** per sprint
- [ ] **Other** (state it): ______________________________

**Team agreement on what counts as a contribution** (the course says "reward students who take up
difficult tasks and project management", and that hours without tangible output count as no
contribution). Write the team's rule here, in one or two sentences:

```
______________________________________________________________________________
______________________________________________________________________________
```

### 2.1 Per-member table (fill every cell; do not estimate)

| Member | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 | **Total** | **Relative weight** |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 `@JHB11Hinson` | | | | | | | |
| 2 `@AKAScarlett` | | | | | | | |
| 3 `@SY1433` | | | | | | | |
| **Mean** | | | | | | | |

**Formula** (from the course's worked example, totals 60 / 55 / 35):

```
Mean = (total₁ + total₂ + total₃) / 3
weightᵢ = totalᵢ / Mean
```

The three weights must **average to 1.0** (project.pdf p. 4: "The average contribution is 1.0").
Check: `(w₁ + w₂ + w₃) / 3 = 1.000`.

**Sprint dates.** The course example uses five sprints. Our team's sprint boundaries are:

| Sprint | From | To |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

*Who confirms:* each member supplies their own row; the team agrees the measure and the sprint dates.

> **Do not** substitute merged-PR counts. The repository shows `@JHB11Hinson` opened 45 of 55 merged
> PRs, but the agent executed the code, so PR count measures who was directing the agent, not effort.
> The course does not permit it as a substitute for hours or story points.

---

## 3. Contribution by dimension (confirmation, not numbers — D6 p. 6)

For each member, confirm which dimensions their work fell in. Tick all that apply; the report's §10.2
matrix was built from git, review memos and the AI-use log and may miss work done in discussion.

| Dimension | `@JHB11Hinson` | `@AKAScarlett` | `@SY1433` |
|---|---|---|---|
| Requirements and planning | [ ] | [ ] | [ ] |
| Architecture and design | [ ] | [ ] | [ ] |
| Implementation | [ ] | [ ] | [ ] |
| Testing and verification | [ ] | [ ] | [ ] |
| Code and document review | [ ] | [ ] | [ ] |
| Documentation and governance | [ ] | [ ] | [ ] |
| Project management / co-ordination | [ ] | [ ] | [ ] |

**Corrections to the draft's §10.2 matrix** (state what is wrong or missing):

```
@JHB11Hinson: ______________________________________________________________
@AKAScarlett: ______________________________________________________________
@SY1433:      ______________________________________________________________
```

---

## 4. Reflection status (D6 p. 6)

Each member writes a short reflection (the course's example is 300–500 words) in their own words. The
report carries it with the member's **name and student number**.

| Member | Worksheet file |
|---|---|
| 1 `@JHB11Hinson` | `Reflection-HaobinJiang.md` |
| 2 `@AKAScarlett` | `Reflection-60907770-ZhongJunqiong.md` |
| 3 `@SY1433` | `Reflection-SY1433.md` |

---

## 5. Transcript authorship and annotation (D5, project.pdf p. 6)

The course requires **five annotated agent-session transcripts** that *collectively* demonstrate the
six supervised stages, "annotated with the student team members' marked interventions".

**Current state (verified):** 27 files in `transcripts/` follow `<student-id>-<student-name>.md`;
**all of them are authored by `60198818 Haobin Jiang`**. Each session carries a
`### Human interventions` table with a `Why` rationale — 27 annotated interventions across 11 sessions.
The index file carries a D5 coverage map naming sessions for **all six stages**.

| Member | Has transcript(s)? | Count | Annotated with rationale? | Confirmed by member |
|---|---|---:|---|---|
| 1 `@JHB11Hinson` | yes (`60198818-HaobinJiang-*`) | 27 files | yes (`Human interventions` tables) | [ ] |
| 2 `@AKAScarlett` | **no** | 0 | — | [ ] |
| 3 `@SY1433` | **no** | 0 | — | [ ] |

**Decision required** (tick one):

- [ ] **A. Add transcripts.** `@AKAScarlett` and `@SY1433` each contribute at least one annotated
      session transcript under `transcripts/<student-id>-<student-name>.md`, covering a stage not
      already covered. *(Preferred: it matches the course's wording that the transcripts are the
      "primary evidence of authentic human authorship" — intro p. 20.)*
- [ ] **B. Disclose the gap.** The report states plainly that transcript evidence is single-author,
      and points to the other members' AI-use-log entries and review memos as their authorship
      evidence.

*Who confirms:* all three members. Chosen option: ______

> **Do not** copy, relabel or re-attribute `@JHB11Hinson`'s transcripts to another member. A
> re-attributed transcript is worse than a disclosed gap.

---

## 6. Outstanding factual confirmations

The draft has `[OWNER TO CONFIRM]` markers. Tick each once resolved.

| # | Question | Answer | Confirmed by |
|---|---|---|---|
| 1 | Were the six `wont` deferrals (CHG-032) a team decision, or one member's? | | |
| 2 | Does the ADR-006 §9 example (rejecting a return-shape change) accurately describe what happened? | | |
| 3 | Should §8.1's three documentation inconsistencies be fixed before submission, or disclosed as open? | | |
| 4 | Is the 10-minute demo video recorded? | | |
| 5 | Can a member with admin access confirm live branch protection matches `protection.json`? | | |

---

**Open items:** §1 course email, §2.1 hours/story points, §4 two reflections, §5 transcript decision.
