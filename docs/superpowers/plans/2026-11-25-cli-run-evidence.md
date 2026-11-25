# CLI Run Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the project's context budget, telemetry, structured debate, termination, guardrail
and memory evidence visible in the existing Rich CLI, without changing the live layout.

**Architecture:** Add a small `cli/evidence.py` renderer that reads the finished state, the
telemetry trace and the manifest. A post-run panel calls it in `cli/run.py`; a new
`tradingagents inspect` command calls it from the saved state log. Guardrail call sites emit
advisory telemetry spans through the existing `span` seam; the state log gains additive fields so
`inspect` can replay the same evidence.

**Tech Stack:** Python 3.11+, Typer, Rich, pytest, existing `tradingagents.telemetry`.

**Spec:** `docs/superpowers/specs/2026-11-25-cli-run-evidence-design.md`

## Global Constraints

- No new dependency; no network, API key or secret in tests.
- Preserve the inherited live `Layout`; only append a post-run panel.
- `ruff` config stays as in `pyproject.toml`; line length 100.
- Tests are deterministic and live under `test/offline/`.
- No commit mixes `test/` and `src/`.
- Branch: `feat/CHG-057-cli-run-evidence`; at most 5 commits.
- Human reviewer supplies the test-approval record (`Verdict: APPROVE`, `Tests:` line) before the
  first `src/` commit. The agent never approves or merges.

## Review Focus

- A run with telemetry disabled or a missing trace/manifest still renders, saying `not written`.
- An old state log without the new fields still renders, saying `not recorded`.
- Long debate/guardrail text is truncated, never printed whole.
- Guardrail reasons contain pattern names and percentages, never the hostile input text.
- `inspect` rejects a missing ticker/date and path-traversal input with one red line, not a traceback.
- A failure in evidence rendering never fails the analysis run.

---

### Task 1: Write the failing tests (test-only commit)

**Files:**
- Create: `test/offline/test_cli_evidence.py`
- Modify: `test/offline/test_guardrails.py`
- Modify: `test/offline/test_cli_display.py`
- Modify: `test/offline/test_cli_commands.py`

**Interfaces:**
- Tests import `cli.evidence` functions that do not exist yet:
  `collect_evidence`, `collect_from_log`, `find_state_log`, `render_evidence`, `Evidence`.
- Tests import `tradingagents.telemetry.guardrail_event`.
- Expected new state-log keys: `final_decision_source`, `memory_note`, `memory_sources`,
  `investment_debate_state.turn_records`, `risk_debate_state.turn_records`.

- [ ] **Step 1: Add `test/offline/test_cli_evidence.py`**

Cover these exact behaviours:

```python
def test_render_evidence_shows_decision_context_debate_memory_and_paths():
    # Build Evidence with rating "Overweight", source "structured",
    # context {"budget": 50000, "total_tokens": 43500, "compacted_calls": 2,
    #          "max_call_tokens": 12100},
    # memory_note "1 past decision could not be settled",
    # memory_sources ("2026-10-01/NVDA",),
    # research_turns (one dict with claim/evidence/converge),
    # risk_turns (one dict), guardrails (one event), phases {...}.
    # Render to a StringIO Console(width=120); assert the output contains
    # "Run Evidence", "Overweight", "structured", "43.5k", "50.0k",
    # "compacted 2", "Research", "Risk", "src:2026-10-01/NVDA",
    # "trace_2026-11-20.json" and "manifest_2026-11-20.json".

def test_long_debate_excerpts_are_truncated():
    # claim = "x" * 500; render; assert "x" * 500 not in output and "…" in output.

def test_missing_trace_and_manifest_renders_not_written(tmp_path):
    # collect_evidence(...) with no files; render; assert "not written" twice
    # and no exception.

def test_telemetry_disabled_says_so():
    # config {"telemetry_enabled": False}; render; assert "telemetry disabled".

def test_collect_evidence_reads_guardrail_spans_from_trace(tmp_path):
    # Write a trace JSON with a span kind="guardrail",
    # name="guardrail.position_clipped",
    # attributes={"node": "Portfolio Manager",
    #             "reason": "position size 50% exceeds the 10% ceiling; clipped to 10%"}.
    # Assert the rendered panel contains "Position clipped" and "50%".

def test_find_state_log_uses_the_latest_file_and_rejects_a_bad_date(tmp_path):
    # Create two full_states_log_*.json files with different mtimes.
    # find_state_log("NVDA", None, tmp_path) returns the newer one.
    # find_state_log("NVDA", "../etc/passwd", tmp_path) raises ValueError.
    # find_state_log("NVDA", "2026-01-09", tmp_path) with no file raises FileNotFoundError.
```

