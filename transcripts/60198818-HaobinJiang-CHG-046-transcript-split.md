# Agent session record - CHG-046 split the combined transcript into session parts

- Date: 2026-11-21
- Harness: OpenCode (DeepSeek V4.1 Flash)
- Owner: 60198818 Haobin Jiang (`@JHB11Hinson`)
- Branch: `docs/CHG-046-transcript-split`
- Scope: D5 / `D1-REQ-GOV-011` evidence layout; no `src/`, prompt, model or gate change

> Annotated session record. The human turn is verbatim; tool actions are summarised with the
> command and the result that mattered. This is not a verbatim export.

## Human request (verbatim)

```text
把JHB的transcripts切割一下，分成多份，然后按规范提交PR，Bot Review
```

## Agent findings

- `transcripts/60198818-HaobinJiang.md` was 30,569 lines and 1,214,646 bytes across 11
  `## Session` sections. A GitHub blob above 1 MB is not viewable in the browser, so the D5
  evidence could be downloaded but not read in review.
- The legacy archive `docs/ai-use-log.yaml` and older review memos cite the file by line range
  (`#L30-L2433`, `#L15391-L25677`, `#L30547-L30569`, `#L1-L30543`). Deleting the file without a
  map would make those historical citations unreadable.
- `docs/code-governance/verification-constraints.md` still said `GOV-011` was "partial - 2 files
  today", and `DEBT-006` still described `transcripts/` as one file.
- No test checked the transcript set; nothing prevented the combined file from growing past the
  render limit again.

## Decisions

- Split at the 11 session boundaries, one part per session, with names
  `60198818-HaobinJiang-S<nn>-<slug>.md` in `transcripts/` so the course convention and any
  `transcripts/*.md` count still see them.
- Keep the original path as an index: part links, the D5 coverage map, the old-to-new line map
  and the split verification. The pre-split blob stays in Git history at `e26f47f`.
- Preserve each session body byte-for-byte. The only added text is a nine-line provenance header;
  concatenating the bodies reproduces the pre-split file (verified, SHA-256
  `642a3ef979f14cfaad6fe99e182edf8d0698df8d4d1a784a194afd415993f9cc`).
- Repoint the two active AI-use entries that cited `#L30547-L30569` to the Session 11 part. Do not
  rewrite the 15 archived entries; add a four-line header note to the archive pointing at the map.
- Add `test/offline/test_transcripts_split.py` with three positive checks and three negative checks,
  and update the `GOV-011` row, the trace matrix and `DEBT-006`.

## Verification

- `python -m pytest -q test/offline/test_transcripts_split.py` -> 6 passed in 1.05 s.
- `python -m pytest -q` -> 1543 passed, 1 skipped, 1 deselected, 99 subtests passed in 17.55 s.
- `python -m ruff check test/offline/test_transcripts_split.py` -> all checks passed.
- `python -m check_jsonschema --schemafile docs/req/req-schema.json docs/req/requirements.yaml`
  -> validation done.
- `python -m eval.run --set eval/fixed-set.json --thresholds eval/thresholds.yaml --budget 40000`
  -> pass (2 cases, 0 failed; ratios 0.270625, capped 0.927049, review 0.0, structured 1.0).
- Byte-identity check: 11 part bodies concatenated equal the `e26f47f` blob (997,914 bytes of
  session body; the pre-split preamble is replaced by the index).

## Pull request

Opened as `docs/CHG-046-transcript-split` after this record was written. The review record and the
bot-review text are added by the following commit; the pull request is labelled `bot-review` only
after the gates are green on the final head. The agent does not merge.
