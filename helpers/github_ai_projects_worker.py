from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from helpers.lane_contracts import validate_lane_input_artifact, validate_lane_output_artifact

GITHUB_URL_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    flags=re.IGNORECASE,
)
BARE_REPO_RE = re.compile(r"(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?![A-Za-z0-9_.-])")
TRAILING_REPO_CHARS_RE = re.compile(r"[\s\].,;:!?)}]+$")
REJECTED_BARE_REPO_OWNERS = {"docs", "issues", "operations", "assets", "src", "tests", "test", "api"}
REJECTED_BARE_REPO_NAMES = {"assets", "prs", "maintenance", "7", "24", "api", "docs"}


def _normalize_repo_id(owner: str, repo: str) -> str | None:
    owner = owner.strip().strip("/")
    repo = TRAILING_REPO_CHARS_RE.sub("", repo.strip().strip("/"))
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not owner or not repo:
        return None
    if owner.lower() in {"http:", "https:", "github.com"}:
        return None
    return f"{owner}/{repo}"


def _extract_repo_ids(text: str, *, include_bare: bool = True) -> list[str]:
    repos: list[str] = []
    seen: set[str] = set()
    for match in GITHUB_URL_RE.finditer(text or ""):
        repo = _normalize_repo_id(match.group(1), match.group(2))
        if repo and repo.lower() not in seen:
            repos.append(repo)
            seen.add(repo.lower())
    if include_bare:
        for match in BARE_REPO_RE.finditer(text or ""):
            owner, repo_name = match.group(1).split("/", 1)
            repo = _normalize_repo_id(owner, repo_name)
            owner_l = owner.lower()
            repo_l = repo_name.lower().strip().removesuffix(".git")
            if owner_l in REJECTED_BARE_REPO_OWNERS or repo_l in REJECTED_BARE_REPO_NAMES:
                continue
            if owner_l.isdigit() or repo_l.isdigit():
                continue
            if repo and repo.lower() not in seen:
                repos.append(repo)
                seen.add(repo.lower())
    return repos


def _raw_field(raw: Any, key: str) -> str:
    if isinstance(raw, dict) and raw.get(key) is not None:
        return str(raw[key])
    return ""


def _signal_repo_ids(signal: dict[str, Any]) -> list[str]:
    raw = signal.get("raw")
    texts = [
        str(signal.get("title") or ""),
        _raw_field(raw, "summary"),
        _raw_field(raw, "source_snippet"),
    ]
    repos: list[str] = []
    seen: set[str] = set()
    for repo in _extract_repo_ids(str(signal.get("url") or ""), include_bare=False):
        repos.append(repo)
        seen.add(repo.lower())
    for text in texts:
        for repo in _extract_repo_ids(text, include_bare=True):
            if repo.lower() not in seen:
                repos.append(repo)
                seen.add(repo.lower())
    return repos


def _lane_reason(source_lanes: list[str]) -> str:
    labels = {
        "github-trending-weekly": "GitHub Trending",
        "x-feed": "X 推荐流",
        "x-following": "X 关注流",
        "reddit-watch": "Reddit",
        "hacker-news-watch": "Hacker News",
        "hacker-news-search-watch": "Hacker News 搜索",
        "product-hunt-watch": "Product Hunt",
    }
    return "、".join(labels.get(lane, lane) for lane in source_lanes) if source_lanes else "GitHub 信号"


def _chinese_summary(repo: str, source_lanes: list[str], evidence_items: list[dict[str, Any]]) -> str:
    reason = _lane_reason(source_lanes)
    mention_count = len(evidence_items)
    if "github-trending-weekly" in source_lanes and mention_count > 1:
        return f"{repo} 同时出现在 {reason}，说明它不只是榜单热度，也被社区讨论或工作流内容反复提到。"
    if "github-trending-weekly" in source_lanes:
        return f"{repo} 来自 GitHub Trending，当前可作为 AI agent / coding workflow 项目候选继续观察。"
    return f"{repo} 被 {reason} 提到，属于从跨 lane 信号里发现的 GitHub AI 项目候选。"


