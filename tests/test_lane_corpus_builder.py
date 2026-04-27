from __future__ import annotations

import json
from pathlib import Path

import pytest

from helpers.lane_corpus_builder import (
    RAW_CORPUS_MISSING,
    build_raw_candidates_from_signal_dir,
    fixed_section_order_from_config,
    missing_registry_entries,
    require_registry_coverage,
)


ROOT = Path(__file__).resolve().parent.parent


def test_fixed_section_order_from_config_reads_current_runtime_lanes() -> None:
    assert fixed_section_order_from_config(ROOT / "config" / "runtime.yaml") == [
        "weather-watch",
        "x-feed",
        "x-following",
        "reddit-watch",
        "hacker-news-watch",
        "hacker-news-search-watch",
        "claude-code-watch",
        "codex-watch",
        "openclaw-watch",
        "github-ai-projects",
        "github-trending-weekly",
        "product-hunt-watch",
        "polymarket-watch",
    ]


def test_registry_coverage_reports_missing_fixed_lanes() -> None:
    fixed_lanes = ["weather-watch", "github-trending-weekly", "polymarket-watch"]
    registry = {"weather-watch": {"implementation": "weather_agent"}}

    assert missing_registry_entries(fixed_lanes, registry) == [
        "github-trending-weekly",
        "polymarket-watch",
    ]
    with pytest.raises(ValueError, match="github-trending-weekly, polymarket-watch"):
        require_registry_coverage(fixed_lanes, registry)


def test_build_raw_candidates_from_signal_dir_preserves_source_material(tmp_path: Path) -> None:
    signal_dir = tmp_path / "signals"
    signal_dir.mkdir()
    (signal_dir / "owner__agent-tool__trending-weekly.md").write_text(
        """---
type: trending-weekly
lane: github-trending-weekly
repo: owner/agent-tool
source: github-trending
url: https://github.com/owner/agent-tool
title: "agent-tool"
rank: 3
language: "Python"
stars_this_week: 1234
description: "Agent workflow toolkit"
---

## Description

Agent workflow toolkit for coding agents.

## README

This repository contains enough raw README text for a lane agent to make its own selection.
""",
        encoding="utf-8",
    )

    candidates = build_raw_candidates_from_signal_dir(signal_dir)

    assert candidates == [
        {
            "id": "repo:owner/agent-tool",
            "title": "owner/agent-tool",
            "source_url": "https://github.com/owner/agent-tool",
            "source_snippet": (
                "Agent workflow toolkit\n\n"
                "## Description\n\n"
                "Agent workflow toolkit for coding agents.\n\n"
                "## README\n\n"
                "This repository contains enough raw README text for a lane agent to make its own selection."
            ),
            "candidate_source": "owner__agent-tool__trending-weekly.md",
            "raw": {
                "metadata": {
                    "description": "Agent workflow toolkit",
                    "language": "Python",
                    "lane": "github-trending-weekly",
                    "rank": 3,
                    "repo": "owner/agent-tool",
                    "source": "github-trending",
                    "stars_this_week": 1234,
                    "title": "agent-tool",
                    "type": "trending-weekly",
                    "url": "https://github.com/owner/agent-tool",
                },
                "markdown": (
                    "## Description\n\n"
                    "Agent workflow toolkit for coding agents.\n\n"
                    "## README\n\n"
                    "This repository contains enough raw README text for a lane agent to make its own selection."
                ),
            },
        }
    ]


def test_github_trending_fixture_contains_raw_candidates_for_selection() -> None:
    fixture_path = ROOT / "tests" / "fixtures" / "agent_first" / "github_trending_2026_04_26_raw_candidates.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    assert payload["lane"] == "github-trending-weekly"
    assert payload["report_date"] == "2026-04-26"
    assert payload["fallback_status"] != RAW_CORPUS_MISSING
    candidates = payload["raw_candidates"]
    assert len(candidates) >= 6
    assert all(candidate["source_url"].startswith("https://github.com/") for candidate in candidates)
    assert all(len(candidate["source_snippet"]) >= 80 for candidate in candidates)
    assert any("agent" in candidate["source_snippet"].lower() for candidate in candidates)
    assert any("hacking" in candidate["source_snippet"].lower() for candidate in candidates)
