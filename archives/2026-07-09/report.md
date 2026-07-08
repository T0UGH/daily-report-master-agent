# AI Agent 日报（2026-07-09）

## 天气

- **北京·海淀**：今日雷暴伴小冰雹，23.7–35.5°C；降水概率 56%、预计 4.4 mm，南风最高 19.9 km/h。相比昨日明显升温、雨量增加，午后注意防暑，雷雨或冰雹时段减少户外停留。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-09&end_date=2026-07-09)
- **上海·杨浦**：今日雷暴，26–28.5°C；降水概率 63%、预计 10 mm，东南风最高 13.3 km/h。较昨日降温但雨量显著增加，通勤带伞并预留路面湿滑、短时强降雨带来的延误。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-09&end_date=2026-07-09)

## X 推荐

- **OpenAI 发布 GPT-Live，把下一代 ChatGPT Voice 推向实时对话。** 官方称 GPT-Live 是面向自然人机交互的新一代语音模型，已开始在 ChatGPT 中 rollout；做语音 agent 的团队应重新评估延迟、打断和工具调用链路。  
  来源：https://x.com/OpenAI/status/2074907025537224840 · https://x.com/juberti/status/2074906710024892694

- **SpaceXAI 与 Cursor 推出面向 coding 和 agents 训练的 Grok 4.5。** 发布帖称它是首个专门为编码与 agent 场景训练的模型，Cursor 参与训练；OpenCode 也已在 Zen 中接入，SuperGrok 用户可直接试用。  
  来源：https://x.com/SpaceXAI/status/2074915721684086811 · https://x.com/cursor_ai/status/2074915744999969059 · https://x.com/opencode/status/2074949468093313500

- **Codex CLI 0.143.0 正式发布，远程插件默认开启。** 这版把 npm marketplace 插件源和可见性带到默认路径，并加入 macOS / Windows 系统代理支持；企业网络和插件治理需要同步检查。  
  来源：https://x.com/CodexReleases/status/2074668188651098181 · https://x.com/Codex_Changelog/status/2074669139042677008

- **Claude Code 2.1.205 发布，继续补 auto mode 和 CLI 行为。** 这版列出 23 项 CLI 变化，摘要提到新增自动模式规则以阻止篡改会话相关设置；昨天的 2.1.203 之后，Claude Code 仍在快速修 agent 运行边界。  
  来源：https://x.com/ClaudeCodeLog/status/2074971760315838689

- **Hermes Agent 推出云端版。** Nous 称用户选择模型和服务器规格后，两次点击、约 60 秒即可启动；这把 Hermes 从本地 agent 工具扩到托管运行环境，适合比较本地凭证、云端隔离和长任务成本。  
  来源：https://x.com/NousResearch/status/2074878754485043333

- **Google AI Studio Build 增加 GitHub 导入。** 官方展示“import from GitHub”即可把代码带入 AI Studio Build；前端原型和 repo 改造流程可少一步手动粘贴或重新上传。  
  来源：https://x.com/GoogleAIStudio/status/2074887756430426379

- **mattpocock/skills v1.1 发布，强化从构想到工单的 agent 流程。** 新版包含 `/wayfinder`、`/to-spec`、`/to-tickets` 等技能；相比单个提示词，它更像把需求澄清、规格化和拆票固化成 coding agent 工作流。  
  来源：https://x.com/mattpocockuk/status/2074860312423997800

- **Lilian Weng 发布 AI 自我改进的 harness engineering 文章。** 她把问题放在未来 AI 系统如何通过 harness、反馈和评估持续改进；做 agent 评测的人可把它当作从提示词转向系统工程的参考材料。  
  来源：https://x.com/lilianweng/status/2074372369213428144

- **TypeScript 7 正式发布。** 虽然不是 agent 专属更新，但 TS 是多数前端 coding agent 的默认目标语言；升级后需关注类型检查、构建链和工具插件兼容性。  
  来源：https://x.com/typescript/status/2074892178745327926

