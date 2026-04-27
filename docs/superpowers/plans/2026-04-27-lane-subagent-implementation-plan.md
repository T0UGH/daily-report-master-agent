# Lane Subagent Daily Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `daily-report-master-agent` 从“master 直接渲染所有栏目”逐步改成“master 调度 lane worker/subagent，收标准 lane artifacts，统一校验、合并、发布”的主日报内部架构，并优先落地 `github-ai-projects` lane。

**Architecture:** 不拆第二套系统；`run_daily_report_flow.py` 仍是唯一主入口。新增 lane input/output contracts、worker runner、artifact validator、report assembler adapter；第一阶段先用 deterministic/local worker 跑通 contract，第二阶段再把 `github-ai-projects` 接入 agent-style worker，第三阶段按 lane 迁移 X/HN/Claude Code 等栏目。Contract 字段以 `docs/2026-04-27-lane-subagent-design.md` 为准：input 必须包含 `timezone/lane_title/target_item_count/min_item_count/signals/recent_history/cross_lane_context/style_contract`；output 必须包含 `markdown/validation`，status 使用 `ok/empty/degraded/blocked`。

**Tech Stack:** Python 3、pytest、YAML runtime config、JSON artifacts、现有 `signals_adapter.py` / `run_daily_report_flow.py` / `validate_report_output_contract.py`、可选后续 subagent CLI/Claude SDK wrapper。

---

## 0. 现状和边界

### 0.1 设计依据

本计划实现 `docs/2026-04-27-lane-subagent-design.md`，核心边界必须保持：

- 主日报系统仍然唯一；不恢复一套外部 `agent-cron` 日报旁路。
- GitHub Trending / GitHub AI Projects 仍然属于主日报系统。
- lane worker/subagent 只产出标准 artifact；不自行发飞书、不自行归档、不自行决定日报是否成功。
- master 负责调度、validation、合并、final output contract、发布、归档、ops notice。
- 第一阶段优先做 vertical slice：`github-ai-projects` lane。

### 0.2 当前代码事实

当前主链路在：

- `helpers/run_daily_report_flow.py`
  - `main()` 负责 collect -> `build_collect_result()` -> `build_selected_items()` -> `build_report_artifact()` -> final validation -> publish/archive。
  - runtime artifacts 当前包括 `collect-result.json`、`selected-items.json`、`validation-bundle.json`、`report-artifact.json`、`report.md`、`run-summary.json`。
- `helpers/signals_adapter.py`
  - `build_report_artifact()` 当前直接从 collect/selected items 构造完整 report markdown。
  - `build_render_items_by_lane()` / `render_body_section()` / `render_source_section()` 是当前 renderer 关键路径。
- `config/runtime.yaml`
  - `reader_facing.fixed_section_order` 当前包含 `github-trending-weekly`。
- `tests/test_run_daily_report_flow.py`
  - 已有 flow-level 测试，可以加 master 调度和 artifact 写入测试。
- `tests/test_signals_adapter.py`
  - 已有 report artifact/rendering 测试，可以加 assembler 兼容测试。

---

## 1. File Structure

### 1.1 新增文件

- Create: `helpers/lane_contracts.py`
  - 定义 lane input/output artifact schema 的轻量校验函数。
  - 必须对齐 design doc 的 common fields；不要自创缩水 schema。
  - 不引入重型 schema 依赖，先用纯 Python dict validation，避免 YAGNI。

- Create: `helpers/lane_workers.py`
  - 定义 worker registry 和 runner。
  - 第一阶段只实现 deterministic local worker：从当前 `selected_items["selected_items"]` 和现有 `build_render_items_by_lane()` 生成 lane output artifact。
  - 后续 subagent worker 只需实现同一接口。

- Create: `helpers/lane_report_assembler.py`
  - 从 lane output artifacts 合并最终正文 sections 和 source sections。
  - Source markdown 要复用现有格式 `- title — url`，不要随意改成新的链接格式。
  - 保留现有 `REPORT_TEMPLATE_PATH`、`FIXED_SECTION_TITLES`、final report contract。

- Create: `tests/test_lane_contracts.py`
  - 单测 lane input/output contract。

- Create: `tests/test_lane_workers.py`
  - 单测 worker runner、artifact 写入、failure/degraded semantics。

- Create: `tests/test_lane_report_assembler.py`
  - 单测从 lane outputs 合并 report artifact，确保 section order/source links 不丢。

- Create: `helpers/github_ai_projects_worker.py`
  - 第二阶段新增。实现 `github-ai-projects` deterministic worker：聚合 GitHub Trending + repo mentions + existing memory-like summary artifacts。
  - 先不接真实 LLM；先把 contract 和主链路跑通。

### 1.2 修改文件

- Modify: `helpers/run_daily_report_flow.py`
  - 增加可配置的 lane worker 模式。
  - 写入 `lane-inputs/*.json`、`lane-outputs/*.json`、`lane-logs/*.md`。
  - master 使用 lane outputs assemble final report。
  - 保留 fallback 到旧 `build_report_artifact()`，降低迁移风险。

- Modify: `helpers/signals_adapter.py`
  - 抽出或复用现有 lane render item builder，供 local worker 使用。
  - 尽量不大拆文件；只加薄 adapter，避免重构过大。

- Modify: `helpers/validate_report_output_contract.py`
  - 如有必要，增加 final report 对 `github-ai-projects` section 的禁用模板词检查。

- Modify: `config/runtime.yaml`
  - 增加 `lane_workers.enabled`、`lane_workers.mode`、`lane_workers.enabled_lanes`。
  - 第一阶段默认关闭或只在测试 config 开启；完成验证后再打开 `github-ai-projects`。

- Modify: `docs/2026-04-27-lane-subagent-design.md`
  - 在 implementation section 链接本计划。

- Modify: `docs/report-feedback-ledger.md`
  - 记录本次架构落地进展、验证命令、commit。

---

## 2. Migration Strategy

### Phase A: Contract + no-op local worker vertical slice

先不引入真实 subagent。把现有 renderer 包装成 lane worker artifact：

```text
selected items -> local lane worker -> lane-output artifact -> assembler -> report.md
```

验收：开启 worker mode 后，对同一 fixture 输入，最终 `artifact["body_markdown"]` 与旧路径等价或至少通过现有 output contract。

### Phase B: GitHub AI Projects lane worker

新增内部 lane：`github-ai-projects`。它覆盖 GitHub Trending，但不只等于 Trending。

输入来源：

- `github-trending-weekly` selected items
- cross-lane repo mentions from X/HN/Reddit/Product Hunt selected items
- recent selected repo history, 7 days
- optional memory artifact path, first version可以只写 runtime markdown，不必马上写外部 memory repo

输出：

- `lane-outputs/github-ai-projects.json`
- `lane-memory/github-ai-projects.md`
- compatibility memory artifact `/Users/haha/workspace/memory/github-ai-projects/YYYY-MM-DD.md`（可先 gated by config，但本计划要实现写入函数和测试）
- final report section: `## GitHub AI 项目`

### Phase C: Incremental lane migration

按风险排序迁移：

