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
REPORT_DATE = "2026-04-12"
SECTION_TITLE = FIXED_SECTION_TITLES["x-feed"]
SOURCE_URL = "https://x.com/example/status/1"


def build_report(body: str, *, prefix: str = "") -> str:
    return (
        f"{prefix}# AI Agent 日报（{REPORT_DATE}）\n\n"
        f"{body}\n\n"
        "## 来源\n\n"
        f"### {SECTION_TITLE}\n"
        f"- 示例 — {SOURCE_URL}\n"
    )


def validate_single_section_report(markdown: str) -> None:
    validate_report_markdown(
        markdown,
        report_date=REPORT_DATE,
        expected_section_titles=[SECTION_TITLE],
        expected_sources={SECTION_TITLE: [SOURCE_URL]},
    )


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
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_leading_content_before_title_start(self) -> None:
        bad_markdown = build_report(
            f"## {SECTION_TITLE}\n- 有效条目。[原帖]({SOURCE_URL})",
            prefix="\n",
        )
        with self.assertRaisesRegex(ValueError, "响应开头"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_status_text_between_title_and_first_section(self) -> None:
        bad_markdown = build_report(
            "生成状态：已完成\n\n"
            f"## {SECTION_TITLE}\n"
            f"- 有效条目。[原帖]({SOURCE_URL})"
        )
        with self.assertRaisesRegex(ValueError, "标题后必须直接进入第一个正文栏目"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_citation_wrappers(self) -> None:
        bad_bodies = [
            f"## {SECTION_TITLE}\n<citation>\n- 有效条目。[原帖]({SOURCE_URL})\n</citation>",
            f"## {SECTION_TITLE}\n```citation\n- 有效条目。[原帖]({SOURCE_URL})\n```",
        ]

        for body in bad_bodies:
            with self.subTest(body=body):
                with self.assertRaisesRegex(ValueError, "citation"):
                    validate_single_section_report(build_report(body))

    def test_validator_rejects_prose_only_body_section(self) -> None:
        bad_markdown = build_report(
            f"## {SECTION_TITLE}\n这是一整段正文摘要，但不是 bullet reader item。[原帖]({SOURCE_URL})"
        )
        with self.assertRaisesRegex(ValueError, "bullet"):
            validate_single_section_report(bad_markdown)

    def test_fixture_schema_is_minimal_json(self) -> None:
        case_path = FIXTURE_ROOT / "empty-section-omission.json"
        case_data = json.loads(case_path.read_text(encoding="utf-8"))
        self.assertIn("report_markdown", case_data)
        self.assertIn("expected_section_titles", case_data)
        self.assertIn("expected_sources", case_data)


if __name__ == "__main__":
    unittest.main()
