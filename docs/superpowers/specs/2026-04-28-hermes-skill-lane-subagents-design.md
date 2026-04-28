# Hermes Skill Lane Subagents Design

Date: 2026-04-28
Branch: `feat/hermes-skill-lane-subagents`

## Background

The previous `agent-first` attempt was still wrong in an important way: it moved lane execution behind process boundaries, but lane judgment and reader-facing writing were still controlled by Python modules such as `github_trending_agent.py` and generic migration shims. That produced template-like output and preserved the core failure mode: code selected, summarized, and rendered content instead of letting real Hermes lane subagents reason over raw material.

This design replaces that direction. The daily report should be orchestrated by a Hermes master agent. Each lane should be handled by a Hermes subagent that loads a lane-specific skill, reads raw corpus, selects/rejects items, and writes lane markdown. The master only integrates the resulting lane markdown.

## Core Principle

Code prepares and validates materials. Agents judge and write.

Python scripts must not become fake agents. They may normalize files, prepare raw corpus packages, validate output structure, assemble markdown, publish, and archive. They must not decide what is important, summarize items, write reader-facing prose, or launch Hermes subagents.

## Non-Negotiable Rules

1. Python must not launch Hermes subagents.
2. Only the Hermes master agent may call `delegate_task`.
3. Python must not select, rank, summarize, rewrite, or render reader-facing lane content.
4. Each lane's judgment and writing must happen inside a Hermes subagent.
5. Each lane subagent must load a lane-specific skill.
6. Lane-specific helper scripts must live with the skill that uses them.
7. Helper scripts may only prepare/normalize/inspect/validate evidence; they must not produce final reader-facing prose.
8. The master agent may assemble lane markdown, but must not rewrite lane markdown.
9. If a lane subagent fails, the lane is `blocked` or `degraded`; there is no silent fallback to old renderer code.
10. `selected_items.json` may be retained for compatibility/audit, but it is not the primary input for lane judgment.

## Target Runtime Shape

```text
Hermes master agent
  -> load daily-report-master skill
  -> run deterministic prepare scripts to create lane packages
  -> for each lane: delegate_task to a Hermes subagent
       -> subagent loads that lane's skill
       -> subagent reads lane package/raw corpus
       -> subagent selects/rejects items
       -> subagent writes lane.md and lane-meta.json
  -> master reads all lane.md files
  -> master runs deterministic validation scripts
  -> master assembles final report markdown
  -> master publishes/archives/notifies
```

The old shape is explicitly rejected:

```text
Python run_daily_report_flow.py
  -> Python lane registry
  -> Python lane agent
  -> Python summary/rendering
```

## Repository Role

`daily-report-master-agent` becomes a Hermes daily report operating system, not a monolithic Python renderer.

It should contain:

- versioned skill source files;
- deterministic raw-corpus packaging scripts;
- output validation scripts;
- assembly/publish/archive scripts;
- fixtures and tests proving that code does not own lane judgment;
- design docs and feedback ledger.

It should not contain Python implementations that act as lane brains.

## Skill Source Layout

Skills should be versioned in the repo and installable/syncable into Hermes' live skill directory.

Proposed source layout:

```text
skills/
  daily-report-master/
    SKILL.md
    scripts/
      prepare_lane_packages.py
      validate_lane_outputs.py
      assemble_lane_markdown.py
      publish_report.py

  daily-report-lane-weather/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-x-feed/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-x-following/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-reddit/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-hacker-news/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-hacker-news-search/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-claude-code/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-codex/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-openclaw/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-github-ai-projects/
    SKILL.md
    scripts/
      normalize_raw.py
      discover_repos.py
      validate_output.py

  daily-report-lane-github-trending/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-product-hunt/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py

  daily-report-lane-polymarket/
    SKILL.md
    scripts/
      normalize_raw.py
      validate_output.py
```

`discover_repos.py` for GitHub AI Projects may gather evidence, search results, or repo metadata, but it must not decide final selection or write the lane prose. The lane subagent makes that judgment.

## Live Skill Sync

Repo skill sources are authoritative. A deterministic install/sync script should copy them into Hermes' skill directory before running the master workflow.

Example destination:

```text
~/.hermes/skills/productivity/daily-report-master/SKILL.md
~/.hermes/skills/productivity/daily-report-lane-github-trending/SKILL.md
```

The sync step is deterministic infrastructure. It does not run the report and does not start subagents.

## Lane Package Contract

The prepare script creates one directory per lane:

```text
runtime/<date>/lane-packages/<lane>/
  input.md
  context.json
  raw/
    ...source files...
```

