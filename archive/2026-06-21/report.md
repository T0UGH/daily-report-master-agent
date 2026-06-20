# AI Agent 日报（2026-06-21）

## 天气

- **北京·海淀：阴，14.2°C–29.4°C。** 降水概率 0%、预计 0 mm，西南风最高 13 km/h；较昨日最高温回升约 1.9°C、低温下降约 4.9°C，白天偏热但早晚温差大，通勤不用重点防雨，注意补水和薄外套。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-21&end_date=2026-06-21)
- **上海·杨浦：雷暴，22.5°C–27.8°C。** 降水概率 88%、预计 15.9 mm，东风最高 10.8 km/h；较昨日最高温下降约 2.5°C、雨量从 9.4 mm 增至 15.9 mm，仍是强降雨/雷暴日，出门带伞、防滑，并尽量避开雷暴时段户外停留。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-21&end_date=2026-06-21)

**今日取舍：** 天气为每日固定实用信息，不因近两日报告已有同类栏目而去重；保留北京·海淀和上海·杨浦两地 2026-06-21 当日预报，并仅用近两日报告辅助判断体感变化。

## X 推荐

1. **Hermes Agent 新增 Blank Slate setup mode。** Quick/Full 仍面向默认安装，新模式留给想从空白配置起步、自己决定连接项和自动化边界的用户；这是昨天 v0.17.0 发布后的具体增量。  
   https://x.com/NousResearch/status/2068405008685539514

2. **有人在 Codex Desktop App 里跑了接近 300 个 subagents，单个 session 持续超过一天。** 这条不是产品公告，但给出了多 agent 长任务的压力信号：要关注队列、恢复、成本、日志和人类接管方式。  
   https://x.com/q_yeon_gyu_kim/status/2067865572139053297

3. **lazycodex harness 把类似 Claude Code 的 team mode 带到 Codex App。** 作者称已让 Codex 也能用 team feature；如果要试，应先看权限、并发写文件冲突和 agent 间交接记录。  
   https://x.com/q_yeon_gyu_kim/status/2068188458737377650

4. **OpenCodex 更新了原生 GPT 模型与自定义模型共存列表。** 用户可以在 GPT 与自定义模型之间切换，并延续上下文；对额度不稳定或多供应商回退的 Codex 工作流有直接价值。  
   https://x.com/Youngxxxxu/status/2068199186781380699

5. **Codex Skill 清单在中文圈继续扩散，Superpowers 被列为首项。** 原帖强调“拆需求、写计划、TDD、再派子 agent 审查”的工程方法被封装成 skill；团队可借此把 agent 使用从一次性提示词转成可复用流程。  
   https://x.com/KyrieCheungYep/status/2068306688651018272

6. **Agent Reach 被推荐给 Claude、Cursor 等 agent 解决联网抓取问题。** 原帖称项目开源、34k+ stars，定位是补齐 agent 浏览网页、处理付费墙/验证码/动态站点时的能力短板；试用时要把登录态和隐私隔离放在首位。  
   https://x.com/hank_aibtc/status/2068171356060217706

7. **Palmier Pro 把视频剪辑暴露给 Claude / Cursor 这类 agent。** 这款 Mac 原生 AI 视频编辑器称核心编辑器和 MCP 服务开源、GPLv3，让 agent 能在时间线里执行剪片动作；适合关注 MCP 从代码走向创作工具。  
   https://x.com/hank_aibtc/status/2068250038942498958

8. **有人做了 `/remove-ai-slop` skill，用来清理 AI 生成内容的“味道”。** 它受 review skill 与 Cursor code quality skill 启发，说明社区正在把审美、表达质量和风格约束做成 agent 可调用的检查步骤。  
   https://x.com/tushaarmehtaa/status/2068209228565918154

9. **FastAPI 现在可以直接服务前端应用，并支持客户端路由。** 对 agent 生成全栈原型很实用：React/TanStack Router 等前端可由同一个 Python 服务托管，减少 demo 部署和本地预览的胶水代码。  
   https://x.com/FastAPI/status/2068141463506935843

