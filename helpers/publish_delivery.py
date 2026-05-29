from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CommandResult:
    command: list[str]
    exit_code: int
    output_path: str
    stdout: str
    stderr: str


DEFAULT_FEISHU_RECEIVE_ID_ENV = "FEISHU_HOME_CHANNEL"
DEFAULT_FEISHU_RECEIVE_ID_TYPE = "chat_id"
CURATED_CARD_LINK_LABEL = "查看完整文档"
CURATED_CARD_DEFAULT_SECTION_ITEM_LIMIT = 2
CURATED_CARD_PRODUCT_HUNT_ITEM_LIMIT = 3
CURATED_CARD_MAX_JSON_BYTES = 25_000
CURATED_CARD_MAX_LARK_MD_TEXT_BYTES = 6_000
PUBLISH_REQUIRED_OUTPUTS = ("doc", "card")
PUBLISH_STAGE_STATUSES = {"succeeded", "failed", "skipped"}
PUBLISH_TOP_LEVEL_STATUSES = {"succeeded", "degraded", "failed", "skipped"}


def run_and_capture(
    command: list[str],
    output_path: Path,
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        env=env,
    )
    rendered = f"$ {' '.join(command)}\n\nSTDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}"
    # Some CLI outputs may contain malformed surrogate pairs from upstream JSON/emoji rendering.
    # Preserve the log without letting encoding errors abort publish delivery.
    output_path.write_text(rendered, encoding="utf-8", errors="replace")
    return CommandResult(
        command=command,
        exit_code=completed.returncode,
        output_path=str(output_path),
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _walk_json_scalars(payload: Any) -> list[tuple[str | None, Any]]:
    if isinstance(payload, dict):
        values: list[tuple[str | None, Any]] = []
        for key, value in payload.items():
            values.append((str(key), value))
            values.extend(_walk_json_scalars(value))
        return values
    if isinstance(payload, list):
        values: list[tuple[str | None, Any]] = []
        for item in payload:
            values.extend(_walk_json_scalars(item))
        return values
    return [(None, payload)]


def _find_json_value(
    payload: Any,
    *,
    exact_keys: set[str] | None = None,
    key_fragments: tuple[str, ...] = (),
    value_pattern: re.Pattern[str] | None = None,
) -> str | None:
    normalized_exact_keys = {key.lower() for key in exact_keys or set()}
    for key, value in _walk_json_scalars(payload):
        if value is None:
            continue
        text = str(value)
        if value_pattern and value_pattern.search(text):
            return text
        if key is None:
            continue
        lowered = key.lower()
        if normalized_exact_keys and lowered in normalized_exact_keys:
            return text
        if key_fragments and any(fragment in lowered for fragment in key_fragments):
            return text
    return None


def _extract_doc_url(text: str) -> str | None:
    match = re.search(r"(https://\S+)", text)
    return match.group(1) if match else None


def extract_json_payload(text: str) -> Any | None:
    candidate = text.strip()
    if not candidate:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\})", candidate, flags=re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None


