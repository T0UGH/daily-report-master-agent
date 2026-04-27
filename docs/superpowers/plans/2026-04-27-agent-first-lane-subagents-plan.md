# Agent-First Lane Subagents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert `daily-report-master-agent` from code-led rendering into an agent-first architecture where every report lane is produced by a dedicated lane subagent and the master agent only orchestrates, validates, assembles, and publishes.

**Architecture:** Keep `run_daily_report_flow.py` as the single master entrypoint, but stop treating subagents as post-processing helpers. The master will collect raw lane corpora, write one `lane-inputs/<lane>.json` per lane, invoke a process-isolated lane subagent for each lane, validate `lane-outputs/<lane>.json`, and assemble the final report without rewriting lane prose. Legacy `selected_items` / generic renderer paths remain only behind explicit compatibility flags during migration and must be forbidden for agent-first lanes such as `github-trending-weekly`.

**Tech Stack:** Python 3, pytest, subprocess-based process isolation, JSON lane contracts, existing `signals-engine` runtime data, Feishu Docx publish via existing flow.

---

## Non-Negotiable Product Rules

1. **Every fixed report lane has a lane subagent.** A lane may be implemented as a deterministic Python worker only as a temporary shim, but it must run through the same isolated subagent process contract and must declare `agent_runtime.kind`.
2. **Master does not write reader-facing lane prose.** Master can assemble already-rendered lane markdown, validate contracts, dedupe sources, and publish. It cannot use `render_body_section()` for agent-first lanes.
3. **No silent fallback.** If a lane subagent fails, that lane is `blocked` or `degraded`; it must not silently fall back to the old generic renderer.
4. **Lane input is raw corpus, not pre-chewed summary.** `selected_items.json` can survive temporarily for audit/compatibility, but lane subagents must receive `raw_candidates`, `recent_history`, `cross_lane_context`, and style/quality contracts.
5. **Lane output exposes judgment.** Each lane output must include `selected_items`, `rejected_items`, `reasoning_notes`, `markdown`, `sources`, and quality metadata.
6. **GitHub Trending is the first hard gate.** It must prove the new architecture by selecting/filtering from raw GitHub candidates itself and explaining why each repo matters today.

---

## Current Problems This Plan Fixes

- `signals_adapter.py` currently pre-selects and pre-summarizes too much; subagents receive code-shaped answers instead of raw material.
- `lane_subagent_worker.py` is process-isolated, but it still calls `lane_workers.py`, which can call local deterministic helpers and legacy `render_body_section()` fallback.
- `github_search_queries` for GitHub AI Projects are present in `cross_lane_context`, but no active GitHub Search/Web discovery executor exists yet.
- `build_local_lane_output()` and `render_body_section()` remain available for every lane and can accidentally reintroduce template prose.
- The architecture has two overlapping content layers: `selected_items` and `lane_output`.

---

## Target Data Flow

```text
collectors / signals-engine
  ↓ raw per-lane corpus
collect_result.json
  ↓
master builds lane-inputs/<lane>.json directly from raw corpus
  ↓
lane_subagent_runner.py
  ↓ isolated process per lane
python -m helpers.lane_subagent_worker --input ... --output ...
  ↓
per-lane agent implementation
  - selects
  - rejects
  - judges
  - writes reader-facing markdown
  ↓
lane-outputs/<lane>.json + lane-logs/<lane>.md
  ↓
master validates contracts
  ↓
lane_report_assembler.py assembles without rewriting lane prose
  ↓
validate_report_output_contract.py
  ↓
Feishu Docx publish
```

---

## File Structure

### Create

- `helpers/lane_agent_contracts.py`  
  Defines strict input/output contract helpers for agent-first lanes: raw candidate schema, selected/rejected item schema, reasoning notes, agent runtime metadata, quality gates.

- `helpers/lane_corpus_builder.py`  
  Builds raw per-lane corpora from `collect_result`, signal files, existing selected items only as compatibility metadata, and cross-lane context. This file must not write reader-facing prose.

- `helpers/lane_agent_registry.py`  
  Declares every lane, its agent implementation, whether it is mandatory, and whether legacy fallback is allowed. GitHub Trending fallback must be `false`.

- `helpers/lane_agents/github_trending_agent.py`  
  First true agent-first lane implementation. It consumes raw GitHub candidates, filters non-AI/coding-agent repos, writes selected/rejected reasoning, and produces final markdown.

