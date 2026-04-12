# daily-report-master-agent

这是 Daily Report Master Agent v0 的最小实现仓库。

- 第一阶段宿主是 Hermes cronjob
- 主链路固定为 `collect -> assess -> build-report -> verdict -> publish -> archive`
- `build-report` 对主 agent 只暴露一个最终 artifact
- 当前仓库只落 contracts、agent、skills、templates、helpers、fixtures 的最小闭环

## 从现成 signals 生成验证输入

当真实 `signals-engine` 结果已经存在时，可以直接用 helpers 生成 `collect result` 和 `selected_items`，再走后续验证。

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python helpers/build_collect_result_from_signals.py \
  --signals-root ~/.daily-lane-data/signals \
  --report-date 2026-04-12 \
  --lanes x-feed x-following product-hunt-watch polymarket-watch \
  --output /tmp/collect-result.json

UV_CACHE_DIR=/tmp/uv-cache uv run python helpers/build_selected_items_from_signals.py \
  --signals-root ~/.daily-lane-data/signals \
  --report-date 2026-04-12 \
  --lanes x-feed x-following product-hunt-watch polymarket-watch \
  --output /tmp/selected-items.json

UV_CACHE_DIR=/tmp/uv-cache uv run python helpers/build_validation_bundle.py \
  --collect-result /tmp/collect-result.json \
  --selected-items /tmp/selected-items.json \
  --output /tmp/validation-bundle.json
```

其中：

- `collect result` 对齐 `contracts/runtime-contracts.md`
- `selected_items` 对齐 `contracts/selected-items.md`
- `build_validation_bundle.py` 只做最小一致性验证，不是 orchestrator