1. `github-ai-projects`
2. `hacker-news-watch` / `hacker-news-search-watch`
3. `x-feed` / `x-following`
4. `claude-code-watch` / `codex-watch` / `openclaw-watch`
5. 其他低风险 lane

每迁移一个 lane 都必须有：contract test、worker test、real-date smoke、final report contract。

---

## 3. Tasks

### Task 1: Add lane artifact contracts

**Files:**
- Create: `helpers/lane_contracts.py`
- Create: `tests/test_lane_contracts.py`

- [ ] **Step 1: Write failing tests for valid lane input/output**

Add `tests/test_lane_contracts.py`:

```python
from __future__ import annotations

import pytest

from helpers.lane_contracts import (
    LaneContractError,
    validate_lane_input_artifact,
    validate_lane_output_artifact,
)


def test_validate_lane_input_artifact_accepts_minimal_valid_payload() -> None:
    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub AI 项目",
        "target_item_count": 5,
        "min_item_count": 1,
        "signals": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "url": "https://github.com/owner/name",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/trending"],
                "raw": {"stars": 1234},
            }
        ],
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": ["采集文本"]},
    }

    validate_lane_input_artifact(payload)


def test_validate_lane_output_artifact_accepts_reader_section_and_sources() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "status": "ok",
        "section_title": "GitHub AI 项目",
        "markdown": "## GitHub AI 项目\n\n- owner/name 做了一个 agent 调度工具。 https://github.com/owner/name",
        "items": [
            {
                "id": "repo:owner/name",
                "title": "owner/name",
                "url": "https://github.com/owner/name",
                "summary": "做 agent 调度。",
                "why_today": "进入 trending 且被 X 提到。",
                "source_urls": ["https://github.com/owner/name"],
            }
        ],
        "sources": [{"label": "owner/name", "url": "https://github.com/owner/name"}],
        "quality": {"item_count": 1, "warnings": []},
        "validation": {"status": "passed", "errors": []},
    }

    validate_lane_output_artifact(payload)
```

- [ ] **Step 2: Write failing tests for invalid payloads**

Append:

```python
def test_validate_lane_output_artifact_rejects_freeform_missing_schema() -> None:
    with pytest.raises(LaneContractError, match="schema_version"):
        validate_lane_output_artifact({"lane": "github-ai-projects", "markdown": "hello"})


def test_validate_lane_output_artifact_rejects_unknown_status() -> None:
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "status": "maybe",
        "section_title": "GitHub AI 项目",
        "markdown": "## GitHub AI 项目\n\n- item",
        "items": [],
        "sources": [],
        "quality": {"item_count": 0, "warnings": []},
        "validation": {"status": "failed", "errors": []},
    }
    with pytest.raises(LaneContractError, match="status"):
        validate_lane_output_artifact(payload)
```

- [ ] **Step 3: Run tests and verify failure**

Run:

```bash
python3 -m pytest -q tests/test_lane_contracts.py
```

Expected: FAIL with `ModuleNotFoundError: No module named 'helpers.lane_contracts'`.

- [ ] **Step 4: Implement minimal contract validators**

Create `helpers/lane_contracts.py`:

```python
from __future__ import annotations

from typing import Any


class LaneContractError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LaneContractError(message)


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    _require(isinstance(value, str) and value.strip(), f"{key} must be non-empty string")
    return value


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    _require(isinstance(value, list), f"{key} must be list")
    return value


def validate_lane_input_artifact(payload: Any) -> None:
    _require(isinstance(payload, dict), "lane input must be object")
    _require(payload.get("artifact_type") == "lane_input", "artifact_type must be lane_input")
    _require(payload.get("schema_version") == 1, "schema_version must be 1")
    _require_str(payload, "report_date")
    _require_str(payload, "lane")
    for key in ["timezone", "lane_title", "target_item_count", "min_item_count", "signals", "recent_history", "cross_lane_context", "style_contract"]:
        _require(key in payload, f"{key} is required")
    signals = _require_list(payload, "signals")
    _require(isinstance(payload.get("recent_history"), dict), "recent_history must be object")
    _require(isinstance(payload.get("cross_lane_context"), dict), "cross_lane_context must be object")
    _require(isinstance(payload.get("style_contract"), dict), "style_contract must be object")
    for index, item in enumerate(signals):
        _require(isinstance(item, dict), f"items[{index}] must be object")
        _require_str(item, "id")
        _require_str(item, "title")
        _require_str(item, "url")
        _require_list(item, "source_urls")


def validate_lane_output_artifact(payload: Any) -> None:
    _require(isinstance(payload, dict), "lane output must be object")
    _require(payload.get("artifact_type") == "lane_output", "artifact_type must be lane_output")
    _require(payload.get("schema_version") == 1, "schema_version must be 1")
    _require_str(payload, "report_date")
    _require_str(payload, "lane")
    status = _require_str(payload, "status")
    _require(status in {"ok", "empty", "degraded", "blocked"}, "status must be ok, empty, degraded, or blocked")
    _require_str(payload, "section_title")
    _require_str(payload, "markdown")
    _require(isinstance(payload.get("validation"), dict), "validation must be object")
    items = _require_list(payload, "items")
    sources = _require_list(payload, "sources")
    _require(isinstance(payload.get("quality"), dict), "quality must be object")
    for index, item in enumerate(items):
        _require(isinstance(item, dict), f"items[{index}] must be object")
        _require_str(item, "id")
        _require_str(item, "title")
        _require_str(item, "url")
        _require_list(item, "source_urls")
    for index, source in enumerate(sources):
        _require(isinstance(source, dict), f"sources[{index}] must be object")
        _require_str(source, "label")
        _require_str(source, "url")
```

- [ ] **Step 5: Run tests and commit**

Run:

```bash
python3 -m pytest -q tests/test_lane_contracts.py
```

Expected: PASS.

Commit:

```bash
git add helpers/lane_contracts.py tests/test_lane_contracts.py
git commit -m "feat: add lane artifact contracts"
```

---

### Task 2: Add local lane worker runner and artifact writing

Important current API facts:

- `selected_items` from the real builder is flat at `selected_items["selected_items"]`, not nested under `lanes[].items`.
- `normalize_render_item(item=..., useful_item_count=..., report_date=...)` returns `ReportRenderItem(lane,title,excerpt,source_url,link_label,source_title,sort_key)`.
- Prefer calling `build_render_items_by_lane(...)` rather than constructing `ReportRenderItem` manually.


**Files:**
- Create: `helpers/lane_workers.py`
- Create: `tests/test_lane_workers.py`
- Modify: `helpers/signals_adapter.py`

- [ ] **Step 1: Write failing worker test for selected items -> lane output**

Create `tests/test_lane_workers.py`:

