# Daily Report Output Contract on Old Lane Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 reader-facing 日报输出从“跨 lane 主题总论稿”收回到老 `daily-lane` 的栏目式骨架，并让 `build-report` 在不重写选材引擎的前提下稳定产出符合新 contract 的 Markdown artifact。最终产物必须使用固定标题 `AI Agent 日报（YYYY-MM-DD）`、固定 9 个栏目映射与顺序、条目式栏目正文、段落尾极简外链引用、统一文末 `## 来源`，并通过真实 `2026-04-12` signals 验证。

**Architecture:**

- Contract layer：先用现有 contract / skill / template 的最小改动锁定标题、9 个栏目映射、固定顺序、禁用结构、正文引用规则和文末来源去重规则；除非实现被证明确实需要，否则不额外引入新的配置层。
- Render layer：保持现有 `build-report` 主链路，只把最终 Markdown 输出收回到“固定顺序下的非空栏目子序列 + 条目式正文 + 统一来源附录”。优先复用现有 artifact 边界，不先重塑一套新的中间模型。
- Validation layer：补一个轻量 contract 校验器，再加一个真实 `2026-04-12` signals 验收样例；focused fixtures 只保留最关键边界，不建设一整套新测试框架。
- Non-goal：不在这轮重写 ranking、quotas、lane 采集逻辑，不引入新的 citation DSL，不扩成通用渲染框架，不为了优雅先搭新的 section-config / schema 子系统。

**Tech Stack:**

- Markdown contracts and templates
- JSON Schema for the minimum `report artifact` render boundary
- Existing `build-report` skill pipeline
- Python helpers for output-contract validation
- Real `2026-04-12` signals fixtures for acceptance testing

---

## Task Order

- Task 1 先锁固定标题、9 栏映射与顺序，避免后续正文和验证各写各的。
- Task 2-3 优先改正文骨架、栏目渲染、段落级外链和文末来源，让最终 Markdown 先长对。
- Task 4 用最少量 focused fixtures 补关键边界。
- Task 5 用真实 `2026-04-12` signals 做验收样例。
- Task 6 最后把新 contract 接回主链路并收口回归验证。

### Task 1: 固定 reader-facing 标题、9 栏映射与顺序

**Files:**
- Create: `contracts/report-output-contract.md`
- Modify: `contracts/runtime-contracts.md`, `skills/build-report/SKILL.md`
- Test: None

- [ ] 在 `contracts/report-output-contract.md` 用中文锁定固定标题 `# AI Agent 日报（YYYY-MM-DD）`，并写死 9 个栏目映射、展示名与固定顺序：`x-feed`、`x-following`、`reddit-watch`、`claude-code-watch`、`codex-watch`、`openclaw-watch`、`github-trending-weekly`、`product-hunt-watch`、`polymarket-watch`；显式排除 `github-watch`。
- [ ] 在同一份 contract 文档中明确 reader-facing 展示名：`X 推荐流`、`X 关注流`、`Reddit 社区`、`Claude Code`、`Codex`、`OpenClaw`、`GitHub 趋势项目`、`Product Hunt 新品`、`Polymarket 市场`，禁止直接输出内部 lane id。
- [ ] 在 `contracts/runtime-contracts.md` 回写“最终正文栏目 = 固定顺序下的非空子序列”，并明确未来新增 lane 不自动进入 reader-facing contract。
- [ ] 在 `skills/build-report/SKILL.md` 同步这套 fixed mapping / fixed order，确保实现前期只有一个单点真源，不急着新开额外 config 文件。

Verification:

```bash
rg -n "AI Agent 日报|X 推荐流|Reddit 社区|Claude Code|Polymarket 市场|github-watch" contracts/report-output-contract.md contracts/runtime-contracts.md skills/build-report/SKILL.md
```

Exit Criteria:

- 标题、9 个栏目、固定顺序和排除 `github-watch` 的规则都被单点写死。
- 实现阶段不需要再从 lane registry 推断栏目集合，也不需要先搭独立 section-config 子系统。

### Task 2: 优先复用现有 artifact 边界，最小化承载新输出

**Files:**
- Create: None
- Modify: `contracts/report-artifact.schema.json`, `skills/build-report/SKILL.md`, `templates/report-body-template.md`
- Test: None

