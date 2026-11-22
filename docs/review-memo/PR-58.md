### PR-58 — CHG-049 runtime prompt store

- Reviewer: `github-actions[bot]` (`.github/workflows/bot-review.yml`). **Automated non-author
  review**, requested by the owner with the `bot-review` label; the record names the reviewer as
  automated.
- Head reviewed: the final CHG-049 tree. The test commit (`3cd847d`) lands first; this record is
  committed before the implementation commit, as gate-1 requires. Final verification evidence is
  added in the documentation commit before the bot approval is posted.
- Scope: `D1-REQ-GOV-012`; related `D1-REQ-EVAL-002`, `D1-REQ-GOV-010`. The change moves the source
  of every agent prompt from `src/tradingagents/agents/**` to the versioned store. It does not
  change the graph, a model, a gate or branch protection.
- Specification:
  - **GOV-012.** Every one of the twelve agent nodes loads its role, preamble and task text at node
    call time with `prompts.load_prompt(name).text`. `prompts/prompt_v1.1.yaml` adds the fragments
    v1.0 does not carry; v1.0 is not edited and `prompts/index.yaml` appends the new file hash.
  - The three shared instruction fragments move too: `shared.debate_turn_instruction`,
    `shared.no_external_tools`, `shared.language_instruction`.
  - Dynamic values (reports, debate history, instrument and portfolio context, dates, ticker,
    subreddit names, language) are `str.format` arguments and are never parsed as templates.
  - A missing, malformed or tampered store raises `PromptError`; there is no embedded fallback.
  - `DEBT-001` moves from `mitigated` to `closed`, naming CHG-049 and the deterministic context
    builders that remain outside the store by design.
- Architecture: no graph or public-interface change. Prompts load inside the node function, not at
  module import, so a missing store cannot break `import tradingagents` / `import cli.main`. ADR-015
  records the decision, the rejected alternatives and the packaging limit (a non-editable wheel does
  not ship `prompts/` yet).
- Code and tests: the new `test/offline/test_prompt_runtime.py` pins all twelve nodes to their store
  entries with a sentinel loader, proves a missing entry fails the node closed, fails when a
  migrated prompt reappears in `src/`, checks braced report values are inserted verbatim, and checks
  that import does not read the store. `test_prompt_versioning.py` adds the v1.1 assertions. Four
  existing tests that asserted prompt text in module source now read the store instead; none is an
  inherited test. Final verification: `pytest -q` -> 1611 passed, 1 skipped, 1 deselected, 99
  subtests passed in 34.03 s; `ruff check` on the changed files -> all checks passed;
  `mypy --follow-imports=silent` on the fifteen changed source files -> no issues;
  `check-jsonschema` -> validation done; `python -m eval.run --set eval/fixed-set.json
  --thresholds eval/thresholds.yaml --budget 40000` -> pass (2 cases, 0 failed; total token ratio
  0.270625, capped 0.927049, review 0.0, structured 1.0). The before/after golden capture of all
  twelve nodes is identical, so the change moves the prompt source, not the text.
- Runtime metadata: no new dependency, model, permission, gate or environment variable. The
  existing `TRADINGAGENTS_PROMPTS_DIR` override is unchanged.
- Safety and efficiency: the loader is read-only and fails closed. The migration preserves the
  prompt text byte-for-byte; the before/after golden capture of all twelve nodes is the evidence in
  the review record. No secret or personal data enters the diff.
- Record truth: this record is the gate-1 test approval. The bot approval posted on the final head
  is the PR approval; `dismiss_stale_reviews` applies, so the label is applied only after the last
  push. The author does not self-approve.

**Findings (non-blocking).**

1. The store is read per node call. A prompt file edited during a run can be observed by later
   nodes; mid-run prompt rotation is not supported and is not needed for a single analysis.
2. A non-editable wheel does not ship the root `prompts/` directory yet. The CI and CLI use
   `pip install -e .`; the limit is recorded in ADR-015 rather than hidden by a fallback.
3. Deterministic context builders (`build_instrument_context`, the "not part of this run" markers)
   and the optional TypeSafe post-screen classifier prompts remain in `src/` as data-producing code,
   not agent role prompts. `DEBT-001` states that boundary.

- Tests: test/offline/test_prompt_runtime.py, test/offline/test_prompt_versioning.py, test/offline/test_prompt_integrity.py, test/offline/test_structured_agent_prompts.py, test/offline/test_news_analyst_prompt.py, test/offline/test_structured_agents.py
- Verdict: APPROVE

The tests make the runtime sourcing claim falsifiable, the node-call load keeps the package import
contract intact, and the fail-closed rule matches the existing loader. The change is additive and
does not touch the authority boundary; the author still does not self-approve.
