from __future__ import annotations

import json
from pathlib import Path

from skills.daily_report_master.scripts import publish_report


def _write_report(run_dir: Path) -> Path:
    report_path = run_dir / "report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "# AI Agent 日报（2026-04-16）\n\n"
        "## Codex\n\n"
        "- Codex 发布了新的 review gate。\n\n"
        "## 来源\n\n"
        "- https://example.com/source\n",
        encoding="utf-8",
    )
    return report_path


def _patch_doc_and_card_helpers(monkeypatch, run_dir: Path, *, card_message_id: str | None) -> dict:
    card_payload = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "[查看完整文档](https://feishu.example/doc)",
                },
            }
        ],
    }
    config = {"audio": {"delivery": {"receive_id_env": "FEISHU_HOME_CHANNEL", "receive_id_type": "chat_id"}}}

    monkeypatch.setattr(publish_report, "load_runtime_config", lambda config_path=None: config)
    monkeypatch.setattr(
        publish_report,
        "import_to_feishu",
        lambda report_path, title, publish_run_dir: {
            "status": "succeeded",
            "log": str(run_dir / "logs" / "feishu-import.log"),
            "doc_url": "https://feishu.example/doc",
        },
    )
    monkeypatch.setattr(
        publish_report,
        "build_curated_card_payload",
        lambda *, report_markdown, doc_url: card_payload,
    )
    monkeypatch.setattr(
        publish_report,
        "send_curated_card_to_feishu",
        lambda *, card_payload, run_dir, config: {
            "status": "succeeded",
            "log": str(run_dir / "logs" / "feishu-card.log"),
            "message_id": card_message_id,
        },
    )
    return card_payload


def test_build_lark_create_command_uses_markdown_file() -> None:
    cmd = publish_report.build_lark_create_command(
        Path("/tmp/report.md"),
        title="AI Agent 日报（2026-04-26）skill-preview",
    )

    assert cmd[:4] == ["lark-cli", "docs", "+create", "--as"]
    assert "user" in cmd
    assert "--title" in cmd
    assert "AI Agent 日报（2026-04-26）skill-preview" in cmd
    assert "--markdown" in cmd
    assert "@report.md" in cmd


def test_publish_wrapper_imports_publish_delivery_not_legacy_flow() -> None:
    source = Path(publish_report.__file__).read_text(encoding="utf-8")

    assert "helpers.publish_delivery" in source
    assert "helpers." + "run_daily_" + "report_flow" not in source


def test_main_writes_publish_state_when_doc_and_card_succeed(monkeypatch, tmp_path: Path) -> None:
    run_dir = tmp_path / "2026-04-16"
    report_path = _write_report(run_dir)
    card_payload = _patch_doc_and_card_helpers(monkeypatch, run_dir, card_message_id="om_card_success")

    exit_code = publish_report.main(
        [
            "--report-path",
            str(report_path),
            "--title",
            "AI Agent 日报（2026-04-16）",
        ]
    )

    assert exit_code == 0
    state = json.loads((run_dir / "publish-state.json").read_text(encoding="utf-8"))
    assert state["report_date"] == "2026-04-16"
    assert state["doc"]["status"] == "succeeded"
    assert state["doc"]["url"] == "https://feishu.example/doc"
    assert state["card"]["status"] == "succeeded"
    assert state["card"]["message_id"] == "om_card_success"
    assert state["card"]["payload_path"] == "artifacts/feishu-card.json"
    assert state["missing_required_outputs"] == []
    assert state["final_delivery_ok"] is True
    assert json.loads((run_dir / "artifacts" / "feishu-card.json").read_text(encoding="utf-8")) == card_payload
    assert json.loads((run_dir / "stage-status" / "publish-doc.json").read_text(encoding="utf-8"))[
        "status"
    ] == "succeeded"
    assert json.loads((run_dir / "stage-status" / "publish-card.json").read_text(encoding="utf-8"))[
        "status"
    ] == "succeeded"


def test_main_marks_missing_card_message_id_as_incomplete_delivery(monkeypatch, tmp_path: Path) -> None:
    run_dir = tmp_path / "2026-04-16"
    report_path = _write_report(run_dir)
    _patch_doc_and_card_helpers(monkeypatch, run_dir, card_message_id=None)

    exit_code = publish_report.main(
        [
            "--report-path",
            str(report_path),
            "--title",
            "AI Agent 日报（2026-04-16）",
        ]
    )

    assert exit_code == 1
    state = json.loads((run_dir / "publish-state.json").read_text(encoding="utf-8"))
    assert state["doc"]["status"] == "succeeded"
    assert state["card"]["message_id"] is None
    assert state["card"]["error_summary"] == "Feishu curated card send succeeded without message_id"
    assert "card" in state["missing_required_outputs"]
    assert state["final_delivery_ok"] is False
    assert json.loads((run_dir / "stage-status" / "publish-card.json").read_text(encoding="utf-8"))[
        "error_summary"
    ] == "Feishu curated card send succeeded without message_id"
