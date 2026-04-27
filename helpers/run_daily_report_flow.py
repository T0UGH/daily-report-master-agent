from __future__ import annotations

import argparse
import json
import os
import re
import shutil
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

from helpers.lane_contracts import validate_lane_input_artifact, validate_lane_output_artifact
from helpers.lane_agent_contracts import validate_agent_lane_output
from helpers.lane_corpus_builder import build_agent_lane_input_artifact
from helpers.lane_report_assembler import build_report_artifact_from_lane_outputs
from helpers.lane_subagent_runner import run_lane_subagent
from helpers.lane_workers import build_lane_output
from helpers.runtime_config import (
    DEFAULT_RUNTIME_CONFIG_PATH,
    load_runtime_config,
    resolve_lane_item_limits,
    resolve_lane_worker_config,
)
from helpers.signals_adapter import (
    FIXED_SECTION_TITLES,
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
DEFAULT_ARCHIVE_REMOTE = "origin"
DEFAULT_ARCHIVE_BRANCH = "main"
DEFAULT_ARCHIVE_DAILY_REPORT_DIR = "raw/inbound/ai-daily-report"
CURATED_CARD_LINK_LABEL = "查看完整文档"
CURATED_CARD_DEFAULT_SECTION_ITEM_LIMIT = 2
CURATED_CARD_PRODUCT_HUNT_ITEM_LIMIT = 3
CURATED_CARD_MAX_JSON_BYTES = 25_000
CURATED_CARD_MAX_LARK_MD_TEXT_BYTES = 6_000
READOUT_INTRO = "以下是今天的 AI Agent 日报语音简报。"
READOUT_OUTRO = "以上就是今天的重点内容，感谢收听。"
READOUT_PLACEHOLDER_SNIPPETS = ("原文围绕", "具体变化见来源", "值得关注")
READOUT_DROP_LINK_LABELS = {"原帖", "release", "github", "product hunt", "polymarket"}
READOUT_SECTION_TRANSITIONS = {
    "Reddit 社区": "下面是 Reddit 社区。",
    "Claude Code": "接着是 Claude Code。",
    "Codex": "接着是 Codex。",
    "OpenClaw": "接着是 OpenClaw。",
    "GitHub AI 项目": "接着看 GitHub AI 项目。",
    "GitHub 趋势项目": "接着看 GitHub 趋势项目。",
    "Product Hunt 新品": "再来看 Product Hunt 新品。",
    "Polymarket 市场": "再来看 Polymarket 市场。",
}
READOUT_OFFICIAL_SOURCE_PREFIXES = {
    "anthropic": "Anthropic 官方提到",
    "anthropicai": "Anthropic 官方提到",
    "claudeai": "Anthropic 官方提到",
    "openai": "OpenAI 这边提到",
}
READOUT_ENGLISH_PHRASE_REWRITES = {
    "source maps": "源码映射",
    "TypeScript": "类型脚本",
    "model-agnostic": "模型无关",
    "heartbeat": "心跳检测",
    "shell": "命令行环境",
    "Ultraplan beta": "云端草案规划测试版",
    "design system": "设计系统",
    "coding harness builder": "AI 编码测试框架构建器",
    "self-hosted / proactive / local-first assistant": "可自托管、主动式、本地优先助手",
    "coding AI model": "编程模型",
    "markdown handoff": "markdown 交接文件",
}
OPS_NOTICE_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "ops-notice.md"
GITHUB_AI_PROJECTS_INPUT_LANES = {
    "github-trending-weekly",
    "x-feed",
    "x-following",
    "reddit-watch",
    "hacker-news-watch",
    "hacker-news-search-watch",
    "product-hunt-watch",
}
GITHUB_REPO_URL_RE = re.compile(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", flags=re.IGNORECASE)
GITHUB_REPO_BARE_RE = re.compile(r"(?<![A-Za-z0-9_.-])[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?![A-Za-z0-9_.-])")


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


def _github_repo_candidate_text(item: dict[str, Any], *, include_urls: bool) -> str:
    parts = [
        item.get("title"),
        item.get("summary"),
        item.get("source_snippet"),
        item.get("excerpt"),
    ]
    if include_urls:
        parts.extend([item.get("source_url"), item.get("url")])
    raw = item.get("raw")
    if isinstance(raw, str):
        parts.append(raw)
    elif isinstance(raw, dict):
        parts.extend([raw.get("title"), raw.get("summary"), raw.get("source_snippet")])
        if include_urls:
            parts.append(raw.get("url"))
    return "\n".join(str(part) for part in parts if part)


def _contains_github_repo_reference(item: dict[str, Any]) -> bool:
    url_text = _github_repo_candidate_text(item, include_urls=True)
    non_url_text = _github_repo_candidate_text(item, include_urls=False)
    return bool(GITHUB_REPO_URL_RE.search(url_text) or GITHUB_REPO_BARE_RE.search(non_url_text))


def build_lane_input_artifact(
    *,
    report_date: str,
    lane_name: str,
    selected_items: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = config or {}
    selection = config.get("selection") or {}
    target_count = resolve_lane_item_limits(config).get(
        lane_name,
        selection.get("default_per_lane_limit", 10),
    )
    if lane_name == "github-ai-projects":
        candidate_lanes = GITHUB_AI_PROJECTS_INPUT_LANES
    else:
        candidate_lanes = {lane_name}
    signals = []
    for item in selected_items.get("selected_items", []):
        if not isinstance(item, dict) or item.get("lane") not in candidate_lanes:
            continue
        if lane_name == "github-ai-projects" and not _contains_github_repo_reference(item):
            continue
        url = str(item.get("source_url") or item.get("url") or "").strip()
        if not url:
            continue
        signals.append(
            {
                "id": str(item.get("id") or item.get("title") or url),
                "title": str(item.get("title") or item.get("summary") or item.get("id") or "untitled"),
                "url": url,
                "source_lane": str(item.get("lane") or lane_name),
                "source_urls": [url],
                "raw": item,
            }
        )
    github_ai_config = (config.get("lane_workers") or {}).get("github_ai_projects") or {}
    github_search_queries = [
        str(query).format(report_date=report_date, date=report_date)
        for query in github_ai_config.get(
            "discovery_queries",
            [
                "GitHub trending AI {date}",
                "GitHub new AI projects {date}",
                "awesome AI GitHub {date}",
            ],
        )
        if str(query).strip()
    ]
    payload = {
        "artifact_type": "lane_input",
        "schema_version": 1,
        "report_date": report_date,
        "lane": lane_name,
        "timezone": config.get("runtime", {}).get("timezone", "Asia/Shanghai"),
        "lane_title": FIXED_SECTION_TITLES[lane_name],
        "target_item_count": target_count,
        "min_item_count": 1,
        "signals": signals,
        "recent_history": {"repo_ids": []},
        "cross_lane_context": {"github_search_queries": github_search_queries} if lane_name == "github-ai-projects" else {},
        "style_contract": {
            "language": "zh-CN",
            "forbidden_phrases": ["采集文本", "保守看", "摘要里能看到"],
        },
    }
    validate_lane_input_artifact(payload)
    return payload


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


def _walk_json_scalars(payload: Any) -> list[tuple[str | None, Any]]:
    if isinstance(payload, dict):
        values: list[tuple[str | None, Any]] = []
        for key, value in payload.items():
            values.append((str(key), value))
            values.extend(_walk_json_scalars(value))
        return values
    if isinstance(payload, list):
        values: list[tuple[str | None, Any]] = []
        for item in payload:
            values.extend(_walk_json_scalars(item))
        return values
    return [(None, payload)]


def _find_json_value(
    payload: Any,
    *,
    exact_keys: set[str] | None = None,
    key_fragments: tuple[str, ...] = (),
    value_pattern: re.Pattern[str] | None = None,
) -> str | None:
    normalized_exact_keys = {key.lower() for key in exact_keys or set()}
    for key, value in _walk_json_scalars(payload):
        if value is None:
            continue
        text = str(value)
        if value_pattern and value_pattern.search(text):
            return text
        if key is None:
            continue
        lowered = key.lower()
        if normalized_exact_keys and lowered in normalized_exact_keys:
            return text
        if key_fragments and any(fragment in lowered for fragment in key_fragments):
            return text
    return None


def _extract_doc_url(text: str) -> str | None:
    match = re.search(r"(https://\S+)", text)
    return match.group(1) if match else None


def summarize_ops_reason(summary: dict[str, Any]) -> str:
    reason = str(summary.get("reason") or "").strip()
    validation_error = str(summary.get("validation_error") or "").strip()
    publish = summary.get("publish") or {}
    archive = summary.get("archive") or {}

    if reason == "report_output_contract_failed":
        if validation_error:
            return f"reader-facing 成稿未通过输出合同校验：{validation_error}"
        return "reader-facing 成稿未通过输出合同校验"
    if reason == "no usable content after collect":
        return "收集结束后没有可用内容，日报未成立"
    if publish.get("status") == "failed":
        return str(publish.get("error_summary") or "发布失败")
    if publish.get("status") == "degraded":
        return str(publish.get("error_summary") or "发布降级")
    if archive.get("status") == "failed":
        return str(archive.get("error_summary") or "knowledge-wiki 归档失败")
    if archive.get("status") == "degraded":
        return str(archive.get("error_summary") or "knowledge-wiki 归档降级")
    if reason:
        return reason
    return "运行结果异常，请检查 run-summary.json 和相关日志"


def build_ops_notice_markdown(summary: dict[str, Any]) -> str:
    try:
        template = OPS_NOTICE_TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError:
        template = (
            "# 日报状态通知\n\n"
            "- 日期：{{report_date}}\n"
            "- 状态：{{verdict_status}}\n"
            "- 原因：{{reason_summary}}\n"
            "- 发布引用：{{publish_reference}}\n"
            "- 归档信息：{{archive_summary}}\n"
        )

    publish = summary.get("publish") or {}
    verdict_status = str(summary.get("decision") or publish.get("status") or "unknown")
    if verdict_status == "generated" and publish.get("status") in {"degraded", "failed"}:
        verdict_status = str(publish.get("status"))
    publish_reference = str(publish.get("doc_url") or publish.get("reference") or "无")
    archive_summary = str((summary.get("archive") or {}).get("summary") or "未归档")
    reason_summary = summarize_ops_reason(summary)
    replacements = {
        "{{report_date}}": str(summary.get("report_date") or ""),
        "{{verdict_status}}": verdict_status,
        "{{reason_summary}}": reason_summary,
        "{{publish_reference}}": publish_reference,
        "{{archive_summary}}": archive_summary,
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def write_ops_notice(summary: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    notice_path = run_dir / "ops-notice.md"
    notice_markdown = build_ops_notice_markdown(summary)
    notice_path.write_text(notice_markdown, encoding="utf-8")
    return {
        "status": "generated",
        "path": str(notice_path),
        "reason_summary": summarize_ops_reason(summary),
    }


def resolve_archive_settings(config: dict[str, Any]) -> dict[str, str]:
    raw_archive = ((config.get("archive") or {}).get("knowledge_wiki") or {})
    daily_report_dir = str(raw_archive.get("daily_report_dir") or DEFAULT_ARCHIVE_DAILY_REPORT_DIR).strip().strip("/")
    if not daily_report_dir:
        daily_report_dir = DEFAULT_ARCHIVE_DAILY_REPORT_DIR
    return {
        "repo_root": str(raw_archive.get("repo_root") or "").strip(),
        "remote": str(raw_archive.get("remote") or DEFAULT_ARCHIVE_REMOTE).strip() or DEFAULT_ARCHIVE_REMOTE,
        "branch": str(raw_archive.get("branch") or DEFAULT_ARCHIVE_BRANCH).strip() or DEFAULT_ARCHIVE_BRANCH,
        "daily_report_dir": daily_report_dir,
    }


def build_archive_note_path(*, report_date: str, daily_report_dir: str) -> Path:
    year_segment = report_date[:4] if len(report_date) >= 4 else report_date
    return Path(daily_report_dir) / year_segment / f"{report_date}.md"


def is_noop_git_commit(result: subprocess.CompletedProcess[str]) -> bool:
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part).lower()
    return "nothing to commit" in combined or "working tree clean" in combined


def archive_report_to_knowledge_wiki(
    *,
    report_path: Path,
    report_date: str,
    run_dir: Path,
    config: dict[str, Any],
) -> dict[str, Any]:
    settings = resolve_archive_settings(config)
    note_path = build_archive_note_path(
        report_date=report_date,
        daily_report_dir=settings["daily_report_dir"],
    )
    log_path = run_dir / "logs" / "knowledge-wiki-archive.json"
    events: list[dict[str, Any]] = []
    repo_root_text = settings["repo_root"]
    repo_root = expand_path(repo_root_text) if repo_root_text else None
    destination_path = repo_root / note_path if repo_root else None

    base_result: dict[str, Any] = {
        "repo": str(repo_root) if repo_root else repo_root_text,
        "remote": settings["remote"],
        "branch": settings["branch"],
        "note_path": note_path.as_posix(),
        "log": str(log_path),
    }
    if destination_path is not None:
        base_result["path"] = str(destination_path)

    def finish(
        *,
        status: str,
        summary_text: str,
        error_summary: str | None = None,
        commit: str | None = None,
    ) -> dict[str, Any]:
        result = {**base_result, "status": status, "summary": summary_text}
        if error_summary:
            result["error_summary"] = error_summary
        if commit:
            result["commit"] = commit
        write_json_log(log_path, {"events": events, "result": result})
        return result

    def run_git(command: list[str]) -> subprocess.CompletedProcess[str]:
        if repo_root is None:
            raise RuntimeError("archive repo_root is not configured")
        completed = subprocess.run(
            command,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        events.append(
            {
                "command": command,
                "cwd": str(repo_root),
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
        return completed

    def command_failed(step: str, completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
        return finish(
            status="failed",
            summary_text=f"归档失败：knowledge-wiki {step} failed",
            error_summary=f"knowledge-wiki {step} failed",
        )

    report_path = report_path.resolve()
    if repo_root is None:
        return finish(
            status="failed",
            summary_text="归档失败：knowledge-wiki repo_root 未配置",
            error_summary="knowledge-wiki repo_root 未配置",
        )
    if not report_path.is_file():
        return finish(
            status="failed",
            summary_text=f"归档失败：Missing report file: {report_path}",
            error_summary=f"Missing report file: {report_path}",
        )
    if not repo_root.is_dir():
        return finish(
            status="failed",
            summary_text=f"归档失败：Missing knowledge-wiki repo: {repo_root}",
            error_summary=f"Missing knowledge-wiki repo: {repo_root}",
        )

    try:
        branch_result = run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        if branch_result.returncode != 0:
            return command_failed("git rev-parse --abbrev-ref HEAD", branch_result)
        current_branch = branch_result.stdout.strip()
        if current_branch != settings["branch"]:
            return finish(
                status="failed",
                summary_text=f"归档失败：knowledge-wiki branch is {current_branch or 'unknown'}, expected {settings['branch']}",
                error_summary=f"knowledge-wiki branch is {current_branch or 'unknown'}, expected {settings['branch']}",
            )

        pull_result = run_git(["git", "pull", "--ff-only", settings["remote"], settings["branch"]])
        if pull_result.returncode != 0:
            return command_failed("git pull", pull_result)

        assert destination_path is not None
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(report_path, destination_path)

        add_result = run_git(["git", "add", note_path.as_posix()])
        if add_result.returncode != 0:
            return command_failed("git add", add_result)

        commit_message = f"archive(ai-daily-report): {report_date}"
        commit_result = run_git(["git", "commit", "-m", commit_message])
        if commit_result.returncode != 0 and not is_noop_git_commit(commit_result):
            return command_failed("git commit", commit_result)

        head_result = run_git(["git", "rev-parse", "HEAD"])
        if head_result.returncode != 0:
            return command_failed("git rev-parse HEAD", head_result)
        commit_sha = head_result.stdout.strip()

        push_result = run_git(["git", "push", settings["remote"], settings["branch"]])
        if push_result.returncode != 0:
            return finish(
                status="failed",
                summary_text="归档失败：knowledge-wiki git push failed",
                error_summary="knowledge-wiki git push failed",
                commit=commit_sha,
            )

        return finish(
            status="succeeded",
            summary_text=f"已归档到 {note_path.as_posix()} @ {commit_sha}",
            commit=commit_sha,
        )
    except Exception as exc:
        events.append({"step": "exception", "error": str(exc)})
        return finish(
            status="failed",
            summary_text=f"归档失败：knowledge-wiki archive failed: {exc}",
            error_summary=f"knowledge-wiki archive failed: {exc}",
        )


def import_to_feishu(report_path: Path, title: str, run_dir: Path) -> dict[str, Any]:
    report_path = report_path.resolve()

    cmd = [
        "lark-cli",
        "docs",
        "+create",
        "--as",
        "user",
        "--title",
        title,
        "--markdown",
        f"@./{report_path.name}",
    ]
    result = run_and_capture(cmd, run_dir / "logs" / "feishu-import.log", cwd=report_path.parent)
    if result.exit_code != 0:
        return {
            "status": "failed",
            "log": result.output_path,
            "error_summary": "Feishu doc import failed",
        }

    doc_url: str | None = None
    doc_token: str | None = None
    doc_id: str | None = None
    stdout = result.stdout.strip()
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            doc_url = _extract_doc_url(f"{result.stdout}\n{result.stderr}")
        else:
            doc_url = _find_json_value(
                payload,
                exact_keys={"url", "doc_url", "document_url", "link"},
                value_pattern=re.compile(r"^https://"),
            )
            doc_token = _find_json_value(
                payload,
                exact_keys={"token", "doc_token", "document_token", "obj_token"},
                key_fragments=("token",),
            )
            doc_id = _find_json_value(
                payload,
                exact_keys={"id", "doc_id", "document_id", "obj_id"},
                key_fragments=("doc_id", "document_id", "_id"),
            )
            if doc_url is None:
                doc_url = _extract_doc_url(stdout)
    if doc_url is None:
        doc_url = _extract_doc_url(f"{result.stdout}\n{result.stderr}")

    response: dict[str, Any] = {
        "status": "succeeded",
        "log": result.output_path,
    }
    if doc_url is not None:
        response["doc_url"] = doc_url
    if doc_token is not None:
        response["doc_token"] = doc_token
    if doc_id is not None:
        response["doc_id"] = doc_id
    return response


def parse_report_markdown_sections(report_markdown: str) -> tuple[str | None, list[tuple[str, list[str]]]]:
    text = report_markdown.replace("\r\n", "\n").strip()
    text = _truncate_sources_tail(text)
    text = re.sub(r"```.*?```", "\n", text, flags=re.S)

    report_title: str | None = None
    sections: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_items: list[str] = []
    current_item_lines: list[str] | None = None

    def flush_item() -> None:
        nonlocal current_item_lines
        if current_item_lines is None:
            return
        item_text = " ".join(line.strip() for line in current_item_lines if line.strip()).strip()
        current_item_lines = None
        if item_text and current_heading is not None:
            current_items.append(item_text)

    def flush_section() -> None:
        nonlocal current_heading, current_items
        if current_heading is None:
            return
        if current_items:
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
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if heading_level == 1:
                report_title = heading_text
                continue
            flush_section()
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

        if current_heading is not None:
            current_items.append(line)

    flush_item()
    flush_section()
    return report_title, sections


def _is_weather_section(heading: str) -> bool:
    return "天气" in heading


def _card_section_item_limit(heading: str) -> int:
    if "product hunt" in heading.lower():
        return CURATED_CARD_PRODUCT_HUNT_ITEM_LIMIT
    return CURATED_CARD_DEFAULT_SECTION_ITEM_LIMIT


def _order_card_sections(sections: list[tuple[str, list[str]]]) -> list[tuple[str, list[str]]]:
    indexed_sections = list(enumerate(sections))
    indexed_sections.sort(key=lambda item: (0 if _is_weather_section(item[1][0]) else 1, item[0]))
    return [section for _, section in indexed_sections]


def _build_card_section_elements(*, heading: str, items: list[str]) -> list[dict[str, Any]]:
    limited_items = items[: _card_section_item_limit(heading)]
    content_lines = [f"- {item}" for item in limited_items]
    return [
        {
            "tag": "div",
            "text": {
                "tag": "plain_text",
                "content": heading,
                "text_size": "section_title",
            },
        },
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "\n".join(content_lines),
                "text_size": "normal",
            },
        },
    ]


def build_curated_card_payload(*, report_markdown: str, doc_url: str) -> dict[str, Any]:
    report_title, sections = parse_report_markdown_sections(report_markdown)
    ordered_sections = _order_card_sections(
        [(heading, items) for heading, items in sections if heading != "来源"]
    )
    elements: list[dict[str, Any]] = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"我不是贵平，我是 Rook。 [{CURATED_CARD_LINK_LABEL}]({doc_url})",
                "text_size": "normal",
            },
        }
    ]

    rendered_sections = [section for section in ordered_sections if section[1]]
    if rendered_sections:
        elements.append({"tag": "hr"})
    for index, (heading, items) in enumerate(rendered_sections):
        elements.extend(_build_card_section_elements(heading=heading, items=items))
        if index != len(rendered_sections) - 1:
            elements.append({"tag": "hr"})

    return {
        "config": {
            "wide_screen_mode": True,
            "style": {
                "text_size": {
                    "section_title": {
                        "default": "heading-2",
                        "pc": "heading-2",
                        "mobile": "heading-2",
                    }
                }
            },
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": report_title or "AI Agent 日报精选",
            },
            "subtitle": {
                "tag": "lark_md",
                "content": f"[{CURATED_CARD_LINK_LABEL}]({doc_url})",
            },
        },
        "elements": elements,
    }


def _json_byte_size(payload: Any) -> int:
    return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def _safe_json_byte_size(payload: Any) -> int | None:
    try:
        return _json_byte_size(payload)
    except (TypeError, ValueError):
        return None


def _extract_curated_card_doc_url(payload: dict[str, Any]) -> str | None:
    markdown_link_pattern = re.compile(rf"\[{re.escape(CURATED_CARD_LINK_LABEL)}\]\(([^)]+)\)")
    raw_url_pattern = re.compile(r"https?://[^\s)]+")
    for _, value in _walk_json_scalars(payload):
        if not isinstance(value, str):
            continue
        markdown_match = markdown_link_pattern.search(value)
        if markdown_match:
            return markdown_match.group(1).strip()
        raw_match = raw_url_pattern.search(value)
        if raw_match:
            return raw_match.group(0).strip()
    return None


def validate_curated_card_payload(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    try:
        card_json_bytes = _json_byte_size(payload)
    except (TypeError, ValueError) as exc:
        issues.append(f"Card payload is not JSON serializable: {exc}")
        card_json_bytes = 0

    if card_json_bytes > CURATED_CARD_MAX_JSON_BYTES:
        issues.append(
            "Card payload JSON is "
            f"{card_json_bytes} bytes, exceeds {CURATED_CARD_MAX_JSON_BYTES} bytes"
        )

    if not isinstance(payload, dict):
        issues.append("Card payload must be a JSON object")
        return issues

    header = payload.get("header")
    if not isinstance(header, dict):
        issues.append("Card payload missing required header object")
    else:
        title = header.get("title")
        if not isinstance(title, dict):
            issues.append("Card payload missing required header.title object")
        elif not isinstance(title.get("content"), str) or not title.get("content", "").strip():
            issues.append("Card payload missing required header.title.content text")

    elements = payload.get("elements")
    if not isinstance(elements, list) or not elements:
        issues.append("Card payload missing required non-empty elements list")
        return issues

    for index, element in enumerate(elements):
        element_path = f"elements[{index}]"
        if not isinstance(element, dict):
            issues.append(f"{element_path} must be an object")
            continue
        if element.get("tag") != "div":
            continue
        text = element.get("text")
        if not isinstance(text, dict):
            issues.append(f"{element_path} div missing required text object")
            continue
        content = text.get("content")
        if not isinstance(content, str):
            issues.append(f"{element_path} div text content must be a string")
            continue
        if text.get("tag") == "lark_md":
            text_bytes = len(content.encode("utf-8"))
            if text_bytes > CURATED_CARD_MAX_LARK_MD_TEXT_BYTES:
                issues.append(
                    f"{element_path} lark_md content is {text_bytes} bytes, "
                    f"exceeds {CURATED_CARD_MAX_LARK_MD_TEXT_BYTES} bytes"
                )

    return issues


def _has_valid_card_header(header: Any) -> bool:
    if not isinstance(header, dict):
        return False
    title = header.get("title")
    return isinstance(title, dict) and isinstance(title.get("content"), str) and bool(title["content"].strip())


def compact_curated_card_payload(payload: dict[str, Any], doc_url: str) -> dict[str, Any]:
    header = payload.get("header") if isinstance(payload, dict) else None
    if not _has_valid_card_header(header):
        header = {
            "title": {
                "tag": "plain_text",
                "content": "AI Agent 日报精选",
            }
        }

    doc_link = f"[{CURATED_CARD_LINK_LABEL}]({doc_url})" if doc_url else CURATED_CARD_LINK_LABEL
    return {
        "config": {"wide_screen_mode": True},
        "header": header,
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"精选卡片内容较长，已简化展示。如需完整内容，请查看完整文档：{doc_link}",
                    "text_size": "normal",
                },
            }
        ],
    }


