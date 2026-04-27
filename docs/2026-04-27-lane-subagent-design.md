---
title: Lane Subagent Daily Report Design
date: 2026-04-27
status: draft
repo: daily-report-master-agent
scope:
  - daily-report-master-agent
  - lane-subagents
  - github-ai-projects
  - github-trending
---

# Lane Subagent Daily Report Design

## 0. 这次设计先纠正一个边界

用户纠正点：**不要把 GitHub Trending / GitHub AI Projects 拆成日报系统外的第二套系统。**

正确方向是：

> 主日报系统仍然是唯一生产链路；GitHub Trending / GitHub AI Projects 必须被包含在主日报系统内，但它可以由一个 lane subagent 生成。

所以本文不是设计一个新的 `agent-cron` 替代品，也不是让 `github-ai-projects` 脱离日报系统独立跑。本文设计的是：

> 在 `daily-report-master-agent` 内部，引入“每条 lane 一个可独立运行的 subagent worker”的结构；master 仍负责统一调度、验收、合并、发布和归档。

老 `agent-cron` 只提供一个思路：**小任务、窄目标、独立产物、短输出、可追溯**。这些能力要吸收到主日报系统里，而不是变成旁路系统。

---

## 1. 当前问题

现在的 `daily-report-master-agent` 已经能完成：

- collect signals
- select items
- render report
- validate output contract
- publish Feishu doc/card/audio
- archive final report
- notify ops when degraded/blocked

但最近 2026-04-27 的修复暴露出结构性问题：

1. **一个大 renderer 管太多 lane**
   - X、HN、Claude Code、OpenClaw、GitHub、Product Hunt 的表达规则完全不同。
   - 通用 fallback 容易产生“采集文本 / 保守看 / 摘要里能看到 / 先按标题本身交代主题”这类机器痕迹。

2. **修一个 lane 容易牵连另一个 lane**
   - HN 需要读 Story / HN Context / Top Comments。
   - X 需要人话复述和数量平衡。
   - Claude Code 需要 release freshness，不应被跨日 dedupe 误杀。
   - GitHub 项目需要项目发现、star 增速、用途判断，不只是 trending item 翻译。

3. **master 同时承担太多职责**
   - 它既像调度器，又像筛选器，又像编辑，又像所有 lane 的作者。
   - 结果是主系统越来越重，任何细节质量问题都要在同一个大文件/大流程里修。

4. **有效信息被 renderer 空字符串压掉**
   - 2026-04-27 X 推荐/关注只剩 4/3 条，根因不是 `lane_limit`，而是部分有价值短帖没有被 renderer 生成可发布 detail，导致最终无法补满。

---

## 2. 设计目标

### 2.1 目标

把日报生成从：

```text
master 直接理解所有 lane → master 直接写完整日报
```

改成：

```text
master 调度 lane workers → lane workers 产出标准 lane artifact → master 验收并合并 Markdown → publish
```

但外部交付保持不变：

- 仍然只有一个主日报 cron。
- 仍然只有一个最终 Feishu 文档。
- 仍然由 `daily-report-master-agent` 负责结果质量。
- 仍然由 master 决定 normal / degraded / blocked。

### 2.2 非目标

本设计明确不做：

- 不把 GitHub AI Projects 拆回独立 `agent-cron` 系统。
- 不让每个 lane 自己单独发飞书日报。
- 不让每个 lane 自己决定最终日报是否成立。
- 不让 subagent 自由发挥无 schema 的 Markdown。
- 不移除现有 output contract；只会增强它。

---

## 3. 总体架构

```text
Hermes cron / future runtime
  |
  v
Daily Report Master Agent
  |
  |-- collect signals / load runtime inputs
  |
  |-- lane workers, serial or parallel
  |     |-- weather lane worker
  |     |-- x-feed lane worker
  |     |-- x-following lane worker
  |     |-- reddit lane worker
  |     |-- hacker-news lane worker
  |     |-- claude-code lane worker
  |     |-- codex lane worker
  |     |-- openclaw lane worker
  |     |-- github-ai-projects lane worker
  |     |-- product-hunt lane worker
  |     |-- polymarket lane worker
  |
  |-- validate lane artifacts
  |
  |-- assemble report.md
  |
  |-- validate final report contract
  |
  |-- publish Feishu doc/card/audio
  |
  |-- archive final report
  |
  |-- notify ops only when degraded/blocked
```

关键原则：

> lane worker 是“栏目作者”；master 是“主编 + 发布负责人”。

---

## 4. Runtime 目录结构

