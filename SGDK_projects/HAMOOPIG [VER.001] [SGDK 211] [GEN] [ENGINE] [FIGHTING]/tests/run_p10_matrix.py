#!/usr/bin/env python3
"""Run fresh, ROM-bound P10 probe cases without inferring unrun coverage.

The probe-short route proves boot, title/select transition, stage selection and
runtime telemetry. It intentionally marks visual/audio review pending; it is
not a substitute for the full sensorial playtest required by P10.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "doc/engine/p10_qa_matrix.json"
HARNESS = ROOT / "tests/capture_visual_ko.py"
REPORT = ROOT / "out/logs/p10_matrix_runner_report.json"


def refresh_statuses(data: dict) -> None:
    data["statuses"] = {
        status: sum(case["status"] == status for case in data["cases"])
        for status in ("not_run", "passed", "failed", "pending_visual_review")
    }


def write_report(data: dict, rom_sha: str, selection_only: bool) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "schema_version": "1.0.0",
        "task": "P10",
        "rom_sha256": rom_sha,
        "mode": "selection_only" if selection_only else "probe_short",
        "required_cases": data["required_cases"],
        "statuses": data["statuses"],
        "cases": [
            {"id": case["id"], "status": case["status"],
             "runtime_status": case.get("runtime_status"),
             "bundle": case.get("bundle"),
             "hprb_report": case.get("probe_report") or case.get("hprb_report")}
            for case in data["cases"]
        ],
        "claim_limit": "selection/probe evidence only; visual, audio and full gameplay review remain pending",
    }, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command_for(case: dict, selection_only: bool, probe_wait: int) -> list[str]:
    command = [
        sys.executable, str(HARNESS),
        f"--p1={case['p1']}", f"--p2fighter={case['p2']}",
    ]
    if case["stage"] == "stage2_swamp_dock":
        command.append("--stage2")
    else:
        # The runtime starts on BGB2.  SHOWDOWN is the explicit C-toggle route;
        # omitting it silently records BGB2 under a SHOWDOWN case.
        command.append("--showdown")
    if case["region"] == "PAL":
        command.append("--pal")
    if selection_only:
        command.append("--select-only")
    else:
        command.extend(["--probe-short", "--probe-combat", f"--probe-wait={probe_wait}"])
    return command


def run_case(case: dict, rom_sha: str, selection_only: bool, probe_wait: int, timeout: int) -> dict:
    process = subprocess.Popen(
        command_for(case, selection_only, probe_wait),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(process.args, timeout, output=stdout, stderr=stderr)
    completed = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    session = None
    for line in completed.stdout.splitlines():
        if line.startswith("session="):
            session = Path(line.split("=", 1)[1].strip())
    manifest = (session / "manifest.json") if session else None
    if completed.returncode != 0 or not manifest or not manifest.is_file():
        tail = (completed.stdout + "\n" + completed.stderr).strip()[-1200:]
        case.update({
            "status": "failed",
            "runtime_status": "failed",
            "rom_sha256": rom_sha,
            "bundle": str(session.relative_to(ROOT)) + "/" if session and session.is_relative_to(ROOT) else None,
            "notes": "fresh harness failed: " + tail,
        })
        return case
    data = json.loads(manifest.read_text(encoding="utf-8"))
    probe_report = None
    if not selection_only:
        sram = session / "userdata/blastem/rom/save.sram"
        if sram.is_file():
            probe_report = session / "hprb_probe_report.json"
            decoded = subprocess.run(
                [sys.executable, str(ROOT / "tests/analyze_hprb_probe.py"),
                 str(sram), "--rom", str(session / "rom.bin"),
                 "--out", str(probe_report)],
                cwd=ROOT, capture_output=True, text=True,
            )
            if decoded.returncode != 0:
                case.update({
                    "status": "failed",
                    "runtime_status": "hprb_decode_failed",
                    "rom_sha256": rom_sha,
                    "bundle": str(session.relative_to(ROOT)) + "/",
                    "notes": "probe manifest exists but HPRB decode failed: " + decoded.stderr[-800:],
                })
                return case
        else:
            case.update({
                "status": "failed",
                "runtime_status": "hprb_missing",
                "rom_sha256": rom_sha,
                "bundle": str(session.relative_to(ROOT)) + "/",
                "notes": "probe manifest exists but SRAM HPRB block is missing",
            })
            return case
    expected_stage = "BGB2" if case["stage"] == "stage2_swamp_dock" else "SHOWDOWN"
    expected_region = "E" if case["region"] == "PAL" else "U"
    checks = {
        "rom_sha256": data.get("rom_sha256") == rom_sha,
        "requested_p1": data.get("requested_p1") == case["p1"],
        "requested_p2": data.get("requested_p2") == case["p2"],
        "stage": data.get("stage") == expected_stage,
        "region": data.get("region_requested") == expected_region,
    }
    bundle = str(session.relative_to(ROOT)) + "/"
    if not all(checks.values()):
        case.update({
            "status": "failed",
            "runtime_status": "manifest_mismatch",
            "rom_sha256": data.get("rom_sha256"),
            "bundle": bundle,
            "notes": "manifest mismatch: " + json.dumps(checks, sort_keys=True),
        })
        return case
    case.update({
        "status": "pending_visual_review",
        "runtime_status": "selection_passed" if selection_only else "probe_passed",
        "rom_sha256": rom_sha,
        "bundle": bundle,
        "probe_report": str(probe_report.relative_to(ROOT)) if probe_report else None,
        "hprb_report": str(probe_report.relative_to(ROOT)) if probe_report else case.get("hprb_report"),
        "notes": (
            "fresh selection framebuffer bound to the current ROM; gameplay, "
            "visual and audio review remain pending"
            if selection_only else
            "fresh probe reached the selected route; HPRB/runtime evidence is "
            "not a gameplay or sensorial approval"
        ),
    })
    return case


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="maximum new cases; 0 means all")
    parser.add_argument("--include-observed", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--case-id", action="append", help="run only this case id (repeatable)")
    parser.add_argument("--selection-only", action="store_true")
    parser.add_argument("--probe-wait", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    if args.retry_failed:
        for case in data["cases"]:
            if case["status"] == "failed":
                case["status"] = "not_run"
                case["runtime_status"] = "not_run"
                case["rom_sha256"] = None
                case["bundle"] = None
                case["notes"] = "retry requested after a previous harness/tooling failure"
        refresh_statuses(data)
    rom = ROOT / "out/rom.bin"
    rom_sha = sha256(rom)
    refresh_statuses(data)
    write_report(data, rom_sha, args.selection_only)
    candidates = [
        case for case in data["cases"]
        if (args.include_observed or case["status"] == "not_run")
        and (not args.case_id or case["id"] in set(args.case_id))
    ]
    if args.limit > 0:
        candidates = candidates[:args.limit]
    for index, case in enumerate(candidates, 1):
        print(f"[{index}/{len(candidates)}] {case['id']}", flush=True)
        try:
            run_case(case, rom_sha, args.selection_only, max(1, args.probe_wait), args.timeout)
        except subprocess.TimeoutExpired as exc:
            case.update({
                "status": "failed",
                "runtime_status": "timeout",
                "rom_sha256": rom_sha,
                "notes": f"harness timeout after {args.timeout}s: {exc}",
            })
        refresh_statuses(data)
        MATRIX.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        write_report(data, rom_sha, args.selection_only)
        print(json.dumps({"id": case["id"], "status": case["status"], "runtime_status": case.get("runtime_status"), "bundle": case.get("bundle")}), flush=True)
    print(json.dumps(data["statuses"], sort_keys=True))
    return 0 if all(case["status"] != "failed" for case in candidates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
