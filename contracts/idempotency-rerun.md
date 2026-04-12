# Daily Report Master Agent Idempotency And Rerun v0

## 最小原则

v0 不引入任务队列、分布式锁或长期状态服务，只定义 Hermes 第一阶段足够使用的最小判重与重跑规则。

## `run_key` 规则

- v0 只有一条固定日报链路，因此 `run_key` 采用稳定格式：`{report_date}:daily-report`
- 同一天、同一日报链路的 `cron 重试` 与 `人工 rerun` 都必须复用同一个 `run_key`
- Hermes 通过 `run_key` 找到同一日报的既有 `run-state`，再判断哪些外部副作用允许再次执行

示例：

- `2026-04-12:daily-report`
- `2026-04-13:daily-report`

## 宿主必须保留的最小 `run-state`

Hermes 至少要保存以下结果，用于后续判重与跳过重复副作用：

- `run_key`
- `report_date`
- `trigger_kind`
- `last_verdict`
- `has_report_artifact`
- `publish_state`
- `archive_state`

## 重跑规则

### `cron 重试`

- 同一 `run_key` 的 `cron 重试` 必须先读取已有 `run-state`
- 如果 `publish_state.status == succeeded`，不得重复发 Feishu
- 如果 `publish_state.status == succeeded` 且 `archive_state.status != succeeded`，允许只重试归档

### `人工 rerun`

- `人工 rerun` 仍然复用同一个 `run_key`
- 人工重跑可以重新执行 `collect -> assess -> build-report` 来获取新的判定结果
- 但在执行 `publish-report` 与 `archive-report` 前，必须先根据已有 `run-state` 跳过已成功的外部副作用

### `publish 已成功后 rerun`

- 一旦 `publish_state.status == succeeded`，后续任意 rerun 都只能复用既有发布摘要
- 不允许因为 rerun 重复发送第二条 Feishu 日报
- 如果此前归档未成功，可以在保留既有发布结果的前提下继续尝试归档

### `archive 已成功后 rerun`

- 一旦 `archive_state.status == succeeded`，后续 rerun 不允许重复归档
- 宿主可直接返回既有归档摘要，保持最终状态不变

### 半成功 rerun

- v0 的半成功主要指“发布已成功、归档失败”
- 这类 rerun 只允许补归档，不允许重复发布

## 结论

- Hermes 只靠 `run_key` 与最小 `run-state`，就能判断是否会重复发 Feishu、是否会重复归档 Obsidian
- v0 的 helper 只校验这些规则，不承担编排或调度逻辑
