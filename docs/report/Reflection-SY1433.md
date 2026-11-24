# Reflection Worksheet — `@SY1433`

> **You write this, not the agent.** D6 requires 300–500 words, with your **name and student number**.
> Everything below the line is evidence and questions. Replace the placeholder block with your own
> account. Do not copy the evidence summaries; they are there so your reflection can be specific.

**Name:** WANG Songyan **Student number:** 60847491
**Word target:** 300–500 **Written:** ☐

---

## Part 1 — What your record shows (verify, then reflect — do not quote)

| Area | Evidence |
|---|---|
| Gate-2 promotion | `ci: CHG-021 promote gate-2 to a blocking scoped type check` (PR #27) — the gate reached blocking status under this change |
| Merge-train runbook | `docs: CHG-028 add the merge-train runbook` (PR #33) — written from observed integration friction |
| Team-record correction | `gov: CHG-026 remove the inactive collaborator from the team records` (PR #30) — relevant to the `zihao9462-creator` question |
| ADR hygiene | `docs: CHG-053 renumber the duplicate ADR-014 to ADR-017` (PR #62) — repaired a numbering collision |
| ADR validator | `feat: CHG-055 ADR status and PR reference validator` (PR #65) — the check that later caught ADR-016's wrong citation |
| README evaluator note | `docs: CHG-052 document the evaluator's installed-package trap` (PR #61) |
| Review | 5 GitHub reviews |
| AI-use log | **`docs/ai-use-log/SY1433.yaml` is currently empty** (header only) |

**One thing to fix.** Your AI-use log has no entries although you authored five merged PRs. Completing it
is a separate, small task — and your reflection is a good place to explain, in your own words, what your
role in those changes actually was.

---

## Part 2 — Decisions you could reflect on

### Incident 1 — Promotions without disturbing branch protection

**Evidence:** PR #27 made gate-2 a blocking scoped type check. Gate-2 later grew further (CHG-054) but
**kept its name and its protection context**, so the branch-protection configuration never churned.
**Why it matters:** promoting a gate and growing a gate are different risks; you handled the one that
touches the protection configuration.

### Incident 2 — Duplicate ADR-014, then a validator

**Evidence:** PR #62 renumbered a duplicate ADR-014 to ADR-017. PR #65 then added an automated
**ADR status and PR-reference validator**, which found that ADR-016 cited "PR-3" instead of PR #60.
**Why it matters:** you fixed an instance *and* then built a check for the class of error. That is the
difference between a repair and a process improvement.

### Incident 3 — The merge-train runbook

**Evidence:** `docs/merge-train` runbook added in PR #33 (CHG-028). The repository history shows a long
run of small, sequential PRs, several of which needed re-basing or were closed to avoid conflicting with
a later change.
**Why it matters:** a runbook is a response to *observed* friction, so the reflection can be concrete
about what was actually breaking.

---

## Part 3 — Five questions (answer in your own words)

1. **Merge train.** What specifically was breaking when you wrote the runbook — ordering, conflicts,
   review latency, or branch staleness? Which of those did the runbook actually fix?
2. **Instance versus class.** For the duplicate ADR-014, what made you decide to renumber (a one-off
   fix) and then, separately, to add a validator? Did you decide both at once, or did the validator come
   later, and why?
3. **Promotion risk.** Making a gate blocking is a step that can stop everyone's work. How did you
   decide gate-2 was ready, and what evidence told you it would not produce false failures?
4. **Review as a non-author.** How did reviewing change what you look for when the agent writes code?
   Give one review where you found something the author had not.
5. **Your own evidence gap.** Your AI-use log is empty and you have no session transcript. What *would*
   your log contain if you wrote it now — and what does that tell you about recording your work as you
   go?

---

## Part 4 — Your reflection (300–500 words)

**Your reflection — `@SY1433`**

```
[WRITE HERE — 300–500 words. First person. Include at least one mistake, how you caught it, and what
you changed afterwards. Do not claim anything the evidence contradicts.]
```

**Word count of your text:** ______  **Signed:** ______________________  **Date:** __________
