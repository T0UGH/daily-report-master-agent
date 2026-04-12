---
title: Daily Report Master Agent Implementation Plan v0
date: 2026-04-12
tags:
  - daily-lane
  - signals-engine
  - agent
  - implementation-plan
status: draft
---

# Daily Report Master Agent Implementation Plan v0

## Goal

v0 只做一条能跑通的最小闭环：由一个主 agent 完成 `collect -> assess -> build-report -> verdict -> publish -> archive`，并稳定产出 `normal / degraded / blocked` 三种结果。

这版的完成标准不是“设计完整”，而是“边界清楚、产物最小、可以验证、能被 Hermes 第一阶段接入”。

## Scope / Non-goals

**Scope**

- 只做最小可运行版本，先锁运行边界，再补最小骨架与最小 fixtures。
- 前 5 个前置任务顺序固定，不换序：最小运行 contract -> 最小 failure matrix -> 最小幂等与重跑 -> Hermes 第一阶段宿主接口 -> `build-report = Editor + Humanizer`。
- v0 只有一个主 agent，`signals-engine` 继续作为外部工具调用。
- 第一轮以 Markdown contract 为主，不把所有对象都 schema 化。只对最关键的机器边界做 schema：`verdict`、`report artifact`、`run-state`、`Hermes run request/response`。
- `build-report` 对主 agent 只暴露一个 skill；内部顺序固定为 `Editor -> Humanizer -> final report artifact`。
- Feishu 是主交付面；Obsidian 只归档最终日报，且只在发布成功后执行。
- helper 只保留两个：`helpers/validate_contracts.py` 和 `helpers/evaluate_minimal_cases.py`。

**Non-goals**

- 不做多宿主平台抽象。
- 不做 OpenClaw 回切实现。
- 不做 CLI 主控制器。
- 不做厚重运行平台、长期状态系统、多 agent runtime。
- 不做 section 级细粒度 schema、复杂 DSL、额外 orchestration helper。
- 不把 runbook、examples、额外模板放进 v0 首轮交付。

## Minimal Flow

```text
Hermes cronjob
  -> daily-report-master-agent
  -> collect-signals
  -> assess-reportability
  -> build-report (Editor -> Humanizer)
  -> verdict
  -> publish-report
  -> archive-report
```

约束：

- `publish-report` 成功后才允许 `archive-report`。
- `archive-report` 失败会把结果降为 `degraded`，但不会推翻当天已成功的发布。
- `notify-ops` 只在 `degraded` 或 `blocked` 时触发。

## Deferred to v0.1+

- `collect result`、`publish result`、`archive result` 的 JSON Schema。
- 手工 runbook 与 `examples/*.json` 示例集。
- `templates/obsidian-note-shell.md` 等额外模板。
- 更完整的 failure matrix、更细的 degraded 分类、重试与 backoff 策略细化。
- 更细的 report section schema、质量评分规则、可观测性与运行指标。

## Task Order

- Task 1-5 是前置任务，顺序固定。
- Task 6-7 只能在 Task 5 完成后开始。
- 如果新增文件不在下面 deliverables 列表中，默认不做。

## Tasks

### Task 1. 最小运行 contract

**Why**

- 没有统一运行边界，后面的 failure matrix、Hermes 接口、fixtures 都会各写各的。
- v0 只需要锁主链路的最小输入输出，不需要把所有对象第一轮都 schema 化。

**Deliverables**

- 新建 `contracts/runtime-contracts.md`
- 新建 `contracts/verdict.schema.json`
- 新建 `contracts/report-artifact.schema.json`

**Steps**

- [ ] 在 `contracts/runtime-contracts.md` 用中文写清 `collect result`、`report artifact`、`verdict`、`publish result`、`archive result` 的最小字段与语义。
- [ ] 明确根规则：只要至少有一条有用内容，日报就成立。
- [ ] 明确 `verdict` 只允许 `normal / degraded / blocked`。
- [ ] 只把 `verdict` 和 `report artifact` 做第一轮 schema；其余对象先保留为 Markdown contract。
- [ ] 在文档里写清哪些字段是必需，哪些字段允许为空或缺失。