10. **browser-use 称 GLM 5.2 在网站设计评测里超过 Fable 5，但也指出它是 text-only。** 这是 GLM 5.2 热度中的一个更具体切面：代码生成能搭站点，不代表能看见或自评视觉结果，仍需要浏览器反馈或视觉模型闭环。  
   https://x.com/browser_use/status/2068405699340853541

## X 关注

- **Hermes Agent 新增 Blank Slate setup mode。** 默认 Quick/Full 适合大多数用户，Blank Slate 则指向更低预设、更可控的初始化路径；raw 未展开完整选项，升级前应看默认权限、技能/MCP 安装范围和迁移说明。https://x.com/NousResearch/status/2068405008685539514

- **Codex + Excalidraw 被展示成原生“无限画布”工作流，无需额外插件。** 这把 coding agent 的输出从代码 diff 扩到草图、架构图和流程图；团队可用它做需求拆解或 PR 讲解，但要确认画布内容能否版本化、回链代码和避免泄露上下文。https://x.com/yanhua1010/status/2068323353421897742

- **dotey 把 agent 写代码的问题重新放回传统软件工程框架：需求分析、让 agent 理解需求，再到验收。** 这不是新工具，但给团队一个实用落点：把“人+Agent”当成新的执行主体后，需求、测试、评审和交付边界仍要显式写清。https://x.com/dotey/status/2068363092904276316

- **jakevin7 提到 Maka 在做闭环式 system prompt 自优化：agent 根据目标自动改自己的提示词，无需人工介入。** raw 只到方向描述，不能写成成熟产品；评估重点应放在目标函数、回归集、坏 prompt 回滚、权限边界和是否会为追分牺牲安全约束。https://x.com/jakevin7/status/2068354579251782068

- **aiedge_ 把“prompt engineering”转向“loop engineering”：让 agent 自己提示自己完成任务。** 这与上面的自优化 prompt 信号互相印证，关注点应从一次性提示词转到循环停止条件、状态观测、错误检测、预算上限和人工接管。https://x.com/aiedge_/status/2068423648046916044

- **UC Berkeley 与 NVIDIA 的 T-Rex 工作把触觉数据叠加到 VLA，转述称翻书、运鸡蛋、擦桌子、剪纸成功率提升 30%+。** 对机器人 agent，这说明视觉/语言之外的高频反馈会影响执行可靠性；raw 截断，仍需核对论文、任务设置和真实硬件泛化。https://x.com/MinLiBuilds/status/2068359670369247730

- **serve-sim 更新被转发：新增 simulator buttons/controls、统一设备面板和快速设备切换。** 这条信号很短，但对移动端/前端 agent 有具体价值：模拟器控制面更稳定，agent 写完 UI 后才更容易自动跑、切设备和复现失败。https://x.com/Dimillian/status/2068409466446287336

- **screenshot-to-code 被再次推荐：把截图、mockup、Figma 设计和屏幕录制转为可工作的代码。** 近日报告已多次覆盖设计到代码，今天仅保留其“屏幕录制也作为输入”的增量；试用时应看生成代码结构、组件语义、响应式细节和人工 diff 审查。https://x.com/GithubProjects/status/2068401007701451204

**今日取舍：** 已读取 `input.md`、`context.json`、100 条 x-following raw，以及 2026-06-20 / 2026-06-19 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日已覆盖 Hermes Agent v0.17.0、Codex Record & Replay、Claude Code Artifacts、AI PR prompt injection、Gemini 循环缓解、Bitrig 自检、GLM-5.2 工程细节、SwiftUI Agent Skill、Mercury Agent 记忆、Hermes MCP Catalog/Box company brain 等，因此今天优先保留 Blank Slate setup、Codex+Excalidraw 画布、agent 软件工程方法、自优化/loop engineering、触觉 VLA、serve-sim 模拟器控制和 screenshot-to-code 屏幕录制输入。剔除纯转发/纯 t.co、生活旅行/政治/金融/体育、低证据模型偏好、GLM 重复讨论、课程/营销、泛 AI 口号，以及与 AI/coding-agent 工作流关联弱于入选项的内容。