建议新增：

```text
~/.daily-lane-data/runtime/daily-report-master/YYYY-MM-DD/
  collect-result.json
  selected-items.json
  validation-bundle.json
  report.md
  report-artifact.json

  lane-inputs/
    weather.json
    x-feed.json
    x-following.json
    reddit-watch.json
    hacker-news-watch.json
    claude-code-watch.json
    codex-watch.json
    openclaw-watch.json
    github-ai-projects.json
    product-hunt-watch.json
    polymarket-watch.json

  lane-outputs/
    weather.json
    x-feed.json
    x-following.json
    reddit-watch.json
    hacker-news-watch.json
    claude-code-watch.json
    codex-watch.json
    openclaw-watch.json
    github-ai-projects.json
    product-hunt-watch.json
    polymarket-watch.json

  lane-logs/
    x-feed.md
    hacker-news-watch.md
    github-ai-projects.md
```

说明：

- `lane-inputs/*.json` 是 master 准备给 worker 的最小输入包。
- `lane-outputs/*.json` 是 worker 的标准产物。
- `lane-logs/*.md` 是人类调试用日志，不参与最终发布。
- `report.md` 仍是唯一最终日报 Markdown。

---

## 5. Lane input contract

每个 lane worker 收到统一输入结构：

```json
{
  "artifact_type": "lane_input",
  "schema_version": 1,
  "report_date": "2026-04-27",
  "timezone": "Asia/Shanghai",
  "lane": "x-feed",
  "lane_title": "X 推荐流",
  "target_item_count": 10,
  "min_item_count": 6,
  "signals": [
    {
      "id": "x-feed:2048341222356619272",
      "source_lane": "x-feed",
      "url": "https://x.com/...",
      "source_urls": ["https://x.com/..."],
      "title": "@Rixhabh__ #57",
      "excerpt": "...",
      "source_snippet": "...",
      "raw": {"source_path": "x-feed/2026-04-27/signals/xxx.md"}
    }
  ],
  "recent_history": {
    "repo_ids": [],
    "items": [
      {
        "date": "2026-04-26",
        "lane": "x-feed",
        "source_url": "https://x.com/...",
        "title": "..."
      }
    ]
  },
  "cross_lane_context": {
    "repo_mentions": ["owner/repo"],
    "topic_hints": ["Claude Code", "Codex", "MCP"]
  },
  "style_contract": {
    "language": "zh-CN",
    "mode": "human_retell",
    "must_include_links": true,
    "forbidden_phrases": ["采集文本", "保守看", "可以让读者复述"]
  }
}
```

不同 lane 可以扩展自己的字段，但必须保留这些通用字段。

---

## 6. Lane output contract

每个 lane worker 必须输出 JSON，不允许只输出散文。

```json
{
  "artifact_type": "lane_output",
  "schema_version": 1,
  "report_date": "2026-04-27",
  "lane": "x-feed",
  "status": "ok",
  "section_title": "X 推荐流",
  "summary": "今日 X 推荐流保留 10 条 agent/coding workflow 相关内容。",
  "items": [
    {
      "rank": 1,
      "title": "@Rixhabh__ #57",
      "summary": "原帖在推荐 Anthropic 团队自己讲 Claude Code 用法的 30 分钟资料，重点是从官方示范里学习怎样正确使用 Claude Code，而不是只看二手技巧清单。",
      "url": "https://x.com/Rixhabh__/status/...",
      "source_urls": ["https://x.com/Rixhabh__/status/..."],
      "why_today": "Claude Code 官方用法资料，属于 coding agent workflow。",
      "quality_flags": ["has_link", "has_subject", "has_action"],
      "confidence": "high"
    }
  ],
  "sources": [
    {"label": "@Rixhabh__ #57", "url": "https://x.com/Rixhabh__/status/..."}
  ],
  "quality": {
    "item_count": 10,
    "warnings": []
  },
  "markdown": "## X 推荐流\n\n- **@Rixhabh__ #57** 原帖在推荐... [原帖](https://x.com/...)\n",
  "validation": {
    "status": "passed",
    "item_count": 10,
    "warnings": [],
    "errors": []
  }
}
```

`status` 取值：

- `ok`：lane 正常成立。
- `empty`：输入不足或无可发布内容，但不是系统错误。
- `degraded`：产出不足或部分校验 warning，但可以进入日报。
- `blocked`：该 lane 产物不可用，master 不应使用其 markdown。

---

## 7. Master 的职责边界

master 负责：

