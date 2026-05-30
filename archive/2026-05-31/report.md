# AI Agent 日报（2026-05-31）

## 天气

- **北京·海淀：阴，22.1°C–35.1°C。** 降水概率 2%、预计 0 mm，西南风最高 14.8 km/h；比昨天夜间低温明显抬升、最高温再高约 1°C，闷热感更强，出门重点防晒补水，基本不用带伞。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-31&end_date=2026-05-31)
- **上海·杨浦：多云间晴，17°C–29.2°C。** 降水概率 0%、预计 0 mm，东南风最高 13.2 km/h；比昨天最高温升约 1.7°C、云量减少，通勤无需雨具，早晚仍较凉、午后偏热。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-31&end_date=2026-05-31)

## X Feed

1. Salesforce 发布了“going agentic with Claude Code”的详细实践复盘，Boris Cherny 摘出的关键点是：一次迁移先由 Claude Code 生成设计文档、测试计划和分阶段实现，再让人类在中间节点审查。对企业采用 coding agent，这比“让 AI 写代码”更接近可复制流程：先固化计划、测试和回滚点，再放大自动化执行。  
   https://x.com/bcherny/status/2060390852619272526

2. Cursor 官方推出 Auto-review mode：agent 可以在更少审批弹窗下运行工具调用，同时宣称有更安全的执行边界。它把前两天 HN 讨论的“权限疲劳”落到了 IDE 产品形态里：真正的竞争点不是完全免确认，而是哪些操作能自动、哪些必须阻断。  
   https://x.com/cursor_ai/status/2060406013098897765

3. Nous Research 宣布 Step 3.7 Flash 在 Nous Portal 免费 30 天，并称它是面向 agent efficiency 的 MoE 视觉语言模型。对本地/多模型 agent 用户，这类小而快的 VLM 更适合做截图理解、UI 状态识别和低成本工具前置判断，而不是直接替代最强推理模型。  
   https://x.com/NousResearch/status/2060722721516872020

4. Teknium 提到 Hermes Agent 的 read file 操作平均可节省 14% input tokens，且已上线。这个更新很小但方向重要：agent 成本优化不只靠换便宜模型，也来自文件读取、裁剪和上下文注入这些基础工具层的持续瘦身。  
   https://x.com/Teknium/status/2060839436330655775

5. 有开发者展示 Hermes Agent 的开源聊天 UI，称官方 dashboard 更偏管理控制台，而这个 UI 补的是日常对话入口。结合近几天 Hermes v0.15、橙皮书和 masterclass 的传播，Hermes 正从“可编排执行器”扩到更完整的用户界面和学习生态。  
   https://x.com/_avichawla/status/2060667121399701724

6. Google Gemma 团队展示 Gemma 4 可在 Google AI Edge Gallery 里 100% 本地运行成“口袋里的 local agent”。这条不是 coding-agent 发布，但说明端侧 agent 继续往手机侧下沉：隐私、离线和低延迟会成为与云端大模型互补的执行层。  
   https://x.com/googlegemma/status/2060411370139795877

7. Ollama 转发 Stanford HazyResearch/Scaling Intelligence 的 OpenJarvis：一个可用 Ollama 运行的 local-first personal AI。它和 Gemma 本地 agent 信号相互印证：个人 agent 的下一条分支是把记忆、工具和推理尽量放在用户设备/本地模型栈里。  
   https://x.com/ollama/status/2060428074102206496

8. NVIDIA AI 发布面向视频搜索的新 agent skills 和模块化架构，目标是让数小时视频可被 agent 检索。对知识工作 agent，这把“文档/RAG”扩到长视频语料；真正价值在于能否把片段定位、引用和后续行动接进工作流，而不只是生成摘要。  
   https://x.com/NVIDIAAI/status/2060481312511623513

9. 有开发者介绍 EverOS：面向 AI Agent 的“长程记忆操作系统”，强调把会话、用户偏好、项目资料和全局知识从短上下文里抽出来长期管理。产品细节仍有限，但它代表一个清晰需求：agent 记忆需要成为可操作、可迁移、可审计的系统层。  
   https://x.com/elliotchen100/status/2060613843622174800

10. Omar Sarwar 提到 HTML Artifacts 正成为他使用 AI agents 的核心部件，因为长程 agent session 需要一种可视化、可交互的中间产物。相比只输出 Markdown，Artifacts 更适合作为 agent 与人共同检查状态、方案和结果的工作台。  
   https://x.com/omarsar0/status/2060751120587497720

