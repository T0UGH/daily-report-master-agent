import json
import unittest
from pathlib import Path

from helpers.validate_report_output_contract import (
    FIXED_SECTION_TITLES,
    load_json,
    validate_fixture_case,
    validate_report_markdown,
)


FIXTURE_ROOT = Path(__file__).resolve().parent.parent / "fixtures" / "report-output-contract"


class ReportOutputContractTest(unittest.TestCase):
    def test_empty_section_omission_fixture_passes(self) -> None:
        case_path = FIXTURE_ROOT / "empty-section-omission.json"
        case_data = load_json(case_path)
        validate_fixture_case(case_path, case_data)

    def test_duplicate_url_same_section_fixture_passes(self) -> None:
        case_path = FIXTURE_ROOT / "duplicate-url-same-section.json"
        case_data = load_json(case_path)
        validate_fixture_case(case_path, case_data)

    def test_validator_rejects_legacy_sections(self) -> None:
        bad_markdown = """# AI Agent 日报（2026-04-12）

## 今日要点

- 旧结构

## 来源

### X 推荐流
- 示例 — https://x.com/example/status/1
"""
        with self.assertRaisesRegex(ValueError, "今日要点"):
            validate_report_markdown(
                bad_markdown,
                report_date="2026-04-12",
                expected_section_titles=[FIXED_SECTION_TITLES["x-feed"]],
                expected_sources={FIXED_SECTION_TITLES["x-feed"]: ["https://x.com/example/status/1"]},
            )

    def test_fixture_schema_is_minimal_json(self) -> None:
        case_path = FIXTURE_ROOT / "empty-section-omission.json"
        case_data = json.loads(case_path.read_text(encoding="utf-8"))
        self.assertIn("report_markdown", case_data)
        self.assertIn("expected_section_titles", case_data)
        self.assertIn("expected_sources", case_data)


if __name__ == "__main__":
    unittest.main()
