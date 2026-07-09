# AI Agent 日报（2026-07-10）

## 天气

- **北京·海淀**：今日雷暴伴小冰雹，24.9–28.7°C；降水概率 90%、预计 21.8 mm，东风最高 9.6 km/h。相比昨日最高温明显下降但雨量大幅增加，通勤带伞，雷雨和冰雹时段减少户外停留。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-10&end_date=2026-07-10)
- **上海·杨浦**：今日阴，25.4–32.8°C；降水概率 10%、预计 0 mm，东南风最高 15 km/h。较昨日雷雨转为少雨但最高温回升，出行主要注意闷热和防晒，室外活动比昨日更稳定。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-10&end_date=2026-07-10)

## X 推荐

- **OpenAI 正式推出 GPT-5.6 系列，Sol / Terra / Luna 开始进 ChatGPT、Codex 和 API。** Devs 口径称 Sol 主打长程 coding、知识工作、网络安全和科学任务，Terra 平衡质量与成本，Luna 走快速低价；昨天还是发布时间窗口，今天已进入 rollout。  
  来源：https://x.com/OpenAI/status/2075271421149020426 · https://x.com/OpenAIDevs/status/2075273992609599834 · https://x.com/OpenAIDevs/status/2075286157186003348

- **ChatGPT Work 发布，把 Codex 和 GPT-5.6 包成 ChatGPT 里的新 agent。** OpenAI 称它可跨应用行动；微软也称 GPT-5.6 with Work IQ 将进入 Copilot Chat、Cowork、M365、GitHub 和 Foundry，企业 agent 入口继续集中到办公套件。  
  来源：https://x.com/OpenAI/status/2075274271845404744 · https://x.com/satyanadella/status/2075318015063925053

- **Codex 并入 ChatGPT 桌面端，形成“ChatGPT Codex”。** 更新帖称 Codex 进入 macOS / Windows 的 ChatGPT desktop，并支持 inline Markdown 与代码编辑；对原 Codex 用户，桌面应用和聊天入口的边界会变模糊。  
  来源：https://x.com/CodexReleases/status/2075265220054782386 · https://x.com/Codex_Changelog/status/2075273900871889169 · https://x.com/dotey/status/2075272687912448127

- **Codex CLI 0.144.0 发布，MCP 交互式认证继续进入稳定路径。** 这版提到 MCP tools 可请求交互式认证且不再依赖实验开关；昨天 0.143.0 刚把远程插件默认化，今天重点转到 agent 调工具时的登录体验。  
  来源：https://x.com/CodexReleases/status/2075261656146522158

- **GPT-5.6 Sol 已接入 Cursor、GitHub Copilot 和 OpenRouter。** Cursor 称 Sol / Terra / Luna 已可用，Sol 在 CursorBench 得分 67.2%；GitHub 称 GPT-5.6 family 正向 Copilot rollout，OpenRouter 也上线三档模型，模型路由和 IDE 选型需要重新测。  
  来源：https://x.com/cursor_ai/status/2075265504105611674 · https://x.com/github/status/2075274864110293060 · https://x.com/OpenRouter/status/2075271807855452196

- **Artificial Analysis 称 GPT-5.6 Sol 在 Intelligence Index 接近 Claude Fable 5，但成本约为三分之一。** 这是第三方榜单信号，不等于真实仓库表现；但对 coding agent 预算，Sol 可能成为“高能力/低单价”新候选。  
  来源：https://x.com/ArtificialAnlys/status/2075268970492657905

- **Perplexity Computer 发布新的 orchestrator model 研究预览。** 官方称这是适配版模型，用于 Perplexity Computer 的编排层；浏览器/桌面 agent 的竞争点正在从单步问答转向“谁来分配、检查和串联任务”。  
  来源：https://x.com/perplexity_ai/status/2075224548476440779

- **Manus 推出 Branch，可把同一对话分叉成继承完整上下文的并行 session。** 这适合在不污染主线程的情况下让 agent 探索多个方案；多分支上下文管理正在变成 agent 产品的基础交互。  
  来源：https://x.com/ManusAI/status/2075236343429599432

- **Claude Code 出现多人共享终端玩法。** dorsa_rohani 称可让多人在同一 terminal 使用 Claude Code，并把多个 Claude 连接起来共享协作上下文；这和“团队共用一个 Claude Code”的中文转述一起指向多人 agent session 需求。  
  来源：https://x.com/dorsa_rohani/status/2074963064231952832 · https://x.com/0xCheshire/status/2075105394704384479

