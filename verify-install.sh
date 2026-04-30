#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
RUNTIME_HOME="$HERMES_HOME/daily-report-master"
PROMPT_SRC="$REPO_ROOT/main-prompt.md"
PROMPT_DST="$RUNTIME_HOME/main-prompt.md"
CONFIG_DST="$RUNTIME_HOME/runtime.yaml"
JOBS_JSON="$HERMES_HOME/cron/jobs.json"

require_file() {
  local path="$1"
  [[ -f "$path" ]] || { echo "missing file: $path" >&2; exit 1; }
}

require_file "$PROMPT_SRC"
require_file "$PROMPT_DST"
require_file "$CONFIG_DST"
require_file "$JOBS_JSON"

cmp -s "$PROMPT_SRC" "$PROMPT_DST" || {
  echo "prompt mismatch between repo and Hermes runtime" >&2
  exit 1
}

export HERMES_HOME

python3 - <<'PY'
import json
import os
from pathlib import Path
hermes_home = Path(os.environ.get('HERMES_HOME', str(Path.home() / '.hermes')))
jobs = json.loads((hermes_home / 'cron' / 'jobs.json').read_text(encoding='utf-8'))['jobs']
job = next((j for j in jobs if j.get('name') == 'daily-report-master-0600'), None)
if job is None:
    raise SystemExit('cron job daily-report-master-0600 not found')
prompt = job.get('prompt', '')
if 'Daily Report Master Cron Main Prompt' not in prompt:
    raise SystemExit('cron prompt does not appear to be sourced from main-prompt.md')
expected_skills = {
    'daily-report-master-collect-signals',
    'daily-report-master',
    'daily-report-lane-weather',
    'daily-report-lane-x-feed',
    'daily-report-lane-x-following',
    'daily-report-lane-reddit',
    'daily-report-lane-hacker-news',
    'daily-report-lane-hacker-news-search',
    'daily-report-lane-claude-code',
    'daily-report-lane-codex',
    'daily-report-lane-openclaw',
    'daily-report-lane-github-ai-projects',
    'daily-report-lane-github-trending',
    'daily-report-lane-product-hunt',
    'daily-report-lane-polymarket',
}
if set(job.get('skills') or []) != expected_skills:
    raise SystemExit(f'cron skills mismatch: {job.get("skills")!r}')
print('cron-ok', job['id'])
PY

for skill in \
  daily-report-master-collect-signals \
  daily-report-master-assess-reportability \
  daily-report-master-build-report \
  daily-report-master-publish-report \
  daily-report-master-archive-report \
  daily-report-master-notify-ops
  do
    require_file "$HERMES_HOME/skills/productivity/$skill/SKILL.md"
  done

echo "verify-install: ok"
