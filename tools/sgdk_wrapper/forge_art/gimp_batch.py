"""Optional, headless GIMP capability adapter for curated operations.

GIMP is not a forge-art colour authority and is never required by the core
converter.  This module only proves that the local GIMP 3 Python batch
interpreter is callable without a GUI.  Production image operations must be
registered as static, reviewed operations before this adapter may execute
them; prompt-generated Python-Fu is deliberately not accepted.
"""
from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from forge_art import schema_gate

TOOL_NAME = "forge_art.gimp_batch"
TOOL_VERSION = "1.0.0"
INTERPRETER = "python-fu-eval"
PROBE_SENTINEL = "FORGE_GIMP_PYTHON_BATCH_OK"
DEFAULT_TIMEOUT_SECONDS = 30

# Empty by design.  A production operation enters this registry only with a
# static script, a declarative schema and positive/negative fixtures.
REGISTERED_PRODUCTION_OPERATIONS: tuple[str, ...] = ()


class GimpBatchError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_executable(explicit: str | None) -> Path | None:
    if explicit:
        candidate = Path(explicit)
        if candidate.parent != Path("."):
            resolved = candidate.expanduser().resolve()
            return resolved if resolved.is_file() and os.access(resolved, os.X_OK) else None
        located = shutil.which(explicit)
        return Path(located).resolve() if located else None
    located = shutil.which("gimp")
    return Path(located).resolve() if located else None


def _run(command: list[str], *, timeout_seconds: int, env: dict[str, str] | None = None) -> dict:
    """Run without a shell and kill the complete process group on timeout."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
    return {
        "exit_code": process.returncode if process.returncode is not None else -1,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
    }


def _version_tuple(text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(?:version\s+)?(\d+)\.(\d+)(?:\.(\d+))?", text, re.IGNORECASE)
    if not match:
        return None
    return tuple(int(value or 0) for value in match.groups())


def _probe_command(executable: Path) -> list[str]:
    return [
        str(executable),
        "-n",
        "-i",
        "-d",
        "-f",
        "-c",
        f"--batch-interpreter={INTERPRETER}",
        "-b",
        f'print("{PROBE_SENTINEL}")',
        "--quit",
    ]


def _warning_lines(stderr: str, maximum: int = 40) -> list[str]:
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    return lines[-maximum:]


def preflight(explicit_executable: str | None = None,
              timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """Probe GIMP 3 Python batch mode in an isolated XDG profile."""
    if timeout_seconds < 1 or timeout_seconds > 120:
        raise GimpBatchError("gimp_batch_timeout_out_of_range")

    executable = _resolve_executable(explicit_executable)
    report = {
        "schema_version": "1.0.0",
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "recorded_at": _now(),
        "status": "unavailable",
        "blocking": True,
        "executable": str(executable) if executable else "",
        "gimp_version": "unknown",
        "interpreter": INTERPRETER,
        "sentinel_observed": False,
        "exit_code": -1,
        "warnings": [],
        "blockers": [],
        "policy": {
            "gui_pointer_automation_allowed": False,
            "arbitrary_generated_script_allowed": False,
            "registered_production_operations": list(REGISTERED_PRODUCTION_OPERATIONS),
            "claim_ceiling": "optional_batch_capability_only",
        },
    }
    if executable is None:
        report["blockers"] = ["gimp_batch_executable_not_found"]
        schema_gate.validate_named(report, "gimp_batch_preflight_report")
        return report

    version_run = _run([str(executable), "--version"], timeout_seconds=timeout_seconds)
    version_text = (version_run["stdout"] + "\n" + version_run["stderr"]).strip()
    version = _version_tuple(version_text)
    report["gimp_version"] = ".".join(str(part) for part in version) if version else "unknown"
    if version_run["timed_out"]:
        report["status"] = "failed"
        report["blockers"] = ["gimp_batch_version_probe_timeout"]
    elif version_run["exit_code"] != 0 or version is None:
        report["status"] = "failed"
        report["exit_code"] = version_run["exit_code"]
        report["warnings"] = _warning_lines(version_run["stderr"])
        report["blockers"] = ["gimp_batch_version_probe_failed"]
    elif version[0] < 3:
        report["status"] = "failed"
        report["exit_code"] = version_run["exit_code"]
        report["blockers"] = ["gimp_batch_requires_gimp3"]
    else:
        with tempfile.TemporaryDirectory(prefix="forge_gimp_batch_") as raw_profile:
            profile = Path(raw_profile)
            env = os.environ.copy()
            for variable, folder in (
                ("XDG_CONFIG_HOME", "config"),
                ("XDG_CACHE_HOME", "cache"),
                ("XDG_DATA_HOME", "data"),
            ):
                target = profile / folder
                target.mkdir()
                env[variable] = str(target)
            probe = _run(_probe_command(executable), timeout_seconds=timeout_seconds, env=env)
        report["exit_code"] = probe["exit_code"]
        report["warnings"] = _warning_lines(probe["stderr"])
        report["sentinel_observed"] = PROBE_SENTINEL in probe["stdout"]
        if probe["timed_out"]:
            report["status"] = "failed"
            report["blockers"] = ["gimp_batch_python_probe_timeout"]
        elif probe["exit_code"] != 0 or not report["sentinel_observed"]:
            report["status"] = "failed"
            report["blockers"] = ["gimp_batch_python_interpreter_failed"]
        else:
            report["status"] = "operational"
            report["blocking"] = False

    schema_gate.validate_named(report, "gimp_batch_preflight_report")
    return report


def require_registered_operation(operation: str) -> str:
    """Fail closed until a reviewed production operation is registered."""
    if operation not in REGISTERED_PRODUCTION_OPERATIONS:
        raise GimpBatchError(f"gimp_batch_operation_not_registered:{operation}")
    return operation


def self_check() -> dict:
    fixtures = []
    command = _probe_command(Path("/usr/bin/gimp"))
    fixtures.append({
        "name": "probe_is_headless_and_non_shell",
        "kind": "positive",
        "passed": all(flag in command for flag in ("-n", "-i", "-c", "--quit")),
    })
    fixtures.append({
        "name": "gimp3_version_is_accepted",
        "kind": "positive",
        "passed": _version_tuple("GNU Image Manipulation Program version 3.2.4") == (3, 2, 4),
    })
    try:
        require_registered_operation("prompt_generated_python")
        rejected = False
    except GimpBatchError:
        rejected = True
    fixtures.append({
        "name": "arbitrary_operation_is_rejected",
        "kind": "negative",
        "passed": rejected,
    })
    fixtures.append({
        "name": "warning_capture_is_bounded",
        "kind": "negative",
        "passed": len(_warning_lines("\n".join(str(i) for i in range(100)))) == 40,
    })
    return {
        "fixtures": fixtures,
        "fixtures_passed": sum(item["passed"] for item in fixtures),
        "fixtures_total": len(fixtures),
        "blocking": not all(item["passed"] for item in fixtures),
    }

