# AI Agent 日报（2026-06-15）

## 天气

- **北京·海淀：中等阵雨，19.9°C–30.2°C。** 降水概率 31%、预计 3.6 mm，东南风最高 12 km/h；较昨日最高温升约 2.0°C、低温升约 2.8°C，白天更热且雨量明显增加，出门建议带伞并注意闷热。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-15&end_date=2026-06-15)
- **上海·杨浦：小雨，21.9°C–25.1°C。** 降水概率 90%、预计 6.4 mm，东风最高 15.5 km/h；较昨日升温约 1.4–1.6°C，但降雨仍接近全天确定，通勤继续带伞、防滑并预留湿滑路面时间。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-15&end_date=2026-06-15)

**今日取舍：** 天气为每日固定实用信息，不因近两日报告已有同类栏目而去重；保留北京·海淀和上海·杨浦两地当日预报，并仅用近两日报告辅助判断体感变化。

## X Feed

1. **GLM-5.2 被高互动帖称为 “Fully Open”，并把开放前沿模型与近期强模型限制放在同一语境下。** raw 文本在 “certain frontier mode” 后截断，不能补写权重、许可证或下载细节；但今天多条 GLM / ZCode 相关帖子同时出现，说明国产 coding model 的讨论重点正在从“能不能用”转向“是否可开放、可接入团队编码方案、可替代受限前沿模型”。落地评估要回到代码任务通过率、工具调用、长上下文、许可证和本地/企业部署成本。  
   https://x.com/jietang/status/2065784751345287314

2. **Codex 团队成员说 Codex 能看到并设置自己的 `/goal`，并称“我们构建的一切也会作为 agent 的工具”。** raw 被截断，不能展开完整机制；但这是比昨日浏览器 developer mode 更进一步的产品方向：agent 不只是执行用户写好的目标，而是能参与生成、修正和使用目标描述。团队试用时应关注 `/goal` 的来源、可编辑性、审计记录、是否会覆盖人工意图，以及多 agent 子任务目标如何防止漂移。  
   https://x.com/thsottiaux/status/2066270561081454989

3. **Matei Zaharia 宣布开源 Omnigent，一个面向 AI agents 的 meta-harness，可用于构建 multi-agent coding。** raw 文本只展开到 “multi-agent codi…”，不能补写架构；但“meta-harness”本身是明确信号：多 agent 编码开始需要统一的任务编排、上下文、评测和运行环境，而不是把几个 CLI 简单并排跑。采用前应看任务隔离、状态持久化、人工介入、日志回放、失败恢复和不同 agent 间通信是否可审计。  
   https://x.com/matei_zaharia/status/2065827057624605146

4. **KimiDevs 发布 Kimi-K2.7-Code 的 weights 与 code。** 这与 Product Hunt 上同日出现的 Kimi K2.7 Code 信号互相呼应，但这里保留 X raw 的“weights & code”事实；对 coding-agent 用户，关键不是又多一个模型名，而是开源/可下载后能否进入自家 benchmark、私有代码库回归、成本测算和工具调用适配。不要只看社区“接近 Fable”的体验帖，应以可合并 PR、测试通过率和许可证为准。  
   https://x.com/KimiDevs/status/2065625327649640916

5. **Open Code Review 被中文 AI 开发圈传播：前身是阿里集团内部 AI 代码审查助手，称过去两年服务数万开发者、识别数百万代码缺陷，现在开源。** 这比“让 AI 看 diff”更具体，指向 code review 工程化：规则、缺陷类型、上下文检索、误报处理和团队审计。试用时应先在历史 PR 上回放，统计漏报/误报、是否能解释证据、是否尊重项目规范，以及它与人工 reviewer、CI 和安全扫描的职责边界。  
   https://x.com/Smartpigai/status/2066010490602459542

6. **中文帖子称 Anthropic 低调发布 `claude-code-setup` 官方插件，用来把 Claude Code 从“裸跑”升级成更完整的 AI 开发环境。** 同作者另一条补充说它会扫描项目结构、组织工作流；raw 仍较短，不能写成完整官方功能清单。可取的增量是：Claude Code 生态正在把项目初始化、规则沉淀和工作区约束插件化。团队应验证它生成/修改哪些配置、是否会覆盖现有 `CLAUDE.md` / hooks / 权限设置，以及能否版本化进入仓库。  
   https://x.com/VincentLogic/status/2065730997011062940

