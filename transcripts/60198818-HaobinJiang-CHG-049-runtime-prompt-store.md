# DeepSeek Harness session record — CHG-049 runtime prompt store

- Date: 2026-11-22 (local, Asia/Shanghai)
- Harness: OpenCode / DeepSeek Harness, root agent `lead`
- Working directory: `/home/jhb/TradingAgents`
- Branch: `feat/CHG-049-runtime-prompt-store`, from `main` at `1b59a33`
- Pull request: #58 (`feat: CHG-049 runtime prompt store`)
- Requirement: `D1-REQ-GOV-012`; related `D1-REQ-EVAL-002`, `D1-REQ-GOV-010`

> Annotated session record. The human turns are verbatim; tool calls are summarised with the
> commands that produced them. The prompts and the prompt store are English, as the repository
> requires; the conversation was in Chinese.

## Human requests (verbatim)

```text
GOV-012 只做了一半
- 现在是“有版本库，但运行时不用它”。
- 要真正完成，需要让 analyst / researcher / manager / trader 通过 load_prompt() 取 prompt，然后旧 prompt 才能算移出版本库。
- DEBT-001 现在写的是 mitigated，不是关闭。 完善这个需求，Bot Review
```

```text
A，范围可以包含3个risk debator
```

```text
开始执行，首先确认会不会和其他open的pr冲突
```

## State before the change

- `main` was `1b59a33` (CHG-048, PR #56). The only open pull request was #57
  (`test/req-tags-debate-004-ctx-002-003-mem-004`, by `@AKAScarlett`).
- The local checkout was `pr57-fix`, one unpushed commit ahead of the PR-57 remote head. That work
  was left untouched; CHG-049 branched from `main`.
- `prompts/prompt_v1.0.yaml` held five analyst fragments. `src/tradingagents/prompts/loader.py`
  verified their SHA-256 and `prompts/index.yaml` locked the file hash, but no agent called it.
- `DEBT-001` was `mitigated`, not closed.

## Conflict check against open PRs

PR #57 touches ten files. The overlap with CHG-049 is three documentation files and no code:

| File | PR #57 | CHG-049 | Resolution |
|---|---|---|---|
| `docs/ai-use-log/JHB11Hinson.yaml` | appends `AI-2026-11-22-004` | appends `AI-2026-11-22-005` | rebase after #57 merges; keep both entries |
| `docs/architecture/trace-matrix.md` | DEBATE-004/CTX-002/MEM-004 rows | GOV-012 row | different rows; expected to merge cleanly |
| `docs/code-governance/verification-constraints.md` | status-table intro and DEBATE-004 row | GOV-012 paragraph | different sections; expected to merge cleanly |

The `src/**`, `prompts/**`, test files and ADR-015 do not overlap. The branch was cut from `main`;
the AI-use-log EOF append is the only guaranteed conflict and is resolved by keeping both entries.

## Design

- ADR-015: every model-facing role, preamble and task prompt of the twelve agent nodes loads at
  node call time with `prompts.load_prompt(name).text`; dynamic values are `str.format` arguments
  and are never parsed as templates.
- `prompts/prompt_v1.1.yaml` adds the twenty fragments v1.0 does not carry. v1.0 is not edited;
  `prompts/index.yaml` appends the new file hash.
- The three shared fragments move too: `shared.debate_turn_instruction`,
  `shared.no_external_tools`, `shared.language_instruction`.
- A missing or tampered entry raises `PromptError`; there is no embedded fallback.
- The prompt text is preserved byte-for-byte. A before/after golden capture of all twelve nodes is
  the evidence.
- `DEBT-001` closes; the deterministic context builders and the optional TypeSafe post-screen
  classifier prompts are named as outside the store by design.
- Scope: four analysts, two researchers, three risk analysts, two managers and the trader, plus the
  three shared fragments.

## Test-first stage

The test commit `3cd847d` added `test/offline/test_prompt_runtime.py` and moved four source-text
assertions to the store. It ran RED as intended:

```text
28 failed, 14 passed in 1.74s
```

The failures were the missing v1.1 entries, the twelve sentinel cases, the twelve fail-closed cases,
the removal guard and the language-instruction case. The documentation and review record followed
in `a07f919`, before the first `src/` commit, as gate-1 requires. The local gate-1 check passed:

```text
gate-1: pass (ok)
```

A test fix (`f8fe786`) replaced direct module assignments with `monkeypatch.setattr` so the
sentiment stubs are restored; the leak had broken three unrelated tool-date tests.

## Implementation

The implementation commit `6ee3cf5` added `prompts/prompt_v1.1.yaml` (twenty entries) and moved
every runtime prompt to the store. `prompts/prompt_v1.0.yaml` is untouched. The golden capture
before and after is identical:

```text
$ diff -q /tmp/opencode/before.json /tmp/opencode/after.json
golden capture identical
```

The before capture was taken on `main` before the change; the after capture uses the same fixed
state, the same recording LLM and the same stubbed sentiment fetchers.

## Verification

```text
pytest -q
1611 passed, 1 skipped, 1 deselected, 20 warnings, 99 subtests passed in 34.03s

ruff check <changed src and test files>
All checks passed!

mypy --follow-imports=silent <fifteen changed source files>
Success: no issues found in 15 source files

python -m eval.run --set eval/fixed-set.json --thresholds eval/thresholds.yaml --budget 40000
eval.run: 2 case(s), 0 failed
  total_tokens_ratio: 0.270625 (pass; required <= 0.5)
  est_cost_ratio: 0.270625 (pass; required <= 0.5)
  capped_tokens_ratio: 0.927049 (pass; required <= 0.98)
  budget_respected_rate: 1.0 (pass; required >= 1)
  review_rate: 0.0 (pass; required <= 0)
  structured_output_pass_rate: 1.0 (pass; required >= 1)
  verdict: pass
```

`main` baseline after PR-57 is 1580 passed; the branch adds 31 passing cases (the new runtime
tests plus the updated source-text tests), for 1611.

## Records

- ADR-015 records the decision and the rejected alternatives.
- `DEBT-001` moves to `closed`, naming CHG-049.
- The trace matrix, verification constraints, structural constraints and blueprint name the runtime
  consumer.
- `docs/review-memo/PR-58.md` is the gate-1 record; `docs/review-memo/PR-58-review.md` is the bot
  review text. The `bot-review` label is applied only after the last push.

## What the agent did not do

- It did not edit `prompts/prompt_v1.0.yaml`.
- It did not approve or merge the pull request.
- It did not touch the local `pr57-fix` commit or PR #57.
