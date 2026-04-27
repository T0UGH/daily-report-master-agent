from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from helpers.validate_report_output_contract import FIXED_SECTION_TITLES


RAW_CORPUS_MISSING = "blocked_raw_corpus_missing"
GITHUB_AI_PROJECTS_NO_OWN_RAW_CORPUS = "degraded/no_own_raw_corpus"
DEFAULT_GITHUB_AI_PROJECTS_DISCOVERY_QUERIES = [
    "GitHub trending AI {date}",
    "GitHub new AI projects {date}",
    "awesome AI GitHub {date}",
]


def fixed_section_order_from_config(config_path: Path) -> list[str]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("runtime config must be object")
    reader_facing = config.get("reader_facing")
    if not isinstance(reader_facing, dict):
        raise ValueError("reader_facing must be object")
    fixed_section_order = reader_facing.get("fixed_section_order")
    if not isinstance(fixed_section_order, list) or not all(isinstance(lane, str) for lane in fixed_section_order):
        raise ValueError("reader_facing.fixed_section_order must be list[str]")
    return list(fixed_section_order)


def missing_registry_entries(
    fixed_lanes: list[str],
    registry_entries: Mapping[str, Any] | set[str],
) -> list[str]:
    registry_keys = set(registry_entries.keys()) if isinstance(registry_entries, Mapping) else set(registry_entries)
    return [lane for lane in fixed_lanes if lane not in registry_keys]


def require_registry_coverage(
    fixed_lanes: list[str],
    registry_entries: Mapping[str, Any] | set[str],
) -> None:
    missing = missing_registry_entries(fixed_lanes, registry_entries)
    if missing:
        raise ValueError(f"agent-first registry missing fixed lanes: {', '.join(missing)}")


def build_raw_candidates_from_signal_dir(signal_dir: Path, *, snippet_char_limit: int = 2000) -> list[dict[str, Any]]:
    if not signal_dir.is_dir():
        return []
    candidates: list[dict[str, Any]] = []
    for path in sorted(signal_dir.glob("*.md")):
        metadata, markdown = _split_frontmatter(path.read_text(encoding="utf-8"))
        title = _candidate_title(metadata, path)
        source_url = metadata.get("url") or metadata.get("source_url")
        if not isinstance(source_url, str) or not source_url.strip():
            continue
        snippet = _build_source_snippet(metadata, markdown, snippet_char_limit=snippet_char_limit)
        candidates.append(
            {
                "id": _candidate_id(metadata, title),
                "title": title,
                "source_url": source_url,
                "source_snippet": snippet,
                "candidate_source": path.name,
                "raw": {
                    "metadata": metadata,
                    "markdown": markdown,
                },
            }
        )
    return candidates


def build_agent_lane_input_artifact(
    *,
    report_date: str,
    lane_name: str,
    collect_result: dict[str, Any],
    selected_items: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    signals_root = _resolve_signals_root(config)
    signal_dir = signals_root / lane_name / report_date / "signals"
    raw_candidates = build_raw_candidates_from_signal_dir(signal_dir)
    raw_corpus_status = _raw_corpus_status(lane_name=lane_name, raw_candidates=raw_candidates)
    cross_lane_context = _build_cross_lane_context(
        lane_name=lane_name,
        report_date=report_date,
        config=config,
    )
    target_item_count = _target_item_count(lane_name=lane_name, config=config)

    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": report_date,
        "lane": lane_name,
        "timezone": (config.get("runtime") or {}).get("timezone", "Asia/Shanghai"),
        "lane_title": FIXED_SECTION_TITLES.get(lane_name, lane_name),
        "agent_first": True,
        "target_item_count": target_item_count,
        "min_item_count": 1,
        "raw_candidates": raw_candidates,
        "raw_corpus_status": raw_corpus_status,
        "raw_corpus_path": str(signal_dir),
        "recent_history": {"repo_ids": []},
        "cross_lane_context": cross_lane_context,
        "style_contract": {
            "language": "zh-CN",
            "forbidden_phrases": [
                "采集文本",
                "保守看",
                "摘要里能看到",
                "值得看的趋势项目",
                "具体变化见来源",
                "当前可作为",
                "候选继续观察",
                "至少因为",
                "原始趋势片段写到",
            ],
        },
        "collect_context": _collect_lane_context(collect_result=collect_result, lane_name=lane_name),
        "compatibility": {
            "selected_items_snapshot": selected_items,
        },
    }
    return payload


