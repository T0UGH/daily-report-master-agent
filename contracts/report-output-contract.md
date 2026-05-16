# Daily Report Reader-Facing Output Contract

## 目标

reader-facing 日报必须回到老 `daily-lane` 的栏目式骨架，而不是跨 lane 主题总论稿。

固定主标题：

```md
# AI Agent 日报（YYYY-MM-DD）
```

标题必须是响应起始位置本身：

- 第一字符就必须开始于 `# AI Agent 日报（YYYY-MM-DD）`
- 标题前禁止任何空行、状态提示、解释性 preamble 或其他前置文本
- 标题后必须直接进入第一个正文栏目；不允许出现 `今日要点`、`正文`、`编辑结论`、运行状态、导语段或专题型前置摘要

## 固定栏目集合与顺序

最终 reader-facing 正文只允许使用以下 13 个 lane 的固定映射与顺序：

| 顺序 | lane id | reader-facing 栏目名 |
| --- | --- | --- |
| 1 | `weather-watch` | `天气` |
| 2 | `x-feed` | `X 推荐流` |
| 3 | `x-following` | `X 关注流` |
| 4 | `reddit-watch` | `Reddit 社区` |
| 5 | `hacker-news-watch` | `Hacker News 热榜` |
| 6 | `hacker-news-search-watch` | `Hacker News 搜索` |
| 7 | `claude-code-watch` | `Claude Code` |
| 8 | `codex-watch` | `Codex` |
| 9 | `openclaw-watch` | `OpenClaw` |
| 10 | `github-trending-weekly` | `GitHub 趋势项目` |
| 11 | `rize-watch` | `Rize AI 工具榜` |
| 12 | `product-hunt-watch` | `Product Hunt 新品` |
| 13 | `polymarket-watch` | `Polymarket 市场` |

约束：

- `github-watch` 明确排除，不进入 reader-facing 输出 contract。
- 正文只允许输出固定顺序下的非空栏目子序列。
- 未来新增 lane 不自动进入 reader-facing contract，必须显式更新本文件。
- 栏目标题必须使用 reader-facing 展示名，禁止直接输出内部 lane id。

## 正文结构

- 每个 reader-facing 栏目使用二级标题：`## 栏目名`
- 栏目内部必须使用 bullet-style reader items；推荐统一使用 `- ` 开头
- 不允许输出纯 prose blob、导语段、长段落式小作文，或用任意散文段替代 reader item
- 日报默认是“忠实原文的中文转写/整理优先，判断总结次之”；先保留原始 signal 的事实骨架，再决定是否补一层判断
- 不再生成跨 lane 主题总论
- 不再生成 `###` repo 小节壳
- `Claude Code`、`Codex`、`OpenClaw` 直接作为 reader-facing 二级栏目出现
- `Claude Code` 与 `Codex` 固定保留；`OpenClaw` 不固定，有真正值得看的更新才放
- `天气` 是固定 utility 模块，默认至少输出北京和上海两条短 bullet
- 空栏目整段省略，不输出空的 `##` 标题或占位文案

## 正文信息密度下限

- 正文不允许只有抽象判断而没有具体变化点；每条 bullet item 都必须保留对象、变化点、主线关联事实
- 允许简短，但不允许写空；对象至少要让读者知道是在说哪个产品、repo、帖子、作者、市场或项目
- 变化点至少要交代“发布了什么 / 改了什么 / 说了什么 / 争议点是什么 / 概率怎么变了”中的一项
- 主线关联事实至少要保留一个可判断信息单元，例如版本号、repo 名、产品名、功能点、接口、实验做法、批评点、概率、发布时间、更新点
- 不允许只写“更清楚了”“值得关注”“值得跟踪”“更偏向真实使用场景”“更像工作流了”之类句子
- 当一个栏目有很多相关 signal 时，应合并成更有料的主题项，而不是堆多条低信息密度条目
- `X 推荐流`、`X 关注流`、`Reddit 社区` 纳入正文的条目，目标不是替读者判断“为什么重要”，而是把原帖讲到没有上下文的人也能复述：谁说的 / 谁做的、做了什么、怎么做、结果是什么、卡点是什么、原帖省略但读者需要知道的背景是什么
- `X 推荐流`、`X 关注流`、`Reddit 社区` 禁止用“这说明……”“值得关注……”“这条有用是因为……”“读者可以把它当作……”“生态继续演进……”“更像真实工作流……”这类空泛判断替代原帖事实链
- `X 推荐流`、`X 关注流` 纳入正文的条目，必须尽量交代原帖核心观点、做法、批评点或争议点
- `X 推荐流`、`X 关注流` 在当天有效 signal 充足时，默认各输出 6–10 段正文；不要压成 1–3 段瘦版
- 只有在当天有效 signal 明显不足时，才允许低于上述下限，并应在运行结果中说明原因
- `Claude Code`、`Codex`、`OpenClaw`、`GitHub 趋势项目`、`Rize AI 工具榜`、`Product Hunt 新品`、`Polymarket 市场` 这类栏目，必须尽量保留版本号、repo、产品、功能点、概率、更新点等可判断事实
- `天气` 这类 utility 模块至少保留天气现象、气温区间，以及降水 / 风力（如原始 signal 提供）；默认覆盖北京和上海
- 当 `source_snippet` 本身已经带出多个事实点时，正文应优先整理成 2~3 句连续事实，而不是再压回一句抽象判断
- 校验器会拒绝明显的 reader-facing 低质兜底句，包括栏目条数占位、`围绕 X 展开 / 具体变化见来源`、`项目说明主要在讲它的定位、工作流和使用场景` 这类泛化改写
- 校验器会拒绝缺少足够中文承接的长英文解释句；但 repo 名、版本号、命令、URL、正常 mixed-language 技术词本身不构成违规

不合格写法示例：

- `Claude Code 最近更清楚了，值得跟踪。`
- `X 上关于 agent workflow 的讨论更成型了。`
- `这个项目更偏向真实使用场景。`
- `GitHub 上又有一些值得关注的更新。`
- `该栏目收录 32 条有用内容。`
- `原文围绕 X 展开，具体变化见来源。`
- `项目说明主要在讲它的定位、工作流和使用场景。`
- `This post explains the agent orchestration workflow for tool routing and memory management in production.`

## 引用与来源

- 最终 Markdown 禁止出现 citation-style tags / wrappers，例如 `<citation>`、`</citation>`、字符串 ` ```citation `、`:::citation` 等明显引用包裹
- 上述 citation-style wrappers 在正文与 `## 来源` 附录里都不允许出现
- 正文条目尾部使用 1~3 个极简外链引用，标签可用：`原帖`、`Release`、`GitHub`、`Reddit`、`Rize`、`Product Hunt`、`Polymarket`、`天气`
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
- 标题必须从响应开头开始，且标题与第一个正文栏目之间不得出现任何前置文本
- 正文栏目属于固定 13 栏集合，顺序为固定顺序下的非空子序列
- 正文每个栏目都必须由 bullet-style reader items 组成，不允许散文段落
- 正文不包含 `今日要点`、`正文`、`编辑结论`、`### Sources`
- 最终 Markdown 不包含 `<citation>`、`</citation>`、` ```citation ` 等 citation-style wrappers
- 正文条目满足“对象 + 变化点 + 主线关联事实”的信息密度下限
- 文末存在统一 `## 来源`
- 文末来源使用 reader-facing 中文栏目名分组
- 同栏同 URL 去重
