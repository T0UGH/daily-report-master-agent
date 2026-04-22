import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers.signals_adapter import (
    DEFAULT_LANE_ITEM_LIMITS,
    build_claude_code_release_detail,
    build_codex_detail,
    build_collect_result,
    build_editor_copy,
    build_hacker_news_detail,
    build_polymarket_detail,
    build_product_hunt_detail,
    build_reddit_detail,
    build_report_artifact,
    build_selected_items,
    build_validation_bundle,
    build_x_post_detail,
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

    def write_selected_items_artifact(self, runtime_root: Path, *, report_date: str, items: list[dict[str, object]]) -> Path:
        artifact_path = runtime_root / report_date / "selected-items.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            json.dumps(
                {
                    "report_date": report_date,
                    "source": "signals-engine",
                    "selected_items": items,
                    "summary": {
                        "selected_item_count": len(items),
                        "lane_counts": [],
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return artifact_path

    def build_reddit_signal_text(
        self,
        *,
        post_id: str,
        slug: str,
        score: int,
        comments: int,
        title: str,
        post_text: str,
    ) -> str:
        return f"""---
type: reddit_thread
lane: reddit-watch
source: reddit
entity_type: thread
entity_id: {post_id}
title: {title}
url: https://www.reddit.com/r/ClaudeAI/comments/{post_id}/{slug}/
fetched_at: {REPORT_DATE}T10:58:49+0000
created_at: '{REPORT_DATE}T10:58:00Z'
post_id: {post_id}
---

## Post

{post_text}

## Thread Context

- Score: {score}
- Comments: {comments}
"""

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
        self.assertEqual(selected_items["summary"]["selected_item_count"], 1)
        self.assertEqual(
            selected_items["summary"]["lane_counts"],
            [
                {"lane": "x-feed", "selected_item_count": 0},
                {"lane": "product-hunt-watch", "selected_item_count": 1},
            ],
        )

        product_item = selected_items["selected_items"][0]
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

    def test_build_selected_items_combines_product_and_market_sections_into_source_snippet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="product-hunt-watch",
                signal_text_by_name={
                    "nicelydone.md": """---
type: producthunt_topic_hit
lane: product-hunt-watch
source: producthunt
entity_type: product
entity_id: nicelydone-mcp
title: Nicelydone MCP — Design context for AI agents
url: https://www.producthunt.com/products/nicely-done
fetched_at: 2026-04-12T10:58:49+0000
created_at: '2026-04-12T10:58:00Z'
---

## Preview

Design context for AI agents

## Snapshot

- **Votes**: 316
- **Comments**: 4
- **Topic**: Artificial Intelligence
""",
                },
            )
            self.write_signal_bundle(
                signals_root,
                lane="polymarket-watch",
                signal_text_by_name={
                    "benchmark.md": """---
type: prediction_market
lane: polymarket-watch
source: polymarket
entity_type: event
entity_id: '79080'
title: AI model scores ≥ 90% on FrontierMath Benchmark before 2027?
url: https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027
fetched_at: 2026-04-12T10:58:49+0000
created_at: '2026-04-12T10:58:00Z'
---

## Expectation

- Question: AI model scores ≥ 90% on FrontierMath Benchmark before 2027?
- Current leader: No (82.0%)

## Outcome Probabilities

- No: 82.0%
- Yes: 18.0%

## Market Strength

- 24h volume: 13,577.3
- Liquidity: 6,870.6
- Price movement: down 6.5% today
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["product-hunt-watch", "polymarket-watch"],
                per_lane_limit=1,
            )

        product_item = selected_items["selected_items"][0]
        self.assertIn("Design context for AI agents", product_item["source_snippet"])
        self.assertIn("Votes", product_item["source_snippet"])
        self.assertIn("Artificial Intelligence", product_item["source_snippet"])

        market_item = selected_items["selected_items"][1]
        self.assertIn("Current leader: No (82.0%)", market_item["source_snippet"])
        self.assertIn("No: 82.0%", market_item["source_snippet"])
        self.assertIn("24h volume: 13,577.3", market_item["source_snippet"])
        self.assertIn("Liquidity: 6,870.6", market_item["source_snippet"])

    def test_build_selected_items_dense_claude_release_source_snippet_keeps_more_release_points(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="claude-code-watch",
                signal_text_by_name={
                    "release.md": """---
type: release
lane: claude-code-watch
source: github
entity_type: repo
entity_id: anthropics/claude-code
title: v2.1.105
url: https://github.com/anthropics/claude-code/releases/tag/v2.1.105
fetched_at: 2026-04-14T15:37:24+0000
created_at: '2026-04-13T21:53:13Z'
---

## Release Notes

## What's changed

- Added `path` parameter to the `EnterWorktree` tool to switch into an existing worktree of the current repository
- Added PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning `{"decision":"block"}`
- Added background monitor support for plugins via a top-level `monitors` manifest key that auto-arms at session start or on skill invoke
- `/proactive` is now an alias for `/loop`
- Improved stalled API stream handling: streams now abort after 5 minutes of no data and retry non-streaming instead of hanging indefinitely
- Improved network error messages: connection errors now show a retry message immediately instead of a silent spinner
- Improved file write display: long single-line writes (e.g. minified JSON) are now truncated in the UI instead of paginating across many screens
- Improved `/doctor` layout with status icons; press `f` to have Claude fix reported issues
- Improved `/config` labels and descriptions for clarity
- Improved skill description handling: raised the listing cap from 250 to 1,536 characters and added a startup warning when descriptions are truncated
- Improved `WebFetch` to strip `<style>` and `<script>` contents from fetched pages so CSS-heavy pages no longer exhaust the content budget before reaching actual text
- Improved stale agent worktree cleanup to remove worktrees whose PR was squash-merged instead of keeping them indefinitely
- Fixed images attached to queued messages (sent while Claude is working) being dropped
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["claude-code-watch"],
                per_lane_limit=1,
            )

        item = selected_items["selected_items"][0]
        self.assertIn("Improved network error messages", item["source_snippet"])
        self.assertIn("Improved `/doctor` layout", item["source_snippet"])
        self.assertIn("Improved `WebFetch`", item["source_snippet"])
        self.assertIn("queued messages", item["source_snippet"])

    def test_build_selected_items_dense_openclaw_release_source_snippet_includes_changes_and_fixes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="openclaw-watch",
                signal_text_by_name={
                    "release.md": """---
type: release
lane: openclaw-watch
source: github
entity_type: repo
entity_id: openclaw/openclaw
title: openclaw 2026.4.14
url: https://github.com/openclaw/openclaw/releases/tag/v2026.4.14
fetched_at: 2026-04-14T15:38:55+0000
created_at: '2026-04-14T13:03:29Z'
---

## Release Notes

OpenClaw `2026.4.14` is another broad quality release focused on model provider with explicit turn improvements for GPT-5 family and channel provider issues. Additionally we improved overal performance with refactors to our underlying core codebase.

## Changes

- OpenAI Codex/models: add forward-compat support for `gpt-5.4-pro`, including Codex pricing/limits and list/status visibility before the upstream catalog catches up. (#66453)
- Telegram/forum topics: surface human topic names in agent context, prompt metadata, and plugin hook metadata by learning names from Telegram forum service messages. (#65973)
- Agents/Ollama: forward the configured embedded-run timeout into the global undici stream timeout tuning so slow local Ollama runs no longer inherit the default stream cutoff instead of the operator-set run timeout. (#63175)

## Fixes

- Models/Codex: include `apiKey` in the codex provider catalog output so the Pi ModelRegistry validator no longer rejects the entry and silently drops all custom models from every provider in `models.json`. (#66180)
- Tools/image+pdf: normalize configured provider/model refs before media-tool registry lookup so image and PDF tool runs stop rejecting valid Ollama vision models as unknown just because the tool path skipped the usual model-ref normalization step. (#59943)
- Slack/interactions: apply the configured global `allowFrom` owner allowlist to channel block-action and modal interactive events, require an expected sender id for cross-verification, and reject ambiguous channel types so interactive triggers can no longer bypass the documented allowlist intent. (#66028)
- Heartbeat/security: force owner downgrade for untrusted `hook:wake` system events [AI-assisted]. (#66031)
- Browser/security: enforce SSRF policy on snapshot, screenshot, and tab routes [AI]. (#66040)
- Microsoft Teams/security: enforce sender allowlist checks on SSO signin invokes [AI]. (#66033)
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["openclaw-watch"],
                per_lane_limit=1,
            )

        item = selected_items["selected_items"][0]
        self.assertIn("gpt-5.4-pro", item["source_snippet"])
        self.assertIn("Telegram/forum topics", item["source_snippet"])
        self.assertIn("`apiKey`", item["source_snippet"])
        self.assertTrue(
            "hook:wake" in item["source_snippet"]
            or "SSRF" in item["source_snippet"]
            or "sender allowlist" in item["source_snippet"]
        )

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

    def test_build_selected_items_reddit_previous_day_selections_are_skipped_and_fill_with_remaining_candidates(
        self,
    ) -> None:
        previous_report_date = "2026-04-11"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            signals_root = temp_root / "signals"
            runtime_root = temp_root / "runtime"
            self.write_signal_bundle(
                signals_root,
                lane="reddit-watch",
                signal_text_by_name={
                    f"r__ClaudeAI__aaa111__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="aaa111",
                        slug="yesterday-url",
                        score=900,
                        comments=150,
                        title="Yesterday URL duplicate",
                        post_text="Claude Code architect builder reviewer markdown handoff workflow.",
                    ),
                    f"r__ClaudeAI__bbb222__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="bbb222",
                        slug="yesterday-id",
                        score=880,
                        comments=140,
                        title="Yesterday ID duplicate",
                        post_text="Codex OpenAI agent matrix harness testing BDD E2E.",
                    ),
                    f"r__ClaudeAI__ccc333__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="ccc333",
                        slug="fresh-third",
                        score=860,
                        comments=130,
                        title="Fresh third candidate",
                        post_text="Anthropic MCP design context workflow for shared memory.",
                    ),
                    f"r__ClaudeAI__ddd444__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="ddd444",
                        slug="fresh-fourth",
                        score=840,
                        comments=120,
                        title="Fresh fourth candidate",
                        post_text="Gemini Plan -> Build -> Review loop with testing and coding AI notes.",
                    ),
                },
            )
            self.write_selected_items_artifact(
                runtime_root,
                report_date=previous_report_date,
                items=[
                    {
                        "lane": "reddit-watch",
                        "title": "Yesterday URL duplicate",
                        "source_url": "https://www.reddit.com/r/ClaudeAI/comments/aaa111/yesterday-url/",
                        "signal_path": f"reddit-watch/{previous_report_date}/signals/yesterday-url.md",
                        "fetched_at": f"{previous_report_date}T10:58:49+0000",
                        "excerpt": "Already selected yesterday.",
                    },
                    {
                        "lane": "reddit-watch",
                        "title": "Yesterday ID duplicate",
                        "source_url": "",
                        "signal_path": (
                            f"reddit-watch/{previous_report_date}/signals/"
                            f"r__ClaudeAI__bbb222__reddit_thread__{previous_report_date}.md"
                        ),
                        "fetched_at": f"{previous_report_date}T10:58:49+0000",
                        "excerpt": "Already selected yesterday.",
                    },
                ],
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["reddit-watch"],
                per_lane_limit=2,
                previous_selected_items_runtime_root=runtime_root,
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 2)
        self.assertCountEqual(
            [item["source_url"] for item in selected_items["selected_items"]],
            [
                "https://www.reddit.com/r/ClaudeAI/comments/ccc333/fresh-third/",
                "https://www.reddit.com/r/ClaudeAI/comments/ddd444/fresh-fourth/",
            ],
        )

    def test_build_selected_items_reddit_missing_previous_day_artifact_falls_back_without_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            signals_root = temp_root / "signals"
            runtime_root = temp_root / "runtime"
            self.write_signal_bundle(
                signals_root,
                lane="reddit-watch",
                signal_text_by_name={
                    f"r__ClaudeAI__aaa111__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="aaa111",
                        slug="top-first",
                        score=900,
                        comments=150,
                        title="Top first candidate",
                        post_text="Claude Code architect builder reviewer markdown handoff workflow.",
                    ),
                    f"r__ClaudeAI__bbb222__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="bbb222",
                        slug="top-second",
                        score=880,
                        comments=140,
                        title="Top second candidate",
                        post_text="Anthropic MCP design context workflow for shared memory.",
                    ),
                    f"r__ClaudeAI__ccc333__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="ccc333",
                        slug="top-third",
                        score=860,
                        comments=130,
                        title="Top third candidate",
                        post_text="Gemini Plan -> Build -> Review loop with testing and coding AI notes.",
                    ),
                },
            )

            baseline_selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["reddit-watch"],
                per_lane_limit=2,
                previous_selected_items_path=temp_root / "baseline-missing" / "selected-items.json",
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["reddit-watch"],
                per_lane_limit=2,
                previous_selected_items_runtime_root=runtime_root,
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 2)
        self.assertEqual(
            [item["source_url"] for item in selected_items["selected_items"]],
            [item["source_url"] for item in baseline_selected_items["selected_items"]],
        )

    def test_build_selected_items_dedupes_non_reddit_lanes_by_previous_day_source_url(self) -> None:
        previous_report_date = "2026-04-11"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            signals_root = temp_root / "signals"
            runtime_root = temp_root / "runtime"
            self.write_signal_bundle(
                signals_root,
                lane="product-hunt-watch",
                signal_text_by_name={
                    "nicelydone.md": """---
type: producthunt_topic_hit
lane: product-hunt-watch
source: producthunt
entity_type: product
entity_id: nicelydone-mcp
title: Nicelydone MCP — Design context for AI agents
url: https://www.producthunt.com/products/nicely-done
fetched_at: 2026-04-12T10:58:49+0000
created_at: '2026-04-12T10:58:00Z'
---

## Preview

Design context for AI agents

## Snapshot

- **Votes**: 316
- **Comments**: 4
- **Topic**: Artificial Intelligence
""",
                },
            )
            self.write_selected_items_artifact(
                runtime_root,
                report_date=previous_report_date,
                items=[
                    {
                        "lane": "product-hunt-watch",
                        "title": "Nicelydone MCP — Design context for AI agents",
                        "source_url": "https://www.producthunt.com/products/nicely-done",
                        "signal_path": f"product-hunt-watch/{previous_report_date}/signals/nicelydone.md",
                        "fetched_at": f"{previous_report_date}T10:58:49+0000",
                        "excerpt": "Already selected yesterday.",
                    },
                ],
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["product-hunt-watch"],
                per_lane_limit=1,
                previous_selected_items_runtime_root=runtime_root,
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 0)
        self.assertEqual(selected_items["selected_items"], [])

    def test_build_selected_items_drops_noisy_x_candidates_when_only_generic_placeholder_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir) / "signals"
            self.write_signal_bundle(
                signals_root,
                lane="x-following",
                signal_text_by_name={
                    "generic.md": """---
type: post
lane: x-following
source: x
entity_type: author
entity_id: simonw
title: '@simonw'
url: https://x.com/simonw/status/1
fetched_at: 2026-04-12T10:57:59+0000
created_at: '2026-04-12T10:31:55Z'
group: uncategorized
---

## Post

People keep bringing up Gemini in coding discussions this week without sharing a concrete change.

## Engagement

- Likes: 8
- Retweets: 1
- Replies: 1
- Views: 482
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["x-following"],
                per_lane_limit=5,
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 0)
        self.assertEqual(selected_items["selected_items"], [])

    def test_build_selected_items_keeps_openclaw_with_release_facts(self) -> None:
        """OpenClaw 2026.4.15 release info now generates proper Chinese facts - should be kept."""
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir) / "signals"
            self.write_signal_bundle(
                signals_root,
                lane="x-feed",
                signal_text_by_name={
                    "openclaw.md": """---
type: feed-exposure
lane: x-feed
source: x
entity_type: author
entity_id: openclaw
title: '@openclaw #39'
url: https://x.com/openclaw/status/2044919054402752638
fetched_at: 2026-04-17T01:11:42+0000
created_at: '2026-04-16T23:21:09Z'
position: 39
---

## Post

OpenClaw 2026.4.15 🦞

🤖 Anthropic Opus 4.7 support
🗣️ Gemini TTS in bundled
🧠 Slimmer context + bounded memory reads
🔧 C

## Engagement

- Likes: 633
- Retweets: 52
- Replies: 51
- Views: 32197
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["x-feed"],
                per_lane_limit=5,
            )

        # openclaw now generates Chinese facts - should be kept
        self.assertEqual(selected_items["summary"]["selected_item_count"], 1)
        self.assertEqual(len(selected_items["selected_items"]), 1)
        self.assertIn("openclaw/status/2044919054402752638", selected_items["selected_items"][0]["source_url"])

    def test_build_selected_items_drops_real_bad_noisy_x_entries_when_only_hollow_template_or_english_fragment_remain(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir) / "signals"
            self.write_signal_bundle(
                signals_root,
                lane="x-feed",
                signal_text_by_name={
                    "bad-fragment.md": """---
type: feed-exposure
lane: x-feed
source: x
entity_type: author
entity_id: _catwu
title: '@_catwu #64'
url: https://x.com/_catwu/status/2044808533905178822
fetched_at: 2026-04-17T01:11:42+0000
created_at: '2026-04-16T16:01:59Z'
position: 64
---

## Post

Opus 4.7 is live in Claude Code today!

The model performs best if you treat it like an engineer you're delegating to,

## Engagement

- Likes: 810
- Retweets: 63
- Replies: 37
- Views: 54447
""",
                    "good.md": """---
type: feed-exposure
lane: x-feed
source: x
entity_type: author
entity_id: theo
title: '@theo #75'
url: https://x.com/theo/status/2043611205856837680
fetched_at: 2026-04-17T01:11:42+0000
created_at: '2026-04-16T05:06:43Z'
position: 75
---

## Post

Agent harnesses aren't the black magic many of y'all seem to think they are.
To prove it, I built one.

## Engagement

- Likes: 900
- Retweets: 60
- Replies: 40
- Views: 50000
""",
                },
            )
            self.write_signal_bundle(
                signals_root,
                lane="x-following",
                signal_text_by_name={
                    "bad-clicks.md": """---
type: post
lane: x-following
source: x
entity_type: author
entity_id: NickADobos
title: '@NickADobos'
url: https://x.com/NickADobos/status/2044885440092877028
fetched_at: 2026-04-17T01:11:47+0000
created_at: '2026-04-16T21:07:35Z'
position: 64
group: uncategorized
---

## Post

With codex computer use + mac's iPhone Mirror app, GPT can use any app on your phone!!!

Seems less accurate with clicks

## Engagement

- Likes: 305
- Retweets: 18
- Replies: 17
- Views: 33020
""",
                    "good-quality-checks.md": """---
type: post
lane: x-following
source: x
entity_type: author
entity_id: addyosmani
title: '@addyosmani'
url: https://x.com/addyosmani/status/2043728421160101881
fetched_at: 2026-04-17T01:11:47+0000
created_at: '2026-04-16T06:00:00Z'
position: 12
group: uncategorized
---

## Post

Want to give your agent quality checks? Chrome's DevTools MCP now includes: Performance checks via Lighthouse.

## Engagement

- Likes: 210
- Retweets: 30
- Replies: 8
- Views: 41000
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["x-feed", "x-following"],
                per_lane_limit=5,
            )

        selected_urls = {item["source_url"] for item in selected_items["selected_items"]}
        # _catwu and NickADobos now generate proper Chinese facts - should be kept
        self.assertIn("https://x.com/_catwu/status/2044808533905178822", selected_urls)
        self.assertIn("https://x.com/NickADobos/status/2044885440092877028", selected_urls)
        self.assertIn("https://x.com/theo/status/2043611205856837680", selected_urls)
        self.assertIn("https://x.com/addyosmani/status/2043728421160101881", selected_urls)

    def test_build_selected_items_reddit_dual_pool_mixes_heat_and_voice_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="reddit-watch",
                signal_text_by_name={
                    f"r__ClaudeAI__aaa111__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="aaa111",
                        slug="thinking-depth",
                        score=1910,
                        comments=283,
                        title="Anthropic stayed quiet until someone showed Claude's thinking depth dropped",
                        post_text=(
                            "Claude Code benchmark discussion about Anthropic, release notes, "
                            "agent workflow reliability, and Claude reasoning depth."
                        ),
                    ),
                    f"r__ClaudeAI__bbb222__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="bbb222",
                        slug="ultraplan",
                        score=609,
                        comments=197,
                        title="Claude Code v2.1.92 introduces Ultraplan — draft plans in the cloud",
                        post_text=(
                            "Claude Code ultraplan release discussion covering cloud review, hooks, "
                            "workflow changes, and launch reactions."
                        ),
                    ),
                    f"r__ClaudeAI__ccc333__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="ccc333",
                        slug="large-repo-question",
                        score=516,
                        comments=90,
                        title="How do you actually use Claude Code on a large repo without losing context?",
                        post_text=(
                            "I keep hitting context loss on a large repo. What's your Claude Code setup, "
                            "workflow, handoff pattern, and practical review loop?"
                        ),
                    ),
                    f"r__ClaudeAI__ddd444__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="ddd444",
                        slug="switch-mcps-to-clis",
                        score=648,
                        comments=80,
                        title="I switched from MCPs to CLIs for Claude Code and honestly never going back",
                        post_text=(
                            "I changed my Claude Code setup to use CLI wrappers instead of MCPs. "
                            "The workflow is simpler and easier to debug."
                        ),
                    ),
                    f"r__ClaudeAI__eee555__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="eee555",
                        slug="workflows",
                        score=449,
                        comments=45,
                        title="Most used Claude Code development workflows",
                        post_text=(
                            "A roundup of Claude Code workflow patterns, repo setup choices, and "
                            "agent coordination tips."
                        ),
                    ),
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["reddit-watch"],
                per_lane_limit=4,
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 4)
        buckets = {item.get("selection_bucket") for item in selected_items["selected_items"]}
        self.assertIn("heat", buckets)
        self.assertIn("voice", buckets)
        titles = [item["title"] for item in selected_items["selected_items"]]
        self.assertIn("Anthropic stayed quiet until someone showed Claude's thinking depth dropped", titles)
        self.assertTrue(
            any(
                title in titles
                for title in [
                    "How do you actually use Claude Code on a large repo without losing context?",
                    "I switched from MCPs to CLIs for Claude Code and honestly never going back",
                ]
            )
        )

    def test_build_selected_items_reddit_dual_pool_fills_when_voice_pool_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="reddit-watch",
                signal_text_by_name={
                    f"r__ClaudeAI__aaa111__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="aaa111",
                        slug="release-notes",
                        score=900,
                        comments=150,
                        title="Claude Code release notes: ultraplan, hooks, and cloud review",
                        post_text=(
                            "Claude Code release coverage with ultraplan, hooks, cloud review, "
                            "and workflow changes."
                        ),
                    ),
                    f"r__ClaudeAI__bbb222__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="bbb222",
                        slug="app-store",
                        score=870,
                        comments=140,
                        title="Claude Code can now submit your app to App Store Connect",
                        post_text=(
                            "Claude Code launch coverage about App Store Connect integration, "
                            "release flow, and workflow automation."
                        ),
                    ),
                    f"r__ClaudeAI__ccc333__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="ccc333",
                        slug="hooks-guide",
                        score=840,
                        comments=130,
                        title="Claude Code Hooks - all 23 explained and implemented",
                        post_text=(
                            "Claude Code hooks guide with workflow examples, repo setup notes, "
                            "and implementation details."
                        ),
                    ),
                    f"r__ClaudeAI__ddd444__reddit_thread__{REPORT_DATE}.md": self.build_reddit_signal_text(
                        post_id="ddd444",
                        slug="repos",
                        score=810,
                        comments=120,
                        title="These 10 GitHub repos completely changed how I use Claude Code",
                        post_text=(
                            "Claude Code repo roundup focused on workflow changes, tooling, "
                            "and practical usage patterns."
                        ),
                    ),
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["reddit-watch"],
                per_lane_limit=3,
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 3)
        self.assertEqual(
            {item.get("selection_bucket") for item in selected_items["selected_items"]},
            {"heat"},
        )

    def test_build_selected_items_non_reddit_lane_selection_stays_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="product-hunt-watch",
                signal_text_by_name={
                    "nicelydone.md": """---
type: producthunt_topic_hit
lane: product-hunt-watch
source: producthunt
entity_type: product
entity_id: nicelydone-mcp
title: Nicelydone MCP — Design context for AI agents
url: https://www.producthunt.com/products/nicely-done
fetched_at: 2026-04-12T10:58:49+0000
created_at: '2026-04-12T10:58:00Z'
---

## Preview

Design context for AI agents

## Snapshot

- **Votes**: 316
- **Comments**: 4
- **Topic**: Artificial Intelligence
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["product-hunt-watch"],
                per_lane_limit=1,
            )

        self.assertEqual(selected_items["summary"]["selected_item_count"], 1)
        self.assertEqual(
            selected_items["selected_items"][0]["title"],
            "Nicelydone MCP — Design context for AI agents",
        )
        self.assertNotIn("selection_bucket", selected_items["selected_items"][0])

    def test_default_lane_item_limits_keep_weather_small_without_changing_main_lanes(self) -> None:
        self.assertTrue(DEFAULT_LANE_ITEM_LIMITS)
        self.assertEqual(DEFAULT_LANE_ITEM_LIMITS["weather-watch"], 1)
        self.assertEqual(
            {
                lane_name: limit
                for lane_name, limit in DEFAULT_LANE_ITEM_LIMITS.items()
                if lane_name != "weather-watch"
            },
            {
                lane_name: 10
                for lane_name in DEFAULT_LANE_ITEM_LIMITS
                if lane_name != "weather-watch"
            },
        )

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

        self.assertEqual(selected_items["summary"]["selected_item_count"], 2)
        self.assertEqual(
            selected_items["summary"]["lane_counts"],
            [
                {"lane": "x-feed", "selected_item_count": 1},
                {"lane": "x-following", "selected_item_count": 1},
            ],
        )
        self.assertEqual(
            [item["source_url"] for item in selected_items["selected_items"]],
            [
                "https://x.com/trq212/status/2042671370186973589",
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
        self.assertEqual(bundle["summary"]["selected_item_count"], 1)
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
        self.assertEqual(artifact["source_lanes"], ["product-hunt-watch"])

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

    def test_weather_watch_round_trips_into_reader_facing_weather_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="weather-watch",
                signal_text_by_name={
                    "beijing-haidian.md": """---
type: weather_snapshot
lane: weather-watch
source: weather
entity_type: district
entity_id: beijing-haidian
title: Beijing Haidian Weather
url: https://weather.example.com/beijing-haidian/2026-04-12
fetched_at: 2026-04-12T05:30:00+0000
created_at: '2026-04-12T05:00:00Z'
---

## Weather

- Condition: 多云转晴
- Temperature: 8°C - 20°C
- Precipitation: 20%
- Wind: 西北风 3-4级
""",
                },
            )

            collect_result = build_collect_result(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["weather-watch"],
            )
            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["weather-watch"],
                per_lane_limit=1,
            )
            artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(
            selected_items["summary"]["lane_counts"],
            [{"lane": "weather-watch", "selected_item_count": 1}],
        )
        self.assertEqual(selected_items["summary"]["selected_item_count"], 1)
        self.assertEqual(artifact["source_lanes"], ["weather-watch"])
        self.assertIn("## 北京海淀天气", artifact["body_markdown"])
        self.assertNotIn("## weather-watch", artifact["body_markdown"])
        self.assertIn("### 北京海淀天气", artifact["body_markdown"])

        validate_report_markdown(
            artifact["body_markdown"],
            report_date=REPORT_DATE,
            expected_section_titles=[FIXED_SECTION_TITLES["weather-watch"]],
            expected_sources={
                FIXED_SECTION_TITLES["weather-watch"]: [
                    "https://weather.example.com/beijing-haidian/2026-04-12"
                ]
            },
        )

    def test_build_report_artifact_renders_weather_watch_as_concise_chinese_weather_bullet(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "weather-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "weather-watch",
                    "title": "Beijing Haidian Weather",
                    "source_url": "https://weather.example.com/beijing-haidian/2026-04-12",
                    "signal_path": "weather-watch/2026-04-12/signals/beijing-haidian.md",
                    "fetched_at": "2026-04-12T05:30:00+0000",
                    "source_snippet": (
                        "Condition: 多云 Temperature: 9°C - 21°C "
                        "Precipitation: 20% Wind: 西北风 3-4级"
                    ),
                    "excerpt": "Condition: 多云 Temperature: 9°C - 21°C",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "weather-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("## 北京海淀天气", body_markdown)
        self.assertIn("多云", body_markdown)
        self.assertIn("9°C - 21°C", body_markdown)
        self.assertIn("20%", body_markdown)
        self.assertIn("西北风 3-4级", body_markdown)
        self.assertNotIn("Condition:", body_markdown)
        self.assertNotIn("Temperature:", body_markdown)
        self.assertNotIn("Precipitation:", body_markdown)
        self.assertNotIn("Wind:", body_markdown)
        self.assertNotIn("该栏目收录", body_markdown)

    def test_hacker_news_lanes_round_trip_into_reader_facing_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="hacker-news-watch",
                signal_text_by_name={
                    "top-story.md": """---
type: hacker_news_story
lane: hacker-news-watch
source: hacker-news
entity_type: story
entity_id: 44000001
title: AI copilots need better review loops
url: https://news.ycombinator.com/item?id=44000001
fetched_at: 2026-04-12T13:00:00+0000
created_at: '2026-04-12T12:58:00Z'
---

## Post

作者在 HN 热榜里讨论 reviewer loop 和 agent handoff，重点是把计划、实现、验收拆开。

## Comments

- Points: 120
- Comments: 44
""",
                },
            )
            self.write_signal_bundle(
                signals_root,
                lane="hacker-news-search-watch",
                signal_text_by_name={
                    "search-hit.md": """---
type: hacker_news_search_hit
lane: hacker-news-search-watch
source: hacker-news
entity_type: story
entity_id: 44000002
title: Shipping agents with tmux and git worktrees
url: https://news.ycombinator.com/item?id=44000002
fetched_at: 2026-04-12T14:00:00+0000
created_at: '2026-04-12T13:58:00Z'
matched_query: Claude Code
---

## Post

作者把 tmux session、git worktree 和 review checklist 串成一条交接链路。
""",
                },
            )

            collect_result = build_collect_result(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["hacker-news-watch", "hacker-news-search-watch"],
            )
            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["hacker-news-watch", "hacker-news-search-watch"],
                per_lane_limit=1,
            )
            artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(
            collect_result["lanes"],
            [
                {"name": "hacker-news-watch", "status": "ok", "useful_item_count": 1},
                {"name": "hacker-news-search-watch", "status": "ok", "useful_item_count": 1},
            ],
        )
        self.assertEqual(
            selected_items["summary"]["lane_counts"],
            [
                {"lane": "hacker-news-watch", "selected_item_count": 1},
                {"lane": "hacker-news-search-watch", "selected_item_count": 1},
            ],
        )
        self.assertEqual(
            artifact["source_lanes"],
            ["hacker-news-watch", "hacker-news-search-watch"],
        )
        self.assertIn("## Hacker News 热榜", artifact["body_markdown"])
        self.assertIn("## Hacker News 搜索", artifact["body_markdown"])
        self.assertIn("### Hacker News 热榜", artifact["body_markdown"])
        self.assertIn("### Hacker News 搜索", artifact["body_markdown"])

        validate_report_markdown(
            artifact["body_markdown"],
            report_date=REPORT_DATE,
            expected_section_titles=[
                FIXED_SECTION_TITLES["hacker-news-watch"],
                FIXED_SECTION_TITLES["hacker-news-search-watch"],
            ],
            expected_sources={
                FIXED_SECTION_TITLES["hacker-news-watch"]: [
                    "https://news.ycombinator.com/item?id=44000001"
                ],
                FIXED_SECTION_TITLES["hacker-news-search-watch"]: [
                    "https://news.ycombinator.com/item?id=44000002"
                ],
            },
        )

    def test_build_selected_items_hacker_news_watch_filters_generic_hot_posts_without_dropping_ai_posts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="hacker-news-watch",
                signal_text_by_name={
                    "claude-design.md": """---
type: hacker_news_story
lane: hacker-news-watch
source: hacker-news
entity_type: story
entity_id: 44000011
title: Claude Design review ownership and repo boundaries
url: https://news.ycombinator.com/item?id=44000011
fetched_at: 2026-04-12T16:05:00+0000
created_at: '2026-04-12T16:00:00Z'
---

## Post

Claude Design 这条热榜讨论把 reviewer loop、review checklist、repo boundaries 和 git worktree handoff 写成了一套可执行做法。

## Comments

- Points: 140
- Comments: 61
""",
                    "emacs.md": """---
type: hacker_news_story
lane: hacker-news-watch
source: hacker-news
entity_type: story
entity_id: 44000012
title: Why I still trust Emacs for coding workflow
url: https://news.ycombinator.com/item?id=44000012
fetched_at: 2026-04-12T16:06:00+0000
created_at: '2026-04-12T16:01:00Z'
---

## Post

这是一篇关于个人编辑器习惯、键盘宏和 Lisp 配置的帖子，重点是长期维护一个安静的 coding workflow。

## Comments

- Points: 560
- Comments: 203
""",
                    "geometry.md": """---
type: hacker_news_story
lane: hacker-news-watch
source: hacker-news
entity_type: story
entity_id: 44000013
title: A visual proof for a geometry shortcut
url: https://news.ycombinator.com/item?id=44000013
fetched_at: 2026-04-12T16:07:00+0000
created_at: '2026-04-12T16:02:00Z'
---

## Post

这篇热榜帖子在讨论三角形、圆和纯几何证明。

## Comments

- Points: 620
- Comments: 244
""",
                },
            )

            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["hacker-news-watch"],
                per_lane_limit=5,
            )

        self.assertEqual(
            [item["title"] for item in selected_items["selected_items"]],
            ["Claude Design review ownership and repo boundaries"],
        )

    def test_build_report_artifact_hacker_news_watch_omits_generic_hot_titles_when_mixed_with_relevant_items(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="hacker-news-watch",
                signal_text_by_name={
                    "claude-design.md": """---
type: hacker_news_story
lane: hacker-news-watch
source: hacker-news
entity_type: story
entity_id: 44000014
title: Claude Design review ownership and repo boundaries
url: https://news.ycombinator.com/item?id=44000014
fetched_at: 2026-04-12T17:05:00+0000
created_at: '2026-04-12T17:00:00Z'
---

## Post

Claude Design 这条热榜讨论把 reviewer loop、review checklist、repo boundaries 和 git worktree handoff 写成了一套可执行做法。

## Comments

- Points: 150
- Comments: 57
""",
                    "emacs.md": """---
type: hacker_news_story
lane: hacker-news-watch
source: hacker-news
entity_type: story
entity_id: 44000015
title: Why I still trust Emacs for coding workflow
url: https://news.ycombinator.com/item?id=44000015
fetched_at: 2026-04-12T17:06:00+0000
created_at: '2026-04-12T17:01:00Z'
---

## Post

这是一篇关于个人编辑器习惯、键盘宏和 Lisp 配置的帖子，重点是长期维护一个安静的 coding workflow。

## Comments

- Points: 580
- Comments: 188
""",
                },
            )
            self.write_signal_bundle(
                signals_root,
                lane="hacker-news-search-watch",
                signal_text_by_name={
                    "search-hit.md": """---
type: hacker_news_search_hit
lane: hacker-news-search-watch
source: hacker-news
entity_type: story
entity_id: 44000016
title: Shipping agents with tmux and git worktrees
url: https://news.ycombinator.com/item?id=44000016
fetched_at: 2026-04-12T17:10:00+0000
created_at: '2026-04-12T17:08:00Z'
matched_query: Claude Code
---

## Post

作者把 tmux、git worktree 和 review checklist 串成一条 agent 交接链路。
""",
                },
            )

            collect_result = build_collect_result(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["hacker-news-watch", "hacker-news-search-watch"],
            )
            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["hacker-news-watch", "hacker-news-search-watch"],
                per_lane_limit=5,
            )
            artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        body_markdown = artifact["body_markdown"]
        self.assertIn("## Hacker News 热榜", body_markdown)
        self.assertIn("Claude Design review ownership and repo boundaries", body_markdown)
        self.assertNotIn("Why I still trust Emacs for coding workflow", body_markdown)
        self.assertIn("Shipping agents with tmux and git worktrees", body_markdown)

    def test_hacker_news_search_watch_preserves_matched_query_in_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            signals_root = Path(temp_dir)
            self.write_signal_bundle(
                signals_root,
                lane="hacker-news-search-watch",
                signal_text_by_name={
                    "query-hit.md": """---
type: hacker_news_search_hit
lane: hacker-news-search-watch
source: hacker-news
entity_type: story
entity_id: 44000003
title: Run agents with tmux + git worktrees
url: https://news.ycombinator.com/item?id=44000003
fetched_at: 2026-04-12T15:00:00+0000
created_at: '2026-04-12T14:58:00Z'
matched_query: Claude Code
---

## Post

作者把 tmux、git worktree 和 review checklist 连成一条 agent 交接链路。
""",
                },
            )

            collect_result = build_collect_result(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["hacker-news-search-watch"],
            )
            selected_items = build_selected_items(
                signals_root=signals_root,
                report_date=REPORT_DATE,
                lane_names=["hacker-news-search-watch"],
                per_lane_limit=1,
            )
            artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        self.assertEqual(selected_items["selected_items"][0]["matched_query"], "Claude Code")
        self.assertIn("Claude Code", artifact["body_markdown"])
        self.assertIn("Run agents with tmux + git worktrees", artifact["body_markdown"])

        validate_report_markdown(
            artifact["body_markdown"],
            report_date=REPORT_DATE,
            expected_section_titles=[FIXED_SECTION_TITLES["hacker-news-search-watch"]],
            expected_sources={
                FIXED_SECTION_TITLES["hacker-news-search-watch"]: [
                    "https://news.ycombinator.com/item?id=44000003"
                ]
            },
        )

    def test_build_report_artifact_rewrites_hacker_news_watch_related_fragments(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "hacker-news-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "hacker-news-watch",
                    "title": "Claude Design",
                    "source_url": "https://news.ycombinator.com/item?id=44000009",
                    "signal_path": "hacker-news-watch/2026-04-12/signals/top-story.md",
                    "fetched_at": "2026-04-12T16:00:00+0000",
                    "source_snippet": (
                        "Related: Claude Design thread on review ownership, reviewer loops, "
                        "and why repo boundaries still matter for agents."
                    ),
                    "excerpt": (
                        "Related: Claude Design thread on review ownership, reviewer loops, "
                        "and why repo boundaries still matter for agents."
                    ),
                    "source": "hacker-news",
                    "signal_type": "hacker_news_story",
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "hacker-news-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        body = artifact["body_markdown"]
        self.assertIn("**Claude Design** 这条 HN 热榜讨论在聊", body)
        self.assertIn("评审分工", body)
        self.assertIn("review loop", body)
        self.assertIn("仓库边界", body)
        self.assertNotIn("Related:", body)
        self.assertNotIn("Claude Design Related", body)
        self.assertNotIn("该栏目收录 1 条有用内容。", body)

    def test_build_report_artifact_keeps_hacker_news_search_query_and_facts(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "hacker-news-search-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "hacker-news-search-watch",
                    "title": "Shipping agents with tmux and git worktrees",
                    "source_url": "https://news.ycombinator.com/item?id=44000010",
                    "signal_path": "hacker-news-search-watch/2026-04-12/signals/search-hit.md",
                    "fetched_at": "2026-04-12T16:30:00+0000",
                    "matched_query": "Claude Code",
                    "source_snippet": (
                        "Search hit: teams using tmux sessions, git worktrees, and review "
                        "checklists as a single handoff loop for Claude Code agents."
                    ),
                    "excerpt": (
                        "Search hit: teams using tmux sessions, git worktrees, and review "
                        "checklists as a single handoff loop for Claude Code agents."
                    ),
                    "source": "hacker-news",
                    "signal_type": "hacker_news_search_hit",
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "hacker-news-search-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)

        body = artifact["body_markdown"]
        self.assertIn("搜索词「Claude Code」", body)
        self.assertIn("tmux", body)
        self.assertIn("git worktree", body)
        self.assertIn("review checklist", body)
        self.assertIn("agent 交接", body)
        self.assertNotIn("该栏目收录 1 条有用内容。", body)
        self.assertNotIn("原文围绕", body)

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

    def test_build_report_artifact_live_like_reddit_items_render_three_concrete_sentences(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "reddit-watch", "status": "ok", "useful_item_count": 10},
            ],
            "summary": {"useful_item_count": 10, "partial_lane_count": 0},
        }
        cases = [
            {
                "title": "Maestro v1.6.1 — multi-agent orchestration now runs on Claude Code, Gemini CLI, AND OpenAI Codex !",
                "selection_bucket": "heat",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1shmul3/maestro_v161_multiagent_orchestration_now_runs_on/",
                "source_snippet": (
                    "Maestro is an open-source multi-agent orchestration platform that coordinates 22 specialized AI "
                    "subagents through structured workflows — design dialogue, implementation planning, parallel "
                    "subagents, and quality gates. It started as a Gemini CLI extension. v1.6.1 adds OpenAI Codex as "
                    "a third native runtime and rebuilds the architecture so all three share a single canonical source tree."
                ),
                "expected_keywords": ["22", "OpenAI Codex", "canonical source tree"],
            },
            {
                "title": "Built a tool that makes Claude Code, Codex, and Gemini deliberate on engineering questions: agent-council",
                "selection_bucket": "heat",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1s8n620/built_a_tool_that_makes_claude_code_codex_and/",
                "source_snippet": (
                    "Install: npx cliagent-council. I built this because API-based LLM councils answer in a vacuum, "
                    "while CLI agents can grep your code, read your migrations, and git log your history. It uses your "
                    "existing Claude Code, Codex, and Gemini CLI subscriptions, so each session is zero marginal cost."
                ),
                "expected_keywords": ["agent-council", "grep", "git", "零边际"],
            },
            {
                "title": "Claude version of Openclaw coming soon?",
                "selection_bucket": "heat",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1sivk1k/claude_version_of_openclaw_coming_soon/",
                "source_snippet": (
                    "Anthropic's roadmap usually leads with Claude Code, then features trickle down to desktop and "
                    "mobile. The author points to Cowork, MCP, and skills as examples. Claude Code now has /monitor, "
                    "which lets it sit on your computer, listen for a trigger, and ping Claude with a message."
                ),
                "expected_keywords": ["/monitor", "Cowork", "MCP"],
            },
            {
                "title": "Anthropic just shipped messaging integration for Claude Code. Direct OpenClaw competitor, no dedicated hardware needed.",
                "selection_bucket": "heat",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1ryrjdg/anthropic_just_shipped_messaging_integration_for/",
                "source_snippet": (
                    "Claude Code Channels launched today. You can now DM your Claude Code session from Telegram or "
                    "Discord and it processes requests with full tool access, including file edits, test runs, and git "
                    "ops. Compared with OpenClaw, this path is just a --channels flag and a bot token instead of a Mac "
                    "Mini, Docker, and a much heavier stack."
                ),
                "expected_keywords": ["Telegram", "Discord", "--channels", "bot token"],
            },
            {
                "title": "I read 17 papers on agentic AI workflows. Most Claude Code advice is measurably wrong",
                "selection_bucket": "voice",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1s8mbqm/i_read_17_papers_on_agentic_ai_workflows_most/",
                "source_snippet": (
                    "I lead a small engineering team doing a greenfield SaaS rewrite. I spent months building agent "
                    "pipelines that worked great in demos and fell apart in production. When I read the research, I "
                    "found out why: telling Claude you are the world's best programmer degrades output quality."
                ),
                "expected_keywords": ["17 篇", "greenfield SaaS", "production", "输出质量"],
            },
            {
                "title": "Non-technical founder: Is OpenClaw a must if Claude Code is currently looking like its working for my SaaS?",
                "selection_bucket": "voice",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1scfv01/nontechnical_founder_is_openclaw_a_must_if_claude/",
                "source_snippet": (
                    "I have no formal computer science background, but Claude has handled the heavy lifting so far. "
                    "My vibecoded landing page is already live, Claude Code is building the n8n workflows, and the MVP "
                    "feels like it is coming together. The real question is whether OpenClaw is necessary now or if the "
                    "current Claude Code stack is already enough."
                ),
                "expected_keywords": ["landing page", "n8n", "MVP", "OpenClaw"],
            },
            {
                "title": "Built a WhatsApp AI assistant with Claude Code as an OpenClaw alternative",
                "selection_bucket": "voice",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1scj0lb/built_a_whatsapp_ai_assistant_with_claude_code_as/",
                "source_snippet": (
                    "The promise of OpenClaw is enticing, but I could not get past the security model. I wanted "
                    "something that combines WhatsApp for messaging with Claude Code as the agentic brain. I am already "
                    "paying for Claude Max, and I trust Anthropic's runtime more."
                ),
                "expected_keywords": ["WhatsApp", "安全模型", "Claude Max", "Anthropic"],
            },
            {
                "title": "Is there a user-wide agent context file that works across Codex, Claude Code, Cursor, etc.?",
                "selection_bucket": "voice",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1s32xx9/is_there_a_userwide_agent_context_file_that_works/",
                "source_snippet": (
                    "I am looking for one global set of instructions and context for AI coding agents across all my "
                    "repos, instead of repeating project-level files like AGENTS.md in each repo. Ideally the same "
                    "user-wide file could work with Codex, Claude Code, Cursor, and similar environments. If there is "
                    "no common standard, I want to know whether the practical path is to keep one canonical file and "
                    "sync it into each tool's own format."
                ),
                "expected_keywords": ["Codex", "Claude Code", "Cursor", "canonical file"],
            },
            {
                "title": "Best approach to use AI agents (Claude Code, Codex) for large codebases and big refactors? Looking for workflows",
                "selection_bucket": "voice",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1rwok87/best_approach_to_use_ai_agents_claude_code_codex/",
                "source_snippet": (
                    "I can already use agents to pick up GitHub issues by giving them the issue link, plan and execute "
                    "tasks in a back-and-forth way, and handle small to medium changes. That workflow is working fine. "
                    "What breaks down is using the same agents on large applications and major refactors."
                ),
                "expected_keywords": ["GitHub issue", "大仓库", "大改版"],
            },
            {
                "title": "Claude Code can now submit your app to App Store Connect and help you pass review",
                "selection_bucket": "voice",
                "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1sdot1s/claude_code_can_now_submit_your_app_to_app_store/",
                "source_snippet": (
                    "I built a native macOS app called Blitz that gives Claude Code full control over App Store "
                    "Connect. Metadata, screenshots, builds, localization, and review notes no longer require leaving "
                    "the terminal. MCP servers let Claude Code handle the whole submission flow."
                ),
                "expected_keywords": ["Blitz", "App Store Connect", "screenshots", "MCP"],
            },
        ]
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "reddit-watch",
                    "title": case["title"],
                    "source_url": case["source_url"],
                    "signal_path": f"reddit-watch/{REPORT_DATE}/signals/{index}.md",
                    "fetched_at": f"{REPORT_DATE}T1{index}:00:00+0000",
                    "source_snippet": case["source_snippet"],
                    "excerpt": case["source_snippet"],
                    "selection_bucket": case["selection_bucket"],
                }
                for index, case in enumerate(cases, start=1)
            ],
            "summary": {
                "selected_item_count": len(cases),
                "lane_counts": [{"lane": "reddit-watch", "selected_item_count": len(cases)}],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_lines = [
            line for line in artifact["body_markdown"].splitlines() if line.strip().startswith("- **")
        ]

        self.assertEqual(len(body_lines), len(cases))
        for case in cases:
            with self.subTest(title=case["title"]):
                body_line = next(line for line in body_lines if case["source_url"] in line)
                self.assertNotIn("原文围绕 Claude Code 展开，具体变化见来源", body_line)
                self.assertGreaterEqual(body_line.count("。"), 3)
                for keyword in case["expected_keywords"]:
                    self.assertIn(keyword, body_line)

    def test_build_report_artifact_expands_target_lanes_with_multiple_concrete_facts(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "reddit-watch", "status": "ok", "useful_item_count": 1},
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
                {"name": "codex-watch", "status": "ok", "useful_item_count": 1},
                {"name": "openclaw-watch", "status": "ok", "useful_item_count": 1},
                {"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1},
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 1},
                {"name": "polymarket-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 7, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "reddit-watch",
                    "title": "I replaced chaotic solo Claude coding with a simple 3-agent team (Architect + Builder + Reviewer) — it's stupidly effective and token-efficient",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/example/three-man-team/",
                    "signal_path": "reddit-watch/2026-04-12/signals/reddit.md",
                    "fetched_at": "2026-04-12T11:00:00+0000",
                    "source_snippet": (
                        "After reading a bunch of papers on agentic workflows and burning way too many tokens on solo AI coding sessions, "
                        "I settled on a structured Three Man Team: Architect plans, Builder implements, Reviewer validates. "
                        "Everything moves through markdown handoff files so the process stays transparent and token-efficient."
                    ),
                    "excerpt": (
                        "After reading a bunch of papers on agentic workflows and burning way too many tokens on solo AI coding sessions, "
                        "I settled on a structured Three Man Team: Architect plans, Builder implements, Reviewer validates. "
                        "Everything moves through markdown handoff files so the process stays transparent and token-efficient."
                    ),
                    "editor_summary": "讨论把角色拆分讲清楚了。",
                },
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.101",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.101",
                    "signal_path": "claude-code-watch/2026-04-12/signals/v2.1.101.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Added `/team-onboarding` command to generate a teammate ramp-up guide from your local Claude Code usage "
                        "Added OS CA certificate store trust by default, so enterprise TLS proxies work without extra setup "
                        "(set `CLAUDE_CODE_CERT_STORE=bundled` to use only bundled CAs) "
                        "`/ultraplan` and other remote-session features now auto-create a default cloud environment "
                        "Improved brief mode to retry once when Claude responds with plain text instead of a structured message"
                    ),
                    "excerpt": (
                        "Added `/team-onboarding` command to generate a teammate ramp-up guide from your local Claude Code usage "
                        "Added OS CA certificate store trust by default, so enterprise TLS proxies work without extra setup "
                        "(set `CLAUDE_CODE_CERT_STORE=bundled` to use only bundled CAs) "
                        "`/ultraplan` and other remote-session features now auto-create a default cloud environment "
                        "Improved brief mode to retry once when Claude responds with plain text instead of a structured message"
                    ),
                    "editor_summary": "这版更新更清楚了。",
                },
                {
                    "lane": "codex-watch",
                    "title": "Add MCP tool wall time to model output",
                    "source_url": "https://github.com/openai/codex/pull/17406",
                    "signal_path": "codex-watch/2026-04-12/signals/pr-17406.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Title: Add MCP tool wall time to model output "
                        "Author: @pakrym-oai "
                        "Merge commit: `7c1e41c` "
                        "Include MCP wall time in the output so the model is aware of how long it's calls are taking."
                    ),
                    "excerpt": (
                        "Title: Add MCP tool wall time to model output "
                        "Author: @pakrym-oai "
                        "Merge commit: `7c1e41c` "
                        "Include MCP wall time in the output so the model is aware of how long it's calls are taking."
                    ),
                    "editor_summary": "这次改动更清楚了。",
                },
                {
                    "lane": "openclaw-watch",
                    "title": "openclaw 2026.4.11",
                    "source_url": "https://github.com/openclaw/openclaw/releases/tag/v2026.4.11",
                    "signal_path": "openclaw-watch/2026-04-12/signals/v2026.4.11.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Dreaming/memory-wiki: add ChatGPT import ingestion plus new `Imported Insights` and `Memory Palace` diary subtabs so Dreaming can inspect imported source chats, compiled wiki pages, and full source pages directly from the UI. "
                        "Control UI/webchat: render assistant media/reply/voice directives as structured chat bubbles and add the `[embed ...]` rich output tag."
                    ),
                    "excerpt": (
                        "Dreaming/memory-wiki: add ChatGPT import ingestion plus new `Imported Insights` and `Memory Palace` diary subtabs so Dreaming can inspect imported source chats, compiled wiki pages, and full source pages directly from the UI. "
                        "Control UI/webchat: render assistant media/reply/voice directives as structured chat bubbles and add the `[embed ...]` rich output tag."
                    ),
                    "editor_summary": "新版本更偏向真实使用场景。",
                },
                {
                    "lane": "github-trending-weekly",
                    "title": "Archon",
                    "source_url": "https://github.com/coleam00/Archon",
                    "signal_path": "github-trending-weekly/2026-04-12/signals/archon.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "The first open-source harness builder for AI coding. "
                        "Make AI coding deterministic and repeatable. "
                        "Author: @coleam00/Archon"
                    ),
                    "excerpt": (
                        "The first open-source harness builder for AI coding. "
                        "Make AI coding deterministic and repeatable. "
                        "Author: @coleam00/Archon"
                    ),
                    "editor_summary": "这个项目值得关注。",
                },
                {
                    "lane": "product-hunt-watch",
                    "title": "Nicelydone MCP — Design context for AI agents",
                    "source_url": "https://www.producthunt.com/products/nicely-done",
                    "signal_path": "product-hunt-watch/2026-04-12/signals/nicelydone.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Design context for AI agents "
                        "Votes: 316 Comments: 4 Topic: Artificial Intelligence "
                        "Author: @Nicelydone MCP"
                    ),
                    "excerpt": (
                        "Design context for AI agents "
                        "Votes: 316 Comments: 4 Topic: Artificial Intelligence "
                        "Author: @Nicelydone MCP"
                    ),
                    "editor_summary": "这个产品更像工作流了。",
                },
                {
                    "lane": "polymarket-watch",
                    "title": "Will Anthropic have the second-best Coding AI model at the end of April 2026?",
                    "source_url": "https://polymarket.com/event/which-company-has-the-second-best-coding-ai-model-end-of-april",
                    "signal_path": "polymarket-watch/2026-04-12/signals/anthropic.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%) "
                        "OpenAI: 8.0% "
                        "24h volume: 48,320.1 Liquidity: 21,405.0 Price movement: up 4.2% today"
                    ),
                    "excerpt": (
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%) "
                        "OpenAI: 8.0% "
                        "24h volume: 48,320.1 Liquidity: 21,405.0 Price movement: up 4.2% today"
                    ),
                    "editor_summary": "市场判断继续收敛。",
                },
            ],
            "summary": {
                "selected_item_count": 7,
                "lane_counts": [
                    {"lane": "reddit-watch", "selected_item_count": 1},
                    {"lane": "claude-code-watch", "selected_item_count": 1},
                    {"lane": "codex-watch", "selected_item_count": 1},
                    {"lane": "openclaw-watch", "selected_item_count": 1},
                    {"lane": "github-trending-weekly", "selected_item_count": 1},
                    {"lane": "product-hunt-watch", "selected_item_count": 1},
                    {"lane": "polymarket-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        def body_line_for(title: str) -> str:
            return next(line for line in body_markdown.splitlines() if f"**{title}**" in line)

        reddit_line = body_line_for("三角色协作流程")
        self.assertIn("Architect", reddit_line)
        self.assertIn("Builder", reddit_line)
        self.assertIn("Reviewer", reddit_line)
        self.assertIn("markdown handoff", reddit_line)
        self.assertGreaterEqual(len(reddit_line), 150)

        claude_line = body_line_for("v2.1.101")
        self.assertIn("/team-onboarding", claude_line)
        self.assertIn("CLAUDE_CODE_CERT_STORE=bundled", claude_line)
        self.assertIn("cloud environment", claude_line)
        self.assertIn("brief mode", claude_line)
        self.assertGreaterEqual(len(claude_line), 160)

        codex_line = body_line_for("Add MCP tool wall time to model output")
        self.assertIn("17406", codex_line)
        self.assertIn("MCP tool wall time", codex_line)
        self.assertIn("model output", codex_line)
        self.assertGreaterEqual(len(codex_line), 120)

        openclaw_line = body_line_for("openclaw 2026.4.11")
        self.assertIn("ChatGPT import ingestion", openclaw_line)
        self.assertIn("Imported Insights", openclaw_line)
        self.assertIn("Memory Palace", openclaw_line)
        self.assertIn("structured chat bubbles", openclaw_line)
        self.assertGreaterEqual(len(openclaw_line), 150)

        archon_line = body_line_for("Archon")
        self.assertIn("harness builder", archon_line)
        self.assertIn("deterministic", archon_line)
        self.assertIn("repeatable", archon_line)
        self.assertGreaterEqual(len(archon_line), 110)

        product_line = body_line_for("Nicelydone MCP — Design context for AI agents")
        self.assertIn("Nicelydone MCP", product_line)
        self.assertIn("Design context", product_line)
        self.assertIn("316", product_line)
        self.assertIn("Artificial Intelligence", product_line)
        self.assertGreaterEqual(len(product_line), 120)

        market_line = body_line_for("Will Anthropic have the second-best Coding AI model at the end of April 2026?")
        self.assertIn("Anthropic", market_line)
        self.assertIn("90.0%", market_line)
        self.assertIn("OpenAI", market_line)
        self.assertIn("48,320.1", market_line)
        self.assertIn("21,405.0", market_line)
        self.assertIn("4.2%", market_line)
        self.assertGreaterEqual(len(market_line), 150)

    def test_build_report_artifact_live_like_key_lanes_keep_more_than_one_short_summary_clause(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
                {"name": "codex-watch", "status": "ok", "useful_item_count": 1},
                {"name": "openclaw-watch", "status": "ok", "useful_item_count": 1},
                {"name": "polymarket-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 4, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.101",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.101",
                    "signal_path": "claude-code-watch/2026-04-12/signals/v2.1.101.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Added `/team-onboarding` command to generate a teammate ramp-up guide from your local Claude Code usage "
                        "Added OS CA certificate store trust by default, so enterprise TLS proxies work without extra setup "
                        "(set `CLAUDE_CODE_CERT_STORE=bundled` to use only bundled CAs) "
                        "`/ultraplan` and other remote-session features now auto-create a default cloud environment"
                    ),
                    "excerpt": (
                        "Added `/team-onboarding` command to generate a teammate ramp-up guide from your local Claude Code usage "
                        "Added OS CA certificate store trust by default, so enterprise TLS proxies work without extra setup "
                        "(set `CLAUDE_CODE_CERT_STORE=bundled` to use only bundled CAs) "
                        "`/ultraplan` and other remote-session features now auto-create a default cloud environment"
                    ),
                },
                {
                    "lane": "codex-watch",
                    "title": "Add MCP tool wall time to model output",
                    "source_url": "https://github.com/openai/codex/pull/17406",
                    "signal_path": "codex-watch/2026-04-12/signals/pr-17406.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": "Include MCP wall time in the output so the model is aware of how long it's calls are taking.",
                    "excerpt": "Include MCP wall time in the output so the model is aware of how long it's calls are taking.",
                },
                {
                    "lane": "openclaw-watch",
                    "title": "openclaw 2026.4.11",
                    "source_url": "https://github.com/openclaw/openclaw/releases/tag/v2026.4.11",
                    "signal_path": "openclaw-watch/2026-04-12/signals/v2026.4.11.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Dreaming/memory-wiki: add ChatGPT import ingestion plus new `Imported Insights` and `Memory Palace` diary subtabs "
                        "so Dreaming can inspect imported source chats, compiled wiki pages, and full source pages directly from the UI."
                    ),
                    "excerpt": (
                        "Dreaming/memory-wiki: add ChatGPT import ingestion plus new `Imported Insights` and `Memory Palace` diary subtabs "
                        "so Dreaming can inspect imported source chats, compiled wiki pages, and full source pages directly from the UI."
                    ),
                },
                {
                    "lane": "polymarket-watch",
                    "title": "Will Anthropic have the second-best Coding AI model at the end of April 2026?",
                    "source_url": "https://polymarket.com/event/which-company-has-the-second-best-coding-ai-model-end-of-april",
                    "signal_path": "polymarket-watch/2026-04-12/signals/anthropic.md",
                    "fetched_at": "2026-04-12T12:00:00+0000",
                    "source_snippet": (
                        "Market: Which company has the second best Coding AI model end of April? "
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%)"
                    ),
                    "excerpt": (
                        "Market: Which company has the second best Coding AI model end of April? "
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%)"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 4,
                "lane_counts": [
                    {"lane": "claude-code-watch", "selected_item_count": 1},
                    {"lane": "codex-watch", "selected_item_count": 1},
                    {"lane": "openclaw-watch", "selected_item_count": 1},
                    {"lane": "polymarket-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("/team-onboarding", body_markdown)
        self.assertIn("CLAUDE_CODE_CERT_STORE=bundled", body_markdown)
        self.assertIn("17406", body_markdown)
        self.assertIn("MCP tool wall time", body_markdown)
        self.assertIn("Imported Insights", body_markdown)
        self.assertIn("Memory Palace", body_markdown)
        self.assertIn("Anthropic", body_markdown)
        self.assertIn("90.0%", body_markdown)
        self.assertNotIn("这版更新把 onboarding、云环境、证书和 brief mode 一起推进", body_markdown)
        self.assertNotIn("原文围绕 MCP 展开，具体变化见来源", body_markdown)
        self.assertNotIn("新版本一边补导入和富媒体能力", body_markdown)
        self.assertNotIn("这份 Polymarket 合约当前把 Anthropic 放在显著领先位置", body_markdown)

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

    def test_build_report_artifact_live_like_x_english_snippet_uses_specific_facts_instead_of_generic_placeholder(self) -> None:
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
                    "title": "@theo #75",
                    "source_url": "https://x.com/theo/status/2043611205856837680",
                    "signal_path": "x-feed/2026-04-14/signals/theo.md",
                    "fetched_at": "2026-04-14T05:06:43+0000",
                    "source_snippet": (
                        "Agent harnesses aren't the black magic many of y'all seem to think they are. "
                        "To prove it, I built one."
                    ),
                    "excerpt": (
                        "Agent harnesses aren't the black magic many of y'all seem to think they are. "
                        "To prove it, I built one."
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(line for line in artifact["body_markdown"].splitlines() if "**@theo #75**" in line)

        self.assertIn("agent harness", body_line)
        self.assertIn("没大家想得那么玄", body_line)
        self.assertIn("自己做了一个", body_line)
        self.assertNotIn("原文围绕 harness 展开，具体变化见来源", body_line)

    def test_build_report_artifact_skips_noisy_x_items_when_reader_excerpt_still_degrades_to_placeholder_or_fragment(
        self,
    ) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 2},
                {"name": "x-following", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": 4, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@theo #75",
                    "source_url": "https://x.com/theo/status/2043611205856837680",
                    "signal_path": "x-feed/2026-04-17/signals/theo.md",
                    "fetched_at": "2026-04-17T05:06:43+0000",
                    "source_snippet": (
                        "Agent harnesses aren't the black magic many of y'all seem to think they are. "
                        "To prove it, I built one."
                    ),
                    "excerpt": (
                        "Agent harnesses aren't the black magic many of y'all seem to think they are. "
                        "To prove it, I built one."
                    ),
                },
                {
                    "lane": "x-feed",
                    "title": "@_catwu #64",
                    "source_url": "https://x.com/_catwu/status/2044808533905178822",
                    "signal_path": "x-feed/2026-04-17/signals/_catwu.md",
                    "fetched_at": "2026-04-17T01:11:42+0000",
                    "source_snippet": (
                        "Opus 4.7 is live in Claude Code today! "
                        "The model performs best if you treat it like an engineer you're delegating to,"
                    ),
                    "excerpt": (
                        "Opus 4.7 is live in Claude Code today! "
                        "The model performs best if you treat it like an engineer you're delegating to,"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@addyosmani",
                    "source_url": "https://x.com/addyosmani/status/2043728421160101881",
                    "signal_path": "x-following/2026-04-17/signals/addyosmani.md",
                    "fetched_at": "2026-04-17T06:00:00+0000",
                    "source_snippet": (
                        "Want to give your agent quality checks? Chrome's DevTools MCP now includes: "
                        "Performance checks via Lighthouse"
                    ),
                    "excerpt": (
                        "Want to give your agent quality checks? Chrome's DevTools MCP now includes: "
                        "Performance checks via Lighthouse"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@NickADobos",
                    "source_url": "https://x.com/NickADobos/status/2044885440092877028",
                    "signal_path": "x-following/2026-04-17/signals/NickADobos.md",
                    "fetched_at": "2026-04-17T01:11:47+0000",
                    "source_snippet": (
                        "With codex computer use + mac's iPhone Mirror app, GPT can use any app on your phone!!! "
                        "Seems less accurate with clicks"
                    ),
                    "excerpt": (
                        "With codex computer use + mac's iPhone Mirror app, GPT can use any app on your phone!!! "
                        "Seems less accurate with clicks"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 4,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 2},
                    {"lane": "x-following", "selected_item_count": 2},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("https://x.com/theo/status/2043611205856837680", body_markdown)
        self.assertIn("https://x.com/addyosmani/status/2043728421160101881", body_markdown)
        # _catwu and NickADobos now generate proper Chinese facts - should be kept
        self.assertIn("https://x.com/_catwu/status/2044808533905178822", body_markdown)
        self.assertIn("https://x.com/NickADobos/status/2044885440092877028", body_markdown)
        # Bad patterns should not appear
        self.assertNotIn("该栏目收录", body_markdown)
        self.assertNotIn("这条帖子围绕", body_markdown)
        self.assertNotIn("The model performs best if you treat it like an engineer you're delegating", body_markdown)
        self.assertNotIn("Seems less accurate with clicks", body_markdown)

    def test_build_report_artifact_live_like_x_multi_fact_snippet_keeps_multiple_specific_units(self) -> None:
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
                    "title": "@heygurisingh",
                    "source_url": "https://x.com/heygurisingh/status/2043907795972698218",
                    "signal_path": "x-following/2026-04-14/signals/heygurisingh.md",
                    "fetched_at": "2026-04-14T05:06:52+0000",
                    "source_snippet": (
                        "Holy shit... someone built a TUI that shows where your Claude Code tokens actually go. "
                        "Turns out 56% of my $200/day spe"
                    ),
                    "excerpt": (
                        "Holy shit... someone built a TUI that shows where your Claude Code tokens actually go. "
                        "Turns out 56% of my $200/day spe"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-following", "selected_item_count": 1}],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(line for line in artifact["body_markdown"].splitlines() if "**@heygurisingh**" in line)

        self.assertIn("TUI", body_line)
        self.assertIn("Claude Code", body_line)
        self.assertIn("56%", body_line)
        self.assertIn("200", body_line)
        self.assertNotIn("原文围绕 Claude Code 展开，具体变化见来源", body_line)
        self.assertNotIn("$200/day spe", body_line)

    def test_build_report_artifact_live_like_release_pr_and_market_items_keep_key_structured_facts(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
                {"name": "codex-watch", "status": "ok", "useful_item_count": 1},
                {"name": "openclaw-watch", "status": "ok", "useful_item_count": 1},
                {"name": "polymarket-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 4, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.105",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.105",
                    "signal_path": "claude-code-watch/2026-04-14/signals/v2.1.105.md",
                    "fetched_at": "2026-04-14T05:07:39+0000",
                    "source_snippet": (
                        "Added `path` parameter to the `EnterWorktree` tool to switch into an existing worktree of the current repository "
                        "Added PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning "
                        '`{"decision":"block"}` '
                        "Added background monitor support for plugins via a top-level `monitors` manifest key that auto-arms at session start or on skill invoke "
                        "`/proactive` is now an alias for `/loop` "
                        "Improved stalled API stream handling: streams now abort after 5 minutes of no data and retry non-streaming instead of hanging indefinitely"
                    ),
                    "excerpt": (
                        "Added `path` parameter to the `EnterWorktree` tool to switch into an existing worktree of the current repository "
                        "Added PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning "
                        '`{"decision":"block"}` '
                        "Added background monitor support for plugins via a top-level `monitors` manifest key that auto-arms at session start or on skill invoke "
                        "`/proactive` is now an alias for `/loop` "
                        "Improved stalled API stream handling: streams now abort after 5 minutes of no data and retry non-streaming instead of hanging indefinitely"
                    ),
                },
                {
                    "lane": "codex-watch",
                    "title": "guardian timeout fix pr 3 - ux touch for timeouts",
                    "source_url": "https://github.com/openai/codex/pull/17557",
                    "signal_path": "codex-watch/2026-04-14/signals/17557.md",
                    "fetched_at": "2026-04-14T05:08:51+0000",
                    "source_snippet": (
                        "**Title:** guardian timeout fix pr 3 - ux touch for timeouts "
                        "**Author:** @won-openai **Merged at:** 2026-04-14T00:43:20Z **Merge commit:** `495ed22` "
                        "This PR teaches the TUI to render guardian review timeouts as explicit terminal history entries instead of dropping them from the live timeline. "
                        "It adds timeout-specific history cells for command, patch, MCP tool, and network approval reviews. "
                        "It also adds snapshot tests covering both the direct guardian event path and the app-server notification path."
                    ),
                    "excerpt": (
                        "**Title:** guardian timeout fix pr 3 - ux touch for timeouts "
                        "**Author:** @won-openai **Merged at:** 2026-04-14T00:43:20Z **Merge commit:** `495ed22` "
                        "This PR teaches the TUI to render guardian review timeouts as explicit terminal history entries instead of dropping them from the live timeline. "
                        "It adds timeout-specific history cells for command, patch, MCP tool, and network approval reviews. "
                        "It also adds snapshot tests covering both the direct guardian event path and the app-server notification path."
                    ),
                },
                {
                    "lane": "openclaw-watch",
                    "title": "openclaw 2026.4.14-beta.1",
                    "source_url": "https://github.com/openclaw/openclaw/releases/tag/v2026.4.14-beta.1",
                    "signal_path": "openclaw-watch/2026-04-14/signals/v2026.4.14-beta.1.md",
                    "fetched_at": "2026-04-14T05:08:56+0000",
                    "source_snippet": (
                        "OpenClaw `2026.4.14-beta.1` is another broad quality release focused on model provider with explicit turn improvements for GPT-5 family and channel provider issues. "
                        "Additionally we improved overal performance with refactors to our underlying core codebase. "
                        "OpenAI Codex/models: add forward-compat support for `gpt-5.4-pro`, including Codex pricing/limits and list/status visibility before the upstream catalog catches up. "
                        "Telegram/forum topics: surface human topic names in agent context, prompt metadata, and plugin hook metadata "
                        "by learning names from Telegram forum service messages. (#65973) "
                        "Models/Codex: include `apiKey` in the codex provider catalog output so the Pi ModelRegistry validator no longer rejects the entry and silently drops all custom models from every provider in `models.json`. "
                        "UI/chat: replace marked.js with markdown-it so maliciously crafted markdown can no longer freeze the Control UI via ReDoS. (#46707) "
                        'Auto-reply/send policy: keep `sendPolicy: "deny"` from blocking inbound message processing, so the agent still runs its turn '
                        "while all outbound delivery is suppressed for observer-style setups. "
                        "Slack/interactions: apply the configured global `allowFrom` owner allowlist to channel block-action and modal interactive events. "
                        "Agents/gateway-tool: reject `config.patch` and `config.apply` calls from the model-facing gateway tool when they would newly enable security-audit flags. "
                        "Heartbeat/security: force owner downgrade for untrusted `hook:wake` system events. "
                        "Microsoft Teams/security: enforce sender allowlist checks on SSO signin invokes."
                    ),
                    "excerpt": (
                        "OpenClaw `2026.4.14-beta.1` is another broad quality release focused on model provider with explicit turn improvements for GPT-5 family and channel provider issues. "
                        "Additionally we improved overal performance with refactors to our underlying core codebase. "
                        "OpenAI Codex/models: add forward-compat support for `gpt-5.4-pro`, including Codex pricing/limits and list/status visibility before the upstream catalog catches up. "
                        "Telegram/forum topics: surface human topic names in agent context, prompt metadata, and plugin hook metadata "
                        "by learning names from Telegram forum service messages. (#65973) "
                        "Models/Codex: include `apiKey` in the codex provider catalog output so the Pi ModelRegistry validator no longer rejects the entry and silently drops all custom models from every provider in `models.json`. "
                        "UI/chat: replace marked.js with markdown-it so maliciously crafted markdown can no longer freeze the Control UI via ReDoS. (#46707) "
                        'Auto-reply/send policy: keep `sendPolicy: "deny"` from blocking inbound message processing, so the agent still runs its turn '
                        "while all outbound delivery is suppressed for observer-style setups. "
                        "Slack/interactions: apply the configured global `allowFrom` owner allowlist to channel block-action and modal interactive events. "
                        "Agents/gateway-tool: reject `config.patch` and `config.apply` calls from the model-facing gateway tool when they would newly enable security-audit flags. "
                        "Heartbeat/security: force owner downgrade for untrusted `hook:wake` system events. "
                        "Microsoft Teams/security: enforce sender allowlist checks on SSO signin invokes."
                    ),
                },
                {
                    "lane": "polymarket-watch",
                    "title": "Will Anthropic have the second-best Coding AI model at the end of April 2026?",
                    "source_url": "https://polymarket.com/event/which-company-has-the-second-best-coding-ai-model-end-of-april",
                    "signal_path": "polymarket-watch/2026-04-14/signals/anthropic.md",
                    "fetched_at": "2026-04-14T05:09:39+0000",
                    "source_snippet": (
                        "Market: Which company has the second best Coding AI model end of April? "
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%) "
                        "Anthropic: 90.0% OpenAI: 3.3% xAI: 3.0% "
                        "24h volume: 369.0 30d volume: 7,419.1 Liquidity: 42,649.1 Price movement: up 1.0% this week"
                    ),
                    "excerpt": (
                        "Market: Which company has the second best Coding AI model end of April? "
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%) "
                        "Anthropic: 90.0% OpenAI: 3.3% xAI: 3.0% "
                        "24h volume: 369.0 30d volume: 7,419.1 Liquidity: 42,649.1 Price movement: up 1.0% this week"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 4,
                "lane_counts": [
                    {"lane": "claude-code-watch", "selected_item_count": 1},
                    {"lane": "codex-watch", "selected_item_count": 1},
                    {"lane": "openclaw-watch", "selected_item_count": 1},
                    {"lane": "polymarket-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        claude_line = next(line for line in body_markdown.splitlines() if "**v2.1.105**" in line)
        self.assertIn("EnterWorktree", claude_line)
        self.assertIn("`path`", claude_line)
        self.assertIn("PreCompact", claude_line)
        self.assertIn("`monitors`", claude_line)
        self.assertNotIn("原文围绕 v2.1.105 展开，具体变化见来源", claude_line)

        codex_line = next(
            line for line in body_markdown.splitlines() if "**guardian timeout fix pr 3 - ux touch for timeouts**" in line
        )
        self.assertIn("PR #17557", codex_line)
        self.assertIn("@won-openai", codex_line)
        self.assertIn("2026-04-14", codex_line)
        self.assertIn("guardian review timeout", codex_line)
        self.assertIn("495ed22", codex_line)
        self.assertIn("command", codex_line)
        self.assertIn("MCP tool", codex_line)
        self.assertIn("app-server notification path", codex_line)

        openclaw_line = next(line for line in body_markdown.splitlines() if "**openclaw 2026.4.14-beta.1**" in line)
        self.assertIn("Telegram", openclaw_line)
        self.assertIn("markdown-it", openclaw_line)
        self.assertIn("ReDoS", openclaw_line)
        self.assertIn('sendPolicy: "deny"', openclaw_line)
        self.assertTrue("hook:wake" in openclaw_line or "SSRF" in openclaw_line or "sender allowlist" in openclaw_line)
        self.assertNotIn("原文围绕 openclaw 2026.4.14-beta.1 展开，具体变化见来源", openclaw_line)

        market_line = next(
            line
            for line in body_markdown.splitlines()
            if "**Will Anthropic have the second-best Coding AI model at the end of April 2026?**" in line
        )
        self.assertIn("Anthropic", market_line)
        self.assertIn("90.0%", market_line)
        self.assertIn("OpenAI", market_line)
        self.assertIn("369.0", market_line)
        self.assertIn("42,649.1", market_line)

    def test_build_report_artifact_live_like_truncated_english_tail_is_rewritten_not_dumped_verbatim(self) -> None:
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
                    "title": "@addyosmani #89",
                    "source_url": "https://x.com/addyosmani/status/2043447970507686248",
                    "signal_path": "x-feed/2026-04-14/signals/addyosmani.md",
                    "fetched_at": "2026-04-14T05:06:43+0000",
                    "source_snippet": (
                        "Memory makes your agent smarter over time. "
                        "The agent harness is key to the memory layer. "
                        "You can't bolt one onto"
                    ),
                    "excerpt": (
                        "Memory makes your agent smarter over time. "
                        "The agent harness is key to the memory layer. "
                        "You can't bolt one onto"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(line for line in artifact["body_markdown"].splitlines() if "**@addyosmani #89**" in line)

        self.assertIn("memory", body_line.lower())
        self.assertIn("harness", body_line)
        self.assertIn("不能事后", body_line)
        self.assertNotIn("You can't bolt one onto", body_line)
        self.assertNotIn("原文围绕 harness 展开，具体变化见来源", body_line)

    def test_build_report_artifact_real_x_following_english_snippets_use_facts_not_generic_placeholders(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-following", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-following",
                    "title": "@robertwiblin",
                    "source_url": "https://x.com/robertwiblin/status/2044017526992994466",
                    "signal_path": "x-following/2026-04-14/signals/robertwiblin__post__2044017526992994466.md",
                    "fetched_at": "2026-04-14T14:24:00+0000",
                    "source_snippet": (
                        "RT @StefanFSchubert: Anthropic overtakes OpenAI on Ventuals, "
                        "a (small) market for private company valuations https://t.c"
                    ),
                    "excerpt": (
                        "RT @StefanFSchubert: Anthropic overtakes OpenAI on Ventuals, "
                        "a (small) market for private company valuations https://t.c"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@Dimillian",
                    "source_url": "https://x.com/Dimillian/status/2043963889532940473",
                    "signal_path": "x-following/2026-04-14/signals/Dimillian__post__2043963889532940473.md",
                    "fetched_at": "2026-04-14T14:24:00+0000",
                    "source_snippet": (
                        "I’m diligently working on enhancing all the features of the Codex app "
                        "to make it even better for you. If you have any su"
                    ),
                    "excerpt": (
                        "I’m diligently working on enhancing all the features of the Codex app "
                        "to make it even better for you. If you have any su"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [{"lane": "x-following", "selected_item_count": 2}],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        robert_line = next(line for line in artifact["body_markdown"].splitlines() if "**@robertwiblin**" in line)
        dimillian_line = next(line for line in artifact["body_markdown"].splitlines() if "**@Dimillian**" in line)

        self.assertIn("Anthropic", robert_line)
        self.assertIn("OpenAI", robert_line)
        self.assertTrue("Ventuals" in robert_line or "估值" in robert_line)
        self.assertNotIn("原文围绕 Anthropic 展开，具体变化见来源", robert_line)

        self.assertIn("Codex app", dimillian_line)
        self.assertTrue("增强" in dimillian_line or "功能" in dimillian_line)
        self.assertNotIn("原文围绕 Codex 展开，具体变化见来源", dimillian_line)

    def test_build_report_artifact_generic_english_repo_and_product_snippets_turn_into_chinese_facts(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1},
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "github-trending-weekly",
                    "title": "seomachine",
                    "source_url": "https://github.com/TheCraigHewitt/seomachine",
                    "signal_path": "github-trending-weekly/2026-04-14/signals/TheCraigHewitt__seomachine.md",
                    "fetched_at": "2026-04-14T05:09:28+0000",
                    "source_snippet": (
                        "A specialized Claude Code workspace for creating long-form, SEO-optimized blog content for any business. "
                        "This system helps you research, write, analyze, and optimize content that ranks well and serves "
                        "**Author:** @TheCraigHewitt/seomachine"
                    ),
                    "excerpt": (
                        "A specialized Claude Code workspace for creating long-form, SEO-optimized blog content for any business. "
                        "This system helps you research, write, analyze, and optimize content that ranks well and serves "
                        "**Author:** @TheCraigHewitt/seomachine"
                    ),
                },
                {
                    "lane": "product-hunt-watch",
                    "title": "SuperHQ — Run AI coding agents in real microVM sandboxes",
                    "source_url": (
                        "https://www.producthunt.com/products/superhq?"
                        "utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=test"
                    ),
                    "signal_path": "product-hunt-watch/2026-04-14/signals/superhq.md",
                    "fetched_at": "2026-04-14T05:09:35+0000",
                    "source_snippet": "Run AI coding agents in real microVM sandboxes **Author:** @SuperHQ",
                    "excerpt": "Run AI coding agents in real microVM sandboxes **Author:** @SuperHQ",
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "github-trending-weekly", "selected_item_count": 1},
                    {"lane": "product-hunt-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        seomachine_line = next(line for line in artifact["body_markdown"].splitlines() if "**seomachine**" in line)
        superhq_line = next(
            line
            for line in artifact["body_markdown"].splitlines()
            if "**SuperHQ — Run AI coding agents in real microVM sandboxes**" in line
        )

        self.assertIn("SEO", seomachine_line)
        self.assertTrue("博客" in seomachine_line or "内容" in seomachine_line)
        self.assertNotIn("A specialized Claude Code workspace for creating long-form", seomachine_line)
        self.assertNotIn("原文围绕 Claude Code 展开，具体变化见来源", seomachine_line)

        self.assertIn("microVM", superhq_line)
        self.assertTrue("沙箱" in superhq_line or "跑在" in superhq_line)
        self.assertNotIn("Run AI coding agents in real microVM sandboxes。", superhq_line)

    def test_build_report_artifact_rewrites_obvious_english_listing_and_market_copy_before_reader_output(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1},
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 1},
                {"name": "polymarket-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 3, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "github-trending-weekly",
                    "title": "claude-mem",
                    "source_url": "https://github.com/thedotmack/claude-mem",
                    "signal_path": "github-trending-weekly/2026-04-16/signals/claude-mem.md",
                    "fetched_at": "2026-04-16T00:00:00+0000",
                    "source_snippet": (
                        "A Claude Code plugin that automatically captures everything Claude does during your coding sessions, "
                        "compresses it with AI, and injects relevant context back into future sessions. "
                        "Author: @thedotmack/claude-mem"
                    ),
                    "excerpt": (
                        "A Claude Code plugin that automatically captures everything Claude does during your coding sessions, "
                        "compresses it with AI, and injects relevant context back into future sessions. "
                        "Author: @thedotmack/claude-mem"
                    ),
                },
                {
                    "lane": "product-hunt-watch",
                    "title": "Hapax",
                    "source_url": "https://www.producthunt.com/products/hapax",
                    "signal_path": "product-hunt-watch/2026-04-16/signals/hapax.md",
                    "fetched_at": "2026-04-16T00:00:00+0000",
                    "source_snippet": (
                        "Watches your workflows. Builds your Agents. Automates the busywork. Topic: Artificial Intelligence"
                    ),
                    "excerpt": (
                        "Watches your workflows. Builds your Agents. Automates the busywork. Topic: Artificial Intelligence"
                    ),
                },
                {
                    "lane": "polymarket-watch",
                    "title": "Anthropic 排名市场",
                    "source_url": "https://polymarket.com/event/which-company-has-the-second-best-coding-ai-model-end-of-april",
                    "signal_path": "polymarket-watch/2026-04-16/signals/anthropic.md",
                    "fetched_at": "2026-04-16T00:00:00+0000",
                    "source_snippet": (
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%) OpenAI: 3.5% 24h volume: 137.1 Liquidity: 29,891.4"
                    ),
                    "excerpt": (
                        "Question: Will Anthropic have the second-best Coding AI model at the end of April 2026? "
                        "Current leader: Anthropic (90.0%) OpenAI: 3.5% 24h volume: 137.1 Liquidity: 29,891.4"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 3,
                "lane_counts": [
                    {"lane": "github-trending-weekly", "selected_item_count": 1},
                    {"lane": "product-hunt-watch", "selected_item_count": 1},
                    {"lane": "polymarket-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        claude_mem_line = next(line for line in artifact["body_markdown"].splitlines() if "**claude-mem**" in line)
        hapax_line = next(line for line in artifact["body_markdown"].splitlines() if "**Hapax**" in line)
        market_line = next(line for line in artifact["body_markdown"].splitlines() if "**Anthropic 排名市场**" in line)

        self.assertIn("Claude Code", claude_mem_line)
        self.assertTrue("插件" in claude_mem_line or "上下文" in claude_mem_line)
        self.assertNotIn("A Claude Code plugin that automatically captures everything Claude does", claude_mem_line)

        self.assertTrue("工作流" in hapax_line or "自动化" in hapax_line)
        self.assertNotIn("Watches your workflows. Builds your Agents. Automates the busywork.", hapax_line)

        self.assertIn("Anthropic", market_line)
        self.assertTrue("第二强" in market_line or "排名" in market_line)
        self.assertNotIn("Will Anthropic have the second-best Coding AI model at the end of April 2026?", market_line)

    def test_build_report_artifact_weather_rewrites_up_to_and_cardinal_wind_into_chinese(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "weather-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "weather-watch",
                    "title": "Beijing Haidian Weather",
                    "source_url": "https://weather.example.com/beijing-haidian/2026-04-20",
                    "signal_path": "weather-watch/2026-04-20/signals/beijing-haidian.md",
                    "fetched_at": "2026-04-20T05:30:00+0000",
                    "source_snippet": (
                        "Condition: Cloudy to sunny Temperature: 11°C to 23°C "
                        "Precipitation: none Wind: up to 22 km/h NW"
                    ),
                    "excerpt": "Condition: Cloudy to sunny Temperature: 11°C to 23°C",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "weather-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(line for line in artifact["body_markdown"].splitlines() if "**今日天气**" in line)

        self.assertIn("多云转晴", body_line)
        self.assertIn("11°C - 23°C", body_line)
        self.assertIn("无明显降水", body_line)
        self.assertIn("西北风", body_line)
        self.assertIn("22 km/h", body_line)
        self.assertNotIn("up to", body_line)
        self.assertNotIn("NW", body_line)
        self.assertNotIn("Condition:", body_line)
        self.assertNotIn("该栏目收录", artifact["body_markdown"])

    def test_build_report_artifact_sparse_codex_support_copy_turns_chinese_first(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "codex-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "codex-watch",
                    "title": "clarify macOS Intel + Windows support wording",
                    "source_url": "https://github.com/openai/codex/pull/17666",
                    "signal_path": "codex-watch/2026-04-20/signals/17666.md",
                    "fetched_at": "2026-04-20T08:03:11+0000",
                    "source_snippet": (
                        "**Title:** clarify macOS Intel + Windows support wording "
                        "**Author:** @sally-openai **Merged at:** 2026-04-20T08:03:11Z "
                        "**Merge commit:** `abc1234` "
                        "This PR clarifies installation and support messaging for macOS Intel and Windows users."
                    ),
                    "excerpt": (
                        "**Title:** clarify macOS Intel + Windows support wording "
                        "**Author:** @sally-openai **Merged at:** 2026-04-20T08:03:11Z "
                        "**Merge commit:** `abc1234` "
                        "This PR clarifies installation and support messaging for macOS Intel and Windows users."
                    ),
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "codex-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(
            line for line in artifact["body_markdown"].splitlines() if "**clarify macOS Intel + Windows support wording**" in line
        )

        self.assertIn("PR #17666", body_line)
        self.assertIn("@sally-openai", body_line)
        self.assertIn("macOS Intel", body_line)
        self.assertIn("Windows", body_line)
        self.assertTrue("支持" in body_line or "安装说明" in body_line)
        self.assertNotIn("This PR clarifies installation and support messaging", body_line)
        self.assertNotIn("原文围绕 clarify macOS Intel + Windows support wording 展开", body_line)
        self.assertNotIn("该栏目收录", artifact["body_markdown"])

    def test_build_report_artifact_github_trending_engineering_skills_stays_chinese_first_and_factual(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "github-trending-weekly",
                    "title": "agent-skills",
                    "source_url": "https://github.com/example/agent-skills",
                    "signal_path": "github-trending-weekly/2026-04-20/signals/agent-skills.md",
                    "fetched_at": "2026-04-20T08:20:00+0000",
                    "source_snippet": (
                        "Production-grade engineering skills for AI coding agents. "
                        "Includes repo setup, review loops, and delivery checklists that teams can reuse."
                    ),
                    "excerpt": (
                        "Production-grade engineering skills for AI coding agents. "
                        "Includes repo setup, review loops, and delivery checklists that teams can reuse."
                    ),
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "github-trending-weekly", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(line for line in artifact["body_markdown"].splitlines() if "**agent-skills**" in line)

        self.assertTrue("生产级" in body_line or "工程技能" in body_line)
        self.assertTrue("评审" in body_line or "checklist" in body_line)
        self.assertNotIn("Production-grade engineering skills for AI coding agents", body_line)
        self.assertNotIn("项目说明主要在讲它的定位、工作流和使用场景", body_line)
        self.assertNotIn("该栏目收录", artifact["body_markdown"])

    def test_build_report_artifact_product_hunt_ai_taglines_turn_into_chinese_explanations(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "product-hunt-watch",
                    "title": "Forgebase — Your AI Technical Cofounder",
                    "source_url": "https://www.producthunt.com/posts/forgebase",
                    "signal_path": "product-hunt-watch/2026-04-20/signals/forgebase.md",
                    "fetched_at": "2026-04-20T09:00:00+0000",
                    "source_snippet": (
                        "Your AI Technical Cofounder. Build product strategy, ship features, and unblock engineering follow-through. "
                        "Votes: 188 Comments: 11 Topic: Artificial Intelligence"
                    ),
                    "excerpt": (
                        "Your AI Technical Cofounder. Build product strategy, ship features, and unblock engineering follow-through. "
                        "Votes: 188 Comments: 11 Topic: Artificial Intelligence"
                    ),
                },
                {
                    "lane": "product-hunt-watch",
                    "title": "SkillSprint — Practice & assess future-ready skills with AI-simulated team",
                    "source_url": "https://www.producthunt.com/posts/skillsprint",
                    "signal_path": "product-hunt-watch/2026-04-20/signals/skillsprint.md",
                    "fetched_at": "2026-04-20T09:05:00+0000",
                    "source_snippet": (
                        "Practice & assess future-ready skills with AI-simulated team. "
                        "Topic: Education Votes: 96 Comments: 7"
                    ),
                    "excerpt": (
                        "Practice & assess future-ready skills with AI-simulated team. "
                        "Topic: Education Votes: 96 Comments: 7"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "product-hunt-watch", "selected_item_count": 2},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]
        forgebase_line = next(line for line in body_markdown.splitlines() if "Forgebase" in line)
        skillsprint_line = next(line for line in body_markdown.splitlines() if "SkillSprint" in line)

        self.assertIn("AI 技术联合创始人", forgebase_line)
        self.assertIn("你的 AI 技术联合创始人", forgebase_line)
        self.assertTrue("AI 模拟团队" in skillsprint_line or "面向未来的技能" in skillsprint_line)
        self.assertIn("用 AI 模拟团队来练习并评估面向未来的技能", skillsprint_line)
        self.assertNotIn("该栏目收录", body_markdown)

    def test_build_report_artifact_general_phrase_localizer_keeps_product_name_but_translates_design_context(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "product-hunt-watch",
                    "title": "Nicelydone MCP — Design context for AI agents",
                    "source_url": "https://www.producthunt.com/products/nicely-done",
                    "signal_path": "product-hunt-watch/2026-04-20/signals/nicelydone.md",
                    "fetched_at": "2026-04-20T09:20:00+0000",
                    "source_snippet": "Design context for AI agents. Topic: Artificial Intelligence Votes: 44 Comments: 3",
                    "excerpt": "Design context for AI agents. Topic: Artificial Intelligence Votes: 44 Comments: 3",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [
                    {"lane": "product-hunt-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(line for line in artifact["body_markdown"].splitlines() if "Nicelydone MCP" in line)

        self.assertIn("Nicelydone MCP", body_line)
        self.assertIn("给 AI agents 提供设计上下文", body_line)
        self.assertNotIn("该栏目收录", artifact["body_markdown"])

    def test_build_report_artifact_live_like_reddit_second_wave_fallbacks_replace_reader_placeholders(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "reddit-watch", "status": "ok", "useful_item_count": 32},
            ],
            "summary": {"useful_item_count": 32, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "reddit-watch",
                    "title": "Peter Steinberger (OpenClaw Creator) credits Boris Cherny (Claude Code Creator) amid anthropic subscription ban for using openclaw",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1scigaq/peter_steinberger_openclaw_creator_credits_boris/",
                    "signal_path": "reddit-watch/2026-04-20/signals/peter-boris.md",
                    "fetched_at": "2026-04-20T09:00:00+0000",
                    "selection_bucket": "heat",
                    "source_snippet": (
                        "Boris Cherny's life story is pretty inspirational. At one point he was homeless and used "
                        "to sleep in his car before turning around his life and now becoming the CTO of claude code."
                    ),
                    "excerpt": (
                        "Boris Cherny's life story is pretty inspirational. At one point he was homeless and used "
                        "to sleep in his car before turning around his life and now becoming the CTO of claude code."
                    ),
                },
                {
                    "lane": "reddit-watch",
                    "title": "Has anyone here actually made money with Claude Code Agents / OpenClaw?",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1s95796/has_anyone_here_actually_made_money_with_claude/",
                    "signal_path": "reddit-watch/2026-04-20/signals/made-money.md",
                    "fetched_at": "2026-04-20T09:05:00+0000",
                    "selection_bucket": "voice",
                    "source_snippet": (
                        "I keep seeing wild claims that Claude Code / Open Claw bots made $60K, but I can't tell "
                        "what's real versus hype. What are you actually using it for, and has it generated revenue, "
                        "saved time, or replaced a hire?"
                    ),
                    "excerpt": (
                        "I keep seeing wild claims that Claude Code / Open Claw bots made $60K, but I can't tell "
                        "what's real versus hype. What are you actually using it for, and has it generated revenue, "
                        "saved time, or replaced a hire?"
                    ),
                },
                {
                    "lane": "reddit-watch",
                    "title": "The gap between what technical and non-technical people get from AI is huge now",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1spnb80/the_gap_between_what_technical_and_nontechnical/",
                    "signal_path": "reddit-watch/2026-04-20/signals/gap.md",
                    "fetched_at": "2026-04-20T09:10:00+0000",
                    "selection_bucket": "voice",
                    "source_snippet": (
                        "Non-technical users still treat LLMs as better search, while technical users know about "
                        "thinking effort, model choice, plugins, automations, skills, and agents."
                    ),
                    "excerpt": (
                        "Non-technical users still treat LLMs as better search, while technical users know about "
                        "thinking effort, model choice, plugins, automations, skills, and agents."
                    ),
                },
                {
                    "lane": "reddit-watch",
                    "title": "I built an open-source plugin that gives Claude Code autonomous iteration with parallel agents and failure memory. 126 skills, works on Cursor/Codex/Gemini too.",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1sdteey/i_built_an_opensource_plugin_that_gives_claude/",
                    "signal_path": "reddit-watch/2026-04-20/signals/godmode.md",
                    "fetched_at": "2026-04-20T09:15:00+0000",
                    "selection_bucket": "voice",
                    "source_snippet": (
                        "I built Godmode to add an autonomous loop to Claude Code: measure, modify, verify, keep or "
                        "revert, repeat. Every change is committed before verification and bad changes get auto-reverted."
                    ),
                    "excerpt": (
                        "I built Godmode to add an autonomous loop to Claude Code: measure, modify, verify, keep or "
                        "revert, repeat. Every change is committed before verification and bad changes get auto-reverted."
                    ),
                },
                {
                    "lane": "reddit-watch",
                    "title": "Why are people running Claude Code on a Mac mini instead of their personal MacBook?",
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/1sgix71/why_are_people_running_claude_code_on_a_mac_mini/",
                    "signal_path": "reddit-watch/2026-04-20/signals/mac-mini.md",
                    "fetched_at": "2026-04-20T09:20:00+0000",
                    "selection_bucket": "voice",
                    "source_snippet": (
                        "The thread is asking whether Mac mini setups are better because they stay dedicated and "
                        "online 24/7, or because of real performance, cost, convenience, and remote access benefits."
                    ),
                    "excerpt": (
                        "The thread is asking whether Mac mini setups are better because they stay dedicated and "
                        "online 24/7, or because of real performance, cost, convenience, and remote access benefits."
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 5,
                "lane_counts": [
                    {"lane": "reddit-watch", "selected_item_count": 5},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]
        made_money_line = next(
            line for line in body_markdown.splitlines() if "https://www.reddit.com/r/ClaudeAI/comments/1s95796/" in line
        )
        gap_line = next(
            line for line in body_markdown.splitlines() if "https://www.reddit.com/r/ClaudeAI/comments/1spnb80/" in line
        )
        godmode_line = next(
            line for line in body_markdown.splitlines() if "https://www.reddit.com/r/ClaudeAI/comments/1sdteey/" in line
        )
        mac_mini_line = next(
            line for line in body_markdown.splitlines() if "https://www.reddit.com/r/ClaudeAI/comments/1sgix71/" in line
        )
        peter_line = next(
            line for line in body_markdown.splitlines() if "https://www.reddit.com/r/ClaudeAI/comments/1scigaq/" in line
        )

        self.assertNotIn("该栏目收录 32 条有用内容", body_markdown)
        self.assertIn("变现", made_money_line)
        self.assertTrue("提效" in made_money_line or "省时间" in made_money_line)
        self.assertIn("技术用户", gap_line)
        self.assertIn("非技术用户", gap_line)
        self.assertTrue("模型选择" in gap_line or "agents" in gap_line)
        self.assertIn("Godmode", godmode_line)
        self.assertTrue("并行" in godmode_line or "parallel agents" in godmode_line)
        self.assertTrue("自动回滚" in godmode_line or "回滚" in godmode_line)
        self.assertIn("Mac mini", mac_mini_line)
        self.assertTrue("常驻" in mac_mini_line or "24/7" in mac_mini_line)
        self.assertTrue("远程" in mac_mini_line or "成本" in mac_mini_line)
        self.assertIn("Peter Steinberger", peter_line)
        self.assertIn("Boris Cherny", peter_line)
        self.assertTrue("OpenClaw" in peter_line or "Claude Code" in peter_line)

    def test_build_report_artifact_live_like_github_trending_second_wave_fallbacks_replace_generic_placeholder(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "github-trending-weekly", "status": "ok", "useful_item_count": 3},
            ],
            "summary": {"useful_item_count": 3, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "github-trending-weekly",
                    "title": "agent-skills",
                    "source_url": "https://github.com/addyosmani/agent-skills",
                    "signal_path": "github-trending-weekly/2026-04-20/signals/agent-skills.md",
                    "fetched_at": "2026-04-20T10:00:00+0000",
                    "source_snippet": (
                        "**Production-grade engineering skills for AI coding agents.** Skills encode the workflows, "
                        "quality gates, and best practices that senior engineers use when building software. These "
                        "ones are packaged so AI agents follow them consistently across every phase of development."
                    ),
                    "excerpt": (
                        "**Production-grade engineering skills for AI coding agents.** Skills encode the workflows, "
                        "quality gates, and best practices that senior engineers use when building software. These "
                        "ones are packaged so AI agents follow them consistently across every phase of development."
                    ),
                },
                {
                    "lane": "github-trending-weekly",
                    "title": "android-reverse-engineering-skill",
                    "source_url": "https://github.com/SimoneAvogadro/android-reverse-engineering-skill",
                    "signal_path": "github-trending-weekly/2026-04-20/signals/android-reverse-engineering-skill.md",
                    "fetched_at": "2026-04-20T10:05:00+0000",
                    "source_snippet": (
                        "A Claude Code skill that decompiles Android APK/XAPK/JAR/AAR files and extracts the HTTP APIs "
                        "used by the app so you can document and reproduce them without the original source code."
                    ),
                    "excerpt": (
                        "A Claude Code skill that decompiles Android APK/XAPK/JAR/AAR files and extracts the HTTP APIs "
                        "used by the app so you can document and reproduce them without the original source code."
                    ),
                },
                {
                    "lane": "github-trending-weekly",
                    "title": "markitdown",
                    "source_url": "https://github.com/microsoft/markitdown",
                    "signal_path": "github-trending-weekly/2026-04-20/signals/markitdown.md",
                    "fetched_at": "2026-04-20T10:10:00+0000",
                    "source_snippet": (
                        "![PyPI](badge) ![Downloads](badge) > [!TIP] > MarkItDown now offers an MCP (Model Context "
                        "Protocol) server for integration with LLM applications like Claude Desktop. > [!IMPORTANT] "
                        "> Breaking changes between 0.0.1 to 0.1.0: dependencies are now organized into optional "
                        "feature-groups."
                    ),
                    "excerpt": (
                        "![PyPI](badge) ![Downloads](badge) > [!TIP] > MarkItDown now offers an MCP (Model Context "
                        "Protocol) server for integration with LLM applications like Claude Desktop. > [!IMPORTANT] "
                        "> Breaking changes between 0.0.1 to 0.1.0: dependencies are now organized into optional "
                        "feature-groups."
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 3,
                "lane_counts": [
                    {"lane": "github-trending-weekly", "selected_item_count": 3},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]
        agent_skills_line = next(line for line in body_markdown.splitlines() if "https://github.com/addyosmani/agent-skills" in line)
        android_line = next(
            line
            for line in body_markdown.splitlines()
            if "https://github.com/SimoneAvogadro/android-reverse-engineering-skill" in line
        )
        markitdown_line = next(line for line in body_markdown.splitlines() if "https://github.com/microsoft/markitdown" in line)

        self.assertNotIn("项目说明主要在讲它的定位、工作流和使用场景", body_markdown)
        self.assertTrue("生产级" in agent_skills_line or "工程技能" in agent_skills_line)
        self.assertTrue("质量门槛" in agent_skills_line or "工作流" in agent_skills_line or "最佳实践" in agent_skills_line)
        self.assertTrue("反编译" in android_line or "提取" in android_line)
        self.assertIn("HTTP API", android_line)
        self.assertIn("MCP", markitdown_line)
        self.assertTrue("Claude Desktop" in markitdown_line or "LLM" in markitdown_line)

    def test_build_report_artifact_live_like_product_hunt_second_wave_localizes_generic_english_taglines(self) -> None:
        report_date = "2026-04-20"
        collect_result = {
            "report_date": report_date,
            "source": "signals-engine",
            "lanes": [
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": report_date,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "product-hunt-watch",
                    "title": "Fixa.dev — A cloud-native AI agent that can build literally anything",
                    "source_url": "https://www.producthunt.com/products/fixa-dev",
                    "signal_path": "product-hunt-watch/2026-04-20/signals/fixa-dev.md",
                    "fetched_at": "2026-04-20T11:00:00+0000",
                    "source_snippet": "Votes: 87 Comments: 5 Topic: Developer Tools",
                    "excerpt": "Votes: 87 Comments: 5 Topic: Developer Tools",
                },
                {
                    "lane": "product-hunt-watch",
                    "title": "Avina — GTM Agents to Find and Reach Your Next Customer",
                    "source_url": "https://www.producthunt.com/products/avina-2",
                    "signal_path": "product-hunt-watch/2026-04-20/signals/avina.md",
                    "fetched_at": "2026-04-20T11:05:00+0000",
                    "source_snippet": "Votes: 170 Comments: 10 Topic: Artificial Intelligence",
                    "excerpt": "Votes: 170 Comments: 10 Topic: Artificial Intelligence",
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "product-hunt-watch", "selected_item_count": 2},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]
        fixa_line = next(line for line in body_markdown.splitlines() if "https://www.producthunt.com/products/fixa-dev" in line)
        avina_line = next(line for line in body_markdown.splitlines() if "https://www.producthunt.com/products/avina-2" in line)

        self.assertNotIn("A cloud-native AI agent that can build literally anything", body_markdown)
        self.assertNotIn("GTM Agents to Find and Reach Your Next Customer", body_markdown)
        self.assertIn("Fixa.dev", fixa_line)
        self.assertTrue("cloud-native" in fixa_line or "云原生" in fixa_line)
        self.assertTrue("几乎什么都能构建" in fixa_line or "什么都能做" in fixa_line)
        self.assertIn("Avina", avina_line)
        self.assertTrue("找" in avina_line or "获取" in avina_line)
        self.assertTrue("触达" in avina_line or "客户" in avina_line)
        self.assertNotIn("该栏目收录", body_markdown)

    def test_build_report_artifact_sparse_release_without_notes_uses_non_placeholder_summary(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.104",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.104",
                    "signal_path": "claude-code-watch/2026-04-14/signals/anthropics__claude-code__release__v2.1.104.md",
                    "fetched_at": "2026-04-14T14:25:24+0000",
                    "source_snippet": "",
                    "excerpt": "",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "claude-code-watch", "selected_item_count": 1}],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_line = next(line for line in artifact["body_markdown"].splitlines() if "**v2.1.104**" in line)

        self.assertIn("Claude Code", body_line)
        self.assertIn("v2.1.104", body_line)
        self.assertTrue("release" in body_line.lower() or "版本更新" in body_line)
        self.assertNotIn("原文围绕 v2.1.104 展开，具体变化见来源", body_line)

    def test_build_report_artifact_sparse_live_items_use_minimal_fact_sentences_instead_of_editor_placeholders(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 2},
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
                {"name": "openclaw-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 4, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@ClaudeCodeLog #23",
                    "source_url": "https://x.com/ClaudeCodeLog/status/2043835961755189345",
                    "signal_path": "x-feed/2026-04-14/signals/ClaudeCodeLog__feed__2043835961755189345.md",
                    "fetched_at": "2026-04-14T14:51:14+0000",
                    "source_snippet": (
                        "Claude Code 2.1.105 has been released. "
                        "2 flag changes, 37 CLI changes, 4 system prompt changes "
                        "Highlights: • claude-ap"
                    ),
                    "excerpt": (
                        "Claude Code 2.1.105 has been released. "
                        "2 flag changes, 37 CLI changes, 4 system prompt changes "
                        "Highlights: • claude-ap"
                    ),
                },
                {
                    "lane": "x-feed",
                    "title": "@AndrewYNg #51",
                    "source_url": "https://x.com/AndrewYNg/status/2043742105852621052",
                    "signal_path": "x-feed/2026-04-14/signals/AndrewYNg__feed__2043742105852621052.md",
                    "fetched_at": "2026-04-14T14:51:14+0000",
                    "source_snippet": (
                        "As AI agents accelerate coding, what is the future of software engineering? "
                        "Some trends are clear, such as the Product M"
                    ),
                    "excerpt": (
                        "As AI agents accelerate coding, what is the future of software engineering? "
                        "Some trends are clear, such as the Product M"
                    ),
                },
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.107",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.107",
                    "signal_path": "claude-code-watch/2026-04-14/signals/anthropics__claude-code__release__v2.1.107.md",
                    "fetched_at": "2026-04-14T14:52:33+0000",
                    "source_snippet": "Show thinking hints sooner during long operations",
                    "excerpt": "Show thinking hints sooner during long operations",
                },
                {
                    "lane": "openclaw-watch",
                    "title": "openclaw 2026.4.14",
                    "source_url": "https://github.com/openclaw/openclaw/releases/tag/v2026.4.14",
                    "signal_path": "openclaw-watch/2026-04-14/signals/openclaw__openclaw__release__v2026.4.14.md",
                    "fetched_at": "2026-04-14T14:54:06+0000",
                    "source_snippet": (
                        "OpenClaw `2026.4.14` is another broad quality release focused on model provider "
                        "with explicit turn improvements for GPT-5 family and channel provider issues. "
                        "Additionally we improved overal performance with refactors to our underlying core codebase."
                    ),
                    "excerpt": (
                        "OpenClaw `2026.4.14` is another broad quality release focused on model provider "
                        "with explicit turn improvements for GPT-5 family and channel provider issues. "
                        "Additionally we improved overal performance with refactors to our underlying core codebase."
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 4,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 2},
                    {"lane": "claude-code-watch", "selected_item_count": 1},
                    {"lane": "openclaw-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        claudecodelog_line = next(
            line for line in body_markdown.splitlines() if "**@ClaudeCodeLog #23" in line
        )
        self.assertIn("Claude Code 2.1.105", claudecodelog_line)
        self.assertTrue("37 CLI changes" in claudecodelog_line or "2 flag changes" in claudecodelog_line)
        self.assertNotIn("原文围绕 Claude Code 展开，具体变化见来源", claudecodelog_line)
        self.assertNotIn("claude-ap", claudecodelog_line)

        andrew_line = next(line for line in body_markdown.splitlines() if "**@AndrewYNg #51" in line)
        self.assertIn("AI agents", andrew_line)
        self.assertIn("software engineering", andrew_line)
        self.assertNotIn("原文围绕 X 推荐流 展开，具体变化见来源", andrew_line)
        self.assertNotIn("Product M", andrew_line)

        claude_release_line = next(line for line in body_markdown.splitlines() if "**v2.1.107**" in line)
        self.assertIn("Claude Code", claude_release_line)
        self.assertIn("v2.1.107", claude_release_line)
        self.assertTrue("thinking hints" in claude_release_line or "release" in claude_release_line.lower())
        self.assertNotIn("原文围绕 v2.1.107 展开，具体变化见来源", claude_release_line)

        openclaw_line = next(line for line in body_markdown.splitlines() if "**openclaw 2026.4.14**" in line)
        self.assertIn("OpenClaw", openclaw_line)
        self.assertIn("2026.4.14", openclaw_line)
        self.assertTrue("GPT-5" in openclaw_line or "model provider" in openclaw_line or "release" in openclaw_line.lower())
        self.assertNotIn("原文围绕 openclaw 2026.4.14 展开，具体变化见来源", openclaw_line)

    def test_build_report_artifact_dense_live_like_claude_and_openclaw_entries_keep_more_groups(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
                {"name": "openclaw-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.105",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.105",
                    "signal_path": "claude-code-watch/2026-04-14/signals/v2.1.105.md",
                    "fetched_at": "2026-04-14T05:07:39+0000",
                    "source_snippet": (
                        "Added `path` parameter to the `EnterWorktree` tool to switch into an existing worktree of the current repository "
                        "Added PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning "
                        '`{"decision":"block"}` '
                        "Added background monitor support for plugins via a top-level `monitors` manifest key that auto-arms at session start or on skill invoke "
                        "`/proactive` is now an alias for `/loop` "
                        "Improved stalled API stream handling: streams now abort after 5 minutes of no data and retry non-streaming instead of hanging indefinitely "
                        "Improved network error messages: connection errors now show a retry message immediately instead of a silent spinner "
                        "Improved `/doctor` layout with status icons; press `f` to have Claude fix reported issues "
                        "Improved `WebFetch` to strip `<style>` and `<script>` contents from fetched pages so CSS-heavy pages no longer exhaust the content budget before reaching actual text "
                        "Improved MCP large-output truncation prompt to give format-specific recipes (e.g. `jq` for JSON, computed Read chunk sizes for text) "
                        "Fixed queued user prompts disappearing from focus mode "
                        "Fixed images attached to queued messages (sent while Claude is working) being dropped"
                    ),
                    "excerpt": "v2.1.105 dense summary",
                },
                {
                    "lane": "openclaw-watch",
                    "title": "openclaw 2026.4.14",
                    "source_url": "https://github.com/openclaw/openclaw/releases/tag/v2026.4.14",
                    "signal_path": "openclaw-watch/2026-04-14/signals/v2026.4.14.md",
                    "fetched_at": "2026-04-14T05:08:56+0000",
                    "source_snippet": (
                        "OpenClaw `2026.4.14` is another broad quality release focused on model provider with explicit turn improvements for GPT-5 family and channel provider issues. "
                        "OpenAI Codex/models: add forward-compat support for `gpt-5.4-pro`, including Codex pricing/limits and list/status visibility before the upstream catalog catches up. "
                        "Telegram/forum topics: surface human topic names in agent context, prompt metadata, and plugin hook metadata by learning names from Telegram forum service messages. "
                        "Models/Codex: include `apiKey` in the codex provider catalog output so the Pi ModelRegistry validator no longer rejects the entry and silently drops all custom models from every provider in `models.json`. "
                        "Slack/interactions: apply the configured global `allowFrom` owner allowlist to channel block-action and modal interactive events. "
                        "Agents/gateway-tool: reject `config.patch` and `config.apply` calls from the model-facing gateway tool when they would newly enable security-audit flags."
                    ),
                    "excerpt": "openclaw 2026.4.14 dense summary",
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "claude-code-watch", "selected_item_count": 1},
                    {"lane": "openclaw-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        claude_line = next(line for line in body_markdown.splitlines() if "**v2.1.105**" in line)
        self.assertIn("network error", claude_line)
        self.assertIn("/doctor", claude_line)
        self.assertIn("WebFetch", claude_line)
        self.assertIn("queued messages", claude_line)
        self.assertGreaterEqual(len(claude_line), 260)

        openclaw_line = next(line for line in body_markdown.splitlines() if "**openclaw 2026.4.14**" in line)
        self.assertIn("gpt-5.4-pro", openclaw_line)
        self.assertIn("Telegram/forum topics", openclaw_line)
        self.assertIn("apiKey", openclaw_line)
        self.assertTrue("allowFrom" in openclaw_line or "config.patch" in openclaw_line)
        self.assertGreaterEqual(len(openclaw_line), 240)

    def test_build_report_artifact_live_report_remaining_x_placeholders_turn_into_minimal_fact_sentences(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 4},
                {"name": "x-following", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 5, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@realBigBrainAI #42",
                    "source_url": "https://x.com/realBigBrainAI/status/2043668202061017177",
                    "signal_path": "x-feed/2026-04-14/signals/realBigBrainAI__feed__2043668202061017177.md",
                    "fetched_at": "2026-04-14T15:20:08+0000",
                    "source_snippet": (
                        'Peter Steinberger, creator of OpenClaw, on why AI agents still produce "slop" '
                        'without human taste in the loop: "You can'
                    ),
                    "excerpt": (
                        'Peter Steinberger, creator of OpenClaw, on why AI agents still produce "slop" '
                        'without human taste in the loop: "You can'
                    ),
                },
                {
                    "lane": "x-feed",
                    "title": "@npm_i_shaders #70",
                    "source_url": "https://x.com/npm_i_shaders/status/2044041810440319391",
                    "signal_path": "x-feed/2026-04-14/signals/npm_i_shaders__feed__2044041810440319391.md",
                    "fetched_at": "2026-04-14T15:20:08+0000",
                    "source_snippet": (
                        "Introducing Shaders MCP. "
                        "The way you build shaders just changed. "
                        "Your agent now finds, tweaks, and ships the perfect"
                    ),
                    "excerpt": (
                        "Introducing Shaders MCP. "
                        "The way you build shaders just changed. "
                        "Your agent now finds, tweaks, and ships the perfect"
                    ),
                },
                {
                    "lane": "x-feed",
                    "title": "@heygurisingh #60",
                    "source_url": "https://x.com/heygurisingh/status/2043530834356134323",
                    "signal_path": "x-feed/2026-04-14/signals/heygurisingh__feed__2043530834356134323.md",
                    "fetched_at": "2026-04-14T15:20:08+0000",
                    "source_snippet": (
                        "Someone built the most complete Claude Code setup Boris Cherny uses at Anthropic "
                        "on GitHub and it's 100%"
                    ),
                    "excerpt": (
                        "Someone built the most complete Claude Code setup Boris Cherny uses at Anthropic "
                        "on GitHub and it's 100%"
                    ),
                },
                {
                    "lane": "x-feed",
                    "title": "@exploraX_ #32",
                    "source_url": "https://x.com/exploraX_/status/2043578742778277962",
                    "signal_path": "x-feed/2026-04-14/signals/exploraX___feed__2043578742778277962.md",
                    "fetched_at": "2026-04-14T15:20:08+0000",
                    "source_snippet": (
                        "the creators of agent skills at Anthropic explained why they stopped building agents. "
                        "and started building skills inste"
                    ),
                    "excerpt": (
                        "the creators of agent skills at Anthropic explained why they stopped building agents. "
                        "and started building skills inste"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@heygurisingh",
                    "source_url": "https://x.com/heygurisingh/status/2044071026162819561",
                    "signal_path": "x-following/2026-04-14/signals/heygurisingh__post__2044071026162819561.md",
                    "fetched_at": "2026-04-14T15:20:27+0000",
                    "source_snippet": (
                        "RT @heygurisingh: Mark this tweet "
                        "Catdoes v4 is the first ai builder where the agent has its own computer in the cloud."
                    ),
                    "excerpt": (
                        "RT @heygurisingh: Mark this tweet "
                        "Catdoes v4 is the first ai builder where the agent has its own computer in the cloud."
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 5,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 4},
                    {"lane": "x-following", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertNotIn("原文围绕", body_markdown)

        realbigbrain_line = next(line for line in body_markdown.splitlines() if "**@realBigBrainAI #42**" in line)
        self.assertIn("OpenClaw", realbigbrain_line)
        self.assertTrue("slop" in realbigbrain_line or "human taste" in realbigbrain_line or "Peter Steinberger" in realbigbrain_line)

        shaders_line = next(line for line in body_markdown.splitlines() if "**@npm_i_shaders #70**" in line)
        self.assertTrue("Shaders MCP" in shaders_line or "shader" in shaders_line.lower())
        self.assertIn("agent", shaders_line.lower())

        setup_line = next(line for line in body_markdown.splitlines() if "**@heygurisingh #60**" in line)
        self.assertIn("Claude Code", setup_line)
        self.assertTrue("Anthropic" in setup_line or "GitHub" in setup_line or "setup" in setup_line.lower())

        skills_line = next(line for line in body_markdown.splitlines() if "**@exploraX_ #32**" in line)
        self.assertIn("Anthropic", skills_line)
        self.assertIn("skills", skills_line.lower())
        self.assertIn("agents", skills_line.lower())

        catdoes_line = next(
            line
            for line in body_markdown.splitlines()
            if "**@heygurisingh**" in line and "Catdoes" in line
        )
        self.assertIn("Catdoes v4", catdoes_line)
        self.assertTrue("云端" in catdoes_line or "cloud" in catdoes_line.lower() or "电脑" in catdoes_line)

    def test_build_report_artifact_live_report_current_x_placeholders_turn_into_minimal_fact_sentences(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 2},
                {"name": "x-following", "status": "ok", "useful_item_count": 3},
            ],
            "summary": {"useful_item_count": 5, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@steipete #94",
                    "source_url": "https://x.com/steipete/status/2043726001750900770",
                    "signal_path": "x-feed/2026-04-14/signals/steipete__feed__2043726001750900770.md",
                    "fetched_at": "2026-04-14T16:20:58+0000",
                    "source_snippet": (
                        "RT @cherry_mx_reds: A few more OpenClaw 2026.4.12 changes that didn’t make the first tweet 🦞 "
                        "Better local models with"
                    ),
                    "excerpt": (
                        "RT @cherry_mx_reds: A few more OpenClaw 2026.4.12 changes that didn’t make the first tweet 🦞 "
                        "Better local models with"
                    ),
                },
                {
                    "lane": "x-feed",
                    "title": "@lmstudio #9",
                    "source_url": "https://x.com/lmstudio/status/2043741629492666659",
                    "signal_path": "x-feed/2026-04-14/signals/lmstudio__feed__2043741629492666659.md",
                    "fetched_at": "2026-04-14T16:20:58+0000",
                    "source_snippet": (
                        "LM Studio is now an official @openclaw provider! "
                        "Run: openclaw onboard --auth-choice lmstudio "
                        "Use your local model"
                    ),
                    "excerpt": (
                        "LM Studio is now an official @openclaw provider! "
                        "Run: openclaw onboard --auth-choice lmstudio "
                        "Use your local model"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@danshipper",
                    "source_url": "https://x.com/danshipper/status/2044027331556077928",
                    "signal_path": "x-following/2026-04-14/signals/danshipper__post__2044027331556077928.md",
                    "fetched_at": "2026-04-14T16:21:06+0000",
                    "source_snippet": (
                        "Re: the report that older models can find the same exploits as Mythos: "
                        "This doesn’t mean much about its power relative"
                    ),
                    "excerpt": (
                        "Re: the report that older models can find the same exploits as Mythos: "
                        "This doesn’t mean much about its power relative"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@cyrilXBT",
                    "source_url": "https://x.com/cyrilXBT/status/2044087415841673518",
                    "signal_path": "x-following/2026-04-14/signals/cyrilXBT__post__2044087415841673518.md",
                    "fetched_at": "2026-04-14T16:21:06+0000",
                    "source_snippet": (
                        "A Google engineer with 11 years of experience automated 80% of his job with Claude Code. "
                        "He now works 2-3 hours a day i"
                    ),
                    "excerpt": (
                        "A Google engineer with 11 years of experience automated 80% of his job with Claude Code. "
                        "He now works 2-3 hours a day i"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@carlvellotti",
                    "source_url": "https://x.com/carlvellotti/status/2044087745254138081",
                    "signal_path": "x-following/2026-04-14/signals/carlvellotti__post__2044087745254138081.md",
                    "fetched_at": "2026-04-14T16:21:06+0000",
                    "source_snippet": (
                        "I literally sell a course teaching PMs to build with Claude Code. "
                        "I'll tell you straight: raw Claude is not an enterpri"
                    ),
                    "excerpt": (
                        "I literally sell a course teaching PMs to build with Claude Code. "
                        "I'll tell you straight: raw Claude is not an enterpri"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 5,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 2},
                    {"lane": "x-following", "selected_item_count": 3},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertNotIn("原文围绕", body_markdown)

        steipete_line = next(line for line in body_markdown.splitlines() if "**@steipete #94**" in line)
        self.assertIn("OpenClaw 2026.4.12", steipete_line)
        self.assertTrue("first tweet" in steipete_line or "首条" in steipete_line)
        self.assertTrue("local model" in steipete_line.lower() or "本地模型" in steipete_line)

        lmstudio_line = next(line for line in body_markdown.splitlines() if "**@lmstudio #9**" in line)
        self.assertIn("LM Studio", lmstudio_line)
        self.assertIn("OpenClaw", lmstudio_line)
        self.assertTrue("provider" in lmstudio_line.lower() or "接入" in lmstudio_line or "接进" in lmstudio_line)
        self.assertTrue("local model" in lmstudio_line.lower() or "本地模型" in lmstudio_line)

        danshipper_line = next(line for line in body_markdown.splitlines() if "**@danshipper**" in line)
        self.assertIn("Mythos", danshipper_line)
        self.assertTrue("exploit" in danshipper_line.lower() or "漏洞" in danshipper_line)
        self.assertTrue("power" in danshipper_line.lower() or "能力" in danshipper_line)

        cyril_line = next(line for line in body_markdown.splitlines() if "**@cyrilXBT**" in line)
        self.assertIn("Claude Code", cyril_line)
        self.assertIn("80%", cyril_line)
        self.assertTrue("2-3" in cyril_line or "2 到 3" in cyril_line or "2 至 3" in cyril_line)

        carlvellotti_line = next(line for line in body_markdown.splitlines() if "**@carlvellotti**" in line)
        self.assertIn("PM", carlvellotti_line)
        self.assertIn("Claude Code", carlvellotti_line)
        self.assertTrue("enterprise" in carlvellotti_line.lower() or "企业" in carlvellotti_line)

    def test_build_report_artifact_live_like_2026_04_15_x_bad_cases_render_three_concrete_sentences(self) -> None:
        cases = [
            {
                "lane": "x-feed",
                "title": "@trq212 #40",
                "source_url": "https://x.com/trq212/status/2044100766445805823",
                "signal_path": "x-feed/2026-04-15/signals/trq212__feed__2044100766445805823.md",
                "source_snippet": (
                    "RT @noahzweben: Claude Code Routines are here! "
                    "In addition to a schedule, you can now trigger templated agents via GitHu"
                ),
                "expected_keywords": ["Claude Code", "Routines", "schedule", "GitHub"],
            },
            {
                "lane": "x-feed",
                "title": "@icanvardar #73",
                "source_url": "https://x.com/icanvardar/status/2043652025339023845",
                "signal_path": "x-feed/2026-04-15/signals/icanvardar__feed__2043652025339023845.md",
                "source_snippet": (
                    "wait… claude code literally punishes you for turning off telemetry?? "
                    "if you disable it, anthropic drops your cache"
                ),
                "expected_keywords": ["Claude Code", "telemetry", "Anthropic", "cache"],
            },
            {
                "lane": "x-following",
                "title": "@trq212",
                "source_url": "https://x.com/trq212/status/2044100766445805823",
                "signal_path": "x-following/2026-04-15/signals/trq212__post__2044100766445805823.md",
                "source_snippet": (
                    "RT @noahzweben: Claude Code Routines are here! "
                    "In addition to a schedule, you can now trigger templated agents via GitHu"
                ),
                "expected_keywords": ["Claude Code", "Routines", "schedule", "GitHub"],
            },
            {
                "lane": "x-following",
                "title": "@aiedge_",
                "source_url": "https://x.com/aiedge_/status/2044151244416299381",
                "signal_path": "x-following/2026-04-15/signals/aiedge___post__2044151244416299381.md",
                "source_snippet": (
                    "Anyone using Claude Code NEEDS to save this resource. "
                    "A fully curated website with the top Claude Code Skills, MCPs"
                ),
                "expected_keywords": ["Claude Code", "Skills", "MCP", "网站"],
            },
        ]
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 2},
                {"name": "x-following", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": len(cases), "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": case["lane"],
                    "title": case["title"],
                    "source_url": case["source_url"],
                    "signal_path": case["signal_path"],
                    "fetched_at": "2026-04-15T00:00:00+0000",
                    "source_snippet": case["source_snippet"],
                    "excerpt": case["source_snippet"],
                }
                for case in cases
            ],
            "summary": {
                "selected_item_count": len(cases),
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 2},
                    {"lane": "x-following", "selected_item_count": 2},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_lines = [
            line for line in artifact["body_markdown"].splitlines() if line.strip().startswith("- **")
        ]

        self.assertEqual(len(body_lines), len(cases))
        for case in cases:
            with self.subTest(title=case["title"]):
                body_line = next(line for line in body_lines if case["source_url"] in line)
                self.assertNotIn("原文围绕", body_line)
                self.assertGreaterEqual(body_line.count("。"), 3)
                for keyword in case["expected_keywords"]:
                    self.assertIn(keyword, body_line)

    def test_build_report_artifact_live_like_2026_04_15_generic_x_fallback_still_renders_three_clauses(self) -> None:
        cases = [
            {
                "lane": "x-feed",
                "title": "@ashpreetbedi #81",
                "source_url": "https://x.com/ashpreetbedi/status/2044098660586111022",
                "signal_path": "x-feed/2026-04-15/signals/ashpreetbedi__feed__2044098660586111022.md",
                "source_snippet": (
                    "New post: Systems Engineering "
                    "Coding agents have lowered the barrier to writing code, but they haven't lowered the requ"
                ),
                "expected_keywords": ["Systems Engineering", "coding agents", "写代码"],
            },
            {
                "lane": "x-following",
                "title": "@felixrieseberg",
                "source_url": "https://x.com/felixrieseberg/status/2044128194647994585",
                "signal_path": "x-following/2026-04-15/signals/felixrieseberg__post__2044128194647994585.md",
                "source_snippet": (
                    "Today is a big day! We're launching a ~ new ~ version of Claude Code in the desktop app. "
                    "It's been redesigned"
                ),
                "expected_keywords": ["Claude Code", "desktop", "重新设计"],
            },
        ]
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 1},
                {"name": "x-following", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": len(cases), "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": case["lane"],
                    "title": case["title"],
                    "source_url": case["source_url"],
                    "signal_path": case["signal_path"],
                    "fetched_at": "2026-04-15T00:00:00+0000",
                    "source_snippet": case["source_snippet"],
                    "excerpt": case["source_snippet"],
                }
                for case in cases
            ],
            "summary": {
                "selected_item_count": len(cases),
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 1},
                    {"lane": "x-following", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_lines = [
            line for line in artifact["body_markdown"].splitlines() if line.strip().startswith("- **")
        ]

        self.assertEqual(len(body_lines), len(cases))
        for case in cases:
            with self.subTest(title=case["title"]):
                body_line = next(line for line in body_lines if case["source_url"] in line)
                self.assertNotIn("原文围绕", body_line)
                self.assertGreaterEqual(body_line.count("。"), 3)
                for keyword in case["expected_keywords"]:
                    self.assertIn(keyword, body_line)

    def test_build_report_artifact_release_single_english_sentences_get_minimal_chinese_rewrites(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "claude-code-watch", "status": "ok", "useful_item_count": 1},
                {"name": "openclaw-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "claude-code-watch",
                    "title": "v2.1.107",
                    "source_url": "https://github.com/anthropics/claude-code/releases/tag/v2.1.107",
                    "signal_path": "claude-code-watch/2026-04-14/signals/anthropics__claude-code__release__v2.1.107.md",
                    "fetched_at": "2026-04-14T14:52:33+0000",
                    "source_snippet": "Show thinking hints sooner during long operations",
                    "excerpt": "Show thinking hints sooner during long operations",
                },
                {
                    "lane": "openclaw-watch",
                    "title": "openclaw 2026.4.14",
                    "source_url": "https://github.com/openclaw/openclaw/releases/tag/v2026.4.14",
                    "signal_path": "openclaw-watch/2026-04-14/signals/openclaw__openclaw__release__v2026.4.14.md",
                    "fetched_at": "2026-04-14T14:54:06+0000",
                    "source_snippet": (
                        "OpenClaw `2026.4.14` is another broad quality release focused on model provider "
                        "with explicit turn improvements for GPT-5 family and channel provider issues. "
                        "Additionally we improved overal performance with refactors to our underlying core codebase."
                    ),
                    "excerpt": (
                        "OpenClaw `2026.4.14` is another broad quality release focused on model provider "
                        "with explicit turn improvements for GPT-5 family and channel provider issues. "
                        "Additionally we improved overal performance with refactors to our underlying core codebase."
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "claude-code-watch", "selected_item_count": 1},
                    {"lane": "openclaw-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        claude_line = next(line for line in body_markdown.splitlines() if "**v2.1.107**" in line)
        self.assertIn("Claude Code", claude_line)
        self.assertTrue("thinking hints" in claude_line or "长操作" in claude_line or "提前" in claude_line)
        self.assertNotIn("Show thinking hints sooner during long operations", claude_line)
        self.assertNotIn("原文围绕 v2.1.107 展开，具体变化见来源", claude_line)

        openclaw_line = next(line for line in body_markdown.splitlines() if "**openclaw 2026.4.14**" in line)
        self.assertIn("OpenClaw", openclaw_line)
        self.assertTrue("GPT-5" in openclaw_line or "model provider" in openclaw_line or "质量" in openclaw_line)
        self.assertTrue("性能" in openclaw_line or "provider" in openclaw_line or "channel" in openclaw_line)
        self.assertNotIn("is another broad quality release focused on model provider", openclaw_line)
        self.assertNotIn("原文围绕 openclaw 2026.4.14 展开，具体变化见来源", openclaw_line)

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

    def test_build_editor_copy_returns_empty_detail_for_real_residual_noisy_x_fragments(self) -> None:
        # These cases only have truncated English fragments with no reliable Chinese facts
        cases = [
            (
                "x-feed",
                "@eng_khairallah1 #73",
                "This 25-minute Claude Code workshop by Anthropic's own applied AI team will teach you more about Claude Code best pract",
            ),
            (
                "x-following",
                "@steipete",
                "they: OpenClaw is so insecure look at all these GHSAs! reality: we are just an indicator of the coming storm",
            ),
            (
                "x-following",
                "@Dimillian",
                "RT @Baconbrix: A pleasure working with the OpenAI team on the official @Expo plugin for Codex! Gives you everything",
            ),
        ]

        for lane_name, title, excerpt in cases:
            with self.subTest(title=title):
                headline, detail = build_editor_copy(
                    lane_name=lane_name,
                    title=title,
                    excerpt=excerpt,
                    front_matter={},
                )

                self.assertTrue(headline)
                self.assertEqual(detail, "")

    def test_build_report_artifact_skips_real_residual_noisy_x_bad_cases(self) -> None:
        # Only steipete returns empty detail - should be skipped
        # _catwu and NickADobos now generate proper Chinese facts - should be kept
        bad_cases = [
            {
                "lane": "x-following",
                "title": "@steipete",
                "source_url": "https://x.com/steipete/status/2044888081141223442",
                "signal_path": "x-following/2026-04-17/signals/steipete__post__2044888081141223442.md",
                "source_snippet": (
                    "they: OpenClaw is so insecure look at all these GHSAs! "
                    "reality: we are just an indicator of the coming storm"
                ),
            },
        ]
        good_cases = [
            {
                "lane": "x-feed",
                "title": "@_catwu #63",
                "source_url": "https://x.com/_catwu/status/2044808533905178822",
                "signal_path": "x-feed/2026-04-17/signals/_catwu__feed__2044808533905178822.md",
                "source_snippet": (
                    "Opus 4.7 is live in Claude Code today! "
                    "The model performs best if you treat it like an engineer you're delegating"
                ),
            },
            {
                "lane": "x-feed",
                "title": "@NickADobos #82",
                "source_url": "https://x.com/NickADobos/status/2044885440092877028",
                "signal_path": "x-feed/2026-04-17/signals/NickADobos__feed__2044885440092877028.md",
                "source_snippet": (
                    "With codex computer use + mac's iPhone Mirror app, GPT can use any app on your phone!!! "
                    "Seems less accurate with clicks"
                ),
            },
        ]
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": case["lane"],
                    "title": case["title"],
                    "source_url": case["source_url"],
                    "signal_path": case["signal_path"],
                    "fetched_at": "2026-04-17T01:23:53+0000",
                    "source_snippet": case["source_snippet"],
                    "excerpt": case["source_snippet"],
                }
                for case in bad_cases + good_cases
            ]
            + [
                {
                    "lane": "product-hunt-watch",
                    "title": "Nicelydone MCP — Design context for AI agents",
                    "source_url": "https://www.producthunt.com/products/nicely-done",
                    "signal_path": "product-hunt-watch/2026-04-17/signals/nicelydone.md",
                    "fetched_at": "2026-04-17T01:23:53+0000",
                    "source_snippet": "Design context for AI agents",
                    "excerpt": "Design context for AI agents",
                }
            ],
            "summary": {
                "selected_item_count": 4,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 2},
                    {"lane": "x-following", "selected_item_count": 1},
                    {"lane": "product-hunt-watch", "selected_item_count": 1},
                ],
            },
        }
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 2},
                {"name": "x-following", "status": "ok", "useful_item_count": 1},
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 4, "partial_lane_count": 0},
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("Nicelydone MCP", body_markdown)
        # steipete should be skipped
        self.assertNotIn("@steipete", body_markdown)
        self.assertNotIn("reality: we are just an indicator of the coming storm", body_markdown)
        # _catwu and NickADobos should be kept (they generate proper Chinese facts)
        self.assertIn("@_catwu #63", body_markdown)
        self.assertIn("@NickADobos #82", body_markdown)
        self.assertNotIn("这条帖子围绕", body_markdown)
        self.assertNotIn("The model performs best if you treat it like an engineer you're delegating", body_markdown)
        self.assertNotIn("Seems less accurate with clicks", body_markdown)

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

    def test_build_report_artifact_discards_noisy_x_with_truncated_english_fragments(self) -> None:
        """Items with only truncated English fragments that can't form Chinese facts should be discarded."""
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 5},
                {"name": "x-following", "status": "ok", "useful_item_count": 5},
            ],
            "summary": {"useful_item_count": 10, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@openclaw #74",
                    "source_url": "https://x.com/openclaw/status/2044919054402752638",
                    "signal_path": "x-feed/2026-04-17/signals/openclaw.md",
                    "fetched_at": "2026-04-17T01:23:48+0000",
                    "source_snippet": (
                        "OpenClaw 2026.4.15 🦞\n\n🤖 Anthropic Opus 4.7 support\n"
                        "🗣️ Gemini TTS in bundled\n🧠 Slimmer context + bounded memory reads\n🔧 C"
                    ),
                    "excerpt": (
                        "OpenClaw 2026.4.15 🦞\n\n🤖 Anthropic Opus 4.7 support\n"
                        "🗣️ Gemini TTS in bundled\n🧠 Slimmer context + bounded memory reads\n🔧 C"
                    ),
                },
                {
                    "lane": "x-feed",
                    "title": "@eng_khairallah1 #73",
                    "source_url": "https://x.com/eng_khairallah1/status/2044787496681390571",
                    "signal_path": "x-feed/2026-04-17/signals/eng_khairallah1.md",
                    "fetched_at": "2026-04-17T01:23:48+0000",
                    "source_snippet": (
                        "This 25-minute Claude Code workshop by Anthropic's own applied AI team will teach "
                        "you more about Claude Code best pract"
                    ),
                    "excerpt": (
                        "This 25-minute Claude Code workshop by Anthropic's own applied AI team will teach "
                        "you more about Claude Code best pract"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@steipete",
                    "source_url": "https://x.com/steipete/status/2044888081141223442",
                    "signal_path": "x-following/2026-04-17/signals/steipete.md",
                    "fetched_at": "2026-04-17T01:23:53+0000",
                    "source_snippet": (
                        "they: OpenClaw is so insecure look at all these GHSAs!\n"
                        "reality: we are just an indicator of the coming storm"
                    ),
                    "excerpt": (
                        "they: OpenClaw is so insecure look at all these GHSAs!\n"
                        "reality: we are just an indicator of the coming storm"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@Dimillian",
                    "source_url": "https://x.com/Dimillian/status/2044875379001766315",
                    "signal_path": "x-following/2026-04-17/signals/Dimillian.md",
                    "fetched_at": "2026-04-17T01:23:53+0000",
                    "source_snippet": (
                        "RT @Baconbrix: A pleasure working with the OpenAI team on the official @Expo plugin for Codex!\n\n"
                        "Gives you everything fr"
                    ),
                    "excerpt": (
                        "RT @Baconbrix: A pleasure working with the OpenAI team on the official @Expo plugin for Codex!\n\n"
                        "Gives you everything fr"
                    ),
                },
                {
                    "lane": "x-following",
                    "title": "@NickADobos",
                    "source_url": "https://x.com/NickADobos/status/2044885440092877028",
                    "signal_path": "x-following/2026-04-17/signals/NickADobos.md",
                    "fetched_at": "2026-04-17T01:23:53+0000",
                    "source_snippet": (
                        "With codex computer use + mac's iPhone Mirror app, GPT can use any app on your phone!!!\n\n"
                        "Seems less accurate with clicks"
                    ),
                    "excerpt": (
                        "With codex computer use + mac's iPhone Mirror app, GPT can use any app on your phone!!!\n\n"
                        "Seems less accurate with clicks"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 5,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 2},
                    {"lane": "x-following", "selected_item_count": 3},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        # openclaw and NickADobos generate proper Chinese facts and should be kept
        self.assertIn("openclaw/status/2044919054402752638", body_markdown)
        self.assertIn("NickADobos/status/2044885440092877028", body_markdown)
        # eng_khairallah1, steipete, Dimillian only generate placeholders/empty and should be discarded
        self.assertNotIn("eng_khairallah1/status/2044787496681390571", body_markdown)
        self.assertNotIn("steipete/status/2044888081141223442", body_markdown)
        self.assertNotIn("Dimillian/status/2044875379001766315", body_markdown)
        # Bad patterns should not appear
        self.assertNotIn("该栏目收录", body_markdown)
        self.assertNotIn("这条帖子围绕", body_markdown)
        self.assertNotIn("reality: we are just an indicator of the coming storm", body_markdown)
        self.assertNotIn("Gives you everything", body_markdown)
        self.assertNotIn("Seems less accurate with clicks", body_markdown)
        self.assertNotIn("The model performs best if you treat it like an engineer you're delegating", body_markdown)

    def test_build_report_artifact_x_items_with_concrete_chinese_facts_are_kept(self) -> None:
        """Items that can generate concrete Chinese factual sentences should be kept."""
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "x-feed", "status": "ok", "useful_item_count": 2},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "x-feed",
                    "title": "@punk2898 #60",
                    "source_url": "https://x.com/punk2898/status/2044612209746264350",
                    "signal_path": "x-feed/2026-04-17/signals/punk2898.md",
                    "fetched_at": "2026-04-17T01:23:48+0000",
                    "source_snippet": "没有 Vibe Coding 的人是不懂的这种爽感的，这可比什么 OpenClaw 爽太多太多了",
                    "excerpt": "没有 Vibe Coding 的人是不懂的这种爽感的，这可比什么 OpenClaw 爽太多太多了",
                },
                {
                    "lane": "x-feed",
                    "title": "@dotey #66",
                    "source_url": "https://x.com/dotey/status/2044830688587706710",
                    "signal_path": "x-feed/2026-04-17/signals/dotey.md",
                    "fetched_at": "2026-04-17T01:23:48+0000",
                    "source_snippet": "Codex 大更新：从写代码工具变成能操作你电脑的助手",
                    "excerpt": "Codex 大更新：从写代码工具变成能操作你电脑的助手",
                },
            ],
            "summary": {
                "selected_item_count": 2,
                "lane_counts": [
                    {"lane": "x-feed", "selected_item_count": 2},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("punk2898/status/2044612209746264350", body_markdown)
        self.assertIn("dotey/status/2044830688587706710", body_markdown)
        self.assertNotIn("该栏目收录", body_markdown)
        self.assertNotIn("这条帖子围绕", body_markdown)

    def test_build_report_artifact_opencclaw_release_generates_chinese_facts(self) -> None:
        """OpenClaw 2026.4.15 release info should generate Chinese factual sentences."""
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
                    "title": "@openclaw #74",
                    "source_url": "https://x.com/openclaw/status/2044919054402752638",
                    "signal_path": "x-feed/2026-04-17/signals/openclaw.md",
                    "fetched_at": "2026-04-17T01:23:48+0000",
                    "source_snippet": (
                        "OpenClaw 2026.4.15 🦞\n\n🤖 Anthropic Opus 4.7 support\n"
                        "🗣️ Gemini TTS in bundled\n🧠 Slimmer context + bounded memory reads\n🔧 C"
                    ),
                    "excerpt": (
                        "OpenClaw 2026.4.15 🦞\n\n🤖 Anthropic Opus 4.7 support\n"
                        "🗣️ Gemini TTS in bundled\n🧠 Slimmer context + bounded memory reads\n🔧 C"
                    ),
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

        self.assertIn("openclaw/status/2044919054402752638", body_markdown)
        self.assertNotIn("该栏目收录", body_markdown)
        self.assertNotIn("这条帖子围绕", body_markdown)
        # Should have Chinese facts about the release
        self.assertIn("OpenClaw 2026.4.15", body_markdown)

    def test_build_x_post_detail_rewrites_claude_design_launch_into_chinese(self) -> None:
        detail = build_x_post_detail(
            lane_name="x-following",
            title="@claudeai",
            source_text=(
                "Introducing Claude Design by Anthropic Labs: make prototypes, slides, and one-pagers "
                "by talking to Claude. Powered by Claude Opus 4.7."
            ),
        )

        self.assertIn("Claude Design", detail)
        self.assertIn("prototype、slides 和 one-pagers", detail)
        self.assertNotIn("by talking to Claude", detail)

    def test_build_product_hunt_detail_rewrites_sparse_english_agent_titles(self) -> None:
        detail = build_product_hunt_detail(
            title="LIVE: wtf are agents buying? — Watch agents spend money in real time",
            source_text="Watch agents spend money in real time **Author:** @LIVE: wtf are agents buying?",
        )

        self.assertIn("实时看 agent 在花钱买什么", detail)
        self.assertIn("采购和支付权限", detail)
        self.assertNotIn("主打 agent 相关的自动化能力", detail)
        self.assertNotIn("Watch agents spend money in real time", detail)

    def test_build_reddit_detail_covers_live_2026_04_21_placeholder_cases(self) -> None:
        cases = [
            (
                "Got roasted for not open sourcing my agent OS (dashboard), so I did. Built the whole thing with Claude Code",
                (
                    "Got a lot of hate for not open sourcing my agent OS so decided to just do it. "
                    "I've been building Octopoda with Claude Code over the past few months. Pretty much the entire thing "
                    "was pair programmed with Claude, not just boilerplate but actually architecting systems, debugging "
                    "production issues at 2am, fixing database migrations, all of it. The idea is basically one place to "
                    "manage your AI agents."
                ),
                ("Octopoda", "开源", "数据库迁移"),
            ),
            (
                "Claude Code's source code just leaked — so I had Claude Code analyze its own internals and build an open-source multi-agent framework from it",
                (
                    "Claude Code's full source was exposed via source maps. 500K+ lines of TypeScript with the full "
                    "architecture visible. I studied the multi-agent orchestration layer — coordinator mode, team "
                    "management, task scheduling, inter-agent messaging — and re-implemented it from scratch as a "
                    "standalone open-source framework. The key difference from the original: it's model-agnostic. "
                    "You can run a team where one agent uses Claude for planning and another uses GPT for "
                    "implementation — same workflow, shared memory, message bus between them."
                ),
                ("500K+", "source maps", "model-agnostic"),
            ),
            (
                "Anthropic just restricted OpenClaw from Claude subscriptions. I haven't used OpenClaw once — autonomous Claude agents with zero external harnesses.",
                (
                    "I have Claude Cowork sessions running in parallel right now: One manages a sales pipeline "
                    "(runs every hour, logs findings to Notion, DMs me when a lead needs attention). One handles "
                    "background research and prep work (fires nightly). One monitors metrics and surfaces anomalies "
                    "(AM/PM). A heartbeat session rolls up status from all of them every 30 minutes and tells me "
                    "what needs my attention. No servers. No custom code. No always-on processes. I'm not running "
                    "OpenClaw. The full stack: Cowork scheduled sessions — the execution engine."
                ),
                ("Claude Cowork", "Notion", "不需要服务器"),
            ),
            (
                "Claude Code v2.1.92 introduces Ultraplan — draft plans in the cloud, review in your browser, execute anywhere",
                (
                    "Claude Code just shipped /ultraplan (beta) — you run it in your terminal, review the plan in your "
                    "browser with inline comments, then execute remotely or send it back to your CLI. It shipped "
                    "alongside Claude Code Web at claude.ai/code, pushing toward cloud-first workflows while keeping "
                    "the terminal as the power-user entry point. Anyone tried it yet?"
                ),
                ("/ultraplan", "浏览器", "claude.ai/code"),
            ),
            (
                "Switched from MCPs to CLIs for Claude Code and honestly never going back",
                (
                    "I went pretty hard on MCPs at first. Set up a bunch of them, thought I was doing things the right "
                    "way. But after actually using them for a bit it just got frustrating. Claude would mess up "
                    "parameters, auth would randomly break, stuff would time out. And everything felt slower than it "
                    "should be. Once I started using CLIs, it turned out Claude is genuinely excellent with them. "
                    "Makes sense, it's been trained on years of shell scripts, docs, Stack Overflow answers, GitHub issues."
                ),
                ("MCP", "CLI", "shell scripts"),
            ),
        ]

        for title, source_text, expected_terms in cases:
            with self.subTest(title=title):
                detail = build_reddit_detail(title=title, source_text=source_text)

                self.assertTrue(detail)
                self.assertNotIn("该栏目收录", detail)
                for term in expected_terms:
                    self.assertIn(term, detail)

    def test_build_hacker_news_detail_covers_live_2026_04_21_cases(self) -> None:
        qwen_detail = build_hacker_news_detail(
            lane_name="hacker-news-watch",
            title="Qwen3.6-Max-Preview: Smarter, Sharper, Still Evolving",
            source_text="Qwen3.6-Max-Preview: Smarter, Sharper, Still Evolving",
        )
        self.assertIn("Qwen3.6-Max-Preview", qwen_detail)
        self.assertIn("预览", qwen_detail)
        self.assertNotIn("不是泛聊概念", qwen_detail)

        busybee_detail = build_hacker_news_detail(
            lane_name="hacker-news-search-watch",
            title="Show HN: Busybee - a FIFO build queue for multi-agent dev workflows",
            source_text=(
                "My old 8-core MacBook Pro used to get wrecked the moment two Claude Code sessions decided to build "
                "at the same time. To combat that, I wanted to make sure dev agents queue up when they want to make "
                "heavy builds. At the same time, I like to keep a constant overview of my CPU usage in the terminal. "
                "Busybee solves both by rendering a compact set of core usage gauges with a one-line queue status underneath."
            ),
            matched_query="agent workflow",
        )
        self.assertIn("Busybee", busybee_detail)
        self.assertIn("FIFO", busybee_detail)
        self.assertIn("CPU", busybee_detail)
        self.assertNotIn("不是泛聊概念", busybee_detail)

        lazyagent_detail = build_hacker_news_detail(
            lane_name="hacker-news-search-watch",
            title="Show HN: Lazyagent – TUI for to watch all your AI coding agents",
            source_text=(
                "Running multiple coding agents could make user losing track of what they were doing. Once subagents "
                "start spawning other subagents, basic questions get hard to answer: what is running right now, what "
                "tool did it just call, did the child agent actually do what the parent asked. Lazyagent is a "
                "terminal TUI that collects events from Claude Code, Codex, and OpenCode and shows them in one place. "
                "It groups sessions from different runtimes by working directory, so Claude and Codex runs on the "
                "same repo appear under the same project."
            ),
            matched_query="terminal coding agent",
        )
        self.assertIn("Lazyagent", lazyagent_detail)
        self.assertIn("终端 TUI", lazyagent_detail)
        self.assertIn("工作目录", lazyagent_detail)
        self.assertNotIn("不是泛聊概念", lazyagent_detail)

    def test_build_product_hunt_detail_localizes_live_2026_04_21_taglines(self) -> None:
        cases = [
            (
                "PangeAI — Instant, agent-driven spatial analysis and decisio",
                "Instant, agent-driven spatial analysis and decision-making **Author:** @PangeAI",
                ("空间分析", "决策"),
            ),
            (
                "Pegasus 1.5 by TwelveLabs — AI model for transforming video into Time-Based Me",
                "AI model for transforming video into Time-Based Metadata **Author:** @Pegasus 1.5 by TwelveLabs",
                ("视频", "时间", "元数据"),
            ),
            (
                "MaxHermes — World's first cloud sandbox Hermes Agent from Mini",
                "World's first cloud sandbox Hermes Agent from MiniMax **Author:** @MaxHermes",
                ("云端沙箱", "Hermes Agent", "MiniMax"),
            ),
            (
                "Makko AI — Make 2D game art and playable games. No drawing. N",
                "Make 2D game art and playable games. No drawing. No coding. **Author:** @Makko",
                ("2D 游戏", "不用画图", "不用写代码"),
            ),
            (
                "Dune — Context-aware Mac keypad to automate workflows + m",
                "Context-aware Mac keypad to automate workflows + meetings **Author:** @Dune",
                ("Mac", "工作流", "会议"),
            ),
        ]

        for title, source_text, expected_terms in cases:
            with self.subTest(title=title):
                detail = build_product_hunt_detail(title=title, source_text=source_text)

                self.assertTrue(detail)
                self.assertNotIn("这条 Product Hunt 记录里写到：`", detail)
                for term in expected_terms:
                    self.assertIn(term, detail)

    def test_build_polymarket_detail_rewrites_best_coding_ai_question_into_chinese(self) -> None:
        detail = build_polymarket_detail(
            title="Will DeepSeek have the best Coding AI model at the end of April 2026?",
            source_text=(
                "Question: Will DeepSeek have the best Coding AI model at the end of April 2026? "
                "Current leader: Anthropic (92.0%) Anthropic: 92.0% OpenAI: 6.6% DeepSeek: 1.2% "
                "24h volume: 8,804.4 Liquidity: 107,019.2 Price movement: down 1.6% this week"
            ),
        )

        self.assertIn("DeepSeek 到 2026 年 4 月底时会不会拥有最强的 Coding AI 模型", detail)
        self.assertIn("Anthropic", detail)
        self.assertIn("24 小时成交量 8,804.4", detail)
        self.assertIn("流动性 107,019.2", detail)
        self.assertIn("本周下跌 1.6%", detail)
        self.assertNotIn("Will DeepSeek have the best Coding AI model", detail)

    def test_build_report_artifact_rewrites_long_english_titles_for_reader_facing_lanes(self) -> None:
        collect_result = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "lanes": [
                {"name": "reddit-watch", "status": "ok", "useful_item_count": 1},
                {"name": "hacker-news-watch", "status": "ok", "useful_item_count": 1},
                {"name": "hacker-news-search-watch", "status": "ok", "useful_item_count": 1},
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 4, "partial_lane_count": 0},
        }
        selected_items = {
            "report_date": REPORT_DATE,
            "source": "signals-engine",
            "selected_items": [
                {
                    "lane": "reddit-watch",
                    "title": (
                        "I replaced chaotic solo Claude coding with a simple 3-agent team "
                        "(Architect + Builder + Reviewer) — it's stupidly effective and token-efficient"
                    ),
                    "source_url": "https://www.reddit.com/r/ClaudeAI/comments/example/review/",
                    "signal_path": "reddit-watch/2026-04-12/signals/review.md",
                    "fetched_at": "2026-04-12T01:23:53+0000",
                    "source_snippet": (
                        "The workflow splits Architect, Builder, and Reviewer with markdown handoff files "
                        "and focuses on token efficiency."
                    ),
                    "excerpt": (
                        "The workflow splits Architect, Builder, and Reviewer with markdown handoff files "
                        "and focuses on token efficiency."
                    ),
                },
                {
                    "lane": "hacker-news-watch",
                    "title": "CLI tools that actually work well with AI coding agents (Claude Code, Codex)",
                    "source_url": "https://news.ycombinator.com/item?id=44000021",
                    "signal_path": "hacker-news-watch/2026-04-12/signals/cli-tools.md",
                    "fetched_at": "2026-04-12T01:24:53+0000",
                    "source_snippet": (
                        "CLI flags won't block on a prompt, structured JSON output matters, and review "
                        "checklist handoff is part of the workflow."
                    ),
                    "excerpt": (
                        "CLI flags won't block on a prompt, structured JSON output matters, and review "
                        "checklist handoff is part of the workflow."
                    ),
                },
                {
                    "lane": "hacker-news-search-watch",
                    "title": (
                        "Swarm Orchestrator v4.1.0, verification layer for AI coding agents "
                        "(Copilot CLI, Claude Code, Codex)"
                    ),
                    "source_url": "https://news.ycombinator.com/item?id=44000022",
                    "signal_path": "hacker-news-search-watch/2026-04-12/signals/swarm-orchestrator.md",
                    "fetched_at": "2026-04-12T01:25:53+0000",
                    "matched_query": "Claude Code",
                    "source_snippet": (
                        "A verification layer for AI coding agents across Copilot CLI, Claude Code, and Codex."
                    ),
                    "excerpt": (
                        "A verification layer for AI coding agents across Copilot CLI, Claude Code, and Codex."
                    ),
                },
                {
                    "lane": "product-hunt-watch",
                    "title": (
                        "Crispy — VS Code extension with Agent Memory that wraps Claude Code and Codex "
                        "with a Powerful GUI"
                    ),
                    "source_url": "https://www.producthunt.com/posts/crispy",
                    "signal_path": "product-hunt-watch/2026-04-12/signals/crispy.md",
                    "fetched_at": "2026-04-12T01:26:53+0000",
                    "source_snippet": (
                        "Agent Memory and a GUI wrap Claude Code and Codex inside VS Code for team workflows. "
                        "Votes: 42 Comments: 7 Topic: Developer Tools"
                    ),
                    "excerpt": (
                        "Agent Memory and a GUI wrap Claude Code and Codex inside VS Code for team workflows. "
                        "Votes: 42 Comments: 7 Topic: Developer Tools"
                    ),
                },
            ],
            "summary": {
                "selected_item_count": 4,
                "lane_counts": [
                    {"lane": "reddit-watch", "selected_item_count": 1},
                    {"lane": "hacker-news-watch", "selected_item_count": 1},
                    {"lane": "hacker-news-search-watch", "selected_item_count": 1},
                    {"lane": "product-hunt-watch", "selected_item_count": 1},
                ],
            },
        }

        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
        body_markdown = artifact["body_markdown"]

        self.assertIn("- **三角色协作流程**", body_markdown)
        self.assertIn("- **适合 agent 的 CLI 工具**", body_markdown)
        self.assertIn("- **Swarm Orchestrator 验证层**", body_markdown)
        self.assertIn("- **Crispy：给 Claude Code / Codex 加记忆层和图形界面**", body_markdown)
        self.assertIn("- 三角色协作流程 — https://www.reddit.com/r/ClaudeAI/comments/example/review/", body_markdown)
        self.assertIn("- 适合 agent 的 CLI 工具 — https://news.ycombinator.com/item?id=44000021", body_markdown)
        self.assertIn("- Swarm Orchestrator 验证层 — https://news.ycombinator.com/item?id=44000022", body_markdown)
        self.assertIn("- Crispy：给 Claude Code / Codex 加记忆层和图形界面 — https://www.producthunt.com/posts/crispy", body_markdown)
        self.assertNotIn("I replaced chaotic solo Claude coding with a simple 3-agent team", body_markdown)
        self.assertNotIn("CLI tools that actually work well with AI coding agents", body_markdown)
        self.assertNotIn("Swarm Orchestrator v4.1.0, verification layer for AI coding agents", body_markdown)
        self.assertNotIn("VS Code extension with Agent Memory that wraps Claude Code and Codex with a Powerful GUI", body_markdown)

    def test_build_claude_code_release_detail_localizes_sparse_release_fix(self) -> None:
        detail = build_claude_code_release_detail(
            title="v2.1.112",
            source_text='Fixed "claude-opus-4-7 is temporarily unavailable" for auto mode',
        )

        self.assertIn("auto mode", detail)
        self.assertIn("temporarily unavailable", detail)
        self.assertIn("问题被修掉了", detail)
        self.assertNotIn('Fixed "claude-opus-4-7 is temporarily unavailable" for auto mode', detail)

    def test_build_codex_detail_localizes_dependency_alert_commit(self) -> None:
        detail = build_codex_detail(
            title="[codex] Fix high severity dependency alerts (#18167)",
            source_text=(
                "Pin vulnerable npm dependencies through the existing root `resolutions` mechanism so the lockfile moves only to patched versions. "
                "Refresh `pnpm-lock.yaml` for `@modelcontextprotocol/sdk`, `handlebars`"
            ),
            source_url="https://github.com/openai/codex/commit/fe04d75e0fdbbff77e02b5355c86108712abd151",
        )

        self.assertIn("高危依赖告警", detail)
        self.assertIn("已修补版本", detail)
        self.assertIn("pnpm-lock.yaml", detail)
        self.assertNotIn("Pin vulnerable npm dependencies", detail)

    def test_build_codex_detail_localizes_sparse_commit_and_realtime_summary(self) -> None:
        fixture_detail = build_codex_detail(
            title="[codex] Fix agent identity auth test fixture (#18697)",
            source_text="Add the missing `background_task_id: None` field to the `AgentIdentityAuthRecord` fixture introduced in `auth_tests.rs`.",
            source_url="https://github.com/openai/codex/commit/6b17adc231e038c35aeb6ac613fdaf6c6d79bb26",
        )
        self.assertIn("background_task_id: None", fixture_detail)
        self.assertIn("数据形状", fixture_detail)
        self.assertNotIn("Add the missing", fixture_detail)

        merged_pr_detail = build_codex_detail(
            title="[codex] Fix agent identity auth test fixture",
            source_text="**Title:** [codex] Fix agent identity auth test fixture **Author:** @adrian-openai **Merged at:** 2026-04-20T18:05:58Z **Merge commit:** `6b17adc`",
            source_url="https://github.com/openai/codex/pull/18697",
        )
        self.assertIn("PR #18697", merged_pr_detail)
        self.assertIn("测试 fixture", merged_pr_detail)
        self.assertNotIn("Title:", merged_pr_detail)

        guardian_detail = build_codex_detail(
            title="chore(guardian) disable mcps and plugins (#18722)",
            source_text="Disables apps, plugins, mcps for the guardian subagent thread",
            source_url="https://github.com/openai/codex/commit/14ebfbced9dc502713cf68d457ea78618563b7dc",
        )
        self.assertIn("guardian 子代理线程", guardian_detail)
        self.assertIn("执行边界", guardian_detail)
        self.assertNotIn("Disables apps, plugins, mcps", guardian_detail)

        realtime_detail = build_codex_detail(
            title="Update realtime handoff transcript handling (#18597)",
            source_text=(
                "This PR aims to improve integration between the realtime model and the codex agent by sharing more context with each other. "
                "In particular, we now share full realtime conversation transcript deltas in addition to the delegation message."
            ),
            source_url="https://github.com/openai/codex/commit/126bd6e7a8839a861ee9bb40ec72c72ea1bf7b4d",
        )
        self.assertIn("上下文共享", realtime_detail)
        self.assertIn("transcript deltas", realtime_detail)
        self.assertNotIn("This PR aims to improve integration", realtime_detail)


if __name__ == "__main__":
    unittest.main()
