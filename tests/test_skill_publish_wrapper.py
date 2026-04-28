from pathlib import Path
from skills.daily_report_master.scripts.publish_report import build_lark_create_command
def test_build_lark_create_command_uses_markdown_file():
    cmd=build_lark_create_command(Path('/tmp/report.md'), title='AI Agent 日报（2026-04-26）skill-preview')
    assert cmd[:4] == ['lark-cli','docs','+create','--as']; assert 'user' in cmd; assert '--title' in cmd; assert 'AI Agent 日报（2026-04-26）skill-preview' in cmd; assert '--markdown' in cmd; assert '@report.md' in cmd
