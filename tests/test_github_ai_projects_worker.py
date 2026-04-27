from __future__ import annotations

import pytest

from helpers.github_ai_projects_worker import build_github_ai_projects_output
from helpers.lane_contracts import validate_lane_output_artifact
from helpers.lane_workers import build_lane_output


def _lane_input(*, recent_repo_ids: list[str] | None = None) -> dict:
    return {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "signals": [
            {
                "id": "repo:owner/trending-agent",
                "title": "owner/trending-agent",
                "url": "https://github.com/owner/trending-agent",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/owner/trending-agent"],
                "raw": {"summary": "A local-first agent orchestration toolkit with MCP tools."},
            },
            {
                "id": "x:1",
                "title": "@dev 推荐 owner/trending-agent",
                "url": "https://x.com/dev/status/1",
                "source_lane": "x-following",
                "source_urls": ["https://x.com/dev/status/1"],
                "raw": {"summary": "@dev 说 owner/trending-agent 适合多 agent 并行任务。"},
            },
            {
                "id": "hn:1",
                "title": "Show HN: other/new-agent",
                "url": "https://news.ycombinator.com/item?id=1",
                "source_lane": "hacker-news-watch",
                "source_urls": ["https://news.ycombinator.com/item?id=1"],
                "raw": {"source_snippet": "repo: https://github.com/other/new-agent"},
            },
        ],
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub AI 项目",
        "target_item_count": 5,
        "min_item_count": 1,
        "recent_history": {"repo_ids": recent_repo_ids or []},
        "cross_lane_context": {"github_search_queries": []},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": ["采集文本"]},
    }


def test_build_github_ai_projects_output_merges_trending_and_cross_lane_mentions() -> None:
    output = build_github_ai_projects_output(_lane_input())

    validate_lane_output_artifact(output)
    assert output["lane"] == "github-ai-projects"
    assert output["section_title"] == "GitHub AI 项目"
    assert output["quality"]["item_count"] == 2
    assert "owner/trending-agent" in output["markdown"]
    assert "other/new-agent" in output["markdown"]
    assert "多 agent" in output["markdown"] or "agent" in output["markdown"]
    assert len(output["sources"]) >= 2


def test_build_github_ai_projects_output_skips_recent_history_repo_ids() -> None:
    output = build_github_ai_projects_output(_lane_input(recent_repo_ids=["owner/trending-agent"]))

    assert output["quality"]["item_count"] == 1
    assert "owner/trending-agent" not in output["markdown"]
    assert "other/new-agent" in output["markdown"]


def test_build_github_ai_projects_output_includes_memory_markdown() -> None:
    lane_input = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "signals": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "url": "https://github.com/owner/name",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/owner/name"],
                "raw": {"summary": "agent tool"},
            }
        ],
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub AI 项目",
        "target_item_count": 5,
        "min_item_count": 1,
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {"github_search_queries": []},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": ["采集文本"]},
    }

    output = build_github_ai_projects_output(lane_input)

    assert output["side_artifacts"]["memory_markdown"].startswith("# GitHub AI 项目 2026-04-27")
    assert "owner/name" in output["side_artifacts"]["memory_markdown"]


def test_build_lane_output_dispatches_github_ai_projects_to_specialized_worker() -> None:
    output = build_lane_output(
        report_date="2026-04-27",
        lane_name="github-ai-projects",
        selected_items={"selected_items": []},
        lane_input=_lane_input(),
    )

    assert output["lane"] == "github-ai-projects"
    assert output["section_title"] == "GitHub AI 项目"


def test_build_lane_output_requires_lane_input_for_github_ai_projects() -> None:
    with pytest.raises(ValueError, match="requires lane_input"):
        build_lane_output(
            report_date="2026-04-27",
            lane_name="github-ai-projects",
            selected_items={"selected_items": []},
        )
