# AI Agent 日报（2026-06-27）

## 天气

- **北京·海淀：中等毛毛雨，22.4°C–35.7°C。** 降水概率 47%、预计 1.2 mm，西南风最高 14.2 km/h；较昨日最高温小降约 0.5°C、低温上升约 1.1°C。高温仍接近 36°C，且从无雨转为有小雨概率，出门兼顾防晒、补水和轻便雨具。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-27&end_date=2026-06-27)
- **上海·杨浦：小毛毛雨，20.4°C–28.6°C。** 降水概率 6%、预计 0.1 mm，东风最高 10.1 km/h；较昨日最高温和低温都小幅上升，雨量仍很低。今天体感温和偏湿，通勤主要防零星小雨和路面湿滑，不必按强降雨准备。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-27&end_date=2026-06-27)

**今日取舍：** 天气为每日固定实用信息，不因近两日报告已有同类栏目而去重；保留北京·海淀和上海·杨浦两地 2026-06-27 当日预报，并仅用 2026-06-26 / 2026-06-25 历史报告辅助判断体感变化。

## X 推荐

1. **Claude Code 配置正在被产品化：社区在推荐 `claude-code-setup`，让新用户按向导安装 hooks、skills、MCP servers 和 subagents。** 这说明 coding agent 的门槛不只在模型，而在“把自动化能力安全装好”；团队试用时要把插件来源、权限和默认启用项纳入 review。  
   https://x.com/0xJokker/status/2070524928751698345

2. **OpenAI GPT-5.6 limited preview 在 X 上被多条帖子集中传播，提到 Sol / Terra / Luna 三档模型和小范围合作伙伴预览。** raw 证据主要来自转述与短帖，不能写成完整能力评测；对 agent 团队，当前更适合记录发布节奏与访问限制，而不是急着迁移默认模型。  
   https://x.com/dotey/status/2070589767608144370

3. **Codex CLI 0.142.3 发布，但 release note 明确是 maintenance-only patch，较 0.142.2 没有用户可见变化。** 这类小版本仍值得升级窗口记录：不要把它包装成功能增量，重点做回归、锁版本和确认与 0.142.2 的配置兼容。  
   https://x.com/CodexReleases/status/2070621353347371141

4. **Anthropic 宣布推进 Claude 经济影响研究，会结合小时级抽样和调查数据。** 这不是产品功能，但对采用 agent 的组织有参考：厂商开始把“AI 到底改变哪些工作”做成持续测量问题，企业内部也应记录任务类型、节省时间和替代/新增工作。  
   https://x.com/AnthropicAI/status/2070528961235575278

5. **有人用 ESP32 S3 做了一个小硬件，专门管理服务器上的 Claude Code 和 Codex 会话。** 这条很具体：远端 coding agent 需要的不只是网页 UI，也可能需要随手查看/控制的物理入口；真正落地要关注认证、误触、任务状态同步和紧急停止。  
   https://x.com/LBacaj/status/2070320972662464833

6. **HumanLayer 相关开源项目被中文社区转述为“帮 Agent 从 demo 变实盘”，核心问题是生产环境中的人工确认与执行边界。** raw 只截到开头，但方向清晰：agent 上线难点在审批、权限、工具失败和责任链，不是再多一个演示脚本。  
   https://x.com/SUOHA_AI/status/2070498876759441879

7. **一条多 agent 工程案例称 100+ agents 协作一周，把 Gemma 4 在 vLLM 上加速到原来的 5×。** 即便需要后续核验，它给出的信号很实用：长跑多 agent 会遇到沟通规范、配额池化、算力分工和跨 agent kernel debug，而不只是“多开几个子任务”。  
   https://x.com/servasyy_ai/status/2070399271652991066

8. **shadcn 写了一组 streaming chat 体验原则，第一条是不要在用户阅读时强行滚动。** 对 agent UI 很实用：长输出、工具日志和多轮流式响应都要尊重用户当前位置，否则再聪明的 agent 也会变成难审阅的噪声。  
   https://x.com/shadcn/status/2070394918720221522

9. **zats 给 Codex 响应加了 sticky notes，用标注代替一问一答地追问。** 这是一种小而具体的人机协作界面改造：把 review 意见锚到回复片段，可减少上下文漂移；适合借鉴到代码 diff、计划文档和长任务复盘。  
   https://x.com/zats/status/2070492220084326907

10. **主流 Coding Agent 的 5 小时额度引发焦虑，有产品开始尝试周额度和未用额度 80% 结转。** 这不是模型能力新闻，但命中真实采用成本：agent 订阅正在从“固定时长上限”走向更细的预算/额度设计，团队也应把额度耗尽、排队和降级策略写进工作流。  
   https://x.com/jysperm/status/2070406676428238903

