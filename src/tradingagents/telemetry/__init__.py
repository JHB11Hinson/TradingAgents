"""In-process telemetry: the event seam, the run trace and the run manifest.

(D1-REQ-OBS-001/002/003.) Additive to the graph: nodes emit spans, a run writes
two JSON files, and a subscriber failure is a warning rather than a run failure.
"""

from .callback import TelemetryCallback
from .events import SAFE_ATTRIBUTE_KEYS, Telemetry, TelemetryEvent
from .manifest import build_manifest, write_manifest
from .pricing import DEFAULT_PRICING, estimate_cost
from .spans import Span, current_span, current_telemetry, span, telemetry_scope
from .trace import load_trace, write_trace
from .wiring import run_output_dir, write_run_telemetry

__all__ = [
    "DEFAULT_PRICING",
    "SAFE_ATTRIBUTE_KEYS",
    "Span",
    "Telemetry",
    "TelemetryCallback",
    "TelemetryEvent",
    "build_manifest",
    "current_span",
    "current_telemetry",
    "estimate_cost",
    "load_trace",
    "run_output_dir",
    "span",
    "telemetry_scope",
    "write_manifest",
    "write_run_telemetry",
    "write_trace",
]