def write_json_log(log_path: Path, payload: Any) -> str:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(log_path)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def set_feishu_doc_public_readable(doc_token: str, run_dir: Path) -> dict[str, Any]:
    """Set a Feishu docx to “互联网获得链接的人可阅读”."""
    permission_payload = {
        "link_share_entity": "anyone_readable",
        "external_access": True,
        "security_entity": "anyone_can_view",
        "comment_entity": "anyone_can_view",
        "share_entity": "anyone",
    }
    patch_result = run_and_capture(
        [
            "lark-cli",
            "api",
            "PATCH",
            f"/open-apis/drive/v1/permissions/{doc_token}/public",
            "--params",
            json.dumps({"type": "docx"}, ensure_ascii=False),
            "--data",
            json.dumps(permission_payload, ensure_ascii=False),
            "--as",
            "bot",
        ],
        run_dir / "logs" / "feishu-permission-public.log",
    )
    if patch_result.exit_code != 0:
        return {
            "status": "failed",
            "log": patch_result.output_path,
            "error_summary": "Feishu doc public permission update failed",
        }

    verify_result = run_and_capture(
        [
            "lark-cli",
            "api",
            "GET",
            f"/open-apis/drive/v1/permissions/{doc_token}/public",
            "--params",
            json.dumps({"type": "docx"}, ensure_ascii=False),
            "--as",
            "bot",
        ],
        run_dir / "logs" / "feishu-permission-public-verify.log",
    )
    if verify_result.exit_code != 0:
        return {
            "status": "failed",
            "log": verify_result.output_path,
            "error_summary": "Feishu doc public permission verification failed",
        }

    payload = extract_json_payload(verify_result.stdout)
    permission_public = ((payload or {}).get("data") or {}).get("permission_public") or {}
    verified = (
        permission_public.get("external_access") is True
        and permission_public.get("link_share_entity") == "anyone_readable"
    )
    return {
        "status": "succeeded" if verified else "failed",
        "log": patch_result.output_path,
        "verify_log": verify_result.output_path,
        "permission_public": permission_public,
        **({} if verified else {"error_summary": "Feishu doc public permission verification mismatch"}),
    }


def import_to_feishu(report_path: Path, title: str, run_dir: Path) -> dict[str, Any]:
    report_path = report_path.resolve()

    cmd = [
        "lark-cli",
        "docs",
        "+create",
        "--as",
        "bot",
        "--title",
        title,
        "--markdown",
        f"@./{report_path.name}",
    ]
    result = run_and_capture(cmd, run_dir / "logs" / "feishu-import.log", cwd=report_path.parent)
    if result.exit_code != 0:
        return {
            "status": "failed",
            "log": result.output_path,
            "error_summary": "Feishu doc import failed",
        }

    doc_url: str | None = None
    doc_token: str | None = None
    doc_id: str | None = None
    stdout = result.stdout.strip()
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            doc_url = _extract_doc_url(f"{result.stdout}\n{result.stderr}")
        else:
            doc_url = _find_json_value(
                payload,
                exact_keys={"url", "doc_url", "document_url", "link"},
                value_pattern=re.compile(r"^https://"),
            )
            doc_token = _find_json_value(
                payload,
                exact_keys={"token", "doc_token", "document_token", "obj_token"},
                key_fragments=("token",),
            )
            doc_id = _find_json_value(
                payload,
                exact_keys={"id", "doc_id", "document_id", "obj_id"},
                key_fragments=("doc_id", "document_id", "_id"),
            )
            if doc_url is None:
                doc_url = _extract_doc_url(stdout)
    if doc_url is None:
        doc_url = _extract_doc_url(f"{result.stdout}\n{result.stderr}")

    response: dict[str, Any] = {
        "status": "succeeded",
        "log": result.output_path,
    }
    if doc_url is not None:
        response["doc_url"] = doc_url
    if doc_token is not None:
        response["doc_token"] = doc_token
    if doc_id is not None:
        response["doc_id"] = doc_id

    permission_token = doc_token or doc_id
    if permission_token is not None:
        public_permission = set_feishu_doc_public_readable(permission_token, run_dir)
        response["public_permission"] = public_permission
        if public_permission.get("status") != "succeeded":
            response["status"] = "failed"
            response["error_summary"] = public_permission.get(
                "error_summary",
                "Feishu doc public permission update failed",
            )

    return response


def _truncate_sources_tail(text: str) -> str:
    sources_match = re.search(r"^##\s*来源\s*$", text, flags=re.M)
    if sources_match:
        return text[: sources_match.start()].rstrip()
    return text


