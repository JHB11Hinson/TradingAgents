#!/usr/bin/env python3
"""gate-2 mypy quarantine guard (ADR-016).

``docs/code-governance/mypy-legacy.txt`` is a one-way ratchet: inherited modules may
leave the quarantine list as they become type-clean, but no pull request may *add* a
path to it (that would hide a type error behind the exemption that gate-2 grants).

The checker compares the quarantine list between the base branch and the head commit,
ignoring blank lines and ``#`` comments.  It fails when a path exists at the head but
not at the base; removing a path or leaving the file untouched passes.

The checker is CI glue, not runtime code, so it lives under ``.github/scripts/``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Protocol

QUARANTINE = "docs/code-governance/mypy-legacy.txt"


class Git(Protocol):
    def show(self, commit: str, path: str) -> str | None: ...


class SubprocessGit:
    """The real git implementation used by the workflow."""

    def show(self, commit: str, path: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", "show", f"{commit}:{path}"],
                check=True,
                text=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            return None
        return result.stdout


def quarantined_paths(text: str | None) -> set[str]:
    if not text:
        return set()
    paths = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        paths.add(line)
    return paths


def check(git: Git, base: str, head: str) -> tuple[bool, str]:
    base_paths = quarantined_paths(git.show(base, QUARANTINE))
    if not base_paths:
        return True, "no base quarantine list; nothing to compare"

    head_paths = quarantined_paths(git.show(head, QUARANTINE))
    added = sorted(head_paths - base_paths)
    if added:
        listing = ", ".join(added)
        return False, (
            f"mypy-legacy.txt gained {len(added)} path(s): {listing}. "
            "The quarantine list may only shrink (ADR-016, DEBT-009): fix the type error "
            "instead of de-listing the file."
        )
    return True, "quarantine list did not grow"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)

    ok, reason = check(SubprocessGit(), args.base, args.head)
    if ok:
        print(f"gate-2: pass ({reason})")
        return 0

    print(f"::error file={QUARANTINE}::gate-2: {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
