# ADR-015: Runtime prompts load from the versioned store

- **Status:** accepted (CHG-049, PR-58, 2026-11-22). The coding agent applied the change; the
  automated non-author review approved it via the `bot-review` workflow; the agent did not approve
  or merge.
- **Requirement:** `D1-REQ-GOV-012`; related `D1-REQ-EVAL-002`, `D1-REQ-GOV-010`.
- **Related:** ADR-001 (baseline extension), PR-56 / CHG-048 (the loader and `prompt_v1.0.yaml`),
  `DEBT-001`.

## Context

CHG-048 added `prompts/prompt_v1.0.yaml`, `prompts/index.yaml` and
`src/tradingagents/prompts/loader.py`, but no agent called the loader. Every runtime prompt was
still a string literal in `src/tradingagents/agents/**`, so the store was a parallel copy that could
drift and the claim "runtime prompts are versioned" was only half true. `DEBT-001` records the
remaining literals as batch work and is `mitigated`, not closed.

A prompt change is only versioned if the text that reaches the model comes from the store. Copying
the text into the store while the agents keep their own literals creates two sources of truth and
makes the index a documentation artefact rather than a runtime control.

## Decision

- Every model-facing role, preamble and task prompt of the twelve agent nodes is loaded at node call
  time with `load_prompt(name).text`. Dynamic values (reports, debate history, instrument and
  portfolio context, dates, ticker, subreddit names, language) are passed as `str.format` values and
  are never parsed as templates.
- `prompts/prompt_v1.1.yaml` adds the fragments that v1.0 does not carry. v1.0 is not edited;
  `prompts/index.yaml` appends the new file's SHA-256.
- The shared fragments move as well: `shared.debate_turn_instruction`,
  `shared.no_external_tools`, `shared.language_instruction`.
- A missing, malformed or tampered store raises `PromptError`; there is no embedded fallback. A run
  fails closed rather than silently using an unversioned prompt.
- The prompt text is preserved byte-for-byte from the pre-change runtime. This change moves the
  source of the text; it does not change prompt quality or behaviour.
- `DEBT-001` moves to `closed`, naming CHG-049 as the closure and stating what remains outside the
  store (deterministic context builders and the optional TypeSafe post-screen classifier prompts).
- A guard test fails when a migrated role prompt's opening text reappears in
  `src/tradingagents/agents/**`.

## Alternatives rejected

- **Keep the literals and treat the store as documentation.** This leaves the drift the requirement
  exists to prevent, and the runtime still has no versioned prompt.
- **Move the full rendered prompt, including reports and histories, into YAML.** This couples run
  data to the store, makes every external text block a template, and increases formatting risk for
  no governance gain. The role text is the stable, reviewable part.
- **Load the store at module import.** A missing store would then break `import tradingagents`,
  violating the package import contract in `AGENTS.md` §8.

## Consequences

- A prompt edit is a new version file plus a loader call; gate-4 evaluates the text the model
  actually receives.
- The store is read per node call. A prompt file edited during a run can be observed by later nodes;
  mid-run prompt rotation is not supported.
- The store lives at the repository root. Editable installs (`pip install -e .`, the CI and CLI
  path) resolve it. A non-editable wheel does not ship `prompts/` yet; that packaging limit is
  recorded rather than hidden behind a fallback.
- Adding an agent means adding its prompt names to the store and to the runtime test inventory.
