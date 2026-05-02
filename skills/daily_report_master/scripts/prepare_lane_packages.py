from __future__ import annotations
import argparse, json, shutil
from datetime import date, timedelta
from pathlib import Path
LANES=['weather','x-feed','x-following','reddit','hacker-news','hacker-news-search','claude-code','codex','openclaw','github-ai-projects','github-trending','product-hunt','polymarket']
SIGNAL_LANE_MAP={'weather':'weather-watch','x-feed':'x-feed','x-following':'x-following','reddit':'reddit-watch','hacker-news':'hacker-news-watch','hacker-news-search':'hacker-news-search-watch','claude-code':'claude-code-watch','codex':'codex-watch','openclaw':'openclaw-watch','github-ai-projects':'github-ai-projects','github-trending':'github-trending-weekly','product-hunt':'product-hunt-watch','polymarket':'polymarket-watch'}
LANE_SKILL_MAP={lane:f'daily-report-lane-{lane}' for lane in LANES}

def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob('*') if p.is_file())


def _source_dir(signal_root: Path, signal_lane: str, report_date: str) -> Path:
    """Resolve the raw signal directory for a lane/date.

    `signals-engine` has run with two data-root conventions in production:
    - <root>/<lane>/<date>/signals
    - <root>/signals/<lane>/<date>/signals

    Package preparation must tolerate both, otherwise collect can succeed while
    lane packages are empty. Prefer the candidate that actually contains files.
    """
    candidates=[]
    for root in (signal_root, signal_root/'signals'):
        base=root/signal_lane/report_date
        candidates.append(base/'signals' if (base/'signals').exists() else base)
    existing=[p for p in candidates if p.exists()]
    if not existing:
        return candidates[0]
    return max(existing, key=_count_files)

def _recent_report_doc_url(report_dir: Path) -> str | None:
    summary_path=report_dir/'run-summary.json'
    if not summary_path.exists():
        return None
    try:
        data=json.loads(summary_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError,OSError):
        return None
    publish=data.get('publish') if isinstance(data,dict) else None
    if isinstance(publish,dict) and isinstance(publish.get('doc_url'),str):
        return publish['doc_url']
    if isinstance(data,dict) and isinstance(data.get('doc_url'),str):
        return data['doc_url']
    return None

def _recent_report_sources(report_date: str, history_root: Path) -> list[dict[str, str]]:
    current=date.fromisoformat(report_date)
    reports=[]
    for days_back in (1,2):
        recent_date=(current-timedelta(days=days_back)).isoformat()
        report_dir=history_root/recent_date
        report=report_dir/'report.md'
        if report.exists():
            entry={'date':recent_date,'path':str(report)}
            doc_url=_recent_report_doc_url(report_dir)
            if doc_url:
                entry['doc_url']=doc_url
            reports.append(entry)
    return reports

def prepare_lane_packages(report_date: str, signal_root: Path, runtime_root: Path, selected_items_path: Path|None=None) -> dict[str, Path]:
    packages={}; pkg_root=runtime_root/'lane-packages'; out_root=runtime_root/'lane-outputs'; pkg_root.mkdir(parents=True, exist_ok=True); out_root.mkdir(parents=True, exist_ok=True)
    recent_reports=_recent_report_sources(report_date,runtime_root.parent)
    for lane in LANES:
        package=pkg_root/lane; raw=package/'raw'; history=package/'history'; output=out_root/lane
        if package.exists(): shutil.rmtree(package)
        raw.mkdir(parents=True); output.mkdir(parents=True, exist_ok=True)
        src=_source_dir(signal_root, SIGNAL_LANE_MAP[lane], report_date)
        files=[]
        if src.exists():
            for f in sorted(p for p in src.rglob('*') if p.is_file()):
                rel=f.relative_to(src); dest=raw/rel; dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(f,dest); files.append(dest)
        recent_report_paths=[]
        recent_report_entries=[]
        for recent_report in recent_reports:
            recent_date=recent_report['date']
            report=Path(recent_report['path'])
            history.mkdir(parents=True, exist_ok=True)
            dest=history/f'{recent_date}-report.md'
            shutil.copy2(report,dest)
            recent_report_paths.append(dest)
            entry={'date':recent_date,'path':str(dest),'source_path':str(report)}
            if recent_report.get('doc_url'):
                entry['doc_url']=recent_report['doc_url']
            recent_report_entries.append(entry)
        status='ok' if files else ('degraded' if lane=='github-ai-projects' else 'missing')
        context={'report_date':report_date,'lane':lane,'signal_lane':SIGNAL_LANE_MAP[lane],'skill':LANE_SKILL_MAP[lane],'raw_dir':str(raw),'raw_corpus_status':status,'raw_file_count':len(files),'output_markdown':str(output/'lane.md'),'output_meta':str(output/'lane-meta.json'),'selected_items_path':str(selected_items_path) if selected_items_path else None,'selected_items_mode':'audit_only','recent_report_paths':[str(p) for p in recent_report_paths],'recent_report_urls':[e['doc_url'] for e in recent_report_entries if e.get('doc_url')],'recent_reports':recent_report_entries,'recent_report_mode':'agent_dedup_reference_only'}
        (package/'context.json').write_text(json.dumps(context,ensure_ascii=False,indent=2),encoding='utf-8')
        index='\n'.join(f'- raw/{f.relative_to(raw)}' for f in files[:200]) or '- No raw files found.'
        recent_lines=[]
        for entry in recent_report_entries:
            line=f"- {entry['date']}: history/{Path(entry['path']).name} — source file: {entry['source_path']}"
            if entry.get('doc_url'):
                line += f" — published doc: {entry['doc_url']}"
            recent_lines.append(line)
        recent_index='\n'.join(recent_lines) or '- No recent report files found.'
        sample=[]
        for f in files[:20]:
            txt=f.read_text(encoding='utf-8',errors='ignore')[:2500]
            sample.append(f'\n### raw/{f.relative_to(raw)}\n\n```text\n{txt}\n```')
        sample_text = ''.join(sample)
        (package/'input.md').write_text(f"""# Lane Package: {lane}\n\nReport date: {report_date}\nSkill: {LANE_SKILL_MAP[lane]}\nRaw corpus status: {status}\n\nUse raw corpus as primary evidence. `selected_items.json` is audit-only and must not drive judgment.\n\n## Recent report dedupe references\n{recent_index}\n\nRead yesterday and day-before-yesterday reports before selecting or writing. Prefer the local `history/` markdown copies; if a copy is missing or unclear, use the source file paths and published doc URLs listed here or in `context.json`. Use them only as reference-only dedupe context: reject exact repeats or substantially unchanged topics; keep meaningful follow-ups with new facts and state what changed. For recurring sections, do not dedupe weather/current market items purely because yesterday had the same section. This is agent judgment, not code-controlled filtering.\n\nWrite output files exactly:\n- {output/'lane.md'}\n- {output/'lane-meta.json'}\n\n## Raw file index\n{index}\n\n## Raw excerpts\n{sample_text}\n""",encoding='utf-8')
        packages[lane]=package
    return packages

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--report-date',required=True); ap.add_argument('--signal-root',type=Path,default=Path.home()/'.daily-lane-data'/'signals'); ap.add_argument('--runtime-root',type=Path,required=True); ap.add_argument('--selected-items-path',type=Path)
    a=ap.parse_args(); packages=prepare_lane_packages(a.report_date,a.signal_root.expanduser(),a.runtime_root.expanduser(),a.selected_items_path)
    print(json.dumps({k:str(v) for k,v in packages.items()},ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
