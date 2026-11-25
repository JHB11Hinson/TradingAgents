# CS5351 D6 — Course Requirement Compliance Checklist

**Re-derived** from `.opencode/manual/CS5351-2026-2027-project.pdf` (extracted text) and `.opencode/manual/cs5351-2026-2027-introduction.pdf`, on 2026-11-25, at repository `b3e0d93`.
**Assessed artifact:** `Report-Improved-Draft.md` (this round's revision).
**Status vocabulary:** `satisfied` · `partial` · `missing` · `blocked` (needs data only a student can supply) · `unverifiable` (cannot be checked from the repository).

---

## A. Formal D6 requirements (project.pdf p. 6–7)

| # | Requirement (verbatim anchor) | Location in draft | Status | What remains |
|---|---|---|---|---|
| A1 | "list all students' **names and student numbers**" | Title block | **satisfied** | Names and IDs supplied by the team (JIANG Haobin / ZHONG Junqiong / WANG Songyan). Handle-to-person mapping confirmed by the team. |
| A2 | "the whole team's **relative contribution**" | §10.1 | **satisfied** | Team-agreed shares 34 / 33 / 33; weights 1.02 / 0.99 / 0.99, mean 1.0. No sprint split recorded. |
| A3 | "at most **10,000 words** (excluding diagrams)" | whole file | **satisfied** | ~8,600 words (see measurement note). |
| A4 | "contain **more than 15 pages** in Point 12 with single-line spacing" | whole file | **unverifiable** | Markdown has no pages. Must be rendered at 12 pt and counted. |
| A5 | "present the team's **software engineering process** and **how the team optimizes it**" | §1–§6, §5.4 | **satisfied** | Gate-2's three-stage growth and the evaluation-method correction are the two optimisation narratives. |
| A6 | "each member's **self-reflection** … **with name and student ID**" | §11.1–§11.3 | **blocked** | Two reflections are written in `docs/report/`; the report still needs the final text, and `@SY1433`'s reflection is open. |
| A7 | "Cover process quality evidence (**requirement volatility**, **defect trends**, **ambiguity resolution**)" | §7.7 (new) | **satisfied** | Computed from git history, bug diary, review memos, ADR revision history. See §B. |
| A8 | "how the team kept **artifacts co-evolving** when anything changed" | §8.2 (new) | **partial** | Three evidenced cases (CHG-029 schema split, CHG-032 deferral, CHG-055 validator). Honest about the gaps. |
| A9 | "what **human oversight caught that the agent did not**" | §9 | **satisfied** | Three cases from the AI-use log; one flagged for owner confirmation. |

## B. Contribution formula compliance (project.pdf p. 4, p. 7; intro p. 22)

| # | Requirement | Status | Note |
|---|---|---|---|
| B1 | A relative-contribution section | **satisfied** | §10.1 has the team-agreed shares, totals and weights. |
| B2 | "The **average contribution is 1.0**" (p. 4) | **satisfied** | (1.02 + 0.99 + 0.99) / 3 = 1.00. |
| B3 | Measure = "productive hours … or **story points**"; teams choose | **partial** | Team chose a normalized contribution share (the course permits team-chosen measures); no sprint split recorded. |
| B4 | "reward students who take up **difficult tasks and project management**" | **partial** | §10.2 records project management and difficult tasks; co-member confirmation is still pending. |
| B5 | "A student saying … 100 hours … **without tangible output** … no contribution" (intro p. 22) | **satisfied** | §10.2 records tangible output per dimension, so hours cannot stand alone. |
| B6 | Role **rotation** (p. 4: "rotate roles") | **partial** | README §10 assigns fixed primary responsibilities; rotation is not evidenced. Disclose as a limitation. |

## C. D5 — Agent session transcripts (project.pdf p. 6, p. 2)

| # | Requirement | Status | Note |
|---|---|---|---|
| C1 | "**five** annotated agent-session transcripts" | **satisfied (count)** | 27 files under the `<student-id>-<student-name>.md` convention; 11 are session-numbered parts. |
| C2 | Each "**annotated** with … marked interventions and a **rationale** for each" | **satisfied** | Each session opens with a `### Human interventions` table: `#` / `Type` / `What` / `Why`. 27 interventions across the 11 sessions. |
| C3 | Covers "the **entire supervised pipeline**" (six stages) | **satisfied** | Index `transcripts/60198818-HaobinJiang.md` carries an explicit D5 coverage map naming sessions per stage, all six present. |
| C4 | Authored by "the student **team members**" (plural) | **partial / blocker** | **All 27 belong to `60198818 Haobin Jiang` (`@JHB11Hinson`).** `@AKAScarlett` and `@SY1433` have no transcript. See `Transcript-Compliance.md`. |
| C5 | File naming `<student-id>-<student-name>.md` | **satisfied** | Three non-prefixed legacy names (`CHG-021-…`, `CHG-034-bot-review.md`, `CHG-034-telemetry.md`) do not follow it — minor cleanup, not a blocker. |
| C6 | Raw transcript to build "from scratch" | **unverifiable** | The split index records the original combined file's SHA-256 and pre-split commit; whether it is "from scratch" is a judgement. |

## D. Other D-series items the report touches

| # | Requirement | Status | Note |
|---|---|---|---|
| D1 | D7 branch protection "must require passing CI, and changes to safety-critical paths must require human review with an accompanying architecture decision" | **partial** | Six contexts committed in `protection.json`; live rule details could not be re-read (token lacks admin). ADR-018 + `safety-paths.txt` implement the ADR requirement. |
| D2 | D7 gate 4: "for any **prompt or model** change, the pipeline replays a fixed evaluation set" | **partial** | gate-4 runs on every pull request; `EVAL-002` (restricting to prompt changes) is `wont`. Broader than required, not narrower — acceptable. |
| D3 | Intro p. 23: **10-minute demo video**, excluded from the zip | **missing** | No video tracked; `docs/demo/` holds scripts only. |
| D4 | Intro p. 20: "**AI-generated code is explicitly permitted and expected**. No non-agentic modification … allowed" | **satisfied** | Stated in §4.3 with the AI-use log as evidence. |
| D5 | D2.2: "**layered context structure** … assembly pipeline … **token-budget cap with its compaction threshold** … **re-injecting critical constraints after compaction**" | **partial** | §3.3 states all four, but the **numeric compaction threshold** is not quoted from the code. `[NEEDS VERIFICATION]` — cite the constant. |

## E. The relative-contribution formula (transcribed from intro p. 22 and project.pdf p. 7)

```
Mean contribution      = (total_a + total_b + total_c) / 3
Relative weight(member)= member_total / Mean contribution
```

Worked example given by the course: totals 60 / 55 / 35 → mean 50 → weights **1.2 / 1.1 / 0.7**.
The report must reproduce this shape with the team's own agreed measure.

## F. Summary

Counted from the four tables above: **26 checked items.**

| Status | Count | Items |
|---|---:|---|
| satisfied | 14 | A1, A2, A3, A5, A7, A9, B1, B2, B5, C1, C2, C3, C5, D4 |
| partial | 8 | A8, B3, B4, B6, C4, D1, D2, D5 |
| blocked (student-supplied only) | 1 | A6 |
| unverifiable | 2 | A4, C6 |
| missing | 1 | D3 |

**The report is not submission-ready.** One blocked item remains student-supplied (the three
reflections); the D5 transcript gap (C4), the demo video (D3) and the page-count check (A4) also remain
open. Everything else is satisfied or honestly marked.

*A1 was recorded as blocked in the first pass; the team supplied the three names and student numbers, so
it is now satisfied. A2/B1/B2 were also blocked until the team supplied the 34/33/33 share on
2026-11-25.*
