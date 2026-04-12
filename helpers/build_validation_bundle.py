from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.signals_adapter import build_validation_bundle, dump_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and validate a minimal bundle from collect result and selected_items.")
    parser.add_argument("--collect-result", type=Path, required=True)
    parser.add_argument("--selected-items", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    args = parse_args()
    bundle = build_validation_bundle(
        collect_result=load_json(args.collect_result),
        selected_items=load_json(args.selected_items),
    )
    dump_json(bundle, output_path=args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
