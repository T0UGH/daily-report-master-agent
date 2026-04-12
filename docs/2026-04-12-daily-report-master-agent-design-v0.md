---
title: Daily Report Master Agent Design v0
date: 2026-04-12
tags:
  - daily-lane
  - signals-engine
  - agent
  - design
  - orchestrator
status: draft
source_repo: https://github.com/T0UGH/knowledge-vault
---

# Daily Report Master Agent Design v0

这份设计文档用于承接同日的 brainstorm 记录，并把当前已经收敛的内容整理成一版**可继续推进实现设计的正式骨架**。

这里先不追求把所有细节定死，而是把：

- 系统身份
- 运行边界
- 仓库形态
- 关键职责分层
- 最小成立规则

先钉住，避免后续实现时再回到“它到底是什么”这个问题上反复摇摆。

---

## 一、设计目标

建立一个真正对**每日 AI 日报结果**负责的主 agent 系统。

这个系统的目标不是“把几个已有步骤串起来”，而是：

> **把每日 signals → 日报生成 → 飞书发布 → 最终归档，收敛成一个单一 owner 负责的日报生产链路。**

该系统第一阶段先运行在 **Hermes cronjob** 上，但长期不应与 Hermes 强绑定。

---

## 二、核心设计结论

### 1. 一个 cron，一个主 agent owner

日报系统的外部入口只保留一个 cron 主入口。

这个 cron 背后不是多个并列责任主体，而是一个真正的主 agent owner。它需要对以下问题负责：

- 今天有没有日报输入
- 今天是否应生成日报
- 今天结果属于正常 / 降级 / 阻断
- 是否需要额外运维通知
- 是否完成对外交付

### 2. 交付哲学是强 delivery

系统的核心不是“只有输入很完整才发”，而是：

> **只要至少有一条有用内容，日报就成立。**

因此：

- 短日报完全允许
- 单 lane 日报完全允许
- 一两条高价值内容也算正常成品
- blocked 应该是罕见状态

### 3. 内容层判断优先于系统异常

`signals-engine` 的职责是提供 signal 输入，不是替日报系统提前做最终内容判断。

因此：

- 是否“值得看”，主要由内容层判断
- 系统层异常不应轻易压过内容层结果
- 即使某些 lane 异常，只要最终仍能形成成立日报，系统应优先交付

### 4. 主聊天是唯一主交付面

日报与必要时的运维通知，都发往同一个主聊天。

但：

- 正常日不刷运维消息
- 降级/阻断时才额外出现运维通知
- 运维通知只讲状态、异常、最终链接，不做内容总结

### 5. Obsidian 只承担最终日报归档角色

Obsidian 不是运行日志仓库，也不是中间草稿仓库。

它的角色是：

> **最终日报归档库**

约束：

- 只归档最终日报
- 不归档运维通知
- 不归档中间草稿
- 允许加 metadata 壳，但不重写正文
- 归档在 Feishu 成功后进行
- 归档失败不影响当天日报交付成功

---

## 三、系统身份：独立 agent pack，而不是宿主私有流程

### 1. 第一阶段宿主：Hermes cronjob

第一阶段为了快速落地，系统先运行在 Hermes cronjob 上。

这是一个**宿主选择**，不是系统本体定义。

### 2. 长期身份：runtime-agnostic 的 agent pack

该系统长期不应被定义成：

- Hermes-only cron prompt
- `daily-lane` 的附属流程
- `signals-engine` 的子模块
- command-heavy 的 workflow app

而应被定义成：

> **一个 runtime-agnostic 的 daily report master agent pack**

这意味着：

- 未来可以切回 OpenClaw
- 宿主可替换
- 主 agent 定义、skills、contracts、templates 不应依赖宿主方言

### 3. 主入口是主 agent prompt，不做 CLI 主入口

该 pack 的主入口是主 agent 本身，而不是命令行外壳。

因此：

- 不单独设计一个 CLI controller 作为第一入口
- 宿主通过加载主 agent 定义来运行系统
- 少量 helper scripts 可以存在，但只是辅助，不负责主流程控制

---

## 四、与现有仓库的关系

### 1. 与 `signals-engine` 的关系

`signals-engine` 是该系统的**外部 signal collection tool**。