def send_curated_card_to_feishu(*, card_payload: dict[str, Any], run_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    delivery = resolve_feishu_audio_delivery(config)
    log_path = run_dir / "logs" / "feishu-card.log"
    preflight_log: str | None = None
    preflight_issues: list[str] = []
    degraded = False
    if delivery["receive_id_type"] != "chat_id":
        return {
            "status": "failed",
            "log": write_json_log(
                log_path,
                {"error": f"Unsupported receive_id_type for curated card delivery: {delivery['receive_id_type']}"},
            ),
            "error_summary": f"Unsupported receive_id_type for curated card delivery: {delivery['receive_id_type']}",
        }
    if not delivery["receive_id"]:
        return {
            "status": "failed",
            "log": write_json_log(log_path, {"error": f"Missing {DEFAULT_FEISHU_RECEIVE_ID_ENV} for curated card delivery"}),
            "error_summary": f"Missing {DEFAULT_FEISHU_RECEIVE_ID_ENV} for curated card delivery",
        }

    validation_issues = validate_curated_card_payload(card_payload)
    if validation_issues:
        degraded = True
        preflight_issues = validation_issues
        doc_url = _extract_curated_card_doc_url(card_payload) or ""
        compact_payload = compact_curated_card_payload(card_payload, doc_url)
        compact_issues = validate_curated_card_payload(compact_payload)
        preflight_log = write_json_log(
            run_dir / "logs" / "feishu-card-preflight.json",
            {
                "degraded": True,
                "issues": validation_issues,
                "compact_issues": compact_issues,
                "doc_url": doc_url,
                "original_json_bytes": _safe_json_byte_size(card_payload),
                "compact_json_bytes": _safe_json_byte_size(compact_payload),
                "max_card_json_bytes": CURATED_CARD_MAX_JSON_BYTES,
                "max_lark_md_text_bytes": CURATED_CARD_MAX_LARK_MD_TEXT_BYTES,
            },
        )
        if compact_issues:
            return {
                "status": "failed",
                "log": preflight_log,
                "error_summary": "Feishu curated card preflight validation failed: " + " | ".join(compact_issues),
                "degraded": True,
                "preflight_log": preflight_log,
                "preflight_issues": validation_issues,
                "compact_preflight_issues": compact_issues,
            }
        card_payload = compact_payload

    command = [
        "lark-cli",
        "im",
        "+messages-send",
        "--as",
        "user",
        "--chat-id",
        delivery["receive_id"],
        "--msg-type",
        "interactive",
        "--content",
        json.dumps(card_payload, ensure_ascii=False),
    ]
    result = run_and_capture(command, log_path)
    if result.exit_code != 0:
        failed_result: dict[str, Any] = {
            "status": "failed",
            "log": result.output_path,
            "error_summary": "Feishu curated card send failed",
        }
        if degraded:
            failed_result["degraded"] = True
            failed_result["preflight_log"] = preflight_log
            failed_result["preflight_issues"] = preflight_issues
        return failed_result

    message_id: str | None = None
    stdout = result.stdout.strip()
    if stdout:
        payload = extract_json_payload(stdout)
        if payload is not None:
            message_id = _find_json_value(
                payload,
                exact_keys={"message_id", "new_message_id"},
                key_fragments=("message_id",),
            )

    send_result: dict[str, Any] = {
        "status": "succeeded",
        "log": result.output_path,
        "message_id": message_id,
    }
    if degraded:
        send_result["degraded"] = True
        send_result["preflight_log"] = preflight_log
        send_result["preflight_issues"] = preflight_issues
    return send_result


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


def _rewrite_social_source_identity(text: str) -> str:
    handle_match = re.match(r"^@([A-Za-z0-9_]+)(?:\s+#\d+)?(?:\s+|$)", text)
    if handle_match is None:
        return text

    handle = handle_match.group(1).lower()
    body = text[handle_match.end() :].strip()
    if not body:
        return ""

    official_prefix = READOUT_OFFICIAL_SOURCE_PREFIXES.get(handle)
    if official_prefix:
        return f"{official_prefix}，{body}"

    if re.match(r"^(有人|有用户|一条帖子|这条帖子)", body):
        return body
    return f"有用户提到，{body}"


def _strip_leading_english_title(text: str) -> str:
    first_cjk_match = re.search(r"[\u4e00-\u9fff]", text)
    if first_cjk_match is None:
        return text
    prefix = text[: first_cjk_match.start()].strip()
    if len(prefix) < 24:
        return text
    if re.search(r"[A-Za-z]", prefix) is None:
        return text
    if re.search(r"[。！？]", prefix):
        return text
    return text[first_cjk_match.start() :].lstrip(" ：:,-—–")


def _rewrite_readout_english_phrases(text: str) -> str:
    rewritten = text
    for raw, replacement in READOUT_ENGLISH_PHRASE_REWRITES.items():
        rewritten = rewritten.replace(raw, replacement)
    return rewritten


def _to_spoken_sentence(text: str) -> str:
    cleaned = _clean_readout_fragment(text)
    if not cleaned:
        return ""
    cleaned = _strip_leading_english_title(cleaned)
    cleaned = _rewrite_readout_english_phrases(cleaned)
    cleaned = _rewrite_social_source_identity(cleaned)
    cleaned = re.sub(r"^@[A-Za-z0-9_]+(?:\s+#\d+)?\s*", "", cleaned)
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
    doc_result = import_to_feishu(report_path, title, run_dir)

    publish_result: dict[str, Any] = {
        "target": "feishu",
        "doc_status": doc_result["status"],
        "doc_log": doc_result.get("log"),
        "doc_url": doc_result.get("doc_url"),
        "card_status": "skipped",
        "card_payload": None,
        "card_message_log": None,
        "card_message_id": None,
        "audio_generation_status": "skipped",
        "audio_status": "skipped",
        "audio_readout_path": None,
        "audio_intermediate_path": None,
        "audio_intermediate_format": None,
        "audio_opus_path": None,
        "audio_tts_log": None,
        "audio_convert_log": None,
    }

    if doc_result["status"] != "succeeded":
        publish_result["status"] = "failed"
        publish_result["error_summary"] = doc_result.get("error_summary") or "Feishu doc import failed"
        return publish_result

    card_result: dict[str, Any]
    if doc_result.get("doc_url"):
        card_payload = build_curated_card_payload(
            report_markdown=report_markdown,
            doc_url=str(doc_result["doc_url"]),
        )
        publish_result["card_payload"] = card_payload
        card_result = send_curated_card_to_feishu(
            card_payload=card_payload,
            run_dir=run_dir,
            config=config,
        )
    else:
        card_result = {
            "status": "failed",
            "error_summary": "Missing Feishu doc URL for curated card delivery",
        }
    publish_result["card_status"] = card_result["status"]
    publish_result["card_message_log"] = card_result.get("log")
    publish_result["card_message_id"] = card_result.get("message_id")
    if card_result.get("degraded"):
        publish_result["card_degraded"] = True
    if card_result.get("preflight_log"):
        publish_result["card_preflight_log"] = card_result.get("preflight_log")
    if card_result.get("preflight_issues"):
        publish_result["card_preflight_issues"] = card_result.get("preflight_issues")

    audio_result = generate_audio_bundle(
        report_markdown=report_markdown,
        report_date=report_date,
        run_dir=run_dir,
        config=config,
    )
    publish_result["audio_generation_status"] = audio_result["status"]
    publish_result["audio_readout_path"] = audio_result.get("readout_path")
    publish_result["audio_intermediate_path"] = audio_result.get("intermediate_path")
    publish_result["audio_intermediate_format"] = audio_result.get("intermediate_format")
    publish_result["audio_opus_path"] = audio_result.get("opus_path")
    publish_result["audio_tts_log"] = audio_result.get("tts_log")
    publish_result["audio_convert_log"] = audio_result.get("convert_log")

    failures: list[str] = []
    if card_result["status"] != "succeeded":
        failures.append(card_result.get("error_summary") or "Feishu curated card send failed")

    if audio_result["status"] != "succeeded":
        publish_result["audio_status"] = "failed"
        failures.append(audio_result.get("error_summary") or "Audio bundle generation failed")
    else:
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
            failures.append(sent_audio.get("error_summary") or "Feishu audio send failed")

    if failures:
        publish_result["status"] = "degraded"
        publish_result["error_summary"] = " | ".join(failures)
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
        "archive": {
            "status": "skipped",
            "reason": "publish_not_attempted",
            "summary": "未归档：未进入发布阶段",
        },
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

    lane_worker_config = resolve_lane_worker_config(config)
    summary["lane_workers"] = {
        "enabled": lane_worker_config["enabled"],
        "mode": lane_worker_config["mode"],
        "agent_first": lane_worker_config["agent_first"],
        "forbid_legacy_fallback_for": lane_worker_config["forbid_legacy_fallback_for"],
        "outputs": {},
    }
    lane_outputs: list[dict[str, Any]] = []
    if lane_worker_config["enabled"]:
        enabled_lane_set = set(lane_worker_config["enabled_lanes"])
        lane_order_set = set(lane_order)
        if enabled_lane_set != lane_order_set:
            missing = [lane for lane in lane_order if lane not in enabled_lane_set]
            extra = [lane for lane in lane_worker_config["enabled_lanes"] if lane not in lane_order_set]
            details = []
            if missing:
                details.append(f"missing: {missing}")
            if extra:
                details.append(f"extra: {extra}")
            suffix = "; ".join(details) if details else "enabled_lanes does not match fixed_section_order"
            raise ValueError(f"lane worker mode requires all fixed_section_order lanes; {suffix}")

    if collect_result["summary"]["useful_item_count"] <= 0:
        summary["decision"] = "blocked"
        summary["reason"] = "no usable content after collect"
        summary["ops_notice"] = write_ops_notice(summary, run_dir)
        dump_json(summary, summary_path)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 3

    if lane_worker_config["enabled"]:
        lane_inputs_dir = run_dir / "lane-inputs"
        lane_outputs_dir = run_dir / "lane-outputs"
        lane_logs_dir = run_dir / "lane-logs"
        lane_inputs_dir.mkdir(parents=True, exist_ok=True)
        lane_outputs_dir.mkdir(parents=True, exist_ok=True)
        lane_logs_dir.mkdir(parents=True, exist_ok=True)
        for lane_name in lane_order:
            if lane_worker_config["agent_first"]:
                lane_input = build_agent_lane_input_artifact(
                    report_date=args.report_date,
                    lane_name=lane_name,
                    collect_result=collect_result,
                    selected_items=selected_items,
                    config=config,
                )
            else:
                lane_input = build_lane_input_artifact(
                    report_date=args.report_date,
                    lane_name=lane_name,
                    selected_items=selected_items,
                    config=config,
                )
            input_path = lane_inputs_dir / f"{lane_name}.json"
            output_path = lane_outputs_dir / f"{lane_name}.json"
            log_path = lane_logs_dir / f"{lane_name}.md"
            dump_json(lane_input, input_path)
            if lane_worker_config["agent_first"]:
                lane_output = run_lane_subagent(input_path, output_path, log_path)
                validate_agent_lane_output(lane_output)
                validate_lane_output_artifact(lane_output)
            elif lane_worker_config["mode"] == "local":
                lane_output = build_lane_output(
                    report_date=args.report_date,
                    lane_name=lane_name,
                    selected_items=selected_items,
                    lane_input=lane_input,
                )
                validate_lane_output_artifact(lane_output)
                dump_json(lane_output, output_path)
                log_path.write_text(
                    f"# {lane_name}\n\nmode: local\n\nstatus: {lane_output['status']}\n",
                    encoding="utf-8",
                )
            elif lane_worker_config["mode"] == "subagent":
                lane_output = run_lane_subagent(input_path, output_path, log_path)
                validate_lane_output_artifact(lane_output)
            else:
                raise ValueError("lane_workers.mode must be local or subagent")
            lane_outputs.append(lane_output)
            summary["lane_workers"]["outputs"][lane_name] = {
                "status": lane_output["status"],
                "item_count": lane_output.get("quality", {}).get("item_count"),
                "output_path": str(output_path),
                "log_path": str(log_path),
            }
            agent_runtime = lane_output.get("agent_runtime")
            if isinstance(agent_runtime, dict):
                summary["lane_workers"]["outputs"][lane_name]["agent_runtime"] = agent_runtime
            side_artifacts = lane_output.get("side_artifacts") or {}
            memory_markdown = side_artifacts.get("memory_markdown")
            if isinstance(memory_markdown, str) and memory_markdown.strip():
                lane_memory_dir = run_dir / "lane-memory"
                lane_memory_dir.mkdir(parents=True, exist_ok=True)
                memory_path = lane_memory_dir / f"{lane_name}.md"
                memory_path.write_text(memory_markdown, encoding="utf-8")
                summary["lane_workers"]["outputs"][lane_name]["memory_path"] = str(memory_path)
        artifact = build_report_artifact_from_lane_outputs(
            report_date=args.report_date,
            lane_outputs=lane_outputs,
            lane_order=lane_order,
        )
    else:
        artifact = build_report_artifact(collect_result=collect_result, selected_items=selected_items)
    dump_json(artifact, artifact_path)
    report_markdown = artifact["body_markdown"]
    report_path.write_text(report_markdown, encoding="utf-8")

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

    try:
        validate_report_markdown(report_markdown, report_date=args.report_date)
    except ValueError as exc:
        summary["decision"] = "blocked"
        summary["reason"] = "report_output_contract_failed"
        summary["validation"] = {
            "status": "failed",
            "error": str(exc),
        }
        summary["validation_error"] = str(exc)
        summary["publish"] = {
            "status": "skipped",
            "reason": "report_output_contract_failed",
        }
        summary["ops_notice"] = write_ops_notice(summary, run_dir)
        dump_json(summary, summary_path)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 4

    summary["validation"] = {"status": "passed"}
    summary["decision"] = "generated"

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
    publish_status = summary["publish"].get("status")
    doc_status = summary["publish"].get("doc_status")
    should_archive = publish_status in {"succeeded", "degraded"} and doc_status == "succeeded"
    if should_archive:
        summary["archive"] = archive_report_to_knowledge_wiki(
            report_path=report_path,
            report_date=args.report_date,
            run_dir=run_dir,
            config=config,
        )
        if summary["archive"].get("status") != "succeeded":
            summary["decision"] = "degraded"
            summary["reason"] = "knowledge_wiki_archive_failed"
    elif publish_status == "skipped":
        summary["archive"] = {
            "status": "skipped",
            "reason": "publish_skipped",
            "summary": "未归档：发布已跳过",
        }
    elif doc_status != "succeeded":
        summary["archive"] = {
            "status": "skipped",
            "reason": "doc_publish_not_succeeded",
            "summary": "未归档：文档发布未成功",
        }
    else:
        summary["archive"] = {
            "status": "skipped",
            "reason": "publish_not_succeeded",
            "summary": "未归档：发布未成功",
        }

    if summary["publish"].get("status") in {"degraded", "failed"} or summary["archive"].get("status") in {"degraded", "failed"}:
        summary["ops_notice"] = write_ops_notice(summary, run_dir)

    dump_json(summary, summary_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
