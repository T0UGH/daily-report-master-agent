# Hermes Host Interface v0

## 目标

这份文档只回答 Hermes 第一阶段接入需要的最小输入、最小输出与责任边界。

约束：

- v0 只面向 Hermes。
- 本版不包含回切实现。
- 本版不做额外宿主层抽象。

## Hermes 提供给主 agent 的最小输入

Hermes 请求只需要提供以下字段：

| 字段 | 语义 |
| --- | --- |
| `host` | 固定为 `hermes`。 |
| `run_key` | 同一日报链路的稳定判重键。 |
| `report_date` | 本次目标日报日期。 |
| `trigger.kind` | 触发类型，允许 `cron` 或 `manual`。 |
| `trigger.requested_by` | 发起方标识，例如 `hermes-cron` 或人工操作者。 |
| `previous_run_state` | Hermes 已持久化的最小运行状态；首次运行时允许为 `null`。 |

## 主 agent 返回给 Hermes 的最小输出

主 agent 响应必须包含：

| 字段 | 语义 |
| --- | --- |
| `host` | 固定为 `hermes`。 |
| `run_key` | 原样返回本次运行键。 |
| `report_date` | 原样返回本次日报日期。 |
| `verdict` | 最终状态，只允许 `normal / degraded / blocked`。 |
| `run_state` | 更新后的最小运行状态。 |
| `report_artifact` | 有日报时返回最终成品；无日报时返回 `null`。 |
| `publish_result` | Feishu 发布摘要。 |
| `archive_result` | Obsidian 归档摘要。 |

## 责任边界

### Hermes 负责

- 触发运行
- 提供稳定的 `run_key`
- 保存最小 `run-state`
- 在 rerun 前把已保存的 `previous_run_state` 传回主 agent

### 主 agent 负责

- `collect-signals -> assess-reportability -> build-report -> verdict -> publish-report -> archive-report`
- 根据 `previous_run_state` 跳过已成功的发布或归档副作用
- 产出最终 `verdict`、`run_state` 与发布/归档摘要

## 最小状态持久化要求

Hermes 至少要持久化以下字段，供下一次同一 `run_key` 使用：

- `run_key`
- `report_date`
- `trigger_kind`
- `last_verdict`
- `has_report_artifact`
- `publish_state`
- `archive_state`

## 运行边界

- Hermes 是 v0 的唯一宿主入口。
- 主 agent 不提供 CLI 主控制器。
- v0 不引入额外运行平台包装。