```python
from __future__ import annotations

from helpers.lane_contracts import validate_lane_output_artifact
from helpers.lane_workers import build_local_lane_output


def test_build_local_lane_output_wraps_existing_render_items() -> None:
    selected_items = {
        "report_date": "2026-04-27",
        "selected_items": [
                    {
                        "id": "github-trending-weekly:1",
                        "lane": "github-trending-weekly",
                        "title": "owner/project",
                        "summary": "一个 agent workflow 工具，支持本地任务编排。",
                        "source_url": "https://github.com/owner/project",
                        "url": "https://github.com/owner/project",
                    }
        ],
        "summary": {"selected_item_count": 1, "lane_counts": []},
    }

    output = build_local_lane_output(
        report_date="2026-04-27",
        lane_name="github-trending-weekly",
        selected_items=selected_items,
    )

    validate_lane_output_artifact(output)
    assert output["lane"] == "github-trending-weekly"
    assert output["status"] == "ok"
    assert output["section_title"] == "GitHub 趋势项目"
    assert "owner/project" in output["markdown"]
    assert output["quality"]["item_count"] == 1
```

- [ ] **Step 2: Run and verify failure**

```bash
python3 -m pytest -q tests/test_lane_workers.py
```

Expected: FAIL with missing `helpers.lane_workers`.

- [ ] **Step 3: Add thin helper in `signals_adapter.py` if needed**

If current functions are not conveniently reusable, add a small exported function near existing render helpers:

```python
def build_render_items_for_lane(
    *,
    collect_result: dict[str, Any] | None,
    selected_items: dict[str, Any],
    lane_name: str,
) -> list[ReportRenderItem]:
    lanes = [] if collect_result is None else collect_result.get("lanes", [])
    return build_render_items_by_lane(
        collect_result=collect_result or {"report_date": selected_items["report_date"], "lanes": lanes, "summary": {"useful_item_count": 1}},
        selected_items=selected_items,
        renderable_lanes=[lane_name],
    ).get(lane_name, [])
```

Important: keep this helper minimal. Do not restructure `signals_adapter.py` in this task.

- [ ] **Step 4: Implement `helpers/lane_workers.py`**

Create:

```python
from __future__ import annotations

from typing import Any

from helpers.lane_contracts import validate_lane_output_artifact
from helpers.signals_adapter import FIXED_SECTION_TITLES, build_render_items_by_lane, render_body_section


def _selected_lane_items(selected_items: dict[str, Any], lane_name: str) -> list[dict[str, Any]]:
    return [item for item in selected_items.get("selected_items", []) if isinstance(item, dict) and item.get("lane") == lane_name]


def build_local_lane_output(
    *,
    report_date: str,
    lane_name: str,
    selected_items: dict[str, Any],
) -> dict[str, Any]:
    section_title = FIXED_SECTION_TITLES[lane_name]
    raw_items = _selected_lane_items(selected_items, lane_name)
    collect_result = {"report_date": report_date, "source": "lane-worker", "lanes": [{"name": lane_name, "status": "ok", "useful_item_count": len(raw_items)}], "summary": {"useful_item_count": len(raw_items)}}
    selected_payload = {"report_date": report_date, "selected_items": raw_items, "summary": selected_items.get("summary", {})}
    render_items = build_render_items_by_lane(collect_result=collect_result, selected_items=selected_payload, renderable_lanes=[lane_name]).get(lane_name, [])
    render_items = [item for item in render_items if item is not None]
    if render_items:
        body_markdown = render_body_section(section_title, render_items)
        status = "ok"
    else:
        body_markdown = f"## {section_title}\n\n- 无"
        status = "empty"
    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": report_date,
        "lane": lane_name,
        "status": status,
        "section_title": section_title,
        "markdown": body_markdown,
        "items": [
            {
                "id": f"{item.lane}:{item.source_url or item.title}",
                "title": item.title,
                "url": item.source_url,
                "summary": item.excerpt,
                "why_today": item.excerpt,
                "source_urls": [item.source_url] if item.source_url else [],
            }
            for item in render_items
        ],
        "sources": [
            {"label": item.source_title or item.title, "url": item.source_url}
            for item in render_items
            if item.source_url
        ],
        "quality": {"item_count": len(render_items), "warnings": [] if render_items else ["no_renderable_items"]},
        "validation": {"status": "passed" if render_items else "empty", "errors": []},
    }
    validate_lane_output_artifact(output)
    return output
```

If `ReportRenderItem` fields differ, inspect the dataclass in `signals_adapter.py` and adjust names exactly.

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest -q tests/test_lane_contracts.py tests/test_lane_workers.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add helpers/lane_workers.py helpers/signals_adapter.py tests/test_lane_workers.py
git commit -m "feat: add local lane worker runner"
```

---

### Task 3: Add lane output assembler

**Files:**
- Create: `helpers/lane_report_assembler.py`
- Create: `tests/test_lane_report_assembler.py`

- [ ] **Step 1: Write failing assembler test**

Create `tests/test_lane_report_assembler.py`:

```python
from __future__ import annotations

from helpers.lane_report_assembler import build_report_artifact_from_lane_outputs


def test_build_report_artifact_from_lane_outputs_preserves_order_and_sources() -> None:
    lane_outputs = [
        {
            "artifact_type": "lane_output",
            "schema_version": 1,
            "report_date": "2026-04-27",
            "lane": "weather-watch",
            "status": "ok",
            "section_title": "天气预报",
            "markdown": "## 天气预报\n\n- 北京：晴。",
            "items": [{"id": "weather:beijing", "title": "北京", "url": "https://weather.example", "summary": "晴", "why_today": "天气置顶", "source_urls": ["https://weather.example"]}],
            "sources": [{"label": "北京天气", "url": "https://weather.example"}],
            "quality": {"item_count": 1, "warnings": []},
        "validation": {"status": "passed", "errors": []},
        },
        {
            "artifact_type": "lane_output",
            "schema_version": 1,
            "report_date": "2026-04-27",
            "lane": "github-ai-projects",
            "status": "ok",
            "section_title": "GitHub AI 项目",
            "markdown": "## GitHub AI 项目\n\n- owner/name：agent workflow 工具。",
            "items": [{"id": "repo:owner/name", "title": "owner/name", "url": "https://github.com/owner/name", "summary": "agent workflow 工具", "why_today": "trending", "source_urls": ["https://github.com/owner/name"]}],
            "sources": [{"label": "owner/name", "url": "https://github.com/owner/name"}],
            "quality": {"item_count": 1, "warnings": []},
        "validation": {"status": "passed", "errors": []},
        },
    ]

    artifact = build_report_artifact_from_lane_outputs(
        report_date="2026-04-27",
        lane_outputs=lane_outputs,
        lane_order=["weather-watch", "github-ai-projects"],
    )

    markdown = artifact["body_markdown"]
    assert markdown.index("## 天气预报") < markdown.index("## GitHub AI 项目")
    assert "## 来源" in markdown
    assert "https://github.com/owner/name" in markdown
    assert artifact["source_lanes"] == ["weather-watch", "github-ai-projects"]
```

- [ ] **Step 2: Run and verify failure**

```bash
python3 -m pytest -q tests/test_lane_report_assembler.py
```

Expected: FAIL with missing module.

- [ ] **Step 3: Implement assembler**

Create `helpers/lane_report_assembler.py`:

```python
from __future__ import annotations

from typing import Any

from helpers.lane_contracts import validate_lane_output_artifact
from helpers.signals_adapter import REPORT_TEMPLATE_PATH, REPORT_TITLE_TEMPLATE