- [ ] 先审计现有 `contracts/report-artifact.schema.json` 和 `build-report` 当前输出边界，确认哪些字段已经足够承载“固定标题 + 非空栏目子序列 + 条目式正文 + 段落外链 + 文末来源”。
- [ ] 只有在现有 artifact 明确装不下时，才补“实现新输出必需”的最小字段；禁止一上来重塑成完整 `sections[] / entries[] / citations[] / used_sources[]` 新中间模型。
- [ ] 把空栏目省略规则、正文不再出现 `今日要点` / `正文` / `编辑结论`、以及文末统一 `## 来源` 的约束先落到 `skills/build-report/SKILL.md` 和模板要求里，不要优先把复杂度推给 schema。
- [ ] 如果最终验证发现 Markdown 产物已经可稳定校验，就不要为了“模型更优雅”继续扩 artifact schema。

Verification:

```bash
python -m json.tool contracts/report-artifact.schema.json >/dev/null
rg -n "artifact|title|report_date|source_lanes|summary" contracts/report-artifact.schema.json skills/build-report/SKILL.md templates/report-body-template.md
```

Exit Criteria:

- 新输出 contract 可以建立在现有 artifact 边界的最小补丁上。
- 没有为了这轮 reader-facing 调整先搭一套新的中间表示层。

### Task 3: 改写正文模板与栏目渲染规则

**Files:**
- Create: None
- Modify: `templates/report-body-template.md`, `skills/build-report/SKILL.md`, `contracts/report-output-contract.md`
- Test: None

- [ ] 把正文模板改成“标题后直接进入第一个非空栏目”的结构，不再生成任何摘要型前置块。
- [ ] 每个栏目只允许条目式 bullet 或短段落，不再在栏目内部生成 `###` repo 小节，也不再把多个 lane 重新拼成跨 lane 主题总论。
- [ ] 允许粗体结论句提升扫读效率，但禁止把所有条目机械写成同一模板；每条必须保留对象、变化点和与 AI / coding-agent / workflow 主线的关联事实。
- [ ] 明确 `claude-code-watch`、`codex-watch`、`openclaw-watch` 直接渲染为 reader-facing 二级栏目，不再挂到总 `GitHub` 栏位下。
- [ ] 明确每个栏目末尾不再输出 `### Sources`，正文结束后直接继续下一个非空栏目或进入文末来源区。

Verification:

```bash
rg -n "AI Agent 日报|### Sources|今日要点|正文|编辑结论" templates/report-body-template.md skills/build-report/SKILL.md contracts/report-output-contract.md
```

Exit Criteria:

- 新模板稳定输出“固定标题 + 栏目式正文”，不再回退成专题稿骨架。
- repo-specific lane 直接作为 reader-facing 栏目出现，没有额外嵌套层。

### Task 4: 实现段落级极简引用与统一来源附录

**Files:**
- Create: `helpers/validate_report_output_contract.py`
- Modify: `templates/report-body-template.md`, `contracts/report-output-contract.md`
- Test: `helpers/validate_report_output_contract.py`

- [ ] 让信息承载条目在段落尾部输出 1~3 个直达原始外链的极简标签，例如 `原帖`、`Release`、`GitHub`、`Reddit`、`Product Hunt`、`Polymarket`。
- [ ] 禁止正文引用 signal 内部路径；段落尾引用必须直接指向原始外链，且真正承载信息的条目至少带 1 个外链引用。
- [ ] 在文末固定输出 `## 来源`，并按 `### 栏目名` 分组；每组只收录正文实际用到的 URL，不导出当天所有采集来源。
- [ ] 实现来源去重规则为“栏目 + URL”：同栏同 URL 无论正文引用多少次，文末只列一次；同一 URL 出现在不同栏目时允许各自保留。
- [ ] 固定文末来源顺序为“该 URL 在本栏目正文首次被引用的出现顺序”，不要按字母序或抓取时间重排。

Verification:

```bash
rg -n "## 来源|原帖|Release|GitHub|Reddit|Product Hunt|Polymarket" templates/report-body-template.md contracts/report-output-contract.md helpers/validate_report_output_contract.py
```

Exit Criteria:

- 正文引用只承担即时点击职责，文末 `## 来源` 只承担统一回看与归档职责。
- “段落级极简外链 + 文末按栏目分组来源”这套新 contract 被明确且可校验地实现。

### Task 5: 用最少量 focused fixtures 补关键边界

**Files:**
- Create: `fixtures/report-output-contract/empty-section-omission.json`, `fixtures/report-output-contract/duplicate-url-same-section.json`
- Modify: `helpers/validate_report_output_contract.py`
- Test: `fixtures/report-output-contract/empty-section-omission.json`, `fixtures/report-output-contract/duplicate-url-same-section.json`, `helpers/validate_report_output_contract.py`

