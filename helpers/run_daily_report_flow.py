from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.runtime_config import DEFAULT_RUNTIME_CONFIG_PATH, load_runtime_config, resolve_lane_item_limits
from helpers.signals_adapter import (
    build_collect_result,
    build_report_artifact,
    build_selected_items,
    build_validation_bundle,
    dump_json,
    resolve_previous_selected_items_path,
)
from helpers.validate_report_output_contract import validate_report_markdown


@dataclass
class CommandResult:
    command: list[str]
    exit_code: int
    output_path: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the daily-report-master flow end to end.")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_RUNTIME_CONFIG_PATH)
    parser.add_argument("--skip-collect", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--title-suffix", default="")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def is_path_writable(path: Path) -> bool:
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return os.access(candidate, os.W_OK)


def shanghai_date() -> str:
    result = subprocess.run(["date", "+%F"], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def run_and_capture(command: list[str], output_path: Path, *, cwd: Path | None = None) -> CommandResult:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    rendered = f"$ {' '.join(command)}\n\nSTDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}"
    output_path.write_text(rendered, encoding="utf-8")
    return CommandResult(command=command, exit_code=completed.returncode, output_path=str(output_path))


def run_collect_with_retry(*, lane: str, report_date: str, data_dir: Path, run_dir: Path, verbose: bool) -> dict[str, Any]:
    base_cmd = [
        "uvx",
        "--from",
        str(Path.home() / "workspace" / "signals-engine"),
        "signals-engine",
        "collect",
        "--lane",
        lane,
        "--date",
        report_date,
        "--data-dir",
        str(data_dir),
    ]
    first = run_and_capture(base_cmd, run_dir / "logs" / f"collect-{lane}.log")
    if verbose:
        print(f"collect {lane}: exit={first.exit_code}")
    if first.exit_code == 0:
        return {"lane": lane, "status": "ok", "attempts": 1, "collect_log": first.output_path}

    diagnose_cmd = [
        "uvx",
        "--from",
        str(Path.home() / "workspace" / "signals-engine"),
        "signals-engine",
        "diagnose",
        "--lane",
        lane,
        "--data-dir",
        str(data_dir),
    ]
    diagnose = run_and_capture(diagnose_cmd, run_dir / "logs" / f"diagnose-{lane}.log")
    retry = run_and_capture(base_cmd, run_dir / "logs" / f"collect-{lane}-retry.log")
    status = "ok" if retry.exit_code == 0 else "failed"
    if verbose:
        print(f"collect {lane}: retry exit={retry.exit_code}")
    return {
        "lane": lane,
        "status": status,
        "attempts": 2,
        "collect_log": first.output_path,
        "diagnose_log": diagnose.output_path,
        "retry_log": retry.output_path,
    }


def import_to_feishu(report_path: Path, title: str, run_dir: Path) -> dict[str, Any]:
    cmd = ["feishu-cli", "doc", "import", str(report_path), "--title", title]
    result = run_and_capture(cmd, run_dir / "logs" / "feishu-import.log")
    if result.exit_code != 0:
        return {"status": "failed", "log": result.output_path}
    text = Path(result.output_path).read_text(encoding="utf-8")
    match = re.search(r"链接:\s*(https://\S+)", text)
    return {"status": "succeeded", "log": result.output_path, "doc_url": match.group(1) if match else None}


def main() -> int:
    args = parse_args()
    config = load_runtime_config(args.config)
    runtime = config["runtime"]
    paths = config["paths"]
    repo_root = Path(config.get("repo_root", Path(__file__).resolve().parent.parent)).resolve()
    lane_order = list(config["reader_facing"]["fixed_section_order"])
    signals_root = expand_path(paths["signals_root"])
    data_dir = signals_root.parent
    runtime_root = expand_path(paths["runtime_root"])
    if not is_path_writable(runtime_root):
        runtime_root = repo_root / ".runtime" / "daily-report-master"
    run_dir = runtime_root / args.report_date
    run_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "report_date": args.report_date,
        "timezone": runtime["timezone"],
        "lanes": lane_order,
        "collect": [],
    }

    should_collect = not args.skip_collect
    if should_collect and not is_path_writable(data_dir):
        should_collect = False
        summary["collect_note"] = f"configured signals data dir not writable; reused existing snapshots from {signals_root}"
    if runtime_root != expand_path(paths["runtime_root"]):
        summary["runtime_note"] = f"configured runtime_root not writable; wrote artifacts to {runtime_root}"

    if should_collect:
        for lane in lane_order:
            summary["collect"].append(
                run_collect_with_retry(
                    lane=lane,
                    report_date=args.report_date,
                    data_dir=data_dir,
                    run_dir=run_dir,
                    verbose=args.verbose,
                )
            )

    collect_result = build_collect_result(signals_root=signals_root, report_date=args.report_date, lane_names=lane_order)
    previous_selected_items_path = resolve_previous_selected_items_path(runtime_root=runtime_root, report_date=args.report_date)
    selected_items = build_selected_items(
        signals_root=signals_root,
        report_date=args.report_date,
        lane_names=lane_order,
        lane_item_limits=resolve_lane_item_limits(config),
        previous_selected_items_path=previous_selected_items_path,
    )

    collect_result_path = run_dir / "collect-result.json"
    selected_items_path = run_dir / "selected-items.json"
    validation_bundle_path = run_dir / "validation-bundle.json"
    artifact_path = run_dir / "report-artifact.json"
    report_path = run_dir / "report.md"
    summary_path = run_dir / "run-summary.json"

    dump_json(collect_result, collect_result_path)
    dump_json(selected_items, selected_items_path)
    dump_json(build_validation_bundle(collect_result=collect_result, selected_items=selected_items), validation_bundle_path)

    if collect_result["summary"]["useful_item_count"] <= 0:
        summary["decision"] = "blocked"
        summary["reason"] = "no usable content after collect"
        dump_json(summary, summary_path)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 3

    artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
    dump_json(artifact, artifact_path)
    report_markdown = artifact["body_markdown"]
    report_path.write_text(report_markdown, encoding="utf-8")
    validate_report_markdown(report_markdown, report_date=args.report_date)

    summary["decision"] = "generated"
    summary["artifact_path"] = str(artifact_path)
    summary["report_path"] = str(report_path)
    summary["collect_result_path"] = str(collect_result_path)
    summary["selected_items_path"] = str(selected_items_path)
    summary["validation_bundle_path"] = str(validation_bundle_path)
    summary["selected_item_count"] = selected_items["summary"]["selected_item_count"]
    summary["x_lane_counts"] = {
        item["lane"]: item["selected_item_count"]
        for item in selected_items["summary"]["lane_counts"]
        if item["lane"] in {"x-feed", "x-following"}
    }

    if args.publish:
        title = f"AI 日报（{args.report_date}）{args.title_suffix}" if args.title_suffix else f"AI 日报（{args.report_date}）"
        summary["publish"] = import_to_feishu(report_path, title, run_dir)
    else:
        summary["publish"] = {"status": "skipped"}

    dump_json(summary, summary_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
