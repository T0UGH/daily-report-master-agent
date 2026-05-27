# AI Agent 日报（2026-05-28）

## 天气

- **北京·海淀：晴间多云，19.2°C–28.4°C。** 降水概率 0%、预计 0 mm，西北风最高 20 km/h；比昨天继续升温且更干，白天偏热，通勤无需雨具，注意防晒和补水。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-28&end_date=2026-05-28)
- **上海·杨浦：小毛毛雨，22°C–28°C。** 降水概率 76%、预计 2.6 mm，北风最高 12.8 km/h；相比昨天雨量增加、气温略降，出门带伞，路面湿滑但风不大。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-05-28&end_date=2026-05-28)

## X Feed

1. OpenAI Devs 提到 Private MCP servers 可与 ChatGPT、Codex 等 OpenAI 产品配合，同时把 MCP 服务保留在团队内网。对企业 agent 落地，这比“多接一个工具”更关键：私有工具、数据边界和产品内 agent 正在开始被统一打通。  
   https://x.com/OpenAIDevs/status/2059703536825565499

2. Antigravity 2.0 列出 subagents、异步任务管理、定时任务、JSON Hooks 和语音等能力。昨天已写过 Antigravity CLI，今天的新信号是它继续从单入口 agent 走向可编排、可后台运行、可事件触发的工作台。  
   https://x.com/antigravity/status/2059706922312335505

3. Nous Research 宣布 Hermes Agent 内置 MCP Catalog。对本地/多渠道 agent 用户，MCP 发现和安装开始从“自己找 server、手写配置”变成执行器内的目录能力，降低工具生态接入成本。  
   https://x.com/NousResearch/status/2059638198075109769

4. Claude 官方称 Claude Marketplace 新增 Augment Code、Bolt、CodeRabbit、Hebbia、Legora 等伙伴。Claude 正把外部开发、代码审查、法律/知识工作工具纳入 Marketplace，插件/应用分发层的重要性继续上升。  
   https://x.com/claudeai/status/2059662933924123044

5. opencode 宣布 Qwen3.7 Max 已可用，当前为 text-only、1M context，并称其是 Qwen 家族最强模型。对 agent 工具来说，长上下文模型正在更快进入第三方执行器，模型切换不再只依赖官方聊天入口。  
   https://x.com/opencode/status/2059335771002114462

6. Nous Research 还宣布 Krea 已内置为 Hermes Agent 的图像生成 API provider，可让 agent 调用 Krea 2。这个方向说明 agent 工具调用正在从文本/代码外扩到多模态生产，图像生成也会成为可编排能力的一部分。  
   https://x.com/NousResearch/status/2059730199344816407

7. MiniMax 官方表示 M2 系列收尾，MiniMax-M3 即将到来。原帖信息很短，但来自官方账号且互动高，适合作为国产模型迭代节奏信号；真正落地还要等 M3 的能力、价格和 API 细节。  
   https://x.com/MiniMax_AI/status/2059473229253902516

8. @_LuoFuli 解释 MiMo API 降价，最大 99% 降幅集中在 Input Cache Hit。对长上下文 agent 和反复读项目的 coding workflow，缓存命中价格比标称输出价更影响持续运行成本。  
   https://x.com/_LuoFuli/status/2059618247553745204

9. @dotey 认为只有具备明确、可程序化验收标准的 Skills 才更适合自我进化，例如性能优化可用测试样例衡量。这个判断把 skill 优化从口号拉回评测：没有验收标准的 skill 很难安全自动改写。  
   https://x.com/dotey/status/2059434459783389397

10. @steipete 推荐 autoreview skill，称其会自动审查代码并给出反馈，是其 stack 中影响最大的 skill 之一。与昨日“写短 skill”讨论相比，这条增量在于验证类 skill 正成为 coding-agent 日常循环里的高价值组件。  
   https://x.com/steipete/status/2059453909819654554

## X 关注

- **Claude Marketplace 新增 Augment Code、Bolt、CodeRabbit、Hebbia、Legora 等连接。** Claude 官方强调可把现有订阅和账号接入 Claude；对开发者而言，IDE 编码、代码审查、法律/研究工具正在被打包成 Claude 工作区里的可调用服务。https://x.com/claudeai/status/2059662933924123044

- **OpenAI Devs 宣布 private MCP servers 可接入 ChatGPT、Codex 等产品，同时留在团队内网。** 这把 MCP 从本地/开源玩具推进到企业网络边界内的连接层；关键看点会是身份、审计、工具权限和数据不出网的落地方式。https://x.com/OpenAIDevs/status/2059703536825565499

- **Antigravity 2.0 列出 subagents、异步任务、scheduled tasks、JSON hooks、voice 等能力。** 相比昨日 CLI 信号，这条给出更完整产品方向：agent IDE 正在把多代理、后台任务和事件钩子做成一套常驻工作流。https://x.com/antigravity/status/2059706922312335505

