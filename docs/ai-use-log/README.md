# AI-use log (per member)

`docs/ai-use-log.yaml` is a **historical archive** through 2026-11-15. New entries go to one
file per active member:

```text
docs/ai-use-log/JHB11Hinson.yaml
docs/ai-use-log/AKAScarlett.yaml
docs/ai-use-log/SY1433.yaml
```

## Why

The old single list was append-only, so two pull requests that both added an entry conflicted at
the same end of the file. Resolving that conflict created a new commit, which dismissed an existing
approval. One file per member removes the cross-member conflict: each PR adds to its author's file,
and `git merge main` stays conflict-free.

## Rules

1. **Only edit your own file.** A PR may append to `docs/ai-use-log/<your-login>.yaml`.
2. **`members` must match the file name.** The entry format is unchanged from the archive.
3. **Do not edit the archive.** `docs/ai-use-log.yaml` keeps the entries that were already there;
   only its header note may change.
4. **One entry per materially AI-assisted change**, including governance documents.
5. **Do not renumber or rewrite old entries.** IDs are append-only.

## Gate-6

`gate-6-ai-use-log` requires an AI-use-log change when a PR touches `src/`, `test/` or `prompts/`.
It accepts either the legacy `docs/ai-use-log.yaml` or a file under `docs/ai-use-log/`.

## Entry shape

```yaml
- id: AI-YYYY-MM-DD-NNN
  date: YYYY-MM-DD
  members: ["<github-login>"]
  agent: opencode
  summary: >-
    ...
  human_interventions:
    - type: approve | constrain | correct
      what: >-
        ...
      why: >-
        ...
  transcript: transcripts/<student-id>-<name>.md#L<a>-L<b>
```
