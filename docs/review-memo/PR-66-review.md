### Review of PR-66 — CHG-056: the D6 process report and its working papers

**Reviewer:** `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated non-author review.**
The text below is committed in the repository before the `bot-review` label is applied, so the
approval is reproducible. The workflow posts this file verbatim; it names the reviewer as automated and
does not present itself as a human review. The author does not self-approve.

**Head reviewed:** `ddb9914`, the head that carries `Report.md` (768 lines changed), nine new files under
`docs/report/`, `docs/review-memo/PR-66.md` and one AI-use-log entry. **No commit after this one may be
pushed without dismissing this approval and re-applying the label** (`dismiss_stale_reviews: true`).

---

#### Scope

Documentation only. `git diff origin/main --name-only` contains no path under `src/`, `test/` or
`prompts/`, so:

- **gate-1** has nothing to approve (`gate1_check.py` returns "no src/ change");
- **gate-6** is not triggered because no code, test or prompt file changes — the AI-use-log entry is
  added by team policy rather than by the gate;
- **gate-5** is unaffected: the offline suite is not touched.

I verified these three points from the gate implementations, not from the PR description.

---

#### Specification alignment

The deliverable is D6 (project.pdf p. 6–7). Checked against the wording:

- **Names and student numbers** — present in the title block for all three members. *Supplied by the
  team; the handle-to-person mapping is not derivable from the repository and the report says so.*
- **Relative contribution** — **NOT PRESENT.** §10.1 is a blank table with the course formula. This is
  the central open item and the report declares it at the top and in Appendix B.
- **Word count** — 8,951 words, within the 10,000 cap.
- **Pages** — **unverified**; Markdown has no page count and the report says so.
- **Six supervised stages** — §2 requirements, §3 architecture, §4 plan approval, §5–6 build, §7
  verification, §3.4 architecture revision. All six are addressed.
- **Process-quality evidence** — §7.7 covers volatility, defect trends and ambiguity resolution, each
  with a stated calculation and a stated limitation.
- **Co-evolution** — §7.8 gives three cases plus an honest counter-example.
- **Human oversight** — §9 gives three cases from the AI-use log.
- **Reflections** — **NOT WRITTEN.** §11 holds evidence and questions only. Correctly so.

D5 (transcripts) is assessed in `docs/report/Transcript-Compliance.md`: 27 annotated files, 27
interventions with rationales, six stages covered, **but a single author**. The report does not hide
this.

---

#### Factual accuracy

I re-derived the headline figures against `b3e0d93` rather than accepting them:

| Claim in the report | Verified |
|---|---|
| 55 merged pull requests | yes — `gh pr list --state merged` returns 55; 10 closed, 65 total |
| 50 change ids | yes — unique `CHG-xxx` in git log |
| 40 requirements, 21/12/1/6 | yes — parsed from `requirements.yaml` |
| 18 ADRs, 15 accepted, 3 proposed | yes — status lines in `docs/architecture/adr/` |
| 1,672 passed, 1 skipped, 1 deselected | yes — measured on a detached worktree |
| 8 debts closed/mitigated, 2 open, 2 not observed | yes — `debt-register.md` |
| Six probes each reddened their gate | yes — PRs #45, #26, #4, #44, #6, #5 |
| 36 of 48 review memos automated | yes — memo `Reviewer:` lines |
| −22.2 % / −35.6 % / +19.5 % | yes — arithmetic reconciles to 206,694 and 160,833 |
| Compaction threshold 0.8 | yes — `context/assembler.py:32` |

Every claim I could not re-derive carries a marker rather than a number. **The report contains no figure
that I found to be false.**

---

#### Architecture alignment

No module, schema, permission, prompt or gate-name change. `docs/report/` is not imported by the
application or the test suite. The deliverable map in Appendix A points at paths that exist.

---

#### Code and test quality

No code. The working papers were checked for internal consistency: the compliance checklist's **26**
items sum to its own totals (11 satisfied, 7 partial, 5 blocked, 2 unverifiable, 1 missing); the debt
table's 8 + 2 + 2 equals 12; the volatility percentages recompute from 6/40 and 8/40; the transcript
inventory's 1 + 11 + 15 equals the 27 attributed files.

**A correction found during this review:** the checklist's first summary table miscounted (it said 25
items and double-listed A8 while omitting A1 from its count). It was rewritten from the parsed table in
this same PR. Working papers that summarise their own tables must recompute, not restate.

---

#### Operational, security and efficiency metadata

- No secret, token or private key. Scanned the diff for key material and found none.
- **Student numbers appear in `Report.md`, which is in a public repository.** The team supplied them and
  the report states their source. This is a privacy decision the team owns, not a defect the review can
  waive; it is flagged here so it is a recorded choice rather than an oversight.
- All content is English, as the repository contract requires.

---

#### Design of the report itself

I checked the two properties most likely to make a process report misleading:

1. **It does not claim more than it measured.** Output tokens rose (+19.5 %) and the report says so; the
   live comparison and the budget replay are kept separate; the evaluation set is stated as two cases.
2. **It states its own incompleteness.** The status banner, Appendix B and the review memo all name the
   same three blockers. A reader cannot mistake this for a finished submission.

That second property is unusual and it is the reason this PR is approvable as a draft. The report is
honest about what is missing instead of silently omitting it.

---

#### Open items this approval does not cover

Approving this PR **approves the draft as a draft that states its own incompleteness.** It does not
assert that CS5351 D6 is complete:

1. Contribution hours / story points (§10.1).
2. Three student-written reflections (§11).
3. Transcripts from `@AKAScarlett` and `@SY1433`, or an explicit disclosure.
4. Four documentation inconsistencies (§8.1), three of which need a separate governance review.
5. Live branch-protection settings (needs an admin token).
6. The demo video and the 15-page render check.

I also note, as a record, what was **not** done: the contribution table was offered a 34/33/33 split
with work descriptions that do not exist in this repository. Refusing it was correct. A contribution
table describing another project's Qdrant index, NLI layer and citation spans would have been a claim an
assessor could disprove from the git history.

---

#### Tests

None required: documentation-only change; no `src/`, `test/` or `prompts/` file changes.

**Verdict: APPROVE**, for the draft only, with the six open items recorded above.

**Reviewer recorded as:** automated (`github-actions[bot]`). If a human review is also wanted, it should
be added by `@AKAScarlett` or `@SY1433` before merge; it is not required by branch protection but it is
required by the spirit of D6.
