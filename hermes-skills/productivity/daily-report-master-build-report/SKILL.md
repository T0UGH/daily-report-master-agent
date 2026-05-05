---
name: daily-report-master-build-report
description: Deprecated legacy step skill. Use daily-report-master instead.
---

# Deprecated: Daily Report Master Build Report

This legacy step skill is no longer an executable production path.

Use the current Hermes subagent-controlled master skill instead:

- `skills/daily-report-master/SKILL.md`

Current production flow:

- Hermes master prepares lane packages.
- Hermes master calls `delegate_task` for every lane.
- Lane subagents write `lane.md` and `lane-meta.json`.
- Deterministic scripts validate lane outputs, assemble final markdown, and publish.

Do not use this legacy skill to drive report generation.
