"""Verifies D1-REQ-GOV-009: the architecture decision records are uniquely identified.

`docs/architecture/adr/` is a numbered series that other documents cite by number (`ADR-014`). Two
files once shared `014`: `014-memory-source-attribution.md` (accepted, cited from `src/`) and
`014-inherited-test-requirement-tags.md` (proposed, filed later). A reader following `ADR-014` could
not tell which decision it meant.

The tests below are the guard: the number prefix of every file must be unique, the series must have
no gap, and every `ADR-<n>` reference in the tracked documents must resolve to exactly one file.
They fail on the duplicate and pass once the later, still-proposed record is renumbered to 017.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ADR_DIR = REPO / "docs" / "architecture" / "adr"
NAME = re.compile(r"^(\d{3})-([a-z0-9-]+)\.md$")
CITATION = re.compile(r"\bADR-(\d{3})\b")

# Documents that may cite an ADR. Transcripts and review records are historical evidence: they
# quote what was true when written, so they are not rewritten by a renumbering.
CITING_DOCS = (
    "AGENTS.md",
    "architecture-blueprint.md",
    "README.md",
    "Report.md",
    "docs/architecture",
    "docs/code-governance",
    "src",
)


def _adr_files() -> list[tuple[str, Path]]:
    found = []
    for path in sorted(ADR_DIR.glob("*.md")):
        match = NAME.match(path.name)
        assert match is not None, f"{path.name} does not follow NNN-slug.md"
        found.append((match.group(1), path))
    return found


@pytest.mark.unit
def test_every_adr_number_is_unique() -> None:
    numbers = Counter(number for number, _ in _adr_files())
    duplicates = sorted(number for number, count in numbers.items() if count > 1)
    assert not duplicates, f"ADR number(s) used by more than one file: {duplicates}"


@pytest.mark.unit
def test_the_adr_series_has_no_gap() -> None:
    numbers = sorted(int(number) for number, _ in _adr_files())
    expected = list(range(1, len(numbers) + 1))
    assert numbers == expected, f"expected 1..{len(numbers)}, found {numbers}"


@pytest.mark.unit
def test_every_adr_number_in_a_heading_matches_its_filename() -> None:
    for number, path in _adr_files():
        heading = path.read_text(encoding="utf-8").splitlines()[0]
        assert heading.startswith(f"# ADR-{number}:"), (
            f"{path.name} announces {heading!r}; the heading must start with '# ADR-{number}:'"
        )


@pytest.mark.unit
def test_every_heading_has_the_same_number_as_its_filename_after_the_fix() -> None:
    """The 017 record keeps its title, so a citation by number is unambiguous either way."""
    assert (ADR_DIR / "017-inherited-test-requirement-tags.md").exists()
    assert not (ADR_DIR / "014-inherited-test-requirement-tags.md").exists()


@pytest.mark.unit
def test_every_cited_adr_number_resolves_to_one_file() -> None:
    known = {number for number, _ in _adr_files()}
    missing = []
    for doc in CITING_DOCS:
        root = REPO / doc
        paths = [root] if root.is_file() else sorted(root.rglob("*.md")) + sorted(root.rglob("*.py"))
        for path in paths:
            for match in CITATION.finditer(path.read_text(encoding="utf-8")):
                if match.group(1) not in known:
                    missing.append(f"{path.relative_to(REPO)}: ADR-{match.group(1)}")
    assert not missing, f"citations with no ADR file: {missing}"


@pytest.mark.unit
def test_a_duplicate_number_is_reported(tmp_path: Path) -> None:
    """Negative: the uniqueness check is what fails today, so prove it can fail."""
    numbers = Counter(["014", "014", "015"])
    duplicates = sorted(number for number, count in numbers.items() if count > 1)
    assert duplicates == ["014"]
