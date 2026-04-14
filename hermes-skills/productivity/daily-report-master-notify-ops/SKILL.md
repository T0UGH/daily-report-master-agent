---
name: daily-report-master-notify-ops
description: 仅在 degraded 或 blocked 时发送运维通知，只讲状态、异常与最终链接。
---

# Daily Report Master — Notify Ops

## 目标

在 `degraded` 或 `blocked` 场景下发送简短运维通知。

## 规则

- 正常成功时不发
- 内容只讲状态、异常、是否已重试、最终链接
- 不把运维通知写成第二份日报
