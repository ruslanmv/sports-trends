"""Placeholder implementation for `build_manifest`."""

from __future__ import annotations

from typing import Any

def build_manifest(*args: Any, **kwargs: Any) -> Any:
    """Return a safe placeholder until provider-specific logic is implemented."""
    if args or kwargs:
        return {"args": list(args), "kwargs": kwargs}
    return []
