# AI Agent 日报（2026-06-07）

## 天气

- **北京·海淀：小毛毛雨，11.3°C–24.6°C。** 降水概率 35%、预计 0.6 mm，西风最高 11.7 km/h；相比昨日中雨明显转弱、最高温回升约 2.1°C，但最低温下降约 3.0°C，早晚偏凉，出门备轻便雨具。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-07&end_date=2026-06-07)
- **上海·杨浦：阴，20.0°C–27.5°C。** 降水概率 16%、预计 0 mm，东北风最高 13.2 km/h；较昨日仍偏干、气温小幅回升，通勤基本不受降雨影响，午后体感略热。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-07&end_date=2026-06-07)

**今日取舍：** 天气为每日固定实用信息，不因近两日报告已有同类栏目而去重；保留北京·海淀和上海·杨浦两地当日预报，并仅用近日报告辅助判断体感变化。

## X Feed

1. **Codex activity 有了个人主页：activity graph、streaks 和分享入口都被放到 Codex profiles 里。** 这说明 OpenAI 正把 Codex 从“单次 coding 会话”推向可展示、可追踪的开发者活动层；对团队和开源维护者，后续要看 profile 隐私、项目边界、分享粒度和是否会变成 agent 工作成果的默认履历。  
   https://x.com/OpenAIDevs/status/2062674774644687268

2. **Codex Product Design 插件被中文圈重点转述：把产品设计判断直接塞进 coding agent 工作流。** 这和昨日 MagicPath 的“生成插画素材”不同，Product Design 更像让 Codex 在 UI 审美、组件布局和产品表达上补短板；适合前端 demo、落地页和原型迭代，但仍要靠设计规范、截图验收和人工 review 防止“看起来高级但不可用”。  
   https://x.com/BTCqzy1/status/2063165828208746639

3. **Claude Cowork 临时把使用额度翻倍一个月，官方口径是“delegates bigger, more complex tasks”。** 这是很直接的产品信号：Claude 正鼓励用户把更大、更复杂的任务交给 cowork / agent 模式；真正要观察的是额度提高后，长任务的上下文恢复、失败重试、权限审批和结果验收是否跟得上。  
   https://x.com/claudeai/status/2063018337567670285

4. **Elon Musk 只写了一句 “Grok supports worktrees”，但命中并行 agent 开发的关键执行面。** worktree 支持意味着同一仓库可并行跑多个隔离分支，避免 agent 互相覆盖文件；这与近日报告里 HN 的 Lich、本地 dev stack 隔离是同一方向：多 agent 不是多开聊天窗口，而是要有版本、端口、进程和验证环境隔离。  
   https://x.com/elonmusk/status/2062796095764234421

5. **Codex 频繁 Reconnecting 的社区 workaround/修复帖开始传播。** @alin_zone 称已有解决方案可尝试；即使原帖细节需要点开核对，这条也暴露了云端 coding agent 的高频痛点：网络/会话重连不是小瑕疵，而会直接打断长任务、压缩和工具调用。重度用户应把重连恢复、会话保存和降级路径写进日常操作手册。  
   https://x.com/alin_zone/status/2063110484409430017

6. **GitHub Daily 推荐 BrowserAct：给浏览器自动化 agent 提供三层反封锁机制。** X 摘要称它面向 AI Agent 操作浏览器或抓数据时遇到的反爬、验证码和人机验证问题，是一个浏览器自动化命令行工具。它的价值不在“又能点网页”，而在把 web-agent 的真实失败面——反自动化、会话维持、验证中断——做成工具层能力。  
   https://x.com/GitHub_Daily/status/2062746268993216772

7. **Codex / Claude Code 的“项目记忆文件 + AGENTS.md”实践继续被普通用户总结。** @legacyvps 分享会给 Codex 部署两个文件：踩坑记录让 AI 避免重复犯错，AGENTS.md 写项目通用规范。它不是新功能发布，但很可行动：长期 coding agent 的质量提升，往往来自把团队约定、错误复盘和项目规则沉淀成可读文件，而不是每次重新口头提醒。  
   https://x.com/legacyvps/status/2063247378833191316

8. **“awesome codex skills” 类合集开始把 Codex skills 当成可复用生态来整理。** @aronhouyu 转述该合集收录 1000+ skills，并提到支持 Claude Code、Gemini CLI、GitHub 等入口；数字和覆盖范围需以仓库核对，但方向明确：skills 正从个人提示词资产变成跨 agent 工具包，下一步关键是版本、测试、权限声明和质量评分。  
   https://x.com/aronhouyu/status/2063092531563549024

9. **VoxCPM2 语音合成在中文 X 上爆火，被描述为 GitHub 趋势榜第一、2 万+ stars。** 这条更偏多模态基础能力，但对 agent 产品很具体：语音输出越来越接近可直接进入教育、陪伴、内容生产和电话/桌面 agent 场景。要谨慎的是，日报不能只看 demo 震撼度，还要看授权、延迟、可控性、水印和滥用防护。  
   https://x.com/QT9277/status/2062705714943152175

10. **Step 3.7 Flash 的原生多模态 demo 被转述为“识别电脑主机接口，10 秒内输出教学步骤，约 400 tokens/s”。** 这类视觉理解 + 高速文本输出，正好适合桌面/硬件排障 agent：看图识别接口、解释概念、生成操作步骤。单条 demo 不能替代系统评测，但它提示多模态 agent 的竞争会从“能看懂图片”走向“能在真实操作流里快速给出可执行指导”。  
   https://x.com/gengdaJ/status/2063067388028039360