def _source_markdown(section_title: str, sources: list[dict[str, Any]]) -> str:
    lines = [f"### {section_title}"]
    for source in sources:
        label = source.get("label") or source.get("url")
        url = source.get("url")
        if url:
            lines.append(f"- {label} — {url}")
    return "\n".join(lines)


def build_report_artifact_from_lane_outputs(
    *,
    report_date: str,
    lane_outputs: list[dict[str, Any]],
    lane_order: list[str],
) -> dict[str, Any]:
    by_lane = {}
    for output in lane_outputs:
        validate_lane_output_artifact(output)
        by_lane[output["lane"]] = output

    body_sections: list[str] = []
    source_sections: list[str] = []
    source_lanes: list[str] = []
    useful_item_count = 0

    for lane in lane_order:
        output = by_lane.get(lane)
        if not output or output.get("status") in {"empty", "blocked"}:
            continue
        body_sections.append(output["markdown"])
        item_count = output.get("quality", {}).get("item_count", 0)
        useful_item_count += item_count if isinstance(item_count, int) else len(output.get("items", []))
        sources = output.get("sources") or []
        if sources:
            source_lanes.append(lane)
            source_sections.append(_source_markdown(output["section_title"], sources))

    if not body_sections:
        raise ValueError("没有可渲染的 lane output")

    template = REPORT_TEMPLATE_PATH.read_text(encoding="utf-8")
    body_markdown = (
        template.replace("{{report_date}}", report_date)
        .replace("{{body_markdown}}", "\n\n".join(body_sections))
        .replace("{{sources_markdown}}", "\n\n".join(source_sections))
    )
    return {
        "artifact_type": "final_report",
        "report_date": report_date,
        "title": REPORT_TITLE_TEMPLATE.format(report_date=report_date),
        "summary": f"今日共整理 {useful_item_count} 条有用内容。",
        "body_markdown": body_markdown,
        "useful_item_count": useful_item_count,
        "source_lanes": source_lanes,
        "lane_output_count": len(by_lane),
    }
```

- [ ] **Step 4: Run tests and commit**

```bash
python3 -m pytest -q tests/test_lane_report_assembler.py tests/test_lane_contracts.py
```

Expected: PASS.

Commit:

```bash
git add helpers/lane_report_assembler.py tests/test_lane_report_assembler.py
git commit -m "feat: assemble reports from lane outputs"
```

---

### Task 4: Wire worker mode into master flow behind config flag

**Files:**
- Modify: `config/runtime.yaml`
- Modify: `helpers/runtime_config.py`
- Modify: `helpers/run_daily_report_flow.py`
- Modify: `tests/test_run_daily_report_flow.py`

- [ ] **Step 1: Add failing flow test for lane artifacts**

In `tests/test_run_daily_report_flow.py`, add a test near existing `main()` tests:

```python
def test_main_worker_mode_writes_lane_inputs_and_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "runtime.yaml"
    signals_root = tmp_path / "signals"
    runtime_root = tmp_path / "runtime"
    signals_root.mkdir(parents=True)
    config_path.write_text(
        "version: 1\n"
        f"repo_root: {tmp_path}\n"
        "paths:\n"
        f"  signals_root: {signals_root}\n"
        f"  runtime_root: {runtime_root}\n"
        "selection:\n"
        "  per_lane_limits:\n"
        "    github-trending-weekly: 10\n"
        "reader_facing:\n"
        "  fixed_section_order:\n"
        "    - github-trending-weekly\n"
        "runtime:\n"
        "  timezone: Asia/Shanghai\n"
        "lane_workers:\n"
        "  enabled: true\n"
        "  mode: local\n"
        "  enabled_lanes:\n"
        "    - github-trending-weekly\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(flow, "parse_args", lambda: argparse.Namespace(
        report_date="2026-04-27",
        config=config_path,
        skip_collect=True,
        publish=False,
        title_suffix="",
        verbose=False,
    ))
    monkeypatch.setattr(flow, "build_collect_result", lambda **_: {
        "report_date": "2026-04-27",
        "source": "test",
        "lanes": [{"name": "github-trending-weekly", "useful_item_count": 1}],
        "summary": {"useful_item_count": 1},
    })
    monkeypatch.setattr(flow, "build_selected_items", lambda **_: {
        "report_date": "2026-04-27",
        "selected_items": [{"id": "repo:owner/name", "lane": "github-trending-weekly", "title": "owner/name", "summary": "agent workflow 工具", "source_url": "https://github.com/owner/name"}],
        "summary": {"selected_item_count": 1, "lane_counts": [{"lane": "github-trending-weekly", "selected_item_count": 1}]},
    })
    monkeypatch.setattr(flow, "validate_report_markdown", lambda *_args, **_kwargs: None)

    assert flow.main() == 0

    run_dir = runtime_root / "2026-04-27"
    assert (run_dir / "lane-inputs" / "github-trending-weekly.json").is_file()
    assert (run_dir / "lane-outputs" / "github-trending-weekly.json").is_file()
    summary = json.loads((run_dir / "run-summary.json").read_text(encoding="utf-8"))
    assert summary["lane_workers"]["enabled"] is True
    assert summary["lane_workers"]["outputs"]["github-trending-weekly"]["status"] == "ok"
```

- [ ] **Step 2: Run test and verify failure**

```bash
python3 -m pytest -q tests/test_run_daily_report_flow.py -k worker_mode_writes_lane_inputs_and_outputs
```

Expected: FAIL because worker mode is not wired.

- [ ] **Step 3: Add runtime config resolver**

Modify `helpers/runtime_config.py`:

```python
def resolve_lane_worker_config(config: dict[str, Any]) -> dict[str, Any]:
    raw = config.get("lane_workers") or {}
    enabled = bool(raw.get("enabled", False))
    mode = raw.get("mode", "local")
    if mode not in {"local", "subagent"}:
        raise ValueError("lane_workers.mode must be local or subagent")
    enabled_lanes = raw.get("enabled_lanes") or []
    if not isinstance(enabled_lanes, list) or not all(isinstance(lane, str) for lane in enabled_lanes):
        raise ValueError("lane_workers.enabled_lanes must be list[str]")
    return {"enabled": enabled, "mode": mode, "enabled_lanes": enabled_lanes}
```

- [ ] **Step 4: Add config defaults**

Modify `config/runtime.yaml`:

```yaml
lane_workers:
  enabled: false
  mode: local
  enabled_lanes: []
