from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from helpers.lane_agent_contracts import validate_agent_lane_input, validate_agent_lane_output
from helpers.lane_agents.generic_lane_agent import build_generic_lane_agent_output
from helpers.lane_agents.github_trending_agent import build_github_trending_agent_output


@dataclass(frozen=True)
class LaneAgentSpec:
    lane: str
    kind: str
    implementation: str
    forbid_legacy_fallback: bool


_FIXED_LANES = [
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


def _generic_spec(lane: str) -> LaneAgentSpec:
    return LaneAgentSpec(
        lane=lane,
        kind="migration_shim",
        implementation="generic_lane_agent",
        forbid_legacy_fallback=True,
    )


LANE_AGENT_REGISTRY: dict[str, LaneAgentSpec] = {
    **{lane: _generic_spec(lane) for lane in _FIXED_LANES if lane != "github-trending-weekly"},
    "github-trending-weekly": LaneAgentSpec(
        lane="github-trending-weekly",
        kind="specialized_agent",
        implementation="github_trending_agent",
        forbid_legacy_fallback=True,
    ),
}


def registry_coverage(fixed_lanes: list[str]) -> dict[str, list[str]]:
    return {
        "registered": [lane for lane in fixed_lanes if lane in LANE_AGENT_REGISTRY],
        "missing": [lane for lane in fixed_lanes if lane not in LANE_AGENT_REGISTRY],
    }


def get_lane_agent_spec(lane_name: str) -> LaneAgentSpec:
    try:
        return LANE_AGENT_REGISTRY[lane_name]
    except KeyError as error:
        raise ValueError(f"agent-first registry missing lane: {lane_name}") from error


def build_agent_lane_output(lane_input: dict[str, Any]) -> dict[str, Any]:
    validate_agent_lane_input(lane_input)
    spec = get_lane_agent_spec(lane_input["lane"])
    if spec.implementation == "github_trending_agent":
        output = build_github_trending_agent_output(lane_input)
    elif spec.implementation == "generic_lane_agent":
        output = build_generic_lane_agent_output(lane_input)
    else:
        raise ValueError(f"unsupported lane agent implementation: {spec.implementation}")
    validate_agent_lane_output(output)
    return output
