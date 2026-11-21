# ADR-012: Repeated tool-call detection and the inherited bound test

- **Status:** accepted (CHG-044, 2026-11-21). Approved by the owner's standing instruction; the
  coding agent applied the edit and did not approve or merge.
- **Requirement:** `D1-REQ-TERM-002`.
- **Related:** ADR-009 (termination), `graph/setup.py::_analyst_graph`.

## Context

An analyst could repeat the same tool call with the same arguments until `max_tool_rounds`. A
repeated call is not progress, and the round bound is a backstop, not a detector. The inherited
end-to-end test used a fake model that called the same tool with the same arguments every round to
prove the hard bound; after this change that model exercises the new detector instead, so its
`3 * 3` assertion no longer describes the path it claims to test.

## Decision

- Add `identical_call_repeat(messages, limit=2)` in `graph/setup.py`. It canonicalises each call as
  `(name, json.dumps(args, sort_keys=True))`, ignores call ids and dict key order, and returns the
  tool name when the same call occupies `limit` consecutive AI rounds.
- `more_or_wrap_up` wraps up when the bound is reached **or** the detector fires. The detector is
  consulted first in the boolean expression, but the hard bound remains the backstop for a model
  that varies its calls.
- Update the inherited `LoopingModel` to vary a date argument each round. Its `3 * 3` assertion now
  genuinely tests the hard bound; `test_repeated_tool_calls.py` owns the repeated-call path and its
  negative test. No assertion was weakened.

## Consequences

- A model repeating one call is forced to write its report at the second identical round.
- A model that varies its calls still reaches `max_tool_rounds`; the recursion-limit guard is
  unchanged.
- The detector is pure and does not add a model call or a state key.
