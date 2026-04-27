from __future__ import annotations

import pytest

from helpers.lane_contracts import (
    LaneContractError,
    validate_lane_input_artifact,
    validate_lane_output_artifact,
)


def test_validate_lane_input_artifact_accepts_minimal_valid_payload() -> None:
    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub AI 项目",
        "target_item_count": 5,
        "min_item_count": 1,
        "signals": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "url": "https://github.com/owner/name",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/trending"],
                "raw": {"stars": 1234},
            }
        ],
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": ["采集文本"]},
    }

    validate_lane_input_artifact(payload)


def test_validate_lane_output_artifact_accepts_reader_section_and_sources() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "status": "ok",
        "section_title": "GitHub AI 项目",
        "markdown": "## GitHub AI 项目\n\n- owner/name 做了一个 agent 调度工具。 https://github.com/owner/name",
        "items": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "url": "https://github.com/owner/name",
                "summary": "做 agent 调度。",
                "why_today": "进入 trending 且被 X 提到。",
                "source_urls": ["https://github.com/owner/name"],
            }
        ],
        "sources": [{"label": "owner/name", "url": "https://github.com/owner/name"}],
        "quality": {"item_count": 1, "warnings": []},
        "validation": {"status": "passed", "errors": []},
    }

    validate_lane_output_artifact(payload)


def test_validate_lane_output_artifact_rejects_freeform_missing_schema() -> None:
    with pytest.raises(LaneContractError, match="schema_version"):
        validate_lane_output_artifact({"lane": "github-ai-projects", "markdown": "hello"})


def test_validate_lane_output_artifact_rejects_unknown_status() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "status": "maybe",
        "section_title": "GitHub AI 项目",
        "markdown": "## GitHub AI 项目\n\n- item",
        "items": [],
        "sources": [],
        "quality": {"item_count": 0, "warnings": []},
        "validation": {"status": "failed", "errors": []},
    }
    with pytest.raises(LaneContractError, match="status"):
        validate_lane_output_artifact(payload)
