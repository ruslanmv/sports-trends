import argparse
from ruslan_sports.ingestion.fetch_live_results import fetch_live_results
from ruslan_sports.ingestion.fetch_tomorrow_matches import fetch_tomorrow_matches
from ruslan_sports.ranking.rank_top_matches import rank_top_matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Ruslan Sports Intelligence CLI")
    parser.add_argument("command", choices=["live", "tomorrow", "rank"])
    args = parser.parse_args()
    if args.command == "live":
        fetch_live_results()
    elif args.command == "tomorrow":
        fetch_tomorrow_matches()
    elif args.command == "rank":
        rank_top_matches([])


if __name__ == "__main__":
    main()
