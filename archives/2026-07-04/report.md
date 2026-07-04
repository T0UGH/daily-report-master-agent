# AI Agent 日报（2026-07-04）

## 天气

- **北京·海淀**：今日小毛毛雨，24.8–37.2°C，最高温仍在 37°C 以上；降水概率 49%、预计 0.2 mm，西南风最高 11.4 km/h，外出重点仍是防暑补水，阵雨影响较轻。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-04&end_date=2026-07-04)
- **上海·杨浦**：今日雷暴并可能伴轻微冰雹，25.1–32.4°C；降水概率 96%、预计 10.8 mm，西南风最高 9.1 km/h，通勤和外卖/出行安排建议预留强降雨延误。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-04&end_date=2026-07-04)

## X 推荐

- **Claude Code 2.1.200 发布，权限默认切到 Manual。** 社区 changelog 归纳了 17 项 CLI 变化，重点包括 CLI、VS Code 与 IDE extension 的权限模式调整，升级后需要重新检查自动化脚本是否依赖旧默认授权。  
  来源：https://x.com/ClaudeCodeLog/status/2073091434123591872

- **Claude Code Artifacts 扩展到 Pro 和 Max 计划。** ClaudeDevs 表示用户可让 Claude 生成 artifact、写代码并发布链接；这把原本偏演示的产物分享流程放进日常开发订阅层。  
  来源：https://x.com/ClaudeDevs/status/2072770790114914317

- **Claude Platform API 提高限额并简化 tier。** 官方开发者账号称新分层不再按 API 支出划线；对多 agent、长上下文和批量评测用户，限额策略变化比单个模型更新更影响吞吐。  
  来源：https://x.com/ClaudeDevs/status/2072818299361263778

- **Chrome DevTools MCP 被前端开发者拿来接入 Codex / Claude Code。** 讨论点是让 agent 直接读取浏览器状态、调试前端 bug，而不是只靠截图和人工描述复现问题。  
  来源：https://x.com/yunxi0623/status/2073017018572546497

- **Hermes Agent profiles 被社区包装成“一台机器上的多专长代理团队”。** 帖子强调每个 profile 有独立记忆、模型与工具边界；适合把日报、开发、研究等长期任务拆成可隔离身份。  
  来源：https://x.com/IBuzovskyi/status/2073073852012171697

- **Fable 5 autoresearch loop 被用来做 25 个实验。** 作者转述 Superpowers 案例：花费约 165 美元，把构建速度提高 50%、token 开销降低 60%；关键价值是公开了迭代记录，而不只是结果数字。  
  来源：https://x.com/yibie/status/2072965594484543525

- **“给 agent 一台自己的电脑”成为端到端测试建议。** steipete 的短帖把重点放在真实环境执行：让 agent 能跑应用、看界面、点流程，减少只在代码层自我确认的假通过。  
  来源：https://x.com/steipete/status/2073214429655883814

- **video-use 被用于把 Codex 从写代码推进到视频制作。** 中文社区把它描述成“视频制作导演”：素材、目标和剪辑要求交给 agent 后，由工具链完成视频处理流程。  
  来源：https://x.com/369Serena/status/2072937232592195971

- **桥水在 Thinking Machines 平台上做金融文档私有化微调。** 转述称项目用 Qwen3-235B 处理金融文档筛选和央行报告解读；这是大机构把开源模型接到专门领域工作流的案例。  
  来源：https://x.com/FeitengLi/status/2073046885896728625

- **NVIDIA LocateAnything 被拿来讨论视觉语言模型定位瓶颈。** 西语帖称它针对 VLM 的视觉定位能力，适合关注 GUI agent、视觉 grounding 和多模态自动化的人跟进。  
  来源：https://x.com/precisox/status/2073193056250040554

## X 关注

- **给 coding agent 配独立电脑做端到端测试。** steipete 的建议很直接：不要只让 agent 改代码，还要给它能完整运行、点击和验证产品的环境；这对浏览器/UI/桌面类任务尤其能减少“代码看似正确、实际不可用”。来源：https://x.com/steipete/status/2073214429655883814

