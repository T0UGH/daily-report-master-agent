# AI Agent 日报（2026-05-30）

## 天气

- **北京·海淀：雷暴，16.3°C–34°C。** 降水概率 0%、预计 0 mm，西南风最高 16.9 km/h；比昨天最高温再升约 2°C，白天炎热，注意防晒补水，午后若出现对流云要留意临近预警。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-30&end_date=2026-05-30)
- **上海·杨浦：阴，17.8°C–27.5°C。** 降水概率 0%、预计 0 mm，东风最高 7.8 km/h；比昨天略升温但仍偏阴，通勤基本不用带伞，早晚体感较凉。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-30&end_date=2026-05-30)

## X Feed

1. Grok Build 开始出现在 X 推荐流：面向 X Premium+ / SuperGrok 用户的 vibe coding 工具，并已有入门指南转发。对 agent 用户，xAI 正把聊天模型推进到可直接生成/改应用的入口，但可用性仍受订阅和早期文档限制。  
   https://x.com/0xCheshire/status/2060358181285708090

2. AutoS 被介绍为“AI Scientist”方向的新项目，目标不是回答问题或跑固定 workflow，而是让模型参与真实科学研究流程。原帖信息不完整，但信号明确：科研 agent 正从自动化助手转向提出/执行实验的系统。  
   https://x.com/AdaFang_/status/2060075719883891162

3. 有开发者总结 Pi 的一种用法：单 session 里只保留 TDD、handoff、grill-with-docs 等少数 skill，再频繁用 `/tree` 分叉、回退、summary 和 handoff。它提供了一个低复杂度 agent 工作流范式：少装 skill，用分支管理上下文和试错。  
   https://x.com/9hills/status/2060307204176310655

4. OpenAIDevs 发布 Codex 的两个开发者体验改进，其中提到 background agents 获得 stable pixel 相关能力。原帖被截断，细节不足以当升级指南，但可确认 Codex 后台 agent 的 UI/运行稳定性仍在持续打磨。  
   https://x.com/OpenAIDevs/status/2060478367921831936

5. 有用户发布两个 Codex skill：`codex-retrospective` 会定期回看历史会话并最小化更新 AGENTS.md，另一个用于保持使用流畅。重点是把“越用越懂项目”做成可版本化 skill，而不是靠模型临时记忆。  
   https://x.com/mylifcc/status/2059967391761891796

6. Cursor 开发者报告被社区摘出：头部用户的 AI 代码产出、token 消耗和 PR 合并量显著高于中位数，且 input/output token 结构在变化。对团队采用 agent，真正差距可能来自上下文读取和评审闭环，而不是只开不开 AI。  
   https://x.com/op7418/status/2060316035790860754

7. GacUI 作者开始为 automation 写 HTTP server，并指出锁屏状态下 UIAutomation API 会挂。这个细节对桌面 agent 很实用：如果要让 AI 稳定操作 GUI，底层控制通道可能需要绕开系统无障碍 API 的会话限制。  
   https://x.com/geniusvczh/status/2060280643591000495

8. 有开发者介绍 RTK：在 `cat`、`grep`、`rg`、测试日志进入上下文前先本地清洗、裁剪、摘要，只把关键错误、路径和上下文给模型。它解决的是 coding agent 的真实成本点：工具输出比代码本身更容易吞掉 token。  
   https://x.com/vincemask/status/2060362554820665572

9. Anthropic 工程师的 production AI agents workshop 被多位账号转发，内容指向 Agent SDK、Skills、MCP、代码执行和记忆等组合。相比单个提示技巧，这类官方工程教程更适合团队对齐 agent 的生产边界、工具权限和上下文管理。  
   https://x.com/qianmutong/status/2060242450900476004

10. Anthropic 安全负责人被转述称：“如果 90% 代码由 Claude 写、却没人 review，就有麻烦。”这条不是发布新闻，但提醒很具体：agent 代码占比上升后，review、测试和所有权不能同步缺席。  
   https://x.com/zodchiii/status/2059950801208918409

