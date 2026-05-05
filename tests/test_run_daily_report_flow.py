from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import pytest

from helpers import run_daily_report_flow as flow


def _runtime_config() -> dict:
    return {
        "audio": {
            "tts": {
                "default_voice_id": "Chinese (Mandarin)_Soft_Girl",
                "model": "speech-2.8-hd",
                "intermediate_format": "mp3",
            },
            "delivery": {
                "receive_id_env": "FEISHU_HOME_CHANNEL",
                "receive_id_type": "chat_id",
            },
        }
    }


def _write_report(tmp_path: Path) -> Path:
    report_path = tmp_path / "report.md"
    report_path.write_text(
        "# AI Agent 日报（2026-04-16）\n\n"
        "- **OpenAI** 发布了 [新模型](https://example.com/model)\n"
        "- `Claude Code` 增强了 review 流程\n\n"
        "## 来源\n"
        "- https://example.com/source\n",
        encoding="utf-8",
    )
    return report_path


def test_build_readout_text_builds_listener_friendly_spoken_script() -> None:
    report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 推荐流\n"
        "- **@alpha_01 #7** OpenAI 发布了 [新模型](https://example.com/model)，[原帖](https://example.com/post)\n"
        "- 第二条跟进了多代理协作的落地效果。\n"
        "- 第三条不应该被保留。\n\n"
        "## Claude Code\n"
        "- [Release](https://example.com/release) 增加了 review gate，并补充了错误上下文。\n"
        "- CLI 现在会展示更明确的失败原因，另见 [GitHub](https://example.com/repo)\n"
        "- 这条更新也不应该被保留。\n\n"
        "## Reddit 社区\n"
        "- 原文围绕作者经历展开\n"
        "- 社区在讨论长上下文 agent 的成本和收益，具体可参考 https://example.com/thread\n"
        "- 值得关注后续演进\n\n"
        "## 来源\n"
        "- https://example.com/source\n"
    )

    text = flow.build_readout_text(report_markdown)

    assert text.startswith("以下是今天的 AI Agent 日报语音简报。")
    assert text.endswith("以上就是今天的重点内容，感谢收听。")
    assert "先来看 X 推荐流。" in text
    assert "接着是 Claude Code。" in text
    assert "下面是 Reddit 社区。" in text
    assert "OpenAI 发布了 新模型。" in text
    assert "第二条跟进了多代理协作的落地效果。" in text
    assert "@alpha_01" not in text
    assert "第三条不应该被保留" not in text
    assert "增加了 review gate，并补充了错误上下文。" in text
    assert "CLI 现在会展示更明确的失败原因。" in text
    assert "这条更新也不应该被保留" not in text
    assert "社区在讨论长上下文 agent 的成本和收益。" in text
    assert "原文围绕" not in text
    assert "值得关注" not in text
    assert "原帖" not in text
    assert "Release" not in text
    assert "GitHub" not in text
    assert "https://example.com" not in text
    assert "[" not in text
    assert "`" not in text
    assert "## 来源" not in text


def test_build_readout_text_drops_sources_tail_entirely() -> None:
    report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 关注流\n"
        "- 第一条更新\n\n"
        "## 来源\n"
        "- https://example.com/source\n\n"
        "## Codex\n"
        "- 这段不应出现在播报里\n"
    )

    text = flow.build_readout_text(report_markdown)

    assert "再来看 X 关注流。" in text
    assert "第一条更新。" in text
    assert "Codex" not in text
    assert "这段不应出现在播报里" not in text


def test_to_spoken_sentence_removes_raw_handle_prefix() -> None:
    text = flow._to_spoken_sentence("@alpha_01 OpenAI 发布了新模型")

    assert "@alpha_01" not in text
    assert "OpenAI 发布了新模型。" in text


def test_to_spoken_sentence_adds_generic_social_source_prefix() -> None:
    text = flow._to_spoken_sentence("@fkysly Anthropic 每发一个新产品，就会给一批相关竞品带来压力")

    assert text == "有用户提到，Anthropic 每发一个新产品，就会给一批相关竞品带来压力。"


def test_to_spoken_sentence_avoids_double_generic_prefix_when_body_already_reads_naturally() -> None:
    text = flow._to_spoken_sentence("@pengchujin 有人在专门分享低价 GPT Codex 的获取渠道")

    assert text == "有人在专门分享低价 GPT Codex 的获取渠道。"


def test_to_spoken_sentence_uses_known_official_identity_for_social_source() -> None:
    text = flow._to_spoken_sentence("@claudeai Claude Code 新增了 review gate")

    assert text == "Anthropic 官方提到，Claude Code 新增了 review gate。"


def test_to_spoken_sentence_preserves_body_content_when_rewriting_social_source() -> None:
    body = "刚刚发布了 Responses API 的新能力，支持更稳定的工具调用"

    text = flow._to_spoken_sentence(f"@openai {body}")

    assert text == f"OpenAI 这边提到，{body}。"
    assert body in text


def test_build_readout_text_rewrites_long_english_headline_fragments_into_chinese() -> None:
    report_markdown = (
        "# AI Agent 日报（2026-04-19）\n\n"
        "## Reddit 社区\n"
        "- **I replaced chaotic solo Claude coding with a simple 3-agent team "
        "(Architect + Builder + Reviewer) — it's stupidly effective and token-efficient** "
        "这条帖子把 Architect、Builder、Reviewer 拆成三个角色，并强调 markdown handoff。\n\n"
        "## Claude Code\n"
        "- **Claude Code v2.1.92 introduces Ultraplan beta — source maps for TypeScript "
        "model-agnostic heartbeat shell design system coding harness builder "
        "self-hosted / proactive / local-first assistant coding AI model** "
        "这次更新把 source maps、TypeScript、model-agnostic、heartbeat、shell、Ultraplan beta、"
        "design system、coding harness builder、self-hosted / proactive / local-first assistant "
        "和 coding AI model 这些说法一起带进播报。\n"
    )

    text = flow.build_readout_text(report_markdown)

    assert "I replaced chaotic solo Claude coding" not in text
    assert "introduces Ultraplan beta" not in text
    assert "source maps" not in text
    assert "TypeScript" not in text
    assert "model-agnostic" not in text
    assert "heartbeat" not in text
    assert "shell" not in text
    assert "Ultraplan beta" not in text
    assert "design system" not in text
    assert "coding harness builder" not in text
    assert "self-hosted / proactive / local-first assistant" not in text
    assert "coding AI model" not in text
    assert "这条帖子把 Architect、Builder、Reviewer 拆成三个角色，并强调 markdown 交接文件。" in text
    assert "云端草案规划测试版" in text
    assert "源码映射" in text
    assert "类型脚本" in text
    assert "模型无关" in text
    assert "心跳检测" in text
    assert "命令行环境" in text
    assert "设计系统" in text
    assert "AI 编码测试框架构建器" in text
    assert "可自托管、主动式、本地优先助手" in text
    assert "编程模型" in text


def test_generate_audio_bundle_creates_missing_run_dir_before_writing_outputs(monkeypatch, tmp_path: Path) -> None:
    run_dir = tmp_path / "artifacts" / "2026-04-16"
    report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "- **OpenAI** 发布了 [新模型](https://example.com/model)\n"
    )
    minimax_script = tmp_path / "generate_minimax_tts.py"
    opus_script = tmp_path / "convert_to_feishu_opus.py"
    minimax_script.write_text("# mock minimax tts\n", encoding="utf-8")
    opus_script.write_text("# mock opus converter\n", encoding="utf-8")

    monkeypatch.setattr(flow, "MINIMAX_TTS_SCRIPT", minimax_script)
    monkeypatch.setattr(flow, "FEISHU_OPUS_SCRIPT", opus_script)

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> flow.CommandResult:
        del env
        output_path.write_text("mock log\n", encoding="utf-8")
        if output_path.name == "audio-tts.log":
            readout_path = Path(command[command.index("--input") + 1])
            intermediate_path = Path(command[command.index("--output") + 1])
            assert readout_path.exists()
            intermediate_path.write_bytes(b"fake-mp3")
        elif output_path.name == "audio-opus.log":
            intermediate_path = Path(command[2])
            opus_path = Path(command[3])
            assert intermediate_path.exists()
            opus_path.write_bytes(b"fake-opus")
        return flow.CommandResult(
            command=command,
            exit_code=0,
            output_path=str(output_path),
            stdout="ok",
            stderr="",
        )

    monkeypatch.setattr(flow, "run_and_capture", fake_run_and_capture)

    result = flow.generate_audio_bundle(
        report_markdown=report_markdown,
        report_date="2026-04-16",
        run_dir=run_dir,
        config=_runtime_config(),
    )

    readout_path = run_dir / "2026-04-16-readout.txt"
    assert result["status"] == "succeeded"
    assert readout_path.exists()
    assert "OpenAI 发布了 新模型" in readout_path.read_text(encoding="utf-8")
    assert (run_dir / "logs" / "audio-tts.log").exists()
    assert (run_dir / "2026-04-16-tts.mp3").exists()
    assert (run_dir / "2026-04-16-feishu.opus").exists()


