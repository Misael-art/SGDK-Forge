#!/usr/bin/env python3
"""Select the safe SGDK build route for Linux or Windows hosts.

This tool is intentionally read-only unless --output is supplied.  It detects
the compiler/library LTO provenance mismatch that otherwise appears only at the
final link step and emits one machine-readable decision for agents and wrappers.
"""

from __future__ import annotations

import argparse
import json
import platform as host_platform_module
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "sgdk_build_route_report.v1"
LINUX_STAGE_RELATIVE = Path("out/host_tools/sgdk_wine_flatpak/sgdk-2.11")


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        return b""


def detect_compiler_version(gcc_executable: Path) -> str | None:
    """Extract the target GCC version without executing a Windows PE binary."""
    data = _read_bytes(gcc_executable)
    patterns = (
        rb"m68k-elf[/\\](\d+\.\d+\.\d+)",
        rb"(\d+\.\d+\.\d+)\x00gcc version",
    )
    for pattern in patterns:
        match = re.search(pattern, data)
        if match:
            return match.group(1).decode("ascii")
    return None


def detect_library_producer(libmd_archive: Path) -> str | None:
    """Return the first GCC producer version recorded in libmd.a."""
    data = _read_bytes(libmd_archive)
    patterns = (
        rb"GCC: \(GNU\) (\d+\.\d+\.\d+)",
        rb"GCC: \(crosstool-NG [^)]*\) (\d+\.\d+\.\d+)",
    )
    for pattern in patterns:
        match = re.search(pattern, data)
        if match:
            return match.group(1).decode("ascii")
    return None


def library_contains_lto(libmd_archive: Path) -> bool:
    return b".gnu.lto_" in _read_bytes(libmd_archive)


def major(version: str | None) -> int | None:
    if not version:
        return None
    try:
        return int(version.split(".", 1)[0])
    except ValueError:
        return None


def versions_compatible(compiler: str | None, producer: str | None, has_lto: bool) -> bool | None:
    """LTO requires the same GCC major; non-LTO archives are link-compatible."""
    if not has_lto:
        return True
    compiler_major = major(compiler)
    producer_major = major(producer)
    if compiler_major is None or producer_major is None:
        return None
    return compiler_major == producer_major


def normalized_host(requested: str) -> str:
    if requested != "auto":
        return requested
    system = host_platform_module.system().lower()
    if system.startswith("linux"):
        return "linux"
    if system.startswith("windows"):
        return "windows"
    return system or "unknown"