**今日取舍：** 已读取 `input.md`、`context.json`、100 个 x-feed raw 文件，以及 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日已覆盖 Codex iOS/Data Science/Sites、Codex 设置搜索/Python SDK/MagicPath、Cursor Canvas/Design Mode、Paxel、OpenAI 误封、Palantir 数据治理、Hermes Studio 多设备、Kimi Work、Codex for Open Source、Hermes 中文支持、Gemma 4 QAT、Paxel 和 OpenAI 平台导航等，因此今天避免重复这些已展开主题；保留 Codex profiles、Product Design 插件、Claude Cowork 额度、Grok worktrees、Codex 重连问题、BrowserAct、AGENTS.md/踩坑记忆、skills 合集、VoxCPM2 和 Step 3.7 Flash 这些有新增事实或能落到 agent 工作流的信号。剔除纯 t.co、生活/财经/币圈/政治/泛流量课、与近日报告实质重复的 Hermes 中文/桌面介绍、Paxel、Gemma 4 QAT、Codex for Open Source、Claude 提示词课程和普通 GitHub 免费项目清单，以及证据过短不足以支撑具体结论的内容。

- **Codex iOS 的语音输入有一个实用细节：把 Codex app 切到后台后，dictation mode 仍会继续录音。** Nick Dobos 和 Dimillian 都提到可一边使用自己的 app、一边持续对 Codex 说需求；这让移动端 coding-agent 更接近“边试用边口述修改”，但也要注意误录、隐私和会话上下文边界。https://x.com/NickADobos/status/2063327344304271852 / https://x.com/Dimillian/status/2063339981804847400

- **Codex 远程控制 3DS 的小实验显示，agent 可以通过 FTP 等普通接口操作非典型设备。** Dimillian 说已把 3DS 上 FTP server 的 IP 给 Codex，Codex 可直接上传文件；这不是正式产品能力，但说明 coding-agent 的执行面正在从桌面/云环境扩到任意可脚本化硬件。https://x.com/Dimillian/status/2063346025926934605 / https://x.com/Dimillian/status/2063355217832190210

- **dotey 继续修 Hermes Agent Desktop 多语言：从“基础中文支持”推进到补齐硬编码文字。** 他提到最初 PR 只是基本多语言，仍有大量英文，昨天花时间补覆盖；这是昨日“中文支持已合入”的后续，新增点在本地 agent 产品国际化进入硬编码 UI 清理阶段。https://x.com/dotey/status/2063277561266782661

- **wanman 下一版计划把多个 vibe 产品里的 agents 互联，做成“虚拟公司”式工作流。** turingou 举例说可用 mails 管理公司域名邮件，并把邮件里的电话等信息交给 wanman agent 处理；raw 被截断，不能展开完整功能，但信号是个人/小团队 agent 正从单任务工具转向多角色、多渠道协作。https://x.com/turingou/status/2063373480184484016

- **Codex app 更新后弹出新的 macOS 权限提示，提醒本地 agent 的系统权限仍是用户体验关键点。** turingou 的帖子没有展开权限类型，但足以说明桌面 coding-agent 每次新增系统能力都会触发“为什么要这个权限”的信任问题；产品需要把权限用途、范围和可撤销性讲清楚。https://x.com/turingou/status/2063261258976252381

- **Codex 和 Claude Code 仍没有 Linux 桌面版，引发中文开发者直接吐槽。** dashen_wang 的抱怨不是功能发布，但对重度开发者有现实意义：当 coding-agent 桌面入口优先覆盖 macOS/Windows，Linux 用户只能依赖 CLI、Web 或远程环境，体验和权限模型都会不同。https://x.com/dashen_wang/status/2063263556599247021

- **OpenClaw 生态出现“205 个可复制 SOUL.md agents”的项目推荐。** GithubProjects 称这些 agents 都打包成单个 SOUL.md 文件、可在 OpenClaw 生态中使用；证据较短，不能判断质量，但它反映 agent 模板正在从 prompt 片段变成可复制的角色/流程文件。https://x.com/GithubProjects/status/2063327571698434443

- **“Vibe Coding”命名继续被中文开发者反思，dotey 更倾向把程序员描述为指挥 AI 的 Tech Lead。** 他的具体拆解是：人负责分解任务、架构选型、代码审查和验收，AI 负责实现；这不是新工具，但能帮助团队把 coding-agent 使用规范从“让 AI 随便写”改成工程管理流程。https://x.com/dotey/status/2063282159259898162

**今日取舍：** 已读取 `input.md`、`context.json`、100 条 x-following raw，以及 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日已覆盖 Codex iOS 插件、Codex 设置/自动化/压缩恢复、Cursor UI、Hermes 中文支持、OpenAI 误封、Anthropic 加速 AI development、ChatGPT memory、OpenClaw/Hermes 泛信号等，因此今天只保留有新增细节的 Codex iOS 后台听写、Codex 3DS 远程实验、Hermes 多语言硬编码清理、wanman agents 互联、Codex macOS 权限提示、Linux 桌面缺口、OpenClaw SOUL.md agents 和 Vibe Coding 角色拆解。剔除生活/政治/投资/娱乐、纯转发无细节、与近日报告实质重复的 Anthropic recursive self-improvement / Claude 8x code、Claude rate limits、Claude Desktop 泛体验、ChatGPT memory、OpenAI 误封、课程/活动宣传和证据截断到无法支撑具体结论的项目。

## Reddit 社区

- **生产环境里的 MCP 痛点被一位 agent 实施者拆得很具体：6 个服务器、约 180 个工具，Claude 还没执行任务上下文条就先变橙。** 他的案例里，Slack 工具因描述更长且多次出现“find”抢过 Stripe 发票查询，OAuth token 还留在离职承包商本机；可行动结论是把 MCP 工具描述、顺序、授权归属和冷启动 token 成本当成生产配置审计。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1tuqqpn/i_ship_ai_agents_in_production_the_mess_is_mcp/)

