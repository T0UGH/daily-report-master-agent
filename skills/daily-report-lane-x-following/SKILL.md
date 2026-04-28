---
name: daily-report-lane-x-following
description: Generate the X 关注 section of the AI Agent daily report from raw corpus.
---
# X 关注 Lane
## Mission
X 关注流里可信账号的 AI/coding-agent 讨论。目标 5-10 条。
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
Write human paraphrase, not tweet dumps. Explain who did what, what changed, and what result/blocker/background matters. Target around 10 high-signal items for x-feed and 5-10 for x-following. Avoid internal collector voice.

## Writing Style
Write Chinese-first, concrete, human-readable prose. Keep source links.

子条目要信息密度高但不要拖长：
- 每条默认 1-3 句；信息简单时 1 句，复杂更新最多 3 句。
- 单条正文最长不超过 200 个中文字符；链接不计入正文长度。
- 句式优先：`发生了什么 + 关键事实/数字 + 对读者有什么用/风险`，少写铺垫和评价。
- 删除“值得关注/值得跟踪/说明生态变化”等空泛判断，除非同句给出具体证据。

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
