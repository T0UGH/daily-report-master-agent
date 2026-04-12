from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.signals_adapter import DEFAULT_SIGNALS_ROOT, build_collect_result, build_selected_items
from helpers.validate_report_output_contract import (
    FIXED_SECTION_ORDER,
    FIXED_SECTION_TITLES,
    load_json,
    require,
    validate_report_markdown,
)


TITLE_TO_LANE = {title: lane for lane, title in FIXED_SECTION_TITLES.items()}


def validate_real_fixture(fixtures_root: Path) -> None:
    collect_snapshot = load_json(fixtures_root / "collect-result.json")
    expected_report = (fixtures_root / "expected-report.md").read_text(encoding="utf-8")
    expected_sources = load_json(fixtures_root / "expected-sources.json")

    require(collect_snapshot["report_date"] == "2026-04-12", "collect snapshot 必须锁定 2026-04-12")

    live_collect = build_collect_result(
        signals_root=DEFAULT_SIGNALS_ROOT,
        report_date="2026-04-12",
        lane_names=FIXED_SECTION_ORDER,
    )
    require(live_collect == collect_snapshot, "真实 signals 生成的 collect result 与 fixture snapshot 不一致")

    expected_section_titles = [
        FIXED_SECTION_TITLES[lane["name"]]
        for lane in collect_snapshot["lanes"]
        if lane["name"] in FIXED_SECTION_TITLES and lane["useful_item_count"] > 0
    ]
    require(
        list(expected_sources) == expected_section_titles,
        "expected-sources.json 必须与真实 collect snapshot 的非空栏目顺序一致",
    )

    selected_items = build_selected_items(
        signals_root=DEFAULT_SIGNALS_ROOT,
        report_date="2026-04-12",
        lane_names=FIXED_SECTION_ORDER,
    )
    live_urls_by_lane: dict[str, set[str]] = {}
    for item in selected_items["selected_items"]:
        live_urls_by_lane.setdefault(item["lane"], set()).add(item["source_url"])

    for section_title, urls in expected_sources.items():
        lane = TITLE_TO_LANE[section_title]
        live_urls = live_urls_by_lane.get(lane, set())
        for url in urls:
            require(url in live_urls, f"{section_title} 的来源 URL 不存在于真实 {lane} signals 中: {url}")

    validate_report_markdown(
        expected_report,
        report_date="2026-04-12",
        expected_section_titles=expected_section_titles,
        expected_sources=expected_sources,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "用法: uv run python helpers/evaluate_real_2026_04_12_output_contract.py <fixtures-dir>",
            file=sys.stderr,
        )
        return 2

    fixtures_root = Path(sys.argv[1]).resolve()
    try:
        validate_real_fixture(fixtures_root)
    except Exception as error:  # noqa: BLE001
        print(f"[evaluate_real_2026_04_12_output_contract] 失败: {error}", file=sys.stderr)
        return 1

    print("[evaluate_real_2026_04_12_output_contract] 通过: 2026-04-12 真实 signals 输出 contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