- **Codex 做设计可先让图像模型重画方案。** steipete 提出的工作流是：先用 imagegen 重新想象设计，再让 Codex 实现；它把“审美/视觉方向”从纯文本提示里拆出来，适合前端 agent 处理弱设计输入。来源：https://x.com/steipete/status/2073277317464682723

- **有人开始用 agent 自述替代逐行读大 diff。** thdxr 说大改动后会让 agent 按文件总结自己做了什么，再决定看哪些细节；这不是放弃 review，而是把人类注意力从全量 diff 迁到可疑文件和设计决策。来源：https://x.com/thdxr/status/2073238046296924466

- **Fable 5 与 Codex 被组合跑了一个两天 loop。** op7418 称两者一起完成 CodePilot 的 AI SDK 7 升级，跑满两天后额度仍未耗尽；可作为多模型 coding loop 在真实项目里协作的轻量案例。来源：https://x.com/op7418/status/2073221461792464953

- **Fable 5 的提示词讨论从“写具体点”转向更细的策略。** cyrilXBT 转述 Fable 5 团队给出的建议比“be specific”更复杂；对高能力模型来说，提示工程重点正在从口号变成边界、授权和反馈粒度。来源：https://x.com/cyrilXBT/status/2073316884435681724

- **AI agent 项目管理开始出现“可视化作战室”形态。** aiedge_ 说自己给多个具名 agent 做了一个实时任务“tavern”；这类界面把后台 agent 从黑箱命令行变成可观察、可分工的队伍状态。来源：https://x.com/aiedge_/status/2073240468155236480

- **MaxKB 被推荐为企业 RAG agent 平台。** GithubProjects 提到 MaxKB 是开源平台，面向企业级 RAG agent，集成知识检索 pipeline；适合需要把文档问答、知识库和 agent 流程放在一个系统里的团队评估。来源：https://x.com/GithubProjects/status/2073263038061560187

- **Meta 内部也承认 AI Agent 进展慢于高管预期。** AI_jacksaku 摘引称 Zuckerberg 提到 agent 开发速度不及预期，同时 Meta 年初裁员约 8000 人、又把 7000 人调入多个 AI 团队；大厂资源投入不等于 agent 立刻成熟。来源：https://x.com/AI_jacksaku/status/2073225283151482906

## Reddit 社区

- 非技术 solo founder 反映 Claude Chat 与 Claude Code 来回复制很低效；更新中他改为只在 VS Code 里用 Claude Code 后，速度明显提升，也减少了额外聊天用量。  
  来源：https://www.reddit.com/r/ClaudeAI/comments/1twb8c5/anyone_else_copying_and_pasting_between_claude/

- Claude 社区有人担心讨论重心过度偏向 Claude Code、CLAUDE.md、MCP、subagents 和终端工作流；非编码用户仍主要用聊天做写作、思考、学习和规划，但发帖意愿被“技术内容更严肃”的氛围压低。  
  来源：https://www.reddit.com/r/ClaudeAI/comments/1u85myc/the_gap_between_claude_code_power_users_and_us/

- 终端版 Claude Code 与 Claude Desktop 的取舍继续被追问：用户关心多文件上下文、大项目处理、MCP 集成难度，以及从桌面/聊天切到终端后哪些功能会缺失。  
  来源：https://www.reddit.com/r/ClaudeAI/comments/1ueskow/claude_code_in_the_terminal_vs_the_claude_desktop/

## Hacker News

