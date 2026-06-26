"""Placeholder implementation for `read_json`."""

from __future__ import annotations

from typing import Any

def read_json(*args: Any, **kwargs: Any) -> Any:
    """Return a safe placeholder until provider-specific logic is implemented."""
    if args or kwargs:
        return {"args": list(args), "kwargs": kwargs}
    return []
