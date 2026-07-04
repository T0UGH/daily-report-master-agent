# AI Agent 日报（2026-07-05）

## 天气

- **北京·海淀**：今日小阵雨，23.4–32.8°C，最高温较前两天明显回落；降水概率 48%、预计 2.7 mm，北风最高 12.4 km/h，外出仍需带伞，体感压力比昨日高温小。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-05&end_date=2026-07-05)
- **上海·杨浦**：今日雷暴并可能伴轻微冰雹，25.4–29.5°C；降水概率 96%、预计 19.3 mm，西南风最高 16.8 km/h，通勤、外卖和机场/高铁接驳建议预留强降雨延误。来源：[Open-Meteo](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-07-05&end_date=2026-07-05)

## X 推荐

- **Browser Use CLI 被用来给 Claude Code、Hermes Agent、OpenClaw 补浏览器操作能力。** 帖子称它可复用本地 Chrome 的 cookie 和登录态，让本地 agent 访问已登录后台；风险是权限和数据边界要先隔离清楚。  
  来源：https://x.com/canghe/status/2073417552316010811

- **X 官方 MCP 被社区视为信息监控入口。** 讨论点是把 X 账号、关键词搜索和趋势整理接入 AI 工作流，适合做公开情报采集，但也会把平台限流、账号安全和来源偏差带进 agent。  
  来源：https://x.com/huangyihe/status/2073379133514825819

- **LlamaIndex 发布面向 agentic retrieval 的 Retrieval Harness。** jerryjliu0 称它提供持久化评测框架，用来测试现代检索代理；对 RAG agent 团队，价值在于把检索质量从“感觉好用”推进到可重复评测。  
  来源：https://x.com/jerryjliu0/status/2073407100642852871

- **Anthropic 官方 Prompt Library 被日语社区扩散。** 帖子提到库里覆盖设计、修 bug、代码审查、安全检查和自动化等常见场景；适合把零散提示词沉淀成团队可复用模板。  
  来源：https://x.com/ClaudeCode_love/status/2073211441113669827

- **Fable 5 的 reasoning effort 成本差异被实测放大。** petergostev 用同一提示对比 low 与 max，耗时从约 12 分钟拉到接近 2 小时；长任务应先用低档探索，再把高推理留给关键验收。  
  来源：https://x.com/petergostev/status/2073469313474851229

- **有人用“上下文转图片再 OCR”压低 Fable 5 输入成本。** 中文转述称该做法最高可降约 70% 输入费用；这是极端成本优化思路，需额外验证 OCR 误差会不会损坏代码或需求细节。  
  来源：https://x.com/DLKFZWilliam2/status/2073219516667146657

- **Termany 发布 Agent-Native 终端。** 作者把工作区、文件树、标签页和窗格组合成多会话界面，目标是让多个 agent 并行工作时，瓶颈回到人的注意力而不是屏幕和终端数量。  
  来源：https://x.com/idoubicc/status/2073311678440321117

- **Codex plugin for Claude Code 因 Fable 5 回归再度被推到 GitHub Trending。** 社区把它解读为 Claude Code + Codex 混合工作流升温：Claude 做规划/验证，Codex 承接实现或互审。  
  来源：https://x.com/Lonely__MH/status/2073411508181020684

- **Fable 5 重新发布版本在 APEX-SWE 上的成绩低于旧版预期。** Mercor 称 rerelased 版本未达到原先表现；如果团队把 Fable 5 当 coding-agent 主力，仍应按当前版本重跑自家基准。  
  来源：https://x.com/mercor_ai/status/2073080728074727485

- **Hermes Agent 插件接口准备扩展。** Teknium 表示希望扩大插件 interface，让等待中的开发者 PR 能更容易接入；对 Hermes 用户，后续可关注第三方工具和 workflow 扩展是否会更标准化。  
  来源：https://x.com/Teknium/status/2073521617146438093

## X 关注

- **Codex / Claude Code 仍应先做规划和架构。** yyyole 提醒不要一上来让 coding agent 写代码，而是先让它规划、设计产品，再进入实现；这能减少返工和 token 成本。来源：https://x.com/yyyole/status/2073411252517564821

- **lifesinger 区分了写代码工具和知识工作工具。** 他回应“Claude Code / Codex 与 YouMind 有何区别”：写网站或应用仍优先用 Claude Code / Codex；若目标不是产出代码，就应换成更适合知识整理的工作流。来源：https://x.com/lifesinger/status/2073391080532533357

- **alex_prompter 把 AI 使用分成四层。** 他列出 prompt engineering、context engineering、harness engineering、loop engineering，强调高阶用法已从一次性提示转向给模型搭环境、反馈和循环。来源：https://x.com/alex_prompter/status/2073462823179731032

- **Claude Fable 的 UI/UX 提示词继续被转成 Claude Code 工作流。** aiedge_ 称把特定 prompt 注入 Claude Code 后，可生成 Apple 风格界面；这类做法把视觉品味约束直接前置到 coding agent。来源：https://x.com/aiedge_/status/2073451788276248974

