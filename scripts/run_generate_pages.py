from pathlib import Path


def main() -> None:
    Path("generated/pages/sports").mkdir(parents=True, exist_ok=True)
    print("TODO: generate programmatic sports pages into generated/pages/sports")


if __name__ == "__main__":
    main()