def _quoted_command(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def build_report(repo_root: Path, project_root: Path | None, requested_host: str) -> dict[str, Any]:
    host = normalized_host(requested_host)
    gdk = repo_root / "sdk/sgdk-2.11"
    compiler_path = gdk / "bin/gcc.exe"
    source_lib_path = gdk / "lib/libmd.a"
    staged_gdk = repo_root / LINUX_STAGE_RELATIVE
    staged_lib_path = staged_gdk / "lib/libmd.a"
    bridge_path = repo_root / "tools/sgdk_wrapper/build_sgdk_wine_bridge.sh"
    windows_wrapper = repo_root / "tools/sgdk_wrapper/build.bat"

    compiler_version = detect_compiler_version(compiler_path)
    source_producer = detect_library_producer(source_lib_path)
    source_lto = library_contains_lto(source_lib_path)
    source_compatible = versions_compatible(compiler_version, source_producer, source_lto)

    staged_producer = detect_library_producer(staged_lib_path) if staged_lib_path.is_file() else None
    staged_lto = library_contains_lto(staged_lib_path) if staged_lib_path.is_file() else None
    staged_compatible = (
        versions_compatible(compiler_version, staged_producer, bool(staged_lto))
        if staged_lib_path.is_file()
        else None
    )

    blockers: list[dict[str, str]] = []
    warnings: list[str] = []
    selected_route = "unsupported_host"
    command: str | None = None

    required = {
        "canonical_makefile": gdk / "makefile.gen",
        "compiler": compiler_path,
        "source_library": source_lib_path,
    }
    for artifact, path in required.items():
        if not path.is_file():
            blockers.append(
                {
                    "code": f"{artifact}_missing",
                    "message": f"Required SGDK artifact is missing: {path}",
                }
            )

    if project_root is not None and not project_root.is_dir():
        blockers.append(
            {
                "code": "project_root_missing",
                "message": f"Project root does not exist: {project_root}",
            }
        )

    if compiler_version is None:
        blockers.append(
            {
                "code": "compiler_version_unreadable",
                "message": f"Could not determine compiler version from {compiler_path}",
            }
        )
    if source_producer is None:
        blockers.append(
            {
                "code": "source_library_producer_unreadable",
                "message": f"Could not determine libmd.a producer from {source_lib_path}",
            }
        )

    if host == "linux":
        selected_route = "linux_wine_bridge"
        if not bridge_path.is_file():
            blockers.append(
                {
                    "code": "linux_wine_bridge_missing",
                    "message": f"Canonical Linux bridge is missing: {bridge_path}",
                }
            )
        if project_root is None:
            blockers.append(
                {
                    "code": "project_root_required",
                    "message": "Linux bridge selection requires --project-root.",
                }
            )
        else:
            command = _quoted_command(
                ["bash", str(bridge_path), "--project-root", str(project_root)]
            )

        if source_compatible is False:
            warnings.append(
                "Direct linking against the source SDK is blocked by a GCC/LTO major mismatch; "
                "the Linux bridge must stage and rebuild libmd.a without LTO."
            )
        elif source_compatible is None:
            warnings.append(
                "Direct source-SDK LTO compatibility is unknown; use the isolated Linux bridge."
            )

        if staged_lib_path.is_file() and staged_compatible is False:
            warnings.append(
                "Existing staged libmd.a is incompatible and must be rebuilt by the Linux bridge."
            )
        elif not staged_lib_path.is_file():
            warnings.append(
                "No staged Linux libmd.a exists yet; the bridge will create and rebuild it."
            )

    elif host == "windows":
        selected_route = "windows_batch_wrapper"
        windows_parts = ["cmd.exe", "/d", "/c", str(windows_wrapper)]
        if project_root:
            windows_parts.append(str(project_root))
        command = subprocess.list2cmdline(windows_parts)
        if not windows_wrapper.is_file():
            blockers.append(
                {
                    "code": "windows_batch_wrapper_missing",
                    "message": f"Canonical Windows wrapper is missing: {windows_wrapper}",
                }
            )
        if source_compatible is False:
            blockers.append(
                {
                    "code": "source_sdk_lto_version_mismatch",
                    "message": (
                        f"Source libmd.a was produced by GCC {source_producer} with LTO, "
                        f"but bundled gcc.exe is {compiler_version}. Restore or rebuild libmd.a "
                        "with the bundled compiler before a Windows build."
                    ),
                }
            )
        elif source_compatible is None:
            blockers.append(
                {
                    "code": "source_sdk_lto_compatibility_unknown",
                    "message": "Windows source-SDK LTO compatibility could not be proven.",
                }
            )
    else:
        blockers.append(
            {
                "code": "unsupported_host",
                "message": f"Host platform is not supported by the canonical selector: {host}",
            }
        )

    status = "ready" if not blockers else "blocked"
    return {
        "schema": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "host_platform": host,
        "selected_route": selected_route,
        "command": command,
        "rule": (
            "Select by host first; prove compiler/libmd.a LTO provenance before linking; "
            "never classify a link-toolchain failure as project-code failure without stage evidence."
        ),
        "project_root": str(project_root) if project_root else None,
        "repo_root": str(repo_root),
        "canonical_gdk": str(gdk),
        "compiler": {
            "path": str(compiler_path),
            "version": compiler_version,
        },
        "source_library": {
            "path": str(source_lib_path),
            "producer_version": source_producer,
            "lto_detected": source_lto,
            "direct_link_compatible": source_compatible,
        },
        "linux_stage": {
            "path": str(staged_gdk),
            "library_path": str(staged_lib_path),
            "producer_version": staged_producer,
            "lto_detected": staged_lto,
            "link_compatible": staged_compatible,
            "source_sdk_mutated": False,
        },
        "blockers": blockers,
        "warnings": warnings,
        "status_ceiling_after_build": "buildado_emulator_pending",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument(
        "--platform",
        choices=("auto", "linux", "windows"),
        default="auto",
        help="Override host detection for CI/tests.",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    project_root = args.project_root.resolve() if args.project_root else None
    report = build_report(repo_root, project_root, args.platform)
    payload = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    sys.exit(main())