def test_generate_audio_bundle_passes_minimax_env_from_hermes_dotenv(monkeypatch, tmp_path: Path) -> None:
    run_dir = tmp_path / "artifacts" / "2026-04-16"
    report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "- **OpenAI** 发布了 [新模型](https://example.com/model)\n"
    )
    minimax_script = tmp_path / "generate_minimax_tts.py"
    opus_script = tmp_path / "convert_to_feishu_opus.py"
    minimax_script.write_text("# mock minimax tts\n", encoding="utf-8")
    opus_script.write_text("# mock opus converter\n", encoding="utf-8")
    hermes_env_dir = tmp_path / ".hermes"
    hermes_env_dir.mkdir(parents=True, exist_ok=True)
    (hermes_env_dir / ".env").write_text(
        'MINIMAX_API_KEY="from-hermes-env"\n'
        "MINIMAX_TOKEN=from-hermes-token\n"
        "IGNORED_KEY=ignored\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.delenv("MINIMAX_TOKEN", raising=False)
    monkeypatch.setattr(flow, "MINIMAX_TTS_SCRIPT", minimax_script)
    monkeypatch.setattr(flow, "FEISHU_OPUS_SCRIPT", opus_script)

    tts_envs: list[dict[str, str] | None] = []

    def fake_subprocess_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        env = kwargs.get("env")
        if command[:2] == ["python3", str(minimax_script)]:
            tts_envs.append(env)
            assert env is not None
            output_path = Path(command[command.index("--output") + 1])
            output_path.write_bytes(b"fake-mp3")
        elif command[:2] == ["python3", str(opus_script)]:
            output_path = Path(command[3])
            output_path.write_bytes(b"fake-opus")
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(flow.subprocess, "run", fake_subprocess_run)

    result = flow.generate_audio_bundle(
        report_markdown=report_markdown,
        report_date="2026-04-16",
        run_dir=run_dir,
        config=_runtime_config(),
    )

    assert result["status"] == "succeeded"
    assert len(tts_envs) == 1
    assert tts_envs[0]["MINIMAX_API_KEY"] == "from-hermes-env"
    assert tts_envs[0]["MINIMAX_TOKEN"] == "from-hermes-token"
    assert "IGNORED_KEY" not in tts_envs[0]


def test_generate_audio_bundle_marks_minimax_quota_local_fallback_as_failed(monkeypatch, tmp_path: Path) -> None:
    run_dir = tmp_path / "artifacts" / "2026-04-16"
    report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "- **OpenAI** 发布了 [新模型](https://example.com/model)\n"
    )
    minimax_script = tmp_path / "generate_minimax_tts.py"
    opus_script = tmp_path / "convert_to_feishu_opus.py"
    minimax_script.write_text("# mock minimax tts\n", encoding="utf-8")
    opus_script.write_text("# mock opus converter\n", encoding="utf-8")

    monkeypatch.setattr(flow, "MINIMAX_TTS_SCRIPT", minimax_script)
    monkeypatch.setattr(flow, "FEISHU_OPUS_SCRIPT", opus_script)

    convert_calls = 0

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> flow.CommandResult:
        del cwd, env
        nonlocal convert_calls
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.name == "audio-tts.log":
            Path(command[command.index("--output") + 1]).write_bytes(b"fallback-mp3")
            stdout = json.dumps(
                {
                    "status": "succeeded-via-local-fallback",
                    "provider": "macos-say",
                    "recovery_note": "MiniMax error 2056: usage limit exceeded; fell back to macOS say",
                },
                ensure_ascii=False,
            )
            output_path.write_text(stdout, encoding="utf-8")
            return flow.CommandResult(
                command=command,
                exit_code=0,
                output_path=str(output_path),
                stdout=stdout,
                stderr="",
            )

        convert_calls += 1
        output_path.write_text("unexpected convert\n", encoding="utf-8")
        return flow.CommandResult(
            command=command,
            exit_code=0,
            output_path=str(output_path),
            stdout="ok",
            stderr="",
        )

    monkeypatch.setattr(flow, "run_and_capture", fake_run_and_capture)

    result = flow.generate_audio_bundle(
        report_markdown=report_markdown,
        report_date="2026-04-16",
        run_dir=run_dir,
        config=_runtime_config(),
    )

    assert result["status"] == "failed"
    assert "MiniMax" in result["error_summary"]
    assert "2056" in result["error_summary"]
    assert "local fallback" in result["error_summary"]
    assert convert_calls == 0


def test_import_to_feishu_uses_lark_cli_and_parses_json_stdout(monkeypatch, tmp_path: Path) -> None:
    report_path = _write_report(tmp_path)
    seen: dict[str, object] = {}

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> flow.CommandResult:
        del env
        seen["command"] = command
        seen["output_path"] = output_path
        seen["cwd"] = cwd
        return flow.CommandResult(
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

    monkeypatch.setattr(flow, "run_and_capture", fake_run_and_capture)

    result = flow.import_to_feishu(
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


def test_import_to_feishu_falls_back_to_url_extraction_when_stdout_is_not_json(
    monkeypatch, tmp_path: Path
) -> None:
    report_path = _write_report(tmp_path)

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> flow.CommandResult:
        del command, cwd, env
        return flow.CommandResult(
            command=["lark-cli"],
            exit_code=0,
            output_path=str(output_path),
            stdout="Created doc successfully: https://feishu.example/wiki/fallback-doc",
            stderr="",
        )

    monkeypatch.setattr(flow, "run_and_capture", fake_run_and_capture)

    result = flow.import_to_feishu(
        report_path=report_path,
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
    )

    assert result == {
        "status": "succeeded",
        "log": str(tmp_path / "logs" / "feishu-import.log"),
        "doc_url": "https://feishu.example/wiki/fallback-doc",
    }


def test_build_curated_card_payload_puts_doc_link_first_and_caps_product_hunt_items() -> None:
    report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 推荐流\n"
        "- 第一条社区讨论\n"
        "- 第二条社区讨论\n\n"
        "## Claude Code\n"
        "- Claude 条目一\n"
        "- Claude 条目二\n\n"
        "## Product Hunt 新品\n"
        "- **新品 A**\n"
        "- **新品 B**\n"
        "- **新品 C**\n"
        "- **新品 D**\n\n"
        "## Codex\n"
        "- Codex 条目一\n\n"
        "## 天气\n"
        "- **北京海淀天气**：多云，9°C - 21°C，20%，西北风 3-4级\n"
        "- **上海杨浦天气**：阴，13°C - 22°C，40%，东风 3-4级\n\n"
        "## 来源\n"
        "- https://example.com/source\n"
    )

    payload = flow.build_curated_card_payload(
        report_markdown=report_markdown,
        doc_url="https://feishu.example/doc",
    )

    div_contents = [element["text"]["content"] for element in payload["elements"] if element.get("tag") == "div"]

    assert payload["header"]["title"]["content"] == "AI Agent 日报（2026-04-16）"
    assert payload["header"]["subtitle"]["content"] == "[查看完整文档](https://feishu.example/doc)"
    assert payload["config"]["style"]["text_size"]["section_title"]["default"] == "heading-2"
    assert div_contents[0] == "我不是贵平，我是 Rook。 [查看完整文档](https://feishu.example/doc)"
    section_titles = [
        element["text"]["content"]
        for element in payload["elements"]
        if element.get("tag") == "div" and element.get("text", {}).get("tag") == "plain_text"
    ]
    assert section_titles[0] == "天气"
    assert "Claude Code" in section_titles
    assert "Codex" in section_titles
    assert "OpenClaw" not in section_titles
    assert "来源" not in section_titles
    weather_block = div_contents[2]
    assert "**北京海淀天气**" in weather_block
    assert "**上海杨浦天气**" in weather_block

    product_hunt_index = div_contents.index("Product Hunt 新品")
    product_hunt_block = div_contents[product_hunt_index + 1]
    assert "**新品 A**" in product_hunt_block
    assert "**新品 B**" in product_hunt_block
    assert "**新品 C**" in product_hunt_block
    assert "**新品 D**" not in product_hunt_block


def test_validate_curated_card_payload_reports_oversized_lark_md_content() -> None:
    payload = {
        "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报精选"}},
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "x" * 7000,
                },
            }
        ],
    }

    issues = flow.validate_curated_card_payload(payload)

    assert any("elements[0]" in issue and "lark_md" in issue and "exceeds" in issue for issue in issues)


