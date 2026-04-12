import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.signals_adapter import (
    build_collect_result,
    build_report_artifact,
    build_selected_items,
    build_validation_bundle,
    validate_selected_items_object,
)
from helpers.validate_report_output_contract import FIXED_SECTION_TITLES, validate_report_markdown


FIXTURE_ROOT = Path(__file__).resolve().parent.parent / "fixtures" / "signals-adapter"
REPORT_DATE = "2026-04-12"


class SignalsAdapterTest(unittest.TestCase):
    def test_build_collect_result_maps_lane_statuses(self) -> None:
        collect_result = build_collect_result(
            signals_root=FIXTURE_ROOT,
            report_date=REPORT_DATE,
            lane_names=["x-feed", "product-hunt-watch", "broken-lane"],
        )

        self.assertEqual(collect_result["report_date"], REPORT_DATE)
        self.assertEqual(collect_result["source"], "signals-engine")
        self.assertEqual(
            collect_result["lanes"],
            [
                {"name": "x-feed", "status": "ok", "useful_item_count": 2},
                {"name": "product-hunt-watch", "status": "partial", "useful_item_count": 1},
                {"name": "broken-lane", "status": "error", "useful_item_count": 0},
            ],
        )
        self.assertEqual(
            collect_result["summary"],
            {"useful_item_count": 3, "partial_lane_count": 2},
        )
        self.assertTrue(any("product-hunt-watch: warnings=" in item for item in collect_result["errors"]))
        self.assertTrue(any("product-hunt-watch: 缺少 signal 文件" in item for item in collect_result["errors"]))
        self.assertTrue(any("broken-lane: 缺少目录" in item for item in collect_result["errors"]))

    def test_build_selected_items_extracts_minimal_fields(self) -> None:
        selected_items = build_selected_items(
            signals_root=FIXTURE_ROOT,
            report_date=REPORT_DATE,
            lane_names=["x-feed", "product-hunt-watch"],
            per_lane_limit=1,
        )

        self.assertEqual(selected_items["report_date"], REPORT_DATE)
        self.assertEqual(selected_items["source"], "signals-engine")
        self.assertEqual(selected_items["summary"]["selected_item_count"], 2)
        self.assertEqual(
            selected_items["summary"]["lane_counts"],
            [
                {"lane": "x-feed", "selected_item_count": 1},
                {"lane": "product-hunt-watch", "selected_item_count": 1},
            ],
        )

        feed_item = selected_items["selected_items"][0]
        self.assertEqual(feed_item["lane"], "x-feed")
        self.assertEqual(feed_item["title"], "@alpha #1")
        self.assertEqual(feed_item["source_url"], "https://x.com/alpha/status/1")
        self.assertEqual(feed_item["signal_path"], "x-feed/2026-04-12/signals/alpha.md")
        self.assertEqual(feed_item["fetched_at"], "2026-04-12T10:00:00+0000")
        self.assertIn("Alpha signal overview", feed_item["excerpt"])

        product_item = selected_items["selected_items"][1]
        self.assertEqual(product_item["lane"], "product-hunt-watch")
        self.assertEqual(product_item["title"], "Nicelydone MCP — Design context for AI agents")
        self.assertEqual(
            product_item["signal_path"],
            "product-hunt-watch/2026-04-12/signals/nicelydone-mcp.md",
        )
        self.assertEqual(product_item["excerpt"], "Design context for AI agents")

    def test_build_validation_bundle_checks_subset_consistency(self) -> None:
        collect_result = build_collect_result(
            signals_root=FIXTURE_ROOT,
            report_date=REPORT_DATE,
            lane_names=["x-feed", "product-hunt-watch"],
        )
        selected_items = build_selected_items(
            signals_root=FIXTURE_ROOT,
            report_date=REPORT_DATE,
            lane_names=["x-feed", "product-hunt-watch"],
            per_lane_limit=1,
        )

        bundle = build_validation_bundle(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(bundle["report_date"], REPORT_DATE)
        self.assertEqual(bundle["summary"]["collect_useful_item_count"], 3)
        self.assertEqual(bundle["summary"]["selected_item_count"], 2)
        self.assertTrue(bundle["summary"]["is_subset"])

    def test_validate_selected_items_accepts_zero_count_lane_counts(self) -> None:
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@example/status/1",
                    "source_url": "https://x.com/example/status/1",
                    "signal_path": "x-feed/2026-04-12/signals/example.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "excerpt": "社区开始把远程审计划工作流讲清楚。",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 1},
                    {"lane": "broken-lane", "selected_item_count": 0},
                ],
            },
        }

        validate_selected_items_object(selected_items)

    def test_validate_selected_items_rejects_duplicate_or_incorrect_lane_counts(self) -> None:
        base_selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@example/status/1",
                    "source_url": "https://x.com/example/status/1",
                    "signal_path": "x-feed/2026-04-12/signals/example.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "excerpt": "社区开始把远程审计划工作流讲清楚。",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [],
            },
        }

        cases = [
            (
                "duplicate lane",
                [
                    {"lane": "x-feed", "selected_item_count": 1},
                    {"lane": "x-feed", "selected_item_count": 0},
                ],
                "不允许重复",
            ),
            (
                "wrong count",
                [
                    {"lane": "x-feed", "selected_item_count": 0},
                ],
                "与 selected_items 条目不一致",
            ),
        ]
        for name, lane_counts, error_message in cases:
            with self.subTest(name=name):
                selected_items = json.loads(json.dumps(base_selected_items))
                selected_items["summary"]["lane_counts"] = lane_counts
                with self.assertRaisesRegex(ValueError, error_message):
                    validate_selected_items_object(selected_items)

    def test_build_report_artifact_accepts_live_selected_items_with_zero_count_lanes(self) -> None:
        collect_result = build_collect_result(
            signals_root=FIXTURE_ROOT,
            report_date=REPORT_DATE,
            lane_names=["x-feed", "product-hunt-watch", "broken-lane"],
        )
        selected_items = build_selected_items(
            signals_root=FIXTURE_ROOT,
            report_date=REPORT_DATE,
            lane_names=["x-feed", "product-hunt-watch", "broken-lane"],
            per_lane_limit=1,
        )

        self.assertIn(
            {"lane": "broken-lane", "selected_item_count": 0},
            selected_items["summary"]["lane_counts"],
        )

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(artifact["title"], "AI Agent 日报（2026-04-12）")
        self.assertEqual(artifact["source_lanes"], ["x-feed", "product-hunt-watch"])

    def test_build_report_artifact_renders_reader_facing_sections_and_sources(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 1},
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.101",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.101",
                    "signal_path": "claude-code-watch/2026-04-12/signals/release.md",
                    "fetched_at": "2026-04-12T10:00:00+0000",
                    "excerpt": "团队上手和远程协作能力继续补齐。",
                },
                {
                    "lane": "x-feed",
                    "title": "@example/status/1",
                    "source_url": "https://x.com/example/status/1",
                    "signal_path": "x-feed/2026-04-12/signals/example.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "excerpt": "社区开始把远程审计划工作流讲清楚。",
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "claude-code-watch", "selected_item_count": 1},
                    {"lane": "x-feed", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(artifact["title"], "AI Agent 日报（2026-04-12）")
        self.assertEqual(artifact["source_lanes"], ["x-feed", "claude-code-watch"])
        self.assertIn("# AI Agent 日报（2026-04-12）", artifact["body_markdown"])
        self.assertIn("## X 推荐流", artifact["body_markdown"])
        self.assertIn("## Claude Code", artifact["body_markdown"])
        self.assertNotIn("## x-feed", artifact["body_markdown"])
        self.assertIn("## 来源", artifact["body_markdown"])
        self.assertIn("### X 推荐流", artifact["body_markdown"])
        self.assertIn("### Claude Code", artifact["body_markdown"])

        validate_report_markdown(
            artifact["body_markdown"],
            report_date=REPORT_DATE,
            expected_section_titles=[
                FIXED_SECTION_TITLES["x-feed"],
                FIXED_SECTION_TITLES["claude-code-watch"],
            ],
            expected_sources={
                FIXED_SECTION_TITLES["x-feed"]: ["https://x.com/example/status/1"],
                FIXED_SECTION_TITLES["claude-code-watch"]: [
                    "https://github.com/anthropics/claude-code/releases/tag/v2.1.101"
                ],
            },
        )

    def test_build_report_artifact_deduplicates_same_url_within_section(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "reddit-watch", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "reddit-watch",
                    "title": "First mention",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/example/post/",
                    "signal_path": "reddit-watch/2026-04-12/signals/first.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "excerpt": "第一条摘要。",
                },
                {
                    "lane": "reddit-watch",
                    "title": "Second mention",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/example/post/",
                    "signal_path": "reddit-watch/2026-04-12/signals/second.md",
                    "fetched_at": "2026-04-12T10:00:00+0000",
                    "excerpt": "第二条摘要。",
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "reddit-watch", "selected_item_count": 2},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(
            artifact["body_markdown"].count("https://www.reddit.com/r/ClaudeAI/comments/example/post/"),
            3,
        )
        self.assertEqual(artifact["body_markdown"].count("### Reddit 社区"), 1)
        appendix = artifact["body_markdown"].split("## 来源", maxsplit=1)[1]
        self.assertEqual(appendix.count("https://www.reddit.com/r/ClaudeAI/comments/example/post/"), 1)

    def test_build_report_artifact_appendix_ignores_plain_urls_inside_titles(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "reddit-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "reddit-watch",
                    "title": "Thread recap https://example.com/thread and takeaways",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/example/post/",
                    "signal_path": "reddit-watch/2026-04-12/signals/thread.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "excerpt": "讨论把多代理协作里的 reviewer 角色拆清楚了。",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "reddit-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        appendix = artifact["body_markdown"].split("## 来源", maxsplit=1)[1]

        self.assertIn("### Reddit 社区", appendix)
        self.assertIn("- 来源 1：https://www.reddit.com/r/ClaudeAI/comments/example/post/", appendix)
        self.assertNotIn("https://example.com/thread", appendix)

        validate_report_markdown(
            artifact["body_markdown"],
            report_date=REPORT_DATE,
            expected_section_titles=[FIXED_SECTION_TITLES["reddit-watch"]],
            expected_sources={
                FIXED_SECTION_TITLES["reddit-watch"]: [
                    "https://www.reddit.com/r/ClaudeAI/comments/example/post/"
                ]
            },
        )

    def test_build_report_artifact_strips_inline_links_from_body_content(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "[AGENTS.md](http://AGENTS.md) 设计笔记 https://example.com/title",
                    "source_url": "https://x.com/example/status/1",
                    "signal_path": "x-feed/2026-04-12/signals/example.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "excerpt": "围绕 [claude.ai/code](http://claude.ai/code) 工作流整理了结论 https://example.com/details",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertIn("AGENTS.md", artifact["body_markdown"])
        self.assertIn("claude.ai/code", artifact["body_markdown"])
        self.assertNotIn("http://AGENTS.md", artifact["body_markdown"])
        self.assertNotIn("http://claude.ai/code", artifact["body_markdown"])
        self.assertNotIn("https://example.com/title", artifact["body_markdown"])
        self.assertNotIn("https://example.com/details", artifact["body_markdown"])

        validate_report_markdown(
            artifact["body_markdown"],
            report_date=REPORT_DATE,
            expected_section_titles=[FIXED_SECTION_TITLES["x-feed"]],
            expected_sources={
                FIXED_SECTION_TITLES["x-feed"]: ["https://x.com/example/status/1"]
            },
        )

    def test_build_report_artifact_falls_back_to_collect_result_when_selected_items_missing(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": 3, "partial_lane_count": 0},
        }

        artifact = build_report_artifact(collect_result=collect_result)

        self.assertEqual(artifact["source_lanes"], ["claude-code-watch", "product-hunt-watch"])
        self.assertIn("## Claude Code", artifact["body_markdown"])
        self.assertIn("## Product Hunt 新品", artifact["body_markdown"])
        self.assertIn("## 来源", artifact["body_markdown"])
        self.assertIn("https://github.com/example/claude-code-watch/2026-04-12", artifact["body_markdown"])
        self.assertIn("https://www.producthunt.com/posts/product-hunt-watch-2026-04-12", artifact["body_markdown"])

    def test_cli_scripts_run_from_repo_root(self) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as temp_dir:
            collect_output = Path(temp_dir) / "collect.json"
            selected_output = Path(temp_dir) / "selected.json"
            bundle_output = Path(temp_dir) / "bundle.json"

            collect_command = [
                sys.executable,
                "helpers/build_collect_result_from_signals.py",
                "--signals-root",
                str(FIXTURE_ROOT),
                "--report-date",
                REPORT_DATE,
                "--lanes",
                "x-feed",
                "product-hunt-watch",
                "--output",
                str(collect_output),
            ]
            selected_command = [
                sys.executable,
                "helpers/build_selected_items_from_signals.py",
                "--signals-root",
                str(FIXTURE_ROOT),
                "--report-date",
                REPORT_DATE,
                "--lanes",
                "x-feed",
                "product-hunt-watch",
                "--output",
                str(selected_output),
            ]
            bundle_command = [
                sys.executable,
                "helpers/build_validation_bundle.py",
                "--collect-result",
                str(collect_output),
                "--selected-items",
                str(selected_output),
                "--output",
                str(bundle_output),
            ]

            for command in [collect_command, selected_command, bundle_command]:
                completed = subprocess.run(
                    command,
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, msg=completed.stderr)

            bundle = json.loads(bundle_output.read_text(encoding="utf-8"))
            self.assertEqual(bundle["summary"]["collect_useful_item_count"], 3)


if __name__ == "__main__":
    unittest.main()
