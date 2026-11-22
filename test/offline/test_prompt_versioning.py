"""Verifies D1-REQ-GOV-012: runtime prompts are versioned files, never edited in place.

`prompts/prompt_vX.Y.yaml` is the versioned prompt store. Every entry carries a
SHA-256 over its text, the loader verifies it on read and fails closed, and
`prompts/index.yaml` is the append-only checksum ledger for the files themselves.
Adding a prompt change means adding a new version file, not editing v1.0.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest
import yaml
from tradingagents.prompts.loader import (
    PromptError,
    checksum_text,
    load_all,
    load_prompt,
    parse_version,
    prompt_files,
    prompts_dir,
)

REPO = Path(__file__).resolve().parents[2]
PROMPTS = REPO / "prompts"
INDEX = PROMPTS / "index.yaml"
FILENAME = re.compile(r"^prompt_v(\d+)\.(\d+)\.yaml$")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_entries() -> list[dict]:
    data = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    return data["files"]


def write_prompt(
    directory: Path,
    *,
    version: str,
    name: str,
    text: str,
    sha256: str | None = None,
) -> Path:
    path = directory / f"prompt_v{version}.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "version": version,
                "checksum_algorithm": "sha256",
                "prompts": {
                    name: {
                        "description": "test prompt",
                        "sha256": sha256 if sha256 is not None else checksum_text(text),
                        "text": text,
                    }
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.unit
def test_prompt_v1_0_exists_and_loads_its_entries():
    assert (PROMPTS / "prompt_v1.0.yaml").is_file()

    loaded = load_all()

    assert loaded
    assert "analyst.market.system" in loaded
    assert loaded["analyst.market.system"].version == "1.0"


@pytest.mark.unit
def test_every_prompt_text_matches_its_recorded_checksum():
    for path in prompt_files():
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for name, entry in data["prompts"].items():
            assert entry["sha256"] == checksum_text(entry["text"]), f"{path.name}:{name}"


@pytest.mark.unit
def test_the_index_records_every_prompt_file_and_its_checksum():
    files = {path.name: path for path in prompt_files()}
    entries = {entry["file"]: entry for entry in index_entries()}

    assert set(entries) == set(files)
    for name, path in files.items():
        assert entries[name]["version"] == ".".join(map(str, parse_version(path)))
        assert entries[name]["sha256"] == file_sha256(path), f"{name} was edited in place"


@pytest.mark.unit
def test_the_index_has_no_duplicate_versions():
    versions = [entry["version"] for entry in index_entries()]

    assert len(versions) == len(set(versions))


@pytest.mark.unit
def test_prompt_filenames_and_versions_are_well_formed_and_unique():
    versions = [parse_version(path) for path in prompt_files()]

    for path in prompt_files():
        assert FILENAME.match(path.name), path.name
    assert versions
    assert len(versions) == len(set(versions))
    assert versions == sorted(versions)


@pytest.mark.unit
def test_the_loader_returns_the_highest_version_unless_pinned(tmp_path, monkeypatch):
    write_prompt(tmp_path, version="1.0", name="x", text="one")
    write_prompt(tmp_path, version="1.1", name="x", text="two")
    monkeypatch.setenv("TRADINGAGENTS_PROMPTS_DIR", str(tmp_path))

    assert load_prompt("x").text == "two"
    assert load_prompt("x").version == "1.1"
    assert load_prompt("x", version="1.0").text == "one"


@pytest.mark.unit
def test_a_tampered_prompt_text_is_rejected(tmp_path, monkeypatch):
    write_prompt(tmp_path, version="1.0", name="x", text="changed", sha256=checksum_text("original"))
    monkeypatch.setenv("TRADINGAGENTS_PROMPTS_DIR", str(tmp_path))

    with pytest.raises(PromptError, match="checksum"):
        load_prompt("x")


@pytest.mark.unit
def test_a_missing_checksum_is_rejected(tmp_path, monkeypatch):
    write_prompt(tmp_path, version="1.0", name="x", text="text", sha256="")
    monkeypatch.setenv("TRADINGAGENTS_PROMPTS_DIR", str(tmp_path))

    with pytest.raises(PromptError, match="checksum"):
        load_prompt("x")


@pytest.mark.unit
def test_the_yaml_version_must_match_the_filename(tmp_path, monkeypatch):
    write_prompt(tmp_path, version="1.1", name="x", text="text")
    (tmp_path / "prompt_v1.1.yaml").rename(tmp_path / "prompt_v1.0.yaml")
    monkeypatch.setenv("TRADINGAGENTS_PROMPTS_DIR", str(tmp_path))

    with pytest.raises(PromptError, match="version"):
        load_prompt("x")


@pytest.mark.unit
def test_an_unknown_prompt_is_rejected():
    with pytest.raises(PromptError, match="unknown prompt"):
        load_prompt("does.not.exist")


@pytest.mark.unit
def test_the_default_prompt_directory_is_the_repository_store():
    assert prompts_dir() == PROMPTS
