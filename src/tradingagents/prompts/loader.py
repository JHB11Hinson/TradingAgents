"""Versioned runtime prompt store (D1-REQ-GOV-012).

Runtime prompts live in `prompts/prompt_v<major>.<minor>.yaml`. A prompt change
adds a new version file; an existing file is never edited in place. Every entry
carries a SHA-256 over its exact text, checked on read, so a silent edit or a
corrupt store fails closed instead of reaching a model.

`TRADINGAGENTS_PROMPTS_DIR` points the loader at another store (tests use it).
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

_FILENAME = re.compile(r"^prompt_v(?P<major>\d+)\.(?P<minor>\d+)\.yaml$")
ALGORITHM = "sha256"


class PromptError(ValueError):
    """The prompt store is missing, malformed, or has drifted from its checksum."""


@dataclass(frozen=True)
class Prompt:
    """One versioned prompt."""

    name: str
    version: str
    text: str
    description: str = ""


def prompts_dir() -> Path:
    """Return the prompt store directory, honouring the environment override."""
    override = os.environ.get("TRADINGAGENTS_PROMPTS_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[3] / "prompts"


def checksum_text(text: str) -> str:
    """Return the SHA-256 of the exact UTF-8 prompt text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_version(path: Path) -> tuple[int, int]:
    """Parse `prompt_vX.Y.yaml` into an orderable `(major, minor)` pair."""
    match = _FILENAME.match(path.name)
    if not match:
        raise PromptError(f"{path.name} is not a prompt_vX.Y.yaml file")
    return int(match.group("major")), int(match.group("minor"))


def _version_string(path: Path) -> str:
    major, minor = parse_version(path)
    return f"{major}.{minor}"


def prompt_files(directory: Path | None = None) -> list[Path]:
    """List every version file in ascending version order."""
    base = directory or prompts_dir()
    if not base.is_dir():
        raise PromptError(f"prompt directory {base} does not exist")
    files = sorted(
        (path for path in base.glob("prompt_v*.yaml") if path.is_file()),
        key=parse_version,
    )
    if not files:
        raise PromptError(f"no prompt_vX.Y.yaml files in {base}")
    return files


def _read_file(path: Path) -> dict[str, Prompt]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PromptError(f"{path.name} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise PromptError(f"{path.name} must contain a mapping")

    version = str(data.get("version", "")).strip()
    expected_version = _version_string(path)
    if version != expected_version:
        raise PromptError(
            f"{path.name} declares version {version!r}, expected {expected_version}"
        )
    if data.get("checksum_algorithm", ALGORITHM) != ALGORITHM:
        raise PromptError(f"{path.name} must use the {ALGORITHM} checksum")

    raw_prompts = data.get("prompts")
    if not isinstance(raw_prompts, dict) or not raw_prompts:
        raise PromptError(f"{path.name} has no prompts mapping")

    prompts: dict[str, Prompt] = {}
    for name, entry in raw_prompts.items():
        if not isinstance(name, str) or not name.strip():
            raise PromptError(f"{path.name} has an empty prompt name")
        if not isinstance(entry, dict):
            raise PromptError(f"{path.name}:{name} must be a mapping")
        text = entry.get("text")
        if not isinstance(text, str) or not text.strip():
            raise PromptError(f"{path.name}:{name} has no text")
        recorded = entry.get("sha256")
        actual = checksum_text(text)
        if not isinstance(recorded, str) or recorded.lower() != actual:
            raise PromptError(
                f"{path.name}:{name} checksum mismatch "
                f"(recorded {recorded!r}, computed {actual})"
            )
        prompts[name] = Prompt(
            name=name,
            version=version,
            text=text,
            description=str(entry.get("description", "")),
        )
    return prompts


def load_all(version: str | None = None) -> dict[str, Prompt]:
    """Load every prompt, or only one version when pinned.

    With no version, a name declared by more than one file resolves to the
    highest version. A prompt change therefore lands in a new file and takes
    effect without editing the older one.
    """
    files = prompt_files()
    if version is not None:
        files = [path for path in files if _version_string(path) == version]
        if not files:
            raise PromptError(f"prompt version {version} not found")

    prompts: dict[str, Prompt] = {}
    for path in files:
        prompts.update(_read_file(path))
    return prompts


def load_prompt(name: str, version: str | None = None) -> Prompt:
    """Load one prompt, pinned to a version or resolved to the highest."""
    prompts = load_all(version=version)
    try:
        return prompts[name]
    except KeyError:
        suffix = f" in version {version}" if version else ""
        raise PromptError(f"unknown prompt {name!r}{suffix}") from None
