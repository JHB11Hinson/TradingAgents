#!/usr/bin/env python3
"""gate-1-test-approval checker.

A pull request that changes ``src/`` must carry a ``Test-Approval:`` trailer that
points at a review record which:

* existed **before** the first ``src/`` commit in the PR history,
* contains ``Verdict: APPROVE``, and
* lists at least one existing test path under ``test/`` in a ``Tests:`` line.

The record may be the new per-PR file (``docs/review-memo/PR-<n>.md``) or the legacy
``docs/review-memo.md#<anchor>`` form.  Tests and implementation may not share a commit.

The checker is CI glue, not runtime code, so it lives under ``.github/scripts/``.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from typing import Callable, Protocol

TRAILER = re.compile(r"(?m)^Test-Approval:\s*(\S+)\s*$")
VERDICT = re.compile(r"(?im)^\s*(?:-\s*)?Verdict:\s*(.+?)\s*$")
TESTS = re.compile(r"(?im)^\s*(?:-\s*)?Tests:\s*(.+?)\s*$")
HEADING = re.compile(r"^#{1,6}\s")


class Git(Protocol):
    def changed_files(self, base: str, head: str) -> list[str]: ...

    def non_merge_commits(self, base: str, head: str) -> list[str]: ...

    def commit_files(self, commit: str) -> list[str]: ...

    def message(self, commit: str) -> str: ...

    def show(self, commit: str, path: str) -> str | None: ...

    def exists(self, commit: str, path: str) -> bool: ...


class SubprocessGit:
    """The real git implementation used by the workflow."""

    def _run(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout

    def changed_files(self, base: str, head: str) -> list[str]:
        out = self._run("diff", "--name-only", f"{base}...{head}")
        return [line for line in out.splitlines() if line]

    def non_merge_commits(self, base: str, head: str) -> list[str]:
        out = self._run("rev-list", "--reverse", "--no-merges", f"{base}..{head}")
        return [line for line in out.splitlines() if line]

    def commit_files(self, commit: str) -> list[str]:
        out = self._run("show", "--name-only", "--format=", commit)
        return [line for line in out.splitlines() if line]

    def message(self, commit: str) -> str:
        return self._run("show", "-s", "--format=%B", commit)

    def show(self, commit: str, path: str) -> str | None:
        try:
            return self._run("show", f"{commit}:{path}")
        except subprocess.CalledProcessError:
            return None

    def exists(self, commit: str, path: str) -> bool:
        try:
            self._run("cat-file", "-e", f"{commit}:{path}")
        except subprocess.CalledProcessError:
            return False
        return True


def parse_test_approval(text: str) -> str | None:
    match = TRAILER.search(text or "")
    return match.group(1).strip() if match else None


def split_target(target: str) -> tuple[str, str | None]:
    if "#" in target:
        path, anchor = target.split("#", 1)
        return path, anchor or None
    return target, None


def find_section(markdown: str, anchor: str | None) -> str | None:
    if anchor is None:
        return markdown
    lines = markdown.splitlines()
    start = None
    for index, line in enumerate(lines):
        if HEADING.match(line) and anchor in line:
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if HEADING.match(lines[index]):
            end = index
            break
    return "\n".join(lines[start:end])


def record_verdict(section: str) -> str | None:
    match = VERDICT.search(section)
    return match.group(1).strip().upper() if match else None


def record_tests(section: str) -> list[str]:
    match = TESTS.search(section)
    if not match:
        return []
    raw = match.group(1).strip()
    return [part.strip() for part in raw.split(",") if part.strip()]


def validate_record(
    section: str,
    path_exists: Callable[[str], bool],
) -> tuple[bool, str]:
    verdict = record_verdict(section)
    if verdict is None:
        return False, "the review record has no Verdict line"
    if not verdict.startswith("APPROVE"):
        return False, f"the review verdict is {verdict}, not APPROVE"

    tests = record_tests(section)
    if not tests:
        return False, "the review record has no Tests line"

    for path in tests:
        if not path.startswith("test/"):
            return False, f"{path} is not under test/"
        if not path_exists(path):
            return False, f"{path} does not exist"
    return True, "ok"


def check(git: Git, base: str, head: str, pr_body: str) -> tuple[bool, str]:
    changed = git.changed_files(base, head)
    if not any(path.startswith("src/") for path in changed):
        return True, "no src/ change"

    commits = git.non_merge_commits(base, head)
    for commit in commits:
        files = git.commit_files(commit)
        changes_test = any(path.startswith("test/") for path in files)
        changes_src = any(path.startswith("src/") for path in files)
        if changes_test and changes_src:
            return False, f"{commit[:8]} changes both test/ and src/; split the commits"

    first_src = None
    for commit in commits:
        if any(path.startswith("src/") for path in git.commit_files(commit)):
            first_src = commit
            break
    if first_src is None:
        return False, "src/ changed but no non-merge commit touches src/"

    target = parse_test_approval(pr_body)
    if target is None:
        for commit in commits:
            target = parse_test_approval(git.message(commit))
            if target is not None:
                break
    if target is None:
        return False, "no Test-Approval: trailer in the PR body or commit messages"

    path, anchor = split_target(target)
    parent = f"{first_src}^"
    record = git.show(parent, path)
    if record is None:
        return False, f"{path} does not exist before the first src/ commit ({first_src[:8]})"

    section = find_section(record, anchor)
    if section is None:
        return False, f"section {anchor!r} not found in {path}"

    return validate_record(section, lambda test_path: git.exists(head, test_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--pr-body", default="")
    args = parser.parse_args(argv)

    ok, reason = check(SubprocessGit(), args.base, args.head, args.pr_body)
    if ok:
        print(f"gate-1: pass ({reason})")
        return 0

    print(f"::error file=docs/review-memo/README.md::gate-1: {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
