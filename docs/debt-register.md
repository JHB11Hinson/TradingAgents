# Technical Debt Register

## Sprint 1 应补尽补备忘录（基于 PR 批量审查结果）

当前 11 个 PR 已按团队要求先行批准，但审查发现以下待办事项（由对应 PR 的提交者负责），需在后续 Sprint 补齐：

| ID | 类别 | 描述 | 责任人 | 状态 |
|---|---|---|---|---|
| DEBT-001 | 评测债 | 当前 11 个 PR 的 transcripts 缺失，需提交者补齐对应的原始会话记录。 | PR 提交者 (JHB11Hinson) | TODO |
| DEBT-002 | 护栏债 | PR#13 缩减了 gate-6 范围，需恢复对 `.opencode/` 的检查。 | PR 提交者 (JHB11Hinson) | TODO |
| DEBT-003 | 不可触碰代码 | PR#15 修改了人类专属文件 `.opencode/rules.md`，需确认合规性。 | PR 提交者 (JHB11Hinson) | TODO |
| DEBT-004 | 隐藏依赖 | 补登记 `requirements.yaml` 中缺失的 GOV-007、CTX-004 等 ID。 | PR 提交者 (JHB11Hinson) | TODO |
