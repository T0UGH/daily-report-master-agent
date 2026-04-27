from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
LANES=['weather','x-feed','x-following','reddit','hacker-news','hacker-news-search','claude-code','codex','openclaw','github-ai-projects','github-trending','product-hunt','polymarket']
SIGNAL_LANE_MAP={'weather':'weather-watch','x-feed':'x-feed','x-following':'x-following','reddit':'reddit-watch','hacker-news':'hacker-news-watch','hacker-news-search':'hacker-news-search-watch','claude-code':'claude-code-watch','codex':'codex-watch','openclaw':'openclaw-watch','github-ai-projects':'github-ai-projects','github-trending':'github-trending-weekly','product-hunt':'product-hunt-watch','polymarket':'polymarket-watch'}
LANE_SKILL_MAP={lane:f'daily-report-lane-{lane}' for lane in LANES}

def _source_dir(signal_root: Path, signal_lane: str, report_date: str) -> Path:
    base=signal_root/signal_lane/report_date
    return base/'signals' if (base/'signals').exists() else base

def prepare_lane_packages(report_date: str, signal_root: Path, runtime_root: Path, selected_items_path: Path|None=None) -> dict[str, Path]:
    packages={}; pkg_root=runtime_root/'lane-packages'; out_root=runtime_root/'lane-outputs'; pkg_root.mkdir(parents=True, exist_ok=True); out_root.mkdir(parents=True, exist_ok=True)
    for lane in LANES:
        package=pkg_root/lane; raw=package/'raw'; output=out_root/lane
        if package.exists(): shutil.rmtree(package)
        raw.mkdir(parents=True); output.mkdir(parents=True, exist_ok=True)
        src=_source_dir(signal_root, SIGNAL_LANE_MAP[lane], report_date)
        files=[]
        if src.exists():
            for f in sorted(p for p in src.rglob('*') if p.is_file()):
                rel=f.relative_to(src); dest=raw/rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f,dest); files.append(dest)
        status='ok' if files else ('degraded' if lane=='github-ai-projects' else 'missing')
        context={'report_date':report_date,'lane':lane,'signal_lane':SIGNAL_LANE_MAP[lane],'skill':LANE_SKILL_MAP[lane],'raw_dir':str(raw),'raw_corpus_status':status,'raw_file_count':len(files),'output_markdown':str(output/'lane.md'),'output_meta':str(output/'lane-meta.json'),'selected_items_path':str(selected_items_path) if selected_items_path else None,'selected_items_mode':'audit_only'}
        (package/'context.json').write_text(json.dumps(context,ensure_ascii=False,indent=2),encoding='utf-8')
        index='\n'.join(f'- raw/{f.relative_to(raw)}' for f in files[:200]) or '- No raw files found.'
        sample=[]
        for f in files[:20]:
            txt=f.read_text(encoding='utf-8',errors='ignore')[:2500]
            sample.append(f'\n### raw/{f.relative_to(raw)}\n\n```text\n{txt}\n```')
        sample_text = ''.join(sample)
        (package/'input.md').write_text(f"""# Lane Package: {lane}\n\nReport date: {report_date}\nSkill: {LANE_SKILL_MAP[lane]}\nRaw corpus status: {status}\n\nUse raw corpus as primary evidence. `selected_items.json` is audit-only and must not drive judgment.\n\nWrite output files exactly:\n- {output/'lane.md'}\n- {output/'lane-meta.json'}\n\n## Raw file index\n{index}\n\n## Raw excerpts\n{sample_text}\n""",encoding='utf-8')
        packages[lane]=package
    return packages

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--report-date',required=True); ap.add_argument('--signal-root',type=Path,default=Path.home()/'.daily-lane-data'/'signals'); ap.add_argument('--runtime-root',type=Path,required=True); ap.add_argument('--selected-items-path',type=Path)
    a=ap.parse_args(); packages=prepare_lane_packages(a.report_date,a.signal_root.expanduser(),a.runtime_root.expanduser(),a.selected_items_path)
    print(json.dumps({k:str(v) for k,v in packages.items()},ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
