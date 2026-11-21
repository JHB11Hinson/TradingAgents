# 60198818 Haobin Jiang - Session 08 - Teaching collaborators to review pull requests

- Repository: `JHB11Hinson/TradingAgents`
- Owner: 60198818 Haobin Jiang (`@JHB11Hinson`)
- Part 8 of 11. Split from `transcripts/60198818-HaobinJiang.md` on 2026-11-21; the session content below is unchanged.
- Index, D5 coverage map and legacy line map: [`60198818-HaobinJiang.md`](60198818-HaobinJiang.md)

---

## Session 08 - 2026-11-03 23:24 - Teaching collaborators to review pull requests

- Session ID: `ses_e5dfd31a8ffebPnsgpoc3sa5lU`
- Model: `opencode-go/deepseek-v4.1-flash (variant: high)`
- Cost: `$0.051611`
- Tokens: input 59369, output 18780, reasoning 42240
- Related: D4 review process; branch protection
- D5 stages: Verification compliance

### Human interventions

| # | Type | What | Why |
|---|---|---|---|
| 1 | `approve` | Asked for a guide and a reusable prompt to teach collaborators how to review PRs under the automated Git flow. | The team members were new to code review and needed a concrete checklist. |
| 2 | `constrain` | Required the guide to cover this repository's automated flow, not a generic Git tutorial. | The review must check the artifacts the gates and branch protection actually enforce. |

### Transcript

#### Human

```text
我的组员编程经验较少。我该怎么教他们审核现在的 PR？如果采用项目里的自动 Git 管理流程，他们该注意哪些？
```

**Tool: `shell`**

$ ls -la /home/jhb/TradingAgents && ls -la /home/jhb/TradingAgents/.github 2>/dev/null && ls /home/jhb/TradingAgents/docs 2>/dev/null

Output:

```text
总用量 192
drwxr-xr-x 15 jhb jhb  4096 10月 30 14:17 .
drwxr-xr-x 50 jhb jhb  4096 11月  3 22:07 ..
-rw-r--r--  1 jhb jhb     0 10月 30 02:34 AGENTS.md
-rw-r--r--  1 jhb jhb   819 10月 16 20:21 architecture-blueprint.md
drwxr-xr-x  3 jhb jhb  4096  9月 24 00:45 assets
-rw-r--r--  1 jhb jhb 48063 10月  5 16:5
... [truncated 1680 chars]
```

**Tool: `shell`**

$ find /home/jhb/TradingAgents/docs -type f | head -50 && echo "---WORKFLOWS---" && ls -la /home/jhb/TradingAgents/.github/workflows && echo "---OPENCODE---" && find /home/jhb/TradingAgents/.opencode -type f | head -50

Output:

```text
/home/jhb/TradingAgents/docs/ai-use-log.yaml
/home/jhb/TradingAgents/docs/code-governance/protection.json
/home/jhb/TradingAgents/docs/architecture/adr/001-adopt-inherited-architecture.md
/home/jhb/TradingAgents/docs/architecture/adr/002-src-layout.md
/home/jhb/TradingAgents/docs/architecture/trace-
... [truncated 1447 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && for f in .opencode/git-gh-rules/README.md .opencode/git-gh-rules/00-glossary.md .opencode/git-gh-rules/10-discipline.md; do echo "===== $f ====="; cat "$f"; done

Output:

```text
===== .opencode/git-gh-rules/README.md =====
# Git / gh Automation Rules (workspace-only, not committed)

