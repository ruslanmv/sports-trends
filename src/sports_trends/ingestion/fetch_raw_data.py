"""Placeholder implementation for `fetch_raw_data`."""

from __future__ import annotations

from typing import Any

def fetch_raw_data(*args: Any, **kwargs: Any) -> Any:
    """Return a safe placeholder until provider-specific logic is implemented."""
    if args or kwargs:
        return {"args": list(args), "kwargs": kwargs}
    return []
