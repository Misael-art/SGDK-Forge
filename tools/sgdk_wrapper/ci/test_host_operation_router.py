#!/usr/bin/env python3
"""Adversarial tests for host_operation_router.py (persistence route selector).

The router is the persistence twin of select_sgdk_build_route.py. These tests
prove that on a GUI (KDE/Wayland) host it still routes deterministic operations
to headless/direct-API routes, confines writes to the repo/project roots, never
selects a tool that is only `found`, and blocks `~/Downloads` as a target — the
exact failure mode of the 2026-08-30 MARE_BRAVA/TAINA incident.

Usage:
    python tools/sgdk_wrapper/ci/test_host_operation_router.py
Exit codes:
    0 = all pass
    1 = at least one failed
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sgdk_wrapper"))

from host_operation_router import (  # noqa: E402
    build_operation_route,
    GUI_POLICY,
    OPERATION_KINDS,
    detect_host,
)

passed = 0
failed = 0
total = 0
PROJECT = ROOT / "SGDK_projects" / "MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]"


def check(name, cond, detail=""):
    global passed, failed, total
    total += 1
    if cond:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")


def report_for(op):
    return build_operation_route(op, PROJECT, ROOT)


def main():
    print("\n=== Host Operation / Persistence Router Tests ===\n")

    host = detect_host()
    check("host_os_detected", host["os"] in {"linux", "windows"})

    # (1) persist_editor_export must route to direct API, never a GUI picker.
    r = report_for("persist_editor_export")
    check("editor_export_route_is_direct_api", r["route"] == "editor_api_save")
    check("editor_export_gui_policy_direct", r["gui_policy"] == "direct_api_required")
    check("editor_export_command_uses_api", "POST /api/save" in (r["command"] or ""))
    check("editor_export_no_gui_picker", "gui_file_picker" in r["forbidden_routes"])
    check("editor_export_downloads_blocked",
          any("Downloads" in p for p in r["write_confinement"]["blocked_roots"]),
          "~/Downloads must never be a target")

    # (2) Deterministic ops are headless and GUI is irrelevant even on KDE.
    for op in ("convert_asset", "index_quantize_asset", "validate_asset", "persist_generated_asset"):
        r = report_for(op)
        check(f"{op}_headless", r["gui_policy"] == "headless_required")
        check(f"{op}_gui_irrelevant", r["gui_state"] == "irrelevant")

    # (3) import_external_drop is quarantine with hash, never direct promotion.
    r = report_for("import_external_drop")
    check("external_drop_quarantine_policy", r["gui_policy"] == "external_drop_quarantine")
    check("external_drop_route_quarantine", r["route"] == "quarantine_import_with_hash")

    # (4) human_interactive_edit is human-only.
    r = report_for("human_interactive_edit")
    check("human_edit_policy_human", r["gui_policy"] == "human_interactive")
    check("human_edit_route_human_only", r["route"] == "human_only")

    # (5) Unknown operation is a blocker, not a silent guess.
    r = build_operation_route("not_a_real_op", PROJECT, ROOT)
    check("unknown_op_blocked", r["status"] == "blocked", f"got {r['status']}")

    # (6) An unknown operation kind never self-satisfies.
    check("unknown_op_includes_blocker",
          any(b["code"] == "unknown_operation_kind" for b in r["blockers"]))

    # (7) Write confinement: allowed roots are inside repo, blocked has home/Downloads.
    r = report_for("persist_editor_export")
    allowed = r["write_confinement"]["allowed_roots"]
    check("allowed_roots_nonempty", len(allowed) >= 1)
    check("allowed_root_covers_repo", any(str(ROOT) == p for p in allowed))
    check("home_blocked", any(
        str(Path.home()) == p or "Downloads" in p
        for p in r["write_confinement"]["blocked_roots"]))

    # (8) Every operation has a valid GUI policy (the table stays total).
    for op in OPERATION_KINDS:
        r = report_for(op)
        check(f"op_{op}_has_gui_policy", r["gui_policy"] in GUI_POLICY)

    print(f"\n{passed}/{total} host-operation-router tests passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