- **Greg Brockman 提到 “bring-your-own MCP servers”，并单独展示 Codex 的并行浏览器 subagents。** 这两条连在一起看，OpenAI 正把 Codex 从单会话 coding assistant 推向可接私有工具、可并行使用浏览器的 agent 执行环境。https://x.com/gdb/status/2059733344783630352 / https://x.com/gdb/status/2059735815262249392

- **Nous Research 宣布 Krea 已内置到 Hermes Agent，作为图像生成 API provider，可调用 Krea 2。** 这让 Hermes 不只跑文本/代码任务，也能把图像生成纳入同一套 agent 工具链；适合需要自动产出视觉素材、报告配图或多模态工作流的用户试验。https://x.com/NousResearch/status/2059730199344816407

- **RepoPrompt 作者 Eric 被 OpenAI 招入，dotey 补充称 RepoPrompt 现在免费、即将开源，付费用户会获 Codex credits。** 这不是普通招聘：围绕代码库上下文打包、选择和提示的产品经验，正在被吸收到 Codex 生态里。https://x.com/dotey/status/2059729329119006928

- **thdxr 说 Codex subscription endpoints 过去一周不稳定，OpenCode 出现 stalling，并已切到更可靠的 API endpoint。** 这条提醒多模型 agent 客户端：订阅端点和 API 端点的可靠性可能不同，生产化使用要有路由、降级和故障观测。https://x.com/thdxr/status/2059701453925552609

- **dotey 区分“以人为主、Agent 辅助”和“以 Agent 为主”的产品布局。** 他认为前者应让工作区居中、Agent 在侧边辅助；后者则要把任务、执行区和结果审核重新组织，适合做 agent 产品原型时校准信息架构。https://x.com/dotey/status/2059666423538983242

- **Nathan Lambert 判断 continual learning 近几年最可能先出现在知识工作产品里。** 对 agent 用户，这意味着长期记忆不会只表现为模型权重更新，更可能先落在文档、项目上下文、企业知识库和工作流反馈的产品层。https://x.com/natolambert/status/2059676112415035527

## Reddit 社区

