from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from skills.daily_report_master.scripts.sync_skills import main
if __name__ == '__main__':
    raise SystemExit(main())
