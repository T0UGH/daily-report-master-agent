from __future__ import annotations

from helpers.lane_report_assembler import build_report_artifact_from_lane_outputs


def test_build_report_artifact_from_lane_outputs_preserves_order_and_sources() -> None:
    lane_outputs = [
        {
            "artifact_type": "lane_output",
            "schema_version": 1,
            "report_date": "2026-04-27",
            "lane": "weather-watch",
            "status": "ok",
            "section_title": "天气预报",
            "markdown": "## 天气预报\n\n- 北京：晴。",
            "items": [
                {
                    "id": "weather:beijing",
                    "title": "北京",
                    "url": "https://weather.example",
                    "summary": "晴",
                    "why_today": "天气置顶",
                    "source_urls": ["https://weather.example"],
                }
            ],
            "sources": [{"label": "北京天气", "url": "https://weather.example"}],
            "quality": {"item_count": 1, "warnings": []},
            "validation": {"status": "passed", "errors": []},
        },
        {
            "artifact_type": "lane_output",
            "schema_version": 1,
            "report_date": "2026-04-27",
            "lane": "github-ai-projects",
            "status": "ok",
            "section_title": "GitHub AI 项目",
            "markdown": "## GitHub AI 项目\n\n- owner/name：agent workflow 工具。",
            "items": [
                {
                    "id": "repo:owner/name",
                    "title": "owner/name",
                    "url": "https://github.com/owner/name",
                    "summary": "agent workflow 工具",
                    "why_today": "trending",
                    "source_urls": ["https://github.com/owner/name"],
                }
            ],
            "sources": [{"label": "owner/name", "url": "https://github.com/owner/name"}],
            "quality": {"item_count": 1, "warnings": []},
            "validation": {"status": "passed", "errors": []},
        },
    ]

    artifact = build_report_artifact_from_lane_outputs(
        report_date="2026-04-27",
        lane_outputs=lane_outputs,
        lane_order=["weather-watch", "github-ai-projects"],
    )

    markdown = artifact["body_markdown"]
    assert markdown.index("## 天气预报") < markdown.index("## GitHub AI 项目")
    assert "## 来源" in markdown
    assert "https://github.com/owner/name" in markdown
    assert artifact["source_lanes"] == ["weather-watch", "github-ai-projects"]
