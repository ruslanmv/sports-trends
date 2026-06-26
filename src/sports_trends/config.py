"""Configuration constants for sports-trends."""

from __future__ import annotations

import os

PRODUCT_NAME = os.getenv("SPORTS_PRODUCT_NAME", "Ruslan Magana Sports Intelligence")
TECHNICAL_NAME = os.getenv("SPORTS_TECHNICAL_NAME", "sports-trends")
SITE_BASE_URL = os.getenv("SPORTS_SITE_BASE_URL", "https://ruslanmv.com/sports/")
HF_DATASET_REPO = os.getenv("HF_DATASET_REPO", "ruslanmv/sports-trends-dataset")
HF_MODEL_REPO = os.getenv("HF_MODEL_REPO", "ruslanmv/sports-trends-models")
UPDATE_CYCLE_MINUTES = int(os.getenv("SPORTS_UPDATE_CYCLE_MINUTES", "30"))
SUPPORTED_SPORTS = ("football", "basketball", "tennis", "cricket", "baseball", "esports")
