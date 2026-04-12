---
title: Daily Report Master Agent Brainstorm v1
date: 2026-04-12
tags:
  - daily-lane
  - signals-engine
  - feishu
  - obsidian
  - agent
  - orchestrator
status: draft
source_repo: https://github.com/T0UGH/knowledge-vault
---

# Daily Report Master Agent Brainstorm v1

记录时间：2026-04-12 14:26 CST
状态：**brainstorm 记录，暂不进入实现**

## 这轮讨论要解决什么

目标不是再拼几个松散定时任务，而是定义一个**单一 cron 主 agent**，让它真正对每天日报结果负责。

这个主 agent 需要接管：

1. 当天 signals 采集
2. 当天日报是否成立的判断
3. 日报生成与发布
4. 必要时的运维通知
5. 最终日报归档到 Obsidian（后续实现）

---

## 当前共识

### 1. 一个 cron，一个 owner

- 只保留一个 cron 主入口
- 主 agent 是唯一 owner
- 它不是薄调度器，而是“值班主编 + 调度员”

### 2. 交付哲学：强 delivery

- 这套系统的目标是**稳定、高频、诚实地交付日报**
- 哪怕只有 **1 条有用内容**，也应该发
- 短日报是正常形态，不需要为了“像日报”去硬凑
- blocked 应该是罕见状态

### 3. 内容层优先于系统层异常

- “值不值得看”主要由内容层判断
- `signals-engine` 负责抓取、结构化、准备候选输入
- Editor / 内容层负责判断今天是否至少有 1 条值得进入日报的内容
- 系统层异常不应轻易压过内容层结果

### 4. 主聊天是唯一交付面

- 日报发到主聊天
- 运维通知也发到主聊天
- 但运维通知只在必要时出现，不要每天刷屏

### 5. 运维通知只讲状态，不做内容总结

运维通知只负责：

- 状态
- 异常
- 最终产物链接

明确不做：

- 内容摘要
- 再讲一遍日报重点

### 6. 正常 / 降级 / 阻断

#### 正常
- 有可发内容
- 没有值得额外打扰用户的异常
- 发日报，带一点轻量存在感

#### 降级
- 仍有可发内容
- 但存在值得通知用户的异常或缺口
- 发日报
- 日报顶部放轻量降级标记
- 主聊天额外发运维通知

#### 阻断
只在两种情况下成立：

1. 日报里没有任何有用内容
2. 一个 lane 都没出 signal

对外优先表达为：

- **今天没有日报输入 / 未生成日报**

不在主流程里过早归因为“采集失败”或“今天真没内容”。

### 7. 主 agent 的内部组织

外部只有一个 owner，但内部可以有少量明确子角色：

- Collect runner：跑 signals-engine，返回结构化结果
- Editor：判断内容价值，生成日报草稿
- Humanizer：生成最终人类可读文本
- Publisher / Archiver：负责 Feishu 发布与后续 Obsidian 归档
- Master agent：收集阶段结果并做最终裁决

### 8. Obsidian 的角色

Obsidian 只承担一个角色：

> **最终日报归档库**

当前共识：

- 只归档最终日报
- 不归档运维信息
- 不归档中间草稿
- 归档内容以 final report 正文为真源
- 允许加一层轻量 Obsidian metadata 壳
- 时机是 **Feishu 成功后再归档**
- 归档失败不影响当天日报成功

### 9. 主 agent 只主要处理“今天”

- 默认只对今天负责
- 不把多日趋势、连续失败分析压进主流程
- 跨天健康追踪如果以后要做，应作为附加能力

---

## 第三形态：独立 agent pack，而不是绑死在 Hermes

### 1. 第一运行形态先是 Hermes cronjob

当前第一阶段仍然应该先落在 **Hermes cronjob** 上，方便尽快跑起来。

但这只是**运行宿主**，不是系统的长期身份本体。

### 2. 不与 Hermes 强绑定，未来可切回 OpenClaw

这层调度逻辑不应该长成 Hermes-only。

目标是：

- 先由 Hermes 托管执行
- 未来如果要切回 OpenClaw，也能切回去
- 宿主可替换，但主 agent 定义不应跟着重写

### 3. 主定义不放在 cron prompt 里

Hermes cronjob 应该只是**运行入口**，不是主定义载体。

不希望未来演化成：

- 一个越来越胖的 cron prompt
- 所有规则都埋在宿主里
- 所有行为都写成 Hermes 方言

更合理的是：

- cron 负责触发与加载
- 主 agent 的角色、规则、模板、状态机，都放在独立仓库里版本化

### 4. 独立新仓库的身份：agent pack

这个新仓库长期不应被理解成：

- `daily-lane` 子模块
- `signals-engine` 子模块
- workflow app
- command-heavy 工具仓

而应被理解成：

> **一个 runtime-agnostic 的 daily report master agent pack**

它的第一身份是：

- 主 agent
- skills
- templates
- rules
- docs
- 少量 helper scripts

