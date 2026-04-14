---
name: daily-report-master-publish-report
description: 将最终 reader-facing 日报发布到 Feishu，并记录主交付结果。
---

# Daily Report Master — Publish Report

## 目标

把最终日报发布到 Feishu，形成主交付结果。

## 必读位置

- `contracts/runtime-contracts.md`
- `templates/feishu-report.md`

## 规则

- 只有 report artifact 已成立时才可 publish
- publish 成功后才允许 archive
- publish 已成功的同日 rerun 不能重复发送第二条日报
