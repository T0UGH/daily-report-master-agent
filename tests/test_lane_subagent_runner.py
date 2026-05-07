from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from helpers.lane_contracts import validate_lane_output_artifact
from helpers.lane_subagent_runner import run_lane_subagent


def _github_trending_lane_input() -> dict:
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
                    "source_snippet": (
                        "codex-labs/agent-skills is a catalog of Claude Code and Codex agent skills. "
                        "It ships 42 reusable skills, includes MCP workflow examples, "
                        "and documents OpenAI plus Anthropic provider setup."
                    ),
                    "source_url": "https://github.com/codex-labs/agent-skills",
                    "stars": 240,
                },
            }
        ],
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": []},
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_run_lane_subagent_invokes_cli_process_and_logs_command_stdout(tmp_path: Path) -> None:
    input_path = tmp_path / "lane_input.json"
    output_path = tmp_path / "lane_output.json"
    log_path = tmp_path / "lane_log.md"
    _write_json(input_path, _github_trending_lane_input())

    output = run_lane_subagent(input_path, output_path, log_path, timeout_seconds=10)

    validate_lane_output_artifact(output)
    assert output_path.is_file()
    assert output["lane"] == "github-trending-weekly"
    assert "42 reusable skills" in output["markdown"]
    log_text = log_path.read_text(encoding="utf-8")
    assert sys.executable in log_text
    assert "-m helpers.lane_subagent_worker" in log_text
    assert "STDOUT" in log_text
    assert "lane_subagent_worker" in log_text
    assert "github-trending-weekly" in log_text


def test_run_lane_subagent_raises_and_logs_nonzero_exit(tmp_path: Path) -> None:
    input_path = tmp_path / "lane_input.json"
    output_path = tmp_path / "lane_output.json"
    log_path = tmp_path / "lane_log.md"
    _write_json(input_path, {"artifact_type": "lane_input"})

    with pytest.raises(RuntimeError, match="lane subagent worker failed"):
        run_lane_subagent(input_path, output_path, log_path, timeout_seconds=10)

    assert not output_path.exists()
    log_text = log_path.read_text(encoding="utf-8")
    assert "Exit Code: 1" in log_text
    assert "STDERR" in log_text
    assert "schema_version must be 1" in log_text


def test_run_lane_subagent_raises_when_process_succeeds_without_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "lane_input.json"
    output_path = tmp_path / "lane_output.json"
    log_path = tmp_path / "lane_log.md"
    _write_json(input_path, _github_trending_lane_input())

    def fake_run(*args, **kwargs):
        command = args[0]
        return subprocess.CompletedProcess(command, 0, stdout="ok but no file\n", stderr="")

    monkeypatch.setattr("helpers.lane_subagent_runner.subprocess.run", fake_run)

    with pytest.raises(RuntimeError, match="did not create output"):
        run_lane_subagent(input_path, output_path, log_path, timeout_seconds=10)

    log_text = log_path.read_text(encoding="utf-8")
    assert "ok but no file" in log_text
