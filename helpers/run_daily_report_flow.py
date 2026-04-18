from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from helpers.runtime_config import DEFAULT_RUNTIME_CONFIG_PATH, load_runtime_config, resolve_lane_item_limits
from helpers.signals_adapter import (
    build_collect_result,
    build_report_artifact,
    build_selected_items,
    build_validation_bundle,
    dump_json,
    resolve_previous_selected_items_path,
)
from helpers.validate_report_output_contract import validate_report_markdown


@dataclass
class CommandResult:
    command: list[str]
    exit_code: int
    output_path: str
    stdout: str
    stderr: str


DEFAULT_AUDIO_VOICE_ID = "Chinese (Mandarin)_Soft_Girl"
DEFAULT_AUDIO_TTS_MODEL = "speech-2.8-hd"
DEFAULT_AUDIO_INTERMEDIATE_FORMAT = "mp3"
DEFAULT_FEISHU_APP_ID_ENV = "FEISHU_APP_ID"
DEFAULT_FEISHU_APP_SECRET_ENV = "FEISHU_APP_SECRET"
DEFAULT_FEISHU_RECEIVE_ID_ENV = "FEISHU_HOME_CHANNEL"
DEFAULT_FEISHU_RECEIVE_ID_TYPE = "chat_id"
FEISHU_OPEN_API_BASE = "https://open.feishu.cn/open-apis"
FEISHU_AUDIO_SKILL_DIR = Path.home() / ".hermes" / "skills" / "productivity" / "feishu-playable-daily-audio"
MINIMAX_TTS_SCRIPT = FEISHU_AUDIO_SKILL_DIR / "scripts" / "generate_minimax_tts.py"
FEISHU_OPUS_SCRIPT = FEISHU_AUDIO_SKILL_DIR / "scripts" / "convert_to_feishu_opus.py"
READOUT_INTRO = "以下是今天的 AI Agent 日报语音简报。"
READOUT_OUTRO = "以上就是今天的重点内容，感谢收听。"
READOUT_PLACEHOLDER_SNIPPETS = ("原文围绕", "具体变化见来源", "值得关注")
READOUT_DROP_LINK_LABELS = {"原帖", "release", "github", "product hunt", "polymarket"}
READOUT_SECTION_TRANSITIONS = {
    "Reddit 社区": "下面是 Reddit 社区。",
    "Claude Code": "接着是 Claude Code。",
    "Codex": "接着是 Codex。",
    "OpenClaw": "接着是 OpenClaw。",
    "GitHub 趋势项目": "接着看 GitHub 趋势项目。",
    "Product Hunt 新品": "再来看 Product Hunt 新品。",
    "Polymarket 市场": "再来看 Polymarket 市场。",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the daily-report-master flow end to end.")
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_RUNTIME_CONFIG_PATH)
    parser.add_argument("--skip-collect", action="store_true")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--title-suffix", default="")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def is_path_writable(path: Path) -> bool:
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return os.access(candidate, os.W_OK)