**Verification**

```bash
python -m json.tool contracts/verdict.schema.json >/dev/null
python -m json.tool contracts/report-artifact.schema.json >/dev/null
rg -n "只要至少有一条有用内容，日报就成立|normal|degraded|blocked" contracts/runtime-contracts.md contracts/verdict.schema.json
```

**Exit Criteria**

- `contracts/runtime-contracts.md` 可以单独回答主链路 5 个对象的最小边界。
- 机器可校验的 schema 只有 `verdict` 与 `report artifact`，没有扩张到全量 contract。

### Task 2. 最小 failure matrix

**Why**

- 不先锁失败语义，后面的 verdict、通知、发布、归档都会漂移。
- v0 只需要覆盖必须先定下来的最小场景，不需要把所有组合铺满。

**Deliverables**

- 新建 `contracts/failure-matrix.md`
- 更新 `contracts/runtime-contracts.md`

**Steps**

- [ ] 在 `contracts/failure-matrix.md` 只保留最小必测场景：完全成功、部分 lane 异常但仍有内容、无可用内容、发布成功但归档失败、系统异常且无内容。
- [ ] 每个场景写清触发条件、最终 verdict、是否 publish、是否 archive、是否 notify-ops。
- [ ] 明确 `normal / degraded / blocked` 的判定边界，避免同一场景出现两种解释。
- [ ] 把 failure matrix 中涉及的关键规则同步回 `contracts/runtime-contracts.md`。

**Verification**

```bash
rg -n "完全成功|部分 lane 异常|仍有内容|无可用内容|发布成功.*归档失败|系统异常" contracts/failure-matrix.md
rg -n "normal|degraded|blocked" contracts/failure-matrix.md contracts/runtime-contracts.md
```

**Exit Criteria**

- `contracts/failure-matrix.md` 至少覆盖 5 个最小场景。
- 每个场景都能明确回答“最终是什么状态”“还要不要继续下一步”“用户会看到什么”。

### Task 3. 最小幂等与重跑

**Why**

- cron 重试、人工 rerun、半成功 rerun 如果不先定语义，宿主无法安全重跑。
- 这部分不需要厚状态平台，只要定义最小 run-state 和重跑规则。

**Deliverables**

- 新建 `contracts/idempotency-rerun.md`
- 新建 `contracts/run-state.schema.json`
- 更新 `contracts/runtime-contracts.md`

**Steps**

- [ ] 定义一个最小 `run_key` 规则，保证同一天同一触发上下文可以判重。
- [ ] 在 `contracts/run-state.schema.json` 中定义宿主必须保留的最小运行状态。
- [ ] 在 `contracts/idempotency-rerun.md` 中写清 `cron 重试`、`人工 rerun`、`publish 已成功后 rerun`、`archive 已成功后 rerun` 的处理规则。
- [ ] 明确哪些结果要落到 `run-state`，以便 Hermes 判断是否跳过重复发布或重复归档。
- [ ] 保持范围最小，不引入任务队列、分布式锁、长期状态服务。

**Verification**

```bash
python -m json.tool contracts/run-state.schema.json >/dev/null
rg -n "run_key|cron 重试|人工 rerun|publish 已成功|archive 已成功|半成功" contracts/idempotency-rerun.md
```

**Exit Criteria**

- Hermes 只靠 `run_key` 与 `run-state` 就能判断是否允许重跑。
- 文档能明确回答“会不会重复发 Feishu”“会不会重复归档 Obsidian”。

### Task 4. Hermes 第一阶段宿主接口

**Why**

- v0 的唯一接入宿主就是 Hermes，接口不清楚，主 agent 无法落地。
- 这一步只回答 Hermes 现在需要什么，不提前抽象成通用 host layer。

**Deliverables**

- 新建 `contracts/hermes-host-interface.md`
- 新建 `contracts/hermes-run-request.schema.json`
- 新建 `contracts/hermes-run-response.schema.json`

