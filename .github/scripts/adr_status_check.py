#!/usr/bin/env python3
"""ADR status and PR-reference validator (D1-REQ-GOV-009).

An `accepted` ADR is evidence that a decision was reviewed. When the record names the pull
request that carried it, that number must resolve to a review record under `docs/review-memo/`;
otherwise the traceability chain is broken and a reader cannot follow it.

The check is deliberately narrow, because the real corpus is irregular:

* only `accepted` ADRs are checked; a `proposed` record may cite a pull request that is still
  open, so its number is not verified;
* an `accepted` ADR that names no pull request at all is **exempt**, not broken: the inherited
  records predate the per-PR record convention;
* a citation must use the project's explicit forms, `PR #<n>` or `PR-<n>`; a bare number is not a
  citation.

The PR-existence predicate is a parameter, so the tests inject a set of known numbers instead of
calling the network. The command line uses the repository's own `docs/review-memo/` directory.

This is CI glue and a governance check, not runtime code, so it lives under `.github/scripts/`
like `gate1_check.py` and `gate2_check.py`.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Protocol

NAME = re.compile(r"^(\d{3})-([a-z0-9-]+)\.md$")
# `- Status: accepted` and `- **Status:** accepted (...)`; the value ends at the first comma,
# parenthesis or sentence break, so `accepted, implemented in CHG-033` reads as `accepted`.
STATUS = re.compile(r"(?mi)^[-\s]*\**Status:?\**\s*:?\s*\**([a-z]+)")
# Only the two explicit forms count. `PR #40` and `PR-58` are citations; `40` alone is not.
PR_CITATION = re.compile(r"\bPR\s*(?:#\s*|-\s*)(\d+)\b")
KNOWN_STATUSES = {"accepted", "proposed", "superseded", "rejected"}

MEMO_DIR = "docs/review-memo"


class PrExists(Protocol):
    def __call__(self, number: int) -> bool: ...


def read_adrs(adr_dir: Path) -> list[tuple[str, Path, str]]:
    """Return `(nnn, path, text)` for every ADR, in number order."""
    records = []
    for path in sorted(adr_dir.glob("*.md")):
        match = NAME.match(path.name)
        if match:
            records.append((match.group(1), path, path.read_text(encoding="utf-8")))
    return records


def status_of(text: str) -> str | None:
    match = STATUS.search(text)
    return match.group(1).lower() if match else None


def cited_prs(text: str) -> list[int]:
    """Every `PR #<n>` / `PR-<n>` citation, in document order, duplicates kept."""
    return [int(number) for number in PR_CITATION.findall(text)]


def check(adrs: list[tuple[str, Path, str]], pr_exists: PrExists) -> list[str]:
    """Problems as human-readable strings; empty means the corpus agrees with itself."""
    problems = []
    for number, _path, text in adrs:
        status = status_of(text)
        if status is None:
            problems.append(f"ADR-{number}: no status line")
            continue
        if status not in KNOWN_STATUSES:
            problems.append(f"ADR-{number}: unknown status {status!r}")
            continue
        if status != "accepted":
            continue  # a proposed record may cite a pull request that has no record yet
        for pr in cited_prs(text):
            if not pr_exists(pr):
                problems.append(f"ADR-{number}: cites PR #{pr}, which has no review record")
    return problems


def memo_exists_factory(repo: Path) -> Callable[[int], bool]:
    """Real predicate: the per-PR record, in either of the two shapes the project uses."""
    memo_dir = repo / MEMO_DIR

    def memo_exists(number: int) -> bool:
        return (memo_dir / f"PR-{number}.md").exists() or (
            memo_dir / f"PR-{number}-review.md"
        ).exists()

    return memo_exists


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root")
    args = parser.parse_args(argv)
    repo = Path(args.repo)
    problems = check(read_adrs(repo / "docs" / "architecture" / "adr"), memo_exists_factory(repo))
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("ADR status and PR references agree with docs/review-memo/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
