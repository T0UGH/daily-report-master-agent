# publish-report

## 目的

把最终 `report artifact` 发布到 Feishu，形成 v0 的主交付结果。

## 输入

- 最终 `report artifact`
- 发布模板 `templates/feishu-report.md`

## 执行边界

- 只消费最终成品，不接收 Editor 或 Humanizer 中间稿
- 发布目标固定为 Feishu
- 发布成功后才允许继续归档

## 输出

最小 `publish result`：

- `status`
- `target = feishu`
- `reference`
- `error_summary`

## 约束

- Feishu 是主交付面
- v0 不扩展到其他发布目标
