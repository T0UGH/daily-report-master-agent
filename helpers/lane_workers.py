from __future__ import annotations

from typing import Any

from helpers.github_ai_projects_worker import build_github_ai_projects_output
from helpers.github_trending_worker import build_github_trending_output
from helpers.lane_contracts import validate_lane_output_artifact
from helpers.signals_adapter import FIXED_SECTION_TITLES, build_render_items_by_lane, render_body_section


def _selected_lane_items(selected_items: dict[str, Any], lane_name: str) -> list[dict[str, Any]]:
    lane_items: list[dict[str, Any]] = []
    for item in selected_items.get("selected_items", []):
        if not isinstance(item, dict) or item.get("lane") != lane_name:
            continue
        normalized_item = dict(item)
        summary = normalized_item.get("summary")
        if isinstance(summary, str) and summary.strip():
            normalized_item.setdefault("excerpt", summary)
            normalized_item.setdefault("source_snippet", summary)
        lane_items.append(normalized_item)
    return lane_items


def build_local_lane_output(
    *,
    report_date: str,
    lane_name: str,
    selected_items: dict[str, Any],
) -> dict[str, Any]:
    section_title = FIXED_SECTION_TITLES[lane_name]
    raw_items = _selected_lane_items(selected_items, lane_name)
    collect_result = {
        "report_date": report_date,
        "source": "lane-worker",
        "lanes": [
            {
                "name": lane_name,
                "status": "ok",
                "useful_item_count": len(raw_items),
            }
        ],
        "summary": {"useful_item_count": len(raw_items)},
    }
    selected_payload = {
        "report_date": report_date,
        "selected_items": raw_items,
        "summary": selected_items.get("summary", {}),
    }
    render_items = build_render_items_by_lane(
        collect_result=collect_result,
        selected_items=selected_payload,
        renderable_lanes=[lane_name],
    ).get(lane_name, [])
    render_items = [item for item in render_items if item is not None]
    if render_items:
        body_markdown = render_body_section(section_title, render_items)
        status = "ok"
    else:
        body_markdown = f"## {section_title}\n\n- 无"
        status = "empty"
    contract_items = []
    sources = []
    for item in render_items:
        if not item.source_url:
            continue
        contract_items.append(
            {
                "id": f"{item.lane}:{item.source_url or item.title}",
                "title": item.title,
                "url": item.source_url,
                "summary": item.excerpt,
                "why_today": item.excerpt,
                "source_urls": [item.source_url],
            }
        )
        sources.append({"label": item.source_title or item.title, "url": item.source_url})

    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": report_date,
        "lane": lane_name,
        "status": status,
        "section_title": section_title,
        "markdown": body_markdown,
        "items": contract_items,
        "sources": sources,
        "quality": {
            "item_count": len(render_items),
            "warnings": [] if render_items else ["no_renderable_items"],
        },
        "validation": {"status": "passed" if render_items else "empty", "errors": []},
    }
    validate_lane_output_artifact(output)
    return output


def build_lane_output(
    *,
    report_date: str,
    lane_name: str,
    selected_items: dict[str, Any],
    lane_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if lane_name == "github-ai-projects":
        if lane_input is None:
            raise ValueError("github-ai-projects requires lane_input")
        return build_github_ai_projects_output(lane_input)
    if lane_name == "github-trending-weekly":
        if lane_input is None:
            raise ValueError("github-trending-weekly requires lane_input")
        return build_github_trending_output(lane_input)
    return build_local_lane_output(
        report_date=report_date,
        lane_name=lane_name,
        selected_items=selected_items,
    )
