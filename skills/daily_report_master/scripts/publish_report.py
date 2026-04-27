from __future__ import annotations
import argparse, subprocess
from pathlib import Path

def build_lark_create_command(report_path: Path, title: str) -> list[str]:
    # lark-cli requires @file to be relative to cwd, so callers should run with cwd=report_path.parent.
    return ['lark-cli','docs','+create','--as','user','--title',title,'--markdown',f'@{report_path.name}']

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--report-path',type=Path,required=True)
    ap.add_argument('--title',required=True)
    a=ap.parse_args()
    report_path=a.report_path.resolve()
    cmd=build_lark_create_command(report_path,a.title)
    print(' '.join(cmd))
    return subprocess.call(cmd, cwd=report_path.parent)

if __name__=='__main__': raise SystemExit(main())
