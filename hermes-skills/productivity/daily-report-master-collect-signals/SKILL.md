---
name: daily-report-master-collect-signals
description: 06:00 master cron 自己负责调用 signals-engine 收集当天 signals，并在同一 run 内诊断/重试 collect 失败。
---

# Daily Report Master — Collect Signals

用于 daily report 主链路中的 `collect-signals` 阶段。

## 目标

- 调用外部 `signals-engine` 收集当天真实 signals
- 不假设当天 signals 已经存在
- 输出最小 `collect result`
- 输出与主链路后续阶段兼容的真实运行产物

## 必读位置

- `config/runtime.yaml`
- `contracts/runtime-contracts.md`
- `contracts/idempotency-rerun.md`
- `helpers/build_collect_result_from_signals.py`
- `helpers/build_selected_items_from_signals.py`
- `helpers/build_validation_bundle.py`
- `helpers/run_daily_report_flow.py`

## 执行要求

1. 使用 `Asia/Shanghai` 日期作为 `report_date`。
2. 通过 `signals-engine` 逐 lane collect 当天真实 signals。
3. 如果 collect 失败或部分失败：
   - 先记录失败点
   - 在同一 run 内合理 diagnose
   - 合理时 retry
4. collect 完成后生成：
   - `collect-result.json`
   - `selected-items.json`
   - `validation-bundle.json`

## 首选命令

优先使用仓库的稳定入口：

```bash
python3 ~/workspace/daily-report-master-agent/helpers/run_daily_report_flow.py \
  --report-date YYYY-MM-DD \
  --config ~/workspace/daily-report-master-agent/config/runtime.yaml
```

如果只需要执行 collect 阶段，也应先参考该脚本里的 collect / diagnose / retry 顺序，而不是自由发挥。

## 边界

- 这一步只负责收集和中间产物构建
- 不在这一步判断日报是否成立
- 不在这一步直接 publish / archive