```

Keep default disabled until the vertical slice passes real-date smoke.


Mandatory partial-mode rule for this task: before assembling from `lane_outputs`, check `set(enabled_lanes) == set(lane_order)`. If not, raise `ValueError` and add a test for that error. Do not merge a subset and do not silently drop lanes.

- [ ] **Step 5: Wire flow**

Modify imports in `helpers/run_daily_report_flow.py`:

```python
from helpers.lane_contracts import validate_lane_input_artifact, validate_lane_output_artifact
from helpers.lane_report_assembler import build_report_artifact_from_lane_outputs
from helpers.lane_workers import build_local_lane_output
from helpers.runtime_config import (..., resolve_lane_worker_config)
```

Add helper functions near other runtime helpers:

```python
def build_lane_input_artifact(*, report_date: str, lane_name: str, selected_items: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or {}
    fixed_titles = FIXED_SECTION_TITLES
    target_count = resolve_lane_item_limits(config).get(lane_name, (config or {}).get("selection", {}).get("default_per_lane_limit", 10))
    candidate_lanes = {lane_name}
    if lane_name == "github-ai-projects":
        candidate_lanes = {"github-trending-weekly", "x-feed", "x-following", "reddit-watch", "hacker-news-watch", "hacker-news-search-watch", "product-hunt-watch"}
    signals = []
    for item in selected_items.get("selected_items", []):
        if not isinstance(item, dict) or item.get("lane") not in candidate_lanes:
            continue
        url = item.get("source_url") or item.get("url") or ""
        signals.append({
            "id": str(item.get("id") or item.get("title") or url),
            "title": str(item.get("title") or item.get("summary") or item.get("id") or "untitled"),
            "url": str(url),
            "source_lane": str(item.get("lane") or lane_name),
            "source_urls": [str(url)] if url else [],
            "raw": item,
        })
    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": report_date,
        "lane": lane_name,
        "timezone": (config or {}).get("runtime", {}).get("timezone", "Asia/Shanghai"),
        "lane_title": fixed_titles[lane_name],
        "target_item_count": target_count,
        "min_item_count": 1,
        "signals": signals,
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {"github_search_queries": []} if lane_name == "github-ai-projects" else {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": ["采集文本", "保守看", "摘要里能看到"]},
    }
    validate_lane_input_artifact(payload)
    return payload
```

In `main()`, after dumping selected items and before final artifact creation:

```python
lane_worker_config = resolve_lane_worker_config(config)
summary["lane_workers"] = {"enabled": lane_worker_config["enabled"], "mode": lane_worker_config["mode"], "outputs": {}}

lane_outputs = []
if lane_worker_config["enabled"]:
    enabled_lanes = set(lane_worker_config["enabled_lanes"])
    lane_inputs_dir = run_dir / "lane-inputs"
    lane_outputs_dir = run_dir / "lane-outputs"
    lane_inputs_dir.mkdir(parents=True, exist_ok=True)
    lane_outputs_dir.mkdir(parents=True, exist_ok=True)
    for lane_name in lane_order:
        if lane_name not in enabled_lanes:
            continue
        lane_input = build_lane_input_artifact(report_date=args.report_date, lane_name=lane_name, selected_items=selected_items, config=config)
        dump_json(lane_input, lane_inputs_dir / f"{lane_name}.json")
        if lane_worker_config["mode"] != "local":
            raise ValueError("subagent lane worker mode is not implemented yet")
        lane_output = build_local_lane_output(report_date=args.report_date, lane_name=lane_name, selected_items=selected_items)
        validate_lane_output_artifact(lane_output)
        dump_json(lane_output, lane_outputs_dir / f"{lane_name}.json")
        lane_outputs.append(lane_output)
        summary["lane_workers"]["outputs"][lane_name] = {
            "status": lane_output["status"],
            "item_count": lane_output.get("quality", {}).get("item_count"),
            "output_path": str(lane_outputs_dir / f"{lane_name}.json"),
        }
```

Then choose artifact path:

```python
if lane_worker_config["enabled"]:
    missing = [lane for lane in lane_order if lane not in set(lane_worker_config["enabled_lanes"])]
    if missing:
        raise ValueError(f"lane worker mode requires all fixed_section_order lanes; missing: {missing}")
    artifact = build_report_artifact_from_lane_outputs(
        report_date=args.report_date,
        lane_outputs=lane_outputs,
        lane_order=lane_order,
    )
else:
    artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
```

Important: this first wiring only uses worker outputs when worker mode is enabled. Because enabled lanes may be subset, either require all renderable lanes in tests or explicitly document partial mode. Prefer first version: if enabled, enabled_lanes must include all lanes in `fixed_section_order` for that run. Add validation if necessary.

- [ ] **Step 6: Run targeted test**

```bash
python3 -m pytest -q tests/test_run_daily_report_flow.py -k worker_mode_writes_lane_inputs_and_outputs
```

Expected: PASS.

- [ ] **Step 7: Run related tests and commit**

```bash
python3 -m pytest -q tests/test_lane_contracts.py tests/test_lane_workers.py tests/test_lane_report_assembler.py tests/test_run_daily_report_flow.py -k 'worker_mode or run_daily_report_flow'
```

Expected: PASS. If `-k run_daily_report_flow` is too broad or selects none, run full `tests/test_run_daily_report_flow.py`.

Commit:

```bash
git add config/runtime.yaml helpers/runtime_config.py helpers/run_daily_report_flow.py tests/test_run_daily_report_flow.py
git commit -m "feat: wire lane worker mode into daily report flow"
```

---

### Task 5: Add `github-ai-projects` lane to config and titles

**Files:**
- Modify: `config/runtime.yaml`
- Modify: `helpers/validate_report_output_contract.py`
- Modify: `helpers/signals_adapter.py`
- Modify: `tests/test_signals_adapter.py`

- [ ] **Step 1: Write failing title/order test**

In `tests/test_signals_adapter.py`, add a focused test:

```python
def test_github_ai_projects_lane_has_reader_facing_section_title() -> None:
    assert FIXED_SECTION_TITLES["github-ai-projects"] == "GitHub AI 项目"
```

If `FIXED_SECTION_TITLES` is imported from `helpers.validate_report_output_contract`, place the test in the file where similar constants are already tested.

- [ ] **Step 2: Run and verify failure**

```bash
python3 -m pytest -q tests/test_signals_adapter.py -k github_ai_projects_lane_has_reader_facing_section_title
```

Expected: FAIL with KeyError or missing constant.

- [ ] **Step 3: Add section title/order**

Modify `helpers/validate_report_output_contract.py`:

- Add `github-ai-projects` to fixed section titles as `GitHub AI 项目`.
- Keep `github-trending-weekly` for backward compatibility during migration.
- Decide final order in `config/runtime.yaml`: replace or place near current GitHub section:

```yaml
reader_facing:
  fixed_section_order:
    ...
    - github-ai-projects
    - github-trending-weekly
    - product-hunt-watch
```

For first release, keep both lanes but only one should render in production to avoid duplicate GitHub sections. Use config to enable `github-ai-projects` only after worker is ready.

- [ ] **Step 4: Update adapter lane constants**

In `helpers/signals_adapter.py`, add `github-ai-projects` to lane-specific maps where `github-trending-weekly` appears:

- source fallback URL map
- source display names
- per-lane defaults
- section preferences if applicable
- render publishability lane set

Use `github-trending-weekly` behavior as baseline, but title is `GitHub AI 项目`.

- [ ] **Step 5: Run targeted tests and commit**

```bash
python3 -m pytest -q tests/test_signals_adapter.py -k 'github_ai_projects or github_trending'
python3 -m pytest -q tests/test_lane_workers.py tests/test_lane_report_assembler.py
```

Expected: PASS.

Commit:

```bash
git add config/runtime.yaml helpers/validate_report_output_contract.py helpers/signals_adapter.py tests/test_signals_adapter.py
git commit -m "feat: add github ai projects report lane"
```

---

### Task 6: Implement deterministic `github-ai-projects` worker

**Files:**
- Create: `helpers/github_ai_projects_worker.py`
- Modify: `helpers/lane_workers.py`
- Create/Modify: `tests/test_github_ai_projects_worker.py`

- [ ] **Step 1: Write failing worker test for repo aggregation**

Create `tests/test_github_ai_projects_worker.py`:

```python
from __future__ import annotations

from helpers.github_ai_projects_worker import build_github_ai_projects_output
from helpers.lane_contracts import validate_lane_output_artifact


def test_build_github_ai_projects_output_merges_trending_and_cross_lane_mentions() -> None:
    lane_input = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "signals": [
            {
                "id": "repo:owner/trending-agent",
                "title": "owner/trending-agent",
                "url": "https://github.com/owner/trending-agent",
                "source_lane": "github-trending-weekly",
                "source_urls": ["https://github.com/owner/trending-agent"],
                "raw": {"summary": "A local-first agent orchestration toolkit with MCP tools."},
            },
            {
                "id": "x:1",
                "title": "@dev 推荐 owner/trending-agent",
                "url": "https://x.com/dev/status/1",
                "source_lane": "x-following",
                "source_urls": ["https://x.com/dev/status/1"],
                "raw": {"summary": "@dev 说 owner/trending-agent 适合多 agent 并行任务。"},
            },
        ],
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub AI 项目",
        "target_item_count": 5,
        "min_item_count": 1,
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": ["采集文本"]},
    }

    output = build_github_ai_projects_output(lane_input)

    validate_lane_output_artifact(output)
    assert output["lane"] == "github-ai-projects"
    assert output["section_title"] == "GitHub AI 项目"
    assert output["quality"]["item_count"] == 1
    assert "owner/trending-agent" in output["markdown"]
    assert "多 agent" in output["markdown"] or "agent" in output["markdown"]
    assert len(output["sources"]) >= 2
