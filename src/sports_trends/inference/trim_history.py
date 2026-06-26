"""Placeholder implementation for `trim_history`."""

from __future__ import annotations

from typing import Any

def trim_history(*args: Any, **kwargs: Any) -> Any:
    """Return a safe placeholder until provider-specific logic is implemented."""
    if args or kwargs:
        return {"args": list(args), "kwargs": kwargs}
    return []
