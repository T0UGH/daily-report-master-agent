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

#### Implementation progress — lane subagent vertical slice

- Change: completed remaining Tasks 6-9 for the internal `github-ai-projects` worker path.
- Details:
  - Added deterministic GitHub repo aggregation from trending and cross-lane repo mentions.
  - Added `side_artifacts.memory_markdown` and runtime `lane-memory/github-ai-projects.md` writing.
  - Added configured compatibility memory artifact writing to `lane_workers.github_ai_projects.memory_repo_dir` without git commit/push.
  - Added `build_lane_output()` dispatch so `github-ai-projects` uses its lane input and other lanes keep the local renderer.
  - Added `github-ai-projects` lane input composition from GitHub Trending, X, Reddit, HN, HN search, and Product Hunt repo mentions.
- Verification:
  - `python3 -m pytest -q tests/test_github_ai_projects_worker.py tests/test_lane_workers.py tests/test_run_daily_report_flow.py -k 'worker_mode or github_ai_projects or cross_lane_repo_mentions'` -> `9 passed, 30 deselected`
  - `python3 -m pytest -q tests/test_lane_contracts.py tests/test_lane_workers.py tests/test_lane_report_assembler.py tests/test_github_ai_projects_worker.py` -> `11 passed`
  - `python3 -m pytest -q tests/test_run_daily_report_flow.py tests/test_signals_adapter.py` -> `144 passed`
  - `python3 -m pytest -q` -> `178 passed`
  - real-date worker smoke: `python3 helpers/run_daily_report_flow.py --report-date 2026-04-27 --config /tmp/daily-report-lane-worker-smoke-full.yaml --skip-collect --title-suffix 'lane-worker-smoke-full' --verbose` -> exit 0, `decision=generated`, `validation.status=passed`.
  - artifact check: `lane-inputs/github-ai-projects.json`, `lane-outputs/github-ai-projects.json`, `lane-memory/github-ai-projects.md`, and `report.md` all exist; banned phrases `采集文本 / 保守看 / 摘要里能看到 / 先按标题本身交代主题` all false.
- Result: master remains the only report entrypoint; lane worker artifacts are written under runtime `lane-inputs/`, `lane-outputs/`, and `lane-memory/`. Worker mode keeps default disabled in production config and requires `enabled_lanes` to match `fixed_section_order` for a run, so partial mode cannot silently drop columns.

- Correction after preview feedback: the intended migration is agent-cron's discovery logic, not its shared memory file. Removed the shared `memory_repo_dir` read/write compatibility path from report-master runtime behavior; `github-ai-projects` now carries the old agent-cron discovery queries inside `cross_lane_context.github_search_queries` (`GitHub trending AI {date}`, `GitHub new AI projects {date}`, `awesome AI GitHub {date}`), while runtime memory remains under `lane-memory/` only. Also tightened false-positive bare repo filtering for `tokens/s` and `user/assistant`.
- Verification: targeted `python3 -m pytest -q tests/test_github_ai_projects_worker.py tests/test_run_daily_report_flow.py -k 'github_ai_projects'` -> `9 passed`; full `python3 -m pytest -q` -> `180 passed`; 2026-04-27 worker preview -> `decision=generated`, `validation.status=passed`, GitHub input queries present, `memory_repo_path` absent, `/Users/haha/workspace/memory/github-ai-projects/2026-04-27.md` not created.

### 2026-04-28

#### GitHub Trending lane worker grounding
- Added an internal `github-trending-weekly` worker that reads `lane_input.signals` raw snippets, filters non-AI repos, and writes concrete Chinese bullets with GitHub sources instead of renderer template summaries.
- Verification: `python3 -m pytest -q tests/test_github_trending_worker.py tests/test_lane_workers.py tests/test_run_daily_report_flow.py -k 'github_trending or lane_output or worker_mode'` -> `10 passed, 31 deselected`.

#### Process-isolated lane subagent mode
- Added `helpers/lane_subagent_worker.py` and `helpers/lane_subagent_runner.py` so `lane_workers.mode: subagent` writes lane input JSON, invokes `python -m helpers.lane_subagent_worker` in a separate process, captures stdout/stderr to `lane-logs/*.md`, reads lane output JSON, and validates it before report assembly.
- Updated `helpers/run_daily_report_flow.py` to keep local mode in-process and route subagent mode through the process runner; the previous `ValueError("subagent lane worker mode is not implemented yet")` path is removed.
- Verification: `python3 -m pytest -q tests/test_lane_subagent_runner.py tests/test_run_daily_report_flow.py -k 'subagent or worker_mode or github_trending'` -> `7 passed, 31 deselected`; `python3 -m pytest -q` -> `190 passed`.

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

## 2026-04-28

### 用户反馈 / 架构纠偏
- MT 认为上一版 `agent-first` preview “感觉更差”，追问实现方式后确认根因：我把 lane 做成了 Python 规则/模板 agent，而不是真正 Hermes subagent。
- MT 明确要求：忘掉 `.py agent`；日报应是每条 lane 一个 Hermes subagent，每条 lane 一个 skill，subagent 输出 markdown，最后主 agent 整合 markdown。
- MT 进一步纠正边界：Python 脚本不能负责启动 subagent；只有 Hermes 主 agent 能启动 subagent。lane-specific 脚本可以放在 skill 本体里，但只能做整理/校验等辅助工作，不能控制判断和正文。