```

- [ ] **Step 2: Run and verify failure**

```bash
python3 -m pytest -q tests/test_github_ai_projects_worker.py
```

Expected: FAIL missing module.

- [ ] **Step 3: Implement repository extraction and scoring**

Create `helpers/github_ai_projects_worker.py`:

```python
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from helpers.lane_contracts import validate_lane_input_artifact, validate_lane_output_artifact

REPO_RE = re.compile(r"(?:https://github\.com/)?([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")


def _extract_repo_ids(text: str) -> list[str]:
    repos = []
    for match in REPO_RE.finditer(text or ""):
        repo = match.group(1).strip(" .,)\n")
        if "/" in repo and not repo.lower().startswith(("github.com/", "http")):
            repos.append(repo)
    return repos


def _item_text(item: dict[str, Any]) -> str:
    raw = item.get("raw") if isinstance(item.get("raw"), dict) else {}
    parts = [item.get("title"), item.get("url"), raw.get("summary"), raw.get("title"), raw.get("source_snippet")]
    return "\n".join(str(part) for part in parts if part)


def build_github_ai_projects_output(lane_input: dict[str, Any]) -> dict[str, Any]:
    validate_lane_input_artifact(lane_input)
    report_date = lane_input["report_date"]
    recent_repo_ids = set(lane_input.get("recent_history", {}).get("repo_ids") or [])
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in lane_input["signals"]:
        for repo in _extract_repo_ids(_item_text(item)):
            if repo not in recent_repo_ids:
                grouped[repo].append(item)

    ranked = sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0].lower()))[:5]
    lines = ["## GitHub AI 项目"]
    output_items = []
    sources = []
    for repo, evidence_items in ranked:
        repo_url = f"https://github.com/{repo}"
        source_lanes = sorted({str(item.get("source_lane")) for item in evidence_items if item.get("source_lane")})
        why_today = "、".join(source_lanes) if source_lanes else "GitHub 信号"
        summary = f"{repo} 今天被 {why_today} 提到；按输入证据看，它和 AI agent / coding workflow 相关。"
        lines.append(f"- **{repo}**：{summary} {repo_url}")
        source_urls = []
        for item in evidence_items:
            for url in item.get("source_urls", []):
                if url and url not in source_urls:
                    source_urls.append(url)
                    sources.append({"label": repo, "url": url})
        if repo_url not in source_urls:
            source_urls.insert(0, repo_url)
            sources.insert(0, {"label": repo, "url": repo_url})
        output_items.append({
            "id": f"repo:{repo}",
            "title": repo,
            "url": repo_url,
            "summary": summary,
            "why_today": why_today,
            "source_urls": source_urls,
        })

    status = "ok" if output_items else "empty"
    if not output_items:
        lines.append("- 无")
    output = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": report_date,
        "lane": "github-ai-projects",
        "status": status,
        "section_title": "GitHub AI 项目",
        "markdown": "\n\n".join([lines[0], "\n".join(lines[1:])]),
        "items": output_items,
        "sources": sources,
        "quality": {"item_count": len(output_items), "warnings": [] if output_items else ["no_repo_candidates"]},
        "validation": {"status": "passed" if output_items else "empty", "errors": []},
    }
    validate_lane_output_artifact(output)
    return output
```

This is intentionally simple. Do not add live web search or LLM here yet.

- [ ] **Step 4: Register worker in `lane_workers.py`**

Add dispatcher:

```python
from helpers.github_ai_projects_worker import build_github_ai_projects_output


def build_lane_output(*, report_date: str, lane_name: str, selected_items: dict[str, Any], lane_input: dict[str, Any] | None = None) -> dict[str, Any]:
    if lane_name == "github-ai-projects":
        if lane_input is None:
            raise ValueError("github-ai-projects requires lane_input")
        return build_github_ai_projects_output(lane_input)
    return build_local_lane_output(report_date=report_date, lane_name=lane_name, selected_items=selected_items)