1. 准备 lane inputs。
2. 调用 lane workers。
3. 校验 lane outputs。
4. 对 degraded/blocked lane 做状态判断。
5. 合并最终 Markdown。
6. 跑 final output contract。
7. 发布 Feishu。
8. 归档最终日报。
9. 必要时发运维通知。

master 不负责：

- 逐条重写 X 帖子。
- 逐条解释 HN 评论。
- 自己搜索 GitHub 项目。
- 直接猜测 release note 的最新版本。

如果某个 lane 内容不好，应修对应 lane worker 或 lane validator，而不是继续往 master 的通用 renderer 里堆特例。

---

## 8. GitHub AI Projects lane 设计

### 8.1 定位

这个 lane 是主日报系统内的一条 lane，名称建议：

```text
github-ai-projects
```

它不是外部第二套系统。

它负责把 GitHub Trending 纳入日报，但不等同于 Trending 排行榜。

更准确的定义：

> `github-ai-projects` 是主日报系统里的 GitHub 项目发现 lane。它消费 GitHub Trending、GitHub Search、已有 signals 中的 GitHub URL、X/HN/Reddit/Product Hunt 中的 repo mention，并输出当天最值得关注的 AI / agent / coding workflow 项目。

### 8.2 输入源

`github-ai-projects` 至少应覆盖：

1. **GitHub Trending**
   - daily / weekly trending。
   - 作为候选源，不直接等于最终输出。

2. **GitHub Search API**
   - query examples:
     - `ai agent pushed:>=YYYY-MM-DD stars:>20`
     - `claude code stars:>10`
     - `codex agent stars:>10`
     - `mcp server stars:>10`
     - `agent memory stars:>10`
     - `coding agent stars:>10`
     - `llm eval agent stars:>10`

3. **跨 lane repo mentions**
   - X 帖子里的 GitHub URL。
   - HN Story / comments 里的 GitHub URL。
   - Reddit 帖子里的 GitHub URL。
   - Product Hunt item 的 GitHub link。
   - Claude Code / Codex / OpenClaw release notes 里提到的 repo。

4. **历史入选记录**
   - 最近 7 天入选过的 repo 默认降权。
   - 如果今天有重大 release / star 增长 / 多源重复出现，可以再次入选，但必须说明“为什么今天仍值得看”。

### 8.3 输出位置

作为主日报系统的一部分，它需要输出两份产物：

1. lane output artifact:

```text
~/.daily-lane-data/runtime/daily-report-master/YYYY-MM-DD/lane-outputs/github-ai-projects.json
```

2. 兼容旧效果的详细项目档案：

```text
/Users/haha/workspace/memory/github-ai-projects/YYYY-MM-DD.md
```

注意：第二份档案是主日报系统的副产物，不是第二套调度系统。由主日报 master 或该 lane worker 在主链路中写入。

### 8.4 日报 section 格式

最终日报中建议使用：

```md
## GitHub AI 项目

1. **mercury-agent** (cosmicstack-labs) ⭐1326 — 灵魂驱动 AI Agent，权限加固 + Token 预算 + Telegram 接入，4 天破 1300 星
2. **garden-skills** (ConardLi) ⭐1345 — Claude Code Skills 开源合集，覆盖网页设计 / 知识检索 / 图像生成，5 天 1300+ 星
3. **harmonist** (GammaLabTechnologies) ⭐678 — 零依赖 Agent 编排框架，186 内置 Agent + 机械协议执行机制
4. **future-agi** ⭐509 — LLM / Agent 全链路评测平台，追踪 + 仿真 + 数据集 + Guardrails，Apache 2.0 可商用
5. **text-to-cad** (earthtojake) ⭐565 — 文本生成 CAD 模型，WASM 原生，填补 AI 生成 3D 工程模型空白

详情：https://github.com/T0UGH/macmini-memory/blob/main/github-ai-projects/2026-04-26.md
```

### 8.5 项目档案格式

`/Users/haha/workspace/memory/github-ai-projects/YYYY-MM-DD.md`：

```md
# GitHub AI 项目精选 - YYYY-MM-DD

> 数据来源：GitHub Trending + GitHub Search + X/HN/Reddit/Product Hunt repo mentions
> 评分维度：新鲜度 + star 增速 + agent/coding 相关性 + 使用价值 + 多源交叉验证

## 今日 Top 5 精选

### 1. owner/repo ⭐ N
- **一句话**：...
- **为什么今天值得看**：...
- **关键能力**：...
- **使用方式**：...
- **来源线索**：GitHub Trending / GitHub Search / X / HN / Product Hunt
- **链接**：https://github.com/owner/repo

## 其他值得关注

- ...

## 过滤记录

- owner/repo：过滤原因，例如泛 AI、无源码、只是 landing page、信息不足、重复入选。
```