- [ ] 只保留两类最值钱的 synthetic fixtures：`空栏目省略` 和 `同栏同 URL 去重`；不要一开始铺满所有 focused cases。
- [ ] 在校验器中断言最终 Markdown 不包含 `今日要点`、`正文`、`编辑结论`、`### Sources` 等旧结构。
- [ ] 断言最终栏目仍按 fixed order 输出，空栏目不会泄漏空 `##` 标题。
- [ ] 断言文末来源分组标题使用 reader-facing 中文栏目名，且同栏同 URL 只出现一次。

Verification:

```bash
uv run python helpers/validate_report_output_contract.py fixtures/report-output-contract
```

Exit Criteria:

- 最关键的两个边界条件能自动复现并被校验。
- 没有在这一轮 reader-facing 调整里顺手建设一整套新 fixtures 体系。

### Task 6: 用真实 `2026-04-12` signals 做验收样例

**Files:**
- Create: `fixtures/real-2026-04-12-output-contract/collect-result.json`, `fixtures/real-2026-04-12-output-contract/expected-report.md`, `fixtures/real-2026-04-12-output-contract/expected-sources.json`, `helpers/evaluate_real_2026_04_12_output_contract.py`
- Modify: None
- Test: `fixtures/real-2026-04-12-output-contract/collect-result.json`, `fixtures/real-2026-04-12-output-contract/expected-report.md`, `fixtures/real-2026-04-12-output-contract/expected-sources.json`, `helpers/evaluate_real_2026_04_12_output_contract.py`

- [ ] 从真实 `2026-04-12` signals 生成一个稳定的 collect snapshot，作为这次 output contract 的验收输入，而不是手写伪数据。
- [ ] 基于真实 snapshot 产出 `expected-report.md`，只保留进入正文的非空栏目，并验证它们仍按固定 9 栏顺序的非空子序列出现。
- [ ] 在 `expected-report.md` 中覆盖固定标题、条目式正文、段落尾极简外链、无旧结构、文末 `## 来源` 分组和同栏同 URL 去重。
- [ ] 在 `expected-sources.json` 中记录每个 reader-facing 栏目的实际引用 URL 列表和首次出现顺序，供自动比对来源区是否漏项、错序或重复。
- [ ] 让 `helpers/evaluate_real_2026_04_12_output_contract.py` 同时检查 Markdown 结构和 sources appendix against expected data，确保验证建立在真实当天 signals 上。

Verification:

```bash
uv run python helpers/evaluate_real_2026_04_12_output_contract.py fixtures/real-2026-04-12-output-contract
```

Exit Criteria:

- 新 contract 在真实 `2026-04-12` signals 上成立，而不是只在合成 fixtures 上成立。
- 样例能直接暴露顺序漂移、空栏目泄漏、引用缺失和来源去重失败等真实渲染问题。

### Task 7: 接回主链路并完成回归收口

**Files:**
- Create: None
- Modify: `agent/daily-report-master-agent.md`, `skills/build-report/SKILL.md`
- Test: `helpers/validate_report_output_contract.py`, `helpers/evaluate_real_2026_04_12_output_contract.py`

- [ ] 在 `agent/daily-report-master-agent.md` 明确 `build-report` 现在必须输出新 contract 产物，并把 output-contract validation 作为 `build-report` 的完成条件。
- [ ] 把真实 `2026-04-12` 验收命令接入最小回归流程，确保未来修改不会把日报重新退回“总论稿 + 每栏 Sources”的旧错误形态。
- [ ] 只把校验接在现有主链路后面，不新增新的 orchestrator、渲染平台或通用引用框架。
- [ ] 明确本轮交付只重做 reader-facing output contract，不顺手扩大为新的选材框架、引用 DSL 或多模板系统。

Verification:

```bash
python -m json.tool contracts/report-artifact.schema.json >/dev/null
uv run python helpers/validate_report_output_contract.py fixtures/report-output-contract
uv run python helpers/evaluate_real_2026_04_12_output_contract.py fixtures/real-2026-04-12-output-contract
if rg -n "今日要点|正文|编辑结论|### Sources" templates/report-body-template.md fixtures/real-2026-04-12-output-contract/expected-report.md; then exit 1; else echo ok; fi
```
Exit Criteria:

- 主链路已经以新 output contract 为准绳，后续实现不会再把 reader-facing 日报写回旧结构。
- 固定 9 栏、固定标题、条目式正文、段落级极简外链、文末按栏目分组来源、空栏目省略和真实 `2026-04-12` 验证都进入明确的可执行任务与可运行校验。
