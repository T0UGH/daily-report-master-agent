from __future__ import annotations

from helpers.lane_contracts import validate_lane_output_artifact
from helpers.lane_workers import build_local_lane_output


def test_build_local_lane_output_wraps_existing_render_items() -> None:
    selected_items = {
        "report_date": "2026-04-27",
        "selected_items": [
            {
                "id": "github-trending-weekly:1",
                "lane": "github-trending-weekly",
                "title": "owner/project",
                "summary": "一个 agent workflow 工具，支持本地任务编排。",
                "source_url": "https://github.com/owner/project",
                "url": "https://github.com/owner/project",
            }
        ],
        "summary": {"selected_item_count": 1, "lane_counts": []},
    }

    output = build_local_lane_output(
        report_date="2026-04-27",
        lane_name="github-trending-weekly",
        selected_items=selected_items,
    )

    validate_lane_output_artifact(output)
    assert output["lane"] == "github-trending-weekly"
    assert output["status"] == "ok"
    assert output["section_title"] == "GitHub 趋势项目"
    assert "owner/project" in output["markdown"]
    assert output["quality"]["item_count"] == 1
