#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
RUNTIME_HOME="$HERMES_HOME/daily-report-master"
SKILL_SRC_ROOT="$REPO_ROOT/skills"
SKILL_DST_ROOT="$HERMES_HOME/skills/productivity"
PROMPT_SRC="$REPO_ROOT/main-prompt.md"
CONFIG_SRC="$REPO_ROOT/config/runtime.yaml"

mkdir -p "$RUNTIME_HOME" "$SKILL_DST_ROOT"
cp "$PROMPT_SRC" "$RUNTIME_HOME/main-prompt.md"
cp "$CONFIG_SRC" "$RUNTIME_HOME/runtime.yaml"

while IFS= read -r -d '' skill_dir; do
  skill_name="$(basename "$skill_dir")"
  rm -rf "$SKILL_DST_ROOT/$skill_name"
  mkdir -p "$SKILL_DST_ROOT/$skill_name"
  cp -R "$skill_dir"/. "$SKILL_DST_ROOT/$skill_name"/
done < <(find "$SKILL_SRC_ROOT" -mindepth 1 -maxdepth 1 -type d -print0)

export REPO_ROOT HERMES_HOME

python3 - <<'PY'
import json
import os
import subprocess
from pathlib import Path
import yaml

repo_root = Path(os.environ['REPO_ROOT'])
hermes_home = Path(os.environ.get('HERMES_HOME', str(Path.home() / '.hermes')))
prompt = (repo_root / 'main-prompt.md').read_text(encoding='utf-8')
config = yaml.safe_load((repo_root / 'config' / 'runtime.yaml').read_text(encoding='utf-8'))
runtime = config['runtime']
skill_names = [
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
]
job_name = runtime['cron_job_name']
schedule = runtime['cron_schedule']
deliver = runtime['cron_deliver']
jobs_json = hermes_home / 'cron' / 'jobs.json'
job_id = None
if jobs_json.is_file():
    jobs = json.loads(jobs_json.read_text(encoding='utf-8')).get('jobs', [])
    for job in jobs:
        if job.get('name') == job_name:
            job_id = job.get('id')
            break
if job_id:
    cmd = ['hermes', 'cron', 'edit', job_id, '--prompt', prompt, '--schedule', schedule, '--deliver', deliver]
    for skill in skill_names:
        cmd.extend(['--skill', skill])
else:
    cmd = ['hermes', 'cron', 'create', schedule, prompt, '--name', job_name, '--deliver', deliver]
    for skill in skill_names:
        cmd.extend(['--skill', skill])
subprocess.run(cmd, check=True)
print('cron-installed', job_id or 'created')
PY

echo "install: synced runtime prompt/config, Hermes skills, and cron job"