def test_send_curated_card_to_feishu_uses_lark_cli_with_user_chat_delivery(
    monkeypatch, tmp_path: Path
) -> None:
    config = _runtime_config()
    config["audio"]["delivery"]["receive_id_env"] = "ALT_FEISHU_CHANNEL"
    monkeypatch.setenv("FEISHU_HOME_CHANNEL", "oc_home_from_env")
    monkeypatch.setenv("ALT_FEISHU_CHANNEL", "oc_channel_from_config_env")
    seen: dict[str, object] = {}
    card_payload = {
        "config": {"wide_screen_mode": True},
        "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"}}
        ],
    }

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> flow.CommandResult:
        del cwd, env
        seen["command"] = command
        seen["output_path"] = output_path
        return flow.CommandResult(
            command=command,
            exit_code=0,
            output_path=str(output_path),
            stdout=json.dumps({"data": {"message_id": "om_card_success"}}),
            stderr="",
        )

    monkeypatch.setattr(flow, "run_and_capture", fake_run_and_capture)

    result = flow.send_curated_card_to_feishu(
        card_payload=card_payload,
        run_dir=tmp_path,
        config=config,
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


def test_send_curated_card_to_feishu_compacts_oversized_payload_and_logs_preflight(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FEISHU_HOME_CHANNEL", "oc_card_channel")
    oversized_content = "x" * 7000
    card_payload = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"},
            "subtitle": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"},
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": oversized_content,
                },
            }
        ],
    }
    sent_payloads: list[dict] = []

    def fake_run_and_capture(
        command: list[str],
        output_path: Path,
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> flow.CommandResult:
        del cwd, env
        sent_payloads.append(json.loads(command[command.index("--content") + 1]))
        return flow.CommandResult(
            command=command,
            exit_code=0,
            output_path=str(output_path),
            stdout=json.dumps({"data": {"message_id": "om_compacted_card"}}),
            stderr="",
        )

    monkeypatch.setattr(flow, "run_and_capture", fake_run_and_capture)

    result = flow.send_curated_card_to_feishu(
        card_payload=card_payload,
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert result["status"] == "succeeded"
    assert result["degraded"] is True
    assert result["preflight_log"] == str(tmp_path / "logs" / "feishu-card-preflight.json")
    assert result["message_id"] == "om_compacted_card"
    assert len(sent_payloads) == 1
    sent_payload = sent_payloads[0]
    assert sent_payload["header"] == card_payload["header"]
    sent_content = sent_payload["elements"][0]["text"]["content"]
    assert "精选卡片内容较长，已简化展示" in sent_content
    assert "https://feishu.example/doc" in sent_content
    assert oversized_content not in sent_content

    preflight = json.loads((tmp_path / "logs" / "feishu-card-preflight.json").read_text(encoding="utf-8"))
    assert preflight["degraded"] is True
    assert preflight["issues"]
    assert preflight["doc_url"] == "https://feishu.example/doc"


def test_send_audio_to_feishu_uses_native_api_success(monkeypatch, tmp_path: Path) -> None:
    opus_path = tmp_path / "feishu-native-audio-test.opus"
    opus_path.write_bytes(b"opus-audio-bytes")
    config = _runtime_config()
    config["audio"]["delivery"]["receive_id_env"] = "ALT_FEISHU_CHANNEL"
    monkeypatch.setenv("FEISHU_APP_ID", "env-app-id")
    monkeypatch.setenv("FEISHU_APP_SECRET", "env-app-secret")
    monkeypatch.setenv("FEISHU_HOME_CHANNEL", "oc_home_from_env")
    monkeypatch.setenv("ALT_FEISHU_CHANNEL", "oc_channel_from_config_env")

    def fail_if_cli_is_used(*args, **kwargs):
        raise AssertionError("send_audio_to_feishu should not shell out to a CLI")

    monkeypatch.setattr(flow, "run_and_capture", fail_if_cli_is_used)

    requests_seen: list[tuple[str, dict[str, str], bytes]] = []

    class FakeHttpResponse:
        def __init__(self, payload: dict) -> None:
            self.payload = json.dumps(payload).encode("utf-8")

        def read(self) -> bytes:
            return self.payload

        def __enter__(self) -> "FakeHttpResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    def fake_urlopen(request):
        headers = {key.lower(): value for key, value in request.header_items()}
        body = request.data or b""
        requests_seen.append((request.full_url, headers, body))

        if request.full_url.endswith("/auth/v3/tenant_access_token/internal"):
            assert json.loads(body.decode("utf-8")) == {
                "app_id": "env-app-id",
                "app_secret": "env-app-secret",
            }
            return FakeHttpResponse({"tenant_access_token": "tenant-token"})

        if request.full_url.endswith("/im/v1/files"):
            assert headers["authorization"] == "Bearer tenant-token"
            assert "multipart/form-data" in headers["content-type"]
            assert b'name="file_type"' in body
            assert b"\r\n\r\nopus\r\n" in body
            assert b'name="file_name"' in body
            assert b"feishu-native-audio-test.opus" in body
            assert b'name="file"; filename="feishu-native-audio-test.opus"' in body
            assert b"opus-audio-bytes" in body
            return FakeHttpResponse({"data": {"file_key": "file-key-123"}})

        if request.full_url.endswith("/im/v1/messages?receive_id_type=chat_id"):
            assert headers["authorization"] == "Bearer tenant-token"
            assert headers["content-type"] == "application/json; charset=utf-8"
            assert json.loads(body.decode("utf-8")) == {
                "receive_id": "oc_home_from_env",
                "msg_type": "audio",
                "content": "{\"file_key\":\"file-key-123\"}",
            }
            return FakeHttpResponse({"data": {"message_id": "om_audio_success"}, "msg_type": "audio"})

        raise AssertionError(f"Unexpected request URL: {request.full_url}")

    monkeypatch.setattr(flow, "urlopen", fake_urlopen, raising=False)

    result = flow.send_audio_to_feishu(
        opus_path=opus_path,
        run_dir=tmp_path,
        doc_url="https://feishu.example/doc",
        config=config,
    )

    assert result["status"] == "succeeded"
    assert result["message_id"] == "om_audio_success"
    assert result["opus_path"] == str(opus_path)
    assert [url for url, _, _ in requests_seen] == [
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        "https://open.feishu.cn/open-apis/im/v1/files",
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    ]


def test_publish_report_bundle_succeeds(monkeypatch, tmp_path: Path) -> None:
    report_path = _write_report(tmp_path)
    report_markdown = report_path.read_text(encoding="utf-8")
    opus_path = tmp_path / "2026-04-16-feishu.opus"
    sent: dict[str, str] = {}
    call_order: list[str] = []

    monkeypatch.setattr(
        flow,
        "generate_audio_bundle",
        lambda **_: call_order.append("audio_bundle") or {
            "status": "succeeded",
            "readout_path": str(tmp_path / "2026-04-16-readout.txt"),
            "intermediate_path": str(tmp_path / "2026-04-16-tts.mp3"),
            "intermediate_format": "mp3",
            "opus_path": str(opus_path),
            "tts_log": str(tmp_path / "logs" / "audio-tts.log"),
            "convert_log": str(tmp_path / "logs" / "audio-opus.log"),
        },
    )
    monkeypatch.setattr(
        flow,
        "import_to_feishu",
        lambda report_path, title, run_dir: call_order.append("doc") or {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-import.log"),
            "doc_url": "https://feishu.example/doc",
        },
    )
    monkeypatch.setattr(
        flow,
        "build_curated_card_payload",
        lambda **_: call_order.append("card_build") or {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"}}
            ],
        },
    )

    def fake_send_curated_card_to_feishu(*, card_payload: dict, run_dir: Path, config: dict) -> dict:
        del card_payload, run_dir, config
        call_order.append("card_send")
        return {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-card.log"),
            "message_id": "om_card_success",
        }

    monkeypatch.setattr(flow, "send_curated_card_to_feishu", fake_send_curated_card_to_feishu)

    def fake_send_audio_to_feishu(*, opus_path: Path, run_dir: Path, doc_url: str | None, config: dict) -> dict:
        sent["opus_path"] = str(opus_path)
        sent["doc_url"] = doc_url or ""
        call_order.append("audio_send")
        return {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-audio.log"),
            "message_id": "om_audio_success",
        }

    monkeypatch.setattr(flow, "send_audio_to_feishu", fake_send_audio_to_feishu)

    result = flow.publish_report_bundle(
        report_path=report_path,
        report_markdown=report_markdown,
        report_date="2026-04-16",
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert result["status"] == "succeeded"
    assert result["target"] == "feishu"
    assert result["doc_status"] == "succeeded"
    assert result["card_status"] == "succeeded"
    assert result["audio_status"] == "succeeded"
    assert result["card_message_log"] == str(tmp_path / "logs" / "feishu-card.log")
    assert result["card_message_id"] == "om_card_success"
    assert result["audio_opus_path"] == str(opus_path)
    assert result["audio_message_id"] == "om_audio_success"
    assert call_order == ["doc", "card_build", "card_send", "audio_bundle", "audio_send"]
    assert sent == {
        "opus_path": str(opus_path),
        "doc_url": "https://feishu.example/doc",
    }
    state = json.loads((tmp_path / "publish-state.json").read_text(encoding="utf-8"))
    assert state["report_date"] == "2026-04-16"
    assert state["status"] == "succeeded"
    assert state["doc"] == {
        "status": "succeeded",
        "url": "https://feishu.example/doc",
        "log_path": "logs/feishu-import.log",
        "error_summary": None,
    }
    assert state["card"] == {
        "status": "succeeded",
        "message_id": "om_card_success",
        "payload_path": "artifacts/feishu-card.json",
        "preflight_path": None,
        "log_path": "logs/feishu-card.log",
        "error_summary": None,
    }
    assert state["audio"] == {
        "status": "succeeded",
        "message_id": "om_audio_success",
        "opus_path": "2026-04-16-feishu.opus",
        "log_path": "logs/feishu-audio.log",
        "error_summary": None,
    }
    assert state["required_outputs"] == ["doc", "card"]
    assert state["missing_required_outputs"] == []
    assert state["final_delivery_ok"] is True
    assert state["updated_at"].endswith("Z")
    assert json.loads((tmp_path / "artifacts" / "feishu-card.json").read_text(encoding="utf-8")) == result[
        "card_payload"
    ]
    doc_stage = json.loads((tmp_path / "stage-status" / "publish-doc.json").read_text(encoding="utf-8"))
    card_stage = json.loads((tmp_path / "stage-status" / "publish-card.json").read_text(encoding="utf-8"))
    assert doc_stage["status"] == "succeeded"
    assert card_stage["status"] == "succeeded"


def test_publish_report_bundle_succeeds_when_card_send_degraded(monkeypatch, tmp_path: Path) -> None:
    report_path = _write_report(tmp_path)
    report_markdown = report_path.read_text(encoding="utf-8")
    opus_path = tmp_path / "2026-04-16-feishu.opus"

    monkeypatch.setattr(
        flow,
        "generate_audio_bundle",
        lambda **_: {
            "status": "succeeded",
            "readout_path": str(tmp_path / "2026-04-16-readout.txt"),
            "intermediate_path": str(tmp_path / "2026-04-16-tts.mp3"),
            "intermediate_format": "mp3",
            "opus_path": str(opus_path),
            "tts_log": str(tmp_path / "logs" / "audio-tts.log"),
            "convert_log": str(tmp_path / "logs" / "audio-opus.log"),
        },
    )
    monkeypatch.setattr(
        flow,
        "import_to_feishu",
        lambda report_path, title, run_dir: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-import.log"),
            "doc_url": "https://feishu.example/doc",
        },
    )
    monkeypatch.setattr(
        flow,
        "build_curated_card_payload",
        lambda **_: {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"}}
            ],
        },
    )
    monkeypatch.setattr(
        flow,
        "send_curated_card_to_feishu",
        lambda **_: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-card.log"),
            "message_id": "om_card_success",
            "degraded": True,
            "preflight_log": str(tmp_path / "logs" / "feishu-card-preflight.json"),
            "preflight_issues": ["elements[0] lark_md content exceeds limit"],
        },
    )
    monkeypatch.setattr(
        flow,
        "send_audio_to_feishu",
        lambda **_: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-audio.log"),
            "message_id": "om_audio_success",
        },
    )

    result = flow.publish_report_bundle(
        report_path=report_path,
        report_markdown=report_markdown,
        report_date="2026-04-16",
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert result["status"] == "succeeded"
    assert result["card_status"] == "succeeded"
    assert result["card_degraded"] is True
    assert result["card_preflight_log"] == str(tmp_path / "logs" / "feishu-card-preflight.json")
    assert result["card_preflight_issues"] == ["elements[0] lark_md content exceeds limit"]

    state = json.loads((tmp_path / "publish-state.json").read_text(encoding="utf-8"))
    assert state["status"] == "degraded"
    assert state["card"]["status"] == "succeeded"
    assert state["card"]["message_id"] == "om_card_success"
    assert state["card"]["preflight_path"] == "logs/feishu-card-preflight.json"
    assert state["missing_required_outputs"] == []
    assert state["final_delivery_ok"] is True


def test_publish_report_bundle_degrades_when_card_send_fails_but_audio_still_succeeds(
    monkeypatch, tmp_path: Path
) -> None:
    report_path = _write_report(tmp_path)
    report_markdown = report_path.read_text(encoding="utf-8")
    opus_path = tmp_path / "2026-04-16-feishu.opus"
    call_order: list[str] = []

    monkeypatch.setattr(
        flow,
        "generate_audio_bundle",
        lambda **_: call_order.append("audio_bundle") or {
            "status": "succeeded",
            "readout_path": str(tmp_path / "2026-04-16-readout.txt"),
            "intermediate_path": str(tmp_path / "2026-04-16-tts.mp3"),
            "intermediate_format": "mp3",
            "opus_path": str(opus_path),
            "tts_log": str(tmp_path / "logs" / "audio-tts.log"),
            "convert_log": str(tmp_path / "logs" / "audio-opus.log"),
        },
    )
    monkeypatch.setattr(
        flow,
        "import_to_feishu",
        lambda report_path, title, run_dir: call_order.append("doc") or {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-import.log"),
            "doc_url": "https://feishu.example/doc",
        },
    )
    monkeypatch.setattr(
        flow,
        "build_curated_card_payload",
        lambda **_: call_order.append("card_build") or {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"}}
            ],
        },
    )
    monkeypatch.setattr(
        flow,
        "send_curated_card_to_feishu",
        lambda **_: call_order.append("card_send") or {
            "status": "failed",
            "log": str(tmp_path / "logs" / "feishu-card.log"),
            "error_summary": "Feishu curated card send failed",
        },
    )

    def fake_send_audio_to_feishu(*, opus_path: Path, run_dir: Path, doc_url: str | None, config: dict) -> dict:
        del opus_path, run_dir, doc_url, config
        call_order.append("audio_send")
        return {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-audio.log"),
            "message_id": "om_audio_success",
        }

    monkeypatch.setattr(flow, "send_audio_to_feishu", fake_send_audio_to_feishu)

    result = flow.publish_report_bundle(
        report_path=report_path,
        report_markdown=report_markdown,
        report_date="2026-04-16",
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert result["status"] == "degraded"
    assert result["doc_status"] == "succeeded"
    assert result["card_status"] == "failed"
    assert result["audio_status"] == "succeeded"
    assert result["audio_opus_path"] == str(opus_path)
    assert result["error_summary"] == "Feishu curated card send failed"
    assert call_order == ["doc", "card_build", "card_send", "audio_bundle", "audio_send"]

    state = json.loads((tmp_path / "publish-state.json").read_text(encoding="utf-8"))
    assert state["status"] == "degraded"
    assert state["doc"]["status"] == "succeeded"
    assert state["doc"]["url"] == "https://feishu.example/doc"
    assert state["card"]["status"] == "failed"
    assert state["card"]["message_id"] is None
    assert state["card"]["payload_path"] == "artifacts/feishu-card.json"
    assert state["card"]["log_path"] == "logs/feishu-card.log"
    assert state["card"]["error_summary"] == "Feishu curated card send failed"
    assert state["audio"]["status"] == "succeeded"
    assert state["missing_required_outputs"] == ["card"]
    assert state["final_delivery_ok"] is False


def test_publish_report_bundle_degrades_when_card_send_has_no_message_id(
    monkeypatch, tmp_path: Path
) -> None:
    report_path = _write_report(tmp_path)
    report_markdown = report_path.read_text(encoding="utf-8")
    opus_path = tmp_path / "2026-04-16-feishu.opus"

    monkeypatch.setattr(
        flow,
        "generate_audio_bundle",
        lambda **_: {
            "status": "succeeded",
            "readout_path": str(tmp_path / "2026-04-16-readout.txt"),
            "intermediate_path": str(tmp_path / "2026-04-16-tts.mp3"),
            "intermediate_format": "mp3",
            "opus_path": str(opus_path),
            "tts_log": str(tmp_path / "logs" / "audio-tts.log"),
            "convert_log": str(tmp_path / "logs" / "audio-opus.log"),
        },
    )
    monkeypatch.setattr(
        flow,
        "import_to_feishu",
        lambda report_path, title, run_dir: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-import.log"),
            "doc_url": "https://feishu.example/doc",
        },
    )
    monkeypatch.setattr(
        flow,
        "build_curated_card_payload",
        lambda **_: {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"}}
            ],
        },
    )
    monkeypatch.setattr(
        flow,
        "send_curated_card_to_feishu",
        lambda **_: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-card.log"),
            "message_id": None,
        },
    )
    monkeypatch.setattr(
        flow,
        "send_audio_to_feishu",
        lambda **_: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-audio.log"),
            "message_id": "om_audio_success",
        },
    )

    result = flow.publish_report_bundle(
        report_path=report_path,
        report_markdown=report_markdown,
        report_date="2026-04-16",
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert result["status"] == "degraded"
    assert result["card_status"] == "failed"
    assert result["error_summary"] == "Feishu curated card send succeeded without message_id"

    state = json.loads((tmp_path / "publish-state.json").read_text(encoding="utf-8"))
    assert state["card"]["status"] == "failed"
    assert state["card"]["message_id"] is None
    assert state["missing_required_outputs"] == ["card"]
    assert state["final_delivery_ok"] is False


def test_publish_report_bundle_audio_failure_keeps_final_delivery_ok_true(
    monkeypatch, tmp_path: Path
) -> None:
    report_path = _write_report(tmp_path)
    report_markdown = report_path.read_text(encoding="utf-8")

    monkeypatch.setattr(
        flow,
        "generate_audio_bundle",
        lambda **_: {
            "status": "failed",
            "readout_path": str(tmp_path / "2026-04-16-readout.txt"),
            "intermediate_path": str(tmp_path / "2026-04-16-tts.mp3"),
            "intermediate_format": "mp3",
            "opus_path": str(tmp_path / "2026-04-16-feishu.opus"),
            "tts_log": str(tmp_path / "logs" / "audio-tts.log"),
            "convert_log": str(tmp_path / "logs" / "audio-opus.log"),
            "error_summary": "MiniMax TTS failed",
        },
    )
    monkeypatch.setattr(
        flow,
        "import_to_feishu",
        lambda report_path, title, run_dir: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-import.log"),
            "doc_url": "https://feishu.example/doc",
        },
    )
    monkeypatch.setattr(
        flow,
        "build_curated_card_payload",
        lambda **_: {
            "config": {"wide_screen_mode": True},
            "header": {"title": {"tag": "plain_text", "content": "AI Agent 日报（2026-04-16）"}},
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": "[查看完整文档](https://feishu.example/doc)"}}
            ],
        },
    )
    monkeypatch.setattr(
        flow,
        "send_curated_card_to_feishu",
        lambda **_: {
            "status": "succeeded",
            "log": str(tmp_path / "logs" / "feishu-card.log"),
            "message_id": "om_card_success",
        },
    )

    result = flow.publish_report_bundle(
        report_path=report_path,
        report_markdown=report_markdown,
        report_date="2026-04-16",
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert result["status"] == "degraded"
    assert result["doc_status"] == "succeeded"
    assert result["card_status"] == "succeeded"
    assert result["audio_status"] == "failed"
    assert result["error_summary"] == "MiniMax TTS failed"

    state = json.loads((tmp_path / "publish-state.json").read_text(encoding="utf-8"))
    assert state["status"] == "degraded"
    assert state["doc"]["status"] == "succeeded"
    assert state["card"]["status"] == "succeeded"
    assert state["audio"]["status"] == "failed"
    assert state["audio"]["log_path"] == "logs/audio-opus.log"
    assert state["audio"]["error_summary"] == "MiniMax TTS failed"
    assert state["missing_required_outputs"] == []
    assert state["final_delivery_ok"] is True


def test_publish_report_bundle_fails_when_doc_import_fails(monkeypatch, tmp_path: Path) -> None:
    report_path = _write_report(tmp_path)
    report_markdown = report_path.read_text(encoding="utf-8")
    send_calls = 0

    monkeypatch.setattr(
        flow,
        "generate_audio_bundle",
        lambda **_: {
            "status": "succeeded",
            "readout_path": str(tmp_path / "2026-04-16-readout.txt"),
            "intermediate_path": str(tmp_path / "2026-04-16-tts.mp3"),
            "intermediate_format": "mp3",
            "opus_path": str(tmp_path / "2026-04-16-feishu.opus"),
            "tts_log": str(tmp_path / "logs" / "audio-tts.log"),
            "convert_log": str(tmp_path / "logs" / "audio-opus.log"),
        },
    )
    monkeypatch.setattr(
        flow,
        "import_to_feishu",
        lambda report_path, title, run_dir: {
            "status": "failed",
            "log": str(tmp_path / "logs" / "feishu-import.log"),
            "error_summary": "Feishu doc import failed",
        },
    )

    def fake_send_audio_to_feishu(**_: object) -> dict:
        nonlocal send_calls
        send_calls += 1
        return {"status": "succeeded"}

    monkeypatch.setattr(flow, "send_audio_to_feishu", fake_send_audio_to_feishu)

    result = flow.publish_report_bundle(
        report_path=report_path,
        report_markdown=report_markdown,
        report_date="2026-04-16",
        title="AI 日报（2026-04-16）",
        run_dir=tmp_path,
        config=_runtime_config(),
    )

    assert result["status"] == "failed"
    assert result["doc_status"] == "failed"
    assert result["audio_status"] == "skipped"
    assert result["error_summary"] == "Feishu doc import failed"
    assert send_calls == 0

    state = json.loads((tmp_path / "publish-state.json").read_text(encoding="utf-8"))
    assert state["status"] == "failed"
    assert state["doc"]["status"] == "failed"
    assert state["card"]["status"] == "skipped"
    assert state["audio"]["status"] == "skipped"
    assert state["missing_required_outputs"] == ["doc", "card"]
    assert state["final_delivery_ok"] is False


def test_archive_report_to_knowledge_wiki_pulls_writes_commits_and_pushes(
    monkeypatch, tmp_path: Path
) -> None:
    report_path = _write_report(tmp_path)
    repo_root = tmp_path / "knowledge-wiki"
    repo_root.mkdir(parents=True, exist_ok=True)
    run_dir = tmp_path / "runtime" / "2026-04-16"
    commands: list[tuple[list[str], str | None]] = []

    config = {
        "archive": {
            "knowledge_wiki": {
                "repo_root": str(repo_root),
                "remote": "origin",
                "branch": "main",
                "daily_report_dir": "raw/inbound/ai-daily-report",
            }
        }
    }

    def fake_subprocess_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        cwd = kwargs.get("cwd")
        commands.append((command, cwd))
        if command == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, "main\n", "")
        if command == ["git", "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, "abc123def456\n", "")
        return subprocess.CompletedProcess(command, 0, "ok\n", "")

    monkeypatch.setattr(flow.subprocess, "run", fake_subprocess_run)

    result = flow.archive_report_to_knowledge_wiki(
        report_path=report_path,
        report_date="2026-04-16",
        run_dir=run_dir,
        config=config,
    )

    archived_path = repo_root / "raw" / "inbound" / "ai-daily-report" / "2026" / "2026-04-16.md"
    assert archived_path.read_text(encoding="utf-8") == report_path.read_text(encoding="utf-8")
    assert commands == [
        (["git", "rev-parse", "--abbrev-ref", "HEAD"], str(repo_root)),
        (["git", "pull", "--ff-only", "origin", "main"], str(repo_root)),
        (["git", "add", "raw/inbound/ai-daily-report/2026/2026-04-16.md"], str(repo_root)),
        (["git", "commit", "-m", "archive(ai-daily-report): 2026-04-16"], str(repo_root)),
        (["git", "rev-parse", "HEAD"], str(repo_root)),
        (["git", "push", "origin", "main"], str(repo_root)),
    ]
    assert result == {
        "status": "succeeded",
        "repo": str(repo_root),
        "remote": "origin",
        "branch": "main",
        "path": str(archived_path),
        "note_path": "raw/inbound/ai-daily-report/2026/2026-04-16.md",
        "commit": "abc123def456",
        "log": str(run_dir / "logs" / "knowledge-wiki-archive.json"),
        "summary": "已归档到 raw/inbound/ai-daily-report/2026/2026-04-16.md @ abc123def456",
    }


def test_archive_report_to_knowledge_wiki_treats_nothing_to_commit_as_succeeded(
    monkeypatch, tmp_path: Path
) -> None:
    report_path = _write_report(tmp_path)
    repo_root = tmp_path / "knowledge-wiki"
    repo_root.mkdir(parents=True, exist_ok=True)
    run_dir = tmp_path / "runtime" / "2026-04-16"
    commands: list[tuple[list[str], str | None]] = []

    config = {
        "archive": {
            "knowledge_wiki": {
                "repo_root": str(repo_root),
                "remote": "origin",
                "branch": "main",
                "daily_report_dir": "raw/inbound/ai-daily-report",
            }
        }
    }

    def fake_subprocess_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        cwd = kwargs.get("cwd")
        commands.append((command, cwd))
        if command == ["git", "rev-parse", "--abbrev-ref", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, "main\n", "")
        if command == ["git", "commit", "-m", "archive(ai-daily-report): 2026-04-16"]:
            return subprocess.CompletedProcess(command, 1, "On branch main\nnothing to commit, working tree clean\n", "")
        if command == ["git", "rev-parse", "HEAD"]:
            return subprocess.CompletedProcess(command, 0, "existingcommit123\n", "")
        return subprocess.CompletedProcess(command, 0, "ok\n", "")

    monkeypatch.setattr(flow.subprocess, "run", fake_subprocess_run)

    result = flow.archive_report_to_knowledge_wiki(
        report_path=report_path,
        report_date="2026-04-16",
        run_dir=run_dir,
        config=config,
    )

    assert commands == [
        (["git", "rev-parse", "--abbrev-ref", "HEAD"], str(repo_root)),
        (["git", "pull", "--ff-only", "origin", "main"], str(repo_root)),
        (["git", "add", "raw/inbound/ai-daily-report/2026/2026-04-16.md"], str(repo_root)),
        (["git", "commit", "-m", "archive(ai-daily-report): 2026-04-16"], str(repo_root)),
        (["git", "rev-parse", "HEAD"], str(repo_root)),
        (["git", "push", "origin", "main"], str(repo_root)),
    ]
    assert result["status"] == "succeeded"
    assert result["commit"] == "existingcommit123"
    assert result["summary"] == "已归档到 raw/inbound/ai-daily-report/2026/2026-04-16.md @ existingcommit123"


def test_main_publish_path_blocks_and_records_contract_failure_before_publish(
    monkeypatch, tmp_path: Path
) -> None:
    invalid_report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 推荐流\n"
        "- 该栏目收录 32 条有用内容。[原帖](https://example.com/x)\n\n"
        "## 来源\n"
        "### X 推荐流\n"
        "- https://example.com/x\n"
    )
    publish_calls = 0
    runtime_root = tmp_path / "runtime"

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-16",
            config=tmp_path / "runtime-config.json",
            skip_collect=True,
            publish=True,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "load_runtime_config",
        lambda _path: {
            "runtime": {"timezone": "Asia/Shanghai"},
            "paths": {
                "signals_root": str(tmp_path / "signals" / "snapshots"),
                "runtime_root": str(runtime_root),
            },
            "reader_facing": {"fixed_section_order": ["x-feed"]},
            "repo_root": str(tmp_path),
        },
    )
    monkeypatch.setattr(flow, "expand_path", lambda value: Path(value))
    monkeypatch.setattr(flow, "is_path_writable", lambda _path: True)
    monkeypatch.setattr(flow, "build_collect_result", lambda **_: {"summary": {"useful_item_count": 1}})
    monkeypatch.setattr(
        flow,
        "resolve_previous_selected_items_path",
        lambda **_: tmp_path / "previous-selected-items.json",
    )
    monkeypatch.setattr(flow, "resolve_lane_item_limits", lambda _config: {"x-feed": 1})
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            }
        },
    )
    monkeypatch.setattr(flow, "build_validation_bundle", lambda **_: {"status": "ok"})
    monkeypatch.setattr(flow, "build_report_artifact", lambda **_: {"body_markdown": invalid_report_markdown})

    def fake_publish_report_bundle(**_: object) -> dict[str, str]:
        nonlocal publish_calls
        publish_calls += 1
        return {"status": "succeeded"}

    monkeypatch.setattr(flow, "publish_report_bundle", fake_publish_report_bundle)

    exit_code = flow.main()

    run_summary = json.loads(
        (runtime_root / "2026-04-16" / "run-summary.json").read_text(encoding="utf-8")
    )

    assert exit_code == 4
    assert publish_calls == 0
    assert run_summary["decision"] == "blocked"
    assert run_summary["reason"] == "report_output_contract_failed"
    assert run_summary["validation"]["status"] == "failed"
    assert run_summary["validation_error"] == "X 推荐流 的正文条目不得使用占位统计文案"
    assert run_summary["publish"] == {
        "status": "skipped",
        "reason": "report_output_contract_failed",
    }
    assert run_summary["ops_notice"]["status"] == "generated"
    ops_notice_path = Path(run_summary["ops_notice"]["path"])
    assert ops_notice_path.exists()
    ops_notice = ops_notice_path.read_text(encoding="utf-8")
    assert "- 状态：blocked" in ops_notice
    assert "reader-facing 成稿未通过输出合同校验：X 推荐流 的正文条目不得使用占位统计文案" in ops_notice


