from pathlib import Path

def validate_output(output_dir: Path) -> bool:
    return (output_dir / "lane.md").exists() and (output_dir / "lane-meta.json").exists()