def parse_report_markdown_sections(report_markdown: str) -> tuple[str | None, list[tuple[str, list[str]]]]:
    text = report_markdown.replace("\r\n", "\n").strip()
    text = _truncate_sources_tail(text)
    text = re.sub(r"```.*?```", "\n", text, flags=re.S)

    report_title: str | None = None
    sections: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_items: list[str] = []
    current_item_lines: list[str] | None = None

    def flush_item() -> None:
        nonlocal current_item_lines
        if current_item_lines is None:
            return
        item_text = " ".join(line.strip() for line in current_item_lines if line.strip()).strip()
        current_item_lines = None
        if item_text and current_heading is not None:
            current_items.append(item_text)

    def flush_section() -> None:
        nonlocal current_heading, current_items
        if current_heading is None:
            return
        if current_items:
            sections.append((current_heading, current_items[:]))
        current_heading = None
        current_items = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_item()
            continue

        heading_match = re.match(r"^(#{1,6})\s*(.+?)\s*$", line)
        if heading_match:
            flush_item()
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if heading_level == 1:
                report_title = heading_text
                continue
            flush_section()
            current_heading = heading_text
            current_items = []
            continue

        bullet_match = re.match(r"^(?:[-*+]|\d+\.)\s+(.*)$", line)
        if bullet_match:
            flush_item()
            current_item_lines = [bullet_match.group(1).strip()]
            continue

        if current_item_lines is not None:
            current_item_lines.append(line)
            continue

        if current_heading is not None:
            current_items.append(line)

    flush_item()
    flush_section()
    return report_title, sections


def _is_weather_section(heading: str) -> bool:
    return "天气" in heading


def _card_section_item_limit(heading: str) -> int:
    if "product hunt" in heading.lower():
        return CURATED_CARD_PRODUCT_HUNT_ITEM_LIMIT
    return CURATED_CARD_DEFAULT_SECTION_ITEM_LIMIT


def _order_card_sections(sections: list[tuple[str, list[str]]]) -> list[tuple[str, list[str]]]:
    indexed_sections = list(enumerate(sections))
    indexed_sections.sort(key=lambda item: (0 if _is_weather_section(item[1][0]) else 1, item[0]))
    return [section for _, section in indexed_sections]


def _build_card_section_elements(*, heading: str, items: list[str]) -> list[dict[str, Any]]:
    limited_items = items[: _card_section_item_limit(heading)]
    content_lines = [f"- {item}" for item in limited_items]
    return [
        {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": heading,
                "text_size": "section_title",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "\n".join(content_lines),
                "text_size": "normal",
            },
        },
    ]


def build_curated_card_payload(*, report_markdown: str, doc_url: str) -> dict[str, Any]:
    report_title, sections = parse_report_markdown_sections(report_markdown)
    ordered_sections = _order_card_sections([(heading, items) for heading, items in sections if heading != "来源"])
    elements: list[dict[str, Any]] = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"我不是贵平，我是 Rook。 [{CURATED_CARD_LINK_LABEL}]({doc_url})",
                "text_size": "normal",
            },
        }
    ]

    rendered_sections = [section for section in ordered_sections if section[1]]
    if rendered_sections:
        elements.append({"tag": "hr"})
    for index, (heading, items) in enumerate(rendered_sections):
        elements.extend(_build_card_section_elements(heading=heading, items=items))
        if index != len(rendered_sections) - 1:
            elements.append({"tag": "hr"})

    return {
        "config": {
            "wide_screen_mode": True,
            "style": {
                "text_size": {
                    "section_title": {
                        "default": "heading-2",
                        "pc": "heading-2",
                        "mobile": "heading-2",
                    }
                }
            },
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": report_title or "AI Agent 日报精选",
            },
            "subtitle": {
                "tag": "lark_md",
                "content": f"[{CURATED_CARD_LINK_LABEL}]({doc_url})",
            },
        },
        "elements": elements,
    }


def _json_byte_size(payload: Any) -> int:
    return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def _safe_json_byte_size(payload: Any) -> int | None:
    try:
        return _json_byte_size(payload)
    except (TypeError, ValueError):
        return None


