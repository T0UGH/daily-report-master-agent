---
name: daily-report-master-build-report
description: 用 selected_items 构建最终 reader-facing 日报，遵守固定 output contract，并优先保留原始事实密度。
---

# Daily Report Master — Build Report

## 目标

在日报成立时，构建最终 `report artifact`。

## 必读位置

- `config/runtime.yaml`
- `contracts/report-output-contract.md`
- `contracts/selected-items.md`
- `helpers/run_daily_report_flow.py`
- `helpers/validate_report_output_contract.py`
- `templates/report-body-template.md`

## 核心规则

- 固定顺序：`Editor -> Humanizer -> final report artifact`
- 主 agent 只消费最终 artifact
- 忠实原文的中文整理优先，判断总结次之
- 不允许空心总结句代替事实
- X 推荐流 / X 关注流默认各写 6–10 段（信号充足时）
- 生成后必须通过 output contract validation

## 首选命令

```bash
python3 ~/workspace/daily-report-master-agent/helpers/run_daily_report_flow.py \
  --report-date YYYY-MM-DD \
  --config ~/workspace/daily-report-master-agent/config/runtime.yaml
```

若只重建 build 阶段，也应复用该脚本已经产出的 `collect-result.json`、`selected-items.json`、`report-artifact.json`、`report.md` 路径，不要临场造一套新路径。
