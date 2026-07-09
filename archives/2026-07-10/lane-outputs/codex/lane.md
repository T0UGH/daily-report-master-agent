## Codex

- **Codex 继续把网络请求收敛到统一 HTTP client。** 文件上传三段流程和 login 的 device-code/OAuth/API-key token 交换都改走 `HttpClientFactory`，配合 cargo-deny 禁止新增一方 crate 直接依赖 `reqwest`；企业代理、自定义 CA 和敏感 auth 日志边界更容易统一治理。来源：https://github.com/openai/codex/pull/31363 · https://github.com/openai/codex/pull/31637 · https://github.com/openai/codex/pull/31431

- **Code Mode 补上 macOS 安装和缺 host 时的降级路径。** 安装器会把 `code-mode-host` symlink 到 `codex` 旁边；若发行包缺少 companion binary，只在 `NotFound` 时回退到进程内 V8，权限、握手和超时错误仍会显式暴露。来源：https://github.com/openai/codex/pull/31876 · https://github.com/openai/codex/pull/31899

- **Codex Apps 文件参数会按工具 schema 过滤可选字段。** 文件上传重写后始终传 `download_url` 和 `file_id`，但只有 schema 接受时才附带 `mime_type`、`file_name`；严格 MCP 工具不再因多余字段拒绝调用。来源：https://github.com/openai/codex/pull/31686

- **Bundled OpenAI Docs skill 更新到 GPT-5.6。** 新版通过 `latest-model.md` 解析 current/default-model，加入 GPT-5.6 Sol/Terra/Luna 迁移判断，并补 POSIX resolver 与 Windows CommonJS 入口；安装后的 Codex 能直接拉到新模型提示和迁移指南。来源：https://github.com/openai/codex/pull/31842

- **图像生成默认切到 extension 路径。** `Feature::ImageGeneration` 现在专门控制 extension-backed image generation，MCP server 和 core API sample host 默认安装该 extension，同时保留 `imagegenext` 兼容别名。来源：https://github.com/openai/codex/pull/31596