**今日取舍：** 已读取 `input.md`、`context.json`、100 条 x-feed raw、`selected-items.json`（仅审计）以及 2026-06-26 / 2026-06-25 历史报告；raw corpus 为主要证据，历史仅用于去重。近两日已实质覆盖 Codex mobile GA、Codex Remote / DigitalOcean、OpenAI 内部 Codex 使用、Claude Tag、Notion agents、Qwen-AgentWorld、GPT-5.5 Instant、skills 治理、Claude Code egress、loop engineering 等，因此今天优先保留 Claude Code setup、GPT-5.6 limited preview 传播、Codex 0.142.3 maintenance、Claude 经济影响测量、硬件化 agent 控制、多 agent 工程案例、agent UI/审阅界面与额度机制。剔除纯 RT/纯 t.co、传闻过强或证据太薄的模型爆料、生活/金融/娱乐/招聘内容，以及近两日已覆盖但无新增事实的 Claude Tag、OpenAI internal agents、DigitalOcean plugin、GPT-5.5 Instant、Daytona sandbox、Claude Code effort、skills 全局治理等重复主题。

## X 关注

- **OpenAI 开放 GPT-5.6 Sol 有限预览，同时给出 Terra / Luna 两个更均衡或经济的版本。** Sam Altman 称 Sol 与 GPT-5.5 同价，并另行提到 5.5 Instant 本周也更新；对 agent 团队，重点是默认模型、轻量模型和高阶模型的路由不要只按发布名切换。https://x.com/OpenAI/status/2070555272230384038 / https://x.com/sama/status/2070607488274358364 / https://x.com/sama/status/2070612055225483692

- **NousResearch 给 Hermes Agent 加了 MoA presets，可把多个开放模型组合成虚拟模型入口。** 这条的增量不是又一个模型列表，而是用 open-source 组合去接近 gated frontier 模型；采用时要看组合延迟、成本、失败仲裁和每个子模型输出是否可追踪。https://x.com/NousResearch/status/2070610321278988385

- **Antigravity 2.0 更新内置 Antigravity Guide skill、音频文件渲染，并改善大项目支持。** 这是 IDE/agent 产品继续把“使用方法”做成内置 skill 的例子；团队升级后应验证 Guide 是否会修改项目规则、音频渲染产物路径，以及大仓库索引/上下文成本。https://x.com/antigravity/status/2070578618154045448

- **Moxt 更新多 agent 编排工作流，称可自动让一组 Agent 协作并重复驱动更长任务。** raw 信息不够支撑完整评测，但方向很具体：多 agent 不只并行跑，还要能循环推进；试用时要检查角色分工、停止条件、失败回传和人工审批点。https://x.com/op7418/status/2070554759896142280

- **alex_prompter 引用 OpenAI agent 指南提醒：很多“AI agents”其实应该写成脚本。** 这条适合当作架构护栏：只有需要模型判断、工具选择和不确定状态处理的任务才值得 agent 化；固定流程先用脚本、队列和测试覆盖，成本和可控性通常更好。https://x.com/alex_prompter/status/2070589899502494092

- **Nick Dobos 试用新版 Siri 后批评它不说明可用工具、也难以被提示词引导。** 这是负面体验，但对 agent 产品很实用：用户需要知道系统能调哪些工具、哪些权限已开启、失败原因是什么，否则“会话式入口”会变成不可调试黑箱。https://x.com/NickADobos/status/2070507037289779342

- **Xcode 27 被转述为支持通过 Agent Client Protocol 添加自定义 agents。** raw 是转推，细节有限；但如果 ACP 进入 Xcode，Apple 开发工作流会更容易接入外部 coding agent，验证重点是项目权限、构建/签名动作审批和 IDE 内日志。https://x.com/twannl/status/2070531814515462361

- **Anthropic 称正在用小时级采样和调查数据研究 Claude 的经济影响。** 这不是产品功能，但对企业 agent 落地有用：厂商开始把“AI 如何进入真实工作节奏”量化；读者可关注采样口径、岗位差异、自动化与辅助的区分，以及是否能反推组织采用风险。https://x.com/AnthropicAI/status/2070528961235575278

