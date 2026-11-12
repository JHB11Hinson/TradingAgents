# Bug diary

**Deliverable:** D4. **Requirement:** `D1-REQ-GOV-010`.
**Owner:** the whole team (whoever diagnoses the bug writes the entry).
**Fields, per the course:** symptom, reproduction, classification, root cause, fix, and **which
invariant gap it exposed**.

An entry is written for a **significant** bug: one that reached a shared branch, broke a gate, cost
more than an hour, or exposed a gap in an invariant. Typos and one-line fixes belong in the pull
request, not here.

**Classification values:** `code`, `test`, `gate`, `process`, `environment`, `documentation`.

---

## BUG-001 — The blueprint pointed at an ADR that did not exist

- **Date:** 2026-10-16
- **Symptom:** `architecture-blueprint.md` said the inherited CI was "replaced by our six blocking
  gates (see ADR-003 / CHG-002)", but `docs/architecture/adr/` contained only ADR-001 and ADR-002.
  A reader following the reference hit a dead end.
- **Reproduction:** `grep -n "ADR-003" architecture-blueprint.md` and
  `ls docs/architecture/adr/` — the first names ADR-003, the second has no such file.
- **Classification:** documentation (reference integrity)
- **Root cause:** the gate work cited a decision record that was planned but never written; the
  reference was added before the artifact existed, and nothing checked references.
- **Fix:** CHG-003 (PR #7) replaced the dangling reference with `docs/code-governance/protection.json`
  and CHG-002, both of which exist.
- **Invariant gap exposed:** no check verifies that a referenced artifact exists. Today the review
  checklist covers it; a link/reference check is a candidate for a later gate.

## BUG-002 — The gate-2 violation probe was inconclusive

- **Date:** 2026-10-30
- **Symptom:** a deliberate-violation pull request was opened to prove `gate-2-static-analysis`
  blocks a style problem. `gh pr checks` showed only `gate-3-schema`, `gate-5-regression` and
  `gate-6-ai-use-log`; **gate-2 never ran**, so the probe proved nothing.
- **Reproduction:** cut a branch from `main` while the gate-2 job exists only on the open CHG-007
  branch, append an unused import to a `src/` file, open the pull request, and read `gh pr checks`.
- **Classification:** process (probe ordering)
- **Root cause:** a check that is not on the base branch cannot run on a pull request based on that
  branch. The manual's order is write the job → merge it → then run the probe; the probe was run
  early.
- **Fix:** the probe was closed and its branch deleted; the experiment must be re-run after CHG-007
  (PR #11) merges and the gate name has appeared on `main`.
- **Invariant gap exposed:** "a gate is not real until its name has appeared on a pull request"
  (`D1-REQ-GOV-003`). A probe that runs before that is itself the gap.

## BUG-003 — Git and `gh` disagree about the environment proxy

- **Date:** 2026-10-30
- **Symptom:** `git push` failed with `GnuTLS recv error (-110)`, while `gh pr create` succeeded.
  With the proxy variables cleared, `git push` hung; with them set, `gh` returned `EOF` from the API.
- **Reproduction:** with `https_proxy=http://192.168.31.216:7890` set,
  `curl -x "$https_proxy" https://github.com` → 200, `curl --noproxy '*' https://github.com` → timeout;
  `curl --noproxy '*' https://api.github.com` → 200. So `github.com` needs the proxy and
  `api.github.com` does not.
- **Classification:** environment
- **Root cause:** the proxy reaches `github.com` but not the API host reliably, and the direct route
  is the reverse; the shell exports one proxy for both.
- **Fix:** run git commands with the proxy and `gh` commands without it
  (`unset http_proxy https_proxy`). Recorded here so the next person does not re-debug it.
- **Invariant gap exposed:** none — environment only. It is recorded because it cost time and would
  otherwise be rediscovered.