- **多 agent 协作帖的增量不在“谁更强”，而在独立探索后再综合：Claude Code、Codex、Hermes Agent、OpenClaw 本地/远程各自找资料，再由 Supervisor 汇总。** 作者观察到不同 agent 会稳定挖到不同来源，过早共享上下文反而可能收敛；真正难点变成冲突结论的 synthesis、任务是否拆分、以及本地/远程 agent 的桥接协议。 [Reddit](https://www.reddit.com/r/ClaudeAI/comments/1tw9sjc/i_made_claude_code_interoperable_so_it/)

**今日取舍：** 已读取 `input.md`、`context.json`、31 个 Reddit raw 文件，以及 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。raw 中 Reddit 评论数均为 0 或未提供可读评论，因此只能写帖子正文里的实践细节。近两日已覆盖 Opus 4.8/dynamic workflows、SDK 额度、AgentMemory/Skill Index、Claude Code 终端技巧、离线 Claude Code、语音输入、个人 agent manual、prompt dependency、SEO 闭环、结构化 guardrail、人工负责制和开源创意被大厂吸收；今天保留 MCP 生产运维细节和异构 agent 独立探索/综合这两个相对有新增实践信息的讨论。

## Hacker News 热榜

- **Meta 确认至少 20,225 个 Instagram 账号因 AI chatbot 相关重置流程被接管，HN #3、219 分、75 评论。** 评论区抓住 Meta “工具按预期工作、但另一代码路径未校验邮箱”的措辞，认为这正暴露了把 AI 工具接入账号恢复流程时的责任边界；对 agent 产品，密码重置、身份校验和客服自动化必须有独立权限校验与审计日志。 [HN](https://news.ycombinator.com/item?id=48427643) / [报道](https://this.weekinsecurity.com/meta-confirms-thousands-of-instagram-accounts-were-hacked-by-abusing-its-ai-chatbot/)

- **“Benchmarks in Leipzig” 论文上 HN #10、119 分、43 评论；讨论重点是数学 benchmark 正接近“公开文献出题”上限。** 论文作者说明题目难度接近二年级博士、非普通考试题；评论区提醒这些题有公开文献可推断答案，不等于模型解决前沿问题，并拿 GPT-5.5 1043/1389 正确、Opus 294/1306 正确的差异强调“回答率”和“可靠率”要分开看。 [HN](https://news.ycombinator.com/item?id=48425247) / [论文](https://arxiv.org/abs/2606.05818)

- **Universal Memory Protocol 登上 HN #5、32 分、13 评论；agent memory 标准化遇到强烈怀疑。** 评论区认为 coding agents 已能通过文件系统和项目指令发现记忆，真正可能需要的是文件布局标准而非复杂协议；另有人指出仓库初始提交一次性 5,500 行、疑似 LLM 生成，提醒 memory 协议如果缺少真实采用、迁移和冲突处理，很容易变成“万能标准”噪声。 [HN](https://news.ycombinator.com/item?id=48428796) / [项目](https://universalmemoryprotocol.io/)

- **Nvidia Windows PC CPU/SoC 讨论在 HN #6 有 198 分、369 评论；本地 AI 的焦点落到统一内存、CUDA 和实际算力边界。** 支持者认为统一内存能降低小型机/便携设备的内存池管理成本，也利于本地模型；反对者提醒 shared bandwidth/TDP 会压低 GPU 表现，真正优势可能只是 CUDA，而安全上还要面对 CPU/GPU 共享内存的侧信道风险。 [HN](https://news.ycombinator.com/item?id=48424605) / [来源](https://twitter.com/lemire/status/2062880075117113739)

- **Computex “Agentic PC” 文章上 HN #8，但只有 13 分、7 评论；社区态度明显偏冷。** 有人接受“本地模型驱动的 PC”不算离谱，但担心所谓 agentic PC 最终变成订阅入口；另一类反馈则把它和 Copilot 键相提并论，认为消费者并没有明确需求，这对硬件厂商是需求验证风险而非单纯营销命名问题。 [HN](https://news.ycombinator.com/item?id=48428647) / [EE Times](https://www.eetimes.com/computex-2026-are-we-heading-for-the-agentic-pc-era-yet/)

- **Show HN 的 Poincaré disk 无限画布笔记拿到 HN #9、92 分、13 评论；作者明确说 LLM 帮他处理了非欧几何坐标和优化算法。** 评论区反馈集中在交互可用性：有人觉得像在球面上导航、需要网格或明暗层次帮助定位，也有人认为平板+触控笔会比 Web 更合适；这条对 AI coding 读者的增量是，LLM 正在降低小众数学/HCI 原型的实现门槛，但产品化仍要靠可导航性和设备形态验证。 [HN](https://news.ycombinator.com/item?id=48372138) / [Demo](https://uonr.github.io/poincake/)

**今日取舍：** 已读取 `input.md`、`context.json`、10 条 HN raw 文件以及 2026-06-06 / 2026-06-05 历史报告，仅把历史用于去重，未使用 `selected_items.json` 驱动判断。近两日已覆盖 Gemma 4 QAT、pg_durable、Agent TDD skill、Transformers succinctness、Hacker News Sans AI、Mouseless、Anthropic 漏洞 harness、自我改进叙事、Retro-Tech Parenting 和 FFmpeg WebCLI；今天保留 Meta AI chatbot 账号接管、数学 benchmark、agent memory 协议、本地 AI PC 架构、agentic PC 需求争议和 LLM 辅助 HCI 原型，因为它们有新事实或评论区能落到 agent/coding-agent 工作流。剔除 Zeroserve、Ntsc-rs、远程办公心理健康和 fugitive 长文，原因是与 AI/coding-agent 关联弱，或虽可牵强联想到 LLM/AI，但评论 substance 更集中在通用 Web server、复古视频、远程管理和非技术叙事。

## Hacker News 搜索观察

- **“I nerfed our coding agents on purpose”把 coding-agent 成本治理从“少用模型”推进到自动路由：按请求复杂度选择最低可用模型和 reasoning depth，并叠加 token 优化来换取同等预算下约 3x 使用量。** 作者说团队从 Claude Code 转向 Codex 后感到按 token 计费更早、更明显，问题不是不该用强模型，而是把所有内部 coding 任务都打到最高智能/最高推理档会浪费；评论区一边质疑新账号刷量，一边也有人认可“spend optimization + model routing + throughput gains”的角度，还有用户提到自己在同一个 VS 实例里拆给 Codex 与 Claude 以绕开用量瓶颈。对团队落地，信号是 agent 成本优化正在变成一层运行时策略：分类器、预算上限、模型/推理档路由、缓存/压缩和质量回归要一起设计，而不是事后看账单。来源：[HN](https://news.ycombinator.com/item?id=48419614) / [Nerfguard](https://nerfguard.com)

- **Zedra 把 Claude/Codex 等 coding agents 的控制面搬到手机端，但评论指出真正难点不是远程打开终端，而是任务状态和交接可见性。** 原帖描述 Zedra 是一个移动代码编辑器，直连桌面，可在手机上使用 remote terminal、代码编辑器、Markdown、文件浏览器和 git view；连接采用 peer-to-peer、outbound-only networking、QUIC/UDP，不需要端口转发，移动端用 Rust + GPUI，CLI 支持 Mac/Linux/Windows。唯一评论抓住了 agent 工作流的关键：peer-to-peer 很有趣，但更难的是让用户清楚 agent 是否仍在运行、是否被阻塞、是否改了文件且需要 review，避免下一次 handoff 失真。对移动 agent 控制台，这意味着状态 chip、diff/日志/阻塞原因、通知和人工确认比“能在手机上跑命令”更核心。来源：[HN](https://news.ycombinator.com/item?id=48420833) / [GitHub](https://github.com/tanlethanh/zedra)

- **Ask HN “AI dev tech stack / workflow” 继续从工具清单扩展成流程讨论，新增高价值评论把路线分成写代码、和 agent 一起写、多 agent、再到 orchestrator/factory。** 昨日报告已写过 Spec Driven Development 和 slow code/TDD 两条主线；今日 raw 中该帖已到 144 分、126 评论，新增评论强调全自动化阶段更像工业工程：看整体 flow、用 checklist/gates 持续改进、尽量把流程机制化为代码而不是交给 agent、用 CI/CD、覆盖率、e2e、mock、linters 和 repo 内文档维持吞吐；同时也提醒 agent 并发过多会带来代码冲突，需要通过架构来最大化可并行性。相比昨天的“如何教入门工作流”，今天的增量是把多 agent 规模化使用看作产线设计问题。来源：[HN](https://news.ycombinator.com/item?id=48413629)

**今日取舍：** 已读取 `input.md`、`context.json`、14 个 HN search raw 文件，以及 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日报告已实质覆盖 Cost.dev、Hydron、Hyper、Aura、Lich、Ask HN 的 SDD/slow-code 主线、skill regression tests、Lazarus、G-Spot，并明确去重 Clor、Ouijit 等，因此今天不重复旧事实。保留 Nerfguard/agent nerfing、Zedra 和 Ask HN 后续评论：它们分别补充 agent 成本/模型路由、移动端远程控制与 handoff 状态、以及多 agent 工业化流程的新角度。剔除 Piece（消费者关系 app，与 agent 工程弱相关）、Ontology wild idea（0 评论且过于概念化，缺少可操作工程证据）、Clor/Ouijit/Cost.dev/Hydron/Hyper/Aura/Lich/skill tests/Lazarus（近日报告已覆盖或本次无实质新增），以及低互动且证据不足以支撑新结论的重复项目。

## Claude Code

- **Claude Code `v2.1.166` 新增 `fallbackModel` 设置，最多可配置 3 个备用模型，并让 `--fallback-model` 覆盖交互会话。** 主模型过载或不可用时会按顺序回退；遇到 API 返回意外的非重试错误时，也会在 fallback model 上重试一次，但鉴权、限流、请求过大和传输错误仍会立即暴露。 [v2.1.166](https://github.com/anthropics/claude-code/releases/tag/v2.1.166)

- **权限与跨会话消息继续收紧：deny rule 的工具名位置支持 glob，`"*"` 可拒绝所有工具；跨 Claude session 经 `SendMessage` 转发的消息不再携带用户授权。** 接收端会拒绝转发来的 permission request，auto mode 也会阻止它们；同时 allow rules 会拒绝非 MCP glob，deny rules 中未知工具名会在启动时 warning。 [v2.1.166](https://github.com/anthropics/claude-code/releases/tag/v2.1.166)

- **默认会 thinking 的 Claude API 模型现在可被显式关掉 thinking。** `MAX_THINKING_TOKENS=0`、`--thinking disabled` 和 per-model thinking toggle 都会生效；第三方 provider 行为不变。 [v2.1.166](https://github.com/anthropics/claude-code/releases/tag/v2.1.166)

- **`v2.1.166` 修了一批长会话和企业配置坑，重点是避免“卡住、误失效、后台进程失控”。** 包括远程 session 在 worker registration 短暂后端故障后永久卡住、macOS daemon 断开后孤儿 `claude --bg-pty-host` 100% CPU、自带无效项的 managed settings 让其余有效策略静默失效、`${VAR}` 形式的 allowed/denied MCP server predicate 不匹配，以及进入 git worktree 的后台 agent 从 `claude agents` 重开时因 “No conversation found” crash-loop。 [v2.1.166](https://github.com/anthropics/claude-code/releases/tag/v2.1.166)

- **终端与 UI 侧也有具体修复：JetBrains 2026.1+ 终端闪烁、Kitty keyboard protocol 下 Shift+非 ASCII 字符丢失、Windows PowerShell command validation 超时后仍挂很久。** 另修复 unprocessable image 导致反复 “image could not be processed” 和额外 token 消耗、Ctrl+O transcript thinking 文本重复、`claude agents` 多行输入光标卡在首行末尾、无 Unicode 终端中后台 agent 列表多空行等问题。 [v2.1.166](https://github.com/anthropics/claude-code/releases/tag/v2.1.166)

- **同日 `v2.1.167` 又发布，但 release note 只有 “Bug fixes and reliability improvements”。** 可把它视为 `v2.1.166` 后续稳定性补丁：升级策略上优先按上面 `v2.1.166` 的 fallback、权限、managed settings、远程 session、后台 agent 和终端输入路径做 smoke，再用 `v2.1.167` 作为最新补丁版本验证。 [v2.1.167](https://github.com/anthropics/claude-code/releases/tag/v2.1.167)

**今日取舍：** 已读取 `input.md`、`context.json`、4 个 raw 文件，以及 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。昨日已覆盖 `v2.1.165` 且该版说明只有稳定性占位，今天不重复；保留 `v2.1.166` 的 fallback model、权限/跨会话授权、thinking toggle、managed settings、远程/后台 agent 与终端/UI 修复，因为它们有明确工作流影响；`v2.1.167` 仅作为同日最新稳定性补丁简述，不展开资产列表。

## Codex

- **Codex `0.138.0-alpha.5` 与 `0.138.0-alpha.6` 继续推进预发布，但 release note 仍只有占位文本；今天更应把它们当作“承载同日 PR 的安装矩阵”而不是功能说明。** 两个 prerelease 均只写 “Release 0.138.0-alpha.N”，资产矩阵仍覆盖 macOS DMG / tar / zst、Linux musl、Windows x64/ARM64、npm、Python wheel、app-server、responses-api-proxy、Windows sandbox setup、`codex-zsh`、`config-schema.json` 与安装脚本。近两日报告已反复提示 `0.138.0-alpha.*` changelog 缺失，今天新增点只是 alpha.5/alpha.6 已发布；读者动作：升级 smoke 不要从版本号推断功能，按下列 PR 分别回归 auth、permissions、Responses Lite、remote-control、plugins、TUI 和构建链路。 [alpha.5](https://github.com/openai/codex/releases/tag/rust-v0.138.0-alpha.5) / [alpha.6](https://github.com/openai/codex/releases/tag/rust-v0.138.0-alpha.6)

- **Codex 开始支持 v2 personal access tokens，并把 PAT 明确暴露为 `personalAccessToken` app-server auth mode。** PR #25731 给 `codex login --with-access-token` 和 `CODEX_ACCESS_TOKEN` 增加 v2 PAT 支持，把 opaque `at-` token 与 legacy Agent Identity JWT 分开分类；启动时会通过 AuthAPI `/v1/user-auth-credential/whoami` hydrate 必需的 ChatGPT account metadata，并直接把 PAT 当 bearer token 使用。实现上不持久化 hydrate 后的 metadata，而是每次 startup 做 live preflight，使被撤销 token 或账号 metadata 变化不会靠 stale cache 继续通过；AuthAPI 缺少 email 等必需字段时 fail closed。注意它**不**把 `forced_chatgpt_workspace_id` 套到 PAT auth 上，且 v1/v2 app-server API 都报告 `personalAccessToken`，移除了临时把 PAT 映射成 `chatgpt` 的兼容做法。读者动作：使用 PAT 做 headless/CI、app-server 或环境变量登录的团队，应回归 token classification、whoami metadata、revocation、debug redaction、v1/v2 `AuthMode` 客户端兼容，以及 workspace restriction 预期。 [PR #25731](https://github.com/openai/codex/pull/25731)

- **企业权限侧新增闭合式 permission profile allowlist：`allowed_permission_profiles` 可以跨 managed requirements layers 合成、允许或撤销 profile。** PR #24852 把 allowlist 从数组式替换改成可 merge 的 map：effective value 为 `true` 的 profile 可选，缺失或 `false` 的 profile 均拒绝；内置 profile 和未来新增 profile 默认不被允许，除非管理员显式列出。它要求 narrowed/custom allowlist 的 `default_permissions` 必须指向允许的 profile；兼容场景下，如果同时显式允许 `:workspace` 和 `:read-only` 而省略 default，会解析为 `:workspace`，但官方仍建议客户显式设置。配置缺失时，既有 implicit permission 和 legacy `sandbox_mode` 行为不变。读者动作：企业部署应把 `:danger-full-access` 等不希望开放的内置 profile 从 allowlist 中明确省略，校验 custom profile 名称、默认权限、managed layer 覆盖/撤销，以及旧配置在未设置 allowlist 时是否保持原状。 [PR #24852](https://github.com/openai/codex/pull/24852)

- **Responses Lite 链路本轮补齐两件事：模型使用 standalone tool executors，并在 HTTP/WebSocket 传输上带模式 header。** PR #26490 指出 Responses Lite 不执行 hosted Responses tools，因此 web search 与 image generation 要走 Codex-owned executors 和 standalone Responses API endpoints；同时保持这些 executors 在未启用 flags 或 Responses Lite 时隐藏。PR #26542 继续在 HTTP Responses 请求和 WebSocket upgrade 请求上按 model metadata 发送 `X-OpenAI-Internal-Codex-Responses-Lite: true`，并用 client metadata 影响 WebSocket；因为 Responses-over-WebSocket 的模式是 connection-scoped，缓存 socket 若跨模式复用会拿错 transport contract，所以新增了 mode change 时重连的验证。读者动作：启用 Responses Lite 的用户应回归 web search/image generation、hosted tool gating、WebSocket reconnect、代理/header 透传和 app-server standalone endpoints；未启用场景要确认 standalone executors 不被意外暴露。 [PR #26490](https://github.com/openai/codex/pull/26490) / [PR #26542](https://github.com/openai/codex/pull/26542)

- **remote-control 修了一个会造成反复重新 enrollment 的 WebSocket 404 误判：只有明确的 missing-server JSON 才清 enrollment。** PR #26741 说明 WebSocket handshake 经过 intermediary 时可能拿到 generic HTTP 404；过去把所有 404 都当作 remote app server gone，会清掉有效 enrollment，造成重复 re-enrollment、新 environment/server IDs、Habitat churn 和噪声 `/server/enroll` 流量。新逻辑只在 404 JSON 明确包含 `{"detail":"Remote app server not found"}` 时清 enrollment；空 body、纯文本、malformed 或无法识别的 404 会保留 enrollment、返回 transport error，并沿用 reconnect backoff。同时日志会记录 status、`request-id` / `x-oai-request-id`、`cf-ray` 和 bounded/redacted response body。读者动作：依赖 remote-control 的团队应回归 generic 404、真实 missing-server、reconnect backoff、server/environment ID 稳定性，以及日志中 correlation headers 是否足够排查又不泄露内容。 [PR #26741](https://github.com/openai/codex/pull/26741)

- **插件链路同时修了“看不见产品专属插件”和“无效 skill warning 反复刷屏”两个体验问题。** PR #26804 发现 Codex remote plugin requests 未向 plugin-service 发送 `OAI-Product-Sku: codex`，导致 product-specific plugins 被过滤；现在在共享 authenticated request helper 中加 header，覆盖 `/ps/plugins/*` 的 list、installed state、detail、install、uninstall、skills 和 sharing 等端点。PR #26698 则为 skill load warning 做去重：同一个仍 active 的 `(path, message)` 只保留首条 warning，后续重复 suppressed；当错误清除后再出现，或 message 变化时会重新显示。读者动作：插件用户应回归 global/workspace plugin list、installed state、skills/sharing 端点是否能看到 Codex SKU 相关插件；技能开发者则应确认无效 `SKILL.md` 修复/再次出错时 warning 生命周期符合预期。 [PR #26804](https://github.com/openai/codex/pull/26804) / [PR #26698](https://github.com/openai/codex/pull/26698)

- **TUI 的 terminal visualization instructions 进入 under-development gate，默认用户行为不变；benchmark smoke 也从 `just test` 中拆出。** PR #26013 新增 `Feature::TerminalVisualizationInstructions`，默认 disabled，只在 TUI start、resume、fork flows 启用时把 terminal visualization instructions append 到 developer instructions，并明确不应用到 `codex exec`；共享 visualization-selection rule 仍通过 `codex_proxy_model_3` Statsig layer 提供，且 broad rollout 前还要 53-probe all-model treatment comparison 和 production coding evals。PR #26716 则把 `just bench-smoke` 从 Unix/Windows `test` recipes 中移除，并在 `AGENTS.md` 记录 `just bench` / `just bench-smoke` 为显式 benchmark 命令，避免每次项目测试都编译/运行 benchmark smoke。读者动作：TUI dogfooders 可按 feature gate 验证 start/resume/fork prompt stack 与终端可视化；工程贡献者应更新本地/CI 预期，区分常规 `just test` 与显式 benchmark validation。 [PR #26013](https://github.com/openai/codex/pull/26013) / [PR #26716](https://github.com/openai/codex/pull/26716)

- **构建依赖侧更新到 `rusty_v8 149.2.0`，但用户可见 release note 仍不足，主价值是跟踪 V8 静态库和平台资产。** PR #26464 只写 “build(v8): update rusty_v8 to 149.2.0”，无 PR summary；对应 `rusty-v8-v149.2.0` release 也没有 release notes，只提供多平台 `librusty_v8_*` / `rusty_v8_*` 静态库、ptrcomp sandbox 变体、sha256 和 binding assets。读者动作：如果你维护 Codex build、V8 binding 或依赖预构建 rusty-v8 artifact 的环境，需回归 macOS/Linux/Windows、GNU/musl、ptrcomp sandbox 与 checksum；普通 Codex CLI/TUI 用户不应从这条推断新功能。 [PR #26464](https://github.com/openai/codex/pull/26464) / [rusty-v8-v149.2.0](https://github.com/openai/codex/releases/tag/rusty-v8-v149.2.0)

**今日取舍：** 已读取 `input.md`、`context.json`、23 个 raw 文件以及 2026-06-06 / 2026-06-05 历史报告作去重参考，未使用 `selected_items.json` 驱动判断。近两日已覆盖 `0.137.0`、`0.138.0-alpha.1`–`alpha.4` 的占位 release/资产状态、reasoning effort 自定义化、code-mode namespace exclusion、AGENTS.md environment filesystem loading、release signing/ThinLTO/Winget、`response.processed` 删除、TUI 启动与 `resume --last` 性能、goal runtime extension 化、Windows sandbox/terminal color、absolute runtime roots、turn profiling、插件 JSON 输出、WSL curated discovery 和 prompt restore bugfix，因此今天避免重复旧事实；保留 alpha.5/alpha.6 版本状态、v2 PAT、permission profile allowlist、Responses Lite standalone/header、remote-control generic 404、plugin SKU、skill warning 去重、terminal visualization gate、benchmark smoke 拆分和 rusty-v8 149.2.0 这些有新增事实或明确回归价值的变化。

- 今日不新增入选项目：本 lane 从 GitHub Trending、HN、Reddit、X 等 raw corpus 派生筛选；今天最贴近 AI/coding-agent 工作流、但真正属于“新增项目信号”的 `RPate97/lich`、`ExpressGradient/lazarus`、`AIXP-Labs/AISOP`、`CarpseDeam/Aura-IDE`、`arjitj2/skillindex` 均经 GitHub metadata 校验低于 100 stars，不能入选；`Christian-Katzmann/app-it` 虽达 183 stars，但已在近日报告展开，今天 raw 没有新增事实。其他高星候选如 `EveryInc/compound-engineering-plugin`、`affaan-m/ECC`、`anthropics/claude-code`、`can1357/oh-my-pi`、`chopratejas/headroom`、`Leonxlnx/taste-skill`、`hardikpandya/stop-slop`、`supermemoryai/supermemory`、`NousResearch/hermes-agent` 等，多为近两日已写过/明确去重的趋势仓库，或只有一句仓库简介，缺少值得再次写入“AI 项目”栏的新增项目事实。

**今日取舍：** 已读取 `input.md`、`context.json`、raw corpus 索引/摘录与 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，未使用 `selected_items` 驱动判断。按本栏硬门槛用 GitHub API metadata 校验候选仓库 stars ≥100；低于 100 stars 或无法验证 stars 的仓库全部剔除。本次 raw corpus 状态为 ok，但星标门槛、AI/coding-agent 相关性和近日报告去重后输出为空，不视为采集失败。

## GitHub 趋势项目

- **anthropics/claude-code** 登上本周 GitHub Trending，仓库 130,628 stars；它是 Claude 的终端 coding agent，覆盖代码库理解、例行任务、解释复杂代码和 git 工作流，适合团队核对官方入口与安装路径。 [GitHub](https://github.com/anthropics/claude-code)

- **NousResearch/hermes-agent** 以 184,696 stars 出现在本周趋势；项目定位是“会随用户成长的 agent”，对本地/个人 agent 用户，关注点在 skills、记忆、自动化和多入口工作流如何沉淀成长期环境。 [GitHub](https://github.com/NousResearch/hermes-agent)

- **EveryInc/compound-engineering-plugin** 以 20,074 stars 上榜，明确支持 Claude Code、Codex、Cursor 等工具；它把 Compound Engineering 方法封装成插件，适合把团队工程规范、审查和协作习惯接入多个 coding agent。 [GitHub](https://github.com/EveryInc/compound-engineering-plugin)

- **chopratejas/headroom** 以 15,768 stars 上榜，主打在内容进入 LLM 前压缩工具输出、日志、文件和 RAG chunks，宣称减少 60–95% token；长任务 agent 可用它降低上下文成本，但要回归压缩后答案一致性。 [GitHub](https://github.com/chopratejas/headroom)

- **mukul975/Anthropic-Cybersecurity-Skills** 以 14,613 stars 上榜，提供 754 个映射到 MITRE ATT&CK、NIST CSF、ATLAS 等框架的安全 skills，并注明适配 Claude Code、Codex CLI、Cursor、Gemini CLI 等；安全团队可把它当作 agent skill 目录和审计基线。 [GitHub](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)

**今日取舍：** 已读取 `input.md`、`context.json`、20 个 GitHub trending raw 文件和 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。所有入选仓库均通过 GitHub API 校验 stars ≥100，并能落到 AI/coding-agent workflow；剔除近两日已明确重复的 oh-my-pi、taste-skill、stop-slop 等，以及通用 TTS、短视频、漏洞扫描、文档转换、网页抓取等与本栏 agent 工作流关联不够直接的项目。

## Rize AI 工具榜

- **今日不展开新条目：Rize 榜单仍有不少 agent/coding 相关项目，但今日 raw 只给出排名、仓库链接和一句简介，缺少足以覆盖近日报告去重线的新增事实。** 本次 20 条均来自 Rize AI Tools weekly ranking，抓取时间为 2026-06-06T22:03:55+0000；#1–#8 仍是 open-slide、CodeWhale、claude-seo、agents-cli、learn-harness-engineering、awesome-gpt-image-2-API-and-Prompts、terax-ai、agentmemory，近日报告已说明这组此前已逐条展开，随后连续因重复被整体去重。#9–#20 里 ClawRouter、superpowers-zh、OpenViking、Hermes WebUI / hermes-web-ui、9router、DeepSeek-Reasonix 等仍与 agent/coding 工作流相关，但今日证据没有排名变化、release、star 增量、仓库更新或真实使用反馈；因此不因 `selected_items.json` 中出现个别条目而重复写入正文。 [Rize AI Tools](https://rize.io/ai-tools)

**今日取舍：** 已读取 `input.md`、`context.json`、20 条 Rize raw，以及 2026-06-06 / 2026-06-05 历史报告；历史仅用于去重，`selected_items.json` 仅作 audit-only 参考，未作为主要判断。保留原则是“AI 工具排名 + 对 workflow 有具体新增事实”；今天 raw corpus 状态正常，但所有候选都只有榜单快照级信息，故本栏输出空结果，以避免把 2026-06-03 已展开、2026-06-04 至 2026-06-06 已连续判定重复的 weekly ranking 原样再写一遍。

- **Manus Shopify Connector** 把 Shopify 建站和运营动作放进一个 chat 入口：raw 只给出 “Build and manage Shopify stores from one chat”，但方向很明确——它不是通用聊天客服，而是把电商后台的创建、配置和管理流程包成 agent/对话式执行面。对 AI-agent 读者，值得跟踪的是它能否可靠处理店铺配置、商品/主题/插件变更、权限边界、变更预览与回滚；如果这些控制面做得足够清楚，垂直 SaaS 的“从一个 chat 管后台”会比泛用浏览器 agent 更容易落地。 [Product Hunt](https://www.producthunt.com/products/manus-shopify-connector?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **Fox Issue Tracker 4** 是一个 “Track, plan, and release” 的开发者 issue / release 管理工具。它没有在 raw 中直接宣称 AI 能力，因此不能把它写成 coding agent 产品；保留它的理由是它落在开发计划、缺陷跟踪和发布节奏这条 coding-agent 交付链路上：随着 agent 生成的 PR、任务分解和 release note 增多，issue tracker 的价值会更多取决于能否承接 agent 产出的计划、验收状态和发布证据。后续需要核对它是否提供 API、自动化、AI 摘要或与 GitHub / Linear / CI 的集成，否则它更像常规项目管理更新。 [Product Hunt](https://www.producthunt.com/products/fox-issue-tracker-4?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** raw corpus 状态为 ok，但只有 2 个 Product Hunt topic hit；已读取 `input.md`、`context.json`、2 个 raw 文件和 2026-06-06 / 2026-06-05 历史报告，仅用历史作去重参考，未使用 `selected_items.json` 驱动判断。近两日 Product Hunt 栏已覆盖 AppWizzy、Keen Code、Intelligent Terminal、Recursi、Agent Browser Shield、Minimi 等 coding-agent 环境、CLI、终端、安全与记忆产品，今天避免复述这些旧角度。保留 Manus Shopify Connector，因为它直接体现垂直业务后台的 chat/agent 执行入口；保留 Fox Issue Tracker 4 时明确降权处理，因为它与开发交付流程相关但 raw 未提供 AI/coding-agent 机制。由于本次候选总数只有 2 个，无法在不补造来源的情况下达到 3 个入选。

## Polymarket AI 市场

- **6 月最佳 Coding AI 模型盘口仍把 Anthropic 放在压倒性领先：Anthropic 91.0%，OpenAI 5.0%、Z.ai 1.6%；24h 成交量约 1,025.5，30d 约 6,946.7，流动性约 46,447.1。** 相比昨日报告的 Anthropic 91.5% 小幅回落但格局未变；这只是交易者预期，实际 coding-agent 选型仍要看自家仓库里的工具调用、延迟、成本、失败恢复和代码质量。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-june)

- **Coding Arena 门槛盘口给出短期与年末两个能力预期：6 月底前达到 1550 的概率为 62.5%，12 月底前达到 1560 的概率为 77.5%；1550 盘 30d 成交量约 1,132.7，1560 盘约 3,243.8。** 1550 盘较近日报告的约 65.5% 继续降温；raw 的 outcome 名称重复，只能读作门槛预期，不能细分到具体模型。 [6 月底 1550](https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-june-30) / [12 月底 1560](https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-december-31)

- **6 月最佳 AI 模型总榜仍由 Anthropic 领先：Anthropic 84.0%，Google 11.5%、OpenAI 3.6%；24h 成交量约 189,815.7，30d 约 5,829,367.4，流动性约 3,796,694.2。** 相比昨日报告的 Anthropic 83.2% 小幅上行；它可作为外部情绪温度计，但不能直接推出某个模型在长上下文、工具权限、成本或特定仓库任务上最优。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **6 月最佳 Math AI 模型盘口继续给 Google 领先：Google 64.5%，Anthropic 18.5%、OpenAI 18.0%；24h 成交量约 46,596.9，30d 约 103,522.7，流动性约 110,115.4。** Google 概率较昨日报告的约 64.0% 基本持平，但 Anthropic 份额明显低于昨日 raw；对复杂推理、形式化验证和 benchmark-heavy agent 任务，这仍只是市场预期背景，不是实测成绩。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-june)

- **FrontierMath 相关盘口整体仍偏谨慎：Claude ≥50% 的 Yes 为 38.0%，任一 OpenAI GPT ≥60% 为 30.0%，任一 AI 模型 2026 年前 ≥90% 的 Yes 为 23.0%。** 相比昨日报告的 Claude 约 39.0%、90% 市场约 24.0%，变化不大；这些都是 Polymarket 市场预期，不是模型已经达到相应 FrontierMath 水平的事实。 [Claude 市场](https://polymarket.com/event/anthropic-claude-score-on-frontiermath-benchmark-by-june-30) / [OpenAI GPT 市场](https://polymarket.com/event/openai-gpt-score-on-frontiermath-benchmark-by-june-30) / [90% 市场](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027)

**今日取舍：** raw corpus 状态为 ok，共 12 条 Polymarket 证据；已读取 `input.md`、`context.json`、全部 raw 文件和 2026-06-06 / 2026-06-05 报告作为去重参考，未使用 `selected_items.json` 驱动判断。保留与 AI/coding-agent 直接相关且有当日概率、成交量或近日报告可比变化的 Coding AI 主盘口、Coding Arena 门槛、6 月模型总榜、数学模型和 FrontierMath 组合；剔除第三名/第二名盘口、估值盘、Style Control 版总榜，以及与主盘口重叠但对 coding-agent 读者增量较弱的条目。所有概率均为 Polymarket 市场预期，不是已确认事实。
