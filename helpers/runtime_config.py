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


def resolve_lane_worker_config(config: dict[str, Any]) -> dict[str, Any]:
    raw = config.get("lane_workers") or {}
    enabled = bool(raw.get("enabled", False))
    mode = raw.get("mode", "local")
    if mode not in {"local", "subagent"}:
        raise ValueError("lane_workers.mode must be local or subagent")
    agent_first = bool(raw.get("agent_first", False))
    if agent_first and not enabled:
        raise ValueError("lane_workers.agent_first requires lane_workers.enabled=true")
    if agent_first and mode != "subagent":
        raise ValueError("lane_workers.agent_first requires lane_workers.mode=subagent")
    enabled_lanes = raw.get("enabled_lanes") or []
    if not isinstance(enabled_lanes, list) or not all(isinstance(lane, str) for lane in enabled_lanes):
        raise ValueError("lane_workers.enabled_lanes must be list[str]")
    forbid_legacy_fallback_for = raw.get("forbid_legacy_fallback_for") or []
    if not isinstance(forbid_legacy_fallback_for, list) or not all(
        isinstance(lane, str) for lane in forbid_legacy_fallback_for
    ):
        raise ValueError("lane_workers.forbid_legacy_fallback_for must be list[str]")
    github_ai_projects = raw.get("github_ai_projects") or {}
    if not isinstance(github_ai_projects, dict):
        raise ValueError("lane_workers.github_ai_projects must be object")
    return {
        "enabled": enabled,
        "mode": mode,
        "agent_first": agent_first,
        "enabled_lanes": enabled_lanes,
        "forbid_legacy_fallback_for": forbid_legacy_fallback_for,
        "github_ai_projects": github_ai_projects,
    }


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
