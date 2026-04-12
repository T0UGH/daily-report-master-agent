# AI Agent 日报（2026-04-12）

## X 推荐流
- **Claude Code 的 `/ultraplan` 继续从功能点变成工作流叙事。** 这条高传播 X 帖把“先在 Web 上生成和审阅实施计划，再决定是否落到本地执行”的流程讲得非常直白，说明远程审计划式协作已经开始被更广的 agent 用户理解和转述。[原帖](https://x.com/trq212/status/2042671370186973589)

## X 关注流
- **agent harness 的测试思路开始往 `agent matrix` 方向延伸。** 跟踪作者把传统 BDD 驱动的大范围 e2e 测试和 agent 工作流放到一起思考，核心问题不再只是“怎么测”，而是如何减少流程里的人类断点。[原帖](https://x.com/turingou/status/2043276169613844889)

## Reddit 社区
- **Plan -> Build -> Review 三段式团队仍是 Claude Code 用户最自然的组织方式。** 这条 Reddit 热帖把 Architect、Builder、Reviewer 拆成 3 个 agent，并用 markdown handoff 保持流程透明；评论区虽然质疑它是否算新东西，但基本认同这种结构化协作比单 agent 乱跑更稳。[Reddit](https://www.reddit.com/r/ClaudeAI/comments/1sa7ju4/i_replaced_chaotic_solo_claude_coding_with_a/)

## Claude Code
- **v2.1.101 同时补了团队上手、远程协作和受限环境可用性。** 这一版把 `/team-onboarding`、默认云环境、brief mode 重试和工具错误说明一起往前推，读下来最明显的方向不是再加一个炫技命令，而是把多人协作和真实企业环境里的可用性补齐。[Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.101)

## Codex
- **Guardian timeout 被正式和显式拒绝分开处理。** 这次 Codex 变更把审批超时从“像被 policy 拒绝”中拆出来，更新了 command、shell、network 和 MCP 的审批路径，也补了针对性测试，明显是在修 agent 执行链路里的错误语义。[GitHub](https://github.com/openai/codex/pull/17521)

## OpenClaw
- **OpenClaw 2026.4.11 继续把“多模型代理平台”往产品化收口。** 这一版既加了 Dreaming 的 ChatGPT 导入、webchat 结构化富媒体和插件激活描述，也修了 Codex OAuth `invalid_scope`、QA 泄漏和 provider failover 这类真正影响生产可用性的细节。[Release](https://github.com/openclaw/openclaw/releases/tag/v2026.4.11)

## Product Hunt 新品
- **MCP 继续向“上下文打包器”形态外溢。** `Nicelydone MCP` 在 Product Hunt 上的卖点不是又一个通用 agent，而是专门把设计上下文喂给 AI agents，说明面向工作流环节的 MCP 包装已经开始变成可以单独售卖的产品层。[Product Hunt](https://www.producthunt.com/products/nicely-done?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29)

## Polymarket 市场
- **市场对 Anthropic 在 coding AI 第二梯队的位置判断相当集中。** 这份 Polymarket 合约里，“Anthropic 会在 2026 年 4 月底拿到第二好的 Coding AI 模型”当前概率约 89.5%，而且周内又抬了 19%，说明交易者对头部 coding model 排名的分层已经有了较强共识。[Polymarket](https://polymarket.com/event/which-company-has-the-second-best-coding-ai-model-end-of-april)

## 来源

### X 推荐流
- @trq212 #14 — https://x.com/trq212/status/2042671370186973589

### X 关注流
- @turingou — https://x.com/turingou/status/2043276169613844889

### Reddit 社区
- I replaced chaotic solo Claude coding with a simple 3-agent team (Architect + Builder + Reviewer) — https://www.reddit.com/r/ClaudeAI/comments/1sa7ju4/i_replaced_chaotic_solo_claude_coding_with_a/

### Claude Code
- v2.1.101 — https://github.com/anthropics/claude-code/releases/tag/v2.1.101

### Codex
- Clarify guardian timeout guidance — https://github.com/openai/codex/pull/17521

### OpenClaw
- openclaw 2026.4.11 — https://github.com/openclaw/openclaw/releases/tag/v2026.4.11

### Product Hunt 新品
- Nicelydone MCP — Design context for AI agents — https://www.producthunt.com/products/nicely-done?utm_campaign=producthunt-api&utm_medium=api-v2&utm_source=Application%3A+gui-ai-daily+%28ID%3A+279028%29

### Polymarket 市场
- Will Anthropic have the second-best Coding AI model at the end of April 2026? — https://polymarket.com/event/which-company-has-the-second-best-coding-ai-model-end-of-april