**今日取舍：** 近两天已重点写过 Opus 4.8、Claude Code dynamic workflows、Hermes v0.15、Codex pulse threads、Claude Marketplace、private MCP、Antigravity 2.0、Krea/Qwen 等主题；今天只保留有新增事实或能落到 agent 工作流实践的条目。剔除了生活/投资/教育/视频生成等泛流量内容、只有 t.co 的空帖、重复转发，以及证据被截断到无法具体说明的帖子。

## X 关注

- **Codex 的 Computer Use 已支持 Windows，移动端也能连接 Windows 主机。** OpenAI / OpenAI Devs 称 Codex 现在可在 Windows 上测试应用、调试流程和操作桌面；这把原先偏 macOS 的远程 agent 开发闭环扩到更多企业开发机。https://x.com/OpenAI/status/2060428604727771421 / https://x.com/OpenAIDevs/status/2060429591655927942

- **Codex 今天还有两个开发者体验修补：background agents 有稳定 pixel identity，且 chat UI 可开关 monospaced 字体。** 前者让远程/可视化操作中的 agent 视觉身份更稳定，后者改善代码、日志和 diff 的阅读。https://x.com/OpenAIDevs/status/2060478367921831936

- **dotey 提到 Anthropic API 新增 mid-conversation system messages。** 做 Agent 开发时，可在不中断对话的情况下追加系统级约束或策略；这和昨天 swyx 关注的“中途更新 instructions 不破坏 prompt cache”是同一条长会话控制主线的新证据。https://x.com/dotey/status/2060404667423596843

- **Claude Code 2.1.156 修复 API 端点兼容，riba2534 称国产厂商端点也能跑 dynamic workflows。** 昨天已写 dynamic workflows 本体，今天的增量是多模型/国产端点兼容层在跟进，便宜模型可被用于大规模流程编排实验。https://x.com/riba2534/status/2060430958734811526

- **Nick Dobos 指出 Codex app 的配置和聊天日志都是文件，agent 自己也能修改。** 这让 Codex 更像可脚本化工作区：配置、历史和行为可由文件系统驱动，但也意味着权限边界和配置 diff 需要被审查。https://x.com/NickADobos/status/2060470406348423205

- **GithubProjects 推出 Pullfrog：用 GitHub Actions 把 coding agents 接到 issues、PR 和 reviews。** 它对应的是事件触发式代码代理，不再只靠人在聊天框里下任务；关键要看权限、失败回滚和 review 阻断怎么设计。https://x.com/GithubProjects/status/2060398272431477243

- **Mercury Skills 把 reusable Skills 类比为 AI agents 的 npm packages。** 如果这种分发方式成立，团队可把提示、工具约束、领域流程和交付规范打包复用，而不是在每个 agent 项目里复制 Markdown。https://x.com/GithubProjects/status/2060442409558036735

- **dotey 分享用 AI 写 Mac App 的实践：优先 AppKit，少选 SwiftUI。** 他的理由是 AppKit 更强、界面更可控；对让 coding agent 做原生 macOS 应用的人，这比“让 AI 随便选框架”更像可执行的技术约束。https://x.com/dotey/status/2060411347930661235

- **Claude Design 与真实代码的同步，被 dotey 处理成“设计为唯一源 + changelog”。** 这给前端/产品 agent 一个具体工作流：把设计输出当 source of truth，每次改设计先写变更记录，再让代码侧追随，减少视觉稿和实现漂移。https://x.com/dotey/status/2060433841135772012

- **garrytan 认为 AI 让依赖升级接近免费，“以后再升”这个借口会消失。** 对 coding-agent 团队，这意味着可把依赖更新、兼容测试和安全补丁做成持续自动化任务，但仍要保留测试和人工合并门槛。https://x.com/garrytan/status/2060461897594683861

**今日取舍：** 优先保留 Codex Windows/后台 agent、Claude 长会话控制、dynamic workflows 兼容层、agent 事件触发、skills 分发和 AI 编程工作流实践；剔除生活、政治、电影、酒店、泛创业、纯转发和只有 t.co/表情的低信息帖。昨天已展开 Claude Opus 4.8、dynamic workflows 本体、Hermes v0.15、Antigravity 并行 agents、Codex usage/grep 等主题，今天只保留有新增事实的后续。