7. **Claude Code creator 相关摘录称 “100% of our pull requests at Anthropic are run by Claude Code，80–90% of code review too”。** 原帖把 Anthropic 拼成 “Anrtopic” 且 raw 截断，所以只能当作社区转述的强信号，不能当官方统计扩写；但它体现了一个值得跟踪的方向：一线 AI 公司把 coding agent 嵌入 PR 与 review 的比例可能已经很高。读者可把关注点放在 PR 归因、审查责任、测试门禁和人类最终签核，而不是简单模仿比例。  
   https://x.com/0xMovez/status/2066225922928181644

8. **QingQ77 推荐一个基于 `libghostty` 的 GNU screen 风格终端复用器，强调精确屏幕重绘和 AI 友好的自动化接口。** 这不是模型新闻，但对本地 coding agent 很实际：agent 在终端里运行测试、构建、REPL 和长任务时，屏幕状态、滚动、复制、会话恢复和自动化 API 会影响可观察性。评估终端复用器时应看结构化输出、后台任务状态、权限隔离和与 tmux/SSH/IDE 的兼容性。  
   https://x.com/QingQ77/status/2066109895544627344

9. **有人为 Codex 与 Claude Code 做了 Three.js game director skill system，目标是帮助 agents 生成更 polished、可玩的浏览器游戏。** 近两日已有大量 Fable 游戏/视觉 demo，因此这条只保留“skill system”角度：把审美、关卡节奏、交互细节和可玩性变成 agent 可调用的专门 skill，而不是靠一次性 prompt。验证时要看 skill 是否能产生可复用约束、自动测试交互、记录设计决策，并避免只生成炫但不可玩的 demo。  
   https://x.com/majidmanzarpour/status/2066160513969537470

10. **DataChaz 提到一个开源 agent skill，可把 raw 输入转成架构图，试图替代手工拖拽框图。** raw 在 “turns raw…” 后截断，不能补写项目名或格式；但这类 skill 对工程 agent 有明确价值：从代码、说明或系统描述生成架构图，能把 agent 输出从 patch 扩展到可沟通的设计 artifact。采用前要回归图与真实依赖是否一致、更新是否可重复、是否支持人工编辑，以及图生成是否能进入 PR 文档。  
   https://x.com/DataChaz/status/2065735103163363427

**今日取舍：** 已读取 `input.md`、`context.json`、100 个 x-feed raw 文件，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日已覆盖 Codex browser developer mode、Telegram bot 富文本、OpenRouter Fusion、MiniMax M3 权重、Fable 5 大量 demo/WebGPU、Mole、Hermes WhatsApp/Blueprints、OpenAI docs agent、Trellis/harness、Hy-Memory、Trinity、EasyClaw、GLM Coding Plan 等，因此今天优先保留有新事实或新落地角度的 GLM-5.2 fully open、Codex 自设 `/goal`、Omnigent meta-harness、Kimi-K2.7-Code weights/code、Open Code Review、claude-code-setup、Claude Code 进入 PR/review 的使用信号、AI 友好终端复用器、game director skill system 和架构图 agent skill。剔除纯 t.co、无新增转发、课程/提示词营销、Fable 5 限制与视觉 demo 重复、免费额度/中转站/账号充值、金融生活娱乐、证据过短或与 AI/coding-agent 工作流关联弱的内容。

## X 关注

- **Cyril 转述 Anthropic 工程师的说法：不要“提示 Claude”，而要构建一个会自己提示自己的系统。** 这把 agent 设计焦点从单条 prompt 移到运行时：任务分解、状态更新、反思、工具选择和下一步目标应由系统循环管理，而不是每轮靠人工补一句指令。https://x.com/cyrilXBT/status/2066199309888991548

- **Garry Tan 说 AI 不该只用来做简单任务，而要用于涉及多人和多步骤的复杂工作。** 对 agent 团队，这等于把评测从“单次回答是否正确”推向“能否跨角色推进、协调依赖、留下审计记录并在关键节点让人确认”。https://x.com/garrytan/status/2066187431238582700

- **skirano/steipete 的转发给出一个具体工作流：让 Codex 先为自己和每个子 agent 写 `/goal`。** 这比手写大 prompt 更可复用：主 agent 负责把目标拆成可执行目标书，子 agent 按目标推进；风险是目标生成本身也要被 review，否则错误目标会被并行放大。https://x.com/steipete/status/2066246419694948365

- **swyx 转发 autoresearch benchmark：7 个前沿模型在 ML engineering、harness/prompt 等 3 类自动研究任务上被比较。** raw 是转发且被截断，不能写具体排名；但方向明确，研究型 agent 的评估正在从聊天问答转向可复现任务类别、实验 harness 和工程产出质量。https://x.com/swyx/status/2066233371689431427

