from __future__ import annotations
import argparse,json,re
from pathlib import Path
class ValidationError(Exception): pass
FORBIDDEN_PHRASES=['趋势信息包含这些具体点','这条原始信号给出的可核验信息集中在','适合作为今日该栏目的迁移期素材','具体变化见来源','采集文本','当前可作为']
ALLOWED_STATUS={'ok','empty','degraded','blocked'}
def validate_lane_output_dir(path: Path) -> None:
    md=path/'lane.md'; meta_path=path/'lane-meta.json'
    if not md.exists(): raise ValidationError(f'missing lane.md: {path}')
    if not meta_path.exists(): raise ValidationError(f'missing lane-meta.json: {path}')
    text=md.read_text(encoding='utf-8')
    meta=json.loads(meta_path.read_text(encoding='utf-8'))
    for key in ['lane','status','selected_count','rejected_count','sources','rejected','notes']:
        if key not in meta: raise ValidationError(f'missing meta key {key}')
    if meta['status'] not in ALLOWED_STATUS: raise ValidationError('invalid status')
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text: raise ValidationError(f'forbidden phrase: {phrase}')
    if meta['status']=='ok':
        if not text.strip(): raise ValidationError('empty ok markdown')
        if not meta.get('sources'): raise ValidationError('sources required for ok')
        if not re.search(r'https?://', text): raise ValidationError('url required for ok')
def validate_runtime(runtime_root: Path) -> list[str]:
    errors=[]
    for out in sorted((runtime_root/'lane-outputs').glob('*')):
        if out.is_dir():
            try: validate_lane_output_dir(out)
            except Exception as e: errors.append(f'{out.name}: {e}')
    if errors: raise ValidationError('\n'.join(errors))
    return errors
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--runtime-root',type=Path,required=True); a=ap.parse_args(); validate_runtime(a.runtime_root); print('lane outputs validation passed'); return 0
if __name__=='__main__': raise SystemExit(main())
