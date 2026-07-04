## Codex

- Codex 独立安装器现在复用一次 GitHub release metadata：`install.sh` / `install.ps1` 不再为版本、平台包、checksum 和 digest 连续打 4 次未认证 API；遇到 `403` 也会按 GitHub 可用性或限流报错，而不是误报“资产不存在”。来源：https://github.com/openai/codex/pull/31056

- 远程插件列表暴露版本信息：`PluginSummary.version` 表示远程 marketplace 公布的版本，`plugin/installed` 保留后端 release version，`localVersion` 继续表示本地已物化包版本，方便区分“远端可用”和“本地已装”。来源：https://github.com/openai/codex/pull/30981

- Codex Desktop 反馈附件修复 MIME 类型：路径上传的 gzip 日志包不再被标成 `text/plain`，未知二进制回落到 `application/octet-stream`，避免 Sentry 消费端按 UTF-8 解码后破坏日志 bundle。来源：https://github.com/openai/codex/pull/30796

- `0.143.0-alpha.35` 已发布，继 `alpha.33`、`alpha.34` 后继续提供 npm、wheel、macOS/Linux/Windows 二进制与 app-server 相关资产；release note 只有版本号，适合预发布通道用户做兼容性烟测。来源：https://github.com/openai/codex/releases/tag/rust-v0.143.0-alpha.35

- Codex 清理了遗留 `cliff.toml`：TypeScript CLI 时代的 `git-cliff` changelog 配置已不再被当前 Rust release workflow 使用，删除后可减少贡献者对发布流程的误判。来源：https://github.com/openai/codex/pull/31066
