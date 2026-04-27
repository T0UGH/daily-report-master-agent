from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml


RAW_CORPUS_MISSING = "blocked_raw_corpus_missing"


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
        source_url = metadata.get("url")
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
