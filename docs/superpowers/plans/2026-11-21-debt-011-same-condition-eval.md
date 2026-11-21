# DEBT-011 same-condition evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** make `python -m eval.run` prove that the token cap binds, by measuring every fixed-set case twice (capped and uncapped) and adding a `capped_tokens_ratio` threshold.

**Architecture:** the existing replay analyzer gains an uncapped sibling (same fixtures, same graph, no run/call cap). `CaseObservation` carries both totals; `aggregate()` reports both ratios; `eval/run.py` combines the two passes and writes one report. The `COST-001` contract against the 120,000 recorded baseline is unchanged.

**Tech Stack:** Python 3.12, pytest, PyYAML, LangGraph, the existing `eval/` and `tradingagents.evaluation` packages.

**Spec:** `docs/superpowers/specs/2026-11-21-debt-batch-b-design.md`

## Global Constraints

- Branch: `feat/CHG-039-debt-011-same-condition-eval`; tests-only commit before any `src/` commit.
- `pytest -q` stays green; changed `src/**/*.py` passes `ruff`; scoped `mypy` on changed files.
- `eval/thresholds.yaml`: `capped_tokens_ratio: {max: 0.98}`.
- Shipped measurements: capped 89,858 tokens; uncapped 96,820; ratio 0.9281.
- Separate result directories: `<results-dir>/capped` and `<results-dir>/uncapped`.
- No live provider call, no new dependency.
- Commit trailers: `Refs:`, `Agent-Session:`, `AI-Use-Log:`, `Test-Approval:` where the workflow asks.

## Review Focus

- **Uncapped pass isolation:** if both passes share a memory log or cache, the uncapped run sees the capped run's `past_context` and the comparison is false. Test: distinct `memory_log_path` and `data_cache_dir` per pass.
- **Uncapped pass failure:** an exception there must become `cases_failed`, never a silent `capped_tokens_ratio = 1.0` pass. Test: a raising uncapped analyzer fails the report.
- **Missing measurement:** a successful case without an uncapped total must report ratio 1.0 and fail the 0.98 threshold. Test in `aggregate()`.
- **Threshold semantics:** `total_tokens_ratio` stays against 120,000; `capped_tokens_ratio` is the mechanism check. Test both values in the shipped report.
- **Artifact paths:** the report stays at `<results-dir>/report.json`; per-pass artifacts live in subdirectories. Test the CLI path and report location.

---

### Task A1: Publish the test contract

**Files:**
- Create: `test/offline/test_eval_same_condition.py`
- Modify: `test/offline/test_eval_report.py`
- Modify: `test/offline/test_eval_cli.py`

**Interfaces:**
- Consumes: `CaseObservation(total_tokens, budget, rating, ...)`, `aggregate(observations, baseline, case_count)`, `evaluate_cases(...)`.
- Produces: the names `CaseObservation.uncapped_total_tokens`, metric keys `uncapped_tokens` and `capped_tokens_ratio`, and the report fields `uncapped_tokens` / `capped_tokens_ratio`.

- [ ] **Step 1: Write the failing aggregate tests**

Add to `test/offline/test_eval_report.py`:

```python
def test_aggregate_reports_the_same_condition_ratio():
    observations = [
        CaseObservation(total_tokens=900, budget=1000, rating="Hold", uncapped_total_tokens=1000),
        CaseObservation(total_tokens=1000, budget=1000, rating="Hold", uncapped_total_tokens=1000),
    ]
    metrics = aggregate(observations, _baseline(), 2)
    assert metrics["uncapped_tokens"] == 2000
    assert metrics["capped_tokens_ratio"] == 0.95


def test_a_missing_uncapped_measurement_reports_one():
    observations = [CaseObservation(total_tokens=100, budget=1000, rating="Hold")]
    metrics = aggregate(observations, _baseline(), 1)
    assert metrics["capped_tokens_ratio"] == 1.0
```

- [ ] **Step 2: Write the failing threshold test**

Add to `test/offline/test_eval_same_condition.py`:

```python
def _report(uncapped: int) -> EvaluationReport:
    def analyze(case):
        return CaseObservation(
            total_tokens=100, budget=1000, rating="Hold", uncapped_total_tokens=uncapped
        )
    thresholds = (Threshold("capped_tokens_ratio", maximum=0.98),)
    return evaluate_cases([_case("NVDA")], analyze, _baseline(), thresholds)


def test_a_binding_cap_passes():
    assert _report(uncapped=110).ok is True


def test_no_compaction_fails():
    report = _report(uncapped=100)
    assert report.ok is False
    assert report.failed_thresholds()[0].metric == "capped_tokens_ratio"
```

Use the `_baseline()` and `_case()` helpers already in `test_eval_report.py`, or copy the minimal fixture into the new file.

