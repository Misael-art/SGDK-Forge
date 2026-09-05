#!/usr/bin/env python3
"""Select the safe persistence / host-operation route for an agent.

This is the persistence twin of `select_sgdk_build_route.py`. Where the build
selector resolves "how does this host link SGDK?", this router resolves "how must
this kind of artifact be created, stored and validated on THIS host?".

The 2026-08-30 MARE_BRAVA/TAINA incident showed the failure mode: the project
already had a direct, confined save route (editor `POST /api/save` into a fixed
`exports/` dir), but the agent ignored it, opened `xdg-open`/a KDE file picker
and wrote into `/home/misael/Downloads` — two divergent copies with matching PNG
hash but diverging action JSON, breaking provenance. A "detect Linux vs Windows"
alone would not have helped: the host already had every tool. The missing piece
is a *mandatory per-operation decision* that turns detected capability into a
binding route with write-confinement and provenance.

This tool is intentionally read-only unless `--output` is supplied. It emits one
machine-readable decision. It never installs anything, never caches indefinitely,
and never treats "executable exists" as "self-check passed" or "selected".

States are distinct, matching SGDK_GLOBAL §38 (capability declared with proof):
  found            -> executable/binary is present on the host
  selfcheck_passed -> the tool actually passed its own self-check (probed now)
  selected         -> chosen for THIS operation
Something that is only `found` MUST NOT be reported as `selected`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA_VERSION = "persistence_route_report.v1"

# ---------------------------------------------------------------------------
# Operation vocabulary (what kind of artifact is being produced)
# ---------------------------------------------------------------------------
OPERATION_KINDS = {
    "persist_editor_export",
    "persist_generated_asset",
    "convert_asset",
    "index_quantize_asset",
    "validate_asset",
    "import_external_drop",
    "human_interactive_edit",
}

# GUI policy classification (per SGDK_GLOBAL §38 / CLI-first doctrine).
# A host having KDE does NOT mean the agent may drive the KDE file picker for
# deterministic operations; GUI presence is irrelevant to those.
GUI_POLICY = {
    "headless_required": (
        "Conversion, indexing, quantization, resize, validation and repeatable "
        "export must run headless/CLI. GUI is irrelevant to these."
    ),
    "direct_api_required": (
        "Editors that already expose a save endpoint must be driven through it "
        "(e.g. POST /api/save), never through a file picker."
    ),
    "human_interactive": (
        "Subjective visual decisions or deliberate human editing are human "
        "interactive. The agent may present, not decide."
    ),
    "gui_agent_forbidden": (
        "KDE file picker, xdg-open, pointer automation and typing file paths "
        "into a picker are forbidden as agent routes."
    ),
    "external_drop_quarantine": (
        "A file inevitably downloaded by the browser is not yet a project asset; "
        "it must be imported deterministically with hash + provenance, never "
        "promoted directly."
    ),
}

# Mapping each operation kind to a recommended GUI policy. This is a decision
# table, not a brain: it stays small and is consumed by workflows.
OPERATION_GUI_POLICY = {
    "persist_editor_export": "direct_api_required",
    "persist_generated_asset": "headless_required",
    "convert_asset": "headless_required",
    "index_quantize_asset": "headless_required",
    "validate_asset": "headless_required",
    "import_external_drop": "external_drop_quarantine",
    "human_interactive_edit": "human_interactive",
}

# Tools/producers that, if present, may satisfy an operation headlessly. The
# router only reports presence + (optionally) selected route; it never assumes
# a binary works without a probe.
PREFERRED_CLI = ["forge-art", "python3", "magick", "gimp_batch", "editor_api"]

# ---------------------------------------------------------------------------
# Host detection
# ---------------------------------------------------------------------------

def detect_host() -> Dict[str, Any]:
    import platform
    system = platform.system().lower()
    os_name = "linux" if system.startswith("linux") else ("windows" if system.startswith("windows") else system)
    desktop = "unknown"
    session_type = "unknown"
    session_variant = None

    # KDE / Wayland / X11 session detection (Linux); Windows DWM is implicit.
    xdg_session = (__import__("os").environ.get("XDG_SESSION_TYPE") or "").lower()
    if xdg_session in {"wayland", "x11"}:
        session_type = xdg_session
    kde = (__import__("os").environ.get("KDE_SESSION_VERSION") or "")
    desktop_env = (__import__("os").environ.get("XDG_CURRENT_DESKTOP") or "").lower()
    if kde or "kde" in desktop_env or "plasma" in desktop_env:
        desktop = "kde"
        session_variant = f"plasma_{kde}" if kde else "plasma_unknown"
    elif desktop_env:
        desktop = desktop_env
    if os_name == "windows":
        session_type = "windows_session"

    return {
        "os": os_name,
        "distribution": platform.platform(),
        "arch": platform.machine(),
        "desktop": desktop,
        "session_type": session_type,
        "session_variant": session_variant,
        "execution_mode": _detect_execution_mode(),
    }


def _detect_execution_mode() -> str:
    """Distinguish native vs wine/wsl/container/flatpak execution loosely.

    This is best-effort and never used alone to authorize a tool; the caller
    must probe (self-check) before treating a tool as usable.
    """
    import os
    if os.environ.get("WSL_DISTRO_NAME"):
        return "wsl"
    if os.environ.get("FLATPAK_ID"):
        return "flatpak"
    if os.environ.get("container"):
        return "container"
    if shutil.which("wine"):
        return "native_with_wine"
    return "native"


def detect_tools() -> Dict[str, Any]:
    """Report presence of producer candidates (found only, not self-checked).

    Each entry carries its own `state` so the router never conflates 'found'
    with 'selected'. The caller must run the tool's self-check and emit a
    separate probe result before selecting it.
    """
    def probe(name: str) -> Dict[str, Any]:
        path = shutil.which(name)
        if path is None:
            # Some tools live under tools/ subdirs or have alias names.
            return {"name": name, "path": None, "state": "not_found"}
        return {"name": name, "path": str(path), "state": "found"}

    return {
        "python3": probe("python3"),
        "magick": probe("magick"),
        "convert": probe("convert"),
        "gimp": probe("gimp"),
        "pwsh": probe("pwsh"),
        "forge_art_module": {
            "name": "forge_art",
            "path": "tools/sgdk_wrapper/forge_art/",
            "state": _forge_art_present(),
        },
    }


def _forge_art_present() -> str:
    p = Path(__file__).resolve().parent / "forge_art"
    return "found" if (p / "vdp_color.py").is_file() else "not_found"


# ---------------------------------------------------------------------------
# Operation routing
# ---------------------------------------------------------------------------

def _allowed_roots() -> list[str]:
    """Canonical write roots. Never /home, ~/Downloads, or CWD by default."""
    here = Path(__file__).resolve()
    wrapper = here.parent
    repo = wrapper.parent.parent
    return [str(repo)]


def _blocked_roots() -> list[str]:
    import os
    home = os.path.expanduser("~")
    return [
        str(Path(home) / "Downloads"),
        str(Path(home) / "Desktop"),
        str(Path(home) / "Documents"),
        str(Path.home()),
    ]


def build_operation_route(operation: str, project_root: Optional[Path],
                          repo_root: Path) -> Dict[str, Any]:
    import os
    gui_policy = OPERATION_GUI_POLICY.get(operation, "headless_required")

    write_confined = _allowed_roots()
    allowed_writers = _write_targets_for(operation, project_root)

    # Forbidden routes: exact incident.
    forbidden = {
        "gui_file_picker": (
            "KDE/GNOME file picker + xdg-open. The 2026-08-30 TAINA incident "
            "wrote to ~/Downloads via a picker. forbidden as agent route."
        ),
        "pointer_automation": "Pointer automation / typing paths into a picker.",
        "optional_download_drop": (
            "Browser/OS downloads to ~/Downloads are NOT project assets; import "
            "deterministically with hash or leave quarantined."
        ),
    }

    reasons: list[str] = []
    blockers: list[dict[str, str]] = []
    warnings: list[str] = []

    if operation not in OPERATION_KINDS:
        blockers.append({
            "code": "unknown_operation_kind",
            "message": f"Unknown operation kind '{operation}'. Valid: {sorted(OPERATION_KINDS)}",
        })

    if operation == "import_external_drop" and not project_root:
        blockers.append({
            "code": "import_requires_project_root",
            "message": "external_drop import needs a project_root to quarantine into.",
        })

    if project_root is not None and not project_root.is_dir():
        blockers.append({
            "code": "project_root_missing",
            "message": f"Project root does not exist: {project_root}",
        })

    # Persistence route selection per operation.
    route = "cli_confined_write"
    command: Optional[str] = None
    if operation == "persist_editor_export":
        route = "editor_api_save"
        command = "POST /api/save -> <project>/rascunho/<editor>/exports/<name>"
    elif operation == "persist_generated_asset":
        route = "generator_returned_artifact"
        command = "Write the returned artifact to <project>/data/source_art/<role>/<name> via CLI/API."
    elif operation == "import_external_drop":
        route = "quarantine_import_with_hash"
        command = "Import to <project>/rascunho/, compute sha256, require provenance + lineage; never promote directly."
    elif operation == "human_interactive_edit":
        route = "human_only"
        command = "Present to a human; the agent does not decide or save final."

    # Detect the confined/safe write location for this op (informational; the
    # agent must resolve the exact project path against project_root).
    preferred_target = _preferred_save_path(operation, project_root)

    # A host with a GUI is recorded but NOT selected for deterministic ops.
    gui_state = "irrelevant" if gui_policy == "headless_required" else gui_policy

    return {
        "schema": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "ready" if not blockers else "blocked",
        "operation": operation,
        "gui_policy": gui_policy,
        "gui_state": gui_state,
        "route": route,
        "command": command,
        "preferred_target": preferred_target,
        "tools_found": detect_tools(),
        "host": detect_host(),
        "write_confinement": {
            "allowed_roots": write_confined,
            "blocked_roots": _blocked_roots(),
            "rule": "Write only inside allowed_roots; never resolve a path outside project via .. or a picker.",
        },
        "forbidden_routes": forbidden,
        "suggested_selfchecks": [
            "forge-art self-check",
            "pixel_contract.py --validate ...",
            "normalize_indexed_sgdk_png.py transparent0 <file>",
        ],
        "rule": (
            "Pick the persistence route by operation kind first (per GUI policy); "
            "only a `selfcheck_passed` tool may be `selected`; never drive the GUI "
            "picker for deterministic work; external downloads must be quarantined "
            "with hash and provenance. Prohibited ~/Downloads / CWD / ~ as targets."
        ),
        "project_root": str(project_root) if project_root else None,
        "repo_root": str(repo_root),
        "blockers": blockers,
        "warnings": warnings,
        "source_of_truth_note": (
            "Router is an executor, not a record of truth. Provenance and hashes "
            "come from the artifacts (manifests, reports, evidence); this decision "
            "must not be cached forever — re-run when the host changes."
        ),
    }


def _write_targets_for(operation: str, project_root: Optional[Path]) -> list[str]:
    if operation == "import_external_drop":
        return ["<project>/rascunho/"]
    if operation == "persist_editor_export":
        return ["<project>/rascunho/<editor>/exports/"]
    if operation == "persist_generated_asset":
        return ["<project>/data/source_art/<role>/", "<project>/data/raw_ai/<run>/"]
    if operation == "convert_asset":
        return ["<project>/data/processed/"]
    return ["<project>/rascunho/", "<project>/data/processed/", "<project>/data/source_art/"]


def _preferred_save_path(operation: str, project_root: Optional[Path]) -> Optional[str]:
    base = str(project_root) if project_root else "<project>"
    if operation == "persist_editor_export":
        return f"{base}/rascunho/<editor>/exports/<name>"
    if operation == "import_external_drop":
        return f"{base}/rascunho/imports/<name>"
    if operation == "persist_generated_asset":
        return f"{base}/data/source_art/<role>/<name>"
    return f"{base}/rascunho/<name>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation", required=True,
                        choices=sorted(OPERATION_KINDS))
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--repo-root", type=Path,
                        default=Path(__file__).resolve().parent.parent.parent)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--platform",
                        choices=("auto", "linux", "windows"),
                        default="auto",
                        help="Override host detection for CI/tests.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    project_root = args.project_root.resolve() if args.project_root else None

    report = build_operation_route(args.operation, project_root, repo_root)
    if args.platform != "auto":
        report["host"]["os"] = args.platform
        report["host"]["execution_mode"] = "ci_override"

    payload = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    sys.exit(main())
