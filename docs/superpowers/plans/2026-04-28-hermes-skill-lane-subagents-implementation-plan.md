# Hermes Skill Lane Subagents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Python-controlled lane workers with a Hermes-master-orchestrated workflow where every lane is handled by a Hermes subagent that loads a lane-specific skill and writes `lane.md` + `lane-meta.json`.

**Architecture:** Python remains deterministic infrastructure only: skill sync, raw-corpus packaging, output validation, markdown assembly, publish/archive wrappers. The Hermes master skill is the only place that may call `delegate_task`; lane skills are the only place where lane selection, rejection, judgment, and reader-facing prose are defined. Existing Python lane workers/renderers remain available only for legacy mode and must be unreachable from the new Hermes skill workflow.

**Tech Stack:** Hermes skills/subagents, Python 3 helper scripts, pytest, Markdown, JSON metadata, existing Feishu publish/archive helpers.

---

## Reference Documents

- Design spec: `docs/superpowers/specs/2026-04-28-hermes-skill-lane-subagents-design.md`
- Feedback ledger: `docs/report-feedback-ledger.md`
- Existing runtime flow: `helpers/run_daily_report_flow.py`
- Existing lane worker code to avoid in new workflow:
  - `helpers/lane_workers.py`
  - `helpers/lane_subagent_runner.py`
  - `helpers/lane_subagent_worker.py`
  - `helpers/github_trending_worker.py`
  - `helpers/github_ai_projects_worker.py`

## Hard Constraints

- Do not use Codex for this implementation unless MT explicitly re-allows it.
- Do not implement Python lane brains.
- Do not make Python launch Hermes subagents.
- Do not let Python select/rank/summarize/rewrite lane content.
- Do not silently fallback to old renderer or `selected_items.json` in the new workflow.
- Do not switch production defaults until MT reviews and accepts a preview.
- Every task must end with tests and a commit.

## File Structure To Create

```text
skills/
  daily-report-master/
    SKILL.md
    scripts/
      sync_skills.py
      prepare_lane_packages.py
      validate_lane_outputs.py
      assemble_lane_markdown.py
      publish_report.py
  daily-report-lane-weather/SKILL.md
  daily-report-lane-weather/scripts/normalize_raw.py
  daily-report-lane-weather/scripts/validate_output.py
  daily-report-lane-x-feed/SKILL.md
  daily-report-lane-x-feed/scripts/normalize_raw.py
  daily-report-lane-x-feed/scripts/validate_output.py
  daily-report-lane-x-following/SKILL.md
  daily-report-lane-x-following/scripts/normalize_raw.py
  daily-report-lane-x-following/scripts/validate_output.py
  daily-report-lane-reddit/SKILL.md
  daily-report-lane-reddit/scripts/normalize_raw.py
  daily-report-lane-reddit/scripts/validate_output.py
  daily-report-lane-hacker-news/SKILL.md
  daily-report-lane-hacker-news/scripts/normalize_raw.py
  daily-report-lane-hacker-news/scripts/validate_output.py
  daily-report-lane-hacker-news-search/SKILL.md
  daily-report-lane-hacker-news-search/scripts/normalize_raw.py
  daily-report-lane-hacker-news-search/scripts/validate_output.py
  daily-report-lane-claude-code/SKILL.md
  daily-report-lane-claude-code/scripts/normalize_raw.py
  daily-report-lane-claude-code/scripts/validate_output.py
  daily-report-lane-codex/SKILL.md
  daily-report-lane-codex/scripts/normalize_raw.py
  daily-report-lane-codex/scripts/validate_output.py
  daily-report-lane-openclaw/SKILL.md
  daily-report-lane-openclaw/scripts/normalize_raw.py
  daily-report-lane-openclaw/scripts/validate_output.py
  daily-report-lane-github-ai-projects/SKILL.md
  daily-report-lane-github-ai-projects/scripts/normalize_raw.py
  daily-report-lane-github-ai-projects/scripts/discover_repos.py
  daily-report-lane-github-ai-projects/scripts/validate_output.py
  daily-report-lane-github-trending/SKILL.md
  daily-report-lane-github-trending/scripts/normalize_raw.py
  daily-report-lane-github-trending/scripts/validate_output.py
  daily-report-lane-product-hunt/SKILL.md
  daily-report-lane-product-hunt/scripts/normalize_raw.py
  daily-report-lane-product-hunt/scripts/validate_output.py
  daily-report-lane-polymarket/SKILL.md
  daily-report-lane-polymarket/scripts/normalize_raw.py
  daily-report-lane-polymarket/scripts/validate_output.py

tests/
  test_hermes_skill_sync.py
  test_lane_package_prepare.py
  test_lane_output_validation.py
  test_lane_markdown_assembly.py
  test_skill_content_contracts.py
  test_no_python_lane_brains.py
```

## Fixed Lane List

Use this exact order everywhere:

```python
LANES = [
    "weather",
    "x-feed",
    "x-following",
    "reddit",
    "hacker-news",
    "hacker-news-search",
    "claude-code",
    "codex",
    "openclaw",
    "github-ai-projects",
    "github-trending",
    "product-hunt",
    "polymarket",
]
```

Map to existing signal lane names where needed:

