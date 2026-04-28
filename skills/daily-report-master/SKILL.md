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
- The master must not rewrite lane markdown.
- If a lane fails, mark it `blocked` or `degraded`; do not silently fall back to old renderer output.
- `selected_items.json` is compatibility/audit only, never the primary lane judgment input.
## Workflow
1. Sync repo skill sources into Hermes skill directory if necessary.
2. Run `skills/daily-report-master/scripts/prepare_lane_packages.py` to create lane packages.
3. For every lane package, call `delegate_task` with the matching lane skill.
4. In each delegated task, require the lane subagent to load its skill, read `input.md`, inspect raw files, and write `lane.md` plus `lane-meta.json`.
5. Wait for all lane outputs.
6. Run `skills/daily-report-master/scripts/validate_lane_outputs.py`.
7. Run `skills/daily-report-master/scripts/assemble_lane_markdown.py`.
8. Publish using `publish_report.py` or existing Feishu tools.
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
