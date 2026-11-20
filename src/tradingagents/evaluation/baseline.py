"""The recorded baseline a fixed-set run is compared against (D1-REQ-COST-001).

The baseline is data, not a constant in code: the number, the price it was
valued at and its provenance travel together, so a later run can be compared
without guessing where 120 000 tokens came from. ``total_tokens`` and
``est_cost_usd`` are **per analysis**; the aggregator scales them by the number
of cases in the set.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_VERSION = 1


class BaselineError(ValueError):
    """The baseline file is missing, malformed or incomplete."""


@dataclass(frozen=True)
class Baseline:
    """The per-analysis reference point recorded for the fixed set."""

    total_tokens: int
    est_cost_usd: float
    usd_per_million_input_tokens: float
    source: str
    recorded_at: str

    def tokens_for(self, cases: int) -> int:
        return self.total_tokens * cases

    def cost_for(self, cases: int) -> float:
        return round(self.est_cost_usd * cases, 8)


def load_baseline(path: str | Path) -> Baseline:
    target = Path(path)
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except OSError as exc:
        raise BaselineError(f"cannot read the baseline {target}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise BaselineError(f"the baseline {target} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise BaselineError("the baseline must be a JSON object")
    if data.get("version") != SUPPORTED_VERSION:
        raise BaselineError(
            f"unsupported baseline version {data.get('version')!r}; expected {SUPPORTED_VERSION}"
        )

    per_analysis = data.get("per_analysis")
    if not isinstance(per_analysis, dict):
        raise BaselineError("the baseline must carry a 'per_analysis' object")
    total_tokens = _positive_int(per_analysis.get("total_tokens"), "per_analysis.total_tokens")
    est_cost_usd = _positive_number(per_analysis.get("est_cost_usd"), "per_analysis.est_cost_usd")
    price = _positive_number(
        data.get("usd_per_million_input_tokens"), "usd_per_million_input_tokens"
    )
    source = data.get("source")
    if not isinstance(source, str) or not source.strip():
        raise BaselineError("the baseline must say where the number came from in 'source'")
    recorded_at = data.get("recorded_at")
    if not isinstance(recorded_at, str) or not recorded_at.strip():
        raise BaselineError("the baseline must carry 'recorded_at'")

    return Baseline(
        total_tokens=total_tokens,
        est_cost_usd=est_cost_usd,
        usd_per_million_input_tokens=price,
        source=source.strip(),
        recorded_at=recorded_at.strip(),
    )


def _positive_int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise BaselineError(f"{where} must be a positive integer")
    return value


def _positive_number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise BaselineError(f"{where} must be a positive number")
    return float(value)
