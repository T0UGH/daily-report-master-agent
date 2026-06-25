---
name: daily-report-lane-github-trending
description: Generate the GitHub 趋势项目 section of the AI Agent daily report from raw corpus.
---
# GitHub 趋势项目 Lane
## Mission
GitHub Trending 中真正影响 AI/coding-agent workflow 的项目。
## Input
Read the lane package provided by the master:
- `input.md`
- `context.json`
- `raw/`
- `history/` if present

Do not use `selected_items.json` as primary judgment input. Raw corpus is the evidence source.
Use recent reports only as reference-only dedupe context. Before selecting or writing, read yesterday and day-before-yesterday report files listed in `context.json` `recent_report_paths` or package `history/`. Reject exact repeats or substantially unchanged topics. Keep meaningful follow-ups with new facts and state what changed. Do not dedupe weather/current market items purely because yesterday had the same section. This is lane-agent judgment, not code-controlled filtering.
## Selection Rules
Select only items that can be explained concretely for an AI/coding-agent reader. Prefer specific releases, workflows, repos, discussions, failures, tools, versions, or user-visible changes.

Hard GitHub repo floor: every selected repository must have verified `stars >= 100`. Reject repositories below 100 stars and repositories whose star count cannot be verified from raw corpus or GitHub metadata. Discovery/search queries for GitHub repositories must include `stars:>=100`; do not spend reader attention on tiny repos unless MT explicitly asks for an early-stage scan.
## Rejection Rules
Reject items when:
- evidence is too thin;
- source link is missing;
- it is generic tech/news not relevant to AI/coding-agent workflows;
- it repeats another stronger item;
- it cannot be explained in concrete human terms.


## Usefulness Bar（MT 反馈 2026-06-25）
长度不是问题；问题是“有用信息密度”。宁可少选，也不要用低信息量内容填满栏目。每个入选条目必须同时满足：
- **新信息**：今天相对昨天/前天或常识，具体新增了什么；如果只是同一产品/观点反复出现，必须写出新增事实，否则拒绝。
- **可执行/可判断**：读者看完能知道该试用、避坑、跟进、学习、忽略中的哪一种，以及理由。
- **证据锚点**：至少包含一个可核验事实（版本号、repo/产品名、作者、数据、价格、接口/功能变化、错误现象、讨论分歧、链接来源）。
- **非空泛价值**：禁止只写“值得关注/说明趋势/生态变化/更成熟/更清楚”；如果没有具体“为什么有用”，就不要选。

写作时优先保留事实与判断依据；不要为了变短删除最有用的细节。

## Lane-Specific Judgment
Select only repositories with clear AI/coding-agent workflow relevance. Reject generic AI infra unless the raw evidence shows agent workflow impact. For every selected repo explain: what it is, what changed or why it surfaced today, and why an AI/coding-agent reader should care.

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