- [ ] **Step 2: Add telemetry-event tests to `test/offline/test_guardrails.py`**

```python
def test_guardrail_event_is_a_noop_without_telemetry():
    guardrail_event("guardrail.test", "why")  # no exception, no hub

def test_retrieved_block_emits_an_instruction_block_event():
    with telemetry_scope({"telemetry_enabled": True}) as hub:
        retrieved_block("news", HOSTILE[0])
    event = hub.events[-1]
    assert (event.kind, event.name) == ("guardrail", "guardrail.instruction_blocked")
    assert "ignore_instructions" in event.attributes["reason"]

def test_position_clip_emits_a_guardrail_event():
    # create_portfolio_manager(structured 50%, max_position_pct=10) on _pm_state()
    # inside telemetry_scope; assert an event named guardrail.position_clipped
    # whose reason contains "50%" and "10%".

def test_review_fallback_emits_a_guardrail_event():
    # create_portfolio_manager(free_text="We like it.") inside telemetry_scope;
    # assert guardrail.decision_review.
```

- [ ] **Step 3: Add state-log evidence test to `test/offline/test_cli_display.py`**

```python
def test_the_state_log_records_decision_source_memory_and_turn_records(tmp_path):
    # Use _bare_graph(tmp_path) and the existing _state("NVDA") fixture, then
    # extend it with:
    # final_decision_source="structured", memory_note="1 future item withheld",
    # past_context="lesson\n| src:2026-10-01/NVDA |",
    # investment_debate_state["turn_records"]=[{"claim": "c"}],
    # risk_debate_state["turn_records"]=[{"claim": "r"}].
    # Assert the logged JSON has those keys and memory_sources == ["2026-10-01/NVDA"].
```

- [ ] **Step 4: Add `inspect` command tests to `test/offline/test_cli_commands.py`**

```python
def test_help_lists_the_inspect_command(runner):
    assert "inspect" in runner.invoke(m.app, ["--help"]).output

def test_inspect_renders_a_saved_run(runner, tmp_path):
    # Write results/NVDA/TradingAgentsStrategy_logs/full_states_log_2026-11-20.json
    # with final_rating="Hold", final_decision_source="structured",
    # termination_reason="", context_usage={...}, memory_note="".
    # Invoke ["inspect", "NVDA", "2026-11-20", "--results-dir", str(tmp_path)].
    # Assert exit 0 and "Run Evidence" and "Hold" in output.

def test_inspect_reports_a_missing_run_in_one_line(runner, tmp_path):
    # Assert exit 1, "full_states_log" in output, "Traceback" not in output.
```

- [ ] **Step 5: Run the new tests and confirm they fail for the expected reason**

Run:
```bash
.venv/bin/python -m pytest -q test/offline/test_cli_evidence.py test/offline/test_cli_commands.py test/offline/test_guardrails.py test/offline/test_cli_display.py
```
Expected: import errors for `cli.evidence` / `guardrail_event`, and assertion failures for the new
state-log keys. Record the failures in the commit message or PR notes.

- [ ] **Step 6: Commit the tests only**

```bash
git add test/offline/test_cli_evidence.py test/offline/test_cli_commands.py \
        test/offline/test_guardrails.py test/offline/test_cli_display.py
git commit -m "test: CHG-057 add RED tests for CLI run evidence"
```

