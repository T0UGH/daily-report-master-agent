from __future__ import annotations

from typing import Any

from helpers.lane_contracts import validate_lane_output_artifact
from helpers.signals_adapter import REPORT_TEMPLATE_PATH, REPORT_TITLE_TEMPLATE


def _source_markdown(section_title: str, sources: list[dict[str, Any]]) -> str:
    lines = [f"### {section_title}"]
    for source in sources:
        label = source.get("label") or source.get("url")
        url = source.get("url")
        if url:
            lines.append(f"- {label} — {url}")
    return "\n".join(lines)


def build_report_artifact_from_lane_outputs(
    *,
    report_date: str,
    lane_outputs: list[dict[str, Any]],
    lane_order: list[str],
) -> dict[str, Any]:
    by_lane = {}
    for output in lane_outputs:
        validate_lane_output_artifact(output)
        by_lane[output["lane"]] = output

    body_sections: list[str] = []
    source_sections: list[str] = []
    source_lanes: list[str] = []
    useful_item_count = 0

    for lane in lane_order:
        output = by_lane.get(lane)
        if not output or output.get("status") in {"empty", "blocked"}:
            continue
        body_sections.append(output["markdown"])
        item_count = output.get("quality", {}).get("item_count", 0)
        useful_item_count += item_count if isinstance(item_count, int) else len(output.get("items", []))
        sources = output.get("sources") or []
        if sources:
            source_lanes.append(lane)
            source_sections.append(_source_markdown(output["section_title"], sources))

    if not body_sections:
        raise ValueError("没有可渲染的 lane output")

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
        "lane_output_count": len(by_lane),
    }