主 agent pack 应通过：

- `uvx`
- 或 CLI

调用 `signals-engine`，而不是通过源码级 import 强耦合它的内部模块。

这样可以保证：

- signal 层与 orchestration 层解耦
- `signals-engine` 继续专注 signal/source/lane/runtime
- 主 agent pack 专注日报判定、生成、发布、归档

### 2. 与 `daily-lane` 的关系

`daily-lane` 是当前内容层经验、prompt、流程与文档的重要来源。

第一阶段设计会大量借用这里已经沉淀出来的：

- Editor / Humanizer 经验
- Feishu 发布习惯
- 日报流程边界

但长期 identity 不应继续绑定在 `daily-lane` 仓库里。

### 3. 与 `knowledge-vault` 的关系

`knowledge-vault` 用于记录：

- brainstorm
- design
- 决策记录
- 演化过程

但不应承担运行时主定义载体的角色。

---

## 五、仓库形态设计

这个独立新仓库第一阶段应组织成一个**中等厚度的 agent pack**。

不是纯文档壳，也不是大 app。

### 建议顶层骨架

- `agent/`
- `skills/`
- `contracts/`
- `templates/`
- `helpers/`
- `docs/`

可选：
- `examples/` 或 `fixtures/`

### 各层职责

#### `agent/`
放主 agent 定义。

回答：
- 谁是主脑
- 状态机是什么
- 如何调 skills
- 如何做最终 verdict

#### `skills/`
放主 agent 可见的职责块。

第一版按中等颗粒度拆成：
- `collect-signals`
- `assess-reportability`
- `build-report`
- `publish-report`
- `notify-ops`
- `archive-report`

其中，`build-report` 在第一版中应被明确理解为：

> **一个包含 `Editor + Humanizer` 的内容构建职责块。**

也就是说，主 agent 第一版不直接分别编排 `Editor skill` 与 `Humanizer skill` 两个平级外部步骤，而是把它们收敛在 `build-report` 这个技能边界内。这样可以让：

- 主 agent 的状态机更稳定
- `report-contract` 先围绕“成品是否生成”来定义
- 内容层内部链路在后续迭代时仍可重构，而不必每次改主流程

#### `contracts/`
放运行时依赖的成品定义层。

至少应包含：
- `report-contract`
- `verdict-contract`
- `archive-note-contract`

#### `templates/`
放最终对外表达模板，而不是内部 agent prompt。

例如：
- 正常日轻量发布消息模板
- 降级日运维通知模板
- 阻断日通知模板
- Obsidian metadata 壳模板

#### `helpers/`
放少量辅助脚本与小工具。

允许：
- formatter
- metadata builder
- schema validator
- 文件整理
- 小型结果归并/转换

不允许：
- CLI 主入口
- 主流程 controller
- 总 runner

#### `docs/`
放设计、决策、演化记录。

---

## 六、主 agent 结构设计

### 1. agent 层只有一个主 agent

第一版不引入多个平级 agent。

原因：

- 需要保持 owner 边界清晰
- 需要保持 pack 的身份纯粹
- 避免仓库从“主 agent pack”漂成“多 agent runtime”

### 2. 主 agent 风格：orchestrator，而不是胖主脑

主 agent 负责：

- 系统目标
- 状态机
- 决策规则
- 调用顺序
- 最终 verdict

但不吞掉所有执行细节。

执行细节应主要下沉到 skills 与 contracts/templates 层。

---

## 七、状态模型

### 1. 正常 `normal`
条件：
- 有可发日报
- 没有值得额外打扰用户的异常

行为：
- 发日报
- 带轻量存在感
- 不额外发运维通知

### 2. 降级 `degraded`
条件：
- 仍有可发日报
- 存在值得通知用户的异常或缺口

行为：
- 发日报
- 日报顶部允许轻量降级标记
- 额外发一条运维通知

### 3. 阻断 `blocked`
仅在以下两种情况下成立：

1. 日报里没有任何有用内容
2. 一个 lane 都没出 signal

对外优先表达为：

> **今天没有日报输入 / 未生成日报**

而不是急着做重归因。

---

## 八、`report-contract` 的第一原则

