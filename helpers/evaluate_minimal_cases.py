import difflib
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.signals_adapter import build_report_artifact


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def get_archive_failure(collect_result: dict) -> dict | None:
    side_effects = collect_result.get("side_effects")
    if not isinstance(side_effects, dict):
        return None

    archive = side_effects.get("archive")
    if not isinstance(archive, dict):
        return None

    if archive.get("status") != "failed":
        return None

    return archive


def load_selected_items(case_dir: Path) -> dict | None:
    selected_items_path = case_dir / "selected-items.json"
    if not selected_items_path.is_file():
        return None
    selected_items = load_json(selected_items_path)
    require(isinstance(selected_items, dict), f"{selected_items_path.name} 必须是 object")
    return selected_items


def evaluate_case(collect_result: dict, selected_items: dict | None = None) -> dict:
    report_date = collect_result["report_date"]
    run_key = f"{report_date}:daily-report"
    useful_item_count = collect_result["summary"]["useful_item_count"]
    has_lane_issue = any(lane["status"] != "ok" for lane in collect_result["lanes"])
    archive_failure = get_archive_failure(collect_result)

    if useful_item_count == 0:
        verdict = {
            "status": "blocked",
            "reason_summary": "无可用内容，日报不成立",
            "has_report": False,
            "should_publish": False,
            "should_archive": False,
            "should_notify_ops": True,
        }
        report_artifact = None
        publish_result = {
            "status": "skipped",
            "target": "feishu",
            "reference": None,
            "error_summary": None,
        }
        archive_result = {
            "status": "skipped",
            "target": "obsidian",
            "reference": None,
            "error_summary": None,
        }
        publish_state = {
            "status": "skipped",
            "summary": "blocked before publish",
            "reference": None,
        }
        archive_state = {
            "status": "skipped",
            "summary": "publish not succeeded",
            "reference": None,
        }
    else:
        verdict_status = "degraded" if has_lane_issue or archive_failure is not None else "normal"
        reason_summary = "内容与交付链路完整"
        if has_lane_issue:
            reason_summary = "部分 lane 异常，但仍有可发布内容"
        elif archive_failure is not None:
            reason_summary = "归档失败，但日报已成功发布"
        verdict = {
            "status": verdict_status,
            "reason_summary": reason_summary,
            "has_report": True,
            "should_publish": True,
            "should_archive": True,
            "should_notify_ops": has_lane_issue or archive_failure is not None,
        }
        report_artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        publish_result = {
            "status": "succeeded",
            "target": "feishu",
            "reference": f"feishu://daily-report/{report_date}",
            "error_summary": None,
        }
        publish_state = {
            "status": "succeeded",
            "summary": "published to Feishu",
            "reference": publish_result["reference"],
        }
        if archive_failure is None:
            archive_result = {
                "status": "succeeded",
                "target": "obsidian",
                "reference": f"obsidian://daily-report/{report_date}.md",
                "error_summary": None,
            }
            archive_state = {
                "status": "succeeded",
                "summary": "archived to Obsidian",
                "reference": archive_result["reference"],
            }
        else:
            archive_result = {
                "status": "failed",
                "target": "obsidian",
                "reference": None,
                "error_summary": archive_failure.get("error_summary"),
            }
            archive_state = {
                "status": "failed",
                "summary": "archive to Obsidian failed",
                "reference": None,
            }

    return {
        "host": "hermes",
        "run_key": run_key,
        "report_date": report_date,
        "verdict": verdict,
        "run_state": {
            "run_key": run_key,
            "report_date": report_date,
            "trigger_kind": "cron",
            "status": "finished",
            "last_verdict": verdict["status"],
            "has_report_artifact": report_artifact is not None,
            "publish_state": publish_state,
            "archive_state": archive_state,
        },
        "report_artifact": report_artifact,
        "publish_result": publish_result,
        "archive_result": archive_result,
    }


def assert_reference_docs() -> None:
    runtime_contracts = (REPO_ROOT / "contracts" / "runtime-contracts.md").read_text(encoding="utf-8")
    failure_matrix = (REPO_ROOT / "contracts" / "failure-matrix.md").read_text(encoding="utf-8")
    required_runtime_phrases = [
        "只要至少有一条有用内容，日报就成立",
        "publish-report` 成功后才允许 `archive-report`",
    ]
    required_failure_phrases = [
        "部分 lane 异常但仍有内容",
        "无可用内容",
        "发布成功但归档失败",
    ]
    for phrase in required_runtime_phrases:
        require(phrase in runtime_contracts, f"runtime-contracts.md 缺少关键短语: {phrase}")
    for phrase in required_failure_phrases:
        require(phrase in failure_matrix, f"failure-matrix.md 缺少关键短语: {phrase}")


def compare_case(case_dir: Path) -> None:
    collect_result = load_json(case_dir / "collect-result.json")
    selected_items = load_selected_items(case_dir)
    expected = load_json(case_dir / "expected-hermes-response.json")
    actual = evaluate_case(collect_result, selected_items=selected_items)
    if actual != expected:
        expected_text = json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True)
        actual_text = json.dumps(actual, ensure_ascii=False, indent=2, sort_keys=True)
        diff = "\n".join(
            difflib.unified_diff(
                expected_text.splitlines(),
                actual_text.splitlines(),
                fromfile="expected",
                tofile="actual",
                lineterm="",
            )
        )
        raise ValueError(f"{case_dir.name} 结果不匹配\n{diff}")


def is_minimal_case_dir(path: Path) -> bool:
    return path.is_dir() and (path / "collect-result.json").is_file() and (path / "expected-hermes-response.json").is_file()


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: uv run python helpers/evaluate_minimal_cases.py <fixtures-dir>", file=sys.stderr)
        return 2

    fixtures_root = Path(sys.argv[1]).resolve()
    try:
        assert_reference_docs()
        case_dirs = sorted(path for path in fixtures_root.iterdir() if is_minimal_case_dir(path))
        require(case_dirs, "fixtures 目录下没有可评估的 case")
        for case_dir in case_dirs:
            compare_case(case_dir)
            print(f"[evaluate_minimal_cases] 通过: {case_dir.name}")
    except Exception as error:  # noqa: BLE001
        print(f"[evaluate_minimal_cases] 失败: {error}", file=sys.stderr)
        return 1

    print(f"[evaluate_minimal_cases] 共验证 {len(case_dirs)} 个最小场景")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
