# AI Agent 日报（2026-06-23）

## 天气

- **北京·海淀：小毛毛雨，19.8°C–30.8°C。** 降水概率 73%、预计 1.2 mm，北风最高 17.8 km/h；较昨日最高温下降约 2.1°C、低温上升约 1.4°C，炎热感略缓但降雨概率明显升高，通勤建议带伞，午后仍注意补水与防闷热。 [天气](https://api.open-meteo.com/v1/forecast?latitude=39.9593&longitude=116.2981&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-23&end_date=2026-06-23)
- **上海·杨浦：雷暴伴轻微冰雹，21.6°C–23.8°C。** 降水概率 100%、预计 29.8 mm，北风最高 12.2 km/h；较昨日最高温再降约 2.4°C、雨量从 12.5 mm 升至 29.8 mm，强对流和积水风险更突出，出门务必带伞、防滑，并尽量避开雷暴/冰雹时段户外停留。 [天气](https://api.open-meteo.com/v1/forecast?latitude=31.2598&longitude=121.5257&daily=weather_code%2Ctemperature_2m_min%2Ctemperature_2m_max%2Cprecipitation_probability_max%2Cprecipitation_sum%2Cwind_speed_10m_max%2Cwind_direction_10m_dominant&timezone=Asia%2FShanghai&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm&start_date=2026-06-23&end_date=2026-06-23)

**今日取舍：** 天气为每日固定实用信息，不因近两日报告已有同类栏目而去重；保留北京·海淀和上海·杨浦两地 2026-06-23 当日预报，并仅用近两日报告辅助判断体感变化。

## X 推荐

1. **Grok Build 新增 `/goal`：把长任务交给多轮 subagents 自主执行。** 官方帖称它会用多轮子代理实现、测试并迭代目标，这和近两天“loop engineering”主线相比更像产品化入口；试用时要重点看停止条件、预算上限、子任务日志、失败回滚和人类审批点，而不是只看“能跑很久”。  
   https://x.com/grok/status/2069095154691272933

2. **Cursor 在 Compile keynote 后预告三项发布，其中包括与 SpaceX 训练新模型。** raw 只给出 keynote 摘要级信号，不能写成模型能力已验证；但 Cursor 把 coding IDE、专用模型训练和真实工程组织绑定在一起，说明 agent IDE 竞争正在从 UI/补全转向“面向高强度代码库的模型—产品联合优化”。  
   https://x.com/cursor_ai/status/2069149296436330776

3. **OpenAI Devs 展示 Codex 作为 iOS/macOS 开发者的 research partner，用来探索新框架并更快迁移。** 这条不是版本发布，但信号具体：Codex 被包装为“研究搭档”而非单纯代码生成器；对 Apple 平台开发，值得把框架调研、示例工程、API 迁移、编译验证和文档引用做成可审计流程。  
   https://x.com/OpenAIDevs/status/2069153778553737605

4. **OpenAI / Codex 安全方向同步升温：Codex security 更新与 GPT-5.5-Cyber 被同日推到 X。** thsottiaux 写到 “Updates to codex security and a new GPT-5.5-Cyber”，sama 则强调与美国政府和安全生态合作、帮助企业安全；这更适合当作安全产品线信号，落地前应核对模型可用范围、双用途拒答、审计日志、漏洞验证沙箱和企业数据边界。  
   https://x.com/thsottiaux/status/2069152290326630518  
   https://x.com/sama/status/2069121360744550796

5. **`loop-library` 把“循环工程”从口号做成模板库：覆盖工程、运维、评估、设计、内容等 50 个场景，并配套查找、审计、适配、设计四类 skill。** 近两日报告已覆盖 loop engineering 概念，今天的增量是更具体的模板化资产；团队可把它当成 loop 设计清单，但仍要逐项补上观测指标、退出条件、权限和回归集。  
   https://x.com/aigclink/status/2068993817316135064

6. **Claude Code 项目规模变大后，`.claude/` 目录组织开始被专门讨论：CLAUDE.md、rules、hooks、commands、skills 分层。** 这不是官方规范，但很实用：agent 配置一旦散落，后续 review、迁移和权限审计都会困难；建议把 rules/skills/hooks 的职责边界、命名约定、适用范围和禁用方式写清。  
   https://x.com/vincemask/status/2069076711397032263

7. **Codex 被转述可在本地与远程主机之间交接线程：笔记本上开始工作，合盖前发送到远程主机继续跑。** raw 截断、需要核对原始说明，但方向直接命中长任务痛点；如果采用，应验证远端环境一致性、凭证迁移、未提交 diff、网络权限、日志回传和人类如何重新接管。  
   https://x.com/servasyy_ai/status/2068473678787182993

8. **`reverse-skill` 把逆向工程任务做成可喂给 AI 的 skill 路由，被中文社区标注为“比较危险”。** 原帖称通过 `routing.md` 告诉 AI 不同安全任务走哪条路；这类能力对安全研究有用，但双用途风险很高，使用前必须限定靶场/授权目标、禁用真实攻击链、保留操作日志，并把模型拒答和人工审批接入流程。  
   https://x.com/seventhoce56019/status/2068901168940745088

9. **Sakana AI 发布 Sakana Fugu，定位为“指挥多代理的一个模型”。** 官方帖明确写到“マルチエージェントを指揮する、一つのモデル”；这比普通榜单转述更有产品含义：模型层开始直接面向 multi-agent orchestration。评估时应看它如何分解任务、协调子代理、处理冲突、复用记忆，以及是否能在真实代码库或研究流里稳定胜过通用模型。  
   https://x.com/SakanaAILabs/status/2068973497905545461

10. **PixelRAG 被转述为“跳过 HTML 解析，直接截图网页再让视觉模型读答案”。** 这与 agent 抓网页/抗动态站点相关：当 DOM、反爬和前端渲染让传统 scraping 不稳定时，截图+视觉模型是一条实用备选；代价是成本、可追溯性和准确率，落地要保留截图证据、坐标引用、重试策略和隐私过滤。  
   https://x.com/RoundtableSpace/status/2068639188396744937

## X 关注

- **Google 宣布 Interactions API 已 GA，并称它是 Gemini models 与 agents 的主要接口。** raw 只截到“Built bas…”，不能展开具体参数或迁移细节；但官方账号把它定位为 agent 入口，说明 Gemini 侧接口正在从单次模型调用走向更面向交互/agent 的统一层。团队若接入，应优先核对旧 API 兼容、工具调用语义、会话状态、权限审计、速率限制和日志可观测性。https://x.com/Google/status/2069108942102310957

- **OpenAI Daybreak 从漏洞发现扩展到“机器速度修补”，Codex Security plugin 被单独点名。** OpenAI 官方称将扩大 Daybreak，gdb 补充说新工具和模型会加速 patching；另一条 gdb 帖把 Codex Security plugin 描述为面向安全团队的深度扫描、验证发现、追踪攻击路径、构建威胁模型等能力。由于 raw 都被截断，今天只把它当作方向性产品信号：安全 agent 正从发现漏洞进入修复、验证和威胁建模闭环，落地时要看补丁 diff、回归测试、误报处理、权限边界和人工审批。https://x.com/OpenAI/status/2069104283824640023 / https://x.com/gdb/status/2069112120206332130 / https://x.com/gdb/status/2069128701850386834

- **Hermes Agent 通过 trycua 把 computer use 扩到 Windows 与 Linux，补齐原有 macOS 之外的平台覆盖。** 这比同日 200,000 GitHub stars 里程碑更有工作流增量：桌面/浏览器/系统级自动化不再只围绕 macOS 设计。采用前应分别验证 Windows/Linux 的截图、点击、键盘、权限提示、沙箱/远程桌面环境、失败恢复和跨平台任务脚本差异，避免把 macOS 上可行的 UI agent 流程直接迁移。https://x.com/NousResearch/status/2069118782132363662

- **Xcode 27 被开发者发现内置可导出、可检查的 coding skills。** v_pradeilles 称可用一个简单 Terminal 命令导出并查看这些 skills；这说明 Apple 开发工具链也在把“如何使用工具/框架”的知识显式打包给 coding agent。对 iOS/macOS 团队，实用点是把官方 skills 当作可审计提示/流程资产：检查版本绑定、是否能纳入仓库、能否被 Claude/Codex 类工具复用，以及与团队自定义规范冲突时谁优先。https://x.com/v_pradeilles/status/2069104383141556383

- **OpenAI Developers 用 iOS/macOS 开发者案例继续把 Codex 定位成“研究伙伴”，用于探索新框架并加速迁移。** 这不是新功能发布，但和 Xcode 27 skills、Codex Security 同日出现，说明 Codex 的叙事正在分化为框架探索、代码迁移、安全验证等具体开发者场景。真正落地时，应要求 agent 留下探索记录、API 取舍理由、可运行样例和失败路径，而不是只交最终 diff。https://x.com/OpenAIDevs/status/2069153778553737605

- **中文开发者开始实测长时间自循环 `/loop`：目标是用 3 小时逐一检查应用每个功能，并根据代码创建用户故事和规范文档。** MinLiBuilds 预判会消耗大量 token，且 LLM 可能“开始作弊”；这条比泛泛“loop engineering”更具体，给出了测试目标和风险。适合把它当作长跑 agent 验收样例：必须有预算上限、阶段性产物、用户故事与真实代码的交叉校验、停止条件、作弊/自我简化检测和人工抽查。https://x.com/MinLiBuilds/status/2069080210419630325

- **一个“让 agent 把 Postgres 做成多线程”的极端长任务被转发：10 天后产生 1k commits、124k lines、786 个文件变更。** raw 是转发且缺少项目细节，不能写成成功案例；它的价值在于提醒读者，大型 coding-agent 任务很容易变成难以审查的巨型变更。对基础设施/数据库这类高风险代码，应强制拆分里程碑、限制单次改动面、保留可复现实验、要求 benchmark 与回滚路径，并避免用“跑了很久/改了很多”替代正确性证据。https://x.com/steipete/status/2069163022766227640

- **“可拓展的 agent workspace / managed agents”赛道开始被中文开发者直接拿来讨论商业归属。** turingou 问最终会是哪家 managed agents 胜出，还是因为 vibe/workflow 自定义化，利润更多流向基础计算提供商；这不是产品新闻，但点中了当前 agent workspace 的选型风险：买托管平台、省运维和审批体验，还是保留自定义 orchestration、上下文/记忆和工具权限。团队评估时应把锁定成本、workspace 数据可迁移性、子 agent 隔离、算力账单和自建替代方案一起比较。https://x.com/turingou/status/2069159765683413259

**今日取舍：** 已读取 `input.md`、`context.json`、100 条 x-following raw，以及 2026-06-22 / 2026-06-21 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近两日已覆盖 Hermes Blank Slate、Codex+Excalidraw、agent 软件工程方法、自优化/loop engineering、serve-sim、screenshot-to-code、OpenCLI App、Agentic Engineering Workflow、Codex 全功能测试、Spec Kit、prompt examples、personal/company brain、游戏多 agent 仿真和 animejs 给 coding agent 使用等，因此今天优先保留 Google Interactions API GA、OpenAI Daybreak/Codex Security、Hermes computer use 跨 Windows/Linux、Xcode 27 coding skills、Codex 作为 Apple 开发研究伙伴、具体 `/loop 3h` 自循环测试、Postgres 多线程极端 agent 任务，以及 managed agent workspace 赛道判断。剔除纯 RT/纯 t.co、生活娱乐/政治金融/体育、GLM/Mythos/AI loops 等近两日已覆盖或证据不足的泛模型话题、课程/营销、里程碑但工作流增量弱的 stars/活动帖，以及与 AI/coding-agent 工作流关联弱于入选项的内容。

## Reddit 社区

今日暂无可新增的 Reddit 社区更新。本次包内可读到 8 个 r/ClaudeAI 线程，但全部为 0 score / 0 comments；Skill Index、/app-it、Lore、多 agent 协作、自主交易、Claude Fable 5、voxel GTA 等只有发帖正文，没有社区回复可支撑“讨论实质”。其中自主交易 Update 1 虽补充了 Charter、Decision Journal、Playbook、止损/仓位/熔断等护栏，但已作为 6 月 22 日包内同一信号处理过，今天无新增评论或事实，不重复刊登。

**今日取舍：** 已读取 `input.md`、`context.json`、8 个 reddit raw 文件，以及 2026-06-22 / 2026-06-21 历史报告；历史仅用于去重，未使用 `selected_items.json` 作为主要判断。任务上下文提示 Reddit 采集曾遇到 HTTP 429 partial/failed，但当前包内 raw 可读；因可用证据没有未覆盖的社区讨论，本栏输出空结果。

## Hacker News 热榜

- **Show HN: Oak 把“面向 agent 的版本控制”推上 HN #10，118 分、117 评论；作者称 virtual mounts 可让本地/云端 agent 不必完整下载 repo，并支持多任务并行。** 评论区主要质疑“for agents”是否成立：模型已熟悉 Git，新 VCS 反而要额外文档和上下文；也有人分享用 gitnow 给 agent 独立 workspace/scratch space 的替代做法。 [HN](https://news.ycombinator.com/item?id=48631726) / [Oak](https://oak.space/oak/oak)

- **Moebius 以 0.2B inpainting model 声称达到 10B 级表现，登上 HN #9，191 分、58 评论；讨论重点落在小模型实用边界。** 实测评论认可 0.2B 体量下表现不错，但指出自然图像补洞区域更平滑、novel objects 表现差、输出限制在 512×512；另有从广告尺寸扩展项目来的经验提醒，不同托管后端的输入尺寸/预处理要求会让生产流水线很脆弱。 [HN](https://news.ycombinator.com/item?id=48630171) / [Moebius](https://hustvl.github.io/Moebius/)

**今日取舍：** 已加载/遵循 `daily-report-lane-hacker-news`，读取 `input.md`、`context.json`、9 条 HN topstories raw，以及 2026-06-22 / 2026-06-21 历史报告；历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日 HN 已覆盖 Claude 身份验证、Apertus 主权 AI、agent 会话记忆、AI-native 组织、推理成本、Bun/JSC 大 PR 的 AI 代码审计和 AI 套壳抄袭；今天保留 Oak 的 agent 版本控制争议与 Moebius 小型 inpainting 模型实测讨论。剔除 Steam Machine、Optocam Zero、British Columbia/Postgres 时区、Japanese symbols、LG Smart TV proxy SDK、smart glasses 和数学回忆文，主要因与 AI/coding-agent 工作流关联弱，或评论证据不足以支撑本栏展开。

## Hacker News 搜索观察

今日暂无可新增的 Hacker News 搜索观察更新。本次 raw corpus 正常，共 15 条 HN search story hit；其中最有讨论 substance 的 Pulse（39 分、14 评论）和最直接关联长跑 agent 会话接管的 Trustmux，已在 2026-06-22 报告实质刊登，今天不重复。其余条目要么已在近两日报告覆盖（Dapr/Diagrid workflow history signing、CWC、Konxios、Velane、Pagecast、Agentbrowse、语音控制 Pi Coding Agent 等），要么只有标题/自述级证据且 0–1 条评论，暂不足以支撑新的读者向更新。

**今日取舍：** 已读取 `input.md`、`context.json`、15 个 HN search raw 文件，以及 2026-06-22 / 2026-06-21 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 作为主要判断。按近两日去重规则，剔除昨天已刊登的 Trustmux 与 Pulse；同时剔除重复项、标题级弱证据、书签/设计/教育/营销项目、低评论低信息量 Web IDE/agent shell 项目，以及与 AI/coding-agent 工作流新增价值弱于入选线的内容。

## Claude Code

- **Claude Code `v2.1.186` 新增 `claude mcp login <name>` / `logout <name>`，可不进交互式 `/mcp` 菜单完成 MCP 鉴权，并支持 `--no-browser` stdin 重定向用于 SSH。** 对远端、CI 或无浏览器环境的 agent 工作流，这是更可脚本化的 MCP 登录路径；同版还让 `claude mcp get/remove` 对拼错的 server 名给出近似建议。 [v2.1.186](https://github.com/anthropics/claude-code/releases/tag/v2.1.186)

- **`v2.1.186` 改了多个交互工作流：`/workflows` agent 详情页按 `f` 可按状态过滤，`/plugin` Installed tab 新增 “Skills” 区，`/login` 在配置 `awsAuthRefresh` 后增加 “Claude Platform on AWS - refresh credentials”。** 这些变化主要影响多 workflow / plugin / AWS Platform 用户的日常排障与凭证刷新路径。 [CHANGELOG](https://github.com/anthropics/claude-code/blob/HEAD/CHANGELOG.md)

- **`!` bash 命令现在会让 Claude 自动回应命令输出；若想保持旧的“只把输出放进上下文”行为，需要在 `settings.json` 里设 `"respondToBashCommands": false`。** 升级后要回归脚本化/半自动会话，避免原本只用于收集上下文的 shell 输出触发额外模型回复。 [v2.1.186](https://github.com/anthropics/claude-code/releases/tag/v2.1.186)

- **`v2.1.186` 修复了多项长会话和 subagent 可靠性问题：睡眠唤醒后 streaming 的 “Content block not found”/JSON parse 错误、命名 subagent 绕过 `Agent(type)` deny/allowed-types 限制、schema subagent 反复校验失败无限循环等。** 还把后台 subagent 权限提示改为浮到主会话、显示哪个 agent 在请求，Esc 只拒绝该工具。 [v2.1.186](https://github.com/anthropics/claude-code/releases/tag/v2.1.186)

**今日取舍：** 已读取 `input.md`、`context.json`、4 个 raw 文件（CHANGELOG、`v2.1.183`、`v2.1.185`、`v2.1.186`）以及 2026-06-22 / 2026-06-21 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日报告已覆盖 `v2.1.183` 和 `v2.1.185`，今天只保留新增的 `v2.1.186` 与同内容 CHANGELOG 更新；CHANGELOG 与 release 重复处合并为同一组读者条目。

## Codex

- **Codex `0.142.0-alpha.11` 与 `0.142.0-alpha.12` 继续滚动，最新预发布推进到 `alpha.12`；release notes 仍只有 “Release 0.142.0-alpha.x”。** 资产仍覆盖 CLI、app-server、responses proxy、npm / Python 包、Windows sandbox setup、sigstore、symbols、安装脚本和 config schema，因此更适合作为快速预发布/分发回归信号，而不是可解读的功能发布；`alpha.9` 已在昨日报告覆盖，今天只作为版本列车连续性参考。 [alpha.11](https://github.com/openai/codex/releases/tag/rust-v0.142.0-alpha.11) / [alpha.12](https://github.com/openai/codex/releases/tag/rust-v0.142.0-alpha.12)

- **Codex 开始铺设“尊重系统代理”的共享 auth 路由边界，并在同一批变更里补上 Windows 解析器。** #26707 新增 `codex-client/src/outbound_proxy.rs`、`OutboundProxyConfig` / route class / failure class 和 route-aware reqwest client builder，把 browser/device/access-token login、token refresh、cloud-config、plugin auth、app-server account login、TUI/app startup 等 auth/startup HTTP client 接到统一策略；默认行为不变，只有 `respect_system_proxy = true` 时走系统/PAC/WPAD → env proxy → direct 的路径。#26708 则在 Windows 上读取 WinHTTP/IE 配置，支持显式 PAC、WPAD、静态代理和 bypass 规则，并用 URL-specific SHA-256 cache key 避免保留原始 URL。 [PR #26707](https://github.com/openai/codex/pull/26707) / [PR #26708](https://github.com/openai/codex/pull/26708)

- **managed MITM 场景开始更认真处理启动时自定义 CA：Codex 的网络代理会把平台根和启动时 CA override 一起纳入上游 TLS 信任，但不把自身 MITM CA 当成上游根。** #29014 针对 `SSL_CERT_FILE=/path/to/corp-ca.pem codex` 这类企业环境：加载 platform-native roots 时避开继承的 CA override，追加启动时 curated CA file / `SSL_CERT_DIR`，共享给 MITM upstream rustls connector；同时只把证书材料复制到 child-facing bundle，跳过私钥/无关文本，并避免嵌套启动重复追加当前 Codex-managed bundle。变更范围明确限于 `codex-network-proxy` 与依赖元数据，不改 `codex-core` 或 sandbox orchestration。 [PR #29014](https://github.com/openai/codex/pull/29014) / [commit 527ccb4](https://github.com/openai/codex/commit/527ccb4a5df8a75d6aeb4c6ae4341f99a1205a1e)

- **账号与权限表面各有一组客户端可见修正：服务账号 PAT 不再要求 ChatGPT account 必有 email，permission profiles 也会显式标出是否可选。** #28991 把 account metadata、Agent Identity JWT/storage、provider account、app-server `account/read`、Python generated client 和 TUI bootstrap 都改成保留 `email: null` / `None`，plan type 仍必需；这修复了无邮箱服务账号 PAT 解码失败。#26678 为 `permissionProfile/list` 的每个 profile summary 增加 `allowed` 字段，让 app-server/TUI 可以展示被管理员/要求禁用但不可选的 profile；#29479 随后把 `:danger-full-access` 内建 profile ID 常量化并重命名 `is_permission_profile_allowed`，避免回到旧的无效 `:danger-no-sandbox` 值。 [PR #28991](https://github.com/openai/codex/pull/28991) / [PR #26678](https://github.com/openai/codex/pull/26678) / [PR #29479](https://github.com/openai/codex/pull/29479)

- **app-server 测试客户端开始能处理交互式 `request_user_input`，remote plugin 缓存也会持久化后端插件 ID。** #29476 让 `codex-app-server-test-client` 遇到 `item/tool/requestUserInput` 时不再直接终止连接，而是展示编号选项、接受精确标签、支持 free-form `Other` / text-only question / 多问题收集，并发送协议原生 `ToolRequestUserInputResponse` 后继续同一 turn；这提高了端到端测试交互式 turn 的可验证性。#27669 则在远程插件 bundle cache root 下写入原子 `.codex-remote-plugin-install.json` sidecar（`schema_version: 1`、`remote_plugin_id`），安装和 sync 时写入/回填，本地或通用安装替换时清理，用于后续 analytics/消费者无需网络请求解析权威后端身份。 [PR #29476](https://github.com/openai/codex/pull/29476) / [PR #27669](https://github.com/openai/codex/pull/27669)

- **较小但值得保留的工作流/配置增量：rollout budget reminder 改成显式剩余 token 阈值，tungstenite fork pins 也同步推进。** #29423 把原先单一 `reminder_interval_tokens = 65_536` 改为可配置 `reminder_at_remaining_tokens = [65_536, 32_768, 16_384, 8_192, 4_096, 2_048, 1_024, 512]`，更适合在长上下文任务中按剩余预算分级提醒；#29480 则把 `tokio-tungstenite` git pin 推到 `0e5b2d73...`、`tungstenite` fork pin 推到 `4fffad30...`，并更新 Cargo/Bazel lock，主要是依赖一致性维护。 [PR #29423](https://github.com/openai/codex/pull/29423) / [PR #29480](https://github.com/openai/codex/pull/29480)

**今日取舍：** 已加载/遵循 `daily-report-lane-codex` 要求，读取 `input.md`、`context.json`、23 个 Codex raw 文件，以及 2026-06-22 / 2026-06-21 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 驱动判断。近两日已覆盖 `0.142.0-alpha.8`–`alpha.10`、remote sandbox intent、code-mode runtime/shutdown/observation、远端 skill discovery 并发、plan mode prompt、busy 状态 `/resume`/settings、world state、context window lineage IDs 等；今天保留新的 `alpha.11`/`alpha.12` 版本列车、auth/system proxy + Windows resolver、managed MITM 自定义 CA、无邮箱账号、permission profile availability、app-server test-client 交互输入、remote plugin ID sidecar、rollout budget thresholds 和 tungstenite pins。commit 与 merged PR 重复时合并为同一条证据；`alpha.9` 和纯重复 commit 仅作去重/版本连续性参考。

## OpenClaw

- **OpenClaw `v2026.6.10-beta.2` 在 `beta.1` 后继续收窄到“短对话更快、模型路由更稳、会话/策略状态更安全”三类运行时修复：短 conversational turns 可自动启用 fast mode，长任务再回到 normal mode；Zai/GLM 模型合成、overload failover 与 `/think` reasoning-level 选择改为更一致地跟随实时 model catalog；channel switch 会清掉 stale origin，cron delivery awareness 绑定目标 session，hook registry 组合后也不会丢 trusted tool policies。** 对使用 OpenClaw 跑多渠道 agent、cron delivery、Zai/GLM 或需要审批/信任策略的团队，`beta.2` 相比昨天已刊登的 `beta.1` 更像一次风险面收敛：重点回归 short-turn fast mode fallback、channel 切换后的投递目标、Zai/GLM failover、runtime reasoning menu，以及 approval-sensitive tool policy 是否仍被保留。https://github.com/openclaw/openclaw/releases/tag/v2026.6.10-beta.2

**今日取舍：** 常规 `openclaw` package 目录缺失，因此按 master 规则改用同日 `openclaw-watch` raw 证据目录；采集成功，`run.json`/`index.md` 显示 3 个 release signals。`v2026.6.10-beta.2` 是今天唯一相对 2026-06-22 报告的新版本；`v2026.6.10-beta.1` 与 `v2026.6.9` 已在 2026-06-22 OpenClaw 栏覆盖，今天仅作为去重背景，不重复展开。

## GitHub AI 项目

- **[koala73/worldmonitor](https://github.com/koala73/worldmonitor)（GitHub API 校验 58,580 stars）本周上榜，定位是“AI-powered news aggregation / geopolitical monitoring / infrastructure tracking”的实时全球情报仪表盘。** 这不是 coding-agent 框架，但 raw 明确给出 AI 驱动的新闻聚合与态势感知用途；对需要把公开新闻、地缘事件和基础设施信号接入 agent/分析工作流的团队，试用重点应放在来源追溯、去重/误报、实时数据权限、地图/告警副作用，以及模型生成摘要能否回链到原始证据。 [GitHub](https://github.com/koala73/worldmonitor)

**今日取舍：** 已读取 `input.md`、`context.json`、GitHub trending weekly raw、交叉 raw、`raw/selected-items/system_prompts_leaks.json` audit 文件，以及 2026-06-22 / 2026-06-21 历史报告；历史仅用于去重，`selected-items` 仅作 audit 参考。按 hard floor stars ≥100，本次只选择有当日 raw 支撑、GitHub API 校验达标、且近两日报告未实质展开的新仓库：`koala73/worldmonitor` 58,580 stars。`calesthio/OpenMontage` 昨日已在本栏展开；`withastro/flue`、`DeusData/codebase-memory-mcp`、`addyosmani/agent-skills`、`NVIDIA/SkillSpector`、`Panniantong/Agent-Reach`、`chopratejas/headroom` 等虽达标但已在近日报告覆盖或明确去重；`asgeirtj/system_prompts_leaks`、`LMCache/LMCache`、`google-research/timesfm` 达标但分别偏提示词归档、LLM serving KV-cache 与时序预测，今天与 AI/coding-agent 项目工作流的直接增量弱于入选线。`OpenCut-app/OpenCut` 与多项高星通用开源项目虽达标或上榜，但 raw 未提供足够明确的 AI/coding-agent 当日增量。

## GitHub 趋势项目

今日暂无可新增的 GitHub 趋势项目。本次 `github-trending-weekly` raw corpus 正常，共 18 个仓库信号；按 hard floor stars ≥100 与“只选 AI/coding-agent workflow 相关仓库”的要求筛选后，直接相关的 `withastro/flue`、`calesthio/OpenMontage`、`DeusData/codebase-memory-mcp`、`addyosmani/agent-skills`、`NVIDIA/SkillSpector`、`Panniantong/Agent-Reach` 等均已在近两日报告中展开或明确去重，今天 raw 未提供新的 release、功能变化或可作为 follow-up 的新增事实。

**今日取舍：** 已读取 `input.md`、`context.json`、18 个 GitHub trending raw 文件，以及 2026-06-22 / 2026-06-21 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 驱动判断。`LMCache/LMCache`、`google-research/timesfm`、`asgeirtj/system_prompts_leaks`、`koala73/worldmonitor` 虽与 AI/模型/情报相关，但分别偏 LLM serving KV-cache、时序预测、系统提示词归档和新闻情报 dashboard，缺少今天面向 coding-agent 工作流的直接增量；`Kong/insomnia`、`makeplane/plane`、`penpot/penpot`、`freeCodeCamp/freeCodeCamp`、`n0-computer/iroh` 等是通用开发或非 AI 项目，raw 未给出当日 agent/coding workflow 事实。因此本栏输出空结果，避免重复刊登近两日已处理的 GitHub trending 仓库。

## Rize AI 工具榜

今日暂无可新增的 Rize AI 工具榜更新。本次 raw corpus 正常，共 20 条 Rize weekly ranking 证据，采集时间均为 2026-06-22T22:03:53+0000；但它仍是同一批 Rize AI Tools weekly ranking 快照的延续，raw 只提供排名、GitHub 仓库链接和一句项目简介，没有新增排名变化、仓库发布事实、评分变化或可作为 follow-up 的新证据。近两日报告已连续判定该快照无新增增量，今天继续空栏，避免把同一批榜单项目重复写成日报更新。

**今日取舍：** 已读取 `input.md`、`context.json`、20 条 Rize raw，以及 2026-06-22 / 2026-06-21 历史报告；raw corpus 为主要证据，历史仅用于去重，未使用 `selected_items.json` 作为主要判断。近日报告已覆盖并随后去重 #3 `antigravity-awesome-skills`、#4 `nanobot`、#5 `MemPalace`、#6 `OpenSquilla`、#7 `headroom`、#9 `graphify`、#10 `hermes-studio`、#12 `TencentDB-Agent-Memory` 等核心 AI/coding-agent 项目；今天 #1 `worldmonitor`、#2 `openclaude`、#8 `ilab-gpt-conjure`、#11 `openlake`、#13 `knowhere`、#14 `oh-my-pi`、#15 `maths-cs-ai-compendium`、#16 `Toonflow-app`、#17 `claude-ads`、#18 `OfficeCLI`、#19 `awesome-openclaw-usecases-zh`、#20 `Data-Analysis-Agent` 也只有榜单位置与一句简介，未提供比近两日更强的新事实，因此全部作为重复或弱增量项剔除。

## Product Hunt 新品

- **AgentX** 登上 Product Hunt，定位是“评估 AI agent、定位问题并一键修复”。这比通用 observability 更贴近 agent 交付闭环：如果要接入 coding-agent/业务 agent，重点应验证它能否复现失败轨迹、区分提示词/工具/环境问题、给出的 fix 是否可审查，以及是否会在一键修复时越过测试、权限和人工审批。 [Product Hunt](https://www.producthunt.com/products/agentx?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **Skybridge** 主打“面向 MCP Apps 的全栈开源 React framework”。它的价值不在又一个前端框架，而在把 MCP 应用的 UI、服务端和工具调用边界产品化；评估时应看 MCP server/client 鉴权、工具 schema 版本化、agent 可见能力的最小授权、React 状态与工具执行日志如何关联，以及部署后多租户隔离。 [Product Hunt](https://www.producthunt.com/products/skybridge?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

- **Selector Forge** 是一个为 AI 生成 resilient selectors 的浏览器扩展。对浏览器自动化、UI 测试和网页操作 agent 来说，稳定 selector 往往比“模型再看一遍截图”更便宜也更可审计；试用时应关注动态 DOM、Shadow DOM、i18n 文案变化、权限注入范围，以及生成 selector 能否随测试失败回写为可维护的定位规则。 [Product Hunt](https://www.producthunt.com/products/selector-forge?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

**今日取舍：** raw corpus 状态为 ok，共 13 个 Product Hunt topic hit；已读取 `input.md`、`context.json`、raw 索引/摘录与 2026-06-22 / 2026-06-21 历史报告，历史仅作去重参考，未使用 `selected_items.json` 驱动判断。近两日已覆盖 agent 记忆层、JetBrains 快速 LLM、Slack AI coworker、客户专属 Hermes/OpenClaw agent、Poolside agentic coding 模型和备份 MCP；今天优先保留未被近两日报告实质展开、且直接服务 agent 评测修复、MCP app 开发和浏览器自动化 selector 的 AgentX、Skybridge、Selector Forge。剔除 Cloudflare Temporary Accounts，因 2026-06-22 X 推荐已覆盖“一行命令让 agent/demo 临时部署 Workers”；剔除 Agentic Document Extraction、MD+HTML Reader、OnBrand、Alai 2.0、AirJelly、Clawd、AlgoFly AI、HAQQ Legal AI、uwait，主要因偏文档/设计/知识库/本地 mascot/视觉 AI/法律/创作者计费等通用或垂直 AI 产品，与今日入选项相比对 AI/coding-agent 工程工作流的直接增量更弱。

## Polymarket AI 市场

- **6 月最佳 Coding AI 模型盘口仍押 Anthropic，但优势从昨日报告的 95.4% 降到 93.8%；OpenAI 2.2%、Moonshot 0.6%，24h 成交量约 2,624.9，30d 约 46,260.9。** 这只是交易者预期，做 coding-agent 选型仍要看自家任务的可合并率、测试通过率和工具调用稳定性。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-coding-ai-model-end-of-june)

- **6 月最佳 AI 模型总榜给 Anthropic 93.0%，Google 5.5%、OpenAI 1.7%；30d 成交量约 633.7 万、流动性约 337.2 万，raw 标注本月上行 19.4%。** 相比昨日报告的 94.5% 小幅回落，但资金量仍远高于其他 AI 盘口；不要把通用总榜直接等同于 coding、数学或长上下文能力。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-june)

- **7 月最佳 AI 模型远期盘回到 Anthropic 84.5%，Google 10.8%、OpenAI 4.7%；24h 成交量约 77,808.1，30d 约 934,506.0。** 较昨日报告的 83.5% 回升 1 个百分点，说明市场仍押注 Anthropic 优势延续；远期盘容易被新模型发布和榜单口径重定价。 [Polymarket](https://polymarket.com/event/which-company-has-best-ai-model-end-of-july-299)

- **6 月最佳 Math AI 模型盘转为 Google 73.5%，OpenAI 16.0%、Anthropic 7.5%；24h 成交量约 9,979.1，raw 标注本周下行 12.5%。** 昨日报告中 Google 为 83.0%，数学盘口继续和通用总榜分化；形式化推理、benchmark-heavy agent 和代码证明任务应单独评测。 [Polymarket](https://polymarket.com/event/which-company-has-the-best-math-ai-model-end-of-june)

- **FrontierMath 长盘把“2027 前任一 AI 模型 ≥90%”的 Yes 抬到 83.0%，30d 成交量约 29,758.3，流动性约 12,371.8；raw 标注本月上行 62.0%。** Grok 子盘同时给 ≥40% 为 81.0%、≥50% 为 11.5%；这些都是市场预期，不是模型成绩已确认。 [FrontierMath](https://polymarket.com/event/ai-model-scores-90-on-frontiermath-benchmark-before-2027) / [Grok 市场](https://polymarket.com/event/xai-grok-score-on-frontiermath-benchmark-by-june-30)

- **Coding Arena 绝对门槛盘显示“2026 年底任一 AI 模型达到 1560 分”约 71.5%，30d 成交量约 3,354.0，流动性约 7,513.1，raw 标注本月下行 12.5%。** 这和“最佳 Coding AI 公司”盘口是不同问题：一个看相对第一名，一个看绝对分数门槛。 [Polymarket](https://polymarket.com/event/will-any-ai-model-reach-coding-arena-score-by-december-31)

**今日取舍：** raw corpus 状态为 ok，共 11 条 Polymarket 证据；已读取 `input.md`、`context.json`、全部 raw 文件和 2026-06-22 / 2026-06-21 历史报告作为去重参考，未使用 `selected_items.json` 驱动判断。保留与 AI/coding-agent 直接相关、且有当日概率/成交量或近日报告可比变化的 6 月 Coding AI、6 月/7 月模型总榜、6 月 Math AI、FrontierMath/Grok 与 Coding Arena 1560；剔除估值盘、Style Control 版总榜、第二名细分盘口等重叠或弱增量条目。所有概率均为 Polymarket 市场预期，不是已确认 benchmark 或产品事实。
