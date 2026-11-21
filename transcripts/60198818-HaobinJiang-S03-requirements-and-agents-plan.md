# 60198818 Haobin Jiang - Session 03 - Requirements discussion table and AGENTS.md plan

- Repository: `JHB11Hinson/TradingAgents`
- Owner: 60198818 Haobin Jiang (`@JHB11Hinson`)
- Part 3 of 11. Split from `transcripts/60198818-HaobinJiang.md` on 2026-11-21; the session content below is unchanged.
- Index, D5 coverage map and legacy line map: [`60198818-HaobinJiang.md`](60198818-HaobinJiang.md)

---

## Session 03 - 2026-10-07 00:15 - Requirements discussion table and AGENTS.md plan

- Session ID: `ses_eee00043cffeq4yVQZIk8DjQcH`
- Model: `deepseek/deepseek-flash (variant: high)`
- Cost: `$0.206020`
- Tokens: input 183755, output 63701, reasoning 127586
- Related: D1, D3; feeds CHG-004 and CHG-006
- D5 stages: Requirements classification; architecture candidate generation

### Human interventions

| # | Type | What | Why |
|---|---|---|---|
| 1 | `approve` | Asked for a non-committed requirements discussion table aligned with the course brief, split across the four roles, plus the AGENTS.md plan. | Requirements must exist before architecture and implementation, and every member needs an explicit work package. |
| 2 | `constrain` | Required the table to use continuous CHG numbering and to stay out of the repository. | It is a local working draft, not a deliverable; CHG identifies a change, REQ identifies a requirement. |

### Transcript

#### Human

```text
.opencode里有一些你可能用的上的手册，请你在里面写好给团队成员讨论沟通用的功能需求表，非正式，无需提交，中文，根据课程项目要求，改进这个项目，新增功能，要求新增的功能对齐前言工程化开源项目，有一定求职价值和工程价值，第一个需求（紧跟CHG002）也就是写好AGENTS.md，规定后续工程规范、项目逻辑等，后面的需要你自己想，按照管理员，组员1，组员2，组员3分好，每个人工作量接近，管理员可以适当多一些（毕竟设计门禁上线等）
```

#### Agent

I'll start by loading the relevant skill, then explore the `.opencode` manuals you mentioned.

**Using the brainstorming skill** to explore intent and requirements before designing the feature list.

**Tool: `skill`**

skill `brainstorming`

Output:

```text
<skill_content name="brainstorming">
# Skill: brainstorming

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by classifying how much process the request needs, then work
through your path: understand the context,
... [truncated 18385 chars]
```

#### Agent

Now let me explore the project context and the manuals in `.opencode`.

**Tool: `shell`**

$ ls -la .opencode/ 2>/dev/null; echo "---GIT LOG---"; git log --oneline -20; echo "---TOP LEVEL---"; ls -la

Output:

```text
总用量 16
drwxr-xr-x  4 jhb jhb 4096 10月  6 22:40 .
drwxr-xr-x 17 jhb jhb 4096 10月  6 23:48 ..
drwxr-xr-x  2 jhb jhb 4096 10月  6 23:29 manual
drwxr-xr-x  2 jhb jhb 4096 10月  6 22:40 tasks
---GIT LOG---
7c3eb5a ci: CHG-002 bring gate batch 1 online (schema + regression + AI use log) (#2)
a21ec80 chore:
... [truncated 3102 chars]
```

**Tool: `shell`**

$ echo "=== .opencode tree ==="; find .opencode -type f | head -200

Output:

```text
=== .opencode tree ===
.opencode/manual/cs5351-2026-2027-introduction.pdf
.opencode/manual/管理员开局清单.md
.opencode/manual/CS5351-2026-2027-project.pdf
.opencode/manual/开局清单核查指南.md
.opencode/manual/管理员手册.md
.opencode/manual/开发者手册.md
.opencode/manual/门禁上线排期表.md
.opencode/tasks/opencode-task-CHG-001-struc
... [truncated 18 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual; which pdftotext; for f in *.pdf; do echo "=== $f ==="; pdftotext "$f" - 2>/dev/null | head -400; done

Output:

```text
=== cs5351-2026-2027-introduction.pdf ===
=== CS5351-2026-2027-project.pdf ===
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual; ls -la; python3 - <<'PY'
import sys
for mod in ("pypdf","PyPDF2","pdfminer","fitz"):
    try:
        __import__(mod); print("HAVE", mod)
    except Exception as e:
        print("no", mod)
PY

Output:

```text
总用量 1580
drwxr-xr-x 2 jhb jhb   4096 10月  6 23:29 .
drwxr-xr-x 4 jhb jhb   4096 10月  6 22:40 ..
-rw-r--r-- 1 jhb jhb  48164 10月  6 21:35 管理员开局清单.md
-rw-r--r-- 1 jhb jhb 215158 10月  6 21:35 管理员手册.md
-rw-r--r-- 1 jhb jhb  96677 10月  6 19:15 开发者手册.md
-rw-r--r-- 1 jhb jhb  12952 10月  6 21:35 开局清单核查指南.md
-rw-r--r-- 1 jhb jhb  13031 10月  6 19:15 门禁上线排期表.md
-rw-r--r-- 1 jhb jhb 841744  9月  9 12:42 cs5351-2026-2027-introduction.pdf
-rw-r--r-- 1 jhb jhb 364844  9月 16 01:34 CS5351-2026-2027-project.pdf
HAVE pypdf
no PyPDF2
no pdfminer
no fitz
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual; python3 - <<'PY'
from pypdf import PdfReader
for f in ("CS5351-2026-2027-project.pdf","cs5351-2026-2027-introduction.pdf"):
    print("\n\n########## ", f, " ##########")
    r = PdfReader(f)
    for i,p in enumerate(r.pages):
        t = p.extract_text() or ""
        print(f"\n----- page {i+1} -----")
        print(t)
PY

Output:

```text
incorrect startxref pointer(3)
parsing for Object Streams
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype


##########  CS5351-2026-2027-project.pdf  ##########

----- page 1 -----
CS5351  |  Agentic Software Engineering Project
Page 1
CS5351
Agentic Software Engineering Project
Project Requirement Sheet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Core expectation:  Design, build, verify, and maintain an AI-enabled software application using an
AI coding agent under auditable human supervision.

Course Project Specification


