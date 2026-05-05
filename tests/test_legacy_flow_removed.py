from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_FLOW = "helpers/" + "run_daily_" + "report_flow.py"


def _active_text_files() -> list[Path]:
    skipped_dirs = {".git", ".pytest_cache", "__pycache__", "docs", "tests"}
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(REPO_ROOT).parts
        if any(part in skipped_dirs for part in relative_parts):
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files.append(path)
    return files


def test_legacy_flow_file_is_removed() -> None:
    assert not (REPO_ROOT / LEGACY_FLOW).exists()


def test_active_instruction_surfaces_do_not_reference_legacy_flow() -> None:
    offenders = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in _active_text_files()
        if LEGACY_FLOW in path.read_text(encoding="utf-8")
    ]

    assert offenders == []
