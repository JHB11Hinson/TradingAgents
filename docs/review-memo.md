# Review memos

### CHG-001 — src layout alignment
- Operator: JHB11Hinson
- Requirement: D1-REQ-GOV-001
- What changed: `tradingagents/` -> `src/tradingagents/`, `cli/` -> `src/cli/`, `tests/` ->
  `test/offline/`, new `test/live/`; pyproject declares the src layout, the build floor and
  `testpaths`; three inherited tests had their repository-root lookup updated (no assertions
  changed)
- Why: the brief (section 5 / D8) requires `src/` and a split offline/live test layout
- Covered by: the full inherited suite (`pytest -q`: 1262 passed, 1 skipped, 1 deselected,
  9.55 s) + `import tradingagents, cli.main` + a wheel containing both in-package resources
- Records: ADR-001, ADR-002, change card in PR #1
- Rollback: `git revert <squash sha>`

### CHG-002 — first blocking gate batch (gate-3, gate-5, gate-6)
- Operator: JHB11Hinson
- Deliverables: D7, D4, D3
- Requirement: D1-REQ-GOV-001
- What changed: replaced the inherited upstream workflow (`.github/workflows/ci.yml`, `name: CI`,
  7 jobs: the py3.11-3.14 test matrix, clean-install smoke, full-repo ruff) with the first batch of
  our blocking gates (`name: gates`): `gate-3-schema`, `gate-6-ai-use-log` and
  `gate-5-regression`
- Why: the brief asks for machine-enforced blocking gates; batch 1 is the set that can go online
  immediately, now that the src alignment (CHG-001) has merged and the inherited suite is green
- Not in this PR: `docs/code-governance/protection.json`, putting the three names into the branch
  protection `contexts`, and the deliberate-violation experiments - those are the following admin
  nodes; `main` is not protected yet
- Notes: `.github/workflows/**` is human-only (developer manual 4.6 / admin manual 9.11.2); the
  workflow text is authored by JHB11Hinson; submitted on `ci/CHG-002-first-gates`
- Rollback: `git revert <squash sha>` (restores the upstream workflow)

### CHG-002 — branch protection v1 enabled (no PR possible)
- Operator: JHB11Hinson
- What changed: enabled branch protection on `main` with `enforce_admins: true`, one approving
  review, stale reviews dismissed, and force pushes and deletions blocked. `required_status_checks`
  was left `null` because the batch-1 gate names had not yet been registered.
- Why: the rules must bind everyone, admins included (admin manual 9.2); the gates are made
  blocking in their own admin node (9.4)
- Applied at: 2026-10-08
- Verification: `gh api repos/JHB11Hinson/TradingAgents/branches/main/protection --jq
  '.enforce_admins.enabled'` prints `true`
- Config copy: `docs/code-governance/protection.json` (this PR)
- Rollback: `gh api --method PUT
  repos/JHB11Hinson/TradingAgents/branches/main/protection --input protection-backup-20261008.json`

### CHG-002 — gate batch 1 brought blocking (contexts + strict)
- Operator: JHB11Hinson
- What changed: `required_status_checks` set to `strict: true` with
  `contexts = ["gate-3-schema", "gate-5-regression", "gate-6-ai-use-log"]`; the config copy in
  `docs/code-governance/protection.json` updated to match
- Why: the three batch-1 gates run green on `main`; making them blocking is the "online" half of
  admin manual 9.4.1
- Applied at: 2026-10-12
- Verification: `gh api repos/JHB11Hinson/TradingAgents/branches/main/protection --jq
  '.required_status_checks.contexts'` prints the three names; `check-runs` on `main` lists the
  same names
- Deliberate violations (admin manual 9.4.4): `gate-3-schema` failed on PR #4 (dropped
  `fit_criterion`); `gate-6-ai-use-log` failed on PR #5 (changed `src/` without updating
  `docs/ai-use-log.yaml`); `gate-5-regression` failed on PR #6 (broke an inherited assertion).
  Each PR reported `mergeStateStatus: BLOCKED`, and all three were closed without merging and
  their branches deleted.
- Rollback: `gh api --method PUT
  repos/JHB11Hinson/TradingAgents/branches/main/protection --input protection-backup-20261012.json`
