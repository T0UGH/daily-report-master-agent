import json, pytest
from pathlib import Path
from skills.daily_report_master.scripts.validate_lane_outputs import ValidationError, validate_lane_output_dir
def write_output(root: Path, lane: str, markdown: str, meta: dict):
    out=root/'lane-outputs'/lane; out.mkdir(parents=True); (out/'lane.md').write_text(markdown,encoding='utf-8'); (out/'lane-meta.json').write_text(json.dumps(meta,ensure_ascii=False),encoding='utf-8'); return out
def test_validate_accepts_human_lane_output(tmp_path):
    out=write_output(tmp_path,'github-trending','## GitHub 趋势项目\n\n- **owner/repo**：这是一个 Claude Code workflow 项目，今天值得看是因为它解决了本地模型接入问题。 [GitHub](https://github.com/owner/repo)',{'lane':'github-trending','status':'ok','selected_count':1,'rejected_count':1,'sources':[{'title':'owner/repo','url':'https://github.com/owner/repo'}],'rejected':[],'notes':[]})
    validate_lane_output_dir(out)
def test_validate_rejects_template_phrases(tmp_path):
    out=write_output(tmp_path,'github-trending','## GitHub 趋势项目\n\n- owner/repo 的趋势信息包含这些具体点：foo。 [GitHub](https://github.com/owner/repo)',{'lane':'github-trending','status':'ok','selected_count':1,'rejected_count':0,'sources':[{'title':'owner/repo','url':'https://github.com/owner/repo'}],'rejected':[],'notes':[]})
    with pytest.raises(ValidationError, match='forbidden phrase'): validate_lane_output_dir(out)
def test_validate_rejects_ok_without_sources(tmp_path):
    out=write_output(tmp_path,'x-feed','## X 推荐\n\n- 有人分享了 Claude Code 工作流经验。',{'lane':'x-feed','status':'ok','selected_count':1,'rejected_count':0,'sources':[],'rejected':[],'notes':[]})
    with pytest.raises(ValidationError, match='sources'): validate_lane_output_dir(out)