- `helpers/lane_agents/generic_lane_agent.py`  
  Temporary shim for lanes not yet specialized. It must still run in a subagent process and must explicitly label itself `agent_runtime.kind = generic_shim`. It cannot call `render_body_section()` after the migration gate is enabled; it can produce conservative markdown from raw snippets.

- `tests/test_lane_agent_contracts.py`
- `tests/test_lane_corpus_builder.py`
- `tests/test_github_trending_agent.py`
- `tests/test_agent_first_flow.py`

### Modify

- `helpers/run_daily_report_flow.py`  
  Replace lane input construction from `selected_items` with raw corpus construction when `lane_workers.mode: subagent` and `lane_workers.agent_first: true`.

- `helpers/lane_subagent_worker.py`  
  Dispatch through `lane_agent_registry` instead of `lane_workers.build_lane_output()` when `agent_first` is present in lane input.

- `helpers/lane_subagent_runner.py`  
  No major change; add timeout/config metadata if needed.

- `helpers/lane_report_assembler.py`  
  Assert it only assembles `lane_output.markdown`; no lane prose rewrite. It must accept the expanded agent-first output while preserving compatibility with existing `items` / `sources` fields required by `validate_lane_output_artifact()`.

- `helpers/lane_workers.py`  
  Mark as legacy fallback. Add guard: if lane input says `agent_first: true`, this module must not be used.

- `helpers/signals_adapter.py`  
  Keep existing behavior for old non-agent mode, but stop being the source of truth for agent-first lane content.

- `config/runtime.yaml`  
  Add explicit config:
  ```yaml
  lane_workers:
    enabled: true
    mode: subagent
    agent_first: true
    forbid_legacy_fallback_for:
      - github-trending-weekly
  ```

- `docs/report-feedback-ledger.md`  
  Record the architecture shift and verification results.

---

## Task 0: Raw Corpus Discovery and Contract Mapping

**Files:**
- Create: `docs/agent-first-raw-corpus-map.md`
- Create: `tests/test_lane_corpus_builder.py` initial discovery tests

- [ ] **Step 1: Inspect real runtime artifacts before coding**

Run against `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26` and current signals root. Produce a table for every lane in `reader_facing.fixed_section_order`:

- collector/source path;
- available raw fields;
- whether `source_snippet` / `source_url` / raw body are available without `selected_items`;
- whether the lane is ready for specialized agent;
- fallback status if raw corpus is missing.

- [ ] **Step 2: Write the corpus map doc**

`docs/agent-first-raw-corpus-map.md` must include a lane-by-lane matrix and explicitly mark lanes that cannot yet be built without selected_items. Missing raw corpus means `blocked_raw_corpus_missing`, not silent selected_items fallback.

- [ ] **Step 3: Add fixture for GitHub Trending raw corpus**

Create a test fixture from real 2026-04-26 GitHub Trending runtime data. The fixture must include enough raw material for GitHub Trending to select/reject independently.

- [ ] **Step 4: Add registry coverage expectation**

Add a test expectation that every lane in `fixed_section_order` must have a registry entry before agent-first full preview can pass.

- [ ] **Step 5: Commit**

```bash
git add docs/agent-first-raw-corpus-map.md tests/test_lane_corpus_builder.py
git commit -m "docs: map raw corpus for agent-first lanes"
```

---

## Task 1: Add Agent-First Contract Types and Validators

**Files:**
- Create: `helpers/lane_agent_contracts.py`
- Test: `tests/test_lane_agent_contracts.py`

- [ ] **Step 1: Write failing tests for agent-first input/output validation**

Test cases:

```python
def test_validate_agent_lane_input_requires_raw_candidates():
    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "agent_first": True,
        "raw_candidates": [],
        "style_contract": {"language": "zh-CN"},
    }
    validate_agent_lane_input(payload)
```

