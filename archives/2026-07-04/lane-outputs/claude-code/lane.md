## Claude Code

- **Claude Code 2.1.201 调整 Sonnet 5 会话的 harness 提醒方式。** Sonnet 5 会话不再用 mid-conversation system role 承载 harness reminders，依赖系统消息位置做测试或日志分析的团队需要重新核对行为。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.201)

- **2.1.200 把默认权限模式改成 Manual。** CLI、`--help`、VS Code 和 JetBrains 都把 “default” 指向手动确认；配置里可显式写 `--permission-mode manual` 或 `"defaultMode": "manual"`，自动化脚本要避免误以为默认会自动放行。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)

- **`AskUserQuestion` 现在默认不会无人响应后自动继续。** 2.1.200 需要在 `/config` 里主动开启 idle timeout；这能减少代理替用户做假设，但长任务编排要显式配置超时策略。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)

- **2.1.199 改进失败可见性：部分输出和子代理错误不会再被吞掉。** 中途 overloaded/server error 后已有流式内容会保留并标记 incomplete；subagent 遇到 rate limit、server error 或 usage limit 会把部分结果或错误回传给 parent。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.199)

- **2.1.199 支持最多 5 个连续 slash-skill 一次加载。** 形如 `/skill-a /skill-b do XYZ` 会加载所有前置技能，不再只执行第一个；适合把规范、测试、发布等技能组合进同一轮任务。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.199)

- **后台 agent 的守护进程和远程会话继续补可靠性。** 2.1.199 修复 Linux 异常关机后每约 50 秒杀掉全部 agent、macOS SSH 冷启动失败、`claude stop` 被 respawn 抵消；2.1.200 又修 stale `daemon.lock`、sleep/wake 后 mid-turn 停止和取消后重跑。 [Release 2.1.199](https://github.com/anthropics/claude-code/releases/tag/v2.1.199) · [Release 2.1.200](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)

- **插件、MCP 和可访问性也有小修。** 2.1.200 修复 worktree 中 project-scoped plugins 加载、`claude agents --plugin-dir <dir>` 参数位置问题，并改善 `/mcp` 列表焦点与 screen-reader 输出。 [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.200)