**今日取舍：** 已读取 100 条 x-feed raw、context 和近两日报告，仅把历史报告用于去重。昨天/前天已充分覆盖 Opus 4.8、Claude Code dynamic workflows、Codex Windows/后台 agent、OpenAIDevs QOL、Claude prompt/cache workshop、Codex 插件/第三方接入和前端设计 skills，因此今天优先保留企业 Claude Code 实践、Cursor 权限/审批模式、本地/端侧 agent、Hermes 工具层优化、长程记忆/Artifacts、视频检索 agent 等新增信号；剔除了纯转发、只有 t.co、泛 AI 课程/流量帖、生活/教育/投资内容，以及和近日报告重复但无新事实的 Claude/Codex 话题。

## X 关注

- **Codex Chronicle 被用户点名为“长期屏幕上下文”能力：开启后会持续截图屏幕，让 Codex 拥有更完整的个人工作流背景。** 这不是单次截图问答，而是把日常操作痕迹变成 agent 可用上下文；收益是减少反复解释项目和环境，风险是隐私、存储和可审计边界必须先想清楚。https://x.com/lxfater/status/2060657201958543637

- **Codex Mobile 的主机插件与相机输入开始被开发者当作远程 agent 入口使用。** Dimillian 提到移动端可访问 host plugins，并能把相机等输入发给 Codex；结合近期 Windows Computer Use，这条线索说明 coding agent 正从桌面 IDE 扩到“手机触发、远程主机执行、视觉输入补上下文”的形态。https://x.com/Dimillian/status/2060746623223742804

- **Codex desktop 新增“选中文本后直接发送给 Codex”的细节受到关注。** 这类小交互会降低从代码、日志、网页或文档中摘取上下文的摩擦；对 agent 工作流来说，入口越贴近日常阅读/调试现场，越少需要手动复制大段背景。https://x.com/Dimillian/status/2060745487112708389

- **Dan Shipper 晒出 Codex 重度使用数据：38B tokens、最长任务 56 小时、连续 41 天使用。** 这不是产品发布，但给出一个 power-user 量级：真正把 Codex 当长期 agent 跑时，任务时长、token 账单、会话恢复和历史管理会成为一等工程问题。https://x.com/danshipper/status/2060771279280513362

- **“agent-native idea farm”把 Codex 接到 Slack、本地 workspace 和写作材料，用来捕捉实时写作想法。** 这是昨天“pulse threads”晨间巡检的后续形态：agent 不只定时汇总状态，也可以持续监听创作素材并整理成可用选题；关键仍是来源筛选和避免把噪音写进知识库。https://x.com/danshipper/status/2060766875319955742

- **OpenAI Devs 公布 Voice Hack Night 决赛项目，主题是 6 小时内做 realtime voice agents 的真实应用。** 原帖被截断，项目细节不足以逐一评价，但信号明确：OpenAI 正把实时语音 agent 从 demo 推向 hackathon 式应用验证；适合关注语音客服、现场助手和低延迟工具调用的人继续跟进。https://x.com/OpenAIDevs/status/2060768476386689253

- **Pluvio9yte 分享 Claude + OKX Agent Trade Kit 的实验：自动监控 xAI 新闻，并直接在 AI 估值事件上预测下单。** 这条的价值不在交易建议，而在展示 agent 从信息监控、事件判断到外部执行的闭环；金融场景尤其需要权限分层、下单限额、日志和人工确认。https://x.com/Pluvio9yte/status/2060757090617131164

- **有用户把 Claude Opus 4.8 放进“订单对账”业务测试，结论是它更愿意把活做完整。** 测试设定是不联网、不写代码，只给订单、付款、退款三组数据按规则核对；相比抽象 benchmark，这类业务对账更接近企业 agent 的真实可靠性评估，但仍应要求公开样例和可复现实验。https://x.com/AI_jacksaku/status/2060190627019833816

- **aiedge_ 提到 Claude Devs 新插件可审计提示词，聚焦“为什么 agent 没按预期执行”。** 原帖内容被截断，细节不足以当教程，但方向重要：随着 Skills/Plugins 增多，团队需要的不只是更多提示词，而是能检查提示、约束、上下文和工具权限是否互相冲突的审计层。https://x.com/aiedge_/status/2060821102025416881