def _extract_curated_card_doc_url(payload: dict[str, Any]) -> str | None:
    markdown_link_pattern = re.compile(rf"\[{re.escape(CURATED_CARD_LINK_LABEL)}\]\(([^)]+)\)")
    raw_url_pattern = re.compile(r"https?://[^\s)]+")
    for _, value in _walk_json_scalars(payload):
        if not isinstance(value, str):
            continue
        markdown_match = markdown_link_pattern.search(value)
        if markdown_match:
            return markdown_match.group(1).strip()
        raw_match = raw_url_pattern.search(value)
        if raw_match:
            return raw_match.group(0).strip()
    return None


def validate_curated_card_payload(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    try:
        card_json_bytes = _json_byte_size(payload)
    except (TypeError, ValueError) as exc:
        issues.append(f"Card payload is not JSON serializable: {exc}")
        card_json_bytes = 0

    if card_json_bytes > CURATED_CARD_MAX_JSON_BYTES:
        issues.append(f"Card payload JSON is {card_json_bytes} bytes, exceeds {CURATED_CARD_MAX_JSON_BYTES} bytes")

    if not isinstance(payload, dict):
        issues.append("Card payload must be a JSON object")
        return issues

    header = payload.get("header")
    if not isinstance(header, dict):
        issues.append("Card payload missing required header object")
    else:
        title = header.get("title")
        if not isinstance(title, dict):
            issues.append("Card payload missing required header.title object")
        elif not isinstance(title.get("content"), str) or not title.get("content", "").strip():
            issues.append("Card payload missing required header.title.content text")

    elements = payload.get("elements")
    if not isinstance(elements, list) or not elements:
        issues.append("Card payload missing required non-empty elements list")
        return issues

    for index, element in enumerate(elements):
        element_path = f"elements[{index}]"
        if not isinstance(element, dict):
            issues.append(f"{element_path} must be an object")
            continue
        if element.get("tag") != "div":
            continue
        text = element.get("text")
        if not isinstance(text, dict):
            issues.append(f"{element_path} div missing required text object")
            continue
        content = text.get("content")
        if not isinstance(content, str):
            issues.append(f"{element_path} div text content must be a string")
            continue
        if text.get("tag") == "lark_md":
            text_bytes = len(content.encode("utf-8"))
            if text_bytes > CURATED_CARD_MAX_LARK_MD_TEXT_BYTES:
                issues.append(
                    f"{element_path} lark_md content is {text_bytes} bytes, "
                    f"exceeds {CURATED_CARD_MAX_LARK_MD_TEXT_BYTES} bytes"
                )

    return issues


def _has_valid_card_header(header: Any) -> bool:
    if not isinstance(header, dict):
        return False
    title = header.get("title")
    return isinstance(title, dict) and isinstance(title.get("content"), str) and bool(title["content"].strip())


def compact_curated_card_payload(payload: dict[str, Any], doc_url: str) -> dict[str, Any]:
    header = payload.get("header") if isinstance(payload, dict) else None
    if not _has_valid_card_header(header):
        header = {
            "title": {
                "tag": "plain_text",
                "content": "AI Agent 日报精选",
            }
        }

    doc_link = f"[{CURATED_CARD_LINK_LABEL}]({doc_url})" if doc_url else CURATED_CARD_LINK_LABEL
    return {
        "config": {"wide_screen_mode": True},
        "header": header,
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"精选卡片内容较长，已简化展示。如需完整内容，请查看完整文档：{doc_link}",
                    "text_size": "normal",
                },
            }
        ],
    }


def resolve_feishu_audio_delivery(config: dict[str, Any]) -> dict[str, str]:
    raw_delivery = ((config.get("audio") or {}).get("delivery") or {})
    receive_id_env = str(raw_delivery.get("receive_id_env") or DEFAULT_FEISHU_RECEIVE_ID_ENV)
    receive_id_type = str(raw_delivery.get("receive_id_type") or DEFAULT_FEISHU_RECEIVE_ID_TYPE)

    receive_id = os.getenv(DEFAULT_FEISHU_RECEIVE_ID_ENV, "").strip()
    if not receive_id and receive_id_env != DEFAULT_FEISHU_RECEIVE_ID_ENV:
        receive_id = os.getenv(receive_id_env, "").strip()
    if not receive_id:
        receive_id = str(raw_delivery.get("receive_id") or "").strip()

    return {
        "receive_id": receive_id,
        "receive_id_type": receive_id_type,
    }