- **twannl 提到“在 Claude、Codex 和 Cursor 中使用 Xcode 27 Agent Skills”。** 这条证据较短，但对 Apple 开发者很具体：Xcode 技能开始被包装成可给多种 coding agent 复用的上下文/流程；试用时要看技能如何映射到项目结构、构建日志、SwiftUI 预览和测试失败。https://x.com/twannl/status/2066225722444718146

- **Garry Tan 吐槽想给 agent 单独买 Spotify 订阅，避免引用歌词时触发过多拒答。** 这不是娱乐八卦，而是版权内容让 agent 工作流中断的实际边界：写作、营销和内容分析 agent 需要区分可引用范围、授权来源、替代摘要和人工确认，而不是把所有版权文本都当成普通上下文。https://x.com/garrytan/status/2066151773874815386

- **yanhua1010 调研多 agent 并行开发时该用 git branch 还是 git worktree。** 互动很低，但问题本身切中落地：多个 agent 同时改同一仓库时，隔离目录、依赖安装、测试缓存、冲突合并和回滚点会决定并行是否真的省时间。https://x.com/yanhua1010/status/2066170060218187845

- **servasyy_ai 看到一个 vibe coding 做的 Chrome 扩展，把 AI 聊天伪装成 Google Docs。** 功能本身偏玩具，但它暴露了企业环境的真实风险：AI 使用会被伪装进常见办公界面，安全策略不能只靠应用名识别，还要看网络请求、剪贴板、浏览器扩展权限和数据外发。https://x.com/servasyy_ai/status/2066161410955264392

**今日取舍：** 已读取 `input.md`、`context.json`、100 条 x-following raw，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日已覆盖 Hermes WhatsApp、OpenAI docs agent、Codex 浏览器/爬虫模式、长程 session commit、Loopcraft、Mole、Claude Design/Fable 5 大量讨论和研究 agent 成本信号，因此今天优先保留新增的 self-prompting agent 系统观、多步骤复杂任务、Codex 生成 `/goal`、autoresearch benchmark 方向、Xcode Agent Skills、版权拒答边界、多 agent git 隔离问题和 AI 伪装扩展风险。剔除政治/教育/生活娱乐/投资、纯 t.co 或转发无新增、Fable 5 泛赞美/禁用/泄露重复帖、Mole 重复、课程/提示词营销、通用 Swift 技巧、数据中心/住房宏观讨论，以及与 AI/coding-agent 工作流关联弱于入选项的内容。

## Reddit 社区

- **今日不展开新条目：本次 Reddit 采集在 diagnose/retry 后仍未提供可读 raw corpus，package 标记 raw 缺失（0 个 raw 文件），因此没有可用于判断的 Reddit 社区新增事实。** `input.md` 标记 `Raw corpus status: missing`，Raw file index 为 “No raw files found”；`context.json` 同样标记 `raw_corpus_status: "missing"`、`raw_file_count: 0`。按本 lane 的 direct raw evidence 要求，今天不使用 audit-only `selected_items.json`、历史报告或其他 lane 作为替代来源补写 Reddit 条目。

**今日取舍：** 已读取 `daily-report-lane-reddit` skill、`input.md`、`context.json`、raw 文件索引和 2026-06-14 / 2026-06-13 历史报告；历史仅用于确认近两日 Reddit 栏处理方式与去重背景，未作为今天事实来源。近两日已分别处理过 Reddit 429 全阻断与一次部分降级采集；2026-06-15 本包仍没有任何可读 Reddit raw，因此输出 blocked/degraded empty：不复述近日报告中已提到的 Claude Fable 5、Claude Code/Codex adversarial review、AgentMemory、Skill Index、app-it、SEO/growth workflow、多 agent 协作、Lore 记忆等旧主题，也不发明 Reddit 社区增量。

## Hacker News 热榜

- **Kage 以 HN #1 上榜：把任意网站“shadow”成单个二进制用于离线浏览，277 分、61 评论。** 评论里的实用场景集中在公司 wiki / 文档离线分发：在无网络现场也能查内部资料；同时也有人追问既然结果是静态内容，为什么还需要 `kage serve` 而不是一个可直接打开的 HTML 入口。对 agent / 开发团队来说，它不是 AI 工具本身，但切中“把文档、runbook、知识库打包成可携带、可复现上下文”的基础设施问题。 [HN](https://news.ycombinator.com/item?id=48529990) / [GitHub](https://github.com/tamnd/kage)

