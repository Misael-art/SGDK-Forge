#!/usr/bin/env python3
"""Select the BlastEm capture route from the real host.

The selector is deliberately explicit: native Linux uses the Flatpak/Linux
capture script, while Windows uses the PowerShell/Win32 capture script.  A
display variable is evidence about the desktop session, not permission to
cross the host executor boundary.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--target-scene", required=True, type=int)
    parser.add_argument("--output-base", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--powershell-command", default="powershell.exe")
    parser.add_argument("--warmup-seconds", default="20")
    parser.add_argument("--burst-delay", default="1.0")
    parser.add_argument("--burst-count", default="12")
    parser.add_argument("--burst-interval", default="0.10")
    return parser.parse_args()


def host_context() -> dict[str, object]:
    system = platform.system().lower()
    os_name = "windows" if system.startswith("win") else ("linux" if system == "linux" else system)
    return {
        "os": os_name,
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "arch": platform.machine(),
        "display": os.environ.get("DISPLAY"),
        "wayland_display": os.environ.get("WAYLAND_DISPLAY"),
        "xdg_session_type": os.environ.get("XDG_SESSION_TYPE"),
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP"),
        "bash": shutil.which("bash"),
        "flatpak": shutil.which("flatpak"),
        "xdotool": shutil.which("xdotool"),
        "import": shutil.which("import"),
        "convert": shutil.which("convert"),
    }


def select_route(args: argparse.Namespace, host: dict[str, object]) -> dict[str, object]:
    repo = Path(args.repo_root).resolve()
    project = Path(args.project_root).resolve()
    script_dir = repo / "tools" / "sgdk_wrapper"
    linux_script = script_dir / "capture_blastem_evidence_linux.sh"
    windows_script = script_dir / "run_runtime_capture.ps1"

    if host["os"] == "linux":
        command = "bash"
        arguments = [
            str(linux_script),
            "--project-root", str(project),
            "--rom", str(project / "out" / "rom.bin"),
            "--output-base", args.output_base,
            "--canonical-root", str(project / "out" / "evidence" / "blastem"),
            "--target-scene", str(args.target_scene),
            "--warmup-seconds", str(getattr(args, "warmup_seconds", "20")),
            "--burst-delay", str(getattr(args, "burst_delay", "1.0")),
            "--burst-count", str(getattr(args, "burst_count", "12")),
            "--burst-interval", str(getattr(args, "burst_interval", "0.10")),
        ]
        blockers = []
        if not linux_script.is_file():
            blockers.append("linux_capture_script_missing")
        for dependency in ("bash", "flatpak", "xdotool", "import"):
            if not host.get(dependency):
                blockers.append(f"linux_capture_dependency_missing:{dependency}")
        # xdotool/ImageMagick capture the XWayland window. WAYLAND_DISPLAY by
        # itself is not sufficient, while DISPLAY=:0 on KDE/Wayland is valid.
        if not host.get("display"):
            blockers.append("linux_x11_display_missing")
        route = "linux_flatpak_blastem"
        forbidden = ["run_runtime_capture.ps1", "blastem.exe", "wine", "System.Windows.Forms"]
    elif host["os"] == "windows":
        command = args.powershell_command
        arguments = [
            "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(windows_script),
            "-ProjectDir", str(project), "-TargetScene", str(args.target_scene),
            "-Emulator", "blastem",
        ]
        blockers = []
        if not windows_script.is_file():
            blockers.append("windows_capture_script_missing")
        if not host.get("fixture") and shutil.which(command) is None and not Path(command).is_file():
            blockers.append("powershell_missing")
        route = "windows_powershell_blastem"
        forbidden = ["capture_blastem_evidence_linux.sh", "flatpak"]
    else:
        command = None
        arguments = []
        blockers = ["unsupported_capture_host"]
        route = "blocked"
        forbidden = []

    return {
        "schema_version": "blastem_capture_route.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "host": host,
        "selected_route": route,
        "command": command,
        "arguments": arguments,
        "forbidden_route_markers": forbidden,
        "blockers": blockers,
        "status": "selected" if not blockers else "blocked",
        "project_root": str(project),
        "output_base": str(Path(args.output_base).resolve()),
        "target_scene": args.target_scene,
        "decision": "host_executor_route_mismatch_resolved" if not blockers else "host_executor_route_mismatch",
    }


def main() -> int:
    args = parse_args()
    route = select_route(args, host_context())
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(route, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(route, separators=(",", ":")))
    return 0 if route["status"] == "selected" else 1


if __name__ == "__main__":
    sys.exit(main())
