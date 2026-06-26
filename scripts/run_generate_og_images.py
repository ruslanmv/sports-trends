from pathlib import Path


def main() -> None:
    Path("assets/data/sports/og").mkdir(parents=True, exist_ok=True)
    print("TODO: generate Open Graph images for top matches")


if __name__ == "__main__":
    main()
