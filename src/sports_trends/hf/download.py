"""Download helpers for the dataset repo (dry-run safe)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import LOCAL_LAKE_DIR
from ..logging_config import get_logger
from .dataset_client import DatasetClient

logger = get_logger(__name__)


def download_partition(path_in_repo: str, client: DatasetClient | None = None, default: Any = None) -> Any:
    """Return a partition's contents, preferring the local mirror in dry-run."""
    client = client or DatasetClient()
    local_mirror = Path(client.local_dir) / path_in_repo
    if client.dry_run or local_mirror.exists():
        if local_mirror.exists():
            return json.loads(local_mirror.read_text(encoding="utf-8"))
        logger.info("[dry-run] no local mirror for %s; returning default", path_in_repo)
        return default

    from huggingface_hub import hf_hub_download  # lazy

    fp = hf_hub_download(
        repo_id=client.repo_id, repo_type="dataset", filename=path_in_repo, token=client.token
    )
    return json.loads(Path(fp).read_text(encoding="utf-8"))