- **GPT-5.6 Sol 从传闻进入官方发布时间窗口。** Sam Altman 发帖称 Sol 将在周四发布，OpenAI 转发内容还提到 Terra、Luna；昨天只看到 Codex UI/flag 信号，今天应按即将公开上线准备基准和模型路由。  
  来源：https://x.com/sama/status/2074709023807664454 · https://x.com/Dimillian/status/2074714202413953041

## X 关注

- **Hermes Agent 开始提供云端部署入口。** Nous Research 称用户可选模型和服务器规格，两次点击、约 60 秒完成部署；对团队试用 agent，门槛从本机安装降到托管实例，但凭证和数据边界仍需单独审。来源：https://x.com/NousResearch/status/2074878754485043333

- **OpenAI 发布 GPT-Live，并把 Live 系列 API 预告给开发者。** OpenAI、Sam Altman 和 OpenAI Devs 都在推新一代语音模型，开发者可报名 GPT-Live-1 / mini API；语音 agent 的重点会从“能听能说”转向低延迟对话与工具调用编排。来源：https://x.com/OpenAI/status/2074907027378511884 · https://x.com/sama/status/2074909079450050629 · https://x.com/OpenAIDevs/status/2074915334377844896

- **OpenAI 审计 SWE-Bench Pro，认为它已不能可靠衡量前沿 coding 能力。** 这会影响模型发布时的 benchmark 叙事；团队选 coding agent 时，不应只看旧榜单分数，还要看任务分布、污染风险和真实仓库回归。来源：https://x.com/OpenAI/status/2074972179385720836

- **NotebookLM 出现 CLI 与 MCP Server 入口。** GithubProjects 转述称 NotebookLM 可从命令行和 AI agent 调用；如果证据源、笔记和音频摘要能进 MCP，研究型 agent 更容易把 NotebookLM 纳入自动化流水线。来源：https://x.com/GithubProjects/status/2074893787282002415

- **有人用 Codex mobile app 远程操作 Hetzner 服务器上的 coding agent。** Dimillian 转发的案例把移动端、远程 VPS 和 coding agent 连到一起；这是昨天“远程常驻 agent 环境”讨论的具体用法更新。来源：https://x.com/Dimillian/status/2074954033911988580

- **Cloudflare 开放“向 AI agents 收费访问 API / 数据 / 内容”的 waitlist。** alex_prompter 的解读是每次 agent 触碰资源都可计费；如果落地，agent 爬取、工具调用和数据授权会从 robots.txt 式声明走向交易层。来源：https://x.com/alex_prompter/status/2074898605597704278

- **LingBot-VLA 2.0 用大规模机器人数据清洗训练开源模型。** alex_prompter 提到 9 万小时真实机器人视频中约 4 万小时被剔除，留下 6 万小时训练 6B 模型，覆盖 20 种机器人配置；机器人 agent 的瓶颈仍是数据质量而不只是模型大小。来源：https://x.com/alex_prompter/status/2074935175096754519 · https://x.com/alex_prompter/status/2074935260677394521 · https://x.com/alex_prompter/status/2074935275244200036

- **Simon Willison 反思让 AI 写 commit message 的不适感。** 他称最近几乎都让 Claude 和 GLT-5.5 写提交说明，但“不太舒服”；这提醒团队把 agent 接入 git 流程时，commit message 仍是审计线索，不只是可自动生成的文本。来源：https://x.com/simonw/status/2074948137182257284

## Reddit 社区

- **有用户称 Claude Code 在关掉自动更新后仍被静默改动。** 该帖报告本地配置被插入 A/B 实验 token，请求带上 `x-cc-atis` 后 Opus 4.8 不再返回 thinking summaries；同时 `autoUpdates:false` 仍出现原生 updater 切换二进制。证据来自单个用户排障记录，团队应把 CLI 版本、配置 diff 和请求头纳入变更审计。来源：https://www.reddit.com/r/ClaudeAI/comments/1uqov49/anthropic_silently_enrolled_my_claude_code/

## Hacker News

