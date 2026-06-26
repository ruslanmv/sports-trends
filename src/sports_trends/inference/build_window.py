"""Placeholder implementation for `build_inference_window`."""

from __future__ import annotations

from typing import Any

def build_inference_window(*args: Any, **kwargs: Any) -> Any:
    """Return a safe placeholder until provider-specific logic is implemented."""
    if args or kwargs:
        return {"args": list(args), "kwargs": kwargs}
    return []
