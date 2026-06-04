from skills.daily_report_master.scripts.sync_skills import discover_skill_dirs, sync_skills
def test_discover_skill_dirs_returns_repo_skills(tmp_path):
    (tmp_path/'skills'/'daily-report-master').mkdir(parents=True); (tmp_path/'skills'/'daily-report-master'/'SKILL.md').write_text('master')
    (tmp_path/'skills'/'daily-report-lane-x-feed').mkdir(parents=True); (tmp_path/'skills'/'daily-report-lane-x-feed'/'SKILL.md').write_text('lane')
    assert [p.name for p in discover_skill_dirs(tmp_path)] == ['daily-report-lane-x-feed','daily-report-master']
def test_sync_skills_copies_skill_trees_to_destination(tmp_path):
    root=tmp_path/'repo'; source=root/'skills'/'daily-report-lane-x-feed'; source.mkdir(parents=True); (source/'SKILL.md').write_text('skill'); (source/'scripts').mkdir(); (source/'scripts'/'normalize_raw.py').write_text("print('ok')")
    dest=tmp_path/'hermes'/'skills'/'productivity'; synced=sync_skills(root,dest)
    assert synced == ['daily-report-lane-x-feed']; assert (dest/'daily-report-lane-x-feed'/'SKILL.md').read_text()=='skill'; assert (dest/'daily-report-lane-x-feed'/'scripts'/'normalize_raw.py').exists()

def test_synced_master_wrappers_import_from_productivity_destination(tmp_path, monkeypatch):
    root = tmp_path / 'repo'
    source = root / 'skills' / 'daily-report-master'
    canonical = root / 'skills' / 'daily_report_master' / 'scripts'
    wrapper_dir = source / 'scripts'
    canonical.mkdir(parents=True)
    wrapper_dir.mkdir(parents=True)
    (source / 'SKILL.md').write_text('master')
    (root / 'skills' / 'daily_report_master' / '__init__.py').write_text('')
    (canonical / '__init__.py').write_text('')
    (canonical / 'sample.py').write_text('def main():\n    return 0\n')
    (wrapper_dir / 'sample.py').write_text(
        "from pathlib import Path\n"
        "import sys\n\n"
        "_ROOT = Path(__file__).resolve().parents[3]\n"
        "sys.path.insert(0, str(_ROOT))\n"
        "try:\n"
        "    from skills.daily_report_master.scripts.sample import main\n"
        "except ModuleNotFoundError as exc:\n"
        "    if not (exc.name == 'skills' or str(exc.name).startswith('skills.daily_report_master')):\n"
        "        raise\n"
        "    from productivity.daily_report_master.scripts.sample import main\n"
    )
    dest = tmp_path / 'hermes' / 'skills' / 'productivity'
    sync_skills(root, dest)
    # Simulate the underscore canonical package also being installed under the category.
    import shutil
    shutil.copytree(root / 'skills' / 'daily_report_master', dest / 'daily_report_master')
    monkeypatch.syspath_prepend(str(tmp_path / 'hermes' / 'skills'))
    import runpy
    ns = runpy.run_path(str(dest / 'daily-report-master' / 'scripts' / 'sample.py'))
    assert ns['main']() == 0