```python
SIGNAL_LANE_MAP = {
    "weather": "weather-watch",
    "x-feed": "x-feed",
    "x-following": "x-following",
    "reddit": "reddit-watch",
    "hacker-news": "hacker-news-watch",
    "hacker-news-search": "hacker-news-search-watch",
    "claude-code": "claude-code-watch",
    "codex": "codex-watch",
    "openclaw": "openclaw-watch",
    "github-ai-projects": "github-ai-projects",
    "github-trending": "github-trending-weekly",
    "product-hunt": "product-hunt-watch",
    "polymarket": "polymarket-watch",
}
```

---

### Task 1: Add Skill Source Tree And Content Contract Tests

**Files:**
- Create: `tests/test_skill_content_contracts.py`
- Create: all `skills/daily-report-* /SKILL.md` files listed above

- [ ] **Step 1: Write failing tests for required skills**

Create `tests/test_skill_content_contracts.py`:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    "daily-report-master",
    "daily-report-lane-weather",
    "daily-report-lane-x-feed",
    "daily-report-lane-x-following",
    "daily-report-lane-reddit",
    "daily-report-lane-hacker-news",
    "daily-report-lane-hacker-news-search",
    "daily-report-lane-claude-code",
    "daily-report-lane-codex",
    "daily-report-lane-openclaw",
    "daily-report-lane-github-ai-projects",
    "daily-report-lane-github-trending",
    "daily-report-lane-product-hunt",
    "daily-report-lane-polymarket",
]

FORBIDDEN_IN_SKILLS = [
    "Python decides what to select",
    "use selected_items as primary input",
    "fallback to renderer",
]


def read_skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


def test_all_required_skill_files_exist():
    for name in SKILLS:
        assert (ROOT / "skills" / name / "SKILL.md").exists(), name


def test_master_skill_declares_delegate_task_as_agent_only():
    text = read_skill("daily-report-master")
    assert "delegate_task" in text
    assert "Only the Hermes master agent may call delegate_task" in text
    assert "Python must not launch Hermes subagents" in text
    assert "must not rewrite lane markdown" in text


def test_lane_skills_require_markdown_and_meta_outputs():
    for name in SKILLS:
        if name == "daily-report-master":
            continue
        text = read_skill(name)
        assert "lane.md" in text, name
        assert "lane-meta.json" in text, name
        assert "selected" in text.lower(), name
        assert "rejected" in text.lower(), name
        assert "sources" in text.lower(), name
        assert "禁止" in text or "Forbidden" in text, name


def test_skills_do_not_authorize_python_lane_brains():
    for name in SKILLS:
        text = read_skill(name)
        for forbidden in FORBIDDEN_IN_SKILLS:
            assert forbidden not in text, f"{name} contains {forbidden!r}"
```

- [ ] **Step 2: Run failing tests**

Run:

```bash
python3 -m pytest -q tests/test_skill_content_contracts.py
```

Expected: FAIL because skill files do not exist.

- [ ] **Step 3: Create master skill**

Create `skills/daily-report-master/SKILL.md` with these sections:

```markdown
---
name: daily-report-master
description: Orchestrate the AI Agent daily report using Hermes lane subagents and lane skills.
---

# Daily Report Master

## Mission

You are the Hermes master agent for the AI Agent daily report. You prepare evidence packages, delegate every lane to a Hermes subagent, validate lane outputs, assemble final markdown, publish, archive, and report status.

## Non-Negotiable Rules

- Only the Hermes master agent may call `delegate_task`.
- Python must not launch Hermes subagents.
- Python must not select, rank, summarize, rewrite, or render reader-facing lane content.
- The master must not rewrite lane markdown.
- If a lane fails, mark it `blocked` or `degraded`; do not silently fallback to old renderer output.
- `selected_items.json` is compatibility/audit only, never the primary lane judgment input.

## Workflow

1. Sync repo skill sources into Hermes' skill directory if necessary.
2. Run `skills/daily-report-master/scripts/prepare_lane_packages.py` to create lane packages.
3. For every lane package, call `delegate_task` with the matching lane skill.
4. In the delegated task prompt, require the lane subagent to load its skill, read `input.md`, inspect raw files, and write `lane.md` plus `lane-meta.json`.
5. Wait for all lane outputs.
6. Run `skills/daily-report-master/scripts/validate_lane_outputs.py`.
7. Run `skills/daily-report-master/scripts/assemble_lane_markdown.py`.
8. Publish using existing Feishu publishing wrapper or `publish_report.py`.
9. Archive and update `docs/report-feedback-ledger.md`.
10. Report links, degraded lanes, and commit hash.

## Lane Skill Map

- weather -> daily-report-lane-weather
- x-feed -> daily-report-lane-x-feed
- x-following -> daily-report-lane-x-following
- reddit -> daily-report-lane-reddit
- hacker-news -> daily-report-lane-hacker-news
- hacker-news-search -> daily-report-lane-hacker-news-search
- claude-code -> daily-report-lane-claude-code
- codex -> daily-report-lane-codex
- openclaw -> daily-report-lane-openclaw
- github-ai-projects -> daily-report-lane-github-ai-projects
- github-trending -> daily-report-lane-github-trending
- product-hunt -> daily-report-lane-product-hunt
- polymarket -> daily-report-lane-polymarket
```

- [ ] **Step 4: Create lane skill files**

Each lane skill must include:

```markdown
---
name: daily-report-lane-<lane>
description: Generate the <lane> section of the AI Agent daily report from raw corpus.
---

