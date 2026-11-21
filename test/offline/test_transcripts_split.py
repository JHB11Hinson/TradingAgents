"""Verifies D1-REQ-GOV-011: the split transcript index and its session parts agree.

CHG-046 split the combined 1.2 MB transcript into one part per annotated session so that
every part stays below GitHub's 1 MB render limit. The split is only useful evidence while
the index links every part, each session appears once, and no part grows past the limit, so
this check fails rather than warns.
"""

from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TRANSCRIPTS = REPO / "transcripts"
INDEX = TRANSCRIPTS / "60198818-HaobinJiang.md"

PART_NAME = re.compile(r"^60198818-HaobinJiang-S\d{2}-.+\.md$")
LINK = re.compile(r"\((60198818-HaobinJiang-S\d{2}-[^)]+\.md)\)")
SESSION = re.compile(r"^## Session (\d{2})\b", re.MULTILINE)
MAX_BYTES = 1_000_000


def _read_parts() -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(TRANSCRIPTS.iterdir())
        if path.is_file() and PART_NAME.match(path.name)
    }


def _linked_parts(index_text: str) -> set[str]:
    return set(LINK.findall(index_text))


def _problems(index_text: str, parts: dict[str, str], max_bytes: int = MAX_BYTES) -> list[str]:
    problems: list[str] = []
    linked = _linked_parts(index_text)
    for name in sorted(set(parts) - linked):
        problems.append(f"{name} is not linked from the index")
    for name in sorted(linked - set(parts)):
        problems.append(f"the index links {name}, which does not exist")

    seen: dict[str, str] = {}
    for name, text in sorted(parts.items()):
        size = len(text.encode("utf-8"))
        if size > max_bytes:
            problems.append(f"{name} is {size} bytes, over the {max_bytes}-byte render limit")
        sessions = SESSION.findall(text)
        if len(sessions) != 1:
            problems.append(f"{name} has {len(sessions)} session headings, expected 1")
        for session in sessions:
            if session in seen:
                problems.append(f"session {session} appears in both {seen[session]} and {name}")
            else:
                seen[session] = name
    return problems


@pytest.mark.unit
def test_the_split_index_links_every_part_and_every_session_appears_once():
    problems = _problems(INDEX.read_text(encoding="utf-8"), _read_parts())

    assert problems == []


@pytest.mark.unit
def test_all_eleven_sessions_are_present():
    sessions = sorted(
        session for text in _read_parts().values() for session in SESSION.findall(text)
    )

    assert sessions == [f"{number:02d}" for number in range(1, 12)]


@pytest.mark.unit
def test_every_part_stays_under_the_github_render_limit():
    oversized = {
        name: len(text.encode("utf-8"))
        for name, text in _read_parts().items()
        if len(text.encode("utf-8")) > MAX_BYTES
    }

    assert oversized == {}


@pytest.mark.unit
def test_the_checker_rejects_an_index_that_forgets_a_part():
    name = "60198818-HaobinJiang-S01-CHG-001-structural-alignment.md"

    problems = _problems("# index\n", {name: "## Session 01\n"})

    assert any("is not linked from the index" in problem for problem in problems)


@pytest.mark.unit
def test_the_checker_rejects_a_duplicate_session():
    first = "60198818-HaobinJiang-S01-CHG-001-structural-alignment.md"
    second = "60198818-HaobinJiang-S02-CHG-002-first-blocking-gate-batch.md"
    index = f"[one]({first}) [two]({second})"

    problems = _problems(index, {first: "## Session 01\n", second: "## Session 01\n"})

    assert any("appears in both" in problem for problem in problems)


@pytest.mark.unit
def test_the_checker_rejects_an_oversized_part():
    name = "60198818-HaobinJiang-S01-CHG-001-structural-alignment.md"
    index = f"[one]({name})"

    problems = _problems(index, {name: "## Session 01\n"}, max_bytes=1)

    assert any("render limit" in problem for problem in problems)
