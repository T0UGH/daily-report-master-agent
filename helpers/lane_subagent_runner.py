from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from helpers.lane_contracts import validate_lane_output_artifact


DEFAULT_TIMEOUT_SECONDS = 300
REPO_ROOT = Path(__file__).resolve().parent.parent


def _render_log(
    *,
    command: list[str],
    input_path: Path,
    output_path: Path,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    timed_out: bool = False,
) -> str:
    status_line = "timed out" if timed_out else str(exit_code)
    return (
        "# Lane Subagent Worker\n\n"
        f"Command: `{shlex.join(command)}`\n\n"
        f"Input: `{input_path}`\n\n"
        f"Output: `{output_path}`\n\n"
        f"Exit Code: {status_line}\n\n"
        "## STDOUT\n\n"
        "```text\n"
        f"{stdout}"
        "```\n\n"
        "## STDERR\n\n"
        "```text\n"
        f"{stderr}"
        "```\n"
    )


def _write_log(
    log_path: Path,
    *,
    command: list[str],
    input_path: Path,
    output_path: Path,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    timed_out: bool = False,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        _render_log(
            command=command,
            input_path=input_path,
            output_path=output_path,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            timed_out=timed_out,
        ),
        encoding="utf-8",
    )


def _timeout_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def run_lane_subagent(
    input_path: Path,
    output_path: Path,
    log_path: Path,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    input_path = Path(input_path).resolve()
    output_path = Path(output_path).resolve()
    log_path = Path(log_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    command = [
        sys.executable,
        "-m",
        "helpers.lane_subagent_worker",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as error:
        _write_log(
            log_path,
            command=command,
            input_path=input_path,
            output_path=output_path,
            exit_code=None,
            stdout=_timeout_text(error.stdout),
            stderr=_timeout_text(error.stderr),
            timed_out=True,
        )
        raise RuntimeError(f"lane subagent worker timed out after {timeout_seconds}s; log: {log_path}") from error

    _write_log(
        log_path,
        command=command,
        input_path=input_path,
        output_path=output_path,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"lane subagent worker failed with exit code {completed.returncode}; log: {log_path}")
    if not output_path.is_file():
        raise RuntimeError(f"lane subagent worker did not create output: {output_path}; log: {log_path}")

    try:
        output = json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"lane subagent worker wrote invalid JSON: {output_path}; log: {log_path}") from error
    try:
        validate_lane_output_artifact(output)
    except Exception as error:
        raise RuntimeError(f"lane subagent worker wrote invalid lane output: {output_path}; log: {log_path}") from error
    return output
