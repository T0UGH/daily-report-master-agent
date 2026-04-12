# daily-report-master-agent

这是一个 runtime-agnostic 的 daily report master agent pack。

- 第一阶段宿主是 Hermes cronjob
- 未来可切回 OpenClaw
- 通过 `uvx` / CLI 调用 `signals-engine`
- 当前仓库以 main agent + skills + contracts + templates 的骨架起步