# <Lane Title> Lane

## Mission

[Specific lane purpose.]

## Input

Read the lane package provided by the master:

- `input.md`
- `context.json`
- `raw/`

Do not use `selected_items.json` as primary judgment input.

## Selection Rules

[Lane-specific reportability criteria.]

## Rejection Rules

Reject items when:

- evidence is too thin;
- source link is missing;
- it is generic tech/news not relevant to AI/coding-agent workflows;
- it repeats another stronger item;
- it cannot be explained in concrete human terms.

## Writing Style

Write Chinese-first, concrete, human-readable prose. Explain who did what, what changed, why it matters today, and what the reader can do with it. Keep source links.

## Forbidden Output

禁止使用：

- “趋势信息包含这些具体点”
- “这条原始信号给出的可核验信息集中在”
- “适合作为今日该栏目的迁移期素材”
- “具体变化见来源”
- “采集文本”
- “当前可作为”

## Output

Write:

- `lane.md`: reader-facing markdown section only.
- `lane-meta.json`: status, selected, rejected, sources, notes.
```

Add lane-specific notes:

- X lanes: human paraphrase tweets; around 10 high-signal items; no internal collector voice.
- HN/Reddit: include discussion substance/comments, not title-only summaries.
- Claude Code/Codex: preserve version numbers, release notes, workflow changes.
- GitHub AI Projects: use internal discovery/evidence gathering; no shared memory file integration.
- GitHub Trending: coding-agent relevance, reject generic AI infra.
- Product Hunt: 2-3 AI/coding-agent relevant launches only.
- Weather: Beijing and Shanghai first, concise practical context.

- [ ] **Step 5: Run tests**

Run:

```bash
python3 -m pytest -q tests/test_skill_content_contracts.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills tests/test_skill_content_contracts.py
git commit -m "feat: add daily report skill source contracts"
```

---

### Task 2: Add Deterministic Skill Sync Script

**Files:**
- Create: `skills/daily-report-master/scripts/sync_skills.py`
- Create: `tests/test_hermes_skill_sync.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_hermes_skill_sync.py`:

```python
from pathlib import Path

from skills.daily_report_master.scripts.sync_skills import discover_skill_dirs, sync_skills


def test_discover_skill_dirs_returns_repo_skills(tmp_path):
    root = tmp_path
    (root / "skills" / "daily-report-master").mkdir(parents=True)
    (root / "skills" / "daily-report-master" / "SKILL.md").write_text("master", encoding="utf-8")
    (root / "skills" / "daily-report-lane-x-feed").mkdir(parents=True)
    (root / "skills" / "daily-report-lane-x-feed" / "SKILL.md").write_text("lane", encoding="utf-8")

    names = [path.name for path in discover_skill_dirs(root)]

    assert names == ["daily-report-lane-x-feed", "daily-report-master"]


def test_sync_skills_copies_skill_trees_to_destination(tmp_path):
    root = tmp_path / "repo"
    source = root / "skills" / "daily-report-lane-x-feed"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("skill", encoding="utf-8")
    (source / "scripts").mkdir()
    (source / "scripts" / "normalize_raw.py").write_text("print('ok')", encoding="utf-8")
    dest = tmp_path / "hermes" / "skills" / "productivity"

    synced = sync_skills(root, dest)

    assert synced == ["daily-report-lane-x-feed"]
    assert (dest / "daily-report-lane-x-feed" / "SKILL.md").read_text(encoding="utf-8") == "skill"
    assert (dest / "daily-report-lane-x-feed" / "scripts" / "normalize_raw.py").exists()
```

- [ ] **Step 2: Run failing tests**

```bash
python3 -m pytest -q tests/test_hermes_skill_sync.py
```

Expected: import failure because script does not exist/import path is not ready.

- [ ] **Step 3: Make skill scripts importable**

Because `skills/daily-report-master` contains hyphens, create an importable mirror package for deterministic scripts:

```text
skills/daily_report_master/__init__.py
skills/daily_report_master/scripts/__init__.py
skills/daily_report_master/scripts/sync_skills.py
```

Also keep CLI wrappers under the skill source tree if desired:

```text
skills/daily-report-master/scripts/sync_skills.py
```

The hyphenated skill script can import and call the underscore package implementation.

- [ ] **Step 4: Implement `sync_skills.py`**

Implementation requirements:

```python
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def discover_skill_dirs(repo_root: Path) -> list[Path]:
    skills_root = repo_root / "skills"
    return sorted(
        [path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").exists()],
        key=lambda path: path.name,
    )


def sync_skills(repo_root: Path, destination_root: Path) -> list[str]:
    destination_root.mkdir(parents=True, exist_ok=True)
    synced: list[str] = []
    for source in discover_skill_dirs(repo_root):
        dest = destination_root / source.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source, dest)
        synced.append(source.name)
    return synced


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--destination-root", type=Path, default=Path.home() / ".hermes" / "skills" / "productivity")
    args = parser.parse_args()
    synced = sync_skills(args.repo_root.resolve(), args.destination_root.expanduser().resolve())
    print("synced skills:")
    for name in synced:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Add hyphenated CLI wrapper**