```python
def test_validate_agent_lane_output_requires_selected_rejected_reasoning_and_runtime():
    payload = {
        "artifact_type": "lane_output",
        "schema_version": 1,
        "report_date": "2026-04-27",
        "lane": "github-trending-weekly",
        "status": "ok",
        "markdown": "## GitHub 趋势项目\n\n- ...",
        "selected_items": [{"id": "repo:a/b", "title": "a/b", "why_selected": "AI agent workflow", "sources": ["https://github.com/a/b"]}],
        "rejected_items": [{"id": "repo:c/d", "title": "c/d", "reason": "泛技术，不是 AI/coding-agent"}],
        "reasoning_notes": ["selected 1 of 2 raw candidates"],
        "sources": ["https://github.com/a/b"],
        "agent_runtime": {"kind": "specialized_agent", "implementation": "github_trending_agent"},
        "quality": {"item_count": 1, "rejected_count": 1},
    }
    validate_agent_lane_output(payload)
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m pytest -q tests/test_lane_agent_contracts.py
```

Expected: fail because module/functions do not exist.

- [ ] **Step 3: Implement minimal validators**

Implement:

```python
def validate_agent_lane_input(payload: dict[str, Any]) -> None: ...
def validate_agent_lane_output(payload: dict[str, Any]) -> None: ...
def is_agent_first_lane_input(payload: dict[str, Any]) -> bool: ...
```

Validation requirements:

- input requires `agent_first is True`, `raw_candidates` list, `style_contract` object.
- output requires `selected_items`, `rejected_items`, `reasoning_notes`, `agent_runtime`.
- `status` must be one of `ok`, `empty`, `degraded`, `blocked`.
- `blocked` requires empty `markdown` or explicit error note; `ok` requires non-empty `markdown`.

- [ ] **Step 4: Run tests and verify GREEN**

```bash
python3 -m pytest -q tests/test_lane_agent_contracts.py
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add helpers/lane_agent_contracts.py tests/test_lane_agent_contracts.py
git commit -m "feat: add agent-first lane contracts"
```

---

## Task 2: Build Raw Lane Corpus Instead of Pre-Chewed Selected Items

**Files:**
- Create: `helpers/lane_corpus_builder.py`
- Modify: `helpers/run_daily_report_flow.py`
- Test: `tests/test_lane_corpus_builder.py`

- [ ] **Step 1: Write failing tests for raw corpus construction**

Test must prove:

1. For `github-trending-weekly`, the lane input contains `raw_candidates` with `source_snippet`, `source_url`, `raw`, and `candidate_source`.
2. The input does **not** rely on `summary` / `editor_summary` as the primary source.
3. `selected_items` appears only under `compatibility.selected_items_snapshot` if present.
4. `cross_lane_context.github_search_queries` still appears for GitHub AI Projects.

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 -m pytest -q tests/test_lane_corpus_builder.py
```

Expected: fail because builder does not exist.

- [ ] **Step 3: Implement `build_agent_lane_input_artifact()`**

Signature:

```python
def build_agent_lane_input_artifact(
    *,
    report_date: str,
    lane_name: str,
    collect_result: dict[str, Any],
    selected_items: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
```

Rules:

- Use `collect_result` and any available raw item paths as the source of truth.
- Include `raw_candidates` list even if empty.
- Include `recent_history` and `cross_lane_context` using existing logic where possible.
- Include `agent_first: true`.
- Include `compatibility.selected_items_snapshot` only for audit and temporary migration.
- Do not call `render_body_section()`.

- [ ] **Step 4: Wire agent-first mode in `run_daily_report_flow.py`**

When config has:

```yaml
lane_workers:
  enabled: true
  mode: subagent
  agent_first: true
```

then use `build_agent_lane_input_artifact()` instead of `build_lane_input_artifact()`.

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest -q tests/test_lane_corpus_builder.py tests/test_run_daily_report_flow.py -k 'agent_first or lane_input or github_ai_projects'
```

- [ ] **Step 6: Commit**

```bash
git add helpers/lane_corpus_builder.py helpers/run_daily_report_flow.py tests/test_lane_corpus_builder.py tests/test_run_daily_report_flow.py
git commit -m "feat: build raw corpus lane inputs"
```

---

## Task 3: Route Subagent Worker Through Lane Agent Registry

**Contract compatibility rule:** agent-first outputs must pass both the new `validate_agent_lane_output()` and the existing `validate_lane_output_artifact()` until the old contract is formally retired. Therefore each agent output must still include existing fields (`items`, `sources`, `section_title`, `quality.item_count`) plus new judgment fields (`selected_items`, `rejected_items`, `reasoning_notes`, `agent_runtime`).

**Files:**
- Create: `helpers/lane_agent_registry.py`
- Modify: `helpers/lane_subagent_worker.py`
- Modify: `helpers/lane_workers.py`
- Test: `tests/test_agent_first_flow.py`

- [ ] **Step 1: Write failing tests**

Tests:

```python
def test_agent_first_worker_does_not_call_legacy_lane_workers(monkeypatch, tmp_path):
    # monkeypatch helpers.lane_workers.build_lane_output to raise
    # run lane_subagent_worker with agent_first input
    # expect success through registry, not legacy path
```

```python
def test_legacy_fallback_is_forbidden_for_github_trending_agent_first():
    # agent_first github-trending-weekly input without registry implementation
    # must fail blocked/nonzero, not call render_body_section
```

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 -m pytest -q tests/test_agent_first_flow.py
```

- [ ] **Step 3: Implement registry**

`helpers/lane_agent_registry.py`:

```python
@dataclass(frozen=True)
class LaneAgentSpec:
    lane: str
    implementation: str
    allow_legacy_fallback: bool
    mandatory: bool

LANE_AGENT_REGISTRY = {...}

def build_agent_lane_output(lane_input: dict[str, Any]) -> dict[str, Any]: ...
```

Initial registry:

- `github-trending-weekly`: `github_trending_agent`, `allow_legacy_fallback=False`, `mandatory=True`
- all other fixed lanes: `generic_lane_agent`, `allow_legacy_fallback=False` under agent-first mode; if generic is too weak it must still declare itself.

- [ ] **Step 4: Modify subagent worker**

In `lane_subagent_worker.py`:

- if `is_agent_first_lane_input(lane_input)`: call registry.
- else: current legacy `build_lane_output()` path remains for compatibility.

- [ ] **Step 5: Guard legacy worker**

In `lane_workers.py`, if `lane_input.get("agent_first") is True`, raise `ValueError("agent-first lane input cannot use legacy lane_workers")`.

- [ ] **Step 6: Run tests**

```bash
python3 -m pytest -q tests/test_agent_first_flow.py tests/test_lane_subagent_runner.py
```

- [ ] **Step 7: Commit**

```bash
git add helpers/lane_agent_registry.py helpers/lane_subagent_worker.py helpers/lane_workers.py tests/test_agent_first_flow.py
git commit -m "feat: route agent-first lanes through registry"
```

---

## Task 4: Implement True GitHub Trending Agent

**Scope boundary:** This task proves autonomous judgment over available raw GitHub Trending candidates. It does not yet implement external GitHub Search/Web discovery. If raw candidates are insufficient, the lane must report `blocked_raw_corpus_missing` rather than backfill from selected_items.

**Files:**
- Create: `helpers/lane_agents/github_trending_agent.py`
- Create package init: `helpers/lane_agents/__init__.py`
- Modify: `helpers/lane_agent_registry.py`
- Test: `tests/test_github_trending_agent.py`

- [ ] **Step 1: Write failing tests for selection and rejection**

Use raw candidates:

- `openai/openai-agents-python`: should select.
- `Alishahryar1/free-claude-code`: should select.
- `someuser/react-calendar`: should reject as generic frontend.
- `owner/awesome-terminal`: should reject unless source mentions AI/coding-agent workflow.

Assert output includes:

- `selected_items` with `why_selected`.
- `rejected_items` with concrete reason.
- `reasoning_notes` with counts.
- Markdown does not include banned phrases:
  - `值得看的趋势项目`
  - `具体变化见来源`
  - `当前可作为`
  - `候选继续观察`
  - `至少因为`

- [ ] **Step 2: Run tests and verify RED**

```bash
python3 -m pytest -q tests/test_github_trending_agent.py
```

- [ ] **Step 3: Implement deterministic first version**

This first version may be deterministic but must behave like an agent lane:

- inspect raw candidates itself;
- select/reject itself;
- write reasons;
- keep sources;
- produce final markdown.

Important: it must not consume `compatibility.selected_items_snapshot` except as tie-break metadata. Add a test where compatibility contains a repo but `raw_candidates` does not; the agent must not select that repo.

- [ ] **Step 4: Run tests and verify GREEN**

```bash
python3 -m pytest -q tests/test_github_trending_agent.py tests/test_agent_first_flow.py
```

- [ ] **Step 5: Live smoke with 2026-04-26**

Create `/tmp/daily-report-agent-first-preview.yaml` from runtime config with:

```yaml
lane_workers:
  enabled: true
  mode: subagent
  agent_first: true
```

Run:

```bash
python3 helpers/run_daily_report_flow.py --report-date 2026-04-26 --config /tmp/daily-report-agent-first-preview.yaml --skip-collect --title-suffix 'agent-first-preview' --verbose
```

Verify:

```bash
python3 - <<'PY'
from pathlib import Path
import json
base = Path('/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26')
out = json.loads((base/'lane-outputs/github-trending-weekly.json').read_text())
print(out['agent_runtime'])
print(out['quality'])
print(out['reasoning_notes'])
print(out['markdown'])
assert out['agent_runtime']['implementation'] == 'github_trending_agent'
assert out['rejected_items']
assert 'render_body_section' not in (base/'lane-logs/github-trending-weekly.md').read_text()
PY
```

- [ ] **Step 6: Commit**

```bash
git add helpers/lane_agents helpers/lane_agent_registry.py tests/test_github_trending_agent.py docs/report-feedback-ledger.md
git commit -m "feat: add agent-first github trending lane"
```

---

## Task 5: Add Generic Lane Agent Shim for Remaining Lanes

**Important:** This task is migration scaffolding only. Generic shim outputs must be labeled `agent_runtime.kind = "generic_shim"` and `agent_runtime.maturity = "migration_shim"`. Do not claim these lanes are fully specialized agents until each has its own lane-specific implementation.

**Files:**
- Create: `helpers/lane_agents/generic_lane_agent.py`
- Modify: `helpers/lane_agent_registry.py`
- Test: `tests/test_agent_first_flow.py`

- [ ] **Step 1: Write failing tests**

Also add a registry coverage test: registry keys cover every lane in `config["reader_facing"]["fixed_section_order"]`; missing entries fail in agent-first mode.

For a non-GitHub lane such as `x-feed` or `claude-code-watch`, verify:

- agent-first subagent mode produces a valid lane output;
- output has `agent_runtime.kind == "generic_shim"`;
- output has `selected_items`, `rejected_items`, `reasoning_notes`;
- no call to `render_body_section()`.

- [ ] **Step 2: Run RED**

```bash
python3 -m pytest -q tests/test_agent_first_flow.py -k generic
```

- [ ] **Step 3: Implement generic shim**

Rules:

- It is acceptable as migration scaffolding, but must be explicit in metadata.
- It selects up to `target_item_count` raw candidates.
- It rejects the rest with reasons like `超出本 lane item budget` or `缺少可读 source_snippet`.
- It writes direct, source-grounded bullets.
- It must not call `signals_adapter.render_body_section()`.

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest -q tests/test_agent_first_flow.py tests/test_lane_subagent_runner.py
```

- [ ] **Step 5: Commit**

```bash
git add helpers/lane_agents/generic_lane_agent.py helpers/lane_agent_registry.py tests/test_agent_first_flow.py
git commit -m "feat: add generic agent-first lane shim"
```

---

## Task 6: Disable Legacy Fallback for Agent-First Mode

**Files:**
- Modify: `config/runtime.yaml`
- Modify: `helpers/runtime_config.py`
- Modify: `helpers/run_daily_report_flow.py`
- Test: `tests/test_run_daily_report_flow.py`

- [ ] **Step 1: Write failing tests**

Tests:

- `lane_workers.agent_first: true` requires `mode: subagent`.
- `agent_first: true` with `mode: local` raises a clear `ValueError`.
- `agent_first: true` cannot silently omit lanes.
- `github-trending-weekly` cannot use legacy fallback.

- [ ] **Step 2: Run RED**

```bash
python3 -m pytest -q tests/test_run_daily_report_flow.py -k agent_first
```

- [ ] **Step 3: Implement runtime config validation**

Update `resolve_lane_worker_config()` to return:

```python
{
  "enabled": bool,
  "mode": "local" | "subagent",
  "agent_first": bool,
  "enabled_lanes": list[str],
  "forbid_legacy_fallback_for": list[str],
}
```

Validation:

- if `agent_first` then `enabled` must be true.
- if `agent_first` then `mode` must be `subagent`.

- [ ] **Step 4: Update runtime config**

Set default desired architecture in `config/runtime.yaml` only if production behavior is ready. If risky, keep default disabled but add a commented documented section. For preview, use explicit temp config.

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest -q tests/test_run_daily_report_flow.py tests/test_agent_first_flow.py
python3 -m pytest -q
```

- [ ] **Step 6: Commit**

```bash
git add config/runtime.yaml helpers/runtime_config.py helpers/run_daily_report_flow.py tests/test_run_daily_report_flow.py
git commit -m "feat: enforce agent-first subagent mode"
```

---

## Task 7: Full Agent-First Preview and Feishu Publish

**Preview gate:** Do not switch default `config/runtime.yaml` to agent-first and do not push until MT reviews the Feishu preview. This task produces a preview commit and a Feishu doc for human acceptance.

**Files:**
- Modify: `docs/report-feedback-ledger.md`
- Runtime artifacts under `/Users/haha/.daily-lane-data/runtime/daily-report-master/<date>/`

- [ ] **Step 1: Run full tests**

```bash
python3 -m pytest -q
```

Expected: all pass.

- [ ] **Step 2: Run live preview for 2026-04-26**

```bash
python3 helpers/run_daily_report_flow.py --report-date 2026-04-26 --config /tmp/daily-report-agent-first-preview.yaml --skip-collect --title-suffix 'agent-first-preview' --verbose
```

- [ ] **Step 3: Verify runtime artifacts**

Check:

- `run-summary.json`: `lane_workers.mode == "subagent"`, `agent_first == true` if recorded.
- Every lane in `fixed_section_order` has `lane-outputs/<lane>.json`.
- Every lane has `agent_runtime`.
- `github-trending-weekly.agent_runtime.implementation == "github_trending_agent"`.
- `github-trending-weekly.rejected_items` is non-empty.
- `lane-logs/github-trending-weekly.md` contains `python -m helpers.lane_subagent_worker`.
- no `render_body_section` in GitHub Trending log/output.

- [ ] **Step 4: Publish Feishu preview**

Use existing lark CLI flow:

```bash
lark-cli docs +create --as user --title 'AI Agent 日报（2026-04-26）agent-first-subagents-preview' --markdown @report.md
```

- [ ] **Step 5: Update feedback ledger**

Record:

- user complaint: code controls too much; every lane needs a subagent; master integrates.
- architecture change summary.
- tests.
- preview doc URL.
- commit hashes.

- [ ] **Step 6: Commit and push**

```bash
git add docs/report-feedback-ledger.md
git commit -m "docs: record agent-first lane subagent migration"
# Do not push unless MT explicitly confirms after preview review
```

---

## Human Acceptance Checklist

The Feishu preview is not accepted unless MT can verify:

1. GitHub Trending text is source-grounded and not template prose.
2. GitHub Trending includes rejected-item evidence in `lane_output`, even if not shown fully in the report.
3. `lane-logs/github-trending-weekly.md` proves a separate subagent process ran.
4. Master did not rewrite lane markdown after the subagent output.
5. Any blocked/degraded lane appears in `run-summary.json` with a clear reason; no silent fallback.

---

## Final Acceptance Criteria

The migration is acceptable only if all are true:

1. `python3 -m pytest -q` passes.
2. `lane_workers.agent_first: true` only works with `mode: subagent`.
3. Every lane output includes `agent_runtime`, `selected_items`, `rejected_items`, and `reasoning_notes`.
4. GitHub Trending does not call or depend on `build_local_lane_output()` / `render_body_section()`.
5. Master assembles lane markdown without rewriting the body.
6. GitHub Trending preview contains concrete project judgments plus rejected-item evidence.
7. Feishu preview is published and linked in the final report to MT.
8. All changes are committed. Push only after MT explicitly confirms the preview or asks to push.

---

## Important Risks

- This is a real architectural migration, not a one-file patch. Do not try to finish by only renaming helpers to agents.
- The first version may still use deterministic Python implementations inside subagent processes. That is acceptable only if the boundary and responsibility are correct: the lane owns selection/rejection/writing; master does not.
- Later improvement can replace deterministic lane agents with LLM/Codex/Claude lane agents, but this plan first fixes the data ownership and contract.
- Keep `selected_items.json` for audit until the new raw-corpus path is stable; do not delete it in this migration unless tests and previews prove no dependency remains.