### PR-3 — CHG-002-protection-baseline
- Reviewer: zihao9462-creator
- Specification: implements D1-REQ-GOV-001, within the change card scope
- Architecture: follows ADR-001, does not cross the authoritative boundary
- Code and tests: three-layer verification passed, one negative test, no skipped cases
- Runtime metadata: none
- Safety and efficiency:protection-baseline
- Verdict: APPROVE

### PR-7 — CHG-003 fix the dangling gate reference
- Reviewer: zihao9462-creator
- Specification: documentation-only fix; removes the dangling `ADR-003` reference in `architecture-blueprint.md` and points at the existing `docs/code-governance/protection.json` and CHG-002; no requirement claimed (n/a)
- Architecture: no architecture change; the referenced artifacts (ADR-001/002, protection.json, CHG-002) exist; no authoritative boundary crossed
- Code and tests: no `src/`/`test/` change; local `pytest -q` = 1262 passed / 1 skipped / 1 deselected, `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions; docs only
- Verdict: APPROVE

### PR-8 — CHG-004 register the must-priority requirements
- Reviewer: zihao9462-creator
- Specification: registers 20 must requirements plus the existing `D1-REQ-GOV-001`; 21 entries, all `priority: must`, all five required fields present; this PR is the registration, within change-card scope
- Architecture: no architecture change; requirements are the D1 source of truth; no authoritative boundary crossed
- Code and tests: no `src/`/`test/`; local `check-jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml` -> `ok -- validation done`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gate-3 green
- Runtime metadata: none
- Safety and efficiency: no new permissions
- Verdict: APPROVE

### PR-9 — CHG-005 add the requirements trace matrix
- Reviewer: zihao9462-creator
- Specification: adds `docs/architecture/trace-matrix.md` (D2.4), the `fit_criterion` of `D1-REQ-GOV-004`; 40 rows / 40 unique ids / 21 `must`; all 21 ids from CHG-004 present; component/test/monitor columns non-empty; planned components marked
- Architecture: traceability artifact, no architectural decision; consistent with ADR-001/002; no boundary crossed. Depends on CHG-004 (#8) for the `must` registry rows
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions
- Verdict: APPROVE

<!-- Batch review of the first governance/CI series (PR-10, 11, 13-21).
     Reviewed at head commits listed per entry. Local verification identical for every PR:
     `pytest -q` = 1262 passed / 1 skipped / 1 deselected; `ruff check src` = clean;
     gates gate-3-schema / gate-5-regression / gate-6-ai-use-log = pass. None of these PRs
     changes `src/` or `test/`, so checklist item 2 (tests before implementation) and item 3
     (negative test) are not applicable. Verdicts are intentionally left OPEN: no `gh pr review`
     was issued; the reviewer records the findings here and defers the approve / request-changes
     decision. Every entry carries the same blocking finding on checklist item 5 (record truth). -->

### PR-10 — CHG-006 add AGENTS.md, the coding-agent governance entry point
- Reviewer: AKAScarlett
- Head reviewed: `b2757349`
- Specification: adds `AGENTS.md` (D3, `D1-REQ-GOV-002`), twelve fixed sections; declares build target, artifact reading order, code baseline, readable/modifiable/frozen, module organization, integration contracts, verification, human-only/protected paths, STOP points; gate names match `ci.yml` (`gate-3/5/6` online) and `docs/code-governance/protection.json`
- Architecture: governance text only; consistent with ADR-001/002; §13 permission summary matches the JSONC/`permission-model.md` whitelist except for a `.env*` vs `.env` + `.env.*` representation (equivalent in meaning, not character-identical)
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions; the file states default deny. Reviewers must confirm the `.env*` vs `.env`/`.env.*` wording is aligned in the follow-up permission PR (#16)
- Record truth (checklist item 5): **BLOCKING** — the PR body says "Transcript: `transcripts/JHB11Hinson.md` (session export to be appended)" and the AI-use log (`AI-2026-10-30-001`) cites that file as its source, but `transcripts/JHB11Hinson.md` contains only the CHG-001 session (plus one CHG-014 excerpt); it has no CHG-006 session. The record does not yet back the commit it describes. Either append the CHG-006 session export or point the log at a transcript that exists
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5 (transcript/AI-use-log does not contain this change's session)

### PR-11 — CHG-007 add gate-2-static-analysis (batch 2)
- Reviewer: AKAScarlett
- Head reviewed: `b051b026`
- Specification: adds a `gate-2-static-analysis` job to `.github/workflows/ci.yml` (lint only the `src/**/*.py` files a PR touches, plus soft `mypy src`) and a root `mypy.ini`; uses the existing `[tool.ruff]`; does not touch `contexts` yet (registered in a later PR, per the admin manual). Body cites `D1-REQ-GOV-003`; the commit trailer cites `Refs: D7, D3`
- Architecture: gate change on the CI path; borrows the fetch-depth/diff pattern of gate-6; soft `mypy` cannot block, consistent with the "soft launch" note
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gate-2 job is a green no-op on this PR; gates 3/5/6 green
- Runtime metadata: new `mypy.ini` at repo root (`ignore_missing_imports = True`)
- Safety and efficiency: no new permissions; a deliberate violation must be shown red before registration (manual 9.11.4), not yet demonstrated here
- Requirement alignment (checklist item 6): **NOTE** — `D1-REQ-GOV-003` states "all six blocking gates must be online"; this PR brings one of six online and says so honestly in the change card. The body `Refs` (GOV-003) over-states completion of that requirement; the commit trailer (`D7, D3`) does not. Refs should be reconciled
- Record truth (checklist item 5): **BLOCKING** — same as PR-10: `transcripts/JHB11Hinson.md` has no CHG-007 session, yet the AI-use log (`AI-2026-10-30-002`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5, plus Refs reconciliation (GOV-003 scope)

### PR-13 — CHG-009 narrow gate-6 to the course floor (code or prompts)
- Reviewer: AKAScarlett
- Head reviewed: `e9be7c3b`
- Specification: one-line change to `gate-6-ai-use-log` in `.github/workflows/ci.yml`: the trigger regex drops `|\.opencode/`, so a change that touches only `.opencode/**` no longer forces an `ai-use-log.yaml` update. Body cites `D1-REQ-GOV-011`; commit trailer `Refs: D7, D3`
- Architecture: gate change; **relaxes** what the gate enforces
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: **DISPUTED — team ruling required.** Narrowing gate-6 stops `.opencode/**` changes from requiring an AI-use-log entry. AGENTS.md §9 treats gate weakening / renaming as red-line changes (frozen gate names, "never weaken a gate"), and the manual's checklist item 4 treats silently loosening a gate as the most dangerous category. The change may be legitimate (aligning gate-6 to the D5 course floor "code or prompts"), but it must be an explicit, reviewed decision, not a silent scope cut. This reviewer does not approve it unilaterally
- Requirement alignment (checklist item 6): `D1-REQ-GOV-011` is about transcripts + a current AI-use log; the commit trailer names `D7, D3`. The body `Refs` and the trailer do not match, and this PR adds no transcripts
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-009 session; the AI-use log (`AI-2026-10-30-003`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5; **PENDING TEAM RULING** on narrowing gate-6; Refs reconciliation

### PR-14 — CHG-010 add Prompt.md, the coding agent's launch instruction
- Reviewer: AKAScarlett
- Head reviewed: `bbe8d03d`
- Specification: adds `Prompt.md` (D9, `D1-REQ-GOV-013`): execution plan (traceability, interface contract, scope boundaries, testing strategy, steps, rollback), stop-for-approval before branch/code, staged human gates, self-verify with the §9 commands; states it is not a runtime prompt and never goes plan-to-merge unattended
- Architecture: static startup instruction; consistent with AGENTS.md gates; no boundary crossed
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-010 session; the AI-use log (`AI-2026-10-30-004`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5

### PR-15 — CHG-011 add the always-on rules and the project covenant
- Reviewer: AKAScarlett
- Head reviewed: `50f4a3c3`
- Specification: adds `.opencode/rules.md` (always-on behavioural rules) and `.agent/rules.md` (covenant with the five clauses: abstraction limits, dependency constraints, test independence incl. one negative test, safety-critical needs ADR + human approval, context freshness within one sprint); `D1-REQ-GOV-013`
- Architecture: governance text; tiers mirror the manuals and defer the machine-readable whitelist to GOV-006 (#16)
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: **DISPUTED — team ruling required.** This PR adds `.opencode/rules.md`, which the course marks as the single human-only file that the agent must not write. The PR body states the human owner directed the agent to draft it and that a human is "author of record", landing only through a reviewed PR. The file's own header restates "agent must not write it". Whether "agent drafts, human authors/approves" satisfies the human-only rule is a governance decision for the team, not for the reviewer alone. A human must read the file as author and endorse this framing before merge
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-011 session; the AI-use log (`AI-2026-10-30-005`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5; **PENDING TEAM RULING** on agent-drafted human-only `.opencode/rules.md`

### PR-16 — CHG-012 add the default-deny permission model (GOV-006)
- Reviewer: AKAScarlett
- Head reviewed: `f0779f01`
- Specification: adds `.opencode/permissions.jsonc`, `docs/architecture/permission-model.md`, and `docs/architecture/adr/003-authority-and-permission-model.md` (ADR required: safety-critical path, D7); default deny, `deny > ask > allow`, three roles. Body states it assumes PR-10 (AGENTS.md §13) merges first
- Architecture: ADR-003 present; authority boundary stated (model output advisory, deterministic code authoritative; SAFE-002/003); does not cross the boundary
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green. Verified locally: JSONC parses after comment stripping; 36 unique paths; `read.allow` (21) matches AGENTS §13; `write.ask` (10) matches; `write.deny` differs only by `.env*` (AGENTS §13) vs `.env` + `.env.*` (JSONC + `permission-model.md`)
- Runtime metadata: permission whitelist (machine-readable source of truth)
- Safety and efficiency: **NOTE** — the three sources must list the same whitelist; they agree except the `.env*` representation in AGENTS §13. Align the wording so all three are character-identical. No new permission is widened relative to AGENTS §13
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-012 session; the AI-use log (`AI-2026-10-30-006`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5; three-source `.env` wording alignment

### PR-17 — CHG-013 add the MCP and tool manifest (GOV-005)
- Reviewer: AKAScarlett
- Head reviewed: `fb0b965e`
- Specification: adds `docs/code-governance/mcp-tool-manifest.md` (`D1-REQ-GOV-005`): MCP servers = none (verified), 16 native tools, tool x role matrix, unknown tool/path/command denied
- Architecture: consistency rule ties it to `permissions.jsonc` and `permission-model.md`; no runtime-policy engine claimed; no boundary crossed
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions; the manifest should agree with #16's roles (plan/build/review)
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-013 session; the AI-use log (`AI-2026-10-30-007`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5

### PR-18 — CHG-014 ignore the Chinese workspace material under .opencode
- Reviewer: AKAScarlett
- Head reviewed: `e4fdb1b4`
- Specification: `.gitignore` only — keeps `.opencode/manual/` and adds `.opencode/功能需求表-讨论稿.md`, `.opencode/研究-现有Agent功能盘点.md`, `.opencode/tasks/`; leaves `.opencode/rules.md`, `permissions.jsonc`, `git-gh-rules` visible (verified with `git check-ignore`)
- Architecture: repository hygiene; no architectural change
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions; `.gitignore` has no effect on already-tracked files (body notes this correctly)
- Requirement alignment (checklist item 6): **NOTE** — the body cites `D1-REQ-GOV-013` (rules/covenant), which this `.gitignore` change does not implement; the commit trailer cites `Refs: D3`. Refs should point at the actual driver (repository hygiene), reconciled
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-014 session (the file has only a CHG-014 planning-phase excerpt unrelated to this `.gitignore` change); the AI-use log (`AI-2026-10-30-008`) cites the file
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5; Refs reconciliation (GOV-013 mismatch)

### PR-19 — CHG-015 add the structural constraints (GOV-007)
- Reviewer: AKAScarlett
- Head reviewed: `72975b2c`
- Specification: adds `docs/code-governance/structural-constraints.md` (`D1-REQ-GOV-007`): element->module table, extend-never-replace, module->ADR/requirement references, authority boundary; records the SAFE-003 gap honestly
- Architecture: traceability/structure artifact; consistent with ADR-001/002/003; no boundary crossed
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions; honestly discloses that SAFE-003 is not implemented
- Requirement alignment (checklist item 6): **BLOCKING** — `Refs: D1-REQ-GOV-007` is **not registered in `docs/req/requirements.yaml`** (21 entries; GOV-007 absent; it exists only in the draft table and the trace matrix). The checklist rejects a Refs that points at a non-existent requirement id. Register GOV-007 (should) in the registry, or change the Refs to a registered id with a note
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-015 session; the AI-use log (`AI-2026-10-30-009`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist items 5 and 6 (unregistered GOV-007)

### PR-20 — CHG-016 add the debt register and the bug diary (GOV-010)
- Reviewer: AKAScarlett
- Head reviewed: `9902736d`
- Specification: adds `docs/debt-register.md` (eight AI-era categories) and `docs/bug-diary.md` (three entries), each with the required fields (`D1-REQ-GOV-010`, D4)
- Architecture: QA records; no architectural change; correctly references the missing-transcript debt (DEBT-006) and the SAFE-003 gap
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: none
- Safety and efficiency: no new permissions; DEBT-006 openly records "1 of the required >=5 transcripts, stages not all covered"
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-016 session; the AI-use log (`AI-2026-10-30-010`) cites it. Note the self-reported DEBT-006 corroborates the batch-wide transcript gap
- Verdict: PENDING — CHANGES REQUIRED on checklist item 5

### PR-21 — CHG-017 add ADR-004, layered context assembly (CTX-004)
- Reviewer: AKAScarlett
- Head reviewed: `f902ad8d`
- Specification: adds `docs/architecture/adr/004-context-assembly.md` (`D1-REQ-CTX-004`, D2.2): six layers mapped to real fields, pipeline (dedupe->prioritize->budget->compact->assemble), 50k shared budget (COST-003), re-injection of P0, no-op-under-budget contract; states the assembler does not exist yet
- Architecture: design ADR only; consistent with ADR-001/002; honestly marks planned vs existing fields; does not claim implementation
- Code and tests: no `src/`/`test/`; `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green
- Runtime metadata: proposes `context_budget_tokens` default 50 000 (not yet implemented)
- Safety and efficiency: no new permissions; no behaviour change claimed under budget
- Requirement alignment (checklist item 6): **BLOCKING** — `Refs: D1-REQ-CTX-004` is **not registered in `docs/req/requirements.yaml`** (only CTX-001/003 are; CTX-004 exists only in the draft table and the trace matrix). Register CTX-004 (should) in the registry, or change the Refs to a registered id with a note
- Record truth (checklist item 5): **BLOCKING** — `transcripts/JHB11Hinson.md` has no CHG-017 session; the AI-use log (`AI-2026-10-30-011`) cites it
- Verdict: PENDING — CHANGES REQUIRED on checklist items 5 and 6 (unregistered CTX-004)

### Batch summary (PR-10, 11, 13-21)
- Blocking for every PR: checklist item 5 — the AI-use-log entries cite `transcripts/JHB11Hinson.md`, which contains only the CHG-001 session and no session for any of these changes. The record must be made true (append the session export, or repoint the log) before approval.
- Blocking for PR-19 and PR-21: checklist item 6 — Refs point at `D1-REQ-GOV-007` / `D1-REQ-CTX-004`, which are not in `docs/req/requirements.yaml`.
- Pending team ruling: PR-13 (narrows gate-6 below `.opencode/**`) and PR-15 (adds the human-only `.opencode/rules.md`).
- Needs reconciliation: PR-11 (GOV-003 six-gate scope), PR-16 (`.env*` wording across the three permission sources), PR-18 (Refs GOV-013 vs `.gitignore`), plus the body-Refs vs commit-trailer mismatches on PR-11/13.
- Passed locally for all: `pytest -q` 1262 passed / 1 skipped / 1 deselected; `ruff check src` clean; gates 3/5/6 green; no `src`/`test` change (items 2 and 3 not applicable).
- No `gh pr review` verdict was issued; the approve / request-changes decision is deferred to the reviewer + team after the findings above are addressed.

