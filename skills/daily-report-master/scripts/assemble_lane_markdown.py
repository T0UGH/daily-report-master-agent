from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT))
try:
    from skills.daily_report_master.scripts.assemble_lane_markdown import main
except ModuleNotFoundError as exc:
    if not (exc.name == 'skills' or str(exc.name).startswith('skills.daily_report_master')):
        raise
    from productivity.daily_report_master.scripts.assemble_lane_markdown import main

if __name__ == '__main__':
    raise SystemExit(main())
