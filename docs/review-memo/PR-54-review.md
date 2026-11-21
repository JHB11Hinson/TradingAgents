### PR-54 — CHG-046 split the combined transcript by session

- Reviewer: `github-actions` (`.github/workflows/bot-review.yml`). **Automated non-author review**,
  requested by the owner with the `bot-review` label; the record names the reviewer as automated.
- Head reviewed: `17f6848` (the split, the index, the test and the AI-use record). The commit that
  carries this record is docs-only, so the code and evidence the gates run on are unchanged.
- Scope: `D1-REQ-GOV-011` / D5 transcript evidence and its citations. No `src/`, prompt, model,
  gate or branch-protection change.
- Specification: the combined transcript was 30,569 lines / 1,214,646 bytes across 11 sessions;
  GitHub does not render a blob above 1 MB, so the D5 evidence could not be read in review. The
  split produces one part per session and keeps the original path as an index with the part links,
  the six-stage D5 coverage map and an old-to-new line map. This is a layout change, not a rewrite:
  the agent and human words are unchanged.
- Architecture: no runtime component. Eleven `transcripts/60198818-HaobinJiang-S<nn>-<slug>.md`
  files, one index, one offline test, and three governance rows updated (`verification-constraints`,
  trace matrix, `DEBT-006`). The `transcripts/` append-only boundary is preserved in substance: the
  session bodies are byte-identical to `e26f47f:transcripts/60198818-HaobinJiang.md` (997,914 body
  bytes, independently concatenated and compared), and the pre-split blob remains in Git history.
- Code and tests: `pytest -q` -> 1543 passed, 1 skipped, 1 deselected, 99 subtests passed in 17.55 s;
  `ruff check test/offline/test_transcripts_split.py` -> all checks passed;
  `check-jsonschema` -> validation done; `python -m eval.run ... --budget 40000` -> pass (2 cases,
  0 failed; ratios 0.270625, capped 0.927049, review 0.0, structured 1.0). The new test has three
  positive checks (index links every part and keeps the six-stage map, sessions 01-11 appear once,
  every part is under 1,000,000 bytes) and three negative checks (missing link, duplicate session,
  oversized part).
- Runtime metadata: none. No configuration key, dependency, permission or gate changed.
- Safety and efficiency: the split only moves already-published transcript bytes and adds
  navigational headers, so it introduces no secret or new personal data. Every part is far below
  the render limit (largest: 397,835 bytes). The archive `docs/ai-use-log.yaml` keeps all 18
  entries; only a four-line header note points at the map. The two active citations that used
  `#L30547-L30569` now resolve to
  `transcripts/60198818-HaobinJiang-S11-merge-train-protection-audit.md#L10-L32`.
- Record truth: the index reports the real pre-split size, line count and SHA-256; the five
  legacy ranges used by the archive and older review memos are mapped explicitly. The AI-use entry
  `AI-2026-11-21-014` points at the annotated session record and describes the constraints the
  human set. `DEBT-006` moves from `open` to `mitigated`; the `GOV-011` row now names the test that
  enforces the layout.

**Findings (non-blocking).**

1. `test_all_eleven_sessions_are_present` hard-codes the current count. A future session part has
   to extend that assertion and the index; the check is deliberately strict so a lost session fails
   instead of disappearing quietly.
2. The byte-identity proof is a one-off verification against `e26f47f`, not a regression test. A
   hash manifest would make it permanent, but it would also freeze the append-only files against
   legitimate future additions; the Git history and the index SHA cover the current evidence.
3. The old line ranges still appear in the archive and in PR-34/PR-35. They are historical
   citations, not live links; the archive header and the index map make that explicit.
4. The pointer-only update to `AI-2026-11-15-002` and `AI-2026-11-15-003` technically touches
   existing entries. The IDs, summaries and decisions are untouched, and leaving the old range
   would be a dangling citation after the split.

- Tests: test/offline/test_transcripts_split.py
- Verdict: APPROVE

The split is content-preserving, the index and the parts agree, and the new offline check fails on
the three failure modes that would make the evidence misleading. The change is not on a
safety-critical path; the author still does not self-approve.
