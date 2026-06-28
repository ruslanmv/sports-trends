"""High-level upload helpers built on :class:`DatasetClient`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import LOCAL_LAKE_DIR
from ..storage.write_json import write_json
from .dataset_client import DatasetClient


def write_local_partition(records: Any, path_in_repo: str, local_dir: Path | None = None) -> Path:
    """Stage a JSON partition locally before upload."""
    base = Path(local_dir or LOCAL_LAKE_DIR)
    return write_json(base / path_in_repo, records)


def upload_partition(
    records: Any,
    path_in_repo: str,
    client: DatasetClient | None = None,
) -> dict[str, Any]:
    """Stage ``records`` locally then upload (or dry-run) the partition."""
    client = client or DatasetClient()
    local_path = write_local_partition(records, path_in_repo, client.local_dir)
    result = client.upload_file(local_path, path_in_repo)
    result["records"] = len(records) if hasattr(records, "__len__") else None
    return result


# Back-compat alias for the original placeholder name.
def upload_placeholder(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"status": "noop"}
