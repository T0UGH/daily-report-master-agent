from __future__ import annotations

import json
from pathlib import Path

from helpers import publish_delivery


def _write_report(run_dir: Path) -> Path:
    report_path = run_dir / "report.md"
    report_path.write_text(
        "# AI Agent 日报（2026-04-16）\n\n"
        "## Product Hunt 新品\n\n"
        "- **新品 A**\n"
        "- **新品 B**\n"
        "- **新品 C**\n"
        "- **新品 D**\n\n"
        "## 天气\n\n"
        "- **北京海淀天气**：多云，9°C - 21°C，20%，西北风 3-4级\n\n"
        "## 来源\n\n"
        "- https://example.com/source\n",
        encoding="utf-8",
    )
    return report_path


def _runtime_config() -> dict:
    return {
        "audio": {
            "delivery": {
                "receive_id_env": "FEISHU_HOME_CHANNEL",
                "receive_id_type": "chat_id",
            }
        }
    }


def test_import_to_feishu_uses_lark_cli_and_parses_json_stdout(monkeypatch, tmp_path: Path) -> None:
    report_path = _write_report(tmp_path)
    seen: dict[str, object] = {}

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> publish_delivery.CommandResult:
        del env
        seen["command"] = command
        seen["output_path"] = output_path
        seen["cwd"] = cwd
        return publish_delivery.CommandResult(
            command=command,
            exit_code=0,
            output_path=str(output_path),
            stdout=json.dumps(
                {
                    "url": "https://feishu.example/wiki/doc-url",
                    "token": "doc-token-123",
                    "id": "doc-id-456",
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(publish_delivery, "run_and_capture", fake_run_and_capture)

    result = publish_delivery.import_to_feishu(
        report_path=report_path,
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
    )

    resolved_report_path = report_path.resolve()
    assert seen["command"] == [
        "lark-cli",
        "docs",
        "+create",
        "--as",
        "user",
        "--title",
        "AI 日报（2026-04-16）",
        "--markdown",
        f"@./{resolved_report_path.name}",
    ]
    assert seen["output_path"] == tmp_path / "logs" / "feishu-import.log"
    assert seen["cwd"] == resolved_report_path.parent
    assert result == {
        "status": "succeeded",
        "log": str(tmp_path / "logs" / "feishu-import.log"),
        "doc_url": "https://feishu.example/wiki/doc-url",
        "doc_token": "doc-token-123",
        "doc_id": "doc-id-456",
    }


def test_build_curated_card_payload_puts_doc_link_first_and_caps_product_hunt_items(tmp_path: Path) -> None:
    report_markdown = _write_report(tmp_path).read_text(encoding="utf-8")

    payload = publish_delivery.build_curated_card_payload(
        report_markdown=report_markdown,
        doc_url="https://feishu.example/doc",
    )

    div_contents = [element["text"]["content"] for element in payload["elements"] if element.get("tag") == "div"]
    section_titles = [
        element["text"]["content"]
        for element in payload["elements"]
        if element.get("tag") == "div" and element.get("text", {}).get("tag") == "plain_text"
    ]

    assert payload["header"]["title"]["content"] == "AI Agent 日报（2026-04-16）"
    assert payload["header"]["subtitle"]["content"] == "[查看完整文档](https://feishu.example/doc)"
    assert div_contents[0] == "我不是贵平，我是 Rook。 [查看完整文档](https://feishu.example/doc)"
    assert section_titles[0] == "天气"
    assert "来源" not in section_titles

    product_hunt_index = div_contents.index("Product Hunt 新品")
    product_hunt_block = div_contents[product_hunt_index + 1]
    assert "**新品 A**" in product_hunt_block
    assert "**新品 B**" in product_hunt_block
    assert "**新品 C**" in product_hunt_block
    assert "**新品 D**" not in product_hunt_block


def test_send_curated_card_to_feishu_uses_lark_cli_with_user_chat_delivery(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FEISHU_HOME_CHANNEL", "oc_home_from_env")
    card_payload = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"}}
        ],
    }
    seen: dict[str, object] = {}

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> publish_delivery.CommandResult:
        del cwd, env
        seen["command"] = command
        seen["output_path"] = output_path
        return publish_delivery.CommandResult(
            command=command,
            exit_code=0,
            output_path=str(output_path),
            stdout=json.dumps({"data": {"message_id": "om_card_success"}}),
            stderr="",
        )

    monkeypatch.setattr(publish_delivery, "run_and_capture", fake_run_and_capture)

    result = publish_delivery.send_curated_card_to_feishu(
        card_payload=card_payload,
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert seen["command"] == [
        "lark-cli",
        "im",
        "+messages-send",
        "--as",
        "user",
        "--chat-id",
        "oc_home_from_env",
        "--msg-type",
        "interactive",
        "--content",
        json.dumps(card_payload, ensure_ascii=False),
    ]
    assert seen["output_path"] == tmp_path / "logs" / "feishu-card.log"
    assert result == {
        "status": "succeeded",
        "log": str(tmp_path / "logs" / "feishu-card.log"),
        "message_id": "om_card_success",
    }


def test_write_publish_delivery_state_requires_card_message_id(tmp_path: Path) -> None:
    state = publish_delivery.write_publish_delivery_state(
        report_date="2026-04-16",
        run_dir=tmp_path,
        publish_result={
            "status": "succeeded",
            "doc_status": "succeeded",
            "doc_url": "https://feishu.example/doc",
            "doc_log": str(tmp_path / "logs" / "feishu-import.log"),
            "card_status": "succeeded",
            "card_payload_path": str(tmp_path / "artifacts" / "feishu-card.json"),
            "card_message_log": str(tmp_path / "logs" / "feishu-card.log"),
            "card_message_id": None,
            "audio_status": "skipped",
        },
    )

    assert state["missing_required_outputs"] == ["card"]
    assert state["final_delivery_ok"] is False
    assert json.loads((tmp_path / "publish-state.json").read_text(encoding="utf-8")) == state
    assert json.loads((tmp_path / "stage-status" / "publish-card.json").read_text(encoding="utf-8"))[
        "message_id"
    ] is None
