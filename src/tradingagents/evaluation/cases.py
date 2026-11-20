"""The fixed evaluation set (D1-REQ-EVAL-001).

A fixed set is a JSON document with a version and a non-empty list of cases.
Each case names a ticker, a trade date and the analysts to run, so the same
analysis can be replayed on any machine. The loader is strict on purpose: a
typo in a case must fail loudly instead of silently shrinking the set, because
a smaller set makes every threshold easier to pass.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

ANALYSTS: tuple[str, ...] = ("market", "social", "news", "fundamentals")
SUPPORTED_VERSION = 1
_CASE_KEYS = {"id", "ticker", "trade_date", "analysts"}


class FixedSetError(ValueError):
    """The fixed set is missing, malformed or internally inconsistent."""


@dataclass(frozen=True)
class EvaluationCase:
    """One analysis to replay."""

    id: str
    ticker: str
    trade_date: str
    analysts: tuple[str, ...] = ANALYSTS


def load_fixed_set(path: str | Path, today: date | None = None) -> tuple[EvaluationCase, ...]:
    """Read and validate a fixed set; ``today`` is injectable for the date check."""
    target = Path(path)
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FixedSetError(f"cannot read the fixed set {target}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise FixedSetError(f"the fixed set {target} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise FixedSetError("the fixed set must be a JSON object")
    version = data.get("version")
    if version != SUPPORTED_VERSION:
        raise FixedSetError(f"unsupported fixed-set version {version!r}; expected {SUPPORTED_VERSION}")

    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise FixedSetError("the fixed set must carry a non-empty 'cases' list")

    now = today or date.today()
    seen: set[str] = set()
    cases = []
    for index, raw in enumerate(raw_cases):
        case = _parse_case(raw, index, now)
        if case.id in seen:
            raise FixedSetError(f"duplicate case id {case.id!r}")
        seen.add(case.id)
        cases.append(case)
    return tuple(cases)


def _parse_case(raw: Any, index: int, today: date) -> EvaluationCase:
    where = f"cases[{index}]"
    if not isinstance(raw, dict):
        raise FixedSetError(f"{where} must be an object")
    unknown = set(raw) - _CASE_KEYS
    if unknown:
        raise FixedSetError(f"{where} has unknown key(s): {', '.join(sorted(unknown))}")

    case_id = raw.get("id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise FixedSetError(f"{where}.id must be a non-empty string")

    ticker = raw.get("ticker")
    if not isinstance(ticker, str) or not ticker.strip():
        raise FixedSetError(f"{where}.ticker must be a non-empty string")

    trade_date = _parse_date(raw.get("trade_date"), f"{where}.trade_date")
    if trade_date > today:
        raise FixedSetError(f"{where}.trade_date {trade_date} is in the future")

    raw_analysts = raw.get("analysts", list(ANALYSTS))
    if not isinstance(raw_analysts, list) or not raw_analysts:
        raise FixedSetError(f"{where}.analysts must be a non-empty list")
    analysts = []
    for name in raw_analysts:
        if name not in ANALYSTS:
            raise FixedSetError(
                f"{where}.analysts has unknown analyst {name!r}; expected one of {', '.join(ANALYSTS)}"
            )
        if name in analysts:
            raise FixedSetError(f"{where}.analysts repeats {name!r}")
        analysts.append(name)

    return EvaluationCase(
        id=case_id.strip(),
        ticker=ticker.strip(),
        trade_date=trade_date.isoformat(),
        analysts=tuple(analysts),
    )


def _parse_date(value: Any, where: str) -> date:
    if not isinstance(value, str):
        raise FixedSetError(f"{where} must be a YYYY-MM-DD string")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise FixedSetError(f"{where} is not a valid YYYY-MM-DD date: {value!r}") from exc
    return parsed