## Reddit 社区

今日暂无可新增的 Reddit 社区更新。本次 raw corpus 为 `ok`、共 8 个 r/ClaudeAI 线程，均显示 0 score / 0 comments；其中 Opus 4.8、dynamic workflows / ultracode、离线 Claude Code、本地/第三方模型接入 Claude Code、Fable vs Opus 评测、Ultracode vs Max 提问、社区向 Claude Code power users 倾斜等主题，已在近两日报告或相邻 lane 中实质覆盖，今天没有新的评论、分数变化或未报道事实可支撑再次刊登。

**今日取舍：** 已读取 `input.md`、`context.json`、8 个 reddit raw 文件，以及 2026-06-20 / 2026-06-19 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。由于可读 raw 中没有未被近两日报告实质覆盖、且足够支撑 reader-facing 更新的新社区事实，本栏标记为空而非降级。

## Hacker News 热榜

- **推理成本的 napkin math 讨论登上 HN #8，20 分、3 评论；读者把焦点放在 B200 是自购还是租用。** 评论用每张 B200 约 4 万美元、300 用户满载摊销约每用户 133 美元，或租用每用户约 0.013 美元/小时的口径，提醒做 agent 产品时要把占用率、并发、托管和闲置成本分开算。 [HN](https://news.ycombinator.com/item?id=48560227) / [文章](https://injuly.in/blog/napkin-inference-cost/index.html)

- **Bun 给 JavaScriptCore 加 shared-memory threads 的 PR 在 HN #10 引发 130 条评论；高赞质疑点不是线程本身，而是“大 PR + AI 生成代码”能否被信任。** 评论提到这是 Anthropic 生成、单人监督、约 1800 个文件变化的 PR，认为语言运行时需要“obviously no bugs”而不只是“no obvious bugs”；对 coding-agent 团队，这条是自动化大改 runtime/基础库时必须拆 PR、做审计和回归的反例。 [HN](https://news.ycombinator.com/item?id=48610841) / [PR](https://github.com/oven-sh/WebKit/pull/249)

- **“Obscure Sorrows 被批量抄袭”在 HN #5，274 分、117 评论；讨论把 AI 重写/套壳和版权执行问题放到一起。** 高赞评论称自己的免费软件被人用 AI 重命名、重发成新 app，DMCA 在应用商店里很难推进；对用 agent 生成产品、文档或代码的人，关键是保留 provenance、隐藏水印/测试点、许可证证据和人工审核，避免把“AI 生成”当成抄袭免责。 [HN](https://news.ycombinator.com/item?id=48611411) / [文章](https://waxy.org/2026/06/the-wholesale-plagiarism-of-obscure-sorrows/)

**今日取舍：** 已加载 `daily-report-lane-hacker-news` skill，读取 `input.md`、`context.json`、10 条 HN topstories raw，以及 2026-06-20 / 2026-06-19 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日 HN 已覆盖挪威小学 AI 限制、Project Valhalla、Boston Dynamics、ATProto、Workspace/Firefox、Noam Shazeer、GitHub 木马仓库、Mythos/SK Telecom、模型记忆隐私和 Ubiquiti NAS；今天保留推理成本、Bun/JSC 大 PR 的 AI 代码审计争议、AI 套壳抄袭与维权。剔除 CSSQuake、DOS 游戏逆向、StartupWiki、SMPTE 标准开放、UHF X11、PostgresBench、巴西手机警报等，主要因与 AI/coding-agent 工作流关联弱，或只有单条评论提到 Claude Code、证据不足以支撑本栏展开。

## Hacker News 搜索观察

