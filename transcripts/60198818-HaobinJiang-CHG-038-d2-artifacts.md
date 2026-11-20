# CHG-038 — the six D2 architecture artifacts

**Member:** 60198818 HaobinJiang (@JHB11Hinson) · **Agent:** DeepSeek Harness · **Date:** 2026-11-20
**Scope:** `D1-REQ-GOV-009` (D2.5, D2.7, D2.8, and the optional D2.9–D2.11), `D1-REQ-GOV-003`
(the gate-4 probe evidence)

An annotated session record: human turns are quoted verbatim and tool results summarised.

---

## 1. The instruction (human turn, verbatim)

> 把 python -m eval.run 接成 gate-4 并加入分支保护 contexts 补齐D2的三个工件，按照规范来（Bot Review我授权给你）

**Annotation — intervention type: approve + authorize.** The same instruction covered the gate-4
work (CHG-037) and the D2 artifacts. The agent split it into two changes because the branch prefixes
and the reviewers differ (`ci/` vs `arch/`), and because the gate had to land before its probe.

## 2. Discovery (agent)

- The blueprint's known-gaps table named three missing artifacts: memory design, runtime policy
  catalog, evaluation table.
- The registry's `GOV-009` lists **six**: the three above plus `evaluation-logbook.md`, `risk-list.md`
  and `option-ledger.md` (the course marks the last three optional). Filling only three would leave
  the registry's own fit criterion unmet, so all six are written; the optional ones say they are
  optional.
- `docs/code-governance/protection.json` and the live branch protection now carry six contexts; the
  gate-4 probe (PR #44) failed the gate as designed, and the gate-1 probe (PR #45) failed with
  "no Test-Approval: trailer" (gate-6 also failed on the same src change). Together with the earlier
  gate-2/#12, gate-3/#4, gate-5/#6 and gate-6/#5 probes, every gate has now been red once.

## 3. Build (agent)

1. `test/offline/test_d2_artifacts.py` first: every artifact the registry names exists and is
   non-empty, every `src/...` module the blueprint names exists, and the optional artifacts say so.
2. `docs/architecture/memory-design.md` (D2.5): stores, layers, write/retrieval policy, ownership,
   retention, privacy, degradation, versioning.
3. `docs/architecture/runtime-policy-catalog.md` (D2.7): data, model output, budget, observability,
   state and configuration paths, with the module that implements each.
4. `docs/architecture/evaluation-table.md` (D2.8): seven decisions, five criteria, scores and reopen
   conditions.
5. `evaluation-logbook.md`, `risk-list.md`, `option-ledger.md` (D2.9–D2.11, optional).
6. The blueprint's gap table, the trace matrix's `GOV-009` row and the `AGENTS.md` reading order now
   point at the artifacts.

**Tool result:** the 13 artifact tests pass; `pytest -q` stays green; no `src/` change.

## 4. Review

The non-author approval is the automated `github-actions[bot]` review, requested with the
`bot-review` label. The review checks each artifact against the course's D2 requirement and against
the code it describes, and records the gate-4 probe evidence.