- **thdxr 提醒 API 细节可能被 agent 生成掩盖。** 他在做 API design 时发现，很多过去会被人看到的细节，现在会直接由 agent 生成；团队仍要明确哪些接口决策需要人工审查。来源：https://x.com/thdxr/status/2073449533712073005

- **AI coding 工具的稳定性和性能门槛被公开点名。** thdxr 说包括自家产品在内，很多工具还没达到用户应要求的稳定性和性能标准；选型时不能只看 demo，要看长任务和日常延迟。来源：https://x.com/thdxr/status/2073492158821396482

- **steipete 预告 token / reset 可见性改进。** 下一版工具会显示额度重置何时到期，方便用户安排高强度 coding-agent 会话；这说明“额度可观测性”已成为重度用户的刚需。来源：https://x.com/steipete/status/2073482942513565713

- **AI 辅助教育研究被用来提醒“作业提分不等于能力提升”。** AI_jacksaku 摘引一项 26000 名学生、30 个月追踪：作业分数升 18%、用时从 64 分钟降到 45 分钟，但闭卷考试下降约 20%；企业引入 AI 也要区分产出指标和真实能力。来源：https://x.com/AI_jacksaku/status/2073412172726886606

## Reddit 社区

> 本栏今日降级：Reddit 采集出现异常且 lane package 中没有可用 raw corpus，无法基于可核验原始语料筛选社区讨论；按规则不使用 audit-only 数据补写内容。

## Hacker News

