"""Verifies D1-REQ-GOV-008: requirements, invariants and the trace matrix have no gaps.

The registry is the source of truth for requirement ids. Every id needs one
trace-matrix row with a component, evidence and monitor; every `type: invariant`
requirement needs an invariant-register row and a detail block with a source,
enforcer, verification method and concrete fallback. The register's status must
agree with the detail block, and every `must` requirement must appear in the
verification status table. A missing entry is a release blocker, so the check
fails rather than warns.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "docs" / "req" / "requirements.yaml"
MATRIX = REPO / "docs" / "architecture" / "trace-matrix.md"
INVARIANTS = REPO / "docs" / "architecture" / "invariants.md"
VERIFICATION = REPO / "docs" / "code-governance" / "verification-constraints.md"

REQ_ID = re.compile(r"D1-REQ-[A-Z]+-\d+")
BACKTICK = re.compile(r"`([^`]+)`")
INV_ID = re.compile(r"INV-\d+")
INV_HEADING = re.compile(r"(?m)^### (INV-\d+) — .*$")
SEPARATOR = re.compile(r"^:?-{2,}:?$")
INVARIANT_FIELDS = (
    "statement",
    "source",
    "enforcing component",
    "verification",
    "operational fallback",
    "status",
)


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(row: list[str]) -> bool:
    return bool(row) and all(SEPARATOR.match(cell.replace(" ", "")) for cell in row)


def load_registry(path: Path = REGISTRY) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def parse_trace_matrix(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    rows: dict[str, dict[str, str]] = {}
    duplicates: list[str] = []
    in_table = False
    for line in text.splitlines():
        if line.strip().startswith("| REQ ID |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.strip().startswith("|"):
            if line.strip():
                break
            continue
        row = cells(line)
        if is_separator(row) or len(row) < 6:
            continue
        req = row[0].strip("` ")
        if req in rows:
            duplicates.append(req)
        rows[req] = {
            "priority": row[1],
            "requirement": row[2],
            "component": row[3],
            "test": row[4],
            "monitor": row[5],
        }
    return rows, duplicates


def parse_invariant_register(text: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for line in text.splitlines():
        if not line.strip().startswith("| `INV-"):
            continue
        row = cells(line)
        if len(row) < 5:
            continue
        inv = row[0].strip("` ")
        rows[inv] = {
            "statement": row[1],
            "sources": set(REQ_ID.findall(row[2])),
            "enforcer": row[3],
            "status": normalize_status(row[4]),
        }
    return rows


def parse_invariant_blocks(text: str) -> dict[str, dict[str, str]]:
    headings = list(INV_HEADING.finditer(text))
    blocks: dict[str, dict[str, str]] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end():end]
        block: dict[str, str] = {}
        for field in INVARIANT_FIELDS:
            label = re.escape(field)
            match = re.search(rf"(?m)^-\s+\*\*{label}\.\*\*\s*(.+)$", body, re.IGNORECASE)
            block[field] = match.group(1).strip() if match else ""
            if field == "status" and block[field]:
                block[field] = normalize_status(block[field])
        blocks[heading.group(1)] = block
    return blocks


def parse_verification_status_ids(text: str) -> set[str]:
    start = text.find("## 4. Must requirements")
    if start == -1:
        return set()
    body = text[start:]
    end = re.search(r"(?m)^##\s", body[len("## 4. Must requirements"):])
    if end:
        body = body[: len("## 4. Must requirements") + end.start()]
    found: set[str] = set()
    for line in body.splitlines():
        if not line.strip().startswith("| `"):
            continue
        row = cells(line)
        if not row or is_separator(row):
            continue
        found |= set(BACKTICK.findall(row[0]))
    return found


def normalize_status(value: str) -> str:
    cleaned = re.sub(r"[*`]", "", value).strip().lower()
    for status in ("implemented", "partial", "planned"):
        if cleaned.startswith(status):
            return status
    return cleaned.split()[0] if cleaned else ""


def registry_problems(registry: list[dict], matrix: dict[str, dict[str, str]]) -> list[str]:
    problems: list[str] = []
    ids = {item["id"] for item in registry}
    for missing in sorted(ids - set(matrix)):
        problems.append(f"requirement {missing} has no trace-matrix row")
    for extra in sorted(set(matrix) - ids):
        problems.append(f"trace-matrix row {extra} has no registry entry")
    for item in registry:
        if item["priority"] == "wont":
            continue
        row = matrix.get(item["id"])
        if row is None:
            continue
        for field in ("component", "test", "monitor"):
            value = row[field]
            if not value or value.lower().startswith("none"):
                problems.append(f"{item['id']} has an empty {field} column")
    return problems


def invariant_problems(
    registry: list[dict],
    register: dict[str, dict],
    blocks: dict[str, dict[str, str]],
) -> list[str]:
    problems: list[str] = []
    ids = {item["id"] for item in registry}
    invariant_ids = {item["id"] for item in registry if item["type"] == "invariant"}
    covered: set[str] = set()

    for inv, row in sorted(register.items()):
        if inv not in blocks:
            problems.append(f"{inv} has a register row but no detail block")
        for source in sorted(row["sources"]):
            if source not in ids:
                problems.append(f"{inv} cites unknown source {source}")
            if source in invariant_ids:
                covered.add(source)

    for inv, block in sorted(blocks.items()):
        if inv not in register:
            problems.append(f"{inv} has a detail block but no register row")
        for field in INVARIANT_FIELDS:
            if not block.get(field):
                problems.append(f"{inv} is missing its {field} field")

    for missing in sorted(invariant_ids - covered):
        problems.append(f"invariant requirement {missing} has no INV row")

    for inv, row in sorted(register.items()):
        block = blocks.get(inv)
        if block and block.get("status") and row["status"] != block["status"]:
            problems.append(
                f"{inv} register status {row['status']} disagrees with "
                f"detail status {block['status']}"
            )
    return problems


def verification_status_problems(registry: list[dict], status_ids: set[str]) -> list[str]:
    must = {item["id"].removeprefix("D1-REQ-") for item in registry if item["priority"] == "must"}
    return [
        f"must requirement {short} is missing from the verification status table"
        for short in sorted(must - status_ids)
    ]


def real_registry() -> list[dict]:
    return load_registry()


def real_matrix() -> tuple[dict[str, dict[str, str]], list[str]]:
    return parse_trace_matrix(MATRIX.read_text(encoding="utf-8"))


def real_invariants() -> tuple[dict[str, dict], dict[str, dict[str, str]]]:
    text = INVARIANTS.read_text(encoding="utf-8")
    return parse_invariant_register(text), parse_invariant_blocks(text)


@pytest.mark.unit
def test_every_requirement_has_exactly_one_trace_matrix_row():
    matrix, duplicates = real_matrix()

    assert duplicates == []
    assert set(matrix) == {item["id"] for item in real_registry()}


@pytest.mark.unit
def test_every_non_wont_row_has_a_component_test_and_monitor():
    problems = registry_problems(real_registry(), real_matrix()[0])

    assert problems == []


@pytest.mark.unit
def test_every_invariant_requirement_has_a_register_row_and_block():
    register, blocks = real_invariants()
    problems = invariant_problems(real_registry(), register, blocks)

    assert problems == []


@pytest.mark.unit
def test_every_must_requirement_is_in_the_verification_status_table():
    status_ids = parse_verification_status_ids(VERIFICATION.read_text(encoding="utf-8"))
    problems = verification_status_problems(real_registry(), status_ids)

    assert problems == []


@pytest.mark.unit
def test_the_register_status_matches_the_detail_block():
    """INV-02 and INV-03 were finished in CHG-033 but stayed marked planned."""
    register, blocks = real_invariants()

    disagreements = [
        inv
        for inv, row in register.items()
        if inv in blocks and row["status"] != blocks[inv]["status"]
    ]

    assert disagreements == []


@pytest.mark.unit
def test_a_requirement_missing_from_the_matrix_is_reported():
    registry = [
        {"id": "D1-REQ-A-001", "type": "functional", "priority": "must"},
        {"id": "D1-REQ-A-002", "type": "functional", "priority": "must"},
    ]
    matrix = {
        "D1-REQ-A-001": {"component": "c", "test": "t", "monitor": "m", "priority": "must"}
    }

    problems = registry_problems(registry, matrix)

    assert any("D1-REQ-A-002" in problem and "no trace-matrix row" in problem for problem in problems)


@pytest.mark.unit
def test_an_unknown_matrix_row_is_reported():
    registry = [{"id": "D1-REQ-A-001", "type": "functional", "priority": "must"}]
    matrix = {
        "D1-REQ-A-001": {"component": "c", "test": "t", "monitor": "m", "priority": "must"},
        "D1-REQ-A-999": {"component": "c", "test": "t", "monitor": "m", "priority": "must"},
    }

    problems = registry_problems(registry, matrix)

    assert any("D1-REQ-A-999" in problem and "no registry entry" in problem for problem in problems)


@pytest.mark.unit
def test_a_deferred_row_may_say_none():
    registry = [{"id": "D1-REQ-A-001", "type": "functional", "priority": "wont"}]
    matrix = {
        "D1-REQ-A-001": {
            "component": "none — deferred",
            "test": "none — deferred",
            "monitor": "none — deferred",
            "priority": "wont",
        }
    }

    assert registry_problems(registry, matrix) == []


@pytest.mark.unit
def test_a_non_wont_row_with_none_evidence_is_reported():
    registry = [{"id": "D1-REQ-A-001", "type": "functional", "priority": "must"}]
    matrix = {
        "D1-REQ-A-001": {
            "component": "src/x.py",
            "test": "none — deferred",
            "monitor": "run log",
            "priority": "must",
        }
    }

    problems = registry_problems(registry, matrix)

    assert any("D1-REQ-A-001" in problem and "empty test column" in problem for problem in problems)


@pytest.mark.unit
def test_an_invariant_without_a_detail_block_is_reported():
    registry = [{"id": "D1-REQ-A-001", "type": "invariant", "priority": "must"}]
    register = {
        "INV-01": {"sources": {"D1-REQ-A-001"}, "status": "implemented", "statement": "s"}
    }

    problems = invariant_problems(registry, register, {})

    assert any("INV-01" in problem and "no detail block" in problem for problem in problems)


@pytest.mark.unit
def test_an_invariant_requirement_without_a_register_row_is_reported():
    registry = [{"id": "D1-REQ-A-001", "type": "invariant", "priority": "must"}]

    problems = invariant_problems(registry, {}, {})

    assert any("D1-REQ-A-001" in problem and "no INV row" in problem for problem in problems)


@pytest.mark.unit
def test_a_missing_invariant_field_is_reported():
    registry = [
        {
            "id": "D1-REQ-A-001",
            "type": "invariant",
            "priority": "must",
        }
    ]
    register = {
        "INV-01": {"sources": {"D1-REQ-A-001"}, "status": "implemented", "statement": "s"}
    }
    block = {
        "statement": "s",
        "source": "D1-REQ-A-001",
        "enforcing component": "src/x.py",
        "verification": "test/offline/test_x.py",
        "operational fallback": "",
        "status": "implemented",
    }

    problems = invariant_problems(registry, register, {"INV-01": block})

    assert any("INV-01" in problem and "operational fallback" in problem for problem in problems)


@pytest.mark.unit
def test_a_status_mismatch_between_register_and_detail_is_reported():
    registry = [
        {
            "id": "D1-REQ-A-001",
            "type": "invariant",
            "priority": "must",
        }
    ]
    register = {
        "INV-01": {"sources": {"D1-REQ-A-001"}, "status": "planned", "statement": "s"}
    }
    block = {
        "statement": "s",
        "source": "D1-REQ-A-001",
        "enforcing component": "src/x.py",
        "verification": "test/offline/test_x.py",
        "operational fallback": "stop the run",
        "status": "implemented",
    }

    problems = invariant_problems(registry, register, {"INV-01": block})

    assert any("INV-01" in problem and "disagrees" in problem for problem in problems)


@pytest.mark.unit
def test_a_missing_must_status_row_is_reported():
    registry = [
        {"id": "D1-REQ-A-001", "type": "functional", "priority": "must"},
        {"id": "D1-REQ-A-002", "type": "functional", "priority": "should"},
    ]

    problems = verification_status_problems(registry, {"A-002"})

    assert any("A-001" in problem for problem in problems)
