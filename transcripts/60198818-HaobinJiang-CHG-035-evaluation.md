# CHG-035 — evaluation harness and the honest run ledger

**Member:** 60198818 HaobinJiang (@JHB11Hinson) · **Agent:** DeepSeek Harness · **Date:** 2026-11-20
**Scope:** `D1-REQ-EVAL-001`, `D1-REQ-COST-001`, `D1-REQ-COST-003`

An annotated session record: human turns are quoted verbatim, tool calls and their results are
summarised, and each human intervention says what it changed. This is the session that discovered
the ledger under-count and chose to fix it before building the evaluation harness.

---

## 1. The instruction (human turn 1, verbatim)

> .opencode 中有 git-gh-rules，仓库内也有 AGENTS.md 等规范和文档，两份手册属于参考，如果发生冲突，以
> manual 文件夹中的课程 Project PDF 内的内容为裁定参考，并且给出结论向我问询
>
> 现在，查看已完成的 PR 情况，继续实现需求，以组员2（以转移至管理员）的为优先，提交 PR 后直接使用
> Bot Review 审批

**Annotation — intervention type: scope + precedence + approval channel.** The human set the
document precedence (course Project PDF first, then the repository contract, then the two manuals),
asked for conflicts to be reported with a conclusion, scoped the work to member 2's area (context and
cost, transferred to the admin when `@zihao9462-creator` left), and authorised the documented
`bot-review` path for the approval.

## 2. Reconnaissance (agent)

- `git log` / `gh pr list`: `#38` CHG-033 (assembler + budget) and `#39` CHG-034 (telemetry) are
  merged; `#39` used the bot for its non-author review.
- `docs/req/requirements.yaml` + the discussion draft §6: member 2 owned `CTX-001/002/003` and
  `COST-001/003`; the CTX items and `COST-003` landed in CHG-033. The only remaining `must` is
  **COST-001**, whose fit criterion is `python -m eval.run` over `eval/fixed-set.json`, and `eval/`
  is empty (`DEBT-003`).
- Read the two course PDFs, both manuals, `AGENTS.md`, `.opencode/git-gh-rules/`, `gate1_check.py`,
  `bot-review.yml` and the review-memo conventions.
- Built an offline full-graph prototype (scripted model, stubbed vendors) to measure the run ledger.

**Tool result that matters:** the prototype reported `context_usage.total_tokens = 43,616`, while the
same run's full request was 58,359 tokens.

## 3. The surprise and the stop (agent → human)

The agent found that `assemble_context` records only the system-prompt estimate on an uncompacted
call (`src/tradingagents/context/assembler.py:290`), while the history layer is budgeted but not
counted. With a one-line honest counter, the same run under the default `context_budget_tokens =
50_000` compacted once and the Portfolio Manager returned `REVIEW` without a model call.

**Annotation — intervention type: stop for a design decision.** The change would alter CHG-033's
merged behaviour and trade the decision for the cap, which collides with `QUAL-001`. The agent did
not choose; it reported the measurement, the conflict table (bot approval vs human supervision,
per-PR records vs the PDF tree, the three missing D2 artifacts, the offline gate-4, the transcript
count) and four options.

## 4. The decision (human turn 2, verbatim)

> 中文重新问我

**Annotation — intervention type: redirect (language).** The answer was re-asked in Chinese.

## 5. The decision (human turn 3, verbatim)

> A. 先修账本 + 给决策预留预算，再做评测（推荐）

**Annotation — intervention type: approve a behaviour change.** Option A was chosen: make the ledger
count the whole request, withhold a decision reserve from ordinary calls, keep the default 50,000 cap,
and only then build the evaluation harness. This is the human approval for the change to CHG-033's
merged behaviour.

## 6. Build (agent)

1. `RunBudget.reserve` + `available(use_reserve=False)`; `assemble_context(..., use_reserve=...)`
   returns `request_tokens` (assembled text + non-rendered layers) and records **that**.
2. `context_decision_reserve_tokens` (default 2,500) in `DEFAULT_CONFIG`, its `_ENV_OVERRIDES` row
   and `run_settings`; the Portfolio Manager passes `use_reserve=True`.
3. `src/tradingagents/evaluation/` — cases, baseline, metrics, thresholds, report; strict loaders.
4. `eval/` — `python -m eval.run` CLI, the deterministic replay backend, the fixed set, the
   thresholds and the recorded baseline.
5. Six new test modules (loaders and their negative cases, aggregation, the CLI exit codes, the
   ledger and the reserve).

**Tool result:** `pytest -q` → 1389 passed, 1 skipped, 1 deselected (was 1348 passed at `main`);
`python -m eval.run` → 2 cases, `total_tokens_ratio 0.374`, `review_rate 0`, exit 0.

## 7. Review

The test contract is `docs/review-memo/PR-41.md` (test approval before the first `src/` commit). The
non-author approval is the automated `github-actions[bot]` review from
`docs/review-memo/PR-41-review.md`, requested with the `bot-review` label — the channel the human
authorised in turn 1. The record names the reviewer as automated.

**Annotation — intervention type: constrain.** The human's earlier instruction that the agent never
merges still holds: the PR is left open for the author to merge after the review lands.