### 8.6 GitHub lane validator

`github-ai-projects` 输出必须满足：

- Top items 默认 5 条。
- 每条必须有 GitHub repo URL。
- 每条必须有 stars 或明确说明 stars 未取到。
- 每条必须说明：项目做什么 + 为什么今天值得看。
- 至少覆盖一个输入来源；多源交叉出现的项目加权。
- 过滤掉：
  - 非开源项目。
  - 只有 README 营销无代码的项目。
  - 泛 AI 新闻，不是 GitHub 项目。
  - 与 AI agent / coding workflow / LLM toolchain 明显无关的项目。
- 不允许只输出 repo 名称列表。
- 不允许只翻译 GitHub description。

---

## 9. X lane worker 设计

X 推荐流和 X 关注流可以拆成两个 worker，但共享同一套 contract。

### 9.1 输入

- 当天 selected X candidates。
- 原始 source snippet。
- 最近 3-7 天已入选 URLs。
- 用户偏好：推荐/关注流约 10 条，质量过滤不能缩到 3-4 条。

### 9.2 输出约束

- 默认目标 10 条。
- 如果少于 8 条，必须在 validation warnings 里说明原因：候选池不足、跨日重复过多、低信号过多、renderer 不足等。
- 每条必须是人话复述：谁做什么、怎么做、结果/卡点/背景。
- 禁止：
  - `采集文本`
  - `保守看`
  - `摘要里给出的直接变化`
  - `可以让读者复述`
  - 直接搬运截断原文
  - 广告/注册推广/退款稳定性推广

---

## 10. Hacker News lane worker 设计

HN 必须独立，因为它不是标题摘要问题，而是讨论理解问题。

### 10.1 输入

- Story title / URL。
- Story text。
- HN context。
- Top comments。
- matched query。

### 10.2 输出约束

每条必须尽量说明：

- 帖子是什么。
- 为什么和 AI agent / coding workflow 有关。
- 评论区在争什么。
- 有哪些工程建议、指标、benchmark、使用经验。

禁止：

- `先按标题本身交代主题`
- `摘要里能看到的具体信息是`
- `HN 搜索命中的标题是`
- 标题-only 低信息条目硬塞进正文

---

## 11. Release lanes 设计

适用：

- `claude-code-watch`
- `codex-watch`
- `openclaw-watch`

这些 lane 可以不完全 agent 化，适合规则 + 小 agent 混合。

### 11.1 必须保证 freshness

- 同一 release feed/source URL 可能每天出现新版本。
- 不能因为 source_url 或 topic 跨日重复就误杀最新版本。
- version tokens 是强信号。

### 11.2 输出约束

每条 release 至少包含：

- 版本号。
- 具体变更点。
- 对用户 workflow 的影响。
- 原始链接。

禁止只输出英文 release note fallback。

---

## 12. 调度策略

### 12.1 第一阶段：串行 worker

先不要追求并发。先在同一进程内按顺序执行 lane workers：

```text
weather → release lanes → X → HN → GitHub AI Projects → Product Hunt → Polymarket
```

好处：

- 容易 debug。
- 不引入并发日志和资源竞争。
- 先验证 contract 是否合理。

### 12.2 第二阶段：可并发 worker

当 lane output contract 稳定后，可改成并发：

```text
parallel:
  weather
  release lanes
  x-feed
  x-following
  reddit
  hn
  github-ai-projects
  product-hunt
  polymarket

then:
  assemble report
```

并发时必须保证：

- 每个 worker 只写自己的 `lane-outputs/<lane>.json`。
- 共享副作用受控。
- `github-ai-projects` 写 memory repo 时要加锁或由 master 统一写，避免 git 冲突。

---

## 13. 兼容迁移方案

不要一次性重写全部 lane。按 vertical slice 迁移。

### Phase 1：引入 lane output contract，但仍使用现有 renderer

- 新增 `lane-outputs/` 产物。
- 现有 `signals_adapter.py` 仍负责生成内容。
- master 把现有 render result 包装成 lane artifact。
- 目标是让最终 assemble 从 lane artifacts 读取。

### Phase 2：GitHub AI Projects lane subagent

- 新增 `github-ai-projects` worker。
- 消费 GitHub Trending/Search + cross-lane repo mentions。
- 输出 lane artifact。
- 写入 `/Users/haha/workspace/memory/github-ai-projects/YYYY-MM-DD.md`。
- 日报中使用该 lane 的 markdown section。

