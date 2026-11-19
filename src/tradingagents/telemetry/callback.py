"""Attribute model usage to the span of the step that made the call (OBS-002)."""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from .spans import current_span


class TelemetryCallback(BaseCallbackHandler):
    """Read ``usage_metadata`` from each finished call and add it to its span."""

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        record = current_span()
        if record is None:
            return
        try:
            generation = response.generations[0][0]
        except (IndexError, TypeError):
            return
        message = getattr(generation, "message", None)
        usage = getattr(message, "usage_metadata", None)
        if not isinstance(usage, dict):
            return
        record.add_usage(
            int(usage.get("input_tokens", 0) or 0),
            int(usage.get("output_tokens", 0) or 0),
            model=_model_name(response, message),
        )


def _model_name(response: LLMResult, message: object) -> str | None:
    metadata = getattr(message, "response_metadata", None)
    if isinstance(metadata, dict):
        name = metadata.get("model_name") or metadata.get("model")
        if name:
            return str(name)
    llm_output = getattr(response, "llm_output", None)
    if isinstance(llm_output, dict):
        name = llm_output.get("model_name")
        if name:
            return str(name)
    return None
