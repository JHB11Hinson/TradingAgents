"""Deterministic input and decision guardrails (D1-REQ-SAFE-001/002/003).

The package is intentionally free of model calls and network access. Callers
use the instruction scrubber at the retrieved-text and tool-result seams, the
free-text decision contract in the Portfolio Manager fallback, and the position
ceiling on the authoritative decision.
"""

from .instructions import ScrubResult, scrub_untrusted
from .positions import DEFAULT_MAX_POSITION_PCT

__all__ = ["DEFAULT_MAX_POSITION_PCT", "ScrubResult", "scrub_untrusted"]
