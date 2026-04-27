from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from helpers import run_daily_report_flow as flow
from helpers.lane_agent_contracts import validate_agent_lane_output
from helpers.lane_agent_registry import build_agent_lane_output
from helpers.lane_contracts import validate_lane_output_artifact


def _write_x_signal(signals_root: Path, report_date: str = "2026-04-27") -> None:
    signal_dir = signals_root / "x-feed" / report_date / "signals"
    signal_dir.mkdir(parents=True)
    (signal_dir / "agent-runtime.md").write_text(
        """---
lane: x-feed
title: "@dev: Agent runtime notes"
url: https://x.com/dev/status/1
---

开发者记录了 agent runtime 的失败恢复策略、工具调用日志和 MCP workflow 调试方式。
""",
        encoding="utf-8",
    )


def _generic_agent_input(raw_candidates: list[dict] | None = None, raw_corpus_status: str = "ok") -> dict:
    return {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "x-feed",
        "timezone": "Asia/Shanghai",
        "lane_title": "X 推荐流",
        "agent_first": True,
        "target_item_count": 1,
        "raw_corpus_status": raw_corpus_status,
        "raw_candidates": raw_candidates
        if raw_candidates is not None
        else [
            {
                "id": "x:1",
                "title": "@dev: Agent runtime notes",
                "source_url": "https://x.com/dev/status/1",
                "source_snippet": "开发者记录了 agent runtime 的失败恢复策略、工具调用日志和 MCP workflow 调试方式。",
                "candidate_source": "agent-runtime.md",
            },
            {
                "id": "x:2",
                "title": "@dev: Overflow",
                "source_url": "https://x.com/dev/status/2",
                "source_snippet": "第二条 raw 候选超过当前 lane item budget。",
                "candidate_source": "overflow.md",
            },
        ],
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": []},
    }