`report-contract` 第一版不应过早做过细 section schema，而应先抓住成品成立条件与边界。

其第一原则应明确写成：

> **只要至少有一条有用内容，日报就成立。**

这条原则是整个系统的根规则，并直接覆盖：

- 短日报允许
- 单 lane 日报允许
- blocked 只在确实无内容时出现
- 不为“像完整日报”而硬凑

---

## 九、最小运行 contract 与宿主接口

在进入 implementation plan 前，第一版必须先补齐一组**最小运行 contract**，但不把它们扩成厚重平台协议。

### 1. 最小运行 contract 集合

第一版至少应明确这 5 个结构化对象：

- `collect result`：本次 collect 是否完成、产出了哪些可供后续消费的输入、有哪些关键异常
- `report artifact`：本次日报成品是否生成、成品路径是什么、它是否满足最终发布/归档真源要求
- `verdict`：本次 run 的最终状态（`normal` / `degraded` / `blocked`）及其最小原因字段
- `publish result`：Feishu 是否发布成功、主链接是什么、是否需要后续告警
- `archive result`：Obsidian 是否归档成功、归档路径是什么、是否影响最终 run 状态

这里的重点不是先把字段铺满，而是先让 implementation plan 有稳定依赖面。

### 2. 第一阶段宿主接口

既然第一阶段宿主是 Hermes cronjob，就需要定义一个**最小宿主接口**，回答下面这些问题：

- 宿主传给主 agent 的最小上下文是什么
- 主 agent 运行后必须返回哪些结构化结果
- 宿主如何判断本次 run 是成功、降级还是阻断
- 宿主是否需要保存额外状态，还是只消费主 agent 的最终返回

当前设计只要求写清最小必需问题，不为未来多宿主抽象提前做厚框架。

---

## 十、最小主流程

第一版系统主流程可理解成：

1. **Collect**
   - 调用 `signals-engine`
   - 获取当天 signal 输入

2. **Assess input**
   - 判断是否存在日报输入
   - 判断是否进入 blocked 或继续生成

3. **Build report**
   - 由内容层判断是否存在至少一条有用内容
   - 通过 `build-report` 这一职责块完成 `Editor + Humanizer`
   - 生成日报草稿与最终稿

4. **Verdict**
   - 主 agent 判定 normal / degraded / blocked

5. **Publish**
   - 发布 Feishu 日报
   - 必要时发运维通知

6. **Archive**
   - 将最终日报归档到 Obsidian

---

## 十一、状态机补充：failure matrix 与幂等/重跑语义

当前 design 不展开完整状态表，但 implementation plan 前必须至少补一版最小 failure matrix，回答典型组合场景：

- 某些 lane 异常但最终仍有日报内容时，何时算 `normal`，何时算 `degraded`
- Feishu 成功而 archive 失败时，最终 run 如何落状态
- 没有日报内容且伴随系统异常时，对外消息如何收束为“没有日报输入 / 未生成日报”

同时，需要明确最小幂等/重跑语义，避免 cron 与人工 rerun 时产生重复副作用：

- 重复触发是否允许再次发 Feishu
- 半成功 run 重新执行时，如何避免重复发布与重复归档
- 一次 run 至少要留下哪些结构化状态，供后续判断是否需要重跑

这里同样只要求最小必要定义，不提前扩成完整运行平台。

---

## 十二、当前明确不做的事

为了避免设计再次滑向过度细化，当前先明确不在 v0 design 中展开：

- 更细粒度的 prompt 结构切分
- 更细 section 级 schema
- 多日健康追踪逻辑
- 多 agent 分工
- CLI 化主入口
- 过早把 helper 扩成 runtime

这些都留到后续真正进入 implementation planning 时，再按需要展开。

---

## 十三、一句话版设计结论

`daily report master agent` 的第一版设计应被理解成：

> **一个运行在 Hermes cronjob 上、但不与 Hermes 强绑定的 runtime-agnostic agent pack。**

它以：

- 一个 orchestrator 主 agent
- 一组中颗粒度 skills
- 一层明确的 contracts
- 一层对外表达 templates
- 少量 helper scripts

来承接每日 AI 日报的完整责任，并通过 `uvx` / CLI 调用 `signals-engine` 作为外部 signal 输入层。