def test_main_skips_signals_engine_collect_for_derived_reader_lanes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "runtime.yaml"
    signals_root = tmp_path / "signals"
    runtime_root = tmp_path / "runtime"
    signals_root.mkdir(parents=True)
    config_path.write_text(
        "version: 1\n"
        f"repo_root: {tmp_path}\n"
        "paths:\n"
        f"  signals_root: {signals_root}\n"
        f"  runtime_root: {runtime_root}\n"
        "selection:\n"
        "  per_lane_limits:\n"
        "    x-feed: 1\n"
        "    github-ai-projects: 5\n"
        "reader_facing:\n"
        "  fixed_section_order:\n"
        "    - x-feed\n"
        "    - github-ai-projects\n"
        "runtime:\n"
        "  timezone: Asia/Shanghai\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-05-04",
            config=config_path,
            skip_collect=False,
            publish=False,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(flow, "is_path_writable", lambda _path: True)

    collect_calls: list[str] = []

    def fake_run_collect_with_retry(**kwargs: object) -> dict[str, object]:
        lane = str(kwargs["lane"])
        collect_calls.append(lane)
        return {"lane": lane, "status": "ok", "attempts": 1, "collect_log": f"collect-{lane}.log"}

    collect_lane_names: list[list[str]] = []

    def fake_build_collect_result(**kwargs: object) -> dict[str, object]:
        lane_names = list(kwargs["lane_names"])
        collect_lane_names.append(lane_names)
        return {
            "report_date": "2026-05-04",
            "source": "test",
            "lanes": [{"name": lane_names[0], "status": "ok", "useful_item_count": 1}],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        }

    selected_lane_names: list[list[str]] = []

    def fake_build_selected_items(**kwargs: object) -> dict[str, object]:
        selected_lane_names.append(list(kwargs["lane_names"]))
        return {
            "report_date": "2026-05-04",
            "source": "test",
            "selected_items": [],
            "summary": {
                "selected_item_count": 0,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 0}],
            },
        }

    monkeypatch.setattr(flow, "run_collect_with_retry", fake_run_collect_with_retry)
    monkeypatch.setattr(flow, "build_collect_result", fake_build_collect_result)
    monkeypatch.setattr(flow, "build_selected_items", fake_build_selected_items)
    monkeypatch.setattr(flow, "validate_report_markdown", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        flow,
        "build_report_artifact",
        lambda **_: {
            "body_markdown": "# AI Agent 日报（2026-05-04）\n\n## 来源\n",
        },
    )

    assert flow.main() == 0

    run_dir = runtime_root / "2026-05-04"
    summary = json.loads((run_dir / "run-summary.json").read_text(encoding="utf-8"))
    collect_result = json.loads((run_dir / "collect-result.json").read_text(encoding="utf-8"))
    selected_items = json.loads((run_dir / "selected-items.json").read_text(encoding="utf-8"))
    validation_bundle = json.loads((run_dir / "validation-bundle.json").read_text(encoding="utf-8"))

    assert collect_calls == ["x-feed"]
    assert collect_lane_names == [[
        "x-feed",
        "github-trending-weekly",
        "x-following",
        "reddit-watch",
        "hacker-news-watch",
        "hacker-news-search-watch",
        "product-hunt-watch",
    ]]
    assert selected_lane_names == collect_lane_names
    assert summary["collect"][1] == {
        "lane": "github-ai-projects",
        "status": "skipped",
        "kind": "derived",
        "reason": "derived_lane_no_direct_collector",
    }
    assert [lane["name"] for lane in collect_result["lanes"]] == ["x-feed", "github-ai-projects"]
    assert collect_result["lanes"][1]["status"] == "ok"
    assert collect_result["lanes"][1]["collection_mode"] == "derived"
    assert collect_result["lanes"][1]["reason"] == "derived_lane_no_direct_collector"
    assert collect_result["lanes"][1]["useful_item_count"] == 0
    assert selected_items["summary"]["lane_counts"] == [
        {"lane": "x-feed", "selected_item_count": 0},
        {"lane": "github-ai-projects", "selected_item_count": 0},
    ]
    assert validation_bundle["summary"]["is_subset"] is True