**今日取舍：** 已读取 `input.md`、`context.json`、100 条 x-following raw、2026-06-26 / 2026-06-25 历史报告，并只把 `selected-items.json` 作为审计参考。近两日已覆盖 Codex mobile/Remote、GitLab Orbit MCP、Gemini notebooks、Daytona sandbox、Claude effort、Jalapeño、GPT-5.5 Instant、Hermes creative skill、skills 治理、双 agent loop、Claude Code web egress、Exa Connect、Qwen-AgentWorld 等；今天保留 GPT-5.6 / 5.5 Instant follow-up、Hermes MoA、Antigravity 2.0、Moxt 多 agent 编排、agent-vs-script 架构判断、Siri 工具透明度负例、Xcode ACP 线索和 Claude 经济影响研究。剔除纯 RT/纯 t.co、政治/生活/娱乐/金融/活动内容、泛模型传闻、证据过薄的短评，以及与近两日报告重复但无新增事实的 Claude Tag、skills 治理、Qwen-AgentWorld、Claude Code egress、GPT-5.5 Instant 单独短评等。

## Reddit 社区

今日暂无可新增的 Reddit 社区更新。本次包内 raw corpus 状态为 ok，共 16 个 r/ClaudeAI 线程；但逐条检查后，Thread Context 均为 0 score / 0 comments，只有发帖正文，没有评论、投票或后续事实支撑“社区讨论”。其中 Opus 4.8 / dynamic workflows、Fable 5 vs Opus 4.8、GLM 5.2 via Claude Code、多 agent 终端编排等主题贴近 coding-agent 工作流，但今天只能视为单帖陈述，不宜写成社区共识或争议。