`skills/daily-report-master/scripts/sync_skills.py`:

```python
from skills.daily_report_master.scripts.sync_skills import main

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 6: Run tests**

```bash
python3 -m pytest -q tests/test_hermes_skill_sync.py tests/test_skill_content_contracts.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add skills tests/test_hermes_skill_sync.py
git commit -m "feat: add daily report skill sync"
```

---

### Task 3: Add Lane Package Preparation Infrastructure

**Files:**
- Create: `skills/daily_report_master/scripts/prepare_lane_packages.py`
- Create wrapper: `skills/daily-report-master/scripts/prepare_lane_packages.py`
- Create: `tests/test_lane_package_prepare.py`

- [ ] **Step 1: Write failing tests**

Create tests that build temporary signal roots and assert lane packages are created without selected-items primary input:

```python
import json
from pathlib import Path

from skills.daily_report_master.scripts.prepare_lane_packages import prepare_lane_packages


def test_prepare_lane_packages_reads_signal_files_not_selected_items(tmp_path):
    signal_root = tmp_path / "signals"
    lane_dir = signal_root / "x-feed" / "2026-04-26" / "signals"
    lane_dir.mkdir(parents=True)
    (lane_dir / "001.md").write_text("# Tweet\nClaude Code workflow changed.\nhttps://x.com/a/status/1", encoding="utf-8")
    selected_items = tmp_path / "selected_items.json"
    selected_items.write_text(json.dumps({"items": [{"title": "SHOULD NOT BE PRIMARY"}]}), encoding="utf-8")
    runtime_root = tmp_path / "runtime"

    packages = prepare_lane_packages(
        report_date="2026-04-26",
        signal_root=signal_root,
        runtime_root=runtime_root,
        selected_items_path=selected_items,
    )

    package = packages["x-feed"]
    input_text = (package / "input.md").read_text(encoding="utf-8")
    context = json.loads((package / "context.json").read_text(encoding="utf-8"))
    assert "Claude Code workflow changed" in input_text
    assert "SHOULD NOT BE PRIMARY" not in input_text
    assert context["selected_items_mode"] == "audit_only"
    assert context["output_markdown"].endswith("lane.md")
    assert context["output_meta"].endswith("lane-meta.json")


def test_prepare_lane_packages_marks_missing_raw_corpus(tmp_path):
    packages = prepare_lane_packages(
        report_date="2026-04-26",
        signal_root=tmp_path / "signals",
        runtime_root=tmp_path / "runtime",
        selected_items_path=None,
    )

    context = json.loads((packages["github-ai-projects"] / "context.json").read_text(encoding="utf-8"))
    assert context["raw_corpus_status"] in {"missing", "degraded"}
```

- [ ] **Step 2: Run failing tests**

```bash
python3 -m pytest -q tests/test_lane_package_prepare.py
```

Expected: FAIL because module does not exist.

- [ ] **Step 3: Implement lane constants and package builder**

Implement in `skills/daily_report_master/scripts/prepare_lane_packages.py`:

- `LANES`
- `SIGNAL_LANE_MAP`
- `LANE_SKILL_MAP`
- `prepare_lane_packages(report_date, signal_root, runtime_root, selected_items_path=None) -> dict[str, Path]`

Package path:

```text
<runtime_root>/lane-packages/<lane>/
```

For each lane write:

```text
input.md
context.json
raw/<copied source files>
```

`input.md` must include:

- report date;
- lane key;
- matching skill name;
- raw file index;
- output paths;
- instruction: use raw corpus as primary evidence;
- instruction: write `lane.md` and `lane-meta.json`.

Do not embed `selected_items.json` content except a path and `audit_only` marker.

- [ ] **Step 4: Add CLI wrapper**

`skills/daily-report-master/scripts/prepare_lane_packages.py` imports package implementation and exposes CLI.

CLI args:

```bash
--report-date YYYY-MM-DD
--signal-root ~/.daily-lane-data/signals
--runtime-root ~/.daily-lane-data/runtime/daily-report-master/YYYY-MM-DD
--selected-items-path optional
```

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest -q tests/test_lane_package_prepare.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills tests/test_lane_package_prepare.py
git commit -m "feat: prepare raw corpus lane packages"
```

---

### Task 4: Add Lane Output Validation Infrastructure

**Files:**
- Create: `skills/daily_report_master/scripts/validate_lane_outputs.py`
- Create wrapper: `skills/daily-report-master/scripts/validate_lane_outputs.py`
- Create: `tests/test_lane_output_validation.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_lane_output_validation.py`:

