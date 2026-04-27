from __future__ import annotations

from helpers.lane_agent_contracts import validate_agent_lane_output
from helpers.lane_agents.github_trending_agent import build_github_trending_agent_output
from helpers.lane_contracts import validate_lane_output_artifact


BANNED_TEMPLATE_PHRASES = [
    "值得看的趋势项目",
    "具体变化见来源",
    "当前可作为",
    "候选继续观察",
    "至少因为",
    "原始趋势片段写到",
]


def _agent_input() -> dict:
    return {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub 趋势项目",
        "agent_first": True,
        "target_item_count": 3,
        "raw_corpus_status": "ok",
        "raw_candidates": [
            {
                "id": "repo:openai/openai-agents-python",
                "title": "openai/openai-agents-python",
                "source_url": "https://github.com/openai/openai-agents-python",
                "source_snippet": (
                    "OpenAI Agents SDK is a lightweight framework for multi-agent workflows. "
                    "It supports handoffs, tracing, tools, and guardrails for LLM apps."
                ),
                "candidate_source": "openai__openai-agents-python.md",
                "raw": {"metadata": {"stars_this_week": 840}},
            },
            {
                "id": "repo:Alishahryar1/free-claude-code",
                "title": "Alishahryar1/free-claude-code",
                "source_url": "https://github.com/Alishahryar1/free-claude-code",
                "source_snippet": (
                    "A proxy layer for Claude Code that routes Anthropic calls to NVIDIA NIM, "
                    "OpenRouter, DeepSeek, LM Studio, or llama.cpp for local model workflows."
                ),
                "candidate_source": "Alishahryar1__free-claude-code.md",
                "raw": {"metadata": {"stars_this_week": 410}},
            },
            {
                "id": "repo:someuser/react-calendar",
                "title": "someuser/react-calendar",
                "source_url": "https://github.com/someuser/react-calendar",
                "source_snippet": "A reusable React calendar component with date range picking and themes.",
                "candidate_source": "someuser__react-calendar.md",
                "raw": {"metadata": {"stars_this_week": 900}},
            },
            {
                "id": "repo:owner/awesome-terminal",
                "title": "owner/awesome-terminal",
                "source_url": "https://github.com/owner/awesome-terminal",
                "source_snippet": "Terminal themes and shell prompt presets for developers.",
                "candidate_source": "owner__awesome-terminal.md",
                "raw": {"metadata": {"stars_this_week": 500}},
            },
        ],
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": BANNED_TEMPLATE_PHRASES},
        "compatibility": {
            "selected_items_snapshot": {
                "selected_items": [
                    {
                        "id": "repo:compat/selected-only",
                        "title": "compat/selected-only",
                        "source_url": "https://github.com/compat/selected-only",
                    }
                ]
            }
        },
    }


def test_github_trending_agent_selects_and_rejects_from_raw_candidates() -> None:
    output = build_github_trending_agent_output(_agent_input())

    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    assert output["agent_runtime"]["kind"] == "specialized_agent"
    assert output["agent_runtime"]["implementation"] == "github_trending_agent"
    assert [item["title"] for item in output["selected_items"]] == [
        "openai/openai-agents-python",
        "Alishahryar1/free-claude-code",
    ]
    assert {item["title"] for item in output["rejected_items"]} == {
        "someuser/react-calendar",
        "owner/awesome-terminal",
    }
    assert "compat/selected-only" not in output["markdown"]
    assert any("selected 2 of 4 raw candidates" in note for note in output["reasoning_notes"])
    assert output["quality"]["item_count"] == 2
    assert output["quality"]["rejected_count"] == 2


def test_github_trending_agent_avoids_banned_template_phrases() -> None:
    output = build_github_trending_agent_output(_agent_input())
    combined = "\n".join(
        [
            output["markdown"],
            *[item["why_selected"] for item in output["selected_items"]],
            *[item["reason"] for item in output["rejected_items"]],
        ]
    )

    assert all(phrase not in combined for phrase in BANNED_TEMPLATE_PHRASES)


def test_github_trending_agent_rejects_generic_ai_infra_without_agent_workflow() -> None:
    lane_input = _agent_input()
    lane_input["raw_candidates"] = [
        {
            "id": "repo:deepseek-ai/DeepGEMM",
            "title": "deepseek-ai/DeepGEMM",
            "source_url": "https://github.com/deepseek-ai/DeepGEMM",
            "source_snippet": "DeepGEMM is a clean and efficient FP8 GEMM library for MoE training and inference kernels.",
            "candidate_source": "deepseek-ai__DeepGEMM.md",
        }
    ]

    output = build_github_trending_agent_output(lane_input)

    assert output["status"] == "empty"
    assert output["selected_items"] == []
    assert output["rejected_items"][0]["reason"].startswith("原始片段没有体现 coding-agent")


def test_github_trending_agent_strips_broken_markdown_link_fragments_from_fallback_summary() -> None:
    lane_input = _agent_input()
    lane_input["raw_candidates"] = [
        {
            "id": "repo:sample/agent-media",
            "title": "sample/agent-media",
            "source_url": "https://github.com/sample/agent-media",
            "source_snippet": "AI coding agents media toolkit. [Broken](；com/foo/bar) img src logo.png. Ships Claude Code skills and MCP examples for video agents.",
            "candidate_source": "sample__agent-media.md",
        }
    ]

    output = build_github_trending_agent_output(lane_input)

    assert "；com/" not in output["markdown"]
    assert "logo.png" not in output["markdown"]
    assert "Claude Code" in output["markdown"] or "MCP" in output["markdown"]


def test_github_trending_agent_blocks_when_raw_corpus_missing() -> None:
    lane_input = _agent_input()
    lane_input["raw_corpus_status"] = "blocked_raw_corpus_missing"
    lane_input["raw_candidates"] = []

    output = build_github_trending_agent_output(lane_input)

    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    assert output["status"] == "blocked"
    assert output["quality"]["reason"] == "blocked_raw_corpus_missing"
    assert output["items"] == []
