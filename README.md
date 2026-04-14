# daily-report-master-agent

- 当前 authority 仓库：`daily-report-master-agent`
- 当前唯一主入口：`main-prompt.md`（cron runtime 使用的主 prompt 源文件）
- 第一阶段宿主：Hermes cronjob
- 主链路固定为 `collect -> assess -> build-report -> verdict -> publish -> archive`
- `build-report` 对主 agent 只暴露一个最终 artifact
- 当前仓库保存：主 prompt 源、Hermes skill 源、contracts、templates、helpers、fixtures、安装脚本

## 安装到 Hermes runtime

```bash
cd ~/workspace/daily-report-master-agent
./install.sh
./verify-install.sh
```

安装脚本会：

- 同步 `main-prompt.md` 到 Hermes runtime
- 同步 `config/runtime.yaml` 到 Hermes runtime
- 把 `hermes-skills/productivity/*` 安装到 `~/.hermes/skills/productivity/`
- 创建或更新 `daily-report-master-0600` cron job

校验脚本会验证：

- repo prompt 与 Hermes runtime prompt 一致
- daily report skills 已安装
- `daily-report-master-0600` cron 存在且 prompt 来自当前主 prompt

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
