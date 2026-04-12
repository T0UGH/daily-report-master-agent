# Daily Report Master Agent v0

## 角色

这个主 agent 对单日日报链路的最终交付负责。它只执行一条固定主链路，并以 Feishu 作为主交付面。

## 固定主链路

`collect-signals -> assess-reportability -> build-report -> verdict -> publish-report -> archive-report`

补充规则：

- `notify-ops` 只在 `degraded` 或 `blocked` 时触发。
- `build-report` 只返回一个最终 `report artifact`。
- `publish-report` 成功后才允许进入 `archive-report`。

## 各步骤的最小职责

### 1. `collect-signals`

- 调用外部 `signals-engine`
- 产出最小 `collect result`
- 不在这一步决定最终 `verdict`

### 2. `assess-reportability`

- 根据 `collect result` 判断今天是否成立日报
- 规则是：只要至少有一条有用内容，日报就成立
- 无可用内容时直接进入 `blocked`

### 3. `build-report`

- 只在日报成立时调用
- 内部顺序固定为 `Editor -> Humanizer -> final report artifact`
- 主 agent 只消费最终 artifact
- 最终产物必须符合 `contracts/report-output-contract.md`
- `build-report` 的完成条件包含 output-contract validation，而不只是生成任意 Markdown

### 4. `verdict`

- 结合内容是否成立、lane 是否降级、发布与归档结果，产出 `normal / degraded / blocked`
- 同时给出是否 `publish-report`、是否 `archive-report`、是否 `notify-ops`

### 5. `publish-report`

- 把最终日报发到 Feishu
- 这是主交付面的成立边界

### 6. `archive-report`

- 只归档最终日报
- 只在 Feishu 发布成功后执行
- 归档失败会降级，但不会推翻当天已成功发布的日报

### 7. `notify-ops`

- 仅在 `degraded` 或 `blocked` 时发送
- 内容只讲状态、异常与最终链接

## 输入与输出

输入最小集合：

- `run_key`
- `report_date`
- `trigger`
- `previous_run_state`

输出最小集合：

- `verdict`
- `run_state`
- `report_artifact`
- `publish_result`
- `archive_result`

## 约束

- v0 只保留单一主 agent。
- 不增加额外主入口脚本。
- 不增加平台层包装或长期状态系统。
- reader-facing 日报固定使用 old daily-lane 风格的栏目式输出 contract。
- 最小回归验证至少包含：
  - `uv run python helpers/validate_report_output_contract.py fixtures/report-output-contract`
  - `uv run python helpers/evaluate_real_2026_04_12_output_contract.py fixtures/real-2026-04-12-output-contract`
