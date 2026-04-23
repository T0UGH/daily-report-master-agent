# Daily Report Master Agent Runtime Contracts v0

## 目标

这份文档只定义 v0 主链路里 5 个关键对象的最小边界：

- `collect result`
- `report artifact`
- `verdict`
- `publish result`
- `archive result`

v0 的根规则如下：

- 只要至少有一条有用内容，日报就成立。
- `verdict.status` 只允许 `normal`、`degraded`、`blocked`。
- `build-report` 对主 agent 只暴露一个最终 `report artifact`。
- `publish-report` 成功后才允许 `archive-report`。
- Feishu 是主交付面；Obsidian 只归档最终日报，且只在发布成功后执行。
- 默认发布交付物、内容编排与降级语义遵守 `contracts/publish-delivery-contract.md`。
- `notify-ops` 只在 `degraded` 或 `blocked` 时触发。

## 主链路顺序

`collect-signals -> assess-reportability -> build-report -> verdict -> publish-report -> archive-report`

## 对象边界

### 1. `collect result`

用途：描述外部 `signals-engine` 收集回来的最小结果，供 `assess-reportability` 判断今天是否成立日报。

必需字段：

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| `report_date` | string | 日报日期，格式为 `YYYY-MM-DD`。 |
| `source` | string | 收集来源，v0 默认写 `signals-engine`。 |
| `lanes` | array | 各 lane 的最小结果列表。 |
| `summary.useful_item_count` | integer | 今日可用于成稿的内容条数，允许为 `0`。 |

`lanes[*]` 的最小字段：

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| `name` | string | lane 名称。 |
| `status` | string | 允许 `ok`、`partial`、`error`。 |
| `useful_item_count` | integer | 当前 lane 可用内容条数。 |

允许为空或缺失的字段：

| 字段 | 规则 |
| --- | --- |
| `lanes` | 允许为空数组，表示完全没有收集到可用 lane。 |
| `summary.partial_lane_count` | 可缺失，缺失时按 `0` 处理。 |
| `errors` | 可缺失；存在时用于解释 lane 异常或系统异常。 |
| `notes` | 可缺失。 |

最小语义：

- 只要 `summary.useful_item_count >= 1`，就允许继续进入 `build-report`。
- `summary.useful_item_count == 0` 时，不得生成 `report artifact`。
- lane 异常不会自动否决日报，只要最终仍有有用内容，就不能直接判成无日报。

### 2. `report artifact`

用途：`build-report` 交给主 agent 的唯一成品。主 agent 不消费 `Editor` 或 `Humanizer` 的中间产物。

必需字段：

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| `artifact_type` | string | 固定为 `final_report`。 |
| `report_date` | string | 日报日期。 |
| `title` | string | 最终日报标题。 |
| `body_markdown` | string | 最终 Markdown 正文。 |
| `useful_item_count` | integer | 成稿实际使用的有用内容条数，最小值为 `1`。 |
| `source_lanes` | array | 成稿使用到的 lane 名称列表。 |

允许为空或缺失的字段：

| 字段 | 规则 |
| --- | --- |
| `summary` | 允许为空字符串，也允许缺失。 |

最小语义：

- `report artifact` 一旦存在，就必须是最终可发布成品。
- v0 不暴露 section 级 schema，不拆中间稿，不增加第二种模板变体。
- reader-facing 正文栏目必须遵守 `contracts/report-output-contract.md`：
  - 固定标题为 `AI Agent 日报（YYYY-MM-DD）`
  - 固定 9 栏映射只输出非空子序列
  - 未来新增 lane 不自动进入 reader-facing contract
  - 文末统一使用 `## 来源`

### 3. `verdict`

用途：给主链路产出最终状态，并明确是否发布、归档、通知。

必需字段：

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| `status` | string | 只允许 `normal`、`degraded`、`blocked`。 |
| `reason_summary` | string | 一句话解释为何得到该状态。 |
| `has_report` | boolean | 是否存在可交付的最终 `report artifact`。 |
| `should_publish` | boolean | 是否进入 `publish-report`。 |
| `should_archive` | boolean | 是否进入 `archive-report`。 |
| `should_notify_ops` | boolean | 是否触发 `notify-ops`。 |

最小判定边界：

- `normal`：有最终日报，且主链路成功完成发布与归档。
- `degraded`：有最终日报，但存在部分 lane 异常，或发布成功后归档失败等降级情况。
- `blocked`：没有最终日报，或主交付未成立，链路在发布前被阻断。

### 4. `publish result`

用途：记录 Feishu 发布结果，作为主交付面的最小摘要。默认交付物组合与编排规则见 `contracts/publish-delivery-contract.md`。

必需字段：

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| `status` | string | 允许 `succeeded`、`failed`、`skipped`。 |
| `target` | string | v0 固定为 `feishu`。 |

允许为空或缺失的字段：

| 字段 | 规则 |
| --- | --- |
| `reference` | 成功时建议提供 Feishu 全量文档链接或消息 ID；失败或跳过时允许缺失。 |
| `error_summary` | 成功时允许缺失；失败时建议填写。 |
| `deliverables` | 可缺失；存在时应按 `feishu_full_doc`、`feishu_curated_card`、`feishu_native_audio` 提供各自的 `status`、`reference`、`error_summary`。 |

最小语义：

- Feishu 全量文档成功代表主交付成立，且 `reference` 默认指向该文档。
- 默认发布交付物为 Feishu 全量文档、Feishu 精选卡片、Feishu 原生音频；精选卡片顶部必须包含全量文档链接。
- `publish result.status != succeeded` 时，不允许执行 `archive-report`。
- 若全量文档成功但精选卡片或原生音频失败，`publish result.status` 仍可为 `succeeded`，但最终 `verdict` 必须为 `degraded`，且失败明细必须写入 `deliverables` 或 `error_summary`。

### 5. `archive result`

用途：记录 Obsidian 最终日报归档结果。

必需字段：

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| `status` | string | 允许 `succeeded`、`failed`、`skipped`。 |
| `target` | string | v0 固定为 `obsidian`。 |

允许为空或缺失的字段：

| 字段 | 规则 |
| --- | --- |
| `reference` | 成功时建议提供 note 路径；失败或跳过时允许缺失。 |
| `error_summary` | 成功时允许缺失；失败时建议填写。 |

最小语义：

- `archive-report` 只归档最终日报，不归档运维通知，不归档中间稿。
- 发布已成功但归档失败时，最终结果降为 `degraded`，但不推翻当天已成功的 Feishu 发布。

## 与 failure matrix 对齐的关键规则

- 完全成功时，最终 `verdict` 为 `normal`。
- 部分 lane 异常但仍有内容时，最终 `verdict` 为 `degraded`，但仍继续 publish。
- 无可用内容时，最终 `verdict` 为 `blocked`，不 publish，不 archive。
- 全量文档成功但精选卡片或原生音频失败时，最终 `verdict` 为 `degraded`，但允许继续 archive。
- 发布成功但归档失败时，最终 `verdict` 为 `degraded`。
- 系统异常且无内容时，最终 `verdict` 为 `blocked`。
