# Daily Report Master × Hermes 重构实施计划

日期：2026-04-14
状态：实施计划草案
依据：`trd.md`

---

## 1. 目标

把 `daily-report-master-agent` 从当前“repo 内有一套定义、Hermes cron 外面又包一层 prompt”的状态，重构成：

- **cron prompt = 唯一主 prompt / 唯一主入口**
- **本仓库 = authority 源**
- **安装脚本 = 单向同步器**
- **Hermes = runtime 落地点**
- **daily report skills = Hermes 原生 skills**
- **contracts / helpers / validators = 主 prompt 的显式依赖物**

并保证这套系统：

- 更适合单人长期自用
- 更容易换电脑迁移
- 更容易排障
- 不再依赖聊天上下文维持正确行为

---

## 2. 本次实施的边界

### 2.1 本次要做的

1. 收口唯一主入口
2. 为 Hermes 安装 daily report skills
3. 建立 repo → Hermes 的安装 / 更新脚本
4. 让 cron job 使用 repo authority prompt
5. 把关键行为约束从“聊天记忆”落到 config / contract / prompt

### 2.2 本次不做的

1. 不做多用户抽象
2. 不做通用 host layer
3. 不做 OpenClaw / 其他宿主的漂亮适配层
4. 不做双向同步
5. 不优先做复杂 UI / dashboard
6. 不把文本文档改造任务默认交给 Codex

---

## 3. 当前问题拆解

### 3.1 入口冲突

当前存在两个近似“主脑”：

- Hermes cron job prompt
- repo 内 `agent/daily-report-master-agent.md`

这会导致：

- authority 不唯一
- 语义容易漂移
- cron 和 repo 规则脱节

### 3.2 skills 没真正进入 Hermes 运行时

repo 内虽然有 skills 文档，但没有形成 Hermes 原生可调用 skill 包，导致：

- cron 调用不自然
- 手工 rerun 不顺
- 分步调试不顺

### 3.3 contract / helper / validator 关系没有被主入口显式串起来

这些文件存在，但运行时没有唯一入口把它们显式组织起来，导致：

- 模型需要自己猜该读哪些文件
- 临时聊天要求容易压过 repo authority
- debug 路径不清楚

### 3.4 runtime 配置和 reader-facing 要求没有参数化

当前一些关键要求没有真正进入配置层，例如：

- X 推荐流 / X 关注流默认各写 6–10 段
- collect / selected-items / report-body 的层级限制关系
- install / cron / prompt 的同步关系

---

## 4. 实施原则

### 4.1 唯一主入口原则

唯一主入口是：

> **Hermes cron 实际运行的主 prompt**

repo 内不得再保留另一份与其平级竞争 authority 的主入口定义。

### 4.2 repo authority 原则

真正的 authority 在本仓库。

Hermes 中的文件是安装产物，不是长期手改真相源。

### 4.3 单向同步原则

只允许：

`repo -> install script -> Hermes`

不设计 Hermes -> repo 的双向同步。

### 4.4 自用优先原则

设计时优先：

- 自己能看懂
- 自己能修
- 自己能迁移
- 自己能排障

不为了未来潜在外部用户引入复杂抽象。

### 4.5 文本资产不默认交给 Codex

prompt / spec / contract / docs / markdown 等文本资产的重构和维护默认由当前 agent 直接完成。

---

## 5. 目标产物清单

本次重构完成后，仓库内应至少具备以下产物：

### 5.1 主入口相关

- `main-prompt.md`（或等价文件名）
  - 作为 cron 主 prompt 的 authority 源文件
  - 显式引用 skills / contracts / validators / helpers

### 5.2 安装 / 更新相关

- `install.sh`（或等价脚本）
  - 把 authority 内容安装到 Hermes
- `verify-install.sh`（可选）
  - 做安装后校验

### 5.3 Hermes skill 源文件组织

- `hermes-skills/`（或等价目录）
  - 存放将同步到 `~/.hermes/skills/` 的 skill 源

### 5.4 配置相关

- `config/runtime.yaml`（或等价配置文件）
  - 记录 per-lane limits / X lane min-max paragraphs / runtime paths 等

### 5.5 contract / validator 相关

保留并整理已有：

