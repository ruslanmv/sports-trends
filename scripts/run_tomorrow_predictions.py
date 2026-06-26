from ruslan_sports.ingestion.fetch_tomorrow_matches import fetch_tomorrow_matches
from ruslan_sports.predictions.generate_predictions import generate_predictions
from ruslan_sports.ranking.rank_top_matches import rank_top_matches
from ruslan_sports.storage.write_json import write_json


def main() -> None:
    matches = fetch_tomorrow_matches()
    predictions = generate_predictions(matches)
    ranked = rank_top_matches(predictions)
    write_json("assets/data/sports/tomorrow.json", {"matches": ranked})
    print("Updated assets/data/sports/tomorrow.json")


if __name__ == "__main__":
    main()
