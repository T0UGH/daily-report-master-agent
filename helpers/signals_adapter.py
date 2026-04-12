from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from helpers.validate_report_output_contract import FIXED_SECTION_ORDER, FIXED_SECTION_TITLES


DEFAULT_SOURCE = "signals-engine"
DEFAULT_SIGNALS_ROOT = Path.home() / ".daily-lane-data" / "signals"
EXCERPT_LIMIT = 280
REPORT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "report-body-template.md"
REPORT_TITLE_TEMPLATE = "AI Agent 日报（{report_date}）"
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
BARE_URL_PATTERN = re.compile(r"https?://[^\s]+")
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
        lane_items = [
            build_selected_item_from_signal(signal_path=signal_path, signals_root=signals_root, fallback_lane=lane_name)
            for signal_path in lane_snapshot.signal_paths
        ]
        lane_items.sort(
            key=lambda item: (
                item.get("fetched_at", ""),
                item.get("signal_path", ""),
            ),
            reverse=True,
        )
        if per_lane_limit is not None:
            lane_items = lane_items[:per_lane_limit]

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


def build_selected_item_from_signal(signal_path: Path, signals_root: Path, fallback_lane: str) -> dict[str, Any]:
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
        "excerpt": extract_excerpt(body),
    }

    source = as_string(front_matter.get("source"))
    if source:
        item["source"] = source
    signal_type = as_string(front_matter.get("type"))
    if signal_type:
        item["signal_type"] = signal_type

    return item


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
    for raw_line in front_matter_block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if raw_line.startswith((" ", "\t")):
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
    return parsed


def extract_excerpt(body: str) -> str:
    chunks: list[str] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        chunks.append(line)
        candidate = normalize_whitespace(" ".join(chunks))
        if len(candidate) >= EXCERPT_LIMIT:
            return candidate[:EXCERPT_LIMIT].rstrip()

    return normalize_whitespace(" ".join(chunks))


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


def sanitize_body_text(value: str, *, fallback: str) -> str:
    cleaned = MARKDOWN_LINK_PATTERN.sub(r"\1", value)
    cleaned = BARE_URL_PATTERN.sub("", cleaned)
    cleaned = normalize_whitespace(cleaned)
    cleaned = re.sub(r"\s+([,.;:!?，。！？；：])", r"\1", cleaned)
    return cleaned or fallback


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
    title = normalize_whitespace(item.get("title", "")) or f"{FIXED_SECTION_TITLES[lane_name]} 条目"
    excerpt = normalize_whitespace(item.get("excerpt", ""))
    if not excerpt:
        excerpt = f"该栏目收录 {useful_item_count} 条有用内容。"

    source_url = normalize_source_url(item.get("source_url"), lane_name=lane_name, report_date=report_date)
    fetched_at = item.get("fetched_at", "")
    signal_path = item.get("signal_path", "")
    return ReportRenderItem(
        lane=lane_name,
        title=title,
        excerpt=excerpt,
        source_url=source_url,
        link_label=LINK_LABELS[lane_name],
        source_title=title,
        sort_key=(str(fetched_at), str(signal_path)),
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
    bullet_lines = [
        (
            f"- **{sanitize_body_text(item.title, fallback='条目')}**："
            f"{sanitize_body_text(item.excerpt, fallback='详情见来源。')} "
            f"[{item.link_label}]({item.source_url})"
        )
        for item in render_items
    ]
    return f"## {section_title}\n" + "\n".join(bullet_lines)


def render_source_section(section_title: str, render_items: Sequence[ReportRenderItem]) -> str:
    unique_urls: list[str] = []
    seen_urls: set[str] = set()
    for item in render_items:
        if item.source_url in seen_urls:
            continue
        seen_urls.add(item.source_url)
        unique_urls.append(item.source_url)

    source_lines = [f"- 来源 {index}：{url}" for index, url in enumerate(unique_urls, start=1)]
    return f"### {section_title}\n" + "\n".join(source_lines)
