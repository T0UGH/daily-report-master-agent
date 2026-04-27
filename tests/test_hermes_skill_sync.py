from skills.daily_report_master.scripts.sync_skills import discover_skill_dirs, sync_skills
def test_discover_skill_dirs_returns_repo_skills(tmp_path):
    (tmp_path/'skills'/'daily-report-master').mkdir(parents=True); (tmp_path/'skills'/'daily-report-master'/'SKILL.md').write_text('master')
    (tmp_path/'skills'/'daily-report-lane-x-feed').mkdir(parents=True); (tmp_path/'skills'/'daily-report-lane-x-feed'/'SKILL.md').write_text('lane')
    assert [p.name for p in discover_skill_dirs(tmp_path)] == ['daily-report-lane-x-feed','daily-report-master']
def test_sync_skills_copies_skill_trees_to_destination(tmp_path):
    root=tmp_path/'repo'; source=root/'skills'/'daily-report-lane-x-feed'; source.mkdir(parents=True); (source/'SKILL.md').write_text('skill'); (source/'scripts').mkdir(); (source/'scripts'/'normalize_raw.py').write_text("print('ok')")
    dest=tmp_path/'hermes'/'skills'/'productivity'; synced=sync_skills(root,dest)
    assert synced == ['daily-report-lane-x-feed']; assert (dest/'daily-report-lane-x-feed'/'SKILL.md').read_text()=='skill'; assert (dest/'daily-report-lane-x-feed'/'scripts'/'normalize_raw.py').exists()
