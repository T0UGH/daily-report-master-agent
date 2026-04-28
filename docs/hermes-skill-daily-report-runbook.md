# Hermes Skill Daily Report Runbook

## Purpose

Run the AI Agent daily report through Hermes master + lane subagents, not Python lane brains.

## Operator Flow

1. Checkout `feat/hermes-skill-lane-subagents`.
2. Run full tests:
   `python3 -m pytest -q`
3. Sync skills:
   `python3 skills/daily-report-master/scripts/sync_skills.py --repo-root .`
4. Load `daily-report-master` skill in the Hermes main session.
5. Prepare lane packages for the target date:
   `python3 skills/daily-report-master/scripts/prepare_lane_packages.py --report-date <date> --signal-root /Users/haha/.daily-lane-data/signals --runtime-root /Users/haha/.daily-lane-data/runtime/daily-report-master/<date>-skill-preview`
6. Use `delegate_task` once per lane, each with the matching lane skill.
7. Ensure each subagent writes `lane.md` and `lane-meta.json`.
8. Validate outputs:
   `python3 skills/daily-report-master/scripts/validate_lane_outputs.py --runtime-root <runtime-root>`
9. Assemble report:
   `python3 skills/daily-report-master/scripts/assemble_lane_markdown.py --runtime-root <runtime-root> --report-date <date> --title-suffix hermes-skill-preview`
10. Publish preview:
   `python3 skills/daily-report-master/scripts/publish_report.py --report-path <runtime-root>/report.md --title 'AI Agent 日报（<date>）hermes-skill-preview'`
11. Verify Feishu document content.
12. Update `docs/report-feedback-ledger.md`.

## Delegate Prompt Template

```text
You are the <lane> lane subagent for AI Agent daily report <date>.
First load skill `<skill-name>`.
Read package `<package-path>`.
Write `<runtime-root>/lane-outputs/<lane>/lane.md` and `<runtime-root>/lane-outputs/<lane>/lane-meta.json`.
Do not ask questions; if evidence is insufficient, write status `empty`, `degraded`, or `blocked` with reasons.
Do not use selected_items.json as primary input.
Do not call old Python lane workers/renderers.
```

## Boundary Rules

- Python does not launch subagents.
- Python does not decide lane selection.
- Python does not write reader-facing lane prose.
- Master does not rewrite `lane.md`.
- Failed lanes are explicit `blocked`/`degraded`, never hidden by fallback.