## Reddit 社区

- 今日 Reddit 原始语料不可用：`reddit-watch` raw corpus 标记为 `missing`，raw 文件数为 0；采集侧出现 Reddit HTTP 403，因此无法基于社区讨论做可靠筛选。本栏不使用 `selected_items.json` 或近日报告补写，避免把去重参考当作今日证据。

**今日取舍：** 由于 Reddit 抓取被阻断且没有 raw 证据，本栏不选条目；仅阅读 2026-05-29、2026-05-28 报告作为去重参考，未复用其中 Reddit 内容。

## Hacker News 热榜

- **SQLite durable workflow 登上 HN #1，245 分、126 评论；相比昨天 Postgres durable execution，今天讨论转向“本地/小型 agent runner 是否够用 SQLite”。** 评论区一边质疑 SQLite 类型系统和并发边界，一边有人建议用 Temporal，并指出 agent 用 SQLite 查特定行比反复 grep Markdown/JSON 更省上下文。 [HN](https://news.ycombinator.com/item?id=48326802) / [文章](https://obeli.sk/blog/sqlite-is-all-you-need-for-durable-workflows/)

- **Mistral AI Now Summit 笔记在 HN #3，276 分、83 评论；主线是欧洲/本地部署优势能否弥补模型能力落后。** 评论认可 BNP Paribas、Abanca 这类敏感数据 on-prem 场景，但也批评 Mistral 小模型和推理能力落后 Qwen/Gemma 等竞争者。 [HN](https://news.ycombinator.com/item?id=48325340) / [笔记](https://koenvangilst.nl/lab/mistral-ai-now-summit)

- **Liquid AI 发布 8B-A1B MoE、38T tokens 训练模型，HN #10、113 分、34 评论；小模型讨论集中在本地、私有和专用微调。** 有评论把它和 Qwen 小模型放在同一趋势里：低硬件门槛可让团队做离线、低延迟、可微调的专用 agent。 [HN](https://news.ycombinator.com/item?id=48325306) / [Liquid AI](https://www.liquid.ai/blog/lfm2-5-8b-a1b)

- **Show HN: Tiny-vLLM 是 C++/CUDA LLM inference engine，HN #8、42 分但只有 3 评论；看点主要在教学式 README。** 作者说 README 重点是帮读者建立可重建项目的 mental model，评论把它类比早期 llama.cpp，但文档更像分课教程。 [HN](https://news.ycombinator.com/item?id=48328184) / [GitHub](https://github.com/jmaczan/tiny-vllm)

- **“On Rendering Diffs”在 HN #4，100 分、27 评论；它把代码 diff 渲染从 UI 细节拉回 agent 可执行子任务。** 评论者注意到作者用模型反复试探明确子问题，也有人希望 diff 工具能识别“仅空白变化”“import 换行导致的大段噪音”，这直接影响 agent 代码审查可读性。 [HN](https://news.ycombinator.com/item?id=48327809) / [文章](https://pierre.computer/writing/on-rendering-diffs)

- **Shift 免费清洁换取家庭机器人训练数据，HN #5、37 分、57 评论；这是具身 AI 的数据采集样本。** 评论把它和 AirBnB 机器人测试、穿戴摄像头做家务、skill-capture gloves 放在一起讨论：训练数据正在进入真实家庭场景，也带来隐私和劳动边界问题。 [HN](https://news.ycombinator.com/item?id=48327962) / [The Verge](https://www.theverge.com/ai-artificial-intelligence/939765/ai-training-data-startup-shift-free-cleaning)

**今日取舍：** 保留与 agent 持久化基础设施、小/本地模型、推理引擎、代码 diff 审查和机器人训练数据直接相关且评论区有实质讨论的条目；剔除 Framework 12、Bijou64、Protect Our Games Act，因为它们虽有工程讨论但与 AI/coding-agent 工作流关联较弱；“dead economy theory”讨论 AI 劳动替代，但过于宏观，缺少可操作工程增量。

## Hacker News 搜索观察：多代理工作流补人机交互、队列和替代模型