def _unique_source_urls(repo: str, evidence_items: list[dict[str, Any]]) -> list[str]:
    repo_url = f"https://github.com/{repo}"
    urls = [repo_url]
    for item in evidence_items:
        for raw_url in item.get("source_urls", []):
            url = str(raw_url or "").strip()
            if url and url not in urls:
                urls.append(url)
        url = str(item.get("url") or "").strip()
        if url and url not in urls:
            urls.append(url)
    return urls


def _build_memory_markdown(report_date: str, items: list[dict[str, Any]]) -> str:
    lines = [f"# GitHub AI 项目 {report_date}", ""]
    if not items:
        lines.append("- No new repositories selected.")
        return "\n".join(lines).strip() + "\n"
    for index, item in enumerate(items, start=1):
        lines.append(f"## {index}. {item['title']}")
        lines.append("")
        lines.append(f"- Repo: {item['url']}")
        lines.append(f"- Why today: {item['why_today']}")
        lines.append(f"- Summary: {item['summary']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_github_ai_projects_output(lane_input: dict[str, Any]) -> dict[str, Any]:
    validate_lane_input_artifact(lane_input)
    if lane_input["lane"] != "github-ai-projects":
        raise ValueError("github-ai-projects worker requires lane github-ai-projects")

    report_date = lane_input["report_date"]
    target_count = lane_input.get("target_item_count")
    if not isinstance(target_count, int) or target_count <= 0:
        target_count = 5
    recent_repo_ids = {
        str(repo_id).lower()
        for repo_id in (lane_input.get("recent_history") or {}).get("repo_ids", [])
        if str(repo_id).strip()
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in lane_input.get("signals", []):
        if not isinstance(signal, dict):
            continue
        for repo in _signal_repo_ids(signal):
            if repo.lower() in recent_repo_ids:
                continue
            grouped[repo].append(signal)

    ranked = sorted(
        grouped.items(),
        key=lambda pair: (
            -len(pair[1]),
            0 if any(item.get("source_lane") == "github-trending-weekly" for item in pair[1]) else 1,
            pair[0].lower(),
        ),
    )[:target_count]

    output_items: list[dict[str, Any]] = []
    source_map: dict[str, dict[str, str]] = {}
    markdown_lines = ["## GitHub AI 项目", ""]
    for repo, evidence_items in ranked:
        repo_url = f"https://github.com/{repo}"
        source_lanes = sorted({str(item.get("source_lane")) for item in evidence_items if item.get("source_lane")})
        why_today = _lane_reason(source_lanes)
        summary = _chinese_summary(repo, source_lanes, evidence_items)
        source_urls = _unique_source_urls(repo, evidence_items)
        markdown_lines.append(f"- **{repo}**：{summary} [项目链接]({repo_url})")
        output_items.append(
            {
                "id": f"repo:{repo}",
                "title": repo,
                "url": repo_url,
                "summary": summary,
                "why_today": why_today,
                "source_urls": source_urls,
            }
        )
        source_map.setdefault(repo_url, {"label": repo, "url": repo_url})

    if not output_items:
        markdown_lines.append("- 无")

    status = "ok" if output_items else "empty"
    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": report_date,
        "lane": "github-ai-projects",
        "status": status,
        "section_title": "GitHub AI 项目",
        "markdown": "\n".join(markdown_lines).strip(),
        "items": output_items,
        "sources": list(source_map.values()),
        "quality": {
            "item_count": len(output_items),
            "warnings": [] if output_items else ["no_repo_candidates"],
        },
        "validation": {"status": "passed" if output_items else "empty", "errors": []},
        "side_artifacts": {"memory_markdown": _build_memory_markdown(report_date, output_items)},
    }
    validate_lane_output_artifact(output)
    return output