- **Velane 试图做“由 coding agent 编写 workflow”的 n8n 替代品，把工作流从画布节点/JSON blob 转成更适合代码审查、diff 和调试的开发者可读格式。** 作者指出 n8n 的 MCP 可让 agent 生成 workflow，但产物是原始 JSON，B2B 嵌入和多租户规模下难维护；评估这类工具要看格式是否能版本控制、权限/租户隔离、执行回放、失败重试和人工 review 边界。 [HN](https://news.ycombinator.com/item?id=48611785) / [Velane](https://velane.sh/)

**今日取舍：** 已读取 `input.md`、`context.json`、15 个 HN search raw 文件，以及 2026-06-20 / 2026-06-19 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。昨日已在本栏展开 Dapr/Diagrid workflow history signing、Konxios 和 CWC，并明确去重 SSG/SigmaShake、Relaymux、Claude Design、Pagecast、Agentbrowse 等；今天只保留未被近两日报告实质覆盖、且与 coding-agent 工作流产物形态直接相关的 Velane。其余项目因重复、无评论/标题级证据、偏教育/书签/设计营销，或与 AI/coding-agent 工作流增量弱于入选项而剔除。

## Claude Code

- **Claude Code `v2.1.185` 只改了一个很小但会影响长任务体感的 streaming 提示：stream stall 文案从 “No response from API · Retrying in …” 改为 “Waiting for API response · will retry in …”，且静默等待阈值从 10 秒延到 20 秒。** 这不是能力发布，也不是新的重试机制；更像是把“API 没响应”的告警降噪为“仍在等 API，并会重试”。对把 Claude Code 放进长会话、Remote Control、teammate 或后台任务的人，升级后的观察点是：监控/日志/截图指引若依赖旧文案需要同步更新；用户看到提示的时间变晚，可能减少误以为失败的中断，但也要确认真正网络故障时仍有足够快的可见反馈。 [v2.1.185](https://github.com/anthropics/claude-code/releases/tag/v2.1.185)

**今日取舍：** 已读取 `input.md`、`context.json`、4 个 raw 文件（CHANGELOG、`v2.1.181`、`v2.1.183`、`v2.1.185`）以及 2026-06-20 / 2026-06-19 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日报告已实质覆盖 `v2.1.181` 的 `/config key=value`、Apple Events、presence file、Bun 1.4、streaming/retry/subagent/OAuth 与可靠性修复，以及 `v2.1.183` 的 auto mode 破坏性操作护栏、模型 warning、`attribution.sessionUrl`、`/config --help`、subagent / MCP / teammate / scheduled task / webhook / TUI 修复；今天只保留新增的 `v2.1.185` 和同内容 CHANGELOG 更新。

## Codex

- **Codex TUI 允许在任务运行和 MCP 启动期间执行 `/resume` 与部分设置命令。** #29154 让 `/model`、`/permissions`、`/personality`、`/fast` 等可在 busy 状态下更新后续 turn 的设置，当前 turn 仍使用启动时捕获的配置；慢 MCP 启动时不再阻塞恢复会话和切换后续任务参数。 [PR #29154](https://github.com/openai/codex/pull/29154) / [commit d667082](https://github.com/openai/codex/commit/d66708232299bdbf373ec55b0d6b938c246cfa60)

- **environment context 迁移到 typed world state，并移除并行的 legacy environment DTO。** #29252 让 `EnvironmentsState` 直接从每个 turn environment 构建，支持多 environment 按序渲染；持久化和 diff 仍只限 `cwd`，shell、日期、时区、网络、文件系统和 subagent 信息保持 live-only。 [PR #29252](https://github.com/openai/codex/pull/29252)

- **`<token_budget>` 开始暴露 context window lineage IDs。** #29256 在 auto-compaction 状态中跟踪 first、previous、current UUIDv7 window ID，并渲染 `thread_id`、`first_window_id`、`previous_window_id` 与当前 window ID；这些 ID 会随 compaction checkpoint 保存并在 resume、rollback、rollout reconstruction 中恢复。 [PR #29256](https://github.com/openai/codex/pull/29256) / [commit d1209bd](https://github.com/openai/codex/commit/d1209bddfce79e8f6cafd7f9212a2df6915aec5d)

**今日取舍：** 已加载 `daily-report-lane-codex` skill，读取 `input.md`、`context.json`、5 个 Codex raw 文件，以及 2026-06-20 / 2026-06-19 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日已覆盖 `0.141.0`、`0.142.0-alpha.6`、indexed web search、environment-scoped network approvals、remote unified-exec plain argv、rollout budget abort、orchestrator skills/MCP toggles、skill description preservation、tracing 与 websocket 修复等；今天保留 busy 状态下 resume/settings 命令、environment context → world state 迁移、context window lineage IDs。commit 与 merged PR 重复时合并为同一条证据。

## OpenClaw

今日暂无可新增的 OpenClaw 更新；本次 `openclaw-watch` raw 仍是 3 个 release 信号（`v2026.6.9-beta.1`、`v2026.6.8`、`v2026.6.8-beta.2`），采集成功但均已在近日报告覆盖或被正式版收口：`v2026.6.9-beta.1` 已在 2026-06-20 OpenClaw 栏刊登，`v2026.6.8` 与 `v2026.6.8-beta.2` 已在 2026-06-18/2026-06-20 的去重判断中处理，因此今天不重复刊登。

## GitHub AI 项目

- **[withastro/flue](https://github.com/withastro/flue)（GitHub API 校验 6,067 stars）把 agent “harness”做成 TypeScript 框架：sessions、tools、skills、filesystem access、local/remote/virtual sandbox、durable execution 和 subagents 都在同一套运行边界里配置。** raw 只给出“sandbox agent framework”的 weekly trending 信号，我补查 README 与 GitHub metadata 后确认它直接面向可行动 agent；试用时应重点看 sandbox 隔离、工具权限、失败恢复、部署到托管 runtime 的密钥边界，以及 subagent 任务交接是否可审计。 [GitHub](https://github.com/withastro/flue)

**今日取舍：** 已读取 `input.md`、`context.json`、GitHub trending weekly raw、HN search/topstories raw、Reddit/X 交叉 raw、selected-items-compatible audit 文件，以及 2026-06-20 / 2026-06-19 历史报告；历史仅用于去重，`selected-items` 仅作 audit 参考，未作为主要判断。按 hard floor stars ≥100，本次只选择已用 GitHub API 校验达标、且有当日 raw 支撑、并未被近两日报告实质覆盖的新仓库：`withastro/flue` 6,067 stars。`DeusData/codebase-memory-mcp`、`addyosmani/agent-skills`、`NVIDIA/SkillSpector`、`Panniantong/Agent-Reach`、`chopratejas/headroom`、`phuryn/pm-skills` 等虽达标但已在近日报告覆盖或明确去重；`fayzan123/claude-workflow-composer` 23 stars、`Amal-David/pagecast` 91 stars、`mupt-ai/relaymux` 10 stars 未达本 lane 星标门槛；`LMCache/LMCache`、`lfnovo/open-notebook`、`google-research/timesfm` 达标但分别偏 serving KV-cache、NotebookLM 复刻和时序预测，今天与 AI/coding-agent 项目工作流的直接增量弱于入选线。

## GitHub 趋势项目

- **[withastro/flue](https://github.com/withastro/flue) 本周上榜，GitHub API 校验 6,067 stars；它是 Astro 团队推出的 TypeScript agent harness，README 明确包含 sessions、tools、skills、filesystem access、sandbox、durable execution、subagents、MCP 与 observability。** 这类框架把 Claude Code/Codex 式“给任务和工具，让 agent 在沙箱里持续执行”的模式产品化；试用重点是沙箱隔离、事件渠道权限、MCP 鉴权、持久执行恢复和遥测是否足够审计。

**今日取舍：** 已读取 `input.md`、`context.json`、21 个 GitHub trending raw 文件，以及 2026-06-20 / 2026-06-19 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。入选仓库来自本 lane raw corpus，并通过 GitHub REST API 校验 stars ≥100。近两日报告已覆盖或明确去重 `DeusData/codebase-memory-mcp`、`kenn-io/agentsview`、`addyosmani/agent-skills`、`NVIDIA/SkillSpector`、`Panniantong/Agent-Reach`、`chopratejas/headroom`、`phuryn/pm-skills` 等；今天只保留此前未展开、且直接服务 agent harness / sandbox / skills / MCP / durable execution 工作流的 `withastro/flue`。`asgeirtj/system_prompts_leaks`、`LMCache/LMCache`、`lfnovo/open-notebook` 等虽达标，但分别偏提示词归档、LLM serving KV-cache 与 NotebookLM 复刻；`chatwoot/chatwoot`、`freeCodeCamp/freeCodeCamp`、`puppeteer/puppeteer`、`pytest-dev/pytest`、`swc-project/swc` 等是高星通用项目，但 raw 只有通用描述，没有当日 AI/coding-agent 工作流增量。

## Rize AI 工具榜

今日暂无可新增的 Rize AI 工具榜更新；本次 raw corpus 正常，共 20 条 Rize weekly ranking 证据，但榜单快照仍与近日报告已处理的同一批 Rize weekly snapshot 实质相同。2026-06-19 已判定不再重复刊登，2026-06-20 也已再次去重；今天 raw 未提供新的排名变化、仓库发布事实或可作为 follow-up 的新增信息，因此继续空栏，避免连续日报重复同一批项目。

**今日取舍：** 已读取 `input.md`、`context.json`、20 条 Rize raw，以及 2026-06-20 / 2026-06-19 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近日报告已覆盖并随后去重 #3 antigravity-awesome-skills、#4 nanobot、#5 MemPalace、#6 OpenSquilla、#7 headroom、#9 graphify、#10 hermes-studio、#12 TencentDB-Agent-Memory；今天的 #1 worldmonitor、#2 openclaude、#8 ilab-gpt-conjure、#11 openlake、#13–#20 也没有比近日报告更强的 AI agent / coding-agent 工作流增量，全部作为重复或弱相关项剔除。

## Product Hunt 新品

- **pumaDB** 发布到 Product Hunt，定位是给 AI agents 用的小型托管记忆层。它对应长任务和多轮 agent 的状态持久化问题；试用时应看记忆写入/读取权限、来源追溯、租户隔离、删除/纠错，以及 agent 是否会把旧记忆误当成最新事实。 [Product Hunt](https://www.producthunt.com/products/pumadb?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **Mellum by JetBrains** 主打低延迟、高性能工作流里的快速 LLM。对 IDE 和 coding-agent 场景，关键不只是“更快”，还要验证代码补全/重构质量、工具调用稳定性、上下文窗口、私有代码处理和与 JetBrains 开发环境的集成边界。 [Product Hunt](https://www.producthunt.com/products/jetbrains?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **WorkClaw** 定位为在 Slack 里协作、主动工作的 AI coworkers。它和近期 Slackbot MCP 主线相近，但更偏“同事式 agent”；采用前应确认它能访问哪些频道/文件、如何标注 agent 身份、动作审批、审计日志和误触发后的回滚。 [Product Hunt](https://www.producthunt.com/products/workclaw?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** raw corpus 状态为 ok，共 8 个 Product Hunt topic hit；已读取 `input.md`、`context.json`、全部 raw 文件和 2026-06-20 / 2026-06-19 历史报告，仅用历史作去重参考，未使用 `selected_items.json` 驱动判断。近两日已覆盖 API→MCP、agent 可观察性、受治理数据 agent、Locofy、Refuse、Claude Code/MCP/Slackbot 等主题；今天保留 agent 记忆层、JetBrains 快速 LLM 和 Slack 中的 AI coworker。剔除 Slackbot’s MCP Client，主要因 2026-06-19 已由 X Feed 明确覆盖；剔除 Are you in the Weights?，因 2026-06-19 HN 已展开同主题；GitSync、Basedash、Pixlie 分别更偏通用 Git 图形界面、数据访问控制和 AI 视频生成，与 AI/coding-agent 工程工作流的新增价值弱于入选项。

## Polymarket AI 市场

- **6 月最佳 Coding AI 模型盘口继续高度集中：Anthropic 95.8%，OpenAI 1.5%、Moonshot 0.6%；24h 成交量约 225.1，30d 约 21,532.6，流动性约 90,689.3。** 与昨日报告的 Anthropic 95.8% 基本持平，但成交量降温；这仍只是交易者预期，不能替代代码库内的合并率、测试通过率、工具调用和长任务稳定性评测。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-june)

- **6 月最佳 AI 模型总榜仍压向 Anthropic：Anthropic 94.5%，Google 3.6%、OpenAI 2.1%；24h 成交量约 124,470.5，30d 约 6,424,244.7，流动性约 3,168,393.7，raw 标注本月上行 20.3%。** 较昨日 94.7% 小幅回落，但交易规模仍远高于其他 AI 盘口；做 agent 选型时应把通用声量拆成 coding、数学、工具调用、长上下文、成本与权限边界分别验证。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **7 月最佳 AI 模型远期盘维持 Anthropic 领先：Anthropic 84.5%，Google 10.1%、OpenAI 5.0%；24h 成交量约 113,906.9，30d 约 631,197.9，流动性约 630,303.3。** 较昨日 83.5% 回升，显示市场仍押注 Anthropic 优势延续到下月；但远期盘容易被新模型发布和榜单口径重定价，不应直接当作技术路线判断。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-july-299)

- **6 月最佳 Math AI 模型盘口从昨日 Google 76.0% 降到 66.5%，OpenAI 18.0%、Anthropic 10.5%；24h 成交量约 15,931.5，30d 约 228,089.6，流动性约 107,191.1，raw 标注本周下行 9.0%。** 数学盘口与通用总榜明显分化，形式化推理、benchmark-heavy agent 和代码证明类任务不应照搬“最佳 AI 模型”主盘。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-june)

- **FrontierMath 长盘继续高位：任一 AI 模型 2026 年前 ≥90% 的 Yes 为 82.0%，30d 成交量约 95,835.6，流动性约 8,340.9，raw 标注本月上行 61.0%。** 昨日报告为 81.5%；同批 Grok 子盘给出 ≥40% 为 81.2%、≥50% 为 18.0%，但这些都是市场预期，不是模型成绩已确认。 [Polymarket](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027) / [Grok 市场](https://polymarket.com/event/xai-grok-score-on-frontiermath-benchmark-by-june-30)

- **Coding Arena 1550 门槛盘仍显示低概率：任一 AI model 到 6 月 30 日达到 1550 Coding Arena Score 的主 outcome 约 3.4%，30d 成交量约 6,739.6，流动性约 4,748.7，raw 标注本月下行 50.1%。** 这与“最佳 Coding AI 公司”盘口高度押注 Anthropic并不矛盾：一个是相对排名，一个是绝对分数门槛，评估 coding agent 时应分开看。 [Polymarket](https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-june-30)

**今日取舍：** raw corpus 状态为 ok，共 11 条 Polymarket 证据；已读取 `input.md`、`context.json`、全部 raw 文件和 2026-06-20 / 2026-06-19 历史报告作为去重参考，未使用 `selected_items.json` 驱动判断。保留与 AI/coding-agent 直接相关、且有当日概率/成交量或近日报告可比变化的 6 月 Coding AI、6 月模型总榜、7 月模型远期盘、6 月 Math AI、FrontierMath 长盘/Grok 弱参考和 Coding Arena 1550 门槛盘。剔除估值盘、Style Control 版总榜、第二名细分盘口等重叠或弱增量条目；所有概率均为 Polymarket 市场预期，不是已确认 benchmark 或产品事实。
