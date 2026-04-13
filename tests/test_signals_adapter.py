import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.signals_adapter import (
    DEFAULT_LANE_ITEM_LIMITS,
    build_editor_copy,
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
    def write_signal_bundle(
        self,
        root: Path,
        *,
        lane: str,
        signal_text_by_name: dict[str, str],
    ) -> None:
        lane_dir = root / lane / REPORT_DATE
        signals_dir = lane_dir / "signals"
        signals_dir.mkdir(parents=True, exist_ok=True)

        signal_files: list[str] = []
        for filename, content in signal_text_by_name.items():
            (signals_dir / filename).write_text(content, encoding="utf-8")
            signal_files.append(f"signals/{filename}")

        (lane_dir / "index.md").write_text(f"# {lane}\n", encoding="utf-8")
        (lane_dir / "run.json").write_text(
            json.dumps(
                {
                    "status": "success",
                    "date": REPORT_DATE,
                    "summary": {"signals_written": len(signal_files)},
                    "artifacts": {
                        "index_file": "index.md",
                        "signal_files": signal_files,
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

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
        self.assertEqual(feed_item["source_snippet"], "Alpha signal overview for testing.")
        self.assertIn("Alpha signal overview", feed_item["excerpt"])

        product_item = selected_items["selected_items"][1]
        self.assertEqual(product_item["lane"], "product-hunt-watch")
        self.assertEqual(product_item["title"], "Nicelydone MCP — Design context for AI agents")
        self.assertEqual(
            product_item["signal_path"],
            "product-hunt-watch/2026-04-12/signals/nicelydone-mcp.md",
        )
        self.assertEqual(product_item["source_snippet"], "Design context for AI agents")
        self.assertEqual(product_item["excerpt"], "Design context for AI agents")

    def test_build_selected_items_adds_source_snippet_from_high_density_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="x-feed",
                signal_text_by_name={
                    "ultraplan.md": """---
type: feed-exposure
lane: x-feed
source: x
entity_type: author
entity_id: trq212
title: '@trq212 #14'
url: https://x.com/trq212/status/2042671370186973589
fetched_at: 2026-04-12T10:58:49+0000
created_at: '2026-04-12T10:58:00Z'
position: 14
---

## Post

Claude Code 新增 /ultraplan：先在网页上生成实施计划，读完可以继续改，再落到本地执行。

## Engagement

- Likes: 9810
- Retweets: 639
- Replies: 498
- Views: 1148694
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["x-feed"],
                per_lane_limit=1,
            )

        item = selected_items["selected_items"][0]
        self.assertIn("source_snippet", item)
        self.assertIn("/ultraplan", item["source_snippet"])
        self.assertIn("网页上生成实施计划", item["source_snippet"])
        self.assertIn("本地执行", item["source_snippet"])
        self.assertNotIn("Likes:", item["source_snippet"])
        self.assertNotIn("Retweets:", item["source_snippet"])

    def test_build_selected_items_preserves_folded_front_matter_titles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="reddit-watch",
                signal_text_by_name={
                    "thread.md": """---
type: reddit_thread
lane: reddit-watch
source: reddit
entity_type: thread
entity_id: folded-title
title: I replaced chaotic solo Claude coding with a simple 3-agent team (Architect
  + Builder + Reviewer) and markdown handoff
url: https://www.reddit.com/r/ClaudeAI/comments/example/folded/
fetched_at: 2026-04-12T10:58:49+0000
created_at: '2026-04-12T10:58:00Z'
---

## Post

After trying several setups, I settled on a simple architect-builder-reviewer loop with markdown handoff files.
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["reddit-watch"],
                per_lane_limit=1,
            )

        self.assertEqual(
            selected_items["selected_items"][0]["title"],
            "I replaced chaotic solo Claude coding with a simple 3-agent team (Architect + Builder + Reviewer) and markdown handoff",
        )

    def test_default_lane_item_limits_are_uniformly_ten(self) -> None:
        self.assertTrue(DEFAULT_LANE_ITEM_LIMITS)
        self.assertEqual(set(DEFAULT_LANE_ITEM_LIMITS.values()), {10})

    def test_build_selected_items_curates_noisy_x_lanes_into_reader_facing_subset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="x-feed",
                signal_text_by_name={
                    "relevant.md": """---
type: feed-exposure
lane: x-feed
source: x
entity_type: author
entity_id: trq212
title: '@trq212 #14'
url: https://x.com/trq212/status/2042671370186973589
fetched_at: 2026-04-12T10:58:49+0000
created_at: '2026-04-12T10:58:00Z'
position: 14
---

## Post

New in Claude Code: /ultraplan

Claude builds an implementation plan for you on the web. You can read it and edit it, then ship it locally.

## Engagement

- Likes: 9810
- Retweets: 639
- Replies: 498
- Views: 1148694
""",
                    "retweet.md": """---
type: feed-exposure
lane: x-feed
source: x
entity_type: author
entity_id: yyyole
title: '@yyyole #41'
url: https://x.com/yyyole/status/2042891440179884479
fetched_at: 2026-04-12T10:57:49+0000
created_at: '2026-04-12T10:57:00Z'
position: 41
---

## Post

RT @sven_ai: Claude Code workflow recap

## Engagement

- Likes: 0
- Retweets: 31
- Replies: 0
- Views: 0
""",
                    "irrelevant.md": """---
type: feed-exposure
lane: x-feed
source: x
entity_type: author
entity_id: elonmusk
title: '@elonmusk #6'
url: https://x.com/elonmusk/status/2042961026468188209
fetched_at: 2026-04-12T10:56:49+0000
created_at: '2026-04-12T10:56:00Z'
position: 6
---

## Post

Falcon has landed

## Engagement

- Likes: 313604
- Retweets: 21328
- Replies: 8262
- Views: 57833144
""",
                },
            )
            self.write_signal_bundle(
                signals_root,
                lane="x-following",
                signal_text_by_name={
                    "relevant.md": """---
type: post
lane: x-following
source: x
entity_type: author
entity_id: turingou
title: '@turingou'
url: https://x.com/turingou/status/2043276169613844889
fetched_at: 2026-04-12T10:58:59+0000
created_at: '2026-04-12T10:32:55Z'
group: uncategorized
---

## Post

今日 vibe 感想，在做产品测试时，我们往往采用 bdd 的方式来驱动大范围的 e2e 测试，不过这仍然是按照软件工程的方式来进行测试规划，在 harness 工程中有明显的人类断点，为什么不把 agent matrix 直接引进来。

## Engagement

- Likes: 15
- Retweets: 2
- Replies: 1
- Views: 1414

## Enrichment

- Group: uncategorized
- Tags:
""",
                    "irrelevant.md": """---
type: post
lane: x-following
source: x
entity_type: author
entity_id: twannl
title: '@twannl'
url: https://x.com/twannl/status/2043275651117895734
fetched_at: 2026-04-12T10:57:59+0000
created_at: '2026-04-12T10:31:55Z'
group: uncategorized
---

## Post

Experiencing the same App Store Connect analytics drop for my apps. Does anyone know what’s going on?

## Engagement

- Likes: 0
- Retweets: 0
- Replies: 1
- Views: 482

## Enrichment

- Group: uncategorized
- Tags:
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["x-feed", "x-following"],
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 3)
        self.assertEqual(
            selected_items["summary"]["lane_counts"],
            [
                {"lane": "x-feed", "selected_item_count": 2},
                {"lane": "x-following", "selected_item_count": 1},
            ],
        )
        self.assertEqual(
            [item["source_url"] for item in selected_items["selected_items"]],
            [
                "https://x.com/trq212/status/2042671370186973589",
                "https://x.com/yyyole/status/2042891440179884479",
                "https://x.com/turingou/status/2043276169613844889",
            ],
        )

    def test_build_selected_items_default_strategy_can_keep_two_distinct_high_signal_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="github-trending-weekly",
                signal_text_by_name={
                    "archon.md": """---
type: trending-weekly
lane: github-trending-weekly
source: github-trending
title: Archon
url: https://github.com/coleam00/Archon
fetched_at: 2026-04-12T11:10:00+0000
---

## Preview

The first open-source harness builder for AI coding. Make AI coding deterministic and repeatable.
""",
                    "agent-memory-mcp.md": """---
type: trending-weekly
lane: github-trending-weekly
source: github-trending
title: Agent Memory MCP
url: https://github.com/example/agent-memory-mcp
fetched_at: 2026-04-12T11:20:00+0000
---

## Preview

MCP workspace for AI coding agents. Keeps design context, task history, and review handoffs synchronized across sessions.
""",
                },
            )

            collect_result = build_collect_result(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["github-trending-weekly"],
            )
            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["github-trending-weekly"],
            )
            artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(
            selected_items["summary"]["lane_counts"],
            [{"lane": "github-trending-weekly", "selected_item_count": 2}],
        )
        self.assertEqual(selected_items["summary"]["selected_item_count"], 2)
        self.assertEqual(
            [item["source_url"] for item in selected_items["selected_items"]],
            [
                "https://github.com/example/agent-memory-mcp",
                "https://github.com/coleam00/Archon",
            ],
        )
        self.assertIn("## GitHub 趋势项目", artifact["body_markdown"])
        self.assertIn("https://github.com/example/agent-memory-mcp", artifact["body_markdown"])
        self.assertIn("https://github.com/coleam00/Archon", artifact["body_markdown"])
        appendix = artifact["body_markdown"].split("## 来源", maxsplit=1)[1]
        self.assertIn("- Agent Memory MCP — https://github.com/example/agent-memory-mcp", appendix)
        self.assertIn("- Archon — https://github.com/coleam00/Archon", appendix)

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

    def test_build_report_artifact_prefers_source_snippet_and_raw_title_over_editor_copy(self) -> None:
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
                    "title": "@trq212 #14",
                    "source_url": "https://x.com/trq212/status/2042671370186973589",
                    "signal_path": "x-feed/2026-04-12/signals/trq212.md",
                    "fetched_at": "2026-04-12T10:58:49+0000",
                    "source_snippet": "Claude Code 新增 /ultraplan：先在网页上生成实施计划，读完可以继续改，再落到本地执行。",
                    "excerpt": "短预览：/ultraplan 这条更新更清楚了。",
                    "editor_headline": "Claude Code 的 `/ultraplan` 正把“先出计划再执行”变成默认工作流。",
                    "editor_summary": "这条线索更清楚了，值得跟踪，也更像工作流了。",
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        for marker in [
            "Likes:",
            "Retweets:",
            "Replies:",
            "Views:",
            "Position in session",
            "Feed context",
            "Group:",
            "Tags:",
            "Community:",
            "Score:",
            "Matched query:",
        ]:
            self.assertNotIn(marker, body_markdown)

        self.assertIn("## X 推荐流", body_markdown)
        self.assertIn("**@trq212 #14**", body_markdown)
        self.assertIn("Claude Code 新增 /ultraplan：先在网页上生成实施计划，读完可以继续改，再落到本地执行。", body_markdown)
        self.assertNotIn("Claude Code 的 `/ultraplan` 正把", body_markdown)
        self.assertNotIn("更清楚了", body_markdown)
        self.assertNotIn("值得跟踪", body_markdown)
        self.assertNotIn("更像工作流了", body_markdown)

    def test_build_report_artifact_prefers_excerpt_before_editor_summary_when_source_snippet_missing(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "codex-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "codex-watch",
                    "title": "[codex] Support flattened deferred MCP tool calls",
                    "source_url": "https://github.com/openai/codex/pull/123",
                    "signal_path": "codex-watch/2026-04-12/signals/pr-123.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "excerpt": "这条 PR 补的是 flattened handler aliases 和 deferred MCP 工具调用路径。",
                    "editor_summary": "这次改动更清楚了，也更像工作流了。",
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "codex-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("flattened handler aliases 和 deferred MCP 工具调用路径", body_markdown)
        self.assertNotIn("这次改动更清楚了", body_markdown)
        self.assertNotIn("更像工作流了", body_markdown)

    def test_build_report_artifact_rewrites_truncated_english_x_snippet_into_reader_facing_chinese(self) -> None:
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
                    "title": "@techwith_ram #47",
                    "source_url": "https://x.com/techwith_ram/status/2043041504109957312",
                    "signal_path": "x-feed/2026-04-12/signals/techwith_ram.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "source_snippet": "Just finished reading this blog on agent harnesses. Man, it’s one of the clearest, most practical takes I’ve seen why th",
                    "excerpt": "Just finished reading this blog on agent harnesses. Man, it’s one of the clearest, most practical takes I’ve seen why th",
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("**@techwith_ram #47：", body_markdown)
        self.assertIn("agent harness", body_markdown)
        self.assertIn("博客", body_markdown)
        self.assertIn("清晰", body_markdown)
        self.assertNotIn("why th。", body_markdown)
        self.assertNotIn("Just finished reading this blog on agent harnesses.", body_markdown)

    def test_build_report_artifact_enhances_weak_x_title_without_editorializing(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-following", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-following",
                    "title": "@addyosmani",
                    "source_url": "https://x.com/addyosmani/status/2043399706634805682",
                    "signal_path": "x-following/2026-04-12/signals/addyosmani.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "source_snippet": "Want to give your agent quality checks? Chrome's DevTools MCP now includes: Performance checks via Lighthouse",
                    "excerpt": "Want to give your agent quality checks? Chrome's DevTools MCP now includes: Performance checks via Lighthouse",
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "x-following", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("**@addyosmani：", body_markdown)
        self.assertIn("DevTools MCP", body_markdown)
        self.assertIn("质量检查", body_markdown)
        self.assertNotIn("Want to give your agent quality checks?", body_markdown)

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
        self.assertIn(
            "- Thread recap and takeaways — https://www.reddit.com/r/ClaudeAI/comments/example/post/",
            appendix,
        )
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

    def test_build_report_artifact_appendix_keeps_distinct_sources_with_stable_order(self) -> None:
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
                    "title": "Swarm governance for Claude + Codex",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/example/swarm/",
                    "signal_path": "reddit-watch/2026-04-12/signals/swarm.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "excerpt": "第一条讨论把 coordinator 和 handoff 讲清楚了。",
                },
                {
                    "lane": "reddit-watch",
                    "title": "Architect Builder Reviewer handoff",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/example/review/",
                    "signal_path": "reddit-watch/2026-04-12/signals/review.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "excerpt": "第二条讨论更偏向角色拆分。",
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
        appendix = artifact["body_markdown"].split("## 来源", maxsplit=1)[1]
        lines = [line.strip() for line in appendix.splitlines() if line.strip().startswith("- ")]

        self.assertEqual(
            lines,
            [
                "- Swarm governance for Claude + Codex — https://www.reddit.com/r/ClaudeAI/comments/example/swarm/",
                "- Architect Builder Reviewer handoff — https://www.reddit.com/r/ClaudeAI/comments/example/review/",
            ],
        )

        validate_report_markdown(
            artifact["body_markdown"],
            report_date=REPORT_DATE,
            expected_section_titles=[FIXED_SECTION_TITLES["reddit-watch"]],
            expected_sources={
                FIXED_SECTION_TITLES["reddit-watch"]: [
                    "https://www.reddit.com/r/ClaudeAI/comments/example/swarm/",
                    "https://www.reddit.com/r/ClaudeAI/comments/example/review/",
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

    def test_build_editor_copy_uses_specific_reader_facing_fallbacks_for_live_like_cases(self) -> None:
        cases = [
            (
                "x-feed",
                "@agentops #3",
                "Claude Code teams are using review checklists to keep agent handoffs aligned.",
                {},
                "Claude Code",
                "review checklist",
            ),
            (
                "x-following",
                "@contextsmith",
                "Your AI coding agent has amnesia. Every new session means re-explaining your architecture, your constraints, and your decisions.",
                {},
                "失忆",
                "架构、约束、历史决定",
            ),
            (
                "reddit-watch",
                "I run a swarm of AI agents across Claude, Codex, and Gemini. Here's the governance",
                (
                    "Claude Code writes the feature. Codex reviews the PR for security. "
                    "Gemini validates the architecture while a coordinator agent tracks the changes."
                ),
                {},
                "治理",
                "Claude、Codex、Gemini",
            ),
            (
                "claude-code-watch",
                "v2.1.102",
                "Added worktree cleanup diagnostics and improved MCP reconnect for managed sessions.",
                {},
                "v2.1.102",
                "worktree cleanup diagnostics",
            ),
            (
                "codex-watch",
                "[codex] Support flattened deferred MCP tool calls",
                "register flattened handler aliases for deferred MCP tools and cover the node_repl path",
                {},
                "MCP",
                "调用路径",
            ),
            (
                "openclaw-watch",
                "openclaw 2026.4.12",
                "Adds structured chat bubbles, plugin activation descriptors, and typed providerOptions for video tools.",
                {},
                "2026.4.12",
                "structured chat bubbles",
            ),
            (
                "github-trending-weekly",
                "Archon",
                "The first open-source harness builder for AI coding. Make AI coding deterministic and repeatable.",
                {},
                "harness",
                "可重复",
            ),
            (
                "product-hunt-watch",
                "ContextVault — Shared memory for coding agents",
                "Persistent project memory and design context for AI coding agents.",
                {},
                "上下文",
                "design context",
            ),
            (
                "polymarket-watch",
                "Will OpenAI ship MCP-native agents by May 2026?",
                "Question about whether OpenAI ships MCP-native agents by May 2026.",
                {
                    "primary_probability": "0.68",
                    "primary_outcome": "Yes",
                    "event_title": "Will OpenAI ship MCP-native agents by May 2026?",
                },
                "Yes",
                "68.0%",
            ),
        ]

        for lane_name, title, excerpt, front_matter, headline_marker, detail_marker in cases:
            with self.subTest(lane_name=lane_name):
                headline, detail = build_editor_copy(
                    lane_name=lane_name,
                    title=title,
                    excerpt=excerpt,
                    front_matter=front_matter,
                )

                self.assertIn(headline_marker, headline)
                self.assertIn(detail_marker, detail)
                self.assertNotIn("原始信号围绕", detail)
                self.assertNotIn("原始更新围绕", detail)
                self.assertNotIn("这里只保留对读者有用的中文结论", detail)
                self.assertNotIn("不直接转贴整段原文", detail)

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
