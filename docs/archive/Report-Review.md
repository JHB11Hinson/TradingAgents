# Review Report — CS5351 Process Report (D6) and Student Reflections

**Reviewed artifact:** `/tmp/opencode/report-draft/Report-draft.md` (copy: `/home/u6206/Report-draft.md`, 18,886 bytes, ~3,010 words)
**Authoritative requirements:** `.opencode/manual/CS5351-2026-2027-project.pdf` (D6 on pp. 6–7; D5 on p. 6; D2 on p. 5) and `.opencode/manual/cs5351-2026-2027-introduction.pdf` (Assessment 3, pp. 20–23)
**Repository state audited:** `origin/main` = `b3e0d93` ("feat: CHG-055 ADR status and PR reference validator (#65)")
**Method:** every factual claim re-derived from files, git history, `gh` API output, or a fresh test run. Claims that could not be re-derived are marked `[NEEDS VERIFICATION]`.

> **Scope statement.** This document is a review only. No file under `src/`, `test/`, `docs/`, `prompts/`, no requirement, ADR, governance file, GitHub setting or historical record was modified. No commit, push, PR, merge, approval or branch deletion was performed.

---

## 0. Executive summary

The draft is well-structured and the *tone* is right: it is honest about limitations and avoids marketing claims. Its two most serious problems are both **factual accuracy**, not style:

1. **Several headline numbers are wrong** — the most visible is "65 pull requests merged" (actual: 55 merged, 10 closed, 65 total). A course assessor who opens the repository sees the mismatch immediately, and that undermines every other number in the document.
2. **Two absolute statements are not supportable** — "every change was written by an AI coding agent" and "every merge was a human decision" are both *technically* defensible, but the surrounding prose implies "every change had a human review", which the evidence contradicts: **36 of 48 review memos are automated reviews by `github-actions[bot]`**, and the current head commit (PR #65) was approved **only** by the bot and merged by a teammate.

There is also a **course-compliance gap that no amount of rewriting fixes**: the course requires *five annotated transcripts covering the full supervised pipeline* (D5), and the repository's 30 transcripts are **all from one student** (`60198818-HaobinJiang`). The draft does not mention this.

Finally, **the D6 format requirements are unmet**: the draft has no student names, no student numbers, and no relative-contribution weights. The course is explicit that names, student numbers and relative contribution must be listed, and it shows the formula (member total ÷ team mean).

| Area | Verdict |
|---|---|
| Reported facts | **Numerous errors** — see §1 |
| Absolute statements | **Overstated** — must be qualified |
| D6 formal requirements (names, IDs, weights, length) | **Missing** — see §2 |
| D5 evidence (five annotated transcripts, multi-member) | **Partially satisfied, single-author** — see §2 |
| Six required D6 analytical themes | **Partially covered** — see §2 |
| Structure and reasoning depth | **Solid skeleton, thin analysis** — see §3 |
| Contribution section | **Misleading (PR-count = contribution)** — see §4 |
| Reflections | **Correctly left as prompts** — keep, expand the framework — see §5 |

---

## 1. Critical factual issues

Every row below was checked against the repository at `b3e0d93`. "Draft says" is the wording in the draft; "Evidence" is the command or file that settles it.

### 1.1 Wrong headline numbers

| # | Draft says | Verified fact | Evidence |
|---|---|---|---|
| F1 | "65 pull requests merged" | **55 merged, 10 closed, 65 total** | `gh pr list --state merged --limit 200 --json number --jq 'length'` → 55; `--state all` grouped by state → `{"CLOSED":10,"MERGED":55}` |
| F2 | "55 change records" | **50 unique `CHG-xxx` ids**; no 51–55 exist | `git log --format="%s%n%b" origin/main \| grep -oE "CHG-[0-9]{3}" \| sort -u \| wc -l` → 50. The sequence has gaps at 008, 020, 022–024, and stops at 055 |
| F3 | "1,672 offline tests" | **Correct**: 1,672 passed, 1 skipped, 1 deselected, 99 subtests, 31.4 s | `PYTHONPATH=<wt>/src pytest -q -m "not integration"` on a detached worktree of `b3e0d93` |
| F4 | "119 test files" | **119** `test/offline/*.py` — correct | `ls test/offline/*.py \| wc -l` |
| F5 | "40 registered requirements" | **40**, correct. Priority: 21 must / 12 should / 1 could / 6 wont. Types: governance 14, functional 10, invariant 5, cost 4, quality 4, security 2, performance 1 | `yaml.safe_load(docs/req/requirements.yaml)` |
| F6 | "18 ADRs" | **18 files, but only 15 are `accepted`**; **three are `proposed`** (ADR-016 `PR #60`, ADR-017 `PR-57`, ADR-018 `CHG-054`) | `grep -h "^- \*\*Status" docs/architecture/adr/*.md` |
| F7 | "10 closed or mitigated" debts | **8 closed/mitigated, 2 "none observed", 2 open (DEBT-005, DEBT-009)** = 12. The draft's "10" is reachable only by counting the two "none observed" watch items as repaid debts, and it omits DEBT-005, which is genuinely open | `docs/debt-register.md`, per-entry `Status:` |

**The F1/F2 error pattern matters.** Both mistakes inflate the same thing — activity — and both would be caught by the first person who runs `gh pr list`. Fix them before anything else; a single wrong headline number discredits the accurate ones beside it.

### 1.2 Overstated absolute statements

The task asked specifically about these. Each is *nearly* true but needs a qualifier.

| # | Draft says | What the evidence actually supports |
|---|---|---|
| A1 | "Every change in this repository was written by an AI coding agent" | **No counter-example was found in the git history** — every commit is authored by a member or the agent, and `docs/ai-use-log/` attributes the work to agent execution under human direction. But this cannot be *proved* from the repository: the repository records authorship, not who typed each line. **Reword to "Every change followed the agent-under-supervision protocol"** and cite `AGENTS.md` §7 plus the AI-use log, rather than asserting a property the evidence cannot establish. |
| A2 | "every merge was a human decision" | **Literally true** (all 55 merges were by a human account), **but misleading in context** — the sentence is used to imply human *review*. Reality: **36 of 48 review memos name `github-actions[bot]`**, 4 name `AKAScarlett`, 2 name `JHB11Hinson`. PR #65 — the current head — was approved by `github-actions` only, merged by `SY1433`. **Split the claim**: "every merge was performed by a human account; *review* of 36 of 48 pull requests was an automated non-author review whose text is committed in the repository." |
| A3 | "All six gates are online and blocking" | **Six jobs exist** (`gate-1`…`gate-6`, exact names confirmed in `ci.yml`). **`main.protected: true` is confirmed**, and the committed baseline `docs/code-governance/protection.json` lists the six contexts with `enforce_admins: true`. **`[NEEDS VERIFICATION]`**: the *live* settings could not be read — `gh api .../branches/main/protection` returns **404** because the token lacks admin rights (`perm.admin:false`); `gh api .../rulesets` returns `[]`. So the report may state "six required contexts are committed in `protection.json` and `main` is protected", but must not claim to have re-read the live rule set. Also: **`README.md:177` still says gate-1 is "implemented on the CHG-030 branch; promotion to `main` pending"** — a stale README row that contradicts "all six online". |
| A4 | "every invariant has a test that fails when violated" | **Supported.** `docs/architecture/invariants.md` names, for each of INV-01…08, a verification test and a negative test; the tests exist. Spot-checked: `test/removing_the_detector_leaves_the_hostile_text` and `test/disabling_block_scrubbing_leaves_the_hostile_text` (`test/offline/test_guardrails.py:108,125`), `test_a_json_turn_with_empty_convergence_is_rejected` (`test/offline/test_debate_turns.py:129`), and all four INV-07 telemetry tests. **Caveat to add**: the tests reference the *requirement* ids (`D1-REQ-SAFE-*`, `D1-REQ-OBS-003`, `D1-REQ-DEBATE-001/2`), not the `INV-0x` labels — only INV-01/02/03 appear by their INV id in `test/`. Say the mapping is *by requirement*, not by invariant id. |
| A5 | "The inherited tests are never modified" | **Supported, and unusually clean.** `git diff --name-status 1394a3f..origin/main -- test/` lists **121 entries, all `A` (added)** — zero `M`, zero `D`. | 
| A6 | "Both non-owner members also acted as non-author reviewers" | **True but rare**: `AKAScarlett` submitted 15 GitHub reviews, `SY1433` 5, `JHB11Hinson` 4, bot 25. In *memo* terms `AKAScarlett` authored 4 review memos, `JHB11Hinson` 2. The sentence is fine if it does not imply human review was the norm. |
| A7 | "A fourth account merged 3 PRs" (not in draft, but a claim the draft's "three-person team" implies) | **`zihao9462-creator` merged PR #7, #8, #9** and submitted 4 reviews. Not in `CODEOWNERS`. The report **must** either explain this (a former collaborator removed by CHG-026, PR #30) or risk an assessor reading it as a fourth contributor. **[OWNER TO CONFIRM: who is this account and why was it removed?]** |

### 1.3 Measurement claims

| # | Draft says | Verified fact |
|---|---|---|
| M1 | Inherited→current: −22.2% total, input −35.6%, output **+19.5%** | **Arithmetic correct**: (160,833−206,694)/206,694 = −22.2%; 100,643/156,321 = −35.6%; 60,190/50,373 = **+19.5%**. Sums reconcile (156,321+50,373 = 206,694; 100,643+60,190 = 160,833). Source: `Report.md`. |
| M2 | Fixed set: 70,061 → 64,950, −7.3%, `capped_tokens_ratio` 0.927 | **Correct**: 64,950/70,061 = 0.9270; (64,950−70,061)/70,061 = −7.3% |
| M3 | The two experiments are kept distinct | **Correct — the draft does keep them distinct.** Do not merge them in the rewrite. |
| M4 | (Draft omits) evaluation-set size | `eval/fixed-set.json` has **2 cases** (NVDA-2026-01-09, BABA-2026-01-09). **The report must say this.** "Fixed evaluation set" sounds larger than two fixtures; an assessor will check. Two cases is defensible as a method but must be stated. |
| M5 | (Draft omits) `est_cost` | `eval/baseline.json` records `est_cost_usd: 0.30` from a **120,000-token estimate**, and `Report.md` says the gateway has no price for the model, so measured `est_cost` is 0. The draft should state that cost is *not* measured. |

### 1.4 Repository facts the draft asserts without evidence

| # | Draft says | Verified fact |
|---|---|---|
| R1 | "55 change records" | See F2 — **50** CHG ids |
| R2 | "the 11 session transcripts" (in the contribution table) | `transcripts/` holds **30 files**; 27 are `60198818-HaobinJiang-*` (11 `S`-series + per-CHG + one review), plus 3 non-prefixed. **All 30 belong to one student.** |
| R3 | "ADR-006 review produced three revision rounds (r2, r3)" | **The revision rounds are marked in the ADR file; the count "three" is consistent with the file's r1/r2/r3.** `[NEEDS VERIFICATION: quote the exact §/line of the ADR-006 revision history in the final report rather than paraphrasing.]` |
| R4 | "an automated reviewer posted the committed review text — and the record said so" | **Correct** — `.github/workflows/bot-review.yml` posts `docs/review-memo/PR-<n>-review.md` as an approving review authored by `github-actions[bot]` |
| R5 | "12 tracked technical debts (10 closed or mitigated)" | See F7 |
| R6 | Deliverable map: every D1–D9 path | **All exist**, except see §2 (D5 multi-author gap) and the demo video (not a tracked file; `docs/demo/` holds scripts only) |
| R7 | "18 ADRs" presented as settled decisions | Three are `proposed` (see F6). A "proposed" ADR is not a decision yet; the report should separate the 15 accepted from the 3 awaiting review |

---

## 2. Course requirement gaps (D6, D5, and Assessment 3)

The D6 spec (project.pdf p. 6–7) is short and explicit. This is the compliance checklist. Quotes are transcribed from the extracted PDF text; the PDF is authoritative.

| # | Course requirement (source) | Draft section | Status | Required improvement |
|---|---|---|---|---|
| C1 | "list **all students' names and student numbers**" (D6, p. 6) | absent | **missing** | Add a title block: names + 8-digit student numbers for `@JHB11Hinson`, `@AKAScarlett`, `@SY1433` |
| C2 | "the whole team's **relative contribution**" (D6, p. 6) | §10 has PR counts, no weights | **missing** | Add a table of manhours/story points by sprint, then `member total ÷ team mean` per the intro p. 22 example. **Do not use PR count as the measure** |
| C3 | "at most **10,000 words** (excluding diagrams)" (D6, p. 6) | ~3,010 | **satisfied (under)** | Can grow to ~10k; target ~5–6k to keep quality high |
| C4 | "more than **15 pages** in Point 12 with single-line spacing" (D6, p. 6) | cannot tell from Markdown | **uncertain** | Must be checked in the rendered PDF/Word, not from word count. See §7 |
| C5 | "present the team's **software engineering process** and **how the team optimizes it**" (D6, p. 6) | §3–§6 partly | **partial** | The draft lists artifacts; it does not narrate *how the process changed over time*. Add a "process evolution" thread (e.g. how CHG-030 → CHG-051 → CHG-054 grew gate-2) |
| C6 | "each member's self-reflection… **name and student ID**" (D6, p. 6) | §11 prompts only | **missing** | Each reflection must carry name + ID and be written by the student |
| C7 | "Cover **process quality evidence**: requirement volatility, defect trends, ambiguity resolution" (D6, p. 6–7) | not covered | **missing** | New subsection. Requires data the team must choose to measure (see §3.4); the draft cannot invent it |
| C8 | "how the team kept **artifacts co-evolving** when anything changed" (D6, p. 7) | §8 drift table touches it | **partial** | Turn the drift anecdotes into a claim: "every requirement change re-ran gate-3 + trace test; here are 3 cases" |
| C9 | "what **human oversight caught that the agent did not**" (D6, p. 7) | §8, §9 | **partial** | Needs concrete, evidenced cases — the AI-use log has 12 `correct` and 43 `constrain` entries; surface 2–3 with quotes |
| C10 | D5: **"five annotated agent-session transcripts"** covering "the entire supervised pipeline" (project.pdf p. 6; p. 2) | §10 mentions "the 11 session transcripts" | **partial / at risk** | **All 30 transcripts are by one student.** The course implies team-wide transcripts. Either obtain at least one annotated transcript from each of the other two members, or state plainly that the transcript evidence is single-author and explain why. **[OWNER TO CONFIRM]** |
| C11 | D5: transcripts "annotated with the student team members' marked interventions and a rationale" (p. 6) | not discussed | **uncertain** | Check annotations exist and are marked; cite one example |
| C12 | Assessment 3: **10-minute demo video** comparing "with/without the new requirements" (intro p. 23), *excluded* from the zip | not mentioned | **missing** | Add a short "demo" note; the video itself is a separate submission item, not a report section. `docs/demo/` scripts exist; **no video file is tracked** `[NEEDS VERIFICATION: has the video been recorded?]` |
| C13 | Quality attribute focus: intro lists correctness, turnaround, success rate, token consumption, and trade-offs among them (intro p. 18) | token consumption only | **partial** | Add a short trade-off discussion; you have token + success/eval data, not wall-clock |
| C14 | "Respect your teammates, as not everyone wants A+" (intro p. 22) | n/a | **note** | Contribution weights are sensitive. Present them without editorialising |

### 2.1 The two most likely-to-cost-marks gaps

**C1 + C2 (names, IDs, contribution weights).** These are trivial to add and are *explicitly* itemised on the D6 page. Omitting them looks like not reading the brief. They must be in the final report.

**C10 (single-author transcripts).** This is the substantive risk. The course's whole model is "authentic human authorship shown through transcripts". Every transcript currently comes from one student. Whether the assessor accepts that depends on the rubric; the safest position is to (a) get one annotated transcript from each other member, or (b) disclose the asymmetry explicitly and let the other members' contribution show through their AI-use-log entries and review memos.

---

## 3. Structural and analytical weaknesses

### 3.1 The draft reports artifacts, not process

Sections 1–6 are written as *inventory* ("18 ADRs", "six gates", "119 test files"). That is what the deliverables are, not what the course asks the report to **explain**. D6 asks for *the process and how it was optimised*. The rewritten draft should make each major artifact a short narrative with the reasoning chain:

`Problem → Alternatives → Decision → Implementation → Evidence → Lessons Learned`

The strongest candidates for that treatment are already visible in the repository:

- **Gate-2's three-stage growth**: it began as `ruff` only (ADR-003), gained a scoped `mypy` with a shrink-only quarantine (CHG-021, ADR-016), then a safety-path guard and a dependency check (CHG-054, ADR-018). That is a *process being optimised in response to evidence* — exactly what D6 wants.
- **The evaluation method**: the initial baseline was an *estimate* (120,000 tokens); E-001 found the ledger under-counted; E-002 ran the fixed set; DEBT-011 found the capped/uncapped comparison was not like-for-like, and CHG-039 fixed it. That is a full Problem→Evidence→Lessons arc.
- **The bot-review mechanism**: a real workflow was built because there were not enough human reviewers. Stating *why* (reviewer capacity) and *what it costs* (review is automated, not human) is stronger than either hiding it or overclaiming human review.

### 3.2 Analysis that is asserted rather than shown

- §5 "Two pain points, two attacks" lists components but does **not show the before/after** for the debate. The structured debate is `agents/debate.py` + `schemas.DebateTurn`; the report should quote one `DebateTurn` field list and say what a free-form turn lacked.
- §6 "A test asserts that mapping has no gaps" — true, but the report never names the test. Name it and the command that runs it.
- §4 "deliberate-violation probes went red" — the *closed* PRs include probes; **`gh pr list --state closed` for titles matching "probe"/"violation" returns none**, so the probes were either PRs with other titles or run locally. **`[NEEDS VERIFICATION: name the probe PR numbers or the local command output; otherwise soften to "we ran deliberate-violation checks and observed them fail".]`**

### 3.3 Terminology and consistency

- "change record" vs "CHG" vs "PR" are used loosely; the draft implies 55 of something (F2). Define: a **CHG** is a recorded change id; a **PR** is a GitHub pull request; they are not 1:1.
- §0 "Scale of the result" mixes merged PRs, requirements, ADRs, CHGs, tests, gates, debts into one sentence — a single wrong number there (and one is wrong) discredits the rest. Break it into labelled facts.
- The draft alternates "we" and "the team" and "the owner"; pick "the team" for process narration and name individuals only in the contribution section.

### 3.4 Missing data the report will need (team must measure)

C7 (requirement volatility, defect trends) and C2 (contribution weights) require **data that does not currently exist in a single place**. These are honest gaps to close, not things to invent:

- **Requirement volatility**: count how many entries in `requirements.yaml` changed `priority` or `fit_criterion` after first registration. Derivable from `git log -p docs/req/requirements.yaml`, but someone must do the count.
- **Defect trends**: `docs/bug-diary.md` exists — count entries by date and by invariant gap exposed.
- **Contribution hours/story points**: only the team can supply these. The repository records *artifacts*, not time.

---

## 4. Contribution section issues

The current §10 is the weakest section analytically.

1. **PR count is presented as the contribution column.** 45 / 5 / 5 reads as "one member did nine times the work". The course (intro p. 22) explicitly suggests hours or story points, and says the measure "should reward students who take up difficult tasks and project management". PR count does neither: it rewards whoever opens pull requests, and the owner opened most of them because the agent did most of the work under that person's direction.
2. **The table conflates authorship with ownership of a theme.** `@AKAScarlett`'s 5 PRs include gate-1 (CHG-030), the mypy-quarantine ratchet test (CHG-051), memory source attribution (MEM-003, ADR-014), and gate-2 safety/deps RED tests (CHG-054) — these are substantial, themed, and gated. Listing "5" understates them; listing them by outcome is fairer.
3. **It does not separate the six dimensions the task asks for**: requirements/planning, architecture/design, implementation, testing/verification, code review, documentation/governance. The rewrite should have a matrix with evidence per cell.
4. **It omits the review load.** `AKAScarlett` submitted 15 GitHub reviews (the most of any human) and authored 4 review memos. That is real contribution and it is currently invisible.
5. **It omits `zihao9462-creator`.** See A7. If that account merged three early PRs, the report must explain it or the "three-person team" framing is fragile.

**Recommended measure** (to be confirmed by the team): a small table with `member × dimension → short evidenced note`, plus a separate **claimed hours/story points** row that only the members can fill, plus the arithmetic `total ÷ mean` to produce the relative weight the course asks for. **Do not fill the hours row with invented numbers.**

---

## 5. Reflection section issues

The draft is **right** to leave reflections as prompts. Keep that. Two improvements:

1. **Each prompt should cite the specific evidence** the student can look at, so their reflection is anchored in what actually happened rather than generic. The improved draft does this: each member's block names 2–3 concrete incidents with file/PR references.
2. **Each reflection must open with name + student number** (C6) and target 300–500 words (the course says "e.g., 300–500 words"; treat 300–500 as the target).
3. **Do not let the agent write these.** A reflection written by the same agent that wrote the code is not evidence of human authorship; it is the opposite. The framework below gives questions; the student supplies the experience.

Per-member evidence summaries and questions are in §5 of the improved draft (`Report-Improved-Draft.md` §11).

---

## 6. Prioritised improvement plan

Ordered by *marks at risk per unit of effort*.

| Priority | Action | Why | Effort | Blocked on |
|---|---|---|---|---|
| **P0** | Fix F1 (55 merged, not 65) and F2 (50 CHGs, not 55) | Wrong headline numbers; trivially checkable | 5 min | — |
| **P0** | Add student names + student numbers (C1) | Explicit D6 item, currently absent | 5 min | members' IDs |
| **P0** | Qualify A1/A2 (AI-written; human merge vs review) | Absolute claims that the evidence refines | 20 min | — |
| **P1** | Add the relative-contribution table with the course formula (C2) | Explicit D6 item | 30 min + team hours | **members' hours [OWNER TO CONFIRM]** |
| **P1** | Disclose the single-author transcript situation (C10) | Substantive D5 risk | 15 min | decision to obtain more transcripts |
| **P1** | State the evaluation set is **2 cases** (M4) and cost is unmeasured (M5) | Prevents overstatement | 10 min | — |
| **P1** | Separate 15 accepted ADRs from 3 proposed (F6/R7) | Accuracy; "18 decisions" overstates | 10 min | — |
| **P2** | Add C7 data: requirement volatility, defect trends | Explicit D6 theme, currently missing | 1–2 h | team must measure |
| **P2** | Rewrite §1–§6 as process narratives (§3.1) | Converts inventory into analysis | 2–3 h | — |
| **P2** | Resolve or soften the "probe PRs" claim (§3.2) | Unverifiable as written | 15 min | evidence or softening |
| **P3** | Render to PDF and confirm >15 pages (C4) | Cannot verify from Markdown | 20 min | final text |
| **P3** | Note the demo video (C12) | Separate submission item | 5 min | video status |

### 6.1 Items that need a human decision before they can be fixed

These cannot be resolved by editing the draft:

1. **Student numbers** for all three members (C1).
2. **Contribution hours/story points** (C2) — only the team knows them.
3. **`zihao9462-creator`** — who it is and why the account merged three PRs (A7).
4. **More transcripts** from `@AKAScarlett` and `@SY1433` (C10), or an explicit disclosure.
5. **Live branch protection** — cannot be re-read with the current token (A3); someone with admin must confirm the live rule set matches `protection.json`.
6. **Stale README gate-1 row** (`README.md:177`) and the `AGENTS.md` §4 "86 files / 1262 passed" baseline and `verification-constraints.md` TERM-001 "partial" — all three are *documentation* corrections in write-ask paths. They are **not** report-editing, so they stay out of this task; the improved draft discloses them as open items rather than fixing them.

---

## 7. Length verification

- The course requires **> 15 pages in Point 12 single spacing** and **≤ 10,000 words excluding diagrams**. The Markdown draft cannot prove the page count; page count depends on font size, margins and the renderer. **`[NEEDS VERIFICATION: render to PDF at 12 pt and count pages.]`**
- Current draft: ~3,010 words. Adding the D6-required sections (names, contribution table, process-quality evidence, deeper narratives) plausibly lands at **5,000–6,500 words**, which is comfortably under the word cap. Whether 5–6k words fills 15 pages at 12 pt depends on tables and figures; a typical 12 pt single-spaced A4 page holds ~500–600 words of prose, so **5,500 words ≈ 10–11 pages of prose**, and tables/diagrams add pages. **It may still fall short of 15 pages.** The safe move is to add the *required* analysis (C5–C9) and then measure; do not pad.
- The improved draft's estimated length is given at its head.

---

## 8. What is genuinely good and should be preserved

Say this plainly, because a rewrite should not lose it:

- **The honesty about the token measurement is exemplary.** `Report.md` (carried into draft §7) separates the two experiments, states "one run per side", says output tokens *rose*, and refuses a general "cheaper" claim. That is exactly the standard D6 asks for, applied rigorously. Preserve it near verbatim.
- **The `wont` decisions with written reasons** are the best evidence of judgement in the repository. Each names a cost the team declined. Keep them.
- **Naming the stale-document drift** (ADR-016 "PR-3" → PR #60; TERM-001 "partial") is real "human oversight caught what the agent did not" material. Do not delete it to look polished.
- **The invariant register's negative tests** are unusually rigorous and are correctly evidenced. This is a strength; present it as one.

---

## 9. Bottom line

The draft is a solid skeleton with reliable *structure* and several *reliable* passages (the measurement section especially), but it is not yet an accurate process report. Fix the wrong headline numbers and the two absolute statements first — they are cheap and they protect the credibility of everything else. Then add the three items D6 names explicitly and the draft omits (names+IDs, contribution weights, process-quality evidence). The transcript single-author issue is the one substantive risk that no editing resolves; it needs either more transcripts or an honest disclosure.

The improved draft that follows implements every fix that can be made from repository evidence, marks every remaining gap as a confirmation item, and leaves all three reflections as evidence-anchored frameworks for the students to write.
