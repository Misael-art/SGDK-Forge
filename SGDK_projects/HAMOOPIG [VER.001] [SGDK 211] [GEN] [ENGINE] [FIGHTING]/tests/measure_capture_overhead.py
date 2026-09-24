#!/usr/bin/env python3
"""Measure the existing BlastEm capture route with and without video recording."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import struct
import subprocess as sp
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "tests" / "capture_visual_ko.py"


def phase_metrics(session: Path | None) -> dict:
    if not session:
        return {}
    path = session / "phase_clock.json"
    if not path.is_file():
        return {"error": "phase_clock_missing"}
    clock = json.loads(path.read_text(encoding="utf-8"))
    def delta(start: str, end: str):
        if start not in clock or end not in clock:
            return None
        return round((clock[end]["monotonic_ns"] - clock[start]["monotonic_ns"]) / 1_000_000.0, 3)
    return {
        "boot_ms": delta("process_start", "window_ready"),
        "capture_ms": delta("capture_start", "capture_end"),
        "finalization_ms": delta("finalization_start", "finalization_end"),
        "total_ms": delta("process_start", "finalization_end"),
        "clock_path": str(path),
    }


def cadence_from_session(session: Path | None) -> tuple[dict | None, str | None]:
    if not session:
        return None, None
    sram = session / "userdata" / "blastem" / "rom" / "save.sram"
    if not sram.is_file():
        return None, None
    raw = sram.read_bytes()
    offset = raw.find(b"HCAD")
    if offset < 0 or len(raw) < offset + 40:
        return None, None
    schema, size = struct.unpack_from(">HH", raw, offset + 4)
    if schema != 1 or size != 40:
        return None, None
    fields = (
        "video_frames", "logic_ticks", "zero_tick_frames", "one_tick_frames",
        "two_tick_frames", "max_ticks_per_frame", "presentation_commits",
        "presentation_without_logic", "fight_video_frames", "fight_logic_ticks",
        "fight_presentation_commits", "fight_zero_tick_frames", "last_logic_ticks",
        "last_scene", "region_hz", "timing_profile",
    )
    values = struct.unpack_from(">16H", raw, offset + 8)
    report = dict(zip(fields, values))
    report["schema"] = schema
    report["cadence_invariant"] = (
        report["video_frames"] == report["presentation_commits"] and
        report["logic_ticks"] == report["one_tick_frames"] + 2 * report["two_tick_frames"])
    report["fight_cadence_invariant"] = (
        report["fight_video_frames"] == report["fight_presentation_commits"] and
        report["fight_logic_ticks"] <= report["logic_ticks"])
    return report, "save.sram"


def compare_cadence(baseline: dict, captured: dict) -> dict:
    fields = ("video_frames", "logic_ticks", "presentation_commits", "zero_tick_frames",
              "fight_video_frames", "fight_logic_ticks", "fight_presentation_commits",
              "fight_zero_tick_frames")
    delta = {field: captured[field] - baseline[field] for field in fields}
    return {"status": "equal" if all(value == 0 for value in delta.values()) else "different",
            "baseline": {field: baseline[field] for field in fields},
            "capture": {field: captured[field] for field in fields},
            "delta_capture_minus_baseline": delta,
            "claim_limit": "HCAD logic/presentation comparison; not perceptual motion or sustained FPS"}


def cadence_is_comparable(probe: dict | None) -> bool:
    """Require persisted runtime telemetry before admitting an overhead pair."""
    return bool(probe and probe.get("cadence_invariant") and
                probe.get("fight_cadence_invariant") and
                probe.get("zero_tick_frames") == 0 and
                probe.get("fight_video_frames", 0) > 0)


def run_case(name: str, no_video: bool, wait: int, rom: Path | None = None) -> dict:
    command = [sys.executable, str(CAPTURE), "--probe-short", "--probe-combat",
               f"--probe-wait={wait}", "--p1=ryo", "--p2fighter=musgo"]
    if rom is not None:
        command.extend(("--rom", str(rom)))
    if no_video:
        command.append("--no-video")
    started = time.monotonic_ns()
    result = sp.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    elapsed_ms = (time.monotonic_ns() - started) / 1_000_000.0
    session = None
    for line in result.stdout.splitlines():
        if line.startswith("session="):
            session = Path(line.split("=", 1)[1].strip())
    manifest = {}
    if session and (session / "manifest.json").is_file():
        manifest = json.loads((session / "manifest.json").read_text(encoding="utf-8"))
    cadence_probe = manifest.get("cadence_probe")
    cadence_source = "manifest.cadence_probe" if cadence_probe else None
    if not cadence_probe:
        cadence_probe, cadence_source = cadence_from_session(session)
    return {
        "name": name,
        "no_video": no_video,
        "command": command,
        "returncode": result.returncode,
        "elapsed_wall_ms": round(elapsed_ms, 3),
        "session": str(session) if session else None,
        "rom_sha256": manifest.get("rom_sha256"),
        "video_capture_enabled": manifest.get("video_capture_enabled"),
        "window_title": manifest.get("title"),
        "cadence_probe": cadence_probe,
        "cadence_probe_source": cadence_source,
        "phase_metrics": phase_metrics(session),
        "stdout_tail": result.stdout[-1000:],
        "stderr_tail": result.stderr[-1000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--wait", type=int, default=8)
    parser.add_argument("--run", action="store_true", help="execute repeated BlastEm sessions")
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--minimum-successful-pairs", type=int, default=2)
    parser.add_argument("--rom", type=Path,
                        help="explicit ROM snapshot to pass to the existing capture route")
    args = parser.parse_args()
    if not args.run:
        report = {"status": "not_run", "required_command": "--run"}
    else:
        cases = []
        pairs = []
        rejected_pairs = []
        for repetition in range(1, max(1, args.repetitions) + 1):
            baseline = run_case(f"without_video_capture_{repetition:02d}", True, args.wait, args.rom)
            captured = run_case(f"with_video_capture_{repetition:02d}", False, args.wait, args.rom)
            cases.extend((baseline, captured))
            same_rom = baseline["rom_sha256"] and baseline["rom_sha256"] == captured["rom_sha256"]
            if same_rom and baseline["returncode"] == 0 and captured["returncode"] == 0:
                pair = {"repetition": repetition, "without_video": baseline, "with_video": captured}
                if cadence_is_comparable(baseline.get("cadence_probe")) and cadence_is_comparable(captured.get("cadence_probe")):
                    pair["cadence_comparison"] = compare_cadence(baseline["cadence_probe"], captured["cadence_probe"])
                    pairs.append(pair)
                else:
                    pair["cadence_comparison"] = {"status": "unsupported", "reason": "persisted HCAD/fight window missing or invalid in one or both paired sessions"}
                    rejected_pairs.append(pair)
        phase_names = ("boot_ms", "capture_ms", "finalization_ms", "total_ms")
        phase_overhead = {name: {"baseline_median_ms": None, "capture_median_ms": None, "delta_median_ms": None}
                          for name in phase_names}
        for name in phase_names:
            baseline_values = [p["without_video"]["phase_metrics"].get(name) for p in pairs
                               if p["without_video"].get("phase_metrics", {}).get(name) is not None]
            capture_values = [p["with_video"]["phase_metrics"].get(name) for p in pairs
                              if p["with_video"].get("phase_metrics", {}).get(name) is not None]
            deltas = [p["with_video"]["phase_metrics"][name] - p["without_video"]["phase_metrics"][name]
                      for p in pairs if p["with_video"].get("phase_metrics", {}).get(name) is not None
                      and p["without_video"].get("phase_metrics", {}).get(name) is not None]
            if baseline_values: phase_overhead[name]["baseline_median_ms"] = round(statistics.median(baseline_values), 3)
            if capture_values: phase_overhead[name]["capture_median_ms"] = round(statistics.median(capture_values), 3)
            if deltas: phase_overhead[name]["delta_median_ms"] = round(statistics.median(deltas), 3)
        cadence_complete = bool(pairs) and all(pair.get("cadence_comparison", {}).get("status") in ("equal", "different") for pair in pairs)
        case_rom_hashes = [case.get("rom_sha256") for case in cases
                           if isinstance(case.get("rom_sha256"), str) and case.get("rom_sha256")]
        report = {
            "schema_version": "1.0.0",
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "tool_name": "measure_capture_overhead",
            "project_root": str(ROOT),
            "cases": cases,
            "successful_pairs": pairs,
            "rejected_pairs": rejected_pairs,
            # Rejected pairs remain evidence, but must not turn a same-ROM
            # assertion false merely because their HCAD was unusable. Pair
            # sufficiency is enforced separately by ``paired_success_count``
            # and ``status`` below.
            "same_rom_sha256": bool(case_rom_hashes) and len(case_rom_hashes) == len(cases) and len(set(case_rom_hashes)) == 1,
            "observed_overhead": {
                "phase_medians": phase_overhead,
                "paired_success_count": len(pairs),
                "repetitions_requested": args.repetitions,
                "cadence_telemetry_complete": cadence_complete,
                "interpretation": "paired phase overhead; boot, capture and finalization are separate; not game FPS or logic cadence",
            },
            "status": "measured" if len(pairs) >= args.minimum_successful_pairs and cadence_complete else "needs_review",
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] in ("measured", "not_run") else 2


if __name__ == "__main__":
    raise SystemExit(main())