### 已采取改动
- 新建分支 `feat/hermes-skill-lane-subagents`，从 main 基线重新做，不继承错误的 `.py agent` 分支。
- 新增设计文档 `docs/superpowers/specs/2026-04-28-hermes-skill-lane-subagents-design.md`，写入硬规则：Python 不启动 subagent，不选择/摘要/改写正文；只有 Hermes master agent 调 `delegate_task`；每条 lane 的判断和写作在 lane subagent + lane skill 中完成。
- 新增实现计划 `docs/superpowers/plans/2026-04-28-hermes-skill-lane-subagents-implementation-plan.md`。
- 新增 repo 内 skill 源目录 `skills/daily-report-*`，包括 master skill 和 13 条 lane skill。
- 新增 deterministic scripts：skill sync、raw corpus lane package prepare、lane output validate、lane markdown assemble、publish wrapper。
- 新增回归测试，保护边界：deterministic Python scripts 不得出现 `delegate_task(`、`build_lane_output(`、`run_lane_subagent(`、旧 GitHub worker 等 forbidden snippets。

### 待验证
- 需要用 Hermes main session 真正 delegate 每条 lane subagent，生成 2026-04-26 skill-preview。
- 需要验证每条 lane 的 `lane.md` 是 subagent 按 skill 写出，而不是 Python renderer/worker 输出。
- 生产默认不切换，直到 MT 看过 skill-preview 并确认方向更好。
- 2026-04-28：完成第一版 Hermes skill/subagent preview 验证：
  - runtime root: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26-skill-preview`
  - Hermes 主 session 直接调用 `delegate_task`，按 lane skill 生成 13 个 `lane.md` + `lane-meta.json`。
  - validation: `python3 skills/daily-report-master/scripts/validate_lane_outputs.py --runtime-root ...` passed。
  - assemble: `report.md` generated by deterministic assembler without rewriting lane content。
  - Feishu preview: `https://www.feishu.cn/docx/WwjKdtN1LooDdNxwDfBcO4KznAd`
  - fetch verification: title present; contains `天气`、`X 推荐`、`GitHub 趋势`、`forrestchang/andrej-karpathy-skills`; does not contain `采集文本` or `具体变化见来源`。
- 2026-04-28：根据 MT 反馈继续修第二版：
  - 13 条 lane skill 的 Writing Style 先增加“子条目更精炼”规则，随后按 MT 反馈修正为：每条默认 1-3 句、正文最长不超过 200 个中文字符，优先保留关键事实/数字/风险，删除空泛判断。
  - 用 2026-04-28 当天数据重新跑 Hermes subagent preview：runtime root `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-28-skill-preview-v2`。
  - Hermes 主 session 直接调用 `delegate_task` 生成 13 个 lane outputs；`validate_lane_outputs.py` passed；`assemble_lane_markdown.py` 生成 `report.md`。
  - Feishu preview: `https://www.feishu.cn/docx/GaiDdxAxAowcH2xGMxDcfPiPn8g`。
  - quality check: forbidden phrases `采集文本`、`具体变化见来源`、`趋势信息包含这些具体点`、`值得关注`、`值得跟踪` 均为 0；83 条 bullet 中仅 3 条超过 260 字，主要是长 URL 导致。

## 2026-04-30

### 生产日报运行记录
- Hermes cron 已按原生 subagent lane 架构运行：13 条 lane 均由 `delegate_task` 拉起的 Hermes subagent 生成 `lane.md` 与 `lane-meta.json`，master 只做 package / validate / assemble / publish / archive。
- 当天大多数 signals raw corpus 缺失，导致 X、Reddit、HN、Claude Code、Codex、OpenClaw、GitHub Trending、Product Hunt、Polymarket 多数为空或降级；仅天气与 GitHub AI 项目有正文内容。
- Feishu 文档：`https://www.feishu.cn/docx/ENWtd8VAUo6a6oxy8hIcvlfhnHc`。
- runtime root：`/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-30/`。
- archive：已归档到 `/Users/haha/workspace/knowledge-vault/Inbox/ai daily report/2026-04-30.md`。

### 待验证 / 待修复
- 需要检查 2026-04-30 signals 为什么缺失，避免生产日报只剩天气和 GitHub 发现补充。
- assembled `report.md` 出现两个 `## Hacker News 搜索` 段，需检查 assembler/fixed section order 或 lane heading 配置。

### 2026-04-30 09:30 rerun 记录
- 重新按 Hermes 原生 subagent lane 架构跑生产链路：本次 run 先在同一 master run 内执行 signals-engine collect/diagnose/retry，再 prepare lane packages，再由 Hermes `delegate_task` 生成 13 条 lane 输出。
- collect 结果：12 条 lane collect 成功；`github-ai-projects` collect 首次失败后 diagnose + retry 仍失败，但该 lane subagent 明确按降级处理并用 GitHub Search / raw README 补证据。
- validation：`validate_lane_outputs.py` passed；`assemble_lane_markdown.py` 生成 `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-30/report.md`。
- lane status：13 total；12 ok；1 degraded（`github-ai-projects`）；0 blocked；subagent selected total 69。
- Feishu 文档：`https://www.feishu.cn/docx/Ij44dAtxMoaTZWxz3EKcN53UnBb`。
- archive：已归档到 knowledge-wiki `raw/inbound/ai-daily-report/2026/2026-04-30.md`，commit `790ebcaa601d11166b81efb8d570e983d96b20bd`。

## 2026-05-01

### 运行记录
- 06:00 cron 使用 Hermes 原生 subagent lane 架构生成日报；collect/validate/assemble/publish/archive 完成。
- `github-ai-projects` deterministic collect 缺少 run.json，lane subagent 按 skill 使用 bounded live GitHub discovery fallback，最终 lane 标记为 degraded。
- Feishu 文档发布成功：https://www.feishu.cn/docx/L0aPdUGQBocInMxm28WcttEXn5d
- knowledge-wiki 归档提交：b3a0639186fba2d341feccf3e45a38ff23a449aa

