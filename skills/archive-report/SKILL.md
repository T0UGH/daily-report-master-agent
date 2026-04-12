# archive-report

## 目的

把最终日报归档到 Obsidian。

## 输入

- 最终 `report artifact`
- `publish_result`

## 执行边界

- 只归档最终日报
- 只在 `publish_result.status == succeeded` 时执行
- 不归档运维通知
- 不归档中间稿

## 输出

最小 `archive result`：

- `status`
- `target = obsidian`
- `reference`
- `error_summary`

## 约束

- 归档失败只会把结果降为 `degraded`
- 不会撤回已经成功发布到 Feishu 的日报
