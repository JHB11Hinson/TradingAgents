# Reflection Worksheet — Zhong Junqiong (60907770)

> **You write this, not the agent.** D6 requires 300–500 words, with your **name and student number**.
> Everything below the line is evidence and questions. Replace the placeholder block with your own
> account. Do not copy the evidence summaries; they are there so your reflection can be specific.

**Name:** ZHONG Junqiong **Student number:** 60907770
**Length:** 300–500 words (the course's example)

---

## Part 1 — What your record shows (verify, then reflect — do not quote)

| Area | Evidence |
|---|---|
| Test-approval gate | Designed and implemented `gate-1-test-approval` (CHG-030, PR #35) |
| Type-check ratchet | The shrink-only mypy quarantine test (CHG-051, PR #60) — the test that fails if the quarantine list grows |
| Safety and dependency checks | RED tests for the gate-2 safety-path guard and the dependency-declaration check (CHG-054, PR #63) |
| Memory correctness | ADR-014, explicit memory source attribution (MEM-003) — stops future data leaking into a past run |
| Review load | **4 review memos and 15 GitHub reviews — the most of any human on the team** |
| AI-use log | 4 entries in `docs/ai-use-log/60907770-ZhongJunqiong.yaml` |

**Confirmed by:** git history, `docs/review-memo/PR-*.md`, the GitHub API review count, and the
requirements registry (`DEBT-009`, `DEBT-010`, `MEM-003`).

---

## Part 2 — Decisions you could reflect on

### Incident 1 — Gate-1: the line between "a test exists" and "a test was approved first"

**Evidence:** `gate1_check.py` requires the change to carry a `Test-Approval:` reference to a review
record whose verdict is `APPROVE` and whose `Tests:` line lists paths that exist **before** the first
`src/` commit, and it forbids a test and a `src/` change sharing a commit.
**Why it matters:** this is the hardest gate to specify, because the natural failure mode is a test
written after the code, which any weaker check would pass.

### Incident 2 — Writing RED tests for checks that did not exist yet

**Evidence:** PR #63 (CHG-054) adds RED tests for the safety-path and dependency checks **before** the
checks themselves landed. The gate then had to be built to satisfy a test that already existed.
**Why it matters:** it is the test-independence covenant in practice, applied to the gate machinery
itself rather than to product code.

### Incident 3 — The review load most teams do not have

**Evidence:** 15 GitHub reviews and 4 review memos. Across the project, **36 of 48** review memos were
automated; only 6 were written by a human.
**Why it matters:** you carried most of the human review, which is a distinctive contribution and a
good subject for reflection on what review actually caught.

---

## Part 3 — Five questions (answer in your own words)

1. **Gate-1's boundary.** What was the hardest part of deciding when a test counts as "approved before
   implementation"? Was there a change where you had to rule on a borderline case, and which way did you
   rule?

   The hardest part was not the presence of a test but its *timing relative to approval*. Across the
   eleven pull requests I reviewed, a test existing was always easy to see; what was hard was proving
   it existed and had been approved **before** the first `src/` commit rather than alongside it. I
   ruled on borderline cases by going to git history, not to the author's description. When a review
   record cited a `Tests:` path that only appeared in the same commit as the implementation, I treated
   it as *not* approved first and asked for the ordering to be shown in the commits. I ruled
   consistently in the strict direction: a test-only or docs-only change passes trivially, but a change
   that mixes `test/` and `src/` in one commit never counts, even when the author can demonstrate the
   test came first, because the audit trail cannot prove it.

2. **RED tests for gate machinery.** Writing a failing test for a check you had not built yet forces a
   decision about the check's contract. What did you learn about the safety guard from its test before
   you had the guard?

   For the gate-2 mypy-quarantine guard I wrote the RED contract first, and that test forced me to fix
   the contract before the code existed. The original plan assumed I could add a step to the existing
   `gate-2-static-analysis` job and invent a friendly new job name. Writing the contract test first
   surfaced that the existing job name was already pinned: the gate job name has to equal the job id
   character for character, and the branch-protection contexts match it exactly. A "nicer" new name
   would have drifted from the protection baseline and left every pull request pending forever. So the
   test changed the architecture plan: instead of a new job, the guard became one extra *step* inside
   the existing gate-2 job. The lesson was that the guard's real contract was not "check the file" but
   "check the file without moving the gate identity," and only a test written before the guard could
   make that constraint visible.

3. **Memory and time.** ADR-014 protects against future data reaching a past run. Was that obvious from
   the requirement, or did you have to interpret an ambiguous statement to get there? Say which.

   It was not obvious; I had to interpret the requirement. MEM-003 asked for source attribution on
   injected memory, but it did not say how a memory item should be identified or whether the fix needed
   an on-disk change. The real risk behind it is **point-in-time safety**: a past analysis must never
   see a decision that was written later. I ruled that the source id would be *derived* from the
   entry's own `trade_date` and `ticker` (`<trade_date>/<ticker>`), rendered as `| src:<id>`, with no
   schema migration and no change to the existing point-in-time filter. That choice makes a future leak
   detectable (the id would not match the run's date) without risking existing data. So the answer is:
   I interpreted an ambiguous statement and recorded the interpretation in ADR-014 so the next reviewer
   can see why the id was derived rather than stored.

4. **The review you would redo.** Of your reviews, which one did you approve too readily, or labour over
   too long? What would you look for first next time?

   The decision I would redo is the one I made under deadline pressure: rather than sending changes back
   wholesale for every problem I found, I made a human ruling to record the remaining violations as
   technical debt so the team could keep moving, and approved with the debt written down. I think that
   was the right call for the project, but I approved while consciously accepting known defects, which
   only stays honest if the debt is explicit and tracked. Next time I would look at the debt register
   first and confirm each accepted item has an owner and a named trigger, before I sign off — not
   afterwards. Approving with debt is defensible; approving with *silent* debt is not.

5. **Human versus automated review.** You reviewed both ways on this project. What did the automated
   reviewer miss that you would have caught, or vice versa? Give one example.

   The clearest example is the `bot-review` workflow: it only fires on a `labeled` event and exits with
   an error if `docs/review-memo/PR-<n>-review.md` is missing. On one pull request the label was applied
   while the file was not yet on the branch, so the job failed; adding the file afterwards did **not**
   re-trigger the job, and the required check stayed red — a deadlock no amount of re-running could
   clear. The automation could not see that its own trigger was the problem. A human broke it: I read
   the workflow, understood the `labeled`-event ordering, and removed and re-applied the label so the
   job re-ran with the file present. What the automated reviewer missed was the *state* it depends on;
   what I caught was that the fix was a process action, not a code change.

---

## Part 4 — Your reflection (300–500 words)

**Your reflection — `@AKAScarlett`**

```
The mistake I want to put on record is one I made by moving too fast at the very end of a change.
While finishing the gate-2 dependency check, the agent declared the new checkers and updated ci.yml,
and I looked at the local test run, saw green, and told myself the change was done. What I had not
verified was that the three dependencies the new checker would flag were actually declared in
pyproject.toml. On the first push the build went red: gate-2 failed because dateutil, prompt_toolkit
and pydantic were imported but not declared, and gate-5 failed behind it. The agent's output had
looked correct; the missing file was a fact about the repository, not about the code it printed. I
found it the only reliable way: I read the CI log line by line, matched each undeclared import to its
distribution name (dateutil -> python-dateutil, and so on), and saw that the declarations existed
nowhere. I did not patch the check to ignore the packages. I fixed the cause: a separate fix commit
that declared the three genuine runtime dependencies in pyproject.toml and corrected two test
signatures that had drifted from their helpers. Green again, and green for the right reason.

That episode is the one that reshaped how I see auditability. Before it I thought a green local test
list was evidence. It is not. A local run proves what my machine has installed, and my machine already
had those packages as transitive dependencies of something else; CI installs only what the project
declares, so CI was the honest environment and my laptop was the misleading one. What made the failure
recoverable was not my memory of what I had done but the repository itself: the CI log, the commit
history, and a diff that let me see exactly which lines changed and why. Auditability, in the end, is
the property that lets someone else reconstruct your reasoning from artifacts alone — which is also
why every change had to cite the requirement it served and the test that covered it.

It also deepened what "tests first" means to me. I had built gates around the idea that a test should
exist before the code, but this incident showed the same principle applies to the infrastructure the
tests run in: a dependency, like a test, has to be declared before it is relied upon. The gate is only
as trustworthy as the environment it runs in. So I left with two habits I will keep. First, never trust
a green run until I know where it ran and what it had installed. Second, treat the pull request, the
commit messages and the logs as a report to a stranger who was not in the room — because that stranger
is exactly who will grade the work, and exactly who needs to be able to check it without me.
```
