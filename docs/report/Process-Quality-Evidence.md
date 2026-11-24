# Process-Quality Evidence Summary

**Scope.** D6 (project.pdf p. 6–7) requires the report to "cover process quality evidence (requirement
volatility, defect trends, ambiguity resolution)". This file derives each metric from the repository
and states **how it was calculated**, **where it came from**, and **where the data is too thin to
support a trend**. No percentage is reported that the data cannot carry.

**Repository state:** `origin/main` = `b3e0d93`, 2026-11-25.

---

## 1. Requirement volatility

### 1.1 Method

`docs/req/requirements.yaml` has exactly **six** commits in its history. For each commit the file was
parsed and consecutive versions diffed by `id`, comparing `priority` and `fit_criterion`. Command:

```bash
git log --format="%h %ad %s" --date=short origin/main -- docs/req/requirements.yaml
# then, per commit: git show <sha>:docs/req/requirements.yaml  → parse → diff by id
```

### 1.2 Result — requirement-file history

| # | Commit | Date | Requirements after | Added | Removed | Fields changed |
|---|---|---|---:|---:|---:|---:|
| 1 | `1558988` | 2026-10-06 | 0 | 0 | 0 | 0 |
| 2 | `a21ec80` | 2026-10-06 | 1 | 1 | 0 | 0 |
| 3 | `3106592` | 2026-10-16 | 21 | 20 | 0 | 0 |
| 4 | `384ec1d` | 2026-11-13 | 40 | 19 | 0 | 0 |
| 5 | `888f87b` | 2026-11-16 | 40 | 0 | 0 | 2 |
| 6 | `be2bcfd` | 2026-11-17 | 40 | 0 | 0 | 6 |

### 1.3 Result — the volatility figures

| Metric | Value | Calculation |
|---|---:|---|
| Requirements ever registered | 40 | final count; none was ever deleted |
| Requirements added | 40 | sum of the "Added" column (1 + 20 + 19) |
| Requirements **removed** | **0** | no id present in an earlier version is absent later |
| Requirements **priority-changed** | **6** | the six `must`/`should` → `wont` flips in `be2bcfd` (CHG-032) |
| Requirements **criterion-changed** | **2** | `GOV-010` and `GOV-011` in `888f87b` (CHG-029), path and wording only |
| Final distribution | 21 must / 12 should / 1 could / 6 wont | `yaml.safe_load` |
| **Priority-volatility rate** | **6 / 40 = 15.0 %** | changed priority ÷ ever registered |
| **Content-volatility rate** | **8 / 40 = 20.0 %** | (priority + criterion changes) ÷ ever registered |

The CHG-032 commit is the only substantive priority change; it flipped six low-value requirements to
`wont` **with a written `deferred_reason` each**. So the internal requirement set was stable: 32 of
40 requirements never changed priority after registration.

### 1.4 What the data does and does not support

**Supports:** "of forty registered requirements, six changed priority (all in one recorded decision,
CHG-032) and two had their fit criterion clarified; none was ever deleted." This is a defensible
statement and it is checked arithmetic.

**Does not support:** any claim that volatility was *low over time*, because there are only **six
commits** touching the file and the file was created once and refilled twice. A trend line needs many
more samples. **State the six-commit limitation in the report** rather than drawing a trend.

**Also note (honest):** the requirements went from 1 → 21 → 40 in two large additions, which suggests
the registry was *written in batches* rather than incrementally refined. That is a real process fact
worth stating: it means volatility is concentrated, not smooth.

---

## 2. Defect trends

### 2.1 Method

1. `docs/bug-diary.md`: split on `^## `, read `Classification` and the invariant-gap sentence.
2. Review records: `docs/review-memo/PR-*.md` (48) and the legacy `docs/review-memo.md`, counting
   verdicts.
3. Debt register: `docs/debt-register.md`, per-entry `Status:`.
4. Failed-then-fixed tests: `git log` messages with a `fix:` prefix.

### 2.2 Result — bug diary (5 entries)

