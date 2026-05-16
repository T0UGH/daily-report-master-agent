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
| `source_snippet` | string | 从原始 signal 高信息密度 section 提取的忠实原文片段；允许做最小中文转写/整理，但不能洗成摘要腔。 |
| `excerpt` | string | 从 signal 正文提取的最小预览文本。 |

允许附加的轻量字段：

- `source`
- `signal_type`
- `matched_query`（供 query-discovery lane 保留命中的搜索词，例如 `hacker-news-search-watch`）
- `rize-watch` 条目来自 Rize `https://rize.io/ai-tools` 周榜，必须保留 repo URL、排名和页面描述；正文渲染时栏目名为 `Rize AI 工具榜`。

## 最小语义

- `selected_items` 是给 `build-report` 的可靠输入，不要求等于 collect 阶段的全量 signal。
- 当设置了 lane 限制或后续筛选策略时，`summary.selected_item_count` 可以小于 `collect result.summary.useful_item_count`。
- `signal_path` 必须稳定且可回溯，v0 推荐使用相对 `signals_root` 的路径。
- `source_snippet` 默认来自原始 signal 的高信息密度 section，优先保留对象、动作、版本号、功能点、概率、争议点等事实单元。
- `source_snippet` 可以做最小中文转写/整理，但不得替换原始事实，不得提前写成判断总结。
- `excerpt` 只做最小抽取，不做摘要改写，不做复杂 NLP。

## 输入颗粒度要求

- `title`、`excerpt` 不能只是为了过接口的最小占位文本；禁止使用“有更新”“一条帖子”“一个项目”“值得关注”这类空占位写法
- 如果 signal 中存在更具体的信息单元，`selected_items` 应优先保留它们，例如产品名、repo 名、版本号、功能点、实验做法、批评点、概率、发布时间、更新点
- `selected_items` 是 `build-report` 的事实输入，不应在这里提前洗成摘要腔；不要把多个具体变化提前压成“更清楚了”“更成型了”“更像工作流了”这类判断句
- 下游默认渲染顺序应为 `source_snippet > excerpt > editor_summary`
- `excerpt` 可以短，但必须保留足以支撑后续成稿的事实颗粒度，至少要让下游知道对象是什么、发生了什么
