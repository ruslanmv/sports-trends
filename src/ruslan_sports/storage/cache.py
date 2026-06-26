from pathlib import Path


CACHE_DIR = Path(".cache/sports")


def cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe = key.replace("/", "_").replace(":", "_")
    return CACHE_DIR / f"{safe}.json"
