from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DETERMINISTIC_SCRIPT_ROOTS=[ROOT/'skills'/'daily_report_master'/'scripts', ROOT/'skills'/'daily-report-master'/'scripts']
FORBIDDEN_SNIPPETS=['delegate_task(','_summary(','build_lane_output(','run_lane_subagent(','github_trending_worker','github_ai_projects_worker','selected_items as primary']
def test_deterministic_scripts_do_not_launch_or_render_agents():
    for root in DETERMINISTIC_SCRIPT_ROOTS:
        if not root.exists(): continue
        for path in root.rglob('*.py'):
            text=path.read_text(encoding='utf-8')
            for snippet in FORBIDDEN_SNIPPETS: assert snippet not in text, f'{path} contains forbidden snippet {snippet!r}'
def test_master_skill_is_the_only_place_that_mentions_delegate_task():
    master=ROOT/'skills'/'daily-report-master'/'SKILL.md'; assert 'delegate_task' in master.read_text(encoding='utf-8')
    for path in (ROOT/'skills').rglob('*.py'): assert 'delegate_task' not in path.read_text(encoding='utf-8'), path
