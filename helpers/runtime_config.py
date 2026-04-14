from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_RUNTIME_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "runtime.yaml"


def load_runtime_config(config_path: Path | None = None) -> dict[str, Any]:
    path = (config_path or DEFAULT_RUNTIME_CONFIG_PATH).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"runtime config not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("runtime config 必须是 YAML object")
    return data


def resolve_lane_item_limits(config: dict[str, Any]) -> dict[str, int]:
    selection = config.get("selection") or {}
    per_lane_limits = selection.get("per_lane_limits") or {}
    if not isinstance(per_lane_limits, dict):
        raise ValueError("selection.per_lane_limits 必须是 object")
    result: dict[str, int] = {}
    for lane, value in per_lane_limits.items():
        if isinstance(lane, str) and isinstance(value, int) and value > 0:
            result[lane] = value
    return result


def resolve_lane_paragraph_targets(config: dict[str, Any]) -> dict[str, dict[str, int]]:
    reader_facing = config.get("reader_facing") or {}
    targets = reader_facing.get("lane_paragraph_targets") or {}
    if not isinstance(targets, dict):
        raise ValueError("reader_facing.lane_paragraph_targets 必须是 object")
    normalized: dict[str, dict[str, int]] = {}
    for lane, payload in targets.items():
        if not isinstance(lane, str) or not isinstance(payload, dict):
            continue
        min_paragraphs = payload.get("min_paragraphs")
        max_paragraphs = payload.get("max_paragraphs")
        if isinstance(min_paragraphs, int) and isinstance(max_paragraphs, int):
            normalized[lane] = {
                "min_paragraphs": min_paragraphs,
                "max_paragraphs": max_paragraphs,
            }
    return normalized
