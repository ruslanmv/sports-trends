"""Central configuration for sports-trends.

All settings are read from environment variables so the same code runs in
local development (with fallback mock data) and in GitHub Actions (with real
API keys and an ``HF_TOKEN``). Importing this module never raises, and running
``python -m sports_trends.config`` prints a readable, secret-safe summary.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# Repository layout -----------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "assets" / "data" / "sports"
LOCAL_LAKE_DIR = Path(_env("SPORTS_LOCAL_LAKE", str(REPO_ROOT / ".data_lake")))
MANIFEST_PATH = LOCAL_LAKE_DIR / "registry" / "dataset_manifest.json"

# Product identity ------------------------------------------------------------
PRODUCT_NAME = _env("SPORTS_PRODUCT_NAME", "Ruslan Magana Sports Intelligence")
TECHNICAL_NAME = _env("SPORTS_TECHNICAL_NAME", "sports-trends")
SITE_BASE_URL = _env("SPORTS_SITE_BASE_URL", "https://ruslanmv.com/sports/")
HEADLINE = "Tomorrow’s Biggest Games"
TAGLINE = "AI predictions, live results, and trending games updated every 30 minutes."

# Hugging Face ----------------------------------------------------------------
HF_TOKEN = _env("HF_TOKEN")
FOOTBALL_DATA_TOKEN = _env("FOOTBALL_DATA_TOKEN")  # World Cup free provider (optional)
HF_DATASET_REPO = _env("HF_DATASET_REPO", "ruslanmv/sports-trends-dataset")
HF_MODEL_REPO = _env("HF_MODEL_REPO", "ruslanmv/sports-trends-models")

# Pipeline knobs --------------------------------------------------------------
UPDATE_CYCLE_MINUTES = int(_env("SPORTS_UPDATE_CYCLE_MINUTES", "30"))
SUPPORTED_SPORTS = ("football", "basketball", "tennis", "cricket", "baseball", "esports")

# API keys (one per provider; absence triggers fallback mock data) ------------
API_KEYS = {
    "default": _env("SPORTS_API_KEY"),
    "football": _env("SPORTS_API_FOOTBALL_KEY"),
    "basketball": _env("SPORTS_BASKETBALL_API_KEY"),
    "tennis": _env("SPORTS_TENNIS_API_KEY"),
    "cricket": _env("SPORTS_CRICKET_API_KEY"),
}


def api_key_for(sport: str) -> str:
    """Return the configured API key for ``sport`` or the shared default."""
    return API_KEYS.get(sport) or API_KEYS.get("default", "")


def has_hf_token() -> bool:
    return bool(HF_TOKEN)


@dataclass(slots=True)
class Settings:
    """Snapshot of the active configuration (secret-safe for printing)."""

    product_name: str = PRODUCT_NAME
    technical_name: str = TECHNICAL_NAME
    site_base_url: str = SITE_BASE_URL
    hf_dataset_repo: str = HF_DATASET_REPO
    hf_model_repo: str = HF_MODEL_REPO
    update_cycle_minutes: int = UPDATE_CYCLE_MINUTES
    supported_sports: tuple[str, ...] = SUPPORTED_SPORTS
    hf_token_present: bool = field(default_factory=has_hf_token)
    api_keys_present: dict[str, bool] = field(
        default_factory=lambda: {k: bool(v) for k, v in API_KEYS.items()}
    )

    def to_dict(self) -> dict:
        return asdict(self)


def get_settings() -> Settings:
    return Settings()


def main() -> None:
    print(json.dumps(get_settings().to_dict(), indent=2, default=list))


if __name__ == "__main__":
    main()
