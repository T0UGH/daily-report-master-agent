# Daily Report Master × Hermes 重构 TRD

日期：2026-04-14
状态：讨论结论整理稿
适用范围：`daily-report-master-agent` 自用运行体系重构

---

## 1. 这份 TRD 要解决什么问题

当前 `daily-report-master-agent` 虽然已经有主链路、skills、contracts、helpers、validators，但对 Hermes 来说仍然“不顺手”：

- Hermes cron 里有一份外层 prompt
- repo 里又有一份像“主 agent 定义”的文档
- skills 在 repo 里，但没有真正作为 Hermes 原生 skills 安装
- contracts / helpers / validators 分散存在，运行时没有一个唯一入口把它们显式串起来
- 导致 cron prompt 很容易漂移，和 repo 内部约束脱节
- 导致“主入口到底是谁”不清楚
- 导致出问题时调试路径不清楚

这份 TRD 的目标不是继续补文档，而是**把 daily report 这套链路重构成对 Hermes 触发更友好的、单人长期自用的运行包**。

---

## 2. 设计前提（必须遵守）

### 2.1 这是自用系统，不是多用户产品

在相当长的一段时间内，这套系统主要只有仓库所有者本人使用。

因此设计取舍应优先：

- 个人可靠性
- 可读性
- 可调试性
- 可迁移性（尤其是换电脑）

而不是优先：

- 多用户抽象
- 宿主通用化
- 通用平台层
- 给他人复用的优雅 API

### 2.2 主沉淀仍然在 `daily-report-master-agent` 仓库

真正的 authority 仍应放在本仓库，而不是把核心定义长期散落进 `~/.hermes/`。

Hermes 是运行时落地点，不是长期源码真相源。

### 2.3 文本类改动不默认交给 Codex

这次重构主要涉及：

- prompt
- spec
- contract
- docs
- Markdown
- 说明性配置

这类任务不是代码实现任务，不应默认交给 Codex。只有真正的代码文件改动，才属于必须优先走专业 coding agent 的范围。

---

## 3. 核心结论：唯一主入口应该是什么

### 3.1 `cron prompt = 主 prompt`

本次讨论后的明确结论是：

> **Hermes cron 里实际运行的那份 prompt，本身就应该是 daily report agent 的唯一主 prompt / 主入口。**

这意味着：

- cron 不是单纯的薄调度器
- cron 里的 prompt 不是另一个外壳
- repo 里不应该再并列存在另一份与 cron prompt 平级竞争 authority 的“主 agent prompt”

### 3.2 repo 不再保留“第二主脑”

repo 内可以保留：

- cron 主 prompt 的源码文件 / 模板文件
- 主 prompt 所依赖的 contracts
- 主 prompt 所依赖的 helpers / validators / templates
- 被主 prompt 调用的 skills 源文件

但 repo 不应再保留一份会与 cron prompt 竞争“谁才是主入口”的平级定义。

---

## 4. 新的 authority 链条

重构后应形成如下单向 authority 链：

`daily-report-master-agent repo（主沉淀）`
→ `安装脚本`
→ `Hermes runtime（skills / cron / runtime files）`
→ `实际定时运行`

这里最重要的是：

- **authority 在 repo**
- **runtime 在 Hermes**
- **同步靠安装脚本**
- **不做 repo 和 Hermes 双向漂移维护**

---

## 5. 安装方式原则：用安装脚本，不靠手工拷贝

### 5.1 为什么必须有安装脚本

由于这套系统包含混合资产：

- 主 prompt
- Hermes skills
- contracts
- helpers / validators
- templates
- cron 配置

如果继续靠手工同步，会非常容易出现：

- repo 改了，Hermes 没更新
- Hermes 被手改，repo 没回写
- 换电脑后缺步骤
- cron 跑的不是 repo 当前版本

因此应当明确：

> **通过一个安装脚本，把本仓库的 authority 内容单向同步到 Hermes。**

### 5.2 安装脚本应承担的职责

安装脚本至少应负责：

1. 安装 / 更新 daily report 相关 Hermes skills
2. 安装 / 更新主 prompt 到 Hermes 可运行位置
3. 创建 / 更新 cron job，使其始终使用 repo 当前 authority prompt
4. 确保 runtime 依赖路径稳定可引用
5. 做安装后校验

### 5.3 安装脚本必须幂等

重复执行安装脚本时，应满足：

- 不重复创建 skill
- 不重复创建 cron
- 可以安全覆盖旧版本
- 能清楚显示当前装的版本 / 来源
- 不制造双份脏状态

---

## 6. Hermes skills 的重构方向

### 6.1 当前问题

repo 里虽然已经有 skills：

- `collect-signals`
- `assess-reportability`
- `build-report`
- `publish-report`
- `archive-report`
- `notify-ops`

但它们主要还停留在 repo 内文档层，不是 Hermes 原生运行时能力。

### 6.2 目标状态

这些 skills 应安装到当前 Hermes 中，成为可直接调用的 Hermes skills。

目标收益：

- cron 主 prompt 直接调用
- 手工 rerun 时也直接调用
- 调试时可以分步运行
- 不再需要在 repo 里人工猜“这一步该看哪个 md”

### 6.3 技术边界

skills 安装到 Hermes 后：

- 源文件 authority 仍在本 repo
- Hermes 中的是安装产物 / runtime 副本
- 不应默认把 `~/.hermes` 里的副本作为长期手改位置

---

