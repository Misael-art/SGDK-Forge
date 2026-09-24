#!/usr/bin/env python3
"""
imagegen_circuit.py
Ring 1 of the MegaDrive_DEV image generation stack.

Purpose:
    Single entry point the AI agent or human can call to generate, gate, and
    persist a source-candidate image for a specific project. Coordinates
    `imagegen_tool.py` (Ring 2) plus a triple gate (license + host + scope)
    plus a multi-path master_style_manifest lookup, and never writes anything
    under `res/`. Native callable/inline channels win before local gates.

Design rules (locked, do not relax):
    - Native channels (callable / inline) win over local.
    - Bonsai is opt-in fallback; if native/API is unavailable and any Bonsai
      gate fails, the circuit returns a structured
      `generation_channel_decision.json` and writes NOTHING.
    - Initial status of any Bonsai output is `source_candidate` only. Promotion
      to `premium_source_accepted` is out of scope and requires the human
      pipeline (art-translation-to-vdp + pixel-strict-rules + visual audit).
    - Every run emits a `prompt_pack_manifest.json` co-located with the raw
      output. This is the per-run evidence.
    - Asset roles outside `bonsai_4b_ternary.allowed_scopes` are refused
      BEFORE any backend is invoked.
    - The circuit never reads/writes under `res/`. The `convert` step
      (`imagegen_tool.py convert`) is the only path to `res/`, and it enforces
      the role allowlist.

Usage:
    # Dry-run preflight only (read-only, no files created)
    python tools/ai_imagegen/imagegen_circuit.py preflight \\
        --project "..." --asset-role concept_art [--style-manifest PATH] [--json]

    # Real run: native selection returns next_action=use_native_channel; local
    # Bonsai run requires all Bonsai gates to pass
    python tools/ai_imagegen/imagegen_circuit.py run \\
        --project "..." --asset-role concept_art \\
        --prompt "1-bit Bonsai tree silhouette, monochrome, hard dithering" \\
        [--style-manifest PATH] [--seed 42] [--width 1024] [--height 1024] \\
        [--profile bonsai_4b_ternary] [--json]

Exit codes:
    0  success (run or preflight-only)
    2  license_blocked
    3  scope_blocked
    4  blocked_host_capability
    5  asset_role is forbidden (Bonsai forbidden_scopes)
    6  backend refused (license/host/serve_offline)
    7  filesystem error (could not write required reports)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from imagegen_tool import (  # noqa: E402
    REPO_ROOT,
    DATA_RAW_AI,
    DATA_SOURCE_ART,
    BONSAI_LICENSE_ACK,
    BONSAI_VENDOR_MANIFEST,
    _load_license_ack,
    _validate_asset_scope,
    _resolve_master_style_manifest,
    _bonsai_serve_online,
    _hash_file,
    _build_preflight_report,
    _license_gate_status,
    _host_gate_status,
    _scope_gate_status,
    parse_bool_auto,
    BONSAI_ALLOWED_SCOPES,
    BONSAI_FORBIDDEN_SCOPES,
    cmd_bonsai_generate,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_project_root(project: str | None, project_root: str | None) -> Path | None:
    if project_root:
        p = Path(project_root).resolve()
        return p if p.exists() else None
    if project:
        candidate = REPO_ROOT / "SGDK_projects" / project
        if candidate.exists():
            return candidate
    return None


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_imagegen_tool(args: list[str]) -> tuple[int, str, str]:
    """Run imagegen_tool.py as a subprocess and return (rc, stdout, stderr).

    Defense in depth: if subprocess returned rc=0 but stdout (or stderr)
    contains a JSON `{"ok": false, ...}` payload, treat it as a failure
    (return rc=2). This protects against any future regression in
    imagegen_tool.py's main() exit-code propagation.
    """
    import re
    _OK_FALSE_RE = re.compile(r'"ok"\s*:\s*false')
    cmd = [sys.executable, str(SCRIPT_DIR / "imagegen_tool.py"), *args]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=900
        )
        rc = result.returncode
        combined = (result.stdout or "") + (result.stderr or "")
        if rc == 0 and _OK_FALSE_RE.search(combined):
            rc = 2
        return rc, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def write_preflight_decision(report: dict, project_root: Path) -> Path:
    out_dir = project_root / "out" / "logs"
    ensure_dirs(out_dir)
    out_path = out_dir / "generation_channel_decision.json"
    write_json(out_path, report)
    return out_path


def promote_to_source_art(
    raw_output: Path,
    project_root: Path,
    asset_role: str,
    lineage_id: str,
    preflight: dict,
    pack_path: Path,
) -> tuple[Path, Path]:
    """Copy raw output to <project>/data/source_art/<role>/source.png
    and write a premium_source_manifest.json with status=source_candidate.
    """
    source_dir = project_root / "data" / "source_art" / asset_role
    ensure_dirs(source_dir)
    dest_png = source_dir / "source.png"
    if raw_output.exists():
        # copy bytes
        dest_png.write_bytes(raw_output.read_bytes())
    lineage = {
        "lineage_id": lineage_id,
        "run_id": preflight.get("run_id", ""),
        "timestamp": now_iso(),
        "raw_path": str(raw_output.relative_to(REPO_ROOT)).replace("\\", "/")
        if raw_output.exists()
        else "",
        "source_art_path": str(dest_png.relative_to(REPO_ROOT)).replace("\\", "/")
        if dest_png.exists()
        else "",
        "res_paths": [],
        "conversion_log": "",
        "prompt_pack_path": str(pack_path.relative_to(REPO_ROOT)).replace("\\", "/")
        if pack_path.exists()
        else "",
        "vendor_manifest_sha256": _hash_file(BONSAI_VENDOR_MANIFEST)
        if BONSAI_VENDOR_MANIFEST.exists()
        else "",
        "license_ack_sha256": _license_gate_status().get("ack_sha256", ""),
        "style_manifest_sha256": preflight.get("style_manifest_lookup", {}).get("sha256", ""),
        "style_manifest_path": preflight.get("style_manifest_lookup", {}).get("resolved_path", ""),
        "asset_role": asset_role,
        "initial_status": "source_candidate",
    }
    lineage_path = project_root / "out" / "logs" / f"asset_lineage_record_{lineage_id}.json"
    ensure_dirs(lineage_path.parent)
    write_json(lineage_path, lineage)

    premium = {
        "asset_id": f"{asset_role}_{lineage_id[:6]}",
        "accepted_as_premium_source": False,
        "license_or_generation_basis": "Bonsai 4B opt-in source_candidate; requires "
        "art-translation-to-vdp + megadrive-pixel-strict-rules + visual-excellence-standards "
        "PASS before promotion to accepted.",
        "role": asset_role,
        "rejection_reasons": [
            "Initial Bonsai output is always source_candidate; never premium_source_accepted."
        ],
        "notes": "Generated by imagegen_circuit.py. Run by human or auto-trigger from "
        "art-creation-sourcing Rota A passo 3.",
    }
    premium_path = source_dir / "premium_source_manifest.json"
    write_json(premium_path, premium)
    return dest_png, lineage_path


def cmd_preflight(args) -> int:
    project_root = resolve_project_root(args.project, args.project_root)
    asset_role = args.asset_role

    # asset_role_required semantics: if user passed --asset-role, gate it strictly.
    asset_role_required = bool(asset_role)

    report = _build_preflight_report(
        project_root=project_root,
        asset_role=asset_role,
        style_manifest_override=args.style_manifest,
        native_callable=args.native_callable,
        native_inline=args.native_inline,
        asset_role_required=asset_role_required,
    )

    if project_root is not None and args.write_decision:
        decision_path = write_preflight_decision(report, project_root)
        report["_decision_written_to"] = str(decision_path.relative_to(REPO_ROOT)).replace(
            "\\", "/"
        )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Selected source: {report['selected_source']}")
        print(f"Profile used:    {report['profile_used']}")
        print(
            "Gates: "
            f"license={'PASS' if report['gates']['license']['passed'] else 'FAIL'} "
            f"host={'PASS' if report['gates']['host']['passed'] else 'FAIL'} "
            f"scope={'PASS' if report['gates']['scope']['passed'] else 'FAIL'}"
        )
        print(f"Rationale: {report['rationale']}")
        print(f"Next:     {report['next_action']}")
        if "_decision_written_to" in report:
            print(f"Decision saved to: {report['_decision_written_to']}")

    sel = report["selected_source"]
    if sel == "license_blocked":
        return 2
    if sel == "scope_blocked":
        return 3
    if sel == "blocked_host_capability":
        return 4
    return 0


def cmd_run(args) -> int:
    project_root = resolve_project_root(args.project, args.project_root)
    if project_root is None:
        print(
            f"ERROR: could not resolve project root from --project={args.project!r} "
            f"or --project-root={args.project_root!r}"
        )
        return 7

    asset_role = args.asset_role
    if not asset_role:
        print("ERROR: --asset-role is required for run (preflight is the no-asset-role mode)")
        return 7

    preflight = _build_preflight_report(
        project_root=project_root,
        asset_role=asset_role,
        style_manifest_override=args.style_manifest,
        native_callable=args.native_callable,
        native_inline=args.native_inline,
        asset_role_required=True,
    )

    if args.write_decision:
        write_preflight_decision(preflight, project_root)

    sel = preflight["selected_source"]
    if sel == "license_blocked":
        print("REFUSED: license_blocked. Create bonsai_license_ack.json first.")
        return 2
    if sel == "scope_blocked":
        print("REFUSED: scope_blocked. asset_role out of Bonsai allowed_scopes.")
        return 3
    if sel == "blocked_host_capability":
        print("REFUSED: blocked_host_capability.")
        print("Reasons:", preflight["gates"]["host"]["block_reasons"])
        return 4

    # sel is now one of the runnable channels
    if sel not in ("bonsai_4b_ternary", "bonsai_4b_binary"):
        print(
            f"NOTE: selected_source={sel}; this circuit only drives Bonsai. "
            "For other channels use imagegen_tool.py generate directly."
        )
        return 0

    profile_arg = "bonsai-4b-binary" if sel == "bonsai_4b_binary" else "bonsai-4b-ternary"

    # Dispatch to imagegen_tool.py bonsai generate (the Ring 2 command).
    run_id = uuid.uuid4().hex[:12]
    raw_dir = project_root / "data" / "raw_ai" / run_id
    ensure_dirs(raw_dir)
    tool_args = [
        "--json",
        "bonsai",
        "generate",
        "--profile", profile_arg,
        "--asset-role", asset_role,
        "--prompt", args.prompt or "",
        "--output-dir", str(raw_dir),
        "--width", str(args.width or 1024),
        "--height", str(args.height or 1024),
    ]
    if args.negative:
        tool_args += ["--negative", args.negative]
    if args.seed is not None:
        tool_args += ["--seed", str(args.seed)]
    if args.dry_run:
        tool_args += ["--dry-run"]

    rc, out, err = run_imagegen_tool(tool_args)
    if rc != 0:
        print(f"imagegen_tool.py bonsai generate exited with rc={rc}")
        print("stdout:", out[:2000])
        print("stderr:", err[:2000])
        return 6

    if args.dry_run:
        if args.json:
            print(out)
        else:
            print("[dry-run] Bonsai dispatch plan printed by imagegen_tool.py above.")
        return 0

    try:
        result = json.loads(out.strip().splitlines()[-1])
    except Exception:
        try:
            result = json.loads(out)
        except Exception:
            print("ERROR: could not parse Bonsai generate output as JSON")
            print(out[:2000])
            return 7

    if not result.get("ok"):
        print(f"imagegen_tool.py bonsai generate returned ok=false: {result}")
        return 6

    raw_output = Path(REPO_ROOT / result["output_path"])
    pack_path = Path(REPO_ROOT / result["prompt_pack_path"])
    lineage_id = f"lineage_{run_id}"

    if not args.dry_run:
        try:
            dest_png, lineage_path = promote_to_source_art(
                raw_output=raw_output,
                project_root=project_root,
                asset_role=asset_role,
                lineage_id=lineage_id,
                preflight=preflight,
                pack_path=pack_path,
            )
        except Exception as e:
            print(f"ERROR: could not promote raw output to source_art/: {e}")
            return 7
    else:
        dest_png = None
        lineage_path = None

    summary = {
        "run_id": run_id,
        "timestamp": now_iso(),
        "project_root": str(project_root.relative_to(REPO_ROOT)).replace("\\", "/"),
        "asset_role": asset_role,
        "selected_source": sel,
        "raw_output_path": str(raw_output.relative_to(REPO_ROOT)).replace("\\", "/")
        if raw_output.exists()
        else "",
        "prompt_pack_path": str(pack_path.relative_to(REPO_ROOT)).replace("\\", "/")
        if pack_path.exists()
        else "",
        "source_art_path": str(dest_png.relative_to(REPO_ROOT)).replace("\\", "/")
        if dest_png and dest_png.exists()
        else "",
        "lineage_path": str(lineage_path.relative_to(REPO_ROOT)).replace("\\", "/")
        if lineage_path
        else "",
        "initial_status": "source_candidate",
        "promoted_to_res": False,
        "next_action": (
            "human_or_skill_pipeline: art-translation-to-vdp "
            "+ megadrive-pixel-strict-rules + visual-excellence-standards "
            "+ contact sheet + BlastEm screenshot before any res/ promotion"
        ),
    }

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"OK  raw_output={summary['raw_output_path']}")
        print(f"OK  prompt_pack={summary['prompt_pack_path']}")
        print(f"OK  source_art={summary['source_art_path']}  (status=source_candidate)")
        print(f"OK  lineage={summary['lineage_path']}")
        print(f"BLOCKED: res/ promotion. Next: {summary['next_action']}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="imagegen_circuit.py — Ring 1 of MegaDrive_DEV image stack"
    )
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pf = sub.add_parser(
        "preflight",
        help="Run preflight only (license + host + scope + style_manifest lookup)",
    )
    p_pf.add_argument("--json", action="store_true")
    p_pf.add_argument("--project", default=None)
    p_pf.add_argument("--project-root", default=None)
    p_pf.add_argument("--asset-role", default=None)
    p_pf.add_argument("--style-manifest", default=None)
    p_pf.add_argument(
        "--native-callable",
        type=parse_bool_auto,
        default=None,
    )
    p_pf.add_argument(
        "--native-inline",
        type=parse_bool_auto,
        default=None,
    )
    p_pf.add_argument(
        "--write-decision",
        action="store_true",
        help="Also persist the decision to <project>/out/logs/generation_channel_decision.json",
    )
    p_pf.set_defaults(func=cmd_preflight)

    p_run = sub.add_parser(
        "run",
        help="Preflight + dispatch + persist (never writes under res/)",
    )
    p_run.add_argument("--json", action="store_true")
    p_run.add_argument("--project", default=None)
    p_run.add_argument("--project-root", default=None)
    p_run.add_argument(
        "--asset-role",
        required=True,
        choices=BONSAI_ALLOWED_SCOPES,
        help="MUST be one of the Bonsai allowed_scopes",
    )
    p_run.add_argument(
        "--style-manifest", default=None, help="Override path to master_style_manifest.json"
    )
    p_run.add_argument(
        "--native-callable",
        type=parse_bool_auto,
        default=None,
    )
    p_run.add_argument(
        "--native-inline",
        type=parse_bool_auto,
        default=None,
    )
    p_run.add_argument("--prompt", default="")
    p_run.add_argument("--negative", default="")
    p_run.add_argument("--seed", type=int, default=None)
    p_run.add_argument("--width", type=int, default=1024)
    p_run.add_argument("--height", type=int, default=1024)
    p_run.add_argument(
        "--profile",
        default="bonsai_4b_ternary",
        choices=["bonsai_4b_ternary", "bonsai_4b_binary"],
    )
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument(
        "--write-decision",
        action="store_true",
        help="Also persist the preflight decision to out/logs/",
    )
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    rc = args.func(args)
    sys.exit(rc)


if __name__ == "__main__":
    main()
