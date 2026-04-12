# notify-ops

## 目的

在 `degraded` 或 `blocked` 时向主聊天发送最小运维通知。

## 触发条件

- `verdict.status == degraded`
- `verdict.status == blocked`

## 输入

- `verdict`
- `publish_result`
- `archive_result`
- 模板 `templates/ops-notice.md`

## 通知内容

最小通知只包含：

- 当前状态
- 一句话异常原因
- 已发布链接或消息引用（如果有）
- 归档失败信息（如果有）

## 约束

- 正常日不发送运维通知
- 运维通知不做内容总结，不归档到 Obsidian