- [ ] **Step 3: Write the failing CLI assertion**

In `test/offline/test_eval_cli.py::test_the_runner_exits_zero_when_every_threshold_passes`, add:

```python
assert report["metrics"]["uncapped_tokens"] > report["metrics"]["total_tokens"]
assert report["metrics"]["capped_tokens_ratio"] <= 0.98
```

- [ ] **Step 4: Run the tests and confirm they fail for the missing fields**

Run: `.venv/bin/pytest -q test/offline/test_eval_report.py test/offline/test_eval_same_condition.py test/offline/test_eval_cli.py`
Expected: FAIL with `TypeError: CaseObservation.__init__() got an unexpected keyword argument 'uncapped_total_tokens'` or `KeyError: 'capped_tokens_ratio'`.

- [ ] **Step 5: Commit the tests only**

```bash
git switch -c feat/CHG-039-debt-011-same-condition-eval
git add test/offline/test_eval_report.py test/offline/test_eval_same_condition.py test/offline/test_eval_cli.py
git commit -m "test: CHG-039 DEBT-011 same-condition evaluation" \
           -m "Refs: D1-REQ-EVAL-001, D1-REQ-COST-001
Agent-Session: transcripts/60198818-HaobinJiang-CHG-039-debt-011.md#L1-L40
AI-Use-Log: docs/ai-use-log/JHB11Hinson.yaml
Test-Approval: docs/review-memo/PR-<n>.md"
git push -u origin HEAD
gh pr create --title "feat: CHG-039 DEBT-011 same-condition evaluation" --body-file /tmp/chg-039-card.md --base main
```

Write `/tmp/chg-039-card.md` with the scope, the two measured numbers and the out-of-scope list (live mode, other debts).

- [ ] **Step 6: Test approval before implementation**

Create `docs/review-memo/PR-<n>.md` (test-approval section) and `docs/review-memo/PR-<n>-review.md` (the bot text) with `Verdict: APPROVE`, `Tests:` naming the three test files, and the measured numbers. Commit, push, add the `bot-review` label, and wait for `gh pr view <n> --json reviews` to show an APPROVE from `github-actions[bot]`.

---

### Task A2: Extend the observation and aggregation

**Files:**
- Modify: `src/tradingagents/evaluation/metrics.py`

**Interfaces:**
- Produces: `CaseObservation.uncapped_total_tokens: int | None = None`; `KNOWN_METRICS` contains `uncapped_tokens` and `capped_tokens_ratio`; `aggregate()` returns both.

- [ ] **Step 1: Add the field and metrics**

Add `uncapped_total_tokens: int | None = None` to `CaseObservation`. In `aggregate()`:

```python
uncapped_tokens = sum(
    observation.uncapped_total_tokens
    if observation.uncapped_total_tokens is not None
    else observation.total_tokens
    for observation in observations
)
```

Return `"uncapped_tokens": uncapped_tokens` and
`"capped_tokens_ratio": _ratio(total_tokens, uncapped_tokens)` (with `1.0` when `uncapped_tokens == 0`). Add both names to `KNOWN_METRICS` and `metric_names()`.

- [ ] **Step 2: Run the aggregate tests**

Run: `.venv/bin/pytest -q test/offline/test_eval_report.py`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add src/tradingagents/evaluation/metrics.py
git commit -m "feat: CHG-039 report the same-condition token ratio" \
           -m "Refs: D1-REQ-EVAL-001, D1-REQ-COST-001
Agent-Session: transcripts/60198818-HaobinJiang-CHG-039-debt-011.md#L1-L60
AI-Use-Log: docs/ai-use-log/JHB11Hinson.yaml"
```

---

### Task A3: Carry the uncapped total through the report

**Files:**
- Modify: `src/tradingagents/evaluation/report.py`

**Interfaces:**
- Consumes: `CaseObservation.uncapped_total_tokens`.
- Produces: `CaseResult.uncapped_tokens`; `EvaluationReport.summary()` prints both ratios; `to_dict()` includes the per-case total.

- [ ] **Step 1: Add the per-case field**

Add `uncapped_tokens: int = 0` to `CaseResult`, set it in `evaluate_cases()` from `observation.uncapped_total_tokens or 0`, include it in `to_dict()`, and add an `uncapped` line to `summary()`.

- [ ] **Step 2: Run the report tests**

Run: `.venv/bin/pytest -q test/offline/test_eval_report.py`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add src/tradingagents/evaluation/report.py
git commit -m "feat: CHG-039 carry uncapped tokens in the report" \
           -m "Refs: D1-REQ-EVAL-001, D1-REQ-COST-001
Agent-Session: transcripts/60198818-HaobinJiang-CHG-039-debt-011.md#L1-L70
AI-Use-Log: docs/ai-use-log/JHB11Hinson.yaml"
```