**今日取舍：** 已读取 `input.md`、`context.json`、16 个 reddit raw 文件、`selected-items.json`（仅审计）以及 2026-06-26 / 2026-06-25 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected-items.json` 驱动判断。近两日报告已连续因 Reddit 线程缺少评论展开而空栏；今天 raw 数量增加，但仍缺少可验证社区反馈，且部分主题与昨日已判空素材重合，因此本栏输出空结果。

## Hacker News 热榜

- **GPT‑5.6 Sol 发布登上 HN #1，670 分、408 评论；讨论重点很快从“能力版本号”转到延迟和价格。** 评论抓住 Cerebras 最高 750 tokens/s 的计划，认为代码库检索、长链路 agent 等场景会直接受益；也有人担心旧便宜模型被下线后，被迫迁到更贵替代型号。 [HN](https://news.ycombinator.com/item?id=48689028) / [OpenAI](https://openai.com/index/previewing-gpt-5-6-sol/)

- **“美国政府将决定谁能用 GPT‑5.6”登上 HN #4，582 分、729 评论；技术发布被拆成了政策线程。** 评论主要担心不透明准入会变成监管俘获：大厂和少数客户拿到前沿模型，开源权重、自训练和非美国团队则面临更高不确定性。 [HN](https://news.ycombinator.com/item?id=48690101) / [Washington Post](https://www.washingtonpost.com/technology/2026/06/26/openai-says-us-government-will-vet-users-its-latest-ai-model/)

- **AWS Lambda MicroVMs 登上 HN #5，213 分、126 评论；评论把它直接放进 agent sandbox 竞争里。** 讨论点包括 snapshot/fork、SSH/VPN、网络层遮蔽 secrets、GPU 分享和本地 libkrun；对 coding-agent 运行环境，问题不是“能隔离”而是能否低成本、可审计地管理远端/本地沙箱生命周期。 [HN](https://news.ycombinator.com/item?id=48642510) / [AWS](https://aws.amazon.com/blogs/aws/run-isolated-sandboxes-with-full-lifecycle-control-aws-lambda-introduces-microvms/)

- **Show HN: Weave Router 登上 HN #7，112 分、79 评论；它把 Claude Code、Codex、Cursor 请求转成模型路由问题。** 作者称用 agent traces 训练 RL 路由器、内部节省 40% token 成本；评论质疑代理层会破坏 prompt cache、agent 已有的模型感知控制环，以及单一组织 traces 是否能泛化。 [HN](https://news.ycombinator.com/item?id=48688700) / [GitHub](https://github.com/workweave/router)

- **开放权重与闭源 LLM 差距讨论登上 HN #2，分数不高但切中开源模型供给风险。** 评论认为开放权重很大程度依赖少数公司“慈善式”放水，若没有社区拥有的算力，供给可随时中断；另一个争议是开源模型追赶是否依赖闭源模型蒸馏。 [HN](https://news.ycombinator.com/item?id=48692058) / [文章](https://blog.doubleword.ai/frontier-os-llm)

**今日取舍：** 已加载并遵循 `daily-report-lane-hacker-news`，读取 `input.md`、`context.json`、9 条 HN topstories raw，以及 2026-06-26 / 2026-06-25 历史报告；历史仅用于去重，`selected-items.json` 只作审计参考。近两日已覆盖 OpenKnowledge、OpenAI/Broadcom 推理芯片、Gemini computer use、PR spam、RubyLLM 等，因此今天保留 GPT‑5.6 Sol、GPT‑5.6 准入政策、AWS MicroVMs、Weave Router 和开放权重差距。剔除恐龙展、nomogram、C++ hopscotch map，因与 AI/coding-agent 工作流弱相关；超声脑成像虽有“mind reading”争议，但更偏医疗影像验证，今天不挤占 agent/模型基础设施主线。

## Hacker News 搜索观察

- **Statey 把“agent 共享数据库”做成无 UI 的 MCP 工具：Claude Desktop、Claude Code、Codex、ChatGPT 都可写同一套结构化数据。** 它会按对话创建 collection、版本化 schema，并记录多用户归因与活动日志；作者也明确担心 prompt injection 和过宽写权限，因为审计只能事后看见问题。 [HN](https://news.ycombinator.com/item?id=48691461) / [Statey](https://www.statey.ai)

- **TBD 是一个 Mac-native coding-agent multiplexer：人用 GUI，LLM 和脚本用 CLI，后台 daemon 统一管状态。** 作者从 Conductor、dmux、claude-squad 等工具迁移后选择自建，核心原则是“用户能手动做的事都要暴露给 CLI”，目前主打 Claude Code，兼有 Codex 基础支持。 [HN](https://news.ycombinator.com/item?id=48688943) / [GitHub](https://github.com/cheapsteak/tbd)

- **“哪些 AI 概念会留下来”这条 Ask HN 把分歧集中到 MCP、skills、agents 与 rigid agentic workflows。** 评论倾向认为 agents 和 MCP 更可能长期存在，硬编码 prompt chain / state machine 会被替换；同时把执行权限、未经检查的 agent 决策、agent-to-agent payments 列为暗角。 [HN](https://news.ycombinator.com/item?id=48691972)

- **另一个 Ask HN 把 coding agents 用作学习和 onboarding 工具：读代码模块、架构、会议转录和专题资料，再产出 Markdown insight。** 该帖暂无评论，但问题本身具体：下一步不是让 agent 多写总结，而是设计可复查的提问、抽取、验证和知识沉淀流程。 [HN](https://news.ycombinator.com/item?id=48691675)

**今日取舍：** 已读取 `input.md`、`context.json`、15 个 HN search raw 文件、2026-06-26 / 2026-06-25 历史报告，并仅把 `selected-items.json` 用作审计参考。近两日报告已实质覆盖 OpenKnowledge、paraNOyar、conference-planner、inplan、ebookaloud、Drip、Agnes AI，以及更早被去重的 Compilr.dev、Woltspace、Hourly、Kimchi 等；今天保留未被近日报告展开、且能补充 agent 数据层、Mac 本地多路复用、概念生命周期/权限风险、学习型 agent workflow 的 Statey、TBD、AI concepts Ask HN 和 learning with coding agents。剔除 OpenKnowledge/ebookaloud 等重复项，AssertGo、AI front-end design 问答、独立研究者求助、Ventora 等因与本栏 coding-agent 读者的可操作增量较弱或证据不足未选。

## Claude Code

- **Claude Code `v2.1.195` 新增 `CLAUDE_CODE_DISABLE_MOUSE_CLICKS`，可在 fullscreen mode 禁用点击、拖拽和 hover，同时保留滚轮滚动。** 这给远端/全屏终端里的误点击提供了硬开关，适合回归 tmux/SSH/全屏工作流下的选择、滚动与链接操作。 [v2.1.195](https://github.com/anthropics/claude-code/releases/tag/v2.1.195)

- **`v2.1.195` 修复带连字符的 hook matcher 被误当子串匹配的问题。** `code-reviewer`、`mcp__brave-search` 这类标识现在精确匹配；若要匹配某个带连字符 MCP server 的全部工具，应改用 `mcp__brave-search__.*`，升级后需要检查既有 hooks 是否依赖旧行为。 [v2.1.195](https://github.com/anthropics/claude-code/releases/tag/v2.1.195)

- **插件安全和开关路径补了两个坑：项目 `.claude/settings.json` 启用的外部插件在所有 loader path 都会要求显式安装同意，`/plugin` Enable/Disable 也能处理 `plugin.json` 名称与 marketplace 条目名不同的插件。** 这会影响团队项目自带插件的首次运行、审计和禁用验证。 [CHANGELOG](https://github.com/anthropics/claude-code/blob/HEAD/CHANGELOG.md)

- **后台 agent 可靠性继续修复：新版写入的 background jobs 不再从 `claude agents` 消失或丢数据，崩溃后台任务重开时也不再先空白 5 秒。** 同版还修复 control socket 启动失败后 daemon 变成不可达、阻塞重启的问题；长跑任务应重点回归停止、重开和跨版本恢复。 [v2.1.195](https://github.com/anthropics/claude-code/releases/tag/v2.1.195)

- **语音模式修复了两类实际输入问题：macOS 长会话切换默认输入设备后不再只录到静音，中文、日文、泰文等无空格语言的 dictation auto-submit 也会触发。** Linux 端则把“无麦克风”和“SoX 未安装”区分开，方便排查语音环境。 [v2.1.195](https://github.com/anthropics/claude-code/releases/tag/v2.1.195)

**今日取舍：** 已读取 `input.md`、`context.json`、4 个 raw 文件、`selected-items.json`（仅审计）以及 2026-06-26 / 2026-06-25 历史报告；raw corpus 为主要证据，历史仅用于去重。近两日报告已分别实质刊登 `v2.1.191` 与 `v2.1.193`，今天只保留新增且有具体条目的 `v2.1.195`；CHANGELOG 与 release 重复处合并为同一组读者条目。

## Codex

- **Codex 稳定版 `0.142.3` 发布，但 release notes 明确是维护补丁：相对 `0.142.2` 没有用户可见变化。** 已在昨天覆盖 `0.142.2` 的 MCP tool search、macOS 系统代理和 Bedrock/远程 MCP 修复；今天只把 `0.142.3` 作为稳定线版本状态提醒，不重复展开。 [v0.142.3](https://github.com/openai/codex/releases/tag/rust-v0.142.3)

- **`0.143.0` 预发布推进到 `alpha.26`，release notes 仍只有版本号，资产继续覆盖 CLI、app-server、responses proxy、npm/Python 包、Windows sandbox 和 config schema。** 这延续近两天 alpha 分发验证节奏；跟随预发布的团队应把安装脚本、schema、app-server 与 Windows sandbox 一起做 smoke test。 [alpha.26](https://github.com/openai/codex/releases/tag/rust-v0.143.0-alpha.26)

- **Codex marketplace 现在支持 `source: "npm"` 的插件来源。** 安装时会用 `npm pack --ignore-scripts` 拉取包内容，并校验包名、semver、HTTPS registry、archive root 与大小限制；这让插件可从 npm/私有 HTTPS registry 分发，但目标机器必须有 `npm`。 [PR #29375](https://github.com/openai/codex/pull/29375)

- **远端 executor 的 skill catalog 构建改为并行读取 `SKILL.md` 与解析 plugin namespace。** 旧流程先等 namespace 查完才读 skill 文件，会在远端 executor 上多吃网络延迟；新流程保留 64 并发上限、排序和 namespace 规则，`codex-core-skills` 111 个测试通过。 [PR #30225](https://github.com/openai/codex/pull/30225)

- **Codex 对 skills 的使用边界继续放宽：code-review 提示会纳入 `$CODEX_HOME/skills/code-review-*`，MAv2 prompt 也更明确允许 AGENTS.md 与 skills 授权 delegation。** 这对团队意味着用户级 review 规则和项目级 agent 授权都会影响行为，应把高权限 skills 的来源、范围和停用方式纳入 review。 [PR #30143](https://github.com/openai/codex/pull/30143) / [PR #30274](https://github.com/openai/codex/pull/30274)

- **MCP OAuth 过期后的启动失败识别又补了一层：RMCP 把认证错误藏在 `ClientInitializeError::TransportError` 里时，现在也会给 app clients 返回 `failureReason: "reauthenticationRequired"`。** 这是昨天 MCP 重新认证信号的 follow-up，能减少客户端把“需要重新连接”显示成泛化启动失败。 [PR #30257](https://github.com/openai/codex/pull/30257)

- **线程存储和分叉语义继续收紧：`thread.history_mode` 写入首个 `SessionMeta` 后不可被后续 metadata 覆盖，`thread/fork` 新增可选 `turnId` 只复制到指定 turn。** 前者避免旧二进制回放把 paginated thread 降级为 legacy；后者为废弃 `thread/rollback` 后的“从某一步分叉”提供稳定替代。 [PR #30261](https://github.com/openai/codex/pull/30261) / [PR #30277](https://github.com/openai/codex/pull/30277)

- **TUI 新线程会消费 managed new-thread defaults，plain `codex` 可按组织配置启动到指定模型、reasoning effort 和 service tier。** 显式 `codex -m ...` 仍优先，resumed/forked threads 不变；企业部署升级后应回归 `/new`、`/clear` 与 `/model` 的覆盖顺序。 [PR #30147](https://github.com/openai/codex/pull/30147)

- **Amazon Bedrock catalog 新增 GPT-5.6 Sol/Terra/Luna，并保留 GPT-5.5 为默认优先级最高项。** 三个条目继承 GPT-5.5 元数据，增加 Bedrock-only `max` reasoning effort；使用 Bedrock 后端的团队需要确认模型选择 UI、优先级和 service-tier 显示。 [PR #30285](https://github.com/openai/codex/pull/30285)

**今日取舍：** 已读取 `input.md`、`context.json`、23 个 Codex raw 文件和 2026-06-26 / 2026-06-25 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected-items.json` 驱动判断。近两日已覆盖 `0.142.2`、`alpha.13/14/15/22/25`、AGENTS/Git root 并行探测、symlink skill discovery、agent thread graph、credential broker、MCP matcher/reauth 信号、code-mode IPC、extension World State、独立 zsh artifacts 与 TUI rollback warning 修复；今天保留 `0.142.3` 维护状态、`alpha.26`、npm marketplace plugins、远端 skill catalog 并行、用户级 code-review skills / delegation 授权、嵌套 MCP auth 错误识别、thread history/fork 语义、TUI managed defaults 与 Bedrock GPT-5.6 catalog。commit 与 merged PR 重复时合并为同一条证据；线程 writer teardown、submission-channel close 等偏局部可靠性修复，未单独刊登。

