"""Partition path helpers for the Hugging Face data lake.

Layout (see docs/HF_DATASET_ARCHITECTURE.md):
    raw/<sport>/provider=<p>/date=<YYYY-MM-DD>/fixtures.json
    bronze|silver/<entity>/sport=<sport>/date=<YYYY-MM-DD>/part.parquet
    gold/features/<feature>/sport=<sport>/date=<YYYY-MM-DD>/part.parquet
    gold/inference/tomorrow/date=<YYYY-MM-DD>/<name>.parquet
"""

from __future__ import annotations


def raw_partition(sport: str, provider: str, day: str, filename: str = "fixtures.json") -> str:
    return f"raw/{sport}/provider={provider}/date={day}/{filename}"


def layer_partition(layer: str, entity: str, sport: str, day: str, filename: str = "part.parquet") -> str:
    return f"{layer}/{entity}/sport={sport}/date={day}/{filename}"


def feature_partition(feature: str, sport: str, day: str, filename: str = "part.parquet") -> str:
    return f"gold/features/{feature}/sport={sport}/date={day}/{filename}"


def training_partition(sport: str, filename: str = "train.parquet") -> str:
    return f"gold/training/{sport}/{filename}"


def inference_partition(day: str, filename: str) -> str:
    return f"gold/inference/tomorrow/date={day}/{filename}"


def predictions_partition(sport: str, day: str, filename: str = "predictions.parquet") -> str:
    """Prediction ledger (open rows logged at prediction time)."""
    return f"predictions/{sport}/date={day}/{filename}"


def outcomes_partition(sport: str, day: str, filename: str = "settled.parquet") -> str:
    """Settled outcomes (prediction joined to the real result), gold layer."""
    return f"gold/outcomes/{sport}/date={day}/{filename}"


def registry_path(filename: str) -> str:
    return f"registry/{filename}"


def quality_path(filename: str) -> str:
    return f"quality/{filename}"