def test_main_worker_mode_writes_lane_inputs_and_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "runtime.yaml"
    signals_root = tmp_path / "signals"
    runtime_root = tmp_path / "runtime"
    signals_root.mkdir(parents=True)
    config_path.write_text(
        "version: 1\n"
        f"repo_root: {tmp_path}\n"
        "paths:\n"
        f"  signals_root: {signals_root}\n"
        f"  runtime_root: {runtime_root}\n"
        "selection:\n"
        "  per_lane_limits:\n"
        "    github-trending-weekly: 10\n"
        "reader_facing:\n"
        "  fixed_section_order:\n"
        "    - github-trending-weekly\n"
        "runtime:\n"
        "  timezone: Asia/Shanghai\n"
        "lane_workers:\n"
        "  enabled: true\n"
        "  mode: local\n"
        "  enabled_lanes:\n"
        "    - github-trending-weekly\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-27",
            config=config_path,
            skip_collect=True,
            publish=False,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "build_collect_result",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "lanes": [{"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1}],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        },
    )
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "selected_items": [
                {
                    "id": "repo:owner/name",
                    "lane": "github-trending-weekly",
                    "title": "owner/name",
                    "summary": "agent workflow 工具",
                    "excerpt": "agent workflow 工具",
                    "source_snippet": "agent workflow 工具",
                    "source_url": "https://github.com/owner/name",
                    "signal_path": "github-trending-weekly/2026-04-27/signals/name.md",
                    "fetched_at": "2026-04-27T00:00:00Z",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "github-trending-weekly", "selected_item_count": 1}],
            },
        },
    )
    monkeypatch.setattr(flow, "validate_report_markdown", lambda *_args, **_kwargs: None)

    assert flow.main() == 0

    run_dir = runtime_root / "2026-04-27"
    assert (run_dir / "lane-inputs" / "github-trending-weekly.json").is_file()
    assert (run_dir / "lane-outputs" / "github-trending-weekly.json").is_file()
    summary = json.loads((run_dir / "run-summary.json").read_text(encoding="utf-8"))
    assert summary["lane_workers"]["enabled"] is True
    assert summary["lane_workers"]["outputs"]["github-trending-weekly"]["status"] == "ok"