- `contracts/runtime-contracts.md`
- `contracts/report-output-contract.md`
- `contracts/selected-items.md`
- `contracts/idempotency-rerun.md`
- `contracts/failure-matrix.md`
- 相关 validators / helpers

---

## 6. 分阶段实施方案

# Phase 1：收口唯一主入口

## 目标

把“谁是主 prompt”这件事彻底定死。

## 任务

1. 新建或确定 cron authority prompt 源文件
   - 建议文件名：`main-prompt.md`
   - 内容应直接对应 cron 运行时主 prompt

2. 把 repo 中现有主链路定义迁移进该文件
   - 固定主链路
   - collect / assess / build / verdict / publish / archive
   - collect 失败时同 run 诊断 / 重试
   - rerun / idempotency 要求

3. 主 prompt 中显式列出依赖引用
   - skill 名称
   - contract 路径
   - validator 路径
   - helper 路径
   - config 路径

4. 处理旧入口文件
   - `agent/daily-report-master-agent.md` 改成“说明 / 兼容文档”或移除主入口地位
   - 明确它不再是与 cron 平级竞争的主定义

## 验收标准

- 仓库里能明确指出“哪一个文件是 cron 主 prompt 源”
- 不再存在两个平级主脑
- 主 prompt 能独立说明完整主链路和依赖位置

---

# Phase 2：把 daily report skills 原生安装到 Hermes

## 目标

让 daily report 的核心步骤成为 Hermes 原生 skills，而不是 repo 内文档孤岛。

## 任务

1. 盘点现有 skills：
   - `collect-signals`
   - `assess-reportability`
   - `build-report`
   - `publish-report`
   - `archive-report`
   - `notify-ops`

2. 统一命名策略
   - 避免和其他通用 skills 混淆
   - 建议增加命名空间前缀，如：
     - `daily-report-collect-signals`
     - `daily-report-build-report`

3. 调整 skill 文案
   - 改为 Hermes 安装后可直接消费的版本
   - 去掉 repo 内自嗨式描述
   - 强调输入/输出、路径、依赖、边界

4. 设计安装目标路径
   - 例如同步到 `~/.hermes/skills/daily-report/...`

## 验收标准

- Hermes 中能看到并加载这些 skills
- 主 prompt 中可以直接引用这些 skills
- 手工调试时可单独调用关键 skills

---

# Phase 3：建立安装脚本（repo -> Hermes）

## 目标

让 authority 内容可单向、幂等同步到 Hermes runtime。

## 任务

1. 编写安装脚本
   - 创建 / 更新 Hermes skills
   - 同步主 prompt
   - 同步必要 runtime 文件
   - 创建 / 更新 cron job

2. 设计幂等策略
   - 重复执行可安全覆盖
   - 不制造重复 cron / 重复 skill
   - 输出安装版本和来源

3. 处理旧版本替换
   - 如果 Hermes 中已有旧 daily report 相关 skill / prompt / cron
   - 明确覆盖、替换或清理策略

4. 编写校验逻辑
   - skill 是否存在
   - cron 是否存在且 prompt 为最新
   - 主依赖路径是否存在
   - 必要命令如 `uvx` / `feishu-cli` / `signals-engine` 是否可用

## 验收标准

- 新机器 clone 仓库后执行一次安装脚本即可把 runtime 装起来
- 重复跑安装脚本不会造成脏状态
- 安装完成后可自动看到校验结果

---

# Phase 4：把 reader-facing 行为约束参数化

## 目标

把现在靠聊天记忆维持的报告要求落成 config / contract。

## 任务

1. 新增或整理运行配置
   - per-lane selected item limit
   - X 推荐流最少段落数
   - X 推荐流最多段落数
   - X 关注流最少段落数
   - X 关注流最多段落数

2. 更新 output contract
   - 明确 X 两条 lane 在信号充足时默认应写 6–10 段
   - 明确不足时的降级行为

3. 更新主 prompt
   - 显式读取这些配置
   - 不再把这类规则仅写成聊天记忆或软性说明

4. 更新必要 validator
   - 至少能验证 section 存在、顺序正确、来源正确
   - 后续可扩展为验证 X 两栏最少条数

## 验收标准

