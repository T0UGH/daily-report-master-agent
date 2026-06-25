---
name: daily-report-lane-rize
description: Generate the Rize AI 工具榜 section of the AI Agent daily report from Rize weekly AI tools ranking raw corpus.
---
# Rize AI 工具榜 Lane
## Mission
从 Rize weekly AI tools ranking 中产出“Rize AI 工具榜”栏目，保留榜单排名、项目名、GitHub repo 链接、Rize 榜单页和页面描述。

## Input
Read the lane package provided by the master:
- `input.md`
- `context.json`
- `raw/`
- `history/` if present

Do not use `selected_items.json` as primary judgment input. Raw corpus is the evidence source.
Use recent reports only as reference-only dedupe context. For this lane, rankings are current-list facts; do not remove the whole section just because the same source existed yesterday. You may avoid exact duplicate wording, but keep today’s rank evidence.

## Selection Rules
- Select up to 8 ranked tools from the raw Rize corpus, normally the highest-ranked entries.
- Each selected item must have a concrete GitHub repo URL or Rize/source URL.
- Preserve the numeric rank (`#1`, `#2`, …) in the reader-facing bullet.
- Prefer AI/coding-agent/developer-tool/workflow-relevant items when the top list contains mixed tools; otherwise keep the top ranked items and state only facts present in raw evidence.

## Rejection Rules
Reject items when:
- repo/source link is missing;
- description is too thin to explain what the tool is;
- it is clearly irrelevant to AI/coding-agent/tooling readers and enough stronger ranked items exist;
- it duplicates another selected repo.

## Usefulness Bar（MT 反馈 2026-06-25）
长度不是问题；问题是“有用信息密度”。Rize 是榜单栏目，可以保留排名事实，但不要只机械搬榜。每个入选条目必须写清：它是什么、为什么对 AI/coding-agent/developer-tool/workflow 读者有用、有什么可核验来源。如果只能写出空泛描述且没有 repo/source 细节，宁可少选或标 empty。

## Writing Style
Write Chinese-first, concrete, human-readable prose. Keep links.

每条默认 1 句，最多 2 句：`#排名 + 项目名 + 它是什么/做什么 + repo/source link`。
不要把 Rize 榜单误写成 GitHub AI 项目榜或 GitHub 趋势榜；栏目标题必须是：`## Rize AI 工具榜`。

## Forbidden Output
禁止使用：
- “值得关注/值得跟踪/说明生态变化”等空泛判断，除非同句给出具体证据；
- “趋势信息包含这些具体点”
- “这条原始信号给出的可核验信息集中在”
- “适合作为今日该栏目的迁移期素材”
- “采集文本”
- internal collector voice

## Output
Write exactly:
- `lane.md`: reader-facing markdown section only.
- `lane-meta.json`: JSON metadata with `lane`, `status`, `selected_count`, `rejected_count`, `sources`, `rejected`, and `notes`.
Allowed status: `ok`, `empty`, `degraded`, `blocked`.
Use `selected` and `rejected` reasoning in metadata so the master can audit the lane without rewriting it.
