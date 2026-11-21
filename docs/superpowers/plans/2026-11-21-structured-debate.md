# Structured Debate Implementation Plan (CHG-043)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** implement `D1-REQ-DEBATE-001` and `D1-REQ-DEBATE-002` with one `DebateTurn` schema, a
deterministic adapter and state records for all five debate nodes.

**Architecture:** schema + render/parse helpers in `agents/`; additive state fields; no new graph
node or edge.

**Tech Stack:** Python 3.11+, Pydantic v2, pytest, ruff, mypy.

**Spec:** `docs/superpowers/specs/2026-11-21-structured-debate-design.md`

## Global Constraints

- Tests before `src/`, separate commits.
- Every test names `DEBATE-001` or `DEBATE-002`; negative test for a missing field / missing
  convergence.
- `pytest -q` green; eval replay green; no prompt file edited in place.

## Review Focus

- A prose-only provider still produces a schema-valid turn and the debate continues.
- A JSON turn with `converge: ""` is rejected, not silently accepted.
- The termination digest still covers every turn and the bound still wins first.
- The risk debate's three-speaker cycle still rotates and one turn adds one record.

---

### Task 1: Schema, render and parse

**Files:**
- Modify: `src/tradingagents/agents/schemas.py`
- Create: `src/tradingagents/agents/debate.py`
- Test: `test/offline/test_debate_turns.py`

**Interfaces:**
- Produces: `DebateEvidence(source: str, quote: str)`;
  `DebateTurn(claim, evidence, rebuttal, confidence, diverge, converge)`;
  `render_debate_turn(turn: DebateTurn, side: str) -> str`;
  `parse_debate_turn(text: str, *, side: str, opponent: str = "") -> DebateTurn`;
  `invoke_debate_turn(llm, prompt, *, side: str, opponent: str = "") -> tuple[DebateTurn, str]`.

- [ ] **Step 1: Write the failing tests**

```python
def _turn(**over):
    base = dict(claim="c", evidence=[DebateEvidence(source="s", quote="q")],
                rebuttal="r", confidence="high", diverge="d", converge="c")
    base.update(over)
    return DebateTurn(**base)

def test_a_turn_missing_a_field_is_rejected():
    with pytest.raises(ValidationError):
        _turn(claim="")

def test_a_turn_without_convergence_is_rejected():
    with pytest.raises(ValidationError):
        _turn(converge="")

def test_a_json_turn_renders_all_sections():
    text = render_debate_turn(_turn(), "Bull Analyst")
    for label in ("Claim", "Evidence", "Rebuttal", "Confidence", "Diverge", "Converge"):
        assert f"**{label}**" in text

def test_a_prose_turn_is_adapted():
    turn = parse_debate_turn("Bull Analyst: growth is intact", side="Bull Analyst")
    assert turn.claim and turn.evidence and turn.converge
```

- [ ] **Step 2: Run and verify failure**

Run: `pytest -q test/offline/test_debate_turns.py`
Expected: FAIL (imports missing).

- [ ] **Step 3: Implement**

Model validators reject empty strings and an empty evidence list. `parse_debate_turn` tries
`DebateTurn.model_validate_json`, then a fenced JSON block, then adapts prose with a non-empty
converge marker. `invoke_debate_turn` tries `llm.with_structured_output(DebateTurn)` and validates
the return is a `DebateTurn`; otherwise it calls `llm.invoke` and parses. Return the raw text for the
termination digest.

- [ ] **Step 4: Run and verify pass**

Run: `pytest -q test/offline/test_debate_turns.py`
Expected: PASS.

### Task 2: State and propagation

**Files:**
- Modify: `src/tradingagents/agents/state.py`
- Modify: `src/tradingagents/graph/propagation.py`
- Modify: `src/tradingagents/agents/managers/research_manager.py`
- Modify: `src/tradingagents/agents/managers/portfolio_manager.py`
- Test: `test/offline/test_debate_turns.py`

**Interfaces:**
- `turn_records: list[dict]` on both debate states; one record per turn.

- [ ] **Step 1: Write the failing tests**

```python
def test_initial_state_has_empty_turn_records():
    state = Propagator().create_initial_state("NVDA", "2026-01-09")
    assert state["investment_debate_state"]["turn_records"] == []
    assert state["risk_debate_state"]["turn_records"] == []

def test_managers_copy_the_records_through():
    ...
```

- [ ] **Step 2: Run and verify failure**

Run: `pytest -q test/offline/test_debate_turns.py -k records`
Expected: FAIL.

- [ ] **Step 3: Implement**

Add the TypedDict field and the initial value; managers copy with `.get("turn_records", [])`.

- [ ] **Step 4: Run and verify pass**

Run: `pytest -q test/offline/test_debate_turns.py -k records`
Expected: PASS.

### Task 3: Wire the five debate nodes

**Files:**
- Modify: `src/tradingagents/agents/researchers/bull_researcher.py`
- Modify: `src/tradingagents/agents/researchers/bear_researcher.py`
- Modify: `src/tradingagents/agents/risk_mgmt/aggressive_debator.py`
- Modify: `src/tradingagents/agents/risk_mgmt/conservative_debator.py`
- Modify: `src/tradingagents/agents/risk_mgmt/neutral_debator.py`
- Test: `test/offline/test_debate_turns.py`

**Interfaces:**
- Each node returns one new `turn_records` entry and one digest.

- [ ] **Step 1: Write the failing tests**

Parametrize the five factories. A fake LLM returns a JSON turn; assert
`len(debate["turn_records"]) == 1`, the record has all six keys, and the rendered history contains
the six section labels. A prose fake still produces one record.

- [ ] **Step 2: Run and verify failure**

Run: `pytest -q test/offline/test_debate_turns.py -k "five or prose"`
Expected: FAIL.

- [ ] **Step 3: Implement**

Replace `llm.invoke` with `invoke_debate_turn`; render the turn into `argument` with the speaker
prefix; keep `turn_digest(raw)`; append `turn.model_dump()` to `turn_records`; add the JSON
instruction to each task text (without editing a prompt file).

- [ ] **Step 4: Run and verify pass**

Run: `pytest -q test/offline/test_debate_turns.py`
Expected: PASS. Also run the inherited `test_debate_opening.py` and `test_termination.py`.

### Task 4: Docs and gates

**Files:**
- Create: `docs/architecture/adr/011-structured-debate-turns.md`
- Modify: `docs/architecture/invariants.md`, `trace-matrix.md`, `structural-constraints.md`

- [ ] **Step 1: Record the decision and the adapter's limits.**
- [ ] **Step 2: Run `pytest -q`, `ruff check src`, `python -m eval.run ...`; all green.**
