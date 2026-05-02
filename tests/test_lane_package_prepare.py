import json
from skills.daily_report_master.scripts.prepare_lane_packages import prepare_lane_packages

def test_prepare_lane_packages_reads_signal_files_not_selected_items(tmp_path):
    lane_dir=tmp_path/'signals'/'x-feed'/'2026-04-26'/'signals'; lane_dir.mkdir(parents=True); (lane_dir/'001.md').write_text('# Tweet\nClaude Code workflow changed.\nhttps://x.com/a/status/1',encoding='utf-8')
    selected=tmp_path/'selected_items.json'; selected.write_text(json.dumps({'items':[{'title':'SHOULD NOT BE PRIMARY'},{'title':'Claude Code workflow changed.'}]}),encoding='utf-8')
    packages=prepare_lane_packages('2026-04-26',tmp_path/'signals',tmp_path/'runtime',selected)
    text=(packages['x-feed']/'input.md').read_text(encoding='utf-8'); context=json.loads((packages['x-feed']/'context.json').read_text(encoding='utf-8'))
    assert 'Claude Code workflow changed' in text; assert 'SHOULD NOT BE PRIMARY' not in text; assert context['selected_items_mode']=='audit_only'; assert context['output_markdown'].endswith('lane.md'); assert context['output_meta'].endswith('lane-meta.json')

def test_prepare_lane_packages_marks_missing_raw_corpus(tmp_path):
    packages=prepare_lane_packages('2026-04-26',tmp_path/'signals',tmp_path/'runtime',None)
    context=json.loads((packages['github-ai-projects']/'context.json').read_text(encoding='utf-8'))
    assert context['raw_corpus_status'] in {'missing','degraded'}


def test_prepare_lane_packages_reads_nested_signals_root(tmp_path):
    lane_dir=tmp_path/'signals'/'signals'/'weather-watch'/'2026-04-26'/'signals'
    lane_dir.mkdir(parents=True)
    (lane_dir/'weather.md').write_text('北京天气',encoding='utf-8')

    packages=prepare_lane_packages('2026-04-26',tmp_path/'signals',tmp_path/'runtime',None)

    context=json.loads((packages['weather']/'context.json').read_text(encoding='utf-8'))
    text=(packages['weather']/'input.md').read_text(encoding='utf-8')
    assert context['raw_corpus_status']=='ok'
    assert context['raw_file_count']==1
    assert '北京天气' in text


def test_prepare_lane_packages_prefers_candidate_with_files(tmp_path):
    empty_dir=tmp_path/'signals'/'x-feed'/'2026-04-26'/'signals'
    empty_dir.mkdir(parents=True)
    nested_dir=tmp_path/'signals'/'signals'/'x-feed'/'2026-04-26'/'signals'
    nested_dir.mkdir(parents=True)
    (nested_dir/'tweet.md').write_text('nested x signal',encoding='utf-8')

    packages=prepare_lane_packages('2026-04-26',tmp_path/'signals',tmp_path/'runtime',None)

    context=json.loads((packages['x-feed']/'context.json').read_text(encoding='utf-8'))
    text=(packages['x-feed']/'input.md').read_text(encoding='utf-8')
    assert context['raw_corpus_status']=='ok'
    assert context['raw_file_count']==1
    assert 'nested x signal' in text

def test_prepare_lane_packages_copies_recent_reports_for_agent_dedup_reference(tmp_path):
    (tmp_path/'2026-04-25').mkdir()
    (tmp_path/'2026-04-25'/'report.md').write_text('# 2026-04-25\nYesterday report topic',encoding='utf-8')
    (tmp_path/'2026-04-25'/'run-summary.json').write_text(json.dumps({'publish':{'doc_url':'https://www.feishu.cn/docx/YESTERDAY'}}),encoding='utf-8')
    (tmp_path/'2026-04-24').mkdir()
    (tmp_path/'2026-04-24'/'report.md').write_text('# 2026-04-24\nDay before report topic',encoding='utf-8')
    (tmp_path/'2026-04-24'/'run-summary.json').write_text(json.dumps({'doc_url':'https://www.feishu.cn/docx/DAYBEFORE'}),encoding='utf-8')
    (tmp_path/'2026-04-23').mkdir()
    (tmp_path/'2026-04-23'/'report.md').write_text('# 2026-04-23\nToo old topic',encoding='utf-8')

    packages=prepare_lane_packages('2026-04-26',tmp_path/'signals',tmp_path/'runtime',None)

    package=packages['x-feed']
    yesterday=package/'history'/'2026-04-25-report.md'
    day_before=package/'history'/'2026-04-24-report.md'
    assert yesterday.read_text(encoding='utf-8')=='# 2026-04-25\nYesterday report topic'
    assert day_before.read_text(encoding='utf-8')=='# 2026-04-24\nDay before report topic'
    assert not (package/'history'/'2026-04-23-report.md').exists()

    context=json.loads((package/'context.json').read_text(encoding='utf-8'))
    assert context['recent_report_mode']=='agent_dedup_reference_only'
    assert context['recent_report_paths']==[str(yesterday),str(day_before)]
    assert context['recent_report_urls']==['https://www.feishu.cn/docx/YESTERDAY','https://www.feishu.cn/docx/DAYBEFORE']
    assert context['recent_reports']==[
        {'date':'2026-04-25','path':str(yesterday),'source_path':str(tmp_path/'2026-04-25'/'report.md'),'doc_url':'https://www.feishu.cn/docx/YESTERDAY'},
        {'date':'2026-04-24','path':str(day_before),'source_path':str(tmp_path/'2026-04-24'/'report.md'),'doc_url':'https://www.feishu.cn/docx/DAYBEFORE'},
    ]

    text=(package/'input.md').read_text(encoding='utf-8')
    assert 'Read yesterday and day-before-yesterday reports before selecting or writing' in text
    assert 'history/2026-04-25-report.md' in text
    assert 'history/2026-04-24-report.md' in text
    assert 'https://www.feishu.cn/docx/YESTERDAY' in text
    assert 'https://www.feishu.cn/docx/DAYBEFORE' in text
    assert str(tmp_path/'2026-04-25'/'report.md') in text
    assert str(tmp_path/'2026-04-24'/'report.md') in text
    assert 'if a copy is missing or unclear, use the source file paths and published doc URLs' in text
    assert 'reject exact repeats or substantially unchanged topics' in text
    assert 'do not dedupe weather/current market items purely because yesterday had the same section' in text
    assert 'agent judgment, not code-controlled filtering' in text
