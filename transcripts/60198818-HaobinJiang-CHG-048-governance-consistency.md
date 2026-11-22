# Agent session record - CHG-048 governance consistency

- Date: 2026-11-22
- Harness: OpenCode (DeepSeek V4.1 Flash)
- Owner: 60198818 Haobin Jiang (`@JHB11Hinson`)
- Branch: `gov/CHG-048-governance-consistency`
- Scope: `D1-REQ-GOV-006`, `D1-REQ-GOV-008`, `D1-REQ-GOV-012`; one new `src/` package and three
  offline checks

> Annotated session record. The human turn is verbatim; tool actions are summarised with the
> command and the result that mattered. This is not a verbatim export.

## Human request (verbatim)

```text
GOV-006：加一个离线一致性测试，解析 permissions.jsonc、permission-model.md、AGENTS.md §13，任何一处缺路径即失败。
GOV-008：加 requirements/invariants/trace-matrix 的缺失条目检查；顺手把 INV-02/03 改成 implemented。
GOV-012：先做 loader + prompt_v1.0.yaml + checksum 测试，再按 agent 分批迁移，避免一次性改动过大。 做吧，Bot Review
```

## Agent findings

- The inherited baseline was green before any change: `pytest -q` -> 1543 passed, 1 skipped,
  1 deselected, 99 subtests passed.
- The three permission sources already listed the same read/write paths, but the only check was a
  review step in `permission-model.md` section 9; nothing failed on a drift.
- The registry, trace matrix and invariant register were complete, but `INV-02` and `INV-03` were
  still marked **planned** in the register while their detail blocks said **Implemented (CHG-033)**.
  The trace matrix also named generic evidence for the two context invariants.
- `prompts/` was empty. Runtime prompts still lived in `src/tradingagents/agents/**`, so there was no
  versioned baseline and no checksum to detect an in-place edit.

## Decisions

- Add three offline checks: `test_permission_consistency.py` (three-way read/write set equality and
  default deny), `test_governance_registry.py` (missing requirement, invariant, trace row, required
  invariant field, register/detail status and must-status row) and `test_prompt_versioning.py`
  (loader, entry checksum, file checksum index, version resolution and tamper negatives).
- Keep the GOV-012 step deliberately small: build the loader and `prompt_v1.0.yaml` baseline for the
  five analyst prompt fragments, then migrate agents in batches. A later batch adds a new version
  file; it does not edit v1.0.
- Correct `INV-02`/`INV-03` to **implemented** and name the context tests in the trace matrix. Update
  the verification status table, `DEBT-001` and the structural module table in the same change.
- Commit the tests before the implementation and the review record before the first `src/` commit,
  per gate-1. The agent does not merge.

## Verification

- `pytest -q` -> 1577 passed, 1 skipped, 1 deselected, 99 subtests passed in 15.11 s.
- `ruff check` on the new `src/` package and the three tests -> all checks passed.
- `mypy --follow-imports=silent` on the new package -> success, no issues in 2 source files.
- `check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml` -> validation
  done.
- `python -m eval.run ... --budget 40000` -> verdict pass (2 cases, 0 failed; token ratio 0.270625,
  capped ratio 0.927049, review 0.0, structured 1.0).

## Pull request

Opened as `gov/CHG-048-governance-consistency` after the tests and this record. The review record is
`docs/review-memo/PR-56.md`; the bot-review text follows on the final head. The agent does not merge.
