# Publish Delivery Contract v0

## 目标

这份文档定义 `publish-report` 的默认交付物、默认栏目编排和降级语义。它是仓库内 publish 规则的显式 contract；技能提示词只能引用，不能替代。

## 1. 默认交付物

| key | 中文名 | 默认属性 | 规则 |
| --- | --- | --- | --- |
| `feishu_full_doc` | Feishu 全量文档 | 必选 | 主交付锚点。 |
| `feishu_curated_card` | Feishu 精选卡片 | 必选 | 顶部必须包含 `feishu_full_doc` 链接。 |
| `feishu_native_audio` | Feishu 原生音频 | 必选 | 基于同一份最终日报内容生成。 |

- 默认发布交付物就是 `feishu_full_doc + feishu_curated_card + feishu_native_audio`。
- 如无显式运行时配置关闭，三种交付物都应被尝试生成。

## 2. 默认栏目编排与选材规则

- 在 Feishu 全量文档、Feishu 精选卡片、Feishu 原生音频这三种默认交付物里，天气模块都排第一。
- 天气模块默认收录北京和上海；上海固定使用杨浦，标识为 `shanghai-yangpu`，不再使用 `shanghai-xuhui`。
- 读者可见标题默认写作 `北京…天气` 与 `上海杨浦天气`，不得再写 `上海徐汇天气`。
- `Claude Code` 与 `Codex` 是固定保留 lane；只要当日有有效内容，就不能因为压缩篇幅而被挤掉。
- `OpenClaw` 默认不进入交付物；只有 MT 明确要求临时查看 OpenClaw 时，才作为一次性补充处理，不改变默认日报 contract。
- `Product Hunt` 默认保留 2-3 条；不足时按实际可用条数输出，默认不扩到 4 条以上。

## 3. 主次关系与链接规则

- `feishu_full_doc` 是主交付锚点，也是发布成功与否的首要判断对象。
- `feishu_curated_card` 顶部必须放 `feishu_full_doc` 的链接。
- `publish result.reference` 默认指向 `feishu_full_doc` 的链接或消息 ID。

## 4. 成功、失败与降级语义

- 三项默认交付物全部成功时，发布结果为完整成功，最终 `verdict` 可保持 `normal`。
- `feishu_full_doc` 失败时，主交付未成立，`publish result.status = failed`，不得继续 `archive-report`。
- `feishu_full_doc` 成功但 `feishu_curated_card` 或 `feishu_native_audio` 任一失败时，主交付仍成立，`publish result.status` 可保持 `succeeded`，但最终 `verdict` 必须为 `degraded`。
- 上述降级场景下，可以继续 `archive-report`，因为主交付文档已经成立；失败项必须写入 `deliverables` 或 `error_summary`。

## 5. 建议的 `deliverables` 明细结构

```json
{
  "deliverables": {
    "feishu_full_doc": {
      "status": "succeeded",
      "reference": "https://feishu.example.com/doc/123"
    },
    "feishu_curated_card": {
      "status": "failed",
      "error_summary": "card render timeout"
    },
    "feishu_native_audio": {
      "status": "succeeded",
      "reference": "audio-file-token"
    }
  }
}
```