## 2026-05-02

### 生产运行记录
- Hermes 原生 subagent lane 架构完成 cron 主链路；本次先执行 deterministic collect/diagnose/retry，再 prepare lane packages，再由 13 个 Hermes lane subagent 写 `lane.md` / `lane-meta.json`。
- collect 结果：12 条 lane collect 成功；`github-ai-projects` collect 首次失败后 diagnose + retry 仍失败，最终该 lane 因 raw corpus 为空标记 degraded / no-info。
- package/raw 结果：除 `github-ai-projects` raw_file_count=0 外，其余 12 条 lane package 均有 raw files；之前 “collect 成功但 package raw 缺失” 的 signals root 适配问题本次已避开。
- validation：`validate_lane_outputs.py` passed；`assemble_lane_markdown.py` 生成 `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-02/report.md`；补 `## 来源` 附录后 `validate_report_markdown()` passed。
- lane status：13 total；12 ok；1 degraded（`github-ai-projects`）；0 blocked；compat selected_item_count=41。
- 发布：Feishu 文档和精选卡片成功，doc URL `https://www.feishu.cn/docx/Xs5kdPuO7ouiy6xUig0cn6T9nWe`；音频生成因 MiniMax `2056 usage limit exceeded` 失败，整体 publish degraded。
- 归档：最终 `report.md` 已归档到 `knowledge-wiki/raw/inbound/ai-daily-report/2026/2026-05-02.md`，commit `95e4dba710d7a183be9b20690f644962b5471309`。

### 当天实际表现 / 待跟进
- 13 条 lane 全部有真实 Hermes subagent 输出文件，报告主体不使用旧 renderer/local fallback。
- `github-ai-projects` 没有可核验 raw corpus，本次按 no-info contract 输出 `- 无`，没有复用昨日旧项目。
- 输出 contract 暴露两个 runtime hardening 点：assembler 只拼接 lane.md，未自动生成统一 `## 来源`；empty/degraded no-info lane 需要严格输出 `- 无` 才能跳过 source 要求。后续应把这两点固化到 `assemble_lane_markdown.py` / lane validation，而不是每次人工补。

## 2026-05-03

### 生产运行记录
- Hermes 原生 subagent lane 架构完成 06:00 cron 主链路；本次先执行 deterministic collect/diagnose/retry，再 prepare lane packages，再由 13 个 Hermes lane subagent 写 `lane.md` / `lane-meta.json`。
- collect 结果：11 条 lane ok；`x-feed` collect 命令成功但 run status empty/source fetch browser session error，`github-ai-projects` collect 首次失败后 diagnose + retry 仍缺少 run.json；两条 lane raw corpus 为空并由 subagent 降级输出 `- 无`。
- package/raw 结果：除 `x-feed`、`github-ai-projects` raw_file_count=0 外，其余 11 条 lane package 均有 raw files。
- validation：`validate_lane_outputs.py` passed；`assemble_lane_markdown.py` 生成 `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-03/report.md`；补 `## 来源` 附录后 `validate_report_markdown()` passed。
- lane status：13 total；11 ok；2 degraded（`x-feed`、`github-ai-projects`）；0 blocked；compat selected_item_count=197。
- 发布：Feishu 文档成功，doc URL `https://www.feishu.cn/docx/ATzvdyk3VoDq0qxaRoQcY0cjn4f`；本次未发送卡片/音频。
- 归档：最终 `report.md` 已归档到 `knowledge-wiki/raw/inbound/ai-daily-report/2026/2026-05-03.md`，commit `425d839e6fcddd1e3cc94f7666b1ab7023470af4`。

### 当天实际表现 / 待跟进
- 13 条 lane 全部有真实 Hermes subagent 输出文件，报告主体不使用旧 renderer/local fallback。
- `x-feed` browser collector 不稳定导致当天推荐流缺失；需要后续单独修复 browser session/collector 稳定性。
- `github-ai-projects` 仍持续缺 run.json；需要修复 deterministic collect，而不是依赖 lane 降级。

## 2026-05-04

### 运行记录
- 06:00 Hermes 原生 subagent lane 架构完成生产运行：collect → prepare lane packages → 13 个真实 Hermes lane subagent → validate → assemble → Feishu doc publish → knowledge-wiki archive。
- GitHub AI 项目 lane collect 命令首轮与 retry 均失败，package raw 为空；lane subagent 按规则输出 degraded / `- 无`，未使用旧 renderer 或 selected_items fallback。
- final report contract 首次校验发现 Reddit 空泛判断句；已交回 Reddit lane subagent 基于 raw thread 修复，不由 master/Python 改写正文。

### 产物
- runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-04/`
- final report: `report.md`
- Feishu doc: https://www.feishu.cn/docx/XRO8dA95boNqoexQKXCcxQdqnSd
- archive: `knowledge-wiki/raw/inbound/ai-daily-report/2026/2026-05-04.md` @ `5e8755194cef0825aad5a20f88d14f671da47aea`

## 2026-05-05

### 运行记录
- 06:00 Hermes 原生 subagent lane 架构完成生产运行：先 collect signals，再 prepare lane packages，再逐 lane 调用真实 Hermes subagent 写 `lane.md` / `lane-meta.json`。
- Feishu 文档发布成功： https://www.feishu.cn/docx/BnjNd9JG2o3fa2xKY3ccLzbFn6g
- knowledge-wiki 归档成功：`raw/inbound/ai-daily-report/2026/2026-05-05.md`（commit `cb5283dbaf92262c3877b8dbdfeec517a3d963d6`）。

### 质量/链路观察
- `x-feed` collect 命令返回 ok，但 lane package raw 为空，subagent 按合同输出 `- 无` / `empty`，没有 fallback 到旧 renderer。
- final report 缺少统一 `## 来源` 时 output contract 会失败；本次用确定性 appendix 从正文链接生成来源附录后通过校验。
- 卡片/音频未在本次 wrapper 发布中尝试；`publish_report.py` 只创建 Feishu doc。