### 5. 仓库组织方式：主 agent + 一组 skills

理想形态更像：

- 一个主 agent
- 一组围绕日报流程拆开的 skills

而不是一个巨大的单脑 prompt 或一个命令工具集合。

主 agent 负责：

- 目标
- 状态机
- 决策规则
- 调用顺序
- 最终 verdict

skills 负责：

- 明确的小职责块
- 被主 agent 编排调用

### 6. 主入口就是主 agent prompt，不要命令行入口

这个 pack 第一入口应当是：

- **主 agent prompt / 主 agent 定义**

不希望再做一个命令行壳来承载主流程。

少量 helper scripts 可以保留，但它们只应该承担：

- validator
- formatter
- metadata builder
- file prep
- 其他通用辅助逻辑

不应该成为主流程 controller。

### 7. 表达形式：文档为主，辅以少量通用脚本

当前偏好是：

- markdown / prompt / skills 文档为主
- 少量通用脚本为辅

这样更利于：

- 在 Hermes 与 OpenClaw 之间迁移
- 让主逻辑保持 agent-native
- 同时避免所有判断都挤进自然语言 prompt

### 8. 与 signals-engine 的关系：外部能力，而非内部模块

新仓库不直接吞并 `signals-engine`，也不应做源码级强耦合。

更好的关系是：

> **通过 `uvx` 或 CLI 调用 `signals-engine`，把它当外部 signal collection tool 使用。**

这意味着：

- `signals-engine` 继续专注 signal/source/lane/runtime
- 新仓库专注 orchestration/verdict/publish/archive
- 两者通过调用面与已有产物契约配合，而不是内部 import 绑定

### 9. 厚度：中等厚度的 agent pack

这个新仓库不应只是文档壳，也不应吞掉大量执行代码。

当前更合适的厚度是：

- 有主 agent
- 有 skills
- 有模板和规则
- 有少量 helper scripts / schema / 校验
- 但不变成一个越来越胖的 workflow runtime

---

## 目前最关键的设计骨架

可以先把主流程理解成：

1. Collect：运行当天 signals 采集
2. Assess input：判断是否存在日报输入
3. Edit：内容层判断是否至少有 1 条有用内容，并生成草稿
4. Humanize：生成最终日报文本
5. Verdict：主 agent 判定 normal / degraded / blocked
6. Publish：发 Feishu 日报；必要时发运维通知
7. Archive：后续把最终日报落到 Obsidian

同时，长期载体上应理解成：

- Hermes cronjob：第一阶段宿主
- 独立仓库：主定义载体
- signals-engine：外部 signal collection tool

---

## 当前仍待继续 brainstorm 的问题

### 1. 正常日的“轻量存在感”具体长什么样
- 是一句“今日日报已生成 + 链接”
- 还是再带一点 lanes 信息

### 2. 哪些异常配得上“降级通知”
- blocked 的标准已经很窄
- 但 degraded 的边界还没彻底量化

### 3. 日报顶部的轻量降级标记长什么样
- 要足够透明
- 但不能把正文搞成运维面板

### 4. Obsidian note 的 metadata 壳长什么样
- 路径
- frontmatter
- tags
- 命名规范

### 5. 主 agent 的结构化 verdict 长什么样
- final status
- report path
- feishu link
- degraded reason
- archive result

### 6. 独立 agent pack 的内部目录与 skill 切分
- 主 agent 定义文件放哪里
- skills 如何命名和分层
- 哪些 helper 值得脚本化
- 哪些规则应该留在文档/模板层

---

## 一句话总结

这轮不是在讨论“再加几个定时任务”，而是在定义一个真正对每天结果负责的**daily report master agent**，并进一步收敛出它的第三形态：

- 第一阶段先跑在 Hermes cronjob 上
- 但不与 Hermes 强绑定
- 长期应落在独立新仓库中
- 这个仓库更像一个 **runtime-agnostic 的主 agent + skills pack**
- `signals-engine` 通过 `uvx` / CLI 作为外部能力被调用
- Feishu 是主交付面
- Obsidian 是最终日报归档层

---

## 当前停点：先停在够用骨架，避免过度设计

这轮已经收到了足够支撑下一阶段设计的骨架，先不继续往更细的 schema、section 规则、细粒度 prompt 切分里钻。

当前足够成立的骨架是：

- 独立新仓库
- runtime-agnostic 的主 agent + skills pack
- 第一阶段宿主是 Hermes cronjob
- 未来可切回 OpenClaw
- 通过 `uvx` / CLI 调用 `signals-engine`
- 仓库顶层可先理解为：`agent/`、`skills/`、`contracts/`、`templates/`、`helpers/`、`docs/`
- `report-contract` 的第一原则是：**只要至少有一条有用内容，日报就成立**

下一阶段如果继续推进，更适合进入：

1. 正式 design/spec 收束
2. 新仓库骨架与命名确认
3. 再写 implementation plan

而不是继续在 brainstorm 阶段把细节打磨到过深。