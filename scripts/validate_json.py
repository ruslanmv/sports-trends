import json
from pathlib import Path


def main() -> None:
    for path in Path("assets/data/sports").rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    print("All sports JSON files are valid")


if __name__ == "__main__":
    main()
