from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class SportsConfig:
    output_dir: Path = Path(os.getenv("SPORTS_OUTPUT_DIR", "assets/data/sports"))
    timezone: str = os.getenv("SPORTS_TIMEZONE", "UTC")
    site_base_url: str = os.getenv("SPORTS_SITE_BASE_URL", "https://ruslanmv.com/sports/")
    update_cycle_minutes: int = int(os.getenv("SPORTS_UPDATE_CYCLE_MINUTES", "30"))


def get_config() -> SportsConfig:
    return SportsConfig()