Include the human reviewer's `Test-Approval:` record in this commit (or a docs commit before the
first `src/` commit). If the PR number is not known yet, use the legacy
`docs/review-memo.md#CHG-057` form accepted by gate-1.

---

### Task 2: Emit guardrail events and record run evidence (src backend commit)

**Files:**
- Modify: `src/tradingagents/telemetry/spans.py`
- Modify: `src/tradingagents/telemetry/__init__.py`
- Modify: `src/tradingagents/context/agent_layers.py`
- Modify: `src/tradingagents/agents/analysts/turn.py`
- Modify: `src/tradingagents/agents/analysts/sentiment_analyst.py`
- Modify: `src/tradingagents/agents/managers/portfolio_manager.py`
- Modify: `src/tradingagents/graph/trading_graph.py`

**Interfaces:**
- Produces: `guardrail_event(name: str, reason: str, *, node: str | None = None) -> None`.
- Produces: state-log keys listed in Task 1.
- Consumes: existing `span`, `current_span`, `scrub_untrusted`, `enforce_position_ceiling`,
  `clip_free_text_decision`.

- [ ] **Step 1: Add `guardrail_event` in `telemetry/spans.py`**

```python
def guardrail_event(name: str, reason: str, *, node: str | None = None) -> None:
    """Emit an advisory guardrail span; no-op outside a telemetry scope."""
    parent = current_span()
    phase = parent.phase if parent is not None else "guardrail"
    with span(name, phase=phase, kind="guardrail",
              attributes={"node": node or "run", "reason": reason}):
        pass
```

Export it from `telemetry/__init__.py`.

- [ ] **Step 2: Instrument the instruction-scrub call sites**

In `context/agent_layers.py` `retrieved_block`, keep the scrubbed text and emit once when
`scrubbed.blocked`:

```python
scrubbed = scrub_untrusted(text)
if scrubbed.blocked:
    guardrail_event("guardrail.instruction_blocked", ",".join(scrubbed.matches), node=source)
```

In `agents/analysts/turn.py` `sanitize_messages`, deduplicate by tool-call id and emit
`guardrail.instruction_blocked` with `node=message.name or "tool"`.
In `agents/analysts/sentiment_analyst.py`, use the same helper for `news`, `stocktwits` and `reddit`.

- [ ] **Step 3: Instrument the Portfolio Manager**

In `agents/managers/portfolio_manager.py`:

```python
# budget exception
guardrail_event("guardrail.budget_review", "context budget exhausted", node="Portfolio Manager")

# structured/free-text clip
guardrail_event("guardrail.position_clipped", ceiling_warning, node="Portfolio Manager")

# invalid free-text fallback
guardrail_event("guardrail.decision_review", "no single explicit rating", node="Portfolio Manager")
```

Do not put the raw hostile text in `reason`; keep the warning/pattern text only.

- [ ] **Step 4: Add state-log fields in `trading_graph.py`**

Add `import re` to `trading_graph.py` and a module helper:

```python
_SRC_RE = re.compile(r"src:([^\s|]+)")

def _memory_sources(past_context: str) -> list[str]:
    return sorted(set(_SRC_RE.findall(past_context or "")))
```

In `_log_state`, add:

```python
"final_decision_source": final_state.get("final_decision_source", ""),
"memory_note": final_state.get("memory_note", ""),
"memory_sources": _memory_sources(final_state.get("past_context", "")),
```

and add `"turn_records": final_state[...].get("turn_records", [])` to both debate-state dictionaries.

- [ ] **Step 5: Run the backend tests**

```bash
.venv/bin/python -m pytest -q test/offline/test_guardrails.py test/offline/test_cli_display.py \
  test/offline/test_debate_turns.py test/offline/test_telemetry_trace.py
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/tradingagents/telemetry/spans.py src/tradingagents/telemetry/__init__.py \
        src/tradingagents/context/agent_layers.py src/tradingagents/agents/analysts/turn.py \
        src/tradingagents/agents/analysts/sentiment_analyst.py \
        src/tradingagents/agents/managers/portfolio_manager.py \
        src/tradingagents/graph/trading_graph.py
git commit -m "feat: CHG-057 emit guardrail events and record run evidence"
```

