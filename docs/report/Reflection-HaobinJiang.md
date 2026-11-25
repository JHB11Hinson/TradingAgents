# Reflection — JIANG Haobin (60198818)

**Name:** JIANG Haobin **Student number:** 60198818 **GitHub:** `@JHB11Hinson`

I came into this project expecting to rewrite the inherited framework. My first real decision was not
to. Keeping the baseline and adding governance around it was less satisfying, but it forced me to
define what "better" meant: a deterministic authority boundary, a context budget, and gates that fail
the build. I made that call for the wrong reason, though. I wanted a clean architecture, not a
defensible one, and the difference only became obvious once the agent was producing changes faster
than I could review them.

The hardest lesson came from the structured-output decision. My first instruction was to fix the
free-text fallback after a schema failure. The agent did exactly that: it adjusted the fallback and
the prose parsing, and we went through five revisions. Somewhere around the second round I noticed I
was reviewing the solution to a problem I had never stated precisely. The real defect was that the
code could not distinguish "the provider cannot produce structured output" from "the call returned an
invalid decision", and in both cases prose could still become a tradeable rating. I had described a
symptom and the agent had optimised it. The question I should have asked in round one was: which
failure states exist, and which of them is allowed to set the rating? Once I asked it, the design
collapsed into a small table. I now write the failure states before I ask for a fix.

The second mistake was easier to catch and harder to admit. The agent diagnosed an import failure as
a bug that affected every checkout. It sounded plausible, so I nearly wrote it into the
documentation. Re-running the suite in my own tree gave 1626 passing tests. The failure only
reproduced when a second checkout shared one editable install. The correction was small, but it
changed my habit: reproduce a diagnosis before it becomes a published fact.

The gates worked on code and not on prose. Three stale statements in governance documents survived to
the end because none of my checks read a sentence. I also opened 45 of 55 pull requests, which bought
speed and cost the team shared understanding; the review load fell on the two people who were not the
author. If I did it again, I would give each member ownership of one gate and one decision record,
and I would have written the safety requirement as a table of failure states from the start. The
project taught me that supervising an agent is mostly the work of making the problem precise before
the agent makes the solution cheap.