def _resolve_signals_root(config: dict[str, Any]) -> Path:
    raw_path = (config.get("paths") or {}).get("signals_root") or "~/.daily-lane-data/signals"
    return Path(os.path.expandvars(os.path.expanduser(str(raw_path)))).resolve()


def _target_item_count(*, lane_name: str, config: dict[str, Any]) -> int:
    selection = config.get("selection") or {}
    per_lane_limits = selection.get("per_lane_limits") or {}
    default_limit = selection.get("default_per_lane_limit", 10)
    value = per_lane_limits.get(lane_name) if isinstance(per_lane_limits, dict) else None
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(default_limit, int) and default_limit > 0:
        return default_limit
    return 10


def _raw_corpus_status(*, lane_name: str, raw_candidates: list[dict[str, Any]]) -> str:
    if raw_candidates:
        return "ok"
    if lane_name == "github-ai-projects":
        return GITHUB_AI_PROJECTS_NO_OWN_RAW_CORPUS
    return RAW_CORPUS_MISSING


def _build_cross_lane_context(*, lane_name: str, report_date: str, config: dict[str, Any]) -> dict[str, Any]:
    if lane_name != "github-ai-projects":
        return {}
    lane_workers = config.get("lane_workers") or {}
    github_ai_config = lane_workers.get("github_ai_projects") or {}
    raw_queries = github_ai_config.get("discovery_queries", DEFAULT_GITHUB_AI_PROJECTS_DISCOVERY_QUERIES)
    queries = [
        str(query).format(report_date=report_date, date=report_date)
        for query in raw_queries
        if str(query).strip()
    ]
    return {
        "github_search_queries": queries,
        "compatibility_note": "github-ai-projects has no dedicated raw corpus yet; discovery context is declared explicitly.",
    }


def _collect_lane_context(*, collect_result: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lanes = collect_result.get("lanes")
    if isinstance(lanes, list):
        for lane in lanes:
            if isinstance(lane, dict) and lane.get("name") == lane_name:
                return lane
    return {}


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text.strip()
    parts = text.split("---", 2)
    if len(parts) != 3:
        return {}, text.strip()
    metadata = yaml.safe_load(parts[1]) or {}
    if not isinstance(metadata, dict):
        metadata = {}
    return metadata, parts[2].strip()


def _candidate_title(metadata: dict[str, Any], path: Path) -> str:
    repo = metadata.get("repo")
    if isinstance(repo, str) and repo.strip():
        return repo
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title
    return path.stem


def _candidate_id(metadata: dict[str, Any], title: str) -> str:
    repo = metadata.get("repo")
    if isinstance(repo, str) and repo.strip():
        return f"repo:{repo}"
    lane = metadata.get("lane")
    if isinstance(lane, str) and lane.strip():
        return f"{lane}:{title}"
    return title


def _build_source_snippet(
    metadata: dict[str, Any],
    markdown: str,
    *,
    snippet_char_limit: int,
) -> str:
    parts: list[str] = []
    description = metadata.get("description")
    if isinstance(description, str) and description.strip():
        parts.append(description.strip())
    if markdown.strip():
        parts.append(markdown.strip())
    snippet = "\n\n".join(parts).strip()
    if len(snippet) > snippet_char_limit:
        return snippet[: snippet_char_limit - 1].rstrip() + "..."
    return snippet
