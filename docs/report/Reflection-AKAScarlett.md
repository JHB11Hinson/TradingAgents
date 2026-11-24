# Reflection Worksheet — `@AKAScarlett`

> **You write this, not the agent.** D6 requires 300–500 words, with your **name and student number**.
> Everything below the line is evidence and questions. Replace the placeholder block with your own
> account. Do not copy the evidence summaries; they are there so your reflection can be specific.

**Name:** ZHONG Junqiong **Student number:** 60907770
**Word target:** 300–500 **Written:** ☐

---

## Part 1 — What your record shows (verify, then reflect — do not quote)

| Area | Evidence |
|---|---|
| Test-approval gate | Designed and implemented `gate-1-test-approval` (CHG-030, PR #35) |
| Type-check ratchet | The shrink-only mypy quarantine test (CHG-051, PR #60) — the test that fails if the quarantine list grows |
| Safety and dependency checks | RED tests for the gate-2 safety-path guard and the dependency-declaration check (CHG-054, PR #63) |
| Memory correctness | ADR-014, explicit memory source attribution (MEM-003) — stops future data leaking into a past run |
| Review load | **4 review memos and 15 GitHub reviews — the most of any human on the team** |
| AI-use log | 4 entries in `docs/ai-use-log/AKAScarlett.yaml` |

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
2. **RED tests for gate machinery.** Writing a failing test for a check you had not built yet forces a
   decision about the check's contract. What did you learn about the safety guard from its test before
   you had the guard?
3. **Memory and time.** ADR-014 protects against future data reaching a past run. Was that obvious from
   the requirement, or did you have to interpret an ambiguous statement to get there? Say which.
4. **The review you would redo.** Of your reviews, which one did you approve too readily, or labour over
   too long? What would you look for first next time?
5. **Human versus automated review.** You reviewed both ways on this project. What did the automated
   reviewer miss that you would have caught, or vice versa? Give one example.

---

## Part 4 — Your reflection (300–500 words)

**Your reflection — `@AKAScarlett`**

```
[WRITE HERE — 300–500 words. First person. Include at least one mistake, how you caught it, and what
you changed afterwards. Do not claim anything the evidence contradicts.]
```

**Word count of your text:** ______  **Signed:** ______________________  **Date:** __________