- **本地跑 SOTA LLM 的成本争议被拉到硬件与量化细节。** James O’Beirne 的 local-llm 指南在 HN 引发 103 条评论，用户提醒示例构建可能接近 5–5.5 万美元，4-bit/REAP 在长上下文编码和数据分析上会明显掉质量。 [HN](https://news.ycombinator.com/item?id=48775921) · [GitHub](https://github.com/jamesob/local-llm)

- **Wafer 用 AMD 跑 GLM-5.2 的性能/美元数据，引发“别只报 TPS”的讨论。** 评论希望补充 performance per watt 和量化精度；多人指出 FP4/低比特量化常让 Kimi、GLM 这类模型在真实任务中“看起来快、实际被削弱”。 [HN](https://news.ycombinator.com/item?id=48780417) · [文章](https://www.wafer.ai/blog/glm52-amd)

- **Mistral 发布 Leanstral 1.5，主打小模型做 Lean 证明与 bug finding。** HN 讨论认可“专用小模型低成本覆盖 OCR/文件分析/形式化任务”的价值，但也质疑对比基准偏旧、示例 bug 是否真是测试和 fuzzing 难覆盖的边界。 [HN](https://news.ycombinator.com/item?id=48780801) · [Mistral](https://mistral.ai/news/leanstral-1-5/)

- **SearXNG 热帖下，Searx 原作者转而推荐 Hister：本地全文索引可把浏览历史和文件内容经 MCP 给 AI 助手用。** 讨论也提醒 metasearch 仍依赖 Google 等后端，更多价值是绕开 AI Overview、广告和单一搜索入口。 [HN](https://news.ycombinator.com/item?id=48779454) · [SearXNG](https://github.com/searxng/searxng)

- **Dan Luu 的 agentic coding 笔记把 HN 讨论带到“大上下文世界模型”。** 评论认为百万级上下文让许多复杂提示工程被简化，但企业协作的新难点变成：如何让团队共同维护同一个业务世界模型，并自动发现约束过期。 [HN](https://news.ycombinator.com/item?id=48782671) · [文章](https://danluu.com/ai-coding/#appendix-agentic-loops-and-writing-this-post)

- **Kagi 给搜索产品加 AI toggle，同时因翻译成本调整服务。** 评论正面看待“想用时才出现 AI”的选择权，也有付费用户质疑 Kagi Translate 被临时移除、未来转订阅制是否削弱原订阅价值。 [HN](https://news.ycombinator.com/item?id=48779352) · [Changelog](https://kagi.com/changelog#10959)

## HN 搜索

- **Ultracodex 用 Codex 跑 Claude Ultracode 工作流。** 作者想让 Claude Fable 负责规划/验证，把实现环节交给 Codex agents 执行同一批 JavaScript workflow scripts，用来节省 Claude 额度并实践“loop engineering”。来源：[HN](https://news.ycombinator.com/item?id=48776386) / [GitHub](https://github.com/YuanpingSong/ultracodex)
- **EEBench 用物理仿真评测 AI 电路设计。** 任务要求 agent 提交可编译的电路设计源码，grader 跑 compiler checks 和波形仿真；frontier 模型约 45–72%，Claude Fable 5 为 71.7%，开源模型在 5–13%。来源：[HN](https://news.ycombinator.com/item?id=48766320) / [EEBench](https://www.eebench.org/)
- **Emra 把“AI 生成应用”放进共享数据库工作区。** 它像 Notion meets Lovable：每个生成 app 共用一层数据库和服务层，后续可互相交互；评论直接追问它与 Lovable 的差异，核心看点是数据可下载与平台锁定边界。来源：[HN](https://news.ycombinator.com/item?id=48778145) / [Emra](https://emra.app)
- **Cadreen 预览 memory、governance、tool execution 一体化 agent 基础设施。** 现有 API、TypeScript/Python/Go SDK、CLI 和审计轨迹，目标是让 agent 记忆、决策、请求权限和执行工具都可治理。来源：[HN](https://news.ycombinator.com/item?id=48780219)
- **Imagent 给 agent workflow 加统一多媒体生成接口。** 它把图片、视频、语音生成包装成同一接口，评论首先问视频生成成本是否应由用户自带 API key 控制，说明多模态 agent 的成本归属仍是产品设计问题。来源：[HN](https://news.ycombinator.com/item?id=48770383) / [GitHub](https://github.com/unliftedq/imagent)
- **TermRover 把移动端 SSH/tmux 做成 coding-agent 操作台。** iOS/Android 原生终端围绕 tmux sessions/windows 做快捷操作，付费项包括 agent workflow 的无限图片附件和 voice mode；Mosh 尚未支持。来源：[HN](https://news.ycombinator.com/item?id=48723755) / [TermRover](https://termrover.sh/)

## Claude Code

- **Claude Code 2.1.201 调整 Sonnet 5 会话的 harness 提醒方式。** Sonnet 5 会话不再用 mid-conversation system role 承载 harness reminders，依赖系统消息位置做测试或日志分析的团队需要重新核对行为。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.201)

- **2.1.200 把默认权限模式改成 Manual。** CLI、`--help`、VS Code 和 JetBrains 都把 “default” 指向手动确认；配置里可显式写 `--permission-mode manual` 或 `"defaultMode": "manual"`，自动化脚本要避免误以为默认会自动放行。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)

- **`AskUserQuestion` 现在默认不会无人响应后自动继续。** 2.1.200 需要在 `/config` 里主动开启 idle timeout；这能减少代理替用户做假设，但长任务编排要显式配置超时策略。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)

- **2.1.199 改进失败可见性：部分输出和子代理错误不会再被吞掉。** 中途 overloaded/server error 后已有流式内容会保留并标记 incomplete；subagent 遇到 rate limit、server error 或 usage limit 会把部分结果或错误回传给 parent。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.199)

- **2.1.199 支持最多 5 个连续 slash-skill 一次加载。** 形如 `/skill-a /skill-b do XYZ` 会加载所有前置技能，不再只执行第一个；适合把规范、测试、发布等技能组合进同一轮任务。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.199)

- **后台 agent 的守护进程和远程会话继续补可靠性。** 2.1.199 修复 Linux 异常关机后每约 50 秒杀掉全部 agent、macOS SSH 冷启动失败、`claude stop` 被 respawn 抵消；2.1.200 又修 stale `daemon.lock`、sleep/wake 后 mid-turn 停止和取消后重跑。 [Release 2.1.199](https://github.com/anthropics/claude-code/releases/tag/v2.1.199) · [Release 2.1.200](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)

- **插件、MCP 和可访问性也有小修。** 2.1.200 修复 worktree 中 project-scoped plugins 加载、`claude agents --plugin-dir <dir>` 参数位置问题，并改善 `/mcp` 列表焦点与 screen-reader 输出。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)

## Codex

- Codex 独立安装器现在复用一次 GitHub release metadata：`install.sh` / `install.ps1` 不再为版本、平台包、checksum 和 digest 连续打 4 次未认证 API；遇到 `403` 也会按 GitHub 可用性或限流报错，而不是误报“资产不存在”。来源：https://github.com/openai/codex/pull/31056

- 远程插件列表暴露版本信息：`PluginSummary.version` 表示远程 marketplace 公布的版本，`plugin/installed` 保留后端 release version，`localVersion` 继续表示本地已物化包版本，方便区分“远端可用”和“本地已装”。来源：https://github.com/openai/codex/pull/30981

- Codex Desktop 反馈附件修复 MIME 类型：路径上传的 gzip 日志包不再被标成 `text/plain`，未知二进制回落到 `application/octet-stream`，避免 Sentry 消费端按 UTF-8 解码后破坏日志 bundle。来源：https://github.com/openai/codex/pull/30796

- `0.143.0-alpha.35` 已发布，继 `alpha.33`、`alpha.34` 后继续提供 npm、wheel、macOS/Linux/Windows 二进制与 app-server 相关资产；release note 只有版本号，适合预发布通道用户做兼容性烟测。来源：https://github.com/openai/codex/releases/tag/rust-v0.143.0-alpha.35

- Codex 清理了遗留 `cliff.toml`：TypeScript CLI 时代的 `git-cliff` changelog 配置已不再被当前 Rust release workflow 使用，删除后可减少贡献者对发布流程的误判。来源：https://github.com/openai/codex/pull/31066

## OpenClaw

- OpenClaw `v2026.6.11` 稳定版补了一轮多渠道送达可靠性：Telegram、WhatsApp、Matrix、Google Chat、iMessage、Feishu 等都覆盖错投、重复、卡住和重连问题，适合运营多入口 agent 的团队升级验证。来源：https://github.com/openclaw/openclaw/releases/tag/v2026.6.11
- 该版本强化模型与 provider 恢复：Codex 用量限制、Claude CLI 额度耗尽、本地 provider 泛化失败、OpenRouter/Google catalog 异常等场景会更明确地 fallback 或 fail-safe，降低 agent run 直接中断的概率。来源：https://github.com/openclaw/openclaw/releases/tag/v2026.6.11
- 运维侧新增 `openclaw agent --message-file`、RAFT CLI wake bridge、Slack relay mode、Mattermost `/oc_queue`、per-DM 模型覆盖和 per-agent usage-cost 统计，重点是把远程唤醒、队列和成本核算做进正式工作流。来源：https://github.com/openclaw/openclaw/releases/tag/v2026.6.11

## GitHub AI 项目

- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)（23,473 stars）：OpenAI 开源 Claude Code 插件，让用户可在 Claude Code 内调用 Codex 做 code review 或任务委派，适合需要跨 coding agent 互审的团队试验。
- [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template)（25,385 stars）：这个模板把“用 AI coding agent 复刻网站”封成一条命令，适合前端原型、竞品拆解和 UI 迁移场景，但要注意授权与素材合规。
- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr)（11,014 stars）：herdr 是运行在终端里的 agent multiplexer，用来组织多个 agent 会话；对仍靠多终端手工切换的 coding-agent 工作流，是更轻量的控制台形态。
- [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)（126,741 stars）：agency-agents 提供一组带角色、流程和交付物定义的 AI 专家代理，从前端到社区运营都有模板；适合把一次性提示词沉淀成可复用角色库。
- [kunchenguid/no-mistakes](https://github.com/kunchenguid/no-mistakes)（5,140 stars）：no-mistakes 用“git push no-mistakes”包装提交前检查，切入点是减少 agent 或人类把低级错误推上远端，可作为轻量 pre-push 守门思路参考。
- [interviewstreet/hiring-agent](https://github.com/interviewstreet/hiring-agent)（4,586 stars）：hiring-agent 用 AI agent 评估和打分简历，适合观察招聘筛选自动化如何把评分规则、偏差控制和可解释性显式化。

## GitHub 趋势项目

- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)（23,475 stars）：OpenAI 的 Claude Code 插件让用户在 Claude Code 里调用 Codex 做 code review 或任务委派；对同时使用两套 coding agent 的团队，这是跨代理协作的官方入口。
- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr)（11,017 stars）：Herdr 是运行在终端里的 agent multiplexer，用来在一个界面里调度多个代理；适合评估多 agent 并行开发从“多个终端”收敛到统一操作层。
- [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template)（25,386 stars）：这个模板把“用 AI coding agent 克隆网站”封装成一条命令；前端 agent 工作流可参考它如何把抓取、生成和项目模板串成可重复流程。
- [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)（126,741 stars）：agency-agents 收集前端、社区、现实检查等多类专家代理角色；它的价值不在模型能力，而在把可复用角色、流程和交付物沉淀成 agent 配置资产。

## Rize AI 工具榜

- #2 OpenMontage：开源的 agentic 视频生产系统，包含 12 条 pipeline、52 个工具和 500+ agent skills，可把 AI 编程助手扩展成视频制作工作室；repo：https://github.com/calesthio/OpenMontage，榜单页：https://rize.io/ai-tools。
- #3 Anthropic-Cybersecurity-Skills：面向 AI agents 的 817 个结构化网络安全技能集，映射 MITRE ATT&CK、NIST CSF 2.0、MITRE ATLAS、D3FEND、NIST AI RMF 与 MITRE F3，支持 Claude Code、GitHub Copilot、Codex CLI、Cursor、Gemini CLI 等平台；repo：https://github.com/mukul975/Anthropic-Cybersecurity-Skills，榜单页：https://rize.io/ai-tools。
- #4 Vibe-Trading：定位为个人交易智能体（Personal Trading Agent）；repo：https://github.com/HKUDS/Vibe-Trading，榜单页：https://rize.io/ai-tools。
- #5 taste-skill：给 AI 增加“品味”约束的技能项目，目标是减少无聊、泛化的生成结果；repo：https://github.com/Leonxlnx/taste-skill，榜单页：https://rize.io/ai-tools。
- #6 omlx：面向 Apple Silicon 的 LLM 推理服务器，支持 continuous batching 与 SSD caching，并可从 macOS 菜单栏管理；repo：https://github.com/jundot/omlx，榜单页：https://rize.io/ai-tools。
- #7 agency-agents-zh：266 个即插即用 AI 专家角色，支持 Hermes Agent、Claude Code、Cursor、Copilot 等 18 种工具，覆盖工程、设计、营销、金融等 20 个部门，并可配合 agency-orchestrator 进行 DAG 协作；repo：https://github.com/jnMetaCode/agency-agents-zh，榜单页：https://rize.io/ai-tools。
- #8 Crucix：个人情报智能体，从多个数据源观察外部变化并在有变化时提醒用户；repo：https://github.com/calesthio/Crucix，榜单页：https://rize.io/ai-tools。
- #9 browser-harness：Browser Use 的自修复浏览器 harness，用于让 LLM 完成浏览器任务；repo：https://github.com/browser-use/browser-harness，榜单页：https://rize.io/ai-tools。

## Product Hunt 新品

- **Glaze by Raycast**：Raycast 推出用聊天生成 Mac app 的 Glaze，生成的应用会进 Dock、可离线运行，并能调用本机能力；适合观察“自然语言→个人桌面软件”的低代码边界。来源：[Product Hunt](https://www.producthunt.com/products/glaze-4?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Osloq**：面向 GitHub issue 的复现代理，会拉取仓库、启动 sandbox、运行项目并给出带步骤和证据的 bug 复现报告；对 coding agent 来说，价值在把“读代码猜测”推进到可运行验证。来源：[Product Hunt](https://www.producthunt.com/products/osloq?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Macuse**：原生 macOS 应用，把 Claude、Codex、Cursor、Raycast 或任意 MCP 客户端接到 Calendar、Mail、Notes、Reminders、Messages 和 Computer Use；风险点是本地权限边界要配置清楚。来源：[Product Hunt](https://www.producthunt.com/products/macuse?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场

- 7 月底“最佳 AI 模型公司”主市场继续押 Anthropic：当前 Anthropic 90.5%、Google 8.2%、OpenAI 1.1%；相比昨日 Anthropic 约 87.5%，集中度继续上升，但这是市场预期不是评测结论。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-july-299
- FrontierMath 90% 达标市场回落但仍偏乐观：2027 年前有模型达到 ≥90% 的 Yes 为 82.0%，30d 成交约 3.17 万、流动性约 1.30 万；昨日同题约 89.5%，短线波动较大。来源：https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027
- 7 月底“最佳中国 AI 公司”市场把 Alibaba 上调到 91.5%，DeepSeek 2.7%、Z.ai 2.5%；相比昨日 Alibaba 约 87.0%，国内模型预期进一步向阿里集中。来源：https://polymarket.com/event/best-chinese-ai-company-end-of-july
- 年底“最佳 AI 模型公司”市场没有像 7 月市场那样一边倒：Anthropic 63.5%、Google 14.0%、OpenAI 12.5%，流动性约 67.7 万；适合把短期榜单热度和全年模型路线预期分开看。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-2026
- 7 月底“最佳 Math AI 模型”仍押 Anthropic 85.5%，Google 11.5%、OpenAI 3.9%；相比昨日约 87.5% 略降，但本周仍显示大幅上行，数学能力预期仍集中在 Anthropic。来源：https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-july
