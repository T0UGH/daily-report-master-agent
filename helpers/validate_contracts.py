import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = REPO_ROOT / "contracts"


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_with_schema(schema_name: str, data: object) -> None:
    schema = load_json(CONTRACTS_DIR / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
    if errors:
        messages = []
        for error in errors:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            messages.append(f"{schema_name} -> {location}: {error.message}")
        raise ValueError("\n".join(messages))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_collect_result(data: object) -> None:
    require(isinstance(data, dict), "collect-result.json 必须是 JSON object")
    require(isinstance(data.get("report_date"), str), "collect result 必须包含 report_date")
    require(isinstance(data.get("source"), str), "collect result 必须包含 source")
    lanes = data.get("lanes")
    require(isinstance(lanes, list), "collect result 必须包含 lanes 数组")
    summary = data.get("summary")
    require(isinstance(summary, dict), "collect result 必须包含 summary object")
    useful_item_count = summary.get("useful_item_count")
    require(isinstance(useful_item_count, int) and useful_item_count >= 0, "summary.useful_item_count 必须是非负整数")

    partial_lane_count = summary.get("partial_lane_count", 0)
    require(isinstance(partial_lane_count, int) and partial_lane_count >= 0, "summary.partial_lane_count 必须是非负整数")

    lane_sum = 0
    partial_count = 0
    for index, lane in enumerate(lanes):
        require(isinstance(lane, dict), f"lanes[{index}] 必须是 object")
        require(isinstance(lane.get("name"), str) and lane["name"], f"lanes[{index}].name 必须是非空字符串")
        require(lane.get("status") in {"ok", "partial", "error"}, f"lanes[{index}].status 非法")
        count = lane.get("useful_item_count")
        require(isinstance(count, int) and count >= 0, f"lanes[{index}].useful_item_count 必须是非负整数")
        lane_sum += count
        if lane["status"] != "ok":
            partial_count += 1

    require(lane_sum == useful_item_count, "summary.useful_item_count 必须等于各 lane useful_item_count 之和")
    require(partial_lane_count == partial_count, "summary.partial_lane_count 必须等于非 ok lane 数")

    errors = data.get("errors")
    if errors is not None:
        require(isinstance(errors, list), "errors 存在时必须是数组")
        for index, item in enumerate(errors):
            require(isinstance(item, str) and item, f"errors[{index}] 必须是非空字符串")

    side_effects = data.get("side_effects")
    if side_effects is not None:
        require(isinstance(side_effects, dict), "side_effects 存在时必须是 object")
        archive = side_effects.get("archive")
        if archive is not None:
            require(isinstance(archive, dict), "side_effects.archive 存在时必须是 object")
            require(archive.get("status") == "failed", "v0 side_effects.archive.status 只允许 failed")
            error_summary = archive.get("error_summary")
            if error_summary is not None:
                require(isinstance(error_summary, str) and error_summary, "side_effects.archive.error_summary 存在时必须是非空字符串")


def validate_result_summary(name: str, data: object, expected_target: str) -> None:
    require(isinstance(data, dict), f"{name} 必须是 object")
    require(data.get("status") in {"succeeded", "failed", "skipped"}, f"{name}.status 非法")
    require(data.get("target") == expected_target, f"{name}.target 必须是 {expected_target}")
    reference = data.get("reference")
    if reference is not None:
        require(isinstance(reference, str) and reference, f"{name}.reference 存在时必须是非空字符串")
    error_summary = data.get("error_summary")
    if error_summary is not None:
        require(isinstance(error_summary, str) and error_summary, f"{name}.error_summary 存在时必须是非空字符串")


def validate_cross_fields(collect_result: dict, response: dict) -> None:
    report_date = collect_result["report_date"]
    has_lane_issue = any(lane["status"] != "ok" for lane in collect_result["lanes"])
    require(response["report_date"] == report_date, "response.report_date 必须与 collect result 一致")
    expected_run_key = f"{report_date}:daily-report"
    require(response["run_key"] == expected_run_key, "response.run_key 必须符合最小 run_key 规则")
    require(response["host"] == "hermes", "response.host 必须为 hermes")

    run_state = response["run_state"]
    verdict = response["verdict"]
    report_artifact = response["report_artifact"]
    publish_result = response["publish_result"]
    archive_result = response["archive_result"]

    require(run_state["run_key"] == response["run_key"], "run_state.run_key 必须与 response.run_key 一致")
    require(run_state["report_date"] == report_date, "run_state.report_date 必须与 report_date 一致")
    require(run_state["last_verdict"] == verdict["status"], "run_state.last_verdict 必须与 verdict.status 一致")
    require(run_state["has_report_artifact"] == (report_artifact is not None), "run_state.has_report_artifact 与 report_artifact 不一致")
    require(verdict["has_report"] == (report_artifact is not None), "verdict.has_report 与 report_artifact 不一致")
    require(run_state["publish_state"]["status"] == publish_result["status"], "publish_state.status 必须与 publish_result.status 一致")
    require(run_state["archive_state"]["status"] == archive_result["status"], "archive_state.status 必须与 archive_result.status 一致")

    useful_item_count = collect_result["summary"]["useful_item_count"]
    if useful_item_count >= 1:
        require(report_artifact is not None, "有可用内容时必须存在 report_artifact")
        require(verdict["status"] in {"normal", "degraded"}, "有可用内容时 verdict 只能是 normal 或 degraded")
        require(verdict["should_publish"] is True, "有可用内容时 should_publish 必须为 true")
        require(publish_result["status"] == "succeeded", "最小样例中有可用内容时 publish_result 必须成功")
    else:
        require(report_artifact is None, "无可用内容时 report_artifact 必须为 null")
        require(verdict["status"] == "blocked", "无可用内容时 verdict 必须为 blocked")
        require(verdict["should_publish"] is False, "blocked 时 should_publish 必须为 false")
        require(verdict["should_archive"] is False, "blocked 时 should_archive 必须为 false")
        require(publish_result["status"] == "skipped", "blocked 时 publish_result 必须是 skipped")
        require(archive_result["status"] == "skipped", "blocked 时 archive_result 必须是 skipped")

    if publish_result["status"] != "succeeded":
        require(archive_result["status"] == "skipped", "publish 未成功时 archive_result 必须是 skipped")

    if has_lane_issue and useful_item_count >= 1:
        require(verdict["status"] == "degraded", "存在 lane 异常但仍有内容时 verdict 必须为 degraded")
        require(verdict["should_notify_ops"] is True, "存在 lane 异常时 should_notify_ops 必须为 true")

    if archive_result["status"] == "failed":
        require(publish_result["status"] == "succeeded", "archive 失败前 publish_result 必须成功")
        require(verdict["status"] == "degraded", "archive 失败时 verdict 必须为 degraded")
        require(verdict["should_archive"] is True, "archive 失败时 should_archive 必须仍为 true")
        require(verdict["should_notify_ops"] is True, "archive 失败时 should_notify_ops 必须为 true")

    if verdict["status"] == "normal":
        require(publish_result["status"] == "succeeded", "normal 时 publish_result 必须成功")
        require(archive_result["status"] == "succeeded", "normal 时 archive_result 必须成功")
        require(verdict["should_notify_ops"] is False, "normal 时 should_notify_ops 必须为 false")

    if report_artifact is not None:
        require(report_artifact["report_date"] == report_date, "report_artifact.report_date 必须与 report_date 一致")
        require(report_artifact["useful_item_count"] == useful_item_count, "report_artifact.useful_item_count 必须与 collect summary 一致")


def validate_fixture_dir(fixture_dir: Path) -> None:
    collect_result = load_json(fixture_dir / "collect-result.json")
    response = load_json(fixture_dir / "expected-hermes-response.json")

    validate_collect_result(collect_result)
    validate_with_schema("hermes-run-response.schema.json", response)
    validate_with_schema("verdict.schema.json", response["verdict"])
    validate_with_schema("run-state.schema.json", response["run_state"])
    if response["report_artifact"] is not None:
        validate_with_schema("report-artifact.schema.json", response["report_artifact"])
    validate_result_summary("publish_result", response["publish_result"], "feishu")
    validate_result_summary("archive_result", response["archive_result"], "obsidian")
    validate_cross_fields(collect_result, response)


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: uv run python helpers/validate_contracts.py <fixture-dir>", file=sys.stderr)
        return 2

    fixture_dir = Path(sys.argv[1]).resolve()
    try:
        validate_fixture_dir(fixture_dir)
    except Exception as error:  # noqa: BLE001
        print(f"[validate_contracts] 失败: {error}", file=sys.stderr)
        return 1

    print(f"[validate_contracts] 通过: {fixture_dir.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
