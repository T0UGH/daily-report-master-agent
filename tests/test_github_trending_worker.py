from __future__ import annotations

import pytest

from helpers.github_trending_worker import build_github_trending_output
from helpers.lane_contracts import validate_lane_output_artifact
from helpers.lane_workers import build_lane_output


BANNED_GENERIC_PHRASES = [
    "值得看的趋势项目",
    "具体变化见来源",
    "当前可作为",
    "候选继续观察",
    "至少因为",
]


def _lane_input() -> dict:
    return {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub 趋势项目",
        "target_item_count": 5,
        "min_item_count": 1,
        "signals": [
            {
                "id": "repo:codex-labs/agent-skills",
                "title": "codex-labs/agent-skills",
                "url": "https://github.com/codex-labs/agent-skills",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/codex-labs/agent-skills"],
                "raw": {
                    "summary": "值得看的趋势项目，具体变化见来源。",
                    "source_snippet": (
                        "codex-labs/agent-skills is a catalog of Claude Code and Codex agent skills. "
                        "It ships 42 reusable skills, includes MCP workflow examples, "
                        "and documents OpenAI plus Anthropic provider setup."
                    ),
                    "source_url": "https://github.com/codex-labs/agent-skills",
                    "stars": 240,
                },
            },
            {
                "id": "repo:procureco/vendor-portal",
                "title": "procureco/vendor-portal",
                "url": "https://github.com/procureco/vendor-portal",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/procureco/vendor-portal"],
                "raw": {
                    "source_snippet": (
                        "procureco/vendor-portal is an enterprise procurement portal. "
                        "It manages purchase orders, supplier onboarding, and invoice approvals."
                    ),
                    "source_url": "https://github.com/procureco/vendor-portal",
                    "stars": 1000,
                },
            },
            {
                "id": "repo:deepwiki-labs/context-engine",
                "title": "deepwiki-labs/context-engine",
                "url": "https://github.com/deepwiki-labs/context-engine",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/deepwiki-labs/context-engine"],
                "raw": {
                    "excerpt": (
                        "DeepWiki context-engine indexes repositories for AI-assisted coding. "
                        "The README highlights LLM retrieval, workflow traces, and editor handoff."
                    ),
                    "source_url": "https://github.com/deepwiki-labs/context-engine",
                    "stars": 360,
                },
            },
        ],
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": []},
    }


def test_build_github_trending_output_uses_source_snippet_not_template_summary() -> None:
    output = build_github_trending_output(_lane_input())

    validate_lane_output_artifact(output)
    assert output["lane"] == "github-trending-weekly"
    assert output["section_title"] == "GitHub 趋势项目"
    assert "codex-labs/agent-skills" in output["markdown"]
    assert "42 reusable skills" in output["markdown"]
    assert "MCP workflow examples" in output["markdown"]
    assert "OpenAI plus Anthropic provider setup" in output["markdown"]
    assert "值得看的趋势项目" not in output["markdown"]
    assert output["items"][0]["summary"].find("42 reusable skills") != -1


def test_build_github_trending_output_filters_generic_non_ai_repos() -> None:
    output = build_github_trending_output(_lane_input())

    assert "procureco/vendor-portal" not in output["markdown"]
    assert [item["title"] for item in output["items"]] == [
        "codex-labs/agent-skills",
        "deepwiki-labs/context-engine",
    ]
    assert output["quality"]["item_count"] == 2


def test_build_github_trending_output_avoids_banned_generic_phrases() -> None:
    output = build_github_trending_output(_lane_input())

    combined = output["markdown"] + "\n" + "\n".join(
        item["summary"] + "\n" + item["why_today"] for item in output["items"]
    )
    assert all(phrase not in combined for phrase in BANNED_GENERIC_PHRASES)


def test_build_github_trending_output_requires_matching_lane() -> None:
    lane_input = _lane_input()
    lane_input["lane"] = "github-ai-projects"

    with pytest.raises(ValueError, match="github-trending-weekly"):
        build_github_trending_output(lane_input)


def test_build_lane_output_dispatches_github_trending_to_specialized_worker() -> None:
    output = build_lane_output(
        report_date="2026-04-27",
        lane_name="github-trending-weekly",
        selected_items={
            "report_date": "2026-04-27",
            "selected_items": [
                {
                    "id": "repo:codex-labs/agent-skills",
                    "lane": "github-trending-weekly",
                    "title": "codex-labs/agent-skills",
                    "summary": "当前可作为候选继续观察，具体变化见来源。",
                    "source_url": "https://github.com/codex-labs/agent-skills",
                }
            ],
            "summary": {"selected_item_count": 1},
        },
        lane_input=_lane_input(),
    )

    assert "42 reusable skills" in output["markdown"]
    assert "当前可作为" not in output["markdown"]


def test_build_github_trending_output_filters_repos_below_100_stars() -> None:
    lane_input = _lane_input()
    lane_input["signals"] = [
        {
            "id": "repo:tiny/agent-memory",
            "title": "tiny/agent-memory",
            "url": "https://github.com/tiny/agent-memory",
            "source_lane": "github-trending-weekly",
            "source_urls": ["https://github.com/tiny/agent-memory"],
            "raw": {
                "source_snippet": "tiny/agent-memory is an MCP memory server for Claude Code agents.",
                "source_url": "https://github.com/tiny/agent-memory",
                "stars": 99,
            },
        },
        {
            "id": "repo:solid/agent-memory",
            "title": "solid/agent-memory",
            "url": "https://github.com/solid/agent-memory",
            "source_lane": "github-trending-weekly",
            "source_urls": ["https://github.com/solid/agent-memory"],
            "raw": {
                "source_snippet": "solid/agent-memory is an MCP memory server for Claude Code agents.",
                "source_url": "https://github.com/solid/agent-memory",
                "stars": 100,
            },
        },
    ]

    output = build_github_trending_output(lane_input)

    assert output["quality"]["item_count"] == 1
    assert "tiny/agent-memory" not in output["markdown"]
    assert "solid/agent-memory" in output["markdown"]
    assert output["items"][0]["stars"] == 100


def test_build_lane_output_requires_lane_input_for_github_trending() -> None:
    with pytest.raises(ValueError, match="github-trending-weekly requires lane_input"):
        build_lane_output(
            report_date="2026-04-27",
            lane_name="github-trending-weekly",
            selected_items={"selected_items": []},
        )