def shanghai_date() -> str:
    result = subprocess.run(["date", "+%F"], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def parse_dotenv_value(raw_value: str) -> str:
    value = raw_value.strip()
    quoted_match = re.match(r"""^(['"])(.*)\1(?:\s+#.*)?$""", value)
    if quoted_match:
        return quoted_match.group(2)
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def load_hermes_minimax_env() -> dict[str, str]:
    env_path = Path.home() / ".hermes" / ".env"
    try:
        raw_text = env_path.read_text(encoding="utf-8")
    except OSError:
        return {}

    minimax_env: dict[str, str] = {}
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key.startswith("MINIMAX_"):
            continue
        value = parse_dotenv_value(raw_value)
        if value:
            minimax_env[key] = value
    return minimax_env


def build_minimax_tts_env() -> dict[str, str]:
    env = os.environ.copy()
    for key, value in load_hermes_minimax_env().items():
        env.setdefault(key, value)
    return env


def run_and_capture(
    command: list[str],
    output_path: Path,
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        env=env,
    )
    rendered = f"$ {' '.join(command)}\n\nSTDOUT:\n{completed.stdout}\n\nSTDERR:\n{completed.stderr}"
    output_path.write_text(rendered, encoding="utf-8")
    return CommandResult(
        command=command,
        exit_code=completed.returncode,
        output_path=str(output_path),
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def run_collect_with_retry(*, lane: str, report_date: str, data_dir: Path, run_dir: Path, verbose: bool) -> dict[str, Any]:
    base_cmd = [
        "uvx",
        "--from",
        str(Path.home() / "workspace" / "signals-engine"),
        "signals-engine",
        "collect",
        "--lane",
        lane,
        "--date",
        report_date,
        "--data-dir",
        str(data_dir),
    ]
    first = run_and_capture(base_cmd, run_dir / "logs" / f"collect-{lane}.log")
    if verbose:
        print(f"collect {lane}: exit={first.exit_code}")
    if first.exit_code == 0:
        return {"lane": lane, "status": "ok", "attempts": 1, "collect_log": first.output_path}

    diagnose_cmd = [
        "uvx",
        "--from",
        str(Path.home() / "workspace" / "signals-engine"),
        "signals-engine",
        "diagnose",
        "--lane",
        lane,
        "--data-dir",
        str(data_dir),
    ]
    diagnose = run_and_capture(diagnose_cmd, run_dir / "logs" / f"diagnose-{lane}.log")
    retry = run_and_capture(base_cmd, run_dir / "logs" / f"collect-{lane}-retry.log")
    status = "ok" if retry.exit_code == 0 else "failed"
    if verbose:
        print(f"collect {lane}: retry exit={retry.exit_code}")
    return {
        "lane": lane,
        "status": status,
        "attempts": 2,
        "collect_log": first.output_path,
        "diagnose_log": diagnose.output_path,
        "retry_log": retry.output_path,
    }


def import_to_feishu(report_path: Path, title: str, run_dir: Path) -> dict[str, Any]:
    cmd = ["feishu-cli", "doc", "import", str(report_path), "--title", title]
    result = run_and_capture(cmd, run_dir / "logs" / "feishu-import.log")
    if result.exit_code != 0:
        return {
            "status": "failed",
            "log": result.output_path,
            "error_summary": "Feishu doc import failed",
        }
    text = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"链接:\s*(https://\S+)", text)
    if match is None:
        match = re.search(r"(https://\S+)", text)
    return {
        "status": "succeeded",
        "log": result.output_path,
        "doc_url": match.group(1) if match else None,
    }


def resolve_audio_settings(config: dict[str, Any]) -> dict[str, Any]:
    audio = config.get("audio") or {}
    tts = audio.get("tts") or {}
    delivery = audio.get("delivery") or {}
    intermediate_format = str(tts.get("intermediate_format") or DEFAULT_AUDIO_INTERMEDIATE_FORMAT).lstrip(".").lower()
    if not intermediate_format:
        intermediate_format = DEFAULT_AUDIO_INTERMEDIATE_FORMAT
    return {
        "tts": {
            "default_voice_id": str(tts.get("default_voice_id") or DEFAULT_AUDIO_VOICE_ID),
            "model": str(tts.get("model") or DEFAULT_AUDIO_TTS_MODEL),
            "intermediate_format": intermediate_format,
        },
        "delivery": {
            "receive_id_env": str(delivery.get("receive_id_env") or DEFAULT_FEISHU_RECEIVE_ID_ENV),
            "receive_id_type": str(delivery.get("receive_id_type") or DEFAULT_FEISHU_RECEIVE_ID_TYPE),
        },
    }


def build_audio_artifact_paths(*, report_date: str, run_dir: Path, intermediate_format: str) -> dict[str, Path]:
    suffix = intermediate_format.lstrip(".").lower() or DEFAULT_AUDIO_INTERMEDIATE_FORMAT
    return {
        "readout_path": run_dir / f"{report_date}-readout.txt",
        "intermediate_path": run_dir / f"{report_date}-tts.{suffix}",
        "opus_path": run_dir / f"{report_date}-feishu.opus",
    }


def _truncate_sources_tail(text: str) -> str:
    sources_match = re.search(r"^##\s*来源\s*$", text, flags=re.M)
    if sources_match:
        return text[: sources_match.start()].rstrip()
    return text


def _replace_readout_link(match: re.Match[str]) -> str:
    label = match.group(1).strip()
    normalized = re.sub(r"\s+", " ", label).strip().lower()
    if normalized in READOUT_DROP_LINK_LABELS:
        return ""
    return label


def _clean_readout_fragment(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", _replace_readout_link, text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
    text = re.sub(r"_([^_\n]+)_", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[，,、 ]*(?:另见|详见|参见|可参考|具体可参考|更多见)\s*$", "", text)
    text = re.sub(r"[（(]\s*[)）]", "", text)
    text = re.sub(r"\s+([，。！？；：,.!?;:])", r"\1", text)
    text = re.sub(r"[，,、；;：: ]+$", "", text)
    text = re.sub(r"^[：:，,、\- ]+", "", text)
    return text.strip()


def _to_spoken_sentence(text: str) -> str:
    cleaned = _clean_readout_fragment(text)
    if not cleaned:
        return ""
    cleaned = re.sub(r"\b([A-Za-z0-9_.+-]+(?:\s+[A-Za-z0-9_.+-]+){0,3})\s+\1\b", r"\1", cleaned)
    cleaned = re.sub(r"[。！？；：,.!?;:，、 ]+$", "", cleaned).strip()
    if not cleaned:
        return ""
    return f"{cleaned}。"


def _build_section_transition(heading: str) -> str:
    cleaned = _clean_readout_fragment(heading)
    if not cleaned:
        return ""
    if cleaned.endswith("推荐流"):
        return f"先来看 {cleaned}。"
    if cleaned.endswith("关注流"):
        return f"再来看 {cleaned}。"
    return READOUT_SECTION_TRANSITIONS.get(cleaned, f"接着看 {cleaned}。")


def _select_readout_items(items: list[str], *, limit: int = 2) -> list[str]:
    selected: list[str] = []
    for raw_item in items:
        if any(snippet in raw_item for snippet in READOUT_PLACEHOLDER_SNIPPETS):
            continue
        sentence = _to_spoken_sentence(raw_item)
        if not sentence:
            continue
        if any(snippet in sentence for snippet in READOUT_PLACEHOLDER_SNIPPETS):
            continue
        selected.append(sentence)
        if len(selected) >= limit:
            break
    return selected


def build_readout_text(report_markdown: str) -> str:
    text = report_markdown.replace("\r\n", "\n").strip()
    text = _truncate_sources_tail(text)
    text = re.sub(r"```.*?```", "\n", text, flags=re.S)
    default_items: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_items: list[str] = []
    current_item_lines: list[str] | None = None

    def flush_item() -> None:
        nonlocal current_item_lines
        if current_item_lines is None:
            return
        item_text = " ".join(line for line in current_item_lines if line).strip()
        current_item_lines = None
        if not item_text:
            return
        if current_heading is None:
            default_items.append(item_text)
        else:
            current_items.append(item_text)

    def flush_section() -> None:
        nonlocal current_heading, current_items
        if current_heading is None:
            return
        sections.append((current_heading, current_items[:]))
        current_heading = None
        current_items = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_item()
            continue

        heading_match = re.match(r"^(#{1,6})\s*(.+?)\s*$", line)
        if heading_match:
            flush_item()
            flush_section()
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if heading_level == 1 and "日报" in heading_text:
                continue
            current_heading = heading_text
            current_items = []
            continue

        bullet_match = re.match(r"^(?:[-*+]|\d+\.)\s+(.*)$", line)
        if bullet_match:
            flush_item()
            current_item_lines = [bullet_match.group(1).strip()]
            continue

        if current_item_lines is not None:
            current_item_lines.append(line)
            continue

        if current_heading is None:
            default_items.append(line)
        else:
            current_items.append(line)

    flush_item()
    flush_section()

    spoken_lines: list[str] = []
    spoken_lines.extend(_select_readout_items(default_items))
    for heading, items in sections:
        spoken_items = _select_readout_items(items)
        if not spoken_items:
            continue
        transition = _build_section_transition(heading)
        if transition:
            spoken_lines.append(transition)
        spoken_lines.extend(spoken_items)

    if not spoken_lines:
        return ""
    return "\n".join([READOUT_INTRO, *spoken_lines, READOUT_OUTRO]).strip()


def generate_audio_bundle(*, report_markdown: str, report_date: str, run_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    settings = resolve_audio_settings(config)
    tts_settings = settings["tts"]
    paths = build_audio_artifact_paths(
        report_date=report_date,
        run_dir=run_dir,
        intermediate_format=tts_settings["intermediate_format"],
    )
    tts_log_path = run_dir / "logs" / "audio-tts.log"
    convert_log_path = run_dir / "logs" / "audio-opus.log"

    try:
        for artifact_path in (*paths.values(), tts_log_path, convert_log_path):
            artifact_path.parent.mkdir(parents=True, exist_ok=True)

        readout_text = build_readout_text(report_markdown)
        if not readout_text:
            return {
                "status": "failed",
                "readout_path": str(paths["readout_path"]),
                "intermediate_path": str(paths["intermediate_path"]),
                "intermediate_format": tts_settings["intermediate_format"],
                "opus_path": str(paths["opus_path"]),
                "tts_log": str(tts_log_path),
                "convert_log": str(convert_log_path),
                "error_summary": "Readout text is empty after markdown cleanup",
            }

        if not MINIMAX_TTS_SCRIPT.is_file():
            return {
                "status": "failed",
                "readout_path": str(paths["readout_path"]),
                "intermediate_path": str(paths["intermediate_path"]),
                "intermediate_format": tts_settings["intermediate_format"],
                "opus_path": str(paths["opus_path"]),
                "tts_log": str(tts_log_path),
                "convert_log": str(convert_log_path),
                "error_summary": f"Missing MiniMax TTS script: {MINIMAX_TTS_SCRIPT}",
            }

        if not FEISHU_OPUS_SCRIPT.is_file():
            return {
                "status": "failed",
                "readout_path": str(paths["readout_path"]),
                "intermediate_path": str(paths["intermediate_path"]),
                "intermediate_format": tts_settings["intermediate_format"],
                "opus_path": str(paths["opus_path"]),
                "tts_log": str(tts_log_path),
                "convert_log": str(convert_log_path),
                "error_summary": f"Missing Feishu opus script: {FEISHU_OPUS_SCRIPT}",
            }

        paths["readout_path"].write_text(readout_text, encoding="utf-8")
        tts_result = run_and_capture(
            [
                "python3",
                str(MINIMAX_TTS_SCRIPT),
                "--input",
                str(paths["readout_path"]),
                "--output",
                str(paths["intermediate_path"]),
                "--voice-id",
                tts_settings["default_voice_id"],
                "--model",
                tts_settings["model"],
                "--format",
                tts_settings["intermediate_format"],
            ],
            tts_log_path,
            env=build_minimax_tts_env(),
        )
        tts_failure_summary = detect_minimax_tts_failure(tts_result)
        if tts_result.exit_code != 0 or tts_failure_summary:
            return {
                "status": "failed",
                "readout_path": str(paths["readout_path"]),
                "intermediate_path": str(paths["intermediate_path"]),
                "intermediate_format": tts_settings["intermediate_format"],
                "opus_path": str(paths["opus_path"]),
                "tts_log": tts_result.output_path,
                "convert_log": str(convert_log_path),
                "error_summary": tts_failure_summary or "MiniMax TTS generation failed",
            }

        convert_result = run_and_capture(
            [
                "python3",
                str(FEISHU_OPUS_SCRIPT),
                str(paths["intermediate_path"]),
                str(paths["opus_path"]),
            ],
            convert_log_path,
        )
        if convert_result.exit_code != 0:
            return {
                "status": "failed",
                "readout_path": str(paths["readout_path"]),
                "intermediate_path": str(paths["intermediate_path"]),
                "intermediate_format": tts_settings["intermediate_format"],
                "opus_path": str(paths["opus_path"]),
                "tts_log": tts_result.output_path,
                "convert_log": convert_result.output_path,
                "error_summary": "Feishu opus conversion failed",
            }

        return {
            "status": "succeeded",
            "readout_path": str(paths["readout_path"]),
            "intermediate_path": str(paths["intermediate_path"]),
            "intermediate_format": tts_settings["intermediate_format"],
            "opus_path": str(paths["opus_path"]),
            "tts_log": tts_result.output_path,
            "convert_log": convert_result.output_path,
        }
    except Exception as exc:
        return {
            "status": "failed",
            "readout_path": str(paths["readout_path"]),
            "intermediate_path": str(paths["intermediate_path"]),
            "intermediate_format": tts_settings["intermediate_format"],
            "opus_path": str(paths["opus_path"]),
            "tts_log": str(tts_log_path),
            "convert_log": str(convert_log_path),
            "error_summary": f"Audio bundle generation failed: {exc}",
        }


def detect_minimax_tts_failure(result: CommandResult) -> str | None:
    payloads = [
        extract_json_payload(text)
        for text in (result.stdout, result.stderr)
        if isinstance(text, str) and text.strip()
    ]
    status_markers: list[str] = []
    notes: list[str] = []
    for payload in payloads:
        if payload is None:
            continue
        status_value = find_nested_value(payload, {"status", "audio_generation_status"})
        if status_value:
            status_markers.append(status_value.lower())
        note = find_nested_value(payload, {"recovery_note", "error_summary", "status_msg", "message", "msg"})
        if note:
            notes.append(note.lower())

    combined = "\n".join(part for part in (result.stdout, result.stderr, "\n".join(notes)) if part).lower()
    used_local_fallback = any("fallback" in marker for marker in status_markers) or any(
        marker in combined
        for marker in ("local fallback", "succeeded-via-local-fallback", "macos say", "macos-say", "fell back to")
    )
    quota_exceeded = ("2056" in combined and "usage limit exceeded" in combined) or "quota exceeded" in combined

    if quota_exceeded and used_local_fallback:
        return "MiniMax quota exceeded (2056 usage limit exceeded); local fallback via macOS say is not treated as a successful audio build"
    if quota_exceeded:
        return "MiniMax quota exceeded (2056 usage limit exceeded)"
    if used_local_fallback:
        return "MiniMax TTS did not complete on MiniMax; local fallback via macOS say is not treated as a successful audio build"
    return None


def extract_json_payload(text: str) -> Any | None:
    candidate = text.strip()
    if not candidate:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\})", candidate, flags=re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None


def find_nested_value(payload: Any, candidate_keys: set[str]) -> str | None:
    if isinstance(payload, dict):
        for key in candidate_keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in payload.values():
            found = find_nested_value(value, candidate_keys)
            if found:
                return found
    if isinstance(payload, list):
        for item in payload:
            found = find_nested_value(item, candidate_keys)
            if found:
                return found
    return None


def write_json_log(log_path: Path, payload: Any) -> str:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(log_path)


def post_http_request(*, url: str, body: bytes, headers: dict[str, str]) -> tuple[int, str, Any | None]:
    request = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(request) as response:
            status_code = getattr(response, "status", 200)
            raw_body = response.read()
    except HTTPError as exc:
        status_code = exc.code
        raw_body = exc.read()
    return status_code, raw_body.decode("utf-8", errors="replace"), extract_json_payload(raw_body.decode("utf-8", errors="replace"))


def build_multipart_form_data(*, fields: dict[str, str], file_field: str, file_name: str, file_bytes: bytes) -> tuple[bytes, str]:
    boundary = f"----daily-report-{uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    chunks.extend(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"\r\n'.encode("utf-8"),
            b"Content-Type: application/octet-stream\r\n\r\n",
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def resolve_feishu_audio_delivery(config: dict[str, Any]) -> dict[str, str]:
    raw_delivery = ((config.get("audio") or {}).get("delivery") or {})
    settings = resolve_audio_settings(config)["delivery"]
    receive_id_env = settings["receive_id_env"]
    app_id_env = str(raw_delivery.get("app_id_env") or DEFAULT_FEISHU_APP_ID_ENV)
    app_secret_env = str(raw_delivery.get("app_secret_env") or DEFAULT_FEISHU_APP_SECRET_ENV)

    app_id = os.getenv(DEFAULT_FEISHU_APP_ID_ENV, "").strip()
    if not app_id and app_id_env != DEFAULT_FEISHU_APP_ID_ENV:
        app_id = os.getenv(app_id_env, "").strip()
    if not app_id:
        app_id = str(raw_delivery.get("app_id") or "").strip()

    app_secret = os.getenv(DEFAULT_FEISHU_APP_SECRET_ENV, "").strip()
    if not app_secret and app_secret_env != DEFAULT_FEISHU_APP_SECRET_ENV:
        app_secret = os.getenv(app_secret_env, "").strip()
    if not app_secret:
        app_secret = str(raw_delivery.get("app_secret") or "").strip()

    receive_id = os.getenv(DEFAULT_FEISHU_RECEIVE_ID_ENV, "").strip()
    if not receive_id and receive_id_env != DEFAULT_FEISHU_RECEIVE_ID_ENV:
        receive_id = os.getenv(receive_id_env, "").strip()
    if not receive_id:
        receive_id = str(raw_delivery.get("receive_id") or "").strip()

    return {
        "app_id": app_id,
        "app_secret": app_secret,
        "receive_id": receive_id,
        "receive_id_type": settings["receive_id_type"],
    }


def get_feishu_api_error(payload: Any | None, status_code: int) -> str | None:
    if isinstance(payload, dict):
        code = payload.get("code")
        if isinstance(code, int) and code != 0:
            message = find_nested_value(payload, {"msg", "message"}) or f"HTTP {status_code}"
            return f"code={code}, msg={message}"
    if status_code >= 400:
        if isinstance(payload, dict):
            message = find_nested_value(payload, {"msg", "message"}) or f"HTTP {status_code}"
            return f"HTTP {status_code}: {message}"
        return f"HTTP {status_code}"
    return None


def send_audio_to_feishu(*, opus_path: Path, run_dir: Path, doc_url: str | None, config: dict[str, Any]) -> dict[str, Any]:
    del doc_url
    delivery = resolve_feishu_audio_delivery(config)
    log_path = run_dir / "logs" / "feishu-audio.log"
    events: list[dict[str, Any]] = []

    if not opus_path.is_file():
        return {
            "status": "failed",
            "log": write_json_log(log_path, {"events": events, "error": f"Missing audio file: {opus_path}"}),
            "opus_path": str(opus_path),
            "error_summary": f"Missing audio file: {opus_path}",
        }
    if not delivery["app_id"] or not delivery["app_secret"]:
        return {
            "status": "failed",
            "log": write_json_log(
                log_path,
                {"events": events, "error": f"Missing {DEFAULT_FEISHU_APP_ID_ENV}/{DEFAULT_FEISHU_APP_SECRET_ENV} for Feishu audio delivery"},
            ),
            "opus_path": str(opus_path),
            "error_summary": f"Missing {DEFAULT_FEISHU_APP_ID_ENV}/{DEFAULT_FEISHU_APP_SECRET_ENV} for Feishu audio delivery",
        }
    if not delivery["receive_id"]:
        return {
            "status": "failed",
            "log": write_json_log(log_path, {"events": events, "error": f"Missing {DEFAULT_FEISHU_RECEIVE_ID_ENV} for Feishu audio delivery"}),
            "opus_path": str(opus_path),
            "error_summary": f"Missing {DEFAULT_FEISHU_RECEIVE_ID_ENV} for Feishu audio delivery",
        }

    try:
        auth_body = json.dumps(
            {"app_id": delivery["app_id"], "app_secret": delivery["app_secret"]},
            ensure_ascii=False,
        ).encode("utf-8")
        auth_status, auth_text, auth_payload = post_http_request(
            url=f"{FEISHU_OPEN_API_BASE}/auth/v3/tenant_access_token/internal",
            body=auth_body,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        events.append(
            {
                "step": "tenant_access_token",
                "request": {
                    "url": f"{FEISHU_OPEN_API_BASE}/auth/v3/tenant_access_token/internal",
                    "app_id": delivery["app_id"],
                    "app_secret_present": True,
                },
                "response": {
                    "status_code": auth_status,
                    "code": auth_payload.get("code") if isinstance(auth_payload, dict) else None,
                    "msg": find_nested_value(auth_payload, {"msg", "message"}) if auth_payload is not None else None,
                    "tenant_access_token_present": bool(
                        find_nested_value(auth_payload, {"tenant_access_token"}) if auth_payload is not None else None
                    ),
                },
            }
        )
        auth_error = get_feishu_api_error(auth_payload, auth_status)
        token = find_nested_value(auth_payload, {"tenant_access_token"}) if auth_payload is not None else None
        if auth_error or not token:
            return {
                "status": "failed",
                "log": write_json_log(log_path, {"events": events}),
                "opus_path": str(opus_path),
                "error_summary": f"Feishu tenant token request failed: {auth_error or 'missing tenant_access_token'}",
            }

        upload_body, upload_content_type = build_multipart_form_data(
            fields={"file_type": "opus", "file_name": opus_path.name},
            file_field="file",
            file_name=opus_path.name,
            file_bytes=opus_path.read_bytes(),
        )
        upload_status, upload_text, upload_payload = post_http_request(
            url=f"{FEISHU_OPEN_API_BASE}/im/v1/files",
            body=upload_body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": upload_content_type,
            },
        )
        events.append(
            {
                "step": "upload_audio_file",
                "request": {
                    "url": f"{FEISHU_OPEN_API_BASE}/im/v1/files",
                    "file_type": "opus",
                    "file_name": opus_path.name,
                    "authorization_present": True,
                },
                "response": {"status_code": upload_status, "body": upload_text},
            }
        )
        upload_error = get_feishu_api_error(upload_payload, upload_status)
        file_key = find_nested_value(upload_payload, {"file_key"}) if upload_payload is not None else None
        if upload_error or not file_key:
            return {
                "status": "failed",
                "log": write_json_log(log_path, {"events": events}),
                "opus_path": str(opus_path),
                "error_summary": f"Feishu audio upload failed: {upload_error or 'missing file_key'}",
            }

        message_body = json.dumps(
            {
                "receive_id": delivery["receive_id"],
                "msg_type": "audio",
                "content": json.dumps({"file_key": file_key}, ensure_ascii=False, separators=(",", ":")),
            },
            ensure_ascii=False,
        ).encode("utf-8")
        message_url = f"{FEISHU_OPEN_API_BASE}/im/v1/messages?receive_id_type={delivery['receive_id_type']}"
        message_status, message_text, message_payload = post_http_request(
            url=message_url,
            body=message_body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        events.append(
            {
                "step": "send_audio_message",
                "request": {
                    "url": message_url,
                    "receive_id": delivery["receive_id"],
                    "receive_id_type": delivery["receive_id_type"],
                    "msg_type": "audio",
                    "authorization_present": True,
                },
                "response": {"status_code": message_status, "body": message_text},
            }
        )
        message_error = get_feishu_api_error(message_payload, message_status)
        message_id = find_nested_value(message_payload, {"message_id", "new_message_id"}) if message_payload is not None else None
        if message_error:
            return {
                "status": "failed",
                "log": write_json_log(log_path, {"events": events}),
                "opus_path": str(opus_path),
                "error_summary": f"Feishu audio send failed: {message_error}",
            }

        return {
            "status": "succeeded",
            "log": write_json_log(log_path, {"events": events}),
            "opus_path": str(opus_path),
            "message_id": message_id,
        }
    except URLError as exc:
        return {
            "status": "failed",
            "log": write_json_log(log_path, {"events": events, "error": str(exc)}),
            "opus_path": str(opus_path),
            "error_summary": f"Feishu audio send failed: {exc}",
        }
    except Exception as exc:
        return {
            "status": "failed",
            "log": write_json_log(log_path, {"events": events, "error": str(exc)}),
            "opus_path": str(opus_path),
            "error_summary": f"Feishu audio send failed: {exc}",
        }


def publish_report_bundle(
    *,
    report_path: Path,
    report_markdown: str,
    report_date: str,
    title: str,
    run_dir: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    audio_result = generate_audio_bundle(
        report_markdown=report_markdown,
        report_date=report_date,
        run_dir=run_dir,
        config=config,
    )
    doc_result = import_to_feishu(report_path, title, run_dir)

    publish_result: dict[str, Any] = {
        "target": "feishu",
        "doc_status": doc_result["status"],
        "doc_log": doc_result.get("log"),
        "doc_url": doc_result.get("doc_url"),
        "audio_generation_status": audio_result["status"],
        "audio_status": "skipped",
        "audio_readout_path": audio_result.get("readout_path"),
        "audio_intermediate_path": audio_result.get("intermediate_path"),
        "audio_intermediate_format": audio_result.get("intermediate_format"),
        "audio_opus_path": audio_result.get("opus_path"),
        "audio_tts_log": audio_result.get("tts_log"),
        "audio_convert_log": audio_result.get("convert_log"),
    }

    if doc_result["status"] != "succeeded":
        publish_result["status"] = "failed"
        publish_result["error_summary"] = doc_result.get("error_summary") or "Feishu doc import failed"
        return publish_result

    if audio_result["status"] != "succeeded":
        publish_result["status"] = "degraded"
        publish_result["audio_status"] = "failed"
        publish_result["error_summary"] = audio_result.get("error_summary") or "Audio bundle generation failed"
        return publish_result

    sent_audio = send_audio_to_feishu(
        opus_path=Path(audio_result["opus_path"]),
        run_dir=run_dir,
        doc_url=doc_result.get("doc_url"),
        config=config,
    )
    publish_result["audio_status"] = sent_audio["status"]
    publish_result["audio_message_log"] = sent_audio.get("log")
    publish_result["audio_message_id"] = sent_audio.get("message_id")

    if sent_audio["status"] != "succeeded":
        publish_result["status"] = "degraded"
        publish_result["error_summary"] = sent_audio.get("error_summary") or "Feishu audio send failed"
        return publish_result

    publish_result["status"] = "succeeded"
    return publish_result


def main() -> int:
    args = parse_args()
    config = load_runtime_config(args.config)
    runtime = config["runtime"]
    paths = config["paths"]
    repo_root = Path(config.get("repo_root", Path(__file__).resolve().parent.parent)).resolve()
    lane_order = list(config["reader_facing"]["fixed_section_order"])
    signals_root = expand_path(paths["signals_root"])
    data_dir = signals_root.parent
    runtime_root = expand_path(paths["runtime_root"])
    if not is_path_writable(runtime_root):
        runtime_root = repo_root / ".runtime" / "daily-report-master"
    run_dir = runtime_root / args.report_date
    run_dir.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "report_date": args.report_date,
        "timezone": runtime["timezone"],
        "lanes": lane_order,
        "collect": [],
    }

    should_collect = not args.skip_collect
    if should_collect and not is_path_writable(data_dir):
        should_collect = False
        summary["collect_note"] = f"configured signals data dir not writable; reused existing snapshots from {signals_root}"
    if runtime_root != expand_path(paths["runtime_root"]):
        summary["runtime_note"] = f"configured runtime_root not writable; wrote artifacts to {runtime_root}"

    if should_collect:
        for lane in lane_order:
            summary["collect"].append(
                run_collect_with_retry(
                    lane=lane,
                    report_date=args.report_date,
                    data_dir=data_dir,
                    run_dir=run_dir,
                    verbose=args.verbose,
                )
            )

    collect_result = build_collect_result(signals_root=signals_root, report_date=args.report_date, lane_names=lane_order)
    previous_selected_items_path = resolve_previous_selected_items_path(runtime_root=runtime_root, report_date=args.report_date)
    selected_items = build_selected_items(
        signals_root=signals_root,
        report_date=args.report_date,
        lane_names=lane_order,
        lane_item_limits=resolve_lane_item_limits(config),
        previous_selected_items_path=previous_selected_items_path,
    )

    collect_result_path = run_dir / "collect-result.json"
    selected_items_path = run_dir / "selected-items.json"
    validation_bundle_path = run_dir / "validation-bundle.json"
    artifact_path = run_dir / "report-artifact.json"
    report_path = run_dir / "report.md"
    summary_path = run_dir / "run-summary.json"

    dump_json(collect_result, collect_result_path)
    dump_json(selected_items, selected_items_path)
    dump_json(build_validation_bundle(collect_result=collect_result, selected_items=selected_items), validation_bundle_path)

    if collect_result["summary"]["useful_item_count"] <= 0:
        summary["decision"] = "blocked"
        summary["reason"] = "no usable content after collect"
        dump_json(summary, summary_path)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 3

    artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
    dump_json(artifact, artifact_path)
    report_markdown = artifact["body_markdown"]
    report_path.write_text(report_markdown, encoding="utf-8")
    validate_report_markdown(report_markdown, report_date=args.report_date)

    summary["decision"] = "generated"
    summary["artifact_path"] = str(artifact_path)
    summary["report_path"] = str(report_path)
    summary["collect_result_path"] = str(collect_result_path)
    summary["selected_items_path"] = str(selected_items_path)
    summary["validation_bundle_path"] = str(validation_bundle_path)
    summary["selected_item_count"] = selected_items["summary"]["selected_item_count"]
    summary["x_lane_counts"] = {
        item["lane"]: item["selected_item_count"]
        for item in selected_items["summary"]["lane_counts"]
        if item["lane"] in {"x-feed", "x-following"}
    }

    if args.publish:
        title = f"AI 日报（{args.report_date}）{args.title_suffix}" if args.title_suffix else f"AI 日报（{args.report_date}）"
        summary["publish"] = publish_report_bundle(
            report_path=report_path,
            report_markdown=report_markdown,
            report_date=args.report_date,
            title=title,
            run_dir=run_dir,
            config=config,
        )
    else:
        summary["publish"] = {"status": "skipped"}

    dump_json(summary, summary_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