| ID | Title | Classification | Invariant gap exposed |
|---|---|---|---|
| BUG-001 | Blueprint pointed at an ADR that did not exist | documentation (reference integrity) | no check that a referenced artifact exists |
| BUG-002 | Gate-2 violation probe was inconclusive | process (probe ordering) | "a gate is not real until its name has appeared on a pull request" |
| BUG-003 | Git and `gh` disagree about the proxy | environment | none — environment only |
| BUG-004 | GitHub Actions stopped running on the fork | environment (platform policy) | pre-flight assumed Actions were running |
| BUG-005 | Run ledger under-counted the request it was capping | code (accounting), safety consequence | `COST-003` said the log reports `≤ budget`, but no code enforced it |

**Classification split:** code 1 · documentation 1 · process 1 · environment 2.
**Bugs that exposed an invariant or requirement gap:** 3 of 5 (BUG-001, 002, 005).

### 2.3 Result — defects found in review

| Source | Records | `APPROVE` | `CHANGES REQUIRED` | Notes |
|---|---:|---:|---:|---|
| Legacy `docs/review-memo.md` | 23 PR entries | 12 | **11** | includes 2 marked `PENDING TEAM RULING` |
| `docs/review-memo/PR-*.md` | 48 files | 48 | 0 | all merged changes passed |
| **Total** | **71 verdicts** | **60** | **11** | |

**Read this carefully.** The 11 `CHANGES REQUIRED` verdicts are all in the **early** memo archive. The
later per-PR memos show zero. That is *not* evidence that later changes were defect-free; it is
evidence that `CHANGES REQUIRED` stopped being recorded once the workflow changed to pre-committed
review text (`bot-review`). **State this limitation** — do not claim the defect rate fell.

### 2.4 Result — fixes and open defects

