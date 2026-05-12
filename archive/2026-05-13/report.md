# AI Agent 日报（2026-05-13）

## 天气
- **北京·海淀：雷暴，21.1°C–35°C** 今天降水概率 0%、0 mm，南风最高 10.8 km/h；较昨天最高温升到 35°C、体感更热，午后外出优先防晒补水，并留意雷暴预报与实际降水信号可能不一致。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-13&end_date=2026-05-13)
- **上海·杨浦：阴，18.9°C–31.4°C** 今天降水概率 12%、0 mm，东南风最高 12.6 km/h；较昨天小雨信号减弱、最高温略降但仍闷热，通勤主要防晒补水，备伞优先级不高。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-13&end_date=2026-05-13)

## X 推荐流
- 无

## X 关注流
- 无

## Reddit 社区

- **【实测成本】52 组 Claude Code 基准：先写 CONTRACT.md 比多代理并行更划算** 85 分帖给出生产 Next.js/TypeScript/Supabase 实验：结构化 brief 让质量从 5/10 到 9/10、成本降 54%；Agent Teams 成本反而高 73–124%，因为每个子代理都重复装入代码库上下文。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1ss7f38/we_ran_52_controlled_benchmarks_on_claude_code/)
- **【Claude Code 争议】用户把 Opus 4.7 问题归因到“读少、整文件重写、提问变多”** 351 分帖称作者重新订阅 Codex，并引用 AMD 团队 6,852 次 Claude Code 会话分析：Read:Edit 从 6.6 降到 2.0、“lazy”提示增 93%；讨论焦点从单纯抱怨转向是否需要多模型切换和 max reasoning 成本。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1stfc4t/opus_47_made_me_resubscribe_to_codex_after_two/)
- **【透明度批评】328 分帖称 Claude Code 的隐藏指令与上下文填充仍需公开治理** 作者认可 Anthropic 发布 post-mortem 和 dogfooding 承诺，但认为 silent/conflicting instructions、秘密系统提示和上下文注意力污染才是许多用户体验波动的根因；这是昨天模型发布热度后的反向社区审计。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1strcoa/claude_code_has_big_problems_and_the_postmortem/)
- **【多会话管理】Pokegents 把 Claude/Codex 会话做成带本地编排服务器的开源工作台** 183 分帖介绍 Pokémon 风格 dashboard：支持 iTerm2 里的 Claude Code，以及 ACP chat runtime 下的 Claude/Codex，还带持久 agent 身份、MCP 消息、通知和 session cloning；它延续多 agent 看板需求，但重点是本地编排和跨工具会话管理。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1t7m3j3/i_built_a_pokémonstyled_multiagent_dashboard_to/)
- **【项目记忆】Storybloq Mac app 把 `.story/` 里的 backlog、handover 和 Claude 终端合到一个窗口** 166 分帖称 CLI/MCP 把 tickets、roadmap、lessons 暴露给 Claude Code，Mac app 实时看板展示状态；作者还用该框架记录了约 580 个 ticket、260 次 handover，并让 Claude 写 Swift/TypeScript 后经 Codex review。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1symv0c/your_claude_code_project_dashboard_is_now_on_the/)
- **【Deep Research 技能】HyperResearch 试图把 Claude Code 变成可持久检索的研究代理** 129 分帖称该开源 skill harness 用 16 步 pipeline、会话内 searchable knowledge store、fact-checking 和 adversarial review，并通过 crawl4ai 扩展网页抓取；适合观察 Claude Code skills 从编码迁移到研究工作流。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sz9ib0/converting_claude_code_into_the_most_intelligent/)
- **【垂直代理】社区讨论 Anthropic 金融/保险 10 个 ready-to-run agents 是否会吃掉 niche startup** 126 分帖关注 pitchbook、KYC、月结等流程，并指出 Reuters 称金融服务已是 Anthropic 第二大行业；争议点不是模型能力，而是 Claude Cowork/Code/Managed Agents 是否会成为银行和保险的工作流层。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1t4xpwj/anthropics_new_finance_ai_agents_feel_like_a/)

