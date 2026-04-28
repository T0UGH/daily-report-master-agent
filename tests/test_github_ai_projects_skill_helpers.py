from skills.daily_report_lane_github_ai_projects.scripts.discover_repos import build_query_list, write_discovery_bundle
def test_build_query_list_formats_date():
    q=build_query_list('2026-04-26'); assert 'GitHub trending AI 2026-04-26' in q; assert 'GitHub new AI projects 2026-04-26' in q; assert 'awesome AI GitHub 2026-04-26' in q
def test_write_discovery_bundle_writes_evidence_not_selection(tmp_path):
    out=write_discovery_bundle('2026-04-26',tmp_path,search_results=[{'title':'owner/repo','url':'https://github.com/owner/repo','snippet':'agent workflow'}]); text=out.read_text(encoding='utf-8')
    assert 'Candidate evidence' in text; assert 'selected' not in text.lower(); assert 'final summary' not in text.lower()
