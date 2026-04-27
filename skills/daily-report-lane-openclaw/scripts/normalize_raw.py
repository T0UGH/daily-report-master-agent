from pathlib import Path

def normalize(raw_dir: Path) -> list[Path]:
    return sorted(path for path in raw_dir.rglob("*") if path.is_file()) if raw_dir.exists() else []