----- page 2 -----
CS5351  |  Agentic Software Engineering Project
Page 2
Document Contents
• 1. Project Overview
• 2. Team Composition and Role Assignment
• 3. Deliverables
• 4. Submission Format
• 5. Required Reposit
... [truncated 35527 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "=== docs tree ==="; find docs -type f | sort
echo; echo "=== .github tree ==="; find .github -type f | sort
echo; echo "=== .agent/.opencode/prompts/eval/transcripts ==="; find .agent .opencode prompts eval transcripts -type f 2>/dev/null | sort
echo; echo "=== src top ==="; find src -maxdepth 2 -type d | sort
echo; echo "=== git status ==="; git status --short | head -30
echo; echo "=== AGENTS.md size ==="; wc -c AGENTS.md Prompt.md Report.md architecture-blueprint.md docs/req/*.json docs/req/*.yaml docs/ai-use-log.yaml 2>/dev/null

Output:

```text
=== docs tree ===
docs/ai-use-log.yaml
docs/architecture/adr/001-adopt-inherited-architecture.md
docs/architecture/adr/002-src-layout.md
docs/req/req-schema.json
docs/req/requirements.yaml
docs/review-memo.md

=== .github tree ===
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/bug-report.yml
.github/ISSU
... [truncated 1061 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "=== requirements.yaml ==="; cat docs/req/requirements.yaml 2>/dev/null
echo; echo "=== ai-use-log.yaml ==="; cat docs/ai-use-log.yaml 2>/dev/null
echo; echo "=== ci.yml ==="; cat .github/workflows/ci.yml 2>/dev/null
echo; echo "=== architecture-blueprint.md ==="; cat architecture-blueprint.md 2>/dev/null

Output:

```text
=== requirements.yaml ===
- id: D1-REQ-GOV-001
  type: governance
  statement: The repository layout must satisfy the required structure before any feature work starts.
  fit_criterion: src/ holds all application source; test/offline and test/live exist; pip install -e ".[dev]" succeeds; pytest -q i
... [truncated 4005 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "=== src/tradingagents files ==="; find src/tradingagents -name '*.py' -not -path '*__pycache__*' | sort
echo; echo "=== src/cli files ==="; find src/cli -type f -not -path '*__pycache__*' | sort
echo; echo "=== test/offline count ==="; find test -name 'test_*.py' | wc -l; find test -maxdepth 2 -type d | sort
echo; echo "=== prompts/eval/transcripts ==="; ls -la prompts eval transcripts 2>&1

Output:

```text
=== src/tradingagents files ===
src/tradingagents/agents/analysts/fundamentals_analyst.py
src/tradingagents/agents/analysts/__init__.py
src/tradingagents/agents/analysts/market_analyst.py
src/tradingagents/agents/analysts/news_analyst.py
src/tradingagents/agents/analysts/sentiment_analyst.py
src/tra
... [truncated 4191 chars]
```

#### Agent

我已经把 `.opencode/manual/` 里的四份手册、CHG-001/CHG-002 的任务书与现状、以及课程 Requirement Sheet（PDF）都读了一遍。下面先给结论，再给完整草案。

## 一、我了解到的背景（用来对齐需求）

- 课程核心：**在可审计的人类监督下**，用 OpenCode 设计/构建/验证/维护一个含 AI 组件的应用；交付物是 **D1–D9** + 五份会话记录 + `Report.md` + `ai-use-log.yaml`。
- 项目定位：**增强** `TauricResearch/TradingAgents`（不是重写），课程明确点名两个痛点——**慢、烧 token**，以及**子代理辩论过于自由**。
- 现状：CHG-001（src 布局）、CHG-002（治理骨架 + 第 1 批门禁：`gate-3/5/6`）已合并；`AGENTS.md`、`Prompt.md`、`Report.md`、`architecture-blueprint.md`（仅 `Code baseline` 段）、`eval/`、`prompts/` 基本为空占位。
- 团队：`@JHB11Hinson`(管理员) + 三名组员。课程评分还看**相对贡献度**（工时/故事点折算）。

所以这份“功能需求表”会同时覆盖**治理/工程规范类**（对齐 D1–D9 与六道门禁）和**产品功能类**（对齐课程 hint 与前沿工程实践），并按人分派、工时尽量均衡。

> 我把它当作一份规划/规格产出（不是代码），所以先把草案全文放在对话里给你审，确认后再落盘。

## 二、建议的文件与结构

- 路径：`/home/jhb/TradingAgents/.opencode/功能需求表-讨论稿.md`（放 `.opencode/` 根，非正式、不提交；文件名你可以改）
- 结构：背景与来源 → 角色映射 → 按人分工总表 → 工时汇总 → NFR 指标 → 对标前沿开源 → 里程碑 → 待拍板问题
- 语言：中文；仓库内仍需英文交付物，本文件属仓库外讨论稿（`README`/PR 描述里引用时用英文）。

## 三、需求与分工草案

编号说明：CHG-001/002 已用；管理员用 `CHG-003…`，组员用 `CHG-1xx/2xx/3xx`（讨论稿易读，正式登记时再统一重排为连续号）。

### 管理员（`@JHB11Hinson`）— 工程规范 / 门禁 / 发布 / 可观测性（约 68h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据（fit criterion） | 工程/求职价值 |
|---|---|---|---|---|---|
| **CHG-003** | **AGENTS.md 工程总纲**（紧跟 CHG-002，第一件事） | `AGENTS.md`(D3) | 12 | >200B；含 build target、架构工件阅读顺序、code baseline、可读/可改/冻结清单、模块组织、模块间集成契约、生成代码的验证要求、human-only 与 STOP 点；团队评审 APPROVE | Agent 治理/规范编写 |
| CHG-004 | 架构主约束 + 结构约束 | `architecture-blueprint.md` 完整化(D2.1)、`structural-constraints.md`(D3) | 10 | 含 scope/drivers/boundaries/authority/workflow/permissions/verification/observability/change policy；模块与架构元素一一对应 | 架构设计、SA |
| CHG-005 | 权限模型与运行策略 | `permission-model.md`(D2.6)、`runtime-policy-catalog.md`(D2.7)、`.opencode/permissions.jsonc`、`.opencode/rules.md`、`.agent/rules.md`、`mcp-tool-manifest.md` | 12 | 默认拒绝、逐路径白名单；规则被 agent 实际读取生效 | AI 安全边界、权限工程 |
| CHG-006 | 门禁分批上线 + 分支保护终态 | `ci.yml` 第 2/3/4 批、`protection.json` | 12 | 六道门禁名与 `contexts` 一字不差；每道**故意红过一次**；直推 `main` 被拒 | CI/CD、分支保护、发布 |
| CHG-007 | 运行时可观测性与成本计量 | run manifest + 结构化 trace + 成本/时延汇总 | 14 | 一次运行产出可解析的 trace JSON；token/成本/耗时可按阶段汇总 | LLM 可观测性（OTel 风格） |
| CHG-008 | 追溯矩阵与冻结发布 | `trace-matrix.md`(D2.4)、需求登记册维护、`review-memo.md` 汇总、评审排班、贡献度统计、冻结 tag | 8 | 每条需求→组件→测试→运行时监控可查；冻结 tag 已推 | 可追溯性、项目管理 |

### 组员1 — 结构化辩论与质量控制（约 60h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据 | 价值 |
|---|---|---|---|---|---|
| CHG-101 | **结构化辩论协议**：限定轮次 + 主张/证据/反驳结构 + Osborn 式先发散后收敛 | 辩论模块改造 | 20 | 轮次≤上限；输出结构化（claim/evidence/rebuttal/confidence）；质量指标≥基线 | 多智能体编排/Prompt 工程 |
| CHG-102 | **终止纪律**：振荡/停滞/预算耗尽检测，防死循环 | 终止判定模块 | 8 | 构造振荡用例能自停；含负向测试 | Agent 稳定性 |
| CHG-103 | 提示词版本化 + 辩论质量评测 | `prompts/prompt_v1.x.yaml`、指标与用例 | 14 | 改提示词触发 `gate-4`；指标可复现 | Prompt 版本治理、LLM 评测 |
| CHG-104 | 不变量/评测表/债务登记 | `invariants.md`(D2.3)、`evaluation-table.md`(D2.8)、`debt-register.md`(D4) | 10 | 每条不变量有来源需求、执行组件、验证方法、回退动作 | QA、不变量设计 |
| — | 亲手让某道门禁红一次 + 评审他人 PR | 记录 | 8 | review-memo 里有 APPROVE 记录 | 代码评审 |

### 组员2 — 上下文工程与成本（约 58h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据 | 价值 |
|---|---|---|---|---|---|
| CHG-201 | **分层上下文结构 + 装配管线**（identity/standing constraints/retrieved knowledge/history/state/current task；dedupe→prioritize→budget→compact→assemble） | 上下文模块 | 18 | 结构可配置；装配单测通过 | Context Engineering、RAG 基础 |
| CHG-202 | **Token 预算守卫**：预算上限 + 压缩阈值 + 压缩后重注入关键约束 | 预算守卫模块 | 12 | 超预算触发压缩；压缩后关键约束断言仍在；总 token≤阈值 | 成本优化（课程加分项） |
| CHG-203 | LLM/数据缓存层 | 缓存模块 + 命中率统计 | 10 | 重复运行命中缓存；节省率可量化 | 性能、缓存设计 |
| CHG-204 | 记忆设计 + 评测台账 + **eval 框架** | `memory-design.md`(D2.5)、`evaluation-logbook.md`(D2.9)、`eval/{fixed-set.json,thresholds.yaml,run.py}` | 12 | 本地 `python -m eval.run` 跑通并输出阈值判定（供 `gate-4` 用） | LLM Evals |
| — | 门禁红实验 + 评审 | 记录 | 6 | 同上 | — |

### 组员3 — 记忆、安全与评测（约 58h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据 | 价值 |
|---|---|---|---|---|---|
| CHG-301 | **决策记忆语义检索（RAG）**：历史决策/反思 embedding + 检索相关条目注入（跨 ticker 学习） | 记忆检索模块 | 18 | 正/负检索用例通过；注入内容可追溯来源 | RAG/向量检索、Reflexion |
| CHG-302 | **安全边界与确定性护栏**：检索文本防注入清洗 + 决策 schema 校验 + 交易规模确定性上限拦截 | 护栏模块 | 16 | 对抗注入样本 100% 拦截（负向测试必红）；非法决策被拒并降级 | LLM 安全/Guardrails（课程“安全边界”要求） |
| CHG-303 | 回测/消融对比（有/无新功能） | 对比数据与图表 | 10 | 可复现对比表（成本/时延/通过率/质量） | 实验设计、量化评估 |
| CHG-304 | 选项台账 + 风险清单 | `option-ledger.md`(D2.11)、`risk-list.md`(D2.10) | 8 | 被拒方案与再评估触发条件成文 | 架构决策 |
| — | 门禁红实验 + 评审 | 记录 | 6 | 同上 | — |

### 工时汇总（均衡性）

| 角色 | 工时 | 相对贡献 |
|---|---|---|
| 管理员 | 68 | ≈1.12 |
| 组员1 | 60 | ≈0.99 |
| 组员2 | 58 | ≈0.96 |
| 组员3 | 58 | ≈0.96 |

（管理员略多，落在“设计门禁/上线/发布”一侧；正式动工前可微调。）

## 四、非功能需求（NFR，metric + threshold + verification）

| 需求 ID | 类型 | 指标 → 阈值 | 验证方式 |
|---|---|---|---|
| D1-REQ-COST-001 | cost | 单次分析 token/成本 ≤ 基线 50% | eval 固定集汇总 |
| D1-REQ-PERF-001 | performance | wall-clock ≤ 基线 60% | 固定集重复取中位数 |
| D1-REQ-QUAL-001 | quality | 结构化输出通过率 100%；辩论证据引用率 ≥ 基线 | schema 校验 + 评测指标 |
| D1-REQ-SAFE-001 | security/invariant | 注入样本拦截率 100%；交易规模不超确定性上限 | 负向测试（零容忍） |
| D1-REQ-CTX-001 | invariant | 装配后上下文 ≤ 预算；压缩后关键约束仍在 | 装配单测断言 |
| D1-REQ-GOV-002 | governance | AGENTS.md 覆盖 6 个必需小节 | 评审 checklist |

## 五、对标的前沿开源实践（“对齐前沿工程化开源项目”）

| 方向 | 本项目落点 | 对标 |
|---|---|---|
| 可观测性 | CHG-007 trace（span/成本/时延） | OpenTelemetry GenAI、Langfuse/LangSmith |
| LLM 评测 | CHG-103/204 + `gate-4` | promptfoo、DeepEval、OpenAI Evals |
| 安全护栏 | CHG-302 | NeMo Guardrails、Guardrails AI |
| 语义缓存 | CHG-203 | GPTCache |
| 结构化输出 | CHG-302 schema 校验 | Pydantic / instructor / Outlines |
| 反思式记忆 | CHG-301 | Reflexion（论文）、mem0 |

## 六、里程碑（波次）

1. **Sprint 1 · 治理地基**：CHG-003→008 + `Prompt.md`；门禁第 2 批上线。**此波不写产品功能**。
2. **Sprint 2 · 三条主线首版**：CHG-101 / 201 / 301 + CHG-007 可观测性。
3. **Sprint 3 · 质量与安全**：CHG-102 / 202 / 302 / 103 / 203。
4. **Sprint 4 · 评测与收尾**：CHG-104 / 204 / 304 / 303 + 门禁第 3/4 批 + 冻结发布 + `Report.md`/演示视频。

## 七、需要团队拍板的问题（写进讨论稿）

1. **组员1/2/3 分别对应哪位同学**及其 GitHub 账号？（文档先留占位）
2. 四条产品主线是否全做，还是砍到三条（YAGNI）？尤其缓存 CHG-203 的收益/成本。
3. **评测是否真的调用 LLM**（花钱）：谁提供 key/预算、Actions Secrets 怎么配。
4. **依赖政策**：语义检索用轻量 numpy 余弦（零新依赖）还是引入 faiss/chromadb？需与 `.agent/rules.md` 的依赖约束一致。
5. `AGENTS.md` / 安全护栏是否划为**安全关键路径**（改动需 ADR + 人工评审）？
6. sprint 长度、冻结与拍摄演示视频的时间点。

---

## 下一步

我现在处于 **Plan 模式**，只能讨论、不能写仓库文件。上面就是准备写入 `.opencode/功能需求表-讨论稿.md` 的草案内容。

请确认/修改（尤其是**组员对应关系**和**是否砍功能**这两点），然后**切到执行/构建模式**，我就把这份内容按你选定的文件名落盘。需要我先把草案改到什么程度再写，直接说即可。

#### Agent

Now that we're out of Plan mode, I'll write the draft. Let me first check how `.opencode/` is handled by git so the Chinese discussion doc stays untracked.

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
grep -n "opencode\|manual" .gitignore || echo "(no .opencode rule)"
echo "--- check-ignore ---"
git check-ignore -v .opencode/manual/管理员手册.md 2>&1 || echo "manual NOT ignored"
git check-ignore -v .opencode/功能需求表-讨论稿.md 2>&1 || echo "new file NOT ignored"

Output:

```text
225:# Local, non-English course manuals (kept out of the repository on purpose)
226:.opencode/manual/
--- check-ignore ---
.gitignore:226:.opencode/manual/	.opencode/manual/管理员手册.md
new file NOT ignored
```

#### Agent

We're clear now. Writing the draft discussion doc.

**Tool: `write`**

write `/home/jhb/TradingAgents/.opencode/功能需求表-讨论稿.md` (7881 chars)

```text
# 新增功能需求表（讨论稿）

> **状态**：非正式、供团队讨论，**不提交**（仓库内交付物一律英文；本文件属仓库外中文讨论稿）。
> **依据**：CS5351 Requirement Sheet D1–D9 与第 6 节六道门禁、导论 Assessment 3 原文、以及仓库内《管理员/开发者手册》系列。
> **现状基线**：CHG-001（src 布局对齐）、CHG-002（治理骨架 + 第 1 批门禁 `gate-3/5/6`）已合并。
> **日期**：2026-10-07
> **怎么用**：Sprint 1 是后续所有功能的前置；先确认第 11 节“待拍板问题”再动工。
... [truncated 7580 chars]
```

Output:

```text
Created file successfully: .opencode/功能需求表-讨论稿.md
```

#### Agent

已写入。快速核对一下文件与 git 状态：

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
ls -la .opencode/功能需求表-讨论稿.md
wc -l .opencode/功能需求表-讨论稿.md
echo "--- git status (该文件应仍未跟踪) ---"
git status --short .opencode/
echo "--- 标题 ---"
head -6 .opencode/功能需求表-讨论稿.md

Output:

```text
-rw-r--r-- 1 jhb jhb 12698 10月  7 00:38 .opencode/功能需求表-讨论稿.md
187 .opencode/功能需求表-讨论稿.md
--- git status (该文件应仍未跟踪) ---
?? .opencode/
--- 标题 ---
# 新增功能需求表（讨论稿）

> **状态**：非正式、供团队讨论，**不提交**（仓库内交付物一律英文；本文件属仓库外中文讨论稿）。
> **依据**：CS5351 Requirement Sheet D1–D9 与第 6 节六道门禁、导论 Assessment 3 原文、以及仓库内《管理员/开发者手册》
... [truncated 93 chars]
```

#### Agent

已写好：`.opencode/功能需求表-讨论稿.md`（187 行，中文、非正式讨论稿，当前仍未跟踪，不会误提交）。

**这份讨论稿包含：**
- 背景与对齐（课程 D1–D9、六道门禁、Assessment 3 的两个痛点）
- 角色映射：管理员 `@JHB11Hinson`，组员1 `@AKAScarlett`、组员2 `@zihao9462-creator`、组员3 `@SY1433`（建议值，可整列调换）
- 四张按人分工表，共 **18 个工作包 + 各自的“门禁红一次/评审”**：
  - 管理员（68h）：CHG-003 `AGENTS.md`（第一件事）→ 架构主约束 / 权限模型 / 门禁分批上线 / 可观测性 / 追溯发布
  - 组员1（60h）：结构化辩论协议、终止纪律、提示词版本化、不变量评测表
  - 组员2（58h）：分层上下文装配、Token 预算守卫、缓存、记忆设计 + eval 框架
  - 组员3（58h）：决策记忆 RAG、安全护栏（防注入 + schema + 确定性上限）、消融对比、选项/风险台账
- NFR 指标表（cost/perf/quality/safety/context/governance，metric+threshold+verification）
- 对标前沿开源（OTel、promptfoo/DeepEval、NeMo Guardrails、GPTCache、Reflexion 等）
- 四个 Sprint 里程碑
- D1–D9 与全部 D2/D3/D4 工件的覆盖核对表（确保不遗漏）

**动手前建议先拍板（稿子第 11 节）：**
1. 组员1/2/3 的最终对应关系
2. 四条产品主线是否全做（缓存 CHG-203 是否砍）
3. 评测是否真调用 LLM（谁出 key/预算、Actions Secrets）
4. 语义检索用轻量 numpy 还是引入 faiss/chromadb（受 `.agent/rules.md` 依赖约束）
5. `AGENTS.md`/安全护栏是否划为安全关键路径
6. Sprint 长度与冻结/拍摄时间点

两点补充：
- 该文件目前在 `?? .opencode/` 里。若要它**永远进不了仓库**，可在 `.gitignore` 追加 `.opencode/功能需求表-讨论稿.md`（与现有 `.opencode/manual/` 规则同理）——需要我加就说一声。
- 需要我把它改成连续 CHG 编号（去掉 1xx/2xx/3xx）、或拆成每人一份任务书时，告诉我即可。

#### Human

```text
永远不进仓库，改成CHG连续编号，以及告诉我需求表里CHG的含义是什么
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "=== all CHG occurrences with line numbers ==="
grep -n "CHG" .opencode/功能需求表-讨论稿.md

Output:

```text
=== all CHG occurrences with line numbers ===
5:> **现状基线**：CHG-001（src 布局对齐）、CHG-002（治理骨架 + 第 1 批门禁 `gate-3/5/6`）已合并。
19:  - **治理/工程规范类**（对齐 D1–D9 与六道门禁，含紧跟 CHG-002 的 `AGENTS.md`）；
39:- **编号**：`CHG-001/002` 已用；本稿管理员用 `CHG-003…`，组员用 `CHG-1xx / 2xx / 3xx`（讨论稿更易读，正式登记时统一重排为连续号）。
42:- **纪律**：每条工作包开分支 `f
... [truncated 4616 chars]
```

#### Agent

理解。我来做三件事：改为连续编号、写清 `CHG` 的含义、并加 gitignore 规则确保它永不进仓库。

先更新文档（连续编号：管理员 `CHG-003–008`，组员1 `CHG-009–012`，组员2 `CHG-013–016`，组员3 `CHG-017–020`）：

**Tool: `write`**

write `/home/jhb/TradingAgents/.opencode/功能需求表-讨论稿.md` (8295 chars)

```text
# 新增功能需求表（讨论稿）

> **状态**：非正式、供团队讨论，**不提交**（仓库内交付物一律英文；本文件属仓库外中文讨论稿）。
> **依据**：CS5351 Requirement Sheet D1–D9 与第 6 节六道门禁、导论 Assessment 3 原文、以及仓库内《管理员/开发者手册》系列。
> **现状基线**：CHG-001（src 布局对齐）、CHG-002（治理骨架 + 第 1 批门禁 `gate-3/5/6`）已合并。
> **日期**：2026-10-07
> **怎么用**：Sprint 1 是后续所有功能的前置；先确认第 11 节“待拍板问题”再动工。
... [truncated 7994 chars]
```

Output:

```text
Wrote file successfully: .opencode/功能需求表-讨论稿.md
```

#### Agent

Now the gitignore rule. Let me see the current tail of `.gitignore` to append consistently:

**Tool: `shell`**

$ cd /home/jhb/TradingAgents; tail -6 .gitignore | cat -A | sed 's/\$$//'

Output:

```text
# Enterprise env file (secrets) and generated run reports
.env.enterprise
reports/

# Local, non-English course manuals (kept out of the repository on purpose)
.opencode/manual/
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.gitignore`

old:
```text
# Local, non-English course manuals (kept out of the repository on purpose)
.opencode/manual/
```
new:
```text
# Local, non-English course manuals (kept out of the repository on purpose)
.opencode/manual/

# Local, non-English team discussion drafts (kept out of the repository on purpose)
.opencode/功能需求表-讨论稿.m
... [truncated 1 chars]
```

Output:

```text
Edited .gitignore (1 replacement)
```

#### Agent

Now verify everything:

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "=== 该文件是否已被忽略 ==="
git check-ignore -v .opencode/功能需求表-讨论稿.md
echo
echo "=== git status（文件应不出现在待提交里） ==="
git status --short
echo
echo "=== 残留的旧编号（应为空） ==="
grep -n "CHG-1[0-9][0-9]\|CHG-2[0-9][0-9]\|CHG-3[0-9][0-9]\|1xx\|2xx\|3xx" .opencode/功能需求表-讨论稿.md || echo "无残留 ✓"
echo
echo "=== 连续编号核对（应出现 CHG-003..CHG-020） ==="
grep -o "CHG-0[0-2][0-9]" .opencode/功能需求表-讨论稿.md | sort -u | tr '\n' ' '; echo
echo
echo "=== CHG 含义段落 ==="
grep -n "CHG 是什么" .opencode/功能需求表-讨论稿.md

Output:

```text
=== 该文件是否已被忽略 ===
.gitignore:229:.opencode/功能需求表-讨论稿.md	.opencode/功能需求表-讨论稿.md

=== git status（文件应不出现在待提交里） ===
 M .gitignore
?? .opencode/

=== 残留的旧编号（应为空） ===
无残留 ✓

=== 连续编号核对（应出现 CHG-003..CHG-020） ===
CHG-001 CHG-002 CHG-003 CHG-004 CHG-005 CHG-006 CHG-007 CHG-008 CHG-009 CHG-010 CHG-011 CHG-012
... [truncated 381 chars]
```

#### Agent

三件事都完成了：

**1. 永远不进仓库 ✓**
`.gitignore` 末尾新增规则（第 229 行）：
```
# Local, non-English team discussion drafts (kept out of the repository on purpose)
.opencode/功能需求表-讨论稿.md
```
`git check-ignore` 已确认命中该规则，即使 `git add -A` 也不会被暂存。（注意：`git status` 现在会显示 `.gitignore` 被修改 `M` —— 那是这条规则本身，属于正常且必要的改动。）

**2. 连续编号 ✓**
`CHG-003 … CHG-020`，无旧编号残留：

| 角色 | 连续编号 |
|---|---|
| 管理员 | CHG-003 – CHG-008 |
| 组员1 | CHG-009 – CHG-012 |
| 组员2 | CHG-013 – CHG-016 |
| 组员3 | CHG-017 – CHG-020 |

（CHG-001/002 已被 src 布局、治理骨架 + 第一批门禁占用。）

**3. `CHG` 的含义（已写进文档第 2 节）**

`CHG` = **Change（变更）**，就是课程手册里的**变更卡编号 / Change ID**（对应手册里的 `### Change card - Change ID: CHG-014`）。它是**一次变更的全局唯一编号**，把整条链路串起来：

```
需求(D1-REQ-xxx) → 变更卡(CHG-020) → 分支(feat/chg-020-...)
→ 提交 trailer(Refs: CHG-020) → PR 描述 → review-memo → ai-use-log
```

- **来源**：每次“同步 main → 开分支 → 登记需求 → 计划获批 → 测试先行 → AI 写实现 → 开 PR → 评审合并”就是一个 CHG。
- **出现位置**：分支名、提交信息 trailer（`Refs: CHG-020`）、PR 描述、`docs/review-memo.md`、`docs/ai-use-log.yaml`。
- **规则**：全局唯一、**只增不减、不复用**；这样期末审计/贡献度统计时可以用 `git log --grep=CHG-020` 把一件事的所有痕迹一次找出来。

文档路径：`.opencode/功能需求表-讨论稿.md`（已改连续编号）。需要我把“组员映射”按最终决定填实、或改成更粗的 `.opencode/讨论稿/` 目录整体忽略，随时说。

#### Human

```text
需求ID怎么填含义是什么
```

#### Agent

需求 ID 是 D1 交付物里的主键，和 `CHG` 是两个不同维度。我先把含义和填法加到文档里，再在这里讲清楚。

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/功能需求表-讨论稿.md`

old:
```text
- 组员3 `CHG-017 – CHG-020`（4 项）
- **工时**：单位为人时，仅用于估算与贡献度对齐，动工前可微调。
```
new:
```text
- 组员3 `CHG-017 – CHG-020`（4 项）
- **需求 ID 是什么 / 怎么填**：每一条需求在 `docs/req/requirements.yaml` 里的 `id:` 字段。本表统一格式 **`D1-REQ-<领域>-<三位序号>`**：
  - `D1`：固定前缀，表示这是 **D1 交付物**（machine-readable requirements regist
... [truncated 715 chars]
```

Output:

```text
Edited .opencode/功能需求表-讨论稿.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/功能需求表-讨论稿.md`

old:
```text
| D1-REQ-GOV-002 | governance | AGENTS.md 覆盖 6 个必需小节 | 评审 checklist |

---
```
new:
````text
| D1-REQ-GOV-002 | governance | AGENTS.md 覆盖 6 个必需小节 | 评审 checklist |

> **怎么填一条**（写入 `docs/req/requirements.yaml`，字段以 `docs/req/req-schema.json` 为准）：
>
> ```yaml
> - id: D1-REQ-COST-001
>   type: cos
... [truncated 752 chars]
````

Output:

```text
Edited .opencode/功能需求表-讨论稿.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
grep -n "需求 ID 是什么\|需求 ID 与 CHG\|怎么填一条" .opencode/功能需求表-讨论稿.md
echo "--- 确认仍被忽略 ---"
git check-ignore -v .opencode/功能需求表-讨论稿.md

Output:

```text
45:- **需求 ID 是什么 / 怎么填**：每一条需求在 `docs/req/requirements.yaml` 里的 `id:` 字段。本表统一格式 **`D1-REQ-<领域>-<三位序号>`**：
51:- **需求 ID 与 CHG 的关系**：两者是不同维度 —— **需求 ID = “要满足什么”**（长期稳定，可被多条 CHG 触碰）；**CHG = “实现它的那一次变更”**（一次性，带分支/PR/记录）。一个 CHG 可实现多条需求（PR 里写 `Refs: D1-REQ-COST-001, D1-REQ-PERF-001`），一条需求也可能由多条 CHG 迭代满足。
... [truncated 265 chars]
```

#### Agent

已把说明写进文档（第 2 节“需求 ID 是什么 / 怎么填”+ 第 8 节“怎么填一条”示例）。下面是完整解释：

## `需求 ID` 是什么

它是 D1 交付物 `docs/req/requirements.yaml` 里**每一条需求的 `id:` 字段**——需求的**主键**。课程 D1 要求每条需求都要有：`id`、`type`、`statement`、`fit_criterion`、`priority`（可选 `tradeoff`、`source`）。

> 注意：`req-schema.json` 只校验 `id` 是字符串，**格式是我们自己定的约定**，但必须全队一致、且一旦引用就不再改。仓库里现成的一个真实例子就是 `D1-REQ-GOV-001`（src 布局那条）。

## 格式与各段含义

```
D1-REQ-<领域>-<三位序号>
```

| 段 | 含义 | 取值 |
|---|---|---|
| `D1` | 固定前缀，表示它属于 **D1 交付物**（需求登记册） | 恒为 `D1` |
| `REQ` | 固定，表示这是 requirement 条目 | 恒为 `REQ` |
| `<领域>` | 类别代码，建议与 schema 的 `type` 对齐；同类下可按模块细分 | `FUNC`功能 / `INV`不变量 / `QUAL`质量 / `PERF`性能 / `COST`成本 / `GOV`治理 / `SEC`安全；细分：`CTX`上下文 / `MEM`记忆 / `DEBATE`辩论 / `OBS`可观测 / `EVAL`评测 |
| `<三位序号>` | 同类内从 `001` 递增 | `001`、`002`… **不复用、不改号** |

例：`D1-REQ-COST-001`（第 1 条成本需求）、`D1-REQ-SAFE-001`（第 1 条安全需求）。

## 怎么填（一条完整示例）

```yaml
- id: D1-REQ-COST-001
  type: cost
  statement: A single analysis run must spend no more than half of the baseline tokens and estimated cost.
  fit_criterion: python -m eval.run over eval/fixed-set.json reports total_tokens <= 0.5 * baseline and est_cost <= 0.5 * baseline.
  priority: must
  tradeoff: Aggressive compaction can drop evidence the debaters rely on; quality must stay at or above baseline.
  source: project brief section 5 / D1; intro slide "Assessment 3" (slow and token-burning)
```

| 字段 | 怎么填 |
|---|---|
| `id` | 上面的格式 |
| `type` | 七选一：`functional` / `invariant` / `quality` / `performance` / `cost` / `governance` / `security` |
| `statement` | 一句话：“必须做到什么” |
| `fit_criterion` | **机器可验**的判据（命令/阈值/断言），门禁与测试照它写 |
| `priority` | MoSCoW：`must` / `should` / `could` / `wont`（**必须写清取舍**） |
| `tradeoff` | 这条需求换来了什么代价 |
| `source` | 来源证据：`文件:行`、课程原文、slide |

## 它和 `CHG` 的区别（关键）

| | 需求 ID（`D1-REQ-…`） | 变更（`CHG-…`） |
|---|---|---|
| 回答的问题 | **要满足什么** | **实现它的那一次变更** |
| 生命周期 | 长期稳定，一直存在 | 一次性：分支→PR→合并 |
| 数量关系 | 一条需求可被多条 CHG 迭代满足 | 一个 CHG 可实现多条需求 |

追踪链：
```
需求 ID → 变更卡 Related requirement → 提交 trailer Refs:
        → 测试里引用 → trace-matrix.md → review-memo.md
```
PR 里可以一次写多条，例如 `Refs: D1-REQ-COST-001, D1-REQ-PERF-001`。

一句话记住：**`D1-REQ-x` 是“需求的名字”，`CHG-x` 是“为它做的那次变更的名字”。**

文档已更新并仍被 `.gitignore` 忽略（不会进仓库）。

#### Human

```text
完整的需求讨论文档给我，我通读一遍
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/功能需求表-讨论稿.md`

old:
```text
*本文件为讨论稿；如要长期保留且不进仓库，可在 `.gitignore` 追加一行 `.opencode/功能需求表-讨论稿.md`。*
```
new:
```text
*本文件为讨论稿，已加入 `.gitignore`（`.opencode/功能需求表-讨论稿.md`），永不进仓库。*
```

Output:

```text
Edited .opencode/功能需求表-讨论稿.md (1 replacement)
```

#### Agent

这是完整文档（`.opencode/功能需求表-讨论稿.md`，已改成连续编号、含 `CHG` 与需求 ID 说明、已加入 `.gitignore`）：

---

# 新增功能需求表（讨论稿）

> **状态**：非正式、供团队讨论，**不提交**（仓库内交付物一律英文；本文件属仓库外中文讨论稿）。
> **依据**：CS5351 Requirement Sheet D1–D9 与第 6 节六道门禁、导论 Assessment 3 原文、以及仓库内《管理员/开发者手册》系列。
> **现状基线**：CHG-001（src 布局对齐）、CHG-002（治理骨架 + 第 1 批门禁 `gate-3/5/6`）已合并。
> **日期**：2026-10-07
> **怎么用**：Sprint 1 是后续所有功能的前置；先确认第 11 节“待拍板问题”再动工。

---

## 0. 背景与对齐

- 课程核心：**在可审计的人类监督下**，用 OpenCode 设计/构建/验证/维护一个含 AI 组件的应用。
- 项目定位：**增强** `TauricResearch/TradingAgents`（不重写）。课程原文点名两个痛点：
  1. **慢、烧 token**（分析单只股票成本高）；
  2. **子代理辩论过于自由散漫**（可引入需求工程方法，如 Osborn 头脑风暴法）。
- 更高分要求（导论“Higher Grade”）：需求/架构/治理能力更强、**生产级考量**、**更低 token 消耗**、低耦合高内聚、强可追溯。
- 因此本表同时覆盖两类需求：
  - **治理/工程规范类**（对齐 D1–D9 与六道门禁，含紧跟 CHG-002 的 `AGENTS.md`）；
  - **产品功能类**（对齐课程痛点与前沿工程化开源实践，具备求职与工程价值）。

---

## 1. 角色映射（建议，待群里确认）

| 角色 | GitHub | 说明 |
|---|---|---|
| 管理员 | `@JHB11Hinson` | 仓库基础设施、门禁上线、发布冻结；同时是开发者 |
| 组员1 | `@AKAScarlett` | 建议 |
| 组员2 | `@zihao9462-creator` | 建议 |
| 组员3 | `@SY1433` | 建议 |

> 映射可自由调换；调换后把下方表格的“负责人”整列同步即可。

---

## 2. 编号与约定

- **CHG 是什么**：`CHG` = **Change（变更）**，就是课程手册里的**变更卡编号 / Change ID**。每一次“同步 main → 开分支 → 登记需求 → 写计划并获批 → 测试先行 → 让 AI 写实现 → 开 PR → 评审合并”对应一个 CHG。它出现在分支名、提交信息 trailer（`Refs: CHG-020`）、PR 描述、`review-memo.md` 与 `docs/ai-use-log.yaml` 里，用来把“需求 / 架构决策 / 代码 / 测试 / 会话记录”串成一条**可审计的链路**。**全局唯一、只增不减、不复用**。
- **编号分配**：`CHG-001`（src 布局）、`CHG-002`（治理骨架 + 第 1 批门禁）已用；本稿从 **CHG-003 起连续编号**：
  - 管理员 `CHG-003 – CHG-008`（6 项）
  - 组员1 `CHG-009 – CHG-012`（4 项）
  - 组员2 `CHG-013 – CHG-016`（4 项）
  - 组员3 `CHG-017 – CHG-020`（4 项）
- **需求 ID 是什么 / 怎么填**：每一条需求在 `docs/req/requirements.yaml` 里的 `id:` 字段。本表统一格式 **`D1-REQ-<领域>-<三位序号>`**：
  - `D1`：固定前缀，表示这是 **D1 交付物**（machine-readable requirements registry）里的条目；用 `grep 'id: D1-REQ-'` 即可清点全部需求。
  - `REQ`：固定，表示 requirement 条目。
  - `<领域>`：类别代码，建议与 `req-schema.json` 的 `type` 对齐；同一大类下可按模块细分 —— `FUNC` 功能 / `INV` 不变量 / `QUAL` 质量 / `PERF` 性能 / `COST` 成本 / `GOV` 治理 / `SEC` 安全；细分例：`CTX` 上下文 / `MEM` 记忆 / `DEBATE` 辩论 / `OBS` 可观测性 / `EVAL` 评测。
  - `<三位序号>`：从 `001` 起、同类内递增；**不复用、不改号**（一旦被引用就保持稳定）。
  - 已存在示例：`D1-REQ-GOV-001`（仓库布局）；本表新增示例见第 8 节。
- **需求 ID 与 CHG 的关系**：两者是不同维度 —— **需求 ID = “要满足什么”**（长期稳定，可被多条 CHG 触碰）；**CHG = “实现它的那一次变更”**（一次性，带分支/PR/记录）。一个 CHG 可实现多条需求（PR 里写 `Refs: D1-REQ-COST-001, D1-REQ-PERF-001`），一条需求也可能由多条 CHG 迭代满足。追踪链：需求 ID → 变更卡 `Related requirement` → 提交 trailer `Refs:` → 测试引用 → `trace-matrix.md` → `review-memo.md`。
- **工时**：单位为人时，仅用于估算与贡献度对齐，动工前可微调。
- **判据**：尽量写成**机器可验**的 fit criterion（供 D1 需求登记册与门禁使用）。
- **纪律**：每条工作包开分支 `feat|gov|ci/<CHG号>-...`，走 PR，测试先行，更新 `docs/ai-use-log.yaml`。

---

## 3. 管理员（`@JHB11Hinson`）— 工程规范 / 门禁 / 发布 / 可观测性（约 68h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据（fit criterion） | 工程 / 求职价值 |
|---|---|---|---|---|---|
| **CHG-003** | **AGENTS.md 工程总纲**（紧跟 CHG-002 的第一件事） | `AGENTS.md` (D3) | 12 | >200B；含 build target、架构工件阅读顺序、code baseline、可读/可改/冻结清单、模块组织、模块间集成契约、生成代码必须满足的验证要求、human-only 文件与 STOP 点；团队评审 APPROVE | Agent 治理、规范编写 |
| CHG-004 | 架构主约束 + 结构约束 | `architecture-blueprint.md` 完整化 (D2.1)、`docs/code-governance/structural-constraints.md` (D3) | 10 | 含 scope / drivers / boundaries / authority / workflow / permissions / verification / observability / change policy；模块与架构元素一一对应 | 架构设计（SA） |
| CHG-005 | 权限模型与运行策略 | `permission-model.md` (D2.6)、`runtime-policy-catalog.md` (D2.7)、`.opencode/permissions.jsonc`、`.opencode/rules.md`、`.agent/rules.md`、`mcp-tool-manifest.md` | 12 | 默认拒绝、逐路径白名单；规则被 agent 实际读取生效 | AI 安全边界、权限工程 |
| CHG-006 | 门禁分批上线 + 分支保护终态 | `ci.yml` 第 2/3/4 批、`docs/code-governance/protection.json` | 12 | 六道门禁名与 `contexts` 一字不差；每道**故意红过一次**；直推 `main` 被拒 | CI/CD、分支保护、发布 |
| CHG-007 | 运行时可观测性与成本计量 | run manifest + 结构化 trace + 成本/时延汇总 | 14 | 一次运行产出可解析 trace JSON；token/成本/耗时可按阶段汇总 | LLM 可观测性（OTel 风格） |
| CHG-008 | 追溯矩阵与冻结发布 | `trace-matrix.md` (D2.4)、需求登记册维护、`review-memo.md` 汇总、评审排班、贡献度统计、冻结 tag | 8 | 每条需求→组件→测试→运行时监控可查；冻结 tag 已推 | 可追溯性、项目管理 |

---

## 4. 组员1（`@AKAScarlett`）— 结构化辩论与质量控制（约 60h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据 | 价值 |
|---|---|---|---|---|---|
| CHG-009 | **结构化辩论协议**：限定轮次 + 主张/证据/反驳结构 + Osborn 式先发散后收敛 | 辩论模块改造 | 20 | 轮次 ≤ 上限；输出结构化（claim/evidence/rebuttal/confidence）；质量指标 ≥ 基线 | 多智能体编排、Prompt 工程 |
| CHG-010 | **终止纪律**：振荡/停滞/预算耗尽检测，防死循环 | 终止判定模块 | 8 | 构造振荡用例能自停；含负向测试 | Agent 稳定性 |
| CHG-011 | 提示词版本化 + 辩论质量评测 | `prompts/prompt_v1.x.yaml`、质量指标与用例 | 14 | 改提示词触发 `gate-4`；指标可复现 | Prompt 版本治理、LLM 评测 |
| CHG-012 | 不变量 / 评测表 / 债务登记 | `invariants.md` (D2.3)、`evaluation-table.md` (D2.8)、`debt-register.md` (D4) | 10 | 每条不变量有来源需求、执行组件、验证方法、回退动作 | QA、不变量设计 |
| — | 亲手让某道门禁红一次 + 评审他人 PR | 记录 | 8 | `review-memo.md` 里有 APPROVE 记录 | 代码评审 |

---

## 5. 组员2（`@zihao9462-creator`）— 上下文工程与成本（约 58h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据 | 价值 |
|---|---|---|---|---|---|
| CHG-013 | **分层上下文结构 + 装配管线**（identity / standing constraints / retrieved knowledge / history / resumable state / current task；dedupe→prioritize→budget→compact→assemble） | 上下文模块 | 18 | 结构可配置；装配单测通过 | Context Engineering、RAG 基础 |
| CHG-014 | **Token 预算守卫**：预算上限 + 压缩阈值 + 压缩后重注入关键约束 | 预算守卫模块 | 12 | 超预算触发压缩；压缩后关键约束断言仍在；总 token ≤ 阈值 | 成本优化（课程加分项） |
| CHG-015 | LLM / 数据缓存层 | 缓存模块 + 命中率统计 | 10 | 重复运行命中缓存；节省率可量化 | 性能、缓存设计 |
| CHG-016 | 记忆设计 + 评测台账 + **eval 框架** | `memory-design.md` (D2.5)、`evaluation-logbook.md` (D2.9)、`eval/{fixed-set.json,thresholds.yaml,run.py}` | 12 | 本地 `python -m eval.run` 跑通并输出阈值判定（供 `gate-4` 用） | LLM Evals |
| — | 门禁红实验 + 评审 | 记录 | 6 | `review-memo.md` 里有 APPROVE 记录 | — |

---

## 6. 组员3（`@SY1433`）— 记忆、安全与评测（约 58h）

| 编号 | 工作包 | 交付物 | 工时 | 验收判据 | 价值 |
|---|---|---|---|---|---|
| CHG-017 | **决策记忆语义检索（RAG）**：历史决策/反思 embedding + 检索相关条目注入（跨 ticker 学习） | 记忆检索模块 | 18 | 正/负检索用例通过；注入内容可追溯来源 | RAG/向量检索、Reflexion |
| CHG-018 | **安全边界与确定性护栏**：检索文本防注入清洗 + 决策 schema 校验 + 交易规模确定性上限拦截 | 护栏模块 | 16 | 对抗注入样本 100% 拦截（负向测试必红）；非法决策被拒并降级 | LLM 安全 / Guardrails（课程“安全边界”要求） |
| CHG-019 | 回测 / 消融对比（有 / 无新功能） | 对比数据与图表 | 10 | 可复现对比表（成本/时延/通过率/质量） | 实验设计、量化评估 |
| CHG-020 | 选项台账 + 风险清单 | `option-ledger.md` (D2.11)、`risk-list.md` (D2.10) | 8 | 被拒方案与再评估触发条件成文 | 架构决策 |
| — | 门禁红实验 + 评审 | 记录 | 6 | `review-memo.md` 里有 APPROVE 记录 | — |

---

## 7. 工时汇总（均衡性）

| 角色 | 工时 | 相对贡献（÷均值） |
|---|---|---|
| 管理员 | 68 | ≈ 1.12 |
| 组员1 | 60 | ≈ 0.99 |
| 组员2 | 58 | ≈ 0.96 |
| 组员3 | 58 | ≈ 0.96 |
| **合计** | **244** | 均值 ≈ 61 |

> 管理员略多，落在“设计门禁 / 上线 / 发布 / 可观测性”一侧。

---

## 8. 非功能需求（NFR：metric + threshold + verification）

写入 `docs/req/requirements.yaml`，供 `gate-3-schema` 校验、`gate-4` 评测。

| 需求 ID | 类型 | 指标 → 阈值 | 验证方式 |
|---|---|---|---|
| D1-REQ-COST-001 | cost | 单次分析 token / 成本 ≤ 基线 50% | eval 固定集汇总 |
| D1-REQ-PERF-001 | performance | wall-clock ≤ 基线 60% | 固定集重复取中位数 |
| D1-REQ-QUAL-001 | quality | 结构化输出通过率 100%；辩论证据引用率 ≥ 基线 | schema 校验 + 评测指标 |
| D1-REQ-SAFE-001 | security / invariant | 注入样本拦截率 100%；交易规模不超确定性上限 | 负向测试（零容忍） |
| D1-REQ-CTX-001 | invariant | 装配后上下文 ≤ 预算；压缩后关键约束仍在 | 装配单测断言 |
| D1-REQ-GOV-002 | governance | AGENTS.md 覆盖 6 个必需小节 | 评审 checklist |

> **怎么填一条**（写入 `docs/req/requirements.yaml`，字段以 `docs/req/req-schema.json` 为准）：
>
> ```yaml
> - id: D1-REQ-COST-001
>   type: cost
>   statement: A single analysis run must spend no more than half of the baseline tokens and estimated cost.
>   fit_criterion: python -m eval.run over eval/fixed-set.json reports total_tokens <= 0.5 * baseline and est_cost <= 0.5 * baseline.
>   priority: must
>   tradeoff: Aggressive compaction can drop evidence the debaters rely on; quality must stay at or above baseline.
>   source: project brief section 5 / D1; intro slide "Assessment 3" (slow and token-burning)
> ```
>
> 字段含义：`id` 命名见第 2 节；`type` 七选一（functional / invariant / quality / performance / cost / governance / security）；`statement` 一句话说清“必须做到什么”；`fit_criterion` 给**机器可验**的判据；`priority` 用 MoSCoW（must / should / could / wont）；`tradeoff` 写取舍；`source` 写来源证据（`文件:行`、课程原文、slide）。

---

## 9. 对标的前沿开源实践（“对齐前沿工程化开源项目”）

| 方向 | 本项目落点 | 对标 |
|---|---|---|
| 可观测性 / tracing | CHG-007 trace（span / 成本 / 时延） | OpenTelemetry GenAI、Langfuse / LangSmith |
| LLM 评测 | CHG-011 / CHG-016 + `gate-4` | promptfoo、DeepEval、OpenAI Evals |
| 安全护栏 | CHG-018 | NeMo Guardrails、Guardrails AI |
| 语义缓存 | CHG-015 | GPTCache |
| 结构化输出 | CHG-018 schema 校验 | Pydantic / instructor / Outlines |
| 反思式记忆 | CHG-017 | Reflexion（arXiv 2303.11366）、mem0 |

---

## 10. 里程碑（波次）

| 波次 | 内容 | 出口标志 |
|---|---|---|
| **Sprint 1 · 治理地基** | CHG-003 → CHG-008 + `Prompt.md`；门禁第 2 批上线。**此波不写产品功能** | AGENTS.md / 蓝图 / 权限模型就绪；门禁第 2 批上线并故意红过 |
| **Sprint 2 · 三条主线首版** | CHG-009 / 013 / 017 + CHG-007 可观测性 | 三条主线可运行、有单测 |
| **Sprint 3 · 质量与安全** | CHG-010 / 014 / 018 / 011 / 015 | 终止纪律、预算守卫、护栏、评测接入 |
| **Sprint 4 · 评测与收尾** | CHG-012 / 016 / 020 / 019 + 门禁第 3/4 批 + 冻结发布 + `Report.md` / 演示视频 | 六道门禁齐全；冻结 tag；对比数据齐 |

---

## 11. 待团队拍板的问题

1. **组员1/2/3 分别对应哪位同学**及其 GitHub 账号？（第 1 节先给建议）
2. 四条产品主线是否全做，还是砍到三条（YAGNI）？尤其缓存 CHG-015 的收益/成本。
3. **评测是否真的调用 LLM**（花钱）：谁提供 key / 预算、Actions Secrets 怎么配。
4. **依赖政策**：语义检索用轻量 numpy 余弦（零新依赖）还是引入 faiss/chromadb？需与 `.agent/rules.md` 依赖约束一致。
5. `AGENTS.md` / 安全护栏是否划为**安全关键路径**（改动需 ADR + 人工评审）？
6. sprint 长度、冻结与拍摄演示视频的时间点。

---

## 12. 附：课程交付物覆盖核对表

| 交付物 / 工件 | 负责人 | 对应工作包 |
|---|---|---|
| D1 `requirements.yaml` + `req-schema.json` | 管理员（全员补条目） | CHG-008 + 各工作包 |
| D2.1 蓝图 | 管理员 | CHG-004 |
| D2.2 ADR（新增决策） | 各功能 owner | CHG-009/013/017/018 |
| D2.3 invariants | 组员1 | CHG-012 |
| D2.4 trace-matrix | 管理员 | CHG-008 |
| D2.5 memory-design | 组员2 | CHG-016 |
| D2.6 permission-model | 管理员 | CHG-005 |
| D2.7 runtime-policy-catalog | 管理员 | CHG-005 |
| D2.8 evaluation-table | 组员1 | CHG-012 |
| D2.9 evaluation-logbook | 组员2 | CHG-016 |
| D2.10 risk-list | 组员3 | CHG-020 |
| D2.11 option-ledger | 组员3 | CHG-020 |
| D3 AGENTS.md / structural-constraints / mcp-tool-manifest / permissions.jsonc / rules.md / .agent/rules.md | 管理员 | CHG-003/004/005 |
| D4 verification-constraints | 管理员 | CHG-006 |
| D4 review-memo / debt-register / bug-diary | 全员（各自维护） | 随各 PR |
| D5 transcripts | 全员（每人至少一份） | 随各工作包 |
| D6 Report.md | 管理员汇总 | Sprint 4 |
| D7 六道门禁 + 分支保护 | 管理员 | CHG-006 |
| D8 src / test 布局 | 已完成 | CHG-001 |
| D9 Prompt.md | 管理员 | Sprint 1 |
| 门禁 1–6 | 管理员上线，全员各红一次 | CHG-006 |

---

*本文件为讨论稿，已加入 `.gitignore`（`.opencode/功能需求表-讨论稿.md`），永不进仓库。*

---

通读时重点关注两处，它们最影响后续落地：
1. **第 1 节的角色映射**——组员1/2/3 是否就按现在的建议值；
2. **第 11 节第 2 条**——四条产品主线是否全做（尤其是否砍掉 CHG-015 缓存）。

需要调整任何一处，或把它拆成每人一份任务书 / 生成对应的 `requirements.yaml` 草案，告诉我即可。

#### Human

```text
哦对了，看看开发者手册对齐了吗？有无和现在的仓库过时和错误内容，可以的话我发给组员们
```

#### Agent

好主意——发给组员前先做一次“手册 vs 当前仓库”的一致性审计。我先把手册读完，再逐条核对仓库实际状态。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "=== git log (last 8) ==="; git log --oneline -8
echo; echo "=== 关键文件是否存在 ==="
for f in AGENTS.md Prompt.md Report.md architecture-blueprint.md docs/req/requirements.yaml docs/req/req-schema.json docs/ai-use-log.yaml docs/review-memo.md docs/debt-register.md docs/bug-diary.md docs/code-governance/structural-constraints.md docs/code-governance/verification-constraints.md docs/code-governance/mcp-tool-manifest.md docs/code-governance/protection.json docs/architecture/adr/001-adopt-inherited-architecture.md docs/architecture/adr/002-src-layout.md .opencode/permissions.jsonc .opencode/rules.md .agent/rules.md .github/CODEOWNERS .github/PULL_REQUEST_TEMPLATE.md .gi
... [truncated 423 chars]

Output:

```text
=== git log (last 8) ===
7c3eb5a ci: CHG-002 bring gate batch 1 online (schema + regression + AI use log) (#2)
a21ec80 chore: CHG-001 align src layout (D8) (#1)
580e81b chore: add CODEOWNERS and the PR template
1558988 chore: initialise the project skeleton and add CODEOWNERS
1394a3f Merge pull request #1478 from TauricResearch/v0.6.0
ff0d0b1 release: 0.6.0
dca93d5 docs: show the Tauric Research logo from the SVG the report uses
f723824 fix(tools): send a start date that is not a date back to the model (#1476)

=== 关键文件是否存在 ===
OK   AGENTS.md                                                    0 B
OK   Prompt.md                                                    0 B
OK   Report.md                                                    0 B
OK   architecture-blueprint.md                                    786 B
OK   docs/req/requirements.yaml                                   551 B
OK   docs/req/req-schema.json                                     733 B
OK   docs/ai-use-log.yaml                                         1258 B
OK   docs/review-memo.md                                          1876 B
MISS docs/debt-register.md
MISS docs/bug-diary.md
MISS docs/code-governance/structural-constraints.md
MISS docs/code-governance/verification-constraints.md
MISS docs/code-governance/mcp-tool-manifest.md
MISS docs/code-governance/protection.json
OK   docs/architecture/adr/001-adopt-inherited-architecture.md    3831 B
OK   docs/architecture/adr/002-src-layout.md                      1757 B
MIS
... [truncated 634 chars]
```

#### Agent

手册已读完。现在跑一批核对命令（测试数量、test/live 内容、pyproject、README 的命令、工具可用性等）。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== pyproject.toml ====="; cat pyproject.toml
echo; echo "===== test 目录 ====="; find test -name 'test_*.py' -not -path '*__pycache__*' | sort
echo "offline 文件数: $(find test/offline -name 'test_*.py' -not -path '*__pycache__*' | wc -l)"
echo "live 文件数: $(find test/live -name '*.py' -not -path '*__pycache__*' | wc -l)"
echo; echo "===== test/live 内容 ====="; ls -la test/live
echo; echo "===== mypy 配置? ====="; ls mypy.ini setup.cfg 2>&1 | head; grep -n "mypy" pyproject.toml || echo "pyproject 无 mypy 配置"
echo; echo "===== README 里的测试命令 ====="; grep -n "pytest" README.md | head -20
echo; echo "===== CODEOWNERS ====="; cat .github/CODEOWNERS
echo; echo "===== open
... [truncated 52 chars]

Output:

```text
===== pyproject.toml =====
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[project]
name = "tradingagents"
dynamic = ["version"]
description = "TradingAgents: Multi-Agents LLM Financial Trading Framework"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "langchain-core>=1.6.5",
    "langchain-anthropic>=1.7.4",
    "langchain-google-genai>=4.4.0",
    "langchain-openai>=1.6.6",
    "langgraph>=1.2.12",
    "langgraph-checkpoint-sqlite>=3.1.1",
    "markdown-it-py>=4.0",
    "pandas>=3.0.6",
    "python-dotenv>=1.0.0",
    "pytz>=2025.2",
    "questionary>=2.1.0",
    "requests>=2.32.4",
    "rich>=14.0.0",
    "typer>=0.21.0",
    "stockstats>=0.6.5",
    "typing-extensions>=4.14.0",
    "yfinance>=1.7.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.16",
    "pytest>=8.0",
    "pytest-subtests>=0.13",
]
# Amazon Bedrock support (AWS SigV4 auth + boto3). Optional so the core install
# stays lean: pip install "tradingagents[bedrock]".
bedrock = [
    "langchain-aws>=1.7.9",
]

[project.scripts]
tradingagents = "cli.main:app"

[tool.setuptools.dynamic]
version = {attr = "tradingagents.__version__"}

[tool.setuptools.packages.find]
where = ["src"]
include = ["tradingagents*", "cli*"]

[tool.setuptools.package-data]
cli = ["static/*"]
tradingagents = ["assets/*.svg"]

[tool.pytest.ini_options]
testpaths = ["test/offline"]
pythonpath = ["src"]
addopts = "-ra --strict-markers -m \"not integration\""
markers = [
... [truncated 5087 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== dev 工具是否安装 ====="; ls .venv/bin/ | grep -E '^(ruff|mypy|pytest|check-jsonschema)$' || true
echo "ruff: $(.venv/bin/ruff --version 2>&1 | head -1)"
echo "mypy: $(.venv/bin/mypy --version 2>&1 | head -1)"
echo "check-jsonschema: $(.venv/bin/check-jsonschema --version 2>&1 | head -1)"
echo; echo "===== test 全部文件（含 conftest） ====="; find test -type f -not -path '*__pycache__*' | wc -l
echo; echo "===== 3 个曾改路径的测试现状 ====="; sed -n '8,16p' test/offline/test_version.py; echo '---'; sed -n '10,16p' test/offline/test_layering.py; echo '---'; sed -n '13,17p' test/offline/test_i18n_coverage.py
echo; echo "===== 跑 pytest -q（约十几秒） ====="; .venv/bin/pytest -q 2>&1 |
... [truncated 8 chars]

Output:

```text
===== dev 工具是否安装 =====
check-jsonschema
pytest
ruff
ruff: ruff 0.16.10
mypy: /bin/bash: 行 4: .venv/bin/mypy: 没有那个文件或目录
check-jsonschema: check-jsonschema, version 0.38.2

===== test 全部文件（含 conftest） =====
87

===== 3 个曾改路径的测试现状 =====
import tradingagents

PYPROJECT = (Path(__file__).resolve().parents[2] / "pyproject.toml").read_text(encoding="utf-8")


@pytest.mark.unit
def test_the_build_reads_the_version_from_the_package():
    assert re.search(r'^dynamic = \["version"\]', PYPROJECT, re.M)
    assert 'version = {attr = "tradingagents.__version__"}' in PYPROJECT
---
import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
VENDOR_LIBRARIES = {"yfinance"}


---
from tradingagents.agents.context import get_language_instruction

_AGENTS_DIR = Path(__file__).resolve().parents[2] / "src" / "tradingagents" / "agents"

# Every node whose text reaches the saved report. If you add a report-producing

===== 跑 pytest -q（约十几秒） =====

test/offline/test_openai_reasoning_effort.py::test_non_reasoning_model_drops_effort
test/offline/test_temperature_config.py::TestTemperatureForwarding::test_temperature_reaches_client_when_set[openai-gpt-4.1]
test/offline/test_temperature_config.py::TestTemperatureForwarding::test_temperature_omitted_leaves_provider_default
  /home/jhb/TradingAgents/src/tradingagents/llm_clients/openai_client.py:279: RuntimeWarning: Model 'gpt-4.1' is not in the known model list for provider 'openai'. Continuing anyway.
    self.warn_if_unknown_model()

t
... [truncated 709 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== ruff check src（全量，看是否绿） ====="; .venv/bin/ruff check src 2>&1 | tail -8
echo; echo "===== 哪个是 deselected 的 integration 测试 ====="; .venv/bin/pytest --collect-only -q -m integration 2>&1 | tail -8
echo; echo "===== test/offline 里是否有需要密钥/网络的用例 ====="; grep -rln "API_KEY\|api_key\|os.environ\|getenv\|monkeypatch.setenv" test/offline | head -30
echo; echo "计数: $(grep -rln 'API_KEY\|api_key\|getenv' test/offline | wc -l) 个文件提到 key/getenv"
echo; echo "===== 是否有 integration 标记 ====="; grep -rn "mark.integration" test/offline | head

Output:

```text
===== ruff check src（全量，看是否绿） =====
All checks passed!

===== 哪个是 deselected 的 integration 测试 =====
test/offline/test_deepseek_reasoning.py::TestDeepSeekLiveStructuredOutput::test_v4_flash_returns_structured_output

1/1264 tests collected (1263 deselected) in 1.70s

===== test/offline 里是否有需要密钥/网络的用例 =====
test/offline/test_cli_env_skip.py
test/offline/test_google_api_key.py
test/offline/test_fred.py
test/offline/test_llm_max_tokens.py
test/offline/test_ollama_base_url.py
test/offline/test_get_scrubbed.py
test/offline/test_llm_max_retries.py
test/offline/test_google_thinking_level.py
test/offline/test_cli_headless.py
test/offline/test_api_key_env.py
test/offline/test_sec_edgar.py
test/offline/test_tier_providers.py
test/offline/test_env_overrides.py
test/offline/test_anthropic_effort.py
test/offline/test_openai_compatible_provider.py
test/offline/conftest.py
test/offline/__pycache__/test_bedrock_provider.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_alpha_vantage_hardening.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_minimax.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_fred.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_cli_config_precedence.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_anthropic_effort.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_llm_max_tokens.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_post_screen.cpython-312-pytest-9.1.1.pyc
test/offline/__pycache__/test_get_scru
... [truncated 555 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== opencode 版本 ====="; timeout 20 opencode --version 2>&1 | head -3
echo; echo "===== opencode 顶层命令 ====="; timeout 20 opencode --help 2>&1 | sed -n '1,60p'
echo; echo "===== 试探 session/export 子命令 ====="; timeout 20 opencode session --help 2>&1 | head -20; echo '---'; timeout 20 opencode export --help 2>&1 | head -20

Output:

```text
===== opencode 版本 =====
opencode v2.0.18

===== opencode 顶层命令 =====
DESCRIPTION
  OpenCode command line interface

USAGE
  opencode <subcommand> [flags] [<directory>]

ARGUMENTS
  directory string    Directory to start OpenCode in (optional)

FLAGS
  --standalone            Run with a private server
... [truncated 3870 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== session export --help ====="; timeout 20 opencode session export --help 2>&1
echo; echo "===== session list --help ====="; timeout 20 opencode session list --help 2>&1 | head -25

Output:

```text
===== session export --help =====
DESCRIPTION
  Export session data as JSON

USAGE
  opencode session export [flags] [<session>]

ARGUMENTS
  session string    Session ID to export (optional)

FLAGS
  --standalone       Run with a private server instead of the background service
  --server string
... [truncated 2047 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== test/ 下非 test_*.py 文件 ====="; find test -type f -not -path '*__pycache__*' ! -name 'test_*.py'
echo; echo "===== README 是否提到测试命令（不分大小写） ====="; grep -in "pytest\|test/offline\|test/live\|run the tests" README.md | head
echo; echo "===== README 是否还是上游内容（看标题） ====="; grep -n "TauricResearch\|Check out the CLI\|Contributing" README.md | head
echo; echo "===== 手册提到的工程/架构工件是否已在仓库 ====="; ls docs/architecture/ 2>&1; ls prompts/ 2>&1

Output:

```text
===== test/ 下非 test_*.py 文件 =====
test/offline/__init__.py
test/offline/conftest.py
test/live/.gitkeep

===== README 是否提到测试命令（不分大小写） =====

===== README 是否还是上游内容（看标题） =====
8:  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
9:  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
13:  <a href="https://github.com/TauricResearch" target="_blank"><img alt="TradingAgents #1 Repository of the Day" src="https://trendshift.io/api/badge/repositories/16192" width="250" height="55"/></a>
18:  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> |
19:  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> |
20:  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> |
21:  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> |
22:  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> |
23:  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> |
24:  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> |

===== 手册提到的工程/架构工件是否已在仓库 =====
adr
```

#### Agent

审计完成。我把《开发者手册》逐条对照了当前仓库（OpenCode v2.0.18、`pytest -q` 实跑、文件树、git 历史）。**结论：主干流程准确，可以发；但有 3 处“照着做会失败”的硬错误、2 处已过时/会误导的地方，建议先修再发。**

## A. 硬错误（照做会失败或误解）

| # | 位置 | 问题 | 正确做法 |
|---|---|---|---|
| A1 | §6.3 会话导出 | 写的 `opencode export <sessionID> --sanitize`。当前是 **v2.0.18**，`export` 是 `session` 的子命令，这条会失败 | `opencode session export <sessionID> --sanitize > /tmp/session.json`（`opencode session list` 是对的） |
| A2 | §3.6 / §3.7 / §7.2 / §8.4 / §9.5 | 让人跑 `mypy src`，但 `[dev]` 依赖里**没有 mypy**，仓库也无 mypy 配置 → `mypy: command not found` | 要么在第 2 批门禁时把 mypy 加进 `[dev]` 并补 `mypy.ini`，要么这几处先删掉 mypy |
| A3 | §2.3 与 §3.6 等 | 三条测试命令口径错：仓库 `testpaths=["test/offline"]`，所以 **`pytest -q` 只跑离线**，手册却把它标成“全量”；而 §3.6 又用 `pytest -q test/` 当“回归” | 离线=`pytest -q`（或 `test/offline`）；实时=`pytest -q test/live`；**全量=`pytest -q test/`**；回归应对齐 gate-5，用 `pytest -q` |

> A3 现在因为 `test/live/` 是空目录，两者结果一样（都是 1262 passed / 1 skipped / 1 deselected，已实测），所以今天不会立刻炸；但等 live 有测试就会踩坑。

## B. 已过时（事情已发生，手册还是“将来式”）

| # | 位置 | 问题 |
|---|---|---|
| B1 | §2 / §2.2 | 把 src 结构对齐写成“**要发生**的一次性对齐”。实际 **CHG-001 已合并**：`src/tradingagents`、`src/cli`、`test/offline`、`test/live` 都已就位，3 个测试文件已是 `parents[2]`（我逐一核过）。手册读起来像还没做 |
| B2 | §0.4 / §4.7 / §9.5 | 把“六道门禁”当既成事实。实际**只有第 1 批 `gate-3/5/6` 在线**，`gate-1/2/4` 还没上。新人按手册去找 `gate-1-test-approval` 会找不到，也没说明分批计划 |

## C. 内部口径冲突

| # | 位置 | 问题 |
|---|---|---|
| C1 | §2.4 vs §3.6/§3.7/§8.4 | §2.4 说静态分析“**只查本 PR 改动的文件**”，但后面又让人跑全量 `ruff check src && mypy src`。（全量 ruff 现在恰好是绿的 `All checks passed!`，所以今天不炸；但策略自相矛盾，改动继承代码后就会爆量） |

## D. 仓库缺口（手册假设“已完成”，其实没有——发之前最好让组员知道）

| # | 手册假设 | 实际 |
|---|---|---|
| D1 | §2.2/§2.3：需要 API 的测试进 `test/live/` | **没有真正分开**：`test/live/` 是空的；唯一需要 API 的用例 `test_deepseek_reasoning.py::TestDeepSeekLiveStructuredOutput::test_v4_flash_returns_structured_output` 仍在 `test/offline/`（靠 `-m "not integration"` 被 deselect）。D8 的“物理分开”未落实 |
| D2 | §2.3：README 要写清三条测试命令 | README 里 **`pytest` 一次都没出现**，且 README 基本还是上游原文（D7 未做） |
| D3 | 多处在 `git add`/引用 `docs/architecture/trace-matrix.md`、`docs/code-governance/*`、`.opencode/permissions.jsonc`、`.opencode/rules.md`、`.agent/rules.md`、`prompts/*` | 这些文件**尚不存在**（属未来交付物，`docs/architecture/` 现在只有 `adr/`） |

## E. 小瑕疵（不影响使用）

- §4.4 示例 `source: src/agents/analyst.py:42` 不存在（真实路径是 `src/tradingagents/agents/analysts/...`）。
- 会话记录命名：手册用 `transcripts/<学号>-<姓名>.md`、示例 `12345678-AKAScarlett.md`；仓库现有 `transcripts/JHB11Hinson.md`（GitHub 名，无学号）。建议统一。
- 分支名大小写不一：§3.3 `feat/chg-014-...` vs §4.6 `feat/CHG-014-...`。
- “86 个测试文件”= 84 个 `test_*.py` + `conftest.py` + `__init__.py`；`1262 passed` 完全正确，可忽略。

---

**给组员的结论**：流程部分（日常七步、四类变更、六道门禁设计、评审六项、会话/日志、提交 trailer、密钥纪律）都没问题，**可以发**；但建议先修 A1–A3 三条硬错误，并在 §0.4 补一句“当前只有第 1 批门禁在线，2–4 批分批上线”，再发。

要我把上述 A/B/C 的修正**直接落进 `开发者手册.md`** 吗？（它也受 `.gitignore` 的 `.opencode/manual/` 保护，不会被提交。）另外，`开局清单核查指南.md` 也明显过时（它写“阶段 2 未开始”，而 CHG-001/002 已合并）——要不要一并审？

#### Human

```text
全部修复一下
```

#### Agent

明白，全部修。先精确定位《开发者手册》里所有需要改的原文。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "===== mypy ====="; grep -n "mypy" 开发者手册.md
echo; echo "===== pytest -q test/ ====="; grep -n "pytest -q test/\|pytest -q\b" 开发者手册.md
echo; echo "===== opencode export ====="; grep -n "opencode export\|opencode session" 开发者手册.md
echo; echo "===== 结构对齐未来式 ====="; grep -n "要发生\|先落两份决策记录\|已实测：有 3 个继承测试文件\|86 个文件\|86个文件" 开发者手册.md
echo; echo "===== 门禁六道表述 ====="; grep -n "六道门禁\|六道阻塞\|六道" 开发者手册.md
echo; echo "===== 示例路径 / 分支大小写 ====="; grep -n "src/agents/analyst.py\|feat/chg\|feat/CHG\|chg-XXX\|12345678-AKAScarlett" 开发者手册.md

Output:

```text
===== mypy =====
93:| **2 静态分析** | 代码风格、类型、依赖 | `ruff` / `mypy` 报错 |
1057:ruff check src && mypy src      # 结构层
1063:| **结构层** | `ruff check src && mypy src` | 无新增违规；模块边界与架构元素一致 |
1101:ruff check src && mypy src                              # 静态检查
1660:ruff check src && mypy src
1788:| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `ruff check src && mypy src`，**让 AI 改**（不要手改） |
1880:| **静态分析** | 不运行代码，只"看"代码有没有风格问题、类型错误（`ruff`、`mypy`） |

===== pytest -q test/ =====
195:**如果 `pytest -q` 冒出一批 `ImportError: Using SOCKS proxy, but the 'socksio' package is not installed`**（约 31 个用例，堆栈里能看到 `proxy = Proxy('socks5://127.0.0.1:7890')`）：
199:pytest -q                          # 期望：1262 passed, 1 skipped, 1 deselected
210:| 想临时绕开 | `env -u ALL_PROXY -u all_proxy -u HTTPS_PROXY -u https_proxy pytest -q` |
867:pytest -q                    # 继承套件现在必须全绿；不绿先记进 docs/bug-diary.md
868:time pytest -q               # 记下耗时（门禁 5 每次都要跑它）
902:README 要写清的三条命令：`pytest -q test/offline`（离线）、`pytest -q test/live`（实时，要密钥）、`pytest -q`（全量）。
1058:pytest -q test/                 # 回归层
1064:| **回归层** | `pytest -q test/` | **此前所有测试零回归**（以前能过的现在还得能过） |
1103:pytest -q test/                                         # 回归
1507:pytest -q test/
1661:pytest -q test/
1700:pytest -q test/
1791:| `gate-5-regression` | 有测试挂了 | 本地 `pytest -q test/` 复现，修到零回归 |

===== opencode export =====
1391:opencode session list
1394:opencode export <sessionID> --sanitize > /tmp/session.json

===== 结构对齐未来式 =====
20:  - [2.2 要发生的一次性结构对
... [truncated 1109 chars]
```

#### Agent

现在开始改。先读几处需要重写的原文，确保替换精确：

#### Agent

开始逐处修复。第 1 组（§0.4 门禁状态、§2 结构对齐改为已完成）：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| **6 AI 使用日志** | 改了代码/提示词就必须更新日志 | 漏了 `docs/ai-use-log.yaml` |
```
new:
```text
| **6 AI 使用日志** | 改了代码/提示词就必须更新日志 | 漏了 `docs/ai-use-log.yaml` |

> **当前状态（2026-10）**：第 1 批 `gate-3-schema`、`gate-5-regression`、`gate-6-ai-use-log` **已上线**；`gate-1-test-approval`、`gate-2-static-analysi
... [truncated 79 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
- [2.2 要发生的一次性结构对齐](#22-要发生的一次性结构对齐管理员做你们只需知道结果)
```
new:
```text
- [2.2 已完成的一次性结构对齐](#22-已完成的一次性结构对齐管理员已做你们只需知道结果)
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
继承代码**不改逻辑**，只做一次结构对齐，然后才是增量功能。
```
new:
```text
继承代码**不改逻辑**；结构对齐（CHG-001）**已完成并合并**，之后才是增量功能。
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| 继承测试套件 | 86 个文件：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~12 秒（Python 3.12.14，干净 venv） |
```
new:
```text
| 继承测试套件 | 84 个测试模块（连同 `conftest.py`／`__init__.py` 共 86 个 Python 文件）：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~11 秒（Python 3.12.14，干净 venv，实测） |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
## 2.2 要发生的一次性结构对齐（管理员做，你只需知道结果）
```
new:
```text
## 2.2 已完成的一次性结构对齐（管理员已做，你只需知道结果）
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
所以管理员必须**同时**改几处配置/文档。
```
new:
```text
所以这次对齐**同时**改了多处配置与文档（CHG-001，已合并）。
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

#### Agent

第 2 组（§2.2 正文、§2.3 测试命令、§4.2 状态说明、§6.3/§6.4 会话相关）：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| 上游 | 变成 | 对你的影响 |
```
new:
```text
| 上游 | 现在是 | 对你的影响 |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
**已实测**：有 **3 个**继承测试文件用 `parents[1]` 找仓库根，搬目录后要改成 `parents[2]`（`test_i18n_coverage.py` 还要多插一层 `src`）——**只改路径解析，不动断言**。另外 `tests/__init__.py` 的存在曾让 pytest 把仓库根插进 `sys.path`；搬完 basedir 变成 `test/`，所以**不
... [truncated 43 chars]
```
new:
```text
**已实测并已完成**：那次搬迁只改了 **3 个**继承测试文件的路径解析（`test_version.py`、`test_layering.py`、`test_i18n_coverage.py`，把 `parents[1]` 改成 `parents[2]`，其中一个多插一层 `src`）——**没动任何断言**。另外 `test/offline/__init__.py` 的存在会让 pytes
... [truncated 292 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
先落两份决策记录：**ADR-001 采纳继承基线**（扩展而非重写）、**ADR-002 src layout 对齐**（见《管理员开局清单》步骤 1-5 与 2-3）。
```
new:
```text
**ADR-001**（采纳继承基线，扩展而非重写）与 **ADR-002**（src layout 对齐）**已写入仓库**：`docs/architecture/adr/`。
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
README 要写清的三条命令：`pytest -q test/offline`（离线）、`pytest -q test/live`（实时，要密钥）、`pytest -q`（全量）。
```
new:
```text
README 要写清的三条命令（注意 `pyproject.toml` 的 `testpaths` 已设为 `test/offline`）：

- **离线**：`pytest -q`（等价 `pytest -q test/offline`；门禁 5 跑的就是它）
- **实时**（要密钥）：`pytest -q test/live`
- **全量**：`pytest -q test/`（显式给路
... [truncated 74 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
**`test/offline/` 和 `test/live/` 必须分开**：这是课程明确要求的
```
new:
```text
> **当前状态**：上表中 `docs/architecture/` 除 `adr/` 外的工件、`docs/code-governance/*`、`.opencode/permissions.jsonc`、`.opencode/rules.md`、`.agent/rules.md`、`docs/debt-register.md`、`docs/bug-diary.md`、`prompts/*`
... [truncated 109 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
opencode export <sessionID> --sanitize > /tmp/session.json
```
new:
```text
opencode session export <sessionID> --sanitize > /tmp/session.json   # v2 起 export 是 session 的子命令
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
团队约定：**每人一个文件**，放在 `transcripts/<学号>-<姓名>.md`，**只追加，不要删改历史内容**。
```
new:
```text
团队约定：**每人一个文件**，放在 `transcripts/<学号>-<姓名>.md`，**只追加，不要删改历史内容**。

> **当前状态**：仓库现有 `transcripts/JHB11Hinson.md`（用的是 GitHub 用户名，且未含学号）。按课程 D5 的命名约定，提交前应改成 `transcripts/<学号>-<姓名>.md`。
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

#### Agent

第 3 组用 sed 做机械替换（含空格的命令行用 edit 工具容易对不齐），随后我会核对：

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
cp 开发者手册.md /tmp/dev-backup.md
# 1) 去掉全量 mypy（尚未安装）：ruff check src && mypy src -> ruff check src
sed -i 's/ruff check src && mypy src/ruff check src/g' 开发者手册.md
# 2) 独立成行的 pytest -q test/
sed -i -E 's|^pytest -q test/[[:space:]]*$|pytest -q|' 开发者手册.md
# 3) 带注释的两行
sed -i 's|pytest -q test/  *# 回归层|pytest -q  # 回归层|' 开发者手册.md
sed -i 's|pytest -q test/  *# 回归$|pytest -q  # 回归|' 开发者手册.md
echo "===== 剩余 pytest -q test/ （应只剩 §2.3 全量 与 §9.5 一处待手改） ====="
grep -n "pytest -q test/" 开发者手册.md
echo; echo "===== 剩余 mypy ====="; grep -n "mypy" 开发者手册.md

Output:

```text
===== 剩余 pytest -q test/ （应只剩 §2.3 全量 与 §9.5 一处待手改） =====
908:- **离线**：`pytest -q`（等价 `pytest -q test/offline`；门禁 5 跑的就是它）
909:- **实时**（要密钥）：`pytest -q test/live`
910:- **全量**：`pytest -q test/`（显式给路径，才会连 `test/live` 一起收）
1074:| **回归层** | `pytest -q test/` | **此前所有测试零回归**（以前能过的现在还得能过） |
1805:| `gate-5-regression` | 有测试挂了 | 本地 `pytest -q test/` 复现，修到零回归 |

===== 剩余 mypy =====
93:| **2 静态分析** | 代码风格、类型、依赖 | `ruff` / `mypy` 报错 |
1802:| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `ruff check src`，**让 AI 改**（不要手改） |
1894:| **静态分析** | 不运行代码，只"看"代码有没有风格问题、类型错误（`ruff`、`mypy`） |
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "=== §3.7 自检块 ==="; grep -n -A1 "静态检查" 开发者手册.md | head
echo; echo "=== §7.2 / §8.4 / §8.7 附近的 pytest -q ==="; grep -n "pytest -q$\|pytest -q  *# 回归" 开发者手册.md
echo; echo "=== 示例路径 ==="; grep -n "src/agents/analyst.py" 开发者手册.md
echo; echo "=== 分支大小写 ==="; grep -n "feat/chg" 开发者手册.md
echo; echo "=== transcript 占位 ==="; grep -n "12345678-AKAScarlett" 开发者手册.md

Output:

```text
=== §3.7 自检块 ===
1111:ruff check src                              # 静态检查
1112-check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml

=== §7.2 / §8.4 / §8.7 附近的 pytest -q ===
1068:pytest -q  # 回归层
1113:pytest -q  # 回归
1521:pytest -q
1675:pytest -q
1714:pytest -q

=== 示例路径 ===
1247:  source: src/agents/analyst.py:42 (baseline: about 120000 tokens per analysis)

=== 分支大小写 ===
958:> **分支名用英文**（本项目是全英文项目）：`feat/chg-014-token-budget-guard`，不要写 `feat/预算守卫`。分支名会进 `git log` 和 PR 页面，属于仓库产物。
962:| `feat/` | 加新功能、改提示词 | `feat/chg-014-token-budget-guard` |
1653:git switch -c feat/chg-XXX-<short-description>

=== transcript 占位 ===
1346:Agent-Session: transcripts/12345678-AKAScarlett.md#L81-L160
1469:  members: ["12345678-AKAScarlett"]
1479:  transcript: transcripts/12345678-AKAScarlett.md#L1-L160
```

#### Agent

第 4 组（§3.6/§3.7 说明、§9.5 门禁行、§4.4 示例路径、分支大小写、会话占位符）：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
````text
pytest -q  # 回归层
```

| 层 | 命令 | 要求 |
````
new:
````text
pytest -q  # 回归层
```

> **注意**：`mypy` **尚未加入** `[dev]` 依赖（`pip install -e ".[dev]"` 不会装它），所以现在跑 `mypy src` 会报 `command not found`；第 2 批门禁上线时再补 `mypy.ini` 并把它加入依赖。当前结构层只跑 `ruff check src`。

| 层 | 命令 |
... [truncated 4 chars]
````

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| **结构层** | `ruff check src` | 无新增违规；模块边界与架构元素一致 |
| **回归层** | `pytest -q test/` | **此前所有测试零回归**（以前能过的现在还得能过） |
```
new:
```text
| **结构层** | `ruff check src` | 无新增违规；模块边界与架构元素一致（门禁 2 只查本 PR 改动的文件） |
| **回归层** | `pytest -q` | **此前所有测试零回归**（以前能过的现在还得能过） |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `ruff check src`，**让 AI 改**（不要手改） |
```
new:
```text
| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `ruff check src`（mypy 在第 2 批门禁上线后加入），**让 AI 改**（不要手改） |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| `gate-5-regression` | 有测试挂了 | 本地 `pytest -q test/` 复现，修到零回归 |
```
new:
```text
| `gate-5-regression` | 有测试挂了 | 本地 `pytest -q` 复现（只跑离线，与门禁一致），修到零回归 |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
source: src/agents/analyst.py:42 (baseline: about 120000 tokens per analysis)
```
new:
```text
source: src/tradingagents/graph/trading_graph.py (run entry; baseline: about 120000 tokens per analysis)
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
feat/chg-014-token-budget-guard
```
new:
```text
feat/CHG-014-token-budget-guard
```

Output:

```text
Edited .opencode/manual/开发者手册.md (2 replacements)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
git switch -c feat/chg-XXX-<short-description>
```
new:
```text
git switch -c feat/CHG-XXX-<short-description>
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
12345678-AKAScarlett
```
new:
```text
<student-id>-<name>
```

Output:

```text
Edited .opencode/manual/开发者手册.md (3 replacements)
```

#### Agent

核对《开发者手册》改动结果：

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 残留 old 命令（应为空）=="; grep -n "ruff check src && mypy src\|opencode export \|pytest -q test/  *#\|^pytest -q test/\|feat/chg\|12345678" 开发者手册.md || echo "无 ✓"
echo; echo "== 关键改动确认 =="; grep -n "已完成的一次性结构对齐\|当前状态\|mypy 尚未\|opencode session export\|feat/CHG-014\|<student-id>-<name>\|graph/trading_graph.py\|84 个测试模块" 开发者手册.md | head -30
echo; echo "== §2.3 三条命令 =="; sed -n '905,915p' 开发者手册.md

Output:

```text
== 残留 old 命令（应为空）==
无 ✓

== 关键改动确认 ==
20:  - [2.2 已完成的一次性结构对齐](#22-已完成的一次性结构对齐管理员已做你们只需知道结果)
99:> **当前状态（2026-10）**：第 1 批 `gate-3-schema`、`gate-5-regression`、`gate-6-ai-use-log` **已上线**；`gate-1-test-approval`、`gate-2-static-analysis`、`gate-4-semantic-eval` **尚未上线**（按《门禁上线排期表》分批推进）。所以现在 PR 上只看到三道，这是正常的，不是配置漏了。
880:| 继承测试套件 | 84 个测试模块（连同 `conftest.py`／`__init__.py` 共 86 个 Python 文件）：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~11 秒（Python 3.12.14，干净 venv，实测） |
882:## 2.2 已完成的一次性结构对齐（管理员已做，你只需知道结果）
896:> **当前状态**：`test/live/` 目录已建但目前**为空**；唯一需要 API 的用例（`test/offline/test_deepseek_reasoning.py` 里标 `@pytest.mark.integration` 的那个，默认被 deselect）仍在 `test/offline/`。课程 D8 要求的离线/实时**物理分开尚未落地**，属待办事项，别以为已经分好了。
912:> **当前状态**：README 里目前**还没有**这三条命令（仍是上游原文），属 D7 待办。
958:> **分支名用英文**（本项目是全英文项目）：`feat/CHG-014-token-budget-guard`，不要写 `feat/预算守卫`。分支名会进 `git log` 和 PR 页面，属于仓库产物。
962:| `feat/` | 加新功能、改提示词 | `feat/CHG-014-token-budget-guard` |
1035:Agent-Session: transcripts/<student-id>-<name>.md#L1-L80"
1098:Agent-Session: transcripts/<student-id>-<name>.md#L81-L160
1220:> **当前状态**：上表中 `docs/architecture/` 除 `adr/` 外的工件、`docs/code-governance/*`、`.opencode/permissions.jsonc`、`.opencode/rules.md`、`.agent/rules.md`、`docs/debt-register.md`、`docs/bug-diary.md`、`prompts/*` **尚未创建**，属 Sprint 1 的待交付物；`AGENTS.md`、`Prompt.md` 目前仍是空文件。
1249:  source: src/tradingagents/graph/trading_graph.py (run entry; baseline: about 120000 tokens per analysis)
1306:git switc
... [truncated 853 chars]
```

#### Agent

《开发者手册》改完并核对无误。现在刷新《开局清单核查指南》里过时的“现状快照”。先读原文：

#### Agent

刷新《核查指南》的现状快照与交接：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开局清单核查指南.md`

old:
```text
## 一、现状快照（2026-10-06 通过 GitHub API 实测，main @ `580e81b`）
```
new:
```text
## 一、现状快照（2026-10-07，本地实测）
```

Output:

```text
Edited .opencode/manual/开局清单核查指南.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开局清单核查指南.md`

old:
```text
| SHA | 时间 | 提交信息 | 谁 |
|---|---|---|---|
| `580e81b` | 10-06 10:02 | `chore: add CODEOWNERS and the PR template` | Haobin Jiang |
| `1558988` | 10-06 09:35 | `chore: initialise the project skeleton a
... [truncated 403 chars]
```
new:
```text
| SHA | 提交信息 | 谁 |
|---|---|---|
| `7c3eb5a` | `ci: CHG-002 bring gate batch 1 online (#2)` | Haobin Jiang |
| `a21ec80` | `chore: CHG-001 align src layout (D8) (#1)` | Haobin Jiang |
| `580e81b` | `c
... [truncated 366 chars]
```

Output:

```text
Edited .opencode/manual/开局清单核查指南.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开局清单核查指南.md`

old:
```text
| 清单要求 | 仓库现状 | 判定 |
|---|---|---|
| `.github/CODEOWNERS`（四人通配） | ✅ 存在，486 B | **PASS**（需按 7.5.2 核对内容是那一行） |
| `.github/PULL_REQUEST_TEMPLATE.md` | ✅ 存在，690 B | **PASS** |
| `docs/req/requirements.yam
... [truncated 1025 chars]
```
new:
```text
| 清单要求 | 仓库现状 | 判定 |
|---|---|---|
| `.github/CODEOWNERS`（四人通配） | ✅ 存在，四人齐全 | **PASS** |
| `.github/PULL_REQUEST_TEMPLATE.md` | ✅ 存在 | **PASS** |
| `docs/req/requirements.yaml` | ✅ 有真实条目（`D1-REQ-GOV-0
... [truncated 1061 chars]
```

Output:

```text
Edited .opencode/manual/开局清单核查指南.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开局清单核查指南.md`

old:
```text
### 1.3 结论：当前处在 **"阶段 1 完成 / 阶段 3-1 做了一半 / 阶段 2 未开始"**

按顺序，接下来**唯一该做的事是阶段 2（结构对齐）**，而且要先补需求与 ADR——这正是
`opencode-task-CHG-001-structural-alignment.md` 那份任务书的内容。
```
new:
```text
### 1.3 结论：当前处在 **"阶段 1、2 完成；阶段 3 第一批门禁已上线；其余待做"**

`pytest -q` 本地实测 **1262 passed, 1 skipped, 1 deselected**（~11 秒）。
接下来按顺序：**CHG-003（`AGENTS.md`）** → `architecture-blueprint.md` 完整化 → 治理文件（permissio
... [truncated 39 chars]
```

Output:

```text
Edited .opencode/manual/开局清单核查指南.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开局清单核查指南.md`

old:
```text
| 期望（阶段 5 之后） | 现在应该是 |
|---|---|
| `contexts` = 三或四个门禁名 | **404**（保护还没开）或 `null` |
| `admins` = `true` | 同上 |
| `check-runs` = 有门禁名 | 空（`ci.yml` 还是上游的） |
```
new:
```text
| 项 | 期望 |
|---|---|
| `admins` | `true` |
| `contexts` | 含 `gate-3-schema`、`gate-5-regression`、`gate-6-ai-use-log` |
| `check-runs` | 出现上述三个门禁名 |
```

Output:

```text
Edited .opencode/manual/开局清单核查指南.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开局清单核查指南.md`

old:
```text
1. 先按《管理员手册》1.2.0 把环境弄绿（`pytest -q` = 1262 passed）。
2. 把 `opencode-task-CHG-001-structural-alignment.md` 交给 OpenCode（建议放仓库 `.opencode/tasks/CHG-001-structural-alignment.md`）。
3. 它做完阶段 2 之后，回到本指南第二节的**
... [truncated 20 chars]
```
new:
```text
1. CHG-001、CHG-002 已完成，**不要再重复做阶段 2、阶段 3 的骨架**。
2. 下一步是 **CHG-003：写 `AGENTS.md`**（见《功能需求表-讨论稿.md》）。
3. 之后按《门禁上线排期表》推进门禁第 2/3/4 批；本指南第二节的阶段表仍可作为**核验命令**反复使用。
```

Output:

```text
Edited .opencode/manual/开局清单核查指南.md (1 replacement)
```

#### Agent

核对《核查指南》，并做最终一致性检查：

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 核查指南残留过时标记（应为空）=="; grep -n "阶段 2 未开始\|580e81b\|1999 B\|只有 \*\*3 B\*\*\|只有 \*\*27 B\*\*\|196.5" 开局清单核查指南.md || echo "无 ✓"
echo; echo "== 新的结论/下一步 =="; grep -n "阶段 1、2 完成\|CHG-003\|7c3eb5a\|a21ec80" 开局清单核查指南.md
echo; echo "== 两份文件是否仍被忽略 =="; cd /home/jhb/TradingAgents; git check-ignore -v .opencode/manual/开发者手册.md .opencode/manual/开局清单核查指南.md
echo; echo "== git status（manual 不应出现）=="; git status --short | head
echo; echo "== 备份对比：开发者手册改动行数 =="; diff <(cat /tmp/dev-backup.md) .opencode/manual/开发者手册.md | grep -c '^[<>]'

Output:

```text
== 核查指南残留过时标记（应为空）==
17:| `580e81b` | `chore: add CODEOWNERS and the PR template` | Haobin Jiang |
119:| 3-2 | `head -1 .github/workflows/ci.yml; grep -c 'name: gate-' .github/workflows/ci.yml` | 你们自己的 `ci.yml`，**含 3 个 gate job**（不是上游那 1999 B 的文件） |
191:| `ci.yml` 还是上游的（1999 B、7 个 job） | `grep -c 'n
... [truncated 716 chars]
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| `.github/workflows/ci.yml` | 你们自己的六道门禁 | 上游那 7 个 job 会消失（正常） |
```
new:
```text
| `.github/workflows/ci.yml` | 你们自己的门禁（现为第 1 批 3 道） | 上游那 7 个 job 会消失（正常） |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "== 最终：两份文件仍被忽略（不会进仓库）=="
git check-ignore -v .opencode/manual/开发者手册.md .opencode/manual/开局清单核查指南.md
echo; echo "== 开发者手册改动规模 ==="; diff /tmp/dev-backup.md .opencode/manual/开发者手册.md | grep -c '^>'
echo "== 语法粗检：代码围栏成对？ =="
for f in .opencode/manual/开发者手册.md .opencode/manual/开局清单核查指南.md; do
  n=$(grep -c '^```' "$f"); echo "$f: $n 个围栏 $( [ $((n%2)) -eq 0 ] && echo '(成对 ✓)' || echo '(奇数 ✗)')"
done
rm -f /tmp/dev-backup.md

Output:

```text
== 最终：两份文件仍被忽略（不会进仓库）==
.gitignore:226:.opencode/manual/	.opencode/manual/开发者手册.md
.gitignore:226:.opencode/manual/	.opencode/manual/开局清单核查指南.md

== 开发者手册改动规模 ===
21
== 语法粗检：代码围栏成对？ ==
.opencode/manual/开发者手册.md: 158 个围栏 (成对 ✓)
.opencode/manual/开局清单核查指南.md: 6 个围栏 (成对 ✓)
```

#### Agent

全部修复完成。两份文档现在与仓库实际状态一致，且仍在 `.gitignore` 的 `.opencode/manual/` 保护下，不会进仓库。

## 《开发者手册.md》修复清单

| # | 修复内容 |
|---|---|
| A1 | `opencode export …` → **`opencode session export <sessionID> --sanitize …`**（适配 v2.0.18） |
| A2 | 所有 `ruff check src && mypy src` → **`ruff check src`**；并加说明：mypy 尚未加入 `[dev]`、第 2 批门禁再补 |
| A3 | 测试命令口径全部校正：§2.3 三条命令改为**离线 `pytest -q`／实时 `pytest -q test/live`／全量 `pytest -q test/`**；§3.6/§3.7/§7.2/§8.4/§8.7/§9.5 的“回归”统一为 `pytest -q`（与门禁 5 一致） |
| B1 | §2/§2.2 结构对齐由“要发生”改为**已完成（CHG-001）**；标题、目录锚点、3 个测试文件、ADR-001/002 均已落地 |
| B2 | §0.4 增加**门禁当前状态**：第 1 批 `gate-3/5/6` 已上线，其余三道上线中；`ci.yml` 行同步 |
| C1 | §3.6 结构层注明“门禁 2 只查本 PR 改动的文件” |
| D | 加了三处 **当前状态** 提示：`test/live/` 为空且集成用例仍在 offline、README 缺三条命令、大批治理/架构工件尚未创建、`AGENTS.md`/`Prompt.md` 仍空 |
| E | 示例路径改为真实路径；分支名统一大写 `feat/CHG-014…`；会话记录占位统一 `<student-id>-<name>`；测试数改为“84 个模块（共 86 个 Python 文件）” |

## 《开局清单核查指南.md》修复清单

- §1.1 提交历史更新到 `7c3eb5a`（CHG-002）、`a21ec80`（CHG-001）。
- §1.2 文件现状表**整表重写**：`src/`、`test/offline|live`、需求/schema/AI 日志/ADR/review-memo/pyproject 全部 PASS；`AGENTS.md`、`Prompt.md`、治理文件、`prompts/`、`eval/` 标为待做。
- §1.3 结论改为“阶段 1、2 完成；阶段 3 第一批门禁已上线；其余待做”。
- §1.4 权限期望改为“`admins=true` + 三个门禁名”。
- §五 交接改为“下一步 CHG-003（`AGENTS.md`）”，不再让人重复做阶段 2。

两份文件的代码围栏都成对（158 / 6），Markdown 结构完整。

## 需要你知道的两点

1. 我修的是**文档**，让它如实反映现状。文档里标为“待办”的那些**仓库缺口仍在**（`test/live/` 空、README 无测试命令、`AGENTS.md` 空、治理/架构工件缺失）——这些要各自走 CHG 才能补上。
2. **《管理员手册.md》和《管理员开局清单.md》还没动**。它们篇幅很大，而且大概率也带着同一批“CHG-001/002 之前”的旧口径（比如“先落 ADR-001”“阶段 2 未做”“mypy 全量”等）。要不要我也按同样方式审一遍、一并修，再一起发给组员？

#### Human

```text
呃，还有个问题，每次改代码前，是不是都要先提交需求测试的PR，开发者手册里提了吗？如果没有的话，在日常工作里面加！
```

#### Agent

好问题——这其实是课程门禁 1（测试批准）的核心。让我先确认手册现在到底写没写、写得够不够显眼。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "===== 含“测试”+“批准/先于/早于”的行 ====="
grep -n "测试必须\|先于实现\|早于实现\|先写测试\|只提交测试\|测试批准\|拿批准\|approval pending\|Test-Approval" 开发者手册.md
echo; echo "===== §3.1 七步图 ====="
sed -n '/## 3.1 一张图/,/## 3.2/p' 开发者手册.md
echo; echo "===== §3.4 / §3.5 标题 ====="
grep -n "^## 3\.[0-9]\|^# 三" 开发者手册.md
echo; echo "===== §4.1 表里 src 行 ====="
grep -n "测试必须先于实现提交\|必须更新" 开发者手册.md | head

Output:

```text
===== 含“测试”+“批准/先于/早于”的行 =====
92:| **1 测试批准** | 改 `src/` 之前，测试有没有先提交并获批准 | 只改实现不写测试，或没有 `APPROVE` 记录 |
919:| 测试批准 | 看的是"这次改动由**哪些测试**覆盖"，**可以是已有的继承测试**——所以别以为改继承代码没写新测试就一定过不了 |
928:① 同步 main  →  ② 开分支  →  ③ 让 AI 出计划，你批准  →  ④ 先写测试并提交（拿批准）
1019:## 3.5 第 ④ 步：先写测试，提交，拿到批准
1023:> **测试必须早于实现提交。** 先只把测试推
... [truncated 2051 chars]
```

#### Agent

手册里其实**已经写了**（多处），先给你确认原文，再顺手把它做成一条显眼的“铁律”。

#### Agent

手册里**已经写了**（不是我漏的），位置如下：

- §0.4 门禁 1 表格行
- §2.4「测试批准」判据（可用**已有的继承测试**覆盖）
- §3.1 七步图第 ④ 步「先写测试并提交（拿批准）」
- **§3.5 整节：先写测试，提交，拿到批准**（含命令与 `review-memo` 模板）
- §4.1 表格：`src/**` 行注明「测试必须先于实现提交」
- §7.3 评审第 2 项：`git log … -- test src`，`test` 必须排在 `src` 前
- §8.3「只提交测试（拿批准）」命令块
- 结尾「五条最容易忘的」第 3 条

不过它散在各处，确实不够显眼。我按你的意思，在日常循环开头加一条**铁律框**，并说清“不是两个 PR”这个容易误解的点：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
## 3.2 第 ① 步：同步 main
```
new:
```text
> **🔒 铁律：改代码 = 先测后码（门禁 1）**
>
> **规则一句话**：凡是改动 `src/`（应用代码或提示词）的变更，**测试必须先提交并获得批准，然后才允许提交实现**。
>
> | 情形 | 要不要测试先行 |
> |---|---|
> | 改 `src/**`、`prompts/**`（会改变程序行为） | **要**：先提 `test/` + `review-memo.m
... [truncated 691 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
n=$(grep -c '^```' .opencode/manual/开发者手册.md); echo "开发者手册围栏: $n $([ $((n%2)) -eq 0 ] && echo '(成对 ✓)' || echo '(奇数 ✗)')"
git check-ignore -v .opencode/manual/开发者手册.md

Output:

```text
开发者手册围栏: 158 (成对 ✓)
.gitignore:226:.opencode/manual/	.opencode/manual/开发者手册.md
```

#### Agent

已加好。回答你的问题：

## 是，但要分清两件事

1. **改 `src/`（应用代码或提示词）→ 必须“先测试、后实现”。** 这是课程**门禁 1（测试批准）**的硬要求：`src` 变更在实现开始前，覆盖它的测试必须先提交并拿到批准。
2. **不是“两个 PR”。** 是**同一条分支、同一个 PR，分两次提交**：
   - 先提交 `test/` + `review-memo.md`（标 `approval pending`）→ 拿到 `APPROVE`
   - 同分支再提交 `src/` 实现 → PR 自动更新、重跑检查
   - `Test-Approval:` 小尾巴指向 `docs/review-memo.md#<CHG号>`
3. **“需求测试”不一定得新写**：由需求 `fit_criterion` 导出的验收测试即可，**也可以是已有的继承测试**（§2.4）——但要在 `review-memo.md` 里写清“由哪些测试覆盖”并先获批准。
4. **例外**：只改 `docs/**`、`README.md`、`Report.md`、`.github/**`、`AGENTS.md`、`.opencode/**` 等（不改变程序行为）→ 不触发门禁 1，但仍要走 PR + 别人批准。

## 手册里原本已经写了（不是漏的）

§0.4 门禁 1 行、§2.4 判据、§3.1 七步图第④步、**§3.5 整节**、§4.1 表格、§7.3 评审第 2 项、§8.3 命令块、结尾“五条最容易忘的”第 3 条。

## 我在日常工作里新加的“铁律框”

放在 §3.1 七步图之后、§3.2 之前（就是你现在一进“日常开发循环”就会看到的位置），写明：触发/不触发条件、“不是两个 PR”、“需求测试可以是继承测试”、“为什么必须分开交”，以及当前状态。

## 一个关键提醒

**门禁 1 现在还没上线（属第 4 批）**，所以这条规矩目前靠**人工评审**执行（评审时看 `git log --oneline origin/main..HEAD -- test src`，`test` 必须排在 `src` 前面）——不是没人管，只是还没自动化。等第 4 批上线后，`src` 变更没带已批准测试的 PR 会被 CI 直接拦下。

另外提醒一个易踩点（手册 §7.6 有讲）：分支保护里 `dismiss_stale_reviews` 开着，**你推“实现提交”会把之前对测试的批准作废**，所以最终合并前通常还要再请人批一次——这也是为什么手册说“尽量一次性推完、最后再请人批”。

文件仍在 `.opencode/manual/`（被 `.gitignore` 忽略），不会进仓库。

#### Human

```text
那要先登记需求吧，而且不是每次改代码都要写一个新的测试的，具体点，详细点
```

#### Agent

明白，我把“先登记需求”和“不是每次都要新写测试”这两点补成日常流程里的一节，写具体。

先微调铁律框那一行（避免它暗示“每次都必须改测试文件”）：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
> | 改 `src/**`、`prompts/**`（会改变程序行为） | **要**：先提 `test/` + `review-memo.md`（标记 `approval pending`）→ 拿到 `APPROVE` → 再提 `src/` 实现 |
```
new:
```text
> | 改 `src/**`、`prompts/**`（会改变程序行为） | **要**：先让“覆盖它的测试”被批准（**可复用已有测试**，详见 §3.1.1）→ 再提 `src/` 实现 |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

#### Agent

现在补上详细小节 §3.1.1：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
## 3.2 第 ① 步：同步 main
```
new:
```text
## 3.1.1 动手前的决策：先登记需求，再决定“要不要写新测试”

**先纠两个常见误解**：① **不是**“每次改代码都要新写测试”；② **但一定要先有需求登记**——代码是照着需求写的，不是反过来。

### 第 0 步 · 先看需求登记册里有没有这条

`docs/req/requirements.yaml` 是唯一真源。

| 情况 | 怎么做 |
|---|---|
| 要做的行
... [truncated 1918 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
n=$(grep -c '^```' .opencode/manual/开发者手册.md); echo "围栏: $n $([ $((n%2)) -eq 0 ] && echo '(成对 ✓)' || echo '(奇数 ✗)')"
echo "== 3.1.1 与铁律框交叉引用 =="; grep -n "§3.1.1\|详见 §3.1.1\|先登记需求" .opencode/manual/开发者手册.md
echo "== 仍被忽略 =="; git check-ignore -v .opencode/manual/开发者手册.md
echo "== git status =="; git status --short

Output:

```text
围栏: 158 (成对 ✓)
== 3.1.1 与铁律框交叉引用 ==
947:> | 改 `src/**`、`prompts/**`（会改变程序行为） | **要**：先让“覆盖它的测试”被批准（**可复用已有测试**，详见 §3.1.1）→ 再提 `src/` 实现 |
955:## 3.1.1 动手前的决策：先登记需求，再决定“要不要写新测试”
== 仍被忽略 ==
.gitignore:226:.opencode/manual/	.opencode/manual/开发者手册.md
== git status ==
 M .gitignore
?? .opencode/
```

#### Agent

对，你说的两点都对。我把它们补成了 §3.1.1「动手前的决策：先登记需求，再决定要不要写新测试」（就在日常循环 §3.1 七步图之后）。要点如下：

## 顺序：先登记需求，再写代码

`docs/req/requirements.yaml` 是唯一真源。

| 情况 | 怎么做 |
|---|---|
| 要做的行为**已有**需求条目 | 在变更卡 `Related requirement` 引用它的 `D1-REQ-…`，直接进入下一步 |
| 行为**是新的** / 要**改删**已有需求 | **先单独走一次 `req/CHG-xxx` 变更**：加/改条目（`id`/`type`/`statement`/`fit_criterion`/`priority`/`tradeoff`/`source`）→ `check-jsonschema` 通过 → PR 合并。**必须跑在代码之前**（否则 `Refs:` 会指向一条还不存在的需求） |

判定：**行为变了 / 多了验收标准 / 多了不变量 → 要**；**只重构、修 bug 且行为不变 → 不要**。

## 不是每次都要新写测试

| 这次改什么 | 要新写测试吗 | 覆盖证据写什么 |
|---|---|---|
| 新行为 / 新 `fit_criterion` / 新不变量 | **要**：验收测试 + 至少一个**负向测试** | 新测试文件 + 测试名 |
| 已有行为，继承测试已覆盖 | **不要**，直接复用（§2.4 允许） | 引用已有测试名 |
| 只改 `docs/`、`README`、`Report`、`.github/`、`AGENTS.md`、`.opencode/**` | **不要**（不触发门禁 1） | — |
| 改了 `src/` 行为，但旧测试**没覆盖改动的边界** | **仍然要** | 新测试 + 测试名 |

## 提交顺序（关键：同一个 PR，两次提交）

1. **有测试改动**：先只提 `test/` + `review-memo.md`（标 `approval pending`）→ 开 PR → 请人 `APPROVE`。
2. **不改测试**：在变更卡写 `Covered by which tests: <已有测试>`，评审人确认覆盖成立 = 测试批准。
3. 拿到批准后，同分支再提 `src/` 实现。
4. **合并前通常还要再拿一次批准**（`dismiss_stale_reviews` 会把实现提交前的批准作废，见 §7.6）。

## 四个具体例子

- **例 A｜新功能**：做 token 预算守卫 → 先 `req/` 加 `D1-REQ-COST-003`（`fit_criterion: 单次 ≤ 50000 tokens`）合并 → 再写 `test_token_budget.py`（含负向用例）→ 批准 → 才写实现。
- **例 B｜纯重构**：内部函数改名/拆分，行为不变；既有需求仍成立、继承测试已覆盖 → **不写新测试**，靠 `pytest -q` 全量回归证明零回归。
- **例 C｜修 bug**：一般补一个“**修复前红、修复后绿**”的回归测试；若某已有测试在修复前本就因该 bug 会失败，则复用即可。
- **例 D｜只改文档**：只改 `README.md` → `docs/CHG-xxx` PR + 批准，不需要测试。

同时我把 §3.1 铁律框那一行也改准了：从“先提 test/”改成“**先让覆盖它的测试被批准（可复用已有测试，详见 §3.1.1）**”，避免误导成“每次都得改测试文件”。

补充一句现状：门禁 1 属第 4 批、**尚未上线**，现在靠人工评审执行（评审时用 `git log --oneline origin/main..HEAD -- test src`，`test` 必须排在 `src` 前）；上线后由 CI 自动拦。文档仍在 `.opencode/manual/`，被 gitignore 忽略，不会进仓库。

#### Human

```text
呃，开发者手册符合课程项目PDF的具体要求吗？
```

#### Agent

这是个更本质的问题——不是“和仓库是否一致”，而是“和课程 PDF 的硬要求是否一致”。我逐条把 PDF 的 D1–D9、第 5/6 节要求对照手册。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
python3 - <<'PY'
from pypdf import PdfReader
r = PdfReader(".opencode/manual/CS5351-2026-2027-project.pdf")
import re
for i in (4,5,6,7,8,9):
    t = r.pages[i].extract_text() or ""
    print(f"\n########## page {i+1} ##########")
    print(t)
PY

Output:

```text
incorrect startxref pointer(3)
parsing for Object Streams
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype
Multiple definitions in dictionary at byte 0x79 for key /Subtype
Multiple definitions in dictionary at byte 0x251 for key /Subtype

########## page 5 ##########
CS5351  |  Agentic Software Engineering Project
Page 5
3. Deliverables
D1 — Requirements (machine-readable)
Produce a machine-readable product requirements document and a consolidated requirements
registry, both in YAML, under `./docs/req/` where `.` is the project root.
• `docs/req/requirements.yaml` — every requirement as an entry with an ID, type, statement, and a
machine-checkable fit criterion, plus priority. Types cover functional behavior, invariants (non-
negotiable rules with zero-tolerance fit criteria), quality attributes, performance, cost, governance,
and security. Non-functional requirements are expressed as metric + threshold + verification.
Prioritization uses MoSCoW, and states the tradeoff explicitly. Requirements discovered through
analysis of any existing system or repository are included and linked to their sources.
• `docs/req/req-schema.json` — the schema used by CI in GitHub to validate the registry as a date.
D2 — Architecture Artifacts (all as markdown .md files)
Pr
... [truncated 13040 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 手册是否覆盖 D2/D3/D4 各工件 =="
for k in "authority\|权威边界\|advisory" "structural-constraints" "verification-constraints" "mcp-tool-manifest\|mcp-tool" "permission-model\|permissions.jsonc" "runtime-policy" "memory-design" "evaluation-table" "evaluation-logbook" "option-ledger" "risk-list" "分层上下文" "压缩" "invariant\|不变量" "trace-matrix" "debt-register\|技术债" "bug-diary\|缺陷日记" "prompt rot\|prompt 腐化\|提示词腐化"; do
  printf '%-40s %s\n' "$k" "$(grep -cE "$k" 开发者手册.md)"
done
echo; echo "== README / Report / 自省 / 贡献 =="
grep -n "README" 开发者手册.md | head
echo "---"; grep -n "自省\|贡献表\|10000\|10,000\|15 页" 开发者手册.md | head
echo; echo "== 六道门禁原文行 =="; grep -n "gate
... [truncated 136 chars]

Output:

```text
== 手册是否覆盖 D2/D3/D4 各工件 ==
authority\|权威边界\|advisory        0
structural-constraints                   2
verification-constraints                 2
mcp-tool-manifest\|mcp-tool              0
permission-model\|permissions.jsonc      0
runtime-policy                           3
memory-design
... [truncated 2376 chars]
```

#### Agent

PDF 逐页要求已拿到。刚才的 grep 因为模式写错（`-E` 里用了 `\|`）不可靠，我重跑一次正确的覆盖检查，并把 §4.5/§4.6 也读出来核对：

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 正确覆盖计数（-E 用 | 作或） =="
for k in "权威边界|advisory|authoritative" "structural-constraints" "verification-constraints" "mcp-tool-manifest" "permission-model|permissions.jsonc" "runtime-policy" "memory-design" "invariants|不变量" "trace-matrix" "evaluation-table" "evaluation-logbook" "option-ledger" "risk-list" "debt-register|技术债" "bug-diary|缺陷日记" "prompt rot|提示词腐化|prompt 腐化"; do
  printf '%-42s %s\n' "$k" "$(grep -cE "$k" 开发者手册.md)"
done
echo; echo "== 门禁 2 的定义：PDF 有两部分，手册怎么写的 =="
grep -n "静态分析" 开发者手册.md
echo; echo "== 报告内容要求（过程质量证据等） =="
grep -nE "需求波动|缺陷趋势|歧义|co-evolv|共同演进|过程质量|oversight" 开发者手册.md || echo "未覆盖"
echo; echo "== D8 模块名与架构元素对应 =="; g
... [truncated 63 chars]

Output:

```text
== 正确覆盖计数（-E 用 | 作或） ==
权威边界|advisory|authoritative        5
structural-constraints                     2
verification-constraints                   2
mcp-tool-manifest                          2
permission-model|permissions.jsonc         7
runtime-policy                             3
memory-design
... [truncated 649 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
for k in "structural-constraints" "mcp-tool-manifest" "debt-register" "bug-diary" "verification-constraints"; do
  echo "== $k =="; grep -n "$k" 开发者手册.md
done
echo; echo "== 权威边界 上下文 =="; grep -n "权威边界" 开发者手册.md
echo; echo "== §0.3 交付物表 =="; sed -n '/## 0.3/,/## 0.4/p' 开发者手册.md

Output:

```text
== structural-constraints ==
1251:│   │   ├── structural-constraints.md
1981:| **D3** | 编码治理 | `AGENTS.md`、`docs/code-governance/structural-constraints.md`、`mcp-tool-manifest.md`、`.opencode/permissions.jsonc`、`.opencode/rules.md`、`.agent/rules.md` |
== mcp-tool-manifest ==
1253:│   │   └── mcp-tool-
... [truncated 2688 chars]
```

#### Agent

对照完了。直接说结论：**大体符合**——手册把 D1–D9 的交付物、六道门禁、目录结构、README/报告/会话记录要求都覆盖了；但作为“开发者操作手册”，它不是 D1–D9 的**完整规格**，有 **7 处具体缺口**（PDF 有明确要求，手册没写或写不全）。

## 逐条对照

| PDF 要求 | 手册 | 位置 | 判定 |
|---|---|---|---|
| D1 登记册字段 / 7 类型 / MoSCoW / tradeoff / source | ✅ | §4.4、§0.4 | 符合 |
| D1 `req-schema.json` + 门禁 3 | ✅ | §4.2、§9.5 | 符合 |
| D2.1 蓝图（含**权威边界 advisory/authoritative**） | ✅ | §4.3、§4.5 | 符合 |
| D2.2 ADR（含 AI **分层上下文/装配管线/预算/压缩/再注入**） | ✅ | §4.5 | 符合（很细） |
| D2.3–D2.11（invariants/trace/memory/permission/runtime-policy/eval-table 等） | ✅ | §4.5 | 符合 |
| D3 `AGENTS.md` 内容 | ✅ | §4.3 | 符合 |
| D3 `.opencode/rules.md`、`permissions.jsonc`、`.agent/rules.md`（5 条） | ✅ | §4.3 | 符合 |
| **D3 `structural-constraints.md` 的 4 条规则** | ❌ **只列了文件名** | §4.2 | **缺内容** |
| **D3 `mcp-tool-manifest.md` 内容（工具 + 哪些角色可调）** | ❌ **只列了文件名** | §4.2 | **缺内容** |
| D4 三层验证（结构/回归/行为） | ✅ | §3.6 | 符合 |
| D4 `review-memo.md` 字段 + 三种结论 | ✅ | §7.4/§7.5 | 符合 |
| **D4 `verification-constraints.md` 的 4 条规则** | ❌ **只列了文件名** | §4.2 | **缺内容** |
| **D4 `debt-register.md` 的 8 类 AI 技术债** | ❌ 未提 | — | **缺** |
| **D4 `bug-diary.md` 的规定字段** | ⚠️ 只在 1.2.0 出现过一次例子 | §1.2.0 | **不完整** |
| D5 原始会话 + 六环节 + 干预类型 | ✅ | §6 | 符合 |
| D6 报告字数/页数/贡献表/自省 300–500 词 | ✅ | §0.3 | 符合 |
| **D6 报告必写内容**（过程质量证据：需求波动/缺陷趋势/歧义消解；制品共同演进；人类监督抓到什么） | ❌ | — | **缺** |
| D7 六道门禁 | ✅ | §0.4、§9.5 | 符合 |
| **D7 门禁 2 的第二部分**（对触及安全相关路径的 PR 跑 contract / security / API-surface / permission 检查） | ❌ 只写了“lint/类型/依赖” | §0.4 | **不完整** |
| D7 分支保护（安全关键路径需人工评审 + ADR） | ✅ | §0.4、§7.3#6 | 符合 |
| D7 README 四要素（用途+架构/文件组织/测试/仓库链接） | ✅ | §0.3、§2.3 | 符合 |
| D8 `src`/`test` 分离 offline/live | ✅ | §2.2/§2.3 | 符合 |
| **D8 模块名与架构元素对应** | ❌ 未提 | — | **缺** |
| D9 `Prompt.md` 内容（先出计划+停等人批） | ✅ | §4.3、§3.4 | 符合 |
| 第 5 节目录结构 | ✅ | §4.2 | 符合 |
| 第 6 节六道门禁 | ✅ | §0.4、§9.5 | 符合 |

## 7 处缺口汇总

1. **门禁 2 不完整**：PDF 明确门禁 2 有两部分——每次提交跑 lint/类型/依赖；**触及安全相关路径的 PR 还要跑 contract / security / API-surface / permission 检查**。手册只写了前半句。
2. **`structural-constraints.md`** 的必写内容没写：① 每个架构元素只映射到一个模块；② 新工作**扩展**基线、绝不替换；③ 每个模块/函数引用它实现的 ADR 与不变量；④ 权威边界。
3. **`mcp-tool-manifest.md`** 的内容没写：代理可调用哪些工具、哪些角色可调。
4. **`verification-constraints.md`** 的 4 条规则没写：每条 `fit_criterion` ≥1 个测试；每条不变量 ≥1 个“违反即失败”的测试；每个测试引用它验证的需求/不变量；每轮跑全部历史套件、零回归。
5. **`debt-register.md`** 的 8 类 AI 技术债没写：prompt rot、幻觉依赖、不可触碰代码、隐藏依赖、agent 膨胀、评测债、护栏债、人/认知债。
6. **`bug-diary.md`** 的规定字段没写：症状、复现、分类、根因、修复、暴露了哪条不变量缺口。
7. **D6 报告 + D8** 的两处：报告的“过程质量证据/制品共同演进/人类监督抓到什么”没写；D8 的“模块名与架构元素一一对应”没提。

## 建议

这 7 处都是“清单里有、但没有内容要求”，补起来不大。我建议在 §4.5 后面加一节 **§4.8「D3/D4 各文件的具体内容要求」**（把上面 2–6 写全），并顺手补全 §0.4 的门禁 2、§0.3 的报告内容要求、§4.5 的 D8 模块对应一句话。

要我直接补进去吗？

#### Human

```text
都写进去，注意哪些是管理员的，哪些是组员（开发者）的，而且管理员手册也没对齐现有情况，对齐一下
```

#### Agent

明白，分两步：先把 7 处缺口补进《开发者手册》（并标注归属），再来对齐《管理员手册》。先做开发手册。

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
| **2 静态分析** | 代码风格、类型、依赖 | `ruff` / `mypy` 报错 |
```
new:
```text
| **2 静态分析** | 每次提交跑 lint / 类型 / 依赖；**触及安全相关路径的 PR 还要跑 contract / security / API-surface / permission 检查** | `ruff` / `mypy` 报错，或安全相关检查未过 |
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
**最容易漏的是第 1、2 和第 6 项。** 很多人只记录了"让 AI 写代码"那一段，结果六个环节只覆盖了 3 个。
```
new:
```text
**最容易漏的是第 1、2 和第 6 项。** 很多人只记录了"让 AI 写代码"那一段，结果六个环节只覆盖了 3 个。

**报告内容还有硬要求**（不只是字数/页数）：贡献表（相对贡献，按 manhours 或 story points 折算）、每人 **300–500 词自省**（含姓名 + 学号）、**过程质量证据**（需求波动、缺陷趋势、歧义消解）、任何变更时**制品如何共同演进**、以
... [truncated 65 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
**ADR-001**（采纳继承基线，扩展而非重写）与 **ADR-002**（src layout 对齐）**已写入仓库**：`docs/architecture/adr/`。
```
new:
```text
**ADR-001**（采纳继承基线，扩展而非重写）与 **ADR-002**（src layout 对齐）**已写入仓库**：`docs/architecture/adr/`。

**D8 的另一条要求**：**模块名要与架构元素一一对应**——每个架构元素映射到**唯一模块**。这条会落进 `docs/code-governance/structural-constraints.md`（见 4
... [truncated 4 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
**一个对齐要求**：`permission-model.md` 里写的白名单，要和 `.opencode/permissions.jsonc` 里写的**一致**。两处不一致是常见的评审退回原因。
```
new:
```text
**一个对齐要求**：`permission-model.md` 里写的白名单，要和 `.opencode/permissions.jsonc` 里写的**一致**。两处不一致是常见的评审退回原因。

**归属（角色层面）**：**【管理员】** 主导 `architecture-blueprint.md`、`permission-model.md`、`runtime-policy-catalog
... [truncated 211 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
# 五、提交信息的写法
```
new:
```text
## 4.8 D3/D4 各文件的具体内容要求（PDF 逐条）

> **归属标记**：**【管理员】** = 管理员主导初版与维护、组员评审；**【全员】** = 每个人都要按它做事并在自己 PR 里维护。
> D2 的 11 类见 4.5；D1 的需求字段见 4.4。

| 文件 | 必须写什么（PDF 逐条要求） | 归属 |
|---|---|---|
| `docs/code-gover
... [truncated 1273 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "===== 管理员手册：过时/待改标记定位 ====="
for k in "要发生" "先落两份" "先落 ADR" "阶段 2" "阶段 3" "86 个文件" "86个文件" "mypy src" "pytest -q test/" "opencode export" "上游原文件" "1999" "未上线" "还没开\|尚未\|未开始" "未做" "ADR-001" "六道门禁" "1262"; do
  printf '%-28s %s\n' "$k" "$(grep -cE "$k" 管理员手册.md)"
done
echo; echo "===== 命中行（部分） ====="
grep -nE "要发生|先落|86 个文件|mypy src|pytest -q test/|opencode export|上游原文件|1999 B|未开始" 管理员手册.md | head -40
echo; echo "管理员手册行数：$(wc -l < 管理员手册.md)"; echo "管理员开局清单行数：$(wc -l < 管理员开局清单.md)"

Output:

```text
===== 管理员手册：过时/待改标记定位 =====
要发生                    0
先落两份                 0
先落 ADR                   1
阶段 2                     1
阶段 3                     0
86 个文件                 1
86个文件                  0
mypy src                     8
pytest -q test/              13
opencode export              1
上游原文件              0
1999                         0
未上线                    0
还没开\|尚未\|未开始 0
未做                       0
ADR-001                      1
六道门禁                 11
1262                         2

===== 命中行（部分） =====
895:**第一步决策先落 ADR-001**：`docs/architecture/adr/001-adopt-inherited-architecture.md` —— 采纳继承架构作为基线、在其上增量演进（对照的备选方案：重写、旁挂一套并行系统、换编排框架）。它是 ADR-002（src layout 对齐）的上位依据；顺序**先 001 再 002**。
904:| 继承测试套件 | 86 个文件：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~12 秒（Python 3.12.14，干净 venv） |
1046:pytest -q test/offline    # README 里的"离线测试"
1047:pytest -q test/live       # README 里的"实时测试"（要密钥）
1551:ruff check src && mypy src      # 结构层
1552:pytest -q test/                 # 回归层
1557:| **结构层** | `ruff check src && mypy src` | 无新增违规；模块边界与架构元素一致 |
1558:| **回归层** | `pytest -q test/` | **此前所有测试零回归** |
1595:ruff check src && mypy src
1597:pytest -q test/
1902:ruff check src && mypy src
1903:pytest -q test/
2115:opencode export <sessionID> --sanitize > /tmp/session.json
2226:pytest -q test/
2744:      - run: mypy src || true
2752:| `mypy src \|\| true` | 先软上线观察；确认不再乱报之后**去掉 `\|\| true`** 再算正式上线 |
3351:#    - run: pytest -q test/offl
... [truncated 436 chars]
```

#### Agent

《开发者手册》第 1 部分补完。现在对齐《管理员手册》（4195 行，很大的文档）。先定位并读取需要改的区域。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 章标题 =="; grep -nE "^# 第" 管理员手册.md
echo; echo "== 需要看的片段上下文 =="
for ln in 1593 1901 2113 2224 3455 4002; do echo "--- around $ln ---"; sed -n "$((ln-2)),$((ln+2))p" 管理员手册.md; done

Output:

```text
== 章标题 ==
98:# 第一章 环境 【全员 · 每个组员各自做一遍，管理员也要做】
870:# 第二章 基线盘点与结构对齐 【全员 · 管理员主导，组员各做一遍 2.2】
980:# 第 12 行：仓库根现在多了一层
984:# 第 28 行
987:# 第 30 行：让日志里仍然显示 tradingagents/dataflows/x.py，而不是 src/tradingagents/...
990:# 第 31-32 行（包名不变，只把扫描根换成 SRC）
1078:# 第三章 仓库初始化（一次性） 【管理员 · 3.7 全员】
1411:# 第四章 日常开发循环 【全员】
162
... [truncated 1634 chars]
```

#### Agent

开始对齐《管理员手册》。先用 sed 修机械命令，再补状态说明。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
cp 管理员手册.md /tmp/admin-backup.md
# mypy（未安装）从日常命令里去掉；保留第 9 章门禁设计里的 `mypy src || true`
sed -i 's/ruff check src && mypy src/ruff check src/g' 管理员手册.md
# opencode 导出子命令
sed -i 's/opencode export /opencode session export /g' 管理员手册.md
# 独立成行的 pytest -q test/
sed -i -E 's|^pytest -q test/[[:space:]]*$|pytest -q|' 管理员手册.md
# 带“# 回归层”注释的
sed -i 's|pytest -q test/  *# 回归层|pytest -q  # 回归层|' 管理员手册.md
echo "== 剩余 pytest -q test/ =="; grep -n "pytest -q test/" 管理员手册.md
echo; echo "== 剩余 ruff check src && mypy =="; grep -n "ruff check src && mypy" 管理员手册.md || echo "无 ✓"
echo; echo "== opencode export 残留 =="; grep -n "opencode export" 管理员手册.md || echo "无 ✓"
ech
... [truncated 57 chars]

Output:

```text
== 剩余 pytest -q test/ ==
1046:pytest -q test/offline    # README 里的"离线测试"
1047:pytest -q test/live       # README 里的"实时测试"（要密钥）
1558:| **回归层** | `pytest -q test/` | **此前所有测试零回归** |
3351:#    - run: pytest -q test/offline || true
3352:#    + run: pytest -q test/offline
3355:pytest -q test/offline
3367:pytest -q test/offline   # 期望本地就红；推上去确认 CI 也红
3457:| 3 | 本地等价命令通过 | `ruff check src`；`pytest -q test/offline`；`check-jsonschema ...` |
4007:| `gate-5-regression` | 有测试挂了 | 本地 `pytest -q test/` 复现，修到零回归 |

== 剩余 ruff check src && mypy ==
无 ✓

== opencode export 残留 ==
无 ✓

== 保留的 mypy 设计行 ==
2744:      - run: mypy src || true
2752:| `mypy src \|\| true` | 先软上线观察；确认不再乱报之后**去掉 `\|\| true`** 再算正式上线 |
```

#### Agent

《管理员手册》补状态与修正（第 1 组）：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
# 第一章 环境 【全员 · 每个组员各自做一遍，管理员也要做】
```
new:
```text
## 现状快照（2026-10-07）【全员看一次】

- **已完成**：**CHG-001**（src 布局对齐）、**CHG-002**（治理骨架 + 第 1 批门禁上线）；`main` @ `7c3eb5a`。
- **门禁在线**：`gate-3-schema`、`gate-5-regression`、`gate-6-ai-use-log`（第 1 批）；`gate-1/2/4` 待第
... [truncated 541 chars]
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
> 所以你们交付的是**对一个成熟开源项目的受约束改进**：继承代码 + 治理 + 增量功能。**先盘点，再动结构，最后才谈功能。**
```
new:
```text
> 所以你们交付的是**对一个成熟开源项目的受约束改进**：继承代码 + 治理 + 增量功能。**先盘点，再动结构，最后才谈功能。**
>
> **当前状态（2026-10-07）**：本章的“结构对齐”**已完成**（**CHG-001** 已合并）；下面 2.2–2.4 保留作追溯与复用，**不需要重跑**。
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
| `.github/workflows/ci.yml`（上游 CI，7 个 job） | 你们自己的六道门禁 | 覆盖或改名（2.6） |
```
new:
```text
| `.github/workflows/ci.yml`（上游 CI，7 个 job） | 你们自己的门禁（现为第 1 批 3 道） | 覆盖或改名（2.6） |
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
**第一步决策先落 ADR-001**：`docs/architecture/adr/001-adopt-inherited-architecture.md` —— 采纳继承架构作为基线、在其上增量演进（对照的备选方案：重写、旁挂一套并行系统、换编排框架）。它是 ADR-002（src layout 对齐）的上位依据；顺序**先 001 再 002**。
```
new:
```text
**ADR-001 与 ADR-002 已落并合并（CHG-001）**：`docs/architecture/adr/001-adopt-inherited-architecture.md`（采纳继承架构为基线、增量演进；备选：重写、旁挂一套并行系统、换编排框架）与 `002-src-layout.md`（src layout 对齐）。顺序**先 001 再 002**（001 是 002 的上
... [truncated 5 chars]
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
| 继承测试套件 | 86 个文件：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~12 秒（Python 3.12.14，干净 venv） |
```
new:
```text
| 继承测试套件 | 84 个测试模块（连同 `conftest.py`／`__init__.py` 共 86 个 Python 文件）：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~11 秒（Python 3.12.14，干净 venv，实测） |
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
## 2.3 一次性结构对齐（这是**唯一**一次动目录）
```
new:
```text
## 2.3 一次性结构对齐（CHG-001 已完成；这是**唯一**一次动目录）
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
### 2.3.1 搬目录
```
new:
```text
> **当前状态（2026-10-07）**：本节每一步都已在 **CHG-001** 执行并合并；`src/tradingagents`、`src/cli`、`test/offline`、`test/live` 已就位。**以下内容保留作追溯与复用，不需要重做**。

### 2.3.1 搬目录
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

#### Agent

（第 2 组）

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
| **结构层** | `ruff check src` | 无新增违规；模块边界与架构元素一致 |
| **回归层** | `pytest -q test/` | **此前所有测试零回归** |
```
new:
```text
| **结构层** | `ruff check src` | 无新增违规；模块边界与架构元素一致（门禁 2 只查本 PR 改动的文件） |
| **回归层** | `pytest -q` | **此前所有测试零回归** |
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
````text
pytest -q  # 回归层
```

| 层 | 命令 | 要求 |
````
new:
````text
pytest -q  # 回归层
```

> **注意**：`mypy` **尚未加入** `[dev]` 依赖，现在跑 `mypy src` 会报 `command not found`；第 2 批门禁上线时再补 `mypy.ini` 并加入依赖。当前结构层只跑 `ruff check src`。

| 层 | 命令 | 要求 |
````

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `ruff check src`，**让 AI 改**（不要手改） |
```
new:
```text
| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `ruff check src`（mypy 在第 2 批门禁上线后加入；触及安全相关路径的 PR 还会跑 contract / security / API-surface / permission 检查），**让 AI 改**（不要手改） |
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
| `gate-5-regression` | 有测试挂了 | 本地 `pytest -q test/` 复现，修到零回归 |
```
new:
```text
| `gate-5-regression` | 有测试挂了 | 本地 `pytest -q` 复现（只跑离线，与门禁一致），修到零回归 |
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
> **切到管理员状态。** 这一章全是一次性操作，但做错了后面处处别扭。
```
new:
```text
> **切到管理员状态。** 这一章全是一次性操作，但做错了后面处处别扭。
>
> **当前状态（2026-10-07）**：本章的仓库初始化**已完成**（骨架 + CODEOWNERS，随 CHG-002）；保留作参考。
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
> **切到管理员状态。** 这一章是全手册最容易出事的地方。
```
new:
```text
> **切到管理员状态。** 这一章是全手册最容易出事的地方。
>
> **当前状态（2026-10-07）**：第 1 批 `gate-3-schema`、`gate-5-regression`、`gate-6-ai-use-log` **已上线**；`gate-1/2/4` 待第 2–4 批（见 9.4）。
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
> **切到管理员状态，而且这是最后一班岗。**
```
new:
```text
> **切到管理员状态，而且这是最后一班岗。**
>
> **当前状态**：尚未到冻结阶段；本章留待冲刺收尾时执行。
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

#### Agent

再给《管理员开局清单》加一个归档状态（它也是这次“已完成”的一次性清单），然后统一核对。

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员开局清单.md`

old:
```text
# 管理员开局清单：从 fork 到第一批门禁上线

> **给谁看**：管理员（`@JHB11Hinson`）。**一次性**，走完就可以归档。
```
new:
```text
# 管理员开局清单：从 fork 到第一批门禁上线

> **状态（2026-10-07）：已完成，转为归档/复用参考。** 阶段 0–6 已走完：**CHG-001**（src 布局）、**CHG-002**（治理骨架 + 第 1 批门禁 `gate-3/5/6` 上线）均已合并；`main` @ `7c3eb5a`。**不要再从头跑一遍。** 下一个待做是 **CHG-003：`AGENTS.
... [truncated 91 chars]
```

Output:

```text
Edited .opencode/manual/管理员开局清单.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== 残留错误命令（应仅剩 test/offline、test/live 与设计行）====="
for f in .opencode/manual/管理员手册.md .opencode/manual/开发者手册.md .opencode/manual/管理员开局清单.md .opencode/manual/开局清单核查指南.md; do
  echo "--- $f ---"
  grep -nE "opencode export |ruff check src && mypy src|86 个文件|先落 ADR|pytest -q test/ " "$f" || echo "  无残留 ✓"
done
echo; echo "===== 管理员手册里 mypy 剩余（应只有第9章设计行）====="
grep -n "mypy" .opencode/manual/管理员手册.md
echo; echo "===== 围栏成对检查 ====="
for f in .opencode/manual/*.md; do n=$(grep -c '^```' "$f"); printf '%-46s %s %s\n' "$(basename "$f")" "$n" "$([ $((n%2)) -eq 0 ] && echo '(成对✓)' || echo '(奇数✗)')"; done
echo; echo "===== 仍全部被忽略 ====="; git check-ignore -q .opencode/m
... [truncated 57 chars]

Output:

```text
===== 残留错误命令（应仅剩 test/offline、test/live 与设计行）=====
--- .opencode/manual/管理员手册.md ---
  无残留 ✓
--- .opencode/manual/开发者手册.md ---
  无残留 ✓
--- .opencode/manual/管理员开局清单.md ---
165:| 继承测试套件 | 86 个文件：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~12 秒（Python 3.12.14，干净 venv） |
--- .opencode/manual/开局清单核查指南.md ---
  无残留 ✓

===== 管理员手册里 mypy 剩余（应只有第9章设计行）=====
1571:> **注意**：`mypy` **尚未加入** `[dev]` 依赖，现在跑 `mypy src` 会报 `command not found`；第 2 批门禁上线时再补 `mypy.ini` 并加入依赖。当前结构层只跑 `ruff check src`。
2735:**`mypy` 上游没有配置**（全文没有 `[tool.mypy]`，CI 只跑 ruff）。你们要用 `mypy` 就自己加一个文件，**别碰 `pyproject.toml`**：
2738:cat > mypy.ini <<'EOF'
2739:[mypy]
2756:      - run: pip install ruff mypy
2764:      - run: mypy src || true
2772:| `mypy src \|\| true` | 先软上线观察；确认不再乱报之后**去掉 `\|\| true`** 再算正式上线 |
3125:| 在本地验证等价命令 | **AI（在会话里）+ 人（在终端）** | `ruff` / `mypy` / `pytest` / `check-jsonschema` |
3748:     "*/.pytest_cache/*" "*/.mypy_cache/*" "*/runs/*" "*/logs/*"
4026:| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `ruff check src`（mypy 在第 2 批门禁上线后加入；触及安全相关路径的 PR 还会跑 contract / security / API-surface / permission 检查），**让 AI 改**（不要手改） |
4111:| **静态分析** | 不运行代码，只"看"代码有没有风格问题、类型错误（`ruff`、`mypy`） |

===== 围栏成对检查 =====
管理员开局清单.md                       96 (成对✓)
管理员手册.md                             298 (成对✓)
开发者手册.md                             158 (成对✓)
开局清单核查指南.md                    6 (成对✓)
门禁上线排期表.md                       8 (成对✓)

===== 仍全部被忽略 =====
manual/ 已忽略 ✓
 M .
... [truncated 23 chars]
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员开局清单.md`

old:
```text
| 继承测试套件 | 86 个文件：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~12 秒（Python 3.12.14，干净 venv） |
```
new:
```text
| 继承测试套件 | 84 个测试模块（连同 `conftest.py`／`__init__.py` 共 86 个 Python 文件）：**1262 passed, 1 skipped**（可选依赖 `langchain_aws`）, **1 deselected**（`-m "not integration"`），~11 秒（Python 3.12.14，干净 venv，实测） |
```

Output:

```text
Edited .opencode/manual/管理员开局清单.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 开局清单 命令类问题 =="; grep -nE "opencode export |ruff check src && mypy src|pytest -q test/ " 管理员开局清单.md || echo "无 ✓"
echo; echo "== 排期表 前 25 行（看是否有过时状态） =="; sed -n '1,25p' 门禁上线排期表.md
echo; echo "== 排期表里 mypy/pytest/opencode =="; grep -nE "mypy src|pytest -q test/ |opencode export " 门禁上线排期表.md || echo "无 ✓"

Output:

```text
== 开局清单 命令类问题 ==
无 ✓

== 排期表 前 25 行（看是否有过时状态） ==
# 门禁上线排期表

> **给谁用**：管理员（本表全篇【管理员】）。
> **配哪份文件**：《管理员手册》第九章（分支保护与门禁上线）、第十章 10.1–10.2（冻结与核验）。
> **怎么用**：按 **节点 0 → 节点 4** 顺序推进，**每个节点都过了"完成标志"再进下一个**。
>
> **本表不复制命令正文**：YAML 与 `gh api` 的完整写法在《管理员手册》9.2–9.7（首次上线）与 **9.10–9.15**（门禁怎么看、让 AI 写门禁、新增/修改/删除的完整示例），本表只给**触发条件、前置检查、验证命令、故意违规实验、回退动作**。两份文件各管一件事，避免改一处漏一处。

---

## 一、总排期（一张表看完）

| 节点 | 什么时候能上（触发条件） | 门禁 | 手册节 | 完成标志 |
|---|---|---|---|---|
| **0. 保护 v1** | **现在**（CODEOWNERS 合并进 main 之后立刻） | 无门禁，只要求 PR + 1 批准 | 9.2 / 9.3 | `enforce_admins.enabled` = `true` |
| **1. 第 1 批** | 结构对齐合并之后（继承测试已全绿） | `gate-3-schema`、`gate-6-ai-use-log`、**`gate-5-regression`** | 9.4.3 / 9.4.4 | `contexts` 里出现这三个名字，且**各自故意红过一次** |
| **2. 第 2 批** | 第 1 批已在 `main` 上跑绿 | `gate-2-static-analysis`（**只查本 PR 改动的文件**） | 9.4.5 | 四道齐全；`mypy src \|\| true` 已按计划去掉 |
| **3. 第 3 批** | 评测集 + 评测脚本**能本地跑通** | `gate-4-semantic-eval`（先软上线） | 9.4.6 | 观察期内不再乱报错 → 转正进 `contexts` |
| **4. 第 4 批** | 团队**已养成**"先测试后实现"的习惯 | `gate-1-test-approval` | 9.4.7 | 六道齐全 |
| **5. 冻结复核** | 截止前 3–5 天 | 不加新门禁，只核对 | 10.1 / 10.2 | 冻结 tag 已推；六道在 main 上全绿 |

**节点之间的最短间隔由"内容"决定，不由日期决定** —— 在继承项目里**测试本来就有**（`test/offline/` 是上游那 86 个测试文件），所以第 1 批等的不是"测试"，而是"**结构对齐先合并**"（见《管理员手册》2.3、《管理员开局清单》阶段 2）。

---


== 排期表里 mypy/pytest/opencode ==
17:| **2. 第 2 批** | 第 1 批已在 `main` 上跑绿 | `gate-2-static-analysis`（**只查本 PR 改动的文件**） | 9.4.5 | 四道齐全；`mypy src \|\| true` 已按计划去掉 |
111:- [ ] `gate-2`：本 PR 改动文件的 `ruff check` 全绿；`mypy src` 结果可接受（不满意就先只查新模块，但要把这条策略写进
... [truncated 109 chars]
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/门禁上线排期表.md`

old:
```text
## 一、总排期（一张表看完）
```
new:
```text
> **状态（2026-10-07）**：**节点 0（保护 v1）与节点 1（第 1 批门禁）已完成**（CHG-002，`main` @ `7c3eb5a`）；**当前在节点 2 之前**。下一步是 CHG-003 `AGENTS.md` 与后续功能，之后按节点 2 → 3 → 4 推进。

## 一、总排期（一张表看完）
```

Output:

```text
Edited .opencode/manual/门禁上线排期表.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/门禁上线排期表.md`

old:
```text
**节点之间的最短间隔由"内容"决定，不由日期决定** —— 在继承项目里**测试本来就有**（`test/offline/` 是上游那 86 个测试文件），所以第 1 批等的不是"测试"，而是"**结构对齐先合并**"（见《管理员手册》2.3、《管理员开局清单》阶段 2）。
```
new:
```text
**节点之间的最短间隔由"内容"决定，不由日期决定** —— 在继承项目里**测试本来就有**（`test/offline/` 是上游那 84 个测试模块，共 86 个 Python 文件），所以第 1 批等的不是"测试"，而是"**结构对齐先合并**"（见《管理员手册》2.3、《管理员开局清单》阶段 2）。
```

Output:

```text
Edited .opencode/manual/门禁上线排期表.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "===== 全部手册：残留错误命令终检 ====="
grep -rnE "opencode export |ruff check src && mypy src|86 个文件|先落 ADR" .opencode/manual/*.md || echo "无残留 ✓"
echo; echo "===== 围栏成对 ====="
for f in .opencode/manual/*.md; do n=$(grep -c '^```' "$f"); printf '%-40s %s %s\n' "$(basename "$f")" "$n" "$([ $((n%2)) -eq 0 ] && echo '✓' || echo '✗')"; done
echo; echo "===== 全部仍被忽略、不入仓库 ====="
git check-ignore -q .opencode/manual/开发者手册.md && git check-ignore -q .opencode/manual/管理员手册.md && echo "manual/ 全部忽略 ✓"
git status --short

Output:

```text
===== 全部手册：残留错误命令终检 =====
无残留 ✓

===== 围栏成对 =====
管理员开局清单.md                 96 ✓
管理员手册.md                       298 ✓
开发者手册.md                       158 ✓
开局清单核查指南.md              6 ✓
门禁上线排期表.md                 8 ✓

===== 全部仍被忽略、不入仓库 =====
manual/ 全部忽略 ✓
 M .gitignore
?? .opencode/
```

#### Agent

全部完成。两份手册 + 两份配套清单都对齐了，并且把“管理员 vs 组员”的归属写清楚了。

## 一、《开发者手册》：7 处缺口全部补上

| # | 补在哪 | 内容 |
|---|---|---|
| 1 | §0.4 门禁 2 + §9.5 | 补全 PDF 要求：除“每次提交跑 lint/类型/依赖”外，**触及安全相关路径的 PR 还要跑 contract / security / API-surface / permission 检查** |
| 2 | 新增 **§4.8「D3/D4 各文件的具体内容要求」** | 逐条写全 PDF 要求：`structural-constraints` 的 4 条规则、`mcp-tool-manifest`、`verification-constraints` 的 4 条+三层验证、`debt-register` 的 **8 类 AI 技术债**、`bug-diary` 的字段、`review-memo` 字段 |
| 3 | §0.3 | 报告（D6）内容硬要求：贡献表、每人 300–500 词自省、过程质量证据（需求波动/缺陷趋势/歧义消解）、制品共同演进、人类监督抓到什么 |
| 4 | §2.2 | D8 的“**模块名与架构元素一一对应**”，并指向 `structural-constraints.md` |
| 5 | §4.5 | D2 各工件的角色归属说明 |

**归属划分（已写进 §4.8 与 §4.5）：**
- **【管理员】负责“规则与机器”**：`AGENTS.md`、`architecture-blueprint.md`、`structural-constraints.md`、`mcp-tool-manifest.md`、`permissions.jsonc`、`.opencode/rules.md`、`.agent/rules.md`、`verification-constraints.md`、`permission-model.md`、`runtime-policy-catalog.md`、`trace-matrix.md`、门禁与分支保护。
- **【组员】负责“证据与记录”**：需求条目、`invariants.md`、`memory-design.md`、`evaluation-table.md`、`evaluation-logbook.md`、`risk-list.md`、`option-ledger.md`、`debt-register.md`、`bug-diary.md`、`review-memo.md`、`transcripts`；**ADR 由做该功能的人写**（管理员管流程）。

## 二、《管理员手册》等：对齐现有情况

- **《管理员手册》**：顶部加「现状快照（2026-10-07）」；第二章标“结构对齐已完成（CHG-001）”、ADR-001/002 已落、测试数改 84 模块；§2.3 加“已完成”提示；§4.6 日常命令去掉未安装的 `mypy`、`pytest -q test/`→`pytest -q` 并加 mypy 说明；`opencode export`→`opencode session export`；门禁 2/5 行修正；第三/九/十章加状态（第 1 批门禁已上线、其余待做）。
- **《管理员开局清单》**：顶部加“已完成，转归档”横幅；测试数修正。
- **《门禁上线排期表》**：顶部加“节点 0/1 已完成，当前在节点 2 之前”；测试数修正。
- （上一轮已改）**《开发者手册》**、**《开局清单核查指南》**。

## 三、核对结果

- 全 5 份手册：**无残留错误命令**（`opencode export` / `ruff check src && mypy src` / `86 个文件` / `先落 ADR` 均已清）。
- 代码围栏全部成对（158 / 298 / 96 / 6 / 8）。
- 全部在 `.opencode/manual/` 下，**被 `.gitignore` 忽略，不会进仓库**。

一个提醒：第 9 章里 `mypy.ini` 与 `mypy src || true` 是**第 2 批门禁的设计**（有意保留，属未来步骤），不是错误；日常命令里的 mypy 已去掉并注明原因。现在是“文档如实反映现状、仓库缺口标为待办”的状态。

#### Human

```text
所以提需求怎么提，在开发者手册里演示一下，日常工作那里要写的具体，从提一个/改一个需求开始，一直到合并完成
```

#### Agent

明白，补一个“提/改需求”的完整闭环演示，放进日常循环（紧跟 §3.1.1）。

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
## 3.2 第 ① 步：同步 main
```
new:
```text
## 3.1.2 完整走一遍：提一条 / 改一条需求（type A，从开分支到合并）

> **这一节演示最小、最完整的“需求变更”闭环。** 需求变更 = §4.6 的 **A 类**（分支前缀 `req/`），**不写代码、不需要测试**，但必须走 PR + 别人批准 + 门禁 3。
> 例子：给登记册**新增**一条性能需求——单次分析的 wall-clock 时间不得超过基线 60%。示例
... [truncated 3684 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
**通用四件套**：1) 变更卡（进 PR 描述，见 3.4）2) 分支名带 CHG 编号 3) 提交信息带 trailer（`Refs:` / `Agent-Session:` / `AI-Use-Log:` / `Test-Approval:`）4) `docs/review-memo.md` 一条记录（见 7.5）。
```
new:
```text
> **A 类（改需求）的完整例子**（从开分支到合并）见 **3.1.2**。

**通用四件套**：1) 变更卡（进 PR 描述，见 3.4）2) 分支名带 CHG 编号 3) 提交信息带 trailer（`Refs:` / `Agent-Session:` / `AI-Use-Log:` / `Test-Approval:`）4) `docs/review-memo.md` 一条记录（见 7
... [truncated 4 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
**先单独走一次 `req/CHG-xxx` 变更**：在 `requirements.yaml` 增/改条目（七个字段：`id / type / statement / fit_criterion / priority / tradeoff / source`）→ `check-jsonschema --schemafile docs/req/req-schema.json docs/req/r
... [truncated 81 chars]
```
new:
```text
**先单独走一次 `req/CHG-xxx` 变更**：在 `requirements.yaml` 增/改条目（七个字段：`id / type / statement / fit_criterion / priority / tradeoff / source`）→ `check-jsonschema --schemafile docs/req/req-schema.json docs/req/r
... [truncated 100 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "== 新增小节存在 =="; grep -n "## 3.1.2\|完整例子\|完整命令演示见 3.1.2\|A 类（改需求）的完整例子" .opencode/manual/开发者手册.md
echo; echo "== 围栏成对 =="; for f in .opencode/manual/开发者手册.md; do n=$(grep -c '^```' "$f"); echo "$n $([ $((n%2)) -eq 0 ] && echo ✓ || echo ✗)"; done
echo; echo "== 仍被忽略 =="; git check-ignore -q .opencode/manual/开发者手册.md && echo ok

Output:

```text
== 新增小节存在 ==
1001:## 3.1.2 完整走一遍：提一条 / 改一条需求（type A，从开分支到合并）
1480:> **A 类（改需求）的完整例子**（从开分支到合并）见 **3.1.2**。

== 围栏成对 ==
172 ✓

== 仍被忽略 ==
ok
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
grep -n "完整命令演示" .opencode/manual/开发者手册.md
echo "---"; sed -n '1001,1006p' .opencode/manual/开发者手册.md

Output:

```text
970:| 要做的行为**是新的**，或要**改/删**一条已有需求 | **先单独走一次 `req/CHG-xxx` 变更**：在 `requirements.yaml` 增/改条目（七个字段：`id / type / statement / fit_criterion / priority / tradeoff / source`）→ `check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml` 通过 → 开 PR 合并。**这一步必须跑在写代码之前**（顺序反了，提交信息里的 `Re
... [truncated 311 chars]
```

#### Agent

补齐了。在《开发者手册》日常循环里新增 **§3.1.2「完整走一遍：提一条/改一条需求（type A，从开分支到合并）」**，紧跟 §3.1.1 的决策之后；并在 §3.1.1 和 §4.6（A 类行）加了指向它的交叉引用。

## 这一节演示的完整闭环（8 步）

例子：**新增**一条性能需求 `D1-REQ-PERF-001`（单次分析 wall-clock ≤ 基线 60%），编号 `CHG-021`。

| 步 | 做什么 | 关键命令/产物 |
|---|---|---|
| 0 | 同步 main、开 `req/` 分支 | `git switch -c req/CHG-021-perf-budget` |
| 1 | 改 `docs/req/requirements.yaml`（新增/修改/删除；含完整 YAML 与七字段说明表） | 按 ID 排序插入 |
| 2 | 本地先跑门禁 3 | `check-jsonschema --schemafile …` → `ok -- validation done` |
| 3 | 写变更卡（进 PR 描述） | Change ID / Deliverables / Related requirement / Fit criterion … |
| 4 | 提交、开 PR、请评审 | `git commit`（`req:` 前缀 + `Refs:`）、`gh pr create`、`gh pr checks` |
| 5 | 评审人查什么（需求专项） | source 真实、`fit_criterion` 机器可判、priority/tradeoff、ID 合规 |
| 6 | 评审记录 + 批准（**先 push 记录再 Approve**） | `review-memo.md` 模板 + `gh pr review --approve` |
| 7 | squash 合并、同步 | `gh pr merge --squash --delete-branch` |
| 8 | 收尾 + 下一步 | 另开 `feat/CHG-022-…` 走**先测试后实现**，把需求 ID 写进 `Refs:` 和 `trace-matrix.md` |

## 顺带讲清的几个易混点

- **需求变更不触发门禁 1、6**（没动 `src/`/`prompts/`/`.opencode/`），**但门禁 3 会跑**，门禁 5 也会照常跑一遍继承套件（应保持绿）。
- **不需要测试**；实现它的测试在之后的 `feat/` 里由“测试先行”产生。
- **改/删需求**的额外注意：改阈值/类型要检查测试与 `trace-matrix` 是否引用了旧值；**删需求必须同步删掉引用它的测试并登记**，否则门禁 5 一直红。
- 一句话收尾：**`req/CHG-xxx` 分支 → 改 `requirements.yaml` → `check-jsonschema` → PR+变更卡 → 门禁 3 绿 → 别人 APPROVE → squash 合并 →（之后另开 `feat/` 实现）。**

核对：开发者手册代码围栏 172、成对 ✓；仍在 `.opencode/manual/`、被 `.gitignore` 忽略，不进仓库。

需要的话，我可以照这个格式，再把 **B 类（改代码，含“先测试后实现”两次提交）** 和 **C 类（改治理文件）** 也各补一个同样的“从头到尾”完整演示。

#### Human

```text
可以，也包括最简单的改改普通文档（我知道有些文档不普通，可能是治理文件）
```

#### Agent

好，把 B/C 以及“普通文档”三类也按同样格式补全。一次性插入 §3.1.3–§3.1.5：

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
## 3.2 第 ① 步：同步 main
```
new:
```text
## 3.1.3 完整走一遍：改代码（type B，含“先测试后实现”两次提交）

> 例子：实现 **`D1-REQ-FUNC-001`**（假设已经在登记册里；登记见 3.1.2）——CLI 遇到空 `--ticker` 要报清晰错误、非零退出，而不是启动一次分析。示例编号 **CHG-022**。
> **这是最常见、也最需要纪律的一类**：门禁 1（测试批准）+ 门禁 5（回归）+ 门禁
... [truncated 5366 chars]
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
> **A 类（改需求）的完整例子**（从开分支到合并）见 **3.1.2**。
```
new:
```text
> **A / B / C 与“普通文档”的完整例子**（从开分支到合并）分别见 **3.1.2 / 3.1.3 / 3.1.4 / 3.1.5**；D 类（动门禁，仅管理员）见《管理员手册》9.12–9.15。
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "== 新增小节 =="; grep -nE "^## 3\.1\.[2-5] " .opencode/manual/开发者手册.md
echo; echo "== §4.6 指针 =="; grep -n "A / B / C 与" .opencode/manual/开发者手册.md
echo; echo "== 围栏成对 =="; n=$(grep -c '^```' .opencode/manual/开发者手册.md); echo "$n $([ $((n%2)) -eq 0 ] && echo ✓ || echo ✗)"
echo; echo "== 仍被忽略 =="; git check-ignore -q .opencode/manual/开发者手册.md && echo ok
echo; echo "== 行数 =="; wc -l .opencode/manual/开发者手册.md

Output:

```text
== 新增小节 ==
1001:## 3.1.2 完整走一遍：提一条 / 改一条需求（type A，从开分支到合并）
1117:## 3.1.3 完整走一遍：改代码（type B，含“先测试后实现”两次提交）
1199:## 3.1.4 完整走一遍：改治理文件（type C）
1243:## 3.1.5 完整走一遍：只改普通文档（最简单，type docs）

== §4.6 指针 ==
1646:> **A / B / C 与“普通文档”的完整例子**（从开分支到合并）分别见 **3.1.2 / 3.1.3 / 3.1.4 / 3.1.5**；D 类（动门禁，仅管理员）见《管理员手册》9.1
... [truncated 81 chars]
```

#### Agent

四类闭环都补齐了，放在日常循环里、紧跟 §3.1.1：

| 小节 | 类型 | 分支 | 要点 |
|---|---|---|---|
| **3.1.2** | A 改需求 | `req/CHG-021` | 登记需求 → `check-jsonschema` → PR + 变更卡 → 门禁 3 绿 → APPROVE → 合并 |
| **3.1.3** | B 改代码 | `feat/CHG-022` | 计划获批 → **先提测试拿批准** → 再提实现 + AI 日志 → 门禁 3/5/6 全绿 → **再批一次** → 合并 |
| **3.1.4** | C 改治理文件 | `gov/CHG-023` | **人落盘、AI 只出稿**；安全关键路径带 ADR；改 `.opencode/` 触发门禁 6 |
| **3.1.5** | 普通文档 | `docs/CHG-024` | 最简单：改 README 之类 → 不触发门禁 1/3/6 → 门禁 5 绿 → 批准 → 合并 |

## 每节都写了“具体到命令”的完整步骤

- **B 类**重点演示了两次提交：先 `git add test/ docs/review-memo.md`（标 `approval pending`）拿批准，再 `git add src/ docs/ai-use-log.yaml …` 提实现；并点明两个坑：
  - 只提测试时**门禁 6 可能暂时红**（它把 `test/` 也算触发条件），实现提交带上 AI 日志后转绿；
  - 推实现会**作废**之前的批准（`dismiss_stale_reviews`），合并前要**再请人批一次**。
- **C 类**先给了一张“三条关键差别”表（谁改 / 是否安全关键 / 门禁），并明确 **D 类（动门禁）不算 C，只有管理员能做**，指向《管理员手册》9.12–9.15。
- **普通文档**那节末尾附了一张 **“哪些‘文档’其实不普通”** 清单：`docs/req/**`=A、`docs/architecture/**` 要先 ADR、`AGENTS.md`/`Prompt.md`/`.opencode/**`/`.agent/**`/`.github/**`=C、`ai-use-log`/`review-memo` 各有触发规则、`bug-diary`/`debt-register` 有规定字段（见 §4.8）。

另外：§3.1.1 和 §4.6 都已加好交叉引用（“完整例子见 3.1.2–3.1.5”）。

核对：开发者手册 **190 个围栏、成对 ✓**；当前 2314 行；仍在 `.opencode/manual/`、被 `.gitignore` 忽略，不进仓库。

现在《开发者手册》日常循环的“看”是：§3.1 七步图 → §3.1.1 决策（先登记需求、要不要新测试）→ §3.1.2–3.1.5 四类完整闭环 → §3.2 起逐步拆解。

#### Human

```text
开发者手册已经完整了吗？对标整个课程项目要求来说，如果完整的话就顺手修下管理员手册，如果有不合理的地方的话
```

#### Agent

先给《开发者手册》做最终对标体检，再处理《管理员手册》。

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 开发手册：D1-D9 交付物速查是否齐全 =="
sed -n '/^# 附录：交付物速查/,/^## 附/p' 开发者手册.md | grep -oE "\*\*D[0-9]\*\*" | sort -u | tr '\n' ' '; echo
echo "== 开发手册：六道门禁是否都出现 =="
for g in gate-1-test-approval gate-2-static-analysis gate-3-schema gate-4-semantic-eval gate-5-regression gate-6-ai-use-log; do printf '%s:%s ' "$g" "$(grep -c "$g" 开发者手册.md)"; done; echo
echo "== 开发手册：ADB 设计过程/架构设计过程 =="; grep -n "架构设计过程\|design process" 开发者手册.md || echo "未提（小缺口）"
echo; echo "===== 管理员手册：日常循环的测试先行 ======"
grep -nE "先写测试|测试必须早于|先测试|第 ④ 步|测试批准|已有测试|不是每次" 管理员手册.md | head -20
echo; echo "===== 管理员手册：门禁2 设计（9.4.5 附近） ====="
grep -nE "gate-2-static-analysis|contract|API-surface|
... [truncated 39 chars]

Output:

```text
== 开发手册：D1-D9 交付物速查是否齐全 ==
**D1** **D2** **D3** **D4** **D5** **D6** **D7** **D8** **D9**
== 开发手册：六道门禁是否都出现 ==
gate-1-test-approval:2 gate-2-static-analysis:2 gate-3-schema:3 gate-4-semantic-eval:2 gate-5-regression:2 gate-6-ai-use-log:2
== 开发手册：ADB 设计过程/架构设计过程 ==
未提（小缺口）

===== 管理员手册：日常循环的测试先行 ==
... [truncated 1475 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 管理员手册 §5.6 标题与开头 =="; grep -n "^## 5.6\|^# 第五章" 管理员手册.md
sed -n '/^## 5.6/,/^## 5.7\|^# 第六章/p' 管理员手册.md | head -30
echo; echo "== 管理员手册是否已有“不是每次都要新测试/可复用继承测试”的日常提示 =="
grep -n "可复用\|继承测试\|不是每次" 管理员手册.md | head

Output:

```text
== 管理员手册 §5.6 标题与开头 ==
1644:# 第五章 仓库文件与交付物 【全员】
1785:## 5.6 变更登记：四类变更的完整操作示例 【全员】
## 5.6 变更登记：四类变更的完整操作示例 【全员】

> **这一节回答一个问题**：手上有件事要改，从开口到留下痕迹，**每一步该敲什么命令**。
>
> 四类变更 = **A 改需求 / B 改代码 / C 改 `AGENTS.md`（治理文件）/ D 动门禁**。
> 前三类里 A、B 人人都会做，C 只有人能改（AI 不许改），D 只有管理员能做（完整示例在 9.10–9.14）。
>
> **一句话**：**没有 C
... [truncated 1717 chars]
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents/.opencode/manual
echo "== 可疑命令扫描（管理员手册）=="
grep -nE "ruff check \.|ruff format|git add -A|git add \.|git push origin main" 管理员手册.md | head -20 || echo "无明显可疑 ✓"
echo; echo "== §5.6 结尾/指向 =="; sed -n '1785,1800p' 管理员手册.md
echo; echo "== 管理员手册是否提 PDF §6 门禁2 第二半句 ==="; grep -n "contract\|API-surface\|API surface\|权限检查" 管理员手册.md || echo "未提"

Output:

```text
== 可疑命令扫描（管理员手册）==
1235:git add .
1318:> **这一步做完必须提交并推送**（3.5.4 末尾就是那三行：`git add .github/` → `git commit` → `git push`）。
1357:| ② 200、③ 404 | 文件**还没提交/推送到 main**（只在本地或只在分支上）；分支保护读的是 main 上的那份 | `git add .github/CODEOWNERS && git commit -m "chore: add CODEOWNERS" && git push`，或先查分支：`gh api "repos/.../codeowners/errors?ref=<分支名>"` |
1391:git add .github/
2562:| **第 2 批** | `gate-2-static-analysis` | 确认"只查本 PR 改动文件"的写法能跑（见 2.7）之后 | **不要**对继承代码全量跑 `ruff check .`：那是在用你们的规则查上游代码，一次报几百条 |
2951:git add .github/workflows/ci.yml docs/code-governance/protection.json
3269:git add .github/workflows/ci.yml
3378:git add .github/workflows/ci.yml
3410:git add .github/workflows/ci.yml
3531:git add .github/workflows/ci.yml

== §5.6 结尾/指向 ==
## 5.6 变更登记：四类变更的完整操作示例 【全员】

> **这一节回答一个问题**：手上有件事要改，从开口到留下痕迹，**每一步该敲什么命令**。
>
> 四类变更 = **A 改需求 / B 改代码 / C 改 `AGENTS.md`（治理文件）/ D 动门禁**。
> 前三类里 A、B 人人都会做，C 只有人能改（AI 不许改），D 只有管理员能做（完整示例在 9.10–9.14）。
>
> **一句话**：**没有 CHG 编号的改动，不算一次变更。** CHG 是变更卡编号，说明见 4.4。

**语言约定（重要）**：本项目是**全英文项目**——仓库里的文件（代码、注释、配置、提示词、门禁、`AGENTS.md`、YAML/JSON 数据、提交信息、PR 标题）**一律用英文**。本手册正文是中文，但下面示例里凡是**会落到仓库或 PR 上**的内容都用英文写。第四章的示例先用中文帮你读懂流程；**实际提交照本节写**。

### 5.6.1 四类变更一张总表

| 变更类型 | 典型触发 | 分支前缀 | 走 PR | 谁批准 | 要不要更新 AI 日志 | 主要交付物 | 相关门禁 |
|---|---|---|---|---|---|---|---|
| **A 改需求** | 加 / 改 / 删一条需求 | `req/CHG-xxx` | 要 | 任意一位组员（`*` 四人通配，不能是自己） | 不要（不在门禁 6 的路径里） | D1、D2（追溯矩阵）、D6 | `gate-3-schema` |

== 管理员手册是否提 PDF §6 门禁2 第二半句 ===
4026:| `gate-2-static-analysis` | `ruff` / `mypy` 报错 | 本地跑 `
... [truncated 121 chars]
```

#### Agent

《开发者手册》对标结论：**硬要求已齐全**（D1–D9 速查、六道门禁、四类变更闭环、D3/D4 文件内容、报告要求都在）。只差一处小项：ADR 要“展示架构设计过程”。补上，然后修《管理员手册》里对标 PDF 不合理的地方。

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/开发者手册.md`

old:
```text
选定的架构、考虑过的备选、理由、后果、**什么情况下要重新考虑**。另外要写：
```
new:
```text
选定的架构、考虑过的备选、理由、后果、**什么情况下要重新考虑**，并展示**架构设计过程**。另外要写：
```

Output:

```text
Edited .opencode/manual/开发者手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
| `mypy src \|\| true` | 先软上线观察；确认不再乱报之后**去掉 `\|\| true`** 再算正式上线 |
```
new:
```text
| `mypy src \|\| true` | 先软上线观察；确认不再乱报之后**去掉 `\|\| true`** 再算正式上线 |

> **补课（PDF §6 门禁 2 的第二半句）**：课程要求门禁 2 除了“每次提交跑 lint / 类型 / 依赖”，**对触及安全相关路径的 PR 还要跑 contract / security / API-surface / permission 检查
... [truncated 136 chars]
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
**为什么**：如果实现和测试一起交，没人能判断"测试是不是照着实现写的"——那样的测试证明不了任何东西。**先交测试，等于先声明"我认为对的应该长这样"，然后再看实现能不能满足它。**
```
new:
```text
**为什么**：如果实现和测试一起交，没人能判断"测试是不是照着实现写的"——那样的测试证明不了任何东西。**先交测试，等于先声明"我认为对的应该长这样"，然后再看实现能不能满足它。**

> **两个前提别漏**：① **先登记需求**——新行为要先有 `D1-REQ-…`（见 5.6 与《开发者手册》3.1.2）；② **不是每次都要新写测试**——已有继承测试覆盖时**可复用**（见 2.4
... [truncated 74 chars]
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `edit`**

edit `/home/jhb/TradingAgents/.opencode/manual/管理员手册.md`

old:
```text
> **一句话**：**没有 CHG 编号的改动，不算一次变更。** CHG 是变更卡编号，说明见 4.4。
```
new:
```text
> **一句话**：**没有 CHG 编号的改动，不算一次变更。** CHG 是变更卡编号，说明见 4.4。
>
> **逐类的最短命令演示**（从开分支到合并）：见《开发者手册》**3.1.2**（A 改需求）/ **3.1.3**（B 改代码）/ **3.1.4**（C 改治理）/ **3.1.5**（普通文档）。
```

Output:

```text
Edited .opencode/manual/管理员手册.md (1 replacement)
```

**Tool: `shell`**

$ cd /home/jhb/TradingAgents
echo "== 改动落地确认 =="
grep -n "架构设计过程" .opencode/manual/开发者手册.md
grep -n "补课（PDF §6 门禁 2\|两个前提别漏\|逐类的最短命令演示" .opencode/manual/管理员手册.md
echo; echo "== 围栏成对 =="
for f in .opencode/manual/开发者手册.md .opencode/manual/管理员手册.md; do n=$(grep -c '^```' "$f"); printf '%-32s %s %s\n' "$(basename "$f")" "$n" "$([ $((n%2)) -eq 0 ] && echo ✓ || echo ✗)"; done
echo; echo "== 仍被忽略 =="; git check-ignore -q .opencode/manual/开发者手册.md && git check-ignore -q .opencode/manual/管理员手册.md && echo ok
echo; echo "== git status =="; git status --short

Output:

```text
== 改动落地确认 ==
1618:| `docs/architecture/adr/001-<choice>.md` | 选定的架构、考虑过的备选、理由、后果、**什么情况下要重新考虑**，并展示**架构设计过程**。另外要写：AI 组件的**分层上下文结构**（身份、常驻约束、检索知识、对话历史、可恢复状态、当前任务）、**组装流水线**（去重、排序、预算、压缩、组装）、**token 预算上限与压缩阈值**、**压缩后如何重新注入关键约束** |
1531:> **两个前提别漏**：① **先登记需求**——新行为要先有 `D1-REQ-…`（见 5.6 与《开发者手册》3.1.2）；②
... [truncated 626 chars]
```

#### Agent

## 《开发者手册》对标结论：硬要求已齐全 ✅

我对着 PDF 的 D1–D9、第 4/5/6 节逐条体检：

- **D1–D9 速查齐全**（附录里 9 个都在）；**六道门禁**都在。
- **D1** 需求字段/7 类型/MoSCoW/tradeoff/source + `req-schema` + 门禁 3 ✅
- **D2** 11 类工件（含蓝图权威边界、ADR 的 AI 分层上下文/装配/预算/压缩/再注入）✅
- **D3/D4** 全部文件内容要求（structural-constraints、mcp-tool-manifest、verification-constraints、debt-register 8 类、bug-diary 字段）✅（§4.8）
- **D5** 会话记录（原始 + 六环节 + 干预类型）✅
- **D6** 报告字数/贡献表/自省 + 内容硬要求 ✅
- **D7** 六道门禁 + 分支保护 + README 四要素 ✅
- **D8** src/test 分离 + 模块名对应架构元素 ✅
- **D9** Prompt.md ✅
- **四类变更**（A/B/C/普通文档）都有“从开分支到合并”的完整命令演示（§3.1.2–3.1.5）✅
- **第 4/5/6 节**结构、README、门禁要求 ✅

**唯一补的一处小项**：ADR 还要求“展示**架构设计过程**”，已加进 §4.5。

> 剩下的只有**报告/提交层面**的东西没进开发者手册（角色轮换、zip 提交格式、“更高分”标准）——那些属于 `Report.md`/D6 与提交说明，不是开发者工作流手册的职责，我没往里塞。

**所以：对“整个课程项目要求”而言，《开发者手册》作为开发者工作流手册已经完整。**

## 《管理员手册》修掉的不合理/不齐之处

| 位置 | 问题 | 修法 |
|---|---|---|
| §9.4.5 门禁 2 设计 | 只做了 PDF 门禁 2 的**前半句**（lint/类型/依赖），漏了**后半句**：对触及安全相关路径的 PR 要跑 contract / security / API-surface / permission 检查 | 加“补课”说明，指出第二半怎么补（落实安全关键路径判定后并入或另开 `gate-2b`） |
| §4.5 第④步 | 读起来像“每次都要新写测试”，且没说“先登记需求” | 加“两个前提别漏”：① 先登记需求；② **可复用已有继承测试**，只新行为/新不变量才必须新写，并指向《开发者手册》3.1.3 |
| §5.6 | 只有厚重的“四类变更”长示例，没指向更轻的命令演示 | 加指向《开发者手册》3.1.2–3.1.5 |
| （前几轮） | 章节状态、命令错误、基线数字、`opencode export`、`pytest -q test/`、`mypy src` 等 | 已全部对齐 |

核对：开发者手册 190 围栏、管理员手册 298 围栏，均成对 ✓；两份仍在 `.opencode/manual/`、被 `.gitignore` 忽略，不进仓库。

如果你还想让两份手册在“门禁 2 第二半句”上**真正落地**（而不只是文档提醒），那属于仓库里的门禁改造（`ci/` 变更 + 故意红实验），需要单开一条 `ci/CHG-xxx`——要的话我可以按第 9 章流程给你出一份任务书。

#### Human

```text
可以指定多个评审人吗？以及还有个小问题，评审意见可以直接推啊，不需要分支保护吗？不用写在手册里，我看下答案就行
```

#### Agent

可以，两个问题分开答。

## 1. 指定多个评审人

可以。命令层面：

- 建 PR 时：`gh pr create --reviewer alice,bob,carol`（逗号分隔）
- 建完再加：`gh pr edit <PR> --add-reviewer alice,bob,carol`
- 移除：`gh pr edit <PR> --remove-reviewer bob`
- 也能指定团队：`--reviewer <org>/<team>`

但要注意两点：

- **“请求评审”≠“必须都批”。** 加三个评审人只是通知/点名，真正卡合并的是**分支保护里的批准数**。你们现在的 `protection.json` 是 `required_approving_review_count: 1`，所以**只要一个人批准**就能合。
- 想要求**多个批准**，得改分支保护：把 `required_approving_review_count` 设成 `2`（甚至 3）。同一人不能重复计票。
- 另外 `require_code_owner_reviews`：你们现在是 `false`。若设成 `true`，则至少要有一个 **CODEOWNER** 批准——你们 `CODEOWNERS` 是四人通配 `*`，所以四人中任意一个批准都算。

一句话：**加几个评审人随意；“必须几个人批”由分支保护的批准数决定。**

## 2. 评审记录为什么能直接推 —— 它推的不是 main

关键点：**分支保护只保护 `main`（和显式标记为 protected 的分支），不保护功能分支。**

- 评审人做的是 `gh pr checkout <PR>` 切到**发起人的功能分支**（比如 `feat/CHG-022-...`），把 `docs/review-memo.md` 追加一段，`git push` —— 这个 push 落在**功能分支**上，**不是 main**，所以和分支保护没有冲突。
- 之所以评审人能往别人的分支推：你们是**同一个仓库的协作者（write 权限）**，所有分支都在同一个 repo 里，push 自己的任意分支（包括别人的功能分支）是允许的。**如果 PR 来自 fork**，评审人就推不上去了（除非开“允许维护者编辑”）——你们不是 fork 流程，所以没这个问题。
- **分支保护拦的是“合进 main”这一步**：必须走 PR、必须有足够批准、必须过要求的检查。评审记录的 push 不在这个环节。

所以流程是：

```
贡献者功能分支 ──(测试提交/实现提交，随便推)──► PR 等待
评审人 checkout 该分支 ── push review-memo（落在功能分支，不受保护）──► 再点 Approve
└─ 这时分支上多了评审人的提交
最后 gh pr merge --squash 才是唯一受分支保护约束的动作
```

⚠️ 一个副作用（手册 §7.6 讲的就是它）：评审人 push 记录这一步会新增提交，若 `dismiss_stale_reviews: true`，**会把之前的批准作废**。所以顺序必须是**先 push 评审记录，再点 Approve**，否则自己的批准会被自己刚推的提交清掉。

补充一句：如果评审人只想表态、不想动文件，也可以直接在 PR 上 `gh pr review --approve/--request-changes/--comment`（这是“评审”，不是 push）；`review-memo.md` 只是团队要求的**可审计留痕**，所以选择写进文件再推。

---

