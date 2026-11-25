# Reflection Worksheet — `@JHB11Hinson`

> **You write this, not the agent.** D6 requires 300–500 words, with your **name and student number**.
> Everything below the line is evidence and questions. Replace the placeholder block with your own
> account. Do not copy the evidence summaries; they are there so your reflection can be specific.

**Name:** JIANG Haobin **Student number:** 60198818
**Word target:** 300–500 **Written:** ☐

---

## Part 1 — What your record shows (verify, then reflect — do not quote)

These are facts derived from the repository. Check them against your memory; correct anything that is
wrong before it goes into the report.

| Area | Evidence |
|---|---|
| Project frame | Adopted the inherited baseline (ADR-001), `src/` layout (ADR-002), authority boundary (ADR-003) |
| Context and cost | ADR-004 layered context with a budget; ADR-005 telemetry that never fails a run; 28 AI-use-log entries in `docs/ai-use-log/HaobinJiang.yaml` |
| Gates | Six gates in `.github/workflows/ci.yml`; gate-2 grew in three stages (lint → mypy quarantine → safety/deps checks) |
| Verification | Fixed evaluation set, `eval/thresholds.yaml`, gate-4 |
| Transcripts | 11 annotated sessions, 27 recorded interventions, all six D5 stages covered |
| Review | 2 review memos; 4 GitHub reviews; 45 of 55 merged PRs opened by this account |
| Correction examples | Rejected an agent return-shape change (ADR-006); corrected a false environment-bug diagnosis; corrected an unsupported-code description |

**An apparent inconsistency you may want to address:** you were simultaneously the dominant author
(45 PRs) and the person who built the gates and review protocol. That concentration is itself a
process-quality finding.

---

## Part 2 — Decisions you could reflect on

### Incident 1 — The contract-shape rejection (ADR-006)

**Evidence:** ADR-006 went through **five revisions (r1 → r5)**; the `Earlier:` note records what each
round changed. The ADR states the return shape stayed fixed and the counters were observed through the
existing mock entry points.
**Why it matters:** this is the clearest case of a human protecting a frozen interface against a small
convenience change.

### Incident 2 — The environment-bug misdiagnosis

**Evidence:** `docs/ai-use-log/HaobinJiang.yaml` records a `correct` entry; `README.md` (CHG-052)
documents the installed-package trap. The agent's claimed "affects every checkout" was narrowed to one
stale editable install after re-testing.
**Why it matters:** it shows the difference between accepting a plausible diagnosis and reproducing it.

### Incident 3 — The gates caught code, not prose

**Evidence:** three documentation inconsistencies are still open at `b3e0d93` (`AGENTS.md` stale test
baseline, `verification-constraints.md` `TERM-001` row, `README.md` gate-1 state). Compare with
BUG-001, BUG-002 and BUG-005, each of which is a *checkable* gap that became a check.
**Why it matters:** it names the limit of your own gate design.

---

## Part 3 — Five questions (answer in your own words)

1. **Direction-setting.** Which single human intervention changed where this project was going, and
   what would the project have looked like without it? Be specific about the alternative you rejected.
2. **Plan review.** ADR-006 needed five rounds. Which round was the one where you realised the agent
   had misunderstood the *problem* rather than the solution — and what question would have caught it in
   round one?
3. **Concentration of work.** You opened 45 of 55 merged PRs. Did that produce a better project or a
   less resilient team? What would you change about how you distributed the work?
4. **Gates versus prose.** The gates caught code defects, but nothing caught a stale number in a
   governance document. Why do you think you did not attempt to guard the prose, and would you now?
5. **Requirements timing.** 40 requirements were registered in two large batches (21, then 19), not
   incrementally. Looking back, did that batching help (coherent design) or hurt (late discovery)? Which
   requirement would you have written differently?

---

## Part 4 — Your reflection (300–500 words)

**Your reflection — `@JHB11Hinson`**

```
[WRITE HERE — 300–500 words. First person. Include at least one mistake, how you caught it, and what
you changed afterwards. Do not claim anything the evidence contradicts.]
```

**Word count of your text:** ______  **Signed:** ______________________  **Date:** __________
