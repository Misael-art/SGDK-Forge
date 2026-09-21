#!/usr/bin/env python3
"""Run scene regression through the host-selected BlastEm route.

The legacy PowerShell runner owns a Win32 automation implementation.  This
runner keeps the regression report schema but delegates capture to the same
explicit host selector used by scene closeout, so Linux never imports or
launches the Win32/Forms path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "sgdk_wrapper"))
from select_blastem_capture_route import host_context, select_route  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--manifest-path")
    parser.add_argument("--scene-id")
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--reuse-evidence", action="store_true")
    parser.add_argument("--warn-only", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scene_status_row(scene: dict, evidence_dir: Path, capture: dict) -> dict:
    return {
        "scene_key": scene.get("scene_key", scene.get("scene_id")),
        "scene_id": scene.get("scene_id"),
        "expected_app_scene_id": scene.get("expected_app_scene_id"),
        "status": capture["scene_status"],
        "captures": [{
            "mode": "host_selected",
            "status": capture["capture_status"],
            "expected_scene_id": scene.get("expected_app_scene_id"),
            "captured_scene_id": capture.get("captured_scene_id"),
            "screenshot": str(evidence_dir / "screenshot.png") if (evidence_dir / "screenshot.png").is_file() else None,
            "save_sram": str(evidence_dir / "save.sram") if (evidence_dir / "save.sram").is_file() else None,
            "visual_vdp_dump": str(evidence_dir / "visual_vdp_dump.bin") if (evidence_dir / "visual_vdp_dump.bin").is_file() else None,
            "bundle_json": str(evidence_dir / "evidence_manifest.json") if (evidence_dir / "evidence_manifest.json").is_file() else None,
            "readiness_ok": capture.get("readiness_ok"),
            "ready_heartbeat_ok": capture.get("ready_heartbeat_ok"),
            "scene_match": capture.get("scene_match"),
            "failure_reason": capture.get("failure_reason"),
        }],
    }


def copy_baseline(evidence_dir: Path, baseline_dir: Path) -> None:
    baseline_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "screenshot.png",
        "save.sram",
        "visual_vdp_dump.bin",
        "runtime_metrics.json",
        "evidence_manifest.json",
        "session_runtime.json",
    ):
        source = evidence_dir / name
        if source.is_file():
            shutil.copy2(source, baseline_dir / name)


def run_capture(project: Path, scene: dict, output_root: Path, route_index: int) -> dict:
    boot_mode = str(scene.get("boot_mode", "unsupported"))
    expected = scene.get("expected_app_scene_id")
    capture = {
        "scene_status": "failed",
        "capture_status": "failed",
        "captured_scene_id": None,
        "scene_match": None,
        "readiness_ok": None,
        "ready_heartbeat_ok": None,
        "failure_reason": None,
        "route_report": None,
    }
    if boot_mode not in {"direct_boot", "sram_bootstrap"} or expected is None:
        capture["failure_reason"] = f"host regression bootstrap unsupported: boot_mode={boot_mode}"
        return capture

    output_base = output_root / "sessions"
    route_report_path = project / "out" / "logs" / f"scene_regression_capture_route_{route_index:02d}.json"
    args = SimpleNamespace(
        repo_root=str(ROOT),
        project_root=str(project),
        target_scene=int(expected),
        output_base=str(output_base),
        powershell_command="powershell.exe",
        warmup_seconds=str(scene.get("capture_warmup_seconds", 20)),
        burst_delay=str(scene.get("capture_burst_delay", 1.0)),
        burst_count=str(scene.get("capture_burst_count", 12)),
        burst_interval=str(scene.get("capture_burst_interval", 0.10)),
    )
    route = select_route(args, host_context())
    route_report_path.parent.mkdir(parents=True, exist_ok=True)
    route_report_path.write_text(json.dumps(route, indent=2) + "\n", encoding="utf-8")
    capture["route_report"] = str(route_report_path)
    if route["status"] != "selected":
        capture["failure_reason"] = "capture route blocked: " + ",".join(route["blockers"])
        return capture

    command = [str(route["command"]), *[str(value) for value in route["arguments"]]]
    for index, value in enumerate(command):
        if value == "--canonical-root" and index + 1 < len(command):
            command[index + 1] = str(output_root)
            break
    output_root.mkdir(parents=True, exist_ok=True)
    protected_logs = {}
    for name in ("emulator_session.json", "blastem_evidence.json", "runtime_metrics.json"):
        path = project / "out" / "logs" / name
        if path.is_file():
            protected_logs[name] = (path.read_bytes(), path.stat().st_atime_ns, path.stat().st_mtime_ns)
        else:
            protected_logs[name] = None
    result = subprocess.run(command, cwd=str(ROOT), text=True, capture_output=True, check=False)
    # The Linux capture script publishes project-level logs for closeout. A
    # per-scene regression capture must not replace the canonical session
    # selected for the project, or claim reconciliation will see mixed runs.
    for name, snapshot in protected_logs.items():
        path = project / "out" / "logs" / name
        if snapshot is None:
            if path.is_file():
                path.unlink()
        else:
            payload, access_ns, modify_ns = snapshot
            path.write_bytes(payload)
            os.utime(path, ns=(access_ns, modify_ns))
    (output_root / "host_capture.stdout.log").write_text(result.stdout, encoding="utf-8")
    (output_root / "host_capture.stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        capture["failure_reason"] = f"capture command exit={result.returncode}"
        return capture

    metrics_path = output_root / "runtime_metrics.json"
    metrics = load_json(metrics_path) if metrics_path.is_file() else {}
    captured_scene = metrics.get("scene_id")
    if captured_scene is None and isinstance(metrics.get("vlab"), dict):
        captured_scene = metrics["vlab"].get("scene_id")
    capture["captured_scene_id"] = captured_scene
    capture["scene_match"] = None if expected is None or captured_scene is None else int(captured_scene) == int(expected)
    capture["readiness_ok"] = True if (output_root / "evidence_manifest.json").is_file() else False
    capture["ready_heartbeat_ok"] = capture["readiness_ok"]
    required = [(output_root / "screenshot.png").is_file(), (output_root / "save.sram").is_file()]
    if not all(required):
        capture["failure_reason"] = "required screenshot/SRAM artifact missing"
        return capture
    if capture["scene_match"] is False:
        capture["failure_reason"] = f"runtime scene mismatch expected={expected} captured={captured_scene}"
        return capture
    capture["capture_status"] = "ok"
    capture["scene_status"] = "captured"
    return capture


def reuse_capture(scene: dict, evidence_dir: Path) -> dict:
    """Re-evaluate an already sealed scene bundle without launching BlastEm."""
    expected = scene.get("expected_app_scene_id")
    capture = {
        "scene_status": "failed",
        "capture_status": "failed",
        "captured_scene_id": None,
        "scene_match": None,
        "readiness_ok": False,
        "ready_heartbeat_ok": False,
        "failure_reason": None,
        "route_report": None,
    }
    metrics_path = evidence_dir / "runtime_metrics.json"
    manifest_path = evidence_dir / "evidence_manifest.json"
    if not manifest_path.is_file() or not metrics_path.is_file():
        capture["failure_reason"] = "sealed evidence manifest/runtime metrics missing"
        return capture
    metrics = load_json(metrics_path)
    captured = metrics.get("scene_id")
    if captured is None and isinstance(metrics.get("vlab"), dict):
        captured = metrics["vlab"].get("scene_id")
    capture["captured_scene_id"] = captured
    capture["scene_match"] = None if expected is None or captured is None else int(captured) == int(expected)
    capture["readiness_ok"] = True
    capture["ready_heartbeat_ok"] = True
    if not (evidence_dir / "screenshot.png").is_file() or not (evidence_dir / "save.sram").is_file():
        capture["failure_reason"] = "sealed evidence screenshot/SRAM missing"
    elif capture["scene_match"] is False:
        capture["failure_reason"] = f"sealed evidence scene mismatch expected={expected} captured={captured}"
    else:
        capture["capture_status"] = "ok"
        capture["scene_status"] = "captured"
    return capture


def compare_baseline(scene: dict, evidence_dir: Path, baseline_dir: Path) -> tuple[str, str]:
    artifact_names = {"screenshot": "screenshot.png", "sram": "save.sram", "vdp_dump": "visual_vdp_dump.bin"}
    requested = scene.get("comparison_artifacts") or ["screenshot"]
    differences = []
    for label in requested:
        name = artifact_names.get(str(label), str(label))
        current = evidence_dir / name
        baseline = baseline_dir / name
        if not current.is_file() or not baseline.is_file():
            differences.append(f"{name}:missing")
            continue
        if sha256(current) != sha256(baseline):
            differences.append(f"{name}:hash_mismatch")
    if differences:
        return "failed", "Baseline mismatch: " + ", ".join(differences)
    return "passed", "Matches baseline by artifact SHA-256"


def main() -> int:
    args = parse_args()
    project = Path(args.project_root).resolve()
    manifest_path = Path(args.manifest_path).resolve() if args.manifest_path else project / "doc" / "scene-regression.json"
    report_path = project / "out" / "logs" / "scene_regression_report.json"
    matrix_path = project / "out" / "logs" / "scene_regression_matrix.json"
    rom_path = project / "out" / "rom.bin"
    manifest = load_json(manifest_path)
    scenes = manifest.get("scenes", [])
    if args.scene_id:
        scenes = [scene for scene in scenes if scene.get("scene_id") == args.scene_id]
    current_rom = sha256(rom_path) if rom_path.is_file() else "MISSING"
    evidence_root = project / "out" / "evidence" / "scenes_host"
    rows = []
    results = []
    for route_index, scene in enumerate(scenes, 1):
        scene_id = str(scene.get("scene_id"))
        evidence_dir = evidence_root / scene_id
        baseline_rel = str(scene.get("baseline_root", f"doc/baselines/{scene_id}")).replace("\\", "/")
        baseline_dir = project / baseline_rel
        capture = reuse_capture(scene, evidence_dir) if args.reuse_evidence else run_capture(project, scene, evidence_dir, route_index)
        if capture["scene_status"] == "captured":
            if args.update_baseline:
                copy_baseline(evidence_dir, baseline_dir)
                result_status = "passed"
                reason = "Baseline updated"
            elif not baseline_dir.is_dir() or not any(baseline_dir.iterdir()):
                result_status = "missing"
                reason = f"No baseline found at: {baseline_dir}"
            else:
                result_status, reason = compare_baseline(scene, evidence_dir, baseline_dir)
        else:
            result_status = "unsupported" if "unsupported" in str(capture.get("failure_reason")) else "error"
            reason = capture.get("failure_reason")
        capture["failure_reason"] = reason
        rows.append(scene_status_row(scene, evidence_dir, capture))
        results.append({
            "scene_id": scene_id,
            "scene_key": scene.get("scene_key", scene_id),
            "status": result_status,
            "current_rom_sha256": current_rom,
            "evidence_path": str(evidence_dir),
            "baseline_path": str(baseline_dir),
            "failure_reason": reason,
            "capture_status": capture["capture_status"],
            "captured_app_scene_id": capture.get("captured_scene_id"),
            "expected_app_scene_id": scene.get("expected_app_scene_id"),
            "scene_match": capture.get("scene_match"),
            "route_report": capture.get("route_report"),
            "artifacts": [name for name in ("screenshot.png", "save.sram", "visual_vdp_dump.bin") if (evidence_dir / name).is_file()],
        })

    failed = [result["scene_id"] for result in results if result["status"] not in {"passed"}]
    report = {
        "schema_version": "1.0.0",
        "tool_name": "run_scene_regression_host",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rom_sha256": current_rom,
        "host_capture_route": "selected_per_scene",
        "scenes_total": len(results),
        "scenes_passed": sum(result["status"] == "passed" for result in results),
        "scenes_failed": sum(result["status"] in {"failed", "error", "unsupported"} for result in results),
        "scenes_errors": sum(result["status"] == "error" for result in results),
        "scenes": rows,
        "results": results,
        "summary": {"scene_count": len(results), "failed_scene_keys": failed, "all_captured": not failed},
        "status": "passed" if not failed else ("warn" if args.warn_only else "error"),
        "failure_reason": "; ".join(result["failure_reason"] for result in results if result.get("failure_reason")),
        "claim_limit": "Regression proves only scenes captured by the selected host route and compared to an explicit baseline.",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    matrix = {
        "schema_version": "1.0.0",
        "tool_name": "run_scene_regression_host",
        "generated_at": report["generated_at"],
        "rom_sha256": current_rom,
        "matrix": {result["scene_id"]: result for result in results},
    }
    matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "scenes": len(results), "failed": failed}))
    return 0 if not failed or args.warn_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