## OpenClaw

今日暂无可新增的 OpenClaw 更新。本次 openclaw-watch raw corpus 正常，共 3 个 release signals：`v2026.6.10-beta.2`、`v2026.6.10`、`v2026.6.11-beta.1`；但 2026-06-25 报告已刊登 `v2026.6.10` 正式版相对 beta 的新增事实，2026-06-26 报告已刊登 `v2026.6.11-beta.1` 的 Slack relay、Mattermost `/oc_queue`、per-DM model override、`--message-file`、RAFT CLI wake bridge、通道投递与 provider/model 修复。今天 raw 未提供新版本、新 PR、新发布验证变化或可作为 follow-up 的增量证据，因此本栏空栏，避免连续重复同一批 release notes。

**今日取舍：** 已读取 `input.md`、`context.json`、3 个 OpenClaw raw release 文件、2026-06-25 / 2026-06-26 历史报告，并仅将历史用于去重；`selected-items.json` 只做审计参考且其中没有 openclaw-watch 入选项。

## GitHub AI 项目

- **[workweave/router](https://github.com/workweave/router)（GitHub API 校验 223 stars）在 HN #7 发布，做面向 Claude Code、Codex、Cursor 等 coding agent 的模型路由代理。** 作者称用数万条 agent traces 训练路由模型，内部一个月节省 40% token 成本；HN 讨论集中在代理层会破坏 prompt cache、长链路上下文和 agent 自身模型选择闭环。 [HN](https://news.ycombinator.com/item?id=48688700) / [GitHub](https://github.com/workweave/router)

- **[aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws)（GitHub API 校验 1,337 stars）本周上榜，定位为 AWS 官方支持的 MCP servers、skills 和 plugins 集合。** 对把 agent 接入云资源的团队，它的价值在于把 AWS 操作封装成更标准的工具层；试用时应先核对 IAM 最小权限、可写操作审批、CloudTrail/日志归属和本地/远端凭证边界。 [GitHub](https://github.com/aws/agent-toolkit-for-aws)

- **[google-labs-code/design.md](https://github.com/google-labs-code/design.md)（GitHub API 校验 21,127 stars）本周上榜，给 coding agents 定义可持久读取的视觉身份规范格式。** 这把“设计系统”从口头提示变成仓库内结构化文件，适合前端 agent 复用品牌、组件和风格约束；落地时要看规范能否覆盖真实组件状态、token 版本和设计变更 review。 [GitHub](https://github.com/google-labs-code/design.md)

- **[BuilderIO/agent-native](https://github.com/BuilderIO/agent-native)（GitHub API 校验 2,519 stars）本周上榜，定位为构建 agent-native applications 的框架。** raw 只给出一句简介，但仓库直接切中“应用如何原生容纳 agent”这一层；评估时应优先看运行时抽象、工具/权限模型、状态持久化和与现有前端/后端框架的接入成本。 [GitHub](https://github.com/BuilderIO/agent-native)

**今日取舍：** 已读取 `input.md`、`context.json`、59 个 raw 文件索引/关键 raw、HN/HN search 交叉证据与 2026-06-26 / 2026-06-25 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 作为主要判断。按 hard floor stars ≥100，本次保留有当日 raw 支撑、GitHub API 校验达标、且近两日报告未实质展开的 `workweave/router`、`aws/agent-toolkit-for-aws`、`google-labs-code/design.md` 与 `BuilderIO/agent-native`。`DeusData/codebase-memory-mcp`、`Panniantong/Agent-Reach`、`calesthio/OpenMontage`、`mukul975/Anthropic-Cybersecurity-Skills`、`stablyai/orca`、`mattpocock/skills`、`inkeep/open-knowledge` 等虽达标但近两日已覆盖或明确去重；`cheapsteak/tbd`、`gofixpoint/amika` 等未达到 100 stars；`system_prompts_leaks`、`voicebox`、`hiring-agent`、`daily_stock_analysis` 等对今日 AI/coding-agent 项目工作流的直接增量弱于入选项。

## GitHub 趋势项目

- **[google-labs-code/design.md](https://github.com/google-labs-code/design.md) 本周上榜，GitHub API 校验 21,127 stars；它定义 `DESIGN.md`，把视觉识别和设计系统写成 coding agent 可长期读取的结构化规范。** 对前端/产品 agent 有用的是减少“每次重新解释品牌风格”；落地时要看 token 预算、设计 token 同步、截图验收和多项目继承规则。

- **[BuilderIO/agent-native](https://github.com/BuilderIO/agent-native) 本周上榜，GitHub API 校验 2,519 stars；它定位为构建 agent-native applications 的框架。** 这类框架的关键不在又包一层聊天 UI，而是能否把工具调用、状态、审批、人机接管和前端交互做成应用级原语，适合评估团队自己的 agent 产品架构。

- **[aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) 本周上榜，GitHub API 校验 1,336 stars；AWS 官方把 MCP servers、skills 和 plugins 打包给 agents 在 AWS 上开发。** 对云上 coding agent，重点是权限最小化、账号/region 边界、IaC 变更审批、日志审计，以及 agent 能否安全读取和修改真实云资源。

- **[JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) 本周上榜，GitHub API 校验 21,303 stars；它用 AI coding agents 一条命令克隆任意网站。** 它适合做前端复刻/迁移的 agent workflow 样板，但团队应先处理版权、资源引用、无障碍、响应式差异和人工验收，避免把“像素相似”误当成可上线交付。

**今日取舍：** 已读取 `input.md`、`context.json`、19 个 GitHub trending weekly raw 文件、`selected-items.json`（仅审计）以及 2026-06-26 / 2026-06-25 历史报告；raw corpus 为主要证据，历史仅用于去重。入选仓库均来自本 lane raw corpus，并通过 GitHub API 校验 stars ≥100。近两日报告已覆盖或明确去重 `mukul975/Anthropic-Cybersecurity-Skills`、`stablyai/orca`、`mattpocock/skills`、`Panniantong/Agent-Reach`、`DeusData/codebase-memory-mcp`、`calesthio/OpenMontage`、`koala73/worldmonitor` 等；今天保留未在近两日实质展开、且直接服务 agent 设计上下文、agent-native 应用框架、AWS agent 工具链和网站克隆工作流的四个项目。`asgeirtj/system_prompts_leaks` 虽达标但偏提示词归档且合规风险高；`interviewstreet/hiring-agent`、`jamiepine/voicebox`、`ZhuLinsen/daily_stock_analysis` 分别偏 HR、语音和投资分析；`Kong/insomnia`、`penpot/penpot`、`Stirling-Tools/Stirling-PDF` 等通用工具 raw 未给出当日 AI/coding-agent 工作流增量。

## Rize AI 工具榜

- **#1 [voicebox](https://github.com/jamiepine/voicebox)**：Rize 本期榜首，raw 描述为开源 AI 语音工作室，可用于声音克隆、听写和创作；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。
- **#2 [DeepTutor](https://github.com/HKUDS/DeepTutor)**：面向个性化学习的 agent-native tutoring 项目，raw 另给出项目页 [deeptutor.info](https://deeptutor.info/)；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。
- **#3 [openfang](https://github.com/RightNow-AI/openfang)**：开源 Agent Operating System，Rize raw 给出的定位集中在 agent 操作系统；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。
- **#4 [ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template)**：用 AI coding agents 一条命令克隆网站的模板项目；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。
- **#5 [zeroclaw](https://github.com/zeroclaw-labs/zeroclaw)**：面向个人 AI 助手的基础设施，raw 强调 fast、small、fully autonomous、跨 OS / 平台部署和组件可替换；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。
- **#6 [PixelRAG](https://github.com/StarTrail-org/PixelRAG)**：Rize raw 称其面向 scalable pixel-native search，目标是减少对传统网页解析的依赖；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。
- **#7 [headroom](https://github.com/headroomlabs-ai/headroom)**：在工具输出、日志、文件和 RAG chunks 进入 LLM 前做压缩，raw 标称减少 60–95% tokens，并提供 library、proxy、MCP server 形态；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。
- **#8 [hive](https://github.com/aden-hive/hive)**：面向 production AI 的 multi-agent harness；榜单页见 [Rize AI Tools](https://rize.io/ai-tools)。

## Product Hunt 新品

- **Agent Arena** 登上 Product Hunt，定位为面向 AI agents 的公共 arena。它更像 agent 评测/对战入口而非普通聊天产品；可关注任务定义、评分口径、参赛 agent 身份和结果是否可复现。 [Product Hunt](https://www.producthunt.com/products/agent-arena?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **DMV by Agent Community** 主打“community-governed namespace for AI agents”。如果 agent 要跨社区、工具和服务被识别，命名空间治理会影响身份、防冒充、权限映射和审计；目前 raw 只够确认定位，不能展开成已成熟标准。 [Product Hunt](https://www.producthunt.com/products/dmv-department-of-machine-verification?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **note.md** 把 notes 和 research documentation 做成本地 LLM Memory。对个人/团队 agent，价值在让研究资料进入可检索记忆层；试用时要看本地存储边界、引用回链、隐私隔离和旧笔记污染上下文的问题。 [Product Hunt](https://www.producthunt.com/products/note-md?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** 已读取 `input.md`、`context.json`、11 个 Product Hunt raw 文件、2026-06-26 / 2026-06-25 历史报告，并只把 `selected-items.json` 用作审计参考。近两日已覆盖 Heron、Grass 2.0、BrowserBash、Tencent EdgeOne Makers、Mindstone Rebel、Propane 等；今天保留未重复且更贴近 agent 评测、身份命名空间和本地记忆的 Agent Arena、DMV by Agent Community、note.md。剔除 Gemini Spark、Cewsco、ModuleX、Atlas、AI Slide Editor、Basedash、SquidHub、LockIn MCP，主要因为 raw 只有一句泛化定位，或偏通用助手、办公/仪表盘、协作空间、专注工具，对 AI/coding-agent 工作流的可解释增量弱于入选项。

## Polymarket AI 市场

- **6 月最佳 AI 模型总榜进一步收敛到 Anthropic：99.1%，OpenAI 0.7%、Google 0.3%；24h 成交量约 149,281.9，30d 约 1,135.5 万，流动性约 312.6 万。** 较昨日报告的 98.6% 小幅上行；这只是市场预期，不是模型实测结论。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **6 月最佳 Coding AI 模型盘口给 Anthropic 98.0%，OpenAI 0.6%、Alibaba 0.4%；24h 成交量约 10,418.9，30d 约 90,161.0，流动性约 100,891.8。** 较昨天 96.5% 继续上抬，临近月底更像收官定价；coding-agent 选型仍要看自家仓库测试、合并率和工具调用稳定性。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-june)

- **7 月远期盘仍押 Anthropic，但不如 6 月锁死：通用模型 Anthropic 85.5%、Google 11.0%、OpenAI 3.3%，24h 成交量约 306,255.9。** 7 月最佳 Coding AI 也给 Anthropic 90.5%、OpenAI 6.8%、Google 2.2%；下月盘口更容易被新模型发布、榜单口径或真实评测重定价。 [7 月总榜](https://polymarket.com/event/which-company-has-best-ai-model-end-of-july-299) / [7 月 Coding AI](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-july)

- **6 月最佳 Math AI 模型盘继续和通用/编码盘口分化：Google 95.5%，Anthropic 3.8%、OpenAI 0.4%；30d 成交量约 227,313.7。** 较昨天 Google 94.5% 再上行，说明数学/形式化推理预期没有简单跟随 Anthropic 总榜热度。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-june)

- **FrontierMath 长盘上行：“2027 前任一 AI 模型 ≥90%”的 Yes 为 89.0%，30d 成交量约 29,507.5，流动性约 13,653.9。** Grok 子盘给 ≥40% 为 96.8%、≥50% 仅 2.5%；前者较昨天 92.8% 继续上行，后者仍显示市场不认为 Grok 会很快跨过更高门槛。 [FrontierMath](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027) / [Grok 市场](https://polymarket.com/event/xai-grok-score-on-frontiermath-benchmark-by-june-30)

**今日取舍：** raw corpus 状态为 ok，共 11 条 Polymarket 证据；已读取 `input.md`、`context.json`、raw 文件、2026-06-26 / 2026-06-25 历史报告，并仅用历史做去重和变化对照，`selected_items.json` 只作审计参考。保留与 AI/coding-agent 直接相关、且有可解释概率/成交量变化的 6 月总榜、6 月 Coding AI、7 月总榜/7 月 Coding AI、6 月 Math AI 与 FrontierMath/Grok；剔除估值盘、第二名细分盘口和 Style Control 版总榜等重叠或弱增量条目。所有概率均为 Polymarket 市场预期，不是已确认 benchmark 或产品事实。