## 2026-05-06

### 当天运行记录
- 06:00 Hermes 原生 subagent lane 架构运行成功：collect、prepare lane packages、13 个 lane subagent、validate、assemble、final contract、Feishu doc/card publish 均完成。
- 当天修复 `helpers/publish_delivery.py`：`lark-cli` 输出日志中出现 malformed surrogate 时，写 `feishu-import.log` 使用 `errors="replace"`，避免发布链路因日志编码中断。
- 归档：最终 `report.md` 已复制到 `~/.daily-lane-data/reports/2026-05-06.md` 与 knowledge-wiki `raw/inbound/ai-daily-report/2026-05-06.md`。

### 待观察
- 多个 lane subagent 反馈在 `~/.hermes` 中未直接找到同名 skill 文件，但本次 package 指令与系统已注入 skill 内容足够完成输出；后续可继续检查 skill sync 是否需要强化。


## 2026-05-07 cron delivery

- runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-07`
- report: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-07/report.md`
- archive: `/Users/haha/.daily-lane-data/reports/2026-05-07/report.md`
- doc_url: 
- card_message_id: 
- status: succeeded

## 2026-05-08

### 当天运行记录
- 06:00 Hermes 原生 subagent lane 架构完成生产运行：collect、prepare lane packages、13 个 lane subagent、validate、assemble、Feishu doc/card publish 均成功。
- collect preflight 使用 repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`，生产 config `/Users/haha/.signal-engine/config/lanes.yaml`，data-dir `/Users/haha/.daily-lane-data`；lane registry 包含 weather、Reddit、HN、Claude、Codex、OpenClaw、Polymarket 等全量 collector。
- Polymarket collect 首次和 retry 均有部分 query 网络失败，但 retry 写出 6 条 raw evidence；lane subagent 基于 raw evidence 生成 `ok` 输出。
- 最终 13 lanes 全部 `ok`，subagent selected_count 合计 74。
- Feishu 文档：https://www.feishu.cn/docx/QExJdW5IuoWGOfxrURqchD87nsd；精选卡片 message_id：`om_x100b50e4b65eb4a4b3ff66c757210ab`；audio skipped。

### 待观察
- 继续观察 Polymarket API/网络稳定性；如果连续多日部分 query SSL EOF/connection reset，应在 signals-engine 层加更稳健的重试或降级记录。

## 2026-05-09

- status: published
- doc_url: https://www.feishu.cn/docx/MxYJddQLtoJaOexLSGFcjOo1nTh
- card_message_id: om_x100b50d245c634a4b2486a73de51bc7
- lanes: total=13 ok=12 degraded=0 blocked=0 empty=1
- runtime: /Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-09
- archive: /Users/haha/workspace/daily-report-master-agent/reports/2026-05-09
## 2026-05-10
- Hermes subagent lane architecture run completed for 2026-05-10.
- Feishu doc: https://www.feishu.cn/docx/VhIudcqXSoGD1gxPYAfcHwrFn5c
- Card message: om_x100b50cf6ccb7ca4b15683cc361e48c
- Knowledge-wiki archive commit: 31beca08afb4288ba9315bf0191e7f09e305c616
## 2026-05-11

### 运行记录
- 06:00 cron 按 Hermes 原生 subagent lane 架构执行：repo-local `signals-engine` preflight、逐 lane collect、prepare lane packages、13 个 lane subagent 写 `lane.md` / `lane-meta.json`、validator + final output contract 通过。
- `github-ai-projects` 继续按 derived lane 处理，不作为直接 signals-engine collector；collect artifact 中规范化为 skipped/derived。
- Feishu 发布成功：文档和精选卡片均返回成功；音频未在当前 publish wrapper 中生成，状态为 skipped。

### 待观察
- 继续观察 X browser-session diagnose 偶发 `Execution context was destroyed`，本次 collect 命令最终成功且 raw corpus 非空。

## 2026-05-12 cron run
- Hermes native subagent lane architecture completed.
- Feishu doc/card publish succeeded; archive committed to knowledge-wiki `d8ad43b06e863d75e7faa9046904efb5fa90de07`.
- Note: x-feed preflight diagnose initially reported browser-session native API probe failure, but collect succeeded on same repo-local CLI/config/data-dir.

## 2026-05-13 cron delivery
- runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-13`
- report: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-13/report.md`
- Feishu doc: https://www.feishu.cn/docx/TZaudQT7zogM33xW2ugcA3SInOc
- card: succeeded / `om_x100b6f0e30de2ca0b307db7b3440bd7`
- audio: skipped



## 2026-05-14 cron run

- Feishu doc: https://www.feishu.cn/docx/NR73dwUA2oW80vxhttQcsVP5n8d
- Card: succeeded; message_id=om_x100b6f7bd9bcd4a0b32ebb82cd2f0d0
- Runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-14`
- Contract: passed after lane-output repair loop.

## 2026-05-15 cron run
- Runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-15`
- Report: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-15/report.md`
- Feishu doc: https://www.feishu.cn/docx/JYCgdUthGoLWGNxn9Fect2qInUc
- Feishu card_message_id: `om_x100b6f50ef13c8a0b3d8f3121a31a5e`
- Final delivery ok: `True`

