# Demo scripts and evidence

These are the scripts behind the CS5351 demo video. Run them from the repository root with
`.venv` active. They are evidence, not runtime code: no file under `src/`, `test/` or
`prompts/` changes with this folder.

## Scripts

| File | What it shows |
|---|---|
| `demo.sh` | The demo runner: the real live run, then the deterministic B1–B6 checks |
| `demo_live.py` | One real analysis: prints each phase, tool call, model call and token count |
| `demo_debate.py` | Free prose versus a schema-bound debate turn, including the malformed-JSON rejection |
| `demo_guardrails.py` | A 50% position claim clipped to 10%, and a bad decision turned into `REVIEW` |

## Commands

```bash
docs/demo/demo.sh live    # real model; prints the process in the terminal
docs/demo/demo.sh full    # live run, then B1-B6
docs/demo/demo.sh all     # B1-B6 only (quick, deterministic)
docs/demo/demo.sh b1      # only the no-compaction gate check; exits 1 on purpose
```

The B1–B6 checks are the same fixed-set and test commands the repository's gates use. `B1`
must exit 1: without compaction, gate-4 fails on `capped_tokens_ratio`.

## Live run

`demo_live.py` defaults to one analyst (market), one debate round, one risk round, NVDA on
2026-11-20. It uses the CityU endpoint when `CITYUCS_LLM_BASE_URL` and `CITYUCS_LLM_API_KEY`
are set (`CS5351/DeepSeek-V4-Flash`). Override with:

```text
DEMO_TICKER, DEMO_DATE, DEMO_ANALYSTS, DEMO_LANGUAGE, DEMO_ROUNDS,
DEMO_BASE_URL, DEMO_MODEL, DEMO_API_KEY, DEMO_CONTEXT_BUDGET,
DEMO_RESULTS_DIR, DEMO_MEMORY, DEMO_OHLCV
```

`DEMO_OHLCV=cache` (the default) serves the ticker's OHLCV from
`~/.tradingagents/cache/<TICKER>-YFin-data.csv`, the same cache the measured runs used, so a
Yahoo 429 does not stop the demo. `DEMO_OHLCV=live` forces Yahoo.

The terminal output has one line per event:

```text
[phase] Market Analyst report ready
    [tool] get_stock_data(...)
    [data] 17,409 chars
    [tokens] call 4: 20,430 in / 3,227 out (running 51,070 / 4,147)
Done.
  rating: Underweight
  provider tokens: 131,262 in / 23,802 out / 155,064 total
```

The live run is a demonstration; it is not the controlled comparison on the slide. Its token
count depends on the model, language and tool rounds.

## Controlled measurement

`Report.md` records the same-config live comparison: upstream v0.6.0 `1394a3f` used 206,694
provider tokens; the current tree used 160,833, 22.2% fewer. The fixed-set replay is 70,061
uncapped versus 64,950 with `--budget 40000` (−7.3%). The scripts here do not change those
numbers; they make the demo reproducible.

## Notes

- No API key or secret is stored in this folder.
- `demo.sh` sets `DEMO_REPO` only when the repository is not the parent of this folder.
- `demo_debate.py` and `demo_guardrails.py` add `src/` to `sys.path` so they also run from a
  checkout whose package is not installed.
