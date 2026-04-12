# collect-signals

## 目的

调用外部 `signals-engine`，收集生成日报所需的最小 signal 结果。

## 输入

- `report_date`
- 宿主提供的最小触发上下文

## 执行边界

- 通过现有命令入口调用 `signals-engine`
- 只要求拿到最小 `collect result`
- 不在本 skill 内做日报是否成立、发布、归档或通知判断

## 输出

输出必须满足 `contracts/runtime-contracts.md` 中对 `collect result` 的最小约定，至少包含：

- `report_date`
- `source`
- `lanes`
- `summary.useful_item_count`

## 约束

- `signals-engine` 仍然是外部工具，不做源码级强耦合
- helper 不在本 skill 中承担 orchestration