- **OpenAI 讨论 SWE-Bench 等 coding evaluation 的噪声问题。** HN 评论抓住“不到 800 个任务也需要人工工程师逐项清理”这一点，认为 LLM 能辅助找问题，但专业工程师仍发现更多缺陷；做 agent 评测时，别把真实 issue 派生任务默认当金标准。 [HN](https://news.ycombinator.com/item?id=48837396) · [OpenAI](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)

- **Grok 4.5 发布讨论集中在 Cursor 数据和 agent 训练闭环。** 评论关注其 $2/$6 定价、接近 Opus 4.7 的基准说法，以及用真实开发者—agent 交互和分布式 agent 系统构造训练环境；重点是 IDE 使用数据可能成为模型差异来源。 [HN](https://news.ycombinator.com/item?id=48835111) · [xAI](https://x.ai/news/grok-4-5)

- **OpenAI GPT‑Live 引发“语音模型终于接近前沿，但仍缺工具”的争论。** 试用者称可边散步边做一小时项目头脑风暴，并能后台委派给 GPT-5.5；反方则指出语音模式仍不能用 connectors/tools，生产力链路会被迫中断。 [HN](https://news.ycombinator.com/item?id=48834405) · [OpenAI](https://openai.com/index/introducing-gpt-live/)

- **Microsoft Flint 把图表生成做成 agent 更容易输出的中间语言。** 作者称 LLM 生成低层 chart spec 容易失真，Flint 用语义类型和布局优化器补足视觉决策，并提供 MCP server；评论把它概括为“LLM 生成 IR，确定性编译器收尾”的模式。 [HN](https://news.ycombinator.com/item?id=48834924) · [Flint](https://microsoft.github.io/flint-chart/#/)

- **Mistral Robostral Navigate 被 HN 当成 embodied agent 的导航短板讨论。** 评论关心它是否支持无地图导航，以及个人/爱好者能否拿来接 OpenClaw、农场机器人等实验；这类模型的落地障碍不只在推理，还在授权、硬件和路径规划集成。 [HN](https://news.ycombinator.com/item?id=48832212) · [Mistral](https://mistral.ai/news/robostral-navigate/)

- **DocuBrowser 用本地小模型把杂乱文档夹变成可搜索知识库。** 作者称目标是处理 1.2 万个本地文件，支持 PII 过滤、重复删除、摘要、语义/关键词搜索且不联网；适合需要把私有资料交给 agent 前先做本地索引的人参考。 [HN](https://news.ycombinator.com/item?id=48837110) · [GitHub](https://github.com/linuxrebel/DocuBrowser)

## HN 搜索

- **Claude Design System Prompt 的讨论集中在“仿制 prompt 是否可信”。** 评论质疑仓库没有说明逆向过程，也缺少可运行 demo；另有用户分享 Claude Design 做 SVG 动画时，要先让模型定义几何算法，否则会乱猜位置。来源：[HN](https://news.ycombinator.com/item?id=48792399) / [GitHub](https://github.com/Trystan-SA/claude-design-system-prompt)
- **Dex 把 analytics agent 的成本控制写成 skills。** 它给 Claude Code 等 coding agent 加 `/dex:explore`、`/dex:transform`、`/dex:maintain`，用脚本约束 Snowflake/Databricks 查询和 dbt 转换；作者称 Claude Sonnet 5 在 ade-bench 上 76%，且比 Fable 5 便宜 2.5 倍。来源：[HN](https://news.ycombinator.com/item?id=48832208) / [GitHub](https://github.com/exmergo/dex)
- **FactIQ 给 Claude Code/Codex 提供投资研究数据插件。** 它把 SEC、宏观经济、贸易和美股基本面整理成 3 张同构表、20 个字段，减少 agent 把上下文花在清洗数据上；当前声称覆盖 2500 万+ series。来源：[HN](https://news.ycombinator.com/item?id=48826422) / [GitHub](https://github.com/defog-ai/factiq-plugin)
- **Cruxible 把 agent 记忆从 Markdown/wiki 推向“受治理的 truth layer”。** 它要求用显式 typed ontology 建模事实，确定性读写在 LLM 外执行，需判断的变更进入带 attribution receipt 的 review queue；适合需要可审计状态而非纯 RAG 记忆的团队。来源：[HN](https://news.ycombinator.com/item?id=48833404) / [GitHub](https://github.com/cruxible-ai/cruxible)
- **Ask HN 讨论 agent sandbox 缺什么，反馈落在网络、挂载和网关。** 发帖者想做 OpenCode SDK 沙箱平台，带 CLI、队列、数据/提示取回和类似 Tailscale Aperture 的访问控制；评论提到 Claude sandbox IP 被平台屏蔽、Docker 类方案资源重、目录挂载和防火墙能力还不够顺手。来源：[HN](https://news.ycombinator.com/item?id=48835097)

## Claude Code

- **Claude Code v2.1.205 加固 auto mode 和结构化输出。** 新版会阻止篡改 session transcript 文件，`rm -rf` 变量无法从上下文解析时会先询问；同时修复 `--json-schema` 在 schema 无效时悄悄退回非结构化输出、以及 `format` 关键字被拒的问题。来源：https://github.com/anthropics/claude-code/releases/tag/v2.1.205

- **v2.1.205 继续修后台 agent、PR 关联和远程状态。** `claude attach` 会等待 mid-upgrade restart 的后台 agent 恢复，超过 30K inline output 的 Bash 创建 PR 也能被 session-to-PR linking 识别；Web/移动 Remote Control 的任务状态会在成员变化时完整转发，减少“Running”陈旧状态。来源：https://github.com/anthropics/claude-code/releases/tag/v2.1.205

- **Windows 与插件用户需要关注 v2.1.205 的安全/稳定修复。** Windows worktree 删除在遇到 NTFS junction 或目录 symlink 时不再误删 worktree 外文件；插件 LSP 初始化失败也不会阻断另一个插件处理同一扩展名。来源：https://github.com/anthropics/claude-code/releases/tag/v2.1.205

- **Claude Code v2.1.204 修复 headless SessionStart hook 事件流。** 之前 hook events 不流式输出，可能让 remote workers 在 hook 期间被 idle-reap；跑无头远程 worker 或自动化启动钩子的团队应升级验证。来源：https://github.com/anthropics/claude-code/releases/tag/v2.1.204

## Codex

- **Responses WebSocket 现在会遵守系统代理。** #31622 先抽出 `codex-websocket-client`，#31441 再把 Responses API 接入同一套 HTTP 代理、自定义 CA 和 Happy Eyeballs 策略；启用 `features.respect_system_proxy` 时，不必为代理放弃低延迟 WebSocket。来源：https://github.com/openai/codex/pull/31622 · https://github.com/openai/codex/pull/31441

- **Windows Desktop 沙箱补上主运行时访问权限。** #31574 把 `%USERPROFILE%\.cache\codex-runtimes` 纳入 ACL 修复，沙箱用户可读/执行 bundled Python、Node 和 native tools，但不增加写权限；此前 elevated sandbox 命令可能因 `ACCESS_DENIED` 读不到运行时。来源：https://github.com/openai/codex/pull/31574

- **MCP 工具列表在一次 sampling request 内复用快照。** #31292 让 Apps World State 和 tool-router 共用 `StepContext` 的懒加载 MCP snapshot，避免 `list_all_tools()` 重走客户端、增加延迟，或在同一请求内看到不同工具状态。来源：https://github.com/openai/codex/pull/31292

- **命令执行和 hook prompt 继续迁到 canonical `TurnItem` 生命周期。** #31629 移除 core 里直接发 `ExecCommandBegin/End` 的最后路径，#31630 让 stop-hook prompt 走 `ItemStarted` / `ItemCompleted`；legacy replay 仍保留兼容 fanout。来源：https://github.com/openai/codex/pull/31629 · https://github.com/openai/codex/pull/31630

- **Windows CI 构建 I/O 改走 Dev Drive。** #31357 让 `setup-ci` 统一设置 `CI_BUILD_ROOT`、Cargo target、Bazel cache/output 和 temp 路径；冷缓存跟踪里 Bazel shard 的 `C:` 流量从约 85 GiB 降到 13–16 GiB，测试步从 16 分钟级降到 11–12 分钟级。来源：https://github.com/openai/codex/pull/31357

- **Bedrock 的 GPT-5.6 模型显示名变清楚。** #31636 把 Amazon Bedrock 三个变体从 `Sol`、`Terra`、`Luna` 改成 `GPT-5.6 Sol/Terra/Luna`；模型 ID、排序、优先级、reasoning 支持和默认选择不变。来源：https://github.com/openai/codex/pull/31636



## GitHub AI 项目

- [alibaba/page-agent](https://github.com/alibaba/page-agent)（25,193 stars）：阿里开源浏览器页面内 GUI agent，用自然语言控制网页界面；适合把表单、后台和业务页面自动化从截图点击升级到页面内执行。
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)（21,680 stars）：收集 345 个 Claude Code / Codex / Gemini CLI / Cursor 等可用的 skills、agents 和插件；团队可用它快速对照 skill 目录结构、命令和引用资料组织方式。
- [stablyai/orca](https://github.com/stablyai/orca)（14,143 stars）：Orca 把多路 coding agent 做成 ADE，可用自己的订阅在桌面和移动端调度 agent fleet；适合观察多 agent 工作台如何处理会话、任务和人工接管。
- [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire)（12,016 stars）：项目把 Claude Code / Codex 用到价值投资研究，内置巴菲特、芒格等方法论和多 agent 对抗分析；它是把 coding agent 套进专业研究流程的垂直样例。
- [facebook/astryx](https://github.com/facebook/astryx)（7,150 stars）：Meta 开源可定制、agent-ready 的设计系统；做前端 agent 或设计到代码工作流时，可参考组件约束如何提前暴露给自动化工具。
- [Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily)（21,599 stars）：本地优先 AI 会议助手，Rust 实现实时转写、说话人分离和 Ollama 总结；对不想把会议音频交给云端的团队，是可自托管的会议上下文入口。

## GitHub 趋势项目

- [alibaba/page-agent](https://github.com/alibaba/page-agent)（25,193 stars）：阿里开源 in-page GUI agent，用自然语言控制网页界面；做浏览器自动化或前端验收的团队，可把它作为页面内操作层参考。
- [stablyai/orca](https://github.com/stablyai/orca)（14,143 stars）：Orca 定位为并行 coding agents 的 ADE，可用自己的订阅调度多代理，并覆盖桌面和移动端；适合观察多 agent 工作台如何处理会话、状态和跨设备接力。
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)（21,680 stars）：仓库汇总 345 个 Claude Code / agent skills、30+ agents 和 70+ 自定义命令；想把团队流程沉淀成 skill 时，可参考其分类和脚本/引用文件组织。
- [bradautomates/claude-video](https://github.com/bradautomates/claude-video)（5,997 stars）：这个 Claude Code 扩展用 `/watch` 下载视频、抽帧、转写并交给 Claude；会议录屏、教程和 demo 可更容易进入 coding-agent 上下文。
- [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire)（12,016 stars）：项目把 Claude Code / Codex 用到价值投资研究，多 agent 并行分析巴菲特、芒格等方法论；它是垂直研究型 agent workflow 的中文样例。
- [Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily)（21,599 stars）：Meetily 是本地优先 AI 会议助手，提供 Parakeet/Whisper 实时转写、说话人分离和 Ollama 总结；重视隐私的团队可用它把会议上下文留在本机再交给 agent。

## Rize AI 工具榜

- #1 CodeWhale：开源、社区驱动的 agent harness；repo：https://github.com/Hmbown/CodeWhale，榜单页：https://rize.io/ai-tools。
- #2 loop-engineering：面向 AI coding agents 的 loop engineering 实践、starter 与 CLI 工具集，包含 loop-audit、loop-init、loop-cost；repo：https://github.com/cobusgreyling/loop-engineering，榜单页：https://rize.io/ai-tools。
- #3 garden-skills：ConardLi 的开源 Skills 集合，覆盖网页设计、知识检索、图像生成等能力；repo：https://github.com/ConardLi/garden-skills，榜单页：https://rize.io/ai-tools。
- #4 agents-cli：Google Cloud 上用于创建、评估和部署 AI agents 的 CLI 与 skills，目标是把任意 coding assistant 变成 agent 开发助手；repo：https://github.com/google/agents-cli，榜单页：https://rize.io/ai-tools。
- #5 graphify：面向 Claude Code、Codex、OpenCode、Cursor、Gemini CLI 等 AI coding assistant 的 skill，可把代码、SQL schema、脚本、文档、论文、图片或视频转成可查询知识图谱；repo：https://github.com/Graphify-Labs/graphify，榜单页：https://rize.io/ai-tools。
- #6 learn-harness-engineering：面向初学者的 harness engineering 0 到 1 教程；repo：https://github.com/walkinglabs/learn-harness-engineering，榜单页：https://rize.io/ai-tools。
- #7 claude-seo：Claude Code 的通用 SEO skill，包含 25 个 sub-skills 与 18 个 sub-agents，覆盖技术 SEO、E-E-A-T、schema、GEO/AEO、语义聚类、国际 SEO 和报表等场景；repo：https://github.com/AgriciDaniel/claude-seo，榜单页：https://rize.io/ai-tools。
- #8 agentmemory：面向 AI coding agents 的持久记忆项目，描述称基于真实世界 benchmark；repo：https://github.com/rohitg00/agentmemory，榜单页：https://rize.io/ai-tools。

## Product Hunt 新品

- **agents-cli**：Product Hunt 新上架的开发者工具，定位是“让 coding agent 用来交付 agent 的 CLI”；昨天 Rize 榜已出现同名项目，今天新增事实是 PH 产品页上线。来源：[Product Hunt](https://www.producthunt.com/products/agents-cli?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Compendium**：把团队、agents 和数据放到同一页的知识/协作工具；适合观察 agent 工作流里“共享上下文”和团队资料同步如何被产品化。来源：[Product Hunt](https://www.producthunt.com/products/compendium-2?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Knowledge Atlas by Fini**：自称“会自我改进的知识库”，切入客服/内部知识库质量维护；对知识库 agent，关注点是更新、纠错和资料漂移能否自动闭环。来源：[Product Hunt](https://www.producthunt.com/products/fini-2?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场

- 7 月底“最佳 AI 模型公司”主市场仍押 Anthropic：Anthropic 85.0%、Google 10.8%、OpenAI 4.2%，24h 成交约 17.79 万；相比昨日 Google 下降、OpenAI 回升，但头部判断基本没变。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-july-299
- “7 月底最佳 Coding AI 模型”继续几乎锁定 Anthropic：Anthropic 95.0%、OpenAI 4.0%、xAI 1.9%，24h 成交约 1332；相较昨日仍在 95% 附近，市场不押注短线反超。来源：https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-july
- “7 月底最佳 Math AI 模型”中 Anthropic 回落到 64.0%，Google 30.0%、OpenAI 7.9%，24h 成交约 1.63 万；相比昨日 71.5% 明显降温，数学榜预期重新给 Google 留出空间。来源：https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-july
- FrontierMath 90% 达标市场从昨日高位回落：2027 年前有模型达到 ≥90% 的 Yes 为 83.0%，30d 成交约 10.79 万、本月仍上涨 58.0%；这是市场预期，不代表基准已被攻破。来源：https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027
- 中国模型公司市场继续偏向阿里：7 月底 Alibaba 95.5%、DeepSeek 2.1%、Z.ai 1.6%，24h 成交约 1.17 万；相比昨日 95.4% 基本持平，短线反超预期很弱。来源：https://polymarket.com/event/best-chinese-ai-company-end-of-july
- 年底最佳 AI 模型公司市场仍更分散：Anthropic 62.5%、Google 15.0%、OpenAI 11.0%，流动性约 53.99 万；半年维度比 7 月底主市场给 Google/OpenAI 留出更多反超空间。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-2026
- “2026 年底是否有模型达到 1560 Coding Arena Score”当前主项为 51.5%，24h 成交约 772、30d 成交约 11.40 万；相比昨日 47.0% 上行，但原始分档标签不清，解读需先看市场规则。来源：https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-december-31
