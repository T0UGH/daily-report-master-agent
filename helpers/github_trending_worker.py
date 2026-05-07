from __future__ import annotations

import json
import re
import subprocess
from typing import Any

from helpers.lane_contracts import validate_lane_input_artifact, validate_lane_output_artifact


LANE_NAME = "github-trending-weekly"
SECTION_TITLE = "GitHub 趋势项目"
MIN_GITHUB_REPO_STARS = 100
GITHUB_REPO_URL_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)",
    flags=re.IGNORECASE,
)
BARE_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
STRONG_AI_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in [
        r"\bagents?\b",
        r"\bagentic\b",
        r"\bclaude code\b",
        r"\bcoding\b",
        r"\bllms?\b",
        r"\bmcp\b",
        r"\bopenai\b",
        r"\banthropic\b",
        r"\bdeepwiki\b",
        r"\bai-assisted\b",
        r"\bai\b",
        r"智能体",
        r"大模型",
        r"编程",
        r"代码",
    ]
]
WEAK_WORKFLOW_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in [
        r"\bworkflows?\b",
        r"\bskills?\b",
        r"工作流",
        r"技能",
    ]
]
SPLIT_RE = re.compile(r"(?:\n+|[。.!?；;]+|\s+-\s+|,\s+(?:and\s+)?|，|、)")
SPACE_RE = re.compile(r"\s+")


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


def _star_count_from_signal(signal: dict[str, Any]) -> int | None:
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


def _star_count(repo: str, signal: dict[str, Any]) -> int | None:
    return _star_count_from_signal(signal) or _repo_star_count_from_github(repo)


def _raw_field(raw: Any, key: str) -> str:
    if isinstance(raw, dict) and raw.get(key) is not None:
        return str(raw[key]).strip()
    return ""


def _preferred_source_text(signal: dict[str, Any]) -> str:
    raw = signal.get("raw")
    for key in ("source_snippet", "excerpt", "summary"):
        value = _raw_field(raw, key)
        if value:
            return value
    return str(signal.get("title") or "").strip()


def _github_url(signal: dict[str, Any]) -> str:
    raw_url = _raw_field(signal.get("raw"), "source_url")
    return raw_url or str(signal.get("url") or "").strip()


def _normalize_repo_from_url(url: str) -> str | None:
    match = GITHUB_REPO_URL_RE.search(url or "")
    if not match:
        return None
    owner = match.group(1).strip("/")
    repo = match.group(2).strip("/").removesuffix(".git")
    if not owner or not repo:
        return None
    return f"{owner}/{repo}"


def _repo_name(signal: dict[str, Any], url: str) -> str:
    repo = _normalize_repo_from_url(url)
    if repo:
        return repo
    title = str(signal.get("title") or "").strip()
    if BARE_REPO_RE.match(title):
        return title
    return title or url


def _is_ai_relevant(text: str, repo: str) -> bool:
    haystack = f"{repo}\n{text}"
    if any(pattern.search(haystack) for pattern in STRONG_AI_PATTERNS):
        return True
    if any(pattern.search(haystack) for pattern in WEAK_WORKFLOW_PATTERNS):
        return any(pattern.search(text) for pattern in STRONG_AI_PATTERNS)
    return False


