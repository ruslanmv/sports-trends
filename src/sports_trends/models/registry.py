"""Model artifact upload + production registry for the HF model repo.

Mirrors the dataset client's dry-run behaviour: with an HF token it pushes
artifacts to ``HF_MODEL_REPO`` under ``<sport>/latest/`` and updates the
registry files; without a token it stages everything to the local model dir.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import HF_MODEL_REPO, HF_TOKEN, LOCAL_LAKE_DIR
from ..logging_config import get_logger

logger = get_logger(__name__)

LOCAL_MODELS_DIR = Path(LOCAL_LAKE_DIR).parent / ".models"


class ModelRegistry:
    def __init__(
        self,
        repo_id: str = HF_MODEL_REPO,
        token: str | None = None,
        dry_run: bool | None = None,
        local_dir: Path | None = None,
    ) -> None:
        self.repo_id = repo_id
        self.token = token if token is not None else HF_TOKEN
        self.dry_run = (not self.token) if dry_run is None else dry_run
        self.local_dir = Path(local_dir or LOCAL_MODELS_DIR)
        self._api = None
        self._ensured = False

    @property
    def mode(self) -> str:
        return "dry-run" if self.dry_run else "live"

    def _hf_api(self):
        if self._api is None:
            from huggingface_hub import HfApi
            self._api = HfApi(token=self.token)
        return self._api

    def _upload(self, local_path: Path, path_in_repo: str) -> None:
        if self.dry_run:
            logger.info("[dry-run] would upload %s -> %s/%s", local_path, self.repo_id, path_in_repo)
            mirror = self.local_dir / path_in_repo
            mirror.parent.mkdir(parents=True, exist_ok=True)
            if local_path.resolve() != mirror.resolve():
                mirror.write_bytes(local_path.read_bytes())
            return
        if not self._ensured:
            self._hf_api().create_repo(self.repo_id, repo_type="model", exist_ok=True, token=self.token)
            self._ensured = True
        self._hf_api().upload_file(
            path_or_fileobj=str(local_path), path_in_repo=path_in_repo,
            repo_id=self.repo_id, repo_type="model", token=self.token,
        )

    def publish(self, sport: str, artifact_dir: Path, version: str, metrics: dict[str, Any]) -> dict[str, Any]:
        """Upload every file in ``artifact_dir`` to ``<sport>/latest/`` and register it."""
        artifact_dir = Path(artifact_dir)
        uploaded = []
        for fp in sorted(artifact_dir.iterdir()):
            if fp.is_file():
                self._upload(fp, f"{sport}/latest/{fp.name}")
                uploaded.append(fp.name)
        self.update_registry(sport, version, metrics)
        return {"mode": self.mode, "sport": sport, "version": version, "files": uploaded}

    def update_registry(self, sport: str, version: str, metrics: dict[str, Any]) -> None:
        reg_path = self.local_dir / "registry" / "latest_versions.json"
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        registry = {}
        if reg_path.exists():
            registry = json.loads(reg_path.read_text())
        registry[sport] = {
            "version": version,
            "path": f"{sport}/latest/",
            "updated": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
        }
        reg_path.write_text(json.dumps(registry, indent=2))
        self._upload(reg_path, "registry/latest_versions.json")


def model_card(sport: str, version: str, metrics: dict[str, Any]) -> str:
    return f"""---
tags: [sports-prediction, {sport}, baseline]
license: mit
---

# sports-trends · {sport} baseline ({version})

Baseline scikit-learn classifier for **{sport}** match outcomes, part of
**Ruslan Magana Sports Intelligence** (`sports-trends`).

## Metrics
```json
{json.dumps(metrics, indent=2)}
```

Predictions are informational only and are **not betting advice**.
"""
