"""Dataset manifest construction and persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import (
    HF_DATASET_REPO,
    MANIFEST_PATH,
    PRODUCT_NAME,
    SITE_BASE_URL,
    SUPPORTED_SPORTS,
    TECHNICAL_NAME,
)
from ..storage.read_json import read_json
from ..storage.write_json import write_json


def build_manifest(
    *,
    sports: tuple[str, ...] | list[str] = SUPPORTED_SPORTS,
    duplicates: int = 0,
    schema_errors: int = 0,
    leakage_errors: int = 0,
    layers: dict[str, bool] | None = None,
) -> dict[str, Any]:
    """Build the dataset manifest dict (matches the spec example)."""
    now = datetime.now(timezone.utc)
    return {
        "dataset_name": HF_DATASET_REPO,
        "technical_name": TECHNICAL_NAME,
        "product_name": PRODUCT_NAME,
        "version": now.strftime("%Y.%m.%d.%H%M"),
        "last_updated": now.isoformat(),
        "website_url": SITE_BASE_URL,
        "sports": list(sports),
        "layers": layers or {"raw": True, "bronze": True, "silver": True, "gold": True},
        "quality": {
            "duplicates": duplicates,
            "schema_errors": schema_errors,
            "leakage_errors": leakage_errors,
        },
    }


def write_manifest(manifest: dict[str, Any], path: Path | str = MANIFEST_PATH) -> Path:
    return write_json(path, manifest)


def load_manifest(path: Path | str = MANIFEST_PATH) -> dict[str, Any]:
    return read_json(path, default={})
