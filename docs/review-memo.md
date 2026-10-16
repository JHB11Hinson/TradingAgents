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

