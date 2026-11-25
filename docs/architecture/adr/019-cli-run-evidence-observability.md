# ADR-019: CLI run evidence and advisory guardrail telemetry

- **Status:** proposed (CHG-057, 2026-11-25) — awaiting the non-author review of the pull
  request. The coding agent applied the edit; the agent did not approve or merge.
- **Requirement:** `D1-REQ-OBS-001`, `D1-REQ-OBS-002`, `D1-REQ-OBS-003`, `D1-REQ-COST-003`,
  `D1-REQ-TERM-001`; supports `D1-REQ-SAFE-001`, `D1-REQ-SAFE-002`, `D1-REQ-SAFE-003`,
  `D1-REQ-DEBATE-001`, `D1-REQ-DEBATE-002`, `D1-REQ-MEM-003`.
- **Related:** `AGENTS.md` §8 (authority boundary), §11 (safety-critical paths); ADR-004 (context
  assembly), ADR-005 (telemetry seam), ADR-010 (guardrails), ADR-018 (safety-path guard).

## Context

The inherited CLI still shows only the upstream live view. The project's context budget, telemetry,
structured debate, termination, guardrails and memory attribution write machine-readable artifacts,
but a person running `tradingagents` cannot see them. This weakens the demo and makes the new
modules invisible to a reviewer even though the evidence exists in the state log, trace and
manifest.

The change touches one safety-critical path: `src/tradingagents/agents/managers/`. The Portfolio
Manager is the authority boundary's final decision point (`D1-REQ-SAFE-002/003`). Editing that file
for presentation alone would be unsafe; the change must be observational and must not alter what
the deterministic guardrails do.

## Decision

- Add a post-run Rich `Run Evidence` panel and a read-only `tradingagents inspect` command. Both
  read existing artifacts; neither changes the live layout, the graph wiring or the saved report
  tree.
- Add `guardrail_event(name, reason, *, node=None)` to the existing telemetry seam (ADR-005). It is
  a `span(kind="guardrail")` that inherits the active parent phase, is a no-op outside a telemetry
  scope, and stores only allowlisted `node`/`reason` attributes.
- Emit advisory events at the existing guardrail call sites:
  `guardrail.instruction_blocked` from retrieved blocks, analyst tool-result scrubbing and the
  sentiment pre-fetch; `guardrail.position_clipped`, `guardrail.decision_review` and
  `guardrail.budget_review` from the Portfolio Manager.
- `reason` carries only pattern names, percentages or fixed contract text. Raw external text never
  enters the event.
- The state log gains additive `final_decision_source`, `memory_note`, `memory_sources` and
  `turn_records` fields so `inspect` can replay the evidence. Older logs remain readable through
  `.get` defaults.
- The run path degrades a corrupt trace to `not written`; `inspect` is strict and reports a corrupt
  saved trace as one red line and exit 1. Evidence rendering in `run.py` is wrapped so it can never
  fail a finished run.
- The pure guardrail functions (`scrub_untrusted`, `enforce_position_ceiling`,
  `clip_free_text_decision`, `validate_free_text_decision`) are unchanged. The authority boundary
  remains deterministic code; telemetry is advisory.

## Consequences

- The safety-critical change is observational only: a telemetry failure is a warning, never a
  changed decision (`OBS-003`), and the Portfolio Manager's clipping/review paths keep their exact
  prior behavior.
- The CLI now exposes the context budget, structured debate records, guardrail actions, memory
  source ids and telemetry paths without changing the inherited style.
- A corrupt trace cannot fail a run; it is either omitted from the panel or reported by `inspect`.
- No new dependency is introduced (`re` is stdlib; Rich is already declared).
- Future changes that alter guardrail behavior still require their own ADR; this record covers only
  the telemetry seam and the read-only presentation.

## Alternatives considered

- **Parse `message_tool.log` or the logger output.** Rejected: guardrails log through `logging`, not
  the CLI message buffer, and the log lacks structured events.
- **Add a fourth `run_evidence.json` artifact.** Rejected: the state log, trace and manifest already
  carry the data; another artifact adds a retention and consistency surface.
- **Change the pure guardrail functions to return display metadata.** Rejected: it couples safety
  code to presentation and risks changing authoritative behavior.
- **Rebuild the live layout.** Rejected: large blast radius on inherited display tests, no
  requirement asks for it, and it would obscure the intended additive change.

## Verification

- `test/offline/test_guardrails.py`: all four guardrail event paths, the no-op outside telemetry,
  and the hostile-text absence assertion.
- `test/offline/test_cli_evidence.py`: collector/renderer, truncation, missing files, disabled
  telemetry, guardrail spans, mtime selection and old logs.
- `test/offline/test_cli_commands.py`: `inspect` success, missing run, markup-looking date and no
  analysis run.
- `test/offline/test_cli_memory_log.py`: an evidence-rendering failure does not fail the run.
- `test/offline/test_cli_display.py`: the state log records the new evidence fields.
- Full offline suite green; `ruff check src` clean; gate-1 test-approval record exists before the
  first `src/` commit.

## Rollback

Revert the pull request. The state log gains only additive fields, so older code ignores them; the
CLI panel and `inspect` are additive, and no persisted user state depends on them.
