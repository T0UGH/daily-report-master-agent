from __future__ import annotations
import argparse,json
from pathlib import Path
def build_query_list(report_date: str) -> list[str]:
    return [f'GitHub trending AI {report_date}', f'GitHub new AI projects {report_date}', f'awesome AI GitHub {report_date}']
def write_discovery_bundle(report_date: str, output_dir: Path, search_results: list[dict]|None=None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True); path=output_dir/'github-ai-projects-discovery-evidence.md'
    rows='\n'.join(f"- {r.get('title','untitled')}: {r.get('url','')} — {r.get('snippet','')}" for r in (search_results or [])) or '- No search results supplied.'
    path.write_text(f'# Candidate evidence for GitHub AI Projects {report_date}\n\n## Queries\n'+'\n'.join(f'- {q}' for q in build_query_list(report_date))+f'\n\n## Candidate evidence\n{rows}\n',encoding='utf-8')
    return path
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--report-date',required=True); ap.add_argument('--output-dir',type=Path,required=True); a=ap.parse_args(); print(write_discovery_bundle(a.report_date,a.output_dir)); return 0
if __name__=='__main__': raise SystemExit(main())
