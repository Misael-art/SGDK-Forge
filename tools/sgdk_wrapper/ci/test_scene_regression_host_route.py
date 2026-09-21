#!/usr/bin/env python3
"""Fixtures proving scene regression follows the same host route contract."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sgdk_wrapper"))
from select_blastem_capture_route import select_route  # noqa: E402


class Args:
    repo_root = str(ROOT)
    project_root = str(ROOT / "SGDK_projects" / "TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]")
    target_scene = 3
    output_base = str(ROOT / "out" / "evidence" / "scenes_host")
    powershell_command = "powershell.exe"


def fake_host(os_name: str) -> dict[str, object]:
    linux = os_name == "linux"
    return {
        "os": os_name,
        "platform_system": "Linux" if linux else "Windows",
        "platform_release": "fixture",
        "arch": "x86_64",
        "display": ":0" if linux else None,
        "wayland_display": "wayland-0" if linux else None,
        "xdg_session_type": "wayland" if linux else None,
        "desktop": "KDE" if linux else None,
        "bash": "/usr/bin/bash" if linux else None,
        "flatpak": "/usr/bin/flatpak" if linux else None,
        "xdotool": "/usr/bin/xdotool" if linux else None,
        "import": "/usr/bin/import" if linux else None,
        "convert": "/usr/bin/convert" if linux else None,
        "fixture": True,
    }


def main() -> int:
    linux = select_route(Args(), fake_host("linux"))
    assert linux["status"] == "selected"
    assert linux["command"] == "bash"
    assert "capture_blastem_evidence_linux.sh" in " ".join(linux["arguments"])
    forbidden_linux = " ".join(linux["arguments"])
    assert "run_runtime_capture.ps1" not in forbidden_linux
    assert "blastem.exe" not in forbidden_linux
    assert "System.Windows.Forms" not in forbidden_linux

    windows = select_route(Args(), fake_host("windows"))
    assert windows["status"] == "selected"
    assert windows["command"] == "powershell.exe"
    forbidden_windows = " ".join(windows["arguments"])
    assert "capture_blastem_evidence_linux.sh" not in forbidden_windows
    assert "flatpak" not in forbidden_windows
    print("[PASS] scene regression host route fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