def send_curated_card_to_feishu(*, card_payload: dict[str, Any], run_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    delivery = resolve_feishu_audio_delivery(config)
    log_path = run_dir / "logs" / "feishu-card.log"
    preflight_log: str | None = None
    preflight_issues: list[str] = []
    degraded = False
    if delivery["receive_id_type"] != "chat_id":
        return {
            "status": "failed",
            "log": write_json_log(
                log_path,
                {"error": f"Unsupported receive_id_type for curated card delivery: {delivery['receive_id_type']}"},
            ),
            "error_summary": f"Unsupported receive_id_type for curated card delivery: {delivery['receive_id_type']}",
        }
    if not delivery["receive_id"]:
        return {
            "status": "failed",
            "log": write_json_log(
                log_path,
                {"error": f"Missing {DEFAULT_FEISHU_RECEIVE_ID_ENV} for curated card delivery"},
            ),
            "error_summary": f"Missing {DEFAULT_FEISHU_RECEIVE_ID_ENV} for curated card delivery",
        }

    validation_issues = validate_curated_card_payload(card_payload)
    if validation_issues:
        degraded = True
        preflight_issues = validation_issues
        doc_url = _extract_curated_card_doc_url(card_payload) or ""
        compact_payload = compact_curated_card_payload(card_payload, doc_url)
        compact_issues = validate_curated_card_payload(compact_payload)
        preflight_log = write_json_log(
            run_dir / "logs" / "feishu-card-preflight.json",
            {
                "degraded": True,
                "issues": validation_issues,
                "compact_issues": compact_issues,
                "doc_url": doc_url,
                "original_json_bytes": _safe_json_byte_size(card_payload),
                "compact_json_bytes": _safe_json_byte_size(compact_payload),
                "max_card_json_bytes": CURATED_CARD_MAX_JSON_BYTES,
                "max_lark_md_text_bytes": CURATED_CARD_MAX_LARK_MD_TEXT_BYTES,
            },
        )
        if compact_issues:
            return {
                "status": "failed",
                "log": preflight_log,
                "error_summary": "Feishu curated card preflight validation failed: " + " | ".join(compact_issues),
                "degraded": True,
                "preflight_log": preflight_log,
                "preflight_issues": validation_issues,
                "compact_preflight_issues": compact_issues,
            }
        card_payload = compact_payload

    command = [
        "lark-cli",
        "im",
        "+messages-send",
        "--as",
        "user",
        "--chat-id",
        delivery["receive_id"],
        "--msg-type",
        "interactive",
        "--content",
        json.dumps(card_payload, ensure_ascii=False),
    ]
    result = run_and_capture(command, log_path)
    if result.exit_code != 0:
        failed_result: dict[str, Any] = {
            "status": "failed",
            "log": result.output_path,
            "error_summary": "Feishu curated card send failed",
        }
        if degraded:
            failed_result["degraded"] = True
            failed_result["preflight_log"] = preflight_log
            failed_result["preflight_issues"] = preflight_issues
        return failed_result

    message_id: str | None = None
    stdout = result.stdout.strip()
    if stdout:
        payload = extract_json_payload(stdout)
        if payload is not None:
            message_id = _find_json_value(
                payload,
                exact_keys={"message_id", "new_message_id"},
                key_fragments=("message_id",),
            )

    send_result: dict[str, Any] = {
        "status": "succeeded",
        "log": result.output_path,
        "message_id": message_id,
    }
    if degraded:
        send_result["degraded"] = True
        send_result["preflight_log"] = preflight_log
        send_result["preflight_issues"] = preflight_issues
    return send_result


def _publish_state_path(path: Any, run_dir: Path) -> str | None:
    if path is None:
        return None
    raw_path = str(path)
    if not raw_path:
        return None
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        return candidate.as_posix()
    try:
        return candidate.resolve().relative_to(run_dir.resolve()).as_posix()
    except ValueError:
        return raw_path


def _publish_stage_status(value: Any) -> str:
    status = str(value or "skipped")
    if status in PUBLISH_STAGE_STATUSES:
        return status
    return "failed"


def _publish_top_level_status(value: Any) -> str:
    status = str(value or "failed")
    if status in PUBLISH_TOP_LEVEL_STATUSES:
        return status
    return "failed"


def _build_publish_state(
    *,
    report_date: str,
    run_dir: Path,
    publish_result: dict[str, Any],
    updated_at: str,
) -> dict[str, Any]:
    doc_status = _publish_stage_status(publish_result.get("doc_status"))
    card_status = _publish_stage_status(publish_result.get("card_status"))
    audio_status = _publish_stage_status(publish_result.get("audio_status"))
    publish_status = _publish_top_level_status(publish_result.get("status"))
    if publish_status == "succeeded" and publish_result.get("card_degraded"):
        publish_status = "degraded"
    card_message_id = publish_result.get("card_message_id")
    missing_required_outputs = []
    if doc_status != "succeeded":
        missing_required_outputs.append("doc")
    if card_status != "succeeded" or not card_message_id:
        missing_required_outputs.append("card")
    final_delivery_ok = (
        doc_status == "succeeded"
        and card_status == "succeeded"
        and bool(card_message_id)
        and not missing_required_outputs
    )

    return {
        "report_date": report_date,
        "status": publish_status,
        "doc": {
            "status": doc_status,
            "url": publish_result.get("doc_url"),
            "log_path": _publish_state_path(publish_result.get("doc_log"), run_dir),
            "error_summary": publish_result.get("doc_error_summary"),
        },
        "card": {
            "status": card_status,
            "message_id": publish_result.get("card_message_id"),
            "payload_path": _publish_state_path(publish_result.get("card_payload_path"), run_dir),
            "preflight_path": _publish_state_path(publish_result.get("card_preflight_log"), run_dir),
            "log_path": _publish_state_path(publish_result.get("card_message_log"), run_dir),
            "error_summary": publish_result.get("card_error_summary"),
        },
        "audio": {
            "status": audio_status,
            "message_id": publish_result.get("audio_message_id"),
            "opus_path": _publish_state_path(publish_result.get("audio_opus_path"), run_dir),
            "log_path": _publish_state_path(
                publish_result.get("audio_message_log")
                or publish_result.get("audio_convert_log")
                or publish_result.get("audio_tts_log"),
                run_dir,
            ),
            "error_summary": publish_result.get("audio_error_summary"),
        },
        "required_outputs": list(PUBLISH_REQUIRED_OUTPUTS),
        "missing_required_outputs": missing_required_outputs,
        "final_delivery_ok": final_delivery_ok,
        "updated_at": updated_at,
    }


def write_publish_delivery_state(
    *,
    report_date: str,
    run_dir: Path,
    publish_result: dict[str, Any],
) -> dict[str, Any]:
    updated_at = utc_timestamp()
    state = _build_publish_state(
        report_date=report_date,
        run_dir=run_dir,
        publish_result=publish_result,
        updated_at=updated_at,
    )
    write_json_log(run_dir / "publish-state.json", state)
    write_json_log(
        run_dir / "stage-status" / "publish-doc.json",
        {
            "report_date": report_date,
            "stage": "publish-doc",
            **state["doc"],
            "updated_at": updated_at,
        },
    )
    write_json_log(
        run_dir / "stage-status" / "publish-card.json",
        {
            "report_date": report_date,
            "stage": "publish-card",
            **state["card"],
            "updated_at": updated_at,
        },
    )
    return state


def write_card_payload_artifact(*, run_dir: Path, card_payload: dict[str, Any]) -> str:
    return write_json_log(run_dir / "artifacts" / "feishu-card.json", card_payload)
