---
name: daily-report-master-publish-report
description: 将最终 reader-facing 日报发布到 Feishu，并记录主交付结果。
---

# Daily Report Master — Publish Report

## 目标

把最终日报发布到 Feishu，形成默认主交付结果：`Feishu 文档 + Feishu 原生可播放音频`。

## 必读位置

- `contracts/runtime-contracts.md`
- `templates/feishu-report.md`

## 规则

- 只有 report artifact 已成立时才可 publish
- publish 成功后才允许 archive
- publish 已成功的同日 rerun 不能重复发送第二条日报
- 文档发布继续走 `feishu-cli doc import`
- 音频必须先转成 `.opus`（Ogg/Opus），再以 Feishu 原生音频消息发送
- 不要用外链、说明页或普通文件附件代替原生可播音频
- publish 状态语义固定：
  - 文档失败 => `failed`
  - 文档成功但音频失败 => `degraded`
  - 文档和音频都成功 => `succeeded`
