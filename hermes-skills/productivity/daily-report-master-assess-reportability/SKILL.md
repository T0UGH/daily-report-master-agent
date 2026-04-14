---
name: daily-report-master-assess-reportability
description: 根据 collect result 判断当天日报是否成立，并决定是 normal/degraded/blocked 路线里的哪一种入口。
---

# Daily Report Master — Assess Reportability

## 目标

根据 `collect result` 判断今天是否成立日报。

## 必读位置

- `contracts/runtime-contracts.md`
- `contracts/failure-matrix.md`
- `contracts/idempotency-rerun.md`

## 核心规则

- 只要至少有一条有用内容，日报就成立
- lane 异常不会自动否决日报
- `summary.useful_item_count == 0` 时直接进入 `blocked`
- assess 结果必须与后续 `verdict` 逻辑一致
