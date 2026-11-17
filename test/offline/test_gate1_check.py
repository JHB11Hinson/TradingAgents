"""Contract tests for the gate-1 test-approval checker.

The checker lives in .github/scripts/gate1_check.py because it is CI glue, not runtime
code.  It is loaded by path so the test suite does not need a package import.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github" / "scripts" / "gate1_check.py"

spec = importlib.util.spec_from_file_location("gate1_check", SCRIPT)
gate1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate1)


class FakeGit:
    def __init__(self, changed, commits, files, messages, contents):
        self._changed = changed
        self._commits = commits
        self._files = files
        self._messages = messages
        self._contents = contents

    def changed_files(self, base, head):
        return self._changed

    def non_merge_commits(self, base, head):
        return self._commits

    def commit_files(self, commit):
        return self._files.get(commit, [])

    def message(self, commit):
        return self._messages.get(commit, "")

    def _resolve(self, commit):
        if commit.endswith("^") and commit[:-1] in self._commits:
            index = self._commits.index(commit[:-1])
            if index > 0:
                return self._commits[index - 1]
        return commit

    def show(self, commit, path):
        return self._contents.get((self._resolve(commit), path))

    def exists(self, commit, path):
        return (self._resolve(commit), path) in self._contents


RECORD = "### PR-1 — CHG-030 gate-1\n- Verdict: APPROVE\n- Tests: test/offline/test_foo.py\n"


def valid_git(**overrides):
    contents = {
        ("c1", "docs/review-memo/PR-1.md"): RECORD,
        ("HEAD", "test/offline/test_foo.py"): "",
    }
    contents.update(overrides.pop("contents", {}))
    data = {
        "changed": ["src/foo.py"],
        "commits": ["c1", "c2"],
        "files": {"c1": ["test/offline/test_foo.py"], "c2": ["src/foo.py"]},
        "messages": {"c1": "", "c2": "feat: change\n\nTest-Approval: docs/review-memo/PR-1.md\n"},
        "contents": contents,
    }
    data.update(overrides)
    return FakeGit(**data)


def test_parse_test_approval_accepts_trailer():
    assert gate1.parse_test_approval("body\nTest-Approval: docs/review-memo/PR-1.md\n") == (
        "docs/review-memo/PR-1.md"
    )


def test_parse_test_approval_missing():
    assert gate1.parse_test_approval("body only") is None


def test_find_section_by_anchor():
    text = "### CHG-1 — one\n- Verdict: APPROVE\n\n### CHG-2 — two\n- Verdict: REJECT\n"
    section = gate1.find_section(text, "CHG-1")
    assert section is not None
    assert "APPROVE" in section
    assert "CHG-2" not in section


def test_validate_record_accepts_inherited_test():
    ok, reason = gate1.validate_record(RECORD, lambda p: p == "test/offline/test_foo.py")
    assert ok, reason


def test_validate_record_requires_verdict():
    ok, _ = gate1.validate_record("- Tests: test/offline/test_foo.py\n", lambda p: True)
    assert not ok


def test_validate_record_requires_tests_line():
    ok, _ = gate1.validate_record("- Verdict: APPROVE\n", lambda p: True)
    assert not ok


def test_validate_record_rejects_path_outside_test():
    text = "- Verdict: APPROVE\n- Tests: src/foo.py\n"
    ok, _ = gate1.validate_record(text, lambda p: True)
    assert not ok


def test_validate_record_rejects_missing_test_path():
    text = "- Verdict: APPROVE\n- Tests: test/offline/missing.py\n"
    ok, _ = gate1.validate_record(text, lambda p: False)
    assert not ok


def test_no_src_change_passes():
    git = FakeGit(changed=["docs/x.md"], commits=[], files={}, messages={}, contents={})
    ok, reason = gate1.check(git, "main", "HEAD", "")
    assert ok, reason


def test_src_without_trailer_fails():
    git = valid_git(messages={"c1": "", "c2": "feat: change"})
    ok, _ = gate1.check(git, "main", "HEAD", "")
    assert not ok


def test_same_commit_cannot_mix_test_and_src():
    git = valid_git(files={"c1": ["test/offline/test_foo.py", "src/foo.py"], "c2": ["src/foo.py"]})
    ok, _ = gate1.check(git, "main", "HEAD", "")
    assert not ok


def test_record_after_first_src_commit_fails():
    git = valid_git(
        contents={
            ("c1", "docs/review-memo/PR-1.md"): None,
            ("c2", "docs/review-memo/PR-1.md"): RECORD,
        }
    )
    ok, _ = gate1.check(git, "main", "HEAD", "")
    assert not ok


def test_valid_record_before_src_passes():
    ok, reason = gate1.check(valid_git(), "main", "HEAD", "")
    assert ok, reason


def test_pr_body_trailer_is_accepted():
    git = valid_git(messages={"c1": "", "c2": "feat: change"})
    ok, reason = gate1.check(git, "main", "HEAD", "Test-Approval: docs/review-memo/PR-1.md\n")
    assert ok, reason


def test_legacy_anchor_is_accepted():
    legacy = "### CHG-030 — gate-1\n- Verdict: APPROVE\n- Tests: test/offline/test_foo.py\n"
    git = valid_git(
        messages={"c1": "", "c2": "Test-Approval: docs/review-memo.md#CHG-030\n"},
        contents={("c1", "docs/review-memo.md"): legacy},
    )
    ok, reason = gate1.check(git, "main", "HEAD", "")
    assert ok, reason


@pytest.mark.parametrize("verdict", ["CHANGES REQUIRED", "REJECT", "PENDING"])
def test_non_approve_verdicts_fail(verdict):
    text = f"- Verdict: {verdict}\n- Tests: test/offline/test_foo.py\n"
    ok, _ = gate1.validate_record(text, lambda p: True)
    assert not ok
