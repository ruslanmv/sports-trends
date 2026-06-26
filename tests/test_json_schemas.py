import json
from pathlib import Path


def test_schemas_are_valid_json():
    for path in Path("src/ruslan_sports/schemas").glob("*.json"):
        json.loads(path.read_text())
