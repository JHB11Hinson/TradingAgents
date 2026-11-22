### PR-56 — CHG-048 governance consistency checks and versioned prompt store

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: the final CHG-048 tree. The test commit (`5cd1be4`) lands first; this record is
  committed before the implementation commit, as gate-1 requires.
- Scope: `D1-REQ-GOV-006`, `D1-REQ-GOV-008` and `D1-REQ-GOV-012`. The change is governance and
  additive runtime infrastructure; it does not alter the graph, a model call, a gate or branch
  protection.
- Specification:
  - **GOV-006.** Add an offline check that parses `.opencode/permissions.jsonc`,
    `docs/architecture/permission-model.md` and `AGENTS.md` section 13, compares the read and write
    path sets, and fails when a path is present in one source and absent from another. It also
    checks that every source declares default deny and that no parser silently reads an empty set.
  - **GOV-008.** Add an offline check that fails on a registry requirement without a trace-matrix
    row, a trace row without a registry entry, a non-`wont` row with empty evidence, an invariant
    requirement without an `INV-` row, an `INV-` row without a detail block, a missing required
    invariant field, a register/detail status disagreement, or a `must` requirement missing from the
    verification status table.
  - **GOV-012.** Add `src/tradingagents/prompts/loader.py`, `prompts/prompt_v1.0.yaml` and
    `prompts/index.yaml`. The loader verifies every entry's SHA-256, resolves a name to its highest
    version unless pinned, and fails closed on a tampered entry. The index locks each file hash so an
    in-place edit of v1.0 is visible. v1.0 baselines the five analyst prompt fragments; agent
    migration follows in batches as new version files.
- Architecture: one new additive package, `src/tradingagents/prompts/`, with a row in
  `docs/code-governance/structural-constraints.md` and the blueprint component table. No existing
  module, public entry point or authority boundary changes. `INV-02` and `INV-03` are corrected from
  **planned** to **implemented** (CHG-033), matching their already-published detail blocks.
- Code and tests: `pytest -q` -> 1577 passed, 1 skipped, 1 deselected, 99 subtests passed in 15.11 s;
  `ruff check` on the new package and the three tests -> all checks passed;
  `mypy --follow-imports=silent` on the new package -> no issues in 2 source files;
  `check-jsonschema` -> validation done; `python -m eval.run ... --budget 40000` -> pass (2 cases,
  0 failed; token ratio 0.270625, capped 0.927049, review 0.0, structured 1.0). The three checks add
  34 tests: positive checks against the live files and negative parser/tamper/status-mismatch cases.
- Runtime metadata: one new environment override, `TRADINGAGENTS_PROMPTS_DIR`, used only by the
  loader to point at another prompt store (tests use it). No dependency, model, permission or gate
  changed.
- Safety and efficiency: the loader is read-only and fails closed on a checksum mismatch; it does not
  write prompts or touch the authority boundary. The prompt baseline adds 8.7 KB of versioned text
  and no runtime calls. No secret or personal data enters the diff.
- Record truth: `AI-2026-11-22-002` names the change and the human constraints; the annotated session
  record captures the baseline, the RED step and the final verification. `DEBT-001` records that the
  remaining runtime prompts are still embedded, so the prompt store is not described as complete.

**Findings (non-blocking).**

1. The file-hash index detects an accidental in-place edit; a deliberate edit that also rewrites the
   index is a review signal rather than a cryptographic proof. A future CI history check can close
   that gap, but it would need full Git history in gate-5.
2. v1.0 covers the five analyst prompt fragments, not every runtime prompt. The remaining prompts are
   explicitly visible in `DEBT-001` and migrate in batches, each as a new version file.
3. `INV-02`/`INV-03` were already implemented in CHG-033; this change fixes the register, not the
   behavior. The status check now fails if the register and detail block disagree again.
4. The permission test compares read/write paths, not the command tiers. `AGENTS.md` section 13
   summarises commands in prose while the other two files list them; the requirement's fit criterion
   is the read/write whitelist, so command comparison remains a review step.

- Tests: test/offline/test_permission_consistency.py, test/offline/test_governance_registry.py, test/offline/test_prompt_versioning.py
- Verdict: APPROVE

The three checks make the existing governance claims falsifiable, the prompt store is read-only and
fails closed, and the docs corrections match the code already shipped in CHG-033. The change is not
on a safety-critical path; the author still does not self-approve.
