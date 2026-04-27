from __future__ import annotations

from pathlib import Path

from helpers.lane_agent_registry import LANE_AGENT_REGISTRY, get_lane_agent_spec, registry_coverage
from helpers.lane_corpus_builder import fixed_section_order_from_config


ROOT = Path(__file__).resolve().parent.parent


def test_lane_agent_registry_covers_every_fixed_runtime_lane() -> None:
    fixed_lanes = fixed_section_order_from_config(ROOT / "config" / "runtime.yaml")

    coverage = registry_coverage(fixed_lanes)

    assert coverage["missing"] == []
    assert coverage["registered"] == fixed_lanes
    assert set(LANE_AGENT_REGISTRY) >= set(fixed_lanes)


def test_github_trending_registry_entry_forbids_legacy_fallback() -> None:
    spec = get_lane_agent_spec("github-trending-weekly")

    assert spec.kind == "specialized_agent"
    assert spec.implementation == "github_trending_agent"
    assert spec.forbid_legacy_fallback is True


def test_non_specialized_lanes_are_explicit_migration_shims() -> None:
    fixed_lanes = fixed_section_order_from_config(ROOT / "config" / "runtime.yaml")
    shim_lanes = [lane for lane in fixed_lanes if lane != "github-trending-weekly"]

    for lane in shim_lanes:
        spec = get_lane_agent_spec(lane)
        assert spec.kind in {"generic_shim", "migration_shim"}
        assert spec.implementation == "generic_lane_agent"