## 7. contracts / helpers / templates 的定位

这些文件不应该再形成“第二入口”，而应该明确退回到：

> **主 prompt 的依赖物**

### 7.1 contracts 用来定义硬边界

应保留并继续使用的 contract 类型包括：

- runtime contract
- report output contract
- selected items contract
- idempotency / rerun rules
- failure matrix

未来新增的 reader-facing 约束，也应优先进入 contract / config，而不是只存在于聊天记忆里。

### 7.2 helpers / validators 用来提供可执行校验

主 prompt 应明确引用它们的路径和用途，例如：

- 生成 collect result
- 生成 selected items
- 构建 validation bundle
- 校验 report output contract
- 校验 cross-field consistency

### 7.3 templates 只作为模板，不再承担主定义

`templates/` 可以保留：

- 报告模板
- ops 通知模板
- Feishu 输出模板

但模板不是主链路定义本身。

---

## 8. cron 的新职责边界

### 8.1 cron 不是“只负责触发”

这次讨论已经明确：

- cron 不只是 scheduler
- cron 里的 prompt 本身就是主 prompt

所以未来 cron 的职责是：

- 承载 daily report 唯一主入口 prompt
- 按固定时间触发该主入口
- 使用 Hermes 已安装的 daily report skills

### 8.2 但 cron 不应再独立发明另一套业务语义

虽然 cron prompt 是主 prompt，但这份主 prompt 的 authority 源仍应来自 repo，并通过安装脚本同步。

也就是说：

- cron 在 runtime 上是主入口
- repo 在源码层是 authority 源
- 不应再在 Hermes 里手工养出一份越改越胖、越改越偏的野生 prompt

---

## 9. collect / retry / rerun 的重构原则

### 9.1 06:00 master cron 自己负责 collect

已确认的真实业务设定是：

> **06:00 这条 master cron 本身负责 signal collection，而不是只消费预先存在的 signals。**

因此主 prompt 必须明确：

- 先 `collect-signals`
- collect 失败时在同一 run 内诊断
- 合理时同一 run 内重试
- 再进入 assess / build / publish / archive

### 9.2 rerun 要遵守同一日报 run_key 规则

- 同日报应复用相同逻辑 run
- 已成功 publish 时不得重复发 Feishu
- 半成功 rerun 只允许补缺失副作用

这些规则继续由 contract 锁定，并由主 prompt 显式遵守。

---

## 10. X 两条 lane 的输出约束要进配置，不靠记忆

### 10.1 当前问题

日报中的：

- `X 推荐流`
- `X 关注流`

当前容易写得过短。用户希望默认各写 **6–10 段**，而不是 1–3 段的瘦版。

### 10.2 结论

这不应只靠聊天记忆或 prompt 软提醒，而应进入：

- config（数值下限 / 上限）
- contract（作为 reader-facing 的硬要求）

### 10.3 配置层建议

未来应具备类似如下配置能力：

- `x-feed.min_paragraphs = 6`
- `x-feed.max_paragraphs = 10`
- `x-following.min_paragraphs = 6`
- `x-following.max_paragraphs = 10`

并与现有的 `selected_items` lane limit 配置配合使用。

---

## 11. 这次重构有意放弃什么

为了保证这套系统适合“长期自用 + 换电脑迁移”，本次重构**不优先考虑**：

- 多用户服务能力
- 抽象 host layer
- 对 OpenClaw / 其他宿主的漂亮通用接口
- 复杂权限模型
- 双向同步系统
- 为未来陌生用户做大量向后兼容包袱

如果未来真的需要重新做通用化，那应视为下一阶段独立问题，而不是这次自用重构的前置要求。

---

## 12. 推荐落地顺序

### Phase 1：收口唯一主入口

- 确认 cron 主 prompt 的 authority 源文件位置
- 消除 repo 内与其平级竞争的“第二主脑”
- 让主 prompt 显式引用 contracts / helpers / skills

### Phase 2：做安装脚本

- 安装 / 更新 skills
- 安装 / 更新主 prompt
- 安装 / 更新 cron
- 做运行前校验

### Phase 3：skills 原生化

- 把 daily report 相关 skills 安装到 Hermes
- 统一调用路径
- 统一调试入口

### Phase 4：把行为约束配置化

- X lane 的 6–10 段要求
- per-lane item limit
- 其他 reader-facing 规则

### Phase 5：补换机迁移能力

理想迁移步骤应收敛到：

1. clone 本 repo
2. 运行安装脚本
3. 校验 Hermes skills / cron / dependencies
4. 开始跑 daily report

---

## 13. 这份 TRD 对旧文档的影响

本 TRD 与仓库中部分更早的讨论方向存在明确差异，尤其是以下旧假设应视为**待废弃或待修正**：

- “Hermes cron 应只是运行入口，不是主定义载体”
- “主定义不放在 cron prompt 里”
- “长期应避免 Hermes-only cron prompt”

在新的重构前提下，上述思路不再成立。

新的结论是：

> **运行时主定义就应该落在 cron prompt；但它的 authority 源文件与相关依赖，应由本 repo 持有并通过安装脚本同步到 Hermes。**

---

## 14. 最终目标（一句话）

把 `daily-report-master-agent` 重构成：

> **一个以本仓库为 authority、以安装脚本同步到 Hermes、以 cron prompt 作为唯一主入口、以 Hermes 原生 skills 承载能力块、以 contracts/helpers 提供硬边界和校验的单人自用日报系统。**
