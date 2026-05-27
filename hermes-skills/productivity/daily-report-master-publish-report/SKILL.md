---
name: daily-report-master-publish-report
description: 将最终 reader-facing 日报发布到 Feishu，并记录主交付结果。
---

# Daily Report Master — Publish Report

## 目标

把最终日报发布到 Feishu，形成默认主交付结果：`Feishu 文档 + Feishu 精选卡片 + Feishu 原生可播放音频`。

## 必读位置

- `contracts/runtime-contracts.md`
- `contracts/publish-delivery-contract.md`
- `templates/feishu-report.md`

## 规则

- 只有 report artifact 已成立时才可 publish
- publish 成功后才允许 archive
- publish 已成功的同日 rerun 不能重复发送第二条日报
- 文档发布继续走 `feishu-cli doc import`
- 发布顺序固定为：先发文档，再发 Feishu 精选卡片，最后发 Feishu 原生音频
- 精选卡片顶部必须带文档链接；天气模块默认排第一，至少覆盖北京和上海（上海默认杨浦）
- `Claude Code` 与 `Codex` 是卡片固定保留栏目；`OpenClaw` 默认不进卡片，除非 MT 明确要求临时查看；`Product Hunt` 默认 2~3 条
- 音频必须先转成 `.opus`（Ogg/Opus），再以 Feishu 原生音频消息发送
- 不要用外链、说明页或普通文件附件代替原生可播音频
- publish 状态语义固定：
  - 文档失败 => `failed`
  - 文档成功但卡片或音频任一失败 => `degraded`
  - 文档、卡片、音频都成功 => `succeeded`
