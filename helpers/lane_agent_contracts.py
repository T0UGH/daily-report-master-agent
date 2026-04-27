from __future__ import annotations

from typing import Any


class LaneAgentContractError(ValueError):
    pass


_ALLOWED_STATUSES = {"ok", "empty", "degraded", "blocked"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LaneAgentContractError(message)


def _require_object(payload: Any, label: str) -> dict[str, Any]:
    _require(isinstance(payload, dict), f"{label} must be object")
    return payload


def _require_str(payload: dict[str, Any], key: str, *, allow_empty: bool = False) -> str:
    value = payload.get(key)
    if allow_empty:
        _require(isinstance(value, str), f"{key} must be string")
    else:
        _require(isinstance(value, str) and bool(value.strip()), f"{key} must be non-empty string")
    return value


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    _require(isinstance(value, list), f"{key} must be list")
    return value


def _require_common_lane_artifact(payload: dict[str, Any], artifact_type: str) -> None:
    _require(payload.get("artifact_type") == artifact_type, f"artifact_type must be {artifact_type}")
    _require(payload.get("schema_version") == 1, "schema_version must be 1")
    _require_str(payload, "report_date")
    _require_str(payload, "lane")


def is_agent_first_lane_input(payload: Any) -> bool:
    return (
        isinstance(payload, dict)
        and payload.get("artifact_type") == "lane_input"
        and payload.get("agent_first") is True
    )


def validate_agent_lane_input(payload: Any) -> None:
    lane_input = _require_object(payload, "agent lane input")
    _require_common_lane_artifact(lane_input, "lane_input")
    _require(lane_input.get("agent_first") is True, "agent_first must be true")
    raw_candidates = _require_list(lane_input, "raw_candidates")
    _require(isinstance(lane_input.get("style_contract"), dict), "style_contract must be object")

    for index, candidate in enumerate(raw_candidates):
        item = _require_object(candidate, f"raw_candidates[{index}]")
        _require_str(item, "id")
        _require_str(item, "title")
        if "source_url" in item:
            _require_str(item, "source_url")
        if "source_snippet" in item:
            _require_str(item, "source_snippet")
        if "candidate_source" in item:
            _require_str(item, "candidate_source")


def validate_agent_lane_output(payload: Any) -> None:
    lane_output = _require_object(payload, "agent lane output")
    _require_common_lane_artifact(lane_output, "lane_output")
    status = _require_str(lane_output, "status")
    _require(status in _ALLOWED_STATUSES, "status must be ok, empty, degraded, or blocked")

    _require_str(lane_output, "section_title")
    markdown = _require_str(lane_output, "markdown", allow_empty=True)
    items = _require_list(lane_output, "items")
    sources = _require_list(lane_output, "sources")
    selected_items = _require_list(lane_output, "selected_items")
    rejected_items = _require_list(lane_output, "rejected_items")
    reasoning_notes = _require_list(lane_output, "reasoning_notes")
    agent_runtime = _require_object(lane_output.get("agent_runtime"), "agent_runtime")
    quality = _require_object(lane_output.get("quality"), "quality")

    _require_str(agent_runtime, "kind")
    _require_str(agent_runtime, "implementation")

    if status == "ok":
        _require(bool(markdown.strip()), "ok status requires non-empty markdown")
    if status == "blocked":
        _require(_has_blocked_reason(lane_output, quality, reasoning_notes), "blocked status requires error or reason note")

    for index, item in enumerate(items):
        output_item = _require_object(item, f"items[{index}]")
        _require_str(output_item, "id")
        _require_str(output_item, "title")
        _require_str(output_item, "url")
        _require_list(output_item, "source_urls")

    for index, source in enumerate(sources):
        if isinstance(source, str):
            _require(bool(source.strip()), f"sources[{index}] must be non-empty string")
            continue
        source_item = _require_object(source, f"sources[{index}]")
        _require_str(source_item, "label")
        _require_str(source_item, "url")

    for index, item in enumerate(selected_items):
        selected = _require_object(item, f"selected_items[{index}]")
        _require_str(selected, "id")
        _require_str(selected, "title")
        _require_str(selected, "why_selected")
        _require_list(selected, "sources")

    for index, item in enumerate(rejected_items):
        rejected = _require_object(item, f"rejected_items[{index}]")
        _require_str(rejected, "id")
        _require_str(rejected, "title")
        _require_str(rejected, "reason")

    for index, note in enumerate(reasoning_notes):
        _require(isinstance(note, str) and bool(note.strip()), f"reasoning_notes[{index}] must be non-empty string")


def _has_blocked_reason(
    lane_output: dict[str, Any],
    quality: dict[str, Any],
    reasoning_notes: list[Any],
) -> bool:
    for key in ("error", "reason"):
        value = lane_output.get(key)
        if isinstance(value, str) and value.strip():
            return True
        quality_value = quality.get(key)
        if isinstance(quality_value, str) and quality_value.strip():
            return True
    return any(isinstance(note, str) and note.strip() for note in reasoning_notes)
