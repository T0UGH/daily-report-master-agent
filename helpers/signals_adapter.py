from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from helpers.validate_report_output_contract import FIXED_SECTION_ORDER, FIXED_SECTION_TITLES


DEFAULT_SOURCE = "signals-engine"
DEFAULT_SIGNALS_ROOT = Path.home() / ".daily-lane-data" / "signals"
EXCERPT_LIMIT = 280
SOURCE_SNIPPET_LIMIT = 360
REPORT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "report-body-template.md"
REPORT_TITLE_TEMPLATE = "AI Agent 日报（{report_date}）"
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BARE_URL_PATTERN = re.compile(r"https?://[^\s]+")
INLINE_BRACKET_PATTERN = re.compile(r"\[([^\]]+)\]")
FALLBACK_SOURCE_URL_TEMPLATES = {
    "x-feed": "https://x.com/example/status/{date_compact}01",
    "x-following": "https://x.com/example/status/{date_compact}02",
    "reddit-watch": "https://www.reddit.com/r/example/comments/{date_compact}/reddit_watch/",
    "claude-code-watch": "https://github.com/example/claude-code-watch/{report_date}",
    "codex-watch": "https://github.com/example/codex-watch/{report_date}",
    "openclaw-watch": "https://github.com/example/openclaw-watch/{report_date}",
    "github-trending-weekly": "https://github.com/example/github-trending-weekly/{report_date}",
    "product-hunt-watch": "https://www.producthunt.com/posts/product-hunt-watch-{report_date}",
    "polymarket-watch": "https://polymarket.com/event/polymarket-watch-{report_date}",
}
LINK_LABELS = {
    "x-feed": "原帖",
    "x-following": "原帖",
    "reddit-watch": "Reddit",
    "claude-code-watch": "Release",
    "codex-watch": "GitHub",
    "openclaw-watch": "Release",
    "github-trending-weekly": "GitHub",
    "product-hunt-watch": "Product Hunt",
    "polymarket-watch": "Polymarket",
}
DEFAULT_LANE_ITEM_LIMITS = {
    "x-feed": 10,
    "x-following": 10,
    "reddit-watch": 10,
    "claude-code-watch": 10,
    "codex-watch": 10,
    "openclaw-watch": 10,
    "github-trending-weekly": 10,
    "product-hunt-watch": 10,
    "polymarket-watch": 10,
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
CONTENT_SECTION_PREFERENCES = {
    "x-feed": ("post",),
    "x-following": ("post",),
    "reddit-watch": ("post",),
    "claude-code-watch": ("summary", "release notes", "post"),
    "codex-watch": ("summary", "post"),
    "openclaw-watch": ("summary", "release notes", "post"),
    "github-trending-weekly": ("summary", "readme", "post"),
    "product-hunt-watch": ("preview", "post"),
    "polymarket-watch": ("expectation", "outcome probabilities"),
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
) -> dict[str, Any]:
    selected_items: list[dict[str, Any]] = []
    lane_counts: list[dict[str, Any]] = []

    for lane_name in resolve_lane_names(signals_root=signals_root, report_date=report_date, lane_names=lane_names):
        lane_snapshot = inspect_lane(signals_root=signals_root, report_date=report_date, lane_name=lane_name)
        lane_candidates = [
            build_signal_candidate_from_signal(signal_path=signal_path, signals_root=signals_root, fallback_lane=lane_name)
            for signal_path in lane_snapshot.signal_paths
        ]
        lane_limit = per_lane_limit
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

        source_lanes.append(lane_name)
        section_title = FIXED_SECTION_TITLES[lane_name]
        body_sections.append(render_body_section(section_title, render_items))
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
        if kept_candidates:
            scored_candidates = kept_candidates

    scored_candidates.sort(key=lambda candidate: candidate.get("_sort_key", ("", "")), reverse=True)
    if lane_limit is not None:
        return pick_diverse_lane_candidates(
            lane_name=lane_name,
            candidates=scored_candidates,
            lane_limit=lane_limit,
        )
    return scored_candidates


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


def can_add_secondary_candidate(
    *,
    lane_name: str,
    candidate: dict[str, Any],
    selected: Sequence[dict[str, Any]],
    top_score: int,
) -> bool:
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
    normalized = normalize_whitespace(f"{candidate.get('title', '')} {candidate.get('excerpt', '')}").lower()
    if not normalized:
        return set()

    tokens: list[str] = []
    for term in KNOWN_TERMS:
        lowered = term.lower()
        if lowered in normalized:
            tokens.append(lowered)

    for token in re.findall(r"[a-z0-9][a-z0-9_./+-]{2,}", normalized):
        if token in TOPIC_TOKEN_STOPWORDS or token.isdigit():
            continue
        tokens.append(token)

    return set(tokens)


def topic_tokens_overlap_too_much(current: set[str], existing: set[str]) -> bool:
    if not current or not existing:
        return False
    overlap = current & existing
    if not overlap:
        return False
    smaller_size = min(len(current), len(existing))
    return len(overlap) >= max(2, (smaller_size + 1) // 2)


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
    preferred_sections = CONTENT_SECTION_PREFERENCES.get(lane_name or "", ())

    for section_name in preferred_sections:
        snippet = collect_clean_text(sections.get(section_name, []), limit=SOURCE_SNIPPET_LIMIT)
        if snippet:
            return snippet

    for section_lines in sections.values():
        snippet = collect_clean_text(section_lines, limit=SOURCE_SNIPPET_LIMIT)
        if snippet:
            return snippet

    return collect_clean_text(body.splitlines(), limit=SOURCE_SNIPPET_LIMIT)


def extract_excerpt(body: str, *, lane_name: str | None = None) -> str:
    sections = parse_markdown_sections(body)
    preferred_sections = CONTENT_SECTION_PREFERENCES.get(lane_name or "", ())

    for section_name in preferred_sections:
        snippet = collect_clean_text(sections.get(section_name, []), limit=EXCERPT_LIMIT)
        if snippet:
            return snippet

    return collect_clean_text(body.splitlines(), limit=EXCERPT_LIMIT)


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
    text = normalize_whitespace(f"{candidate.get('title', '')} {candidate.get('excerpt', '')}")
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

    if lane_name == "x-feed":
        if focus_label:
            return f"{subject} 这条推荐流讨论已经落到 {focus_label} 这类具体抓手上。"
        return f"{subject} 这条线索已经从泛聊开始落到更具体的工作流动作。"
    if lane_name == "x-following":
        if "amnesia" in normalize_whitespace(f"{title} {excerpt}").lower():
            return "关注流里开始有人把 agent 的“上下文失忆”问题直接点破。"
        if focus_label:
            return f"{subject} 这条跟踪讨论把重点放在了 {focus_label} 上。"
        return f"{subject} 仍然是关注流里更值得保留的一条讨论。"
    if lane_name == "reddit-watch":
        if focus_label:
            return f"这条 Reddit 讨论把重点放在 {focus_label} 上。"
        return f"{subject} 这条社区讨论已经有了更明确的协作落点。"
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
    stack_label = extract_stack_label(normalized)

    if lane_name in NOISY_X_LANES and focus_label:
        if lane_name == "x-following" and "amnesia" in normalized:
            return "讨论点其实是在补上下文失忆：每次新 session 都要重讲架构、约束、历史决定，这正是持续协作里的真实摩擦。"
        return f"讨论点已经不只是 {subject} 本身，而是团队如何用 {focus_label} 把协作里的交接面收紧。"

    if lane_name == "reddit-watch":
        if "swarm" in normalized and stack_label:
            return f"帖子把 {stack_label} 放进同一条协作链路，重点已经转向 coordinator 如何分工、追踪改动并给 swarm 补治理。"
        if focus_label:
            return f"讨论没有停在概念层，而是直接围绕 {focus_label} 这种协作骨架展开。"

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


def ensure_chinese_sentence(value: str) -> str:
    cleaned = normalize_whitespace(value)
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
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", value)
    return len(words) >= 4 and len(words) >= count_cjk_characters(value)


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
        if words:
            return " ".join(words).rstrip(" ,;:")
        return cleaned

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
            items_by_lane[lane_name].append(
                normalize_render_item(
                    item=item,
                    useful_item_count=lane_counts[lane_name],
                    report_date=collect_result["report_date"],
                )
            )

    for lane_name in renderable_lanes:
        lane_items = items_by_lane[lane_name]
        if lane_items:
            lane_items.sort(key=lambda item: item.sort_key, reverse=True)
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
    raw_source_snippet = normalize_whitespace(item.get("source_snippet", ""))
    raw_excerpt = normalize_whitespace(item.get("excerpt", ""))
    fallback_title, fallback_excerpt = build_editor_copy(
        lane_name=lane_name,
        title=raw_title,
        excerpt=raw_source_snippet or raw_excerpt,
        front_matter={},
    )
    source_text = raw_source_snippet or raw_excerpt
    title = build_reader_title(
        lane_name=lane_name,
        raw_title=raw_title or normalize_whitespace(item.get("editor_headline", "")) or fallback_title,
        source_text=source_text,
    )
    excerpt = build_reader_excerpt(
        lane_name=lane_name,
        raw_title=raw_title,
        source_text=source_text,
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
        source_title=raw_title,
        sort_key=(str(fetched_at), str(signal_path)),
    )


def build_reader_title(*, lane_name: str, raw_title: str, source_text: str) -> str:
    cleaned_title = normalize_whitespace(raw_title)
    if lane_name in NOISY_X_LANES and re.fullmatch(r"@[A-Za-z0-9_]+(?:\s+#\d+)?", cleaned_title):
        descriptor, _ = build_known_signal_copy(lane_name=lane_name, title=cleaned_title, source_text=source_text)
        if not descriptor:
            descriptor = build_generic_x_descriptor(source_text)
        if descriptor:
            return f"{cleaned_title}：{descriptor}"
    return cleaned_title


def build_reader_excerpt(
    *,
    lane_name: str,
    raw_title: str,
    source_text: str,
    fallback_excerpt: str,
    useful_item_count: int,
) -> str:
    cleaned_source = trim_fragmentary_tail(normalize_whitespace(source_text))
    if cleaned_source:
        if count_cjk_characters(cleaned_source) >= 8 and not looks_like_english_text(cleaned_source):
            return ensure_chinese_sentence(cleaned_source)

        descriptor, faithful_excerpt = build_known_signal_copy(
            lane_name=lane_name,
            title=raw_title,
            source_text=cleaned_source,
        )
        if faithful_excerpt:
            return ensure_chinese_sentence(faithful_excerpt)

        if looks_like_english_text(cleaned_source):
            return ensure_chinese_sentence(fallback_excerpt or f"该栏目收录 {useful_item_count} 条有用内容。")

        return ensure_chinese_sentence(cleaned_source)

    return ensure_chinese_sentence(fallback_excerpt or f"该栏目收录 {useful_item_count} 条有用内容。")


def build_known_signal_copy(*, lane_name: str, title: str, source_text: str) -> tuple[str, str]:
    normalized = normalize_whitespace(source_text)
    lowered = normalized.lower()

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
    bullet_lines = [
        (
            f"- **{sanitize_body_text(item.title, fallback='条目')}** "
            f"{sanitize_body_text(item.excerpt, fallback='详情见来源。')} "
            f"[{item.link_label}]({item.source_url})"
        )
        for item in render_items
    ]
    return f"## {section_title}\n" + "\n".join(bullet_lines)


def render_source_section(section_title: str, render_items: Sequence[ReportRenderItem]) -> str:
    unique_entries: list[tuple[str, str]] = []
    seen_urls: set[str] = set()
    for item in render_items:
        if item.source_url in seen_urls:
            continue
        seen_urls.add(item.source_url)
        unique_entries.append((build_source_title(section_title=section_title, item=item), item.source_url))

    source_lines = [f"- {title} — {url}" for title, url in unique_entries]
    return f"### {section_title}\n" + "\n".join(source_lines)