- **Rio de Janeiro 的“homegrown” LLM 被质疑其实是现有模型权重合并；HN #4、231 分、125 评论。** 链接 issue 称 Rio-3.5-Open-397B 的权重像是约 60% Nex-N2 Pro + 40% Qwen3.5-397B-A17B 的线性混合；评论也提醒可能存在“上传了错误模型 / 缺少后续 distillation 版本”的解释，结论仍需等官方上传正确模型或补充说明。对开源模型和 agent 选型，重点是 provenance：模型声称、base model、merge/finetune/distillation、许可证和 benchmark 都要可验证，不能只看“本土/自研”标签。 [HN](https://news.ycombinator.com/item?id=48528371) / [Issue](https://github.com/nex-agi/Nex-N2/issues/4)

- **Show HN: Trace 是一个离线 Mac 会议转录工具，可用快捷键在会中标记关键时刻；HN #7、58 分、15 评论。** 作者强调所有转录模型本地运行，首次从 Hugging Face 下载约 500MB 模型后可离线使用，输出音频和 Markdown transcript；Trace 本身不做总结，但会把会中 flag 和备注按时间戳写进 transcript，方便之后交给 LLM 处理。评论把它和 MacWhisper 等工具比较，指出真正难点是 crash recovery、磁盘占用、麦克风串音和低延迟 live recap；这对会议/个人知识 agent 的启发是：原始记录、实时标注和本地隐私边界，比“会后自动总结”更基础。 [HN](https://news.ycombinator.com/item?id=48521236) / [Trace](https://traceapp.info)

**今日取舍：** 已读取 `input.md`、`context.json`、10 条 HN topstories raw 文件，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日 HN 热榜已覆盖 Pyodide WebAssembly wheels、Anthropic 模型限制、AI 证据可信度、本地 coding agent、agentic analytics、AI 前端质量、KV cache 复用和 Fable 5 游戏原型等，因此今天保留新的离线网站打包、开源 LLM provenance / 权重合并争议、以及本地会议转录 + 会中标注工作流。剔除 Firewood Splitting Simulator、Segmented type、Yserver、Chaosnet、Zinnia 等主要因为它们虽有技术/趣味价值，但与 AI/coding-agent 工作流的直接增量弱；`Ask HN: What are you working on?` 评论量高但主题过散，未形成比入选项更明确的当日信号；`zeroserve` 的 Caddy 兼容讨论偏通用服务端性能与 ACME/插件缺口，也不如入选项贴近本日报告主线。

## Hacker News 搜索观察