## 2026-05-16 cron run
- runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-16`
- report: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-16/report.md`
- archive: `/Users/haha/.daily-lane-data/archive/daily-report-master/2026-05-16`
- publish-state: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-16/publish-state.json`
- notes: Hermes subagent lane architecture; collect used repo-local signals-engine with production config/data root; Feishu doc+card succeeded; audio skipped.
## 2026-05-17 cron run
- Hermes native subagent lane architecture completed: collect -> package -> lane subagents -> validate -> assemble -> Feishu publish.
- Collect used repo-local signals-engine with /Users/haha/.signal-engine/config/lanes.yaml and /Users/haha/.daily-lane-data. HN search initially timed out, diagnose healthy, retry succeeded.
- Metadata normalization repaired several lane-meta schema aliases/missing keys before validation. Weather lane needed explicit H2 for final contract.
- Final report contract passed after appending deterministic ## 来源 appendix.

## 2026-05-18

### 生产运行记录
- Hermes 原生 subagent lane 架构完成当日生产运行：collect / package / delegate lane subagents / validate / assemble / Feishu publish / knowledge-wiki archive 全链路完成。
- Lane 状态：total 14 / ok 13 / degraded 0 / blocked 0 / empty 1；最终 selected_count=68。
- Collect preflight 使用 repo-local signals-engine：`uvx --from /Users/haha/workspace/signals-engine signals-engine`，config `/Users/haha/.signal-engine/config/lanes.yaml`，data-dir `/Users/haha/.daily-lane-data`；lane registry 包含 weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket。
- Feishu 文档：https://www.feishu.cn/docx/NBVJdhRuRoz9bkxtdKpcVc7FnXg；卡片状态 `succeeded`，message_id `om_x100b6f97baf190acb14c3c8cd9b1a15`；音频 `skipped`。
- 归档：knowledge-wiki `raw/inbound/ai-daily-report/2026/2026-05-18.md`，commit `36c614548f07`。

### 待观察
- Claude Code lane 因近两日报告已覆盖当前 raw releases，本日为 `empty`；后续需继续观察 release freshness 与去重是否符合 MT 对“固定保留”的预期。


### 2026-05-19 production run
- lane totals: total=14, ok=13, degraded=0, blocked=0, empty=1, selected_count=63.
- collect preflight: repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`; config `/Users/haha/.signal-engine/config/lanes.yaml`; data-dir `/Users/haha/.daily-lane-data`; registry complete for weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket. collect summary: ok=13, partial=1, error=0, useful=345.
- Feishu: doc=https://www.feishu.cn/docx/GF5cdjALQo7xtkxzAlvcKK8snUc; card_status=succeeded; card_message_id=om_x100b6f8d44f864a4b3439ce44b7b124; audio_status=skipped.
- Artifacts: runtime `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-19`; report `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-19/report.md`; collect log `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-19/logs/collect.log`.
- Archive: knowledge-wiki `raw/inbound/ai-daily-report/2026-05-19.md`, commit `77a4f8d`.
- Follow-up: Claude Code lane empty because same raw releases were already covered in recent reports; github-ai-projects remained a derived lane with no direct collector and was packaged from upstream evidence.

## 2026-05-20 production run
- lane totals: total=14, ok=14, degraded=0, blocked=0, empty=0, selected_count=73.
- collect preflight: repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`; config `/Users/haha/.signal-engine/config/lanes.yaml`; data-dir `/Users/haha/.daily-lane-data`; registry complete for weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket. collect summary: ok=13, partial=1, error=0, useful=341. HN collect failed once, diagnose/retry in same run succeeded.
- Feishu: doc=https://www.feishu.cn/docx/MapidD6JtoUPPxxGHAfcaykUnMd; card_status=succeeded; card_message_id=om_x100b6ffa6eb3c4a0b269bb8cf6d3be6; audio_status=skipped.
- Artifacts: runtime `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-20`; packages `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-20/lane-packages`; outputs `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-20/lane-outputs`; report `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-20/report.md`.
- Archive: local `/Users/haha/.daily-lane-data/archive/daily-report-master/2026-05-20`; knowledge-wiki `raw/inbound/ai-daily-report/2026/2026-05-20.md`, commit `1ada166`.
- Follow-up: codex/openclaw/x-following lane-meta required schema-key normalization before validation; subagent-written lane markdown was not rewritten.

## 2026-05-21 生产运行记录

- runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-21`；collect 使用 repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`、config `/Users/haha/.signal-engine/config/lanes.yaml`、data-dir `/Users/haha/.daily-lane-data`。
- collect preflight: lane registry 覆盖 weather / reddit / HackerNews / Claude Code / Codex / OpenClaw / Polymarket / Rize；`product-hunt-watch` 与 `x-feed` diagnose 均 HEALTHY。
- collect/retry: `hacker-news-watch` 首次因 SSL handshake timeout 失败，同一 run 内 diagnose 后 retry 成功；最终 collect-result 13 ok + `github-ai-projects` derived partial，0 error，useful_item_count=350。
- Hermes lane subagents: 14 个 lane package 均为 `raw_corpus_status=ok` 且 `raw_file_count>0`；14 个 lane-output 均由 subagent 写入 `lane.md` + `lane-meta.json`。
- lane totals: total=14, ok=13, empty=1, degraded=0, blocked=0；Reddit 因 raw 缺评论 substance 且近两日重复，状态 empty。selected_count=73。
- validation/assembly: `validate_lane_outputs.py` passed；最终 report `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-21/report.md`。
- Feishu: doc succeeded `https://www.feishu.cn/docx/BGPmd2FeuoQyQJxf8bQchDObnXf`；card succeeded `om_x100b6fd7757c64a0b228ff4b1e30a40`，并在 Rook DM recent history 中验证为 user-sent interactive card；audio skipped。
- archive: knowledge-wiki `raw/inbound/ai-daily-report/2026/2026-05-21.md` committed and pushed at `336e6117d0e4da6d5c2f5f374535d0dbda392b56`。


