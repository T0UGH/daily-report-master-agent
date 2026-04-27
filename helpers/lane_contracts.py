from __future__ import annotations

from typing import Any


class LaneContractError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LaneContractError(message)


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    _require(isinstance(value, str) and value.strip(), f"{key} must be non-empty string")
    return value


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    _require(isinstance(value, list), f"{key} must be list")
    return value


def validate_lane_input_artifact(payload: Any) -> None:
    _require(isinstance(payload, dict), "lane input must be object")
    _require(payload.get("schema_version") == 1, "schema_version must be 1")
    _require(payload.get("artifact_type") == "lane_input", "artifact_type must be lane_input")
    _require_str(payload, "report_date")
    _require_str(payload, "lane")
    for key in [
        "timezone",
        "lane_title",
        "target_item_count",
        "min_item_count",
        "signals",
        "recent_history",
        "cross_lane_context",
        "style_contract",
    ]:
        _require(key in payload, f"{key} is required")
    signals = _require_list(payload, "signals")
    _require(isinstance(payload.get("target_item_count"), int), "target_item_count must be int")
    _require(isinstance(payload.get("min_item_count"), int), "min_item_count must be int")
    _require(isinstance(payload.get("recent_history"), dict), "recent_history must be object")
    _require(isinstance(payload.get("cross_lane_context"), dict), "cross_lane_context must be object")
    _require(isinstance(payload.get("style_contract"), dict), "style_contract must be object")
    for index, item in enumerate(signals):
        _require(isinstance(item, dict), f"signals[{index}] must be object")
        _require_str(item, "id")
        _require_str(item, "title")
        _require_str(item, "url")
        _require_str(item, "source_lane")
        _require_list(item, "source_urls")


def validate_lane_output_artifact(payload: Any) -> None:
    _require(isinstance(payload, dict), "lane output must be object")
    _require(payload.get("schema_version") == 1, "schema_version must be 1")
    _require(payload.get("artifact_type") == "lane_output", "artifact_type must be lane_output")
    _require_str(payload, "report_date")
    _require_str(payload, "lane")
    status = _require_str(payload, "status")
    _require(status in {"ok", "empty", "degraded", "blocked"}, "status must be ok, empty, degraded, or blocked")
    _require_str(payload, "section_title")
    _require_str(payload, "markdown")
    _require(isinstance(payload.get("validation"), dict), "validation must be object")
    items = _require_list(payload, "items")
    sources = _require_list(payload, "sources")
    _require(isinstance(payload.get("quality"), dict), "quality must be object")
    if "side_artifacts" in payload:
        _require(isinstance(payload.get("side_artifacts"), dict), "side_artifacts must be object")
    for index, item in enumerate(items):
        _require(isinstance(item, dict), f"items[{index}] must be object")
        _require_str(item, "id")
        _require_str(item, "title")
        _require_str(item, "url")
        _require_list(item, "source_urls")
    for index, source in enumerate(sources):
        _require(isinstance(source, dict), f"sources[{index}] must be object")
        _require_str(source, "label")
        _require_str(source, "url")
