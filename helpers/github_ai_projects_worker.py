from __future__ import annotations

import json
import re
import subprocess
from collections import defaultdict
from typing import Any

from helpers.lane_contracts import validate_lane_input_artifact, validate_lane_output_artifact

MIN_GITHUB_REPO_STARS = 100

GITHUB_URL_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    flags=re.IGNORECASE,
)
BARE_REPO_RE = re.compile(r"(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?![A-Za-z0-9_.-])")
TRAILING_REPO_CHARS_RE = re.compile(r"[\s\].,;:!?)}]+$")
REJECTED_BARE_REPO_OWNERS = {
    "api",
    "apk",
    "assets",
    "docs",
    "issues",
    "jar",
    "javascript",
    "operations",
    "src",
    "test",
    "tests",
    "tokens",
    "user",
    "users",
}
REJECTED_BARE_REPO_NAMES = {
    "7",
    "24",
    "aar",
    "api",
    "assets",
    "assistant",
    "docs",
    "maintenance",
    "min",
    "prs",
    "s",
    "typescript",
    "xapk",
}


def _parse_star_count(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        return int(value) if value >= 0 else None
    text = str(value).strip().lower().replace(",", "")
    if not text:
        return None
    if not re.fullmatch(r"\d+(?:\.\d+)?\s*[km]?", text):
        return None
    number_match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([km])?", text)
    if not number_match:
        return None
    number = float(number_match.group(1))
    suffix = number_match.group(2)
    if suffix == "k":
        number *= 1000
    elif suffix == "m":
        number *= 1_000_000
    return int(number)


def _parse_star_count_from_text(text: Any) -> int | None:
    normalized = str(text or "").lower().replace(",", "")
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*([km])?\s*(?:stars?|stargazers?|⭐|星)", normalized)
    if not matches:
        return None
    values: list[int] = []
    for number_text, suffix in matches:
        number = float(number_text)
        if suffix == "k":
            number *= 1000
        elif suffix == "m":
            number *= 1_000_000
        values.append(int(number))
    return max(values) if values else None


def _signal_star_count(signal: dict[str, Any]) -> int | None:
    candidates: list[Any] = [
        signal.get("stars"),
        signal.get("stargazerCount"),
        signal.get("stargazers"),
        signal.get("star_count"),
        signal.get("repo_stars"),
    ]
    raw = signal.get("raw")
    if isinstance(raw, dict):
        candidates.extend(
            [
                raw.get("stars"),
                raw.get("stargazerCount"),
                raw.get("stargazers"),
                raw.get("star_count"),
                raw.get("repo_stars"),
            ]
        )
        text_candidates = [raw.get(key) for key in ("summary", "source_snippet", "excerpt")]
    else:
        text_candidates = []
    parsed = [_parse_star_count(value) for value in candidates]
    parsed.extend(_parse_star_count_from_text(value) for value in text_candidates)
    parsed = [value for value in parsed if value is not None]
    return max(parsed) if parsed else None


def _repo_star_count_from_github(repo: str) -> int | None:
    try:
        completed = subprocess.run(
            ["gh", "repo", "view", repo, "--json", "stargazerCount"],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return None
    return _parse_star_count(payload.get("stargazerCount"))


def _repo_star_count(repo: str, evidence_items: list[dict[str, Any]]) -> int | None:
    from_signals = [_signal_star_count(item) for item in evidence_items]
    from_signals = [value for value in from_signals if value is not None]
    if from_signals:
        return max(from_signals)
    return _repo_star_count_from_github(repo)


def _meets_min_star_threshold(repo: str, evidence_items: list[dict[str, Any]]) -> tuple[bool, int | None]:
    stars = _repo_star_count(repo, evidence_items)
    return stars is not None and stars >= MIN_GITHUB_REPO_STARS, stars


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

    ranked_candidates = sorted(
        grouped.items(),
        key=lambda pair: (
            -len(pair[1]),
            0 if any(item.get("source_lane") == "github-trending-weekly" for item in pair[1]) else 1,
            pair[0].lower(),
        ),
    )

    output_items: list[dict[str, Any]] = []
    source_map: dict[str, dict[str, str]] = {}
    filtered_low_star_repos: list[str] = []
    markdown_lines = ["## GitHub AI 项目", ""]
    for repo, evidence_items in ranked_candidates:
        meets_threshold, stars = _meets_min_star_threshold(repo, evidence_items)
        if not meets_threshold:
            star_label = "unknown" if stars is None else str(stars)
            filtered_low_star_repos.append(f"{repo}:{star_label}")
            continue
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
                "stars": stars,
                "source_urls": source_urls,
            }
        )
        source_map.setdefault(repo_url, {"label": repo, "url": repo_url})
        if len(output_items) >= target_count:
            break

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
            "warnings": ([] if output_items else ["no_repo_candidates"])
            + (["filtered_repos_below_100_stars"] if filtered_low_star_repos else []),
        },
        "validation": {"status": "passed" if output_items else "empty", "errors": []},
        "side_artifacts": {"memory_markdown": _build_memory_markdown(report_date, output_items)},
    }
    validate_lane_output_artifact(output)
    return output