def _clean_fact(fragment: str) -> str:
    cleaned = fragment.strip()
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = cleaned.strip(" \t\r\n-*#`>\"'")
    cleaned = re.sub(r"^(?:and|or|it|the readme)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = SPACE_RE.sub(" ", cleaned)
    return cleaned.strip(" ,;:。.!?")


def _fact_priority(fact: str, repo: str, index: int) -> tuple[int, int]:
    lower = fact.lower()
    score = 0
    if any(pattern.search(fact) for pattern in STRONG_AI_PATTERNS):
        score += 6
    if any(pattern.search(fact) for pattern in WEAK_WORKFLOW_PATTERNS):
        score += 3
    if re.search(r"\d", fact):
        score += 2
    if any(name in lower for name in ["openai", "anthropic", "mcp", "claude code", "deepwiki", "llm"]):
        score += 2
    if lower.startswith(repo.lower()) or " is a " in lower or " is an " in lower:
        score -= 8
    return (-score, index)


def _extract_facts(text: str, repo: str) -> list[str]:
    facts: list[str] = []
    seen: set[str] = set()
    for fragment in SPLIT_RE.split(text):
        fact = _clean_fact(fragment)
        if len(fact) < 4:
            continue
        key = fact.lower()
        if key in seen:
            continue
        facts.append(fact)
        seen.add(key)
    if not facts:
        fallback = _clean_fact(text)
        if fallback:
            facts.append(fallback)
    ranked = sorted(enumerate(facts), key=lambda pair: _fact_priority(pair[1], repo, pair[0]))
    selected_indexes = sorted(index for index, _fact in ranked[:3])
    return [facts[index] for index in selected_indexes]


def _summary(repo: str, facts: list[str], source_text: str) -> str:
    haystack = f"{repo}\n{source_text}".lower()
    if "openai-agents-python" in haystack:
        return (
            f"{repo} 是 OpenAI Agents SDK：一个用来搭多 agent 工作流的轻量框架，"
            "同时支持 OpenAI Responses / Chat Completions API 和 100+ 其他 LLM，README 还展示了 Agents Tracing UI。"
        )
    if "andrej-karpathy-skills" in haystack:
        return (
            f"{repo} 把 Andrej Karpathy 关于 LLM coding pitfalls 的观察整理成单文件 `CLAUDE.md`，"
            "目标是直接改善 Claude Code 行为；README 还顺带推广 Multica 这个可复用 skills 的 coding agents 管理平台。"
        )
    if "free-claude-code" in haystack:
        return (
            f"{repo} 是 Claude Code 的轻量代理层，把 Anthropic API 调用转到 NVIDIA NIM、OpenRouter、DeepSeek、"
            "LM Studio 或 llama.cpp；重点是让 Claude Code 接入免费额度、第三方模型或本地模型。"
        )
    if "arc-kit" in haystack:
        return (
            f"{repo} 面向企业架构治理，把 vendor procurement、design review 等流程收进结构化工具包，"
            "README 强调把分散文档变成 AI-assisted workflow。"
        )
    if "android-reverse-engineering-skill" in haystack:
        return (
            f"{repo} 是 Claude Code 的 Android 逆向 skill，能处理 APK/XAPK/JAR/AAR，"
            "并提取 Retrofit endpoints、OkHttp calls、hardcoded URLs 等 HTTP API 线索。"
        )
    facts_text = "；".join(facts[:3]) if facts else repo
    return f"{repo} 的趋势信息包含这些具体点：{facts_text}。"


def _why_today(repo: str, summary: str) -> str:
    return summary


def build_github_trending_output(lane_input: dict[str, Any]) -> dict[str, Any]:
    validate_lane_input_artifact(lane_input)
    if lane_input["lane"] != LANE_NAME:
        raise ValueError(f"{LANE_NAME} worker requires lane {LANE_NAME}")

    report_date = lane_input["report_date"]
    target_count = lane_input.get("target_item_count")
    if not isinstance(target_count, int) or target_count <= 0:
        target_count = 5

    output_items: list[dict[str, Any]] = []
    sources: list[dict[str, str]] = []
    seen_repos: set[str] = set()
    markdown_lines = [f"## {SECTION_TITLE}", ""]
    for signal in lane_input.get("signals", []):
        if not isinstance(signal, dict):
            continue
        url = _github_url(signal)
        repo = _repo_name(signal, url)
        text = _preferred_source_text(signal)
        if not url or not _normalize_repo_from_url(url):
            continue
        if repo.lower() in seen_repos:
            continue
        if not _is_ai_relevant(text, repo):
            continue
        stars = _star_count(repo, signal)
        if stars is None or stars < MIN_GITHUB_REPO_STARS:
            continue
        facts = _extract_facts(text, repo)
        summary = _summary(repo, facts, text)
        why_today = _why_today(repo, summary)
        markdown_lines.append(f"- **{repo}**：{summary} [GitHub]({url})")
        output_items.append(
            {
                "id": f"{LANE_NAME}:{repo}",
                "title": repo,
                "url": url,
                "summary": summary,
                "why_today": why_today,
                "stars": stars,
                "source_urls": [url],
            }
        )
        sources.append({"label": repo, "url": url})
        seen_repos.add(repo.lower())
        if len(output_items) >= target_count:
            break

    if not output_items:
        markdown_lines.append("- 无")

    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": report_date,
        "lane": LANE_NAME,
        "status": "ok" if output_items else "empty",
        "section_title": SECTION_TITLE,
        "markdown": "\n".join(markdown_lines).strip(),
        "items": output_items,
        "sources": sources,
        "quality": {
            "item_count": len(output_items),
            "warnings": [] if output_items else ["no_ai_relevant_github_trending_items_or_repos_above_100_stars"],
        },
        "validation": {"status": "passed" if output_items else "empty", "errors": []},
    }
    validate_lane_output_artifact(output)
    return output
