from pathlib import Path
import shutil
from datetime import datetime, timezone


def archive_file(path: str | Path, archive_dir: str | Path = "generated/reports/archive") -> Path:
    source = Path(path)
    target_dir = Path(archive_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = target_dir / f"{source.stem}-{stamp}{source.suffix}"
    shutil.copy2(source, target)
    return target