```python
import json
from pathlib import Path

import pytest

from skills.daily_report_master.scripts.validate_lane_outputs import ValidationError, validate_lane_output_dir


def write_output(root: Path, lane: str, markdown: str, meta: dict):
    out = root / "lane-outputs" / lane
    out.mkdir(parents=True)
    (out / "lane.md").write_text(markdown, encoding="utf-8")
    (out / "lane-meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return out


def test_validate_accepts_human_lane_output(tmp_path):
    out = write_output(
        tmp_path,
        "github-trending",
        "## GitHub 趋势项目\n\n- **owner/repo**：这是一个 Claude Code workflow 项目，今天值得看是因为它解决了本地模型接入问题。 [GitHub](https://github.com/owner/repo)",
        {"lane": "github-trending", "status": "ok", "selected_count": 1, "rejected_count": 1, "sources": [{"title": "owner/repo", "url": "https://github.com/owner/repo"}], "rejected": [], "notes": []},
    )

    validate_lane_output_dir(out)


def test_validate_rejects_template_phrases(tmp_path):
    out = write_output(
        tmp_path,
        "github-trending",
        "## GitHub 趋势项目\n\n- owner/repo 的趋势信息包含这些具体点：foo。 [GitHub](https://github.com/owner/repo)",
        {"lane": "github-trending", "status": "ok", "selected_count": 1, "rejected_count": 0, "sources": [{"title": "owner/repo", "url": "https://github.com/owner/repo"}], "rejected": [], "notes": []},
    )

    with pytest.raises(ValidationError, match="forbidden phrase"):
        validate_lane_output_dir(out)


def test_validate_rejects_ok_without_sources(tmp_path):
    out = write_output(
        tmp_path,
        "x-feed",
        "## X 推荐\n\n- 有人分享了 Claude Code 工作流经验。",
        {"lane": "x-feed", "status": "ok", "selected_count": 1, "rejected_count": 0, "sources": [], "rejected": [], "notes": []},
    )

    with pytest.raises(ValidationError, match="sources"):
        validate_lane_output_dir(out)
```

- [ ] **Step 2: Run failing tests**

```bash
python3 -m pytest -q tests/test_lane_output_validation.py
```

Expected: FAIL.

- [ ] **Step 3: Implement validator**

Implement:

```python
class ValidationError(Exception):
    pass

FORBIDDEN_PHRASES = [
    "趋势信息包含这些具体点",
    "这条原始信号给出的可核验信息集中在",
    "适合作为今日该栏目的迁移期素材",
    "具体变化见来源",
    "采集文本",
    "当前可作为",
]

ALLOWED_STATUS = {"ok", "empty", "degraded", "blocked"}
```

`validate_lane_output_dir(path: Path) -> None` checks:

- `lane.md` exists;
- `lane-meta.json` exists and parses;
- meta `status` allowed;
- `ok` requires non-empty markdown and non-empty sources;
- markdown includes at least one URL for `ok`;
- forbidden phrases absent;
- meta has `selected_count`, `rejected_count`, `sources`, `rejected`, `notes`.

Do not rewrite files.

- [ ] **Step 4: Add CLI wrapper**

CLI accepts:

```bash
--runtime-root <path>
```

and validates all `lane-outputs/*` directories.

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest -q tests/test_lane_output_validation.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills tests/test_lane_output_validation.py
git commit -m "feat: validate lane markdown outputs"
```

---

### Task 5: Add Markdown Assembly Without Rewrite

**Files:**
- Create: `skills/daily_report_master/scripts/assemble_lane_markdown.py`
- Create wrapper: `skills/daily-report-master/scripts/assemble_lane_markdown.py`
- Create: `tests/test_lane_markdown_assembly.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_lane_markdown_assembly.py`:

```python
from pathlib import Path

from skills.daily_report_master.scripts.assemble_lane_markdown import assemble_report


def test_assemble_report_concatenates_lane_markdown_without_rewrite(tmp_path):
    runtime = tmp_path / "runtime"
    for lane, body in [
        ("weather", "## 天气\n\n北京晴。"),
        ("x-feed", "## X 推荐\n\n- 原样保留这一句 [原帖](https://x.com/a/status/1)"),
    ]:
        out = runtime / "lane-outputs" / lane
        out.mkdir(parents=True)
        (out / "lane.md").write_text(body, encoding="utf-8")

    report = assemble_report(runtime_root=runtime, report_date="2026-04-26", title_suffix="skill-preview")

    text = report.read_text(encoding="utf-8")
    assert text.startswith("# AI Agent 日报（2026-04-26）skill-preview")
    assert "北京晴。" in text
    assert "原样保留这一句" in text
    assert text.index("## 天气") < text.index("## X 推荐")


def test_assemble_report_skips_missing_lane_with_note(tmp_path):
    runtime = tmp_path / "runtime"
    out = runtime / "lane-outputs" / "weather"
    out.mkdir(parents=True)
    (out / "lane.md").write_text("## 天气\n\n北京晴。", encoding="utf-8")

    report = assemble_report(runtime_root=runtime, report_date="2026-04-26")

    text = report.read_text(encoding="utf-8")
    assert "## 天气" in text
    assert "未生成" in text
```

- [ ] **Step 2: Run failing tests**

```bash
python3 -m pytest -q tests/test_lane_markdown_assembly.py
```

Expected: FAIL.

- [ ] **Step 3: Implement assembler**

Implement `assemble_report(runtime_root: Path, report_date: str, title_suffix: str = "") -> Path`.

Requirements:

- read lane markdown in fixed order;
- concatenate without modifying lane content;
- if lane missing, append a short ops note under `## <lane> 未生成` or collect missing lanes in a final ops section;
- write `runtime_root/report.md`;
- return report path.

