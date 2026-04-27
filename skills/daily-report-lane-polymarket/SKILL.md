---
name: daily-report-lane-polymarket
description: Generate the Polymarket 市场 section of the AI Agent daily report from raw corpus.
---
# Polymarket 市场 Lane
## Mission
AI/coding-agent 相关预测市场；质量不足 empty。
## Input
Read the lane package provided by the master:
- `input.md`
- `context.json`
- `raw/`

Do not use `selected_items.json` as primary judgment input. Raw corpus is the evidence source.
## Selection Rules
Select only items that can be explained concretely for an AI/coding-agent reader. Prefer specific releases, workflows, repos, discussions, failures, tools, versions, or user-visible changes.
## Rejection Rules
Reject items when:
- evidence is too thin;
- source link is missing;
- it is generic tech/news not relevant to AI/coding-agent workflows;
- it repeats another stronger item;
- it cannot be explained in concrete human terms.

## Lane-Specific Judgment
Only include markets relevant to AI/coding-agent ecosystem. If evidence is weak, output status `empty` with reason.

## Writing Style
Write Chinese-first, concrete, human-readable prose. Explain who did what, what changed, why it matters today, and what the reader can do with it. Keep source links.

## Forbidden Output
禁止使用：
- “趋势信息包含这些具体点”
- “这条原始信号给出的可核验信息集中在”
- “适合作为今日该栏目的迁移期素材”
- “具体变化见来源”
- “采集文本”
- “当前可作为”
- internal collector voice

## Output
Write exactly:
- `lane.md`: reader-facing markdown section only.
- `lane-meta.json`: JSON metadata with `lane`, `status`, `selected_count`, `rejected_count`, `sources`, `rejected`, and `notes`.
Allowed status: `ok`, `empty`, `degraded`, `blocked`.
Use `selected` and `rejected` reasoning in metadata so the master can audit the lane without rewriting it.
