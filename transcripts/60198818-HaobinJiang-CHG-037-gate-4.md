# CHG-037 — bring `gate-4-semantic-eval` online

**Member:** 60198818 HaobinJiang (@JHB11Hinson) · **Agent:** DeepSeek Harness · **Date:** 2026-11-20
**Scope:** `D1-REQ-GOV-003` (six blocking gates), `D1-REQ-EVAL-001`

An annotated session record: human turns are quoted verbatim and tool results summarised.

---

## 1. The instruction (human turn, verbatim)

> 把 python -m eval.run 接成 gate-4 并加入分支保护 contexts 补齐D2的三个工件，按照规范来（Bot Review我授权给你）

**Annotation — intervention type: approve + authorize.** The human authorized the CI job, the live
branch-protection change (an administrator operation the agent may not perform on its own), the three
missing D2 artifacts and the automated non-author review.

## 2. Discovery (agent)

- `.github/workflows/ci.yml` defines five jobs; `gate-4-semantic-eval` is absent.
- `docs/code-governance/protection.json` lists the same five contexts.
- `README.md` §6, `AGENTS.md` §9/§10, `architecture-blueprint.md` §10 and
  `docs/code-governance/verification-constraints.md` all say gate-4 is planned.
- `src/tradingagents/evaluation/thresholds.py` imports `yaml`, but `pyyaml` is not declared in
  `pyproject.toml`; it arrives transitively through `langchain-core` (debt category 4: hidden
  dependency). The gate would work today and break silently if that transitive edge disappeared.

## 3. Build (agent)

1. `test/offline/test_gate_contract.py` first: the workflow and protection contexts must be exactly
   the six gate names, gate-4 must run `python -m eval.run` on the shipped set and thresholds, the
   YAML dependency must be declared, and the admin rules (no force push, no deletion, stale-review
   dismissal) must stay.
2. `gate-4-semantic-eval` job: `pip install -e .` then `python -m eval.run --set
   eval/fixed-set.json --thresholds eval/thresholds.yaml`; the command's exit code is the job's.
3. `protection.json` gains the context (numeric order); `pyproject.toml` declares `pyyaml>=6.0`.
4. Docs: `AGENTS.md` §9/§10, `README.md` §6, the blueprint's known-gaps table, the trace matrix,
   `verification-constraints.md`, `ADR-007`, `DEBT-003`.

**Tool result:** the five contract tests are red before the change and green after; `pytest -q` stays
green; `ruff check src` clean (no `src/` change).

## 4. Review and branch protection

The non-author approval is the automated `github-actions[bot]` review, requested with the
`bot-review` label. After the merge, the live branch protection is updated with the six contexts
(administrator operation, authorized in turn 1) and read back with `gh api`.