- **Claude Code 一次“小任务”烧到 12.8M input tokens、40.78 美元，社区把问题归到长会话上下文膨胀。** 发帖者只改部署脚本、611 行代码却账单失控，讨论焦点是清上下文、缩短 session、显式限制读取范围和把成本当作工作流约束，而不是事后才看 token。来源：[Spent $40 on a single Claude Code session](https://www.reddit.com/r/ClaudeAI/comments/1sztmrq/spent_40_on_a_single_claude_code_session_for_a/)

- **“道歉不是修复，架构才是修复”这条 agent 失败复盘，得到不少实践者共鸣。** 帖主认为模型承认错误不会改变下次行为，必须把失败模式转成代码校验、执行边界、验收测试或外部 guardrail；这比继续优化提示词更接近工程治理。来源：[Opus reframed AI agent failures](https://www.reddit.com/r/ClaudeAI/comments/1t9ak8o/opus_said_something_today_that_completely/)

- **高赞工作流帖反驳“Claude 变差”，核心建议是把 AI 代码当成自己负责的代码。** 作者强调 human review 是瓶颈，AI 适合生成候选实现、ASM 分析和算法推理，但确定性工作不该交给无监督 agent；他的做法是 skills/harness 补上下文、并行 sandbox/worktree，再人工审查和手改。来源：[tf are y’all’s workflows?](https://www.reddit.com/r/ClaudeAI/comments/1t9fyns/i_read_threads_complaining_about_claude_every/)

- **“Claude 自己低估任务可做性”的讨论暴露了 coding agent 的另一类失败：不是做不到，而是默认给保守 quick fix。** 用户抱怨 Claude 会说某任务需数周，于是建议短平快方案；可操作的启发是把目标、允许改动范围和验收标准写清，否则模型会用传统人力工期去压低方案野心。来源：[Claude limits itself by claiming tasks take weeks](https://www.reddit.com/r/ClaudeAI/comments/1t77r81/when_using_claude_code_for_agentbased_coding_ive/)

- **“最大 entirely vibe-coded app 是什么”这个问题，把社区从 demo 成功感拉回规模证据。** 帖主想找 2026 年真正令人信服的大型案例，隐含质疑是许多 vibe-coded 项目仍停留在小工具、一次性 app 或维护责任不清；对团队采用 agent，规模、可维护性和长期 owner 比首版速度更关键。来源：[biggest known app/platform entirely vibe coded](https://www.reddit.com/r/ClaudeAI/comments/1tjmy6b/what_is_the_biggest_known_appplatform_thats_been/)

- **非编码 agent 为什么难落地的讨论，把差距归到“现实工作流”而不是模型智商。** 帖主引用 Anthropic 工具调用分析称软件工程约占 agentic activity 一半，认为销售、市场、金融、法律等场景缺少代码那样清晰的状态、测试和可回滚边界；这提示企业 agent 要先补数据权限、流程状态、验收与审批。来源：[why non-coding AI agents fail in production](https://www.reddit.com/r/ClaudeAI/comments/1tph5u4/anthropic_just_confirmed_why_90_of_noncoding_ai/)

**今日取舍：** 近两日报告已展开 Claude Code vs Codex、Agent SDK credit、24/7 订阅争论、Pokegents、Storybloq、HyperResearch、语音输入、persistent memory、PACE/AgentMemory、terminal tips、官方课程/skills、本地 LLM 和安全网关，今天不重复。保留的是仍有实质讨论且未在近两日作为 Reddit 主条目展开的成本失控、失败治理、人工负责制、保守方案倾向、vibe coding 规模证据和非编码 agent 落地难点；剔除低信息图片/meme、标题党和只重复已有项目发布的帖子。

## Hacker News 热榜

- **Simon Willison 称 Anthropic / OpenAI 已找到 PMF，HN 讨论把焦点拉到 token 经济账。** #2 热帖 496 分、608 评论；高赞质疑 5–10 万亿美元算力投入需要每年万亿美元级 token 消费，开发者 20%–40% 提速未必能支撑同等成本，另有人质疑“首个盈利季度”的非 GAAP 口径。对 agent 团队，这条不是乐观/悲观之争，而是提醒：日常 driver 之外，还要证明自动化在真实业务结果上足够增量。 [HN](https://news.ycombinator.com/item?id=48296794) / [Simon Willison](https://simonwillison.net/2026/May/27/product-market-fit/)

- **YouTube 将自动给 AI 生成视频打标，评论区担心检测误报和音乐内容灰区。** #1 热帖 283 分、151 评论；讨论者拿 ZeroGPT 误判《独立宣言》类案例提醒“用 AI 识别 AI”会有假阳性/假阴性，也有人指出 YouTube 上“focus music”等 AI 音乐密集发布却未标注。对内容 agent/生成视频工具，平台标签会变成分发和信任的一部分，不能只靠生成端自报。 [HN](https://news.ycombinator.com/item?id=48299753) / [YouTube](https://blog.youtube/news-and-events/improving-ai-labels-viewers-creators/)

- **Google 强推 AI Mode 后 DuckDuckGo 访问量被报道增长 28%，HN 的主线是“搜索”和“问 AI”不是同一需求。** #5 热帖 545 分、274 评论；高赞说需要搜索时不想被默认带进 AI 答案，也有人观察非技术用户因反感 AI 被硬推而开始找 Google Search / Maps 替代品。对做 AI 搜索或浏览器 agent 的团队，默认入口和可关闭性会直接影响信任。 [HN](https://news.ycombinator.com/item?id=48296649) / [PC Gamer](https://www.pcgamer.com/hardware/duckduckgos-ai-free-search-saw-nearly-28-percent-more-visits-in-the-week-following-googles-insistence-that-people-love-ai-mode/)

- **GitHub PR、Issues、Git 操作和 API 又出事故，评论区最担心的是代码评审看到的 diff 不可信。** #10 热帖 227 分、176 评论；有人说这是一个月内又一次严重事件，另有人报告 Web UI 和 API 上 PR 未稳定反映全部 commits/branch changes，可能导致合并未完整审过的变更。对依赖 GitHub API 的 coding agent、CI bot 和自动 review 流程，关键是把“平台状态异常”纳入暂停/复核条件，而不是继续自动合并。 [HN](https://news.ycombinator.com/item?id=48293080) / [GitHub Status](https://www.githubstatus.com/incidents/xy1tt3hs572m)

**今日取舍：** 保留与 AI 产品化、生成内容标注、AI 搜索默认入口、以及 coding-agent 依赖的 GitHub 基础设施可靠性直接相关且评论区有实质争议的条目；剔除 Last.fm 独立、加拿大军机采购、SimCity 3k、push notifications、Labubu 和 Kindle/Rust，因为它们虽有讨论但与 AI/coding-agent 工作流关联较弱，或证据不足以形成面向本栏读者的增量判断。

## Hacker News 搜索观察：agent 工作流开始转向可移植、可协作和可验证

- **VAEN 想把 coding-agent harness 从一堆 Markdown 变成可打包的 `.agent` 文件。** 作者说可用 YAML 声明 skills、MCP servers 等配置，再用 CLI 打包/导入；评论虽少，但已经追问 `.agent` 是否二进制编码，说明社区关心的是 harness 能否像依赖包一样迁移和审计。来源：[HN](https://news.ycombinator.com/item?id=48300485) / [GitHub](https://github.com/sjhalani7/vaen)

- **Workplane 把人和 AI 共用的文件空间做成浏览器内可评论、自动版本化的协作层。** 它让 Claude Desktop、Claude Code、OpenClaw 等 MCP 工具读写共享文件夹，重点不是“又一个网盘”，而是让 agent 产物、团队评论和客户分享落在同一个可追踪 workspace。来源：[HN](https://news.ycombinator.com/item?id=48296569) / [Workplane](https://workplane.co)

- **GridPath 把 spreadsheet agent 做成 Tauri/Rust 桌面应用，并刻意收窄工具集提速。** 作者称只给模型 web fetch、对话和 Excel 操作，SpaceX 模型约 2 分 30 秒完成、快于约 5 分钟的 Excel 插件；下一步要做多 sheet 效率和长会话 context compacting，显示表格 agent 的瓶颈在工具边界与上下文管理。来源：[HN](https://news.ycombinator.com/item?id=48295594) / [GridPath](https://gridpath.dev/)

- **Enju 把人、AI agent 和确定性 compute 放到同一 live task graph，并把结果落成 git commit。** 评论补充说 review、vote、answer 是一等动作，项目用 Claude 辅助但按 spec-driven、模块化和大量并发/边界测试推进；这类设计把“多 agent 协作”从聊天编排推向可审计工作流图。来源：[HN](https://news.ycombinator.com/item?id=48294355) / [GitHub](https://github.com/tamerh/enju)

- **Gonfire 用代理记录 Claude Code 请求，并故意把候选人引向朴素/暴力解法，暴露 AI 时代编程面试的新对抗面。** 作者认为 Opus 级模型会过早给出系统设计洞见，降低 take-home 题的区分度；这条没有评论支撑，但问题具体：评估平台开始从“禁用 AI”转向“控制 AI 帮助的信号强度”。来源：[HN](https://news.ycombinator.com/item?id=48300444) / [Gonfire](https://www.gonfire.io/)

**今日取舍：** 昨日已展开过 OpenRig、Cordium、Claude 默认配色、Raft 学习项目和 TravElly vibe-coding，今天按去重规则不重复；Herdr、CodeWhale、Mirdel、医疗 workflow benchmark 等因只有标题/新闻稿或缺少讨论实质，未作为主条目。

## Claude Code

- **Claude Code `v2.1.152` 发布，`/code-review --fix` 会把 review findings 直接应用到 working tree，`/simplify` 也改为调用它。** 这把“审查→改动”合成一个更自动的修复循环；升级后建议先在干净分支或小改动上验证 diff 质量。 [v2.1.152](https://github.com/anthropics/claude-code/releases/tag/v2.1.152)

- **Skills / slash commands 新增 `disallowed-tools` frontmatter，另有 `/reload-skills` 与 `SessionStart.reloadSkills: true`。** 团队可以在某个 skill 激活时移除高风险工具，并让 hook 安装的新 skill 在同一会话立即可用，不必重启 Claude Code。 [v2.1.152](https://github.com/anthropics/claude-code/releases/tag/v2.1.152)

- **Hooks 和插件治理继续增强：新增 `MessageDisplay` hook、`SessionStart` 可设置 `hookSpecificOutput.sessionTitle`，管理员可用 `pluginSuggestionMarketplaces` allowlist 插件建议来源。** 做企业插件市场或会话审计时，这些改动能把展示文本、会话标题和插件推荐纳入更可控的策略层。 [v2.1.152](https://github.com/anthropics/claude-code/releases/tag/v2.1.152)

- **模型与交互细节有几处直接影响日常使用：主模型不存在时会切到配置的 `--fallback-model` 并保持本会话，Auto mode 不再要求 opt-in consent，Vim NORMAL 模式下 `/` 进入反向历史搜索。** 这减少了模型配置错误导致的整会话失败，也让 vi-mode 用户的历史检索更接近 bash/zsh。 [v2.1.152](https://github.com/anthropics/claude-code/releases/tag/v2.1.152)

- **`v2.1.152` 修复了一批长会话、插件和远程场景故障。** 包括超长会话终端样式退化、插件 MCP server 因 command 相同但环境变量不同被错误去重、git branch 插件不再更新、Remote sessions 经 egress proxy 连接远程 MCP 失败，以及模型/登录切换后 stale thinking-block signatures 让会话卡住。 [v2.1.152](https://github.com/anthropics/claude-code/releases/tag/v2.1.152)

**今日取舍：** 今日新增事实集中在 `v2.1.152`；`v2.1.149` 已在前两日报告中按升级建议覆盖，`v2.1.150` 仅写明 internal infrastructure improvements、无用户可见变化，因此不重复展开。CHANGELOG 与 `v2.1.152` release 内容重合，只作为交叉验证来源。

## Codex

- **`0.135.0` alpha 线已经开始，`rust-v0.135.0-alpha.1` 与 `rust-v0.135.0-alpha.2` 在同日发布；正式用户仍可停在昨日已写过的 `0.134.0`，但测试/打包团队应注意 alpha 资产形态变化。** `alpha.1` 只有简短 release note 和完整多平台资产；`alpha.2` 同样没有详细 changelog，但 macOS 资产改成 `*-unsigned` 包，并额外提供 `signed-macos-rust-v0.135.0-alpha.2.tar.gz`。如果你维护镜像、校验脚本或自动下载规则，不要只按 `codex-aarch64-apple-darwin.tar.gz` 这类旧文件名匹配 alpha 包。 [alpha.1](https://github.com/openai/codex/releases/tag/rust-v0.135.0-alpha.1) / [alpha.2](https://github.com/openai/codex/releases/tag/rust-v0.135.0-alpha.2)

- **Python SDK 的 sandbox 参数变得更像产品 API，而不是 app-server wire shape：新增 `Sandbox.read_only`、`Sandbox.workspace_write`、`Sandbox.full_access` 预设。** 以前 thread lifecycle 接受 `SandboxMode`、turn 接受较底层的 `SandboxPolicy`，现在 sync/async thread 与 turn API 都可用同一个 `sandbox=Sandbox...`；高层 turn 调用从 `sandbox_policy=` 转向 `sandbox=`，省略时仍交给 app-server 默认值，显式 turn override 会继续 sticky 到后续 turns。SDK 用户升级后应把示例、notebook 和内部 wrapper 里的低层 policy 构造迁到新枚举，并注意 raw string sandbox input 会被拒绝。 [PR #24772](https://github.com/openai/codex/pull/24772)

- **远程 `codex exec-server` 注册现在可直接使用 API key，不必先建立 ChatGPT 登录态，但凭据发送范围被限制。** 新路径接受 `CodexAuth::ApiKey`，文档示例是 `CODEX_API_KEY="$OPENAI_API_KEY" codex exec-server --remote "https://<host>.openai.org/api" --environment-id ...`；安全边界是只允许 HTTPS 的 `openai.com` / `openai.org` 及其子域，HTTP 仅给 loopback 本地开发，并禁用 registry registration redirects，避免 API key 被转发到未验证目的地。远程环境/CI 自动注册脚本可以简化，但自建网关域名若不在允许范围内需要复核。 [PR #24666](https://github.com/openai/codex/pull/24666)

- **TUI Markdown 可读性继续补齐：普通表格改成更接近 App 的无外框行式样，窄表格则退化为 key/value records。** #24489 把 Markdown 表格渲染为带内边距、对齐的行，表头使用当前 syntax theme 的 accent + bold，分隔线低对比且保留 wrapping、streaming、history replay；#24636 进一步检测长链接或多 prose-heavy 列导致的 systemic token fragmentation，在列宽太挤时改为重复的 label/value 记录，并在极窄宽度下切到堆叠布局。对经常让 Codex 输出 rollout summary、审查表格或长 URL 表格的用户，窄终端下不再需要强行读“竖排单词”。 [PR #24489](https://github.com/openai/codex/pull/24489) / [PR #24636](https://github.com/openai/codex/pull/24636)

- **富文本输出里的 Web 链接新增 OSC 8 语义链接，重点解决“长 URL 在表格里换行后无法正确打开/复制”的问题。** 新实现只接受 `http://` / `https://` destination，会清洗 terminal payload，并把链接 metadata 与可见宽度/布局分离；assistant/proposed-plan Markdown 的显式链接和裸 URL、表格 cell、streaming、transcript overlay、history insertion 与 resize replay 都会保留完整目标，同时排除 code 和非 Web Markdown destination。使用 Ghostty 等支持 OSC 8 的终端时，可在换行后的任意 URL 片段上执行 open-link/copy-link。 [PR #24472](https://github.com/openai/codex/pull/24472)

- **`Esc` 不再是唯一的 turn interruption 键：`/keymap` 新增 `tui.keymap.chat.interrupt_turn`，默认仍是 `esc`，但可改绑或解绑。** 配置会作用到 running-turn status、queued steer interruption、`request_user_input` 和可见提示；同时保留 popup、Vim insert mode、`/agent` 编辑里的本地 `Esc` 行为，并校验与 fixed/backtrack、request-input navigation 等绑定冲突。容易误按 Esc 中断长任务的用户，可以按 release 测试路径把 Interrupt Turn 改到 `f12`，确认提示变成 `f12 to interrupt`，再决定是否清空该绑定。 [PR #24766](https://github.com/openai/codex/pull/24766)

- **TUI Vim 模式补上常见 text object 组合，prompt composer 更接近日常 Vim 编辑体验。** 新增 operator/text-object pending state，支持 `c` 作为 normal-mode operator，覆盖 `ciw`、`daw`、`di(`、`da(`、`ci"` 等 word、WORD、括号/方括号/花括号、单双引号和反引号 text objects，并为新的 Vim text-object context 加入可配置 keymap entries。开启 Vim composer mode 的用户可用 `cargo test -p codex-tui --lib vim_` 对应的行为做本地 smoke：例如删除 `foo[bar]` 内部、删除整个括号段、删除引号内容后进入 insert mode。 [PR #24382](https://github.com/openai/codex/pull/24382)

- **Linux sandbox 中断清理修复了一个容易积累脏状态的 race：被打断的 `shell_command` 会等待运行时完成 SIGTERM cleanup。** 旧路径里 outer tool-dispatch cancellation 可能先 drop runtime future，bwrapd-backed Linux sandbox 命令来不及清理 synthetic protected-path mount bookkeeping（如 `/tmp` 下 `.git/.codex` registrations）。现在 `shell_command` 可声明等待 runtime cancellation，取消和 timeout 都走 `ExecExpiration`，先发 `SIGTERM`、短暂等待，再 hard-kill 原 process group，并把 `ESRCH` 当作进程组已消失处理。频繁在 TUI 中断 shell tool 的 Linux 用户，升级后应减少 `/tmp` 残留挂载/登记状态。 [PR #22729](https://github.com/openai/codex/pull/22729)

- **MCP/模型后端侧有两条小但实际的兼容更新：Bedrock 开启 client-side `namespace_tools`，`rmcp` 升到 `1.7.0` 并改进认证失败定位。** Bedrock provider 现在启用 namespace tools，但仍禁用不支持的 hosted tools（image generation、web search）；`rmcp 1.7.0` 同时带来 reqwest 兼容更新，并支持从 `WWW-Authenticate` header 里识别失败 scope，方便后续支持新 draft spec 时定位授权问题。使用 Amazon Bedrock 或 streamable HTTP MCP/OAuth 的团队可把这两项放进下一轮集成测试。 [PR #24713](https://github.com/openai/codex/pull/24713) / [PR #24763](https://github.com/openai/codex/pull/24763)

**今日取舍：** 昨日已完整展开 `0.134.0` 正式版、打包资产、profile/MCP/OAuth 主线和一批 0.134 期 PR，今天不重复；保留 `0.135.0` alpha 资产变化、Python SDK sandbox API、remote exec-server API-key 注册、TUI Markdown/链接/键位/Vim 体验、Linux sandbox 中断清理与 Bedrock/rmcp 兼容更新。提交与 merged PR 重复时采用 PR 为主证据；ChatGPT telemetry 的 thread/turn timing 更偏内部观测，未写入主条目。

## GitHub AI 项目

- **[ogulcancelik/herdr](https://github.com/ogulcancelik/herdr)（2,627 stars）把多路 AI coding agent 会话做成 tmux-like 终端 multiplexer。** HN 原始条目标题直接指向“terminal multiplexer for AI coding agents”；对同时跑 Claude Code、Codex 等长任务的人，它解决的是会话编排、切换和终端拥挤问题。来源：[HN](https://news.ycombinator.com/item?id=48247248) / [GitHub](https://github.com/ogulcancelik/herdr)

- **[Hmbown/CodeWhale](https://github.com/Hmbown/CodeWhale)（35,312 stars）是一个终端 coding agent，GitHub 元数据标注为“DeepSeek + MiMo coding agent in terminal”。** HN 原始条目只给出“Terminal coding agent for DeepSeek V4”，信息不厚，但星数和仓库定位达标；适合关注非 Claude/OpenAI 模型进入终端代理执行器的读者先做技术尽调。来源：[HN](https://news.ycombinator.com/item?id=48285545) / [GitHub](https://github.com/Hmbown/CodeWhale)

**今日取舍：** 只选 raw 中有 GitHub 仓库证据、GitHub API 校验 stars ≥100、且未在 2026-05-26/27 日报中实质展开过的 coding-agent 项目。`VAEN` 很贴合 harness 迁移主题但只有 4 stars，未过硬门槛；`Anthropic-Cybersecurity-Skills`、`academic-research-skills`、`agentmemory`、`codegraph`、`Understand-Anything`、`oh-my-pi` 等昨天或前天已覆盖/去重说明，今天没有足够新增事实；`dograh`、`ViMax`、`openhuman`、`supertonic`、`RuView` 等偏语音、视频、个人 AI 或感知场景，未纳入本栏。

## GitHub 趋势项目

- **[aiming-lab/AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw)（12,834 stars）把“从想法到论文”的研究流程做成 fully autonomous / self-evolving agent。** 原始趋势摘录写得很直接：“Fully autonomous & self-evolving research from idea to paper. Chat an Idea. Get a Paper.” 这不是 coding agent 本体，但和 agent 工作流高度相关：它把任务入口、资料/实验推进、写作与迭代收束成端到端流水线。对读者的价值在于观察研究型 agent 如何组织长任务、阶段产物和自我迭代，而不是只把 LLM 当一次性摘要器。

- **[mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)（10,897 stars）把 754 个网络安全能力整理成多平台 AI agent skills。** 原始摘录强调它映射 MITRE ATT&CK、NIST CSF 2.0、MITRE ATLAS、D3FEND 与 NIST AI RMF，并支持 Claude Code、GitHub Copilot、Codex CLI、Cursor、Gemini CLI 等 20+ 平台。昨天 Rize 栏已把它作为安全 skills 样本提过；今天它进入 GitHub weekly trending，新增信号是这类“可安装、可映射框架、可跨工具复用”的安全能力库正在获得更广泛关注。对团队来说，重点不是一次性让 agent 扫漏洞，而是把威胁建模、审计、攻击面检查和合规术语做成可版本化技能层。

- **[hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop)（5,617 stars）用一个 skill file 约束 AI 输出，专门去掉 prose 里的“AI 味”。** 原始摘录只有一句“A skill file for removing AI tells from prose”，但它值得保留为轻量信号：agent skills 不只在补技术栈知识，也开始承担交付物质量控制，比如文案、README、方案说明、报告和客户沟通稿的风格清洗。对 coding-agent 工作流的意义是，很多工程任务最终要交付可读文档；把“少写套话、减少 AI 痕迹”做成可调用 skill，比每次在 prompt 末尾临时提醒更可复用。

**今日取舍：** 硬门槛为 GitHub API 校验 stars ≥ 100，并只选 raw corpus 中与 AI/coding-agent 工作流、agent skills、长任务自动化或交付质量控制有明确关系的仓库。`Chachamaru127/claude-code-harness`、`anthropics/knowledge-work-plugins`、`humanlayer/12-factor-agents`、`dograh-hq/dograh` 昨日 GitHub 趋势栏已展开，今日无足够新增事实，按去重规则不重复；`codegraph`、`Understand-Anything`、`oh-my-pi`、`agentmemory`、`academic-research-skills`、`cursor/plugins` 也已在近日报告中充分覆盖。`ViMax`、`MoneyPrinterTurbo`、`openhuman`、`supertonic`、`RuView`、`OpenWA` 等虽有星数或 AI 标签，但主题偏视频/短视频/TTS/个人 AI/感知/WhatsApp 网关，和本栏 coding-agent 工程化主线较远，未选。

## Rize AI 工具榜

- **今日不展开新条目：Rize 原始榜单可用，但与 2026-05-26 / 2026-05-27 已覆盖内容高度重复。** 今日 raw 仍是同一批 Rize AI tools weekly ranking #1–#20，抓取时间为 2026-05-27T22:03:59+0000；其中与 AI/coding-agent 读者最相关的 context-mode、claude-plugins-official、prompt-master、agency-agents-zh、Anthropic-Cybersecurity-Skills、browser-harness、TencentDB-Agent-Memory、html-anything、anything-analyzer、claude-code-book 等，已在 2026-05-26 Rize 栏逐项展开，2026-05-27 也已说明因无新增排名变化、仓库事实或可验证更新而不重复报道。今天 raw 只提供排名、仓库链接和一句简介，未给出足够新证据支撑再次展开。 [Rize](https://rize.io/ai-tools)

**今日取舍：** raw corpus 状态为 ok，共 20 个 Rize 榜单条目；本栏按去重规则全部暂不展开。排除原因不是证据缺失，而是避免把已写过且今天无新增事实的 weekly ranking 原样重复。

## Product Hunt 新品

- **BobCA** 把卖点直接放在 coding agent 上：一个“sovereign agent”，会学习你的代码偏好。相较泛 AI 助手，它更像是在争夺长期本地/个人开发代理的位置；真正值得观察的是偏好学习能否沉淀成可审计、可迁移的项目规则，而不只是更会迎合用户风格。 [Product Hunt](https://www.producthunt.com/products/bob-s-workshop?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Calling Skills for AI Agents** 主打“通过你的 coding agent 添加语音和视频通话”。这条有意思的不是通话本身，而是把实时通信能力包装成 agent/coding-agent 可调用技能：如果接入顺畅，应用内音视频功能可能从 SDK 手工集成，变成让代理按需求装配和配置的组件。 [Product Hunt](https://www.producthunt.com/products/cometchat-skills?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **zero.xyz** 提供给 AI agent 访问约 8,000 个工具、API 和服务的入口。对 agent 工作流来说，这是典型“工具层/连接层”产品：价值取决于权限、审计、认证隔离和失败恢复是否做好，而不只是工具数量足够大。 [Product Hunt](https://www.producthunt.com/products/zero-xyz?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** raw corpus 状态为 ok。优先保留与 coding agent、agent 技能/工具调用层直接相关的产品；排除泛 AI 内容、财务/PDF 转换、宠物声学、代码视频、SSH/云架构/数据库编辑等开发者工具但非 agent 主线的条目。**Chunk sidecars** 虽然很相关，但昨日已在 HN 搜索观察里展开过“agent 代码验证提前到 push 前”，今天 Product Hunt 原始信息没有足够新增事实，按去重规则不重复入选。

## Polymarket AI 市场

- **5 月最佳 Coding AI 模型市场进一步押向 Anthropic：97.3%，OpenAI 2.1%、Google 0.5%；24h 成交量约 18,150.8，30d 约 64,820.2，流动性约 125,788.0。** 与昨日报告的 Anthropic 97.5% 基本持平，月底前分歧仍很小；这只能反映交易者对“榜首归属”的预期，不等于真实 coding benchmark 结论。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may)

- **6 月最佳 Coding AI 模型市场也暂由 Anthropic 领先：88.0%，Google 5.5%、OpenAI 4.9%；24h/30d 成交量约 5,458.2，流动性约 19,292.9。** 相比 5 月盘，6 月给 Google/OpenAI 留出的追赶空间更大；对关注 Claude、Gemini、OpenAI 在编码代理任务上迭代的人，这是下月发布预期的一个外部温度计。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-may-619)

- **5 月最佳 AI 模型总榜市场仍几乎锁定 Anthropic：98.8%，Google 0.5%、OpenAI 0.4%；24h 成交量约 68,440.2，30d 约 7,984,715.8，流动性约 2,489,281.3。** 这比昨日 98.6% 小幅上行，说明月底总榜预期继续高度集中；实际模型/agent 选型仍应回到自家任务集、工具链和成本验证。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-ai-model-end-of-may)

- **6 月最佳 AI 模型市场给 Anthropic 76.6%、Google 16.5%、OpenAI 4.9%；24h 成交量约 167,262.7，30d 约 3,304,762.5，流动性约 2,226,689.2。** 相比昨日报告的 Anthropic 77.5%、Google 18.5%，Google 追赶空间略收窄但仍明显高于 5 月盘；可作为下月模型发布和 agent 能力预期的背景信号。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **5 月最佳数学 AI 模型市场当前押 Google：88.5%，Anthropic 11.0%、OpenAI 1.1%；24h 成交量约 18,038.9，30d 约 211,052.9，且 Google 今天上行 13.5%。** 这是今天相对昨日变化最大的 AI 能力盘口之一；数学能力会影响复杂规划、形式化验证和代码推理，但仍不能替代公开 benchmark 或项目内评测。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-may)

- **中国 AI 公司 5 月榜首市场明显偏向 Alibaba：93.5%，Baidu 3.1%、Z.ai 2.1%；24h 成交量约 30,486.9，30d 约 308,793.9，流动性约 95,571.6。** 该盘与 coding-agent 主线不是一一对应，但能补充中文/中国模型生态的市场预期；如果团队在评估 Qwen、文心或 Z.ai 相关能力，仍需用具体工程任务复测。 [Polymarket](https://polymarket.com/event/best-chinese-ai-company-end-of-may)

- **FrontierMath 盘口继续显示交易者对高难数学 benchmark 的短期突破谨慎：Claude 到 6 月前达到 50% 的 Yes 为 22.5%，本周下行 29.0%；Gemini 达到 45% 为 45.0%，本月下行 24.5%；任一 AI 模型 2026 年前达到 90% 的 Yes 为 24.5%。** 这些盘口更适合作为“推理能力预期”背景，不应被写成模型能力事实。 [Claude 市场](https://polymarket.com/event/anthropic-claude-score-on-frontiermath-benchmark-by-june-30) / [Gemini 市场](https://polymarket.com/event/gemini-3-score-on-frontiermath-benchmark-by-june-30) / [90% 市场](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027)

**今日取舍：** 保留与 AI 模型能力、coding AI、数学/benchmark 和中国模型竞争直接相关、且成交/流动性足够的盘口；剔除第二名 Coding AI、Style Control 版 5 月总榜和 OpenAI+Anthropic vs Google 估值盘，前两者与已选主盘口高度重叠，估值盘则偏资本市场且 30d 成交量仅约 327.7。所有概率均为 Polymarket 市场预期，不是已确认事实。
