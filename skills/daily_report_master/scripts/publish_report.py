from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Sequence

from helpers.publish_delivery import (
    build_curated_card_payload,
    import_to_feishu,
    send_curated_card_to_feishu,
    write_card_payload_artifact,
    write_publish_delivery_state,
)
from helpers.runtime_config import DEFAULT_RUNTIME_CONFIG_PATH, load_runtime_config


REPORT_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def build_lark_create_command(report_path: Path, title: str) -> list[str]:
    # lark-cli requires @file to be relative to cwd, so callers should run with cwd=report_path.parent.
    return [
        "lark-cli",
        "docs",
        "+create",
        "--as",
        "user",
        "--title",
        title,
        "--markdown",
        f"@{report_path.name}",
    ]


def infer_report_date(report_path: Path, title: str) -> str:
    for value in (report_path.parent.name, title):
        match = REPORT_DATE_RE.search(value)
        if match:
            return match.group(0)
    raise ValueError("could not infer --report-date from report path parent or title")


def _initial_publish_result(doc_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "target": "feishu",
        "doc_status": doc_result["status"],
        "doc_log": doc_result.get("log"),
        "doc_url": doc_result.get("doc_url"),
        "doc_error_summary": doc_result.get("error_summary"),
        "card_status": "skipped",
        "card_payload": None,
        "card_payload_path": None,
        "card_message_log": None,
        "card_message_id": None,
        "card_error_summary": None,
        "audio_status": "skipped",
        "audio_message_log": None,
        "audio_message_id": None,
        "audio_error_summary": None,
    }


def _apply_card_result(publish_result: dict[str, Any], card_result: dict[str, Any]) -> None:
    if card_result.get("status") == "succeeded" and not card_result.get("message_id"):
        card_result = {
            **card_result,
            "status": "failed",
            "error_summary": "Feishu curated card send succeeded without message_id",
        }

    publish_result["card_status"] = card_result["status"]
    publish_result["card_message_log"] = card_result.get("log")
    publish_result["card_message_id"] = card_result.get("message_id")
    publish_result["card_error_summary"] = card_result.get("error_summary")
    if card_result.get("degraded"):
        publish_result["card_degraded"] = True
    if card_result.get("preflight_log"):
        publish_result["card_preflight_log"] = card_result.get("preflight_log")
    if card_result.get("preflight_issues"):
        publish_result["card_preflight_issues"] = card_result.get("preflight_issues")


def publish_report_to_feishu(
    *,
    report_path: Path,
    title: str,
    report_date: str,
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    report_path = report_path.expanduser().resolve()
    run_dir = report_path.parent
    report_markdown = report_path.read_text(encoding="utf-8")

    doc_result = import_to_feishu(report_path, title, run_dir)
    publish_result = _initial_publish_result(doc_result)

    if doc_result["status"] != "succeeded":
        publish_result["status"] = "failed"
        publish_result["error_summary"] = doc_result.get("error_summary") or "Feishu doc import failed"
        publish_result["doc_error_summary"] = publish_result["error_summary"]
    elif not doc_result.get("doc_url"):
        publish_result["status"] = "degraded"
        publish_result["card_status"] = "failed"
        publish_result["card_error_summary"] = "Missing Feishu doc URL for curated card delivery"
        publish_result["error_summary"] = publish_result["card_error_summary"]
    else:
        card_payload = build_curated_card_payload(
            report_markdown=report_markdown,
            doc_url=str(doc_result["doc_url"]),
        )
        publish_result["card_payload"] = card_payload
        publish_result["card_payload_path"] = write_card_payload_artifact(
            run_dir=run_dir,
            card_payload=card_payload,
        )
        card_result = send_curated_card_to_feishu(
            card_payload=card_payload,
            run_dir=run_dir,
            config=config,
        )
        _apply_card_result(publish_result, card_result)
        if publish_result["card_status"] != "succeeded":
            publish_result["status"] = "degraded"
            publish_result["card_error_summary"] = (
                publish_result.get("card_error_summary") or "Feishu curated card send failed"
            )
            publish_result["error_summary"] = publish_result["card_error_summary"]
        else:
            publish_result["status"] = "succeeded"

    state = write_publish_delivery_state(
        report_date=report_date,
        run_dir=run_dir,
        publish_result=publish_result,
    )
    return publish_result, state


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-path", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--report-date")
    parser.add_argument("--config", type=Path, default=DEFAULT_RUNTIME_CONFIG_PATH)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report_path = args.report_path.expanduser().resolve()
    try:
        report_date = args.report_date or infer_report_date(report_path, args.title)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    config = load_runtime_config(args.config)
    publish_result, state = publish_report_to_feishu(
        report_path=report_path,
        title=args.title,
        report_date=report_date,
        config=config,
    )
    print(
        json.dumps(
            {
                "status": publish_result.get("status"),
                "doc_url": publish_result.get("doc_url"),
                "card_message_id": publish_result.get("card_message_id"),
                "final_delivery_ok": state.get("final_delivery_ok"),
                "missing_required_outputs": state.get("missing_required_outputs"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if state.get("final_delivery_ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
