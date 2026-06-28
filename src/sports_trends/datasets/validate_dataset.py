"""Validate the small public frontend JSON files against the JSON schemas."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..config import DATA_DIR

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"

# Map frontend files to the schema that validates each match/record.
RECORD_SCHEMAS = {
    "tomorrow.json": "match.schema.json",
    "today.json": "match.schema.json",
    "live.json": "live-result.schema.json",
    "predictions.json": "prediction.schema.json",
    "trending.json": "trending.schema.json",
}


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / name).read_text())


def validate_frontend_json(data_dir: Path | str = DATA_DIR) -> dict[str, Any]:
    """Return a schema-validation report for the public JSON files."""
    try:
        from jsonschema import Draft7Validator
    except ImportError:  # pragma: no cover
        return {"skipped": "jsonschema not installed", "schema_errors": 0}

    data_dir = Path(data_dir)
    errors: list[str] = []
    checked = 0
    for filename, schema_name in RECORD_SCHEMAS.items():
        path = data_dir / filename
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        records = payload.get("matches", payload if isinstance(payload, list) else [])
        validator = Draft7Validator(_load_schema(schema_name))
        for rec in records:
            checked += 1
            for err in validator.iter_errors(rec):
                errors.append(f"{filename}: {err.message}")

    return {"files": list(RECORD_SCHEMAS), "records_checked": checked,
            "schema_errors": len(errors), "errors": errors[:25], "passed": not errors}
