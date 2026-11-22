"""Verifies D1-REQ-GOV-006: the three permission sources list the same whitelist.

`.opencode/permissions.jsonc`, `docs/architecture/permission-model.md` and
`AGENTS.md` section 13 must agree on the read and write path sets. A path that
appears in one source and is absent from another is a review blocker, so the
check fails rather than warns.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
JSONC = REPO / ".opencode" / "permissions.jsonc"
MODEL = REPO / "docs" / "architecture" / "permission-model.md"
AGENTS = REPO / "AGENTS.md"

MODES_BY_KIND = {
    "read": ("allow", "deny"),
    "write": ("allow", "ask", "deny"),
}
KINDS = tuple(MODES_BY_KIND)
BACKTICK = re.compile(r"`([^`]+)`")
AGENTS_ROW = re.compile(
    r"^\|\s*\*\*(Read|Write)\s*—\s*(allow|ask|deny)\*\*\s*\|(.*)\|\s*$",
    re.MULTILINE,
)
MODEL_ROW = re.compile(
    r"^\|\s*\*\*(allow|ask|deny)\*\*\s*\|(.*)\|\s*$",
    re.MULTILINE,
)


def strip_jsonc_comments(text: str) -> str:
    """Remove whole-line `//` comments; the file has no `//` inside strings."""
    return re.sub(r"(?m)^\s*//.*$", "", text)


def load_jsonc(path: Path) -> dict:
    return json.loads(strip_jsonc_comments(path.read_text(encoding="utf-8")))


def section(text: str, heading: str) -> str:
    """Return one markdown section, from `heading` to the next `## ` heading."""
    start = text.index(heading)
    rest = text[start + len(heading):]
    end = re.search(r"(?m)^##\s", rest)
    return rest[: end.start()] if end else rest


def backtick_paths(cell: str) -> set[str]:
    return {value.strip() for value in BACKTICK.findall(cell) if value.strip()}


def parse_agents(text: str) -> dict[tuple[str, str], set[str]]:
    body = section(text, "## 13.")
    parsed = {
        (kind.lower(), mode.lower()): set()
        for kind in KINDS
        for mode in MODES_BY_KIND[kind]
    }
    for kind, mode, cell in AGENTS_ROW.findall(body):
        parsed[(kind.lower(), mode.lower())] |= backtick_paths(cell)
    return parsed


def parse_permission_model(text: str) -> dict[tuple[str, str], set[str]]:
    parsed: dict[tuple[str, str], set[str]] = {}
    for kind, heading in (("read", "## 3. Read whitelist"), ("write", "## 4. Write whitelist")):
        body = section(text, heading)
        for mode, cell in MODEL_ROW.findall(body):
            parsed[(kind, mode.lower())] = backtick_paths(cell)
    return parsed


def parse_jsonc(data: dict) -> dict[tuple[str, str], set[str]]:
    return {
        (kind, mode): set(data[kind].get(mode, []))
        for kind in KINDS
        for mode in MODES_BY_KIND[kind]
    }


def compare_sources(sources: dict[str, dict[tuple[str, str], set[str]]]) -> list[str]:
    """Report every (kind, mode, path) that is not present in every source."""
    problems: list[str] = []
    keys = {(kind, mode) for kind in KINDS for mode in MODES_BY_KIND[kind]}
    for key in sorted(keys):
        per_source = {name: set(parsed.get(key, set())) for name, parsed in sources.items()}
        union = set().union(*per_source.values())
        for name, paths in sorted(per_source.items()):
            missing = sorted(union - paths)
            if missing:
                problems.append(f"{name} is missing {key[0]}/{key[1]}: {missing}")
    return problems


def default_deny_problems(jsonc: dict, model_text: str, agents_text: str) -> list[str]:
    problems = []
    if jsonc.get("default") != "deny":
        problems.append("permissions.jsonc default is not deny")
    if "default: deny" not in model_text.lower():
        problems.append("permission-model.md does not declare default: deny")
    if "default deny" not in agents_text.lower():
        problems.append("AGENTS.md section 13 does not declare default deny")
    return problems


def parsed_sources() -> dict[str, dict[tuple[str, str], set[str]]]:
    return {
        "permissions.jsonc": parse_jsonc(load_jsonc(JSONC)),
        "permission-model.md": parse_permission_model(MODEL.read_text(encoding="utf-8")),
        "AGENTS.md": parse_agents(AGENTS.read_text(encoding="utf-8")),
    }


@pytest.mark.unit
def test_three_sources_list_the_same_read_and_write_whitelists():
    sources = parsed_sources()

    assert compare_sources(sources) == []


@pytest.mark.unit
def test_every_source_actually_declares_paths():
    """Guard against a parser that silently reads nothing and passes vacuously."""
    sources = parsed_sources()

    for name, parsed in sources.items():
        for key in ((kind, mode) for kind in KINDS for mode in MODES_BY_KIND[kind]):
            assert parsed[key], f"{name} has no {key[0]}/{key[1]} paths"


@pytest.mark.unit
def test_every_source_declares_default_deny():
    problems = default_deny_problems(
        load_jsonc(JSONC),
        MODEL.read_text(encoding="utf-8"),
        AGENTS.read_text(encoding="utf-8"),
    )

    assert problems == []


@pytest.mark.unit
def test_a_path_missing_from_one_source_is_reported():
    sources = {
        "one": {("read", "allow"): {"docs/**", "src/**"}},
        "two": {("read", "allow"): {"docs/**"}},
    }

    problems = compare_sources(sources)

    assert any("two is missing read/allow" in problem and "src/**" in problem for problem in problems)


@pytest.mark.unit
def test_a_whole_mode_missing_from_one_source_is_reported():
    sources = {
        "one": {("write", "deny"): {".env"}},
        "two": {("write", "deny"): set()},
    }

    problems = compare_sources(sources)

    assert any("two is missing write/deny" in problem and ".env" in problem for problem in problems)


@pytest.mark.unit
def test_agents_parser_reads_the_five_permission_rows():
    parsed = parse_agents(
        "## 13. Permission model\n"
        "| Mode | Paths |\n"
        "|---|---|\n"
        "| **Read — allow** | `AGENTS.md`, `src/**` |\n"
        "| **Read — deny** | `.env` |\n"
        "| **Write — allow** | `docs/**` |\n"
        "| **Write — ask** | `AGENTS.md` |\n"
        "| **Write — deny** | `.git/**` |\n"
        "\n## 14. Next\n"
        "| **Read — allow** | `ignored/**` |\n"
    )

    assert parsed[("read", "allow")] == {"AGENTS.md", "src/**"}
    assert parsed[("read", "deny")] == {".env"}
    assert parsed[("write", "allow")] == {"docs/**"}
    assert parsed[("write", "ask")] == {"AGENTS.md"}
    assert parsed[("write", "deny")] == {".git/**"}


@pytest.mark.unit
def test_permission_model_parser_reads_both_whitelists():
    parsed = parse_permission_model(
        "## 3. Read whitelist\n"
        "| Mode | Paths |\n"
        "|---|---|\n"
        "| **allow** | `AGENTS.md`, `src/**` |\n"
        "| **deny** | `.env` |\n"
        "\n## 4. Write whitelist\n"
        "| Mode | Paths |\n"
        "|---|---|\n"
        "| **allow** | `docs/**` |\n"
        "| **ask** | `AGENTS.md` |\n"
        "| **deny** | `.git/**` |\n"
    )

    assert parsed[("read", "allow")] == {"AGENTS.md", "src/**"}
    assert parsed[("read", "deny")] == {".env"}
    assert parsed[("write", "allow")] == {"docs/**"}
    assert parsed[("write", "ask")] == {"AGENTS.md"}
    assert parsed[("write", "deny")] == {".git/**"}


@pytest.mark.unit
def test_jsonc_parser_reads_the_three_tiers():
    parsed = parse_jsonc(
        {
            "read": {"allow": ["src/**"], "deny": [".env"]},
            "write": {"allow": ["docs/**"], "ask": ["AGENTS.md"], "deny": [".git/**"]},
        }
    )

    assert parsed[("read", "allow")] == {"src/**"}
    assert parsed[("write", "ask")] == {"AGENTS.md"}
    assert parsed[("write", "deny")] == {".git/**"}


@pytest.mark.unit
def test_default_deny_helper_reports_each_missing_declaration():
    problems = default_deny_problems({"default": "allow"}, "nothing", "nothing")

    assert len(problems) == 3