- **garrytan 转发 Hermes Agent self-learning loop：有用 workflow 沉淀成 skill，经验进入 Gbra。** 这延续近几天 Hermes v0.15 和社区教程主线，今天的增量是把“自学习”拆成可操作循环：从成功流程抽象为 skill，再把运行经验写回长期记忆/知识层。https://x.com/garrytan/status/2060806000530333760

**今日取舍：** 已阅读 2026-05-30、2026-05-29 报告作去重参考。昨天已充分覆盖 Codex Windows Computer Use、background agents、dynamic workflows、mid-conversation system messages、Pullfrog、Mercury Skills、依赖升级自动化等，因此今天剔除 op7418/jungeAGI 的 Windows Computer Use 重复帖、GithubProjects 的低信息 Grok/晒 GitHub 帖，以及生活、政治、酒店、投资、空链接、纯转发和只有情绪表达的内容。保留的重点是 Codex 长期上下文/移动端/入口交互、真实使用量级、语音/交易/写作 agent 闭环、Opus 4.8 业务测试，以及 Hermes/Claude 插件治理这类有新增工作流含义的信号。

## Reddit 社区

- 今日 Reddit 原始语料不可用：`reddit-watch` raw corpus 标记为 `missing`，raw 文件数为 0；采集日志显示 4 个 Reddit search.json 查询均返回 HTTP 403（Claude Code workflows、Codex agent、OpenClaw、AI coding agents），因此无法基于社区讨论做可靠筛选。本栏不使用 `selected_items.json`、外部 fallback 或近日报告补写，避免把去重参考当作今日证据。

**今日取舍：** 由于 Reddit 抓取被阻断且没有 raw 证据，本栏不选条目；仅阅读 2026-05-30、2026-05-29 报告作为去重参考，未复用其中 Reddit 内容。

## Hacker News 热榜

- **OpenRouter 完成 1.13 亿美元 B 轮融资，HN #1、307 分、131 评论；讨论焦点是多模型网关到底替用户解决了什么。** 评论区把价值落到低摩擦试模型、统一 API、billing caps 和模型流行度信号，也有人指出重度 agent 用 Claude Opus 这类高价模型时，5% surcharge 会很快变成成本问题。 [HN](https://news.ycombinator.com/item?id=48338660) / [OpenRouter](https://openrouter.ai/announcements/series-b)

- **“Domain expertise has always been the real moat”登上 HN #2，69 分、34 评论；它把 AI 编程讨论拉回领域知识。** 高赞评论用海上天气应用举例：模型会抽象系统，但真实用户知道数据怎么被使用；对 coding-agent 团队，这意味着需求访谈、领域校验和人工验收仍是产品质量核心。 [HN](https://news.ycombinator.com/item?id=48340411) / [文章](https://www.brethorsting.com/blog/2026/05/domain-expertise-has-always-been-the-real-moat/)

**今日取舍：** 保留与 AI/agent 基础设施成本、模型路由、以及 coding-agent 产品落地方法直接相关且评论区有实质讨论的条目；剔除 Zig ELF linker、Voxel Space、Jef Raskin、Twilight Princess decompilation、wolfCOSE、Joseon omens 和沙漠贝壳，因为它们虽有工程或社区趣味，但与 AI/coding-agent 工作流关联较弱。Accenture 收购 Ookla 的评论涉及“AI 冲击咨询、数据业务成为护城河”，但主要是电信数据与企业并购，缺少可落到 agent 实践的新增事实。

## Hacker News 搜索观察：agent 记忆、空间 IDE 和真实 App 生产样本

