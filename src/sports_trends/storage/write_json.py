"""Atomic JSON writer used for the data lake and the public frontend files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: str | Path, data: Any, *, indent: int = 2) -> Path:
    """Write ``data`` as UTF-8 JSON, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=indent, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    return path
