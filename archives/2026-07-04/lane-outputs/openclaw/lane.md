## OpenClaw

- OpenClaw `v2026.6.11` 稳定版补了一轮多渠道送达可靠性：Telegram、WhatsApp、Matrix、Google Chat、iMessage、Feishu 等都覆盖错投、重复、卡住和重连问题，适合运营多入口 agent 的团队升级验证。来源：https://github.com/openclaw/openclaw/releases/tag/v2026.6.11
- 该版本强化模型与 provider 恢复：Codex 用量限制、Claude CLI 额度耗尽、本地 provider 泛化失败、OpenRouter/Google catalog 异常等场景会更明确地 fallback 或 fail-safe，降低 agent run 直接中断的概率。来源：https://github.com/openclaw/openclaw/releases/tag/v2026.6.11
- 运维侧新增 `openclaw agent --message-file`、RAFT CLI wake bridge、Slack relay mode、Mattermost `/oc_queue`、per-DM 模型覆盖和 per-agent usage-cost 统计，重点是把远程唤醒、队列和成本核算做进正式工作流。来源：https://github.com/openclaw/openclaw/releases/tag/v2026.6.11
