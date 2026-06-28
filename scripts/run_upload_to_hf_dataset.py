#!/usr/bin/env python3
"""Upload current raw partitions to the Hugging Face dataset repo.

Fetches the (mock or live) slate, normalizes it, stages raw JSON partitions per
sport, uploads them (dry-run when no HF_TOKEN), and refreshes the manifest.

Usage:
    python scripts/run_upload_to_hf_dataset.py            # auto (dry-run if no token)
    python scripts/run_upload_to_hf_dataset.py --dry-run  # force dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.config import SUPPORTED_SPORTS
from sports_trends.hf.dataset_client import DatasetClient
from sports_trends.hf.manifest import build_manifest, write_manifest
from sports_trends.hf.partitions import raw_partition, registry_path
from sports_trends.hf.upload import upload_partition
from sports_trends.ingestion.normalize_matches import find_duplicate_ids, normalize_matches
from sports_trends.logging_config import get_logger
from sports_trends.providers import get_provider

logger = get_logger("run_upload_to_hf_dataset")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Never contact Hugging Face.")
    args = parser.parse_args()

    client = DatasetClient(dry_run=True if args.dry_run else None)
    logger.info("Dataset upload starting in %s mode (repo=%s)", client.mode, client.repo_id)

    day = datetime.now(timezone.utc).date().isoformat()
    all_matches: list[dict] = []
    results = []

    for sport in SUPPORTED_SPORTS:
        provider = get_provider(sport)
        raw = provider.fetch_tomorrow_matches() + provider.fetch_today_matches()
        if not raw:
            continue
        matches = normalize_matches(raw, provider=type(provider).__name__)
        all_matches.extend(matches)
        path = raw_partition(sport, provider.mode, day)
        res = upload_partition(matches, path, client=client)
        logger.info("  %-10s %s (%s records)", sport, res["status"], res.get("records"))
        results.append(res)

    duplicates = find_duplicate_ids(all_matches)
    manifest = build_manifest(duplicates=len(duplicates))
    manifest_path = write_manifest(manifest)
    logger.info("Manifest written to %s (version %s)", manifest_path, manifest["version"])

    # Publish the manifest into the dataset repo's registry/ folder too.
    client.upload_file(manifest_path, registry_path("dataset_manifest.json"))

    print(json.dumps({
        "mode": client.mode,
        "partitions": len(results),
        "matches": len(all_matches),
        "duplicates": len(duplicates),
        "manifest": str(manifest_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
