# Selected Items Contract v0

## 目标

`selected_items` 是 `build-report` 的最小输入之一。它表示“已经从 signals 中筛出、可直接用于成稿”的内容列表。

它不是新的 runtime 主对象，不参与 verdict / publish / archive 判定；它只定义 `build-report` 的输入边界。

## 顶层结构

最小 JSON object：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `report_date` | string | 日报日期，格式为 `YYYY-MM-DD`。 |
| `source` | string | v0 默认写 `signals-engine`。 |
| `selected_items` | array | 已筛出的可用内容列表。 |
| `summary.selected_item_count` | integer | `selected_items` 实际条数。 |
| `summary.lane_counts` | array | 每个 lane 进入 `selected_items` 的条数。 |

## `selected_items[*]` 最小字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `lane` | string | 来源 lane，例如 `x-feed`。 |
| `title` | string | 从 signal front matter 提取的标题；缺失时可退回文件名。 |
| `source_url` | string | 原始来源链接。 |
| `signal_path` | string | 相对 `signals_root` 的稳定引用路径。 |
| `fetched_at` | string | signal 被抓取的时间。 |
| `excerpt` | string | 从 signal 正文提取的最小预览文本。 |

允许附加的轻量字段：

- `source`
- `signal_type`

## 最小语义

- `selected_items` 是给 `build-report` 的可靠输入，不要求等于 collect 阶段的全量 signal。
- 当设置了 lane 限制或后续筛选策略时，`summary.selected_item_count` 可以小于 `collect result.summary.useful_item_count`。
- `signal_path` 必须稳定且可回溯，v0 推荐使用相对 `signals_root` 的路径。
- `excerpt` 只做最小抽取，不做摘要改写，不做复杂 NLP。
