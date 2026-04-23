# publish-report

## 目的

把最终 `report artifact` 发布到 Feishu，形成 v0 的主交付结果。

## 输入

- 最终 `report artifact`
- 发布模板 `templates/feishu-report.md`
- 显式交付契约 `contracts/publish-delivery-contract.md`

## 执行边界

- 默认交付物、内容编排和降级语义以 `contracts/publish-delivery-contract.md` 为准
- 只消费最终成品，不接收 Editor 或 Humanizer 中间稿
- 发布目标固定为 Feishu
- Feishu 全量文档是主交付锚点；精选卡片顶部必须带文档链接
- 发布成功后才允许继续归档

## 输出

最小 `publish result`：

- `status`
- `target = feishu`
- `reference`（默认指向 Feishu 全量文档）
- `error_summary`
- `deliverables`（如返回明细，键名与 contract 保持一致）

## 约束

- `contracts/publish-delivery-contract.md` 是 publish 默认规则的唯一显式 contract；prompt prose 只能引用，不能替代
- Feishu 是主交付面
- v0 不扩展到其他发布目标