- **BrowserSkill 把已登录浏览器桥接给 Cursor、Claude Code、Codex 等 shell 型 agent。** 中文介绍称 agent 可通过 `bs` 操作本机浏览器而不打断用户正常工作；这类桥接能绕开重复登录，但也需要额外审权限和隔离。  
  来源：https://x.com/geekbb/status/2075103909333651491

## X 关注

- **OpenAI 把 Codex 和 ChatGPT 合到同一个桌面应用。** OpenAI Devs 称 Codex coding agent 会和 ChatGPT Work 并列出现；对开发者来说，代码任务、日常工作 agent 和聊天入口正在从多个应用收敛到一个工作台。来源：https://x.com/OpenAIDevs/status/2075275868268789885

- **GPT-5.6 正式给出 Sol / Terra / Luna 三档模型。** OpenAI Devs 称 Sol 面向长周期 coding、agentic work、规划和工具使用；昨天还是发布时间窗口，今天已进入可面向模型路由和任务分层设计的发布阶段。来源：https://x.com/OpenAIDevs/status/2075286157186003348

- **GPT-5.6 API 新增 programmatic tool calling 和 multi-agent 能力。** Simon Willison 记录了这批 API 变化；做 agent harness 的团队应重点验证工具调用控制、子代理编排和旧 Realtime/Responses 链路的兼容性。来源：https://x.com/simonw/status/2075306164993315192

- **Codex / ChatGPT 插件目录开始统一。** Dimillian 转发的 OpenAI 开发者信息称，开发者现在可向跨 ChatGPT 和 Codex 的统一 Plugins Directory 提交插件；插件分发、审核和可见性会影响 agent 工具生态。来源：https://x.com/Dimillian/status/2075302993260368279

- **Codex 更新开始把“编辑文件 + 运行终端”等 IDE 行为放进 ChatGPT。** steipete 转发的 Codex 更新提到可直接编辑文件、运行命令等开发者能力；这说明 OpenAI 不只发布模型，也在补 coding agent 的桌面操作面。来源：https://x.com/steipete/status/2075293627501429067

- **Vercel 把 GPT-5.6 用到内部数据科学 agent。** OpenAI Devs 称 Vercel 的 Andrew Qu 用新模型让内部 data science agent 处理更难任务；这是企业内部分析 agent 的公开用例，而不只是 demo 级 coding 展示。来源：https://x.com/OpenAIDevs/status/2075289656225374647

- **GPT-5.6 Sol 在 ARC-AGI-3 上达到 7.8%。** steipete 转发 ARC Prize 称 Sol 是首个超过某个 ARC-AGI-3 验证基线的前沿模型；分数仍低，但可作为推理 benchmark 变化的新增信号。来源：https://x.com/steipete/status/2075328260704288885

- **levelsio 用 Claude Code 搭了 iOS app 的 Web 测试入口。** 他称让 Claude Code 设置 serve 流程后，可在网页里测试 iOS app；这延续昨天“远程常驻 agent 环境”，新增点是把移动应用调试也接进 agent 自动化。来源：https://x.com/levelsio/status/2075328941317886210

- **thdxr 用 opencode 做 Slack 更新，不再为小功能单独做 Slack app。** 他说让 opencode 负责把进展同步到 Slack；对团队内部 agent 来说，轻量通知可以先由现有编码/自动化 agent 拼起来，再决定是否产品化。来源：https://x.com/thdxr/status/2075331244083040682

## Reddit 社区

- **多 agent 编排仍被吐槽像“六个终端”。** 发帖者想要每个 agent 有 Docker 隔离、worktree 级审查和可随时人工接管，但现有工作台常在花哨 UI 与手工分屏之间摇摆；这正是并行 coding agent 产品的未解痛点。来源：https://www.reddit.com/r/ClaudeAI/comments/1ua3252/is_there_actually_a_good_way_to_orchestrate/

- **有人建议把 Fable 5 的高额度窗口用来升级“Claude Code OS”。** 讨论重点不是再做一个项目，而是让高能力模型审计现有流程、固化 chief operator、按需加载 skills、收敛小型 agent team；对团队更像一次 harness 重构清单。来源：https://www.reddit.com/r/ClaudeAI/comments/1uou7ow/friendly_reminder_what_to_fix_before_fable_5/

