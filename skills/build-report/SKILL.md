# build-report

## 目的

`build-report` 是主 agent 可调用的单一 skill。它接收已经判断为“可成立日报”的内容输入，内部固定按 `Editor -> Humanizer -> final report artifact` 的顺序产出最终成品。

reader-facing 产物必须遵守 `contracts/report-output-contract.md` 的固定 contract，而不是自由发挥成跨 lane 主题分析稿。

主 agent 只能消费一个最终 `report artifact`，不能依赖两个平级中间步骤。

## 输入

最小输入应包含：

- `report_date`
- `collect result`
- 已筛出的可用内容列表 `selected_items`

输入约束：

- 只有在“只要至少有一条有用内容，日报就成立”的规则满足时才调用本 skill。
- 如果没有可用内容，主 agent 必须直接进入 `blocked`，而不是强行调用 `build-report`。
- `selected_items` 结构见 `contracts/selected-items.md`。
- `selected_items.selected_items[*]` 至少应包含：
  - `lane`
  - `title`
  - `source_url`
  - `signal_path`
  - `fetched_at`
  - `source_snippet`
  - `excerpt`
- `selected_items` 可以是 `collect result` 的子集，但不得引用 collect 中不存在的 lane。

## 内部顺序

### 1. Editor

- 负责把可用内容整理成最小日报结构
- 产出的是内部中间稿，不对主 agent 暴露
- 固定 reader-facing 标题为 `AI Agent 日报（YYYY-MM-DD）`
- 只允许使用以下固定顺序与映射：
  - `x-feed` -> `X 推荐流`
  - `x-following` -> `X 关注流`
  - `reddit-watch` -> `Reddit 社区`
  - `claude-code-watch` -> `Claude Code`
  - `codex-watch` -> `Codex`
  - `github-trending-weekly` -> `GitHub 趋势项目`
  - `product-hunt-watch` -> `Product Hunt 新品`
  - `polymarket-watch` -> `Polymarket 市场`

  额外 reader-facing 约束：
  - `weather-watch` 作为天气模块，默认至少覆盖北京和上海两条天气信号
  - `claude-code-watch` 与 `codex-watch` 固定保留，只要当天有有效信号就必须进 reader-facing 输出
  - `openclaw-watch` 默认不进入 reader-facing 输出；只有 MT 明确要求临时查看 OpenClaw 时，才作为一次性补充处理
  - `product-hunt-watch` 默认保留 2~3 条，而不是只留 1 条
- `github-watch` 不进入 reader-facing 输出
- 最终正文栏目必须是固定顺序下的非空子序列
- 标题后直接进入第一个非空栏目，不生成 `今日要点`、`正文`、`编辑结论`
- repo-specific lane 直接渲染为 `## Claude Code`、`## Codex`，不再挂到总 `GitHub` 栏位下
- 栏目内部使用条目式 bullet / 短段落，不再生成 `###` repo 小节壳或跨 lane 主题总论
- 日报默认是“忠实原文的中文转写/整理优先，判断总结次之”
- 默认正文输入优先级为 `source_snippet > excerpt > editor_summary`；不要默认优先吃 `editor_headline/editor_summary`
- 禁止使用“值得跟踪”“更清楚了”“更成型了”“更像工作流了”“更偏向真实使用场景”之类空心模板句充当正文；这类判断句只能补充，不能替代事实
- 当单个 lane 的信号很多时，优先把相关 signal 合并成更完整的主题项，而不是堆更多低信息密度条目
- `X 推荐流`、`X 关注流` 的条目必须写出帖子到底说了什么，至少交代核心观点、做法、实验结果、批评点、争议点中的一项
- `Claude Code`、`Codex`、`GitHub 趋势项目` 以及其他 GitHub / release / repo 类内容，必须展开具体更新点，例如版本号、repo、产品名、功能点、接口变化、发布内容、作者说明；不能只剩一句方向判断
- 当 `source_snippet` 已经带出多个功能点、概率或项目定位时，正文默认应整理成 2~3 句连续事实，不要再缩成一句概括

### 2. Humanizer

- 负责把中间稿润色为最终可交付文本
- 不允许改变主事实，不允许扩写成 section 级复杂结构
- 可以保留粗体判断句提升扫读效率，但不得把所有条目机械化成单一模板
- Humanizer 不得把已经写明的事实压成更短、更空的句子；如果改写后只剩抽象判断，必须保留或恢复原事实
- 真正承载信息的条目必须在段落尾部附 1~3 个极简外链引用，例如 `原帖`、`Release`、`GitHub`、`Reddit`、`Product Hunt`、`Polymarket`
- 外链必须直达原始来源，不允许引用内部 signal 路径
- 每个栏目末尾不再输出 `### Sources`
- 正文全部栏目结束后统一输出 `## 来源`
- `## 来源` 只按 reader-facing 中文栏目名分组正文实际引用过的 URL，并按“栏目 + URL”去重与首次出现顺序输出

### 3. final report artifact

- 输出必须符合 `contracts/report-artifact.schema.json`
- `body_markdown` 必须已经符合 `contracts/report-output-contract.md`
- 这是主 agent 唯一可见的最终 artifact

## 输出

输出必须是最终 `report artifact`，最少包含：

- `artifact_type = final_report`
- `report_date`
- `title`
- `body_markdown`
- `useful_item_count`
- `source_lanes`

## 边界

- `build-report` 对主 agent 是单一 skill。
- v0 不输出 Editor 稿或 Humanizer 稿。
- v0 不提供第二种正文模板，也不引入额外编排逻辑。
- `build-report` 完成前必须通过 output contract validation：
  - `uv run python helpers/validate_report_output_contract.py fixtures/report-output-contract`
  - `uv run python helpers/evaluate_real_2026_04_12_output_contract.py fixtures/real-2026-04-12-output-contract`