```

Update `run_daily_report_flow.py` to call `build_lane_output()` instead of `build_local_lane_output()`.

- [ ] **Step 5: Run tests and commit**

```bash
python3 -m pytest -q tests/test_github_ai_projects_worker.py tests/test_lane_workers.py tests/test_run_daily_report_flow.py -k 'worker_mode or github_ai_projects'
```

Expected: PASS.

Commit:

```bash
git add helpers/github_ai_projects_worker.py helpers/lane_workers.py helpers/run_daily_report_flow.py tests/test_github_ai_projects_worker.py
git commit -m "feat: add github ai projects lane worker"
```

---

### Task 7: Build `github-ai-projects` lane input from multiple sources

**Files:**
- Modify: `helpers/run_daily_report_flow.py`
- Modify: `tests/test_run_daily_report_flow.py`
- Modify: `helpers/github_ai_projects_worker.py` if needed

- [ ] **Step 1: Write failing test for cross-lane input composition**

Add to `tests/test_run_daily_report_flow.py`:

```python
def test_build_lane_input_artifact_for_github_ai_projects_includes_cross_lane_repo_mentions() -> None:
    selected_items = {
        "report_date": "2026-04-27",
        "selected_items": [
            {"id": "gh:1", "lane": "github-trending-weekly", "title": "owner/trending-agent", "source_url": "https://github.com/owner/trending-agent"},
            {"id": "x:1", "lane": "x-following", "title": "@dev", "summary": "推荐 owner/trending-agent 做 agent 编排", "source_url": "https://x.com/dev/status/1"},
            {"id": "ph:1", "lane": "product-hunt-watch", "title": "Another Tool", "summary": "没有 repo", "source_url": "https://producthunt.com/posts/tool"},
        ],
        "summary": {"selected_item_count": 3, "lane_counts": []},
    }

    payload = flow.build_lane_input_artifact(
        report_date="2026-04-27",
        lane_name="github-ai-projects",
        selected_items=selected_items,
    )

    source_lanes = {item["source_lane"] for item in payload["signals"]}
    assert "github-trending-weekly" in source_lanes
    assert "x-following" in source_lanes
    assert all(item["source_urls"] for item in payload["signals"])
```

- [ ] **Step 2: Run and verify failure**

```bash
python3 -m pytest -q tests/test_run_daily_report_flow.py -k cross_lane_repo_mentions
```

Expected: FAIL because generic builder only reads same lane.

- [ ] **Step 3: Implement special input composition**

Modify `build_lane_input_artifact()` in `helpers/run_daily_report_flow.py`:

- If `lane_name != "github-ai-projects"`, keep existing same-lane behavior.
- If `lane_name == "github-ai-projects"`, include items from:
  - `github-trending-weekly`
  - `x-feed`
  - `x-following`
  - `reddit-watch`
  - `hacker-news-watch`
  - `hacker-news-search-watch`
  - `product-hunt-watch`
- Only include items whose title/summary/source URL contains `github.com/owner/repo` or `owner/repo` pattern. Also include a placeholder `github_search_queries` list in `cross_lane_context`; actual live GitHub Search fetching is explicitly deferred to the next subagent-backed worker plan, not silently forgotten.
- Include `recent_history.repo_ids` by reading previous selected/runtime history if already available; if not, set empty list for now and add TODO comment.

- [ ] **Step 4: Run tests and commit**

```bash
python3 -m pytest -q tests/test_run_daily_report_flow.py -k 'cross_lane_repo_mentions or worker_mode_writes_lane_inputs_and_outputs'
python3 -m pytest -q tests/test_github_ai_projects_worker.py
```

Expected: PASS.

Commit:

```bash
git add helpers/run_daily_report_flow.py tests/test_run_daily_report_flow.py
git commit -m "feat: compose github ai project lane inputs"
```

---

### Task 8: Add runtime memory markdown side artifact for GitHub projects

**Files:**
- Modify: `helpers/github_ai_projects_worker.py`
- Modify: `helpers/run_daily_report_flow.py`
- Modify: `tests/test_github_ai_projects_worker.py`
- Modify: `tests/test_run_daily_report_flow.py`

- [ ] **Step 1: Write failing test for memory markdown**

Add to `tests/test_github_ai_projects_worker.py`:

```python
def test_build_github_ai_projects_output_includes_memory_markdown() -> None:
    lane_input = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-ai-projects",
        "signals": [{"id": "repo:owner/name", "title": "owner/name", "url": "https://github.com/owner/name", "source_lane": "github-trending-weekly", "source_urls": ["https://github.com/owner/name"], "raw": {"summary": "agent tool"}}],
        "timezone": "Asia/Shanghai",
        "lane_title": "GitHub AI 项目",
        "target_item_count": 5,
        "min_item_count": 1,
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {},
        "style_contract": {"language": "zh-CN", "forbidden_phrases": ["采集文本"]},
    }

    output = build_github_ai_projects_output(lane_input)

    assert output["side_artifacts"]["memory_markdown"].startswith("# GitHub AI 项目 2026-04-27")
    assert "owner/name" in output["side_artifacts"]["memory_markdown"]
