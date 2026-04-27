# Report Feedback Ledger

这个文件专门记录 MT 对 AI Agent 日报的逐日反馈，以及后续在 `daily-report-master-agent` 里做过哪些对应改动。

原则：
- 反馈按日期记录，不用事后美化。
- 区分“用户反馈 / 当天实际表现 / 已采取改动 / 待验证”。
- 如果后续改代码、prompt、contract、validator、配置或发布链路，必须回填到对应日期或新增“改动记录”。
- 不把“我记住了”当修复；必须能追到仓库文件、commit 或验证产物。

## 2026-04-24

### 用户反馈 / 目标
- 日报整体仍像信号搬运，不够像给人读的情报产品。
- X / Reddit / HackerNews 难读，缺少“人话复述”。
- 需要的不只是临时润色当天日报，而是切分支做一版系统实现，跑真实结果给 MT 看。
- 需要“今日主线 / 读者入口 / 更像情报产品”的结构，让读者先知道今天主线，再看各栏目细节。

### 当时归纳的问题
- 天气之后直接进入大量 X / Reddit / HN 条目，缺少入口框架。
- X / Reddit / HackerNews 仍像原帖搬运或信号流水账。
- 当时 `report-output-contract` 禁止 `今日要点`、跨 lane 总论等结构，导致更可读的结构没有合法落点。

### 拟定改动方向
- 增加合法的 `今日主线` 模块，放在天气之后、X 之前。
- X 推荐流 / 关注流改成主题组，不再只是逐条搬运。
- Reddit / HackerNews 改成“热帖 / 原声 / 争议点 / Show HN / 技术讨论 / 工具发布”等更可读结构。
- Claude Code / Codex / Product Hunt / Polymarket 保留事实密度，不压成空泛总结。

### 后续状态
- 后续实际主线没有完整落地到 2026-04-26、2026-04-27 的生产日报里；这说明 2026-04-24 的改造目标没有形成稳定的 runtime 约束。

## 2026-04-26

### 用户反馈
- “修了一版没生效”的感觉基本成立。
- 日报仍不够人话，可读性差。
- 之前说的“今日主线 / 读者入口 / 情报产品结构”没有在当天日报出现。
- Feishu 卡片仍像把整份日报塞进卡片，不像精选入口。
- MT 明确提出：`reddit消除`。

### 当天实际表现
- 2026-04-26 cron、validation、publish、archive 都成功，问题不是运行失败。
- 当天报告 section 仍是旧 lane 顺序：天气、X、Reddit、Hacker News、Claude Code、Codex、OpenClaw、GitHub、Product Hunt、Polymarket。
- 报告里没有 `## 今日主线`。
- 最近落地的提交主要解决 Feishu 卡片 preflight / compact fallback，不是正文内容结构。
- compact card 只有超限时触发，因此默认仍可能发送过长卡片。

### 已采取 / 已确认的改动方向
- Reddit 不再继续作为“要润色的栏目”处理；用户方向是移除/消除。
- 后续应默认把“Reddit 是否还出现”作为发布前验收点，而不是只看 validator 是否 passed。
- Feishu 卡片应该默认是入口卡/精选卡，而不是完整日报搬运。

### 待验证
- Reddit 是否已从 06:00 master flow 的 collect lanes、selected items、report sections、card sections 中真正移除。
- `今日主线` 是否真正进入 runtime，而不是只停留在设计讨论。

## 2026-04-27

### 用户反馈
- 当天日报仍然“很差”，没什么进步。
- MT 认为昨天和前天犯过的错今天还在犯。
- 今天先不改生产日报，先“记账”：以后每天 MT 给的 feedback 都记录到 `daily-report-master-agent` 仓库里。
- 后续如果有改动，也要在 feedback 记录里体现“改了什么”。

### 重点质量问题
- **HackerNews 可读性差**：MT 要求主要看 HackerNews 的可读性。当前问题不是有没有 HN 栏目，而是读起来不像人话，不能快速知道帖子/讨论到底在说什么、为什么值得看。
- **X 没有按约定润色成人话**：之前说过 X 要做“人话复述”，但 2026-04-27 的输出仍像原帖摘录/搬运，没明显润色。
- **重复犯错**：说明之前的 hardening 没有变成足够强的 contract / validator / runtime gate。
- **Claude Code 不是最新版本**：2026-04-27 日报里的 Claude Code 信息没有反映最新版本，说明 release/source freshness 或版本选择逻辑也需要纳入发布前检查。

### 后续改动记录
- 2026-04-27：新增本文件 `docs/report-feedback-ledger.md`，开始把每日反馈和后续修复动作放进仓库。这个改动本身不修复日报内容，只解决“反馈不可追踪、每天重复丢上下文”的问题。
- 2026-04-27：修复 HN renderer / gate：
  - `helpers/signals_adapter.py` 增加 2026-04-27 真实 HN case 的人话复述分支，覆盖 SWE-bench Verified 饱和、AI memory biological decay、parallel Claude agents、Agent MCP Studio。
  - HN source snippet 抽取改为保留 `Story / Hacker News Context / Top Comments`，避免只拿标题导致热榜条目被 fallback 成“先按标题本身交代主题”。
  - publishability gate 新增拦截 `摘要里能看到的具体信息是`、`命中的 HN 标题是` 等搜索日志式模板；低信息 title-only HN 搜索命中会被过滤，不再进正文。
  - `tests/test_signals_adapter.py` 新增 2026-04-27 HN 回归测试，禁止这些模板回流。
  - 验证：`python3 -m pytest -q tests/test_signals_adapter.py -k 'hacker_news'` 通过；真实 2026-04-27 selected-items smoke 中，HN 热榜两条从不可发布变为 publishable，Invincat / text-to-CAD / minimal context / TurbineFi 这类模板化低信息搜索命中变为不可发布。
