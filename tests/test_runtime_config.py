import unittest
from pathlib import Path

import pytest

from helpers.runtime_config import (
    load_runtime_config,
    resolve_lane_item_limits,
    resolve_lane_paragraph_targets,
    resolve_lane_worker_config,
)


class RuntimeConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config_path = Path(__file__).resolve().parent.parent / "config" / "runtime.yaml"

    def test_runtime_config_loads_yaml_object(self) -> None:
        config = load_runtime_config(self.config_path)
        self.assertIsInstance(config, dict)
        self.assertEqual(config["runtime"]["cron_job_name"], "daily-report-master-0600")

    def test_runtime_config_exposes_lane_item_limits(self) -> None:
        config = load_runtime_config(self.config_path)
        lane_limits = resolve_lane_item_limits(config)
        self.assertEqual(lane_limits["x-feed"], 10)
        self.assertEqual(lane_limits["x-following"], 10)

    def test_runtime_config_exposes_x_lane_paragraph_targets(self) -> None:
        config = load_runtime_config(self.config_path)
        targets = resolve_lane_paragraph_targets(config)
        self.assertEqual(targets["x-feed"], {"min_paragraphs": 6, "max_paragraphs": 10})
        self.assertEqual(targets["x-following"], {"min_paragraphs": 6, "max_paragraphs": 10})


def test_resolve_lane_worker_config_exposes_agent_first_flags() -> None:
    config = {
        "lane_workers": {
            "enabled": True,
            "mode": "subagent",
            "agent_first": True,
            "enabled_lanes": ["github-trending-weekly"],
            "forbid_legacy_fallback_for": ["github-trending-weekly"],
        }
    }

    assert resolve_lane_worker_config(config) == {
        "enabled": True,
        "mode": "subagent",
        "agent_first": True,
        "enabled_lanes": ["github-trending-weekly"],
        "forbid_legacy_fallback_for": ["github-trending-weekly"],
        "github_ai_projects": {},
    }


def test_resolve_lane_worker_config_rejects_agent_first_local_mode() -> None:
    with pytest.raises(ValueError, match="agent_first.*subagent"):
        resolve_lane_worker_config(
            {
                "lane_workers": {
                    "enabled": True,
                    "mode": "local",
                    "agent_first": True,
                    "enabled_lanes": ["github-trending-weekly"],
                }
            }
        )


if __name__ == "__main__":
    unittest.main()
