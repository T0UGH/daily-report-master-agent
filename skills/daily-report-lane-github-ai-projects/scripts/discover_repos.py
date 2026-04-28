from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from skills.daily_report_lane_github_ai_projects.scripts.discover_repos import main
if __name__ == '__main__':
    raise SystemExit(main())