def test_generic_agent_first_lane_uses_raw_candidates_without_render_body_section(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_render(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("render_body_section must not be called in agent-first mode")

    monkeypatch.setattr("helpers.signals_adapter.render_body_section", forbidden_render)

    output = build_agent_lane_output(_generic_agent_input())

    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    assert output["agent_runtime"]["kind"] == "migration_shim"
    assert output["agent_runtime"]["implementation"] == "generic_lane_agent"
    assert output["selected_items"][0]["title"] == "@dev: Agent runtime notes"
    assert output["rejected_items"][0]["reason"] == "超出本 lane item budget"
    assert "失败恢复策略" in output["markdown"]


def test_generic_agent_first_lane_blocks_missing_raw_corpus() -> None:
    output = build_agent_lane_output(_generic_agent_input(raw_candidates=[], raw_corpus_status="blocked_raw_corpus_missing"))

    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    assert output["status"] == "blocked"
    assert output["quality"]["reason"] == "blocked_raw_corpus_missing"


def test_generic_agent_first_lane_deduplicates_source_urls() -> None:
    lane_input = _generic_agent_input(
        raw_candidates=[
            {
                "id": "ph:1",
                "title": "same source one",
                "source_url": "https://www.producthunt.com/posts/example",
                "source_snippet": "Agent workflow launch with MCP tools.",
                "candidate_source": "one.md",
            },
            {
                "id": "ph:2",
                "title": "same source two",
                "source_url": "https://www.producthunt.com/posts/example",
                "source_snippet": "Second raw signal from the same Product Hunt page.",
                "candidate_source": "two.md",
            },
        ]
    )
    lane_input["lane"] = "product-hunt-watch"
    lane_input["lane_title"] = "Product Hunt 新品"

    output = build_agent_lane_output(lane_input)

    assert [source["url"] for source in output["sources"]] == ["https://www.producthunt.com/posts/example"]


def test_main_agent_first_subagent_mode_writes_raw_lane_inputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "runtime.yaml"
    signals_root = tmp_path / "signals"
    runtime_root = tmp_path / "runtime"
    _write_x_signal(signals_root)
    config_path.write_text(
        "version: 1\n"
        f"repo_root: {tmp_path}\n"
        "paths:\n"
        f"  signals_root: {signals_root}\n"
        f"  runtime_root: {runtime_root}\n"
        "selection:\n"
        "  per_lane_limits:\n"
        "    x-feed: 1\n"
        "reader_facing:\n"
        "  fixed_section_order:\n"
        "    - x-feed\n"
        "runtime:\n"
        "  timezone: Asia/Shanghai\n"
        "lane_workers:\n"
        "  enabled: true\n"
        "  mode: subagent\n"
        "  agent_first: true\n"
        "  enabled_lanes:\n"
        "    - x-feed\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-27",
            config=config_path,
            skip_collect=True,
            publish=False,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "build_collect_result",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "lanes": [{"name": "x-feed", "status": "ok", "useful_item_count": 1}],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        },
    )
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "selected_items": [
                {
                    "id": "legacy-x",
                    "lane": "x-feed",
                    "title": "legacy selected item",
                    "source_url": "https://x.com/legacy/status/1",
                    "signal_path": "x-feed/2026-04-27/signals/legacy.md",
                    "fetched_at": "2026-04-27T00:00:00Z",
                    "excerpt": "legacy selected item",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            },
        },
    )
    monkeypatch.setattr(flow, "validate_report_markdown", lambda *_args, **_kwargs: None)

    def fake_run_lane_subagent(input_path: Path, output_path: Path, log_path: Path) -> dict:
        lane_input = json.loads(input_path.read_text(encoding="utf-8"))
        assert lane_input["agent_first"] is True
        assert lane_input["raw_candidates"][0]["title"] == "@dev: Agent runtime notes"
        assert "legacy selected item" not in json.dumps(lane_input["raw_candidates"], ensure_ascii=False)
        output = {
            "artifact_type": "lane_output",
            "schema_version": 1,
            "report_date": "2026-04-27",
            "lane": "x-feed",
            "status": "ok",
            "section_title": "X 推荐流",
            "markdown": "## X 推荐流\n\n- agent runtime 调试方式被明确记录。[原帖](https://x.com/dev/status/1)",
            "items": [
                {
                    "id": "x:1",
                    "title": "@dev: Agent runtime notes",
                    "url": "https://x.com/dev/status/1",
                    "summary": "agent runtime 调试方式被明确记录。",
                    "source_urls": ["https://x.com/dev/status/1"],
                }
            ],
            "sources": [{"label": "@dev: Agent runtime notes", "url": "https://x.com/dev/status/1"}],
            "selected_items": [
                {
                    "id": "x:1",
                    "title": "@dev: Agent runtime notes",
                    "why_selected": "raw corpus includes concrete agent runtime debugging details",
                    "sources": ["https://x.com/dev/status/1"],
                }
            ],
            "rejected_items": [],
            "reasoning_notes": ["selected 1 of 1 raw candidates"],
            "agent_runtime": {"kind": "migration_shim", "implementation": "generic_lane_agent"},
            "quality": {"item_count": 1, "rejected_count": 0},
            "validation": {"status": "passed", "errors": []},
        }
        output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        log_path.write_text("agent-first subagent fake log\n", encoding="utf-8")
        return output

    monkeypatch.setattr(flow, "run_lane_subagent", fake_run_lane_subagent)

    assert flow.main() == 0

    run_dir = runtime_root / "2026-04-27"
    lane_input = json.loads((run_dir / "lane-inputs" / "x-feed.json").read_text(encoding="utf-8"))
    summary = json.loads((run_dir / "run-summary.json").read_text(encoding="utf-8"))
    assert lane_input["agent_first"] is True
    assert lane_input["raw_corpus_status"] == "ok"
    assert summary["lane_workers"]["agent_first"] is True
    assert summary["lane_workers"]["outputs"]["x-feed"]["agent_runtime"]["implementation"] == "generic_lane_agent"