## Hacker News 热榜

- **Needle：26M 参数工具调用模型把 agent 能力往端侧压缩** Show HN #4，作者称 Needle 专门做 single-shot function calling，消费级设备上可达 6000 tok/s prefill、1200 tok/s decode；训练包括 200B tokens 预训练和 2B Gemini 合成工具调用数据，主张工具调用更像“检索与 JSON 组装”而非大模型推理。对 agent 产品，信号是端侧手表、手机、眼镜里的工具选择/参数抽取可能不必依赖云端大模型。 [Hacker News](https://news.ycombinator.com/item?id=48111896)
- **Google AI Pointer 遭遇隐私与交互怀疑：用户不想让 AI 一直“看着桌面”** #9 热帖 85 分、73 评论；DeepMind 设想把鼠标指针变成可对屏幕对象发起 AI 操作的入口，但高赞评论质疑语音控制在日常场景不现实、很多示例可由右键菜单完成，并追问是否要持续把屏幕内容发给 Google。它延续了近期 GUI/桌面 agent 的核心矛盾：上下文越全，隐私、联网依赖和成本问题越尖锐。 [Hacker News](https://news.ycombinator.com/item?id=48111581)
- **Googlebook 登顶但评论集中反感 AI 营销与 Google 产品信任赤字** #1 热帖 452 分、712 评论；外链是 Googlebook 页面，讨论区对“AI 帮你购物/选衣服”的营销叙事反应强烈，认为大公司仍在向想象中的 AI 用户做广告；另一条高赞评论则说看到新的 Google 产品会先假设它很快被砍。对 AI 硬件/终端入口，社区关注点不是概念是否新，而是实际需求、品牌可信度和长期支持。 [Hacker News](https://news.ycombinator.com/item?id=48111545)
- **Obsidian 新社区插件体系缓解审核瓶颈，也暴露 AI 写插件后的规模压力** #7 热帖 245 分、101 评论；Obsidian CEO 在评论中说团队花近一年做 Community site 和 review system，要在兼容旧流程的同时提升安全与发现能力；社区补充称 AI 让写插件变容易后，人工审核几乎无法提交新插件。这个案例说明 AI 生成扩展生态后，真正瓶颈会转向审核、权限、安全和分发治理。 [Hacker News](https://news.ycombinator.com/item?id=48109970)
- **dnsmasq 六个严重 CVE 引发对基础组件更新与审计节奏的讨论** #3 热帖 164 分、70 评论；CERT 释放 dnsmasq 严重漏洞信息后，评论一边比较 MaraDNS 等替代实现的安全审计情况，一边抱怨发行版 stable 可能只做补丁回移而不升级到包含更多非 CVE 修复的新版本。对依赖本地网络、容器和开发环境的 agent 工作区，底层 DNS/DHCP/TFTP 组件仍是不可忽视的攻击面。 [Hacker News](https://news.ycombinator.com/item?id=48112042)
- **DuckDB Quack 协议把嵌入式分析数据库推向客户端/服务端部署形态** #6 热帖 112 分、24 评论；DuckDB 发布 Quack 远程协议后，评论关注它是否解决内部应用横向扩展，以及能否未来作为 DuckLake catalog 数据库。对数据分析 agent 或内部 BI 工具，DuckDB 从本地嵌入式组件扩展到远程服务，意味着可在多用户/多进程场景复用同一分析后端。 [Hacker News](https://news.ycombinator.com/item?id=48111765)

## Hacker News 搜索

