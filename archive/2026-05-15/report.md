# AI Agent 日报（2026-05-15）

## 天气
- **北京·海淀：小雨，19.6°C–31.9°C** 今天降水概率 72%、约 2.2 mm，东风最高 13.9 km/h；较昨天最高温再降约 2.6°C，但仍接近 32°C，外出带伞，午后注意防晒补水。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-15&end_date=2026-05-15)
- **上海·杨浦：阴，19.2°C–28.1°C** 今天降水概率 2%、0 mm，东南风最高 15.1 km/h；气温与昨天接近、降水信号明显减弱，通勤备伞优先级不高，体感仍偏暖。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-15&end_date=2026-05-15)

## X 推荐流

- **@OpenAIDevs：Codex 增加 hooks、可定制上下文与 GitHub Actions 支持** OpenAI Devs 称 Codex 可用脚本定制循环、配置 repo 级上下文，并在 GitHub Actions 中运行；团队可以把 lint、测试、部署前检查接进 coding-agent 工作流。 [原帖](https://x.com/OpenAIDevs/status/2055032115964870838)
- **@Kimi_Moonshot：Kimi Web Bridge 让 Agent 操作浏览器** Kimi 发布浏览器扩展 Web Bridge，称 Agent 可像人一样搜索、滚动和点击网页；这是 Kimi K2 后续把模型能力接到真实网页执行环境的具体产品化。 [原帖](https://x.com/Kimi_Moonshot/status/2054918374837322140)
- **@TencentAI_News：腾讯开源 Agent 记忆引擎** 腾讯团队称用 6 个月解决长会话丢上下文问题，开源 agent memory；中文转述补充其默认用 SQLite 与 sqlite-vec 做本地后端，可作为 OpenClaw 插件安装。 [英文原帖](https://x.com/TencentAI_News/status/2054822609863496178) / [中文转述](https://x.com/0xLogicrw/status/2054826520531882088)
- **@ClaudeDevs：Claude Code 强化长任务持续执行** ClaudeDevs 解释 Claude Code 如何让 Claude 持续工作到任务完成，并提到刚上线的一项相关能力；对长链路编码任务，关键是减少中途停下等待人工续推。 [原帖](https://x.com/ClaudeDevs/status/2054351031279186040)
- **@NousResearch：Hermes Agent 原生运行在 NVIDIA RTX PC 与 DGX Spark** Nous 称 Hermes Agent 已可在 NVIDIA RTX PC 和 DGX Spark 上原生运行，定位 always-on 工作负载；本地/边缘 agent 部署又多了一个 GPU 侧入口。 [原帖](https://x.com/NousResearch/status/2054703962121482622)
- **@tuturetom：html-anything 开源，把任意数据转成 HTML 展示** 作者称项目历时 3 天、约 1.5 万行代码，支持 75 套效果，让 Agent 把数据转成高质量 HTML；适合做报告、看板、结果页的可视化输出层。 [原帖](https://x.com/tuturetom/status/2054860276088860819)
- **@benhylak：本地 Agent 调试工具开放** 作者称做了一个本地调试 agent 的方式，可查看 traces，并让 Codex/Claude Code 也读到这些轨迹；这把“看不见 agent 为什么失败”的问题转成可审计日志。 [原帖](https://x.com/benhylak/status/2054987683928383872)
- **@bozhou_ai：InsForge 给 AI 编程智能体补后端** 帖子介绍 YC S26 项目 InsForge，Apache 开源，面向 AI 编程智能体处理数据库、登录、文件存储和权限；它瞄准的是前端生成容易、后端搭建卡人的断点。 [原帖](https://x.com/bozhou_ai/status/2054920165394161910)
- **@skirano：MagicPath 2.0 变成多人画布** MagicPath 2.0 宣称支持人类与 Codex、Claude Code 等 agent 在同一画布设计；设计协作从文本提示扩展到多人/多 agent 的可视化工作台。 [原帖](https://x.com/skirano/status/2054975534539370708)
- **@BTCqzy1：Claude Code 通过 MCP 接入 Financial Datasets** 帖子称 Claude Code 可经 MCP 连接 Financial Datasets，覆盖 17,000+ 股票、30+ 年财务底稿、SEC 原始文件等；这是 coding agent 通过 MCP 进入垂直金融数据源的例子。 [原帖](https://x.com/BTCqzy1/status/2054789148356366358)

## X 关注流

- **@OpenAI / @OpenAIDevs：Codex 进入 ChatGPT 手机 App 预览** OpenAI 称现在可在手机端启动新任务、查看输出并继续 Codex 工作；OpenAI Devs 补充 Codex 仍在电脑和文件上运行，手机更像远程控制与审批入口。 [OpenAI](https://x.com/OpenAI/status/2055016850849993072) / [OpenAI Devs](https://x.com/OpenAIDevs/status/2055016926213181608)
- **@dotey：Codex 手机端覆盖 iOS/安卓与免费用户** dotey 补充称 Codex in ChatGPT app 今日在 iOS 和安卓同步 preview，免费版和 Go 套餐也可用；增量是 Codex 从桌面/CLI 扩到大众 ChatGPT 入口。 [原帖](https://x.com/dotey/status/2055029251762422196)
- **@OpenAIDevs：Codex 增加 hooks 等自动化定制入口** OpenAI Devs 称 Codex 更容易围绕代码自动化和定制，hooks 可用脚本改造 Codex loop；这把 coding agent 从单次对话推进到可插入团队脚本和流程约束的运行环。 [原帖](https://x.com/OpenAIDevs/status/2055032115964870838)
- **@Dimillian：Codex mobile 的线程页与远程连接文档开始补齐** Dimillian 连发多条 Codex mobile 体验与设置说明，提到新线程页、remote connections 文档和使用技巧；发布后的重点从“能用”转向让移动端管理项目线程与远程开发环境。 [线程页](https://x.com/Dimillian/status/2055032081831334265) / [远程连接](https://x.com/Dimillian/status/2055022500828819836)
- **@steipete：mcporter 0.11.0 用作更稳定的浏览器自动化 CLI** steipete 发布 mcporter 0.11.0，并称主要拿它给 agent 测试浏览器场景；这类工具补的是 GUI/browser agent 的可重复控制层，而不是模型本身。 [原帖](https://x.com/steipete/status/2054986075232199038)
- **@aiedge_：xAI 推 Grok Build，把 Grok 带进桌面终端** 帖子称 Grok Build 可在 desktop terminal 里编码，并运行多个子任务；虽互动不高，但它是 Claude Code/Codex 之外又一个模型厂商把 coding agent 放进终端的信号。 [原帖](https://x.com/aiedge_/status/2055010653782659533)
- **@thdxr：GPT-5.5 caching 疑似导致用量放大 2.5 倍** thdxr 称 GPT-5.5 caching 出问题，图上看不明显但用量变成约 2.5 倍；对长上下文 agent，缓存异常会直接变成成本和延迟风险。 [原帖](https://x.com/thdxr/status/2055007370103681404)
- **@danshipper：组织是否“agent-pilled”取决于内部传播者** Dan Shipper 认为推动组织使用 agent 的领先指标，是团队里是否有人主动把工作流教给别人；企业落地不只是买工具，还要有人把可复用用法扩散到日常流程。 [原帖](https://x.com/danshipper/status/2055015466054410400)

## Reddit 社区

- **【工作流清单】1007 分帖把 Claude Code 日常用法压成 6 条：skills、`@`、`!`、短 `CLAUDE.md`、`AGENTS.md`、`/security`** 作者称重复流程应沉淀成 skill，并用精确描述让 Claude 自动触发；文件引用直接用 `@/path/to/file.ts`，测试/类型检查直接用 `!` 跑命令；`CLAUDE.md` 控制在约 200 行，只放业务上下文和内部规则，通用规范迁到可跨工具复用的 `AGENTS.md`。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sv852q/claude_code_cheat_sheet_after_6_months_of_daily/)
- **【订阅边界】338 分帖认为 24/7 agent loop 应从订阅池迁到 API** 讨论点不是“限额小气”，而是 Pro/Max 原本面向人机交互，OpenClaw、Ralph loops、多代理编排和长跑任务把非交互 token 消耗拉高；作者反对社区传播绕限额办法，认为如果 Agent SDK 单独计费会影响你，说明工作流本就更像生产/API 用量。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1tcpxi2/youre_abusing_your_subscription_with_agentic_247/)
- **【官方回应】1253 分帖转述 Anthropic：Claude Code/Cowork 改变了 Max 订阅的用量模型** Anthropic 称约 2% 新 prosumer signup 小范围测试，不影响现有 Pro/Max；Max 最初只按重度聊天设计，后来 Claude Code、Cowork 和数小时 async agents 被打包进来，订阅 engagement 明显上升，所以正在测试新的可持续方案，并承诺若影响老用户会提前通知。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1ss5fi4/anthropic_response_to_claude_code_change/)
- **【技能性价比】148 分帖用 880 次 eval 说明“便宜模型 + 好 skill”可胜过裸跑大模型** Tessl 作者披露 11 个 coding skills × 8 个模型 × 5 场景测试：Haiku 4.5 baseline 61.2%，加 skill 后 84.3%，超过 Opus 4.7 baseline 80.5%；单次 Haiku+skill 约 $0.12，对比裸 Opus $0.61，适合 commit message、code review、重构建议等例行任务。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1srpv7c/tested_9_models_with_and_without_agent_skills/)
- **【Claude vs Codex】158 分帖用两个实战任务比较 Opus 4.7 Claude Code 与 GPT-5.5 Codex** 作者同机同 prompt 同 MCP 测 PR triage bot 和实时 code review UI：Claude 先验证 MCP、12 分钟生成 36 文件、首跑零错误、约 $2.50；Codex 因 Cursor 环境没连上 GitHub MCP 导致任务 1 失败，任务 2 需修 React 无限循环，但架构更紧凑、约 $2.04。结论是复杂架构仍偏 Claude，紧凑自包含任务开始需要看 Codex 的价格压力。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1tcpe8y/i_tested_gpt55_codex_against_opus_47_claude_code/)
- **【成本警报】180 分求助帖显示小任务也可能烧到 12.8M input tokens / $40.78** 作者只是改 deploy script、变更 611 行，却因上下文持续膨胀产生高账单；结合近两天 CONTRACT.md、索引和短会话讨论，这条社区信号提醒重度 Claude Code 用户要主动清理上下文、缩短会话、显式指定文件和边界。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sztmrq/spent_40_on_a_single_claude_code_session_for_a/)

## Hacker News 热榜

- **拆掉 RAV4 调制解调器后，车联网隐私问题没有完全结束** #1 热帖 437 分、244 评论；作者实拆 2024 RAV4 Hybrid 的 modem/GPS，评论区很快把焦点转到“即使拆掉蜂窝模块，蓝牙/CarPlay/Android Auto 仍可能成为数据路径”。高赞质疑一边为隐私拆车、一边继续用 CarPlay；另有评论提醒 Apple/Google 车载系统本身也会拿到车辆遥测。对做移动端/车载 agent 或本机自动化的人，这是一个现实边界：禁掉设备内置网络，不等于切断所有遥测链路。 [Hacker News](https://news.ycombinator.com/item?id=48138136)
- **Amazonbot 开始尊重 robots.txt，但站长对 AI 爬虫的信任已经被消耗** #2 热帖 55 分、10 评论；外链称 Amazonbot 终于会按 robots.txt 行事，评论里站长反馈它此前持续抓取被 disallow 的天气站路径，最后只能在 AWS/WAF 里封掉 Amazon 自家的爬虫。讨论还追问电商公司为何要大规模 crawl 外部网站。对搜索、RAG、网页 agent 团队，信号是“合规抓取”已从礼貌问题变成站点运营者会直接封禁的信任问题。 [Hacker News](https://news.ycombinator.com/item?id=48140730)
- **macOS M5 首个公开 kernel memory corruption exploit：社区更担心 LLM 降低武器化门槛** #3 热帖 137 分、22 评论；Calif 团队发布 exploit 报告，评论虽然指出细节偏少、好奇漏洞如何穿过 MTE，但更大的讨论是 LLM 对安全研究/利用开发的放大效应，以及苹果 bug bounty 中如何定价这类成果。对安全 agent 观察者，这不是“模型发现漏洞”的单一故事，而是 exploit 研发、报告包装和赏金激励都在被自动化能力重塑。 [Hacker News](https://news.ycombinator.com/item?id=48139219)
- **M4 MacBook Air 外接 RTX 5090 的看点不只游戏，而是本地 LLM prefill 差距** #4 热帖 419 分、112 评论；文章测试 eGPU Mac 游戏，评论区反而抓住 LLM 基准：M4 MacBook Air 在 4K token prompt 上开始生成前要约 17 秒，而 eGPU 约 150ms，差约 120 倍。高赞评论指出 Mac 统一内存适合本地大模型，但长上下文 prompt processing/TTFT 经常被低估。对本地 agent 工作站，瓶颈可能不是能否装下模型，而是长上下文交互是否卡在 prefill。 [Hacker News](https://news.ycombinator.com/item?id=48137145)
- **Nginx-Rift 漏洞讨论提醒：有 ASLR 不等于可以不补丁** #5 热帖 221 分、53 评论；PoC 需要特定 rewrite 与 set 指令组合，且示例假设 ASLR 关闭，但安全从业者在评论中强烈反驳“ASLR 开着就没风险”的说法：writeup 声称可绕过 ASLR，而 LLM agent 正在降低补齐 bypass 的时间和技能门槛。对把 agent 接进运维/修复流程的团队，结论很直接：缓解措施买时间，不替代尽快 patch 和核查配置。 [Hacker News](https://news.ycombinator.com/item?id=48138268)
- **Codex 移动/桌面入口上 HN，用户关注点落在“免费、但不是 Linux App”** #7 热帖 47 分、13 评论；OpenAI 宣布 Work with Codex from Anywhere，评论里有人惊讶 Codex 桌面 app/CLI 可免费用，也有人失望这更像 Codex App 集成而不是 Codex Cloud 或 Linux 桌面支持。另有用户说自己已经用 Termius 在手机上远程让 agent 干活。对 coding-agent 产品，评论焦点已经从模型能力转到云端任务、移动 UI、CLI 和 Linux/远程开发入口的衔接。 [Hacker News](https://news.ycombinator.com/item?id=48140529)

## Hacker News 搜索

- **PlanBridge：把 coding-agent 计划审阅从终端搬到本地浏览器批注** Show HN 项目开源一个 CLI：通过 Claude Code 的 `ExitPlanMode` hook 或 Codex 的 `Stop` hook，在 agent 产出 markdown 计划时打开本地渲染页，用户可选中文本写 inline comments，再把结构化、锚定的反馈回传给 agent 修订或批准后开工。作者的问题定义很具体：终端里滚动读计划、把反馈塞进单个聊天框，会让工程师接受“差不多”的计划，后面再用时间和 token 清理 code slop。当前 HN 互动不高（4 分、0 评论），但它对应的是“先把计划审准，再让 agent 写代码”的工具层补位。 [Hacker News](https://news.ycombinator.com/item?id=48139177) / [GitHub](https://github.com/contextbridge/planbridge)
- **Ask HN：如果 AI 写代码更快，手写代码还剩什么价值？** 讨论帖把问题限定在“AI 完成多数代码改动总体更快”的假设下，提出两类保留手写代码的理由：一是通过亲手写形成对代码的 embodied understanding，避免只审阅生成结果时漏掉某些错误；二是经济现实中一部分资深开发者未必会完全转向跑 agent。评论虽少，但方向清楚：有人认为未来最多写伪代码，也有人强调关键基础设施、固件和会造成现实伤害的软件仍会长期需要人类直接掌控，vibe coding 不适合这类边界。 [Hacker News](https://news.ycombinator.com/item?id=48140228)
- **JDS：给 Copilot 加 skill 化纪律，强制 think → plan → execute** Show HN 作者受 `obra/superpowers` 启发，为 GitHub Copilot 做了一套 skill suite；它不追求换模型，而是通过严格阶段管线防止 agent 跳步骤、跑偏或长会话失焦，并利用 Copilot 内置 SQL todo dependencies 与 live task graph 可视化 workflow 并行关系。这个项目的信号是：coding agent 生态继续从“提示词技巧”转向可安装的流程约束、任务图和技能包。 [Hacker News](https://news.ycombinator.com/item?id=48140677) / [GitHub](https://github.com/josipmusa/jds)
- **Conductor：微软开源博客强调多代理工作流要“确定性编排”** HN 搜索收录微软开源博客《Deterministic orchestration for multi-agent AI workflows》，分数和评论都很低（1 分、0 评论），但主题与近期社区焦点一致：多 agent 不是简单并发聊天，而需要可复跑、可观测、可约束的 orchestrator。可作为观察项：大厂正在把 agent workflow 的卖点从“自治”拉回到 deterministic control。 [Hacker News](https://news.ycombinator.com/item?id=48137833) / [Microsoft Open Source](https://opensource.microsoft.com/blog/2026/05/14/conductor-deterministic-orchestration-for-multi-agent-ai-workflows/)
- **Claude Design 开源替代仍缺“成品 polish”共识** Ask HN 用户寻找 Claude Design 的可用开源替代，提到试用 OpenDesign + GPT-5.5 后，视觉一致性和 polish 仍达不到 Claude Design。该帖还没有评论，但和昨天“退订后项目访问/导出”争议构成同一条线：用户一边担心闭源 SaaS 的项目历史、订阅和 credits 绑定，一边发现开源替代在设计质量上还未完全补位。 [Hacker News](https://news.ycombinator.com/item?id=48140859) / [OpenDesign](https://github.com/nexu-io/open-design)

## Claude Code

- **v2.1.141：hooks、插件安装、workload identity 与 `claude agents` 继续补齐实用边界** 新版给 hook JSON 输出新增 `terminalSequence`，让无控制终端的 hooks 也能触发桌面通知、窗口标题和 bell；新增 `CLAUDE_CODE_PLUGIN_PREFER_HTTPS`，便于无 GitHub SSH key 的环境用 HTTPS clone 插件；新增 `ANTHROPIC_WORKSPACE_ID`，在 workload identity federation 规则覆盖多个 workspace 时把 minted token 限定到指定 workspace；`claude agents --cwd <path>` 可按目录过滤会话列表，后台 agent 也会保留当前 permission mode。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.141) / [Changelog](https://github.com/anthropics/claude-code/blob/HEAD/CHANGELOG.md)
- **v2.1.141：一大批真实工作流 bug 修复，重点在后台代理、MCP、权限弹窗和终端交互** 修复 Bedrock/Vertex/Foundry/gateway 下 background side-query 在没有 `ANTHROPIC_SMALL_FAST_MODEL` 时误发不可用 Haiku model ID，改为回退主循环模型；`claude daemon status` 和 `/doctor` 在 Windows daemon pipe key file 被锁/不可读时不再抛 opaque failure；`claude agents` 修复 wrapper flags 入口、crashed session、pre-warmed worker unhealthy、空闲 background REPL 占位会话等问题。MCP 侧还修了 HTTP/SSE 403 应显示 “needs auth”、server-events stream 失败不应断开 POST tool calls、Remote Control token rotation 401、`.mcp.json` malformed entry 不应拖垮其他 server 等边界。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.141)
- **v2.1.141：交互体验修复覆盖输入历史、diff、状态行、VS Code 语音和 SDK 包装** 新增 rewind 菜单 “Summarize up to here”，压缩早期上下文同时保留近期 turns；长思考 spinner 10 秒后变 amber；恢复 connected IDE 下 file-edit permission prompt 的 “view diff in your IDE”。同时修复 Ctrl+C 在 vim INSERT/VISUAL mode 不能打断、重绑定 Enter 后 `meta+enter`/`ctrl+enter` 不生效、markdown table wrap 退化、multi-line statusline 宽行损坏、Windows Alt+V screenshot paste 报无图、Linux 同时安装 glibc/musl 包时 SDK 找不到 native binary，以及 Bedrock `awsCredentialExport` 在跨账号场景被跳过。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.141)

## Codex

- **企业 ChatGPT 工作区限制从单 workspace 扩到 allowlist** #18161 让 `forced_chatgpt_workspace_id` 在保持旧 key 名的同时接受多个 workspace ID，并兼容 `config.toml` 里的单字符串配置；登录强制、app-server config surfaces 和本地 ChatGPT auth helper 都会把它规范化为允许工作区列表。服务端登录流也改为把 allowlist 作为逗号分隔的 `allowed_workspace_id` query 参数发送，适合一个部署允许多个 ChatGPT workspace、但仍保留组织边界的场景。 [PR](https://github.com/openai/codex/pull/18161)
- **MCP OAuth 支持显式 public client ID，兼容不能动态注册的 provider** #22575 在 `[mcp_servers.<server>]` 下新增 `oauth.client_id`，并贯穿 CLI、app-server、plugin login、MCP skill dependency OAuth 入口和 RMCP 授权；未配置时继续走既有 dynamic registration。配置编辑、schema、解析/序列化与 OAuth URL 生成也补了测试；原始验证同时提到更大范围本地包测试仍受两个既有 stack overflow 噪声影响。 [PR](https://github.com/openai/codex/pull/22575)
- **SIWC 用户模型列表优先使用后端返回值，避免 bundled list 暴露不可用模型** #22547 调整 model list merge/cache 逻辑：对 SIWC 用户，后端抓取的模型列表优先于随包模型列表，覆盖“用户只被允许使用更少模型”的特殊授权场景；相关单测在 `codex-rs/models-manager/src/manager_tests.rs` 更新，但 raw 标注未运行完整测试。 [PR](https://github.com/openai/codex/pull/22547)
- **TUI 网络审批历史改为按 target 渲染，不再留下空 command 文案** #22229 修复 app-server 路径下 network approval 没有 command string 时，历史记录出现 `You approved codex to run  every time this session` 这类破损文本的问题。现在审批记录会保留 subject 是 command 还是 network target，并覆盖 approve once / approve session / cancel；managed-proxy `network-access` target、协议与非默认端口（如 `https://example.com:8443`）都会进入 transcript。 [PR](https://github.com/openai/codex/pull/22229)
- **Git metadata/status 子进程忽略仓库 `core.fsmonitor`，减少状态读取被本地配置污染** #22652 让 Codex 的 Git metadata/status helper 不受 repo 自定义 fsmonitor command 影响，同时保留既有 working-tree state reporting；新增 `get_has_changes` 遇到 fsmonitor 配置的回归覆盖。对开启 watchman/fsmonitor 的大仓库，重点是让 Codex 判断“有无改动”更可预测。 [PR](https://github.com/openai/codex/pull/22652)
- **测试与远程环境 fixtures 继续去宿主状态化** #22563 给 live CLI 子进程设置临时 `HOME` 和 `CODEX_HOME`，并把 arg0 alias 状态放到显式 home，避免 `HOME=/tmp` 时在宿主 `/tmp/.codex` 留状态；#22512 让 exec review policy 测试禁用 host-managed config，避免企业托管配置影响本地测试；#22572 修正 remote-env 测试同时选择 `local`/`remote`、approval 缓存和 `view_image` PNG fixture，5 个 Docker remote-env 定向测试通过。 [#22563](https://github.com/openai/codex/pull/22563) / [#22512](https://github.com/openai/codex/pull/22512) / [#22572](https://github.com/openai/codex/pull/22572)
- **插件 CLI 编译修复跟进 profile-aware config API** #22666 把 `codex plugin marketplace list` 和插件 snapshot validation helper 从已移除的 `ConfigLayerStack::get_user_layer()` 改到 `get_active_user_layer()`，恢复 `main` 编译，并保留“当前 active writable user layer”的语义；验证包括 `cargo check -p codex-cli` 与 `cargo test -p codex-cli --test plugin_cli`。 [PR](https://github.com/openai/codex/pull/22666)
- **release 工作流改用 environment secret，alpha 线继续滚到 0.131.0-alpha.18** #22702 为 `rust-release-prepare` 建 environment，把所需 API key 放到环境 secret 而不是 action secret，作者计划确认可用后移除 action secret；同日 raw 出现 `rust-v0.131.0-alpha.16` 与 `alpha.18`，release note 仍只有版本号，但资产继续覆盖 Codex CLI、app-server、responses-api-proxy、Windows sandbox setup、bwrap、command-runner、config-schema 等多平台构件。 [PR](https://github.com/openai/codex/pull/22702) / [alpha.16](https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.16) / [alpha.18](https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.18)

## OpenClaw

- **2026.5.14-beta.1 继续把 OpenClaw 与 Codex app-server 深度合流** 新预发布移除 bundled `codex-cli` backend，将 legacy `codex-cli/*` model refs 修到 `openai/*` 的 Codex app-server route，并新增 node-backed Codex CLI session listing/binding，让 OpenClaw 对话可继续已在 paired node 上运行的 Codex CLI session；相比昨天覆盖的 Codex MCP 投射与认证修复，今天更像迁移到 app-server/节点会话统一路径。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1)
- **通道运行态从“发消息”升级到更完整的生命周期反馈** WhatsApp 接入 `StatusReactionController`，把 queued、thinking、tool、done/error 等状态用默认 emoji 反应呈现，并新增 deploy/build/concierge 等工具类别；Telegram 同时把 isolated polling 扩展到 topics、DM、status/control commands 并发 drain，Mini App `web_app` buttons 也可通过 presentation payload 渲染。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1)
- **发布与依赖风险管理明显加强** 5.14-beta.1 加入 release dependency evidence reports、npm advisory gating、PR dependency-change awareness，并让 CI 拒绝新增 package patch files 或 pnpm patched dependencies；还新增多条 package-installed Docker user-journey/release validation lane，覆盖 onboarding、外部插件安装卸载、消息、Gateway 重启和 doctor。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1)
- **2026.5.12 稳定版把前几轮 beta 收敛成一次大版本：核心安装更瘦、Telegram 更稳、插件更新更难卡死** Highlights 明确把 WhatsApp、Slack、Amazon Bedrock、Anthropic Vertex 等 provider/plugin dependency cones 移出 core runtime；Telegram 获得隔离轮询、本地 durable spool、群媒体过滤和 HTML/Markdown 格式保留；插件安装/更新则补 pnpm 11、peer dependency preservation、runtime scan 与 source/git install 修复。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.12)
- **Control UI 与子代理可审计性继续补体验细节** 5.14-beta.1 增加浏览器本地 Text size 设置，避免移动 Safari focus zoom，同时把 native `sessions_spawn` 任务放进子会话第一条可见 `[Subagent Task]` 消息，而不是藏在 sub-agent system prompt；这让委派内容可审计，也减少重复 token。 [Release](https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1)

## GitHub AI 项目

- **PlanBridge：把 coding agent 的计划审阅从终端搬到本地浏览器批注** `contextbridge/planbridge` 是开源 CLI：通过 Claude Code 的 `ExitPlanMode` plugin hook 或 Codex 的 Stop hook，在本地浏览器渲染 markdown plan，用户可选中文本做内联评论、要求修改或批准后再让 agent 开始编码；重点是把“计划阶段的精确反馈”结构化，减少后面清理代码垃圾的时间和 token。 [GitHub](https://github.com/contextbridge/planbridge) / [HN](https://news.ycombinator.com/item?id=48139177)
- **JDS：给 GitHub Copilot 做的 skill suite，用 think → plan → execute 约束长任务** `josipmusa/jds` 受 `obra/superpowers` 启发，面向 Copilot 强制执行技能化流程，避免 agent 长会话跑偏；它还利用 Copilot 内置 SQL todo 依赖，并提供 live task graph visualizer 来看 agentic workflow 与并行关系。 [GitHub](https://github.com/josipmusa/jds) / [HN](https://news.ycombinator.com/item?id=48140677)
- **9router：把 Claude Code、Codex、Cursor、Cline 等接到 40+ 免费模型提供方** `decolua/9router` 本周进入 GitHub Trending，标语是“Unlimited FREE AI coding”，主打把多种 coding-agent 客户端路由到 Claude/GPT/Gemini 等 provider，并提供自动 fallback、RTK 降 token 等能力；适合关注“模型/额度路由层”如何被封装进开发工具链的人跟踪，但需自行核验 provider 合规与稳定性。 [GitHub](https://github.com/decolua/9router)
- **local-deep-research：本地优先的 deep research/RAG 工作流** `LearningCircuit/local-deep-research` 预览称可在 3090 上用 Qwen3.6-27B 达到约 95% SimpleQA，支持 llama.cpp、Ollama、Google 等本地/云模型，以及 arXiv、PubMed、私有文档等 10+ 搜索源；对研究型 agent，信号是 deep research 正在被做成可本地运行、可接私有资料的开源栈。 [GitHub](https://github.com/LearningCircuit/local-deep-research)
- **OpenDesign：HN 用户把它作为 Claude Design 开源替代试用，但成熟度仍待验证** HN 问答帖提到 `nexu-io/open-design` 是正在尝试的开源 Claude Design 替代，作者反馈用 GPT-5.5 时“还达不到 Claude Design 的 polish/consistency”；证据不是发布帖，而是早期替代品线索，适合只作为设计类 agent/open-source UI 生成方向的观察项。 [GitHub](https://github.com/nexu-io/open-design) / [HN](https://news.ycombinator.com/item?id=48140859)

## GitHub 趋势项目

- **9router：把多个 AI 编码入口接到 40+ 免费模型提供商** `decolua/9router` 本周 Trending，描述称可连接 Claude Code、Codex、Cursor、Cline、Copilot、Antigravity 到 Claude/GPT/Gemini 等 40+ providers，并提供自动 fallback、RTK 节省 token、规避用量限制。对重度 coding-agent 用户，它对应的是“模型路由/额度管理”层，而不是又一个编辑器插件。 [GitHub](https://github.com/decolua/9router)
- **local-deep-research：本地优先的深度研究代理栈** `LearningCircuit/local-deep-research` 预览称可在本地 3090 上用 Qwen 等模型达到约 95% SimpleQA，支持 llama.cpp、Ollama、Google 等本地/云 LLM，并接入 arXiv、PubMed、私有文档等 10+ 搜索源。对研究型 agent，重点是把检索、私有资料和本地模型组合成可离线/可控的 deep research 工作流。 [GitHub](https://github.com/LearningCircuit/local-deep-research)

## Product Hunt 新品

- **Open Computer Use** 是面向 AI agents 的开源 Computer Use MCP；看点是把桌面/计算机操作能力做成 MCP 组件，而不是绑定在单个闭源 agent 产品里，适合关注本地 GUI 自动化、权限边界和可替换模型栈的团队跟踪。 [Product Hunt](https://www.producthunt.com/products/open-computer-use?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Open Browser Use** 主打给本地 AI agents 的开源浏览器自动化；和通用 computer-use 相比，它更聚焦网页任务执行，可作为 Rotunda、Playwright/CDP 和浏览器 agent 工作流之外的新品观察项。 [Product Hunt](https://www.producthunt.com/products/open-browser-use?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Raindrop Workshop** 是开源、免费、本地运行的 AI agent debugger；它把 agent 开发痛点从“能否执行任务”推进到“如何本地调试、复现和观察执行过程”，适合做多工具/多步骤代理的开发者试用。 [Product Hunt](https://www.producthunt.com/products/raindrop?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场

- **5 月最佳 AI 模型主市场从昨日高位回落到 Anthropic 80.5%** “5 月底最佳 AI 模型”当前给 Anthropic 80.5%、Google 18.5%、OpenAI 1.2%，24h 成交约 48.68 万、30d 成交约 671.35 万、流动性约 226.82 万；相比昨日 Anthropic 86.5%明显下修、Google 从 10.5%抬到 18.5%，市场仍押 Anthropic 领先，但短线分歧回到 Google 追赶。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may)
- **6 月最佳 AI 模型预期同步降温：Anthropic 66.1%、Google 23.5%** “6 月底最佳 AI 模型”给 Anthropic 66.1%、Google 23.5%、OpenAI 7.5%，24h 成交约 7.33 万、30d 成交约 252.10 万、流动性约 83.10 万；相比昨日 Anthropic 73.0%回落、Google 从 16.0%升到 23.5%，说明远月市场也在重新给 Google 追赶留空间。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)
- **5 月 Style Control On 榜单仍偏向 Anthropic：77.0%** “5 月底 #1 AI model（Style Control On）”给 Anthropic 77.0%、Google 18.0%、OpenAI 1.2%，24h 成交约 7.21 万、30d 成交约 38.79 万、流动性约 18.39 万；与主市场同向，Anthropic 领先但不是昨日那种接近锁定的定价。 [Polymarket](https://polymarket.com/event/which-company-has-the-1-ai-model-end-of-may-style-control-on)
- **OpenAI GPT 的 FrontierMath 60% 线继续小幅升到 66.0%** “6 月底前任一 OpenAI GPT 模型 FrontierMath 至少 60%”当前 66.0%，70% 线为 25.1%，30d 成交约 1.44 万、流动性约 1508，且本周上行 43.0%；相比昨日 64.5%只是小幅上修，但数学 benchmark 预期仍是今日较强信号。 [Polymarket](https://polymarket.com/event/openai-gpt-score-on-frontiermath-benchmark-by-june-30)
- **Claude 的 FrontierMath 50% 线升到 54.5%，仍接近五五开** “6 月底前任一 Anthropic Claude 模型 FrontierMath 至少 50%”当前 Yes 54.5%、No 45.5%，30d 成交约 5.19 万、流动性约 1816，本周上行 22.0%；它和 OpenAI 60% 线一起显示市场在给前沿数学能力重新加价，但仍只是预期不是成绩确认。 [Polymarket](https://polymarket.com/event/anthropic-claude-score-on-frontiermath-benchmark-by-june-30)

## 来源
### 天气
- https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-15&end_date=2026-05-15
- https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-15&end_date=2026-05-15
### X 推荐流
- https://x.com/OpenAIDevs/status/2055032115964870838
- https://x.com/Kimi_Moonshot/status/2054918374837322140
- https://x.com/TencentAI_News/status/2054822609863496178
- https://x.com/0xLogicrw/status/2054826520531882088
- https://x.com/ClaudeDevs/status/2054351031279186040
- https://x.com/NousResearch/status/2054703962121482622
- https://x.com/tuturetom/status/2054860276088860819
- https://x.com/benhylak/status/2054987683928383872
- https://x.com/bozhou_ai/status/2054920165394161910
- https://x.com/skirano/status/2054975534539370708
- https://x.com/BTCqzy1/status/2054789148356366358
### X 关注流
- https://x.com/OpenAI/status/2055016850849993072
- https://x.com/OpenAIDevs/status/2055016926213181608
- https://x.com/dotey/status/2055029251762422196
- https://x.com/OpenAIDevs/status/2055032115964870838
- https://x.com/Dimillian/status/2055032081831334265
- https://x.com/Dimillian/status/2055022500828819836
- https://x.com/steipete/status/2054986075232199038
- https://x.com/aiedge_/status/2055010653782659533
- https://x.com/thdxr/status/2055007370103681404
- https://x.com/danshipper/status/2055015466054410400
### Reddit 社区
- https://www.reddit.com/r/ClaudeAI/comments/1sv852q/claude_code_cheat_sheet_after_6_months_of_daily/
- https://www.reddit.com/r/ClaudeAI/comments/1tcpxi2/youre_abusing_your_subscription_with_agentic_247/
- https://www.reddit.com/r/ClaudeAI/comments/1ss5fi4/anthropic_response_to_claude_code_change/
- https://www.reddit.com/r/ClaudeAI/comments/1srpv7c/tested_9_models_with_and_without_agent_skills/
- https://www.reddit.com/r/ClaudeAI/comments/1tcpe8y/i_tested_gpt55_codex_against_opus_47_claude_code/
- https://www.reddit.com/r/ClaudeAI/comments/1sztmrq/spent_40_on_a_single_claude_code_session_for_a/
### Hacker News 热榜
- https://news.ycombinator.com/item?id=48138136
- https://news.ycombinator.com/item?id=48140730
- https://news.ycombinator.com/item?id=48139219
- https://news.ycombinator.com/item?id=48137145
- https://news.ycombinator.com/item?id=48138268
- https://news.ycombinator.com/item?id=48140529
### Hacker News 搜索
- https://news.ycombinator.com/item?id=48139177
- https://github.com/contextbridge/planbridge
- https://news.ycombinator.com/item?id=48140228
- https://news.ycombinator.com/item?id=48140677
- https://github.com/josipmusa/jds
- https://news.ycombinator.com/item?id=48137833
- https://opensource.microsoft.com/blog/2026/05/14/conductor-deterministic-orchestration-for-multi-agent-ai-workflows/
- https://news.ycombinator.com/item?id=48140859
- https://github.com/nexu-io/open-design
### Claude Code
- https://github.com/anthropics/claude-code/releases/tag/v2.1.141
- https://github.com/anthropics/claude-code/blob/HEAD/CHANGELOG.md
### Codex
- https://github.com/openai/codex/pull/18161
- https://github.com/openai/codex/pull/22575
- https://github.com/openai/codex/pull/22547
- https://github.com/openai/codex/pull/22229
- https://github.com/openai/codex/pull/22652
- https://github.com/openai/codex/pull/22563
- https://github.com/openai/codex/pull/22512
- https://github.com/openai/codex/pull/22572
- https://github.com/openai/codex/pull/22666
- https://github.com/openai/codex/pull/22702
- https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.16
- https://github.com/openai/codex/releases/tag/rust-v0.131.0-alpha.18
### OpenClaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.5.14-beta.1
- https://github.com/openclaw/openclaw/releases/tag/v2026.5.12
### GitHub AI 项目
- https://github.com/contextbridge/planbridge
- https://news.ycombinator.com/item?id=48139177
- https://github.com/josipmusa/jds
- https://news.ycombinator.com/item?id=48140677
- https://github.com/decolua/9router
- https://github.com/LearningCircuit/local-deep-research
- https://github.com/nexu-io/open-design
- https://news.ycombinator.com/item?id=48140859
### GitHub 趋势项目
- https://github.com/decolua/9router
- https://github.com/LearningCircuit/local-deep-research
### Product Hunt 新品
- https://www.producthunt.com/products/open-computer-use?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
- https://www.producthunt.com/products/open-browser-use?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
- https://www.producthunt.com/products/raindrop?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29
### Polymarket 市场
- https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may
- https://polymarket.com/event/which-company-has-best-ai-model-end-of-june
- https://polymarket.com/event/which-company-has-the-1-ai-model-end-of-may-style-control-on
- https://polymarket.com/event/openai-gpt-score-on-frontiermath-benchmark-by-june-30
- https://polymarket.com/event/anthropic-claude-score-on-frontiermath-benchmark-by-june-30
