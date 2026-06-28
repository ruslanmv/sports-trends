"""Resolve trained models from the local cache or the HF model repo."""

from __future__ import annotations

from pathlib import Path

from ..config import HF_MODEL_REPO, HF_TOKEN
from ..logging_config import get_logger

logger = get_logger(__name__)


def ensure_model(sport: str, models_root: str | Path = ".models", download: bool | None = None) -> Path | None:
    """Return a local path to ``<sport>/latest/model.pkl``, downloading if needed."""
    models_root = Path(models_root)
    local = models_root / sport / "latest" / "model.pkl"
    if local.exists():
        return local
    build = models_root / sport / "build" / "model.pkl"
    if build.exists():
        return build
    do_download = bool(HF_TOKEN) if download is None else download
    if not do_download:
        return None
    try:
        from huggingface_hub import hf_hub_download
        fp = hf_hub_download(repo_id=HF_MODEL_REPO, repo_type="model",
                             filename=f"{sport}/latest/model.pkl", token=HF_TOKEN)
        return Path(fp)
    except Exception as exc:  # pragma: no cover - network/absent model
        logger.warning("Could not download %s model: %s", sport, exc)
        return None