```

- [ ] **Step 2: Run and verify failure**

```bash
python3 -m pytest -q tests/test_github_ai_projects_worker.py -k memory_markdown
```

Expected: FAIL missing `side_artifacts`.

- [ ] **Step 3: Implement memory markdown string**

In `build_github_ai_projects_output()` add:

```python
def _build_memory_markdown(report_date: str, items: list[dict[str, Any]]) -> str:
    lines = [f"# GitHub AI 项目 {report_date}", ""]
    for index, item in enumerate(items, start=1):
        lines.append(f"## {index}. {item['title']}")
        lines.append("")
        lines.append(f"- Repo: {item['url']}")
        lines.append(f"- Why today: {item['why_today']}")
        lines.append(f"- Summary: {item['summary']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
```

Set:

```python
"side_artifacts": {"memory_markdown": _build_memory_markdown(report_date, output_items)}
```

Update contract validator to allow optional `side_artifacts` object, not require it.

- [ ] **Step 4: Write flow test for side artifact file**

In `tests/test_run_daily_report_flow.py`, assert after worker mode:

```python
assert (run_dir / "lane-memory" / "github-ai-projects.md").is_file()
```

- [ ] **Step 5: Implement side artifact writing**

In `run_daily_report_flow.py`, after each lane output:

```python
side_artifacts = lane_output.get("side_artifacts") or {}
memory_markdown = side_artifacts.get("memory_markdown")
if isinstance(memory_markdown, str) and memory_markdown.strip():
    lane_memory_dir = run_dir / "lane-memory"
    lane_memory_dir.mkdir(parents=True, exist_ok=True)
    memory_path = lane_memory_dir / f"{lane_name}.md"
    memory_path.write_text(memory_markdown, encoding="utf-8")
    summary["lane_workers"]["outputs"][lane_name]["memory_path"] = str(memory_path)
```

- [ ] **Step 6: Write compatibility memory artifact when configured**

Add config key under `lane_workers.github_ai_projects.memory_repo_dir` defaulting to `/Users/haha/workspace/memory/github-ai-projects`. In `run_daily_report_flow.py`, when `lane_name == "github-ai-projects"` and `side_artifacts.memory_markdown` exists, also write `{report_date}.md` to that directory. Test with a temp directory; do not git commit/push the memory repo in this task.

- [ ] **Step 7: Run tests and commit**

```bash
python3 -m pytest -q tests/test_github_ai_projects_worker.py tests/test_run_daily_report_flow.py -k 'github_ai_projects or worker_mode'
```

Expected: PASS.

Commit:

```bash
git add helpers/github_ai_projects_worker.py helpers/lane_contracts.py helpers/run_daily_report_flow.py tests/test_github_ai_projects_worker.py tests/test_run_daily_report_flow.py
git commit -m "feat: write github project lane memory artifact"
```

---

### Task 9: Real-date smoke for 2026-04-27 with worker mode in test config

**Files:**
- Create: `config/runtime.lane-workers-smoke.yaml` or use temp config only
- Modify: `docs/report-feedback-ledger.md`

- [ ] **Step 1: Create temporary smoke config**

Prefer not committing a separate config unless useful. Use a temp file:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
config_path = Path('config/runtime.yaml')
data = yaml.safe_load(config_path.read_text())
# Smoke config intentionally reduces fixed_section_order to the single worker-enabled lane.
data['reader_facing']['fixed_section_order'] = ['github-ai-projects']
data.setdefault('selection', {}).setdefault('per_lane_limits', {})['github-ai-projects'] = 5
data['lane_workers'] = {
    'enabled': True,
    'mode': 'local',
    'enabled_lanes': ['github-ai-projects'],
}
Path('/tmp/daily-report-lane-worker-smoke.yaml').write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
PY
```

For Phase A smoke, `fixed_section_order` must contain only worker-enabled lanes, or `enabled_lanes` must include every lane in `fixed_section_order`; partial replacement is forbidden and tested.

- [ ] **Step 2: Run smoke without publish**

```bash
python3 helpers/run_daily_report_flow.py \
  --report-date 2026-04-27 \
  --config /tmp/daily-report-lane-worker-smoke.yaml \
  --skip-collect \
  --title-suffix 'lane-worker-smoke' \
  --verbose
```

Expected: exit 0, `validation.status = passed` in JSON output.

- [ ] **Step 3: Verify artifacts**

```bash
python3 - <<'PY'
import json
from pathlib import Path
run = Path.home()/'.daily-lane-data/runtime/daily-report-master/2026-04-27'
summary = json.loads((run/'run-summary.json').read_text())
print(summary.get('lane_workers'))
for path in [
    run/'lane-inputs/github-ai-projects.json',
    run/'lane-outputs/github-ai-projects.json',
    run/'lane-memory/github-ai-projects.md',
    run/'report.md',
]:
    print(path, path.exists())
md = (run/'report.md').read_text()
for bad in ['采集文本', '保守看', '摘要里能看到', '先按标题本身交代主题']:
    print(bad, bad in md)
PY
```

Expected:

- All paths exist.
- Bad phrases are `False`.
- GitHub AI 项目 section exists if lane has candidates; otherwise worker output is empty and final report must still pass only if other lanes render. If final report excludes empty GitHub section, record it as a limitation for next task.

- [ ] **Step 4: Run full tests**

```bash
python3 -m pytest -q
```

Expected: PASS.

- [ ] **Step 5: Update feedback ledger**

Append to `docs/report-feedback-ledger.md`:

```markdown
#### Implementation progress — lane subagent vertical slice

- Change: added lane input/output artifacts, local worker runner, report assembler, and internal `github-ai-projects` worker smoke path.
- Verification:
  - `python3 -m pytest -q`
  - `python3 helpers/run_daily_report_flow.py --report-date 2026-04-27 --config /tmp/daily-report-lane-worker-smoke.yaml --skip-collect --title-suffix 'lane-worker-smoke' --verbose`
- Result: master remains the only report entrypoint; lane worker artifacts are written under runtime `lane-inputs/`, `lane-outputs/`, `lane-memory/`.
```

- [ ] **Step 6: Commit**

```bash
git add docs/report-feedback-ledger.md
git commit -m "docs: record lane worker smoke verification"
```

---

### Task 10: Commit design and implementation plan docs

**Files:**
- Modify/Create: `docs/2026-04-27-lane-subagent-design.md`
- Create: `docs/superpowers/plans/2026-04-27-lane-subagent-implementation-plan.md`

- [ ] **Step 1: Link plan from design doc**

Append near the top or in implementation section of `docs/2026-04-27-lane-subagent-design.md`:

```markdown
Implementation plan: `docs/superpowers/plans/2026-04-27-lane-subagent-implementation-plan.md`.
```

- [ ] **Step 2: Review docs formatting**

Run:

```bash
git diff -- docs/2026-04-27-lane-subagent-design.md docs/superpowers/plans/2026-04-27-lane-subagent-implementation-plan.md
```

Expected: Plan is readable, paths exact, no secrets.

- [ ] **Step 3: Commit docs**

```bash
git add docs/2026-04-27-lane-subagent-design.md docs/superpowers/plans/2026-04-27-lane-subagent-implementation-plan.md
git commit -m "docs: plan lane subagent report architecture"
```

---

### Task 11: Final verification and push

**Files:**
- All changed files

- [ ] **Step 1: Run full test suite**

```bash
python3 -m pytest -q
```

Expected: PASS.

- [ ] **Step 2: Run final no-publish real-date smoke**

```bash
python3 helpers/run_daily_report_flow.py --report-date 2026-04-27 --skip-collect --title-suffix 'lane-worker-final-smoke' --verbose
```

Expected: exit 0. Since default worker mode may still be disabled, this verifies no regression to current production path.

- [ ] **Step 3: Check git state**

```bash
git status --short
git log --oneline -5
```

Expected: no uncommitted files except intentionally ignored temp files.

- [ ] **Step 4: Push**

```bash
# git push  # only after parent/user approval
```

- [ ] **Step 5: Report back**

Reply with:

- Plan path
- Design doc path
- Whether implementation was executed or only planned
- Test commands and results
- Commit hashes
- Any remaining risk / next decision

---

## 4. Acceptance Criteria

Implementation is acceptable only when all are true:

1. `run_daily_report_flow.py` remains the single daily report entrypoint.
2. No lane worker publishes Feishu, archives, or sends ops notices by itself.
3. Runtime writes lane artifacts under:
   - `lane-inputs/*.json`
   - `lane-outputs/*.json`
   - optional `lane-memory/*.md`
4. `github-ai-projects` lane can be run as an internal worker and produce a valid lane output artifact.
4a. `empty` means no publishable content; `blocked` means unusable artifact/system failure.
5. Final `report.md` still passes `validate_report_markdown()`.
6. Existing default production path does not regress.
7. Full pytest passes.
8. Ledger records what changed and how it was verified.

---

## 5. Risks and Guardrails

- **Risk: accidentally creating two systems.** Guardrail: no worker publishes externally; master owns publish/archive.
- **Risk: schema too rigid too early.** Guardrail: pure Python validation, optional `side_artifacts`, no heavy dependency.
- **Risk: GitHub AI Projects quality worse than old agent-cron.** Guardrail: first deterministic worker only establishes plumbing; later add subagent prompt/agent runner behind same contract.
- **Risk: partial worker mode drops lanes.** Guardrail: if worker mode is enabled, tests should either include all fixed-order lanes or assembler must intentionally merge worker outputs with old renderer outputs. Prefer explicit behavior and test it.
- **Risk: `signals_adapter.py` keeps growing.** Guardrail: new code goes into `lane_*` modules; only add thin compatibility adapters to `signals_adapter.py`.

---

## 6. Next Plan After This One

After this plan lands, write a separate plan for **subagent-backed GitHub AI Projects worker**:

- define prompt template
- define tool permissions
- define output JSON extraction/repair
- compare output against old `agent-cron` sample `/Users/haha/workspace/memory/github-ai-projects/2026-04-26.md`
- add quality eval fixture for Top 5 repo selection
- only then enable `github-ai-projects` by default in production cron