## 2026-05-22 production run

### 运行记录
- collect preflight 使用 repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`、config `/Users/haha/.signal-engine/config/lanes.yaml`、data-dir `/Users/haha/.daily-lane-data`；lane registry 包含 weather / reddit / HN / Claude / Codex / OpenClaw / Polymarket 等生产 lane。
- collect result：14 lanes，13 ok、1 partial（`github-ai-projects` 为 derived lane，无 direct collector），0 error；`useful_item_count=347`。
- lane packages：`/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-22/lane-packages`，14 个 package 均 `raw_corpus_status=ok` 且 `raw_file_count>0`。
- Hermes lane subagents：14 个 lane 均重新生成 `lane.md` + `lane-meta.json`；validation passed；assembled report path `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-22/report.md`。
- lane status：14 total / 13 ok / 0 degraded / 0 blocked / 1 empty（reddit 按去重与评论 substance 不足输出 empty）。selected_count=69。
- Feishu：doc succeeded `https://www.feishu.cn/docx/Gi2Qd4Zk8oOqdLxUtWUc4pX8n8f`；interactive card succeeded，message_id `om_x100b6fcc089638a0b283a90ce521207`，已在 Rook DM chat history 中验证；audio skipped。
- archive：最终 report 已归档到 knowledge-wiki `raw/inbound/ai-daily-report/2026/2026-05-22.md`。

### 观察 / 待跟进
- Reddit raw 仍能 collect，但 subagent 判断近两日重复且缺少评论正文 substance，输出 empty；后续若继续保留 Reddit，需要 collector 拉取可引用评论正文，否则容易“有 raw 但不可写”。
- 多个 delegated subagent 报 skill 不在本地可见，但凭 package prompt 和 lane contract 仍完成输出；后续可检查 Hermes skill 同步，降低 audit 风险。

## 2026-05-25 production run

- lanes: total=14, ok=12, degraded=0, blocked=2, empty=0, selected_count=64
- collect preflight: repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`; config `/Users/haha/.signal-engine/config/lanes.yaml`; data-dir `/Users/haha/.daily-lane-data`; registry included weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket/Product Hunt/Rize.
- collect artifacts: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-25/collect-result.json`, `selected-items.json`, `validation-bundle.json`; collect summary useful_item_count=309, non_ok=3.
- lane evidence: packages `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-25/lane-packages`, outputs `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-25/lane-outputs`; validation confirmed 14 `lane.md` + 14 `lane-meta.json`.
- degraded/blocked: rize blocked after diagnose/retry (`UNEXPECTED_EOF_WHILE_READING`, and diagnose showed missing lane config); polymarket blocked after diagnose/retry (SSL certificate verify failed on all configured queries).
- final report: lane validation passed; assembled `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-25/report.md`; selected_count=64.
- Feishu: doc `https://www.feishu.cn/docx/TgiGd975Zow0NAxDzEtcxC2KnOg`; card status=succeeded, message_id=om_x100b6e03c665a4a0b2ca05ee89760f9; audio=skipped; chat history verified returned message id from user sender.
- archive: knowledge-wiki `raw/inbound/ai-daily-report/2026/2026-05-25.md`, commit `1c9695c`.


## 2026-05-26 production run

- lanes: total 14 / ok 13 / degraded 0 / blocked 0 / empty 1; selected_count=70.
- collect preflight: repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`; config `/Users/haha/.signal-engine/config/lanes.yaml`; data-dir `/Users/haha/.daily-lane-data`; lane registry included weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket. `x-feed` diagnose still reported browser-session probe BROKEN, but collect/retry produced 100 raw files and package status ok.
- artifacts: `collect-result.json`, `selected-items.json`, `validation-bundle.json`; packages `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-26/lane-packages`; outputs `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-26/lane-outputs`. All lanes had `lane.md` + `lane-meta.json`; validation passed; `report.md` assembled.
- degraded/blocked: none. Empty: claude-code (today's raw releases were repeats of 2026-05-25 coverage, so lane agent left it empty rather than duplicating).
- Feishu: doc `https://www.feishu.cn/docx/Br9jdQ8TpoDFDUxflcxczlsinNg`; card `succeeded` message `om_x100b6e78d10370a0b37e13aeda3f940`; audio `skipped`.
- archive: knowledge-wiki `raw/inbound/ai-daily-report/2026-05-26.md`, commit `578fee4`.


## 2026-05-27 production run

- lanes: total 14 / ok 12 / degraded 0 / blocked 0 / empty 2; selected_count=60. Empty: claude-code（raw releases 与近两日报告重复，无新增用户可见变化）、rize（weekly ranking 与 2026-05-26 高度重复，无新增可验证事实）。
- collect preflight: repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`; config `/Users/haha/.signal-engine/config/lanes.yaml`; data-dir `/Users/haha/.daily-lane-data`; lane registry included weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket/Product Hunt/Rize. `x-feed` diagnose browser-session probe still reported BROKEN, but collect succeeded with 100 raw files.
- collect artifacts: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-27/collect-result.json`, `selected-items.json`, `validation-bundle.json`; collect useful_item_count=355, non_ok=1 (`github-ai-projects` derived lane has no direct collector).
- lane evidence: packages `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-27/lane-packages`, outputs `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-27/lane-outputs`; all 14 lanes have fresh `lane.md` + `lane-meta.json`; validation passed; report assembled at `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-27/report.md`.
- degraded/blocked: none.
- Feishu: doc `https://www.feishu.cn/docx/NRdtdPUEboU3UAxCCiXcnF0jnkc`; card `succeeded` message `om_x100b6e558cf520a0b3bf35f955213e6`, verified in Rook DM recent history as user-sent interactive card; audio `skipped`.
- archive: knowledge-wiki `raw/inbound/ai-daily-report/2026-05-27.md`, commit `c9ec567`.

