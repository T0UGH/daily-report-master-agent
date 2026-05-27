import unittest
from pathlib import Path

from helpers.runtime_config import load_runtime_config, resolve_lane_item_limits, resolve_lane_paragraph_targets


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

    def test_openclaw_is_not_in_default_reader_facing_config(self) -> None:
        config = load_runtime_config(self.config_path)
        lane_limits = resolve_lane_item_limits(config)
        fixed_order = config["reader_facing"]["fixed_section_order"]
        self.assertNotIn("openclaw-watch", lane_limits)
        self.assertNotIn("openclaw-watch", fixed_order)


if __name__ == "__main__":
    unittest.main()