**Steps**

- [ ] 在 `contracts/hermes-host-interface.md` 中写清 Hermes 提供的最小输入、主 agent 返回的最小输出、宿主负责保存的最小状态。
- [ ] 只为 Hermes request/response 建 schema，不扩成多宿主协议。
- [ ] 在响应 contract 中纳入 `verdict`、最小 `run-state`、发布与归档结果摘要。
- [ ] 明确宿主与 agent 的责任边界：谁负责触发、谁负责判重、谁负责持久化最小状态。
- [ ] 明确写出“本版不含 OpenClaw 回切实现，不含多宿主抽象”。

**Verification**

```bash
python -m json.tool contracts/hermes-run-request.schema.json >/dev/null
python -m json.tool contracts/hermes-run-response.schema.json >/dev/null
rg -n "Hermes|run_key|verdict|run-state|publish|archive|宿主" contracts/hermes-host-interface.md
if rg -n "OpenClaw|多宿主|host abstraction|runtime abstraction" contracts/hermes-host-interface.md; then exit 1; else echo ok; fi
```

**Exit Criteria**

- Hermes 可以只靠 request/response contract 接入第一阶段运行。
- 文档没有引入额外宿主层、回切层或平台抽象。

### Task 5. `build-report = Editor + Humanizer`

**Why**

- 如果 `Editor` 和 `Humanizer` 继续以两条平级主流程存在，主 agent 的编排边界会继续摇摆。
- v0 只需要一个可消费的成品 artifact，不需要暴露中间产物。

**Deliverables**

- 新建 `skills/build-report/SKILL.md`
- 新建 `templates/report-body-template.md`
- 更新 `contracts/report-artifact.schema.json`
- 更新 `contracts/runtime-contracts.md`

**Steps**

- [ ] 在 `skills/build-report/SKILL.md` 中明确输入、输出、内部顺序：`Editor -> Humanizer -> final report artifact`。
- [ ] 明确主 agent 只消费一个最终 `report artifact`，不依赖两个平级中间步骤。
- [ ] 在 `contracts/report-artifact.schema.json` 中只保留成品日报所需字段，不扩成 section 级 schema。
- [ ] 在 `templates/report-body-template.md` 中提供一个最小正文模板，不再新增额外模板变体。
- [ ] 把这条边界同步回 `contracts/runtime-contracts.md`。

**Verification**

```bash
rg -n "Editor|Humanizer|final report artifact|单一 skill" skills/build-report/SKILL.md
python -m json.tool contracts/report-artifact.schema.json >/dev/null
rg -n "只要至少有一条有用内容，日报就成立|report artifact" contracts/runtime-contracts.md
```

**Exit Criteria**

- `build-report` 对主 agent 是一个单一 skill，而不是两条平级主流程。
- `report artifact` 足够支撑后续 verdict、publish、archive，但没有扩成厚 contract。

### Task 6. 主 agent 与最小技能骨架

**Why**

- 前 5 个边界锁定后，必须有一个最小骨架把链路串起来，否则 plan 仍然不可执行。
- 这一步只补最小运行骨架，不做 CLI controller，不做多 agent runtime。

**Deliverables**

- 新建 `agent/daily-report-master-agent.md`
- 新建 `skills/collect-signals/SKILL.md`
- 新建 `skills/assess-reportability/SKILL.md`
- 新建 `skills/publish-report/SKILL.md`
- 新建 `skills/notify-ops/SKILL.md`
- 新建 `skills/archive-report/SKILL.md`
- 新建 `templates/feishu-report.md`
- 新建 `templates/ops-notice.md`

**Steps**