这是第一个真正 subagent 化的 lane。

### Phase 3：HN lane worker

- 把 HN 从通用 renderer 拆出。
- 专门读取 Story / HN Context / Top Comments。
- 专门 validator 阻断标题-only 模板腔。

### Phase 4：X lane workers

- 拆 `x-feed` / `x-following`。
- 保证数量和质量同时满足。
- 每个 worker 自己解释为什么不足 8 条。

### Phase 5：Release lanes

- `claude-code-watch`、`codex-watch`、`openclaw-watch` 拆成 release worker。
- 把 version freshness 做成 release-lane 通用规则。

---

## 14. 质量门禁

### 14.1 Lane-level validation

每个 lane output 都要先过 lane validator。

lane validator 输出：

```json
{
  "status": "passed",
  "errors": [],
  "warnings": [],
  "metrics": {
    "item_count": 10,
    "with_links": 10,
    "forbidden_phrase_hits": 0
  }
}
```

### 14.2 Report-level validation

最终 `report.md` 继续跑现有 output contract。

必须继续检查：

- 天气在最上面。
- Claude Code / Codex 固定保留。
- X/HN 禁止坏模板。
- 每条有链接。
- 不能出现内部采集痕迹。
- 日期、标题、section 顺序正确。

---

## 15. 文件建议

第一阶段建议新增/修改：

```text
contracts/lane-output-contract.md
helpers/lane_artifacts.py
helpers/lane_validators.py
helpers/github_ai_projects_worker.py
helpers/github_ai_projects_validator.py
helpers/report_assembler.py

tests/test_lane_artifacts.py
tests/test_github_ai_projects_worker.py
tests/test_report_assembler.py

docs/2026-04-27-lane-subagent-design.md
```

如果不想一开始拆太多文件，可以先最小化：

```text
helpers/lane_artifacts.py
helpers/github_ai_projects_worker.py
tests/test_github_ai_projects_worker.py
contracts/lane-output-contract.md
```

---

## 16. 验收标准

### 16.1 GitHub AI Projects vertical slice

给定 2026-04-26 的候选输入，系统应能生成接近旧 agent-cron 效果的 section：

```text
⭐ GitHub AI 项目 2026-04-26
1. mercury-agent ...
2. garden-skills ...
3. harmonist ...
4. future-agi ...
5. text-to-cad ...
详情：https://github.com/T0UGH/macmini-memory/blob/main/github-ai-projects/2026-04-26.md
```

并满足：

- Top 5 都有 repo URL。
- memory file 被写入或可 dry-run 生成。
- lane output JSON valid。
- 最终日报包含该 section。
- 不需要第二套 cron。

### 16.2 整体系统

- 主 cron 仍只有一个。
- 主日报仍只有一个 Feishu 文档。
- 任一 lane blocked 时，master 可降级继续发布其他 lane。
- lane artifacts 可独立调试。
- final report contract passed。

---

## 17. 风险与控制

### 风险 1：subagent 输出风格不统一

控制：统一 lane output contract + final assembler 只接受结构化 items。

### 风险 2：成本上升

控制：先串行/规则化 worker；只有 GitHub/HN/X 这类高价值 lane 使用 agent；简单 lane 继续规则渲染。

### 风险 3：GitHub memory 写入和主日报发布形成副作用冲突

控制：第一阶段由 master 统一执行 git write/commit/push；worker 只生成 markdown 内容和目标路径。

### 风险 4：系统复杂度从一个大文件变成多个小黑盒

控制：每个 lane output 必须有 validation metrics 和 debug log；master summary 记录每条 lane 的状态、item count、warnings。

---

## 18. 最终结论

这次改造的核心不是“用 agent-cron 替换日报系统”，而是：

> 把 agent-cron 的窄任务优势吸收到 `daily-report-master-agent` 内部，让每条 lane 像一个小 agent 产品一样独立产出，但仍由主日报系统统一调度、验收、合并和发布。

GitHub Trending / GitHub AI Projects 必须留在主日报系统内。它应该成为第一个 lane subagent vertical slice：

```text
github-ai-projects worker
  = GitHub Trending
  + GitHub Search
  + cross-lane GitHub repo mentions
  + recent history dedupe
  + Top 5 项目判断
  + memory markdown 副产物
  + final report section
```

这样既保留主日报系统的一体化交付，又能获得老 `agent-cron` 那种轻、准、直接的效果。