- **有人把 agent memory 从“检索问题”改写成“数据建模问题”，用知识图谱/ontology 总结了一年踩坑。** 关键经验包括不要先套 LangGraph/CrewAI 这类框架、先用 POLE+O 起步而不是预设完美 ontology、区分名称归一化与实体去重，并补上 reasoning memory 记录每次运行的策略/工具/成败；这比单纯扩大上下文或做语义搜索更接近长期 agent 的可维护记忆层。来源：[HN](https://news.ycombinator.com/item?id=48337689)

- **Jynx 把“Claude Code 做完整移动应用”给出了较完整生产样本：214k 行 Dart、23 个功能模块、Flutter + Firebase，上线 iOS/Android。** 作者列出 Claude Code/GLM、22 个 hooks、18 个 skills、13 个 instincts、rule files、custom subagents、slash commands、MCP servers/plugins、GitNexus 与 MemPalace；相比普通 vibe-coding 展示，这条更有价值的是把长期 agent 工程的脚手架和生产监控/安全栈一起暴露出来。来源：[HN](https://news.ycombinator.com/item?id=48336119) / [Jynx](https://jynx.app/)

- **HN 上出现“spatial IDE for agentic coding workflows”的观察帖，把终端、文件和多个 agent 放到画布式空间里管理。** 原帖列出 VoiceTree、AgentBase、Cated，评论补了 OpenCove；信号不是某个项目已成熟，而是 coding-agent 前端正在从 VS Code 侧栏/多终端，试探转向更适合并行任务、文件关系和 agent 状态可视化的空间工作区。来源：[HN](https://news.ycombinator.com/item?id=48336009)

**今日取舍：** 近两日报告已展开 Search Router、Claude Code AskUserQuestion、TheFoundry、dotpi、Cordium、TravElly、CodeWhale 等，今天不重复。保留 5 月 30 日新增且有具体 agent 工程含义的记忆层、生产 App 工程样本和空间 IDE 工作区信号；VT Code 只有标题和很少评论，Claude Design 文章 raw 只有标题，Dynamic Workflows 问答和前日 Claude Code 主栏重复，Zero Operators 证据仍过薄。

## Claude Code

- **Claude Code `v2.1.158` 把 Auto mode 扩到 Bedrock、Vertex 和 Foundry 上的 Opus 4.7 / Opus 4.8，需设置 `CLAUDE_CODE_ENABLE_AUTO_MODE=1` 开启。** 企业或私有云端点用户可以先在非生产任务里复测自动模式的模型/成本路由；昨天已写过 `v2.1.157` 的插件、agents 和 worktree 修复，今天不重复。 [v2.1.158](https://github.com/anthropics/claude-code/releases/tag/v2.1.158)

**今日取舍：** raw corpus 有 `v2.1.156`、`v2.1.157`、`v2.1.158` 和 CHANGELOG。`v2.1.156` 的 Opus 4.8 thinking blocks API error 修复、`v2.1.157` 的插件自动加载、`claude agents`、worktree、粘贴/权限等已在 2026-05-30 日报展开；今天仅保留 `v2.1.158` 对 Auto mode 云端点支持的新增事实。

## Codex

- **Codex CLI 补上 `codex archive <thread>` / `codex unarchive <thread>`，可按 UUID 或精确线程名归档、恢复保存线程。** 这些命令会复用既有 app-server `thread/archive` 与 `thread/unarchive` RPC，也支持 scoped remote flags；同时 `codex resume <thread id>` 与 `codex fork <thread id>` 现在会拒绝 archived session，并提示先运行 `codex unarchive <thread id>`。 [PR #25021](https://github.com/openai/codex/pull/25021)

- **Windows sandbox 现在可被 managed requirements 约束到 `elevated` 或 `unelevated` 实现。** 新增 `[windows].allowed_sandbox_implementations`，配置解析会把不被允许的选择回落到允许项；TUI 也会阻止用户继续使用被组织策略禁用的 unelevated fallback，或保存不符合要求的 sandbox mode。 [PR #23766](https://github.com/openai/codex/pull/23766)

- **`request_user_input` 增加实验开关，可用 `tools.experimental_request_user_input = false` 关闭。** 对需要严格无人值守、批处理或受管 agent 环境的集成方，这给“模型能否主动向用户提问”提供了显式配置边界，而不是只能靠提示词约束。 [PR #24541](https://github.com/openai/codex/pull/24541)

- **multi-agent v2 的后续任务工具表面从 `followup_task` 改名为 `assign_task`。** 核心测试和 spec-plan 期望已同步更新，同时 rollout-trace 分类保持对旧 `followup_task` 的向后兼容；依赖多代理工具名、trace 解析或评测脚本的用户需要同步新命名。 [PR #25267](https://github.com/openai/codex/pull/25267)

- **插件/连接器建议逻辑继续收紧：安装建议会按已安装 app 的 connector IDs 过滤，远程 connector 建议则改用当前 session 已加载插件的 app IDs。** 这让空白用户仍有 starter allowlist，但非 fallback 候选必须来自 `openai-curated` / `openai-bundled` 等可信 marketplace 并与已安装插件相关；同时避免另起 `PluginsManager` 导致远程插件声明的 Databricks 等 connector 丢失。 [PR #24996](https://github.com/openai/codex/pull/24996) / [PR #25172](https://github.com/openai/codex/pull/25172)

- **Amazon Bedrock API-key 路径修复 region 解析：显式配置优先，其次回落到 `AWS_REGION`，再到 `AWS_DEFAULT_REGION`。** 这修复了按文档只导出 `AWS_BEARER_TOKEN_BEDROCK` 与 `AWS_REGION` 仍报 missing-region 的问题；错误信息也会列出全部支持的 region 来源。 [PR #25171](https://github.com/openai/codex/pull/25171)

- **Bedrock GPT 模型目录现在会把 service tier 规范化为仅 `default`。** 因 Bedrock 当前只支持隐式 default tier，Codex 会从内置和自定义 Bedrock catalog 中剥离非 default tier 元数据，避免向用户展示或向服务发送不支持的 tier。 [PR #25318](https://github.com/openai/codex/pull/25318)

**今日取舍：** 近两日报告已写 `0.135.0` 正式版、`0.136.0-alpha.1` 资产、TUI `/archive` slash command、exec-server helper、Code Mode durable session、subagent lineage、PermissionProfile thread-store、web search model 字段和 Vim 修复，今天不重复；提交与 merged PR 重复时采用 PR 链接。`0.135.0-alpha.2`、`0.135.0`、`0.136.0-alpha.1` 均因已覆盖或无新增 release note 被去重；Bazel VSCode extension 推荐过小，未列入主条目。

## GitHub AI 项目

- **[vinhnx/VTCode](https://github.com/vinhnx/VTCode)（641 stars）是一个 Rust 写的开源终端 coding agent，强调 LLM-native code understanding、shell safety、多模型 provider failover 和高效上下文管理。** 今天以 Show HN 形式出现；相比又一个聊天壳，它的看点在于把终端执行安全、模型切换和代码理解层作为一体化 agent runner 来做。

- **[revfactory/harness](https://github.com/revfactory/harness)（4,225 stars）把“设计领域专用 agent team”做成 meta-skill：生成专门 agents，并生成这些 agents 使用的 skills。** 今天进入 weekly trending；对多代理开发者，它对应的是把团队编排、角色定义和 skill 生产标准化，而不是每个项目手写一套 subagent 说明。

- **[voicetreelab/voicetree](https://github.com/voicetreelab/voicetree)（856 stars）与 [DeadWaveWave/opencove](https://github.com/DeadWaveWave/opencove)（1,401 stars）一起出现在 HN 关于“spatial IDE for agentic coding workflows”的讨论里。** 这类项目把 Claude Code、Codex、terminal、任务和知识放到无限画布/图式工作区中；信号是多 agent/多终端工作流正在从线性聊天窗口转向可视化编排与状态管理。

**今日取舍：** 只保留 raw/cross-lane 证据中出现、GitHub API 校验 stars ≥100、且近两日报告未实质展开的 AI/coding-agent 项目。`affaan-m/ECC`/`affaan-m/everything-claude-code`、`microsoft/agent-governance-toolkit`、`anthropics/claude-plugins-official`、`Leonxlnx/taste-skill` 等近两日已写，今天不重复；`oh-my-pi`、`codegraph`、`Understand-Anything`、`cursor/plugins`、`Anthropic-Cybersecurity-Skills`、`herdr`、`claude-code-harness` 等已有覆盖或去重说明且无新增事实；`TheFoundry`、`dotpi`、`zero-operators`、`claude-handoff-revive`、`simple-search` 等虽相关但 GitHub API 校验未达 100 stars；视频生成、语音平台、通用学习资料和非 agent 工程项目未纳入本栏。

## GitHub 趋势项目

- **[revfactory/harness](https://github.com/revfactory/harness)（4,225 stars）把“搭 agent 团队”包装成 meta-skill：先设计领域专用 agent team，再定义专门代理，并生成它们要用的 skills。** 相比只给一个通用 coding agent 下任务，它对应的是把角色、交接和技能资产生成流程标准化；适合关注多代理工作流如何从临时提示变成可复用团队模板的读者。

**今日取舍：** 硬门槛为 GitHub API 校验 stars ≥ 100，并只选与 AI/coding-agent 工作流有明确关系、且近两日报告未实质展开的仓库。`affaan-m/ECC` 昨天已写；`microsoft/agent-governance-toolkit`、`anthropics/claude-plugins-official`、`Leonxlnx/taste-skill` 等在 2026-05-29/30 已实质覆盖或无新增事实；`codegraph`、`Understand-Anything`、`oh-my-pi`、`cursor/plugins`、`Anthropic-Cybersecurity-Skills`、`stop-slop` 等近日报告已去重说明；`MoneyPrinterTurbo` 偏短视频，`dograh` 偏语音平台，`markitdown` 偏通用文档转换，`ai-engineering-from-scratch` 偏学习资料，`heretic` 与本栏 coding-agent 工程工作流关联不够具体，因此未纳入。

## Rize AI 工具榜

- **#10 [holaOS](https://github.com/holaboss-ai/holaOS)**：把重复工作转成持续运行的 AI work-streams；更像面向团队流程的 agent 执行/编排层，而不是单次聊天工具。榜单页：[Rize AI Tools](https://rize.io/ai-tools)

- **#14 [browser-harness](https://github.com/browser-use/browser-harness)**：Browser Use 的自修复浏览器 harness，目标是让 LLM 完成任意浏览器任务；适合关注网页自动化、DOM/视觉失败恢复和 agent 浏览器执行层的人。榜单页：[Rize AI Tools](https://rize.io/ai-tools)

- **#16 [nullclaw](https://github.com/nullclaw/nullclaw)**：Zig 写的自主 AI assistant infrastructure，原始描述强调“最快、最小、全自主”；看点在轻量 agent 运行基础设施，而非模型本身。榜单页：[Rize AI Tools](https://rize.io/ai-tools)

- **#17 [TencentDB-Agent-Memory](https://github.com/Tencent/TencentDB-Agent-Memory)**：腾讯开源的本地长期记忆方案，通过 4 层渐进 pipeline 为 AI Agents 提供 memory，且不依赖外部 API；适合企业/私有化 agent 做记忆层评估。榜单页：[Rize AI Tools](https://rize.io/ai-tools)

- **#18 [html-anything](https://github.com/nexu-io/html-anything)**：本地 agentic HTML editor，提供 75 个 skills、9 类输出 surface、沙箱预览与一键导出；明确支持 Claude Code、Cursor、Codex、Gemini、Copilot、OpenCode、Qwen、Aider 等 coding agents。榜单页：[Rize AI Tools](https://rize.io/ai-tools)

- **#19 [anything-analyzer](https://github.com/Mouseww/anything-analyzer)**：协议分析工具，集成浏览器抓包、MITM 代理、指纹伪装、AI 分析和 MCP Server；价值在把网络调试/抓包能力接进 AI Agent/IDE。榜单页：[Rize AI Tools](https://rize.io/ai-tools)

- **#20 [claude-code-book](https://github.com/lintsinghua/claude-code-book)**：《御舆：解码 Agent Harness》，42 万字拆解 Claude Code 的 agent harness 架构，从对话循环到自建 harness；更偏深度学习资料，但主题直接指向 coding-agent 架构。榜单页：[Rize AI Tools](https://rize.io/ai-tools)

**今日取舍：** raw corpus 状态为 ok，共 20 个 Rize AI tools weekly ranking 条目。近两日报告已连续写过 #1–#8，且 `claude-plugins-official`、`taste-skill`、`Anthropic-Cybersecurity-Skills` 等也在 GitHub 栏近期覆盖，今天按去重只保留未实质展开、且与 AI/coding-agent 工具链直接相关的条目；剔除通用学习资料、纯领域应用或视频/交易等弱相关项目。

## Product Hunt 新品

- **Step 3.7 Flash** 是一个“能看见并行动”的高速 agent 模型。对 agent/coding-agent 用户，信号不在又一个聊天模型，而在 Product Hunt 新品开始直接把视觉理解、动作执行和低延迟作为 agent 模型卖点。 [Product Hunt](https://www.producthunt.com/products/step-3-5-flash?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Openstatus MCP Health Checker** 用真实 AI client 方式测试 MCP server，而不是只做 ping。随着 MCP 连接层进入更多 agent 工作流，这类健康检查更接近生产必需品：要验证工具列表、调用路径和 client 兼容，而不只是端口在线。 [Product Hunt](https://www.producthunt.com/products/openstatus-2?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Wandesk** 主打“Build Your Own AI Desktop”。原始信息很短，但方向贴近桌面 agent：把多个 AI 能力收进可操作的桌面工作区；真正价值要看它能否管理权限、上下文和跨应用动作，而不是只做一个 AI 启动器。 [Product Hunt](https://www.producthunt.com/products/wandesk-ai?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** raw corpus 状态为 ok，共 5 个 Product Hunt topic hit。保留与 agent 模型、MCP server 生产检查、AI desktop/桌面 agent 工作区直接相关的 3 个产品；排除 Wingbits AI（航空监控垂直场景，虽称 AI agents 但与 coding-agent 工作流距离较远）和 Exstats（浏览器扩展竞品监控，开发者属性有但非 AI/agent 主线）。近两日 Product Hunt 栏已覆盖 Vibeocus Lens、MCP Bridge、/monitor、Crew44、Memori、Pancake；今天未重复这些产品。

## Polymarket AI 市场

- **5 月最佳 Coding AI 模型市场几乎收盘锁定 Anthropic：98.6%，OpenAI 0.5%、Google 0.5%；24h 成交量约 3,622.8，30d 约 49,530.9，流动性约 55,187.4。** 相比昨日报告的 98.2% 继续小幅上行；月底市场分歧已很低，但这仍只是交易者预期，不等于真实 coding benchmark 结论。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may)

- **“任一 AI 模型 6 月 30 日前达到 Coding Arena 1550”给出约 64.5% 概率，30d 成交量约 4,681.1、流动性约 1,664.0，并显示本周上行 22.5%。** 这是今天 raw corpus 里少数直接面向编码模型能力门槛的盘口；由于原始 outcome 标签重复为 “any AI model”，这里只按题面 1550 门槛解读，不能外推到具体厂商领先。 [Polymarket](https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-june-30)

- **5 月最佳 AI 模型总榜市场进一步压到 Anthropic：99.8%，OpenAI 0.1%、Google 0.1%；24h 成交量约 130,710.8，30d 约 6,868,074.1，流动性约 2,410,894.3。** 相比昨天 99.4% 再上行，盘口基本把 5 月总榜看成 Anthropic；实际 agent 选型仍应回到自家任务、工具链、延迟和成本验证。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may)

- **6 月最佳 AI 模型市场仍由 Anthropic 领先，但优势较昨天收窄：Anthropic 80.9%，Google 14.5%、OpenAI 4.0%；24h 成交量约 253,589.5，30d 约 3,636,902.4，流动性约 2,518,979.4。** 相比昨天 Anthropic 83.4% 回落、Google 从 11.5% 升到 14.5%，说明下月模型发布/评测预期仍有一定变动空间。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **5 月最佳数学 AI 模型市场明显押向 Google：97.4%，Anthropic 2.4%、OpenAI 0.3%；24h 成交量约 23,331.9，30d 约 335,048.4，流动性约 156,807.4。** Google 较昨天 90.0% 大幅上行；数学能力盘口可作为复杂推理、形式化验证和代码规划预期背景，但不能当作公开 benchmark 结果。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-may)

- **FrontierMath 相关盘口继续显示高难数学突破有分歧：Gemini 达到 45% 为 44.0%、达到 50% 为 41.0%；Claude 到 6 月前达到 50% 的 Yes 为 37.5%；任一 AI 模型 2026 年前达到 90% 的 Yes 为 25.0%。** Claude 50% 较昨天 42.0% 回落，90% 远期盘基本持平；这些都应视为市场预期，而不是模型能力事实。 [Gemini 市场](https://polymarket.com/event/gemini-3-score-on-frontiermath-benchmark-by-june-30) / [Claude 市场](https://polymarket.com/event/anthropic-claude-score-on-frontiermath-benchmark-by-june-30) / [90% 市场](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027)

**今日取舍：** raw corpus 状态为 ok。保留与 AI/coding-agent 直接相关的模型总榜、Coding AI、数学/benchmark 和 Coding Arena 门槛盘口；剔除第二名 Coding AI、中国 AI 公司榜首、Style Control 版 5 月总榜和 OpenAI+Anthropic vs Google 估值盘，因为它们与主盘口重叠、偏泛模型生态或偏资本市场。今日 raw corpus 未提供 6 月最佳 Coding AI 主盘口，因此不沿用昨日报告补写。所有概率均为 Polymarket 市场预期，不是已确认事实。