- **Claude Code 议题下，HN 把“会话/缓存串线”当成中间层隔离问题讨论。** 原帖指向 Anthropic issue；评论称曾见过 API gateway 把上一位调用者的响应发给下一位，也有人报告 Gemini 近几天出现像“别人答案”的输出。 [HN](https://news.ycombinator.com/item?id=48785485) · [Issue](https://github.com/anthropics/claude-code/issues/74066)

- **YouTube 私密视频泄露文章把 prompt injection 拉进创作者后台安全。** 讨论里的攻击路径是：攻击者留言、创作者打开 Studio 评论页、点击 YouTube 设计的 AI 建议提示后触发注入；争议点是平台是否应把这类 AI 功能注入视作安全漏洞。 [HN](https://news.ycombinator.com/item?id=48786781) · [文章](https://javoriuski.com/post/youtube)

- **《Command and Conquer Generals》被用 Fable 辅助移植到 macOS/iPhone/iPad。** 评论认为这是低风险大规模代码转换的合适场景：GPL 源码已有 macOS/Linux 基础，fork 主要补 iOS/iPadOS 与引擎修复；也有人吐槽生成文档的 AI 腔。 [HN](https://news.ycombinator.com/item?id=48788283) · [GitHub](https://github.com/ammaarreshi/Generals-Mac-iOS-iPad/tree/main)

- **Armin Ronacher 的“模型更好、工具更差”引发 harness 适配讨论。** 评论把问题落到 coding agent 工具层：不同模型可能需要不同 system prompt、重试和命令变体，像早年浏览器兼容性一样，评测和执行环境不能只假设一个通用工具协议。 [HN](https://news.ycombinator.com/item?id=48788599) · [文章](https://lucumr.pocoo.org/2026/7/4/better-models-worse-tools/)

- **Codex issue 报告 GPT-5.5 reasoning token 出现固定间距聚类。** 该帖评论很少，但原始信号具体：`reasoning_output_tokens` 会卡在相隔 518 的阈值，且与复杂任务错误强相关；对跑长任务的团队，适合加入失败分析维度。 [HN](https://news.ycombinator.com/item?id=48789428) · [Issue](https://github.com/openai/codex/issues/30364)

## HN 搜索

> 本栏今日不生成新条目：raw corpus 可用，但候选大多已在 7 月 3 日或 7 月 4 日 HN 搜索栏写过；剩余条目要么证据过薄，要么偏通用营销案例，不适合作为 AI/coding-agent 日报新增内容。

## Claude Code

> 本栏今日未生成新条目：raw corpus 只包含 Claude Code v2.1.199、v2.1.200、v2.1.201 三个 GitHub release，均已在 2026-07-04 日报的 Claude Code 栏目中覆盖；按去重规则不重复刊登。

## Codex

> 本栏今日未生成：原始语料仅包含 `0.143.0-alpha.33`、`alpha.34`、`alpha.35` 三个预发布 release 资产列表，release note 只有版本号；其中 `alpha.34` 已在 2026-07-03 报告出现，`alpha.35` 已在 2026-07-04 报告出现，今天没有可解释的新 CLI、工作流、修复或回归信息。

## OpenClaw

> 本栏今日未生成：OpenClaw 原始语料只有已在 7 月 3 日、7 月 4 日日报覆盖过的 `v2026.7.1-beta.1` 与 `v2026.6.11` 发布内容，另一个 `v2026.6.11-beta.2` 是更早的预发布版本，没有比稳定版更新的读者价值。

## GitHub AI 项目

- [usestrix/strix](https://github.com/usestrix/strix)（35,945 stars）：开源 AI 渗透测试工具，用 agent 发现并修复应用漏洞；适合把安全测试从人工 checklist 迁到可审计的自动化流程。
- [allenai/olmocr](https://github.com/allenai/olmocr)（18,691 stars）：Allen AI 的 PDF 线性化工具包，面向 LLM 数据集和训练；做 RAG、文档 agent 或数据清洗时，可用它把复杂 PDF 变成更稳定的模型输入。
- [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute)（11,282 stars）：OmniRoute 提供单端点接入 231+ provider，并声称支持 Claude Code、Codex、Cursor、Cline 与 Copilot；适合评估多模型 fallback、免费额度聚合和 token 压缩的网关层。
- [ouijit/ouijit](https://github.com/ouijit/ouijit)（121 stars）：Ouijit 是基于 git worktree 的本地 coding-agent 任务管理器，集成终端、Lima VM 沙箱和生命周期 hooks；适合想把多个 agent 任务隔离到可审阅工作区的团队试用。
- [ymichael/bb](https://github.com/ymichael/bb)（115 stars）：bb 是开源 agentic IDE，可接 Claude Code、Codex、Cursor、Pi 和 OpenCode，并允许 agent 派生子线程、读输出和操作界面；它把“终端 wrapper”推进到可脚本化的开发环境。
- [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis)（54,247 stars）：这个项目用 LLM 做多市场股票分析、新闻聚合、决策看板和定时推送；对研究型 agent 工作流来说，是把数据源、分析和通知串成闭环的垂直样例。

## GitHub 趋势项目

- [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis)（54,247 stars）：这个 LLM 多市场股票分析系统把行情、新闻、决策看板和定时推送串成自动化研究流；适合参考“数据采集→LLM 分析→通知”的垂直 agent 模板。
- [allenai/olmocr](https://github.com/allenai/olmocr)（18,691 stars）：AllenAI 的 olmocr 用于把 PDF 线性化成适合 LLM 数据集和训练的文本；做文档型 agent、RAG 数据清洗或批量论文处理时，可作为 PDF 预处理工具评估。
- [Starmel/OpenSuperWhisper](https://github.com/Starmel/OpenSuperWhisper)（1,702 stars）：OpenSuperWhisper 是 macOS 听写应用；对常用 Claude Code、Codex 或桌面 agent 的用户，它提供了把语音输入接入日常提示词和编辑流的开源选择。
- [logto-io/logto](https://github.com/logto-io/logto)（13,713 stars）：Logto 提供面向 SaaS 和 AI app 的 OIDC/OAuth 2.1、多租户、SSO 与 RBAC；构建企业 agent 产品时，可用来处理用户、组织和权限边界。

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

- **Termi Protocol**：把 AI coding agent 的构建过程做成 3D 实时可视化，用来观察代理在执行任务时的状态和进度；适合关注多 agent 可观测性与开发工作台形态的人。来源：[Product Hunt](https://www.producthunt.com/products/termi-protocol?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)
- **Vida**：定位为“克隆自己，让 AI 在你提出前先工作”的个人代理产品；PH 信息较少，但切入点是主动式个人工作流自动化，而不是单次聊天问答。来源：[Product Hunt](https://www.producthunt.com/products/vida-5?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场

- 7 月底“最佳 AI 模型公司”主市场继续押注 Anthropic：Anthropic 87.5%、Google 11.2%、OpenAI 1.8%，24h 成交约 38.2 万、30d 成交约 441.4 万；相比昨日，Anthropic 从 90.5% 回落，但仍明显领先。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-july-299
- “7 月底最佳 Coding AI 模型”仍几乎锁定 Anthropic：Anthropic 95.5%、OpenAI 3.4%、xAI 1.4%，流动性约 9.8 万；对 coding agent 选型读者来说，市场短线仍不押注 OpenAI 或 xAI 反超。来源：https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-july
- “7 月底最佳 Math AI 模型”中 Anthropic 降到 72.0%，Google 16.5%、OpenAI 9.8%，24h 成交约 3738；相比昨日 85.5%，数学榜预期明显松动，仍领先但不再接近锁定。来源：https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-july
- FrontierMath 90% 达标市场继续偏乐观但回落：2027 年前有模型达到 ≥90% 的 Yes 为 86.0%，30d 成交约 3.20 万；这是市场预期，不代表基准已被攻破。来源：https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027
- 中国模型公司市场进一步偏向阿里：7 月底 Alibaba 92.0%、DeepSeek 2.6%、Z.ai 1.2%，24h 成交约 1.20 万；相比昨日，阿里小幅上升，Z.ai 预期继续下滑。来源：https://polymarket.com/event/best-chinese-ai-company-end-of-july
- 年底最佳 AI 模型公司市场更分散：Anthropic 64.0%、Google 14.5%、OpenAI 12.5%，流动性约 57.9 万；半年维度仍给 Google/OpenAI 留出比 7 月底市场更大的反超空间。来源：https://polymarket.com/event/which-company-has-best-ai-model-end-of-2026
- “2026 年底是否有模型达到 1560 Coding Arena Score”当前最高档为 39.0%，24h 成交约 2.98 万；市场对代码能力继续跃迁有定价，但原始市场分档标签不清，解读时应看具体规则。来源：https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-december-31
