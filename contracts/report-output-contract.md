# Daily Report Reader-Facing Output Contract

## 目标

reader-facing 日报必须回到老 `daily-lane` 的栏目式骨架，而不是跨 lane 主题总论稿。

固定主标题：

```md
# AI Agent 日报（YYYY-MM-DD）
```

标题后直接进入第一个非空栏目；不允许出现 `今日要点`、`正文`、`编辑结论`、导语段或专题型前置摘要。

## 固定栏目集合与顺序

最终 reader-facing 正文只允许使用以下 12 个 lane 的固定映射与顺序：

| 顺序 | lane id | reader-facing 栏目名 |
| --- | --- | --- |
| 1 | `x-feed` | `X 推荐流` |
| 2 | `x-following` | `X 关注流` |
| 3 | `reddit-watch` | `Reddit 社区` |
| 4 | `hacker-news-watch` | `Hacker News 热榜` |
| 5 | `hacker-news-search-watch` | `Hacker News 搜索` |
| 6 | `claude-code-watch` | `Claude Code` |
| 7 | `codex-watch` | `Codex` |
| 8 | `openclaw-watch` | `OpenClaw` |
| 9 | `github-trending-weekly` | `GitHub 趋势项目` |
| 10 | `product-hunt-watch` | `Product Hunt 新品` |
| 11 | `polymarket-watch` | `Polymarket 市场` |
| 12 | `weather-watch` | `北京海淀天气` |

约束：

- `github-watch` 明确排除，不进入 reader-facing 输出 contract。
- 正文只允许输出固定顺序下的非空栏目子序列。
- 未来新增 lane 不自动进入 reader-facing contract，必须显式更新本文件。
- 栏目标题必须使用 reader-facing 展示名，禁止直接输出内部 lane id。

## 正文结构

- 每个 reader-facing 栏目使用二级标题：`## 栏目名`
- 栏目内部只允许条目式 bullet 或短段落
- 日报默认是“忠实原文的中文转写/整理优先，判断总结次之”；先保留原始 signal 的事实骨架，再决定是否补一层判断
- 不再生成跨 lane 主题总论
- 不再生成 `###` repo 小节壳
- `Claude Code`、`Codex`、`OpenClaw` 直接作为 reader-facing 二级栏目出现
- `北京海淀天气` 是固定 utility 模块，可只输出 1 条短 bullet
- 空栏目整段省略，不输出空的 `##` 标题或占位文案

## 正文信息密度下限

- 正文不允许只有抽象判断而没有具体变化点；每条 bullet / 短段落都必须保留对象、变化点、主线关联事实
- 允许简短，但不允许写空；对象至少要让读者知道是在说哪个产品、repo、帖子、作者、市场或项目
- 变化点至少要交代“发布了什么 / 改了什么 / 说了什么 / 争议点是什么 / 概率怎么变了”中的一项
- 主线关联事实至少要保留一个可判断信息单元，例如版本号、repo 名、产品名、功能点、接口、实验做法、批评点、概率、发布时间、更新点
- 不允许只写“更清楚了”“值得关注”“值得跟踪”“更偏向真实使用场景”“更像工作流了”之类句子
- 当一个栏目有很多相关 signal 时，应合并成更有料的主题项，而不是堆多条低信息密度条目
- `X 推荐流`、`X 关注流` 纳入正文的条目，必须尽量交代原帖核心观点、做法、批评点或争议点
- `X 推荐流`、`X 关注流` 在当天有效 signal 充足时，默认各输出 6–10 段正文；不要压成 1–3 段瘦版
- 只有在当天有效 signal 明显不足时，才允许低于上述下限，并应在运行结果中说明原因
- `Claude Code`、`Codex`、`OpenClaw`、`GitHub 趋势项目`、`Product Hunt 新品`、`Polymarket 市场` 这类栏目，必须尽量保留版本号、repo、产品、功能点、概率、更新点等可判断事实
- `北京海淀天气` 这类 utility 模块至少保留天气现象、气温区间，以及降水 / 风力（如原始 signal 提供）
- 当 `source_snippet` 本身已经带出多个事实点时，正文应优先整理成 2~3 句连续事实，而不是再压回一句抽象判断

不合格写法示例：

- `Claude Code 最近更清楚了，值得跟踪。`
- `X 上关于 agent workflow 的讨论更成型了。`
- `这个项目更偏向真实使用场景。`
- `GitHub 上又有一些值得关注的更新。`

## 引用与来源

- 正文条目尾部使用 1~3 个极简外链引用，标签可用：`原帖`、`Release`、`GitHub`、`Reddit`、`Product Hunt`、`Polymarket`、`天气`
- 正文引用必须直接指向原始外链，禁止引用内部 signal 路径
- 真正承载信息的正文条目必须至少带 1 个外链引用
- 每个栏目末尾不再输出 `### Sources`
- `Hacker News 热榜`、`Hacker News 搜索` 的正文引用标签可使用 `Hacker News`

文末固定追加：

```md
## 来源
```

来源区规则：

- 按 `### 栏目名` 分组
- 只列正文实际用到的 URL
- 按“栏目 + URL”去重
- 同栏同 URL 只保留一次
- 同一 URL 出现在不同栏目时允许分别保留
- 每组来源顺序固定为该 URL 在该栏目正文首次被引用的出现顺序

## 校验重点

合格 reader-facing 日报至少满足：

- 固定标题 `AI Agent 日报（YYYY-MM-DD）`
- 正文栏目属于固定 12 栏集合，顺序为固定顺序下的非空子序列
- 正文不包含 `今日要点`、`正文`、`编辑结论`、`### Sources`
- 正文条目满足“对象 + 变化点 + 主线关联事实”的信息密度下限
- 文末存在统一 `## 来源`
- 文末来源使用 reader-facing 中文栏目名分组
- 同栏同 URL 去重
