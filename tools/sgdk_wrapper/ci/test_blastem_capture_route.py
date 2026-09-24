#!/usr/bin/env python3
"""Permanent host-routing fixtures for BlastEm evidence capture."""
from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sgdk_wrapper"))
from select_blastem_capture_route import select_route  # noqa: E402


class Args:
    repo_root = str(ROOT)
    project_root = str(ROOT / "SGDK_projects" / "TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]")
    target_scene = 3
    output_base = str(ROOT / "out" / "evidence" / "blastem_current")
    powershell_command = "powershell.exe"


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name}: {detail}")
    print(f"[PASS] {name}")


def fake_host(os_name: str, display: str | None = ":0") -> dict[str, object]:
    return {
        "os": os_name,
        "platform_system": "Linux" if os_name == "linux" else "Windows",
        "platform_release": "fixture",
        "arch": "x86_64",
        "display": display,
        "wayland_display": "wayland-0" if os_name == "linux" else None,
        "xdg_session_type": "wayland" if os_name == "linux" else None,
        "desktop": "KDE" if os_name == "linux" else None,
        "bash": "/usr/bin/bash" if os_name == "linux" else None,
        "flatpak": "/usr/bin/flatpak" if os_name == "linux" else None,
        "xdotool": "/usr/bin/xdotool" if os_name == "linux" else None,
        "import": "/usr/bin/import" if os_name == "linux" else None,
        "convert": "/usr/bin/convert" if os_name == "linux" else None,
        "fixture": True,
    }


def main() -> int:
    linux = select_route(Args(), fake_host("linux"))
    check("linux_selects_linux_script", linux["selected_route"] == "linux_flatpak_blastem")
    check("linux_never_selects_winforms", "System.Windows.Forms" not in linux["arguments"])
    check("linux_never_selects_windows_capture", "run_runtime_capture.ps1" not in linux["arguments"])
    check("linux_display_does_not_block", linux["status"] == "selected")
    check("linux_display_is_not_backend_missing", "display_backend_missing" not in linux["blockers"])
    check("linux_command_belongs_to_linux", linux["command"] == "bash")
    check("linux_report_and_command_same_host", linux["selected_route"] == "linux_flatpak_blastem" and linux["command"] == "bash")
    check("linux_publishes_canonical_evidence", "--canonical-root" in linux["arguments"])

    linux_without_display = select_route(Args(), fake_host("linux", None))
    check("linux_without_x11_display_blocks", linux_without_display["status"] == "blocked")
    check("missing_display_has_precise_blocker", "linux_x11_display_missing" in linux_without_display["blockers"])
    check("missing_display_is_not_dependency_missing", all(not item.startswith("linux_flatpak_dependency_missing") for item in linux_without_display["blockers"]))

    windows = select_route(Args(), fake_host("windows", None))
    check("windows_selects_powershell_script", windows["selected_route"] == "windows_powershell_blastem")
    check("windows_never_selects_flatpak", "flatpak" not in windows["arguments"])
    check("windows_command_belongs_to_windows", windows["command"] == "powershell.exe")
    check("windows_report_and_command_same_host", windows["selected_route"] == "windows_powershell_blastem" and windows["command"] == "powershell.exe")

    unknown = select_route(Args(), fake_host("freebsd", None))
    check("unsupported_host_blocks", unknown["status"] == "blocked")
    check("unsupported_host_has_mismatch_decision", unknown["decision"] == "host_executor_route_mismatch")

    linux_capture = (ROOT / "tools/sgdk_wrapper/capture_blastem_evidence_linux.sh").read_text(encoding="utf-8")
    check("linux_capture_accepts_canonical_root", "--canonical-root" in linux_capture)
    check("linux_capture_clears_stale_known_artifacts", 'rm -f "$canonical_root/$artifact"' in linux_capture)
    check("linux_capture_writes_emulator_session", 'emulator_session.json' in linux_capture)
    print("[PASS] blastem capture route fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