`input.md` should be human-readable and optimized for the lane subagent. It may include:

- report date;
- lane name and purpose;
- raw corpus index;
- source links;
- snippets or full source text;
- user preferences relevant to the lane;
- output path requirements.

`context.json` is for deterministic metadata only:

```json
{
  "report_date": "2026-04-26",
  "lane": "github-trending-weekly",
  "input_markdown": ".../input.md",
  "raw_dir": ".../raw",
  "output_markdown": ".../lane.md",
  "output_meta": ".../lane-meta.json",
  "target_item_count": {"min": 3, "max": 7},
  "required_links": true
}
```

## Lane Output Contract

Each lane subagent writes:

```text
runtime/<date>/lane-outputs/<lane>/lane.md
runtime/<date>/lane-outputs/<lane>/lane-meta.json
```

`lane.md` is the reader-facing section and is assembled without rewriting.

`lane-meta.json` is audit metadata:

```json
{
  "lane": "github-trending-weekly",
  "status": "ok",
  "selected_count": 5,
  "rejected_count": 12,
  "sources": [
    {"title": "owner/repo", "url": "https://github.com/owner/repo"}
  ],
  "rejected": [
    {"title": "owner/irrelevant", "reason": "generic AI infra; no coding-agent workflow signal"}
  ],
  "notes": ["why these items matter today"]
}
```

Allowed statuses:

- `ok`
- `empty`
- `degraded`
- `blocked`

## Master Skill Responsibilities

The `daily-report-master` skill tells the Hermes master agent to:

1. sync repo skills into Hermes skill directory if needed;
2. run prepare scripts to create lane packages;
3. delegate all lanes, preferably in parallel where safe;
4. require each subagent to load the matching lane skill;
5. wait for lane outputs;
6. run validation scripts;
7. assemble final markdown in fixed order;
8. publish to Feishu;
9. archive and update feedback ledger;
10. report degraded/blocked lanes without hiding them.

The master skill must explicitly forbid rewriting lane markdown.

## Lane Skill Responsibilities

Each lane skill should define:

- lane mission;
- raw corpus reading order;
- what counts as reportable;
- what must be rejected;
- desired item count;
- Chinese writing style;
- required source-link behavior;
- forbidden phrases and failure modes;
- exact output files.

For example, GitHub Trending should judge whether a repo matters to AI/coding-agent workflows, not whether it merely contains generic AI keywords.

X lanes should produce human paraphrases of original posts: who did what, what changed, what result/blocker/background matters. They must avoid internal collection language.

HN/Reddit lanes should include discussion substance, not just post titles.

Claude Code and Codex lanes should preserve concrete version/change/workflow information.

## Validation Philosophy

Validation should catch structural and obvious quality failures, not rewrite content.

Validations may check:

- `lane.md` exists and is non-empty for `ok` status;
- required links are present;
- no known banned filler phrases;
- `lane-meta.json` parses;
- sources exist for selected items;
- lane did not emit old renderer language;
- output path matches expected lane.

Validation must not:

- select items;
- summarize items;
- replace prose;
- auto-fill missing sections.

## Migration Strategy

Because the user expects option C, all lanes should move to skill/subagent execution in one branch. However, implementation should still be staged internally:

1. create repo skill source layout and sync script;
2. write master skill;
3. write all lane skills;
4. write deterministic package/validate/assemble scripts;
5. run the Hermes master workflow manually from the main session;
6. publish preview;
7. compare against prior preview;
8. only then consider wiring scheduled production execution.

No production default switch until the preview is accepted.

## Acceptance Criteria

A preview is acceptable only if:

1. every lane output was produced by a Hermes subagent that loaded a lane skill;
2. no Python lane agent/renderer selected or wrote reader-facing content;
3. final report is assembled from lane markdown files;
4. master did not rewrite lane sections;
5. `lane-meta.json` records selected/rejected/source evidence;
6. failed lanes are explicitly degraded/blocked;
7. GitHub Trending no longer contains template phrases such as “趋势信息包含这些具体点”;
8. X/HN/Reddit outputs read like human explanations, not collection summaries;
9. GitHub AI Projects runs internal discovery/evidence gathering without using the old shared memory file as an integration point;
10. tests prove the code path cannot silently fall back to old renderer behavior.

## Explicitly Out of Scope For This Branch

- Automatically enabling this as the production default cron flow before user review.
- Using Python scripts as lane brains.
- Preserving the previous `helpers/lane_agents/*.py` approach.
- Shared memory file integration for GitHub AI Projects.