- [ ] 在 `agent/daily-report-master-agent.md` 中固定主链路顺序：`collect-signals -> assess-reportability -> build-report -> verdict -> publish-report -> archive-report`。
- [ ] 明确 `notify-ops` 只在 `degraded` 或 `blocked` 时触发。
- [ ] 在 `skills/collect-signals/SKILL.md` 中写清对外部 `signals-engine` 的最小调用边界。
- [ ] 在 `skills/assess-reportability/SKILL.md` 中写清何时成立日报、何时直接进入 `blocked`。
- [ ] 在 `skills/publish-report/SKILL.md` 与 `templates/feishu-report.md` 中写清 Feishu 最小发布产物。
- [ ] 在 `skills/archive-report/SKILL.md` 中写清“只归档最终日报，且只在发布成功后执行”。
- [ ] 在 `skills/notify-ops/SKILL.md` 与 `templates/ops-notice.md` 中写清降级或阻塞时的最小通知内容。
- [ ] 保持骨架最小，不增加 CLI 主入口、应用层 runner、工作流平台包装。

**Verification**

```bash
test -f agent/daily-report-master-agent.md
rg -n "collect-signals|assess-reportability|build-report|publish-report|notify-ops|archive-report" agent/daily-report-master-agent.md
if rg -n "CLI|controller|main.py|OpenClaw|多宿主|multi-agent" agent/daily-report-master-agent.md; then exit 1; else echo ok; fi
```

**Exit Criteria**

- 主 agent 文档能把最小链路完整串起来。
- 所有 skill 都只描述自己的最小责任边界，没有额外平台逻辑。

### Task 7. 最小 fixtures 与轻量 helper

**Why**

- 没有最小样例，就无法证明 contract、failure matrix、Hermes response 真的能落地。
- v0 只需要能验证 3 个结果：`normal / degraded / blocked`。

**Deliverables**

- 新建 `helpers/validate_contracts.py`
- 新建 `helpers/evaluate_minimal_cases.py`
- 新建 `fixtures/minimal-normal/collect-result.json`
- 新建 `fixtures/minimal-normal/expected-hermes-response.json`
- 新建 `fixtures/minimal-degraded/collect-result.json`
- 新建 `fixtures/minimal-degraded/expected-hermes-response.json`
- 新建 `fixtures/minimal-blocked/collect-result.json`
- 新建 `fixtures/minimal-blocked/expected-hermes-response.json`

**Steps**

- [ ] 在 3 组 fixtures 中分别覆盖 `normal`、`degraded`、`blocked` 的最小输入与期望输出。
- [ ] 让 `helpers/validate_contracts.py` 只做 schema 与字段校验，不承担主流程 orchestration。
- [ ] 让 `helpers/evaluate_minimal_cases.py` 只做最小场景求值与结果比对，不生成运行平台。
- [ ] 用 fixtures 反推检查 `failure-matrix.md`、`runtime-contracts.md`、`hermes-run-response.schema.json` 是否一致。
- [ ] 保持范围最小，不新增 runbook、不新增 examples、不新增第三个 helper。

**Verification**

```bash
uv run python helpers/validate_contracts.py fixtures/minimal-normal
uv run python helpers/validate_contracts.py fixtures/minimal-degraded
uv run python helpers/validate_contracts.py fixtures/minimal-blocked
uv run python helpers/evaluate_minimal_cases.py fixtures
```

**Exit Criteria**

- 3 组 fixtures 都能通过校验，并映射到预期的 `normal / degraded / blocked`。
- 仓库中的 helper 只有 `validate` 与 `evaluate` 两个，没有演变成主控制器。

## Done Definition

- 前 5 个前置任务按固定顺序完成，且没有插入额外平台层。
- `runtime-contracts.md`、`failure-matrix.md`、`idempotency-rerun.md`、`hermes-host-interface.md` 能共同定义 v0 运行边界。
- `build-report` 已明确等于 `Editor + Humanizer`，对主 agent 只暴露单一成品 artifact。
- 主 agent、最小技能骨架、最小模板、最小 fixtures、两个 helper 足以支撑第一轮实现。
- 验证命令可以证明 `normal / degraded / blocked` 三种结果都被覆盖。
- v0 仍然停留在“最小可运行版本”，没有扩到多宿主、回切实现、CLI 控制器或厚运行平台。
