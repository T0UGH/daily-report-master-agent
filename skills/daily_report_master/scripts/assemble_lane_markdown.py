from __future__ import annotations
import argparse
from pathlib import Path
LANES=['weather','x-feed','x-following','reddit','hacker-news','hacker-news-search','claude-code','codex','openclaw','github-ai-projects','github-trending','rize','product-hunt','polymarket']
def assemble_report(runtime_root: Path, report_date: str, title_suffix: str='') -> Path:
    title=f'# AI Agent 日报（{report_date}）' + (f'{title_suffix}' if title_suffix else '')
    parts=[title,'']
    missing=[]
    for lane in LANES:
        md=runtime_root/'lane-outputs'/lane/'lane.md'
        if md.exists(): parts.append(md.read_text(encoding='utf-8').strip()); parts.append('')
        else: missing.append(lane)
    if missing:
        parts += ['## 运维提示','', '以下 lane 未生成：' + ', '.join(missing), '']
    report=runtime_root/'report.md'; report.parent.mkdir(parents=True, exist_ok=True); report.write_text('\n'.join(parts).rstrip()+'\n',encoding='utf-8'); return report
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--runtime-root',type=Path,required=True); ap.add_argument('--report-date',required=True); ap.add_argument('--title-suffix',default='')
    a=ap.parse_args(); print(assemble_report(a.runtime_root,a.report_date,a.title_suffix)); return 0
if __name__=='__main__': raise SystemExit(main())