---

### Task 3: Add the evidence collector and post-run panel (src CLI commit)

**Files:**
- Create: `src/cli/evidence.py`
- Modify: `src/cli/run.py`

**Interfaces:**
- Produces:
  `collect_evidence(final_state, config, ticker, trade_date) -> Evidence`
  `collect_from_log(log_path, config, ticker, trade_date) -> Evidence`
  `find_state_log(ticker, date, results_dir) -> StateLogRef`
  `render_evidence(evidence) -> Panel`
- `Evidence` fields: `ticker`, `trade_date`, `rating`, `decision_source`,
  `termination_reason`, `context`, `research_turns`, `risk_turns`, `guardrails`,
  `memory_note`, `memory_sources`, `phases`, `manifest_totals`, `trace_path`,
  `manifest_path`, `telemetry_status`.
- `StateLogRef` fields: `path: Path`, `ticker: str`, `trade_date: str`.

- [ ] **Step 1: Implement `src/cli/evidence.py`**

Use existing helpers: `run_output_dir`, `load_trace`; `json` for the manifest; `Panel`, `Table`,
`box.SIMPLE_HEAD`, `Text`, `Group` from Rich. Read files defensively: a missing or malformed file
becomes `None`/`not written`, never an exception.

`collect_from_log` reads the state log and constructs a `final_state`-shaped mapping before calling
`collect_evidence`:

```python
{
    "company_of_interest": data.get("company_of_interest", ticker),
    "trade_date": data.get("trade_date", trade_date),
    "final_rating": data.get("final_rating", ""),
    "final_trade_decision": data.get("final_trade_decision", ""),
    "final_decision_source": data.get("final_decision_source", ""),
    "termination_reason": data.get("termination_reason", ""),
    "context_usage": data.get("context_usage", {}),
    "memory_note": data.get("memory_note", ""),
    "memory_sources": data.get("memory_sources", []),
    "past_context": "",
    "investment_debate_state": {
        "turn_records": data.get("investment_debate_state", {}).get("turn_records", [])
    },
    "risk_debate_state": {
        "turn_records": data.get("risk_debate_state", {}).get("turn_records", [])
    },
}
```

If `final_rating` is empty, derive it with `run_rating(final_state)`; if `memory_sources` is empty,
parse `src:` ids from `past_context`.

The renderer must include:

1. a summary grid with Decision, Context, Memory, Telemetry;
2. a Structured Debate table with one row per debate (`Turns`, `Claim`, `Converge`);
3. a Guardrails table with `Name`, `Node`, `Detail`;
4. a Phases table sorted by tokens, top 6 plus `other`, excluding guardrail spans;
5. trace and manifest paths in `dim`.

Use `_short(text, limit)` to collapse whitespace and append `…`; use 80 for debate excerpts and 120
for guardrail details.

- [ ] **Step 2: Wire the panel into `src/cli/run.py`**

After `console.print("\n[bold cyan]Analysis Complete![/bold cyan]\n")`:

```python
try:
    evidence = collect_evidence(
        final_state, config, selections["ticker"], selections["analysis_date"]
    )
    console.print(render_evidence(evidence))
except Exception as exc:  # evidence must never fail the run
    console.print(f"[yellow]Run evidence unavailable: {exc}[/yellow]")
```

Keep the existing REVIEW warning and report-save flow unchanged.

- [ ] **Step 3: Run the CLI evidence tests**

```bash
.venv/bin/python -m pytest -q test/offline/test_cli_evidence.py test/offline/test_cli_memory_log.py \
  test/offline/test_cli_headless.py
```
Expected: PASS.

- [ ] **Step 4: Manually inspect a rendered panel**

Use the test's `StringIO` console or run the offline test that renders a synthetic run. Confirm the
panel fits a 100-column terminal, long text ends in `…`, and no full hostile string appears.

- [ ] **Step 5: Commit**

