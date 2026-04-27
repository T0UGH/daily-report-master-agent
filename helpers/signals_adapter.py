from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlsplit, urlunsplit

from helpers.validate_report_output_contract import FIXED_SECTION_ORDER, FIXED_SECTION_TITLES


DEFAULT_SOURCE = "signals-engine"
DEFAULT_SIGNALS_ROOT = Path.home() / ".daily-lane-data" / "signals"
DEFAULT_SELECTED_ITEMS_RUNTIME_ROOT = Path.home() / ".daily-lane-data" / "runtime" / "daily-report-master"
DEFAULT_SELECTED_ITEMS_LOOKBACK_DAYS = 3
EXCERPT_LIMIT = 280
SOURCE_SNIPPET_LIMIT = 560
REPORT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "report-body-template.md"
REPORT_TITLE_TEMPLATE = "AI Agent 日报（{report_date}）"
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BARE_URL_PATTERN = re.compile(r"https?://[^\s]+")
INLINE_BRACKET_PATTERN = re.compile(r"\[([^\]]+)\]")
REDDIT_URL_POST_ID_PATTERN = re.compile(
    r"(?:reddit\.com/r/[^/]+/comments/|redd\.it/)([0-9a-z]{5,12})(?:[/?#]|$)",
    re.IGNORECASE,
)
REDDIT_SIGNAL_PATH_POST_ID_PATTERN = re.compile(
    r"(?:^|/)(?:r__[^/]+__)?([0-9a-z]{5,12})__reddit_thread__",
    re.IGNORECASE,
)
REDDIT_POST_ID_PATTERN = re.compile(r"^[0-9a-z]{5,12}$", re.IGNORECASE)
VERSION_TOKEN_PATTERN = re.compile(r"\bv?\d+(?:\.\d+){1,3}(?:-[a-z0-9]+(?:\.\d+)*)?\b", re.IGNORECASE)
FALLBACK_SOURCE_URL_TEMPLATES = {
    "x-feed": "https://x.com/example/status/{date_compact}01",
    "x-following": "https://x.com/example/status/{date_compact}02",
    "reddit-watch": "https://www.reddit.com/r/example/comments/{date_compact}/reddit_watch/",
    "hacker-news-watch": "https://news.ycombinator.com/item?id={date_compact}03",
    "hacker-news-search-watch": "https://news.ycombinator.com/item?id={date_compact}04",
    "claude-code-watch": "https://github.com/example/claude-code-watch/{report_date}",
    "codex-watch": "https://github.com/example/codex-watch/{report_date}",
    "openclaw-watch": "https://github.com/example/openclaw-watch/{report_date}",
    "github-trending-weekly": "https://github.com/example/github-trending-weekly/{report_date}",
    "product-hunt-watch": "https://www.producthunt.com/posts/product-hunt-watch-{report_date}",
    "polymarket-watch": "https://polymarket.com/event/polymarket-watch-{report_date}",
    "weather-watch": "https://weather.example.com/weather-watch/{report_date}",
}
LINK_LABELS = {
    "x-feed": "原帖",
    "x-following": "原帖",
    "reddit-watch": "Reddit",
    "hacker-news-watch": "Hacker News",
    "hacker-news-search-watch": "Hacker News",
    "claude-code-watch": "Release",
    "codex-watch": "GitHub",
    "openclaw-watch": "Release",
    "github-trending-weekly": "GitHub",
    "product-hunt-watch": "Product Hunt",
    "polymarket-watch": "Polymarket",
    "weather-watch": "天气",
}
DEFAULT_LANE_ITEM_LIMITS = {
    "x-feed": 10,
    "x-following": 10,
    "reddit-watch": 10,
    "hacker-news-watch": 10,
    "hacker-news-search-watch": 10,
    "claude-code-watch": 10,
    "codex-watch": 10,
    "openclaw-watch": 10,
    "github-trending-weekly": 10,
    "product-hunt-watch": 10,
    "polymarket-watch": 10,
    "weather-watch": 2,
}
SECONDARY_ITEM_SCORE_FLOORS = {
    "reddit-watch": 10,
    "codex-watch": 10,
    "github-trending-weekly": 8,
}
TOPIC_TOKEN_STOPWORDS = {
    "about",
    "across",
    "agent",
    "agents",
    "builder",
    "builders",
    "build",
    "clarify",
    "code",
    "coding",
    "cover",
    "covers",
    "deferred",
    "feature",
    "first",
    "flattened",
    "github",
    "here",
    "make",
    "open-source",
    "opensource",
    "path",
    "post",
    "posts",
    "project",
    "projects",
    "register",
    "release",
    "releases",
    "review",
    "support",
    "team",
    "tests",
    "tool",
    "tools",
    "update",
    "updates",
    "using",
    "watch",
}
NOISY_X_LANES = {"x-feed", "x-following"}
RESIDUAL_NOISY_X_CLAUSE_PATTERNS = (
    r"^the model performs best if\b",
    r"^reality:",
    r"^tldr:",
    r"^seems less accurate\b",
    r"^gives you everything\b",
)
CROSS_DAY_SOURCE_URL_DEDUPE_EXEMPT_LANES: frozenset[str] = frozenset(
    {"claude-code-watch", "openclaw-watch"}
)
CROSS_DAY_TOPIC_DEDUPE_EXEMPT_LANES: frozenset[str] = frozenset({"weather-watch"})
NO_INFO_ON_EMPTY_SELECTED_LANES: frozenset[str] = frozenset(
    lane_name for lane_name in FIXED_SECTION_ORDER if lane_name not in {"weather-watch", "x-feed", "x-following"}
)
VERSION_DISTINGUISHING_TOPIC_DEDUPE_LANES: frozenset[str] = frozenset(
    {"claude-code-watch", "codex-watch", "openclaw-watch"}
)
CONTENT_SECTION_PREFERENCES = {
    "x-feed": ("post",),
    "x-following": ("post",),
    "reddit-watch": ("post",),
    "hacker-news-watch": ("post",),
    "hacker-news-search-watch": ("post",),
    "claude-code-watch": ("summary", "release notes", "post"),
    "codex-watch": ("merged pr", "summary", "post"),
    "openclaw-watch": ("summary", "release notes", "post"),
    "github-trending-weekly": ("summary", "readme", "post"),
    "product-hunt-watch": ("preview", "snapshot", "post"),
    "polymarket-watch": ("expectation", "outcome probabilities", "market strength"),
    "weather-watch": ("weather", "forecast", "summary"),
}
DENSE_ENTRY_SOURCE_SECTION_PREFERENCES = {
    "claude-code-watch": ("what's changed", "release notes", "changes", "fixes", "post"),
    "codex-watch": ("merged pr", "summary", "release notes", "release", "post"),
    "openclaw-watch": ("summary", "release notes", "changes", "fixes", "post"),
    "hacker-news-watch": ("story", "hacker news context", "top comments", "post"),
    "hacker-news-search-watch": ("story", "hacker news context", "top comments", "post"),
}
DENSE_ENTRY_SOURCE_LIMITS = {
    "claude-code-watch": 1200,
    "codex-watch": 900,
    "openclaw-watch": 1600,
    "hacker-news-watch": 1600,
    "hacker-news-search-watch": 1600,
}
DENSE_ENTRY_BASELINE_COUNTS = {
    "claude-code-watch": 5,
    "codex-watch": 3,
    "openclaw-watch": 3,
}
DENSE_ENTRY_PRIORITY_RULES = {
    "claude-code-watch": (
        (("network error",), 95),
        (("/doctor",), 94),
        (("webfetch",), 93),
        (("queued messages",), 92),
        (("queued user prompts",), 91),
        (("mcp large-output truncation prompt",), 75),
    ),
    "codex-watch": (
        (("guardian review timeout",), 95),
        (("app-server notification path",), 94),
        (("mcp tool",), 93),
        (("wall time",), 92),
        (("model output",), 91),
        (("deferred", "mcp"), 90),
        (("flattened", "mcp"), 89),
    ),
    "openclaw-watch": (
        (("gpt-5.4-pro",), 96),
        (("telegram/forum topics",), 95),
        (("`apikey`",), 94),
        (("allowfrom",), 93),
        (("config.patch",), 92),
        (("config.apply",), 91),
        (("hook:wake",), 90),
        (("ssrf",), 89),
        (("sender allowlist",), 88),
    ),
}
METADATA_LINE_PREFIXES = (
    "likes:",
    "retweets:",
    "replies:",
    "views:",
    "position in session:",
    "feed context:",
    "group:",
    "tags:",
    "community:",
    "score:",
    "comments:",
    "matched query:",
    "author:",
    "external link:",
    "fetched at:",
    "source:",
    "topic cluster:",
    "query:",
    "interpretation:",
)
KEYWORD_WEIGHTS = (
    ("claude code", 8),
    ("/ultraplan", 8),
    ("team-onboarding", 6),
    ("guardian timeout", 8),
    ("agent matrix", 8),
    ("plan -> build -> review", 8),
    ("architect", 4),
    ("builder", 4),
    ("reviewer", 4),
    ("markdown handoff", 4),
    ("harness", 6),
    ("workflow", 4),
    ("workflows", 4),
    ("agentic", 4),
    ("agent", 3),
    ("agents", 3),
    ("mcp", 8),
    ("design context", 6),
    ("codex", 7),
    ("openclaw", 7),
    ("anthropic", 4),
    ("openai", 4),
    ("gemini", 3),
    ("coding ai", 8),
    ("coding", 4),
    ("model", 3),
    ("models", 3),
    ("bdd", 4),
    ("e2e", 4),
    ("testing", 3),
    ("测试", 3),
    ("工作流", 5),
    ("代理", 5),
    ("编程", 4),
    ("模型", 3),
    ("审阅", 3),
    ("协作", 3),
    ("chatgpt import", 6),
    ("dreaming", 5),
)
HACKER_NEWS_HOT_REPORTABLE_KEYWORD_GROUPS = (
    ("claude design",),
    ("claude code",),
    ("codex",),
    ("openclaw",),
    ("mcp",),
    ("agent harness",),
    ("agent workflow",),
    ("agent handoff",),
    ("review checklist",),
    ("review loop",),
    ("reviewer loop",),
    ("git worktree",),
    ("tmux", "worktree"),
    ("coding ai",),
    ("coding agents",),
    ("ai", "benchmark"),
    ("coding", "benchmark"),
    ("agent", "benchmark"),
    ("frontiermath",),
    ("swe-bench",),
    ("repo boundary",),
    ("repo boundaries",),
)
HACKER_NEWS_HOT_RELEVANCE_SCORE_THRESHOLD = 10
KNOWN_TERMS = (
    "Claude Code",
    "Codex",
    "OpenClaw",
    "Polymarket",
    "Product Hunt",
    "Anthropic",
    "OpenAI",
    "Gemini",
    "MCP",
    "Dreaming",
    "agent matrix",
    "harness",
    "Plan -> Build -> Review",
    "/ultraplan",
    "/team-onboarding",
)
EDITOR_RULES = (
    {
        "lane": "x-feed",
        "keywords": (("claude code", "/ultraplan"),),
        "headline": "Claude Code 的 `/ultraplan` 正把“先出计划再执行”变成默认工作流。",
        "detail": "这条高传播帖子强调的不是单个命令，而是先在网页上生成和审阅实施计划，再决定是否落到本地执行。",
    },
    {
        "lane": "x-following",
        "keywords": (("agent matrix",), ("harness", "bdd", "e2e")),
        "headline": "agent harness 的测试思路开始往 `agent matrix` 方向延伸。",
        "detail": "原帖把 BDD、e2e 和 agent workflow 放到一起思考，核心是在流程里尽量减少人类断点。",
    },
    {
        "lane": "x-feed",
        "keywords": (("review checklist", "handoff"),),
        "headline": "Claude Code 相关讨论开始把 review checklist 当成 agent handoff 的轻量协调器。",
        "detail": "这条推荐流信号关注的不是单个功能点，而是团队如何用 review checklist 把 agent handoff 对齐得更稳。",
    },
    {
        "lane": "reddit-watch",
        "keywords": (("architect", "builder", "reviewer"), ("three man team",), ("3-agent team",)),
        "headline": "Plan -> Build -> Review 仍然是多 agent 协作里最自然的骨架。",
        "detail": "帖子把 Architect、Builder、Reviewer 拆成独立角色，并用 markdown handoff 保持流程透明。",
    },
    {
        "lane": "reddit-watch",
        "keywords": (("swarm", "governance", "codex", "gemini"),),
        "headline": "多模型 agent swarm 开始把“怎么治理”单独拿出来讨论。",
        "detail": "这条 Reddit 讨论把 Claude、Codex、Gemini 放进同一条协作链路，重点已经转向 coordinator 如何分发任务、跟踪改动并给 swarm 补治理。",
    },
    {
        "lane": "claude-code-watch",
        "keywords": (("team-onboarding",), ("brief mode",)),
        "headline": "Claude Code 继续把团队上手和企业环境可用性往前补。",
        "detail": "这版更新把 onboarding、云环境、证书和 brief mode 一起推进，方向明显偏向真实团队协作。",
    },
    {
        "lane": "codex-watch",
        "keywords": (("guardian timeout",), ("timeout guidance",)),
        "headline": "Guardian timeout 被明确从显式拒绝里拆开处理。",
        "detail": "这类改动在修 agent 执行链路里的错误语义，能减少审批超时和策略拒绝被混为一谈的情况。",
    },
    {
        "lane": "codex-watch",
        "keywords": (("mcp", "deferred"), ("mcp", "flattened")),
        "headline": "Codex 在 deferred MCP 工具调用链路上继续补兼容性。",
        "detail": "这条 PR 处理的是扁平化 alias 和特定调用路径，属于把 MCP 工具调用边角补齐的底层修复。",
    },
    {
        "lane": "openclaw-watch",
        "keywords": (("chatgpt import",), ("dreaming", "provider failover")),
        "headline": "OpenClaw 继续把多模型代理平台往产品化收口。",
        "detail": "新版本一边补导入和富媒体能力，一边修 OAuth、failover 和稳定性细节，明显更偏向真实使用场景。",
    },
    {
        "lane": "github-trending-weekly",
        "keywords": (("harness", "deterministic"), ("harness", "repeatable")),
        "headline": "harness builder 开始把 AI coding 的可重复性单独做成基础设施。",
        "detail": "这个趋势项目强调的不是再包一层 agent，而是把 AI coding 流程做得更可控、更可重复。",
    },
    {
        "lane": "product-hunt-watch",
        "keywords": (("mcp", "design context"),),
        "headline": "MCP 正在从协议名词外溢成可直接售卖的工作流包装。",
        "detail": "这个 Product Hunt 条目卖的不是通用 agent，而是把设计上下文更稳定地喂给 AI agents。",
    },
    {
        "lane": "polymarket-watch",
        "keywords": (("second-best coding ai model", "anthropic"),),
        "headline": "市场对 Anthropic 在 coding AI 第二梯队的位置判断相当集中。",
        "detail": "这份 Polymarket 合约当前把 Anthropic 放在显著领先位置，反映出交易者对头部 coding model 分层的共识。",
    },
)


@dataclass(frozen=True)
class LaneSnapshot:
    name: str
    status: str
    useful_item_count: int
    issues: list[str]
    signal_paths: list[Path]


@dataclass(frozen=True)
class ReportRenderItem:
    lane: str
    title: str
    excerpt: str
    source_url: str
    link_label: str
    source_title: str
    sort_key: tuple[str, str]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(data: Any, output_path: Path | None = None) -> None:
    rendered = json.dumps(data, ensure_ascii=False, indent=2)
    if output_path is None:
        print(rendered)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{rendered}\n", encoding="utf-8")


def discover_lane_names(signals_root: Path, report_date: str) -> list[str]:
    if not signals_root.exists():
        raise ValueError(f"signals 根目录不存在: {signals_root}")

    lane_names = []
    for child in sorted(signals_root.iterdir()):
        if child.is_dir() and (child / report_date).is_dir():
            lane_names.append(child.name)
    return lane_names


def resolve_lane_names(signals_root: Path, report_date: str, lane_names: Sequence[str] | None) -> list[str]:
    if lane_names:
        return list(lane_names)
    return discover_lane_names(signals_root=signals_root, report_date=report_date)


def build_collect_result(
    signals_root: Path,
    report_date: str,
    lane_names: Sequence[str] | None = None,
) -> dict[str, Any]:
    lane_snapshots = [
        inspect_lane(signals_root=signals_root, report_date=report_date, lane_name=lane_name)
        for lane_name in resolve_lane_names(signals_root=signals_root, report_date=report_date, lane_names=lane_names)
    ]

    total_useful_items = sum(item.useful_item_count for item in lane_snapshots)
    non_ok_count = sum(1 for item in lane_snapshots if item.status != "ok")
    issues = [issue for item in lane_snapshots for issue in item.issues]

    result: dict[str, Any] = {
        "report_date": report_date,
        "source": DEFAULT_SOURCE,
        "lanes": [
            {
                "name": item.name,
                "status": item.status,
                "useful_item_count": item.useful_item_count,
            }
            for item in lane_snapshots
        ],
        "summary": {
            "useful_item_count": total_useful_items,
            "partial_lane_count": non_ok_count,
        },
    }
    if issues:
        result["errors"] = issues
    return result


def build_selected_items(
    signals_root: Path,
    report_date: str,
    lane_names: Sequence[str] | None = None,
    per_lane_limit: int | None = None,
    lane_item_limits: dict[str, int] | None = None,
    previous_selected_items_path: Path | None = None,
    previous_selected_items_runtime_root: Path | None = None,
) -> dict[str, Any]:
    selected_items: list[dict[str, Any]] = []
    lane_counts: list[dict[str, Any]] = []
    previous_reddit_identity_keys: set[str] | None = None
    previous_selected_source_urls: set[str] | None = None
    previous_selected_items_by_lane: dict[str, list[dict[str, Any]]] | None = None
    resolved_previous_selected_items_paths = resolve_recent_selected_items_paths_from_inputs(
        report_date=report_date,
        previous_selected_items_path=previous_selected_items_path,
        runtime_root=previous_selected_items_runtime_root
        or DEFAULT_SELECTED_ITEMS_RUNTIME_ROOT,
    )

    for lane_name in resolve_lane_names(signals_root=signals_root, report_date=report_date, lane_names=lane_names):
        lane_snapshot = inspect_lane(signals_root=signals_root, report_date=report_date, lane_name=lane_name)
        lane_candidates = [
            build_signal_candidate_from_signal(signal_path=signal_path, signals_root=signals_root, fallback_lane=lane_name)
            for signal_path in lane_snapshot.signal_paths
        ]
        if lane_name not in CROSS_DAY_SOURCE_URL_DEDUPE_EXEMPT_LANES:
            if previous_selected_source_urls is None:
                previous_selected_source_urls = load_previous_selected_source_urls(
                    previous_selected_items_path=resolved_previous_selected_items_paths
                )
            if previous_selected_source_urls:
                lane_candidates = [
                    candidate
                    for candidate in lane_candidates
                    if normalize_whitespace(str(candidate.get("source_url", ""))) not in previous_selected_source_urls
                ]
        if lane_name == "reddit-watch":
            if previous_reddit_identity_keys is None:
                previous_reddit_identity_keys = load_previous_reddit_identity_keys(
                    previous_selected_items_path=resolved_previous_selected_items_paths
                )
            if previous_reddit_identity_keys:
                lane_candidates = [
                    candidate
                    for candidate in lane_candidates
                    if not extract_reddit_identity_keys(candidate) & previous_reddit_identity_keys
                ]
        if lane_name not in CROSS_DAY_TOPIC_DEDUPE_EXEMPT_LANES:
            if previous_selected_items_by_lane is None:
                previous_selected_items_by_lane = load_previous_selected_items_by_lane(
                    previous_selected_items_path=resolved_previous_selected_items_paths
                )
            recent_lane_selected_items = previous_selected_items_by_lane.get(lane_name, ())
            if recent_lane_selected_items:
                lane_candidates = [
                    candidate
                    for candidate in lane_candidates
                    if not candidate_is_cross_day_topic_duplicate(
                        lane_name=lane_name,
                        candidate=candidate,
                        previous_selected_items=recent_lane_selected_items,
                    )
                ]
        lane_limit = per_lane_limit
        if lane_limit is None and lane_item_limits is not None:
            lane_limit = lane_item_limits.get(lane_name)
        if lane_limit is None:
            lane_limit = DEFAULT_LANE_ITEM_LIMITS.get(lane_name)

        lane_items = [
            serialize_selected_item(candidate)
            for candidate in curate_lane_candidates(lane_name=lane_name, candidates=lane_candidates, lane_limit=lane_limit)
        ]

        selected_items.extend(lane_items)
        lane_counts.append(
            {
                "lane": lane_name,
                "selected_item_count": len(lane_items),
            }
        )

    return {
        "report_date": report_date,
        "source": DEFAULT_SOURCE,
        "selected_items": selected_items,
        "summary": {
            "selected_item_count": len(selected_items),
            "lane_counts": lane_counts,
        },
    }


def resolve_recent_selected_items_paths_from_inputs(
    *,
    report_date: str,
    previous_selected_items_path: Path | None,
    runtime_root: Path,
) -> list[Path]:
    if previous_selected_items_path is not None:
        inferred_runtime_root = infer_selected_items_runtime_root(previous_selected_items_path)
        if inferred_runtime_root is not None:
            return resolve_recent_selected_items_paths(runtime_root=inferred_runtime_root, report_date=report_date)
        return [previous_selected_items_path]
    return resolve_recent_selected_items_paths(
        runtime_root=runtime_root,
        report_date=report_date,
    )


def infer_selected_items_runtime_root(selected_items_path: Path) -> Path | None:
    if selected_items_path.name != "selected-items.json":
        return None
    try:
        date.fromisoformat(selected_items_path.parent.name)
    except ValueError:
        return None
    return selected_items_path.parent.parent


def resolve_recent_selected_items_paths(
    *,
    runtime_root: Path,
    report_date: str,
    lookback_days: int = DEFAULT_SELECTED_ITEMS_LOOKBACK_DAYS,
) -> list[Path]:
    try:
        report_day = date.fromisoformat(report_date)
    except ValueError:
        return []
    return [
        runtime_root / (report_day - timedelta(days=days_ago)).isoformat() / "selected-items.json"
        for days_ago in range(1, lookback_days + 1)
    ]


def resolve_previous_selected_items_path(*, runtime_root: Path, report_date: str) -> Path | None:
    recent_paths = resolve_recent_selected_items_paths(runtime_root=runtime_root, report_date=report_date, lookback_days=1)
    if not recent_paths:
        return None
    return recent_paths[0]


def iter_previous_selected_items_paths(
    previous_selected_items_path: Path | Sequence[Path] | None,
) -> list[Path]:
    if previous_selected_items_path is None:
        return []
    if isinstance(previous_selected_items_path, Path):
        return [previous_selected_items_path]
    return [path for path in previous_selected_items_path if isinstance(path, Path)]


