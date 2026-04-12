# Daily Report Reader-Facing Output Contract

## 目标

reader-facing 日报必须回到老 `daily-lane` 的栏目式骨架，而不是跨 lane 主题总论稿。

固定主标题：

```md
# AI Agent 日报（YYYY-MM-DD）
```

标题后直接进入第一个非空栏目；不允许出现 `今日要点`、`正文`、`编辑结论`、导语段或专题型前置摘要。

## 固定栏目集合与顺序

最终 reader-facing 正文只允许使用以下 9 个 lane 的固定映射与顺序：

| 顺序 | lane id | reader-facing 栏目名 |
| --- | --- | --- |
| 1 | `x-feed` | `X 推荐流` |
| 2 | `x-following` | `X 关注流` |
| 3 | `reddit-watch` | `Reddit 社区` |
| 4 | `claude-code-watch` | `Claude Code` |
| 5 | `codex-watch` | `Codex` |
| 6 | `openclaw-watch` | `OpenClaw` |
| 7 | `github-trending-weekly` | `GitHub 趋势项目` |
| 8 | `product-hunt-watch` | `Product Hunt 新品` |
| 9 | `polymarket-watch` | `Polymarket 市场` |

约束：

- `github-watch` 明确排除，不进入 reader-facing 输出 contract。
- 正文只允许输出固定顺序下的非空栏目子序列。
- 未来新增 lane 不自动进入 reader-facing contract，必须显式更新本文件。
- 栏目标题必须使用 reader-facing 展示名，禁止直接输出内部 lane id。

## 正文结构

- 每个 reader-facing 栏目使用二级标题：`## 栏目名`
- 栏目内部只允许条目式 bullet 或短段落
- 不再生成跨 lane 主题总论
- 不再生成 `###` repo 小节壳
- `Claude Code`、`Codex`、`OpenClaw` 直接作为 reader-facing 二级栏目出现
- 空栏目整段省略，不输出空的 `##` 标题或占位文案

## 引用与来源

- 正文条目尾部使用 1~3 个极简外链引用，标签可用：`原帖`、`Release`、`GitHub`、`Reddit`、`Product Hunt`、`Polymarket`
- 正文引用必须直接指向原始外链，禁止引用内部 signal 路径
- 真正承载信息的正文条目必须至少带 1 个外链引用
- 每个栏目末尾不再输出 `### Sources`

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
- 正文栏目属于固定 9 栏集合，顺序为固定顺序下的非空子序列
- 正文不包含 `今日要点`、`正文`、`编辑结论`、`### Sources`
- 文末存在统一 `## 来源`
- 文末来源使用 reader-facing 中文栏目名分组
- 同栏同 URL 去重