No summarization, no rewriting, no style fixes.

- [ ] **Step 4: Add CLI wrapper**

```bash
python3 skills/daily-report-master/scripts/assemble_lane_markdown.py --runtime-root ... --report-date ... --title-suffix skill-preview
```

- [ ] **Step 5: Run tests**

```bash
python3 -m pytest -q tests/test_lane_markdown_assembly.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills tests/test_lane_markdown_assembly.py
git commit -m "feat: assemble lane markdown without rewrite"
```

---

### Task 6: Add No-Python-Lane-Brain Regression Tests

**Files:**
- Create: `tests/test_no_python_lane_brains.py`
- Possibly Modify: `skills/daily_report_master/scripts/*.py`

- [ ] **Step 1: Write tests that protect boundaries**

Create `tests/test_no_python_lane_brains.py`:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DETERMINISTIC_SCRIPT_ROOTS = [
    ROOT / "skills" / "daily_report_master" / "scripts",
    ROOT / "skills" / "daily-report-master" / "scripts",
]
FORBIDDEN_SNIPPETS = [
    "delegate_task(",
    "_summary(",
    "build_lane_output(",
    "run_lane_subagent(",
    "github_trending_worker",
    "github_ai_projects_worker",
    "selected_items as primary",
]


def test_deterministic_scripts_do_not_launch_or_render_agents():
    for root in DETERMINISTIC_SCRIPT_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for snippet in FORBIDDEN_SNIPPETS:
                assert snippet not in text, f"{path} contains forbidden snippet {snippet!r}"


def test_master_skill_is_the_only_place_that_mentions_delegate_task():
    master = ROOT / "skills" / "daily-report-master" / "SKILL.md"
    assert "delegate_task" in master.read_text(encoding="utf-8")
    for path in (ROOT / "skills").rglob("*.py"):
        assert "delegate_task" not in path.read_text(encoding="utf-8"), path
```

- [ ] **Step 2: Run tests**

```bash
python3 -m pytest -q tests/test_no_python_lane_brains.py
```

Expected: PASS if prior tasks respected boundaries; otherwise fix deterministic scripts.

- [ ] **Step 3: Run focused suite**

```bash
python3 -m pytest -q \
  tests/test_skill_content_contracts.py \
  tests/test_hermes_skill_sync.py \
  tests/test_lane_package_prepare.py \
  tests/test_lane_output_validation.py \
  tests/test_lane_markdown_assembly.py \
  tests/test_no_python_lane_brains.py
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tests skills
git commit -m "test: guard against python lane brains"
```

---

### Task 7: Write The Real Lane Skills In Detail

**Files:**
- Modify: all `skills/daily-report-lane-*/SKILL.md`
- Modify: `tests/test_skill_content_contracts.py` if needed

This is the most important content-quality task. Do not rush it.

- [ ] **Step 1: Expand GitHub Trending skill**

It must instruct the subagent to:

- read all repo candidates and snippets;
- select only projects relevant to AI/coding-agent workflows;
- reject generic AI infra unless it clearly affects agent workflows;
- write 3-7 items;
- for each item explain:
  - what it is;
  - what changed or why it surfaced today;
  - why an AI/coding-agent reader should care;
  - source link;
- explicitly reject phrases from prior failed output.

- [ ] **Step 2: Expand X Feed and X Following skills**

Both must instruct:

- write human paraphrases, not tweet dumps;
- preserve source links;
- target around 10 items for X feed, around 5-10 for following depending quality;
- explain who did what, what result/blocker/background matters;
- filter generic AI/news/promo;
- avoid internal collection voice.

- [ ] **Step 3: Expand Reddit skill**

Must instruct:

- include subreddit/thread context;
- summarize discussion substance;
- reject low-signal questions and generic complaints;
- prefer agent/coding workflow details.

- [ ] **Step 4: Expand HN skills**

For `hacker-news` and `hacker-news-search`:

- include post plus comment-discussion substance;
- distinguish launch/news from discussion;
- reject title-only items;
- explain what practitioners are debating or learning.

- [ ] **Step 5: Expand Claude Code / Codex / OpenClaw skills**

Must preserve:

- versions;
- releases;
- CLI/workflow changes;
- bugs/regressions/workarounds;
- links;
- concrete reader action.

- [ ] **Step 6: Expand GitHub AI Projects skill**

Must instruct:

- run its own evidence gathering/discovery using its helper script if available;
- never use old shared memory output as integration point;
- search/discover project candidates internally;
- select only projects relevant to AI/coding-agent workflows;
- output sources and rejected candidates.

- [ ] **Step 7: Expand Product Hunt / Polymarket / Weather skills**

Product Hunt:

- 2-3 AI/coding-agent relevant products;
- reject generic SaaS/productivity launches;
- preserve Product Hunt links.

Polymarket:

- only include markets relevant to AI/coding-agent ecosystem if meaningful;
- otherwise `empty` with reason.

Weather:

- Beijing and Shanghai first;
- concise practical context;
- no over-writing.

- [ ] **Step 8: Strengthen skill content tests**

Add assertions for lane-specific required phrases/sections, e.g.:

```python
def test_github_trending_skill_rejects_generic_ai_infra():
    text = read_skill("daily-report-lane-github-trending")
    assert "generic AI infra" in text
    assert "coding-agent" in text
    assert "why an AI/coding-agent reader should care" in text
