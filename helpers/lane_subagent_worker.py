from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.lane_agent_contracts import (
    is_agent_first_lane_input,
    validate_agent_lane_input,
    validate_agent_lane_output,
)
from helpers.lane_agent_registry import build_agent_lane_output
from helpers.lane_contracts import validate_lane_input_artifact, validate_lane_output_artifact
from helpers.lane_workers import build_lane_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one lane worker in an isolated Python process.")
    parser.add_argument("--input", required=True, type=Path, help="Path to lane_input JSON")
    parser.add_argument("--output", required=True, type=Path, help="Path to write lane_output JSON")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("lane input JSON must be an object")
    return data


def dump_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_output_from_input(lane_input: dict[str, Any]) -> dict[str, Any]:
    if is_agent_first_lane_input(lane_input):
        validate_agent_lane_input(lane_input)
        output = build_agent_lane_output(lane_input)
        validate_agent_lane_output(output)
        validate_lane_output_artifact(output)
        if output["report_date"] != lane_input["report_date"]:
            raise ValueError("lane output report_date does not match lane input")
        if output["lane"] != lane_input["lane"]:
            raise ValueError("lane output lane does not match lane input")
        return output

    validate_lane_input_artifact(lane_input)
    report_date = lane_input["report_date"]
    lane_name = lane_input["lane"]
    output = build_lane_output(
        report_date=report_date,
        lane_name=lane_name,
        selected_items={"selected_items": []},
        lane_input=lane_input,
    )
    validate_lane_output_artifact(output)
    if output["report_date"] != report_date:
        raise ValueError("lane output report_date does not match lane input")
    if output["lane"] != lane_name:
        raise ValueError("lane output lane does not match lane input")
    return output


def build_blocked_agent_first_output(lane_input: dict[str, Any], error: Exception) -> dict[str, Any]:
    report_date = lane_input.get("report_date")
    lane_name = lane_input.get("lane")
    if not isinstance(report_date, str) or not report_date.strip():
        raise ValueError("cannot write blocked agent-first output without report_date")
    if not isinstance(lane_name, str) or not lane_name.strip():
        raise ValueError("cannot write blocked agent-first output without lane")
    section_title = str(lane_input.get("lane_title") or lane_name)
    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": report_date,
        "lane": lane_name,
        "agent_first": True,
        "status": "blocked",
        "section_title": section_title,
        "markdown": f"## {section_title}\n\n- 无",
        "items": [],
        "sources": [],
        "selected_items": [],
        "rejected_items": [],
        "reasoning_notes": [f"blocked: agent_first_lane_failed: {error}"],
        "agent_runtime": {
            "kind": "blocked",
            "implementation": "lane_subagent_worker",
        },
        "quality": {
            "item_count": 0,
            "rejected_count": 0,
            "reason": "agent_first_lane_failed",
            "error": str(error),
            "warnings": ["agent_first_lane_failed"],
        },
        "validation": {"status": "blocked", "errors": [str(error)]},
    }
    validate_agent_lane_output(output)
    validate_lane_output_artifact(output)
    return output


def main() -> int:
    args = parse_args()
    lane_input: dict[str, Any] | None = None
    try:
        lane_input = load_json(args.input)
        lane_output = build_output_from_input(lane_input)
        dump_json(lane_output, args.output)
    except Exception as error:
        if lane_input is not None and is_agent_first_lane_input(lane_input):
            try:
                lane_output = build_blocked_agent_first_output(lane_input, error)
                dump_json(lane_output, args.output)
            except Exception as blocked_error:
                print(f"lane_subagent_worker failed: {error}", file=sys.stderr)
                print(f"lane_subagent_worker also failed to write blocked output: {blocked_error}", file=sys.stderr)
                return 1
            print(
                "lane_subagent_worker blocked: "
                f"lane={lane_output['lane']} reason=agent_first_lane_failed output={args.output}",
                file=sys.stderr,
            )
            return 0
        print(f"lane_subagent_worker failed: {error}", file=sys.stderr)
        return 1

    item_count = lane_output.get("quality", {}).get("item_count")
    print(
        "lane_subagent_worker ok: "
        f"lane={lane_output['lane']} status={lane_output['status']} item_count={item_count} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
