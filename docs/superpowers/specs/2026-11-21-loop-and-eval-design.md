# Design: repeated tool calls and structured-output measurement (CHG-044/CHG-045)

- **Status:** approved by the owner's standing instruction, 2026-11-21.
- **Scope:** `D1-REQ-TERM-002`, `D1-REQ-QUAL-001`.
- **Out of scope:** the debate schema, guardrails, prompt versioning.

## Intent

Two `should` gaps remain. The analyst loop only stops at `max_tool_rounds`; a model repeating the
same call with the same arguments loops until that bound. The evaluation reports `review_rate` but
not the structured-output pass rate `QUAL-001` names.

## TERM-002 — repeated identical tool calls

- `graph/setup.py` gains a pure `identical_call_repeat(messages, limit=2)` helper: canonicalise every
  `AIMessage.tool_calls` entry by `(name, json.dumps(args, sort_keys=True))`, and return the name when
  the same canonical call appears `limit` times in a row.
- `more_or_wrap_up` returns `wrap_up` when `rounds >= max_tool_rounds` **or** a repeated call is
  detected; the wrap-up log names the repeated tool.
- Tests drive a scripted model that repeats one identical call with a high `max_tool_rounds` and
  assert the wrap-up happens at the second repeat, plus a negative test that disables the detector
  and observes the loop continue.
- No config knob: two identical consecutive calls are not progress; the bound remains the backstop.

## QUAL-001 — structured-output pass rate

- The Portfolio Manager already records `final_decision_source` (`structured`, `free_text`,
  `review`) for SAFE-002. `eval/replay.py` reads it from the final state and passes
  `structured_output_ok = source == "structured"` into `CaseObservation`.
- `evaluation/metrics.py` adds `structured_output_pass_rate` = share of successful cases whose final
  decision came from a validated schema; a case with `structured_output_ok=False` lowers it.
- `eval/thresholds.yaml` adds `structured_output_pass_rate: {min: 1.0}`.
- `eval/replay.py`'s `ScriptedModel` gains a deterministic `with_structured_output` implementation
  for the six schemas it can be asked for (`SentimentReport`, `DebateTurn`, `ResearchPlan`,
  `TraderProposal`, `PortfolioDecision`), so the fixed set exercises the real structured path.
- `CaseResult`/report JSON carry the per-case flag.

## Acceptance

- A repeating call reaches `wrap_up` before `max_tool_rounds`; removing the detector lets it run to
  the bound.
- The fixed set reports `structured_output_pass_rate == 1.0`; a case marked free-text lowers it.
- `pytest -q` and `python -m eval.run` green.
