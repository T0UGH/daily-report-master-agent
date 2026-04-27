from __future__ import annotations
import argparse, shutil
from pathlib import Path

def discover_skill_dirs(repo_root: Path) -> list[Path]:
    skills_root = repo_root / "skills"
    if not skills_root.exists(): return []
    return sorted([p for p in skills_root.iterdir() if p.is_dir() and (p/'SKILL.md').exists()], key=lambda p:p.name)

def sync_skills(repo_root: Path, destination_root: Path) -> list[str]:
    destination_root.mkdir(parents=True, exist_ok=True)
    synced=[]
    for source in discover_skill_dirs(repo_root):
        dest=destination_root/source.name
        if dest.exists(): shutil.rmtree(dest)
        shutil.copytree(source,dest)
        synced.append(source.name)
    return synced

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--repo-root', type=Path, default=Path.cwd()); ap.add_argument('--destination-root', type=Path, default=Path.home()/'.hermes'/'skills'/'productivity')
    args=ap.parse_args(); synced=sync_skills(args.repo_root.resolve(), args.destination_root.expanduser().resolve())
    print('synced skills:'); [print(f'- {n}') for n in synced]; return 0
if __name__=='__main__': raise SystemExit(main())
