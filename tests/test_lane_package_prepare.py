import json
from skills.daily_report_master.scripts.prepare_lane_packages import prepare_lane_packages
def test_prepare_lane_packages_reads_signal_files_not_selected_items(tmp_path):
    lane_dir=tmp_path/'signals'/'x-feed'/'2026-04-26'/'signals'; lane_dir.mkdir(parents=True); (lane_dir/'001.md').write_text('# Tweet\nClaude Code workflow changed.\nhttps://x.com/a/status/1',encoding='utf-8')
    selected=tmp_path/'selected_items.json'; selected.write_text(json.dumps({'items':[{'title':'SHOULD NOT BE PRIMARY'}]}),encoding='utf-8')
    packages=prepare_lane_packages('2026-04-26',tmp_path/'signals',tmp_path/'runtime',selected)
    text=(packages['x-feed']/'input.md').read_text(encoding='utf-8'); context=json.loads((packages['x-feed']/'context.json').read_text(encoding='utf-8'))
    assert 'Claude Code workflow changed' in text; assert 'SHOULD NOT BE PRIMARY' not in text; assert context['selected_items_mode']=='audit_only'; assert context['output_markdown'].endswith('lane.md'); assert context['output_meta'].endswith('lane-meta.json')
def test_prepare_lane_packages_marks_missing_raw_corpus(tmp_path):
    packages=prepare_lane_packages('2026-04-26',tmp_path/'signals',tmp_path/'runtime',None)
    context=json.loads((packages['github-ai-projects']/'context.json').read_text(encoding='utf-8'))
    assert context['raw_corpus_status'] in {'missing','degraded'}
