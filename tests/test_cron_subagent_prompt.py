from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cron_prompt_requires_hermes_lane_subagents() -> None:
    prompt = (REPO_ROOT / "main-prompt.md").read_text(encoding="utf-8")

    assert "delegate_task" in prompt
    assert "Hermes 原生 subagent lane 架构" in prompt
    assert "不得运行 `helpers/run_daily_report_flow.py`" in prompt
    assert "prepare_lane_packages.py" in prompt
    assert "validate_lane_outputs.py" in prompt
    assert "assemble_lane_markdown.py" in prompt


def test_install_syncs_subagent_skills_to_cron() -> None:
    install_script = (REPO_ROOT / "install.sh").read_text(encoding="utf-8")

    assert 'SKILL_SRC_ROOT="$REPO_ROOT/skills"' in install_script
    assert "'daily-report-master'" in install_script
    assert "'daily-report-lane-x-feed'" in install_script
    assert "'daily-report-lane-github-ai-projects'" in install_script
    assert "'daily-report-master-build-report'" not in install_script
    assert "'daily-report-master-collect-signals'" not in install_script