def test_main_subagent_worker_mode_writes_lane_output_via_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "runtime.yaml"
    signals_root = tmp_path / "signals"
    runtime_root = tmp_path / "runtime"
    signals_root.mkdir(parents=True)
    config_path.write_text(
        "version: 1\n"
        f"repo_root: {tmp_path}\n"
        "paths:\n"
        f"  signals_root: {signals_root}\n"
        f"  runtime_root: {runtime_root}\n"
        "selection:\n"
        "  per_lane_limits:\n"
        "    github-trending-weekly: 10\n"
        "reader_facing:\n"
        "  fixed_section_order:\n"
        "    - github-trending-weekly\n"
        "runtime:\n"
        "  timezone: Asia/Shanghai\n"
        "lane_workers:\n"
        "  enabled: true\n"
        "  mode: subagent\n"
        "  enabled_lanes:\n"
        "    - github-trending-weekly\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-27",
            config=config_path,
            skip_collect=True,
            publish=False,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "build_collect_result",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "lanes": [{"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1}],
            "summary": {"useful_item_count": 1, "partial_lane_count": 0},
        },
    )
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "selected_items": [
                {
                    "id": "repo:codex-labs/agent-skills",
                    "lane": "github-trending-weekly",
                    "title": "codex-labs/agent-skills",
                    "summary": "当前可作为候选继续观察，具体变化见来源。",
                    "excerpt": "当前可作为候选继续观察，具体变化见来源。",
                    "source_snippet": (
                        "codex-labs/agent-skills is a catalog of Claude Code and Codex agent skills. "
                        "It ships 42 reusable skills and includes MCP workflow examples."
                    ),
                    "source_url": "https://github.com/codex-labs/agent-skills",
                    "signal_path": "github-trending-weekly/2026-04-27/signals/agent-skills.md",
                    "fetched_at": "2026-04-27T00:00:00Z",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "github-trending-weekly", "selected_item_count": 1}],
            },
        },
    )
    monkeypatch.setattr(flow, "validate_report_markdown", lambda *_args, **_kwargs: None)

    assert flow.main() == 0

    run_dir = runtime_root / "2026-04-27"
    output_path = run_dir / "lane-outputs" / "github-trending-weekly.json"
    log_path = run_dir / "lane-logs" / "github-trending-weekly.md"
    assert output_path.is_file()
    lane_output = json.loads(output_path.read_text(encoding="utf-8"))
    assert lane_output["lane"] == "github-trending-weekly"
    assert "42 reusable skills" in lane_output["markdown"]
    log_text = log_path.read_text(encoding="utf-8")
    assert "-m helpers.lane_subagent_worker" in log_text
    assert "STDOUT" in log_text
    assert "github-trending-weekly" in log_text
    summary = json.loads((run_dir / "run-summary.json").read_text(encoding="utf-8"))
    lane_summary = summary["lane_workers"]["outputs"]["github-trending-weekly"]
    assert lane_summary["status"] == "ok"
    assert lane_summary["output_path"] == str(output_path)
    assert lane_summary["log_path"] == str(log_path)


def test_build_lane_input_artifact_for_github_ai_projects_includes_cross_lane_repo_mentions() -> None:
    selected_items = {
        "report_date": "2026-04-27",
        "selected_items": [
            {
                "id": "gh:1",
                "lane": "github-trending-weekly",
                "title": "owner/trending-agent",
                "source_url": "https://github.com/owner/trending-agent",
            },
            {
                "id": "x:1",
                "lane": "x-following",
                "title": "@dev",
                "summary": "推荐 owner/trending-agent 做 agent 编排",
                "source_url": "https://x.com/dev/status/1",
            },
            {
                "id": "ph:1",
                "lane": "product-hunt-watch",
                "title": "Another Tool",
                "summary": "没有 repo",
                "source_url": "https://producthunt.com/posts/tool",
            },
            {
                "id": "cc:1",
                "lane": "claude-code-watch",
                "title": "owner/not-included",
                "summary": "非候选 lane 不能进入 GitHub AI Projects 输入",
                "source_url": "https://github.com/owner/not-included",
            },
        ],
        "summary": {"selected_item_count": 4, "lane_counts": []},
    }

    payload = flow.build_lane_input_artifact(
        report_date="2026-04-27",
        lane_name="github-ai-projects",
        selected_items=selected_items,
    )

    source_lanes = {item["source_lane"] for item in payload["signals"]}
    assert source_lanes == {"github-trending-weekly", "x-following"}
    assert all(item["source_urls"] for item in payload["signals"])
    assert payload["cross_lane_context"]["github_search_queries"] == [
        "GitHub trending AI 2026-04-27",
        "GitHub new AI projects 2026-04-27",
        "awesome AI GitHub 2026-04-27",
    ]