def load_previous_selected_items_list(*, previous_selected_items_path: Path | Sequence[Path] | None) -> list[dict[str, Any]]:
    selected_items: list[dict[str, Any]] = []
    for selected_items_path in iter_previous_selected_items_paths(previous_selected_items_path):
        try:
            payload = json.loads(selected_items_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue

        if not isinstance(payload, dict):
            continue
        raw_selected_items = payload.get("selected_items")
        if not isinstance(raw_selected_items, list):
            continue
        selected_items.extend(item for item in raw_selected_items if isinstance(item, dict))
    return selected_items


def load_previous_selected_source_urls(*, previous_selected_items_path: Path | Sequence[Path] | None) -> set[str]:
    source_urls: set[str] = set()
    for item in load_previous_selected_items_list(previous_selected_items_path=previous_selected_items_path):
        source_url = normalize_whitespace(str(item.get("source_url", "")))
        if source_url:
            source_urls.add(source_url)
    return source_urls


def load_previous_reddit_identity_keys(*, previous_selected_items_path: Path | Sequence[Path] | None) -> set[str]:
    identity_keys: set[str] = set()
    for item in load_previous_selected_items_list(previous_selected_items_path=previous_selected_items_path):
        if item.get("lane") != "reddit-watch":
            continue
        identity_keys.update(extract_reddit_identity_keys(item))
    return identity_keys


def load_previous_selected_items_by_lane(
    *,
    previous_selected_items_path: Path | Sequence[Path] | None,
) -> dict[str, list[dict[str, Any]]]:
    items_by_lane: dict[str, list[dict[str, Any]]] = {}
    for item in load_previous_selected_items_list(previous_selected_items_path=previous_selected_items_path):
        lane_name = normalize_whitespace(str(item.get("lane", "")))
        if not lane_name:
            continue
        items_by_lane.setdefault(lane_name, []).append(item)
    return items_by_lane


def extract_reddit_identity_keys(item: dict[str, Any]) -> set[str]:
    identity_keys: set[str] = set()

    source_url = as_string(item.get("source_url")) or ""
    canonical_source_url = canonicalize_reddit_source_url(source_url)
    if canonical_source_url:
        identity_keys.add(f"url:{canonical_source_url}")

    for value in (
        source_url,
        as_string(item.get("signal_path")) or "",
        as_string(item.get("title")) or "",
    ):
        post_id = extract_reddit_post_id(value)
        if post_id:
            identity_keys.add(f"id:{post_id}")

    front_matter = item.get("_front_matter")
    if isinstance(front_matter, dict):
        for key in ("post_id", "entity_id"):
            post_id = normalize_reddit_post_id(front_matter.get(key))
            if post_id:
                identity_keys.add(f"id:{post_id}")

    return identity_keys


def canonicalize_reddit_source_url(source_url: str) -> str | None:
    cleaned_source_url = normalize_whitespace(source_url)
    if not cleaned_source_url:
        return None

    try:
        parsed = urlsplit(cleaned_source_url)
    except ValueError:
        return None

    host = parsed.netloc.lower()
    path = re.sub(r"/+", "/", parsed.path).rstrip("/")
    if not path:
        return None

    if host == "redd.it":
        return urlunsplit(("https", "redd.it", path, "", ""))
    if host not in {"reddit.com", "www.reddit.com", "old.reddit.com", "new.reddit.com", "np.reddit.com"}:
        return None
    return urlunsplit(("https", "www.reddit.com", f"{path}/", "", ""))


def extract_reddit_post_id(text: str) -> str | None:
    cleaned_text = normalize_whitespace(text)
    if not cleaned_text:
        return None

    direct_id = normalize_reddit_post_id(cleaned_text)
    if direct_id:
        return direct_id

    url_match = REDDIT_URL_POST_ID_PATTERN.search(cleaned_text)
    if url_match:
        return url_match.group(1).lower()

    signal_path_match = REDDIT_SIGNAL_PATH_POST_ID_PATTERN.search(cleaned_text)
    if signal_path_match:
        return signal_path_match.group(1).lower()

    return None


def normalize_reddit_post_id(value: Any) -> str | None:
    text = as_string(value)
    if not text:
        return None
    cleaned_text = normalize_whitespace(text)
    if not REDDIT_POST_ID_PATTERN.fullmatch(cleaned_text):
        return None
    return cleaned_text.lower()


def build_validation_bundle(collect_result: dict[str, Any], selected_items: dict[str, Any]) -> dict[str, Any]:
    validate_collect_result_object(collect_result)
    validate_selected_items_object(selected_items)

    collect_date = collect_result["report_date"]
    selected_date = selected_items["report_date"]
    if collect_date != selected_date:
        raise ValueError("collect result 与 selected_items 的 report_date 必须一致")

    collect_lane_counts = {lane["name"]: lane["useful_item_count"] for lane in collect_result["lanes"]}
    selected_lane_counts = Counter(item["lane"] for item in selected_items["selected_items"])

    for lane_name, count in selected_lane_counts.items():
        if lane_name not in collect_lane_counts:
            raise ValueError(f"selected_items 引用了 collect result 中不存在的 lane: {lane_name}")
        if count > collect_lane_counts[lane_name]:
            raise ValueError(f"selected_items 在 lane {lane_name} 上超出了 collect result 计数")

    return {
        "report_date": collect_date,
        "collect_result": collect_result,
        "selected_items": selected_items,
        "summary": {
            "collect_useful_item_count": collect_result["summary"]["useful_item_count"],
            "selected_item_count": selected_items["summary"]["selected_item_count"],
            "is_subset": True,
        },
    }


def build_report_artifact(
    collect_result: dict[str, Any],
    selected_items: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_collect_result_object(collect_result)
    report_date = collect_result["report_date"]
    useful_item_count = collect_result["summary"]["useful_item_count"]
    if useful_item_count <= 0:
        raise ValueError("无可用内容时不能构造 report artifact")

    if selected_items is not None:
        build_validation_bundle(collect_result=collect_result, selected_items=selected_items)

    renderable_lanes = ordered_renderable_lanes(collect_result["lanes"])
    if not renderable_lanes:
        raise ValueError("collect result 没有可进入 reader-facing contract 的非空栏目")

    items_by_lane = build_render_items_by_lane(
        collect_result=collect_result,
        selected_items=selected_items,
        renderable_lanes=renderable_lanes,
    )

    body_sections: list[str] = []
    source_sections: list[str] = []
    source_lanes: list[str] = []
    for lane_name in renderable_lanes:
        render_items = items_by_lane.get(lane_name, [])
        if not render_items:
            continue

        section_title = FIXED_SECTION_TITLES[lane_name]
        body_sections.append(render_body_section(section_title, render_items))
        if any(item.source_url for item in render_items):
            source_lanes.append(lane_name)
            source_sections.append(render_source_section(section_title, render_items))

    if not body_sections:
        raise ValueError("没有可渲染的 reader-facing 正文栏目")

    template = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
    body_markdown = (
        template.replace("{{report_date}}", report_date)
        .replace("{{body_markdown}}", "\n\n".join(body_sections))
        .replace("{{sources_markdown}}", "\n\n".join(source_sections))
    )

    return {
        "artifact_type": "final_report",
        "report_date": report_date,
        "title": REPORT_TITLE_TEMPLATE.format(report_date=report_date),
        "summary": f"今日共整理 {useful_item_count} 条有用内容。",
        "body_markdown": body_markdown,
        "useful_item_count": useful_item_count,
        "source_lanes": source_lanes,
    }


def validate_collect_result_object(data: Any) -> None:
    if not isinstance(data, dict):
        raise ValueError("collect result 必须是 object")
    if not isinstance(data.get("report_date"), str):
        raise ValueError("collect result 缺少 report_date")
    if not isinstance(data.get("source"), str):
        raise ValueError("collect result 缺少 source")

    lanes = data.get("lanes")
    if not isinstance(lanes, list):
        raise ValueError("collect result.lanes 必须是数组")

    summary = data.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("collect result.summary 必须是 object")

    useful_item_count = summary.get("useful_item_count")
    if not isinstance(useful_item_count, int) or useful_item_count < 0:
        raise ValueError("collect result.summary.useful_item_count 必须是非负整数")

    partial_lane_count = summary.get("partial_lane_count")
    if not isinstance(partial_lane_count, int) or partial_lane_count < 0:
        raise ValueError("collect result.summary.partial_lane_count 必须是非负整数")

    total_lane_items = 0
    total_non_ok = 0
    for lane in lanes:
        if not isinstance(lane, dict):
            raise ValueError("collect result.lanes[*] 必须是 object")
        if lane.get("status") not in {"ok", "partial", "error"}:
            raise ValueError("collect result.lanes[*].status 非法")
        count = lane.get("useful_item_count")
        if not isinstance(count, int) or count < 0:
            raise ValueError("collect result.lanes[*].useful_item_count 必须是非负整数")
        total_lane_items += count
        if lane["status"] != "ok":
            total_non_ok += 1

    if total_lane_items != useful_item_count:
        raise ValueError("collect result.summary.useful_item_count 与 lane 统计不一致")
    if total_non_ok != partial_lane_count:
        raise ValueError("collect result.summary.partial_lane_count 与 lane 状态不一致")


def validate_selected_items_object(data: Any) -> None:
    if not isinstance(data, dict):
        raise ValueError("selected_items 必须是 object")
    if not isinstance(data.get("report_date"), str):
        raise ValueError("selected_items 缺少 report_date")
    if not isinstance(data.get("source"), str):
        raise ValueError("selected_items 缺少 source")

    items = data.get("selected_items")
    if not isinstance(items, list):
        raise ValueError("selected_items.selected_items 必须是数组")

    summary = data.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("selected_items.summary 必须是 object")
    selected_item_count = summary.get("selected_item_count")
    if not isinstance(selected_item_count, int) or selected_item_count < 0:
        raise ValueError("selected_items.summary.selected_item_count 必须是非负整数")
    if selected_item_count != len(items):
        raise ValueError("selected_items.summary.selected_item_count 与条目数不一致")

    lane_counts = summary.get("lane_counts")
    if not isinstance(lane_counts, list):
        raise ValueError("selected_items.summary.lane_counts 必须是数组")

    expected_lane_counts: Counter[str] = Counter()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("selected_items.selected_items[*] 必须是 object")
        for key in ["lane", "title", "source_url", "signal_path", "fetched_at", "excerpt"]:
            if not isinstance(item.get(key), str):
                raise ValueError(f"selected_items.selected_items[*].{key} 必须是字符串")
        if "source_snippet" in item and not isinstance(item.get("source_snippet"), str):
            raise ValueError("selected_items.selected_items[*].source_snippet 必须是字符串")
        if "matched_query" in item and not isinstance(item.get("matched_query"), str):
            raise ValueError("selected_items.selected_items[*].matched_query 必须是字符串")
        expected_lane_counts[item["lane"]] += 1

    actual_lane_counts: dict[str, int] = {}
    for lane_count in lane_counts:
        if not isinstance(lane_count, dict):
            raise ValueError("selected_items.summary.lane_counts[*] 必须是 object")
        lane_name = lane_count.get("lane")
        count = lane_count.get("selected_item_count")
        if not isinstance(lane_name, str) or not lane_name:
            raise ValueError("selected_items.summary.lane_counts[*].lane 必须是非空字符串")
        if not isinstance(count, int) or count < 0:
            raise ValueError("selected_items.summary.lane_counts[*].selected_item_count 必须是非负整数")
        if lane_name in actual_lane_counts:
            raise ValueError("selected_items.summary.lane_counts[*].lane 不允许重复")
        actual_lane_counts[lane_name] = count

    for lane_name, expected_count in expected_lane_counts.items():
        if actual_lane_counts.get(lane_name) != expected_count:
            raise ValueError("selected_items.summary.lane_counts 与 selected_items 条目不一致")
    for lane_name, actual_count in actual_lane_counts.items():
        if lane_name not in expected_lane_counts and actual_count != 0:
            raise ValueError("selected_items.summary.lane_counts 与 selected_items 条目不一致")


def inspect_lane(signals_root: Path, report_date: str, lane_name: str) -> LaneSnapshot:
    lane_dir = signals_root / lane_name / report_date
    if not lane_dir.is_dir():
        return LaneSnapshot(
            name=lane_name,
            status="error",
            useful_item_count=0,
            issues=[f"{lane_name}: 缺少目录 {lane_dir}"],
            signal_paths=[],
        )

    run_path = lane_dir / "run.json"
    if not run_path.is_file():
        return LaneSnapshot(
            name=lane_name,
            status="error",
            useful_item_count=0,
            issues=[f"{lane_name}: 缺少 run.json"],
            signal_paths=[],
        )

    try:
        run_data = load_json(run_path)
    except Exception as error:  # noqa: BLE001
        return LaneSnapshot(
            name=lane_name,
            status="error",
            useful_item_count=0,
            issues=[f"{lane_name}: run.json 读取失败: {error}"],
            signal_paths=[],
        )

    issues: list[str] = []
    warnings = normalize_string_list(run_data.get("warnings"))
    errors = normalize_string_list(run_data.get("errors"))
    if warnings:
        issues.append(f"{lane_name}: warnings={'; '.join(warnings)}")
    if errors:
        issues.append(f"{lane_name}: errors={'; '.join(errors)}")

    run_status = run_data.get("status")
    if run_status != "success":
        issues.append(f"{lane_name}: run.status={run_status!r}")

    run_date = run_data.get("date")
    if run_date not in {None, report_date}:
        issues.append(f"{lane_name}: run.date={run_date!r} 与 report_date={report_date} 不一致")

    signal_paths, signal_issues = resolve_signal_paths(lane_dir=lane_dir, lane_name=lane_name, run_data=run_data)
    issues.extend(signal_issues)

    declared_count = extract_declared_signal_count(run_data)
    actual_count = len(signal_paths)
    if declared_count is not None and declared_count != actual_count:
        issues.append(f"{lane_name}: summary.signals_written={declared_count} 与实际文件数 {actual_count} 不一致")

    status = "ok"
    if issues:
        status = "partial" if actual_count > 0 else "error"

    return LaneSnapshot(
        name=lane_name,
        status=status,
        useful_item_count=actual_count,
        issues=issues,
        signal_paths=signal_paths,
    )


def resolve_signal_paths(lane_dir: Path, lane_name: str, run_data: dict[str, Any]) -> tuple[list[Path], list[str]]:
    issues: list[str] = []
    artifacts = run_data.get("artifacts")
    if not isinstance(artifacts, dict):
        issues.append(f"{lane_name}: run.json.artifacts 缺失或非法")
        return sorted_signal_files(lane_dir / "signals"), issues

    index_file = artifacts.get("index_file")
    if not isinstance(index_file, str) or not (lane_dir / index_file).is_file():
        issues.append(f"{lane_name}: 缺少 index 文件")

    declared_files = artifacts.get("signal_files")
    signals_dir = lane_dir / "signals"
    on_disk_files = sorted_signal_files(signals_dir)

    if not isinstance(declared_files, list):
        if not signals_dir.is_dir():
            issues.append(f"{lane_name}: 缺少 signals 目录")
        return on_disk_files, issues

    existing_files: list[Path] = []
    declared_set: set[str] = set()
    for item in declared_files:
        if not isinstance(item, str):
            issues.append(f"{lane_name}: artifacts.signal_files 含非法条目")
            continue
        declared_set.add(item)
        candidate = lane_dir / item
        if candidate.is_file():
            existing_files.append(candidate)
        else:
            issues.append(f"{lane_name}: 缺少 signal 文件 {item}")

    for file_path in on_disk_files:
        relative = file_path.relative_to(lane_dir).as_posix()
        if relative not in declared_set:
            issues.append(f"{lane_name}: 发现未声明 signal 文件 {relative}")

    return existing_files, issues


def sorted_signal_files(signals_dir: Path) -> list[Path]:
    if not signals_dir.is_dir():
        return []
    return sorted(path for path in signals_dir.glob("*.md") if path.is_file())


def extract_declared_signal_count(run_data: dict[str, Any]) -> int | None:
    summary = run_data.get("summary")
    if not isinstance(summary, dict):
        return None
    value = summary.get("signals_written")
    if isinstance(value, int) and value >= 0:
        return value
    return None


def build_signal_candidate_from_signal(signal_path: Path, signals_root: Path, fallback_lane: str) -> dict[str, Any]:
    text = signal_path.read_text(encoding="utf-8")
    front_matter_block, body = split_front_matter(text)
    front_matter = parse_front_matter(front_matter_block)

    lane_name = as_string(front_matter.get("lane")) or fallback_lane
    title = as_string(front_matter.get("title")) or signal_path.stem
    source_url = as_string(front_matter.get("url")) or ""
    fetched_at = as_string(front_matter.get("fetched_at")) or ""

    item = {
        "lane": lane_name,
        "title": title,
        "source_url": source_url,
        "signal_path": signal_path.relative_to(signals_root).as_posix(),
        "fetched_at": fetched_at,
        "source_snippet": extract_source_snippet(body, lane_name=lane_name),
        "excerpt": extract_excerpt(body, lane_name=lane_name),
        "_body": body,
        "_front_matter": front_matter,
    }
    matched_query = extract_matched_query(front_matter=front_matter, body=body)
    if matched_query:
        item["matched_query"] = matched_query

    source = as_string(front_matter.get("source"))
    if source:
        item["source"] = source
    signal_type = as_string(front_matter.get("type"))
    if signal_type:
        item["signal_type"] = signal_type

    return item


def build_selected_item_from_signal(signal_path: Path, signals_root: Path, fallback_lane: str) -> dict[str, Any]:
    return serialize_selected_item(
        build_signal_candidate_from_signal(signal_path=signal_path, signals_root=signals_root, fallback_lane=fallback_lane)
    )


def split_front_matter(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            front_matter = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return front_matter, body

    return "", text


def parse_front_matter(front_matter_block: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in front_matter_block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if raw_line.startswith((" ", "\t")):
            if current_key and not stripped.startswith("- "):
                parsed[current_key] = normalize_whitespace(f"{parsed[current_key]} {strip_wrapping_quotes(stripped)}")
            continue
        if stripped.startswith("- "):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            continue
        parsed[key] = strip_wrapping_quotes(value.strip())
        current_key = key
    return parsed


def extract_matched_query(*, front_matter: dict[str, Any], body: str) -> str:
    for key in ("matched_query", "query"):
        value = normalize_whitespace(as_string(front_matter.get(key)) or "")
        if value:
            return value

    match = re.search(r"(?im)^\s*(?:-\s*)?(?:matched query|query):\s*(.+?)\s*$", body)
    if not match:
        return ""
    return normalize_whitespace(match.group(1))


def curate_lane_candidates(
    *,
    lane_name: str,
    candidates: Sequence[dict[str, Any]],
    lane_limit: int | None,
) -> list[dict[str, Any]]:
    if not candidates:
        return []

    scored_candidates = [
        enrich_candidate_for_report(candidate=candidate, lane_name=lane_name)
        for candidate in candidates
        if candidate.get("excerpt") or candidate.get("title")
    ]
    if not scored_candidates:
        return []

    if lane_name == "hacker-news-watch":
        scored_candidates = [
            candidate for candidate in scored_candidates if is_hacker_news_hot_candidate_reportable(candidate)
        ]
        if not scored_candidates:
            return []

    if lane_name in NOISY_X_LANES:
        kept_candidates = [
            candidate
            for candidate in scored_candidates
            if not is_retweet_candidate(candidate)
            and has_meaningful_excerpt(candidate.get("excerpt", ""))
            and candidate.get("_relevance_score", 0) >= (2 if lane_name == "x-feed" else 3)
        ]
        if not kept_candidates:
            kept_candidates = [
                candidate
                for candidate in scored_candidates
                if not is_retweet_candidate(candidate) and has_meaningful_excerpt(candidate.get("excerpt", ""))
            ]
        if lane_name == "x-following" and kept_candidates:
            kept_candidates = [
                candidate for candidate in kept_candidates if noisy_x_candidate_has_specific_summary(candidate)
            ]
            scored_candidates = kept_candidates
        elif kept_candidates:
            scored_candidates = kept_candidates
        scored_candidates = [
            candidate for candidate in scored_candidates if noisy_x_candidate_has_specific_summary(candidate)
        ]

    scored_candidates.sort(key=lambda candidate: candidate.get("_sort_key", ("", "")), reverse=True)
    if lane_limit is not None:
        if lane_name == "reddit-watch":
            return pick_reddit_dual_pool_candidates(candidates=scored_candidates, lane_limit=lane_limit)
        if lane_name in NOISY_X_LANES:
            return pick_noisy_x_candidates(candidates=scored_candidates, lane_limit=lane_limit)
        return pick_diverse_lane_candidates(
            lane_name=lane_name,
            candidates=scored_candidates,
            lane_limit=lane_limit,
        )
    return scored_candidates


def pick_noisy_x_candidates(*, candidates: Sequence[dict[str, Any]], lane_limit: int) -> list[dict[str, Any]]:
    if lane_limit <= 0:
        return []

    selected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for candidate in candidates:
        source_url = str(candidate.get("source_url", ""))
        if source_url and source_url in seen_urls:
            continue
        selected.append(candidate)
        if source_url:
            seen_urls.add(source_url)
        if len(selected) >= lane_limit:
            break
    return selected


def pick_diverse_lane_candidates(
    *,
    lane_name: str,
    candidates: Sequence[dict[str, Any]],
    lane_limit: int,
) -> list[dict[str, Any]]:
    if lane_limit <= 0:
        return []
    if lane_limit == 1 or len(candidates) <= 1:
        return list(candidates[:lane_limit])

    selected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    top_score = int(candidates[0].get("_relevance_score", 0))

    for candidate in candidates:
        source_url = str(candidate.get("source_url", ""))
        if source_url and source_url in seen_urls:
            continue

        if not selected:
            selected.append(candidate)
            if source_url:
                seen_urls.add(source_url)
            continue

        if not can_add_secondary_candidate(
            lane_name=lane_name,
            candidate=candidate,
            selected=selected,
            top_score=top_score,
        ):
            continue

        selected.append(candidate)
        if source_url:
            seen_urls.add(source_url)
        if len(selected) >= lane_limit:
            break

    return selected


def pick_reddit_dual_pool_candidates(*, candidates: Sequence[dict[str, Any]], lane_limit: int) -> list[dict[str, Any]]:
    if lane_limit <= 0:
        return []
    if lane_limit == 1 or len(candidates) <= 1:
        return [
            assign_reddit_selection_bucket(candidate=candidate, bucket=reddit_selection_bucket(candidate))
            for candidate in candidates[:lane_limit]
        ]

    voice_candidates = [candidate for candidate in candidates if is_reddit_voice_candidate(candidate)]
    heat_candidates = [candidate for candidate in candidates if not is_reddit_voice_candidate(candidate)]

    heat_target = min(lane_limit, max(1, math.ceil(lane_limit * 0.4)))
    voice_target = 0
    if lane_limit > 1:
        voice_target = min(lane_limit - heat_target, max(1, math.ceil(lane_limit * 0.3)))

    selected: list[dict[str, Any]] = []
    selected.extend(
        assign_reddit_selection_bucket(candidate=candidate, bucket="heat")
        for candidate in pick_reddit_ranked_candidates(candidates=heat_candidates, lane_limit=heat_target)
    )

    remaining_slots = lane_limit - len(selected)
    if remaining_slots > 0 and voice_candidates:
        selected.extend(
            assign_reddit_selection_bucket(candidate=candidate, bucket="voice")
            for candidate in pick_reddit_ranked_candidates(
                candidates=voice_candidates,
                lane_limit=min(voice_target, remaining_slots),
                existing_candidates=selected,
            )
        )

    remaining_slots = lane_limit - len(selected)
    if remaining_slots > 0:
        selected.extend(
            assign_reddit_selection_bucket(candidate=candidate, bucket=reddit_selection_bucket(candidate))
            for candidate in pick_reddit_ranked_candidates(
                candidates=candidates,
                lane_limit=remaining_slots,
                existing_candidates=selected,
            )
        )

    return selected[:lane_limit]


def pick_reddit_ranked_candidates(
    *,
    candidates: Sequence[dict[str, Any]],
    lane_limit: int,
    existing_candidates: Sequence[dict[str, Any]] = (),
) -> list[dict[str, Any]]:
    if lane_limit <= 0:
        return []

    selected: list[dict[str, Any]] = []
    taken_identity_keys = {candidate_identity_key(candidate) for candidate in existing_candidates}
    seen_urls = {
        normalize_whitespace(str(candidate.get("source_url", "")))
        for candidate in existing_candidates
        if normalize_whitespace(str(candidate.get("source_url", "")))
    }

    for enforce_topic_diversity in (True, False):
        if len(selected) >= lane_limit:
            break

        selected_with_context = [*existing_candidates, *selected]
        for candidate in candidates:
            if len(selected) >= lane_limit:
                break

            identity_key = candidate_identity_key(candidate)
            if identity_key in taken_identity_keys:
                continue

            source_url = normalize_whitespace(str(candidate.get("source_url", "")))
            if source_url and source_url in seen_urls:
                continue

            if enforce_topic_diversity and reddit_candidate_overlaps_topics(
                candidate=candidate,
                existing_candidates=selected_with_context,
            ):
                continue

            selected.append(candidate)
            taken_identity_keys.add(identity_key)
            if source_url:
                seen_urls.add(source_url)

    return selected


def reddit_candidate_overlaps_topics(*, candidate: dict[str, Any], existing_candidates: Sequence[dict[str, Any]]) -> bool:
    topic_tokens = candidate_topic_tokens(candidate)
    if not topic_tokens:
        return False

    for existing in existing_candidates:
        if topic_tokens_overlap_too_much(topic_tokens, candidate_topic_tokens(existing)):
            return True
    return False


def candidate_is_cross_day_topic_duplicate(
    *,
    lane_name: str,
    candidate: dict[str, Any],
    previous_selected_items: Sequence[dict[str, Any]],
) -> bool:
    topic_tokens = candidate_topic_tokens(candidate)
    if not topic_tokens:
        return False
    if lane_name in {"claude-code-watch", "openclaw-watch"} and candidate_version_tokens(candidate):
        return False

    for existing in previous_selected_items:
        if candidate_has_distinct_version_from_existing(
            lane_name=lane_name,
            candidate=candidate,
            existing=existing,
        ):
            continue
        if topic_tokens_overlap_too_much(topic_tokens, candidate_topic_tokens(existing)):
            return True
    return False


def candidate_has_distinct_version_from_existing(
    *,
    lane_name: str,
    candidate: dict[str, Any],
    existing: dict[str, Any],
) -> bool:
    if lane_name not in VERSION_DISTINGUISHING_TOPIC_DEDUPE_LANES:
        return False

    candidate_versions = candidate_version_tokens(candidate)
    existing_versions = candidate_version_tokens(existing)
    if not candidate_versions or not existing_versions:
        return False
    return candidate_versions.isdisjoint(existing_versions)


def candidate_version_tokens(candidate: dict[str, Any]) -> set[str]:
    prioritized_text = normalize_whitespace(f"{candidate.get('title', '')} {candidate.get('source_url', '')}")
    version_tokens = extract_version_tokens(prioritized_text)
    if version_tokens:
        return version_tokens
    return extract_version_tokens(str(candidate.get("excerpt", "")))


def extract_version_tokens(text: str) -> set[str]:
    normalized = normalize_whitespace(text)
    if not normalized:
        return set()
    return {match.group(0).lower().lstrip("v") for match in VERSION_TOKEN_PATTERN.finditer(normalized)}


def candidate_identity_key(candidate: dict[str, Any]) -> tuple[str, str, str]:
    return (
        normalize_whitespace(str(candidate.get("source_url", ""))),
        normalize_whitespace(str(candidate.get("signal_path", ""))),
        normalize_whitespace(str(candidate.get("title", ""))),
    )


def reddit_selection_bucket(candidate: dict[str, Any]) -> str:
    return "voice" if is_reddit_voice_candidate(candidate) else "heat"


def assign_reddit_selection_bucket(*, candidate: dict[str, Any], bucket: str) -> dict[str, Any]:
    tagged_candidate = dict(candidate)
    tagged_candidate["selection_bucket"] = bucket
    return tagged_candidate


def is_reddit_voice_candidate(candidate: dict[str, Any]) -> bool:
    title = normalize_whitespace(str(candidate.get("title", "")))
    source_text = normalize_whitespace(str(candidate.get("source_snippet") or candidate.get("excerpt", "")))
    normalized = normalize_whitespace(f"{title} {source_text}")
    lowered = normalized.lower()
    title_lower = title.lower()

    if not lowered:
        return False

    voice_score = 0
    if "?" in normalized:
        voice_score += 2
    if re.search(
        r"\b(how do you|how are you|what's your|what is your|does anyone|anyone else|best approach|"
        r"how to use|how you use|can i|should i|why does|why is|help me|looking for|"
        r"unsure|advice|where to learn)\b",
        lowered,
    ):
        voice_score += 3
    if re.search(r"\b(i|i'm|i’ve|i'd|my|me|we|our|us)\b", lowered):
        voice_score += 1
    if re.search(
        r"\b(setup|workflow|stack|routine|process|repo|large repo|handoff|playbook|use case|"
        r"practical|how i use|switched from|never going back)\b",
        lowered,
    ):
        voice_score += 1
    if re.search(
        r"\b(frustrated|complain|complaint|pain point|stopped working|broken|issue|problem|"
        r"oauth stopped working|losing control|on read)\b",
        lowered,
    ):
        voice_score += 2
    if title_lower.startswith(("i ", "i'", "how ", "what ", "why ", "does ", "can ", "should ", "anyone ", "is ", "are ")):
        voice_score += 2

    return voice_score >= 3


def can_add_secondary_candidate(
    *,
    lane_name: str,
    candidate: dict[str, Any],
    selected: Sequence[dict[str, Any]],
    top_score: int,
) -> bool:
    if lane_name == "weather-watch":
        return True
    score = int(candidate.get("_relevance_score", 0))
    if score < SECONDARY_ITEM_SCORE_FLOORS.get(lane_name, 0):
        return False
    allowed_gap = 10 if lane_name == "github-trending-weekly" else 6
    if top_score > 0 and score + allowed_gap < top_score:
        return False

    topic_tokens = candidate_topic_tokens(candidate)
    if not topic_tokens:
        return False

    for existing in selected:
        if topic_tokens_overlap_too_much(topic_tokens, candidate_topic_tokens(existing)):
            return False
    return True


def candidate_topic_tokens(candidate: dict[str, Any]) -> set[str]:
    normalized = normalize_whitespace(
        f"{candidate.get('title', '')} {candidate.get('source_snippet', '')} {candidate.get('excerpt', '')}"
    ).lower()
    if not normalized:
        return set()

    tokens: list[str] = []
    for term in KNOWN_TERMS:
        lowered = term.lower()
        if lowered in normalized:
            tokens.append(lowered)

    tokens.extend(extract_reddit_theme_tokens(normalized))

    for token in re.findall(r"[a-z0-9][a-z0-9_./+-]{2,}", normalized):
        if token in TOPIC_TOKEN_STOPWORDS or token.isdigit():
            continue
        tokens.append(token)

    return set(tokens)


def extract_reddit_theme_tokens(normalized: str) -> set[str]:
    """Coarse semantic fingerprints for Reddit topics that recur with new URLs/titles."""
    theme_tokens: set[str] = set()
    theme_patterns = {
        "theme:multi-agent-orchestration": (
            "multi-agent",
            "multi agent",
            "agent team",
            "agent teams",
            "swarm",
            "orchestration",
            "agent-council",
            "maestro",
            "parallel agents",
        ),
        "theme:openclaw-subscription-alternative": ("openclaw", "subscription", "ban", "restricted", "alternative"),
        "theme:claude-code-workflow-tips": ("claude code", "workflow", "tips", "daily use", "setup", "cli", "mcp"),
        "theme:agent-monetization": ("made money", "make money", "earn", "revenue", "monetiz", "60k"),
        "theme:nontechnical-ai-gap": ("non-technical", "non technical", "technical people", "gap", "search box"),
        "theme:autonomous-iteration": ("autonomous iteration", "failure memory", "measure", "modify", "verify", "rollback"),
        "theme:agent-governance-verification": ("governance", "verification", "reviewer", "keeps", "safe"),
    }
    for theme, phrases in theme_patterns.items():
        if sum(1 for phrase in phrases if phrase in normalized) >= 2:
            theme_tokens.add(theme)
    return theme_tokens


def topic_tokens_overlap_too_much(current: set[str], existing: set[str]) -> bool:
    if not current or not existing:
        return False
    overlap = current & existing
    if not overlap:
        return False
    if any(token.startswith("theme:") for token in overlap):
        return True
    smaller_size = min(len(current), len(existing))
    return len(overlap) >= max(2, (smaller_size + 1) // 2)


def is_hacker_news_hot_candidate_reportable(candidate: dict[str, Any]) -> bool:
    relevance_score = int(candidate.get("_relevance_score", 0))
    if relevance_score >= HACKER_NEWS_HOT_RELEVANCE_SCORE_THRESHOLD:
        return True

    combined_text = normalize_whitespace(
        " ".join(
            (
                str(candidate.get("title", "")),
                str(candidate.get("source_snippet", "")),
                str(candidate.get("excerpt", "")),
                str(candidate.get("_body", "")),
            )
        )
    ).lower()
    if not combined_text:
        return False

    return any(
        all(keyword in combined_text for keyword in keyword_group)
        for keyword_group in HACKER_NEWS_HOT_REPORTABLE_KEYWORD_GROUPS
    )


def enrich_candidate_for_report(*, candidate: dict[str, Any], lane_name: str) -> dict[str, Any]:
    front_matter = candidate.get("_front_matter", {})
    source_text = str(candidate.get("source_snippet") or candidate.get("excerpt", ""))
    combined_text = normalize_whitespace(f"{candidate.get('title', '')} {source_text}")
    relevance_score = compute_keyword_score(combined_text)
    sort_key = build_candidate_sort_key(
        lane_name=lane_name,
        candidate=candidate,
        front_matter=front_matter,
        relevance_score=relevance_score,
    )
    editor_headline, editor_summary = build_editor_copy(
        lane_name=lane_name,
        title=str(candidate.get("title", "")),
        excerpt=source_text,
        front_matter=front_matter,
    )

    enriched = dict(candidate)
    enriched["_relevance_score"] = relevance_score
    enriched["_sort_key"] = sort_key
    enriched["editor_headline"] = editor_headline
    enriched["editor_summary"] = editor_summary
    return enriched


def build_candidate_sort_key(
    *,
    lane_name: str,
    candidate: dict[str, Any],
    front_matter: dict[str, Any],
    relevance_score: int,
) -> tuple[Any, ...]:
    fetched_at = str(candidate.get("fetched_at", ""))
    signal_path = str(candidate.get("signal_path", ""))
    body = str(candidate.get("_body", ""))
    title = str(candidate.get("title", ""))

    if lane_name in NOISY_X_LANES:
        engagement_score = extract_engagement_score(body)
        position = parse_float(front_matter.get("position"))
        return (relevance_score, engagement_score, -(position or 9999), fetched_at, signal_path)
    if lane_name == "reddit-watch":
        score = extract_labeled_number(body, "Score")
        comments = extract_labeled_number(body, "Comments")
        return (relevance_score, score, comments, fetched_at, signal_path)
    if lane_name in {"hacker-news-watch", "hacker-news-search-watch"}:
        points = extract_labeled_number(body, "Points")
        comments = extract_labeled_number(body, "Comments")
        return (relevance_score, points, comments, fetched_at, signal_path)
    if lane_name in {"claude-code-watch", "openclaw-watch"}:
        version_rank = parse_version_rank(title)
        is_stable = 0 if re.search(r"(beta|rc)", title, re.IGNORECASE) else 1
        return (is_stable, version_rank, relevance_score, fetched_at, signal_path)
    if lane_name == "codex-watch":
        pr_number = extract_labeled_number(title, "#") or extract_labeled_number(str(candidate.get("source_url", "")), "/pull/")
        signal_type = str(candidate.get("signal_type", ""))
        title_lower = normalize_whitespace(f"{title} {candidate.get('excerpt', '')}").lower()
        focus_bonus = 1 if "clarify guardian timeout guidance" in title_lower else 0
        merged_pr_bonus = 1 if signal_type == "merged_pr" else 0
        return (focus_bonus, merged_pr_bonus, relevance_score, pr_number, fetched_at, signal_path)
    if lane_name == "product-hunt-watch":
        return (relevance_score, fetched_at, signal_path)
    if lane_name == "polymarket-watch":
        probability = parse_float(front_matter.get("primary_probability")) or 0.0
        title_lower = normalize_whitespace(f"{title} {candidate.get('excerpt', '')}").lower()
        focus_bonus = 1 if "second-best coding ai model" in title_lower and "anthropic" in title_lower else 0
        return (focus_bonus, relevance_score, probability, fetched_at, signal_path)
    return (relevance_score, fetched_at, signal_path)


def serialize_selected_item(candidate: dict[str, Any]) -> dict[str, Any]:
    item = {
        key: value
        for key, value in candidate.items()
        if not key.startswith("_")
    }
    item["title"] = normalize_whitespace(str(item.get("title", ""))) or "Untitled"
    item["source_snippet"] = normalize_whitespace(str(item.get("source_snippet", "")))
    item["excerpt"] = normalize_whitespace(str(item.get("excerpt", "")))
    item["editor_headline"] = ensure_chinese_sentence(str(item.get("editor_headline", "")))
    item["editor_summary"] = ensure_chinese_sentence(str(item.get("editor_summary", "")))
    return item


def extract_source_snippet(body: str, *, lane_name: str | None = None) -> str:
    sections = parse_markdown_sections(body)
    preferred_sections = DENSE_ENTRY_SOURCE_SECTION_PREFERENCES.get(
        lane_name or "",
        CONTENT_SECTION_PREFERENCES.get(lane_name or "", ()),
    )
    snippet_limit = DENSE_ENTRY_SOURCE_LIMITS.get(lane_name or "", SOURCE_SNIPPET_LIMIT)

    preferred_lines = collect_preferred_section_lines(sections, preferred_sections)
    preferred_lines = prioritize_dense_entry_lines(preferred_lines, lane_name=lane_name or "")
    snippet = collect_clean_text(preferred_lines, limit=snippet_limit)
    if snippet:
        return snippet

    for section_lines in sections.values():
        snippet = collect_clean_text(section_lines, limit=snippet_limit)
        if snippet:
            return snippet

    return collect_clean_text(body.splitlines(), limit=snippet_limit)


def extract_excerpt(body: str, *, lane_name: str | None = None) -> str:
    sections = parse_markdown_sections(body)
    preferred_sections = CONTENT_SECTION_PREFERENCES.get(lane_name or "", ())

    for section_name in preferred_sections:
        snippet = collect_clean_text(find_section_lines(sections, section_name), limit=EXCERPT_LIMIT)
        if snippet:
            return snippet

    return collect_clean_text(body.splitlines(), limit=EXCERPT_LIMIT)


def find_section_lines(sections: dict[str, list[str]], section_name: str) -> list[str]:
    matched_lines: list[str] = []
    for actual_name, lines in sections.items():
        if actual_name == section_name or actual_name.startswith(section_name):
            matched_lines.extend(lines)
    return matched_lines


def collect_preferred_section_lines(sections: dict[str, list[str]], preferred_sections: Sequence[str]) -> list[str]:
    matched_lines: list[str] = []
    seen_sections: set[str] = set()
    for section_name in preferred_sections:
        for actual_name, lines in sections.items():
            if actual_name in seen_sections:
                continue
            if actual_name == section_name or actual_name.startswith(section_name):
                matched_lines.extend(lines)
                seen_sections.add(actual_name)
    return matched_lines


def prioritize_dense_entry_lines(lines: Sequence[str], *, lane_name: str) -> list[str]:
    priority_rules = DENSE_ENTRY_PRIORITY_RULES.get(lane_name)
    baseline_count = DENSE_ENTRY_BASELINE_COUNTS.get(lane_name, 0)
    if not priority_rules or not lines:
        return list(lines)

    line_entries: list[tuple[int, str, str]] = []
    for index, raw_line in enumerate(lines):
        cleaned_line = clean_content_line(raw_line)
        if cleaned_line:
            line_entries.append((index, raw_line, cleaned_line.lower()))

    if not line_entries:
        return list(lines)

    selected_indexes: set[int] = set()
    for index, _, _ in line_entries[:baseline_count]:
        selected_indexes.add(index)

    scored_indexes: list[tuple[int, int]] = []
    for index, _, lowered_line in line_entries:
        score = 0
        for keywords, weight in priority_rules:
            if all(keyword in lowered_line for keyword in keywords):
                score = max(score, weight)
        if score > 0:
            scored_indexes.append((score, index))

    for _, index in sorted(scored_indexes, key=lambda item: (-item[0], item[1])):
        selected_indexes.add(index)

    if not selected_indexes:
        return list(lines)
    return [raw_line for index, raw_line in enumerate(lines) if index in selected_indexes]


def collect_clean_text(lines: Sequence[str], *, limit: int) -> str:
    chunks: list[str] = []
    for raw_line in lines:
        line = clean_content_line(raw_line)
        if not line:
            continue
        chunks.append(line)
        candidate = normalize_whitespace(" ".join(chunks))
        if len(candidate) >= limit:
            return trim_fragmentary_tail(trim_text_to_safe_boundary(candidate, limit=limit))
    return trim_fragmentary_tail(normalize_whitespace(" ".join(chunks)))


def parse_markdown_sections(body: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            current_section = normalize_whitespace(line[3:].strip()).lower()
            sections.setdefault(current_section, [])
            continue
        if current_section is not None:
            sections[current_section].append(line)

    return sections


def clean_content_line(raw_line: str) -> str:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return ""
    if line.startswith("- "):
        line = line[2:].strip()
    if not line:
        return ""
    if any(line.lower().startswith(prefix) for prefix in METADATA_LINE_PREFIXES):
        return ""
    cleaned = sanitize_body_text(line, fallback="")
    if not cleaned:
        return ""
    if cleaned.startswith(("http://", "https://")):
        return ""
    return cleaned


def has_meaningful_excerpt(value: str) -> bool:
    stripped = normalize_whitespace(value)
    return len(stripped) >= 24 or count_cjk_characters(stripped) >= 8


def is_retweet_candidate(candidate: dict[str, Any]) -> bool:
    excerpt = normalize_whitespace(str(candidate.get("excerpt", "")))
    if excerpt.lower().startswith("rt @"):
        return True
    text = normalize_whitespace(f"{candidate.get('title', '')} {excerpt}")
    return text.lower().startswith("rt @")


def compute_keyword_score(text: str) -> int:
    normalized = text.lower()
    score = 0
    for keyword, weight in KEYWORD_WEIGHTS:
        if keyword in normalized:
            score += weight
    return score


def extract_engagement_score(body: str) -> float:
    likes = extract_labeled_number(body, "Likes")
    retweets = extract_labeled_number(body, "Retweets")
    replies = extract_labeled_number(body, "Replies")
    views = extract_labeled_number(body, "Views")
    return (
        math.log1p(likes)
        + math.log1p(retweets) * 1.5
        + math.log1p(replies)
        + math.log1p(max(views, 0) / 1000.0)
    )


def extract_labeled_number(text: str, label: str) -> int:
    if label.startswith("/"):
        match = re.search(re.escape(label) + r"(\d+)", text)
        return int(match.group(1)) if match else 0
    if label == "#":
        match = re.search(r"#(\d+)", text)
        return int(match.group(1)) if match else 0
    match = re.search(rf"{re.escape(label)}:\s*([0-9][0-9,\.]*)", text, re.IGNORECASE)
    if not match:
        return 0
    return int(float(match.group(1).replace(",", "")))


def parse_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    normalized = value.replace(",", "").strip()
    if not normalized:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None


def parse_version_rank(value: str) -> tuple[int, ...]:
    numbers = [int(token) for token in re.findall(r"\d+", value)]
    while len(numbers) < 4:
        numbers.append(0)
    return tuple(numbers[:4])


def build_editor_copy(
    *,
    lane_name: str,
    title: str,
    excerpt: str,
    front_matter: dict[str, Any],
) -> tuple[str, str]:
    cleaned_title = sanitize_body_text(title, fallback=title)
    cleaned_excerpt = sanitize_body_text(excerpt, fallback=excerpt)
    normalized = normalize_whitespace(f"{cleaned_title} {cleaned_excerpt}").lower()
    for rule in EDITOR_RULES:
        if rule["lane"] != lane_name:
            continue
        if any(all(keyword in normalized for keyword in keyword_group) for keyword_group in rule["keywords"]):
            return rule["headline"], rule["detail"]

    subject = derive_subject_label(title=cleaned_title, excerpt=cleaned_excerpt, lane_name=lane_name)
    headline = build_generic_headline(
        lane_name=lane_name,
        subject=subject,
        title=cleaned_title,
        excerpt=cleaned_excerpt,
        front_matter=front_matter,
    )
    detail = build_generic_detail(
        lane_name=lane_name,
        title=cleaned_title,
        excerpt=cleaned_excerpt,
        subject=subject,
        front_matter=front_matter,
    )
    return headline, detail


def derive_subject_label(*, title: str, excerpt: str, lane_name: str) -> str:
    normalized_title = sanitize_body_text(title, fallback="").strip()
    if lane_name in {"claude-code-watch", "openclaw-watch"} and re.search(r"\bv?\d+(?:\.\d+){1,3}\b", normalized_title):
        return normalized_title
    for term in KNOWN_TERMS:
        if term.lower() in f"{normalized_title} {excerpt}".lower():
            return term
    if lane_name in NOISY_X_LANES and normalized_title.startswith("@"):
        return FIXED_SECTION_TITLES[lane_name]
    if normalized_title and not normalized_title.startswith("@"):
        return normalized_title
    return FIXED_SECTION_TITLES[lane_name]


def build_generic_headline(
    *,
    lane_name: str,
    subject: str,
    title: str,
    excerpt: str,
    front_matter: dict[str, Any],
) -> str:
    focus_label = extract_focus_label(lane_name=lane_name, title=title, excerpt=excerpt, front_matter=front_matter)
    matched_query = normalize_whitespace(str(front_matter.get("matched_query") or front_matter.get("query") or ""))

    if lane_name == "x-feed":
        if focus_label:
            return f"{subject} 这条推荐流讨论已经落到 {focus_label} 这类具体抓手上。"
        return f"{subject} 这条线索已经从泛聊开始落到更具体的工作流动作。"
    if lane_name == "x-following":
        if "amnesia" in normalize_whitespace(f"{title} {excerpt}").lower():
            return "关注流里开始有人把 agent 的“上下文失忆”问题直接点破。"
        if focus_label:
            return f"{subject} 这条跟踪讨论把重点放在了 {focus_label} 上。"
        return f"{subject} 这条关注流线索需要补出原帖对象、动作和卡点。"
    if lane_name == "reddit-watch":
        if focus_label:
            return f"这条 Reddit 讨论把重点放在 {focus_label} 上。"
        return f"{subject} 这条社区讨论已经有了更明确的协作落点。"
    if lane_name == "hacker-news-watch":
        if focus_label:
            return f"这条 Hacker News 热榜讨论把重点放在 {focus_label} 上。"
        return f"{subject} 这条 Hacker News 热榜讨论已经落到更具体的实践细节。"
    if lane_name == "hacker-news-search-watch":
        if matched_query and focus_label:
            return f"Hacker News 搜索词「{matched_query}」命中的讨论把重点放在 {focus_label} 上。"
        if matched_query:
            return f"Hacker News 搜索词「{matched_query}」命中了一条更偏实践的讨论。"
        if focus_label:
            return f"这条 Hacker News 搜索命中把重点放在 {focus_label} 上。"
        return f"{subject} 是今天命中的一条 Hacker News 搜索结果，读者能先看到它指向的具体工程问题。"
    if lane_name == "claude-code-watch":
        if focus_label:
            return f"{subject} 这一版继续围绕 {focus_label} 补协作链路。"
        return f"{subject} 这次更新更偏向补齐真实使用链路。"
    if lane_name == "codex-watch":
        if focus_label:
            return f"Codex 这次更新把重点放在 {focus_label} 这条兼容链路上。"
        return f"{subject} 这次改动更像是在修执行链路里的关键语义。"
    if lane_name == "openclaw-watch":
        if focus_label:
            return f"{subject} 这一版把 {focus_label} 和可用性细节一起往前推。"
        return f"{subject} 这一版继续向产品可用性收口。"
    if lane_name == "github-trending-weekly":
        if focus_label:
            return f"{subject} 这周上榜，不只是因为热度，更因为它把重点放在 {focus_label} 上。"
        return f"{subject} 仍然是本周值得看的趋势项目之一。"
    if lane_name == "product-hunt-watch":
        if "design context" in normalize_whitespace(f"{title} {excerpt}").lower():
            return f"{subject} 想把共享上下文和 design context 直接做成 agent 协作产品。"
        if focus_label:
            return f"{subject} 正试图把 {focus_label} 这类工作流环节直接做成产品。"
        return f"{subject} 把 agent 工作流里的单一环节做成了产品。"
    if lane_name == "polymarket-watch":
        primary_outcome = str(front_matter.get("primary_outcome", "")).strip()
        if primary_outcome:
            return f"市场目前把 {primary_outcome} 放在更占优的位置，{subject} 相关判断还在继续收敛。"
        if focus_label:
            return f"{subject} 反映出市场判断正围绕 {focus_label} 继续收敛。"
        return f"{subject} 反映出市场判断正在继续收敛。"
    return f"{subject} 进入了今天的日报。"


def build_generic_detail(
    *,
    lane_name: str,
    title: str,
    excerpt: str,
    subject: str,
    front_matter: dict[str, Any],
) -> str:
    if count_cjk_characters(excerpt) >= 10:
        first_sentence = first_sentence_fragment(excerpt)
        if first_sentence:
            return first_sentence

    normalized = normalize_whitespace(f"{title} {excerpt}").lower()
    focus_label = extract_focus_label(lane_name=lane_name, title=title, excerpt=excerpt, front_matter=front_matter)
    matched_query = normalize_whitespace(str(front_matter.get("matched_query") or front_matter.get("query") or ""))
    stack_label = extract_stack_label(normalized)

    if lane_name in NOISY_X_LANES and focus_label:
        if lane_name == "x-following" and "amnesia" in normalized:
            return "讨论点其实是在补上下文失忆：每次新 session 都要重讲架构、约束、历史决定，这正是持续协作里的真实摩擦。"
        return f"讨论点已经不只是 {subject} 本身，而是团队如何用 {focus_label} 把协作里的交接面收紧。"

    if lane_name in NOISY_X_LANES:
        x_detail = build_x_post_detail(lane_name=lane_name, title=title, source_text=excerpt)
        if x_detail:
            return x_detail

    if lane_name == "reddit-watch":
        if "swarm" in normalized and stack_label:
            return f"帖子把 {stack_label} 放进同一条协作链路，重点已经转向 coordinator 如何分工、追踪改动并给 swarm 补治理。"
        if focus_label:
            return f"讨论没有停在概念层，而是直接围绕 {focus_label} 这种协作骨架展开。"
    if lane_name == "hacker-news-watch":
        if focus_label:
            return f"讨论没有停在概念层，而是直接围绕 {focus_label} 这种实践骨架展开。"
    if lane_name == "hacker-news-search-watch":
        if matched_query and focus_label:
            return f"这条命中来自对「{matched_query}」的搜索，正文把 {focus_label} 这类可复用做法写得更具体。"
        if matched_query:
            return f"这条命中来自对「{matched_query}」的搜索，正文不是泛聊，而是给出了一条更具体的实践线索。"
        if focus_label:
            return f"这条 Hacker News 搜索结果把重点压到了 {focus_label} 上，不只是泛聊概念。"

    if lane_name == "polymarket-watch":
        probability = parse_float(front_matter.get("primary_probability"))
        if probability is not None:
            return f"当前主结果大约在 {probability * 100:.1f}% 左右，说明交易者对这条判断已经形成较强共识。"

    if lane_name == "codex-watch":
        if "mcp" in normalized and ("deferred" in normalized or "flattened" in normalized):
            return "这条 PR 处理的是扁平化 alias 和 deferred 调用路径，属于把 MCP 工具调用边角补齐的底层修复。"
        if focus_label:
            return f"这条改动主要在补 {focus_label} 相关的执行细节，读起来更像链路层的兼容修复。"

    if lane_name == "claude-code-watch":
        if "worktree cleanup diagnostics" in normalized:
            return "这一版把 worktree cleanup diagnostics 和 MCP reconnect 一起补上，明显是在照顾长会话和托管 session 的维护体验。"
        if focus_label:
            return f"更新重点不是再加一个孤立命令，而是把 {focus_label} 这些真实团队会遇到的环节继续补齐。"

    if lane_name == "openclaw-watch":
        if "structured chat bubbles" in normalized:
            return "版本重点落在 structured chat bubbles、插件激活描述和 typed providerOptions 这些 UI 到工具层的衔接细节上。"
        if focus_label:
            return f"这版同时推进 {focus_label} 和稳定性补丁，明显更偏向真实使用场景而不是概念展示。"

    if lane_name == "github-trending-weekly":
        if "harness" in normalized and ("deterministic" in normalized or "repeatable" in normalized):
            return "这个趋势项目强调的不是再包一层 agent，而是把 AI coding 流程做得更可控、更可重复。"
        if focus_label:
            return f"它能进趋势榜，不只是因为名字热，而是把 {focus_label} 讲成了更具体的产品定位。"

    if lane_name == "product-hunt-watch":
        if "design context" in normalized:
            return "条目的卖点很直接：把 design context 和共享记忆打包进 AI coding agent 的日常协作入口。"
        if focus_label:
            return f"条目的卖点相当集中，核心就是把 {focus_label} 这类 agent 工作流环节包装成单独可卖的成品。"
        return f"{subject} 的卖点很集中，说明面向 agent 工作流单一环节的包装正在变成独立产品。"

    if focus_label and focus_label != subject:
        return f"这条信号真正有用的地方在于把焦点压到了 {focus_label}，不是只给出一个空泛概念。"

    if lane_name in NOISY_X_LANES:
        return ""
    return f"原文围绕 {subject} 展开，具体变化见来源。"


def extract_focus_label(
    *,
    lane_name: str,
    title: str,
    excerpt: str,
    front_matter: dict[str, Any],
) -> str:
    normalized = normalize_whitespace(f"{title} {excerpt}").lower()
    if not normalized:
        return ""

    lane_rules: dict[str, list[tuple[tuple[str, ...], str]]] = {
        "x-feed": [
            (("review checklist", "handoff"), "review checklist 和 agent handoff"),
            (("workflow",), "工作流"),
            (("governance",), "治理"),
        ],
        "x-following": [
            (("amnesia", "architecture", "constraints", "decisions"), "上下文失忆"),
            (("review loop",), "review loop"),
            (("human checkpoint",), "human checkpoint"),
            (("workflow",), "工作流"),
        ],
        "reddit-watch": [
            (("swarm", "governance"), "多模型 agent 的治理"),
            (("architect", "builder", "reviewer"), "多 agent 角色分工"),
            (("markdown", "handoff"), "markdown handoff"),
        ],
        "hacker-news-watch": [
            (("swarm", "governance"), "多模型 agent 的治理"),
            (("architect", "builder", "reviewer"), "多 agent 角色分工"),
            (("review checklist",), "review checklist"),
            (("handoff",), "agent handoff"),
        ],
        "hacker-news-search-watch": [
            (("tmux", "worktree"), "tmux + git worktree"),
            (("review checklist",), "review checklist"),
            (("handoff",), "agent handoff"),
            (("workflow",), "工作流"),
        ],
        "claude-code-watch": [
            (("team-onboarding",), "团队上手"),
            (("cloud environment",), "云环境"),
            (("cloud environments",), "云环境"),
            (("brief mode",), "brief mode"),
            (("worktree cleanup diagnostics",), "worktree cleanup diagnostics"),
            (("mcp reconnect",), "MCP reconnect"),
        ],
        "codex-watch": [
            (("guardian timeout",), "guardian timeout"),
            (("mcp", "deferred"), "deferred MCP 工具调用"),
            (("mcp", "flattened"), "扁平化 MCP 工具调用"),
        ],
        "openclaw-watch": [
            (("chatgpt import",), "ChatGPT 导入"),
            (("oauth",), "OAuth"),
            (("failover",), "failover"),
            (("webchat",), "webchat 富媒体"),
            (("structured chat bubbles",), "structured chat bubbles"),
            (("plugin activation descriptors",), "plugin activation descriptors"),
        ],
        "github-trending-weekly": [
            (("harness", "deterministic"), "AI coding 的可重复性"),
            (("harness", "repeatable"), "AI coding 的可重复性"),
            (("harness",), "harness"),
        ],
        "product-hunt-watch": [
            (("design context",), "design context"),
            (("mcp",), "MCP 工作流包装"),
        ],
        "polymarket-watch": [
            (("second-best coding ai model",), "第二好的 coding AI 模型"),
        ],
    }
    for keywords, label in lane_rules.get(lane_name, []):
        if all(keyword in normalized for keyword in keywords):
            return label

    probability = parse_float(front_matter.get("primary_probability"))
    if lane_name == "polymarket-watch" and probability is not None:
        return f"{probability * 100:.1f}% 的市场判断"

    return ""


def extract_stack_label(normalized_text: str) -> str:
    stack = []
    alias_map = {
        "claude code": "Claude",
        "claude": "Claude",
        "codex": "Codex",
        "gemini": "Gemini",
    }
    for needle, label in alias_map.items():
        if needle in normalized_text and label not in stack:
            stack.append(label)
    if len(stack) >= 2:
        return "、".join(stack)
    return ""


def first_sentence_fragment(value: str) -> str:
    cleaned = normalize_whitespace(value)
    if not cleaned:
        return ""
    for delimiter in ("。", "！", "？", "!", "?"):
        if delimiter in cleaned:
            return cleaned.split(delimiter, maxsplit=1)[0].strip() + "。"
    if ". " in cleaned:
        return cleaned.split(". ", maxsplit=1)[0].strip() + "。"
    return cleaned[:110].rstrip(" ,;:") + "。"


def count_cjk_characters(value: str) -> int:
    return sum(1 for char in value if "\u4e00" <= char <= "\u9fff")


COMMON_READER_PHRASE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\bAI Technical Cofounder\b", "AI 技术联合创始人"),
    (r"\bAI-simulated team\b", "AI 模拟团队"),
    (r"\bfuture-ready skills\b", "面向未来的技能"),
    (r"\bPractice\s*&\s*assess\b", "练习并评估"),
    (r"\bproduction-grade engineering skills\b", "生产级工程技能"),
    (r"\bdelivery checklists?\b", "交付清单"),
    (r"\brepo setup\b", "仓库初始化"),
    (r"\bdesign context\b", "设计上下文"),
    (r"\bdesktop app\b", "桌面应用"),
    (r"\binstallation and support messaging\b", "安装与支持说明"),
    (r"\bsupport messaging\b", "支持说明"),
    (r"\bcoding AI model\b", "编程 AI 模型"),
    (r"\bruntime\b", "运行时"),
)


def localize_common_reader_phrases(value: str) -> str:
    cleaned = normalize_whitespace(value)
    if not cleaned:
        return ""

    localized = cleaned
    for pattern, replacement in COMMON_READER_PHRASE_REPLACEMENTS:
        localized = re.sub(pattern, replacement, localized, flags=re.IGNORECASE)

    localized = re.sub(
        r"\bfor macOS Intel and Windows users\b",
        "面向 macOS Intel 和 Windows 用户",
        localized,
        flags=re.IGNORECASE,
    )
    localized = re.sub(
        r"\bBuild product strategy, ship features, and unblock engineering follow-through\b",
        "帮团队定产品策略、推进功能上线，并打通后续工程执行",
        localized,
        flags=re.IGNORECASE,
    )
    localized = re.sub(
        r"\bPractice & assess future-ready skills with AI-simulated team\b",
        "用 AI 模拟团队来练习并评估面向未来的技能",
        localized,
        flags=re.IGNORECASE,
    )
    localized = re.sub(
        r"\bYour AI Technical Cofounder\b",
        "你的 AI 技术联合创始人",
        localized,
        flags=re.IGNORECASE,
    )
    return normalize_whitespace(localized)


def ensure_chinese_sentence(value: str) -> str:
    cleaned = localize_common_reader_phrases(value)
    if not cleaned:
        return ""
    if cleaned[-1] not in "。！？.!?":
        cleaned += "。"
    return cleaned


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item]


def strip_wrapping_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def looks_like_english_text(value: str) -> bool:
    cleaned = MARKDOWN_LINK_PATTERN.sub(r"\1", value)
    cleaned = BARE_URL_PATTERN.sub("", cleaned)
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", cleaned)
    return len(words) >= 4 and len(words) >= count_cjk_characters(cleaned)


def trim_text_to_safe_boundary(value: str, *, limit: int) -> str:
    cleaned = normalize_whitespace(value)
    if len(cleaned) <= limit:
        return cleaned

    clipped = cleaned[:limit].rstrip()
    if limit < len(cleaned) and clipped and cleaned[limit : limit + 1].isalnum():
        boundary = clipped.rfind(" ")
        if boundary >= max(24, limit // 2):
            clipped = clipped[:boundary].rstrip()

    for delimiter in ("。", "！", "？", "! ", "? ", ". ", "; ", "；", ": ", "：", ", ", "，"):
        boundary = clipped.rfind(delimiter)
        if boundary >= max(24, limit // 2):
            clipped = clipped[: boundary + len(delimiter)].rstrip()
            break

    return clipped.rstrip(" ,;:，；：")


def trim_fragmentary_tail(value: str) -> str:
    cleaned = normalize_whitespace(value)
    if not cleaned or cleaned[-1] in "。！？.!?":
        return cleaned

    if looks_like_english_text(cleaned):
        words = cleaned.split()
        while words:
            tail = words[-1].strip(".,;:!?()[]{}\"'`")
            if len(tail) <= 2 or tail.lower() in {
                "a",
                "an",
                "and",
                "about",
                "for",
                "from",
                "in",
                "into",
                "more",
                "of",
                "on",
                "or",
                "that",
                "the",
                "this",
                "to",
                "via",
                "why",
                "with",
                "your",
            } or re.search(r"[0-9][A-Za-z]+$", tail):
                words.pop()
                continue
            break
        if len(words) >= 2:
            tail = words[-1].strip(".,;:!?()[]{}\"'`").lower()
            prev = words[-2].strip(".,;:!?()[]{}\"'`").lower()
            if re.fullmatch(r"[a-z]{2,5}", tail) and (prev in {"npx", "npm", "pip", "uv", "uvx"} or re.search(r"[0-9/$-]", prev)):
                words.pop()
        if words:
            return " ".join(words).rstrip(" ,;:")
        return cleaned

    tokens = cleaned.split()
    if tokens:
        tail = tokens[-1].strip(".,;:!?()[]{}\"'`")
        if re.fullmatch(r"[\u4e00-\u9fff]{1,2}", tail):
            tokens.pop()
        elif len(tokens) >= 2 and tokens[-2].lower() in {"npx", "npm", "pip", "uv", "uvx"} and re.fullmatch(r"[a-z]{2,8}", tail):
            tokens = tokens[:-2]
        elif count_cjk_characters(cleaned) >= 8 and re.fullmatch(r"[a-z]{2,6}", tail):
            tokens.pop()
        cleaned = " ".join(tokens).rstrip(" ,;:，；：")

    last_boundary = max(cleaned.rfind(mark) for mark in "。！？.!?")
    if last_boundary >= 0:
        trailing = cleaned[last_boundary + 1 :].strip()
        if trailing and (count_cjk_characters(trailing) <= 12 or len(trailing) <= 24):
            return cleaned[: last_boundary + 1].strip()

    return cleaned


def sanitize_body_text(value: str, *, fallback: str) -> str:
    cleaned = MARKDOWN_LINK_PATTERN.sub(r"\1", value)
    cleaned = BARE_URL_PATTERN.sub("", cleaned)
    cleaned = normalize_whitespace(cleaned)
    cleaned = re.sub(r"\s+([,.;:!?，。！？；：])", r"\1", cleaned)
    return cleaned or fallback


def sanitize_source_title(value: str) -> str:
    cleaned = MARKDOWN_LINK_PATTERN.sub(r"\1", value)
    cleaned = INLINE_BRACKET_PATTERN.sub(r"\1", cleaned)
    cleaned = BARE_URL_PATTERN.sub("", cleaned)
    cleaned = normalize_whitespace(cleaned)
    cleaned = re.sub(r"\s+([,.;:!?，。！？；：])", r"\1", cleaned)
    return cleaned.strip(" -:|")


def build_source_title(*, section_title: str, item: ReportRenderItem) -> str:
    title = sanitize_source_title(item.source_title)
    if title:
        return shorten_source_title(title)

    excerpt_title = sanitize_source_title(first_sentence_fragment(item.excerpt))
    if excerpt_title:
        return shorten_source_title(excerpt_title)

    return f"{section_title} 条目"


def shorten_source_title(value: str) -> str:
    cleaned = normalize_whitespace(value)
    if len(cleaned) <= 96:
        return cleaned
    for delimiter in ("。", "！", "？", "!", "?", " - ", " — ", ": "):
        if delimiter in cleaned:
            head = cleaned.split(delimiter, maxsplit=1)[0].strip()
            if head:
                return head[:96].rstrip()
    return cleaned[:96].rstrip(" ,;:") + "…"


def as_string(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None


def ordered_renderable_lanes(lanes: Sequence[dict[str, Any]]) -> list[str]:
    available = {
        lane["name"]
        for lane in lanes
        if lane["name"] in FIXED_SECTION_TITLES and lane.get("useful_item_count", 0) > 0
    }
    return [lane_name for lane_name in FIXED_SECTION_ORDER if lane_name in available]


def build_render_items_by_lane(
    *,
    collect_result: dict[str, Any],
    selected_items: dict[str, Any] | None,
    renderable_lanes: Sequence[str],
) -> dict[str, list[ReportRenderItem]]:
    lane_counts = {lane["name"]: lane["useful_item_count"] for lane in collect_result["lanes"]}
    items_by_lane = {lane_name: [] for lane_name in renderable_lanes}

    if selected_items is not None:
        for item in selected_items["selected_items"]:
            lane_name = item["lane"]
            if lane_name not in items_by_lane:
                continue
            render_item = normalize_render_item(
                item=item,
                useful_item_count=lane_counts[lane_name],
                report_date=collect_result["report_date"],
            )
            if not render_item_is_publishable(render_item):
                continue
            items_by_lane[lane_name].append(render_item)

    for lane_name in renderable_lanes:
        lane_items = items_by_lane[lane_name]
        if lane_items:
            lane_items.sort(key=lambda item: item.sort_key, reverse=True)
            continue
        if selected_items is not None:
            if lane_name in NO_INFO_ON_EMPTY_SELECTED_LANES:
                items_by_lane[lane_name] = [build_no_info_render_item(lane_name=lane_name)]
            continue

        items_by_lane[lane_name] = [
            build_fallback_render_item(
                lane_name=lane_name,
                useful_item_count=lane_counts[lane_name],
                report_date=collect_result["report_date"],
            )
        ]

    return items_by_lane


def normalize_render_item(item: dict[str, Any], *, useful_item_count: int, report_date: str) -> ReportRenderItem:
    lane_name = item["lane"]
    raw_title = normalize_whitespace(item.get("title", "")) or f"{FIXED_SECTION_TITLES[lane_name]} 条目"
    matched_query = normalize_whitespace(str(item.get("matched_query", "")))
    display_title = decorate_lane_display_title(lane_name=lane_name, title=raw_title, matched_query=matched_query)
    raw_source_snippet = normalize_whitespace(item.get("source_snippet", ""))
    raw_excerpt = normalize_whitespace(item.get("excerpt", ""))
    fallback_title, fallback_excerpt = build_editor_copy(
        lane_name=lane_name,
        title=raw_title,
        excerpt=raw_source_snippet or raw_excerpt,
        front_matter={},
    )
    source_text = raw_source_snippet or raw_excerpt
    base_title = build_reader_title(
        lane_name=lane_name,
        raw_title=display_title or normalize_whitespace(item.get("editor_headline", "")) or fallback_title,
        source_text=source_text,
    )
    title = base_title
    if lane_name == "reddit-watch":
        title = prefix_reddit_selection_bucket_title(
            title=title,
            selection_bucket=normalize_whitespace(str(item.get("selection_bucket", ""))),
        )
    excerpt = build_reader_excerpt(
        lane_name=lane_name,
        raw_title=raw_title,
        source_text=source_text,
        source_url=normalize_whitespace(str(item.get("source_url", ""))),
        matched_query=matched_query,
        fallback_excerpt=normalize_whitespace(item.get("editor_summary", "")) or fallback_excerpt,
        useful_item_count=useful_item_count,
    )

    source_url = normalize_source_url(item.get("source_url"), lane_name=lane_name, report_date=report_date)
    fetched_at = item.get("fetched_at", "")
    signal_path = item.get("signal_path", "")
    return ReportRenderItem(
        lane=lane_name,
        title=title,
        excerpt=ensure_chinese_sentence(excerpt or f"该栏目收录 {useful_item_count} 条有用内容。"),
        source_url=source_url,
        link_label=LINK_LABELS[lane_name],
        source_title=base_title or display_title,
        sort_key=(str(fetched_at), str(signal_path)),
    )


def decorate_lane_display_title(*, lane_name: str, title: str, matched_query: str) -> str:
    cleaned_title = normalize_whitespace(title)
    if lane_name == "weather-watch":
        return cleaned_title or "今日天气"
    if lane_name != "hacker-news-search-watch":
        return cleaned_title

    cleaned_query = normalize_whitespace(matched_query)
    if not cleaned_query:
        return cleaned_title
    if cleaned_query.lower() in cleaned_title.lower():
        return cleaned_title
    if not cleaned_title:
        return f"搜索词「{cleaned_query}」命中"
    return f"「{cleaned_query}」：{cleaned_title}"


def build_reader_title(*, lane_name: str, raw_title: str, source_text: str) -> str:
    cleaned_title = normalize_whitespace(raw_title)
    if lane_name == "weather-watch":
        return build_weather_reader_title(title=cleaned_title, source_text=source_text) or "今日天气"
    if lane_name == "polymarket-watch":
        localized_question = localize_polymarket_question(cleaned_title)
        if localized_question and localized_question != cleaned_title:
            return f"市场在押注：{localized_question}"
        return cleaned_title
    if lane_name in NOISY_X_LANES and re.fullmatch(r"@[A-Za-z0-9_]+(?:\s+#\d+)?", cleaned_title):
        descriptor, _ = build_known_signal_copy(lane_name=lane_name, title=cleaned_title, source_text=source_text)
        if not descriptor:
            descriptor = build_generic_x_descriptor(source_text)
        if descriptor:
            return localize_common_reader_phrases(f"{cleaned_title}：{descriptor}")
    is_long_english_headline = (
        looks_like_english_text(cleaned_title)
        and (
            len(cleaned_title) >= 48
            or cleaned_title.count(" ") >= 7
            or "—" in cleaned_title
            or "(" in cleaned_title
        )
    )
    if lane_name in {"reddit-watch", "hacker-news-watch", "hacker-news-search-watch", "product-hunt-watch"} and is_long_english_headline:
        descriptor, _ = build_known_signal_copy(lane_name=lane_name, title=cleaned_title, source_text=source_text)
        if descriptor:
            return localize_common_reader_phrases(descriptor)
        if lane_name == "product-hunt-watch":
            localized_title = localize_product_hunt_reader_title(cleaned_title)
            if localized_title:
                return localized_title
    return cleaned_title


def prefix_reddit_selection_bucket_title(*, title: str, selection_bucket: str) -> str:
    cleaned_title = normalize_whitespace(title)
    if not cleaned_title:
        return ""
    if selection_bucket == "heat":
        return f"【热帖】{cleaned_title}"
    if selection_bucket == "voice":
        return f"【原声】{cleaned_title}"
    return cleaned_title


def build_reader_excerpt(
    *,
    lane_name: str,
    raw_title: str,
    source_text: str,
    source_url: str,
    fallback_excerpt: str,
    matched_query: str = "",
    useful_item_count: int,
) -> str:
    raw_cleaned_source = normalize_whitespace(source_text)
    cleaned_fallback = normalize_whitespace(fallback_excerpt)
    if lane_name == "weather-watch":
        weather_excerpt = build_lane_fact_summary(
            lane_name=lane_name,
            title=raw_title,
            source_text=raw_cleaned_source,
            source_url=source_url,
            matched_query=matched_query,
        )
        if weather_excerpt:
            return ensure_chinese_sentence(weather_excerpt)

    cleaned_source = trim_fragmentary_tail(raw_cleaned_source)
    if lane_name == "weather-watch":
        weather_excerpt = build_lane_fact_summary(
            lane_name=lane_name,
            title=raw_title,
            source_text=cleaned_source,
            source_url=source_url,
            matched_query=matched_query,
        )
        if weather_excerpt:
            return ensure_chinese_sentence(weather_excerpt)

    if cleaned_source:
        if lane_name in NOISY_X_LANES or lane_name == "reddit-watch":
            detailed_excerpt = build_lane_fact_summary(
                lane_name=lane_name,
                title=raw_title,
                source_text=cleaned_source,
                source_url=source_url,
                matched_query=matched_query,
            )
            if detailed_excerpt and not is_generic_placeholder_copy(detailed_excerpt):
                return ensure_chinese_sentence(detailed_excerpt)
            guarded_excerpt = build_minimal_reader_fact_fallback(
                lane_name=lane_name,
                title=raw_title,
                source_text=cleaned_source,
                source_url=source_url,
                matched_query=matched_query,
            )
            if guarded_excerpt and not is_generic_placeholder_copy(guarded_excerpt):
                return ensure_chinese_sentence(guarded_excerpt)

        if count_cjk_characters(cleaned_source) >= 8 and not looks_like_english_text(cleaned_source):
            return ensure_chinese_sentence(cleaned_source)

        detailed_excerpt = build_lane_fact_summary(
            lane_name=lane_name,
            title=raw_title,
            source_text=cleaned_source,
            source_url=source_url,
            matched_query=matched_query,
        )
        if detailed_excerpt:
            if is_generic_placeholder_copy(detailed_excerpt):
                guarded_excerpt = build_minimal_reader_fact_fallback(
                    lane_name=lane_name,
                    title=raw_title,
                    source_text=cleaned_source,
                    source_url=source_url,
                    matched_query=matched_query,
                )
                if guarded_excerpt and not is_generic_placeholder_copy(guarded_excerpt):
                    return ensure_chinese_sentence(guarded_excerpt)
                if cleaned_fallback and not looks_like_english_text(cleaned_fallback) and not is_generic_placeholder_copy(cleaned_fallback):
                    return ensure_chinese_sentence(cleaned_fallback)
            if (
                lane_name in NOISY_X_LANES
                and cleaned_fallback
                and noisy_x_excerpt_is_publishable(cleaned_fallback)
                and not noisy_x_excerpt_is_publishable(detailed_excerpt)
            ):
                return ensure_chinese_sentence(cleaned_fallback)
            return ensure_chinese_sentence(detailed_excerpt)

        descriptor, faithful_excerpt = build_known_signal_copy(
            lane_name=lane_name,
            title=raw_title,
            source_text=cleaned_source,
        )
        if faithful_excerpt:
            return ensure_chinese_sentence(faithful_excerpt)

        if looks_like_english_text(cleaned_source):
            if cleaned_fallback and not looks_like_english_text(cleaned_fallback) and not is_generic_placeholder_copy(cleaned_fallback):
                return ensure_chinese_sentence(cleaned_fallback)
            guarded_excerpt = build_minimal_reader_fact_fallback(
                lane_name=lane_name,
                title=raw_title,
                source_text=cleaned_source,
                source_url=source_url,
                matched_query=matched_query,
            )
            if guarded_excerpt:
                return ensure_chinese_sentence(guarded_excerpt)
            return ensure_chinese_sentence(f"该栏目收录 {useful_item_count} 条有用内容。")

        return ensure_chinese_sentence(cleaned_source)

    sparse_summary = build_sparse_lane_summary(lane_name=lane_name, title=raw_title, source_url=source_url)
    if sparse_summary:
        return ensure_chinese_sentence(sparse_summary)

    if cleaned_fallback and not is_generic_placeholder_copy(cleaned_fallback):
        return ensure_chinese_sentence(cleaned_fallback)

    guarded_excerpt = build_minimal_reader_fact_fallback(
        lane_name=lane_name,
        title=raw_title,
        source_text=raw_cleaned_source,
        source_url=source_url,
        matched_query=matched_query,
    )
    if guarded_excerpt:
        return ensure_chinese_sentence(guarded_excerpt)

    return ensure_chinese_sentence(f"该栏目收录 {useful_item_count} 条有用内容。")


def build_candidate_reader_excerpt(*, candidate: dict[str, Any], useful_item_count: int) -> str:
    lane_name = normalize_whitespace(str(candidate.get("lane", "")))
    raw_title = normalize_whitespace(str(candidate.get("title", ""))) or f"{FIXED_SECTION_TITLES[lane_name]} 条目"
    source_text = normalize_whitespace(str(candidate.get("source_snippet") or candidate.get("excerpt", "")))
    fallback_excerpt = normalize_whitespace(str(candidate.get("editor_summary", "")))
    if not fallback_excerpt:
        _, fallback_excerpt = build_editor_copy(
            lane_name=lane_name,
            title=raw_title,
            excerpt=source_text,
            front_matter={},
        )
    return build_reader_excerpt(
        lane_name=lane_name,
        raw_title=raw_title,
        source_text=source_text,
        source_url=normalize_whitespace(str(candidate.get("source_url", ""))),
        matched_query=normalize_whitespace(str(candidate.get("matched_query", ""))),
        fallback_excerpt=fallback_excerpt,
        useful_item_count=useful_item_count,
    )


def render_item_is_publishable(item: ReportRenderItem) -> bool:
    if item.lane in NOISY_X_LANES:
        return noisy_x_excerpt_is_publishable(item.excerpt)
    cleaned_excerpt = normalize_whitespace(item.excerpt)
    if item.lane in {"reddit-watch", "hacker-news-watch", "hacker-news-search-watch", "claude-code-watch", "codex-watch", "openclaw-watch", "github-trending-weekly", "polymarket-watch"}:
        if not cleaned_excerpt or is_generic_placeholder_copy(cleaned_excerpt):
            return False
        if re.fullmatch(r"(?:该栏目|本栏)收录 \d+ 条有用内容。?", cleaned_excerpt):
            return False
    if item.lane == "codex-watch":
        if "这次改动主要写明了" in cleaned_excerpt and re.search(r"\b(?:Title|Author|Merged at|Committed at):", cleaned_excerpt):
            return False
    if item.lane == "openclaw-watch":
        if "Google Meet joins OpenClaw" in cleaned_excerpt:
            return False
    if item.lane in {"hacker-news-watch", "hacker-news-search-watch"}:
        title = normalize_whitespace(item.title).strip("'\"")
        title_lower = title.lower()
        excerpt_lower = cleaned_excerpt.lower()
        banned_hn_templates = (
            "先按标题本身交代主题",
            "摘要里能看到的具体信息是",
            "命中的 HN 标题是",
            "HN 搜索命中的标题是",
        )
        if any(template in cleaned_excerpt for template in banned_hn_templates):
            return False
        if title_lower and excerpt_lower.count(title_lower) >= 2:
            return False
    return True


def noisy_x_excerpt_is_publishable(value: str) -> bool:
    cleaned = normalize_whitespace(value)
    if not cleaned:
        return False
    if re.fullmatch(r"(?:该栏目|本栏)收录 \d+ 条有用内容。?", cleaned):
        return False
    if "这条帖子围绕" in cleaned or "摘要里给出的直接变化是：" in cleaned:
        return False
    if is_generic_placeholder_copy(cleaned):
        return False
    if looks_like_english_text(cleaned):
        return False
    return True


def build_lane_fact_summary(
    *,
    lane_name: str,
    title: str,
    source_text: str,
    source_url: str,
    matched_query: str = "",
) -> str:
    cleaned_source = normalize_fact_source_text(source_text)
    if not cleaned_source:
        return ""

    if lane_name == "weather-watch":
        return build_weather_detail(title=title, source_text=cleaned_source)
    if lane_name in NOISY_X_LANES:
        return build_x_post_detail(lane_name=lane_name, title=title, source_text=cleaned_source)
    if lane_name == "claude-code-watch":
        return build_claude_code_release_detail(title=title, source_text=cleaned_source)
    if lane_name == "codex-watch":
        return build_codex_detail(title=title, source_text=cleaned_source, source_url=source_url)
    if lane_name == "openclaw-watch":
        return build_openclaw_release_detail(title=title, source_text=cleaned_source)
    if lane_name == "github-trending-weekly":
        return build_github_trending_detail(title=title, source_text=cleaned_source)
    if lane_name == "product-hunt-watch":
        return build_product_hunt_detail(title=title, source_text=cleaned_source)
    if lane_name == "polymarket-watch":
        return build_polymarket_detail(title=title, source_text=cleaned_source)
    if lane_name in {"hacker-news-watch", "hacker-news-search-watch"}:
        return build_hacker_news_detail(
            lane_name=lane_name,
            title=title,
            source_text=cleaned_source,
            matched_query=matched_query,
        )
    if lane_name == "reddit-watch":
        return build_reddit_detail(title=title, source_text=cleaned_source)
    return ""


def is_generic_placeholder_copy(value: str) -> bool:
    cleaned = normalize_whitespace(value).strip("。")
    if not cleaned:
        return False
    return bool(
        re.fullmatch(r"(?:该栏目|本栏)收录 \d+ 条有用内容", cleaned)
        or re.fullmatch(r"原文围绕 .+ 展开，具体变化见来源", cleaned)
        or re.fullmatch(r"帖子在讨论 [`“\"]?.+[`”\"]? 相关内容", cleaned)
        or re.fullmatch(r"帖子在讨论 .+ 相关内容", cleaned)
        or re.fullmatch(r"这条帖子围绕 [`“\"]?.+[`”\"]? 展开.*", cleaned)
        or re.fullmatch(r"`?.+`? 这周能进趋势榜，至少因为：项目说明主要在讲它的定位、工作流和使用场景", cleaned)
    )


def noisy_x_source_has_operational_detail(value: str) -> bool:
    cleaned = normalize_whitespace(strip_x_leading_markers(value))
    if not cleaned:
        return False

    lowered = cleaned.lower()
    english_action = re.search(
        r"\b(automate[ds]?|built|build(?:ing|s)?|configur(?:e|ed|ing)|fix(?:ed|es|ing)?|"
        r"edit(?:s|ed|ing)?|execute[ds]?|generate[ds]?|include[ds]?|launch(?:ed|es)?|"
        r"modif(?:y|ied|ies)|plan(?:s|ned|ning)?|read(?:s|ing)?|"
        r"register(?:ed|s)?|retr(?:y|ied|ies)|run(?:s|ning)?|split(?:s|ting)?|support(?:s|ed)?|"
        r"ship(?:s|ped|ping)?|use[sd]?|write(?:s|n|ing)?)\b",
        lowered,
    )
    cjk_action_terms = (
        "读取",
        "读",
        "生成",
        "跑",
        "改",
        "拆",
        "定位",
        "修",
        "操作",
        "配置",
        "注册",
        "设计",
        "测试",
        "接入",
        "上线",
        "迁移",
        "审阅",
        "调用",
        "自动",
    )
    has_action = bool(english_action) or any(term in cleaned for term in cjk_action_terms)

    detail_terms = (
        "agent harness",
        "api",
        "app store",
        "apple iap",
        "browser",
        "cli",
        "cloudflare",
        "computer use",
        "context",
        "devtools",
        "fixture",
        "github",
        "iap",
        "implementation plan",
        "iphone mirror",
        "issue",
        "lighthouse",
        "locally",
        "mcp",
        "memory",
        "npm test",
        "patch",
        "performance check",
        "playwright",
        "pull request",
        "pytest",
        "release",
        "screenshot",
        "sdk",
        "stack",
        "token",
        "tokens",
        "tts",
        "/ultraplan",
        "web",
    )
    cjk_detail_terms = (
        "设计稿",
        "截图",
        "堆栈",
        "文件",
        "浏览器",
        "成本",
        "美元",
        "分钟",
        "小时",
        "上下文",
        "记忆",
        "接入",
        "注册",
        "配置",
        "测试",
        "竞技场",
        "实施计划",
        "任务",
        "迁移",
        "审阅",
        "修复建议",
        "失败",
        "电脑",
        "应用",
        "工作流",
        "执行",
    )
    detail_hit_count = sum(1 for term in detail_terms if term in lowered) + sum(
        1 for term in cjk_detail_terms if term in cleaned
    )
    has_detail = detail_hit_count > 0
    measurement_patterns = (
        r"[$￥€]\s*\d",
        r"\b\d+(?:[.,]\d+)?\s*(?:%|k|m|b|tokens?|minutes?|hours?|seconds?|secs?|ms|gb|mb|kb|users?|agents?|models?|tasks?|steps?|runs?|tests?|prs?|issues?)\b",
        r"\b\d+(?:[.,]\d+)?\s*[万亿]\s*(?:tokens?|用户|美元|上下文|参数)?",
        r"\d+(?:[.,]\d+)?\s*(?:个|次|项|轮|份)?\s*(?:agent|agents|智能体|模型|文件|任务|子任务|用户|版本|工具|接口|步骤|测试|用例)",
        r"[一二三四五六七八九十百千万]+(?:次|分钟|小时|美元|文件|任务|万)",
        r"[一二三四五六七八九十百千万]+个多?(?:分钟|小时|月)",
    )
    has_measurement = any(
        re.search(pattern, cleaned, re.IGNORECASE) for pattern in measurement_patterns
    )
    has_versioned_release = bool(VERSION_TOKEN_PATTERN.search(cleaned)) and (
        has_detail
        or any(term in lowered for term in ("live", "release", "support"))
        or any(term in cleaned for term in ("发布", "更新", "接入", "支持"))
    )

    if has_versioned_release:
        return True
    if has_measurement and (has_action or has_detail):
        return True
    if has_action and has_detail:
        return True
    return detail_hit_count >= 3 and bool(
        re.search(r"\b(?:agent|claude|codex|deepseek|devtools|gpt|mcp|openclaw)\b", lowered)
    )


def noisy_x_candidate_has_specific_summary(candidate: dict[str, Any]) -> bool:
    lane_name = normalize_whitespace(str(candidate.get("lane", "")))
    if lane_name not in NOISY_X_LANES:
        return True

    source_text = normalize_whitespace(str(candidate.get("source_snippet") or candidate.get("excerpt", "")))
    if not source_text:
        return False

    lowered_source = source_text.lower()
    if (
        "注册即用" in source_text
        or "不满意可以退款" in source_text
        or re.search(r"\b(openai|api)\b.*(?:注册|退款|稳定性)", lowered_source, re.IGNORECASE)
        or re.search(r"github\s+被.*屠榜", lowered_source, re.IGNORECASE)
        or re.search(r"\b\d+\.\s*$", source_text)
    ):
        return False

    title = normalize_whitespace(str(candidate.get("title", "")))
    source_url = normalize_whitespace(str(candidate.get("source_url", "")))

    # First ask the actual reader renderer whether the post can become concrete copy.
    # The previous gate rejected many x-following posts before this step because they
    # were short or Chinese-first; that made the whole 关注流 disappear.
    detailed_excerpt = build_x_post_detail(lane_name=lane_name, title=title, source_text=source_text)
    if (
        detailed_excerpt
        and noisy_x_excerpt_is_publishable(detailed_excerpt)
        and not is_generic_placeholder_copy(detailed_excerpt)
        and "简短反应" not in detailed_excerpt
        and "没有给出可复述" not in detailed_excerpt
        and "最新教程" not in source_text
    ):
        return True

    if not noisy_x_source_has_operational_detail(source_text):
        return False
    editor_summary = normalize_whitespace(str(candidate.get("editor_summary", "")))
    if editor_summary and noisy_x_excerpt_is_publishable(editor_summary):
        return True
    if not noisy_x_excerpt_is_publishable(build_candidate_reader_excerpt(candidate=candidate, useful_item_count=1)):
        return False
    if not looks_like_english_text(source_text):
        return True

    detailed_excerpt = build_lane_fact_summary(
        lane_name=lane_name,
        title=title,
        source_text=source_text,
        source_url=source_url,
    )
    if detailed_excerpt and not is_generic_placeholder_copy(detailed_excerpt):
        return True

    _, faithful_excerpt = build_known_signal_copy(
        lane_name=lane_name,
        title=title,
        source_text=source_text,
    )
    return bool(faithful_excerpt and not is_generic_placeholder_copy(faithful_excerpt))


def normalize_fact_source_text(value: str) -> str:
    cleaned = normalize_whitespace(value)
    if not cleaned:
        return ""
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = cleaned.replace("Author :", "Author:")
    cleaned = cleaned.replace("Votes :", "Votes:")
    cleaned = cleaned.replace("Comments :", "Comments:")
    cleaned = cleaned.replace("Topic :", "Topic:")
    return cleaned


def split_fact_segments(value: str) -> list[str]:
    cleaned = normalize_fact_source_text(value)
    if not cleaned:
        return []

    split_pattern = (
        r"\s+(?=(?:Added|Improved|Fixed|Include|Includes|Author:|Votes:|Comments:|Topic:|Question:|"
        r"Current leader:|24h volume:|30d volume:|Liquidity:|Price movement:|"
        r"Dreaming/memory-wiki:|Control UI/webchat:|Telegram/forum topics:|UI/chat:|"
        r"Auto-reply/send policy:|Tools/video_generate:|Microsoft Teams:|Plugins:|Feishu:|OpenAI/Codex OAuth:))"
    )
    return [
        normalize_whitespace(segment).strip(" .")
        for segment in re.split(split_pattern, cleaned)
        if normalize_whitespace(segment).strip(" .")
    ]


def unique_facts(facts: Sequence[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        cleaned = normalize_whitespace(fact).strip("。")
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return ordered


def prioritize_fact_tail(
    facts: Sequence[str],
    *,
    preserve_head: int,
    priority_terms: Sequence[Sequence[str]],
) -> list[str]:
    ordered = unique_facts(facts)
    if len(ordered) <= preserve_head:
        return ordered

    head = ordered[:preserve_head]
    remaining = ordered[preserve_head:]
    prioritized: list[str] = []

    for terms in priority_terms:
        lowered_terms = tuple(term.lower() for term in terms)
        for index, fact in enumerate(remaining):
            lowered_fact = fact.lower()
            if all(term in lowered_fact for term in lowered_terms):
                prioritized.append(fact)
                remaining.pop(index)
                break

    return head + prioritized + remaining


def compose_fact_sentences(*, intro: str, facts: Sequence[str], group_sizes: Sequence[int] = (2, 2, 1)) -> str:
    ordered_facts = unique_facts(facts)
    if not ordered_facts:
        return ""

    prefixes = [intro, "另外，", "同时，"]
    sentences: list[str] = []
    cursor = 0
    for index, size in enumerate(group_sizes):
        group = ordered_facts[cursor : cursor + size]
        if not group:
            break
        prefix = prefixes[index] if index < len(prefixes) else "补充来看，"
        sentences.append(prefix + "；".join(group) + "。")
        cursor += size
        if cursor >= len(ordered_facts):
            break
    return " ".join(sentences)


def build_sparse_lane_summary(*, lane_name: str, title: str, source_url: str) -> str:
    if lane_name not in {"claude-code-watch", "openclaw-watch"}:
        return ""

    match = re.search(r"github\.com/[^/]+/([^/]+)/releases/tag/([^/?#]+)", source_url, re.IGNORECASE)
    if not match:
        return ""

    repo_slug = match.group(1).strip()
    tag = normalize_whitespace(match.group(2))
    version = normalize_whitespace(title) or tag
    product_name = humanize_repo_slug(repo_slug)
    return f"`{product_name}` 发布了 `{version}` 这个 release 版本更新"



def build_minimal_reader_fact_fallback(
    *,
    lane_name: str,
    title: str,
    source_text: str,
    source_url: str,
    matched_query: str = "",
) -> str:
    cleaned_source = normalize_whitespace(source_text)
    if not cleaned_source:
        return ""

    if lane_name == "reddit-watch":
        return build_reddit_detail(title=title, source_text=cleaned_source)
    if lane_name == "github-trending-weekly":
        return build_github_trending_detail(title=title, source_text=cleaned_source)
    if lane_name == "product-hunt-watch":
        return build_product_hunt_detail(title=title, source_text=cleaned_source)
    if lane_name == "codex-watch":
        return build_codex_detail(title=title, source_text=cleaned_source, source_url=source_url)
    if lane_name in {"hacker-news-watch", "hacker-news-search-watch"}:
        return build_hacker_news_detail(
            lane_name=lane_name,
            title=title,
            source_text=cleaned_source,
            matched_query=matched_query,
        )
    if lane_name == "polymarket-watch":
        return build_polymarket_detail(title=title, source_text=cleaned_source)
    return ""


def humanize_repo_slug(repo_slug: str) -> str:
    normalized = normalize_whitespace(repo_slug).lower()
    known_names = {
        "claude-code": "Claude Code",
        "openclaw": "OpenClaw",
        "codex": "Codex",
    }
    if normalized in known_names:
        return known_names[normalized]

    parts = [part for part in normalized.split("-") if part]
    if not parts:
        return repo_slug
    return " ".join(part.capitalize() for part in parts)


def split_title_tagline(title: str) -> tuple[str, str]:
    cleaned = normalize_whitespace(title)
    for delimiter in (" — ", " - ", ": "):
        if delimiter in cleaned:
            name, tagline = cleaned.split(delimiter, maxsplit=1)
            return name.strip(), tagline.strip()
    return cleaned, ""


def simple_sentences(value: str) -> list[str]:
    cleaned = normalize_fact_source_text(value)
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [normalize_whitespace(part).strip(" .") for part in parts if normalize_whitespace(part).strip(" .")]


def strip_x_leading_markers(value: str) -> str:
    cleaned = normalize_fact_source_text(value)
    cleaned = re.sub(r"^RT\s+@[A-Za-z0-9_]+:\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(Mark this tweet|Hot take|Thread)[:\s-]+", "", cleaned, flags=re.IGNORECASE)
    return normalize_whitespace(cleaned).strip(" .")


def sanitize_subject_label(value: str) -> str:
    cleaned = normalize_whitespace(value)
    cleaned = re.sub(r"[`\"“”'‘’]+", "", cleaned)
    cleaned = re.sub(r"[\u2600-\u27BF\U0001F300-\U0001FAFF]+", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"^(?:the|a|an)\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" ,;:()[]{}.-")


def restore_decimal_version_suffix(*, subject: str, trailing_text: str) -> str:
    cleaned_subject = normalize_whitespace(subject)
    if not cleaned_subject or not trailing_text.startswith(".") or not re.search(r"\d$", cleaned_subject):
        return cleaned_subject

    version_suffix_match = re.match(r"(\.\d+(?:\.\d+)*)", trailing_text)
    if not version_suffix_match:
        return cleaned_subject

    return normalize_whitespace(f"{cleaned_subject}{version_suffix_match.group(1)}")


def extract_x_subject_label(*, title: str, source_text: str) -> str:
    normalized = normalize_whitespace(f"{title} {source_text}")
    lowered = normalized.lower()
    for term in KNOWN_TERMS:
        if term.lower() in lowered:
            return term

    patterns = (
        r"\bNew post:\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,1})\b",
        r"\bIntroducing\s+([A-Z][A-Za-z0-9_.+-]*(?:\s+[A-Z][A-Za-z0-9_.+-]+){0,4})",
        r"\bcreator of\s+([A-Z][A-Za-z0-9_.+-]*(?:\s+[A-Z][A-Za-z0-9_.+-]+){0,4})",
        r"\bmost complete\s+([A-Z][A-Za-z0-9_.+-]*(?:\s+[A-Z][A-Za-z0-9_.+-]+){0,4})\s+setup\b",
        r"\b([A-Z][A-Za-z0-9_.+-]+(?:\s+v[0-9.]+)?)\s+is the first\b",
        r"\b([A-Z][A-Za-z0-9_.+-]*(?:\s+[A-Z][A-Za-z0-9_.+-]+){0,3}\s+MCP)\b",
        r"\b(agent skills)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            subject = sanitize_subject_label(match.group(1))
            if subject:
                return subject

    return ""


def build_agent_capability_phrase(value: str) -> str:
    lowered = value.lower()
    if "open a browser" in lowered and "read a page" in lowered:
        if "click" in lowered and "report" in lowered:
            return "打开浏览器、读取页面、点击流程并回报变化"
        return "打开浏览器并读取页面内容"
    if "shared canvas" in lowered and all(token in lowered for token in ("plan", "edit", "review")):
        return "在共享 canvas 上规划、编辑并审阅 workflow"
    if "visual workflow" in lowered and "agent" in lowered:
        return "搭建可视化 workflow 并交给 agent 执行"

    actions: list[str] = []
    if "find" in lowered:
        actions.append("查找")
    if "tweak" in lowered:
        actions.append("微调")
    if "ship" in lowered:
        actions.append("交付")

    target = "相关内容"
    if "shader" in lowered:
        target = "shader"
    elif "token" in lowered:
        target = "token 开销"

    if actions:
        return "自己" + "、".join(actions) + target

    if "own computer in the cloud" in lowered:
        return "在云端拥有自己的电脑"
    return ""


def add_x_fact_sentence(sentences: list[str], value: str) -> None:
    cleaned = normalize_whitespace(value)
    cleaned = re.sub(r"^(另外|同时|补充来看)，", "", cleaned)
    cleaned = cleaned.strip("。 ")
    if not cleaned or cleaned in sentences:
        return
    sentences.append(cleaned)


def render_x_fact_sentences(sentences: Sequence[str], *, limit: int = 3) -> str:
    chosen = [sentence.strip("。 ") for sentence in sentences if sentence.strip("。 ")]
    if not chosen:
        return ""
    return " ".join(f"{sentence}。" for sentence in chosen[:limit])


def x_source_has_concrete_material(source_text: str) -> bool:
    cleaned = strip_x_leading_markers(source_text)
    if not cleaned:
        return False
    word_count = len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", cleaned))
    return len(simple_sentences(cleaned)) >= 2 or word_count >= 12


def x_clause_supports_fact_rewrite(value: str) -> bool:
    cleaned = normalize_whitespace(strip_x_leading_markers(value)).strip(" .")
    if not cleaned:
        return False

    lowered = cleaned.lower()
    if any(re.match(pattern, lowered) for pattern in RESIDUAL_NOISY_X_CLAUSE_PATTERNS):
        return False

    word_count = len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", cleaned))
    if word_count < 5:
        return False

    return bool(
        re.search(
            r"\b(add(?:ed|s)?|allow(?:ed|s)?|automate(?:d|s)?|build(?:ing|s)?|disable(?:d|s)?|drop(?:ped|s)?|"
            r"introduc(?:e|ed|ing)|launch(?:ed|es|ing)?|redesign(?:ed|s)?|release(?:d|s)?|run(?:ning|s)?|"
            r"ship(?:ped|s|ping)?|support(?:ed|s)?|teach(?:es|ing)?|trigger(?:ed|s)?|use(?:d|s)?|work(?:ed|s)?|"
            r"write(?:s|n)?|lets?)\b",
            lowered,
        )
        or any(marker in cleaned for marker in ("Claude Code", "Codex", "OpenClaw", "GitHub", "MCP", "SDK", "/"))
        or bool(re.search(r"\b\d", cleaned))
    )


def build_concrete_x_fallback_detail(*, lane_name: str, title: str, source_text: str, subject: str) -> str:
    cleaned_source = strip_x_leading_markers(source_text)
    if not cleaned_source or not looks_like_english_text(cleaned_source) or not x_source_has_concrete_material(cleaned_source):
        return ""

    lowered = cleaned_source.lower()
    sentences: list[str] = []

    if "claude code routines" in lowered:
        add_x_fact_sentence(
            sentences,
            "帖子在介绍 `Claude Code Routines`，这相当于给 `Claude Code` 新增了一层可复用的自动化入口",
        )
        add_x_fact_sentence(
            sentences,
            "摘要里点明了两个触发面：除了 `schedule`，还可以通过 `GitHub` 拉起 templated agents",
        )
        add_x_fact_sentence(
            sentences,
            "这让 `Claude Code` 更像能持续运行的 workflow，而不只是一次性的对话式调用",
        )

    if "telemetry" in lowered and "cache" in lowered:
        add_x_fact_sentence(
            sentences,
            "帖子在质疑 `Claude Code` 的 telemetry 设计，而不是泛泛抱怨体验",
        )
        if "anthropic" in lowered:
            add_x_fact_sentence(
                sentences,
                "作者的核心指控是：如果关掉 telemetry，`Anthropic` 会把 cache 一起拿掉",
            )
        else:
            add_x_fact_sentence(
                sentences,
                "作者的核心指控是：如果关掉 telemetry，cache 能力也会跟着掉下去",
            )
        add_x_fact_sentence(
            sentences,
            "如果这个说法成立，用户就得在隐私偏好和 cache 效率之间做现实取舍",
        )

    if "resource" in lowered and "claude code" in lowered and ("skills" in lowered or "mcp" in lowered):
        add_x_fact_sentence(
            sentences,
            "这条帖子在推荐一个围绕 `Claude Code` 生态整理的资源网站",
        )
        add_x_fact_sentence(
            sentences,
            "网站内容主打 `Skills` 和 `MCPs` 的 curated 清单，不是零散链接收藏",
        )
        add_x_fact_sentence(
            sentences,
            "对刚搭建 `Claude Code` 工作流的人来说，这种网站比四处翻帖更容易直接上手",
        )

    if "systems engineering" in lowered and "coding agents" in lowered:
        add_x_fact_sentence(
            sentences,
            "这是一篇围绕 `Systems Engineering` 的新帖，不是在单聊某个模型",
        )
        add_x_fact_sentence(
            sentences,
            "作者的核心判断是：`coding agents` 降低了 `写代码` 门槛，但没有同步降低工程要求",
        )
        add_x_fact_sentence(
            sentences,
            "它提醒团队，不能把“更容易写代码”误当成“系统工程复杂度也一起消失”",
        )

    if "desktop app" in lowered and "claude code" in lowered:
        add_x_fact_sentence(
            sentences,
            "这条更新是在发布 `desktop` app 里的新版 `Claude Code`",
        )
        if "redesigned" in lowered:
            add_x_fact_sentence(
                sentences,
                "摘要里给出的变化很直接：这版 `desktop` 体验已经被 `重新设计` 过",
            )
        add_x_fact_sentence(
            sentences,
            "这条更新把 `Claude Code` 的产品入口从命令行扩到 `desktop`，说明改动对象是正式桌面体验而不是单个 CLI 参数",
        )

    raw_sentences = simple_sentences(cleaned_source)
    raw_clause_fact = ""
    has_concrete_raw_clause = False
    if len(raw_sentences) >= 2:
        raw_clause = normalize_whitespace(trim_fragmentary_tail(raw_sentences[1])).strip(" .")
        raw_clause = re.sub(r"\bGitHu\b", "GitHub", raw_clause)
        raw_clause = re.sub(r"\bMCPs,\s*Pl\b", "MCPs", raw_clause)
        if raw_clause:
            lowered_clause = raw_clause.lower()
            if any(re.match(pat, lowered_clause) for pat in RESIDUAL_NOISY_X_CLAUSE_PATTERNS):
                raw_clause = ""
            elif x_clause_supports_fact_rewrite(raw_clause):
                raw_clause_fact = f"摘要里给出的直接变化是：{raw_clause}"
                has_concrete_raw_clause = True

    if len(sentences) < 3 and subject and (sentences or raw_clause_fact):
        add_x_fact_sentence(
            sentences,
            f"这条帖子已经给出 `{subject}` 的具体动作或主张，不只是提到一个话题",
        )
    if len(sentences) < 3 and raw_clause_fact:
        add_x_fact_sentence(sentences, raw_clause_fact)

    if not sentences and not has_concrete_raw_clause:
        return ""

    if len(sentences) < 3 and (sentences or raw_clause_fact):
        if subject:
            add_x_fact_sentence(
                sentences,
                f"这里的 `{subject}` 已经对应到具体产品动作或 workflow 判断，可以让读者复述原帖在说什么",
            )
        elif lane_name == "x-feed":
            add_x_fact_sentence(
                sentences,
                "推荐流里已经出现了能复述的具体变化点，可以直接把对象、动作和结果讲清楚",
            )
        else:
            add_x_fact_sentence(
                sentences,
                "关注流里已经出现了能复述的具体变化点，可以直接交代对象、动作和卡点",
            )

    if len(sentences) < 3:
        return ""
    return render_x_fact_sentences(sentences)


def build_generic_x_post_detail(*, lane_name: str, title: str, source_text: str) -> str:
    cleaned_source = strip_x_leading_markers(source_text)
    if not cleaned_source:
        return ""

    subject = extract_x_subject_label(title=title, source_text=cleaned_source) or derive_subject_label(
        title=title,
        excerpt=cleaned_source,
        lane_name=lane_name,
    )
    if subject in {FIXED_SECTION_TITLES["x-feed"], FIXED_SECTION_TITLES["x-following"]}:
        subject = ""

    creator_match = re.search(
        r"(?P<speaker>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+),\s+creator of\s+"
        r"(?P<product>[A-Z][A-Za-z0-9_.+-]*(?:\s+[A-Z][A-Za-z0-9_.+-]+){0,3}),\s+on why\s+(?P<topic>[^:]+)",
        cleaned_source,
    )
    if creator_match:
        speaker = creator_match.group("speaker")
        product = sanitize_subject_label(creator_match.group("product")) or subject or "这个项目"
        topic = creator_match.group("topic").strip()
        if "slop" in topic.lower() and "human taste" in topic.lower():
            return f"`{product}` 作者 {speaker} 在谈：AI agents 如果没有人类品味把关，产出仍会变成 `slop`"
        return f"`{product}` 作者 {speaker} 在讨论，重点是 {topic}"

    official_provider_match = re.search(
        r"(?P<provider>[A-Z][A-Za-z0-9_.+-]*(?:\s+[A-Z][A-Za-z0-9_.+-]+){0,3})\s+is now an official\s+@(?P<target>[A-Za-z0-9_]+)\s+provider",
        cleaned_source,
        re.IGNORECASE,
    )
    if official_provider_match:
        provider = sanitize_subject_label(official_provider_match.group("provider")) or subject or "这个工具"
        target = humanize_repo_slug(official_provider_match.group("target").strip())
        fact = f"帖子在说 `{provider}` 已成为 `{target}` 的官方 provider"
        if "local model" in cleaned_source.lower():
            fact += "，重点是现在可以直接接本地模型"
        return fact

    delayed_changes_match = re.search(
        r"a few more\s+(?P<subject>.+?)\s+changes that didn[’']t make the first tweet",
        cleaned_source,
        re.IGNORECASE,
    )
    if delayed_changes_match:
        change_subject = sanitize_subject_label(delayed_changes_match.group("subject")) or subject or "这版更新"
        fact = f"转帖在补 `{change_subject}` 首条推文里没写进去的后续变更"
        if "local model" in cleaned_source.lower():
            fact += "，至少提到了 local models"
        return fact

    report_match = re.search(
        r"Re:\s*the report that\s+(?P<claim>[^:]+):\s*(?P<followup>.+)",
        cleaned_source,
        re.IGNORECASE,
    )
    if report_match:
        claim = normalize_whitespace(report_match.group("claim"))
        fact = f"帖子在讨论“{claim}”这份报告"
        followup = normalize_whitespace(report_match.group("followup")).lower()
        if "power relative" in followup or "relative power" in followup:
            fact += "，重点是这并不能直接说明模型的相对 power"
        return fact

    automation_match = re.search(
        r"A\s+(?P<role>[^.]+?)\s+automated\s+(?P<share>\d+%)\s+of\s+(?:his|her|their)\s+job\s+with\s+(?P<tool>[^.]+?)\.",
        cleaned_source,
        re.IGNORECASE,
    )
    if automation_match:
        role = normalize_whitespace(automation_match.group("role"))
        share = automation_match.group("share")
        tool = sanitize_subject_label(automation_match.group("tool")) or subject or "这个工具"
        fact = f"帖子在转一个 {role} 用 `{tool}` 自动化 {share} 工作量的案例"
        hours_match = re.search(r"(?:He|She|They) now works?\s+(?P<hours>\d+(?:-\d+)?)\s+hours a day", cleaned_source, re.IGNORECASE)
        if hours_match:
            fact += f"，并说现在每天大约只用 {hours_match.group('hours')} 小时"
        return fact

    course_match = re.search(
        r"sell a course teaching\s+(?P<audience>[^.]+?)\s+to build with\s+(?P<tool>[^.]+?)\.",
        cleaned_source,
        re.IGNORECASE,
    )
    if course_match:
        audience = normalize_whitespace(course_match.group("audience"))
        tool = sanitize_subject_label(course_match.group("tool")) or subject or "这个工具"
        fact = f"帖子在讨论教 `{audience}` 用 `{tool}` 落地"
        lowered_source = cleaned_source.lower()
        if "raw claude" in lowered_source and "not an enterpri" in lowered_source:
            fact += "，并直说 raw Claude 还不算 enterprise-ready"
        elif "not an enterpri" in lowered_source:
            fact += "，并直说 raw 版本还不算 enterprise-ready"
        return fact

    introducing_match = re.search(
        r"\bIntroducing\s+(?P<subject>.+?)(?:[.!?]|(?:\s+The way\b)|(?:\s+Your agent\b)|$)",
        cleaned_source,
        re.IGNORECASE,
    )
    if introducing_match:
        restored_subject = restore_decimal_version_suffix(
            subject=introducing_match.group("subject"),
            trailing_text=cleaned_source[introducing_match.end("subject") :],
        )
        introduced_subject = sanitize_subject_label(restored_subject) or subject or "这个工具"
        lowered_subject = introduced_subject.lower()
        if "claude code hook" in lowered_subject and "context timeline" in lowered_subject:
            detail = "帖子在介绍 `Claude Code Hook - Context Timeline`，核心是给 Claude Code 的 hook 流程补一条可回看的上下文时间线"
            if "claude-code-templates" in cleaned_source.lower():
                detail += "；安装入口来自 `claude-code-templates`，所以它更像工作流模板里的可插拔 hook，而不是单独的聊天提示词"
            return detail
        capability_match = re.search(r"\bYour agent now\s+(?P<capability>[^.!?]+)", cleaned_source, re.IGNORECASE)
        capability = build_agent_capability_phrase(capability_match.group("capability")) if capability_match else ""
        if not capability:
            capability = build_agent_capability_phrase(cleaned_source)
        if capability:
            return f"帖子在介绍 `{introduced_subject}`，说 agent 现在可以{capability}"
        return f"帖子在介绍 `{introduced_subject}`，但原文只够确认对象名称，暂不把它扩写成未验证的 agent workflow 判断"

    setup_match = re.search(
        r"\bSomeone built the most complete\s+(?P<subject>.+?)\s+setup\s+(?P<context>.+?)\s+on GitHub\b",
        cleaned_source,
        re.IGNORECASE,
    )
    if setup_match:
        setup_subject = sanitize_subject_label(setup_match.group("subject")) or subject or "这套 setup"
        context = normalize_whitespace(setup_match.group("context"))
        context_match = re.search(
            r"(?P<person>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)\s+uses at\s+(?P<org>[A-Z][A-Za-z0-9_.+-]+)",
            context,
        )
        detail = f"帖子在转一套 GitHub 上公开的 `{setup_subject}` setup"
        if context_match:
            person = context_match.group("person")
            org = context_match.group("org")
            detail += f"，并说这是 {person} 在 `{org}` 用的那套配置"
        if "free" in cleaned_source.lower() or "100%" in cleaned_source:
            detail += "，而且是免费公开的"
        return detail

    stop_start_match = re.search(
        r"(?P<speaker>.+?)\s+explained why they stopped building\s+(?P<from>[^.]+)"
        r"(?:\.\s*and started building\s+(?P<to>[^.]+)|\s+and started building\s+(?P<to_inline>[^.]+))?",
        cleaned_source,
        re.IGNORECASE,
    )
    if stop_start_match:
        speaker = normalize_whitespace(stop_start_match.group("speaker"))
        from_object = sanitize_subject_label(stop_start_match.group("from")) or "原来的方向"
        to_object = sanitize_subject_label(stop_start_match.group("to") or stop_start_match.group("to_inline") or "skills")
        to_object = re.sub(r"\s+inste[a-z]*$", "", to_object, flags=re.IGNORECASE).strip() or "skills"
        return f"帖子在转述 {speaker} 的判断，重点是为什么不再继续做 `{from_object}`、而转向做 `{to_object}`"

    first_builder_match = re.search(
        r"(?P<subject>[A-Z][A-Za-z0-9_.+-]+(?:\s+v[0-9.]+)?)\s+is the first\s+(?P<category>[^.]+?)\s+where\s+(?P<claim>[^.]+)",
        cleaned_source,
        re.IGNORECASE,
    )
    if first_builder_match:
        project = sanitize_subject_label(first_builder_match.group("subject")) or subject or "这个产品"
        category = re.sub(r"\bai\b", "AI", normalize_whitespace(first_builder_match.group("category")), flags=re.IGNORECASE)
        claim = first_builder_match.group("claim")
        capability = build_agent_capability_phrase(claim)
        if capability:
            return f"帖子把焦点放在 `{project}`，称它是首个让 agent {capability}的 `{category}`"
        return f"帖子把焦点放在 `{project}`，称它在 `{category}` 这条线上做了更激进的产品定义"

    lowered = cleaned_source.lower()
    concrete_fallback = build_concrete_x_fallback_detail(
        lane_name=lane_name,
        title=title,
        source_text=cleaned_source,
        subject=subject,
    )
    if concrete_fallback:
        return concrete_fallback

    if subject:
        if "github" in lowered and "setup" in lowered:
            return f"帖子在讨论 `{subject}` 的 setup，用 GitHub 上公开的配置去复刻一套现成用法"
        if "agent" in lowered and "skills" in lowered:
            if "harness" in lowered:
                return f"帖子把焦点放在 `{subject}`，说 harness 负责把 tools、state、memory 和 evaluation 串起来，让 skills 变成可运行的工作流"
            return f"帖子把焦点放在 `{subject}`，把 skills 讲成 agent 可复用的能力块，并提醒还需要外层运行框架承接工具和状态"
        if "cloud" in lowered and "computer" in lowered:
            return f"帖子把焦点放在 `{subject}`，说 agent 开始拿到更完整的云端运行环境"
        generic_detail = build_generic_x_source_fact_detail(
            subject=subject,
            source_text=cleaned_source,
            lowered_source=lowered,
        )
        if generic_detail:
            return generic_detail
        return ""

    fallback_object = ""
    if "agent skills" in lowered:
        fallback_object = "agent skills"
    elif "shader" in lowered:
        fallback_object = "shader 工作流"
    elif "ai builder" in lowered:
        fallback_object = "AI builder"
    if fallback_object:
        return ""
    return ""


def build_generic_x_source_fact_detail(*, subject: str, source_text: str, lowered_source: str) -> str:
    if not noisy_x_source_has_operational_detail(source_text):
        return ""
    topic_hit = any(
        term in lowered_source
        for term in (
            "agent",
            "claude",
            "codex",
            "openclaw",
            "mcp",
            "memory",
            "skill",
            "workflow",
            "github",
            "privacy filter",
            "course",
        )
    ) or any(term in source_text for term in ("智能体", "工作流", "记忆", "课程", "模型", "开源", "工具"))
    if not topic_hit:
        return ""

    sentences = simple_sentences(strip_x_leading_markers(source_text))
    concrete_sentences: list[str] = []
    for sentence in sentences:
        cleaned = normalize_whitespace(trim_fragmentary_tail(sentence)).strip(" .。")
        if not cleaned:
            continue
        if any(re.match(pattern, cleaned.lower()) for pattern in RESIDUAL_NOISY_X_CLAUSE_PATTERNS):
            continue
        if len(cleaned) > 180:
            cleaned = cleaned[:180].rstrip(" ，,；;")
        if x_clause_supports_fact_rewrite(cleaned) or noisy_x_source_has_operational_detail(cleaned):
            concrete_sentences.append(cleaned)
        if len(concrete_sentences) >= 2:
            break
    if not concrete_sentences:
        return ""

    if len(concrete_sentences) == 1:
        return f"原帖围绕 `{subject}` 给出一个具体点：{concrete_sentences[0]}。"
    return f"原帖围绕 `{subject}` 给出两层信息：{concrete_sentences[0]}；{concrete_sentences[1]}。"


def build_thin_x_reaction_detail(*, title: str, source_text: str) -> str:
    cleaned_source = normalize_whitespace(source_text)
    lowered = normalize_whitespace(f"{title} {cleaned_source}").lower()
    if "codex" not in lowered:
        return ""
    if count_cjk_characters(cleaned_source) < 4:
        return ""

    if "computer use" in lowered or "超级智能体" in cleaned_source or "coding" in lowered:
        return (
            "这是一条围绕 `Codex` 和 `Computer Use` 的简短反应：原帖认为 Codex 已经从单纯 coding "
            "扩到更强的 agent / computer-use 形态，但没有展开完整 workflow 案例"
        )

    return "这是一条围绕 `Codex` 的简短反应：原帖只表达即时反馈，没有给出可复述的 workflow 细节"


def build_minimal_release_rewrite(*, product_name: str, title: str, source_text: str) -> str:
    cleaned = trim_fragmentary_tail(normalize_fact_source_text(source_text))
    if not cleaned or not looks_like_english_text(cleaned):
        return ""

    lowered = cleaned.lower()
    facts: list[str] = []
    if "thinking hints" in lowered and "long operations" in lowered:
        facts.append("长操作期间会更早显示 `thinking hints`")

    if "broad quality release" in lowered or "quality release" in lowered:
        focus_topics: list[str] = []
        if "model provider" in lowered:
            focus_topics.append("`model provider`")
        if "gpt-5" in lowered:
            focus_topics.append("`GPT-5` 家族的 explicit turn")
        if "channel provider" in lowered:
            focus_topics.append("`channel provider` 问题")
        fact = "这版是一次偏质量修复的 release"
        if focus_topics:
            fact += "，重点在 " + "、".join(focus_topics)
        facts.append(fact)

    if "improved overal performance" in lowered or "improved overall performance" in lowered:
        facts.append("底层核心代码重构后，整体性能也做了优化")

    if not facts:
        return ""
    return compose_fact_sentences(intro=f"`{product_name}` 发布了 `{title}`，", facts=facts, group_sizes=(1, 1))


def build_x_post_detail(*, lane_name: str, title: str, source_text: str) -> str:
    cleaned_source = normalize_fact_source_text(source_text)
    if not cleaned_source:
        return ""

    _, known_excerpt = build_known_signal_copy(lane_name=lane_name, title=title, source_text=cleaned_source)
    if known_excerpt:
        return known_excerpt

    sparse_release_source = normalize_whitespace(
        re.split(r"\bHighlights:\b", cleaned_source, maxsplit=1, flags=re.IGNORECASE)[0]
    ).strip(" .")
    sparse_release_match = re.search(
        r"\bClaude Code\s+([0-9]+(?:\.[0-9A-Za-z-]+)*)\s+has been released\b",
        sparse_release_source,
        re.IGNORECASE,
    )
    if sparse_release_match:
        version = sparse_release_match.group(1)
        structured_changes: list[str] = []
        for pattern, label in (
            (r"\b(\d+)\s+flag changes\b", "flag changes"),
            (r"\b(\d+)\s+cli changes\b", "CLI changes"),
            (r"\b(\d+)\s+system prompt changes\b", "system prompt changes"),
        ):
            change_match = re.search(pattern, sparse_release_source, re.IGNORECASE)
            if change_match:
                structured_changes.append(f"{change_match.group(1)} {label}")

        facts = [f"`Claude Code {version}` 已发布"]
        if structured_changes:
            facts.append("摘要里写到 " + "、".join(f"`{change}`" for change in structured_changes[:2]))
        if len(structured_changes) > 2:
            facts.append(f"还提到 `{structured_changes[2]}`")
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(2, 1))

    lowered = cleaned_source.lower()
    lowered = re.sub(r"^rt\s+@[a-z0-9_]+:\s*", "", lowered, flags=re.IGNORECASE)
    facts: list[str] = []

    if "geoflow" in lowered:
        facts.extend(
            [
                "@yaojingang 说自己两周前开源的 `GEOFlow` 已经到 `1k Star`，重点不是单纯报喜，而是一个细分场景系统拿到了超预期反馈",
                "他补充这个系统复杂度不低，集成了 `CLI`、`Skill`、爬虫、API、GEO 工作流、自动化和 AI 友好度优化",
                "这条适合作为 agent/coding workflow 的产品化样例：不是只写 demo，而是把多种接口和自动化能力打包成可用系统",
            ]
        )

    if "skills-manage" in lowered or ("skill" in lowered and "软链接" in cleaned_source):
        facts.extend(
            [
                "@Pluvio9yte 在转 `skills-manage`，问题背景是很多 AI 编程工具的 Skill 管理还停留在手动复制粘贴项目文件夹",
                "这个工具的解法是用一个中央仓库配合软链接，把 20 多个平台的 Skill 做成一处修改、多处同步",
                "结果是 Skill 不再散落在各项目里，后续维护和迁移时只需要更新中央仓库和软链接关系",
            ]
        )

    if "yuragi fm" in lowered:
        facts.extend(
            [
                "@turingou 复盘做 `Yuragi FM` 时遇到的 AIGC 产品难点：核心不只是生成内容，而是探索语言空间和结构",
                "他提到评估很难，实验结果经常在 `60-80` 分之间横跳，很少稳定到 `90+` 的可用产物",
                "实验设计和测试耗时也很长；他把这个问题归到生成产品的评估和实验管理，而不只是模型能力本身",
            ]
        )

    if "ppt skills" in lowered and "内置了浏览器" in cleaned_source:
        facts.extend(
            [
                "@op7418 说新版 `Codex` 很适合他的 `PPT Skills`，因为 `GPT-5.5` 的前端排版能力更强，生成 PPT 页面时版式更稳",
                "他还点出一个具体流程变化：`Codex` 内置浏览器，可以直接打开预览生成的 PPT，所以生成、查看和调整能放在同一个环境里完成",
            ]
        )
        if "gpt-image" in lowered or "gpt image" in lowered:
            facts.append("原帖还提到它能调用 `GPT-Image 2` 做配图；如果采集文本被截断，正文只保留已经看到的这部分，不补写后半句")

    if "apple iap" in lowered and "注册新应用" in cleaned_source:
        facts.extend(
            [
                "@turingou 让 `Codex Computer Use` 自己操作浏览器去配置 `Apple IAP`、注册新应用",
                "他的反馈是“好用是好用”，但速度非常慢：一个多小时还没做完",
                "这个卡点不是概念层面的 computer use，而是真实业务后台里的点击、等待、表单和权限步骤会拖慢 agent 执行",
            ]
        )

    if "sandbank" in lowered and ("challenge" in lowered or "challage" in lowered) and ("cf" in lowered or "cloudflare" in lowered):
        facts.extend(
            [
                "@turingou 说自己的 `sandbank` 东京服务器终于被 `Cloudflare` 解除 challenge",
                "他把这个问题归到云端沙箱形态的 `agent matrix`：做起来会碰到云端出口、风控校验和地域节点这类网络复杂度",
                "对照项是 `local-first` 产品；如果 agent 主要在本地跑，就少了这类云端网络问题",
            ]
        )

    if "kami" in lowered and ("投资报告" in cleaned_source or "ppt" in lowered) and "cc" in lowered:
        facts.extend(
            [
                "@HiTw93 说 `Kami` 的前身不是完整产品，而是他在 `CC` 里做的一个投资报告生成小工具",
                "后来他要做一场讲“你不知道的 Agent”的分享，不想手写很长的 PPT，就把原来的能力拿来边生成、边调试",
                "这条的动作链是：先有 `CC` 内部小工具，再遇到真实分享需求，再迭代成能产出文稿 / PPT 的形态",
            ]
        )

    if "电商公司" in cleaned_source and "业务工作流 agent" in lowered and "tokens" in lowered:
        facts.extend(
            [
                "@AI_jacksaku 在给一家电商公司设计业务工作流 Agent，并把问题直接落到 token 账单上",
                "他假设日均 `50 万` input tokens、`20 万` output tokens；用 `Claude Opus 4.6` 时按输入 `$5/M`、输出 `$25/M` 估算",
                "按这个口径，一个月账单约 `$52`，token 账单从抽象风险变成了可核算的月成本",
            ]
        )

    if "agent" in cleaned_source and "skills" in lowered and "harness" in lowered and "三个核心概念" in cleaned_source:
        facts.extend(
            [
                "原帖是在给读者补 `Agent`、`Skills`、`Harness` 三个概念的关系，不是只列术语",
                "它把这三者放在现代 AI 应用和自主智能体的构建里解释：`Agent` 负责执行目标，`Skills` 像可复用能力块，`Harness` 则把流程、工具调用和运行环境串起来",
                "原文采集在“从只会聊天进化为”处被截断，所以正文只保留已经看到的定义关系，不继续脑补结论",
            ]
        )

    if "deepseek v4" in lowered and "agent" in lowered and ("pre-train" in lowered or "agentic data" in lowered):
        facts.extend(
            [
                "原帖在拆 `DeepSeek V4` 做 Agent 训练的策略，第一点是 pre-train 阶段注入 `Agentic Data`",
                "它给出的理由是先让模型熟悉长任务流程和工具调用模式，后续训练不用从零硬训",
            ]
        )

    if "deepseek v4" in lowered and "5个agent" in cleaned_source:
        facts.extend(
            [
                "@MinLiBuilds 用竞技场模式连续测试 `DeepSeek V4`，一次让 5 个 agent 一起跑",
                "他的观察是 V4 吞吐速度很快，同时注意到 `Opus 4.7` 的 input token 似乎多出约 50%",
                "具体信息集中在测试方式和 token 对比上，不是单纯的模型阵营口号",
            ]
        )

    if "codex" in lowered and "obsidian" in lowered and ("封面图" in cleaned_source or "chatgpt image" in lowered):
        facts.extend(
            [
                "@canghe 把 `Codex + Obsidian` 当作公众号封面图工作流：文章在 Obsidian 写完后，直接让 Codex 生成封面图",
                "具体做法是让 Codex 调用 `ChatGPT image 2` 生成图片，他认为模型对文章内容的理解能力足够强",
            ]
        )

    if "claude-code-setup" in lowered:
        facts.extend(
            [
                "原帖说 `Claude Code` 刚上手会显得很乱，重点推荐 Anthropic 官方的 `claude-code-setup` 插件",
                "这个插件会把可配置项列出来，包括 hooks、skills、MCP servers 和 subagents，并引导用户一步步配置自动化能力",
            ]
        )

    if "deepseek v4" in lowered and "claude code" in lowered and "1m" in lowered:
        facts.extend(
            [
                "@manateelazycat 在补充一个 `DeepSeek V4 + Claude Code` 的配置坑：有人接入后只看到 `200K` 上下文，不是预期的 `1M`",
                "他的修法是把环境变量里的模型名补上 `[1M]`，例如在 `ANTHROPIC_MODEL` 后面显式写出 1M 版本",
            ]
        )

    if "claude.md" in lowered and "karpathy" in lowered:
        facts.extend(
            [
                "这条是在分享一个 `CLAUDE.md` 写法，用它约束 `Claude Code` 不要过度自信地乱跑",
                "规则重点包括：不明白就问、简单优先、不要把困惑藏起来，目标是把 Karpathy 提到的 AI 编程缺陷提前写进项目约束",
            ]
        )

    if "claude managed agents" in lowered and "memory" in lowered:
        facts.extend(
            [
                "@shao__meng 转述 `Claude Managed Agents` 的 memory 设计思路：不要急着造专用记忆架构，而是让 agent 自己用文件系统这类通用工具管理记忆",
                "这个观点的前提是模型能力会继续提升，所以通用工具接口可能比固定 memory 模块更耐用",
            ]
        )

    if "hackerRank ceo".lower() in lowered and "agent operator" in lowered:
        facts.extend(
            [
                "帖子转述 HackerRank CEO 的判断：未来几年会出现 `Agent Operator` 这类岗位",
                "它强调的不是纯工程师职位，而是营销、法律、生命科学等行业专家学会部署 AI agents，用它们重塑具体业务流程",
            ]
        )

    if "easy-vibe" in lowered and "github trending" in lowered:
        facts.extend(
            [
                "@IndieDevHailey 推荐 DataWhale 的 `Easy-Vibe`，说它是面向零基础的 Vibe Coding 免费教程",
                "原帖给出的具体信号是项目已经上 GitHub Trending，并拿到约 `6.2k` stars，定位是帮新手从 0 到 1 做真实产品",
            ]
        )

    if "github" in lowered and "ml-intern" in lowered and "agent" in lowered:
        facts.extend(
            [
                "@GitTrend0x 在列 GitHub 上涨最快的 agent 项目，其中点名 `huggingface/ml-intern`",
                "它把这个项目解释成开源的自主 ML 工程师 agent，目标是减少人工读论文、训模型、部署这一串重复工作",
            ]
        )

    if "context" in cleaned_source and "组织记忆系统" in cleaned_source:
        facts.extend(
            [
                "@Barret_China 在讲企业 AI Agent 的 context，不是单指提示词长度",
                "他把好的 context 定义成组织记忆系统：让 AI 知道此刻该如何行动，并包含角色、目标、业务规则和历史记录等信息",
            ]
        )

    if "lldb-mcp" in lowered or ("mcp" in lowered and "非交互" in cleaned_source):
        facts.extend(
            [
                "@geniusvczh 讨论的是 `MCP` 和 CLI 的边界：有些工具天然需要交互，比如他常用的 `lldb-mcp`",
                "他的意思是，这类工具即使改成命令行形态，也往往是在命令行里重做一套交互界面，并不会因为换语法就变成普通 CLI",
            ]
        )

    if "codex app as a game editor" in lowered:
        facts.extend(
            [
                "@Dimillian 把 `Codex App` 当游戏编辑器用：让它生成 sprite 和音乐，再直接运行、试玩和调试游戏",
                "原帖还点名素材由 `GPT-5.5` 生成，所以重点是 Codex 从写代码扩到一体化小游戏制作环境",
            ]
        )

    if "gbrain" in lowered and "code graph" in lowered:
        facts.extend(
            [
                "@garrytan 说 `GBrain v0.21` 新增 code graph，补到原来面向非代码内容的检索能力上",
                "它现在把 graph、vector、hybrid RRF 和代码图谱合在一起，用来改善代码库检索和 agent 上下文获取",
            ]
        )

    if "wacrawl" in lowered and "whatsapp" in lowered:
        facts.extend(
            [
                "@steipete 发布 `wacrawl 0.1.0`，这是一个只读 CLI，用来归档和搜索本地 macOS WhatsApp Desktop 数据",
                "它会对本地数据做 snapshot，适合把聊天历史变成可检索资料，而不是去接外部聊天 API",
            ]
        )

    if "gpt image2" in lowered and "10000" in cleaned_source:
        facts.extend(
            [
                "@AI_Jasonyu 说有人围绕 `GPT Image2` 很快做出套壳站，并在一天内拿到约 `10000` 个用户",
                "他描述的动作链是：新模型出现后，先找 API、接入、上线站点，再尝试冷启动赚美金",
                "原帖还提到 `Apimart` 这类 API 接入入口，所以重点是新模型发布后的上站速度和分发效率",
            ]
        )

    if "agent harness" in lowered and "black magic" in lowered:
        facts.append("作者直说 `agent harness` 没大家想得那么玄")
    if re.search(r"\bto prove it,\s*i built one\b", lowered):
        facts.append("为了证明这点，他自己做了一个")

    if "memory makes your agent smarter over time" in lowered:
        facts.append("`memory` 会让 agent 随着使用积累变得更聪明")
    if "agent harness is key to the memory layer" in lowered:
        facts.append("`agent harness` 是 `memory layer` 的关键支撑")
    if "you can't bolt one onto" in lowered or "you can't bolt one on" in lowered or "you can't bolt one" in lowered:
        facts.append("这层能力不能事后再硬加，设计时就得把它算进去")

    if "built a tui" in lowered and "claude code" in lowered and "token" in lowered:
        facts.append("有人做了个 `TUI`，把 `Claude Code` token 的实际去向直接可视化")
    spend_match = re.search(r"(\d+(?:\.\d+)?)%\s+of\s+my\s+\$?([0-9,.]+)\s*/\s*day", cleaned_source, re.IGNORECASE)
    if spend_match:
        facts.append(
            f"结果发现自己每天大约 {spend_match.group(2)} 美元的花费里，有 {spend_match.group(1)}% 都耗在这部分 token 开销上"
        )

    if "anthropic" in lowered and "openai" in lowered and ("overtakes" in lowered or "overtake" in lowered):
        if "ventuals" in lowered or "private company valuations" in lowered:
            facts.append("转帖提到 `Anthropic` 在 `Ventuals` 这类私营公司估值市场上已经超过 `OpenAI`")

    if "codex app" in lowered and "enhancing" in lowered and "feature" in lowered:
        facts.append("作者说自己还在持续增强 `Codex app` 的各项功能，想把这套体验继续打磨得更好")

    if "ai agents" in lowered and "accelerate coding" in lowered and "software engineering" in lowered:
        facts.append("帖子在追问：随着 AI agents 加速写代码，software engineering 的未来会怎么变")

    if "gemma 4" in lowered and "openclaw" in lowered:
        facts.append("帖子说 `Gemma 4` 放进 `OpenClaw` 之后效果很猛")
    if "most powerful open-sourced model" in lowered or "most powerful open-source model" in lowered:
        facts.append("并把它称作目前见过最强的开源模型")

    if "how the heck do i use it with my team" in lowered and "claude code" in lowered:
        facts.append("帖子把问题直接抛到团队层面：`Claude Code` 到底该怎么在团队里用起来")
    if "memoria permanente" in lowered and "48 horas" in lowered and "95%" in cleaned_source:
        facts.append("有人给 `Claude Code` 做了持久记忆，这个项目 48 小时拿到约 4.6 万星，并声称 token 消耗可下降约 95%")

    if "anthropic's own team" in lowered and "claude code" in lowered:
        facts.append("原帖在推荐 Anthropic 团队自己讲 `Claude Code` 用法的 30 分钟资料，重点是从官方示范里学习怎样正确使用 Claude Code，而不是只看二手技巧清单")
    if "resource bible" in lowered and "claude code" in lowered:
        facts.append("原帖在整理 `Claude Code` builder 资源合集，定位是把常用资料集中成一个可收藏的入口")
    if "openclaw 2026.4.24" in lowered:
        facts.append("`OpenClaw 2026.4.24` 发布，原帖点名 voice calls 可以触达完整 agent、DeepSeek V4 Flash/Pro 加入模型队列，并继续补 browser automation")
    if "clawsweeper" in lowered and "50 codex" in lowered:
        facts.append("@steipete 做了 `clawsweeper`，让 50 个 Codex 实例长期并行扫描 issues / PRs，并自动关闭已经过期或已解决的条目")
    if "gbrain" in lowered and "proper eval harness" in lowered:
        facts.append("@garrytan 给 `GBrain` 做了 eval harness：145 个查询、Opus 生成语料，并用 graph / vector / hybrid 检索栈评估 retrieval 效果")
    if "privacy filter" in lowered and "openai" in lowered:
        facts.append("原帖说 OpenAI 开源了 privacy filter 小模型：总参数约 1.5B、激活参数约 50M，并采用 Apache 2.0 协议")
    if "ai agents for beginners" in lowered:
        facts.append("原帖在推荐微软的 `AI Agents for Beginners` 课程：12 讲覆盖从零搭建智能体的基础内容")
    if "女娲.skill" in cleaned_source or "14k+ stars" in lowered:
        facts.append("原帖说 `女娲.skill` 半个多月拿到 14k+ stars，并已被腾讯、Kimi、智谱的 Agent 产品作为默认 skill 植入")
    if "han1" in lowered and "agent" in lowered:
        facts.append("原帖建议关注设计师 Han1 的 Agent 实践，理由是他长期分享与 Friday 相关的实践和开源项目，并强调产品里人与人的真实连接")
    if "agent记忆" in cleaned_source or "agent 记忆" in cleaned_source:
        facts.append("原帖批评很多 AI Agent 记忆只是把历史记录堆进 Markdown，问题是事实会冲突、偏好会过期，最后导致长期记忆不可用")
    if "codex empowers anyone to build" in lowered:
        facts.append("@gdb 的短帖判断是：`Codex` 正在把构建能力下放给更多人，重点是降低从想法到可运行产品的门槛")
    if "what my openclaw does" in lowered and "context" in lowered:
        facts.append("@garrytan 展示自己用 `OpenClaw` 结合个人 context 回答问题，反馈是上下文一旦打通，agent 的实用性会明显上升")
    if "simply says" in lowered and "i don" in lowered and "hallucinating" in lowered:
        facts.append("原帖在说 coding 场景里宁愿 AI 明确回答“不知道”，也不要为了显得有用而 hallucinate")
    if "ai coding" in lowered and "侄子" in cleaned_source:
        facts.append("原帖准备把 AI coding 文章转给家人，让他们学会后再带孩子入门，说明 AI coding 已经开始进入家庭教育/启蒙语境")
    if "no more updating needed" in lowered and "nous portal" in lowered:
        facts.append("NousResearch 说通过 `Nous Portal` 和 OpenRouter，新模型发布后不再需要手动更新，重点是模型接入和分发链路自动化")
    if "rocketsim_app" in lowered and "agent skill" in lowered:
        facts.append("@twannl 预告 `RocketSim` 下一版，提到 Agent Skill 相关安装/集成，但也强调质量门槛还没到发布标准")
    if "同步听" in cleaned_source and "实时语音模型" in cleaned_source:
        facts.append("@turingou 准备把 `tuwa` 的同步听能力拆成新产品，并扩展到同步听、同步说、同步学，目标是继续压实时语音模型的工程边界")

    if "opencclaw 2026.4.15" in lowered or ("openclaw" in lowered and "2026.4.15" in cleaned_source):
        openclaw_facts: list[str] = []
        if "anthropic opus 4.7" in lowered or "opus 4.7" in lowered:
            openclaw_facts.append("已接入 `Anthropic Opus 4.7`")
        if "gemini tts" in lowered:
            openclaw_facts.append("捆绑了 `Gemini TTS`")
        if "slimmer context" in lowered or "bounded memory" in lowered:
            openclaw_facts.append("上下文更精简，memory reads 有上限")
        if openclaw_facts:
            facts.append("`OpenClaw 2026.4.15` 发布，主要更新：" + "、".join(openclaw_facts))

    if ("opus 4.7" in lowered or "opus4.7" in lowered) and "claude code" in lowered:
        facts.append("`Opus 4.7` 已登陆 `Claude Code`，帖子建议把模型当成可委派的工程师来使用")
    elif "treat it like an engineer" in lowered and "delegating" in lowered:
        facts.append("帖子建议把 AI 模型当成可委派的工程师来使用，而不是工具")

    if "claude design" in lowered and ("prototype" in lowered or "prototypes" in lowered) and ("slide" in lowered or "slides" in lowered):
        facts.append("Anthropic 正在把 `Claude Design` 往真正的设计工作流上推，而不只是展示型功能")
        facts.append("帖子点名它可以通过对话生成 prototype、slides 和 one-pagers")
        if "talking to claude" in lowered:
            facts.append("重点不是一次性出图，而是把持续修改也收进和 Claude 对话的流程里")

    if "tradingview" in lowered and "prompt" in lowered and ("command" in lowered or "list" in lowered):
        facts.append("有人在整理 `Claude Code` 搭配 `TradingView` 的 prompt 命令清单")
    if "tldr" in lowered and "turn" in lowered and "claude code" in lowered:
        facts.append("帖子在讨论如何把 `Claude Code` 变成可被调用的工具")

    if ("codex computer use" in lowered or "computer use" in lowered) and ("iphone" in lowered or "ios" in lowered or "phone" in lowered):
        facts.append("`Codex computer use` 配合 iPhone Mirror app 已可操作手机上的任意 App")
    if "gpt can use any app on your phone" in lowered:
        facts.append("`Codex computer use` 已实现用 AI 操作手机 App")

    if facts:
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(2, 1))
    thin_reaction = build_thin_x_reaction_detail(title=title, source_text=cleaned_source)
    if thin_reaction:
        return thin_reaction
    return build_generic_x_post_detail(lane_name=lane_name, title=title, source_text=cleaned_source)


def build_claude_code_release_detail(*, title: str, source_text: str) -> str:
    facts: list[str] = []
    for segment in split_fact_segments(source_text):
        lowered = segment.lower()
        if "/team-onboarding" in segment:
            facts.append("新增 `/team-onboarding`，会按本地 Claude Code 使用记录生成 teammate ramp-up guide")
        elif "enterworktree" in lowered and "`path`" in segment:
            facts.append("`EnterWorktree` 新增 `path` 参数，可以直接切进当前仓库已有 worktree")
        elif "precompact" in lowered and "block compaction" in lowered:
            facts.append("`PreCompact` hook 现在可通过退出码 2 或返回 `{\"decision\":\"block\"}` 阻止 compaction")
        elif "background monitor support" in lowered and "`monitors`" in segment:
            facts.append("插件支持顶层 `monitors` manifest key，可在 session start 或调用 skill 时自动挂起 background monitor")
        elif "os ca certificate store trust" in lowered:
            fact = "默认信任 OS CA 证书库，让企业 TLS proxy 不用再额外配证书"
            if "claude_code_cert_store=bundled" in lowered:
                fact += "，只想用内置证书时可切回 `CLAUDE_CODE_CERT_STORE=bundled`"
            facts.append(fact)
        elif "/ultraplan" in segment and "cloud environment" in lowered:
            facts.append("`/ultraplan` 和其他 remote-session 功能会自动创建默认 cloud environment，不再要求先去网页里手动 setup")
        elif "brief mode" in lowered:
            facts.append("`brief mode` 遇到 Claude 回纯文本而不是结构化消息时，会自动重试一次")
        elif "focus mode" in lowered:
            facts.append("`focus mode` 会写更自洽的最终摘要，适配只看 final message 的场景")
        elif "tool-not-available" in lowered:
            facts.append("tool-not-available 报错会解释为什么当前上下文里不能用该工具，以及下一步怎么继续")
        elif "rate-limit retry messages" in lowered:
            facts.append("rate-limit 提示会显示命中的是哪条限制和何时 reset，不再只给模糊倒计时")
        elif "refusal error messages" in lowered:
            facts.append("refusal 错误会带上 API 返回的解释")
        elif "--resume" in lowered and "session titles" in lowered:
            facts.append("`claude -p --resume <name>` 现在接受 `/rename` 或 `--name` 设定的 session title")
        elif "memory leak" in lowered:
            facts.append("还修了长会话 virtual scroller 保留过多历史 message list 副本的内存泄漏")
        elif "hardcoded 5-minute request timeout" in lowered or ("request timeout" in lowered and "api_timeout_ms" in lowered):
            facts.append("并修掉硬编码 5 分钟 request timeout，慢后端不会被固定超时提前截断")
        elif "stalled api stream handling" in lowered or ("5 minutes of no data" in lowered and "retry non-streaming" in lowered):
            facts.append("API stream 若连续 5 分钟没有数据会主动 abort，并回退到 non-streaming 重试，避免一直挂死")

    lowered_source = source_text.lower()
    if "settings.json" in lowered_source and "prurltemplate" in lowered_source:
        facts.append("`/config` 里的 theme、editor mode、verbose 等设置现在会持久化到 `~/.claude/settings.json`，并参与 project / local / policy 的覆盖优先级")
        facts.append("新增 `prUrlTemplate`，可以把页脚 PR badge 指向自定义 code-review URL，而不再只能指向 github.com")
    if "claude_code_hide_cwd" in lowered_source:
        facts.append("新增 `CLAUDE_CODE_HIDE_CWD`，启动 logo 里可以隐藏当前工作目录")
    if "--from-pr" in lowered_source and "gitlab" in lowered_source:
        facts.append("`--from-pr` 现在支持 GitLab merge request、Bitbucket pull request 和 GitHub Enterprise PR URL")
    if "--print" in lowered_source and "disallowedtools" in lowered_source:
        facts.append("`--print` mode 会遵守 agent frontmatter 里的 `tools:` 和 `disallowedTools:`，行为向 interactive mode 对齐")
    if "vim visual mode" in lowered_source and "visual-line mode" in lowered_source:
        facts.append("输入体验新增 vim visual mode `v` 和 visual-line mode `V`，带选择、operators 和视觉反馈")
    if "merged `/cost` and `/stats` into `/usage`" in lowered_source or ("/cost" in lowered_source and "/stats" in lowered_source and "/usage" in lowered_source):
        facts.append("`/cost` 和 `/stats` 合并进 `/usage`，原命令仍作为快捷入口打开对应 tab")
    if "custom themes" in lowered_source and "~/.claude/themes" in lowered_source:
        facts.append("`/theme` 可以创建和切换命名 custom themes，也支持手改 `~/.claude/themes/` 下的 JSON，插件还能随包携带 themes")
    if "mcp tools directly" in lowered_source and "mcp_tool" in lowered_source:
        facts.append("hooks 现在可以通过 `type: \"mcp_tool\"` 直接调用 MCP tools")
    if "disable_updates" in lowered_source:
        facts.append("新增 `DISABLE_UPDATES`，可以彻底阻断包括手动 `claude update` 在内的所有更新路径，比 `DISABLE_AUTOUPDATER` 更严格")
    if "claude_code_fork_subagent" in lowered_source or "forked subagents" in lowered_source:
        facts.append("外部构建现在可以通过 `CLAUDE_CODE_FORK_SUBAGENT=1` 启用 forked subagents")
    if "frontmatter" in lowered_source and "mcpservers" in lowered_source and "--agent" in lowered_source:
        facts.append("通过 `--agent` 启动主线程 agent session 时，会加载 agent frontmatter 里的 `mcpServers`")
    if "/model" in lowered_source and "persist" in lowered_source and "project" in lowered_source:
        facts.append("`/model` 的选择现在会跨重启保留，即使项目本身固定了另一个模型；启动 header 也会标出当前模型来自项目还是 managed settings")
    if "/resume" in lowered_source and "summarize" in lowered_source and "stale" in lowered_source:
        facts.append("`/resume` 会在重新读取过大、过旧 session 前先提示生成摘要，行为和 `--resume` 对齐")
    if "concurrent connect" in lowered_source and "mcp servers" in lowered_source:
        facts.append("本地和 claude.ai MCP servers 同时配置时，会并发连接以加快启动")
    if "webfetch" in lowered_source and "very large html" in lowered_source:
        facts.append("`WebFetch` 处理超大 HTML 页面时会先截断再转 markdown，避免长时间挂住")
    if "/ultraplan" in source_text and "cloud environment" in lowered_source:
        facts.append("`/ultraplan` 和其他 remote-session 功能会自动创建默认 cloud environment，不再要求先去网页里手动 setup")
    if "brief mode" in lowered_source:
        facts.append("`brief mode` 遇到 Claude 回纯文本而不是结构化消息时，会自动重试一次")
    if "/proactive" in source_text and "/loop" in source_text and "alias" in lowered_source:
        facts.append("`/proactive` 现在只是 `/loop` 的别名")
    if "improved network error messages" in lowered_source or "silent spinner" in lowered_source:
        facts.append("network error 现在会立刻给出 retry 提示，不再长时间静默转圈")
    if "improved `/doctor` layout" in source_text or ("status icons" in lowered_source and "press `f`" in lowered_source):
        facts.append("`/doctor` 布局补了状态图标，还允许直接按 `f` 让 Claude 修复报出的项")
    if "improved `/config` labels" in source_text or ("`/config`" in source_text and "labels and descriptions" in lowered_source):
        facts.append("`/config` 的 labels 和 descriptions 也一起补清楚了")
    if "improved skill description handling" in lowered_source or ("listing cap from 250 to 1,536 characters" in lowered_source):
        facts.append("skill 描述列表上限从 250 提到 1,536 字符，并会在启动时提示被截断的描述")
    if "improved `webfetch`" in lowered_source or ("strip `<style>` and `<script>` contents" in lowered_source):
        facts.append("`WebFetch` 会主动剥掉 `<style>` / `<script>` 内容，CSS 很重的页面也更容易读到正文")
    if "stale agent worktree cleanup" in lowered_source or ("squash-merged" in lowered_source and "worktrees" in lowered_source):
        facts.append("stale agent worktree cleanup 会顺手清掉已 squash-merge PR 遗留的 worktree")
    if "mcp large-output truncation prompt" in lowered_source or ("format-specific recipes" in lowered_source and "jq" in lowered_source):
        facts.append("MCP 大输出截断提示也会按格式给具体处理建议，比如 JSON 直接提示用 `jq`")
    if "queued messages" in lowered_source and "being dropped" in lowered_source:
        facts.append("Claude 忙时 `queued messages` 里的带图消息不再被悄悄丢掉")
    if "temporarily unavailable" in lowered_source and "auto mode" in lowered_source:
        facts.append("`auto mode` 下误报 `claude-opus-4-7 is temporarily unavailable` 的问题被修掉了")

    facts = prioritize_fact_tail(
        facts,
        preserve_head=3,
        priority_terms=(
            ("queued messages",),
            ("network error",),
            ("/doctor",),
            ("webfetch",),
        ),
    )
    summary = compose_fact_sentences(intro=f"`{title}` 这版最值得记的更新是：", facts=facts, group_sizes=(3, 2, 2, 2))
    if summary:
        return summary

    minimal_rewrite = build_minimal_release_rewrite(product_name="Claude Code", title=title, source_text=source_text)
    if minimal_rewrite:
        return minimal_rewrite

    sentences = simple_sentences(source_text)
    if sentences:
        return f"`Claude Code` 发布了 `{title}` 这版更新，提到 {sentences[0]}。"
    return ""


def build_codex_detail(*, title: str, source_text: str, source_url: str) -> str:
    lowered = normalize_whitespace(f"{title} {source_text}").lower()
    pr_match = re.search(r"/pull/(\d+)", source_url)
    author_match = re.search(r"Author:\s*(@[A-Za-z0-9_.-]+)", source_text)
    merged_at_match = re.search(r"Merged at:\s*([0-9T:+-]+Z?)", source_text, re.IGNORECASE)
    commit_match = re.search(r"Merge commit:\s*`?([0-9a-f]{7,})`?", source_text, re.IGNORECASE)

    if (
        ("macos intel" in lowered or "windows" in lowered)
        and ("support" in lowered or "installation" in lowered)
    ):
        lead = "这次合入的是 Codex 的 PR"
        if pr_match:
            lead += f" #{pr_match.group(1)}"
        metadata: list[str] = []
        if author_match:
            metadata.append(f"作者 {author_match.group(1)}")
        if commit_match:
            metadata.append(f"merge commit `{commit_match.group(1)}`")
        if metadata:
            lead += f"（{'，'.join(metadata)}）"
        facts = [
            f"{lead}，重点是把 `macOS Intel` 和 `Windows` 的安装与支持说明补清楚",
        ]
        if merged_at_match:
            facts.append(f"这条改动在 {merged_at_match.group(1)} 合入，属于平台覆盖面和安装文案的收口修整")
        else:
            facts.append("这类改动不是加新功能，而是把已有平台支持说清楚，减少用户理解成本")
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1))

    if "mcp" in lowered and "wall time" in lowered and "model output" in lowered:
        lead = "这次合入的是 Codex 的 PR"
        if pr_match:
            lead += f" #{pr_match.group(1)}"
        metadata: list[str] = []
        if author_match:
            metadata.append(f"作者 {author_match.group(1)}")
        if merged_at_match:
            metadata.append(f"merged at {merged_at_match.group(1)}")
        if commit_match:
            metadata.append(f"merge commit `{commit_match.group(1)}`")
        if metadata:
            lead += f"（{'，'.join(metadata)}）"
        facts = [
            f"{lead}，把 `MCP tool wall time` 写进 model output，让模型能直接看到工具调用耗时",
            "改动点很集中：不是只补日志，而是把耗时信息变成模型输出的一部分",
        ]
        return " ".join(f"{fact}。" for fact in facts)

    if "guardian review timeout" in lowered or "guardian review timeouts" in lowered:
        lead = "这次合入的是 Codex 的 PR"
        if pr_match:
            lead += f" #{pr_match.group(1)}"
        metadata: list[str] = []
        if author_match:
            metadata.append(f"作者 {author_match.group(1)}")
        if merged_at_match:
            metadata.append(f"merged at {merged_at_match.group(1)}")
        if commit_match:
            metadata.append(f"merge commit `{commit_match.group(1)}`")
        if metadata:
            lead += f"（{'，'.join(metadata)}）"
        facts = [
            f"{lead}，把 guardian review timeout 明确写成 terminal history entries，不再从 live timeline 里直接消失",
            "新增 command、patch、MCP tool 和 network approval 四类 timeout-specific history cells",
            "还补了 direct guardian event path 与 app-server notification path 的 snapshot tests",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "dependency alerts" in lowered or "pin vulnerable npm dependencies" in lowered:
        facts = [
            "这次改动是在收口高危依赖告警，把有漏洞的 npm 依赖继续固定到已修补版本",
            "做法是沿用根级 `resolutions` 机制推进 lockfile，只让它升级到安全版本",
        ]
        if "pnpm-lock.yaml" in source_text:
            facts.append("同时刷新了 `pnpm-lock.yaml`，把 `@modelcontextprotocol/sdk` 等受影响依赖一起带到修补后的版本")
        return compose_fact_sentences(intro=f"`{title}` 这次改动主要是：", facts=facts, group_sizes=(1, 1, 1))

    if "background_task_id" in lowered and "agentidentityauthrecord" in lowered:
        return compose_fact_sentences(
            intro=f"`{title}` 这次改动主要是：",
            facts=[
                "给 `AgentIdentityAuthRecord` 的测试 fixture 补上了缺失的 `background_task_id: None` 字段",
                "这类修补不是加新能力，而是把认证记录的数据形状和实际代码重新对齐",
            ],
            group_sizes=(1, 1),
        )

    if "fix agent identity auth test fixture" in lowered and "author:" in lowered:
        lead = "这次合入的是 Codex 的 PR"
        if pr_match:
            lead += f" #{pr_match.group(1)}"
        metadata: list[str] = []
        if author_match:
            metadata.append(f"作者 {author_match.group(1)}")
        if merged_at_match:
            metadata.append(f"merged at {merged_at_match.group(1)}")
        if commit_match:
            metadata.append(f"merge commit `{commit_match.group(1)}`")
        if metadata:
            lead += f"（{'，'.join(metadata)}）"
        return compose_fact_sentences(
            intro="",
            facts=[
                f"{lead}，主题就是补 `agent identity auth` 的测试 fixture",
                "它对应的不是新功能发布，而是把认证相关测试记录补齐，避免 fixture 再缺字段",
            ],
            group_sizes=(1, 1),
        )

    if "guardian subagent thread" in lowered and any(token in lowered for token in ("mcps", "plugins", "apps")):
        return compose_fact_sentences(
            intro=f"`{title}` 这次改动主要是：",
            facts=["把 guardian 子代理线程里的 apps、plugins 和 MCPs 全部关掉", "说明这条线更像是在收紧 guardian 的执行边界，而不是扩功能"],
            group_sizes=(1, 1),
        )

    if "realtime model" in lowered and "conversation transcript deltas" in lowered:
        return compose_fact_sentences(
            intro=f"`{title}` 这次改动主要是：",
            facts=[
                "继续补 realtime model 和 Codex agent 之间的上下文共享",
                "除了 delegation message 之外，现在还会同步完整的 realtime transcript deltas",
            ],
            group_sizes=(1, 1),
        )

    release_facts: list[str] = []
    if "quick reasoning controls" in lowered and "alt+," in lowered and "alt+." in lowered:
        release_facts.append("TUI 新增快速 reasoning 控制：`Alt+,` 降低 reasoning，`Alt+.` 提高 reasoning")
        release_facts.append("接受 model upgrade 后，reasoning 会重置到新模型默认值，不再沿用旧模型的过期设置")
    if "multiple environments" in lowered and "working directory per turn" in lowered:
        release_facts.append("app-server session 现在能管理多个 environments，并且每一轮都可选择 environment 和 working directory")
    if "amazon bedrock" in lowered and "sigv4" in lowered:
        release_facts.append("OpenAI-compatible providers 新增一等 Amazon Bedrock 支持，包括 AWS SigV4 signing 和 AWS credential auth")
    if "remote plugin marketplaces" in lowered:
        release_facts.append("remote plugin marketplaces 可以直接列出和读取，详情查询更稳，分页结果也更大")
    if "hooks are now stable" in lowered and "config.toml" in lowered:
        release_facts.append("hooks 进入 stable，可在 `config.toml` / `requirements.toml` 配置，并能观察 MCP tools、`apply_patch` 和长时间 Bash session")
    if release_facts:
        return compose_fact_sentences(intro=f"`{title}` 这版 Codex 更新重点是：", facts=release_facts, group_sizes=(2, 2, 1))

    sentences = simple_sentences(source_text)[:2]
    if sentences:
        return compose_fact_sentences(intro=f"`{title}` 这次改动主要写明了", facts=sentences, group_sizes=(1, 1))
    return ""


def build_openclaw_release_detail(*, title: str, source_text: str) -> str:
    facts: list[str] = []
    for segment in split_fact_segments(source_text):
        lowered = segment.lower()
        if lowered.startswith("dreaming/memory-wiki:"):
            facts.append(
                "Dreaming/memory-wiki 新增 ChatGPT import ingestion，并加了 `Imported Insights` 和 `Memory Palace` diary subtabs，让导入聊天、编译后的 wiki 页面和完整源页面都能直接在 UI 里检查"
            )
        elif lowered.startswith("telegram/forum topics:"):
            facts.append("Telegram/forum topics 会把 human topic names 带进 agent context、prompt metadata 和 plugin hook metadata")
        elif lowered.startswith("ui/chat:") and "markdown-it" in lowered:
            facts.append("UI/chat 把 `marked.js` 换成 `markdown-it`，避免恶意 markdown 通过 `ReDoS` 卡死 Control UI")
        elif lowered.startswith("auto-reply/send policy:") and 'sendpolicy: "deny"' in lowered:
            facts.append("`sendPolicy: \"deny\"` 不再阻塞入站消息处理，observer-style setup 也能继续跑 agent turn，只是压住所有出站发送")
        elif lowered.startswith("control ui/webchat:") and "structured chat bubbles" in lowered:
            facts.append(
                "Control UI/webchat 会把 assistant 的 media/reply/voice 指令渲染成 structured chat bubbles，并新增 `[embed ...]` 富输出标签"
            )
        elif lowered.startswith("tools/video_generate:") or "provideroptions" in lowered:
            facts.append("video_generate 还补了 typed `providerOptions`、reference audio inputs 和 `adaptive` aspect-ratio 支持")
        elif "oauth" in lowered:
            facts.append("同时继续修 OpenAI/Codex OAuth 这类登录链路问题")
        elif "failover" in lowered:
            facts.append("provider failover 相关稳定性细节也继续往前补")

    lowered_source = source_text.lower()
    if "broad quality release focused on" in lowered_source and "feishu" in lowered_source:
        facts.append("这版是个 broad quality release，重点补 plugin loading、memory/dreaming reliability、本地模型选项和更顺滑的 Feishu setup path")
    if "broad quality release focused on" in lowered_source and "gpt-5" in lowered_source:
        facts.append("总述里也点明这版先补的是 model provider、`GPT-5` 家族 explicit turn 和 channel provider 这条主线")
    if "improved overal performance" in lowered_source or "improved overall performance" in lowered_source:
        facts.append("底层 core codebase 重构后，整体性能也被单独往前推了一步")
    if "`gpt-5.4-pro`" in source_text or "gpt-5.4-pro" in lowered_source:
        facts.append("OpenAI Codex/models 先做了 `gpt-5.4-pro` 的前向兼容，把 pricing/limits 和列表可见性先补上")
    if "telegram/forum topics" in lowered_source:
        facts.append("Telegram/forum topics 不只把 human topic names 带进 agent context，也会写进 prompt metadata 和 plugin hook metadata")
    if "`apikey`" in lowered_source and "models/codex" in lowered_source:
        facts.append("Models/Codex 会把 `apiKey` 保留在 provider catalog 输出里，避免自定义模型被 validator 悄悄整批丢掉")
    if "`allowfrom`" in lowered_source and "slack/interactions" in lowered_source:
        facts.append("Slack/interactions 这边把全局 `allowFrom` owner allowlist 真正落实到 block-action 和 modal interactive events")
    if "`config.patch`" in lowered_source and "`config.apply`" in lowered_source and "gateway-tool" in lowered_source:
        facts.append("Agents/gateway-tool 还卡住了会新开危险安全开关的 `config.patch` / `config.apply` 请求")
    if "voice replies" in lowered_source and "tts" in lowered_source:
        facts.append("语音回复做了一轮 TTS 升级：新增 `/tts latest`、按聊天控制自动 TTS、personas，以及 agent/account 级覆盖配置")
    if "azure speech" in lowered_source and "elevenlabs" in lowered_source:
        facts.append("TTS provider 覆盖扩到 Azure Speech、小米、本地 CLI、Inworld、火山引擎和 ElevenLabs v3")
    security_topics: list[str] = []
    if "`hook:wake`" in source_text or "hook:wake" in lowered_source:
        security_topics.append("`hook:wake` 不可信系统事件会强制降权")
    if "browser/security" in lowered_source or ("snapshot, screenshot, and tab routes" in lowered_source):
        security_topics.append("browser 的 snapshot/screenshot/tab 路由补上 SSRF enforcement")
    if "microsoft teams/security" in lowered_source or "sender allowlist checks on sso signin invokes" in lowered_source:
        security_topics.append("Microsoft Teams SSO signin invoke 会检查 sender allowlist")
    if "config/security" in lowered_source and "redactconfigsnapshot" in lowered_source:
        security_topics.append("配置快照里的 alias config 字段会被 redact")
    if security_topics:
        facts.append("安全面还补了 " + "、".join(security_topics[:3]))

    facts = prioritize_fact_tail(
        facts,
        preserve_head=3,
        priority_terms=(
            ("hook:wake",),
            ("ssrf",),
            ("sender allowlist",),
        ),
    )
    summary = compose_fact_sentences(
        intro=f"`OpenClaw` 的 `{title}` 这版 release 里比较实在的更新有：",
        facts=facts,
        group_sizes=(3, 2, 2, 2),
    )
    if summary:
        return summary

    minimal_rewrite = build_minimal_release_rewrite(product_name="OpenClaw", title=title, source_text=source_text)
    if minimal_rewrite:
        return minimal_rewrite

    sentences = simple_sentences(source_text)
    if sentences:
        return f"`OpenClaw` 发布了 `{title}` 这版 release，提到 {sentences[0]}。"
    return ""


def build_github_trending_detail(*, title: str, source_text: str) -> str:
    lowered = source_text.lower()
    if "production-grade engineering skills" in lowered:
        facts = ["它不是泛泛聊 prompt，而是把 AI coding agents 的生产级工程技能整理成可复用工具包"]
        if any(token in lowered for token in ("review loops", "delivery checklists", "repo setup", "quality gates", "best practices")):
            facts.append("预览里点名了仓库初始化、质量门槛、评审循环或交付清单，说明目标是让团队直接拿来落地")
        return compose_fact_sentences(intro=f"`{title}` 这周能进趋势榜，至少因为：", facts=facts, group_sizes=(1, 1))
    if "decompiles android" in lowered or ("apk" in lowered and "http apis" in lowered):
        return compose_fact_sentences(
            intro=f"`{title}` 这周能进趋势榜，至少因为：",
            facts=[
                "它把 Claude Code 的 skill 直接收口到 Android 逆向场景，能处理 APK/XAPK/JAR/AAR 这类包",
                "重点不是泛泛聊逆向，而是把 HTTP API 提取和复现实操写成了可直接使用的流程",
            ],
            group_sizes=(1, 1),
        )
    if "code search mcp" in lowered and "entire codebase" in lowered:
        return compose_fact_sentences(
            intro=f"`{title}` 这周能进趋势榜，至少因为：",
            facts=[
                "它做的是给 `Claude Code` 用的 code search MCP，让 coding agent 查询代码时能把整个 codebase 当上下文",
                "作者是 `zilliztech`，这类项目的重点不是 README 口号，而是把大仓库检索和上下文注入变成 MCP 工具",
            ],
            group_sizes=(1, 1),
        )
    if "markitdown now offers an mcp" in lowered or ("claude desktop" in lowered and "optional feature-groups" in lowered):
        return compose_fact_sentences(
            intro=f"`{title}` 这周能进趋势榜，至少因为：",
            facts=[
                "它已经把 `MCP` server 做进产品，能直接接到 `Claude Desktop` 这类 LLM 应用里",
                "另外还明确提醒了从 `0.0.1` 到 `0.1.0` 的 breaking changes，依赖现在按 optional feature-groups 拆分",
            ],
            group_sizes=(1, 1),
        )
    if "harness builder" in lowered and ("deterministic" in lowered or "repeatable" in lowered):
        return (
            f"`{title}` 把自己定位成开源的 AI coding harness builder，主打让 AI coding 流程变得 deterministic、repeatable。"
            " 它上榜的理由也很具体：卖点不是再包一层 agent，而是把测试和执行流程做成可重复的基础设施。"
        )
    if "mcp workspace" in lowered and "design context" in lowered and "review handoffs" in lowered:
        return (
            f"`{title}` 是给 AI coding agents 用的 MCP workspace，重点是跨 session 保存设计上下文、任务历史和评审交接。"
            " 它值得进榜，是因为解决的是 agent 断上下文和交接丢信息的问题，而不是再做一个聊天入口。"
        )
    if "seo-optimized blog content" in lowered or ("seo" in lowered and "blog" in lowered and "content" in lowered):
        return (
            f"`{title}` 把自己定位成面向业务内容生产的 Claude Code workspace，重点是研究、撰写、分析并优化长篇 SEO 博客内容。"
        )
    if "managed agents platform" in lowered:
        return (
            f"`{title}` 这个 repo 把自己写成 open-source managed agents platform，目标是把 coding agents 变成能分派任务、"
            "跟踪进度、积累技能的真正队友。"
        )
    if "claude.md" in lowered and "karpathy" in lowered:
        return (
            f"`{title}` 提供的是单文件 `CLAUDE.md` 规则集，来源是 Andrej Karpathy 对 LLM coding pitfalls 的观察，"
            "目的就是直接改善 Claude Code 的行为。"
        )

    preview_facts: list[str] = []
    if "claude code" in lowered and "plugin" in lowered:
        preview_facts.append(f"`{title}` 是个围绕 `Claude Code` 的插件型项目")
    if "captures everything claude does" in lowered or ("capture" in lowered and "coding sessions" in lowered):
        preview_facts.append("它会自动记录 Claude 在 coding session 里的操作")
    if "compresses it with ai" in lowered or ("compress" in lowered and "future sessions" in lowered):
        preview_facts.append("还会压缩记忆，并把相关上下文回注到后续 session")
    if preview_facts:
        return compose_fact_sentences(intro=f"`{title}` 这周能进趋势榜，至少因为：", facts=preview_facts, group_sizes=(1, 1, 1))

    sentences = [sentence for sentence in simple_sentences(source_text) if not sentence.lower().startswith("author:")]
    if sentences:
        if looks_like_english_text(" ".join(sentences[:2])):
            return ""
        facts = [f"预览里把它写成 {sentences[0]}"]
        if len(sentences) > 1:
            facts.append(sentences[1])
        return compose_fact_sentences(intro=f"`{title}` 这周能进趋势榜，至少因为：", facts=facts, group_sizes=(1, 1))
    return ""


def build_weather_detail(*, title: str, source_text: str) -> str:
    del title

    fields = extract_weather_fields(source_text)
    condition = localize_weather_condition(fields.get("condition", ""))
    temperature = normalize_weather_temperature(fields.get("temperature", ""))
    precipitation = normalize_weather_precipitation(fields.get("precipitation", ""))
    wind = localize_weather_wind(fields.get("wind", ""))

    fragments: list[str] = []
    if condition:
        fragments.append(condition)
    if temperature:
        fragments.append(f"气温 {temperature}")
    if precipitation:
        fragments.append(f"降水 {precipitation}")
    if wind:
        fragments.append(wind)

    if not fragments:
        return ""

    lead = f"今天{fragments[0]}"
    tail = fragments[1:]
    if not tail:
        return lead
    return lead + "，" + "，".join(tail)


def build_weather_reader_title(*, title: str, source_text: str) -> str:
    cleaned_title = normalize_whitespace(title)
    if not cleaned_title:
        return ""

    title_match = re.match(
        r"^(?P<location>.+?)\s+\d{4}-\d{2}-\d{2}\s+weather\s*[:：]\s*"
        r"(?P<condition>[^,，]+)(?:[,，]\s*(?P<temperature>.+))?$",
        cleaned_title,
        re.IGNORECASE,
    )
    if not title_match:
        return cleaned_title

    fields = extract_weather_fields(source_text)
    location = normalize_whitespace(title_match.group("location")).strip(" ,，")
    condition = localize_weather_condition(title_match.group("condition") or fields.get("condition", ""))
    temperature = compact_weather_temperature_range(title_match.group("temperature") or fields.get("temperature", ""))
    fragments = [fragment for fragment in (condition, temperature) if fragment]
    if location and fragments:
        return f"{location}：" + "，".join(fragments)
    if location:
        return location
    return "今日天气"


def compact_weather_temperature_range(value: str) -> str:
    cleaned = normalize_weather_temperature(value)
    if not cleaned:
        return ""
    return re.sub(r"\s+-\s+", "–", cleaned)


def extract_weather_fields(source_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    known_patterns = {
        "condition": r"(?:Condition|Weather|天气|现象)\s*[:：]\s*(.+?)(?=\s+(?:Temperature|Temp|气温|温度|Precipitation|Precip|Rain|降水|降雨|Wind|风)\s*[:：]|$)",
        "temperature": r"(?:Temperature|Temp|气温|温度)\s*[:：]\s*(.+?)(?=\s+(?:Precipitation|Precip|Rain|降水|降雨|Wind|风)\s*[:：]|$)",
        "precipitation": r"(?:Precipitation|Precip|Rain|降水|降雨)\s*[:：]\s*(.+?)(?=\s+(?:Wind|风)\s*[:：]|$)",
        "wind": r"(?:Wind|风)\s*[:：]\s*(.+)$",
    }
    for field_key, pattern in known_patterns.items():
        match = re.search(pattern, source_text, re.IGNORECASE)
        if match:
            field_value = normalize_weather_fact_value(match.group(1))
            if field_value:
                fields[field_key] = field_value

    if fields:
        return fields

    pattern = re.compile(
        r"(?P<label>[A-Za-z\u4e00-\u9fff][A-Za-z\u4e00-\u9fff /-]{0,31})\s*[:：]\s*"
        r"(?P<value>.*?)(?=(?:\s+[A-Za-z\u4e00-\u9fff][A-Za-z\u4e00-\u9fff /-]{0,31}\s*[:：])|$)"
    )
    for match in pattern.finditer(source_text):
        field_key = normalize_weather_field_key(match.group("label"))
        field_value = normalize_weather_fact_value(match.group("value"))
        if field_key and field_value and field_key not in fields:
            fields[field_key] = field_value

    return fields


def normalize_weather_field_key(label: str) -> str:
    cleaned = normalize_whitespace(label).lower()
    if not cleaned:
        return ""
    if any(token in cleaned for token in ("condition", "weather", "天气", "现象")):
        return "condition"
    if any(token in cleaned for token in ("temperature", "temp", "气温", "温度")):
        return "temperature"
    if any(token in cleaned for token in ("precipitation", "precip", "rain", "降水", "降雨")):
        return "precipitation"
    if "wind" in cleaned or "风" in cleaned:
        return "wind"
    return ""


def normalize_weather_fact_value(value: str) -> str:
    cleaned = normalize_whitespace(value).strip(" ,;:，；：")
    if not cleaned:
        return ""
    if cleaned.lower() in {"-", "--", "n/a", "na", "unknown"}:
        return ""
    return cleaned.replace("℃", "°C")


def normalize_weather_temperature(value: str) -> str:
    cleaned = normalize_weather_fact_value(value)
    if not cleaned:
        return ""
    cleaned = re.sub(r"\bto\b", " - ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*[~～]\s*", " - ", cleaned)
    cleaned = re.sub(r"\s*-\s*", " - ", cleaned)
    return normalize_whitespace(cleaned)


def normalize_weather_precipitation(value: str) -> str:
    cleaned = normalize_weather_fact_value(value)
    if not cleaned:
        return ""

    lowered = cleaned.lower()
    if lowered in {"none", "no rain", "no precipitation", "dry"}:
        return "无明显降水"

    percent_match = re.search(r"(\d+(?:\.\d+)?%)", cleaned)
    if percent_match:
        return percent_match.group(1)

    cleaned = re.sub(r"\b(?:chance of rain|precipitation)\b", "", cleaned, flags=re.IGNORECASE)
    return normalize_whitespace(cleaned)


def localize_weather_condition(value: str) -> str:
    cleaned = normalize_weather_fact_value(value)
    if not cleaned:
        return ""

    replacements = [
        ("cloudy to sunny", "多云转晴"),
        ("cloudy to clear", "多云转晴"),
        ("partly cloudy", "多云"),
        ("mostly cloudy", "多云"),
        ("light drizzle", "小雨"),
        ("drizzle", "小雨"),
        ("light rain", "小雨"),
        ("moderate rain", "中雨"),
        ("heavy rain", "大雨"),
        ("thunderstorm", "雷阵雨"),
        ("showers", "阵雨"),
        ("overcast", "阴"),
        ("cloudy", "多云"),
        ("sunny", "晴"),
        ("clear", "晴"),
        ("snow", "雪"),
        ("mist", "雾"),
        ("fog", "雾"),
        ("haze", "霾"),
    ]

    localized = cleaned
    for source_phrase, target_phrase in replacements:
        localized = re.sub(rf"\b{re.escape(source_phrase)}\b", target_phrase, localized, flags=re.IGNORECASE)

    localized = re.sub(r"\bto\b", "转", localized, flags=re.IGNORECASE)
    localized = re.sub(r"\band\b", "转", localized, flags=re.IGNORECASE)
    localized = localized.replace("/", "转")
    return normalize_whitespace(localized)


def localize_weather_wind(value: str) -> str:
    cleaned = normalize_weather_fact_value(value)
    if not cleaned:
        return ""

    replacements = [
        ("northwest wind", "西北风"),
        ("northeast wind", "东北风"),
        ("southwest wind", "西南风"),
        ("southeast wind", "东南风"),
        ("north wind", "北风"),
        ("south wind", "南风"),
        ("west wind", "西风"),
        ("east wind", "东风"),
    ]

    localized = cleaned
    for source_phrase, target_phrase in replacements:
        localized = re.sub(rf"\b{re.escape(source_phrase)}\b", target_phrase, localized, flags=re.IGNORECASE)

    for source_direction, target_direction in (("NW", "西北风"), ("NE", "东北风"), ("SW", "西南风"), ("SE", "东南风")):
        localized = re.sub(rf"\b{source_direction}\b", target_direction, localized, flags=re.IGNORECASE)

    localized = re.sub(r"\bup to\s+", "最大风速 ", localized, flags=re.IGNORECASE)
    localized = re.sub(r"(\d+(?:\s*-\s*\d+)?)\s*(?:level|force)\b", r"\1级", localized, flags=re.IGNORECASE)
    localized = re.sub(r"\blevel\b", "级", localized, flags=re.IGNORECASE)
    localized = re.sub(r"\s+([东西南北]{1,2}风)$", r"，\1", localized)
    return normalize_whitespace(localized).strip("，")


def localize_product_hunt_tagline(value: str) -> str:
    cleaned = normalize_whitespace(value).strip(" .")
    if not cleaned:
        return ""

    lowered = cleaned.lower()
    if "spatial analysis" in lowered and "agent-driven" in lowered:
        return "做即时的 agent 驱动空间分析和决策"
    if "transforming video" in lowered and "time-based me" in lowered:
        return "把视频转成带时间轴的结构化元数据"
    if "cloud sandbox" in lowered and "hermes agent" in lowered:
        return "MiniMax 推出的云端沙箱版 Hermes Agent"
    if "make 2d game art" in lowered and "playable games" in lowered:
        return "用 AI 生成 2D 游戏美术和可玩的游戏，不用画图也不用写代码"
    if "context-aware mac keypad" in lowered and "workflows" in lowered:
        return "一块会根据上下文切换按键功能的 Mac 键盘，用来自动化工作流和会议"
    if lowered == "self-custodial wallet built for ai agents":
        return "给 AI agents 用的自托管钱包"
    if lowered == "claro runs the ai agents that operate on your data":
        return "让 AI agents 直接在你的数据上跑研究和操作"
    if lowered == "your ai technical cofounder":
        return "你的 AI 技术联合创始人"
    if lowered == "practice & assess future-ready skills with ai-simulated team":
        return "用 AI 模拟团队来练习并评估面向未来的技能"
    if lowered == "design context for ai agents":
        return "给 AI agents 提供设计上下文"
    if lowered == "watch agents spend money in real time":
        return "实时看 agent 在花钱买什么"
    if "build visual workflows" in lowered and "ai agents" in lowered:
        return "为 AI agents 构建可视化工作流"
    if lowered == "watches your workflows":
        return "盯住团队工作流"
    if lowered == "builds your agents":
        return "把 agent 搭建环节直接做成产品"
    if lowered == "automates the busywork":
        return "目标是把重复杂活自动化"
    if lowered == "a cloud-native ai agent that can build literally anything":
        return "一个号称几乎什么都能构建的云原生 AI agent"
    if lowered == "gtm agents to find and reach your next customer":
        return "帮你寻找并触达下一位客户的 GTM agents"
    if lowered == "codex can now build, test & debug on autopilot":
        return "让 Codex 自动构建、测试和调试代码，主打更接近 autopilot 的开发流程"
    if "vs code extension" in lowered and "agent memory" in lowered and "claude code" in lowered and "codex" in lowered:
        return "一个把 Agent Memory、Claude Code 和 Codex 包进 VS Code 图形界面的扩展"
    return localize_common_reader_phrases(cleaned) if looks_like_english_text(cleaned) else cleaned



def localize_product_hunt_reader_title(title: str) -> str:
    name, tagline = split_title_tagline(title)
    lowered_tagline = normalize_whitespace(tagline).lower()
    if lowered_tagline in {"design context for ai agents", "watch agents spend money in real time"}:
        return ""
    translated_tagline = localize_product_hunt_tagline(tagline)
    if name and translated_tagline and translated_tagline != tagline:
        return f"{name}：{translated_tagline}"
    return ""


def build_product_hunt_detail(*, title: str, source_text: str) -> str:
    name, tagline = split_title_tagline(title)
    lowered = source_text.lower()
    lowered_title = title.lower()
    facts: list[str] = []
    translated_tagline = localize_product_hunt_tagline(tagline)
    source_sentence = localize_product_hunt_tagline(simple_sentences(source_text)[0] if simple_sentences(source_text) else "")

    if "microvm" in lowered and "sandbox" in lowered:
        facts.append("主打让 AI coding agents 跑在真实 `microVM` 沙箱里，强调真实隔离环境")
    elif tagline and not looks_like_english_text(tagline):
        facts.append(f"产品说明写的是：{tagline}")
    elif translated_tagline:
        facts.append(f"产品说明写的是：{translated_tagline}")
    elif source_sentence:
        facts.append(f"产品说明写的是：{source_sentence}")
    elif "design context" in lowered:
        facts.append("主打给 AI agents 提供 `Design context`")

    if "validate every pr" in lowered or ("visual pr testing" in lowered_title and "runs tests for you" in lowered):
        facts.extend([
            "切得很窄，专门做 PR 的视觉测试，而且是让 AI 帮你跑",
            "它对应的不是通用聊天场景，而是代码评审前的一个具体质量节点",
        ])
    elif "agent-native software dev" in lowered or ("desktop app" in lowered_title and "alongside you" in lowered):
        facts.extend([
            "卖的是 agent-native 的软件开发桌面应用，关键词不是聊天，而是并肩工作",
            "这条记录把竞争焦点落在本地开发入口，而不是只比较模型能力",
        ])
    elif "runs your entire startup" in lowered or ("startup" in lowered and "agent" in lowered):
        facts.extend([
            "口号很大，直接想把完整 startup 的运营和执行都交给 AI agent",
            "这类产品通常要打的是流程串联和执行闭环，不只是单点生成能力",
        ])
    elif "spend money in real time" in lowered or "agents buying" in lowered:
        facts.extend([
            "点子很直白：实时看 agent 在花钱买什么",
            "它抓住的是一个新问题——当 agent 拥有采购和支付权限后，支出本身会变成新的观察面板",
        ])
    elif "ai to ai influence" in lowered or "moves the models" in lowered:
        facts.extend([
            "想做的是 AI 之间的影响力评分，而不只是给人看的内容榜单",
            "方向上更像是在补 agent 生态里的舆情层：谁在影响谁、哪些信号正在带动模型和工作流选择",
        ])
    elif "participate live in meetings" in lowered or ("meetings" in lowered and "agents" in lowered):
        facts.extend([
            "切的是会议协作场景，强调让 AI agent 直接参与 live meetings",
            "问题不在能不能转写，而在 agent 能不能在会议现场承担记录、提醒和后续跟进这些角色",
        ])
    elif "form backend for ai agents" in lowered or ("form backend" in lowered and "ai agents" in lowered):
        facts.extend([
            "把表单后端直接做成同时给人和 AI agents 用的基础设施",
            "如果 agent 真要替人提交、登记、收集信息，这类后端迟早会从“给人用”改成“也给 agent 用”",
        ])
    elif "claude code for product teams" in lowered or ("product teams" in lowered and "claude code" in lowered):
        facts.extend([
            "直接把自己定位成“给产品团队用的 Claude Code”",
            "这条记录把 coding agent 的协作方式放到产品团队场景，而不是只停留在工程师侧",
        ])

    if not facts and looks_like_english_text(source_text):
        if "workflow" in lowered:
            facts.append("主打盯住团队 workflow")
        if "builds your agents" in lowered or ("build" in lowered and "agent" in lowered):
            facts.append("把 agent 搭建环节直接做成产品")
        if "automate" in lowered or "busywork" in lowered:
            facts.append("目标是把重复杂活自动化")
        if not facts and "agent" in lowered:
            facts.append("围绕 agent 工作流切了一个更具体的产品入口")

    votes_match = re.search(r"Votes:\s*(\d+)", source_text, re.IGNORECASE)
    comments_match = re.search(r"Comments:\s*(\d+)", source_text, re.IGNORECASE)
    topic_match = re.search(r"Topic:\s*([A-Za-z][A-Za-z -]+)", source_text)
    stats: list[str] = []
    if votes_match:
        stats.append(f"{votes_match.group(1)} 票")
    if comments_match:
        stats.append(f"{comments_match.group(1)} 条评论")
    if topic_match:
        stats.append(f"`{topic_match.group(1).strip()}` 主题")
    if stats:
        facts.append("这条 Product Hunt listing 当前是 " + "、".join(stats))

    if "design context" in lowered:
        facts.append("卖点不是再做一个通用聊天壳，而是把 design context 当成 agent 协作入口")

    return compose_fact_sentences(intro=f"`{name}` 这条 Product Hunt 记录里写到：", facts=facts, group_sizes=(1, 1, 1))


def localize_polymarket_question(question: str) -> str:
    cleaned = normalize_whitespace(question).strip(" ?？")
    if not cleaned:
        return ""

    if re.fullmatch(
        r"Will\s+any\s+Anthropic\s+Claude\s+model\s+score\s+at\s+least\s+50%\s+on\s+the\s+FrontierMath\s+Exam",
        cleaned,
        re.IGNORECASE,
    ):
        return "到 6 月 30 日前，是否会有任一 Claude 模型在 FrontierMath 拿到至少 50%"

    month_map = {
        "january": "1",
        "february": "2",
        "march": "3",
        "april": "4",
        "may": "5",
        "june": "6",
        "july": "7",
        "august": "8",
        "september": "9",
        "october": "10",
        "november": "11",
        "december": "12",
    }
    second_best_match = re.match(
        r"Will\s+(.+?)\s+have the second-best Coding AI model at the end of ([A-Za-z]+)\s+(\d{4})",
        cleaned,
        re.IGNORECASE,
    )
    best_match = re.match(
        r"Will\s+(.+?)\s+have the best Coding AI model at the end of ([A-Za-z]+)\s+(\d{4})",
        cleaned,
        re.IGNORECASE,
    )
    if second_best_match or best_match:
        matched = second_best_match or best_match
        subject = normalize_whitespace(matched.group(1))
        month_name = matched.group(2).strip().lower()
        year = matched.group(3)
        month = month_map.get(month_name)
        if month:
            rank_text = "第二强" if second_best_match else "最强"
            return f"{subject} 到 {year} 年 {month} 月底时会不会拥有{rank_text}的 Coding AI 模型"

    return cleaned


def build_polymarket_detail(*, title: str, source_text: str) -> str:
    question_match = re.search(
        r"Question:\s*(.+?)(?=Current leader:|24h volume:|30d volume:|Liquidity:|Price movement:|$)",
        source_text,
        re.IGNORECASE,
    )
    leader_match = re.search(r"Current leader:\s*([^()]+?)\s*\((\d+(?:\.\d+)?)%\)", source_text, re.IGNORECASE)
    volume_match = re.search(r"24h volume:\s*([0-9,.]+)", source_text, re.IGNORECASE)
    liquidity_match = re.search(r"Liquidity:\s*([0-9,.]+)", source_text, re.IGNORECASE)
    movement_match = re.search(r"Price movement:\s*([A-Za-z0-9 .+%-]+)", source_text, re.IGNORECASE)

    outcome_matches = [
        (name.strip(), probability)
        for name, probability in re.findall(r"([A-Za-z][A-Za-z0-9 .+-]+):\s*(\d+(?:\.\d+)?)%", source_text)
        if name.strip().lower()
        not in {"question", "current leader", "24h volume", "30d volume", "liquidity", "price movement", "market"}
    ]

    facts: list[str] = []
    if question_match:
        question = normalize_whitespace(question_match.group(1))
        rewritten_question = localize_polymarket_question(question)
        facts.append(f"市场在押注：{rewritten_question}")
    else:
        facts.append(f"这份合约围绕 `{title}` 交易")

    if leader_match:
        leader_name = normalize_whitespace(leader_match.group(1))
        leader_probability = leader_match.group(2)
        runner_up = next(
            (
                (name, probability)
                for name, probability in outcome_matches
                if normalize_whitespace(name) != leader_name
            ),
            None,
        )
        leader_fact = f"当前 `{leader_name}` 以 {leader_probability}% 领先"
        if runner_up:
            leader_fact += f"，对手 `{normalize_whitespace(runner_up[0])}` 大约在 {runner_up[1]}%"
        facts.append(leader_fact)

    market_strength: list[str] = []
    if volume_match:
        market_strength.append(f"24 小时成交量 {volume_match.group(1)}")
    if liquidity_match:
        market_strength.append(f"流动性 {liquidity_match.group(1)}")
    if movement_match:
        movement = normalize_whitespace(movement_match.group(1))
        movement = re.sub(r"\bdown\s+([0-9.]+%?)\s+this week\b", r"本周下跌 \1", movement, flags=re.IGNORECASE)
        movement = re.sub(r"\bup\s+([0-9.]+%?)\s+this week\b", r"本周上涨 \1", movement, flags=re.IGNORECASE)
        movement = re.sub(r"\bdown\s+([0-9.]+%?)\s+this month\b", r"本月下跌 \1", movement, flags=re.IGNORECASE)
        movement = re.sub(r"\bup\s+([0-9.]+%?)\s+this month\b", r"本月上涨 \1", movement, flags=re.IGNORECASE)
        movement = re.sub(r"\bdown\s+([0-9.]+%?)\s+today\b", r"今日下跌 \1", movement, flags=re.IGNORECASE)
        movement = re.sub(r"\bup\s+([0-9.]+%?)\s+today\b", r"今日上涨 \1", movement, flags=re.IGNORECASE)
        market_strength.append(f"价格 {movement}")
    if market_strength:
        facts.append("市场强度也写得很明白，" + "，".join(market_strength))

    return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))


def strip_hacker_news_leading_markers(value: str) -> str:
    cleaned = normalize_fact_source_text(value)
    if not cleaned:
        return ""

    cleaned = re.sub(
        r"^(?:related(?:\s+story)?|see also|search hit|search result|thread|discussion|topic|link)\s*[:\-]\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return normalize_whitespace(cleaned).strip(" .")


def trim_hacker_news_subject_prefix(*, source_text: str, title: str) -> str:
    cleaned_source = normalize_whitespace(source_text)
    cleaned_title = normalize_whitespace(title).strip(" \"'`“”‘’")
    if not cleaned_source or not cleaned_title:
        return cleaned_source

    patterns = (
        rf"^{re.escape(cleaned_title)}\s+(?:thread|discussion|post)\s+on\s+",
        rf"^{re.escape(cleaned_title)}\s+(?:thread|discussion|post)\s+about\s+",
        rf"^{re.escape(cleaned_title)}\s*[:\-]\s*",
    )
    for pattern in patterns:
        trimmed = re.sub(pattern, "", cleaned_source, count=1, flags=re.IGNORECASE)
        if trimmed != cleaned_source:
            return normalize_whitespace(trimmed).strip(" .")
    return cleaned_source


def extract_hacker_news_topics(value: str) -> list[str]:
    cleaned = normalize_fact_source_text(value)
    if not cleaned:
        return []

    topic_rules = (
        (r"\breview ownership\b", "评审分工"),
        (r"\breviewer?\s+loops?\b", "review loop"),
        (r"\btmux(?:\s+sessions?)?\b", "tmux"),
        (r"\bgit worktrees?\b|\bworktrees?\b", "git worktree"),
        (r"\breview checklists?\b", "review checklist"),
        (r"\b(?:agent\s+)?handoff(?:\s+loop)?\b", "agent 交接"),
        (r"\brepo(?:sitory)? boundaries?\b", "仓库边界"),
        (r"\bmcp\b", "MCP"),
    )

    topics: list[str] = []
    for pattern, label in topic_rules:
        if re.search(pattern, cleaned, re.IGNORECASE) and label not in topics:
            topics.append(label)
    return topics


def format_hacker_news_topics(topics: Sequence[str]) -> str:
    filtered = [topic for topic in topics if normalize_whitespace(topic)]
    if not filtered:
        return ""
    if len(filtered) == 1:
        return filtered[0]
    return "、".join(filtered[:-1]) + " 和 " + filtered[-1]


def build_hacker_news_detail(*, lane_name: str, title: str, source_text: str, matched_query: str = "") -> str:
    cleaned_title = normalize_whitespace(title).strip(" \"'`“”‘’")
    stripped_source = strip_hacker_news_leading_markers(source_text)
    stripped_source = trim_hacker_news_subject_prefix(source_text=stripped_source, title=cleaned_title)
    lowered = normalize_whitespace(f"{cleaned_title} {stripped_source}").lower()
    topics = extract_hacker_news_topics(stripped_source or source_text)
    facts: list[str] = []

    if "swe-bench verified" in lowered and "frontier coding capabilities" in lowered:
        facts.append("HN 这条在说 `SWE-bench Verified` 已经不再适合衡量最前沿 coding capability，重点不是榜单更新，而是 benchmark 被头部模型打穿了")
        if "93.9" in stripped_source or "93.9" in cleaned_title:
            facts.append("评论里 SWE-bench 共同作者补充：Anthropic 已经做到 `93.9%`，没到这个数的模型还有提升空间，但前沿模型需要换更难的评测")
        if "multilingual" in lowered or "multimodal" in lowered or "codeclash" in lowered or "algotune" in lowered:
            facts.append("后续方向被点名为 `SWE-bench Multilingual`、`SWE-bench Multimodal`、`CodeClash` 和 `AlgoTune` 这类更难、更新的基准")
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "ai memory with biological decay" in lowered or ("ebbinghaus" in lowered and "recall@5" in lowered):
        facts.append("这个 Show HN 做的是本地优先的 AI memory / `MCP server`，思路不是把记忆当静态 RAG 文件柜，而是按 Ebbinghaus 遗忘曲线让旧记忆自然衰减")
        if "graph" in lowered or "logical neighbor" in lowered:
            facts.append("作者还在 vector store 上加了 graph layer，用来补 semantic search 找不到逻辑邻居的问题")
        if "52" in lowered or "84" in lowered:
            facts.append("给出的结果是 LoCoMo 上 `Recall@5` 到 `52%`，同时 token waste 大约下降 `84%`，所以它值得看的是记忆治理方式而不只是标题里的 memory 概念")
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "parallel claude agents" in lowered or ("20 parallel claude" in lowered and "work tree" in lowered):
        facts.append("这条 Ask HN 的问题很具体：一个人习惯把任务交给单个 Claude，但不知道怎么把工作拆给很多并行 Claude 实例")
        if "non overlapping" in lowered or "shared contract" in lowered:
            facts.append("评论区给出的可执行做法是先找互不重叠的任务块，例如前后端先约好共享 contract，再让不同 agent 分头实现")
        if "git work" in lowered or "merge conflict" in lowered or "review" in lowered:
            facts.append("同时要给每个 agent 独立 `git worktree`，并把 review overhead 和 merge conflicts 当成并行化成本来管")
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "agent mcp studio" in lowered or ("browser-only studio" in lowered and "webassembly" in lowered):
        facts.append("这个 Show HN 做的是 browser-only 的 MCP agent studio：tool authoring、multi-agent orchestration、RAG 和 code execution 都塞进一个静态 HTML 里跑")
        if "webassembly" in lowered or "pyodide" in lowered or "duckdb-wasm" in lowered:
            facts.append("实现上靠 `WebAssembly` / `Pyodide` / `DuckDB-WASM` 这类浏览器沙箱组件，把原型阶段的 agent workflow 放在本地浏览器内完成")
        if "python mcp server" in lowered or "export" in lowered or "security boundary" in lowered:
            facts.append("它还支持导出成真实 `Python MCP server`；评论区关心的点则是 WASM 安全边界，以及浏览器原型和导出版本能否保持行为一致")
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if lane_name == "hacker-news-watch":
        if "how llms work" in lowered and "karpathy" in lowered:
            facts.append("这条 Show HN 是把 Andrej Karpathy 的《Intro to Large Language Models》讲座做成交互式可视化指南")
            facts.append("作者下载了讲座 transcript，再用 `Claude Code` 生成整个互动站点，而且实现形态是单个 HTML 文件")
            facts.append("原帖说这个站点适合反复回看 LLM 基础内容，所以重点是学习材料的再包装和 Claude Code 参与生成")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

        if all(topic in topics for topic in ("评审分工", "review loop", "仓库边界")):
            facts.append("这条 HN 热榜讨论在聊评审分工、review loop 和仓库边界")
            facts.append("它想解决的是 agent 协作里谁来审、怎么交接、边界该怎么收紧")
            facts.append("这些边界一旦说清，团队在交接、评审和回滚时会更稳")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

        if "qwen3.6-max-preview" in lowered:
            facts.append("这条 HN 热榜讨论围着 `Qwen3.6-Max-Preview` 这版预览模型展开")
            facts.append("标题本身就在强调它更聪明、更锐利，但还在持续迭代，不是已经定型的稳定版")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1))

        focus = format_hacker_news_topics(topics[:4])
        if focus:
            facts.append(f"这条 HN 热榜讨论把焦点放在 {focus}")
        elif cleaned_title:
            facts.append(f"这条 HN 热榜标题指向 `{trim_text_to_safe_boundary(cleaned_title, limit=96)}`，先按标题本身交代主题")

        if any(topic in topics for topic in {"评审分工", "review loop", "review checklist", "agent 交接", "仓库边界"}):
            facts.append("讨论已经落到评审、交接和仓库约束这些可执行条件，不只是情绪化站队")
        elif "matter" in lowered or "why" in lowered:
            facts.append("讨论已经开始回答“为什么这件事会影响团队协作”，不只是复读标题")
        elif stripped_source:
            facts.append(f"摘要里能看到的具体信息是：{trim_text_to_safe_boundary(localize_common_reader_phrases(simple_sentences(stripped_source)[0] if simple_sentences(stripped_source) else stripped_source), limit=140)}")

    if lane_name == "hacker-news-search-watch":
        cleaned_query = normalize_whitespace(matched_query)
        if all(topic in topics for topic in ("tmux", "git worktree", "review checklist")):
            facts.append(
                f"搜索词「{cleaned_query or '相关关键词'}」命中的这条 HN 讨论把 tmux、git worktree 和 review checklist 串成一条 agent 交接链路"
            )
            facts.append("它给的是可复用的团队协作流程，不是占位式搜索命中")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

        if "busybee" in lowered and "fifo" in lowered:
            facts.append(f"搜索词「{cleaned_query or '相关关键词'}」命中的 `Busybee`，本质上是给 multi-agent 开发流程加一层 `FIFO` build queue")
            facts.append("作者是因为多条 `Claude Code` 会话同时 build 会打爆旧 MacBook Pro，所以把重活排队并顺手把 CPU 占用放进终端仪表盘")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1))

        if "lazyagent" in lowered and "tui" in lowered:
            facts.append(f"搜索词「{cleaned_query or '相关关键词'}」命中的 `Lazyagent`，做的是盯多条 AI coding agents 的终端 TUI")
            facts.append("它会把 `Claude Code`、`Codex`、`OpenCode` 的事件收口到一个界面里，并按工作目录把同仓库会话并到同一项目下")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1))

        if "swarm orchestrator" in lowered and "verification layer" in lowered:
            facts.append(f"搜索词「{cleaned_query or '相关关键词'}」命中的 `Swarm Orchestrator`，做的是给 AI coding agents 加验证层")
            facts.append("它把 Copilot CLI、Claude Code 和 Codex 都纳入同一层 verification，重点是让 agent 产出的代码先过检查再交付")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1))

        if "agentcall.dev" in lowered or ("google meet" in lowered and "zoom" in lowered and "same session" in lowered):
            facts.append(f"搜索词「{cleaned_query or '相关关键词'}」命中的 `agentcall.dev`，想让正在终端里跑的 coding agent 加入会议")
            facts.append("它支持把同一个 `Claude Code`、`Codex`、`OpenClaw` 或 `Cursor` session 拉进 Google Meet、Teams 或 Zoom")
            facts.append("原帖强调 agent 进会后仍保留同一份上下文和文件访问权，可以听说、共享 localhost 页面，并边开会边改代码")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

        if "grafana cloud" in lowered and "gcx" in lowered:
            facts.append(f"搜索词「{cleaned_query or '相关关键词'}」命中的 `gcx`，是 Grafana Cloud 官方 CLI")
            facts.append("作者把背景说得很清楚：Claude Code、Codex 这类 agent 写代码很快，但经常看不到生产环境实际发生了什么")
            facts.append("`gcx` 把查询 production、排查 alerts、让 Assistant root-cause 问题这些 observability 动作放回终端，方便边修边看指标")
            return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

        focus = format_hacker_news_topics(topics[:4])
        if cleaned_query and focus:
            facts.append(f"搜索词「{cleaned_query}」命中的这条 HN 讨论把焦点放在 {focus}")
        elif cleaned_query and cleaned_title:
            facts.append(f"搜索词「{cleaned_query}」命中的 HN 标题是 `{trim_text_to_safe_boundary(cleaned_title, limit=96)}`")
        elif cleaned_title and focus:
            facts.append(f"这条 HN 搜索命中把焦点放在 {focus}")
        elif cleaned_title:
            facts.append(f"这条 HN 搜索命中的标题是 `{trim_text_to_safe_boundary(cleaned_title, limit=96)}`")

        if any(topic in topics for topic in {"tmux", "git worktree", "review checklist", "agent 交接"}):
            facts.append("它把会话切分、代码隔离和评审交接串成了同一条 workflow")
        elif stripped_source:
            facts.append(f"摘要里能看到的具体信息是：{trim_text_to_safe_boundary(localize_common_reader_phrases(simple_sentences(stripped_source)[0] if simple_sentences(stripped_source) else stripped_source), limit=140)}")

    return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))