```bash
git add src/cli/evidence.py src/cli/run.py
git commit -m "feat: CHG-057 add the post-run evidence panel"
```

---

### Task 4: Add the `inspect` command (src CLI commit)

**Files:**
- Modify: `src/cli/main.py`
- Modify: `src/cli/evidence.py` (only if `StateLogRef`/finder belongs there)

**Interfaces:**
- Produces: `tradingagents inspect TICKER [DATE] [--results-dir PATH]`.
- `find_state_log` validates the date as `YYYY-MM-DD` and the ticker through
  `safe_ticker_component`; no path traversal.

- [ ] **Step 1: Implement the command**

```python
@app.command("inspect")
def inspect_run(
    ticker: str = typer.Argument(..., help="Ticker symbol, e.g. NVDA"),
    date: str = typer.Argument(None, help="Trade date YYYY-MM-DD; omit for the latest run"),
    results_dir: str = typer.Option(None, "--results-dir", help="Results directory"),
):
    """Show the recorded evidence for a finished run."""
    try:
        ref = find_state_log(ticker, date, results_dir or DEFAULT_CONFIG["results_dir"])
        evidence = collect_from_log(
            ref.path, {"results_dir": results_dir or DEFAULT_CONFIG["results_dir"]},
            ref.ticker, ref.trade_date,
        )
    except (OSError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from None
    console.print(render_evidence(evidence))
```

`find_state_log` picks the newest `full_states_log_*.json` when `date` is omitted and raises
`FileNotFoundError` with the expected path when none exists.

- [ ] **Step 2: Run the command tests**

```bash
.venv/bin/python -m pytest -q test/offline/test_cli_commands.py test/offline/test_cli_evidence.py
```
Expected: PASS.

- [ ] **Step 3: Verify the help surface**

```bash
.venv/bin/python -m cli.main --help
.venv/bin/python -m cli.main inspect --help
```
Expected: `inspect` appears in the command list; its help names `TICKER`, `[DATE]` and
`--results-dir`.

- [ ] **Step 4: Commit**

```bash
git add src/cli/main.py src/cli/evidence.py
git commit -m "feat: CHG-057 add the inspect command"
```

---

### Task 5: Document and verify (docs commit)

**Files:**
- Modify: `README.md`
- Modify: `docs/ai-use-log/JHB11Hinson.yaml`
- Create (after PR number is known): `docs/review-memo/PR-<n>.md`

- [ ] **Step 1: Add a short README subsection under §4 Install**

Document:
- the automatic Run Evidence panel after a run;
- `tradingagents inspect NVDA 2026-11-20` and `--results-dir`;
- where trace/manifest live;
- that `inspect` is read-only and works without an API key.

- [ ] **Step 2: Update the AI-use log**

Add one entry in `docs/ai-use-log/JHB11Hinson.yaml` (or the author's own file) naming CHG-057, the
files touched, and the human approval/review that preceded the implementation.

- [ ] **Step 3: Run full verification**

```bash
.venv/bin/ruff check src test
.venv/bin/python -m pytest -q
```
Expected: `ruff` clean on changed files; full offline suite green with zero regressions.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/ai-use-log/JHB11Hinson.yaml
git commit -m "docs: CHG-057 document CLI run evidence"
```

- [ ] **Step 5: Open the PR and add the review memo**

Open `feat/CHG-057-cli-run-evidence` as a PR, then add `docs/review-memo/PR-<n>.md` with the
reviewer's verdict. Do not merge; hand the PR to a human reviewer.

---

## Self-review checklist

- [ ] Every new module is referenced by a task and a test.
- [ ] No task changes prompt files, secrets, `.opencode/rules.md` or the LangGraph wiring.
- [ ] Every new behaviour has a negative test: missing files, disabled telemetry, malformed date,
      missing run, long text, and a run whose evidence rendering raises.
- [ ] Test and implementation commits are separate.
- [ ] The plan stays within the 5-commit branch limit.
- [ ] The panel preserves the inherited Rich style and does not touch the live layout.