def test_build_lane_input_artifact_for_github_ai_projects_uses_configured_discovery_queries() -> None:
    payload = flow.build_lane_input_artifact(
        report_date="2026-04-27",
        lane_name="github-ai-projects",
        selected_items={"report_date": "2026-04-27", "selected_items": []},
        config={
            "lane_workers": {
                "github_ai_projects": {
                    "discovery_queries": [
                        "GitHub trending AI {date}",
                        "GitHub new AI projects {report_date}",
                    ]
                }
            }
        },
    )

    assert payload["signals"] == []
    assert payload["cross_lane_context"]["github_search_queries"] == [
        "GitHub trending AI 2026-04-27",
        "GitHub new AI projects 2026-04-27",
    ]


def test_main_worker_mode_writes_github_ai_projects_memory_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "runtime.yaml"
    signals_root = tmp_path / "signals"
    runtime_root = tmp_path / "runtime"
    compat_memory_dir = tmp_path / "memory" / "github-ai-projects"
    signals_root.mkdir(parents=True)
    config_path.write_text(
        "version: 1\n"
        f"repo_root: {tmp_path}\n"
        "paths:\n"
        f"  signals_root: {signals_root}\n"
        f"  runtime_root: {runtime_root}\n"
        "selection:\n"
        "  per_lane_limits:\n"
        "    github-ai-projects: 5\n"
        "reader_facing:\n"
        "  fixed_section_order:\n"
        "    - github-ai-projects\n"
        "runtime:\n"
        "  timezone: Asia/Shanghai\n"
        "lane_workers:\n"
        "  enabled: true\n"
        "  mode: local\n"
        "  enabled_lanes:\n"
        "    - github-ai-projects\n"
        "  github_ai_projects:\n"
        "    discovery_queries:\n"
        "      - GitHub trending AI {date}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-27",
            config=config_path,
            skip_collect=True,
            publish=False,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "build_collect_result",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "lanes": [
                {"name": "github-ai-projects", "status": "ok", "useful_item_count": 1},
                {"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        },
    )
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "selected_items": [
                {
                    "id": "repo:owner/name",
                    "lane": "github-trending-weekly",
                    "title": "owner/name",
                    "summary": "agent workflow 工具",
                    "excerpt": "agent workflow 工具",
                    "source_snippet": "agent workflow 工具",
                    "source_url": "https://github.com/owner/name",
                    "signal_path": "github-trending-weekly/2026-04-27/signals/name.md",
                    "fetched_at": "2026-04-27T00:00:00Z",
                }
            ],
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "github-trending-weekly", "selected_item_count": 1}],
            },
        },
    )
    monkeypatch.setattr(flow, "validate_report_markdown", lambda *_args, **_kwargs: None)

    assert flow.main() == 0

    run_dir = runtime_root / "2026-04-27"
    memory_path = run_dir / "lane-memory" / "github-ai-projects.md"
    assert memory_path.is_file()
    assert "owner/name" in memory_path.read_text(encoding="utf-8")
    assert not (compat_memory_dir / "2026-04-27.md").exists()
    summary = json.loads((run_dir / "run-summary.json").read_text(encoding="utf-8"))
    lane_summary = summary["lane_workers"]["outputs"]["github-ai-projects"]
    assert lane_summary["memory_path"] == str(memory_path)
    assert "memory_repo_path" not in lane_summary


def test_main_worker_mode_requires_all_fixed_order_lanes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "runtime.yaml"
    signals_root = tmp_path / "signals"
    runtime_root = tmp_path / "runtime"
    signals_root.mkdir(parents=True)
    config_path.write_text(
        "version: 1\n"
        f"repo_root: {tmp_path}\n"
        "paths:\n"
        f"  signals_root: {signals_root}\n"
        f"  runtime_root: {runtime_root}\n"
        "reader_facing:\n"
        "  fixed_section_order:\n"
        "    - github-trending-weekly\n"
        "    - product-hunt-watch\n"
        "runtime:\n"
        "  timezone: Asia/Shanghai\n"
        "lane_workers:\n"
        "  enabled: true\n"
        "  mode: local\n"
        "  enabled_lanes:\n"
        "    - github-trending-weekly\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-27",
            config=config_path,
            skip_collect=True,
            publish=False,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "build_collect_result",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "lanes": [
                {"name": "github-trending-weekly", "status": "ok", "useful_item_count": 1},
                {"name": "product-hunt-watch", "status": "ok", "useful_item_count": 1},
            ],
            "summary": {"useful_item_count": 2, "partial_lane_count": 0},
        },
    )
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "report_date": "2026-04-27",
            "source": "test",
            "selected_items": [],
            "summary": {
                "selected_item_count": 0,
                "lane_counts": [
                    {"lane": "github-trending-weekly", "selected_item_count": 0},
                    {"lane": "product-hunt-watch", "selected_item_count": 0},
                ],
            },
        },
    )

    with pytest.raises(ValueError, match="requires all fixed_section_order lanes"):
        flow.main()


def test_main_writes_ops_notice_when_publish_degrades(monkeypatch, tmp_path: Path) -> None:
    valid_report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 推荐流\n"
        "- Claude Code 新增了 review gate，并补了失败原因。[原帖](https://example.com/x)\n\n"
        "## 来源\n"
        "### X 推荐流\n"
        "- https://example.com/x\n"
    )
    runtime_root = tmp_path / "runtime"

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-16",
            config=tmp_path / "runtime-config.json",
            skip_collect=True,
            publish=True,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "load_runtime_config",
        lambda _path: {
            "runtime": {"timezone": "Asia/Shanghai"},
            "paths": {
                "signals_root": str(tmp_path / "signals" / "snapshots"),
                "runtime_root": str(runtime_root),
            },
            "reader_facing": {"fixed_section_order": ["x-feed"]},
            "repo_root": str(tmp_path),
        },
    )
    monkeypatch.setattr(flow, "expand_path", lambda value: Path(value))
    monkeypatch.setattr(flow, "is_path_writable", lambda _path: True)
    monkeypatch.setattr(flow, "build_collect_result", lambda **_: {"summary": {"useful_item_count": 1}})
    monkeypatch.setattr(
        flow,
        "resolve_previous_selected_items_path",
        lambda **_: tmp_path / "previous-selected-items.json",
    )
    monkeypatch.setattr(flow, "resolve_lane_item_limits", lambda _config: {"x-feed": 1})
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            }
        },
    )
    monkeypatch.setattr(flow, "build_validation_bundle", lambda **_: {"status": "ok"})
    monkeypatch.setattr(flow, "build_report_artifact", lambda **_: {"body_markdown": valid_report_markdown})
    monkeypatch.setattr(
        flow,
        "publish_report_bundle",
        lambda **_: {
            "status": "degraded",
            "doc_url": "https://example.com/doc",
            "error_summary": "Feishu audio send failed",
        },
    )

    exit_code = flow.main()

    run_summary = json.loads(
        (runtime_root / "2026-04-16" / "run-summary.json").read_text(encoding="utf-8")
    )

    assert exit_code == 0
    assert run_summary["publish"]["status"] == "degraded"
    assert run_summary["ops_notice"]["status"] == "generated"
    ops_notice = Path(run_summary["ops_notice"]["path"]).read_text(encoding="utf-8")
    assert "- 状态：degraded" in ops_notice
    assert "- 原因：Feishu audio send failed" in ops_notice
    assert "- 发布引用：https://example.com/doc" in ops_notice


def test_main_archives_report_after_publish_success(monkeypatch, tmp_path: Path) -> None:
    valid_report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 推荐流\n"
        "- Claude Code 新增了 review gate，并补了失败原因。[原帖](https://example.com/x)\n\n"
        "## 来源\n"
        "### X 推荐流\n"
        "- https://example.com/x\n"
    )
    runtime_root = tmp_path / "runtime"
    archive_repo = tmp_path / "knowledge-wiki"
    sequence: list[str] = []

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-16",
            config=tmp_path / "runtime-config.json",
            skip_collect=True,
            publish=True,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "load_runtime_config",
        lambda _path: {
            "runtime": {"timezone": "Asia/Shanghai"},
            "paths": {
                "signals_root": str(tmp_path / "signals" / "snapshots"),
                "runtime_root": str(runtime_root),
            },
            "reader_facing": {"fixed_section_order": ["x-feed"]},
            "repo_root": str(tmp_path),
            "archive": {
                "knowledge_wiki": {
                    "repo_root": str(archive_repo),
                    "remote": "origin",
                    "branch": "main",
                    "daily_report_dir": "raw/inbound/ai-daily-report",
                }
            },
        },
    )
    monkeypatch.setattr(flow, "expand_path", lambda value: Path(value))
    monkeypatch.setattr(flow, "is_path_writable", lambda _path: True)
    monkeypatch.setattr(flow, "build_collect_result", lambda **_: {"summary": {"useful_item_count": 1}})
    monkeypatch.setattr(
        flow,
        "resolve_previous_selected_items_path",
        lambda **_: tmp_path / "previous-selected-items.json",
    )
    monkeypatch.setattr(flow, "resolve_lane_item_limits", lambda _config: {"x-feed": 1})
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            }
        },
    )
    monkeypatch.setattr(flow, "build_validation_bundle", lambda **_: {"status": "ok"})
    monkeypatch.setattr(flow, "build_report_artifact", lambda **_: {"body_markdown": valid_report_markdown})

    def fake_publish_report_bundle(**_: object) -> dict[str, str]:
        sequence.append("publish")
        return {
            "status": "succeeded",
            "doc_status": "succeeded",
            "doc_url": "https://example.com/doc",
        }

    def fake_archive_report_to_knowledge_wiki(
        *, report_path: Path, report_date: str, run_dir: Path, config: dict
    ) -> dict[str, str]:
        sequence.append("archive")
        assert report_date == "2026-04-16"
        assert report_path == run_dir / "report.md"
        assert report_path.read_text(encoding="utf-8") == valid_report_markdown
        assert config["archive"]["knowledge_wiki"]["repo_root"] == str(archive_repo)
        return {
            "status": "succeeded",
            "repo": str(archive_repo),
            "remote": "origin",
            "branch": "main",
            "path": str(archive_repo / "raw" / "inbound" / "ai-daily-report" / "2026" / "2026-04-16.md"),
            "note_path": "raw/inbound/ai-daily-report/2026/2026-04-16.md",
            "commit": "abc123def456",
            "log": str(run_dir / "logs" / "knowledge-wiki-archive.json"),
            "summary": "已归档到 raw/inbound/ai-daily-report/2026/2026-04-16.md @ abc123def456",
        }

    monkeypatch.setattr(flow, "publish_report_bundle", fake_publish_report_bundle)
    monkeypatch.setattr(flow, "archive_report_to_knowledge_wiki", fake_archive_report_to_knowledge_wiki)

    exit_code = flow.main()

    run_summary = json.loads(
        (runtime_root / "2026-04-16" / "run-summary.json").read_text(encoding="utf-8")
    )

    assert exit_code == 0
    assert sequence == ["publish", "archive"]
    assert run_summary["decision"] == "generated"
    assert run_summary["publish"]["status"] == "succeeded"
    assert run_summary["archive"] == {
        "status": "succeeded",
        "repo": str(archive_repo),
        "remote": "origin",
        "branch": "main",
        "path": str(archive_repo / "raw" / "inbound" / "ai-daily-report" / "2026" / "2026-04-16.md"),
        "note_path": "raw/inbound/ai-daily-report/2026/2026-04-16.md",
        "commit": "abc123def456",
        "log": str(runtime_root / "2026-04-16" / "logs" / "knowledge-wiki-archive.json"),
        "summary": "已归档到 raw/inbound/ai-daily-report/2026/2026-04-16.md @ abc123def456",
    }