- 2026-04-27：修复 X renderer / gate，恢复 2026-04-26 更接近“人话复述”的风格：
  - `helpers/signals_adapter.py` 新增 2026-04-27 真实 X case 的复述分支，覆盖 `Claude Code Hook - Context Timeline`、`GEOFlow`、`skills-manage`、`Yuragi FM`。
  - 去掉 `采集文本只给到`、`保守看` 这类内部分析口吻，改成只基于已采集事实说明“对象 / 动作 / 机制 / 卡点 / workflow 关系”。
  - noisy X gate 新增过滤低价值广告/截断搬运：`注册即用`、退款/稳定性推广、`GitHub 被...屠榜...1.` 这类内容不再因为泛泛提到 OpenAI/GitHub/agent 就进入正文。
  - `tests/test_signals_adapter.py` 新增 X 回归测试：正例要求保留 4/26 风格的事实槽位，负例要求拒绝 4/27 的低信号推广和截断榜单帖。
  - 验证：`python3 -m pytest -q tests/test_signals_adapter.py -k 'x_post_detail or noisy_x_candidate or live_2026_04_27'` 通过；完整 `python3 -m pytest -q` 为 `161 passed`；真实 2026-04-27 selected-items smoke 中坏词 `采集文本 / 保守看 / 摘要里给出的直接变化 / 可以让读者复述` 数量为 0，`@zstmfhy` 注册推广和 `@GitTrend0x` 截断榜单帖 gate 为 false。
- 2026-04-27：修复 Claude Code freshness 选择逻辑：
  - 根因：当天采集日志已经拿到 `v2.1.119 / v2.1.118 / v2.1.117`，但 `build_selected_items()` 先做跨日 source_url/topic dedupe；由于之前的回填/重跑产物里已经出现过 `v2.1.119` 和 `v2.1.118`，最新两个版本被过滤掉，lane_limit=1 时反而选中了旧的 `v2.1.117`。
  - `helpers/signals_adapter.py` 对 `claude-code-watch` / `openclaw-watch` 这类版本 release lane 取消跨日 source_url 去重，并让带版本号的 release 不被跨日 topic dedupe 压掉，保证排序后优先选最新版本，而不是用旧版本补位。
  - `tests/test_signals_adapter.py` 新增回归测试：当最新 Claude Code release 已在最近历史里出现、当天 raw signals 同时有新旧版本时，仍应选择最高版本 `v2.1.119`，不能退到 `v2.1.117`。
  - 验证：`python3 -m pytest -q tests/test_signals_adapter.py -k 'claude_code or versioned_release or latest_versioned_release_even_if_seen_recently'` 通过；完整 `python3 -m pytest -q` 为 `162 passed`；真实 2026-04-27 selected-items smoke 中 Claude Code 从 `v2.1.117` 改为 `v2.1.119`。

### 待处理方向
- HN 输出需要从标题搬运改为“人话解释”：谁发了什么、是什么项目/讨论、核心事实、讨论点/卡点、为什么和 AI agent/coding workflow 相关。
- X 输出需要落实 2026-04-24 定义的事实槽位：谁、做了什么、怎么做、结果/反馈、卡点、必要背景；原帖事实不足时降权或过滤。
- X 推荐流 / X 关注流的条目数量需要单独检查：2026-04-27 重生成版里 X 推荐流只有 4 条、X 关注流只有 3 条；用户期望“之前应该是 10”的量级。需要追踪是 `lane_limit`、selection gate、publishability gate、跨日去重，还是低信号过滤过严导致有效条目数被压缩；质量过滤不能把 X 栏目缩到明显不够看的程度。
  - 2026-04-27 追踪结论：不是 `lane_limit` 太小，主要是 X detail renderer 对若干有具体信息的帖子返回空字符串，导致后续 publishability/selection 无法补满；典型被误伤项包括 `@Rixhabh__` Claude Code 官方用法资料、`@steipete` clawsweeper/50 Codex 并行、`@garrytan` GBrain eval harness、`@gdb` Codex 构建能力判断等。
  - 修复：补 X generic/source-fact detail 和 2026-04-27 live cases，让有 agent/coding 事实的短帖能生成可发布人话复述，同时保留广告/截断/低信号 gate。
  - 验证：`python3 -m pytest -q tests/test_signals_adapter.py -k 'x_post_detail or noisy_x_candidate_gate_rejects_live_2026_04_27_low_signal_items'` 为 `6 passed`；完整 `python3 -m pytest -q` 为 `162 passed`；重生成 `python3 helpers/run_daily_report_flow.py --report-date 2026-04-27 --skip-collect --title-suffix '重生成版' --verbose` 通过，`x_lane_counts` 从 `x-feed: 4 / x-following: 3` 修复为 `x-feed: 10 / x-following: 10`，旧坏词 `采集文本 / 保守看 / 摘要里给出的直接变化 / 可以让读者复述 / HN 坏模板` 均为 0。
- 把 HN/X 的人话要求固化到 contract、validator、tests 或 runtime quality gate，不能只写 prompt。
- 每次修复后，在本文件追加：改了哪些文件、commit、验证命令、真实日报 smoke 结果。

## 改动记录模板

### YYYY-MM-DD

#### 对应反馈
- 

#### 改了什么
- 文件：
- 逻辑：
- 约束：

#### 验证
- 命令：
- 结果：
- 真实日报样例：

#### Commit
- 
