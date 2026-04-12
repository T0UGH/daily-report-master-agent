# Daily Report Master Agent Failure Matrix v0

## 范围

v0 只保留最小必测场景，不铺满所有组合。目标是先把 `normal / degraded / blocked` 的判定边界和后续动作锁住。

## 最小场景矩阵

| 场景 | 触发条件 | 最终 verdict | 是否 publish | 是否 archive | 是否 notify-ops | 用户会看到什么 |
| --- | --- | --- | --- | --- | --- | --- |
| 完全成功 | 收集成功，有内容，Feishu 发布成功，Obsidian 归档成功 | `normal` | 是 | 是 | 否 | 一条正常发布并已归档的日报 |
| 部分 lane 异常但仍有内容 | 至少一个 lane 异常，但还有至少一条有用内容，最终成功发布 | `degraded` | 是 | 是 | 是 | 一条可读但可能偏短的日报，加一条运维通知 |
| 无可用内容 | 收集完成但 `useful_item_count == 0` | `blocked` | 否 | 否 | 是 | 不发日报，只发运维通知说明今日无可用内容 |
| 发布成功但归档失败 | 日报已成功发到 Feishu，但 Obsidian 归档失败 | `degraded` | 是 | 已尝试但失败 | 是 | 主聊天里已有日报，外加一条归档失败通知 |
| 系统异常且无内容 | 收集或评估阶段发生系统异常，且最终没有可用内容 | `blocked` | 否 | 否 | 是 | 不发日报，只发阻塞通知 |

## 判定边界

- `normal` 只用于有最终日报，且对外发布与归档都完成的场景。
- `degraded` 只用于“日报已成立，但链路并非完全健康”的场景。
- `blocked` 只用于“没有形成最终日报”或“主交付无法成立”的场景。

## 继续执行规则

- 只要有内容并判定可发布，就继续执行 `publish-report`。
- `publish-report` 未成功时，`archive-report` 必须停止。
- `archive-report` 失败不会撤回已成功的 Feishu 发布，但会把最终状态降为 `degraded`。
- `notify-ops` 只在 `degraded` 或 `blocked` 时触发。
