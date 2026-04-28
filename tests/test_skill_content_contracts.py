from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SKILLS = ["daily-report-master","daily-report-lane-weather","daily-report-lane-x-feed","daily-report-lane-x-following","daily-report-lane-reddit","daily-report-lane-hacker-news","daily-report-lane-hacker-news-search","daily-report-lane-claude-code","daily-report-lane-codex","daily-report-lane-openclaw","daily-report-lane-github-ai-projects","daily-report-lane-github-trending","daily-report-lane-product-hunt","daily-report-lane-polymarket"]
FORBIDDEN_IN_SKILLS = ["Python decides what to select", "use selected_items as primary input", "fallback to renderer"]
def read_skill(name: str) -> str:
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
def test_all_required_skill_files_exist():
    for name in SKILLS:
        assert (ROOT / "skills" / name / "SKILL.md").exists(), name
def test_master_skill_declares_delegate_task_as_agent_only():
    text = read_skill("daily-report-master")
    assert "delegate_task" in text
    assert "Only the Hermes master agent may call delegate_task" in text
    assert "Python must not launch Hermes subagents" in text
    assert "must not rewrite lane markdown" in text
def test_lane_skills_require_markdown_and_meta_outputs():
    for name in SKILLS:
        if name == "daily-report-master": continue
        text = read_skill(name)
        assert "lane.md" in text, name
        assert "lane-meta.json" in text, name
        assert "selected" in text.lower(), name
        assert "rejected" in text.lower(), name
        assert "sources" in text.lower(), name
        assert "禁止" in text or "Forbidden" in text, name
def test_skills_do_not_authorize_python_lane_brains():
    for name in SKILLS:
        text = read_skill(name)
        for forbidden in FORBIDDEN_IN_SKILLS:
            assert forbidden not in text, f"{name} contains {forbidden!r}"
def test_github_trending_skill_rejects_generic_ai_infra():
    text = read_skill("daily-report-lane-github-trending")
    assert "generic AI infra" in text
    assert "coding-agent" in text
    assert "why an AI/coding-agent reader should care" in text
def test_x_skills_require_human_paraphrase():
    for name in ["daily-report-lane-x-feed", "daily-report-lane-x-following"]:
        text = read_skill(name)
        assert "human paraphrase" in text
        assert "who did what" in text
        assert "internal collector voice" in text
def test_hn_reddit_skills_require_discussion_substance():
    for name in ["daily-report-lane-reddit", "daily-report-lane-hacker-news", "daily-report-lane-hacker-news-search"]:
        text = read_skill(name)
        assert "discussion substance" in text
        assert "title-only" in text
def test_github_ai_projects_skill_forbids_shared_memory_integration():
    text = read_skill("daily-report-lane-github-ai-projects")
    assert "old shared memory" in text
    assert "discovery" in text
    assert "evidence" in text
