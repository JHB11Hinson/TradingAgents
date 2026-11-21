# Loop and Evaluation Implementation Plan (CHG-044/CHG-045)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** close `D1-REQ-TERM-002` (repeated identical tool calls) and `D1-REQ-QUAL-001`
(structured-output pass rate).

**Architecture:** a pure detector in `graph/setup.py`; one new evaluation metric fed by the PM's
`final_decision_source`; the scripted replay model learns structured output.

**Tech Stack:** Python 3.11+, LangGraph, Pydantic v2, pytest.

**Spec:** `docs/superpowers/specs/2026-11-21-loop-and-eval-design.md`

## Global Constraints

- Tests before `src/`, separate commits.
- Every test names its requirement; negative test for both features.
- No inherited test is weakened; `pytest -q` and `python -m eval.run` stay green.

## Review Focus

- Two identical calls with different dict key order are still detected.
- A legitimate repeat after a different call is not detected.
- The bound remains the backstop and still wins.
- A free-text/review case lowers the pass rate; a structured case does not.
- A case that fails to run is excluded from the denominator, never counted as a pass.

---

### Task 1: Repeated identical tool call detector

**Files:**
- Modify: `src/tradingagents/graph/setup.py`
- Test: `test/offline/test_repeated_tool_calls.py`

**Interfaces:**
- Produces: `identical_call_repeat(messages, limit: int = 2) -> str | None`.

- [ ] **Step 1: Write the failing tests**

```python
def test_two_identical_calls_are_detected():
    messages = [AIMessage(content="", tool_calls=[call("get_stock_data", {"symbol": "NVDA"})]),
                AIMessage(content="", tool_calls=[call("get_stock_data", {"symbol": "NVDA"})])]
    assert identical_call_repeat(messages) == "get_stock_data"

def test_different_arguments_are_not_detected():
    ...
def test_the_wrap_up_happens_before_the_round_bound():
    # _analyst_graph with max_tool_rounds=20 and a model that repeats twice
    ...
```

- [ ] **Step 2: Run and verify failure**

Run: `pytest -q test/offline/test_repeated_tool_calls.py`
Expected: FAIL (import missing).

- [ ] **Step 3: Implement**

Canonicalise each call with `json.dumps(args, sort_keys=True)`; scan consecutive `AIMessage`s; return
the tool name when the same canonical call reaches `limit` consecutive rounds. `more_or_wrap_up`
returns `wrap_up` when the detector fires; `wrap_up` logs the repeated tool.

- [ ] **Step 4: Run and verify pass**

Run: `pytest -q test/offline/test_repeated_tool_calls.py`
Expected: PASS.

### Task 2: Structured-output pass rate

**Files:**
- Modify: `src/tradingagents/agents/state.py`
- Modify: `src/tradingagents/agents/managers/portfolio_manager.py`
- Modify: `src/tradingagents/evaluation/metrics.py`
- Modify: `src/tradingagents/evaluation/report.py`
- Modify: `eval/replay.py`
- Modify: `eval/thresholds.yaml`
- Modify: `src/tradingagents/graph/propagation.py`
- Test: `test/offline/test_eval_report.py`, `test/offline/test_eval_cli.py`

**Interfaces:**
- `CaseObservation.structured_output_ok: bool = True`
- `CaseResult.structured_output_ok: bool`
- metric `structured_output_pass_rate` (share of successful cases with `True`).

- [ ] **Step 1: Write the failing tests**

Add a metrics test with three observations (two structured, one free text) asserting
`structured_output_pass_rate == 0.666667`; add a report test that the per-case flag survives JSON.
Add a CLI/replay test that the fixed set reports `1.0`.

- [ ] **Step 2: Run and verify failure**

Run: `pytest -q test/offline/test_eval_report.py test/offline/test_eval_cli.py -k structured`
Expected: FAIL.

- [ ] **Step 3: Implement**

PM sets `final_decision_source` in every return path. Replay reads the final state and passes the
flag. `aggregate` computes the rate over successful cases only. Report carries it per case.
`ScriptedModel` returns deterministic schema instances from `with_structured_output` for
`SentimentReport`, `DebateTurn`, `ResearchPlan`, `TraderProposal`, `PortfolioDecision`.

- [ ] **Step 4: Run and verify pass**

Run: `pytest -q test/offline/test_eval_report.py test/offline/test_eval_cli.py -k structured`
Expected: PASS. Then `python -m eval.run --set eval/fixed-set.json --thresholds eval/thresholds.yaml`.

### Task 3: Docs and gates

**Files:**
- Create: `docs/architecture/adr/012-tool-repeat-and-structured-metric.md`
- Modify: `docs/architecture/trace-matrix.md`, `docs/debt-register.md` if a debt closes.

- [ ] **Step 1: Record the decision and the metric definition.**
- [ ] **Step 2: Run `pytest -q`, `ruff check src`, `python -m eval.run ...`; all green.**