- **Statewright：用状态机约束 agent 工具与阶段，争取让小模型更可靠** 作者称把规划、实现、测试拆成可验证状态：规划只读、实现可编辑、测试只能跑测试命令，并在 13–20B 模型和 Claude 系列上减少跑偏；评论认可方向，但追问研究复现代码、专利与开源边界。 [Hacker News](https://news.ycombinator.com/item?id=48108778)
- **Hopper：把 agentic 开发环境带进 z/OS、TN3270 和 COBOL 工作流** Hypercubic 展示 agent 通过主机终端找源成员、看 copybook、提交 JCL、读 JES/SYSPRINT、修固定宽度 COBOL 后重跑，并称敏感操作需审批、终端全程可见；评论焦点是训练数据、客户代码是否被训练，以及“让 LLM 动主机”的风险。 [Hacker News](https://news.ycombinator.com/item?id=48111143)
- **Nimbalyst：把计划、任务、会话和 diff review 合成 coding-agent 本地工作台** 这个 MIT 桌面/iOS 项目整合 markdown/图表/数据模型编辑、并行 session、kanban、worktree、可视化 git 和按块接受/拒绝 agent 修改，支持 Codex、Claude Code、OpenCode 与 Copilot；它延续多会话管理话题，但增量是把上下文产物和任务流放进同一工作区。 [Hacker News](https://news.ycombinator.com/item?id=48108137)
- **Orbit UI：用 n8n 式节点把浏览器/桌面 agent 固定成可复跑流程** 作者称每个节点是一条英文指令，agent 在带浏览器和桌面的 Docker 容器中执行，支持 Navigate/Do/Read/Fill/Check/Code/ForEach、LiteLLM、多模型、noVNC 观看接管、cron/webhook 与人工确认；适合把求职、抓取、LMS 检查这类重复任务从自由提示改成有边界的流程图。 [Hacker News](https://news.ycombinator.com/item?id=48100204)
- **Gigacatalyst：把“给客户临时做功能”变成 SaaS 内嵌 AI builder** 作者称它连接产品 API、数据模型和设计系统，让销售、CS 或客户用自然语言生成受治理的小应用，案例包括备件缺货预测、发票 OCR 和维修优先级矩阵；评论支持可定制 UI 方向，也担心非技术用户把技术债、权限和数据模型误用直接推到生产。 [Hacker News](https://news.ycombinator.com/item?id=48110593)
- **一位后端工程师请 HN 校准 LLM 编程体验：20–50% 提速与强监管并存** 发帖者所在公司强制使用 Cursor/Claude，前端团队提速明显，后端团队因破坏和 token 成本回撤；高赞评论把甜点区定义为“一次生成一个函数”或让 AI 遵守既有架构，而不是交付大量自己不理解的代码。 [Hacker News](https://news.ycombinator.com/item?id=48102861)

## Claude Code

- **v2.1.140：修复 `/goal`、后台服务和企业环境边界问题** 新版修复 `/goal` 在 `disableAllHooks` 或 `allowManagedHooksOnly` 下静默卡住的问题，现在会直接提示；`claude --bg` 在后台服务即将 idle-exit 时不应再报 “connection dropped mid-request”。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.140)
- **Agent、设置热加载和插件诊断继续补细节** Agent tool 的 `subagent_type` 现在大小写、分隔符不敏感，`"Code Reviewer"` 可解析到 `code-reviewer`；symlink settings 热加载误触发 `ConfigChange` hooks、Windows 缺 `gh` 时反复 `where.exe` 导致 event-loop stall、插件默认目录被 `plugin.json` 覆盖却无提示等问题也已修。 [Changelog](https://github.com/anthropics/claude-code/blob/HEAD/CHANGELOG.md)

## Codex

- **PreToolUse hooks 现在可以真正改写即将执行的工具输入** `PreToolUse` 早已有 `updatedInput` schema，但此前 Codex 会拒绝而不是应用；#20527 改为在 `permissionDecision: "allow"` 时把改写后的输入送入 dispatch，覆盖 shell/container/local shell/exec_command、`apply_patch` 以及 MCP 工具，并保留各工具对 hook 暴露的兼容输入形状。这让企业或团队的 hook 不只是“放行/阻断”，也能在执行前做命令、patch 或 MCP 参数的最后修正。 [PR](https://github.com/openai/codex/pull/20527)
- **Windows sandbox 补齐 deny-read 语义，但对无法保证读拒绝的后端选择 fail closed** #18202 把 exact/glob `access = none` 读限制扩展到 Windows：把 deny-read 策略解析成 ACL target、对已有 glob 做启动前快照展开、保留缺失路径以便先 materialize 再加 deny ACE，并把 elevated/logon-user 后端接入 unified exec；关键点是 unelevated restricted-token 的 `WRITE_RESTRICTED` 只能权威约束写入，遇到 deny-read override 会直接拒绝运行，避免假装有读隔离。 [PR](https://github.com/openai/codex/pull/18202)
- **TUI 加入 ambient terminal pets，把 App 的“宠物状态反馈”搬进终端** #21206 新增 `/pets` 选择器、预览和禁用入口，内置 spritesheet 按需从 Codex pets CDN 下载并缓存到 `~/.codex/cache/tui-pets/`，自定义宠物保持本地；渲染侧会根据终端能力启用 Kitty Graphics/SIXEL、在 tmux 下禁用图像宠物，并为 transcript、composer、approval 和 picker 预留布局空间，避免宠物盖住正文。这是偏体验向的大功能，但也说明 TUI 正在追 App 端的状态表达。 [PR](https://github.com/openai/codex/pull/21206)
- **parallel tool 支持从 model-visible spec 下沉到 handler 本身** #22254 移除只为携带并行元数据存在的 `ConfiguredToolSpec`，让 registry/router 存普通 `ToolSpec`，`ToolRouter::tool_supports_parallel()` 只查询 handler registry，找不到 handler 时默认 `false`；这减少“模型看到的工具声明”和“运行时真正可并行执行的处理器”之间的重复状态，后续排查并发调度会更直接。 [PR](https://github.com/openai/codex/pull/22254)
- **旧会话 compaction 会过滤历史遗留的模型 warning，而不是把它们当真实用户消息保留** #22243 删除生产路径里的 `record_model_warning`，并新增 legacy contextual fragments 来识别老会话中以 `user` 形式持久化的 unified exec process-limit、`apply_patch` via `exec_command`、model-mismatch 高风险 cyber fallback 等 warning；压缩历史时这些注入式上下文会走 fragment 过滤路径，避免污染新的对话摘要。 [PR](https://github.com/openai/codex/pull/22243)
- **extension 侧开始能拉起 guardian 类子代理** #22216 是 “guardian as an extension” 的 contributors part：把从 extension spawn 另一个 agent 的逻辑接起来，并在 start thread collaborator 中加入 `ThreadId`。原始说明很短，但信号明确：Codex 的 extension/agent 边界正在为从扩展中创建、追踪协作线程做准备。 [PR](https://github.com/openai/codex/pull/22216)
- **远程插件摘要 ID 规范化为 `plugin@marketplace` 形式** #22265 让 plugin summaries 使用和配置一致的 config-style ID，同时把后端 remote ID 单独暴露为 `remotePluginId`，并修正 `REMOTE_SHARED_WITH_ME_MARKETPLACE_NAME` 一致性问题；对插件市场和共享插件列表而言，这能减少展示 ID、配置 ID、后端 ID 混用造成的定位成本。 [PR](https://github.com/openai/codex/pull/22265)
- **推理请求开始带 `x-codex-inference-call-id`，便于把 call log 挂回 trace** #22311 在 inference calls 上增加该 header，目的很直接：把推理请求和 rollout/trace 中的调用日志关联起来。对排查长任务、并发工具调用或线上回放而言，这是小改动但属于可观测性基础设施。 [PR](https://github.com/openai/codex/pull/22311)
- **0.131.0-alpha.8 / alpha.9 继续滚动多平台资产，release note 仍只有版本号** 今日 raw 同时出现 `rust-v0.131.0-alpha.8` 与 `rust-v0.131.0-alpha.9`，资产覆盖 Codex CLI、app-server、npm、Windows/MSVC、Linux musl、macOS dmg/tar/zst、bwrap、argument-comment-lint 等；由于说明仍是“Release 0.131.0-alpha.x”，适合追 alpha 线的安装/CI 团队验证二进制可用性，不宜从 release note 推断功能完成度。 [alpha.8](https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.8) / [alpha.9](https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.9)

## OpenClaw

- **2026.5.12-beta.1 把重点转到权限收口与多代理可视化** 新预发布要求 memory-wiki ingest 具备 admin scope、Obsidian search 具备 write scope，同时在 Control UI session picker 中用 `└─` 前缀把 subagent session 嵌到父 session 下；相比昨天的 beta.5 稳定性修复，今天增量更偏“谁能读写记忆、谁从属于哪个会话”的治理与可观察性。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.1)
- **OpenAI/Codex 登录默认路径改为 ChatGPT/Codex 账号 OAuth** `openclaw models auth login --provider openai` 现在默认启动 ChatGPT/Codex account login，只有显式 `--method api-key` 才走 OpenAI API key；这延续昨天 Codex app-server 复用 CLI OAuth 的方向，但把入口前移到模型认证命令本身。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.1)
- **Cron 与 ACP 补上“单项检查”和 session lineage** Cron 新增直接 `cron.get`、`openclaw cron get <id>` 和 agent-tool `get`，便于只检查一个存储任务；ACP session listings 和 session info snapshots 暴露 Gateway session lineage metadata，客户端可渲染 subagent 图而不用走私有 Gateway side channel。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.1)
- **工具策略细到按发送方限制危险能力** Agents/tools 新增 canonical channel-scoped sender keys 的 per-sender tool policies，可在 global、agent、group、core、bundled 和 plugin tool surfaces 上按请求者身份限制危险工具；这比单纯按 agent 或频道开关更适合公开/群聊入口的最小权限治理。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.1)
- **通道与 UI 小修继续围绕真实运营边界** iMessage 增加 `openclaw channels status --channel <name>` 过滤并文档化 BlueBubbles-to-imsg cutover；Slack 可配置 `unfurlLinks`/`unfurlMedia`、`replyBroadcast` 并保留 mention 来源；Control UI 在 app module 未注册时显示纯 HTML recovery panel，给空白 dashboard 留下重试和扩展排障路径。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.1)

## GitHub AI 项目

- **Nimbalyst：把 coding agent 的计划、会话、任务和 diff review 收进本地桌面工作区** 这个开源项目集成 markdown/图表/数据模型编辑器、并行 session、kanban、worktree、可视化 git 和按块 accept/reject，支持 Codex、Claude Code、OpenCode alpha 与 Copilot alpha。 [GitHub](https://github.com/nimbalyst/nimbalyst) / [HN](https://news.ycombinator.com/item?id=48108137)
- **Needle：26M 参数工具调用模型面向手机和可穿戴设备开源** Cactus 称 Needle 单次 function calling 可在消费设备上达到 6000 tok/s prefill、1200 tok/s decode，训练含 200B 预训练 token 与 2B Gemini 合成工具调用数据；适合评估端侧 agent 是否需要大模型来做 JSON 参数装配。 [GitHub](https://github.com/cactus-compute/needle) / [HN](https://news.ycombinator.com/item?id=48111896)
- **InsForge：给 coding agent 准备全栈后端底座** `InsForge/InsForge` 本周 Trending，定位是开源 backend platform，给 agent 提供数据库、认证、存储、计算、托管和 AI gateway；重点是让 agent 端到端交付应用时少拼接一堆 SaaS。 [GitHub](https://github.com/InsForge/InsForge)
- **agentmemory：把 coding agent 的持久记忆做成独立组件** `rohitg00/agentmemory` 预览称基于真实 benchmark 提供 AI coding agents 的 persistent memory；在多会话、长项目里，它对应的是“agent 下次还能记住项目约束和历史决策”的基础设施问题。 [GitHub](https://github.com/rohitg00/agentmemory)
- **ruflo：面向 Claude 的多代理编排平台上榜** `ruvnet/ruflo` 主打部署 multi-agent swarms、协调 autonomous workflows 和构建对话系统；适合观察 Claude 生态里从单个 CLI agent 扩展到编排、企业架构和协同执行层的开源实现。 [GitHub](https://github.com/ruvnet/ruflo)

## GitHub 趋势项目

- **InsForge** `InsForge/InsForge` 本周 Trending，把数据库、鉴权、存储、计算、托管和 AI gateway 打包成面向 agentic coding 的开源后端平台。对让 coding agent 端到端交付全栈应用的团队，价值在于减少“生成前端后还要人工拼后端服务”的断点。 [GitHub](https://github.com/InsForge/InsForge)
- **agentmemory** `rohitg00/agentmemory` 主打给 AI coding agents 的持久记忆，并称基于真实 benchmark 排名第一。长跑开发任务的痛点是跨会话记住项目约束、历史决策和失败教训，这类记忆层可作为 Claude Code/Codex 外挂状态库评估。 [GitHub](https://github.com/rohitg00/agentmemory)
- **ruflo** `ruvnet/ruflo` 是面向 Claude 的 agent 编排平台，描述覆盖多 agent swarms、自主工作流和对话式系统。它把“单个 Claude 会话”扩展成可部署、可协调的多代理工作流，适合关注 Claude 周边 orchestration 的读者。 [GitHub](https://github.com/ruvnet/ruflo)
- **CloakBrowser** `CloakHQ/CloakBrowser` 是带源码级指纹补丁的 stealth Chromium，定位为 Playwright 的 drop-in replacement，并声称通过 30/30 bot detection tests。做浏览器 agent 或网页自动化时，它直接触及反自动化检测，但也需要评估合规边界和站点规则风险。 [GitHub](https://github.com/CloakHQ/CloakBrowser)
- **AI-Trader** `HKUDS/AI-Trader` 标语是“100% Fully-Automated Agent-Native Trading”，本周进入 Trending。金融 agent 读者可把它和昨天的多 Agent 交易框架分开看：这里强调“agent-native 全自动交易”，核心风险是数据、执行权限和风控边界是否清楚。 [GitHub](https://github.com/HKUDS/AI-Trader)

## Product Hunt 新品

- **Pixcode** 是自托管的 AI coding agents 控制室，主打把多个代码代理的任务和状态收进一个工作台；适合需要把并行 agent 执行留在自己环境里的团队。 [Product Hunt](https://www.producthunt.com/products/pixcode?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Long Horizon** 让 coding agent 从写 feature 延伸到自动跑测试；对长任务开发，核心看点是把“实现 + 验证”打包成同一轮代理工作，而不是只交代码草稿。 [Product Hunt](https://www.producthunt.com/products/long-horizon?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Khaos Brain** 提供面向 AI agents 的本地预测式记忆；它把长会话常见的上下文/状态延续问题做成独立组件，适合关注本地化 agent memory 的读者。 [Product Hunt](https://www.producthunt.com/products/khaos-brain?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场

- **5 月最佳 AI 模型主市场仍押 Anthropic，24h 成交放大到约 50.69 万** “5 月底最佳 AI 模型”给 Anthropic 83.0%、Google 13.5%、OpenAI 3.4%，流动性约 204.94 万；相比昨日 83.5%基本持平，但成交明显放大，5 月榜首分歧继续集中在 Anthropic vs Google。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may)
- **6 月最佳 AI 模型预期升到 Anthropic 71.2%** “6 月底最佳 AI 模型”给 Anthropic 71.2%、Google 20.0%、OpenAI 7.0%，24h 成交约 3.89 万、流动性约 83.81 万；相比昨日 68.0%继续上行，市场短线削弱了 Google 追赶叙事。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)
- **5 月最佳 Coding AI 对 Anthropic 的定价仍接近锁定** “5 月底最佳 Coding AI model”给 Anthropic 94.6%、Google 2.5%、OpenAI 1.4%，流动性约 6.70 万；相比昨日 94.8%几乎不变，读者可把它视作 coding 评测/榜单预期的强市场共识而非事实结果。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may)
- **OpenAI GPT 在 FrontierMath 60% 线的押注升到 54%** “6 月底前任一 OpenAI GPT 模型 FrontierMath 至少 60%”当前 Yes 为 54.0%，今日上行 17.5%，24h 成交约 2317；这比 90% 极端突破市场更贴近短期能力门槛，可作为数学推理预期的温和指标。 [Polymarket](https://polymarket.com/event/openai-gpt-score-on-frontiermath-benchmark-by-june-30)

## 来源
### 天气
- https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-13&end_date=2026-05-13
- https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-13&end_date=2026-05-13
### Reddit 社区
- https://www.reddit.com/r/ClaudeAI/comments/1ss7f38/we_ran_52_controlled_benchmarks_on_claude_code/
- https://www.reddit.com/r/ClaudeAI/comments/1stfc4t/opus_47_made_me_resubscribe_to_codex_after_two/
- https://www.reddit.com/r/ClaudeAI/comments/1strcoa/claude_code_has_big_problems_and_the_postmortem/
- https://www.reddit.com/r/ClaudeAI/comments/1t7m3j3/i_built_a_pokémonstyled_multiagent_dashboard_to/
- https://www.reddit.com/r/ClaudeAI/comments/1symv0c/your_claude_code_project_dashboard_is_now_on_the/
- https://www.reddit.com/r/ClaudeAI/comments/1sz9ib0/converting_claude_code_into_the_most_intelligent/
- https://www.reddit.com/r/ClaudeAI/comments/1t4xpwj/anthropics_new_finance_ai_agents_feel_like_a/
### Hacker News 热榜
- https://news.ycombinator.com/item?id=48111896
- https://news.ycombinator.com/item?id=48111581
- https://news.ycombinator.com/item?id=48111545
- https://news.ycombinator.com/item?id=48109970
- https://news.ycombinator.com/item?id=48112042
- https://news.ycombinator.com/item?id=48111765
### Hacker News 搜索
- https://news.ycombinator.com/item?id=48108778
- https://news.ycombinator.com/item?id=48111143
- https://news.ycombinator.com/item?id=48108137
- https://news.ycombinator.com/item?id=48100204
- https://news.ycombinator.com/item?id=48110593
- https://news.ycombinator.com/item?id=48102861
### Claude Code
- https://github.com/anthropics/claude-code/releases/tag/v2.1.140
- https://github.com/anthropics/claude-code/blob/HEAD/CHANGELOG.md
### Codex
- https://github.com/openai/codex/pull/20527
- https://github.com/openai/codex/pull/18202
- https://github.com/openai/codex/pull/21206
- https://github.com/openai/codex/pull/22254
- https://github.com/openai/codex/pull/22243
- https://github.com/openai/codex/pull/22216
- https://github.com/openai/codex/pull/22265
- https://github.com/openai/codex/pull/22311
- https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.8
- https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.9
### OpenClaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.5.12-beta.1
### GitHub AI 项目
- https://github.com/nimbalyst/nimbalyst
- https://news.ycombinator.com/item?id=48108137
- https://github.com/cactus-compute/needle
- https://news.ycombinator.com/item?id=48111896
- https://github.com/InsForge/InsForge
- https://github.com/rohitg00/agentmemory
- https://github.com/ruvnet/ruflo
### GitHub 趋势项目
- https://github.com/InsForge/InsForge
- https://github.com/rohitg00/agentmemory
- https://github.com/ruvnet/ruflo
- https://github.com/CloakHQ/CloakBrowser
- https://github.com/HKUDS/AI-Trader
### Product Hunt 新品
- https://www.producthunt.com/products/pixcode?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
- https://www.producthunt.com/products/long-horizon?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
- https://www.producthunt.com/products/khaos-brain?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
### Polymarket 市场
- https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may
- https://polymarket.com/event/which-company-has-best-ai-model-end-of-june
- https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may
- https://polymarket.com/event/openai-gpt-score-on-frontiermath-benchmark-by-june-30