> **Audience**: the AI agent (OpenCode) working in this repository, and the human collaborators.
> **Purpose**: translate the **discipline** and **project-specific vocabulary** from the two manu
... [truncated 39509 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && for f in .opencode/git-gh-rules/20-collaborator.md .opencode/git-gh-rules/40-runbooks.md; do echo "===== $f ====="; cat "$f"; done

Output:

```text
===== .opencode/git-gh-rules/20-collaborator.md =====
# 20 · Collaborator Guide

> **Applies to**: daily development — code, prompts, docs, reviewing other people's PRs.
> **Does not apply to**: branch protection, gate rollout/removal, release freeze, history cleanup. See `30-administrator.md` for t
... [truncated 34812 chars]
```

**Tool: `skill`**

skill `brainstorming`

Output:

```text
<skill_content name="brainstorming">
# Skill: brainstorming

# Brainstorming

You are very good at building. You build what you believe your human
partner wants, and that belief is usually thinner than it feels. This
skill is for finding out what they actually want, and why, before
anything gets bui
... [truncated 14505 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && grep -n "审核\|评审\|Review\|review\|PR" .opencode/manual/开发者手册.md | head -60 && echo "=====MEMO=====" && sed -n '1,120p' docs/review-memo.md && echo "=====CI=====" && cat .github/workflows/ci.yml && echo "=====CODEOWNERS=====" && cat .github/CODEOWNERS

Output:

```text
3:> **这份文档给谁看**：在本项目里**写代码、改提示词、审 PR** 的人。
6:> **团队成员（`CODEOWNERS` 四人通配，所有文件由四人共管）**：`@JHB11Hinson`（admin）、`@AKAScarlett`、`@zihao9462-creator`、`@SY1433`。任何人的 PR 都由**另外三个人中的任意一个**批准。
29:- [七、审查别人的 PR（每个 PR 都要有人做）](#七审查别人的-pr每个-pr-都要有人做)
94:| **1 测试批准** | 改 `src/` 之前，测试有没有先提交并获批准 | 只改实现不写测试，或没有 `APPRO
... [truncated 12263 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && gh pr list --state open 2>&1 | head -20; echo "---MERGED---"; gh pr list --state merged --limit 8 2>&1 | head -20; echo "---LOG---"; git log --oneline -8 2>&1

Output:

```text
21	arch: CHG-017 add ADR-004, layered context assembly (CTX-004)	arch/CHG-017-context-assembly	OPEN
20	docs: CHG-016 add the debt register and the bug diary (GOV-010)	docs/CHG-016-qa-records	OPEN
19	gov: CHG-015 add the structural constraints (GOV-007)	gov/CHG-015-structural-constraints	OPEN
18	chore: CHG-014 ignore the Chinese workspace material under .opencode	chore/CHG-014-gitignore	OPEN
17	gov: CHG-013 add the MCP and tool manifest (GOV-005)	gov/CHG-013-mcp-tool-manifest	OPEN
16	gov: CHG-012 add the default-deny permission model (GOV-006)	gov/CHG-012-permissions	OPEN
15	gov: CHG-011 add the always-on rules and the project covenant (D3)	gov/CHG-011-rules	OPEN
14	gov: CHG-010 add Prompt.md, the coding agent's launch instruction (D9)	gov/CHG-010-prompt-md	OPEN
13	ci: CHG-009 narrow gate-6 to the course floor (code or prompts)	ci/CHG-009-gate-6-scope	OPEN
11	ci: CHG-007 add gate-2-static-analysis (batch 2)	ci/CHG-007-gate-2-static-analysis	OPEN
10	gov: CHG-006 add AGENTS.md, the coding-agent governance entry point (D3)	gov/CHG-006-agents-md	OPEN
---MERGED---
9	arch: CHG-005 add the requirements trace matrix (D2.4)	arch/CHG-005-trace-matrix	MERGED
8	req: CHG-004 register the must-priority requirements	req/CHG-004-must-requirements	MERGED
7	docs: CHG-003 fix the dangling gate reference in the architecture blueprint	docs/CHG-003-fix-blueprint-gate-reference	MERGED
3	gov: CHG-002 record branch protection baseline and bring gate batch 1 online	gov/CHG-002-protection-baseline	MERGE
... [truncated 728 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && sed -n '930,1010p' .opencode/manual/开发者手册.md && echo "=====REVIEW SECTION=====" && grep -n "七、审查别人的 PR" .opencode/manual/开发者手册.md

Output:

```text
> 全章只有两件事：**顺序**（需求 → 测试 → 实现），和**六个完整例子**（把顺序落到具体命令）。
> 每个例子都从 `cd` 进仓库开始，到 PR 合并、本地同步结束，命令可直接照抄。

## 3.1 两条总原则（顺序不能乱）

### 原则一：需求先行 —— 先登记需求，再动手

课程原文（D1 / D4）：

> 每条需求要有 **ID、type、statement、可机器校验的 fit criterion、priority**，并说明 **tradeoff**；从既有系统分析出来的需求要**链接回来源**；**每个测试都要引用它所验证的那条需求/不变量**。

推论很直接：*
... [truncated 3144 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && sed -n '1859,2010p' .opencode/manual/开发者手册.md

Output:

```text
# 七、审查别人的 PR（每个 PR 都要有人做）

> **这一章很重要**：分支保护要求"必须有别人批准"，所以**每个 PR 都有人在等**。审查不是"帮忙看一下"，而是流程里不可缺的一环——**它同时也是"人类监督"能被审计的证据**。
>
> **注意**：这一章和 `管理员手册.md` 第七章内容一致。同一个流程，两边都能查到。

## 7.1 先理解你在做什么

你在做的判断是：**"这次改动可以合进主线了吗？"**

不是"代码写得漂不漂亮"，而是四件事：

1. **该做的做了没有**（有没有测试、有没有按规矩走）
2. **不该碰的碰了没有**（有没有越过权限边界、有没有偷
... [truncated 4862 chars]
```

#### Agent

先说结论：**不要教他们“鉴宝”，要教他们“验货”。**

项目手册第七章其实已经把“审查”定义成四个问题，不是“代码写得漂不漂亮”：

1. 该做的做了没有（需求、测试、顺序）
2. 不该碰的碰了没有（范围、权限、安全路径）
3. 记录和实际对不对得上（行号、AI 日志、transcript）
4. 合进去会不会弄坏 `main`（门禁、全量回归）

代码正确性交给门禁和 agent；**人要负责的是“证据够不够、真不真、范围对不对”**。这四件事，转专业选手完全能做。

一句话原则，让他们背下来：

> **看不懂代码没关系，看不到证据就不批。**

---

## 一、先讲清三层分工

| 层 | 谁 | 负责什么 | 不能做什么 |
|---|---|---|---|
| 机器层 | CI 门禁 | `gate-3-schema`、`gate-5-regression`、`gate-6-ai-use-log` 自动跑 | 只覆盖 3 道，`gate-1/2/4` 还没上线 |
| 代理层 | OpenCode | checkout、跑 `pytest`/`ruff`、读 diff、核对行号、生成证据包和 memo 草稿 | 不能批准、不能推送、不能替人签字 |
| 人类层 | Reviewer | 判断需求对不对、范围越没越、测试有没有被改松、记录里的“人”是不是真的、安全路径有没有 ADR | 不能把“看起来没问题”当结论 |

关键习惯：**代理说“看起来没问题”不算证据。** 教他们一句话：

> “把原始输出贴出来。”

这就是规则里的“Evidence before claims”。

---

## 二、非程序员版 15 分钟审查 SOP

### Step 0：先确认资格

- 不能审自己的 PR，GitHub 也不允许。
- 必须是 `CODEOWNERS` 里的四个人之一：`@JHB11Hinson @AKAScarlett @zihao9462-creator @SY1433`。
- 如果 PR 碰的是 `.github/workflows/**`、分支保护、`CODEOWNERS`、密钥，**不要单独批**，交给你。

### Step 1：让作者用三句话复述

不是让他讲代码，而是讲：

1. 这个 PR 对应哪条需求（`D1-REQ-...`）？
2. 它改了什么用户可见行为？
3. 如果合并后出问题，怎么回滚？

说不清，就是 `CHANGES REQUIRED`。

### Step 2：让 agent 出“证据包”

给他们一段可以复制的 prompt：

```text
按 .opencode/git-gh-rules/20-collaborator.md §10.2 和 40-runbooks.md §C 审查 PR #<N>。
只审查：不要批准、不要推送、不要改代码、不要合并。
逐项给我原始输出，不要只给结论：
1. gh pr checks <N>
2. git log --oneline origin/main..HEAD -- test src
3. test/ diff 里被删除或放宽的断言、新增的 skip/xfail、被注释掉的用例（没有就写“无”）
4. 本 PR 新增/修改的测试名；哪个是负向测试；它喂了什么非法输入
5. 每个 Agent-Session 行号：文件总行数 vs 引用范围，是否越界
6. Refs 的需求 ID 是否存在；是否碰安全关键路径；有无 ADR
7. 改动文件清单是否和变更卡 Impact 一致；有无 .env/密钥/依赖/工作流文件
8. 六项检查逐项 PASS/FAIL + 证据
结果写到 /tmp/opencode/review-PR-<N>.md，并贴出原始命令输出。
```

### Step 3：人只看五个地方

| 看什么 | 不写代码怎么看 | 不合格怎么办 |
|---|---|---|
| 目的与需求 | 读 PR 第一段，再 `grep` 需求 ID 看 `statement` 和 `fit_criterion` 对不对得上 | `CHANGES REQUIRED` |
| 提交顺序 | `git log --oneline origin/main..HEAD -- test src`，`test` 必须在 `src` 前面 | `CHANGES REQUIRED` |
| 测试有没有变松 | 让 agent 列出“删断言、放宽阈值、加 `skip`、注释用例”；作者必须在 PR 里解释 | 没解释就 `CHANGES REQUIRED` |
| 记录真假 | `Agent-Session` 行号是否超过文件总行数；transcript 里有没有“人”的决策；AI log 有没有更新 | 造假就 `REJECT` |
| 范围 | 文件清单 vs 变更卡 `Impact`；有没有夹带工作流、依赖、schema、`.env` | 夹带就 `CHANGES REQUIRED` 或 STOP |

**第 3 项最需要警惕**：把测试改松比不改更糟，因为它看起来“过了”。这是 AI 最容易干、人类最该拦的事。

### Step 4：写评审记录

让他们照抄这个形状，只改内容：

```markdown
### PR-<N> — CHG-xxx <title>
- Reviewer: <你的名字>
- Specification: implements <REQ-ID>; within the change card scope / docs-only, no requirement claimed
- Architecture: follows ADR-00x / no architecture change; no authoritative boundary crossed
- Code and tests: gates 3/5/6 green; local pytest -q = <x passed>; one negative test (<name>); no skipped cases
- Runtime metadata: none / <what changed>
- Safety and efficiency: no new permissions / <...>
- Verdict: APPROVE
```

不合格就写 `Verdict: CHANGES REQUIRED`，下面加一条 `- Required changes:`。

### Step 5：顺序不能反

```bash
gh pr checkout <N>
# 追加 memo
git add docs/review-memo.md
git commit -m "docs: PR-<N> review record" -m "Refs: D4"
git push
gh pr review <N> --approve --body "<依据>"
```

**先 push 记录，再点 Approve。** 分支保护开了 `dismiss_stale_reviews`，顺序反了，你刚点的批准会被自己作废。

合并由人来点：

```bash
gh pr checks <N>
gh pr view <N> --json reviewDecision,mergeStateStatus
gh pr merge <N> --squash --delete-branch
git switch main && git pull --ff-only
```

---

## 三、他们最容易踩的十个坑

| # | 坑 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 看到三个绿勾就以为全过了 | `gate-1/2/4` 还没上线，测试批准、静态分析、语义评估没人替你做 | 只把 3/5/6 当机器结论，其余五项靠人查 |
| 2 | 先 Approve 再 push memo | 批准被 `dismiss_stale_reviews` 作废 | 先 push，再批 |
| 3 | 用 `--comment` 当批准 | PR 永远等不到批准 | 没问题也要用 `--approve`，话写在 body |
| 4 | 想批自己的 PR | GitHub 直接禁止 | 找另外三个人 |
| 5 | 被打回后等系统自动恢复 | 不会自动恢复 | 改完后**同一个人**重新批 |
| 6 | 为了让门禁变绿去改测试、加 `skip`、加 `continue-on-error` | 这是最该拦的作弊，且会毁掉评分证据 | 直接 `CHANGES REQUIRED`，让作者改实现 |
| 7 | 直接 push `main` 或 force push 别人的分支 | 违反保护规则 | 只推自己的 feature 分支 |
| 8 | 用 merge commit / rebase merge | 历史不干净 | 只 `--squash --delete-branch` |
| 9 | 分支放超过 3 天或超过 5 个提交 | 评审范围失控 | 拆 PR 或重建分支 |
| 10 | 事后补记录 | `review-memo` 是评估证据，不能补 | 先写、先 push、再批 |

再加两条 STOP：

- 冲突不要“选一边”，取并集；语义不清就 `git rebase --abort` 问人。
- 发现密钥，**先去服务商吊销**，不是先删文件。

---

## 四、怎么教：三次课，别一次灌完

**第 1 课（30 分钟）：看懂一张 PR 单**

拿已合并的 #7、#8、#9 当“好样板”，带他们走一遍六项检查。只教 8 个词：

`REQ`、`CHG`、`gate`、`ADR`、`src/`、`test/`、`skip`、`squash`

打开 Files changed，明确告诉他们：**你不需要读代码，只看文件名、测试名、提交顺序和记录。**

**第 2 课（45 分钟）：找茬**

准备三个“坏 PR”，让他们用 agent 出证据包并投票：

- A：测试从 `== 50000` 改成 `<= 100000`
- B：`src` 提交排在 `test` 前面
- C：`Agent-Session` 行号超出文件长度，或 `Refs` 指向不存在的需求

每个人必须说出“我凭什么判 FAIL”。**这比讲十遍规则有用。**

**第 3 课（30 分钟）：实战**

现在正好有 11 个 open PR。先从低风险的 docs/gov 类开始，比如 #18（`.gitignore`）、#20（debt register）、#15（structural constraints）。每人审一个，写 memo、push、approve；你只做安全网。

**之后两周双审**：他们批 + 你批。不是不信任，是防止“橡皮图章”把评分证据做废。

教学节奏用“我做、我们做、你做”：

1. 第一次你示范，他们看；
2. 第二次他们做，你在旁边提示；
3. 第三次他们独立做，你抽查 memo 和证据。

---

## 五、你必须兜底的三类 PR

不要让他们单独批准：

1. **安全关键路径**：把 AI 输出转成正式结果的那段 `src/`，没 ADR 直接停。
2. **仓库设置与工作流**：`.github/workflows/**`、分支保护、`CODEOWNERS`、Secrets——手册写明是 human-only / admin 操作。
3. **依赖、schema、测试阈值**：`pyproject.toml`、`requirements.txt`、`req-schema.json`、断言阈值。

这三类他们只需要学会一句话：**“这个我不批，转给负责人。”** 这不是无能，是流程设计。

---

## 六、现在最该先做的一件事

把上面的内容压缩成一张 A4 检查卡，贴在他们的显示器旁边：

- 左边：五看（需求、顺序、测试变松、记录真假、范围）
- 右边：三停（看不懂证据、碰安全路径/工作流/依赖、心里没底）
- 底部：一句“先 push memo，再 approve”

中文材料放 `.opencode/manual/`（这个目录被 `.gitignore` 忽略，允许中文）；不要放进 `docs/`，仓库文件要求全英文。

---

最后一个问题，决定我下一步给你哪版材料：

**他们现在能自己开终端跑 `git` / `gh` / `pytest` 吗，还是只能用 GitHub 网页？**

- 能开终端 → 用上面的“agent 代跑 + 人看证据”版；
- 只能用网页 → 需要改成“你或 agent 跑命令、把原始输出贴给他们看”的版本，否则手册里“必须本地跑一遍”这一条会落空。

你告诉我这一点，我可以直接把《非程序员 PR 审查手册》+ 一页检查卡 + 45 分钟培训脚本写出来。

#### Human

```text
自动流程由覆盖你讲的这些吗？
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && cat .opencode/git-gh-rules/50-permission-matrix.md

Output:

```text
# 50 · Permission Matrix (auto / ask / forbidden)

> This file answers one question: **"May the agent press this button by itself?"**
> Three levels: **Auto** (rules cover it, reversible, affects only the current branch), **Ask** (human confirmation each time), **Forbidden** (the agent must not exec
... [truncated 13622 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && sed -n '1,220p' .opencode/git-gh-rules/60-templates.md

Output:

````text
# 60 · Template Library

> Copy directly and replace the placeholders. Anything committed to the repository must be **English**; explanatory text may be in the workspace language.
> Placeholders: `<...>`. Do not leave unreplaced angle brackets.

---

## 1. Change card (in the PR description)

```mar
... [truncated 5376 chars]
````

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && echo "--- tracked .opencode ---" && git ls-files .opencode | head -20 && echo "--- ignored? ---" && git check-ignore -v .opencode/git-gh-rules/README.md .opencode/manual/开发者手册.md .opencode/功能需求表-讨论稿.md 2>&1 && echo "--- gitignore .opencode ---" && grep -n "opencode" .gitignore

Output:

```text
--- tracked .opencode ---
--- ignored? ---
.gitignore:226:.opencode/manual/	.opencode/manual/开发者手册.md
--- gitignore .opencode ---
226:.opencode/manual/
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && echo "--- gate jobs ---" && grep -n "name: gate" .github/workflows/ci.yml && echo "--- protection contexts ---" && cat docs/code-governance/protection.json | head -60

Output:

```text
--- gate jobs ---
1:name: gates
14:    name: gate-3-schema
25:    name: gate-6-ai-use-log
44:    name: gate-5-regression
--- protection contexts ---
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["gate-3-schema", "gate-5-regression", "gate-6-ai-use-log"]
  },
  "enforce_admins"
... [truncated 250 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && echo "--- status ---" && git status --short --untracked-files=all .opencode | head -20 && echo "--- exclude ---" && cat .git/info/exclude 2>/dev/null | tail -20 && echo "--- check-ignore verbose ---" && git check-ignore -v .opencode/git-gh-rules/README.md .opencode/功能需求表-讨论稿.md .opencode/tasks/opencode-task-CHG-006-agents-md.md 2>&1

Output:

```text
--- status ---
?? .opencode/git-gh-rules/00-glossary.md
?? .opencode/git-gh-rules/10-discipline.md
?? .opencode/git-gh-rules/20-collaborator.md
?? .opencode/git-gh-rules/30-administrator.md
?? .opencode/git-gh-rules/40-runbooks.md
?? .opencode/git-gh-rules/50-permission-matrix.md
?? .opencode/git-gh
... [truncated 539 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && gh api repos/JHB11Hinson/TradingAgents/branches/main/protection --jq '{contexts: .required_status_checks.contexts, strict: .required_status_checks.strict, admins: .enforce_admins.enabled, reviews: .required_pull_request_reviews.required_approving_review_count, codeowners: .required_pull_request_reviews.require_code_owner_reviews, dismiss: .required_pull_request_reviews.dismiss_stale_reviews}' 2>&1 | head -20

Output:

```text
{"admins":true,"codeowners":false,"contexts":["gate-3-schema","gate-5-regression","gate-6-ai-use-log"],"dismiss":true,"reviews":1,"strict":true}
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && find .opencode -name ".gitignore" -o -name ".ignore" 2>/dev/null; echo "--- global excludes ---"; git config --get core.excludesfile; echo "--- full ignore check ---"; git check-ignore -v .opencode/git-gh-rules/README.md; echo "exit=$?"

Output:

```text
--- global excludes ---
--- full ignore check ---
exit=1
```

#### Agent

**一句话：覆盖了“动作层”，没覆盖“判断层”；而且它是“受控自动化”，不是“全自动”。**

项目里的自动流程（`.opencode/git-gh-rules` + agent）已经把**该跑什么命令、该看哪六项、memo 怎么写、谁能点哪个按钮**都写死了。但它不能替人判断“这条证据是真的还是糊弄的”。所以你要教的东西不是从零开始，而是**从“教他们做流程”改成“教他们验收流程”**。

---

## 一、覆盖矩阵：我讲的哪些已经被自动化了

| 我讲的点 | 自动流程覆盖 | 覆盖到哪 | 还缺什么 |
|---|---|---|---|
| 六项检查的取数 | ✅ 已覆盖 | `20-collaborator.md` §10.2、`40-runbooks.md` §C 有完整命令 | 命令要有人让 agent 跑，并看原始输出 |
| review memo 模板 | ✅ 已覆盖 | `60-templates.md` §4，七个字段固定 | 内容真假、Verdict 由人负责 |
| 先 push memo 再 approve | ✅ 已覆盖 | 规则写了，`dismiss_stale_reviews=true` 技术强制 | 人不能把顺序做反 |
| 权限边界 | ✅ 已覆盖 | `50-permission-matrix.md`：写草稿 auto、push memo ask、approve ask、merge forbidden | 规则是 workspace-only，GitHub 不执行 |
| 冲突取并集 / 密钥先吊销 / 回滚 | ✅ 已覆盖 | `40-runbooks.md` §D/§H/§J | 语义冲突仍要人判断 |
| 提交顺序、负向测试、测试变松 | ⚠️ 只覆盖“怎么查” | 规则明确列为六项检查，且标了“第 4 项最危险” | **`gate-1` 没上线，机器不拦；只能靠 reviewer 查** |
| 需求/架构对齐 | ⚠️ 只覆盖“怎么查” | agent 会 grep `REQ-ID`、找 ADR | 需求是否真的被实现，是语义判断 |
| 记录真实性 | ⚠️ 只覆盖“怎么查” | 规则要求核对 `Agent-Session` 行号 | 行号存在 ≠ 人真的做了决策 |
| 范围是否越界 | ⚠️ 只覆盖“怎么查” | PR 模板有 `Impact`，agent 列文件清单 | 没有自动阻断，夹带文件仍可能混过去 |
| 教学、判断力、反橡皮图章 | ❌ 未覆盖 | — | **这才是你要教的** |

---

## 二、三个“规则写了、机器没拦”的缺口

这三个是你必须知道的，不然会误以为“自动化已经兜住了”。

### 1. 三道门禁还没上线

`ci.yml` 里只有：

- `gate-3-schema`
- `gate-5-regression`
- `gate-6-ai-use-log`

也就是说：

- **测试先于实现**（`gate-1`）不是机器拦的；
- **静态分析**（`gate-2`）不是机器拦的；
- **语义评估**（`gate-4`）不是机器拦的。

PR 上三个绿勾，只代表“schema 合法、全量测试过了、AI 日志改了”，**不代表测试先行、代码质量、提示词质量都过了**。这三件事现在只能靠 reviewer 查。

### 2. 门禁只查“形式”和“结果”，不查“质量”

- `gate-3`：YAML 符合 schema ≠ 需求写得对；
- `gate-5`：`pytest` 绿 ≠ 测试能证明这个改动；
- `gate-6`：`docs/ai-use-log.yaml` 改了 ≠ 日志内容真实。

所以“测试有没有被改松”永远是人的活。规则自己也写了：第 4 项最危险，因为它看起来“过了”。

### 3. `CODEOWNERS` 不是硬约束

我查了实际保护配置：

```json
"required_approving_review_count": 1,
"require_code_owner_reviews": false
```

意思是：GitHub 只要求**任意一个人**批，不要求是 `CODEOWNERS` 四人之一。“必须由另外三人之一批”是**团队规则**，不是机器强制。如果你们要它变硬，得让管理员打开 `require_code_owner_reviews`；否则只能靠人自觉。

另外，`.opencode/git-gh-rules/` 现在是**未跟踪、也没被 `.gitignore` 忽略**的状态。规则说它“workspace-only”，但一个 `git add .opencode/git-gh-rules` 就能把它提交进去。所以“不要 `git add .`”这条要重点教。

---

## 三、机器替不了的三个人类判断

这三件事，才是“人类监督”真正的内容，也是课程要评估的东西：

1. **需求语义**：这个 PR 真的实现了那条 `statement` 和 `fit_criterion` 吗？
2. **测试质量**：这个测试真的能证明它吗，还是只是“刚好绿”？
3. **风险取舍**：这个改动值不值得合，尤其碰安全关键路径时？

再补一条心态：

4. **反橡皮图章**：agent 说“看起来没问题”时，人敢不敢说“把原始输出贴出来”。

---

## 四、所以你要教的东西，其实变少了

不用教他们背 `git` 命令，教三个动作：

1. **要原始输出**，不要接受“看起来没问题”；
2. **六项逐项 PASS/FAIL + 证据**，不接受一句“都过了”；
3. **在 memo 上签自己的名字，并对 Verdict 负责**。

再加三个 STOP：

- 证据缺失 / 看不懂 → 停，要原始输出；
- 碰安全关键路径、`.github/workflows/**`、依赖、schema、测试阈值 → 停，转给你；
- 心里没底 → 停，用 `CHANGES REQUIRED`，不要“先批了再说”。

---

## 五、最大的风险

**自动流程 + 不懂的人 = 看起来合规的假证据。**

课程评估的是“可审计的人类监督”，不是“自动化率”。如果他们只会点 Approve，自动化反而更危险——因为它把“没人看”包装成了“有人批”，还留下了一条看起来很完整的 memo。

所以你的教学重点不是“让他们会用工具”，而是：

> **自动流程负责“把该查的东西摆到桌上”，人负责“判断桌上这些东西是不是真的”。**

需要的话，我可以把上面的**覆盖矩阵 + 三个技术缺口 + 三个 STOP**压成一页 A4，直接给组员当审查卡。

#### Human

```text
给他们写一段通用的提示词，我复制给他们
```

#### Agent

下面这段直接复制给组员即可。把 `<PR号>` 换成要审的 PR 编号；不换也行，agent 会先问。

```text
请按本项目规则审查 PR #<PR号>。你是“审查助手”，不是批准人。

## 你的角色
只做证据收集和初判：可以读代码、checkout、跑测试、看 diff、写草稿；
不可以批准、不可以 push、不可以合并、不可以改代码。
最终结论由人签字。

## 先读规则
先读：
- .opencode/git-gh-rules/README.md
- .opencode/git-gh-rules/10-discipline.md
- .opencode/git-gh-rules/20-collaborator.md 第 10 节
- .opencode/git-gh-rules/40-runbooks.md 第 C 节
- .opencode/git-gh-rules/50-permission-matrix.md

规则和你的理解冲突时，以规则为准；规则没写的，停下来问我。

## 审查步骤
1. 确认资格：PR 作者是不是我？是我就不审。PR 是否碰
   `.github/workflows/**`、分支保护、CODEOWNERS、密钥、安全关键路径？
   碰了先标 STOP。
2. 读 PR：`gh pr view <PR号>`、`gh pr diff <PR号>`，
   用三句话概括：改了什么、对应哪条需求（没有就写 n/a）、影响哪些文件。
3. 本地验证：先 `git status --short`；有未提交改动就停下来问我，不要 checkout。
   记录当前分支，`gh pr checkout <PR号>`，跑 `pytest -q`；
   只对 `git diff --name-only --diff-filter=ACMRT origin/main...HEAD -- src`
   里的 .py 文件跑 `ruff check`，不要全量跑继承代码；
   跑完切回原分支。跑不了就写“未验证”和原因，不要猜。
4. 六项检查，逐项给 PASS / FAIL / 无法判断 + 证据：
   (1) 门禁：`gh pr checks <PR号>`。先看 `.github/workflows/ci.yml` 和
       当前 branch protection，确认哪些门禁真的在线；不要背快照。
   (2) 测试先于实现：`git log --oneline origin/main..HEAD -- test src`，
       test 必须在 src 前面。
   (3) 负向测试：列出新增/修改的测试名，指出哪个是负向测试、
       喂了什么非法输入；没有就 FAIL。
   (4) 测试有没有被改松：检查 test/ diff 里被删除或放宽的断言、
       新增的 skip/xfail、被注释掉的用例、放宽的阈值。
       有就列出来，并说明作者有没有在 PR 里解释。
   (5) 记录真假：核对每个 Agent-Session 行号是否在文件总行数内、
       内容是否对得上；docs/ai-use-log.yaml 是否更新；
       transcript 里有没有人的决策（approve/reject/redirect/interrupt/
       correct/constrain），还是只有 AI 输出。
   (6) 需求/架构：Refs 的需求 ID 是否真的在 docs/req/requirements.yaml 里；
       是否碰安全关键路径；碰了有没有 ADR。
5. 额外检查：
   - 文件清单是否和变更卡 Impact 一致；有没有夹带 .env、密钥、依赖、
     schema、工作流文件。
   - 分支是否超过 3 天或超过 5 个提交。
   - PR 描述是否包含变更卡、Gate self-check、transcript 行号、安全路径勾选。
   - 如果改的是 AGENTS.md、.opencode/**、.agent/**、Prompt.md，加查六条治理检查：
     两处规则是否矛盾；权限白名单三处是否一致；门禁名是否和 ci.yml 一字不差；
     有没有偷偷放宽 AI 权限；Refs/行号是否真实；下游文件是否一起更新。
   - 如果这是测试批准阶段（分支上只有 test/ 提交），同样出 memo，
     标题用 CHG 编号，并注明“这是测试批准，不是 PR 批准”。

## 输出格式（中文；memo 草稿用英文）
1. 一句话结论：建议 APPROVE / CHANGES REQUIRED / REJECT / STOP
   （只是建议，不是批准）。
2. 六项检查表：项目 | PASS/FAIL/无法判断 | 证据（命令 + 关键输出）。
3. 原始输出：pytest 最后 5 行、gh pr checks、git log 顺序、
   测试 diff 的关键行。不要只给结论。
4. 异常清单：按严重程度排序；每条写“证据 + 为什么要人看”。
5. 给非程序员的三句话：这个 PR 干了什么；最大风险是什么；
   我还需要问作者什么。
6. 英文 memo 草稿（七个字段，Reviewer 留空给我填）：
### PR-<N> — CHG-xxx <title>
- Reviewer: <填我的名字>
- Specification: ...
- Architecture: ...
- Code and tests: ...
- Runtime metadata: ...
- Safety and efficiency: ...
- Verdict: APPROVE / CHANGES REQUIRED / REJECT

把完整证据包写到 /tmp/opencode/review-PR-<N>.md。

## 硬性禁止
- 不要运行 `gh pr review`、`gh pr merge`、`git push`、`git commit`。
- 不要改代码、不要改测试、不要改 docs/review-memo.md；
  memo 草稿只放 /tmp。
- 不要为了让门禁变绿加 skip、continue-on-error 或放宽断言。
- 不要用 `--comment` 代替批准。
- 不要把“看起来没问题”当结论；没有原始输出就写“未验证”。
- 不要编造行号、需求 ID、门禁名、测试结果。
- 命令失败、网络不通、权限不足：停下来，告诉我哪一步失败、
  原始报错是什么，不要重试超过一次。
- 遇到规则没覆盖、语义判断、安全关键路径、依赖/schema/测试阈值：
  标 STOP，交给我。

## 语言
- 对我解释用中文。
- 写进仓库的 memo 草稿用英文。
- 命令、路径、分支名、门禁名保持原样，不要翻译。

如果我没给 PR 号，先问我，不要猜。
```

**为什么这样写：**

- 它把 agent 的角色限制在“收集证据 + 出草稿”，批准和合并永远留给人。
- 它要求原始输出，防止 agent 用“看起来没问题”糊弄。
- 它明确写了 `gate-1/2/4` 可能没上线，避免组员看到三个绿勾就以为全过了。
- 它给了“无法判断”这个合法选项，不会逼不懂代码的人硬猜。
- 它把 memo 草稿限定在 `/tmp`，不会误提交、不会污染 `docs/review-memo.md`。

组员拿到后只需要做三件事：**贴给 agent、看证据包、决定批不批。**

#### Human

```text
我需要接近完全自动的PR
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && sed -n '1,180p' .opencode/tasks/opencode-task-CHG-006-agents-md.md

Output:

```text
# Task: CHG-006 — `AGENTS.md`, the coding-agent governance entry point (D3)

**Audience:** an autonomous coding agent (`opencode`) working inside a clone of
`JHB11Hinson/TradingAgents`, together with the human owner.
**Human owner and approver:** `@JHB11Hinson`.
**Suggested repository location:** `.
... [truncated 9213 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && grep -n "GOV-\|human\|approval\|gate\|automat" docs/req/requirements.yaml | head -60

Output:

```text
56:  source: D7 gate 4 (semantic evaluation gate); promptfoo/DeepEval frontier
78:- id: D1-REQ-GOV-001
85:- id: D1-REQ-GOV-002
92:- id: D1-REQ-GOV-003
94:  statement: All six blocking gates must be online in branch protection, each having failed on a deliberate violation.
95:  fit_criterion: gh api
... [truncated 1339 chars]
```

#### Agent

**先说结论：能做到“人只做 3～4 次决定”，做不到“没人决定”。**

你的项目规则已经把边界写死了：

- `README.md` §0：agent 最多走到 **feature branch + PR + review draft**；
- `10-discipline.md` 第 1 条：**plan / test / PR 三个人工门禁不能绕过**；
- `50-permission-matrix.md` §4：agent **不得批准、不得 `gh pr merge`、不得替人签字**。

这不是技术限制，是课程评分要的证据。**PR 越自动，人类监督的痕迹越少；全自动 PR 在课程里不是加分，是缺证据。**

但“接近全自动”可以做到：**agent 干 90% 的活，人只做 3～4 次决定。**

---

## 一、自动化边界

| 阶段 | 现在 | 接近全自动后 | 人做什么 |
|---|---|---|---|
| 需求 / 变更卡 | 人写 | agent 从批量任务文件生成 | 批一次 |
| 分支 / 提交 | agent | agent | 无 |
| 写测试 | agent | agent 写，人看测试名和负向测试 | 批一次 |
| 写实现 | agent | agent | 无 |
| 本地验证 | agent | agent 跑 `pytest` / `ruff` / schema | 无 |
| PR 描述 | agent | agent 按模板生成 | 无 |
| 审查 | 人读 diff | agent 出一页证据包 | 读 2 分钟，点 Approve |
| 合并 | 人点 | 人开 auto-merge，GitHub 自动合 | 点一次 |
| 合并后 | 人 | agent 同步 `main`、删分支、补记录 | 无 |

---

## 二、推荐形态：批量流水线

### 1. 批量任务文件

人写一次，agent 读，不能改：

```markdown
# Batch: CHG-020..025
Human owner: @JHB11Hinson
Approved plan: ...
Approved test criteria: ...
| CHG | REQ | Scope | Tests | Acceptance | Risk |
...
STOP points: ...
```

**计划批准**和**测试标准批准**可以在这个文件里一次完成；这是把 3 个门禁压成“批量确认”的关键。

### 2. agent 循环

每个 CHG 自动走：

```text
sync main -> branch -> requirement -> tests commit
  -> STOP: 人批测试
  -> implementation -> verify -> PR -> evidence packet
  -> STOP: 人批 PR
  -> push memo -> 人点 Approve -> auto-merge
  -> sync main + records
```

### 3. 一页证据包

agent 把六项检查、原始输出、异常清单、英文 memo 草稿压成一页，贴在 PR 评论或 `/tmp/opencode/review-PR-N.md`。人只看这一页，不读代码。

### 4. 人只做 3～4 件事

1. 批批量计划（一次）
2. 批测试清单（一次，可批量）
3. 批每个 PR（GitHub 强制 1 approval）
4. 开 auto-merge / 点合并（一次）

### 5. auto-merge

人开一次：

```bash
gh pr merge <N> --auto --squash --delete-branch
```

之后 GitHub 在 checks + approval 都绿时自动合。**这是“人授权、机器执行”，不是 agent 自己合。**

### 6. gate watchdog

一个定时 agent 轮询 open PR，跑六项检查，红了就修（在授权范围内），但**批准后不许再 push**——`dismiss_stale_reviews` 会把批准作废。

### 7. transcript 捕获

每次人做决定，agent 自动追加到 `transcripts/<id>.md` 和 `docs/ai-use-log.yaml`。**D5 要求每人至少一条、全队至少五条**；全自动如果把人的痕迹抹掉，代码再对也缺交付物。

---

## 三、三个方案，你选一个

| 方案 | 人的动作 | 合规 | 风险 |
|---|---|---|---|
| **A. 自动到门口** | 3 次确认 + 1 次合并 | ✅ | 最稳，但每个 PR 都要人点 |
| **B. 批量流水线（推荐）** | 批计划 + 批测试 + 每个 PR 批一次 + auto-merge | ✅ | 需要批量任务文件写得具体，否则变成橡皮图章 |
| **C. 无人批准** | 0 | ❌ | 违反 `10-discipline` 第 1 条、`50-permission-matrix` §4、branch protection；课程证据失效 |

**C 不是技术问题，是课程合规问题。** 如果真要做，得先改 `10-discipline.md`、`50-permission-matrix.md`、branch protection，还要接受 D5/D7 评分风险；我不建议，也不会帮你把 bot 批准伪装成人批准。

---

## 四、最大的三个坑

1. **批准后不要再 push**：`dismiss_stale_reviews=true`，一 push 批准就没了。
2. **不要用 bot 点 Approve**：那是伪造人类监督，规则明令禁止。
3. **不要让 transcript 空着**：全自动最容易把“人”变成零痕迹，D5 会直接扣分。

---

## 五、你现在最该做的

先把 **PR 描述 + 证据包 + memo 草稿** 自动化，这是最耗时的部分；然后把 **红门禁修复** 做成 watchdog；最后再开 **auto-merge**。

---

一个问题决定我下一步给你什么：

**你要的是 B（人保留 3 次决定，agent 干 90%），还是 C（连批准也不要人）？**

如果是 B，我可以直接给你：**批量任务文件模板 + agent 流水线提示词 + 一页证据包模板 + auto-merge 操作卡**。

#### Agent

方案 B 我直接做成一套可复制的流水线文件，放在 `.opencode/manual/pr-pipeline/`（该目录被 `.gitignore` 忽略，中文工作文档，不会进仓库）。

**Tool: `write`**

write `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/README.md` (2727 chars)

```text
# 批量 PR 流水线（B 方案）

> **目标**：agent 干 90% 的活，人只保留 3 次决定。
> **位置**：`.opencode/manual/pr-pipeline/`（workspace-only，不提交）
> **适用**：范围明确、低风险的批量改动。
> **不适用**：安全关键路径、`.github/workflows/**`、分支保护、`CODEOWNERS`、密钥、依赖、schema、测试阈值——这些走人工流程。

---

## 1. 人的 3 次决定

| # | 决定 | 什么时候 | 形式 | 能否批量 |
|---|---|---|---|---|
... [truncated 2426 chars]
```

Output:

```text
Created file successfully: .opencode/manual/pr-pipeline/README.md
```

**Tool: `write`**

write `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/batch-task-template.md` (4381 chars)

```text
# Batch: <BATCH-ID> — <short title>

> 复制本文件到 `.opencode/tasks/batch-<YYYYMMDD>-<slug>.md`，填完、签字，再交给 agent。
> 本文件是**人写的合同**，agent 只读，不得修改。

---

## 0. Approval（agent 只认这两个勾）

- [ ] 我已阅读下面的范围、需求和测试计划，**批准计划**。
- [ ] 我已阅读测试标准，**批准它们作为验收标准**。

- Human owner: `<@github-handle>`
- Signature: `<name>` / `
... [truncated 4080 chars]
```

Output:

```text
Created file successfully: .opencode/manual/pr-pipeline/batch-task-template.md
```

**Tool: `write`**

write `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/pipeline-prompt.md` (5687 chars)

````text
# 流水线提示词

> 用法：把下面 `text` 块整段复制给 agent，把 `<任务文件路径>` 换成你的批量任务文件。
> 如果任务文件还没写，先复制 `batch-task-template.md` 并签字；没有签字，agent 会 STOP。

```text
请执行批量任务文件：<任务文件路径>。
你是流水线执行者，不是批准人。你的工作是让每个 CHG 走到“可以被人批准”的状态，
然后停下来等人。最终批准、合并、安全关键判断都由人做。

## 0. 启动前（任何一项不满足就 STOP）

1. 读任务文件全文。确认 §0 的两个批准框都已勾选，Human owner 和 Sig
... [truncated 5386 chars]
````

Output:

```text
Created file successfully: .opencode/manual/pr-pipeline/pipeline-prompt.md
```

**Tool: `write`**

write `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/evidence-packet-template.md` (2631 chars)

```text
# 证据包模板（一页）

> agent 每个 PR 填一份，写到 `/tmp/opencode/review-PR-<N>.md`。
> 人只读这一页；不读代码。

---

## 0. 头部

| 项 | 内容 |
|---|---|
| PR | `#<N>` |
| CHG | `CHG-xxx` |
| 标题 | `<type>: CHG-xxx <summary>` |
| 作者 | `@...` |
| 评审人 | `@...`（必须是 CODEOWNERS 四人之一，不能是作者） |
| 分支 | `<branch>` |
| 最新提交 | `<sha>` |
| 日期 | `
... [truncated 2330 chars]
```

Output:

```text
Created file successfully: .opencode/manual/pr-pipeline/evidence-packet-template.md
```

**Tool: `write`**

write `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/auto-merge-card.md` (2220 chars)

````text
# auto-merge 操作卡（人执行）

> **只有人能开 auto-merge。** agent 可以准备命令、检查条件，但不得运行 `gh pr merge`。
> 依据：`50-permission-matrix.md` §4 硬禁止第 5 条。

---

## 1. 开之前，逐项确认

```bash
gh pr view <N> --json state,isDraft,reviewDecision,mergeStateStatus,headRefName
gh pr checks <N>
```

- [ ] `state` 是 `OPEN`
- [ ] `isDraft`
... [truncated 1919 chars]
````

Output:

```text
Created file successfully: .opencode/manual/pr-pipeline/auto-merge-card.md
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents && ls -la .opencode/manual/pr-pipeline && echo "--- ignored? ---" && git check-ignore -v .opencode/manual/pr-pipeline/README.md .opencode/manual/pr-pipeline/pipeline-prompt.md && echo "--- wc ---" && wc -l .opencode/manual/pr-pipeline/*.md

Output:

```text
总用量 44
drwxr-xr-x 2 jhb jhb 4096 11月  3 23:56 .
drwxr-xr-x 3 jhb jhb 4096 11月  3 23:55 ..
-rw-r--r-- 1 jhb jhb 3187 11月  3 23:56 auto-merge-card.md
-rw-r--r-- 1 jhb jhb 5837 11月  3 23:56 batch-task-template.md
-rw-r--r-- 1 jhb jhb 3939 11月  3 23:56 evidence-packet-template.md
-rw-r--r-- 1 jhb jhb 90
... [truncated 548 chars]
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/batch-task-template.md`

old:
```text
## 6. Records（每个 CHG 都要有）

- [ ] 变更卡（PR 描述里）
```
new:
```text
## 6. Records（每个 CHG 都要有）

### 6.1 本批授权（agent 只能做这些）

- [ ] 授权 agent 追加 test-approval memo 到 `docs/review-memo.md` 并 push 到本 CHG 分支（仅追加）。
- [ ] 授权 agent 追加 PR memo 到 `docs/review-memo.md` 并 push 到本 CH
... [truncated 156 chars]
```

Output:

```text
Edited .opencode/manual/pr-pipeline/batch-task-template.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/pipeline-prompt.md`

old:
```text
- 批准后：
  - 把测试批准 memo 追加到 `docs/review-memo.md`，标题带 `CHG-xxx`，
    `Reviewer:` 填我给的评审人名字，`Verdict: APPROVE`。
  - `git add docs/review-memo.md && git commit -m "docs: CHG-xxx test approval record" -m "
... [truncated 66 chars]
```
new:
```text
- 批准后：
  - 先看任务文件 §6.1 是否授权 memo push。没有授权：只把草稿给我，不要 commit、不要 push。
  - 有授权：把测试批准 memo 追加到 `docs/review-memo.md`，标题带 `CHG-xxx`，
    `Reviewer:` 填我给的评审人名字，`Verdict: APPROVE`。
  - `git add docs/review-
... [truncated 132 chars]
```

Output:

```text
Edited .opencode/manual/pr-pipeline/pipeline-prompt.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/pipeline-prompt.md`

old:
```text
- 如果任务文件 §5 授权，可以把证据包作为 PR 评论贴出；
  **不要贴 Verdict，不要点 Approve，不要写“我批准”。**
```
new:
```text
- 如果任务文件 §6.1 授权，可以把证据包作为 PR 评论贴出；
  **不要贴 Verdict，不要点 Approve，不要写“我批准”。** 没有授权就只写到 /tmp，给我看。
```

Output:

```text
Edited .opencode/manual/pr-pipeline/pipeline-prompt.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/pr-pipeline/pipeline-prompt.md`

old:
```text
- 我说 `approve PR <N>` 之后：
  - 把最终 PR memo 追加到 `docs/review-memo.md`：
```
new:
```text
- 我说 `approve PR <N>` 之后：
  - 先看任务文件 §6.1 是否授权 memo push。没有授权：只把 memo 草稿给我，不要 commit、不要 push。
  - 有授权：把最终 PR memo 追加到 `docs/review-memo.md`：
```

Output:

```text
Edited .opencode/manual/pr-pipeline/pipeline-prompt.md (1 replacement)
```

---

