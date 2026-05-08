# AI Agent 日报（2026-05-09）

## 天气
- **北京·海淀：阴，14.1°C–24.4°C** 今天降水概率 2%、0 mm，西风最高 11.4 km/h；比昨天最高温略降、早晚回暖，通勤基本不用防雨，注意阴天体感偏凉。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-09&end_date=2026-05-09)
- **上海·杨浦：阴，11.6°C–23.7°C** 今天降水概率 0%、0 mm，东南风最高 13.4 km/h；较昨天早晨更冷、午后升温明显，无雨但温差大，外出建议带轻外套。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-09&end_date=2026-05-09)

## X 推荐流

- **@0xLogicrw：OpenAI 后训练成员开源“启发式学习”RL 实验** 帖子称 Jiayi Weng 用 Codex（GPT-5.4）反复玩 Atari 打砖块，提出 heuristic learning 并放出实验代码；适合跟踪 LLM+RL 从奖励学习转向自我发现策略的尝试。 [原帖](https://x.com/0xLogicrw/status/2052701677615218717)
- **@an_engineer_log：并行管理 20 个 AI Agent 的任务台问题被产品化** 作者指出单个 agent 好用，但 20 个并行任务会遇到 cron 静默失败、阻塞和手动检查；这类工具需求落在队列、状态、告警和人工接管。 [原帖](https://x.com/an_engineer_log/status/2052734571372851545)
- **@dotey：Boris Cherny 描述手机上常驻数百个 Claude Agent** 帖子转述 Anthropic 工程负责人称 Claude App 里常驻 5–10 个 session、几百个 agent，夜里跑数千个深度任务；这把“移动端控制长跑 agent”讲成真实工作方式。 [原帖](https://x.com/dotey/status/2052172481650159690)
- **@dboskovic：把“软件即规格”推进到 AI 生成可用规格** 作者说如果软件本质是 spec，就该让 AI 生成不烂的规格；对 coding agent 来说，前置规格质量会直接影响代码生成、验收和返工成本。 [原帖](https://x.com/dboskovic/status/2052515615768813634)
- **@BTCqzy1：港大 Vibe-Trading 用多 Agent 自动化量化投研** 帖子称 Vibe-Trading 允许用户用自然语言表达交易想法，由 AI 多智能体完成数据、策略和回测流程；金融 agent 正从“问答”进入可执行研究流水线。 [原帖](https://x.com/BTCqzy1/status/2052585954452689318)
- **@0xcherry：Auto-Quant v0.4.1 更新，量化策略挖掘接入多种 coding agent** Auto-Quant 以脚手架分发，可用 Claude Code、Codex、Cursor、OpenCode 等自动化挖掘策略；它是“小型垂直 agent harness”在量化场景的样本。 [原帖](https://x.com/0xcherry/status/2052697786345467925)
- **@yanhua1010：Obsidian + CLI + Claude Code 被组合成个人知识库 Agent** 帖子把 Obsidian Web Clipper、Obsidian CLI 和 Claude Code 串起来，让模型直接接管 Markdown 仓库；个人知识管理的关键从收藏变成可被 agent 查询和改写。 [原帖](https://x.com/yanhua1010/status/2052720961531879779)
- **@ericzakariasson：多 Agent swarm 可视化展示 planners 与 verifiers 分工** 作者展示 agent swarm 如何调用多个 planner、verifier 和执行单元；对做多代理编排的人，重点是把内部角色、依赖和校验过程显式化。 [原帖](https://x.com/ericzakariasson/status/2052453150888755551)
- **@sanbuphy：Hands-On Modern RL 覆盖 LLM 后训练与 Agentic RL** 作者发布 RL 教程，从 CartPole+PPO 到 RLHF、DPO、GRPO、Agentic RL，强调代码先行；适合把 agent 行为优化和后训练概念补成可运行实验。 [原帖](https://x.com/sanbuphy/status/2052191088048558243)
- **@gengdaJ：Codex + Hyperframes + Remotion 做视频生产流水线** 作者用 Minimax 配音、yt-dlp、Hyperframes 和 Remotion 生成动画电影混剪；内容 agent 的价值不只是出脚本，而是把素材获取、剪辑和动画代码串成流程。 [原帖](https://x.com/gengdaJ/status/2052380430385471686)

## X 关注流

- **@OpenAI：把 CoT monitor 作为 Agent 对齐防线** OpenAI 称 chain-of-thought monitors 是防止 agent misalignment 的关键层，并会避免破坏可监控性的训练方式；做长跑 agent 的团队需要同时考虑能力、审计和隐藏推理可见性。 [原帖](https://x.com/OpenAI/status/2052845764507062349)
- **@AnthropicAI：发布 “Teaching Claude why” 研究** Anthropic 继续围绕 Claude 的内部理由与可解释性发研究；继昨日 NLA 后，焦点从“把激活翻译成文字”延伸到让模型更能说明为什么。 [原帖](https://x.com/AnthropicAI/status/2052808787514228772)
- **@bcherny / @ClaudeDevs：Claude Code 一周再修 60+ 个可靠性问题** Boris Cherny 转发称，上周 50+ 修复后本周又发 60+ 项，重点是 long-running 体验；这比单次版本号更能说明 Claude Code 正在补长跑稳定性债。 [原帖](https://x.com/bcherny/status/2052856586033664233)
- **@peterwildeford：Palo Alto Networks 称 Mythos 三周抵一年手工渗透分析** 帖子引用 PAN 测试：3 周模型辅助分析达到 1 年手工渗透分析量级；这是昨日 Mythos/Firefox 案例后的新外部安全用例，但仍需看误报和审查流程。 [原帖](https://x.com/peterwildeford/status/2052826481772855509)
- **@Google：AlphaEvolve 一周年，定位为 Gemini-powered coding agent** Google 回顾 AlphaEvolve 已被用于多个领域；这把 coding agent 从 IDE 编程工具扩到科研、优化和跨领域问题求解，但原帖只给方向，细节需看后续材料。 [原帖](https://x.com/Google/status/2052794893206962598)
- **@zachlloydtweets：尝试本地 subagent 编排工作流** Zach Lloyd 称正在做一种新 agent 编排方式：主 agent 先写 delegation plan，再在本地运行 subagents；重点是把多代理从聊天技巧做成可执行的本地调度流程。 [原帖](https://x.com/zachlloydtweets/status/2052845881314148860)
- **@thdxr：coding agent 的交互瓶颈仍是“开聊天再沟通”** thdxr 认为当前 coding agent 基本工作流仍是开一个 chat 再来回说明；这解释了为什么各家都在做更贴近项目状态、任务队列和上下文的入口。 [原帖](https://x.com/thdxr/status/2052848625684770938)
- **@trq212：用 Claude Code 写 HTML 取代 Markdown 工作笔记** Thariq 称自己几乎停止写 Markdown，改用 Claude Code 生成 HTML；对 agent 用户，HTML 正变成可交互、可视化、可直接交付的工作载体。 [原帖](https://x.com/trq212/status/2052811606032269638)
- **@garrytan：GBrain 目标是开源 Agent 记忆层** Garry Tan 称正把 GBrain 做成“最好的开源 agent memory option”；结合今日 Mercury 对上下文浪费的提醒，记忆层竞争点会落在去重、漂移控制和可审计存取。 [原帖](https://x.com/garrytan/status/2052836113354756513) / [相关](https://x.com/GithubProjects/status/2052803375046230358)
- **@godofprompt：DeepSeek V4 被称可原生接入 Claude Code** 帖子称 DeepSeek V4 now speaks Claude Code natively，并用 $0.14/M tokens 对比 Claude Opus 4.7 的 $5/M；如果可用，第三方模型接入会继续压低 Claude Code 工作流成本。 [原帖](https://x.com/godofprompt/status/2052798956699017621)

## Reddit 社区

- **【工作流复盘】Claude Code 6 个月日用帖把“少量逐步执行”推到核心位置** 1005 分讨论建议复杂任务先 plan、每次只让 agent 做第一步、用 preview 和 `/simplify` 控制过度设计，并把 session retro 保存成项目知识。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sn27yu/claude_code_workflow_tips_after_6_months_of_daily/)
- **【技能沉淀】同一作者的 cheat sheet 继续强调把重复流程写成 skills** 1002 分后续帖把最佳实践扩到 skills、清晰描述触发条件和日常复用；相比昨天的“上下文纪律”，这里更像个人工程规范包的落地清单。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sv852q/claude_code_cheat_sheet_after_6_months_of_daily/)
- **【事故警示】Cursor/Claude 删除数据库事件在社区引发“agent 权限边界”讨论** 960 分帖转述 AI coding agent 9 秒删库且备份也受影响；对团队最直接的教训是生产数据库、备份和 destructive tool 不能放在同一可写权限里。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sxe7cf/claudepowered_ai_coding_agent_deletes_entire/)
- **【研究 Harness】HyperResearch 把 Claude Code 包成 16 步 deep research 流程** 作者称 skill harness 会在每次搜索中建立可持久化知识库，并用 Claude Code 订阅替代 OpenAI/Gemini Pro；适合观察“代码代理 CLI”被改造成研究代理的路线。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sz9ib0/converting_claude_code_into_the_most_intelligent/)
- **【成本失控】小任务跑到 12.8M input tokens、$40.78 的帖子集中追问上下文增长** 178 分讨论把问题落在会话不清理、仓库上下文过大和任务边界不清；这是昨天“省 token harness”之后的反面案例。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sztmrq/spent_40_on_a_single_claude_code_session_for_a/)
- **【能力自限】用户抱怨 Claude Code 会用“开发者要几周”当理由选择 quick fix** 81 分帖的争议点不是模型不会写代码，而是 agent 对自身能力、任务规模和方案深度的估计偏保守；长任务提示需要显式给预算、验收标准和允许探索范围。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1t77r81/when_using_claude_code_for_agentbased_coding_ive/)
- **【OpenClaw 反思】LocalLLaMA 热帖认为 OpenClaw/克隆品对熟练 CLI 用户价值有限** 625 分、264 评论把分歧说清：新手看到“发消息让 AI 操作电脑”很震撼，熟练用户则担心它比 Claude Code、Codex、n8n/Make 更混乱、更不安全。 [Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1srkah3/unpopular_opinion_openclaw_and_all_its_clones_are/)

## Hacker News 热榜

- **AI 正在压缩漏洞披露与补丁窗口** “AI is breaking two vulnerability cultures”在 HN 有 144 分、62 评论；讨论认为公开补丁 diff 已会被 LLM 快速转成漏洞判断和 exploit 指引，协调披露、运维补丁节奏和开源透明度需要重新校准。 [Hacker News](https://news.ycombinator.com/item?id=48066524)
- **reCAPTCHA/硬件证明争议延续到去 Google Android 用户** #1 热帖 194 分、57 评论；评论把新版 reCAPTCHA 理解为 remote attestation，担心无 Google Play、root/旧设备和 Web agent/自动化测试会被拦在服务外，还可能让账号活动被设备证明关联。 [Hacker News](https://news.ycombinator.com/item?id=48067119)
- **io_uring ZCRX LPE 讨论聚焦“漏洞是否被标题放大”** 这篇 Linux 提权分析有 61 分、34 评论；热评指出问题核心是 freelist 边界检查，但也质疑利用链需要 CAP_NET_ADMIN/CAP_SYS_ADMIN、且可能已在 stable 修复，适合安全团队核对真实暴露面。 [Hacker News](https://news.ycombinator.com/item?id=48067734)
- **CVE 修复里的非确定性让 SBOM/复现环境再次被提起** “Non-determinism is an issue with patching CVEs”评论少但指向明确：2026 CVE 数量曲线被认为明显变陡，读者同时提醒文章有销售味；对 agent 自动修补流程，关键是能否复现依赖和构建状态。 [Hacker News](https://news.ycombinator.com/item?id=48068947)

## Hacker News 搜索

- **Rubberduck：把 coding agent 前置成“设计对话→计划→容器执行”** 作者反对 agent 太快给完整方案，要求人在设计阶段做关键决策；执行阶段用用户提供的 dev image、测试/lint/format gate 验收后再提交 PR。 [Hacker News](https://news.ycombinator.com/item?id=48065297)
- **Git for AI Agents：讨论焦点是 prompt 级回滚，而不是再造 Git** re_gent 支持 Claude Code，想回答“agent 为什么删了这个目录、哪轮 prompt 改坏了”；评论认为价值在 commit 之间追踪/撤销 agent 步骤，也有人主张用 git、jj、hooks 已足够。 [Hacker News](https://news.ycombinator.com/item?id=48063548)
- **agentctl：本地控制平面拦截高风险 agent 动作** Go 工具在 Claude Code/Codex MCP 客户端前面管安装包、shell、密钥、写文件和外联；亮点是先宽松运行一周，再用 jsonl trace 回放收紧策略。 [Hacker News](https://news.ycombinator.com/item?id=48057567)
- **多步 agent prompt injection：评论把防护成本落到延迟** 相关文章讨论 multi-step workflow 防注入，HN 评论追问 Omega Walls 这类路由/隔离层会增加多少延迟；有人提到给聊天产品加 router LLM 曾带来约 6000ms 延迟。 [Hacker News](https://news.ycombinator.com/item?id=48063644)

## Claude Code

- **v2.1.136：MCP 与登录凭据竞态集中修复** `.mcp.json`、插件和 claude.ai connectors 里的 MCP server 不应再在 `/clear` 后从 VS Code、JetBrains、Agent SDK 里消失；并修复 OAuth token 并发刷新导致登录循环或多个远程 MCP 每日重登。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.136)
- **v2.1.136：Plan mode、恢复和插件运行坑补齐** 修复 `--resume`/`--continue` 在项目路径含下划线时找不到会话、plan mode 被 `Edit(...)` allow rule 绕过，以及插件 `Stop`/`UserPromptSubmit` hooks 因缓存清理删除运行中版本而失败。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.136)
- **v2.1.136：终端与文件选择器修了多处日常问题** WSL2 可用 PowerShell fallback 粘贴 Windows 剪贴板图片；`@` 文件选择器修复新建文件和 100+ 文件目录匹配，MCP tool results 内容块不可见、长粘贴被截断后静默丢失也已修复。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.136)
- **v2.1.133：worktree 默认基线变回远端默认分支** 新增 `worktree.baseRef`，`fresh` 会让 `--worktree`、`EnterWorktree` 和 agent-isolation worktree 从 `origin/<default>` 分支；若要保留本地未推提交，应设为 `"head"`。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.133)
- **v2.1.133：Hooks、企业策略和远程控制补可观测性** Hooks 现在拿到 `effort.level` 与 `$CLAUDE_EFFORT`，管理员可用 `parentSettingsBehavior` 控制 SDK managedSettings 合并；同时修复远程 stop/interrupt 不能像本地 Esc 一样取消 CLI 会话。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.133)
- **v2.1.133：并发会话与代理环境修复** 修复并行会话因 refresh-token race 全部 401、MCP OAuth 不完整遵守代理/mTLS、subagents 不能通过 Skill tool 发现项目/用户/插件 skills；Linux/WSL 还可配置自定义 `bubblewrap` 与 `socat` 路径。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.133)

## Codex

- **0.130.0-alpha.7 接上 alpha 线，发布资产继续覆盖 CLI、app-server、npm 与 Windows sandbox** 相比昨天的 0.130.0-alpha.1，今日 raw 已到 alpha.5/alpha.7；追预发布的团队应按 alpha.7 重新确认平台包和安装脚本。 [Release](https://github.com/openai/codex/releases/tag/rust-v0.130.0-alpha.7)
- **桌面版 attestation 接入 app-server 请求链路** `codex-rs` / app-server 现在可向已连接桌面 app 请求 DeviceCheck attestation，并把结果作为 `x-oai-attestation` 附到 scoped ChatGPT Codex 请求；桌面集成与服务端鉴权边界更清晰。 [PR](https://github.com/openai/codex/pull/20619)
- **`apply_patch` 只保留 freeform/custom 工具形态** function-style `apply_patch`、JSON spec 与 handler 被删除，模型元数据路径保留 `apply_patch_tool_type = freeform`；自定义模型、Bedrock catalog 或测试夹具需迁到 freeform 调用。 [PR](https://github.com/openai/codex/pull/21651)
- **工具发现改用 connector directory 缓存，减少首轮冷启动阻塞** `tool_suggest` 构建 discoverable tools 时只读缓存，并把目录元数据写入 `~/.codex/cache/codex_app_directory/<hash>.json`；冷缓存网络请求不再挡住 live MCP 工具加载。 [PR](https://github.com/openai/codex/pull/21497)
- **接受代码行开始上报哈希化 fingerprint 分析事件** Codex 会从最终 turn diff 解析 accepted/effective added lines，上传 repo、路径和规范化行内容的哈希，不含原始代码；团队可关注隐私口径与遥测开关。 [PR](https://github.com/openai/codex/pull/21601)
- **Python runtime wheel 发布流程先落地又回滚** #21784 曾计划把 Linux `bwrap`、Windows sandbox helpers 打进 `openai-codex-cli-bin` 平台 wheel 并发 PyPI，但随后 #21810 回滚；依赖 Python wheel 分发的自动化暂不应假设该资产已稳定。 [PR 21784](https://github.com/openai/codex/pull/21784) / [PR 21810](https://github.com/openai/codex/pull/21810)

## OpenClaw
- 无

## GitHub AI 项目

- **agentctl：给 coding agent 加本地风险闸门** `chocks/agentctl` 是 Go 写的小工具，拦在 agent 与包安装、Shell、密钥访问、文件写入、外部 API 调用之间；每次决策写入 JSONL，可用旧会话回放收紧策略，已支持 Claude Code 和 MCP/Codex 客户端。 [GitHub](https://github.com/chocks/agentctl) / [HN](https://news.ycombinator.com/item?id=48057567)
- **Maestro v1.6.1：同一套多 Agent 编排跑进 Codex、Claude Code 和 Gemini CLI** `josstei/maestro-orchestrate` 新增 OpenAI Codex 原生运行时，22 个 agents、19 个 skills 和 MCP 入口共享 canonical `src/`，减少多运行时插件分叉漂移。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1shmul3/maestro_v161_multiagent_orchestration_now_runs_on/)
- **9router：把多个免费/第三方模型源接到主流 coding agent** `decolua/9router` 本周 Trending，描述称可连接 Claude Code、Codex、Cursor、Cline、Copilot、Antigravity 到 40+ Claude/GPT/Gemini provider，并支持自动 fallback；适合评估多供应商路由的成本与稳定性风险。 [GitHub](https://github.com/decolua/9router)
- **Browserbase skills：给 Claude Agent SDK 配浏览器工具** `browserbase/skills` 本周 Trending，预览写明是 “Claude Agent SDK with a web browsing tool”；对需要真实网页操作的 agent，重点是把浏览器能力封成可复用 skill，而不是临时脚本。 [GitHub](https://github.com/browserbase/skills)
- **Auto-Quant v0.4.1：用 coding agent 挖量化策略的脚手架** @0xcherry 称 Auto-Quant 更新到 v0.4.1，是用 LLM 自动化挖掘量化策略的最小 demo，可配 Claude Code、Codex、Cursor、OpenCode 等；更像“领域实验模板”，不是通用 agent 平台。 [X](https://x.com/0xcherry/status/2052697786345467925)

## GitHub 趋势项目

- **skills** `browserbase/skills` 本周进入 Trending，定位是“带网页浏览工具的 Claude Agent SDK”。对需要真实网页登录、页面操作和浏览器验证的 agent，这是把 Browserbase 能力封装进 Claude 工作流的样本。 [GitHub](https://github.com/browserbase/skills)
- **9router** `decolua/9router` 面向 Claude Code、Codex、Cursor、Cline、Copilot 等 AI coding 工具，宣称可接入 40+ provider，并提供自动 fallback 与 token 压缩。对多模型路由用户，重点是成本、限额与可靠性被放到 coding-agent 中间层处理。 [GitHub](https://github.com/decolua/9router)
- **warp** `warpdotdev/warp` 以“从终端生长出的 agentic development environment”进入 Trending。它代表终端产品继续把命令行、上下文和 agent 执行合并成开发入口，适合观察 IDE 外的 agent 工作台形态。 [GitHub](https://github.com/warpdotdev/warp)
- **dexter** `virattt/dexter` 是 autonomous deep financial research agent。金融研究团队可用它观察研究任务如何拆成数据收集、推理和报告生成，而不是只把 LLM 当聊天式分析助手。 [GitHub](https://github.com/virattt/dexter)

## Product Hunt 新品

- **APIEval-20** 是面向“会测试 API 的 AI agents”的开放 benchmark；做 API 自动化、工具调用和回归评测的团队，可用它观察 agent 是否真会构造请求、验证响应，而不是只写测试样板。 [Product Hunt](https://www.producthunt.com/products/kushoai?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Tracea** 把自己定位成 AI agents 的 Datadog，覆盖 traces、RCA 和 team memory；长跑 agent 出错时，重点从“看最终回复”转向能追踪调用链、定位根因并沉淀团队记忆。 [Product Hunt](https://www.producthunt.com/products/tracea?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **KodHau** 主打把团队决策交给 AI，减少 agent 把生产环境改坏；对 coding-agent 落地，核心是把架构约束、历史决定和禁区前置到上下文，而不是事后靠 code review 补救。 [Product Hunt](https://www.producthunt.com/products/kodhau-senior-context-for-ai-agents?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场

- **5 月最佳 AI 模型市场成交放大，Anthropic 仍领先** “5 月底最佳 AI 模型”给 Anthropic 76.5%、Google 19.5%、OpenAI 3.1%，24h 成交约 40.96 万；相比昨天，Anthropic 回升、Google 从 22.5%回落。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may)
- **5 月最佳 Coding AI 几乎押定 Anthropic** “5 月底最佳 Coding AI model”给 Anthropic 94.5%、OpenAI 2.1%、Google 1.1%，24h 成交约 1542；相比前两天 94.0%继续小升，但短线成交仍远小于通用模型市场。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may)
- **6 月最佳 AI 模型预期里 Google 份额继续高于 5 月** “6 月底最佳 AI 模型”给 Anthropic 64.1%、Google 28.0%、OpenAI 6.5%，24h 成交约 1.80 万；Google 比昨天 27.5%略升，仍是中期追赶者。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)
- **FrontierMath 极端突破押注升到 23%** 2026 年前任一 AI 模型 FrontierMath 过 90% 的 Yes 为 23.0%，24h 成交约 2400；相比昨天 16.5%明显回升，但市场主概率仍是 No 77.0%。 [Polymarket](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027)

## 来源
### 天气
- https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-09&end_date=2026-05-09
- https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-09&end_date=2026-05-09
### X 推荐流
- https://x.com/0xLogicrw/status/2052701677615218717
- https://x.com/an_engineer_log/status/2052734571372851545
- https://x.com/dotey/status/2052172481650159690
- https://x.com/dboskovic/status/2052515615768813634
- https://x.com/BTCqzy1/status/2052585954452689318
- https://x.com/0xcherry/status/2052697786345467925
- https://x.com/yanhua1010/status/2052720961531879779
- https://x.com/ericzakariasson/status/2052453150888755551
- https://x.com/sanbuphy/status/2052191088048558243
- https://x.com/gengdaJ/status/2052380430385471686
### X 关注流
- https://x.com/OpenAI/status/2052845764507062349
- https://x.com/AnthropicAI/status/2052808787514228772
- https://x.com/bcherny/status/2052856586033664233
- https://x.com/peterwildeford/status/2052826481772855509
- https://x.com/Google/status/2052794893206962598
- https://x.com/zachlloydtweets/status/2052845881314148860
- https://x.com/thdxr/status/2052848625684770938
- https://x.com/trq212/status/2052811606032269638
- https://x.com/garrytan/status/2052836113354756513
- https://x.com/GithubProjects/status/2052803375046230358
- https://x.com/godofprompt/status/2052798956699017621
### Reddit 社区
- https://www.reddit.com/r/ClaudeAI/comments/1sn27yu/claude_code_workflow_tips_after_6_months_of_daily/
- https://www.reddit.com/r/ClaudeAI/comments/1sv852q/claude_code_cheat_sheet_after_6_months_of_daily/
- https://www.reddit.com/r/ClaudeAI/comments/1sxe7cf/claudepowered_ai_coding_agent_deletes_entire/
- https://www.reddit.com/r/ClaudeAI/comments/1sz9ib0/converting_claude_code_into_the_most_intelligent/
- https://www.reddit.com/r/ClaudeAI/comments/1sztmrq/spent_40_on_a_single_claude_code_session_for_a/
- https://www.reddit.com/r/ClaudeAI/comments/1t77r81/when_using_claude_code_for_agentbased_coding_ive/
- https://www.reddit.com/r/LocalLLaMA/comments/1srkah3/unpopular_opinion_openclaw_and_all_its_clones_are/
### Hacker News 热榜
- https://news.ycombinator.com/item?id=48066524
- https://news.ycombinator.com/item?id=48067119
- https://news.ycombinator.com/item?id=48067734
- https://news.ycombinator.com/item?id=48068947
### Hacker News 搜索
- https://news.ycombinator.com/item?id=48065297
- https://news.ycombinator.com/item?id=48063548
- https://news.ycombinator.com/item?id=48057567
- https://news.ycombinator.com/item?id=48063644
### Claude Code
- https://github.com/anthropics/claude-code/releases/tag/v2.1.136
- https://github.com/anthropics/claude-code/releases/tag/v2.1.133
### Codex
- https://github.com/openai/codex/releases/tag/rust-v0.130.0-alpha.7
- https://github.com/openai/codex/pull/20619
- https://github.com/openai/codex/pull/21651
- https://github.com/openai/codex/pull/21497
- https://github.com/openai/codex/pull/21601
- https://github.com/openai/codex/pull/21784
- https://github.com/openai/codex/pull/21810
### GitHub AI 项目
- https://github.com/chocks/agentctl
- https://news.ycombinator.com/item?id=48057567
- https://www.reddit.com/r/ClaudeAI/comments/1shmul3/maestro_v161_multiagent_orchestration_now_runs_on/
- https://github.com/decolua/9router
- https://github.com/browserbase/skills
- https://x.com/0xcherry/status/2052697786345467925
### GitHub 趋势项目
- https://github.com/browserbase/skills
- https://github.com/decolua/9router
- https://github.com/warpdotdev/warp
- https://github.com/virattt/dexter
### Product Hunt 新品
- https://www.producthunt.com/products/kushoai?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
- https://www.producthunt.com/products/tracea?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
- https://www.producthunt.com/products/kodhau-senior-context-for-ai-agents?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
### Polymarket 市场
- https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may
- https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may
- https://polymarket.com/event/which-company-has-best-ai-model-end-of-june
- https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027
