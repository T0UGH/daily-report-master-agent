import argparse
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers import build_selected_items_from_signals as script


class BuildSelectedItemsScriptTest(unittest.TestCase):
    def test_main_passes_runtime_config_lane_limits_into_builder(self) -> None:
        args = argparse.Namespace(
            signals_root=Path("/tmp/signals"),
            report_date="2026-04-14",
            lanes=["x-feed", "x-following"],
            per_lane_limit=None,
            config=Path("/tmp/runtime.yaml"),
            output=Path("/tmp/selected-items.json"),
        )
        config = {"selection": {"per_lane_limits": {"x-feed": 10, "x-following": 8}}}
        built = {"selected_items": [], "summary": {"selected_item_count": 0, "lane_counts": []}}

        with patch.object(script, "parse_args", return_value=args), \
             patch.object(script, "load_runtime_config", return_value=config), \
             patch.object(script, "resolve_lane_item_limits", return_value={"x-feed": 10, "x-following": 8}), \
             patch.object(script, "build_selected_items", return_value=built) as mock_build, \
             patch.object(script, "dump_json") as mock_dump:
            rc = script.main()

        self.assertEqual(rc, 0)
        mock_build.assert_called_once_with(
            signals_root=Path("/tmp/signals"),
            report_date="2026-04-14",
            lane_names=["x-feed", "x-following"],
            per_lane_limit=None,
            lane_item_limits={"x-feed": 10, "x-following": 8},
        )
        mock_dump.assert_called_once_with(built, output_path=Path("/tmp/selected-items.json"))


if __name__ == "__main__":
    unittest.main()
