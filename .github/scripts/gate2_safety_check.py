#!/usr/bin/env python3
"""gate-2 safety-path guard (ADR-018).

A pull request that changes a safety-critical path must also add or modify an ADR under
``docs/architecture/adr/`` in the same diff (AGENTS.md section 11). The safety-critical
paths come from ``docs/code-governance/safety-paths.txt``; a trailing slash matches every
file under that directory.

The checker is CI glue, not runtime code, so it lives under ``.github/scripts/``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Protocol

SAFETY_FILE = Path(__file__).resolve().parents[2] / "docs" / "code-governance" / "safety-paths.txt"
ADR_PREFIX = "docs/architecture/adr/"


class Git(Protocol):
    def changed_files(self, base: str, head: str) -> list[str]: ...


class SubprocessGit:
    """The real git implementation used by the workflow."""

    def changed_files(self, base: str, head: str) -> list[str]:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...{head}"],
            check=True,
            text=True,
            capture_output=True,
        )
        return [line for line in result.stdout.splitlines() if line]


def parse_safety_paths(text: str) -> list[str]:
    paths = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(line)
    return paths


def matches(path: str, safety_paths: list[str]) -> bool:
    for entry in safety_paths:
        if entry.endswith("/"):
            if path.startswith(entry):
                return True
        elif path == entry:
            return True
    return False


def check(
    git: Git,
    base: str,
    head: str,
    safety_file: Path = SAFETY_FILE,
) -> tuple[bool, str]:
    if not safety_file.is_file():
        return False, f"the safety-path list {safety_file} is missing"

    safety_paths = parse_safety_paths(safety_file.read_text(encoding="utf-8"))
    changed = git.changed_files(base, head)

    touched = [path for path in changed if matches(path, safety_paths)]
    if not touched:
        return True, "no safety-critical path changed"

    has_adr = any(path.startswith(ADR_PREFIX) for path in changed)
    if has_adr:
        return True, f"safety-critical change with an ADR: {', '.join(touched)}"

    return False, (
        f"this PR changes safety-critical path(s) {', '.join(touched)} but adds no ADR. "
        "Add a docs/architecture/adr/<n>-*.md decision record (AGENTS.md section 11)."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)

    ok, reason = check(SubprocessGit(), args.base, args.head)
    if ok:
        print(f"gate-2 safety-path: pass ({reason})")
        return 0

    print(f"::error file=docs/code-governance/safety-paths.txt::gate-2 safety-path: {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
