from __future__ import annotations

import pytest

from helpers.lane_agent_contracts import (
    is_agent_first_lane_input,
    validate_agent_lane_input,
    validate_agent_lane_output,
)


def test_validate_agent_lane_input_requires_raw_candidates() -> None:
    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "agent_first": True,
        "raw_candidates": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "source_url": "https://github.com/owner/name",
                "source_snippet": "Agent framework for coding workflows.",
                "candidate_source": "signals/github-trending-weekly",
            }
        ],
        "style_contract": {"language": "zh-CN"},
    }

    validate_agent_lane_input(payload)


def test_is_agent_first_lane_input_only_matches_explicit_agent_first_inputs() -> None:
    assert is_agent_first_lane_input({"artifact_type": "lane_input", "agent_first": True}) is True
    assert is_agent_first_lane_input({"artifact_type": "lane_input", "agent_first": False}) is False
    assert is_agent_first_lane_input({"artifact_type": "lane_output", "agent_first": True}) is False


def test_validate_agent_lane_input_rejects_missing_raw_candidates() -> None:
    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "agent_first": True,
        "style_contract": {"language": "zh-CN"},
    }

    with pytest.raises(ValueError, match="raw_candidates"):
        validate_agent_lane_input(payload)


def test_validate_agent_lane_output_requires_selected_rejected_reasoning_and_runtime() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "status": "ok",
        "section_title": "GitHub Trending",
        "markdown": "## GitHub Trending\n\n- owner/name matters today.",
        "items": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "url": "https://github.com/owner/name",
                "summary": "Agent framework for coding workflows.",
                "source_urls": ["https://github.com/owner/name"],
            }
        ],
        "selected_items": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "why_selected": "AI agent workflow",
                "sources": ["https://github.com/owner/name"],
            }
        ],
        "rejected_items": [
            {
                "id": "repo:other/tool",
                "title": "other/tool",
                "reason": "Generic developer tool, not AI or coding-agent focused.",
            }
        ],
        "reasoning_notes": ["selected 1 of 2 raw candidates"],
        "sources": [{"label": "owner/name", "url": "https://github.com/owner/name"}],
        "agent_runtime": {
            "kind": "specialized_agent",
            "implementation": "github_trending_agent",
        },
        "quality": {"item_count": 1, "rejected_count": 1},
    }

    validate_agent_lane_output(payload)


def test_validate_agent_lane_output_rejects_unknown_status() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "status": "maybe",
        "section_title": "GitHub Trending",
        "markdown": "## GitHub Trending\n\n- item",
        "items": [],
        "selected_items": [],
        "rejected_items": [],
        "reasoning_notes": [],
        "sources": [],
        "agent_runtime": {"kind": "specialized_agent", "implementation": "github_trending_agent"},
        "quality": {"item_count": 0},
    }

    with pytest.raises(ValueError, match="status"):
        validate_agent_lane_output(payload)


def test_validate_agent_lane_output_rejects_ok_without_markdown() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "status": "ok",
        "section_title": "GitHub Trending",
        "markdown": "",
        "items": [],
        "selected_items": [],
        "rejected_items": [],
        "reasoning_notes": ["no markdown produced"],
        "sources": [],
        "agent_runtime": {"kind": "specialized_agent", "implementation": "github_trending_agent"},
        "quality": {"item_count": 0},
    }

    with pytest.raises(ValueError, match="ok.*markdown"):
        validate_agent_lane_output(payload)


def test_validate_agent_lane_output_allows_blocked_with_reason_and_empty_markdown() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "status": "blocked",
        "section_title": "GitHub Trending",
        "markdown": "",
        "items": [],
        "selected_items": [],
        "rejected_items": [],
        "reasoning_notes": ["error: raw corpus missing"],
        "sources": [],
        "agent_runtime": {"kind": "specialized_agent", "implementation": "github_trending_agent"},
        "quality": {"item_count": 0, "error": "raw corpus missing"},
    }

    validate_agent_lane_output(payload)
