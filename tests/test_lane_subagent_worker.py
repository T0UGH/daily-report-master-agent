from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from helpers import lane_subagent_worker as worker
from helpers.lane_agent_contracts import validate_agent_lane_output
from helpers.lane_contracts import validate_lane_output_artifact


def _github_trending_agent_input() -> dict:
    return {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub 趋势项目",
        "agent_first": True,
        "target_item_count": 2,
        "raw_corpus_status": "ok",
        "raw_candidates": [
            {
                "id": "repo:codex-labs/agent-skills",
                "title": "codex-labs/agent-skills",
                "source_url": "https://github.com/codex-labs/agent-skills",
                "source_snippet": (
                    "codex-labs/agent-skills is a catalog of Claude Code and Codex agent skills. "
                    "It ships MCP workflow examples and provider setup docs."
                ),
                "candidate_source": "agent-skills.md",
            }
        ],
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": []},
    }


def test_agent_first_worker_dispatches_registry_not_legacy_lane_workers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_legacy(*_args: object, **_kwargs: object) -> dict:
        raise AssertionError("legacy lane worker must not be used for agent-first inputs")

    monkeypatch.setattr(worker, "build_lane_output", forbidden_legacy)

    output = worker.build_output_from_input(_github_trending_agent_input())

    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    assert output["agent_runtime"]["kind"] == "specialized_agent"
    assert output["agent_runtime"]["implementation"] == "github_trending_agent"


def test_agent_first_worker_writes_blocked_output_when_agent_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    input_path.write_text(json.dumps(_github_trending_agent_input(), ensure_ascii=False), encoding="utf-8")

    def boom(_lane_input: dict) -> dict:
        raise RuntimeError("agent exploded")

    monkeypatch.setattr(worker, "build_agent_lane_output", boom, raising=False)
    monkeypatch.setattr(worker, "parse_args", lambda: argparse.Namespace(input=input_path, output=output_path))

    assert worker.main() == 0

    output = json.loads(output_path.read_text(encoding="utf-8"))
    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    assert output["status"] == "blocked"
    assert output["quality"]["reason"] == "agent_first_lane_failed"
    assert "agent exploded" in output["quality"]["error"]