## 2026-05-28 cron delivery

- status: succeeded
- doc: https://www.feishu.cn/docx/B2did6kgCoLFuwxL0XvcLB0Wnxh
- card: succeeded / om_x100b6e42aebdd4a4b11804e1d3939ae
- runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-28`
- updated: 2026-05-27T22:20:16.478191+00:00


## 2026-05-29 production run

- lanes: total 13 / ok 12 / degraded 1 / blocked 0 / empty 0; selected_count=64.
- collect preflight: repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`; config `/Users/haha/.signal-engine/config/lanes.yaml`; data-dir `/Users/haha/.daily-lane-data`; lane registry included weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket/Product Hunt/Rize.
- collect artifacts: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-29/collect-result.json`, `selected-items.json`, `validation-bundle.json`; collect useful_item_count=321, non_ok=2.
- lane evidence: packages `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-29/lane-packages`, outputs `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-29/lane-outputs`; all 13 lanes have `lane.md` + `lane-meta.json`; validation passed; report assembled at `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-05-29/report.md`.
- degraded/blocked: reddit degraded because Reddit public JSON search returned HTTP 403 during collect; diagnose reported registered/enabled lane and retry still wrote 0 raw files. `github-ai-projects` was treated as derived/no direct collector, not a blocking collect failure.
- Feishu: doc `https://www.feishu.cn/docx/FA8FdUnmToUjLWxG7IZcdF8bnwf`; card `succeeded` message `om_x100b6ebfa8adc0a0b27764d63d50693` (resent with `Rook｜` title and live-verified); audio `skipped`.
- archive: knowledge-wiki `raw/inbound/ai-daily-report/2026/2026-05-29.md`, commit `ee791fa`.
## 2026-05-30

### 运行记录
- 06:00 Hermes 原生 subagent lane 架构完成当日日报；13 个 lane package 均由 lane subagent 写出 `lane.md` + `lane-meta.json`。
- Reddit collect 因 Reddit public JSON HTTP 403 阻断，已在同一 run 内 diagnose + retry，最终 Reddit lane 标记为 blocked，未用旧 renderer 或历史内容 fallback。
- Feishu 文档发布成功；首次卡片 header 缺少 `Rook｜`，live verification 后已重发修正版卡片并更新 runtime `publish-state.json`。

### 待观察
- Reddit public JSON 403 是否需要继续在 `signals-engine` 层修复或移出默认 reader-facing flow。
- `publish_report.py` 默认卡片标题仍会生成非自说明 header，后续应把 `Rook｜` 标题要求固化到发布脚本测试里。
## 2026-05-31

- Cron run completed with Hermes native subagent lanes.
- Degraded/blocked: Reddit collection blocked by Reddit HTTP 403 after diagnose/retry; lane output marked blocked. GitHub AI projects treated as derived lane.
- Feishu card live-corrected to self-identifying header `Rook｜AI Agent 日报（2026-05-31）`.

## 2026-06-07 cron run
- Status: succeeded; validation passed; Feishu doc/card delivered.
- Runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-06-07`
- Report: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-06-07/report.md`
- Feishu doc: https://www.feishu.cn/docx/DoKcdl9n8oRESixRCkMcSIGunpe
- Card message: om_x100b6d7d932770a0b1d9fff58600cd4
- Notes: Rize and GitHub AI projects empty by lane judgment; OpenClaw degraded due subagent-reported package/evidence fallback, but output was validated. Card header was live-corrected to include `Rook｜`.


- 2026-06-08: Hermes subagent lane daily report delivered; validation passed; OpenClaw lane degraded due package gap; Feishu corrected doc/card succeeded; assemble script patched to include OpenClaw lane.

## 2026-06-09

### 运行记录
- 06:00 cron 使用 Hermes 原生 subagent lane 架构完成当日日报：先 repo-local `signals-engine` collect，再 prepare lane packages，再逐 lane `delegate_task` 写 `lane.md` / `lane-meta.json`，最后 validate / assemble / publish / archive。
- Feishu card 首次发送后 live verification 发现 header 仍是 `AI Agent 日报（2026-06-09）`，同 run 已按卡片规范重发为 `Rook｜AI Agent 日报精选（2026-06-09）`，并撤回 superseded card。
- OpenClaw reader lane 因 prepare package gap 使用 raw `openclaw-watch` evidence 降级生成；需要后续修复 package 映射，避免 lane subagent 依赖 raw fallback。

### 待验证 / 后续
- 修复 `prepare_lane_packages.py` 的 OpenClaw package 映射，让 `lane-packages/openclaw` 正常出现。
- 检查 `publish_report.py` 是否仍会忽略传入 title 生成非自说明 card header；应在 helper 内固定 `Rook｜` header，避免每次 cron 后置重发。
## 2026-06-10 cron run

