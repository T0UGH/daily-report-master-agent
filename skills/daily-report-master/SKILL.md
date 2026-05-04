---
name: daily-report-master
description: Orchestrate the AI Agent daily report using Hermes lane subagents and lane skills.
---
# Daily Report Master
## Mission
You are the Hermes master agent for the AI Agent daily report. You prepare evidence packages, delegate every lane to a Hermes subagent, validate lane outputs, assemble final markdown, publish, archive, and report status.
## Non-Negotiable Rules
- Only the Hermes master agent may call delegate_task (`delegate_task`).
- Python must not launch Hermes subagents.
- Python must not select, rank, summarize, rewrite, or render reader-facing lane content.
- Python may copy prior `report.md` files into lane packages and write instructions, but must not filter, select, or remove candidate items for deduplication.
- The master must not rewrite lane markdown.
- If a lane fails, mark it `blocked` or `degraded`; do not silently fall back to old renderer output.
- `selected_items.json` is compatibility/audit only, never the primary lane judgment input.
- Recent reports in lane package `history/` are reference-only dedupe context. Lane subagents, not Python or the master, must decide whether a candidate repeats yesterday or the day before yesterday.
## Workflow
1. Sync repo skill sources into Hermes skill directory if necessary.
2. Run deterministic signal collection/diagnose/retry for the report date before packaging. Do not assume same-day signals already exist; collect must happen in the same master run and only produce raw evidence.
3. Run `skills/daily-report-master/scripts/prepare_lane_packages.py` to create lane packages.
4. For every lane package, call `delegate_task` with the matching lane skill.
5. In each delegated task, require the lane subagent to load its skill, read `input.md`, inspect raw files, read any recent report paths listed in `context.json`, and write `lane.md` plus `lane-meta.json`.
6. Wait for all lane outputs.
7. Run `skills/daily-report-master/scripts/validate_lane_outputs.py`.
8. Run `skills/daily-report-master/scripts/assemble_lane_markdown.py`.
9. Publish using `publish_report.py` or existing Feishu tools.
10. Archive and update `docs/report-feedback-ledger.md`.
11. Report links, degraded lanes, and commit hash.

## Operational Lessons
- If most lane packages show `raw_corpus_status: missing` / `raw_file_count: 0`, first audit whether collect ran before package preparation and compare package timestamps with same-day signal file timestamps.
- `signals-engine` has used both `~/.daily-lane-data/signals/<lane>/<date>/signals` and `~/.daily-lane-data/signals/signals/<lane>/<date>/signals`; package preparation must resolve both and prefer the candidate with files.
- A collect result with useful item counts but empty lane packages is a packaging/data-root bug, not normal content scarcity and not a subagent-writing problem.
- On reruns, clear or quarantine existing `lane-outputs/*` after `prepare_lane_packages.py` and before `delegate_task`; otherwise stale `lane.md`/`lane-meta.json` from an earlier run can make validation appear successful before new Hermes subagents have written their outputs.
- Hermes `delegate_task` may have a low concurrency cap (observed max 3). Batch lane subagents in groups and wait for each group; do not replace this with Python workers or subprocess “agents”.
- `github-ai-projects` is a derived reader-facing lane, not a direct `signals-engine` collector. Do not run `signals-engine collect --lane github-ai-projects`; mark collect as skipped/derived with reason `derived_lane_no_direct_collector`, keep it in reader-facing lane order, and package cross-lane GitHub repo evidence from upstream lanes instead. Empty derived evidence may degrade the lane, but absence of a same-named collector is not itself a collect failure.

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
