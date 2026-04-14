---
name: daily-report-master-archive-report
description: 在 Feishu 发布成功后归档最终日报；归档失败会降级，但不推翻已成功的主交付。
---

# Daily Report Master — Archive Report

## 目标

归档最终 reader-facing 日报。

## 必读位置

- `contracts/runtime-contracts.md`
- `contracts/failure-matrix.md`

## 规则

- 只归档最终日报
- 只在 publish 成功后执行
- archive 失败时降级为 `degraded`，但不推翻已成功发布的日报
