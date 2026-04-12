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
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build selected_items JSON from signals-engine outputs.")
    parser.add_argument("--signals-root", type=Path, default=DEFAULT_SIGNALS_ROOT)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--lanes", nargs="*")
    parser.add_argument("--per-lane-limit", type=int)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_selected_items(
        signals_root=args.signals_root.expanduser(),
        report_date=args.report_date,
        lane_names=args.lanes,
        per_lane_limit=args.per_lane_limit,
    )
    dump_json(result, output_path=args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