- X 两条 lane 的篇幅要求不再只存在于记忆或人工提醒中
- 报告生成链路可以稳定拿到这些数值型约束

---

# Phase 5：collect / retry / rerun 收口

## 目标

让 06:00 master cron 真正承担“自己 collect、自己 diagnose、自己 retry”的职责。

## 任务

1. 主 prompt 显式写死 collect ownership
   - 06:00 cron 自己 collect
   - 不假设当天 signals 预先存在

2. 明确 diagnose / retry 行为
   - collect 失败后同 run 内先 diagnose
   - 合理时 retry
   - 再基于最新状态 assess/build

3. 对齐 idempotency / rerun 规则
   - publish 成功后不能重复发 Feishu
   - 半成功 rerun 只补缺失副作用

4. 明确 collect artifacts 路径
   - collect result
   - selected items
   - validation bundle
   - final report

## 验收标准

- 06:00 cron 不再只是读现成 signals
- collect 失败时有可解释的同 run 诊断与重试路径
- rerun 行为与 contract 对齐

---

# Phase 6：迁移与自维护能力

## 目标

让这套系统换电脑时可快速恢复。

## 任务

1. 收敛换机最小流程
   - clone repo
   - 运行安装脚本
   - 校验 Hermes runtime
   - 检查外部依赖

2. 明确必须存在的本机依赖
   - Hermes
   - signals-engine
   - uv / uvx
   - feishu-cli
   - 数据目录
   - 必要认证态（如 X / Product Hunt / GitHub / Feishu）

3. 增加迁移说明文档
   - 不写成大而全手册
   - 只写最小恢复路径

## 验收标准

- 在新机器上按最小步骤可恢复这套运行体系
- 恢复后 cron / skills / prompt / config 一次到位

---

## 7. 建议的文件与目录调整

以下是建议方向，不要求第一步全部到位。

### 7.1 建议新增

- `main-prompt.md`
- `install.sh`
- `verify-install.sh`（可选）
- `config/runtime.yaml`
- `hermes-skills/`
- `migration.md`（可选）

### 7.2 建议保留

- `contracts/`
- `helpers/`
- `templates/`
- `fixtures/`
- `trd.md`

### 7.3 建议降级地位

- `agent/daily-report-master-agent.md`

它可以保留，但不再作为唯一主入口候选。

---

## 8. 旧思路兼容处理

仓库内已有文档中，以下旧判断与当前 TRD 冲突：

- cron 只是运行入口，不是主定义载体
- 主定义不放在 cron prompt
- 应避免 Hermes-only cron prompt

实施时不需要先大规模重写所有旧文档，但至少要：

1. 在新主 prompt 和安装脚本落地后，明确标注旧文档已过时
2. 避免新实现继续依赖这些旧假设

---

## 9. 里程碑与完成标准

### M1：唯一主入口落地

完成条件：
- 有明确的 cron authority prompt 源文件
- 旧“第二主脑”降级

### M2：skills 安装到 Hermes

完成条件：
- daily report 关键 skills 可在 Hermes 中直接使用

### M3：安装脚本跑通

完成条件：
- 一次执行可把 runtime 安装到 Hermes
- 重复执行幂等

### M4：X 两条 lane 规则配置化

完成条件：
- 6–10 段要求进入 config / contract

### M5：06:00 collect ownership 真正对齐

完成条件：
- cron 主 prompt 明确先 collect，再 assess/build/publish
- 有 diagnose / retry 路径

### M6：换机迁移最小闭环成立

完成条件：
- 新环境可以靠 repo + install script 重建运行时

---

## 10. 第一阶段建议立即执行的最小动作

如果按最小可行路径推进，建议先做这 5 件事：

1. 写出 `main-prompt.md`
2. 给现有 `agent/daily-report-master-agent.md` 降级
3. 设计 Hermes skill 安装目录与命名
4. 写 `install.sh` 的最小版本
5. 把 X 两条 lane 的 6–10 段要求先写进 contract 草案

---

## 11. 一句话总结

这次实施不是继续补一层文档，而是：

> **把 `daily-report-master-agent` 改造成一个“repo 持有 authority、安装脚本同步到 Hermes、cron prompt 即唯一主入口、skills 原生运行、规则参数化、适合单人长期自用和换机迁移”的日报系统。**