- Hermes native lane-subagent pipeline completed for 2026-06-10.
- Collect used repo-local signals-engine (`uvx --from /Users/haha/workspace/signals-engine`) with `/Users/haha/.signal-engine/config/lanes.yaml` and data root `/Users/haha/.daily-lane-data`; lane registry contained weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket.
- Lane outputs: 14 total, 12 ok, 1 degraded (`openclaw`: package-path anomaly handled with raw evidence), 0 blocked, 1 empty (`reddit`: no non-duplicative discussion substance).
- Publish succeeded; original card header lacked `Rook｜`, corrected card was resent and the superseded message was recalled.
- Knowledge-wiki archive commit: `21c1cc4`.


## 2026-06-11

### 运行记录 / 已采取改动
- 06:00 Hermes master cron 按原生 subagent lane 架构完成：repo-local `signals-engine` preflight、逐 lane collect、lane package 准备、Hermes lane subagent 写作、validate/assemble、Feishu Docx + 精选卡片发布、knowledge-wiki 归档。
- 发布后发现 helper 生成的 Feishu card header 仍是非自说明标题 `AI Agent 日报（2026-06-11）`；同 run 内已按既有规则重发 `Rook｜AI Agent 日报精选（2026-06-11）` 卡片、live verify，并撤回 superseded card。
- `openclaw` package 阶段仍未生成标准 package，但 raw `openclaw-watch` 存在；本次以 degraded lane 输出保留并记录 packaging gap。

### 待验证
- 后续应修复 `openclaw-watch` -> `openclaw` package 映射，避免 lane subagent 需要走降级 raw 路径。
- 发布 helper 应直接生成 `Rook｜...` card header，避免每次发布后再修正重发。

## 2026-06-12

### 运行记录
- 06:00 Hermes master cron 按原生 subagent lane 架构完成：repo-local `signals-engine` preflight、逐 lane collect/diagnose/retry、lane package 准备、Hermes lane subagent 写作、validate/assemble、Feishu Docx + 精选卡片发布。
- Collect preflight 使用 `uvx --from /Users/haha/workspace/signals-engine signals-engine`、生产配置 `/Users/haha/.signal-engine/config/lanes.yaml`、data root `/Users/haha/.daily-lane-data`；lane registry 包含 weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket。
- Reddit collect 首次和 retry 均被 Reddit RSS HTTP 429 限流，最终 Reddit lane 输出为 blocked，不使用 fallback。
- Rize 与 OpenClaw lane 均由 lane subagent 判定为 empty：Rize 排名快照与近两日实质一致；OpenClaw release 信号已被近两日报告覆盖。
- 发布 helper 首次生成的 Feishu card header 仍缺 `Rook｜`；同 run 内已重发 corrected card `Rook｜AI Agent 日报精选（2026-06-12）` 并 live verify，`publish-state.json` 已指向 corrected `message_id`。

### 待验证
- 修复发布 helper 默认 card header，避免后置重发。
- 继续观察 Reddit RSS 429；若持续发生，需要在 signals-engine 内改成更稳的 Reddit 数据源或更保守节流。


## 2026-06-13

### 运行记录 / 待跟踪
- 06:00 Hermes 原生 subagent lane 架构完成：collect、prepare lane packages、13 个 lane subagent、validate、assemble、Feishu doc/card、knowledge-wiki archive。
- Reddit collect 遇到 Reddit RSS HTTP 429；同 run 已 diagnose/retry，最终只有 8 个低信号 raw，lane subagent 输出 empty 并在正文记录降级原因。后续可继续跟踪 Reddit public lane 429 缓解。
- `github-ai-projects` 继续按 derived lane 处理，无 direct collector；本次从 GitHub/cross-lane evidence 产出。
- publish helper 首次 card header 仍生成非自说明 `AI Agent 日报（2026-06-13）`；同 run 已修正为 `Rook｜AI Agent 日报精选（2026-06-13）`、重发、live verify，并撤回 superseded card。后续仍应把 card header live verification 作为强制 gate。
- 当前 runtime config 的 reader-facing order 不含 `openclaw`，assembler 在运维提示里标注“未生成 openclaw”。如果 MT 仍期望 OpenClaw 栏目，需要同步 config 与 package/assemble 规则，而不是让旧 renderer fallback。

## 2026-06-15

### 运行记录
- Hermes 原生 subagent lane 架构完成 2026-06-15 日报：collect → prepare lane packages → 14 个 lane subagent → validate → assemble → Feishu Docx + 精选卡片发布。
- collect preflight 使用 repo-local `uvx --from /Users/haha/workspace/signals-engine signals-engine`、生产配置 `/Users/haha/.signal-engine/config/lanes.yaml`、data-dir `/Users/haha/.daily-lane-data`；lane registry 覆盖 weather/reddit/HN/Claude/Codex/OpenClaw/Polymarket 等生产 lane。
- Reddit collect 首次与 retry 均失败，diagnose 执行成功但 raw 文件仍为 0；日报中 Reddit lane 由 subagent 标记为 blocked/无 raw evidence，不用 selected_items 或旧 renderer 补写。
- `config/runtime.yaml` 的 reader-facing order 未包含 OpenClaw，但 `openclaw-watch` collector 成功产出 raw；本轮手动准备 OpenClaw package 并交给 `daily-report-lane-openclaw` subagent 输出，避免栏目静默遗漏。
- 发布 helper 首发卡片 header 仍为非自说明 `AI Agent 日报（2026-06-15）`；同 run 已修正为 `Rook｜AI Agent 日报精选（2026-06-15）`，live verified 后撤回 superseded card，并回写 runtime publish state。

### 产物
- runtime: `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-06-15/`
- archive: `archive/2026-06-15/`
- doc_url: `https://www.feishu.cn/docx/QkCydFKnpoVkrMx5boDc0kbCnLd`
- final card message: `om_x100b6dc6d52d54a0b3b3c466f4ea634`