- **Claude Code subagents 不能原生 AskUserQuestion，有人用 SQLite + MCP 做了阻塞式人工提问层。** `ask_human_question` 支持 CLI/Web 回答和多种问题类型，目标是让 subagents、agent teams、workflows 在卡点时能向人确认，而不是静默降级或乱猜。来源：[HN](https://news.ycombinator.com/item?id=48320233)

- **TheFoundry 把长任务多代理开发包装成 Markdown Kanban + 失败预算 + TOML A2A 的启动框架。** 作者称 pull-based workflow 让 agents 自取票，5 次失败硬停防止 token 空转，并用 TOML 减少 JSON 幻觉；适合关注“多代理不是多开窗口，而是需要队列和规则”的读者试读。来源：[HN](https://news.ycombinator.com/item?id=48322744) / [GitHub](https://github.com/aavilagallego/TheFoundry)

- **dotpi 试图用 Claude Code 观察并蒸馏自己的工作方式，训练 DeepSeek V4 Flash 等替代 harness。** 这条不是成熟工具，但问题具体：重度 Claude Code 用户开始担心订阅/API 成本和可用性，把“agent 迁移/备份”做成可实验的训练流程。来源：[HN](https://news.ycombinator.com/item?id=48326539) / [GitHub](https://github.com/njbrake/dotpi/tree/main)

**今日取舍：** 近两日报告已展开 OpenRig、Cordium、TravElly、Raft、Workplane、Gonfire、Search Router、Herdr、CodeWhale 等；今天只保留 5 月 29 日新增且能说明多代理工作流缺口的条目。Dynamic Workflows 问答与昨日 Claude Code 主栏高度重复，Zero Operators 只有标题，未展开。

## Claude Code

- **Claude Code `v2.1.157` 让 `.claude/skills` 里的插件无需 Marketplace 自动加载，并新增 `claude plugin init <name>` 脚手架。** `/plugin` 参数也补上子命令、已安装插件和已知 marketplace 插件的自动补全；维护团队内 skills/plugins 的用户可以更快本地分发和初始化。 [v2.1.157](https://github.com/anthropics/claude-code/releases/tag/v2.1.157)

- **`claude agents` 在 `v2.1.157` 开始尊重 `settings.json` 的 `agent` 字段，派发时也可用 `--agent <name>` 覆盖。** 这让后台 session 可以按项目默认代理配置分流，而不是每次手动指定；同时修复已完成 session 因 idle subagent 或泄漏后台 shell 不退休的问题。 [v2.1.157](https://github.com/anthropics/claude-code/releases/tag/v2.1.157)

- **Worktree 与后台恢复修了一批会影响长任务的边界：`EnterWorktree` 可在会话中切换 Claude 管理的 worktree，agent 结束后 worktree 不再锁死，`--resume` 会报告上次进程退出时仍在跑的后台 subagents。** 使用 `--worktree`/`--tmux` 的用户还要注意新版会回到当前 linked worktree，而不是 canonical repo root。 [v2.1.157](https://github.com/anthropics/claude-code/releases/tag/v2.1.157)

- **`v2.1.157` 修复了几个日常卡点：坏图像粘贴/MCP/dialog 附件不再直接 crash 请求，桌面/IDE/SDK 的 auto 与 bypass-permissions 模式不再误弹 sandbox 网络许可，VS Code/Cursor/Windsurf 右键粘贴不再重复剪贴板。** WSL 也补了图片粘贴、Windows 11 截图粘贴和从 Explorer 拖图。 [v2.1.157](https://github.com/anthropics/claude-code/releases/tag/v2.1.157)

- **Opus 4.8 在 `v2.1.156` 有一个紧急修复：thinking blocks 被修改会导致 API errors。** 昨天已写 `v2.1.154` 的 Opus 4.8 默认 high effort 和 dynamic workflows，今天的新事实是 4.8 相关请求错误已单独补丁修复，升级链路不应停在 2.1.154。 [v2.1.156](https://github.com/anthropics/claude-code/releases/tag/v2.1.156)

**今日取舍：** `v2.1.154` 昨天已按 Opus 4.8、dynamic workflows、后台 agents、MCP/插件治理展开，今天不重复；CHANGELOG 与 release 高度重合，只作为交叉验证。保留 `v2.1.156` 的 Opus 4.8 API error 修复，以及 `v2.1.157` 中对插件本地分发、agents 派发、worktree/恢复、终端/IDE 粘贴和权限提示有直接影响的新增变化。

## Codex

- **Codex Rust `0.136.0-alpha.1` 已发布，release note 仍很短，但资产重新覆盖 CLI、app-server、responses-api-proxy、SDK、Windows sandbox setup 与 Python wheel。** 打包/镜像脚本应先按 `rust-v0.136.0-alpha.1` 校验新资产名与平台包，不要把它当稳定版自动推广。 [0.136.0-alpha.1](https://github.com/openai/codex/releases/tag/rust-v0.136.0-alpha.1)

- **TUI 新增 `/archive`，可在当前会话内归档 active session 并退出。** 命令会先弹确认，默认选中“不归档”，并在任务运行中和 side conversations 禁用；这补上了从 TUI 管理历史会话的入口。 [PR #25027](https://github.com/openai/codex/pull/25027)

- **exec-server 连续修复沙箱 filesystem helper 的 macOS/取消场景问题。** 一处在 Tokio child handle drop 时 `kill_on_drop(true)`，避免启动卡住后遗留孤儿 helper；另一处保留 macOS `__CF_USER_TEXT_ENCODING`，绕开 CoreFoundation 默认编码查询导致的间歇性卡死。 [PR #25116](https://github.com/openai/codex/pull/25116) / [PR #25118](https://github.com/openai/codex/pull/25118)

- **Code Mode 引入 `CodeModeSession` durable session 接口，把 cell 生命周期、回调委托、终止和 shutdown 从 Codex 主会话中抽象出来。** 当前仍可用既有 in-process 实现，但为后续外部进程式 code-mode runtime 留出接口边界。 [PR #24180](https://github.com/openai/codex/pull/24180)

- **ResponsesAPI turn metadata 增加 subagent lineage：`parent_thread_id` 与 `subagent_kind` 会进入 `x-codex-turn-metadata`。** 冷恢复 subagent 线程后也会还原来源信息，便于分析哪个父线程生成了哪类 subagent。 [PR #24161](https://github.com/openai/codex/pull/24161)

- **thread-store 从 legacy `SandboxPolicy` 字段迁到 canonical `PermissionProfile`。** 新权限 profile 会以 JSON 写入现有 SQLite metadata，同时继续读取旧 sandbox policy；依赖 thread metadata、rollout 或 app-server 状态同步的客户端要检查字段迁移。 [PR #23165](https://github.com/openai/codex/pull/23165)

- **`web.run` standalone `/v1/alpha/search` 现在会随请求传入有效 per-turn `model`。** 这是跟进 `/v1/alpha/search` 已要求 `model` 的兼容修复，可避免 extension tool call 因缺模型字段失败。 [PR #25131](https://github.com/openai/codex/pull/25131)

- **Vim normal mode 补了两个日常编辑细节：`s` 可替换光标下字符并进入 insert mode，`o` 在最后一行下方开新行时会把光标移到新空行。** 使用 Vim composer mode 的用户升级后可复测自定义 keymap/schema。 [PR #25022](https://github.com/openai/codex/pull/25022)

**今日取舍：** 昨日已写 `0.135.0` 正式发布、diff/exec-server 安全、Windows sandbox、zsh fork、PermissionProfile context、stdio alias 与 Bedrock 目录变动，今天不重复。提交与 merged PR 重复时采用 PR 链接；`/rename` 文案、issue triage CI secret 环境等过小或偏内部，未列入主条目。

## GitHub AI 项目

- **[affaan-m/ECC](https://github.com/affaan-m/ECC)（198,521 stars）把 Claude Code、Codex、OpenCode、Cursor 等 agent harness 的优化方法打包成 skills、instincts、memory、security 与 research-first workflow。** 今天进入 weekly trending；对重度 coding-agent 用户，它更像一套可抄作业的运行手册，而不是单个模型包装器。

**今日取舍：** 只保留 raw corpus 中有仓库证据、GitHub API 校验 stars ≥100、且近两日报告未实质展开的 AI/coding-agent 项目。`oh-my-pi`、`codegraph`、`Understand-Anything`、`knowledge-work-plugins`、`cursor/plugins`、`Anthropic-Cybersecurity-Skills` 等近两日已覆盖或明确去重，今天无新增事实；`Search Router/simple-search` 等虽与 agent 检索相关但未过 100 stars；`ViMax`、`MoneyPrinterTurbo`、`RuView`、`presenton`、`dograh` 等偏视频、感知、演示或语音平台，未纳入本栏。

## GitHub 趋势项目

- **[affaan-m/ECC](https://github.com/affaan-m/ECC)（198,523 stars）把 Claude Code、Codex、OpenCode、Cursor 等 agent harness 的 skills、instincts、memory、安全和研究优先开发打包成优化系统。** 今天进入 weekly trending；对多工具 agent 用户，它对应的是把提示、记忆、权限和工作流规则沉淀成可复用 harness，而不是每个项目临时手写。

**今日取舍：** 硬门槛为 GitHub API 校验 stars ≥ 100，并只选与 AI/coding-agent 工作流有明确关系且近两日报告未实质展开的仓库。`microsoft/agent-governance-toolkit`、`BenedictKing/ccx`、`anthropics/claude-plugins-official`、`taste-skill` 等昨天已写；`knowledge-work-plugins`、`codegraph`、`Understand-Anything`、`oh-my-pi`、`cursor/plugins`、`Anthropic-Cybersecurity-Skills`、`stop-slop` 等近两日已覆盖或去重说明，今天无新增事实；视频、演示、语音、感知、学习资料和通用模型项目未纳入本栏。

## Rize AI 工具榜

- **#1 [how-to-train-your-gpt](https://github.com/raiyanyahya/how-to-train-your-gpt)**：从零构建现代 LLM 的教程型仓库，原始描述强调“每行代码都有注释、像给五岁孩子解释”。榜单页：[Rize](https://rize.io/ai-tools)
- **#2 [context-mode](https://github.com/mksglu/context-mode)**：面向 AI coding agents 的上下文窗口优化工具，通过隔离 tool output 来压缩上下文，原始描述称可减少 98% token、覆盖 15 个平台。榜单页：[Rize](https://rize.io/ai-tools)
- **#3 [ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch)**：AI engineering 学习/构建型仓库，Rize 描述为“Learn it. Build it. Ship it for others.” 榜单页：[Rize](https://rize.io/ai-tools)
- **#4 [Crucix](https://github.com/calesthio/Crucix)**：个人情报 agent，会从多个数据源观察外部变化，并在有变化时通知用户。榜单页：[Rize](https://rize.io/ai-tools)
- **#5 [omlx](https://github.com/jundot/omlx)**：Apple Silicon 上的 LLM inference server，支持 continuous batching、SSD caching，并可从 macOS 菜单栏管理。榜单页：[Rize](https://rize.io/ai-tools)
- **#6 [claude-plugins-official](https://github.com/anthropics/claude-plugins-official)**：Anthropic 官方维护的 Claude Code Plugins 目录，定位是高质量插件分发入口。榜单页：[Rize](https://rize.io/ai-tools)
- **#7 [prompt-master](https://github.com/nidhinjs/prompt-master)**：一个 Claude skill，用来为其他 AI 工具写更准确的 prompts，原始描述强调保留完整 context 和 memory。榜单页：[Rize](https://rize.io/ai-tools)
- **#8 [agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)**：211 个即插即用 AI 专家角色，支持 Hermes Agent、Claude Code、Cursor、Copilot 等 16 种工具，并覆盖工程、设计、营销、金融等 18 个部门。榜单页：[Rize](https://rize.io/ai-tools)

## Product Hunt 新品

- **Vibeocus Lens** 把正在运行的前端直接桥接到 AI agent。对前端 coding-agent 工作流来说，它瞄准的是“让 agent 看见真实 UI 状态并反馈修改”的闭环，而不是只靠截图或口头描述。 [Product Hunt](https://www.producthunt.com/products/vibeocus-lens?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **MCP Bridge by Appfactor** 主打把任意 API 接到任意 AI agent。它延续近两日 private MCP / 工具连接层主线，但今天的新 Product Hunt 信号是把 API-to-agent 适配直接产品化；真正要看认证、权限和失败恢复是否足够工程化。 [Product Hunt](https://www.producthunt.com/products/mcp-bridge-by-appfactor?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **/monitor by Firecrawl** 用来在网页变化时通知 AI agent。适合做定时巡检、竞品/文档/依赖变更监控的 agent 工作流；价值不在“监控网页”本身，而在把外部变化变成可触发的 agent 输入。 [Product Hunt](https://www.producthunt.com/products/extract-by-firecrawl?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** raw corpus 状态为 ok。保留直接涉及前端 agent 闭环、MCP/API 连接层和网页变化触发 agent 的产品；排除销售 BDR、广告视频、家装、销售培训、短视频剪辑、通用 BI、手机 IDE、HN 监控、LLM 用量菜单栏、屏幕尺等条目，因为它们与本报告的 AI/coding-agent 工作流主线较弱，或原始证据不足以形成更具体判断。

## Polymarket AI 市场

- **5 月最佳 Coding AI 模型市场继续几乎锁定 Anthropic：98.2%，OpenAI 1.6%、Google 0.5%；24h 成交量约 5,512.3，30d 约 56,479.5，流动性约 100,613.1。** 相比昨日报告的 97.9% 仍小幅上行，月底前分歧很低；这只是市场预期，不等于真实 coding benchmark 结论。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may)

- **6 月最佳 Coding AI 模型市场仍由 Anthropic 领先：89.5%，Google 5.0%、OpenAI 4.0%；24h 成交量约 3,396.2，30d 约 10,547.7，流动性约 38,312.0。** 相比昨天 92.5% 回落，但仍是压倒性领先；对关注下月编码模型发布的人，市场暂未给 Google/OpenAI 很大反超空间。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-june)

- **5 月最佳 AI 模型总榜市场进一步押向 Anthropic：99.4%，Google 0.3%、OpenAI 0.2%；24h 成交量约 93,690.3，30d 约 7,307,013.7，流动性约 2,420,192.5。** 距离月底只剩很短时间，盘口基本把“5 月榜首”看成 Anthropic；实际模型/agent 选型仍应回到自家任务、工具链和成本验证。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may)

- **6 月最佳 AI 模型市场给 Anthropic 83.4%、Google 11.5%、OpenAI 4.8%；24h 成交量约 225,977.4，30d 约 3,524,260.5，流动性约 2,468,596.9。** 相比昨天 Anthropic 86.0% 略回落、Google 从 10.5% 回升到 11.5%，说明下月总榜仍有一点发布预期空间，但主导预期未变。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **5 月最佳数学 AI 模型市场押 Google：90.0%，Anthropic 9.5%、OpenAI 0.5%；24h 成交量约 23,118.8，30d 约 342,136.5，流动性约 148,188.5。** Google 比昨天 86.0% 上行，数学能力盘口与复杂推理、形式化验证和代码规划有关，但不能当作公开 benchmark 结果。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-may)

- **FrontierMath 相关盘口显示高难数学突破仍有分歧：OpenAI GPT 到 6 月前达到 60% 的概率为 59.0%，Claude 到 6 月前达到 50% 的 Yes 为 42.0%，任一 AI 模型 2026 年前达到 90% 的 Yes 为 25.0%。** 这些盘口适合作为推理能力预期背景，而不是模型能力事实。 [OpenAI 市场](https://polymarket.com/event/openai-gpt-score-on-frontiermath-benchmark-by-june-30) / [Claude 市场](https://polymarket.com/event/anthropic-claude-score-on-frontiermath-benchmark-by-june-30) / [90% 市场](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027)

**今日取舍：** raw corpus 状态为 ok。保留与 AI 模型能力、coding AI、数学/benchmark 预期直接相关且成交/流动性较强的盘口；剔除第二名 Coding AI、中国 AI 公司榜首、Style Control 版 6 月总榜和 OpenAI+Anthropic vs Google 估值盘，因为它们与主盘口重叠、偏泛模型生态或偏资本市场。所有概率均为 Polymarket 市场预期，不是已确认事实。