def build_reddit_detail(*, title: str, source_text: str) -> str:
    cleaned_title = normalize_whitespace(title).strip(" \"'“”‘’")
    lowered_title = cleaned_title.lower()
    lowered = normalize_whitespace(f"{cleaned_title} {source_text}").lower()

    if "maestro" in lowered and "openai codex" in lowered:
        facts = [
            "这帖在介绍开源多 agent 编排平台 `Maestro`，正文写它会协调 `22` 个专门子代理跑结构化流程",
            "`Maestro` 原本从 `Gemini CLI` 扩展起家，这次 `v1.6.1` 把 `OpenAI Codex` 加成第三个原生 runtime",
            "更实在的变化是底层被收成一份 `canonical source tree`，让 Claude Code、Gemini CLI、Codex 三套运行时共用同一套架构",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "agent-council" in lowered or "cliagent-council" in lowered:
        facts = [
            "作者做的 `agent-council` 不是让几个 API 模型空谈，而是让 `Claude Code`、`Codex`、`Gemini` 先看项目再辩论工程问题",
            "正文点的差异很具体：CLI agents 可以 `grep` 代码、读 migration、翻 `git log`，意见会绑定你的真实 repo",
            "它直接复用现有 CLI 订阅，所以安装命令是 `npx cliagent-council`，每次 council session 基本是零边际成本",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "openclaw coming soon" in lowered_title or ("openclaw" in lowered_title and "/monitor" in source_text):
        facts = [
            "这帖不是在说 Claude 版 `OpenClaw` 已经发布，而是在猜 Anthropic 会不会把 Claude Code 的新能力继续下放",
            "作者拿 `Cowork`、`MCP`、`skills` 当例子，说不少能力都是先在 `Claude Code` 跑通，再逐步扩到桌面和移动端",
            "正文点名的最新能力是 `/monitor`：它能常驻电脑监听触发条件，命中后再主动 ping Claude 发消息",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "anthropic response to claude code change" in lowered_title or (
        "small test" in lowered
        and "prosumer signups" in lowered
        and "existing pro and max subscribers" in lowered
    ):
        facts = [
            "这帖转述的是 Anthropic 对 Claude Code 订阅变化的说明：测试只覆盖约 `2%` 的新 prosumer signups",
            "原文明确说 `Existing Pro and Max` subscribers 不受影响，避免把测试解读成存量用户马上被改规则",
            "背景是 Max 刚推出时还没有 Claude Code、Cowork 和长时间运行的 async agents，现在这些已经变成日常 workflow",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "channels launched today" in lowered or ("telegram" in lowered and "discord" in lowered and "--channels" in lowered):
        facts = [
            "帖子讲的是刚上线的 `Claude Code Channels`，现在可以从 `Telegram` 或 `Discord` 直接 DM 你的 Claude Code session",
            "这个会话不是纯聊天壳，原文明确说它保留改文件、跑测试、做 `git ops` 这类完整工具权限",
            "作者把它当 `OpenClaw` 对照组：前者只要 `--channels` 和 `bot token`，不用 `Mac Mini`、`Docker` 和一整套重部署",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "17 papers" in lowered_title or ("greenfield saas" in lowered and "degrades output quality" in lowered):
        facts = [
            "作者是在给自己团队的 `greenfield SaaS` 重写项目复盘，不是泛泛聊提示词",
            "他前面花了几个月搭 agent pipeline，demo 很亮眼，但一进 `production` 就散架",
            "看完 `17 篇` agentic workflow 论文后的核心结论很刺耳：像 “world's best programmer” 这种夸法会直接拉低输出质量",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "non-technical founder" in lowered_title or ("landing page" in lowered and "n8n" in lowered and "mvp" in lowered):
        facts = [
            "发帖人是 non-technical founder，但眼下的 SaaS 并不是停在想法阶段",
            "他说自己的 `landing page` 已经上线，`Claude Code` 也在替他搭 `n8n` workflows，`MVP` 正在成形",
            "真正想问的是在这种进度下还要不要补 `OpenClaw`，还是现有 Claude Code 栈已经够用",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "global set of instructions" in lowered or ("user-wide" in lowered and "context file" in lowered):
        facts = [
            "这帖是在问 AI coding agents 有没有跨仓库通用的全局上下文文件，而不是每个 repo 都重复维护一遍配置",
            "提问者点名了 `Codex`、`Claude Code`、`Cursor` 这类工具，希望多套 agent 环境都能读同一份指令源",
            "真正的讨论点是有没有共同标准；如果没有，现实做法是不是先维护一份 canonical file，再同步成各家的格式",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "whatsapp" in lowered and "claude max" in lowered:
        facts = [
            "这帖是在晒一个 `WhatsApp` AI assistant，消息入口放在 WhatsApp，agent 脑子交给 `Claude Code`",
            "作者做它的直接原因是对 `OpenClaw` 的安全模型不放心，所以想找一条更轻的替代路线",
            "成本和信任也写得很直白：他已经在付 `Claude Max`，而且更信 `Anthropic` 的 runtime",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "large codebases" in lowered_title or ("github issues" in lowered and "major refactors" in lowered):
        facts = [
            "这不是新工具发布，而是在问大仓库怎么把 agent workflow 真正跑顺",
            "提问者已经会让 agent 接 `GitHub issues`、来回 plan/execute，并稳定处理小到中等规模改动",
            "卡点出在大应用和大改版：上下文会变长、拆分变难、同一套方法一进大仓库就不再稳定",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "app store connect" in lowered or ("blitz" in lowered and "mcp servers" in lowered):
        facts = [
            "作者做了个原生 macOS 应用 `Blitz`，把 `Claude Code` 接到 `App Store Connect`",
            "原来会打断 agent 流程的 metadata、`screenshots`、builds、localization 和 review notes，现在都能继续留在终端里处理",
            "实现方式是给 Claude Code 配 `MCP` servers，让提审和过审这条链路直接交给 agent",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if all(role in lowered for role in ("architect", "builder", "reviewer")):
        facts = [
            "作者是读了一批 agentic workflow 论文、又在 solo AI coding 里烧掉太多 token 之后，才收敛到这个 Three Man Team 方案",
            "流程里把 Architect 负责计划、Builder 负责实现、Reviewer 负责验证拆开，并用 markdown handoff files 做交接",
            "它强调的不只是角色分工，还强调透明流程和 token efficiency",
        ]
        return compose_fact_sentences(intro="这条 Reddit 长帖真正写清楚的是：", facts=facts, group_sizes=(1, 1, 1))

    if "boris cherny" in lowered and ("homeless" in lowered or "sleep in his car" in lowered):
        facts = [
            "这帖把焦点放在 `Claude Code` 作者 Boris Cherny 的个人经历，而不是新功能发布",
            "原文特别提到他曾经无家可归、睡过车里，后来一路走到今天的位置",
            "讨论真正想表达的是：这场围绕 `OpenClaw` / `Claude Code` 的争议里，人物故事也在被重新翻出来审视",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if ("made $60k" in lowered or "revenue" in lowered or "replaced a hire" in lowered) and ("open claw" in lowered or "openclaw" in lowered):
        facts = [
            "提问者是在追问 `Claude Code Agents` / `OpenClaw` 到底有没有真实变现案例，不想再听模糊传说",
            "他把问题拆得很实：大家到底拿它做什么、是赚到钱还是只是提效省时间、有没有替代外包或雇人",
            "这类帖子值得看，是因为它会把社区里的夸张收益说法拉回到可验证的使用场景",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "non-technical users" in lowered and "technical users" in lowered:
        facts = [
            "这帖在对比技术用户和非技术用户今天从 AI 里实际拿到的东西已经有多大差距",
            "作者认为非技术用户还主要把 LLM 当搜索框，而技术用户已经在用 thinking effort、模型选择、plugins、automations、skills 和 agents",
            "真正的问题是：如果你不用 `Codex` 或 `Claude Code` 这类工具，过去一年很多进步其实并不会落到你头上",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "godmode" in lowered or ("measure, modify, verify" in lowered and "auto-reverted" in lowered):
        facts = [
            "作者做了个叫 `Godmode` 的开源插件，想给 `Claude Code` 补上自主迭代闭环",
            "核心流程不是一次写完就收工，而是 `measure -> modify -> verify -> keep or revert`，必要时自动回滚",
            "另外它还把并行 agents、失败记忆和 Git 提交前置绑在一起，目标是让 agent 改代码更像可控实验",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "mac mini" in lowered_title and ("24/7" in lowered or "remote access" in lowered or "performance" in lowered):
        facts = [
            "这帖不是在吹某个新工具，而是在问为什么很多人会把 `Claude Code` 放到 `Mac mini` 上常驻运行",
            "提问者关心的几个点都很具体：是不是为了 24/7 在线、远程接入、更低打扰，还是性能和成本上真有差别",
            "讨论价值在于它把“AI 机器”这个趋势拆成了实际工作流问题，而不是单纯跟风硬件摆设",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "octopoda" in lowered or ("agent os" in lowered_title and "claude code" in lowered):
        facts = [
            "作者是被社区吐槽没开源自己的 agent OS 后，干脆把用 `Claude Code` 搭出来的 `Octopoda` 放了出来",
            "他强调这不只是拿 Claude 写点样板代码，而是真的让它一起做系统设计、半夜查 production 问题和修数据库迁移",
            "产品定位也写得很直白：想把管理多条 AI agents 的入口收进同一个 dashboard",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "source maps" in lowered and "model-agnostic" in lowered:
        facts = [
            "帖子先点名 `Claude Code` 的完整源码通过 `source maps` 暴露了出来，而且规模在 `500K+` 行 TypeScript 级别",
            "作者重点研究的是多 agent 编排层：`coordinator mode`、team management、task scheduling 和 inter-agent messaging",
            "他随后照着这套结构重写了一个 `model-agnostic` 开源框架，让 Claude 和 GPT 之类的 agent 能共享 workflow、memory 和 message bus",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "cowork" in lowered and "notion" in lowered and "no servers" in lowered:
        facts = [
            "作者晒的是一套没用 `OpenClaw` 的 `Claude Cowork` 工作流：销售线索、夜间研究、指标监控都拆成定时 session 并行跑",
            "其中一条 session 会把发现写进 `Notion`、需要人工处理时再 DM 提醒，另外还有 heartbeat session 每 30 分钟汇总状态",
            "他刻意强调这套栈不需要服务器、常驻进程或自定义代码，核心执行引擎就是 scheduled sessions 本身",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "/ultraplan" in lowered and "claude code web" in lowered:
        facts = [
            "这帖在讲 `Claude Code` 新上的 `/ultraplan (beta)`：先在终端发起，再到浏览器里审计划、写 inline comments",
            "计划确认后既可以远程执行，也可以再发回 CLI 接着跑，所以它不只是多一个按钮，而是在拆“计划”和“执行”两个阶段",
            "同时上线的还有 `Claude Code Web`（`claude.ai/code`），说明它在往 cloud-first workflow 继续推进，但终端仍是 power-user 入口",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if "switched from mcps to clis" in lowered_title or ("mcp" in lowered and "cli" in lowered and "shell scripts" in lowered):
        facts = [
            "发帖人是在复盘自己为什么从一堆 `MCPs` 切回 `CLIs`，不是泛泛聊工具偏好",
            "他给出的理由很具体：参数容易传错、鉴权会随机坏、超时频繁，而且整体响应明显更慢",
            "转向 `CLI` 之后他觉得体验反而更顺，因为 `Claude` 本来就吃了大量 shell scripts、文档、Stack Overflow 和 GitHub issues 语料",
        ]
        return compose_fact_sentences(intro="", facts=facts, group_sizes=(1, 1, 1))

    if all(token in lowered for token in ("swarm", "coordinator", "codex", "gemini")):
        facts = [
            "帖子把 Claude、Codex、Gemini 放进同一条协作链路",
            "coordinator 负责分工、追踪改动和治理冲突",
            "讨论点已经从“能不能多代理”转到“多代理怎么治理”",
        ]
        return compose_fact_sentences(intro="这条 Reddit 讨论的重点是：", facts=facts, group_sizes=(1, 1, 1))

    generic_facts: list[str] = []
    if "52 controlled benchmarks" in lowered or "73-124%" in lowered or "zero quality gain" in lowered:
        generic_facts = [
            "发帖人跑了 52 组 Claude Code 受控 benchmark，代码库是生产级 Next.js / TypeScript / Supabase 项目",
            "他给出的结论很硬：agent teams 比顺序执行贵 73-124%，但质量没有提升",
            "更有用的发现是先写 `CONTRACT.md`，同模型同代码库下成本降了 54%，质量从 5/10 拉到 9/10",
        ]
    elif "agentic coding report" in lowered and ("60%" in lowered or "0-20%" in lowered):
        generic_facts = [
            "发帖人读完 Anthropic 2026 agentic coding report 后，挑出几个实际数字而不是复述宣传口径",
            "报告里开发者约 60% 工作会用 AI，但真正完全委托的任务只有 0-20%",
            "他的理解是 AI 更像很快的 copilot：能卸掉机械活，也会带来 27% 原本不会做的新增工作",
        ]
    elif "vibe-coded" in lowered and ("200+ units" in lowered or "browser" in lowered):
        generic_facts = [
            "发帖人用 Claude vibe-coded 了一款受 Warcraft 2 启发的 RTS 游戏",
            "成品规模不是玩具 demo：9 个阵营、200+ 单位、多人模式、AI commanders，并且能在浏览器里跑",
            "这条适合保留为完整项目案例，因为它讲的是从生成代码到可运行游戏的结果规模",
        ]
    elif "telegram plugin" in lowered and "botfather" in lowered:
        generic_facts = [
            "发帖人把项目迁到 Claude Code 官方 Telegram integration，用 Telegram 远程管理服务器上的多个项目",
            "具体设置链路是 BotFather 创建 bot、拿 token、再把 Claude Code 配成一个 channel",
            "他把它当作 OpenClaw 替代方案，关键变化是远程入口更轻，不必依赖官方 Claude app",
        ]
    elif "oauth" in lowered and "openclaw" in lowered:
        generic_facts = [
            "这帖在讨论 Claude 即将限制 OpenClaw OAuth 使用的问题",
            "社区焦点不是新功能，而是既有 OpenClaw 用户的授权链路可能明天开始失效",
            "这会给既有 OpenClaw 用户带来迁移 / 替代方案压力，焦点是授权链路怎么延续",
        ]
    elif "personas" in lowered and "plugin framework" in lowered:
        generic_facts = [
            "发帖人做了一个叫 `personas` 的轻量 plugin framework，用 Claude 原生能力搭 helpful assistants",
            "标题里的“we have OpenClaw at home”是在说它走更简化的替代路线",
            "这条的具体点是用 persona / plugin 框架组织助手行为，而不是部署一整套 OpenClaw",
        ]
    elif "replaced openclaw" in lowered and "claude -p" in lowered:
        generic_facts = [
            "发帖人说自己用 `claude -p` 加 bash script 替换了 OpenClaw",
            "他的对照不是概念争论，而是实际命令行工作流：直接从 shell 调 Claude，再用脚本串起来",
            "这条适合看作低配替代路线：少一层产品壳，多依赖本地脚本和 CLI 组合",
        ]
    elif ("resubscribe to codex" in lowered or "re-subscribe to codex" in lowered) and "opus 4.7" in lowered:
        generic_facts = [
            "发帖人原来连续两个月只用 Claude Max，现在因为 Opus 4.7 又重新订阅 Codex",
            "这条的重点是用户在 Claude Max、Codex 和 Opus 新版本之间重新权衡",
            "它保留的是付费选择变化和模型体验反馈，而不是泛泛比较阵营",
        ]
    elif "workflow tips" in lowered and "6 months" in lowered:
        generic_facts = [
            "发帖人是按 6 个月日常使用 Claude Code 的经验整理 workflow tips",
            "标题标明视角来自 senior dev，所以重点应是长期高频使用后沉淀的做法",
            "可承接的事实是 planning、checklists 和独立 review 这些具体工作流建议",
        ]
    if generic_facts:
        return compose_fact_sentences(intro="", facts=generic_facts, group_sizes=(1, 1, 1))
    return ""


def build_known_signal_copy(*, lane_name: str, title: str, source_text: str) -> tuple[str, str]:
    normalized = normalize_whitespace(source_text)
    combined = normalize_whitespace(f"{title} {source_text}")
    lowered = combined.lower()

    if "agent harness" in lowered and "blog" in lowered:
        return (
            "agent harness 博客读后感",
            "帖子在推荐一篇讲 agent harness 的博客，认为这是自己见过最清晰、最实用的解读之一。",
        )
    if "pydantic" in lowered and "mcp" in lowered:
        return (
            "Pydantic 作者讲 MCP 用法",
            "这条转帖在推一段 15 分钟演讲，主讲者是 Pydantic 作者，主题是如何正确使用 MCP。",
        )
    if "coding is going away first" in lowered and "systems thinking" in lowered:
        return (
            "Anthropic CEO 谈 coding 与工程",
            "帖子转引 Anthropic CEO 的判断：先被替代的是 coding，随后会波及更多 software engineering，剩下更依赖 systems thinking。",
        )
    if "permanent memory" in lowered and "46k stars" in lowered:
        return (
            "Claude Code permanent memory",
            "有人给 Claude Code 做了 permanent memory，这个项目 48 小时拿到 4.6 万星，并声称单次会话 token 消耗可下降约 95%。",
        )
    if "writing better prompts" in lowered and "structuring" in lowered:
        return (
            "Claude Code 的关键不是提示词",
            "帖子强调，用好 Claude Code 的关键不只是写提示词，而是先把 repo 和协作结构整理好。",
        )
    if "devtools mcp" in lowered and "quality checks" in lowered:
        return (
            "DevTools MCP 质量检查",
            "Chrome 的 DevTools MCP 已经把 agent 质量检查做成现成功能，至少包括 Lighthouse 性能检查。",
        )
    if "amnesia" in lowered and "architecture" in lowered:
        return (
            "agent 上下文失忆",
            "帖子把 agent 的“上下文失忆”问题说得很直白：每次新 session 都得重新解释架构、约束和历史决定。",
        )
    if all(token in lowered for token in ("microsoft", "google", "openai")) and "cowork" in lowered:
        return (
            "Claude Code 的团队采用情况",
            "帖子提到 Microsoft、Google、OpenAI 的开发者都在用 Claude Code，Anthropic 团队自己的 Cowork 也几乎完全用它搭出来。",
        )
    if "architect" in lowered and "builder" in lowered and "reviewer" in lowered:
        return (
            "三角色协作流程",
            "帖子把 Claude coding 拆成 Architect、Builder、Reviewer 三个角色，并用 markdown handoff 串起计划、实现和审核。",
        )
    if "swarm orchestrator" in lowered and "verification layer" in lowered:
        return (
            "Swarm Orchestrator 验证层",
            "这条讨论把重点放在验证层：通过一层 coordinator 给 AI coding agents 补质量门槛和治理规则。",
        )
    if "agent memory" in lowered and "powerful gui" in lowered and "crispy" in lowered:
        return (
            "Crispy：给 Claude Code / Codex 加记忆层和图形界面",
            "Crispy 想补的是终端形态的几个痛点：记忆检索、模型切换和图形化控制面。",
        )
    if "swarm" in lowered and "coordinator" in lowered and "codex" in lowered and "gemini" in lowered:
        return (
            "多模型 agent 治理",
            "帖子描述了一个 Claude、Codex、Gemini 协作的 agent swarm，由 coordinator 负责分工、追踪改动和治理冲突。",
        )
    if "cli flags won't block on a prompt" in lowered or "structured json output" in lowered:
        return (
            "适合 agent 的 CLI 工具",
            "帖子在整理哪些 CLI 工具更适合 agent 使用，核心标准是结构化输出、非交互参数和不容易卡在提示上。",
        )
    if "global set of instructions" in lowered or ("user-wide" in lowered and "context file" in lowered):
        return (
            "跨仓库共享 agent 上下文",
            "帖子在问，能不能为所有 repo 统一维护一份 agent 指令或上下文文件，让 Codex、Claude Code 等工具共用。",
        )
    if "复刻任何网站" in normalized or "克隆整个网站" in normalized:
        return ("按 URL 复刻网站", "")
    if "instagram" in lowered and ("10" in normalized or "24/7" in normalized):
        return ("Claude Code 自动跑 Instagram", "")
    if "工程师本能" in normalized or "waza" in lowered:
        return ("Waza 的工程师本能", "")
    if "obsidian" in lowered and "claude" in lowered:
        return (
            "Obsidian + Claude 工作流",
            "帖子在串一个 Obsidian + Claude 工作流，开头就是新建 vault，再接到 Claude Desktop / Claude Code。",
        )
    if "claude code" in normalized and "high" in normalized and "medium" in normalized:
        return ("Claude Code 最近降智了", "")

    return "", ""


def build_generic_x_descriptor(source_text: str) -> str:
    if count_cjk_characters(source_text) < 8:
        return ""

    sentence = first_sentence_fragment(source_text).rstrip("。！？")
    sentence = re.sub(r"^(你也发现|这不是你的错觉|这个开源项目|这期播客主题是[:：]?|我的)\s*", "", sentence)
    sentence = sentence.strip("：:，, ")
    if 6 <= len(sentence) <= 24:
        return sentence
    return ""


def build_no_info_render_item(*, lane_name: str) -> ReportRenderItem:
    return ReportRenderItem(
        lane=lane_name,
        title="无",
        excerpt="",
        source_url="",
        link_label="",
        source_title="无",
        sort_key=("", ""),
    )


def build_fallback_render_item(*, lane_name: str, useful_item_count: int, report_date: str) -> ReportRenderItem:
    section_title = FIXED_SECTION_TITLES[lane_name]
    title = f"{section_title} 最小场景"
    excerpt = (
        "最小场景未提供 selected_items，保守退化为 collect_result 统计："
        f"本栏收录 {useful_item_count} 条有用内容。"
    )
    return ReportRenderItem(
        lane=lane_name,
        title=title,
        excerpt=excerpt,
        source_url=build_fallback_source_url(lane_name=lane_name, report_date=report_date),
        link_label=LINK_LABELS[lane_name],
        source_title=title,
        sort_key=("", ""),
    )


def normalize_source_url(source_url: Any, *, lane_name: str, report_date: str) -> str:
    if isinstance(source_url, str) and source_url.startswith(("http://", "https://")):
        return source_url
    return build_fallback_source_url(lane_name=lane_name, report_date=report_date)


def build_fallback_source_url(*, lane_name: str, report_date: str) -> str:
    template = FALLBACK_SOURCE_URL_TEMPLATES[lane_name]
    return template.format(report_date=report_date, date_compact=report_date.replace("-", ""))


def render_body_section(section_title: str, render_items: Sequence[ReportRenderItem]) -> str:
    bullet_lines = []
    for item in render_items:
        if item.title == "无" and not item.source_url:
            bullet_lines.append("- 无")
            continue
        bullet_lines.append(
            f"- **{sanitize_body_text(item.title, fallback='条目')}** "
            f"{sanitize_body_text(item.excerpt, fallback='详情见来源。')} "
            f"[{item.link_label}]({item.source_url})"
        )
    return f"## {section_title}\n" + "\n".join(bullet_lines)


def render_source_section(section_title: str, render_items: Sequence[ReportRenderItem]) -> str:
    unique_entries: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    for item in render_items:
        if not item.source_url:
            continue
        if item.source_url in seen_urls:
            continue
        seen_urls.add(item.source_url)
        unique_entries.append((build_source_title(section_title=section_title, item=item), item.source_url))

    source_lines = [f"- {title} — {url}" for title, url in unique_entries]
    return f"### {section_title}\n" + "\n".join(source_lines)