def test_main_archives_report_when_publish_is_degraded_but_doc_succeeds(monkeypatch, tmp_path: Path) -> None:
    valid_report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 推荐流\n"
        "- Claude Code 新增了 review gate，并补了失败原因。[原帖](https://example.com/x)\n\n"
        "## 来源\n"
        "### X 推荐流\n"
        "- https://example.com/x\n"
    )
    runtime_root = tmp_path / "runtime"
    archive_repo = tmp_path / "knowledge-wiki"
    sequence: list[str] = []

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-16",
            config=tmp_path / "runtime-config.json",
            skip_collect=True,
            publish=True,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "load_runtime_config",
        lambda _path: {
            "runtime": {"timezone": "Asia/Shanghai"},
            "paths": {
                "signals_root": str(tmp_path / "signals" / "snapshots"),
                "runtime_root": str(runtime_root),
            },
            "reader_facing": {"fixed_section_order": ["x-feed"]},
            "repo_root": str(tmp_path),
            "archive": {
                "knowledge_wiki": {
                    "repo_root": str(archive_repo),
                    "remote": "origin",
                    "branch": "main",
                    "daily_report_dir": "raw/inbound/ai-daily-report",
                }
            },
        },
    )
    monkeypatch.setattr(flow, "expand_path", lambda value: Path(value))
    monkeypatch.setattr(flow, "is_path_writable", lambda _path: True)
    monkeypatch.setattr(flow, "build_collect_result", lambda **_: {"summary": {"useful_item_count": 1}})
    monkeypatch.setattr(
        flow,
        "resolve_previous_selected_items_path",
        lambda **_: tmp_path / "previous-selected-items.json",
    )
    monkeypatch.setattr(flow, "resolve_lane_item_limits", lambda _config: {"x-feed": 1})
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            }
        },
    )
    monkeypatch.setattr(flow, "build_validation_bundle", lambda **_: {"status": "ok"})
    monkeypatch.setattr(flow, "build_report_artifact", lambda **_: {"body_markdown": valid_report_markdown})

    def fake_publish_report_bundle(**_: object) -> dict[str, str]:
        sequence.append("publish")
        return {
            "status": "degraded",
            "doc_status": "succeeded",
            "doc_url": "https://example.com/doc",
            "error_summary": "Feishu audio send failed",
        }

    def fake_archive_report_to_knowledge_wiki(
        *, report_path: Path, report_date: str, run_dir: Path, config: dict
    ) -> dict[str, str]:
        sequence.append("archive")
        assert report_date == "2026-04-16"
        assert report_path == run_dir / "report.md"
        assert report_path.read_text(encoding="utf-8") == valid_report_markdown
        assert config["archive"]["knowledge_wiki"]["repo_root"] == str(archive_repo)
        return {
            "status": "succeeded",
            "repo": str(archive_repo),
            "remote": "origin",
            "branch": "main",
            "path": str(archive_repo / "raw" / "inbound" / "ai-daily-report" / "2026" / "2026-04-16.md"),
            "note_path": "raw/inbound/ai-daily-report/2026/2026-04-16.md",
            "commit": "abc123def456",
            "log": str(run_dir / "logs" / "knowledge-wiki-archive.json"),
            "summary": "已归档到 raw/inbound/ai-daily-report/2026/2026-04-16.md @ abc123def456",
        }

    monkeypatch.setattr(flow, "publish_report_bundle", fake_publish_report_bundle)
    monkeypatch.setattr(flow, "archive_report_to_knowledge_wiki", fake_archive_report_to_knowledge_wiki)

    exit_code = flow.main()

    run_summary = json.loads(
        (runtime_root / "2026-04-16" / "run-summary.json").read_text(encoding="utf-8")
    )

    assert exit_code == 0
    assert sequence == ["publish", "archive"]
    assert run_summary["decision"] == "generated"
    assert run_summary["publish"]["status"] == "degraded"
    assert run_summary["archive"]["status"] == "succeeded"
    assert "ops_notice" in run_summary


def test_main_archive_failure_degrades_run_after_publish_success(monkeypatch, tmp_path: Path) -> None:
    valid_report_markdown = (
        "# AI Agent 日报（2026-04-16）\n\n"
        "## X 推荐流\n"
        "- Claude Code 新增了 review gate，并补了失败原因。[原帖](https://example.com/x)\n\n"
        "## 来源\n"
        "### X 推荐流\n"
        "- https://example.com/x\n"
    )
    runtime_root = tmp_path / "runtime"
    archive_repo = tmp_path / "knowledge-wiki"
    sequence: list[str] = []

    monkeypatch.setattr(
        flow,
        "parse_args",
        lambda: argparse.Namespace(
            report_date="2026-04-16",
            config=tmp_path / "runtime-config.json",
            skip_collect=True,
            publish=True,
            title_suffix="",
            verbose=False,
        ),
    )
    monkeypatch.setattr(
        flow,
        "load_runtime_config",
        lambda _path: {
            "runtime": {"timezone": "Asia/Shanghai"},
            "paths": {
                "signals_root": str(tmp_path / "signals" / "snapshots"),
                "runtime_root": str(runtime_root),
            },
            "reader_facing": {"fixed_section_order": ["x-feed"]},
            "repo_root": str(tmp_path),
            "archive": {
                "knowledge_wiki": {
                    "repo_root": str(archive_repo),
                    "remote": "origin",
                    "branch": "main",
                    "daily_report_dir": "raw/inbound/ai-daily-report",
                }
            },
        },
    )
    monkeypatch.setattr(flow, "expand_path", lambda value: Path(value))
    monkeypatch.setattr(flow, "is_path_writable", lambda _path: True)
    monkeypatch.setattr(flow, "build_collect_result", lambda **_: {"summary": {"useful_item_count": 1}})
    monkeypatch.setattr(
        flow,
        "resolve_previous_selected_items_path",
        lambda **_: tmp_path / "previous-selected-items.json",
    )
    monkeypatch.setattr(flow, "resolve_lane_item_limits", lambda _config: {"x-feed": 1})
    monkeypatch.setattr(
        flow,
        "build_selected_items",
        lambda **_: {
            "summary": {
                "selected_item_count": 1,
                "lane_counts": [{"lane": "x-feed", "selected_item_count": 1}],
            }
        },
    )
    monkeypatch.setattr(flow, "build_validation_bundle", lambda **_: {"status": "ok"})
    monkeypatch.setattr(flow, "build_report_artifact", lambda **_: {"body_markdown": valid_report_markdown})

    def fake_publish_report_bundle(**_: object) -> dict[str, str]:
        sequence.append("publish")
        return {
            "status": "succeeded",
            "doc_status": "succeeded",
            "doc_url": "https://example.com/doc",
        }

    def fake_archive_report_to_knowledge_wiki(
        *, report_path: Path, report_date: str, run_dir: Path, config: dict
    ) -> dict[str, str]:
        del report_path, report_date, run_dir, config
        sequence.append("archive")
        return {
            "status": "failed",
            "repo": str(archive_repo),
            "remote": "origin",
            "branch": "main",
            "note_path": "raw/inbound/ai-daily-report/2026/2026-04-16.md",
            "log": str(runtime_root / "2026-04-16" / "logs" / "knowledge-wiki-archive.json"),
            "error_summary": "knowledge-wiki push failed",
            "summary": "归档失败：knowledge-wiki push failed",
        }

    monkeypatch.setattr(flow, "publish_report_bundle", fake_publish_report_bundle)
    monkeypatch.setattr(flow, "archive_report_to_knowledge_wiki", fake_archive_report_to_knowledge_wiki)

    exit_code = flow.main()

    run_summary = json.loads(
        (runtime_root / "2026-04-16" / "run-summary.json").read_text(encoding="utf-8")
    )

    assert exit_code == 0
    assert sequence == ["publish", "archive"]
    assert run_summary["publish"]["status"] == "succeeded"
    assert run_summary["decision"] == "degraded"
    assert run_summary["archive"]["status"] == "failed"
    assert run_summary["archive"]["error_summary"] == "knowledge-wiki push failed"
    assert run_summary["ops_notice"]["status"] == "generated"
    ops_notice = Path(run_summary["ops_notice"]["path"]).read_text(encoding="utf-8")
    assert "- 状态：degraded" in ops_notice
    assert "- 原因：knowledge-wiki push failed" in ops_notice
    assert "- 发布引用：https://example.com/doc" in ops_notice
    assert "- 归档信息：归档失败：knowledge-wiki push failed" in ops_notice