```

Add similar focused tests for X, HN/Reddit, GitHub AI Projects.

- [ ] **Step 9: Run tests**

```bash
python3 -m pytest -q tests/test_skill_content_contracts.py
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add skills tests/test_skill_content_contracts.py
git commit -m "feat: define lane-specific daily report skills"
```

---

### Task 8: Add GitHub AI Projects Evidence Helper Without Making It A Brain

**Files:**
- Create: `skills/daily-report-lane-github-ai-projects/scripts/discover_repos.py`
- Create importable implementation if needed: `skills/daily_report_lane_github_ai_projects/scripts/discover_repos.py`
- Create: `tests/test_github_ai_projects_skill_helpers.py`

- [ ] **Step 1: Write failing tests**

The helper should only gather candidates/evidence, not select final items or write prose.

```python
from pathlib import Path

from skills.daily_report_lane_github_ai_projects.scripts.discover_repos import build_query_list, write_discovery_bundle


def test_build_query_list_formats_date():
    queries = build_query_list("2026-04-26")
    assert "GitHub trending AI 2026-04-26" in queries
    assert "GitHub new AI projects 2026-04-26" in queries
    assert "awesome AI GitHub 2026-04-26" in queries


def test_write_discovery_bundle_writes_evidence_not_selection(tmp_path):
    out = write_discovery_bundle("2026-04-26", tmp_path, search_results=[{"title": "owner/repo", "url": "https://github.com/owner/repo", "snippet": "agent workflow"}])
    text = out.read_text(encoding="utf-8")
    assert "Candidate evidence" in text
    assert "selected" not in text.lower()
    assert "final summary" not in text.lower()
```

- [ ] **Step 2: Implement helper**

Functions:

- `build_query_list(report_date: str) -> list[str]`
- `write_discovery_bundle(report_date: str, output_dir: Path, search_results: list[dict]) -> Path`

No final selection. No markdown section prose. Only evidence.

- [ ] **Step 3: Add wrapper script under hyphenated skill**

`skills/daily-report-lane-github-ai-projects/scripts/discover_repos.py` imports implementation.

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest -q tests/test_github_ai_projects_skill_helpers.py tests/test_no_python_lane_brains.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills tests/test_github_ai_projects_skill_helpers.py
git commit -m "feat: add github ai projects evidence helper"
```

---

### Task 9: Add Publish Wrapper For Skill Workflow

**Files:**
- Create: `skills/daily_report_master/scripts/publish_report.py`
- Create wrapper: `skills/daily-report-master/scripts/publish_report.py`
- Create: `tests/test_skill_publish_wrapper.py`

- [ ] **Step 1: Write tests for command construction only**

Do not call Feishu in tests.

```python
from pathlib import Path

from skills.daily_report_master.scripts.publish_report import build_lark_create_command


def test_build_lark_create_command_uses_markdown_file():
    cmd = build_lark_create_command(Path("/tmp/report.md"), title="AI Agent 日报（2026-04-26）skill-preview")
    assert cmd[:4] == ["lark-cli", "docs", "+create", "--as"]
    assert "user" in cmd
    assert "--title" in cmd
    assert "AI Agent 日报（2026-04-26）skill-preview" in cmd
    assert "--markdown" in cmd
    assert "@/tmp/report.md" in cmd
```

- [ ] **Step 2: Implement wrapper**

`build_lark_create_command(report_path: Path, title: str) -> list[str]`.

`main()` executes command only when invoked directly. Keep tests pure.

- [ ] **Step 3: Run tests**

```bash
python3 -m pytest -q tests/test_skill_publish_wrapper.py
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills tests/test_skill_publish_wrapper.py
git commit -m "feat: add skill workflow publish wrapper"
```

---

### Task 10: Write Manual Hermes Master Runbook And Preview Checklist

**Files:**
- Create: `docs/hermes-skill-daily-report-runbook.md`
- Modify: `docs/report-feedback-ledger.md`

- [ ] **Step 1: Write runbook**

Include exact operator flow:

```markdown
# Hermes Skill Daily Report Runbook

1. Checkout `feat/hermes-skill-lane-subagents`.
2. Run full tests.
3. Sync skills:
   `python3 skills/daily-report-master/scripts/sync_skills.py --repo-root .`
4. Load `daily-report-master` skill in Hermes main session.
5. Run prepare script for date.
6. Use `delegate_task` once per lane, each with the matching lane skill.
7. Ensure each subagent writes `lane.md` and `lane-meta.json`.
8. Run validation script.
9. Assemble report.
10. Publish preview.
11. Verify Feishu document.
12. Update ledger.
```

Add example delegate prompt:

```text
You are the <lane> lane subagent for AI Agent daily report <date>.
First load skill `<skill-name>`.
Read package `<path>`.
Write `<output>/lane.md` and `<output>/lane-meta.json`.
Do not ask questions; if evidence is insufficient, write status `empty`, `degraded`, or `blocked` with reasons.
```

- [ ] **Step 2: Update feedback ledger**

