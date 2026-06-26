from datetime import datetime, timezone
from ruslan_sports.storage.write_json import write_json


def main() -> None:
    payload = {"last_updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "rankings": []}
    write_json("assets/data/sports/trending.json", payload)
    print("Updated assets/data/sports/trending.json")


if __name__ == "__main__":
    main()
