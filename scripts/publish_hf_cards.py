#!/usr/bin/env python3
"""Publish the Hugging Face model & dataset cards (README.md) to their repos.

Cards live (version-controlled) under ``huggingface/<repo>/README.md`` and are
pushed to the matching HF repo:

  * huggingface/sports-trends-models/README.md   -> HF_MODEL_REPO   (repo_type=model)
  * huggingface/sports-trends-dataset/README.md  -> HF_DATASET_REPO (repo_type=dataset)

Dual-mode, like the rest of the project:

  * live    — when ``HF_TOKEN`` is set, uploads the README to each repo.
  * dry-run — without a token (or ``--dry-run``), validates the cards and logs
              what *would* be uploaded. Nothing is sent.

Usage:
    python scripts/publish_hf_cards.py            # live if HF_TOKEN set, else dry-run
    python scripts/publish_hf_cards.py --dry-run  # never upload
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sports_trends.config import HF_DATASET_REPO, HF_MODEL_REPO, HF_TOKEN  # noqa: E402
from sports_trends.logging_config import get_logger  # noqa: E402

logger = get_logger(__name__)

CARDS = [
    ("huggingface/sports-trends-models/README.md", HF_MODEL_REPO, "model"),
    ("huggingface/sports-trends-dataset/README.md", HF_DATASET_REPO, "dataset"),
]


def _validate_front_matter(text: str, rel: str) -> None:
    """Cheap sanity check: a card must open with a YAML front-matter block."""
    if not text.startswith("---"):
        raise ValueError(f"{rel}: missing YAML front-matter (must start with '---').")
    if text.count("---") < 2:
        raise ValueError(f"{rel}: unterminated YAML front-matter block.")
    if "license:" not in text.split("---", 2)[1]:
        raise ValueError(f"{rel}: front-matter is missing a 'license:' field.")


def publish(dry_run: bool) -> list[dict]:
    results: list[dict] = []
    api = None
    if not dry_run:
        from huggingface_hub import HfApi  # imported lazily

        api = HfApi(token=HF_TOKEN)

    for rel, repo_id, repo_type in CARDS:
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f"Card not found: {rel}")
        text = path.read_text(encoding="utf-8")
        _validate_front_matter(text, rel)

        if dry_run:
            logger.info("[dry-run] would upload %s -> %s/%s (README.md)", rel, repo_type, repo_id)
            results.append({"status": "dry-run", "repo_id": repo_id, "repo_type": repo_type,
                            "card": rel, "bytes": len(text.encode("utf-8"))})
            continue

        api.create_repo(repo_id, repo_type=repo_type, exist_ok=True, token=HF_TOKEN)
        api.upload_file(
            path_or_fileobj=str(path),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type=repo_type,
            token=HF_TOKEN,
            commit_message="Update card via publish_hf_cards.py",
        )
        logger.info("uploaded %s -> %s/%s (README.md)", rel, repo_type, repo_id)
        results.append({"status": "uploaded", "repo_id": repo_id, "repo_type": repo_type, "card": rel})

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish HF model & dataset cards.")
    parser.add_argument("--dry-run", action="store_true", help="Validate + log only; never upload.")
    args = parser.parse_args()

    dry_run = args.dry_run or not HF_TOKEN
    mode = "dry-run" if dry_run else "live"
    logger.info("Publishing HF cards (mode=%s)", mode)

    results = publish(dry_run=dry_run)
    print(json.dumps({"mode": mode, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
