"""Thin wrapper around huggingface_hub for the dataset repo.

Operates in two modes:
  * live    — when an HF token is present, uploads to ``HF_DATASET_REPO``.
  * dry-run — when no token (or ``dry_run=True``), writes to a local lake
              directory and logs what *would* be uploaded. Nothing is sent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config import HF_DATASET_REPO, HF_TOKEN, LOCAL_LAKE_DIR
from ..logging_config import get_logger

logger = get_logger(__name__)


class DatasetClient:
    def __init__(
        self,
        repo_id: str = HF_DATASET_REPO,
        token: str | None = None,
        dry_run: bool | None = None,
        local_dir: Path | None = None,
    ) -> None:
        self.repo_id = repo_id
        self.token = token if token is not None else HF_TOKEN
        # dry-run unless explicitly disabled AND a token exists
        self.dry_run = (not self.token) if dry_run is None else dry_run
        self.local_dir = Path(local_dir or LOCAL_LAKE_DIR)
        self._api = None

    @property
    def mode(self) -> str:
        return "dry-run" if self.dry_run else "live"

    def _hf_api(self):
        if self._api is None:
            from huggingface_hub import HfApi  # imported lazily

            self._api = HfApi(token=self.token)
        return self._api

    def ensure_repo(self) -> None:
        if self.dry_run:
            logger.info("[dry-run] would ensure dataset repo %s exists", self.repo_id)
            return
        self._hf_api().create_repo(
            self.repo_id, repo_type="dataset", exist_ok=True, token=self.token
        )

    def upload_file(self, local_path: str | Path, path_in_repo: str) -> dict[str, Any]:
        local_path = Path(local_path)
        if self.dry_run:
            logger.info("[dry-run] would upload %s -> %s/%s", local_path, self.repo_id, path_in_repo)
            mirror = self.local_dir / path_in_repo
            mirror.parent.mkdir(parents=True, exist_ok=True)
            if local_path.resolve() != mirror.resolve():
                mirror.write_bytes(local_path.read_bytes())
            return {"status": "dry-run", "path_in_repo": path_in_repo, "local_mirror": str(mirror)}

        self.ensure_repo()
        self._hf_api().upload_file(
            path_or_fileobj=str(local_path),
            path_in_repo=path_in_repo,
            repo_id=self.repo_id,
            repo_type="dataset",
            token=self.token,
        )
        return {"status": "uploaded", "path_in_repo": path_in_repo}