Add an entry explaining the pivot:

- previous Python agent-first branch was rejected because it still used code as lane brain;
- new branch uses Hermes skill/subagent boundary;
- Python cannot launch subagents or write lane prose;
- preview still pending.

- [ ] **Step 3: Commit**

```bash
git add docs/hermes-skill-daily-report-runbook.md docs/report-feedback-ledger.md
git commit -m "docs: add hermes skill daily report runbook"
```

---

### Task 11: Full Verification Before Manual Preview

**Files:**
- No new files expected unless tests reveal issues.

- [ ] **Step 1: Run focused suite**

```bash
python3 -m pytest -q \
  tests/test_skill_content_contracts.py \
  tests/test_hermes_skill_sync.py \
  tests/test_lane_package_prepare.py \
  tests/test_lane_output_validation.py \
  tests/test_lane_markdown_assembly.py \
  tests/test_no_python_lane_brains.py \
  tests/test_github_ai_projects_skill_helpers.py \
  tests/test_skill_publish_wrapper.py
```

Expected: all pass.

- [ ] **Step 2: Run full suite**

```bash
python3 -m pytest -q
```

Expected: all pass.

- [ ] **Step 3: Run deterministic prepare script against 2026-04-26 data**

```bash
python3 skills/daily-report-master/scripts/prepare_lane_packages.py \
  --report-date 2026-04-26 \
  --signal-root /Users/haha/.daily-lane-data/signals \
  --runtime-root /Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26-skill-preview
```

Expected:

```text
lane-packages/<lane>/input.md
lane-packages/<lane>/context.json
```

for every lane.

- [ ] **Step 4: Sync skills locally**

```bash
python3 skills/daily-report-master/scripts/sync_skills.py --repo-root .
```

Expected: all `daily-report-*` skills copied to `~/.hermes/skills/productivity/`.

- [ ] **Step 5: Commit any verification fixes**

If scripts required fixes:

```bash
git add ...
git commit -m "fix: verify hermes skill lane workflow"
```

If no changes, skip commit.

---

### Task 12: Manual Hermes Subagent Preview Run

**Important:** This task cannot be implemented by Python. It must be run from the Hermes main session because only the main agent may call `delegate_task`.

**Files:**
- Runtime outputs only under `/Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26-skill-preview`
- Modify: `docs/report-feedback-ledger.md`

- [ ] **Step 1: Load master skill**

Use `skill_view("daily-report-master")` after syncing skills.

- [ ] **Step 2: Delegate all lanes**

Call `delegate_task` batch mode with one task per lane. Each task must include:

- lane name;
- report date;
- package path;
- output path;
- required skill name;
- instruction to load the skill first;
- instruction to write `lane.md` and `lane-meta.json`.

- [ ] **Step 3: Validate outputs**

```bash
python3 skills/daily-report-master/scripts/validate_lane_outputs.py \
  --runtime-root /Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26-skill-preview
```

Expected: validation passes or reports explicit degraded/blocked lanes.

- [ ] **Step 4: Assemble report**

```bash
python3 skills/daily-report-master/scripts/assemble_lane_markdown.py \
  --runtime-root /Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26-skill-preview \
  --report-date 2026-04-26 \
  --title-suffix hermes-skill-preview
```

Expected: `report.md` created from lane markdown without rewrite.

- [ ] **Step 5: Publish preview**

```bash
python3 skills/daily-report-master/scripts/publish_report.py \
  --report-path /Users/haha/.daily-lane-data/runtime/daily-report-master/2026-04-26-skill-preview/report.md \
  --title 'AI Agent 日报（2026-04-26）hermes-skill-preview'
```

Expected: Feishu doc URL.

- [ ] **Step 6: Verify preview content**

Check:

- every lane section exists or is explicitly degraded/blocked;
- GitHub Trending has no template phrases;
- X/HN/Reddit are human-readable;
- GitHub AI Projects does not use old shared memory path;
- no `采集文本`, `具体变化见来源`, `趋势信息包含这些具体点`, `迁移期素材`.

- [ ] **Step 7: Update ledger and commit**

```bash
git add docs/report-feedback-ledger.md
git commit -m "docs: record hermes skill preview results"
```

---

### Task 13: Push Branch And Report

**Files:** none

- [ ] **Step 1: Check clean status**

```bash
git status --short
```

Expected: clean.

- [ ] **Step 2: Push branch**

```bash
git push -u origin feat/hermes-skill-lane-subagents
```

- [ ] **Step 3: Report to MT**

Include:

- branch;
- commit hash;
- test results;
- preview Feishu URL;
- degraded/blocked lanes;
- explicit statement that production default was not switched.

---

## Final Acceptance Checklist

- [ ] Repo contains all daily-report master/lane skills.
- [ ] Skill sync works.
- [ ] Prepare script creates lane packages from raw corpus.
- [ ] Python scripts do not launch subagents.
- [ ] Python scripts do not select/rank/summarize/rewrite lane content.
- [ ] Every lane has a Hermes subagent output from its skill.
- [ ] `lane.md` files are assembled without rewrite.
- [ ] Validation catches banned template phrases.
- [ ] 2026-04-26 preview is published.
- [ ] MT confirms quality direction is better before production default switch.
