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

    def test_validator_rejects_placeholder_count_copy_in_body_line(self) -> None:
        bad_markdown = build_report(
            f"## {SECTION_TITLE}\n- 该栏目收录 32 条有用内容。[原帖]({SOURCE_URL})"
        )
        with self.assertRaisesRegex(ValueError, "占位统计"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_placeholder_tail_after_bold_title_prefix(self) -> None:
        bad_markdown = build_report(
            "## {section_title}\n"
            "- **【热帖】Got roasted for not open sourcing my agent OS (dashboard), so I did. Built the whole thing with Claude Code** "
            "该栏目收录 32 条有用内容。[原帖]({source_url})".format(
                section_title=SECTION_TITLE,
                source_url=SOURCE_URL,
            )
        )
        with self.assertRaisesRegex(ValueError, "占位统计"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_generic_source_fallback_in_body_line(self) -> None:
        bad_markdown = build_report(
            f"## {SECTION_TITLE}\n- 原文围绕 agent workflow 展开，具体变化见来源。[原帖]({SOURCE_URL})"
        )
        with self.assertRaisesRegex(ValueError, "兜底句"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_hn_generic_filler_after_title_prefix(self) -> None:
        bad_markdown = build_report(
            "## {section_title}\n"
            "- **「agent workflow」：Show HN: Busybee - a FIFO build queue for multi-agent dev workflows** "
            "搜索词「agent workflow」命中的这条 HN 讨论不是泛聊概念，而是在讲更具体的工程做法。"
            "[原帖]({source_url})".format(
                section_title=SECTION_TITLE,
                source_url=SOURCE_URL,
            )
        )
        with self.assertRaisesRegex(ValueError, "HN"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_generic_github_fallback_in_body_line(self) -> None:
        bad_markdown = build_report(
            f"## {SECTION_TITLE}\n- 项目说明主要在讲它的定位、工作流和使用场景。[GitHub]({SOURCE_URL})"
        )
        with self.assertRaisesRegex(ValueError, "GitHub/README"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_product_hunt_raw_english_tagline_leakage(self) -> None:
        bad_markdown = build_report(
            "## {section_title}\n"
            "- **PangeAI — Instant, agent-driven spatial analysis and decisio** "
            "`PangeAI` 这条 Product Hunt 记录里写到：`PangeAI` 的定位很直接："
            "Instant, agent-driven spatial analysis and decisio。[Product Hunt]({source_url})".format(
                section_title=SECTION_TITLE,
                source_url=SOURCE_URL,
            )
        )
        with self.assertRaisesRegex(ValueError, "Product Hunt"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_english_heavy_explanatory_leakage(self) -> None:
        bad_markdown = build_report(
            "## {section_title}\n"
            "- This post explains the agent orchestration workflow for tool routing and memory management in production."
            "[原帖]({source_url})".format(section_title=SECTION_TITLE, source_url=SOURCE_URL)
        )
        with self.assertRaisesRegex(ValueError, "英文解释泄漏"):
            validate_single_section_report(bad_markdown)

    def test_validator_rejects_hybrid_english_tail_after_chinese_prefix(self) -> None:
        bad_markdown = build_report(
            "## {section_title}\n"
            "- `[codex] Fix high severity dependency alerts (#18167)` 这次改动主要写明了"
            "Pin vulnerable npm dependencies through the existing root `resolutions` mechanism so the lockfile moves only to patched versions。"
            "[GitHub]({source_url})".format(section_title=SECTION_TITLE, source_url=SOURCE_URL)
        )
        with self.assertRaisesRegex(ValueError, "英文解释泄漏"):
            validate_single_section_report(bad_markdown)

    def test_validator_allows_mixed_language_technical_line_with_chinese_grounding(self) -> None:
        markdown = build_report(
            "## {section_title}\n"
            "- Codex CLI v1.2 新增 session replay 导出，命令是 `codex replay --latest`，并补了 tool routing trace。"
            "[Release]({source_url})".format(section_title=SECTION_TITLE, source_url=SOURCE_URL)
        )
        validate_single_section_report(markdown)

    def test_fixture_schema_is_minimal_json(self) -> None:
        case_path = FIXTURE_ROOT / "empty-section-omission.json"
        case_data = json.loads(case_path.read_text(encoding="utf-8"))
        self.assertIn("report_markdown", case_data)
        self.assertIn("expected_section_titles", case_data)
        self.assertIn("expected_sources", case_data)


if __name__ == "__main__":
    unittest.main()
