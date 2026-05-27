from skills.daily_report_master.scripts.assemble_lane_markdown import assemble_report
def test_assemble_report_concatenates_lane_markdown_without_rewrite(tmp_path):
    runtime=tmp_path/'runtime'
    for lane,body in [('weather','## 天气\n\n北京晴。'),('x-feed','## X 推荐\n\n- 原样保留这一句 [原帖](https://x.com/a/status/1)')]:
        out=runtime/'lane-outputs'/lane; out.mkdir(parents=True); (out/'lane.md').write_text(body,encoding='utf-8')
    report=assemble_report(runtime,'2026-04-26','skill-preview'); text=report.read_text(encoding='utf-8')
    assert text.startswith('# AI Agent 日报（2026-04-26）skill-preview'); assert '北京晴。' in text; assert '原样保留这一句' in text; assert text.index('## 天气') < text.index('## X 推荐')
def test_assemble_report_skips_missing_lane_with_note(tmp_path):
    runtime=tmp_path/'runtime'; out=runtime/'lane-outputs'/'weather'; out.mkdir(parents=True); (out/'lane.md').write_text('## 天气\n\n北京晴。',encoding='utf-8')
    text=assemble_report(runtime,'2026-04-26').read_text(encoding='utf-8'); assert '## 天气' in text; assert '未生成' in text


def test_assemble_report_ignores_openclaw_lane_by_default(tmp_path):
    runtime=tmp_path/'runtime'
    openclaw=runtime/'lane-outputs'/'openclaw'
    openclaw.mkdir(parents=True)
    (openclaw/'lane.md').write_text('## OpenClaw\n- should not publish by default',encoding='utf-8')
    report=assemble_report(runtime,'2026-05-28')
    text=report.read_text(encoding='utf-8')
    assert '## OpenClaw' not in text
