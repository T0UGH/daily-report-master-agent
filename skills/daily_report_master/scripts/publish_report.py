from __future__ import annotations
import argparse, subprocess
from pathlib import Path
def build_lark_create_command(report_path: Path, title: str) -> list[str]:
    return ['lark-cli','docs','+create','--as','user','--title',title,'--markdown',f'@{report_path}']
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--report-path',type=Path,required=True); ap.add_argument('--title',required=True); a=ap.parse_args(); cmd=build_lark_create_command(a.report_path,a.title); print(' '.join(cmd)); return subprocess.call(cmd)
if __name__=='__main__': raise SystemExit(main())