- **VibeJam 冠军分享 15 天 AI 游戏工作流。** 作者用 Claude Code、Three.js、Suno、ElevenLabs、GPT Images-2 和 Tripo3d 做出获 $25,000 奖金的网页游戏；实际流程是 2–3 个 Claude Code 会话并行，按新功能开新会话，保留长会话处理需上下文的 bug。来源：https://www.reddit.com/r/ClaudeAI/comments/1urzr1q/i_just_made_25k_usd_with_my_capybara_game_built/

- **无代码背景用户用 Claude 网页版把 17KB 原型迭代成上线小游戏。** 250 次迭代后成品包含 60Hz 确定性模拟、PWA、排行榜和 Cloudflare Worker 反馈后端；经验教训是人类要做规格、真机 QA、回滚和性能排障，不能只等模型“一次生成”。来源：https://www.reddit.com/r/ClaudeAI/comments/1uomrr8/retired_disabled_army_combat_vet_no_coding/

## Hacker News

- **GPT-5.6 发布讨论集中在提示词要变短、约束要更清楚。** 开发者指南称短系统提示在内部评测提升约 10–15%、token 降 41–66%；评论还关注 ARC-AGI-3 7.8% 和 Codex/Claude Code 选择。 [HN](https://news.ycombinator.com/item?id=48849066) · [OpenAI](https://openai.com/index/gpt-5-6/)

- **Colibrì 把 GLM 5.2 744B MoE 用 NVMe 流式跑到普通电脑上。** 作者让约 17B dense 部分常驻内存、2.15 万个 routed experts 放磁盘，32GB 级机器可跑但约 0.05–0.1 tok/s；评论认为可用于隔夜任务，但离交互式本地大模型仍远。 [HN](https://news.ycombinator.com/item?id=48842459) · [GitHub](https://github.com/JustVugg/colibri)

- **GLM 5.2 做记账基准引发“准确率之外谁担责”的争论。** 评论指出人类记账员还要找发票、处理未写明背景，而 benchmark 把这些做成 user notes；税务场景里，LLM 出错后的法律责任和人工复核成本比单项准确率更关键。 [HN](https://news.ycombinator.com/item?id=48850414) · [文章](https://toot-books.pages.dev/blog/glm-5-2-vat-benchmark)

- **Tencent Hy3 的 HN 讨论从模型能力转到分发和价格。** 评论提到 Hy3 早前登顶 OpenRouter 后已掉到第 8/9 名，Novita 在 OpenRouter 提供免费试用到 7 月 21 日；选模型时要同时看排行榜、有效输入价和同档 DeepSeek Flash V4。 [HN](https://news.ycombinator.com/item?id=48847552) · [Tencent](https://hy.tencent.com/research/hy3)

- **EU Chat Control 1.0 重新放行私人消息扫描，HN 追问表决机制和 E2E 边界。** 评论引用 314 票反对、276 票赞成但未达 361 绝对多数而未能否决，且美国平台可继续扫描 Gmail、iCloud、Discord 等私信；做通讯或数据产品要重新核对欧洲隐私合规风险。 [HN](https://news.ycombinator.com/item?id=48843923) · [Patrick Breyer](https://www.patrick-breyer.de/en/eu-parliament-greenlights-chat-control-1-0-breyer-our-children-lose-out/)

## HN 搜索

- **Kastra 给 Claude Code、Cursor 和 Codex 加运行时授权。** 它在 agent 工具调用执行前按确定性策略给出 allow/hold/deny，并可扫描本地会话历史，找出写入 secrets、触碰生产库、force push、curl-to-shell 等高风险动作。来源：[HN](https://news.ycombinator.com/item?id=48847526) / [Kastra](https://kastra.ai/)
- **Abralo 把多路 Claude Code 会话放进一个轻量桌面窗口。** 作者说 VS Code 扩展跑 3 个以上会崩，Abralo 用 Tauri 做并排监控、注意力提示和 5 小时/周额度告警；评论已有用户反馈会话进度刷新卡住。来源：[HN](https://news.ycombinator.com/item?id=48832797) / [Abralo](https://abralo.com/)
- **Spice 2.0 把“agent 可查询实时业务数据”做成无 ETL 分析节点。** 它从 Postgres、MySQL、MongoDB、DynamoDB 等做原生 CDC，称 3 亿行表约 9 分钟 bootstrap，并让 agent 在不压生产库的情况下查秒级新鲜数据。来源：[HN](https://news.ycombinator.com/item?id=48851086) / [Spice](https://spice.ai/blog/spice-2-0-is-now-available)
- **PandaPage 给 coding agent 一个临时发布 HTML 的 curl API。** 一次 POST 可上传 JSON 或 zip，页面默认 24 小时过期、用 KV TTL 和 R2 lifecycle 清理；适合让 Claude Code 直接把 mockup 或 demo 变成可分享 URL。来源：[HN](https://news.ycombinator.com/item?id=48842119) / [PandaPage](https://pandapage.clawshop.sh)
- **ByteAsk 做了面向 C/C++ 的 agent coding harness。** 它补上 gdb、clang-tidy、cppcheck、sanitizers、perf、benchmark、compile DB、Godbolt、符号化和反编译等工具，回应“Claude Code 不够贴合 C++ 工具链”的痛点。来源：[HN](https://news.ycombinator.com/item?id=48805309) / [ByteAsk](https://byteask.ai/)

## Claude Code

今日 Claude Code 原始语料只有 v2.1.203、v2.1.204、v2.1.205 三个 release，均已在 7 月 8 日或 7 月 9 日日报中覆盖；本栏不重复刊登。

## Codex

- **Codex 继续把网络请求收敛到统一 HTTP client。** 文件上传三段流程和 login 的 device-code/OAuth/API-key token 交换都改走 `HttpClientFactory`，配合 cargo-deny 禁止新增一方 crate 直接依赖 `reqwest`；企业代理、自定义 CA 和敏感 auth 日志边界更容易统一治理。来源：https://github.com/openai/codex/pull/31363 · https://github.com/openai/codex/pull/31637 · https://github.com/openai/codex/pull/31431

- **Code Mode 补上 macOS 安装和缺 host 时的降级路径。** 安装器会把 `code-mode-host` symlink 到 `codex` 旁边；若发行包缺少 companion binary，只在 `NotFound` 时回退到进程内 V8，权限、握手和超时错误仍会显式暴露。来源：https://github.com/openai/codex/pull/31876 · https://github.com/openai/codex/pull/31899

- **Codex Apps 文件参数会按工具 schema 过滤可选字段。** 文件上传重写后始终传 `download_url` 和 `file_id`，但只有 schema 接受时才附带 `mime_type`、`file_name`；严格 MCP 工具不再因多余字段拒绝调用。来源：https://github.com/openai/codex/pull/31686

- **Bundled OpenAI Docs skill 更新到 GPT-5.6。** 新版通过 `latest-model.md` 解析 current/default-model，加入 GPT-5.6 Sol/Terra/Luna 迁移判断，并补 POSIX resolver 与 Windows CommonJS 入口；安装后的 Codex 能直接拉到新模型提示和迁移指南。来源：https://github.com/openai/codex/pull/31842

- **图像生成默认切到 extension 路径。** `Feature::ImageGeneration` 现在专门控制 extension-backed image generation，MCP server 和 core API sample host 默认安装该 extension，同时保留 `imagegenext` 兼容别名。来源：https://github.com/openai/codex/pull/31596



## GitHub AI 项目

- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)（27,148 stars）：OpenAI 把“从 Claude Code 调 Codex 做审查或任务委派”做成插件；多 agent 团队可用它测试 Claude Code 主控、Codex 复核的协作路径。
- [steipete/CodexBar](https://github.com/steipete/CodexBar)（17,349 stars）：CodexBar 在菜单栏显示 OpenAI Codex 与 Claude Code 用量统计，且不要求登录；适合重度 CLI 用户监控额度和异常消耗。
- [browser-use/video-use](https://github.com/browser-use/video-use)（16,248 stars）：browser-use 推出让 coding agent 编辑视频的项目；教程、demo 和产品视频可从“人工剪辑”转成 agent 可执行的代码化流程。
- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr)（14,787 stars）：Herdr 是终端里的 agent multiplexer，可把多路 agent 会话集中管理；适合比较 tmux 式工作流、远程 attach 和人工接管体验。
- [bradautomates/claude-video](https://github.com/bradautomates/claude-video)（6,641 stars）：这个 Claude Code 扩展用 `/watch` 下载视频、抽帧、转写并交给 Claude；会议录屏、课程和 demo 更容易进入 coding-agent 上下文。
- [huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech)（5,830 stars）：Hugging Face 的 speech-to-speech 项目面向本地开源语音 agent；做语音入口或离线助手时，可参考其模型组合和本地运行路径。

## GitHub 趋势项目

- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)（27,148 stars）：OpenAI 把“从 Claude Code 调 Codex 审查代码或委派任务”做成插件；多模型 coding agent 团队可用它把 Claude Code 会话内的复核、分工和交叉验证标准化。
- [browser-use/video-use](https://github.com/browser-use/video-use)（16,248 stars）：browser-use 推出“用 coding agents 编辑视频”的项目；它把视频素材处理带进 agent 工作流，适合 demo、教程和产品视频的半自动剪辑实验。
- [huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech)（5,830 stars）：Hugging Face 的本地 voice agent 示例本周上榜，目标是用开源模型搭 speech-to-speech agent；做语音入口时可参考其本地化、模型编排和延迟取舍。
- [steipete/CodexBar](https://github.com/steipete/CodexBar)（17,349 stars）：CodexBar 在菜单栏显示 OpenAI Codex 和 Claude Code 用量，无需登录；对重度 agent 用户，它补的是成本与额度可见性，而不是又一个聊天入口。
- [ogulcancelik/herdr](https://github.com/ogulcancelik/herdr)（14,787 stars）：Herdr 是终端里的 agent multiplexer；继前两天 HN 讨论后又进入 GitHub Trending，说明多 agent pane、远程 attach 和通知这类“终端工作台”需求仍在升温。

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

- **Aura: Agents + Git + Intent Open Source**：开源 IDE，用 Git 与 intent 控制 AI coding agents，并内置循环执行；适合观察 coding agent 工作台如何把变更记录、目标约束和反复执行放到同一界面。来源：[Product Hunt](https://www.producthunt.com/products/aura-28?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Coasty**：Computer-use agent，定位是像人一样运行 legacy software；对仍有桌面旧系统、不可 API 化工具的团队，关注点是 GUI 自动化能否补上 agent 工具链缺口。来源：[Product Hunt](https://www.producthunt.com/products/coasty?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Perfai Security**：面向 vibe-coded app 的安全工具，称可用 1 条 prompt 查找并修复线上漏洞；适合把 agent 生成应用后的安全验收前移到发布和运行期。来源：[Product Hunt](https://www.producthunt.com/products/perfai-security-for-vibe-coded-apps?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场

- 7 月底“最佳 AI 模型公司”主市场继续押 Anthropic：Anthropic 87.5%、Google 8.6%、OpenAI 3.6%，24h 成交约 22.86 万；相比昨日 85.0% 再上行，短线预期更集中。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-july-299
- “7 月底最佳 Coding AI 模型”仍由 Anthropic 领先：Anthropic 94.0%、OpenAI 5.6%、xAI 0.9%，24h 成交约 3451；相较昨日 95.0% 小幅回落，但市场仍不押注短线反超。来源：https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-july
- “7 月底最佳 Math AI 模型”里 Anthropic 升到 75.5%，Google 11.5%、OpenAI 3.1%，24h 成交约 6133；相比昨日 64.0% 明显回升，数学榜预期重新收敛到 Anthropic。来源：https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-july
- FrontierMath 90% 达标市场继续升温：2027 年前有模型达到 ≥90% 的 Yes 为 88.5%，30d 成交约 3.02 万、本月上涨 59.0%；这是市场预期，不代表基准已被攻破。来源：https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027
- “9 月底是否有模型达到 1510 Overall Arena Score”当前主项为 55.5%，24h 成交约 5012、30d 成交约 5.28 万；本月下跌 25.5%，市场对短期 Arena 分数跃升更谨慎。来源：https://polymarket.com/event/will-any-ai-model-reach-overall-arena-score-by-september-30
- 年底最佳 AI 模型公司市场仍更分散：Anthropic 62.5%、Google 13.5%、OpenAI 13.0%，流动性约 55.21 万；半年维度仍比 7 月底主市场给 Google/OpenAI 留出更多反超空间。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-2026