- **Ask HN 追问“有没有人真的用 AI agents 做出能独立存在的软件”，评论给出了一些低调但具体的生产用例。** 原帖质疑 agentic workflow 的展示常常又是在造 AI 工具；评论里有人称过去 6 个月用 Claude 重写了有 15 年历史的内部工具前后端，客户应用的维护和新功能也“99% AI agent written”，但不会公开宣传；另一个非技术场景的例子是用 Claude 快速做出前端，并从分散的行业知识与法律文本中整理数据、生成地理多边形。当前只有 3 分、9 评论，不能当成行业统计，但它补上了一个重要盲点：真实 agent 产出可能更多藏在内部工具、垂直数据整理和非技术部门自动化里，而不是公开的“AI 做 AI 工具”demo。 [HN](https://news.ycombinator.com/item?id=48528665)

- **一个新开发者用 Claude + Perplexity 做出面向英国个体经营者的 bookkeeping app，重点教训是“把 AI 当 pair programmer，而不是无条件代码生成器”。** 作者自述在一个月内做 QuarterPerfect：支持银行 CSV/PDF 导入、交易分类、receipt matching、merchant rules、只读 accountant share link，并要面对 HMRC / MTD ITSA 的合规细节；早期问题是过度接受 AI 输出，后来改成让 Perplexity 帮忙整理想法和生成给 Claude 的详细 prompt，再把结果回传 Perplexity，同时让两者协助项目管理结构。分数和评论都很低，且故事被截断，不能夸大产品成熟度；但它比一般“vibe coded app”更有用的信号是：AI 能把新手推到有支付/合规/真实用户风险的领域，随之而来的责任是人必须理解领域假设、能为 shipped decision 负责，并建立项目结构与人工复核。 [HN](https://news.ycombinator.com/item?id=48527480)

**今日取舍：** 已读取 `input.md`、`context.json`、15 个 HN search raw 文件，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日报告已覆盖 Spanly、低成本本地 VS Code agent workflow、LoadLore、Janus，并在昨日覆盖多 coding-agent 长跑工作流与生产 agent human review / 审批审计，因此今天不重复 48520757、48510369 等旧条目。保留 48528665，因为它把“真实软件是否由 agents 构建”从质疑推进到内部工具、客户应用维护和非技术场景数据产品的具体例子；保留 48527480，因为它提供了新开发者在合规/会计产品中使用 Claude + Perplexity 的工作流与风险教训。剔除 Hydron、Zedra、Cordium、AgentGraphed、LoadLore、Spanly、Checkpoint、Claude Design+Vercel Drop、BeamWeaver、Janus、Omegacode、多 worker 长跑帖和 human-review Ask HN 等，原因是近日报告已覆盖、raw 证据太薄、0 评论无新增，或与 AI/coding-agent 工作流的当日增量弱于入选项。

## Claude Code

- **今日不展开新条目：本次 Claude Code raw corpus 正常，共 3 个 release 文件，但 `v2.1.175`、`v2.1.176`、`v2.1.177` 均已在 2026-06-14 / 2026-06-13 报告中实质覆盖，今天没有新的 release note 或功能事实突破去重线。** 当前 raw 里最新版本仍是 [`v2.1.177`](https://github.com/anthropics/claude-code/releases/tag/v2.1.177)，但 release notes 为空，只列出 macOS / Linux / Windows 资产、`SHASUMS256.txt` 与签名；因此不能从版本号或资产大小推断新能力。`v2.1.175` 的 `enforceAvailableModels` managed setting，以及 `v2.1.176` 对 allowlist alias/env 绕过、`/fast`、Remote Control、background agents、Bedrock credential caching、Fable 5 auto fallback、hook path matching、Linux sandbox、tmux/SSH copy、Windows daemon/state 等修复，已在近两日报告展开，今天只作为升级回归背景保留，不重复改写成新条目。

**今日取舍：** 已读取 `input.md`、`context.json`、3 个 raw release 文件，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日已覆盖 `v2.1.172` nested sub-agents、后台隔离、模型限制/Bedrock/1M context，`v2.1.173` Fable 5 `[1m]` 归一化与 Windows sandbox 假警告，`v2.1.175` managed model allowlist enforcement，`v2.1.176` 模型治理、Remote Control、background sessions、Bedrock、hooks、sandbox、tmux/SSH 修复，以及 `v2.1.177` “最新但无 changelog”的版本信号。本次 package 没有比这些更多的新事实，因此按“拒绝精确重复或实质未变主题”的要求输出 unchanged/empty lane；资产矩阵不展开。

## Codex

- **Codex `0.140.0-alpha.19` 继续滚动，release notes 仍只有占位标题；`alpha.17/18` 昨天已展开，今天只作为版本列车背景。** 本次 raw 中 `alpha.19` 仍延续同一套资产矩阵（macOS / Linux / Windows、npm、Python wheel、app-server、responses-api-proxy、`codex-command-runner`、Windows sandbox setup、`codex-zsh`、schema、安装脚本和符号包等），因此不要从 alpha 号推断功能，应按下面的 PR/commit 做回归。 [alpha.19](https://github.com/openai/codex/releases/tag/rust-v0.140.0-alpha.19)

- **插件 auth-routing 继续收窄到“同名 App declaration 才隐藏 MCP”：ChatGPT/SIWC 只会在插件同时声明同名 App 和 MCP server 时优先 App，其他 MCP server 保留。** #27607 是昨天插件 auth surface stack 的下一步：保留插件 metadata 里的 App declaration names，同时让公开 effective Apps 继续以去重 connector ID 输出。升级后要回归双表面插件、非冲突 MCP、connector listing、安装缓存和显式 plugin mention，避免把一个插件里的所有 MCP 都误隐藏。 [PR #27607](https://github.com/openai/codex/pull/27607)

- **app-server 新增实验性 `parentThreadId` 过滤：`thread/list` 可直接返回某个 thread 的直接 spawned children。** 这解决了客户端恢复或展示 subagent 树时只能扫全部 threads、再靠 rollout history/事件重建关系的问题；实现只读取 persisted `thread_spawn_edges`，不递归返回孙辈，也排除 Review / Guardian threads，并保留原有 filters、排序和 timestamp cursor 语义。使用多 agent / subagent UI 的团队应把 direct child、grandchild omission、混合 source、分页、无 rollout 文件和非法 ID 纳入 smoke。 [PR #26662](https://github.com/openai/codex/pull/26662)

- **跨 OS 路径与远程执行栈继续推进：`PathUri` 增加 native path 渲染，exec-server 开始保留 remote environment cwd 并使用目标环境 shell。** #27819 新增 `PathConvention` / `NativePathString`，可按 POSIX、Windows drive、UNC 等约定把 `PathUri` 转成面向客户端/目标环境的普通路径；#28122 / #28123 则把 turn environment cwd 迁到 `PathUri`，避免 remote primary cwd 被本地 fallback 覆盖，并优先使用 selected environment 发现到的 shell。对 Linux-to-Windows、Wine-backed Windows fixture、权限请求边界和 app-server API path 展示都要做跨平台回归。 [PR #27819](https://github.com/openai/codex/pull/27819) / [PR #28122](https://github.com/openai/codex/pull/28122) / [PR #28123](https://github.com/openai/codex/pull/28123)

- **Bazel / Wine 测试基础设施被补强：Wine harness 加入 x86_64 PowerShell，并把 buildifier 纳入统一 `just fmt` / `fmt-check`。** PowerShell smoke test 让跨 OS exec-server 测试能跑真实 Windows shell 场景，而不只是验证早期路径或 shell mismatch；buildifier 则通过 SHA-256-pinned DotSlash manifest 固定 v8.5.1，并在 CI、devcontainer 和 Windows-safe invocation 中统一 Starlark/Bazel 格式。贡献者升级后应确认 DotSlash/buildifier 可用、`just fmt-check` 覆盖 Bazel 文件，以及 Wine/PowerShell fixture 不受本机环境差异影响。 [PR #28120](https://github.com/openai/codex/pull/28120) / [PR #28125](https://github.com/openai/codex/pull/28125)

- **Codex 把 bundled SQLite 依赖钉到包含 WAL-reset 修复的版本，避免 lock refresh 静默降级到受影响 SQLite。** SQLx 0.9 对 `libsqlite3-sys` 的范围较宽，曾让 bundled SQLite 从 3.51.3 回退到 3.50.2；#27992 固定到带修复的版本，重点是防止依赖刷新把本地状态数据库带回 WAL reset corruption 风险。升级或刷新 lockfile 后，应核对 bundled SQLite / `libsqlite3-sys` 版本和状态库迁移/恢复 smoke。 [PR #27992](https://github.com/openai/codex/pull/27992)

**今日取舍：** 已读取 `input.md`、`context.json`、18 个 Codex raw 文件，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。昨日已覆盖 `alpha.17/18`、插件 auth route 大框架、本地插件建议收口、managed remote-control deny gate、exec-server PathUri/Wine、turn-state/compact 和 Windows ARM64 packaging，因此今天避免复述这些旧项，只保留新增的 `alpha.19`、插件同名 App/MCP dedupe、`thread/list parentThreadId`、PathUri native rendering + remote cwd/shell follow-up、PowerShell Wine / buildifier 基建和 SQLite WAL-reset pin。commit raw 与 merged PR raw 重复时合并为同一条证据。

## OpenClaw

1. **OpenClaw 2026.6.7 beta 把多通道投递、模型容错和发布验证继续补齐。** 这版修复 Slack 同频道 final 转录、Telegram blockquote/草稿回放、静默回复、分页 action results，并加入 Kimi K2.7 Code、Anthropic thinking replay 修复和 QA scorecard/evidence 产物；升级前可重点回归通道投递与 provider fallback。  
   https://github.com/openclaw/openclaw/releases/tag/v2026.6.7-beta.1

## GitHub AI 项目

- **今日不展开新条目：本次 github-ai-projects 是 derived lane，没有独立采集器；package 中可用的上游 GitHub 证据正常，但没有新的仓库同时满足“来自 raw corpus、stars ≥100、AI/coding-agent 工作流相关、且未在近两日报告实质覆盖”的入选线。** 最接近的 `addyosmani/agent-skills`、`NVIDIA/SkillSpector`、`huggingface/OpenEnv` 已在 2026-06-14 的 GitHub AI 项目栏逐条展开；今天 raw 仍是同一批 GitHub trending weekly / selected-items-compatible 证据，没有新增事实足以突破去重线，重复写入会变成旧信号复述。

**今日取舍：** 已读取 `input.md`、`context.json`、GitHub trending weekly raw、HN/X 跨 lane GitHub 证据、selected-items-compatible evidence，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，`selected-items` 仅作 audit 参考，未作为主要判断。按 hard floor stars ≥100 和相关性要求，今天不选择新仓库。近两日报告已展开或明确去重 `addyosmani/agent-skills`、`NVIDIA/SkillSpector`、`huggingface/OpenEnv`、`NVIDIA/cosmos`、`refactoringhq/tolaria`、`aaif-goose/goose`、`phuryn/pm-skills`、`Panniantong/Agent-Reach`、`mvanhorn/last30days-skill`、`chopratejas/headroom`、`Leonxlnx/taste-skill` 等；同时剔除通用容器、文档转换、旧 OpenAI plugins、NotebookLM 复刻、通用计算机视觉库、Mattermost/PowerToys 等与 AI/coding-agent 工作流关联弱于入选线或已在近日报告覆盖的项目。

## GitHub 趋势项目

- **今日不展开新条目：本次 GitHub trending weekly raw corpus 正常，共 19 个仓库信号，但没有新的仓库同时满足“AI/coding-agent 工作流相关、stars ≥100、且未在近两日报告实质覆盖”的入选线。** `addyosmani/agent-skills`、`NVIDIA/SkillSpector`、`huggingface/OpenEnv` 等已在 2026-06-14 的 GitHub 趋势项目栏展开；`aaif-goose/goose`、`Panniantong/Agent-Reach`、`mvanhorn/last30days-skill`、`chopratejas/headroom`、`Leonxlnx/taste-skill`、`phuryn/pm-skills`、`refactoringhq/tolaria` 也已被近两日报告覆盖或明确去重，今天 raw 只重复同一行定位，没有新增事实。

**今日取舍：** 已读取 `input.md`、`context.json`、19 个 GitHub trending raw 文件，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。已用 GitHub API 校验 raw 仓库 stars 均 ≥100，因此未因硬 floor 剔除；最终剔除原因是近两日已实质覆盖、raw 证据无新增，或项目虽有星标但属于通用容器、协作平台、Windows 工具、文档转换、NotebookLM 复刻、计算机视觉/音乐服务等，与 AI/coding-agent 工作流的当日增量弱于入选线。

## Rize AI 工具榜

- **今日不展开新条目：本次 Rize raw corpus 正常，共 20 个 GitHub 仓库排名信号；但 #1–#20 与 2026-06-14、2026-06-13 历史报告中的 Rize 快照实质一致，没有新增排名事实或项目描述变化足以突破去重线。** 当前榜首仍是 #1 [awesome-architecture](https://github.com/study8677/awesome-architecture)、#2 [SenseNova-Skills](https://github.com/OpenSenseNova/SenseNova-Skills)、#3 [awesome-agentic-ai-zh](https://github.com/WenyuChiou/awesome-agentic-ai-zh)、#4 [remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks)、#5 [fireworks-tech-graph](https://github.com/yizhiyanhua-ai/fireworks-tech-graph)、#6 [LTX-2](https://github.com/Lightricks/LTX-2)、#7 [easy-vibe](https://github.com/datawhalechina/easy-vibe)、#8 [modly](https://github.com/lightningpixel/modly)，排名页仍为 [Rize AI Tools](https://rize.io/ai-tools)。这些条目已在 2026-06-10 按排名快照价值逐条展开，2026-06-11 至 2026-06-14 也连续判定为未变快照；今天重复写入会变成同一榜单的复述。

**今日取舍：** 已读取 `input.md`、`context.json`、20 条 Rize raw，以及 2026-06-14 / 2026-06-13 历史报告；历史仅用于去重参考，未使用 `selected_items.json` 作为主要判断。Rize 榜单是 weekly ranking 快照事实，但本次 #1–#8 与近两日报告中的 Rize 正文完全相同，#9–#20（ECC、ClawX、OpenKB、rocketride-server、open-code-review、OB1、memory-lancedb-pro、QuantDinger、awesome-codex-skills、Clawith、inkos、any-auto-register）也仍是同一批未展开候选，且 raw 只提供同样的一行项目描述；因此按“拒绝精确重复或实质未变主题”的要求输出空结果，只保留 unchanged snapshot 说明和链接。

## Product Hunt 新品

- **Conan** 发布到 Product Hunt，定位为 Claude Code 的原生 Mac cockpit。它把 Claude Code 从纯终端体验扩到桌面控制台；试用时应重点看 session 管理、权限提示、命令执行可见性和与现有 Claude Code 配置的兼容。 [Product Hunt](https://www.producthunt.com/products/conan?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **Memoriq** 主打面向 ChatGPT、Claude、Gemini 和 Grok 的私有 AI memory。对长期使用多模型 agent 的读者，关键是能否把偏好、项目事实和历史决策跨工具复用；落地前要核对记忆写入、删除、纠错、导出和隐私边界。 [Product Hunt](https://www.producthunt.com/products/memoriq?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **Taste Lab** 用 AI 提取任意网站的 “design DNA”。它更适合作为前端/设计 agent 的上下文采集工具：把竞品页面的视觉规则转成可引用素材；raw 未说明采集粒度、版权边界或是否输出结构化 token，试用时不要直接当成可复用设计规范。 [Product Hunt](https://www.producthunt.com/products/taste-lab?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** raw corpus 状态为 ok，共 5 个 Product Hunt topic hit；已读取 `input.md`、`context.json`、全部 raw 文件和 2026-06-14 / 2026-06-13 历史报告，仅用历史作去重参考，未使用 `selected_items.json` 驱动判断。近两日 Product Hunt 栏已覆盖 Kimi K2.7 Code、Prometheus by Firecrawl、Bob's CLI、Qursor、Slack Data Agent 等代码模型、网页数据 agent、本地 CLI、UI 上下文和数据问答入口；今天保留新的 Claude Code Mac cockpit、跨模型私有记忆和网站设计上下文提取。剔除 Cloudback for Linear（Linear 备份/恢复，偏通用开发协作运维）与 Slashy（邮件 AI 助理，和 coding-agent 工作流关联弱于入选项）。

## Polymarket AI 市场

- **6 月最佳 Coding AI 模型盘口继续压向 Anthropic：Anthropic 96.5%，OpenAI 2.0%、Z.ai 1.1%；24h 成交量约 1,108.6，30d 约 51,665.8，流动性约 71,349.2，raw 标注本周上行 5.0%。** 较昨日报告的 96.2% 小幅抬升，市场仍把月底 coding 领先者预期集中在 Anthropic；但这只是交易者预期，不能替代自家 repo 的可合并率、测试通过率和长任务稳定性评测。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-june)

- **6 月最佳 AI 模型总榜维持 Anthropic 高位：Anthropic 89.2%，Google 6.5%、OpenAI 4.5%；24h 成交量约 1,118,521.3，30d 约 8,637,457.1，流动性约 3,026,536.6，raw 标注本月下行 1.0%。** 较昨日报告的 88.3% 略升，高流动性主盘仍显示通用强模型情绪偏向 Anthropic；做 agent 选型时仍要拆分 coding、数学、工具调用和长上下文表现。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **6 月最佳 Math AI 模型盘口继续与总榜分化：Google 62.5%，Anthropic 20.0%、OpenAI 11.5%；24h 成交量约 1,934.6，30d 约 183,327.1，流动性约 76,847.2，raw 标注本周上行 4.5%。** 昨日报告 Google 为 64.5%，今天仍明显领先；数学/形式化推理类 agent 不应直接照搬通用模型总榜情绪。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-june)

- **FrontierMath 长盘继续回落但仍偏高：任一 AI 模型 2026 年前 ≥90% 的 Yes 为 79.5%，24h 成交量约 2,314.8，30d 约 21,730.9，流动性约 5,950.8，raw 标注本周上行 58.5%。** 昨日报告该盘为 83.5%，今天再降；同批 xAI/Grok FrontierMath 子盘流动性很低且阈值标题/主 outcome 有混淆，只能作为弱参考，不能写成模型成绩已确认。 [Polymarket](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027) / [Grok 市场](https://polymarket.com/event/xai-grok-score-on-frontiermath-benchmark-by-june-30)

- **Coding Arena 月底门槛盘更谨慎：6 月 30 日达到 1550 的主概率为 10.5%，24h 成交量约 397.7，30d 约 1,146.3，流动性约 2,445.1，raw 标注本周下行 44.0%。** 昨日报告同类月底门槛为 19.0%，今天明显降温；由于 raw outcomes 都显示为 `any AI model`，只能解读为月底高分突破预期转弱，不能推断具体模型或完整门槛曲线。 [Polymarket](https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-june-30)

**今日取舍：** raw corpus 状态为 ok，共 11 条 Polymarket 证据；已读取 `input.md`、`context.json`、全部 raw 摘要/文件索引和 2026-06-14 / 2026-06-13 历史报告作为去重参考，未使用 `selected_items.json` 驱动判断。保留与 AI/coding-agent 直接相关、且有当日概率/成交量或近日报告可比变化的 6 月 Coding AI、6 月模型总榜、6 月 Math AI、FrontierMath 长盘/Grok 弱参考和 Coding Arena 月底门槛；剔除估值盘、Style Control 版总榜、7 月最佳模型、第二名细分盘口等重叠或弱增量条目。所有概率均为 Polymarket 市场预期，不是已确认 benchmark 或产品事实。
