import json
from pathlib import Path


def test_schemas_are_valid_json():
    for path in Path("src/sports_trends/schemas").glob("*.json"):
        json.loads(path.read_text())
