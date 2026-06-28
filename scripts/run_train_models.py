#!/usr/bin/env python3
"""Train the sport-optimized models for each sport and publish to the HF model repo.

Each sport uses its own algorithm (see models/model_zoo.py). Publishes to
``ruslanmv/sports-trends-models`` under ``<sport>/latest/`` when HF_TOKEN is set;
otherwise stages artifacts locally (dry-run). Writes a model-registry summary to
``assets/data/sports/models.json`` for the dynamic README and the site.

Usage:
    python scripts/run_train_models.py [--dry-run] [--no-publish]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.config import DATA_DIR
from sports_trends.logging_config import get_logger
from sports_trends.models._train_core import train_sport
from sports_trends.models.model_zoo import SPORT_MODELS
from sports_trends.models.registry import ModelRegistry
from sports_trends.storage.write_json import write_json

logger = get_logger("run_train_models")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-publish", action="store_true")
    args = parser.parse_args()

    registry = ModelRegistry(dry_run=True if args.dry_run else None)
    logger.info("Training sport-optimized models in %s mode (repo=%s)", registry.mode, registry.repo_id)

    results = {}
    for sport, meta in SPORT_MODELS.items():
        res = train_sport(sport, publish=not args.no_publish, registry=registry,
                          out_dir=registry.local_dir / sport / "build")
        results[sport] = {
            "version": res["version"],
            "algo": meta["algo"],
            "model_name": meta["model_name"],
            "task": meta["task"],
            "rationale": meta["rationale"],
            "metrics": res["metrics"],
        }

    summary = {
        "product": "Ruslan Magana Sports Intelligence",
        "model_repo": registry.repo_id,
        "last_trained": datetime.now(timezone.utc).isoformat(),
        "mode": registry.mode,
        "models": results,
    }
    write_json(DATA_DIR / "models.json", summary)
    logger.info("Wrote model registry summary -> %s", DATA_DIR / "models.json")
    print(json.dumps({"mode": registry.mode, "models": {k: v["metrics"]["accuracy"] for k, v in results.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