| Metric | Value | Source |
|---|---:|---|
| Commits with a `fix:` prefix | **33 total, but only 2 are ours** | `git log --format=%s origin/main \| grep -cE "^fix:"` → 33; of these, 31 are inherited upstream commits (e.g. #781, #572, #543). Our tree's own fixes are `#48` (CHG-040) and `a58aa61` |
| Debts closed or mitigated | 8 of 12 | `debt-register.md` |
| Debts "none observed" | 2 | DEBT-007, DEBT-008 |
| Debts **open** at submission | **2** | DEBT-005 (no graph-wiring walkthrough), DEBT-009 (26 modules quarantined from `mypy`) |
| Dangling debt reference | **1** | ADR-006 cites **`DEBT-013`**, which does not exist in the 12-entry register |

**Important caveat on the `fix:` count.** The repository is a fork, so `git log` mixes inherited
upstream history (545 commits total) with ours. **Do not report "33 fix commits"** as a team metric —
31 belong to the upstream project. Only two fix-prefixed commits are ours, and the substantive
defect-fix record lives in `bug-diary.md` and the review verdicts, not in commit prefixes.

### 2.5 What to state, and what not to

**Supports:** "five significant bugs were recorded; three exposed a missing check and each produced a
concrete change (a validator, a probe-ordering rule, an enforced budget)." That is a genuine
defect-trend *narrative*.

**Does not support:** a defect *rate*, a defects-per-PR figure, or "defects fell over time". The diary
is small (5), the review records use two incompatible formats, and the later zero-`CHANGES REQUIRED`
count is an artefact of the workflow change, not a quality improvement.

---

## 3. Ambiguity resolution

### 3.1 Method

1. ADR revision histories: the header carries `Revision: rN` with an `Earlier:` note per round.
2. Review memos: wording `PENDING TEAM RULING`, `ambiguous`, `clarif`.
3. Requirement criterion changes (§1.2 rows 5–6).
4. AI-use log entries typed `redirect` or `correct`.

### 3.2 Result — ADR-006 is the strongest case

`docs/architecture/adr/006-decision-authority-fallback.md` records **r5** with an explicit chain:

- **r4** corrected the §10 repository-state premise, moved the debt id to `DEBT-013`, made the
  §Context quote verbatim, and stated the status-flip sequence.
- **r3** added the four failure identifiers, the T2/T7 test-role split, and the ADR PR file scope.

So a single ADR went through **five revisions**, each with a named reason, before it was accepted and
flipped at the owner's direction. It also carries an explicit **`## Reconsider if`** section with four
written reopen conditions (e.g. "the evaluation set shows that turning free-text decisions into REVIEW
loses material quality … then a stricter structured re-ask deserves its own ADR").

That is exactly the "ambiguity → human decision → documented resolution" pattern D6 asks for.

### 3.3 Result — ambiguity resolved in review

| Evidence | Count | What it shows |
|---|---:|---|
| Reviews marked `PENDING TEAM RULING` | 2 | a decision was escalated rather than guessed |
| `constrain` entries in the AI-use log | 43 | human refusals of a wrong direction |
| `correct` entries | 12 | human corrections of an agent error |
| `redirect` interventions in transcripts | see §3.4 | human redirection of approach |

Session 06 (governance batch) alone records six interventions, including a `redirect` where the agent
claimed more files were "human-only" than the course permits, and the human rejected the blanket claim
after checking the PDF. That is an ambiguity *resolved by going to the source*.

### 3.4 What to state

**Supports:** "ambiguity was usually resolved by escalating it — two review memos are marked PENDING
TEAM RULING, ADR-006 was revised five times with reasons, and a transcript records a human rejecting an
over-broad reading of a course rule after checking the source document." All verifiable.

**Does not support:** counting distinct requirements that were "*ambiguous*" — no field records that.

---

## 4. Cases where artifacts co-evolved (D6 p. 7)

These are the three cases where a change to one artifact forced a change in another, and the change is
recorded:

| Case | Trigger | Co-evolution | Evidence |
|---|---|---|---|
| CHG-029 sharded the append-only logs | a file exceeded GitHub's 1 MB render limit | gate-6's path was taught the new `docs/ai-use-log/<member>.yaml` layout; `GOV-010`/`GOV-011` fit criteria rewritten to match | `888f87b` diff on `requirements.yaml` |
| CHG-032 deferred six requirements | cost/benefit at the end of the build | six `wont` entries gained `deferred_reason`; the trace matrix and report narrative follow | `be2bcfd` |
| CHG-055 added an ADR validator | ADR-016 cited the wrong PR | the citation was corrected **and** a check now prevents the class of error | ADR-016 header; `docs/architecture/adr/017-*.md` |

**Honest counter-example** (and it is a real one): three documentation inconsistencies were *not* kept
co-evolving — `AGENTS.md`'s test baseline, `verification-constraints.md`'s `TERM-001` row, and
`README.md`'s gate-1 state. The report should present the three successes **and** the three misses, or
the "co-evolution" claim is one-sided.

---

## 5. Summary table the report can quote

| Metric | Value | Method | Limitation |
|---|---:|---|---|
| Requirements ever registered | 40 | `requirements.yaml` final parse | — |
| Never deleted | 40 (0 removed) | id diff across 6 commits | — |
| Priority changed | 6 (15.0 %) | id diff, `priority` field | one batch decision (CHG-032) |
| Fit criterion clarified | 2 | id diff, `fit_criterion` field | — |
| Bug diary entries | 5 | `^## ` split | small sample |
| Bugs exposing a gap | 3 | manual read of invariant-gap sentence | — |
| Review verdicts | 71 (60 approve / 11 changes required) | memo count | formats differ; later zero is a workflow artefact |
| Debts resolved / open | 8 → 2 open | `debt-register.md` | 2 "none observed" are not debt |
| ADR-006 revisions | 5 (r1→r5) | ADR header | one ADR, not a rate |
| Dangling references | 1 (`DEBT-013`) | grep | — |

**Do not convert any of these into a percentage that the data cannot carry.** The three honest
qualifiers — six commits, five bugs, two memo formats — belong in the report next to the numbers.
