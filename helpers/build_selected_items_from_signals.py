from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.signals_adapter import (
    DEFAULT_SIGNALS_ROOT,
    build_selected_items,
    dump_json,
    resolve_previous_selected_items_path,
)
from helpers.runtime_config import DEFAULT_RUNTIME_CONFIG_PATH, load_runtime_config, resolve_lane_item_limits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build selected_items JSON from signals-engine outputs.")
    parser.add_argument("--signals-root", type=Path, default=DEFAULT_SIGNALS_ROOT)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--lanes", nargs="*")
    parser.add_argument("--per-lane-limit", type=int)
    parser.add_argument("--config", type=Path, default=DEFAULT_RUNTIME_CONFIG_PATH)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_runtime_config(args.config)
    build_kwargs = {
        "signals_root": args.signals_root.expanduser(),
        "report_date": args.report_date,
        "lane_names": args.lanes,
        "per_lane_limit": args.per_lane_limit,
        "lane_item_limits": resolve_lane_item_limits(config),
    }
    runtime_root = ((config.get("paths") or {}) if isinstance(config, dict) else {}).get("runtime_root")
    if isinstance(runtime_root, str) and runtime_root.strip():
        previous_selected_items_path = resolve_previous_selected_items_path(
            runtime_root=Path(runtime_root).expanduser(),
            report_date=args.report_date,
        )
        if previous_selected_items_path is not None:
            build_kwargs["previous_selected_items_path"] = previous_selected_items_path
    result = build_selected_items(
        **build_kwargs,
    )
    dump_json(result, output_path=args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
