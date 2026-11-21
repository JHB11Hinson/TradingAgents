# CHG-040 — DEBT-012 budget exhaustion degrades to REVIEW

**Member:** 60198818 HaobinJiang (@JHB11Hinson) · **Agent:** DeepSeek Harness · **Date:** 2026-11-21
**Scope:** `D1-REQ-COST-003`, `D1-REQ-TERM-001`, `DEBT-012`

An annotated session record: human turns are quoted verbatim, tool calls and results are summarised,
and each intervention says what it changed.

---

## 1. Scope and process (human turn 1, verbatim, abridged to the operative block)

> 继续 TradingAgents 仓库的 PR B（DEBT-012），使用 native（inline）方式执行，非作者审查走 bot-review。
> Agent 不批准、不合并。
>
> ## 范围
> 只做 DEBT-012：预算耗尽时，所有入口返回确定性 `REVIEW`，并设置
> `termination_reason="budget_exhausted"`。
> - 入口：`propagate`、`_run_graph(debug=True)`、`stream_run`、`src/cli/run.py`。
> - 写 state log；仅当最终是 `REVIEW` 非决策时跳过 memory log；保留 checkpoint。
> - PM 已有 catch 保留，并补 `termination_reason`。
> - 新 ADR-008；更新 runtime-policy-catalog、invariants INV-03、trace-matrix、debt-register。
> - **不要**碰 PR C/TERM-001，也不要修 PR A 的 deferred minors。
>
> ## 执行方式
> - 按计划 Task B1 → B4 逐项执行，native 模式，不派 subagent。
> - 分支：`fix/CHG-040-debt-012-budget-review`，从最新 `main` 开。
> - 测试先行…
> - 测试提交里**不要**写 `Test-Approval: PR-<n>` 占位；把
>   `Test-Approval: docs/review-memo/PR-<n>.md` 只放进 PR body。
> - test-only commit 后：创建 `docs/review-memo/PR-<n>.md` 和 `PR-<n>-review.md`，
>   推送、加 `bot-review`，等到 `github-actions[bot]` APPROVED 后再写 `src/`。
> - 实现按计划拆成独立 `src/` commit；test/ 和 src/ 不能同一个 commit。
> - **不要**自己 merge。

**Annotation — intervention type: scope + constrain.** The human fixed the batch to DEBT-012, named
the four entry points, the logging and checkpoint rules, and the four documents plus ADR-008. PR C
(TERM-001 detectors) and PR A's deferred minors were explicitly excluded. The human also fixed the
review channel (`bot-review`), the commit trailer rule and the no-merge rule.

## 2. Pre-flight

- PR #47 (DEBT-011) was merged at `2026-11-21T07:31:31Z`; `main` was clean and in sync at `f76a7dd`.
- Baseline `.venv/bin/pytest -q` → 1416 passed, 1 skipped, 1 deselected.
- Branch `fix/CHG-040-debt-012-budget-review` created from that head.

## 3. Tests first

- Created `test/offline/test_budget_degradation.py` and extended the existing PM budget test in
  `test/offline/test_token_budget.py`.
- The first run failed for the intended reasons: no `termination_reason` field, no graph handler,
  and the CLI cleared the checkpoint for a REVIEW. 11 failed, 12 passed (the passing ones are
  deliberate regression fences).
- Tests-only commit `c556c07`; the review record `5fa6690` was pushed and the `bot-review` label
  produced an APPROVE from `github-actions` on PR #48 before any `src/` commit.

## 4. What the implementation changed

- `src/tradingagents/agents/state.py`: `AgentState.termination_reason`.
- `src/tradingagents/graph/propagation.py`: initial `termination_reason = ""`.
- `src/tradingagents/graph/trading_graph.py`: `_budget_exhausted_state`, the catch on the normal and
  debug paths, the catch in `stream_run`, the state full-state memory for a resume, the memory skip
  in `record_decision`, the conditional checkpoint clear, telemetry `degraded`, and the reason in
  `_log_state`.
- `src/tradingagents/agents/managers/portfolio_manager.py`: the PM catch sets the same reason.
- `src/cli/run.py`: the conditional checkpoint clear and a budget-specific REVIEW message.
- `docs/architecture/adr/008-budget-exhaustion-review.md`: the decision record.
- `docs/architecture/runtime-policy-catalog.md`, `docs/architecture/invariants.md` (INV-03),
  `docs/architecture/trace-matrix.md`, `docs/debt-register.md`: the shipped policy.

## 5. Evidence

- Tests-only head `c556c07`: 11 failed, 12 passed, red for the intended missing handler/field.
- After the implementation: `pytest -q test/offline/test_budget_degradation.py
  test/offline/test_token_budget.py` → 24 passed.
- Real one-token run (no patched exception): `REVIEW` with `budget_exhausted`, before any model call.
- Full suite, `ruff` and the non-quarantined `mypy` modules: green (see PR body / review record).
- Bot approval: PR #48, `github-actions` APPROVED on the tests-only head, then re-requested for the
  final head.

## 6. Boundaries kept

- The Portfolio Manager catch is unchanged in behaviour; it gains the reason field only.
- `RuntimeError` and any non-budget exception still propagate.
- PR C / TERM-001 detectors are untouched; PR A's deferred minors are untouched.
- The agent does not approve or merge.