---

### Task A4: Run both passes in `eval/run.py`

**Files:**
- Modify: `eval/run.py`

**Interfaces:**
- Consumes: `build_replay_analyzer(results_dir, overrides)`.
- Produces: a combined analyzer whose `CaseObservation` carries both totals.

- [ ] **Step 1: Build two isolated analyzers**

In `main()`:

```python
capped = build_replay_analyzer(Path(args.results_dir) / "capped", overrides)
uncapped_overrides = {
    "context_budget_tokens": 10**9,
    "context_call_budget_tokens": 10**9,
    "context_decision_reserve_tokens": 0,
}
uncapped = build_replay_analyzer(Path(args.results_dir) / "uncapped", uncapped_overrides)

def analyze(case):
    observation = capped(case)
    same_condition = uncapped(case)
    return replace(observation, uncapped_total_tokens=same_condition.total_tokens)
```

Use `dataclasses.replace`. Keep the report path `<results-dir>/report.json`.

- [ ] **Step 2: Run the CLI test**

Run: `.venv/bin/pytest -q test/offline/test_eval_cli.py`
Expected: PASS; the report carries `uncapped_tokens` and `capped_tokens_ratio`.

- [ ] **Step 3: Run the real command**

Run: `.venv/bin/python -m eval.run --results-dir /tmp/opencode/eval-a`
Expected: exit 0; `capped_tokens_ratio: 0.928... (pass; required <= 0.98)`; `total_tokens_ratio: 0.374408`.

- [ ] **Step 4: Commit**

```bash
git add eval/run.py
git commit -m "feat: CHG-039 replay capped and uncapped in one run" \
           -m "Refs: D1-REQ-EVAL-001, D1-REQ-COST-001
Agent-Session: transcripts/60198818-HaobinJiang-CHG-039-debt-011.md#L1-L80
AI-Use-Log: docs/ai-use-log/JHB11Hinson.yaml"
```

---

### Task A5: Add the threshold and close the debt record

**Files:**
- Modify: `eval/thresholds.yaml`
- Modify: `docs/debt-register.md`
- Modify: `docs/architecture/evaluation-logbook.md`
- Modify: `docs/architecture/evaluation-table.md`
- Modify: `docs/architecture/adr/007-evaluation-harness.md`
- Modify: `docs/architecture/trace-matrix.md`
- Modify: `docs/ai-use-log/JHB11Hinson.yaml`
- Create: `transcripts/60198818-HaobinJiang-CHG-039-debt-011.md`

- [ ] **Step 1: Add the threshold**

```yaml
  # DEBT-011: the cap must bind; 1.0 means no compaction at all.
  capped_tokens_ratio: {max: 0.98}
```

- [ ] **Step 2: Rewrite DEBT-011 honestly**

In `docs/debt-register.md`, change the entry's **What** to the comparability defect (a 120,000
production estimate vs a synthetic replay; 0.403 already passes without the cap), record the
same-condition metric and the two numbers, set **Status:** `mitigated`, and keep the live release
check as a **Trigger to revisit**. Do not claim the harness is production-representative.

- [ ] **Step 3: Record E-006 and the caveat**

Add E-006 to `evaluation-logbook.md`: capped 89,858, uncapped 96,820, ratio 0.9281; `total_tokens_ratio`
0.403417 uncapped against 120,000, so `COST-001`'s 0.374 is mechanism evidence, not a production
claim. Add the same sentence to `evaluation-table.md` section B/F and an amendment note under
ADR-007 **Consequences**. Update the trace-matrix rows for `COST-001` and `EVAL-001` to name
`capped_tokens_ratio`.

- [ ] **Step 4: AI-use log and transcript**

Append one entry to `docs/ai-use-log/JHB11Hinson.yaml` and create the annotated transcript. The
transcript quotes the human approval and the decision not to build a live mode; it points at the
same line range in the AI-use entry.

- [ ] **Step 5: Run the full verification**

```bash
.venv/bin/pytest -q
.venv/bin/ruff check src/tradingagents/evaluation/metrics.py src/tradingagents/evaluation/report.py eval/run.py
.venv/bin/mypy src/tradingagents/evaluation/metrics.py src/tradingagents/evaluation/report.py
.venv/bin/python -m eval.run --results-dir /tmp/opencode/eval-a
```

Expected: all tests pass; ruff/mypy clean; exit 0 with both ratios.

- [ ] **Step 6: Commit docs and open the final review**

Commit with `Refs: D1-REQ-GOV-010, D1-REQ-GOV-011`, `Agent-Session:` and `AI-Use-Log:` trailers.
Update `docs/review-memo/PR-<n>.md` with the implementation verdict, update `PR-<n>-review.md`, push,
re-add `bot-review`, and wait for the final approval. Do not merge.
