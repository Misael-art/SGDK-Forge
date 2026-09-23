#!/usr/bin/env python3
"""Hash-bound audiovisual capture review for SGDK evidence.

This tool extends the existing BlastEm/capture/audio paths.  It never rewrites
the master media, never CFR-normalizes input, and never turns a screenshot,
metadata or signal metric into a perceptual approval.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess as sp
import sys
import wave
from pathlib import Path
from typing import Any

TOOL_VERSION = "2.6.0"
SCHEMA_VERSION = "2.3.0"
AXES = ("artifact_identity", "media_temporal_integrity", "av_sync",
        "game_cadence", "event_observed", "visual_legibility", "visual_quality",
        "motion_quality", "audio_quality", "coverage")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def command_json(command: list[str]) -> dict[str, Any]:
    result = sp.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"command_failed:{' '.join(command)}:{result.stderr[-400:]}")
    return json.loads(result.stdout)


def preflight() -> dict[str, Any]:
    commands = {name: shutil.which(name) for name in ("ffmpeg", "ffprobe", "ffplay", "pactl")}
    modules: dict[str, bool] = {}
    for name in ("PIL", "numpy", "soundfile", "cv2"):
        try:
            __import__(name)
            modules[name] = True
        except Exception:
            modules[name] = False
    capabilities = {
        "video_metadata_and_pts": bool(commands["ffprobe"]),
        "lossless_frame_query_passthrough": bool(commands["ffmpeg"]),
        "event_player": bool(commands["ffplay"]),
        "audio_signal_metrics": bool(commands["ffprobe"]),
        "isolated_blastem_audio_route": bool(commands["pactl"]),
        "direct_agent_auditory_perception": False,
        "direct_agent_video_playback_perception": False,
    }
    blockers = [f"missing_command:{name}" for name, value in commands.items()
                if name in ("ffmpeg", "ffprobe") and not value]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "tool_name": "audiovisual_review",
        "tool_version": TOOL_VERSION,
        "commands": commands,
        "python_modules": modules,
        "capabilities": capabilities,
        "perception_policy": {
            "image_sequences_are_limited_temporal_evidence": True,
            "audio_metrics_are_not_audition": True,
            "metadata_is_not_review": True,
            "human_or_capable_reviewer_required_for_temporal_approval": True,
            "human_or_capable_listener_required_for_audio_approval": True,
        },
        "status": "blocked" if blockers else "ready_with_limits",
        "blockers": blockers,
    }


def file_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": os.path.relpath(path, root).replace(os.sep, "/"),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def freeze(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    out = Path(args.out).resolve()
    rom = Path(args.rom).resolve() if args.rom else project / "out" / "rom.bin"
    route = Path(args.route).resolve() if args.route else project / "out" / "logs" / "blastem_capture_route_report.json"
    freeze_dir = out / "freeze"
    freeze_dir.mkdir(parents=True, exist_ok=True)
    copied_rom = freeze_dir / "rom.bin"
    shutil.copy2(rom, copied_rom)
    files = [rom]
    if route.is_file():
        files.append(route)
    for candidate in (project / "tests" / "capture_visual_ko.py",
                      project / "tests" / "blastem_qa.cfg",
                      project / "tests" / "analyze_hcad_cadence.py"):
        if candidate.is_file():
            files.append(candidate)
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "tool_name": "audiovisual_review",
        "tool_version": TOOL_VERSION,
        "stage": "V0_freeze",
        "project_root": str(project),
        "rom": file_record(rom, project),
        "frozen_rom": file_record(copied_rom, out),
        "configuration": file_record(route, project) if route.is_file() else None,
        "inputs": [file_record(path, project) for path in files],
        "claims": {
            "rom_identity_frozen": True,
            "capture_route_frozen": route.is_file(),
            "quality_approval": False,
        },
    }
    write_json(out / "freeze_manifest.json", report)
    print(json.dumps(report, indent=2))
    return 0


def parse_capture_log(path: Path | None) -> dict[str, Any]:
    if not path or not path.is_file():
        return {"present": False, "drop_count": None, "dup_count": None, "matches": []}
    text = path.read_text(encoding="utf-8", errors="replace")
    matches = []
    for match in re.finditer(r"frame=\s*(\d+).*?dup=(\d+)\s+drop=(\d+)", text):
        matches.append({"frame": int(match.group(1)), "dup": int(match.group(2)),
                        "drop": int(match.group(3))})
    return {
        "present": True,
        "drop_count": max((item["drop"] for item in matches), default=None),
        "dup_count": max((item["dup"] for item in matches), default=None),
        "matches": matches,
    }


def probe_video(path: Path, capture_log: Path | None, region_hz: int) -> dict[str, Any]:
    probe = command_json([
        "ffprobe", "-v", "error", "-count_frames",
        "-show_entries", "format=duration,size:stream=index,codec_name,width,height,avg_frame_rate,r_frame_rate,time_base,start_time,duration,nb_frames,nb_read_frames",
        "-of", "json", str(path)])
    frames_json = command_json([
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time,pts_time,pkt_duration_time,pict_type",
        "-of", "json", str(path)])
    stream = next((item for item in probe.get("streams", []) if item.get("codec_type", "video") == "video"),
                  (probe.get("streams") or [{}])[0])
    frames = []
    invalid = []
    previous = None
    for index, frame in enumerate(frames_json.get("frames", [])):
        raw_pts = frame.get("best_effort_timestamp_time", frame.get("pts_time"))
        try:
            pts = float(raw_pts)
        except (TypeError, ValueError):
            invalid.append({"frame_index": index, "reason": "missing_or_invalid_pts"})
            continue
        reason = None
        if previous is not None and pts <= previous:
            reason = "non_monotonic_or_duplicate_pts"
        record = {
            "frame_index": index,
            "pts_seconds": pts,
            "pkt_duration_seconds": float(frame.get("pkt_duration_time", 0) or 0),
            "coded_picture_number": None,
            "pict_type": frame.get("pict_type"),
            "eligible_for_temporal_claim": reason is None,
        }
        if reason:
            record["excluded_reason"] = reason
            invalid.append(record)
        frames.append(record)
        previous = pts
    expected = 1.0 / float(region_hz)
    gaps = []
    for before, after in zip(frames, frames[1:]):
        interval = after["pts_seconds"] - before["pts_seconds"]
        if interval > expected * 1.5:
            gaps.append({
                "before_frame_index": before["frame_index"],
                "after_frame_index": after["frame_index"],
                "before_pts_seconds": before["pts_seconds"],
                "after_pts_seconds": after["pts_seconds"],
                "gap_seconds": interval,
                "missing_nominal_frames": max(0, round(interval / expected) - 1),
                "claim_status": "excluded_from_temporal_approval",
            })
    intervals = [b["pts_seconds"] - a["pts_seconds"] for a, b in zip(frames, frames[1:])]
    log = parse_capture_log(capture_log)
    return {
        "path": str(path),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
        "stream": stream,
        "master_preserved": True,
        "frame_count_from_probe": len(frames_json.get("frames", [])),
        "frame_count_with_valid_pts": len(frames),
        "frames": frames,
        "duration_seconds": float((probe.get("format") or {}).get("duration") or 0),
        "avg_frame_rate_metadata": stream.get("avg_frame_rate"),
        "r_frame_rate_metadata": stream.get("r_frame_rate"),
        "not_game_fps": True,
        "pts_audit": {
            "expected_region_hz": region_hz,
            "expected_interval_seconds": expected,
            "first_pts_seconds": frames[0]["pts_seconds"] if frames else None,
            "last_pts_seconds": frames[-1]["pts_seconds"] if frames else None,
            "mean_interval_seconds": sum(intervals) / len(intervals) if intervals else None,
            "max_interval_seconds": max(intervals) if intervals else None,
            "non_monotonic_count": sum(1 for item in invalid if "non_monotonic" in item.get("excluded_reason", "")),
            "invalid_pts_count": sum(1 for item in invalid if item.get("reason") == "missing_or_invalid_pts"),
            "gaps": gaps,
            "eligible_frame_count": sum(1 for item in frames if item["eligible_for_temporal_claim"]),
            "excluded_frames": invalid,
        },
        "encoder_log": log,
    }


def audio_metrics(path: Path) -> dict[str, Any]:
    report: dict[str, Any] = {"path": str(path), "sha256": sha256(path), "master_preserved": True}
    try:
        with wave.open(str(path), "rb") as source:
            report["duration_seconds"] = source.getnframes() / source.getframerate()
            report["sample_rate_hz"] = source.getframerate()
            report["channels"] = source.getnchannels()
            report["frames"] = source.getnframes()
    except (OSError, wave.Error) as exc:
        report["error"] = str(exc)
    return report


def load_audio_analyzer(project: Path):
    candidate = project / "tests" / "audit_captured_audio_signal.py"
    shared = Path(__file__).resolve().parent / "analyze_audio_capture.py"
    if shared.is_file():
        spec = importlib.util.spec_from_file_location("sgdk_audio_analyzer", shared)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    return None


def hcad_from_bundle(bundle: Path) -> dict[str, Any] | None:
    candidates = list(bundle.glob("**/save.sram"))
    for path in candidates:
        try:
            data = path.read_bytes()
            offset = data.find(b"HCAD")
            if offset < 0 or len(data) < offset + 40:
                continue
            schema, size = __import__("struct").unpack_from(">HH", data, offset + 4)
            if schema != 1 or size != 40:
                continue
            words = __import__("struct").unpack_from(">16H", data, offset + 8)
            names = ("video_frames", "logic_ticks", "zero_tick_frames", "one_tick_frames",
                     "two_tick_frames", "max_ticks_per_frame", "presentation_commits",
                     "presentation_without_logic", "fight_video_frames", "fight_logic_ticks",
                     "fight_presentation_commits", "fight_zero_tick_frames", "last_logic_ticks",
                     "last_scene", "region_hz", "timing_profile")
            result = dict(zip(names, words))
            result.update({"schema": schema, "source_report": str(path.relative_to(bundle))})
            result["cadence_invariant"] = (result["video_frames"] == result["presentation_commits"] and
                                            result["logic_ticks"] == result["one_tick_frames"] + 2 * result["two_tick_frames"])
            result["fight_cadence_invariant"] = (result["fight_video_frames"] == result["fight_presentation_commits"])
            return result
        except (OSError, ValueError, __import__("struct").error):
            continue
    return None


def game_cadence_from_manifest(manifest: dict[str, Any], rom_sha256: str | None,
                               bundle_probe: dict[str, Any] | None = None) -> dict[str, Any]:
    probe = manifest.get("cadence_probe") or bundle_probe
    required = ("video_frames", "logic_ticks", "zero_tick_frames", "one_tick_frames",
                "two_tick_frames", "max_ticks_per_frame", "presentation_commits",
                "presentation_without_logic", "fight_video_frames", "fight_logic_ticks",
                "fight_presentation_commits", "fight_zero_tick_frames", "region_hz")
    if not isinstance(probe, dict) or any(key not in probe for key in required):
        return {
            "status": "unsupported",
            "reason": "no hash-bound HCAD cadence probe in this capture manifest",
            "source": None,
            "rom_sha256": rom_sha256,
            "claim_limit": "media capture does not establish game cadence",
        }
    errors: list[str] = []
    if not isinstance(rom_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", rom_sha256):
        errors.append("rom_identity_missing_or_invalid")
    manifest_rom = manifest.get("rom_sha256")
    if manifest_rom != rom_sha256:
        errors.append("manifest_rom_sha_mismatch")
    probe_rom = probe.get("rom_sha256")
    if probe_rom is not None and probe_rom != rom_sha256:
        errors.append("probe_rom_sha_mismatch")

    values: dict[str, int] = {}
    for key in required:
        value = probe.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"{key}_must_be_integer")
            continue
        if value < 0 or value > 0xFFFF:
            errors.append(f"{key}_out_of_u16_range")
            continue
        values[key] = value

    region = values.get("region_hz")
    if region not in (50, 60):
        errors.append("region_hz_unsupported_or_invalid")
    video = values.get("video_frames", 0)
    logic = values.get("logic_ticks", 0)
    zero = values.get("zero_tick_frames", 0)
    one = values.get("one_tick_frames", 0)
    two = values.get("two_tick_frames", 0)
    presentation = values.get("presentation_commits", 0)
    without_logic = values.get("presentation_without_logic", 0)
    fight_video = values.get("fight_video_frames", 0)
    fight_logic = values.get("fight_logic_ticks", 0)
    fight_presentation = values.get("fight_presentation_commits", 0)
    fight_zero = values.get("fight_zero_tick_frames", 0)
    max_ticks = values.get("max_ticks_per_frame", 0)
    if video <= 0:
        errors.append("empty_video_window")
    if presentation <= 0:
        errors.append("empty_presentation_window")
    if video != zero + one + two:
        errors.append("video_frame_tick_class_counts_mismatch")
    if logic != one + (two * 2):
        errors.append("logic_tick_count_mismatch")
    expected_max = 2 if two else 1 if one else 0
    if max_ticks != expected_max:
        errors.append("max_ticks_per_frame_mismatch")
    if video != presentation:
        errors.append("presentation_count_mismatch")
    if without_logic != 0:
        errors.append("presentation_without_logic_nonzero")
    if fight_video > video:
        errors.append("fight_video_exceeds_video_window")
    if fight_logic > logic:
        errors.append("fight_logic_exceeds_logic_window")
    if fight_presentation > presentation:
        errors.append("fight_presentation_exceeds_presentation_window")
    if fight_presentation != fight_video:
        errors.append("fight_presentation_count_mismatch")
    if fight_zero > fight_video:
        errors.append("fight_zero_tick_exceeds_fight_window")
    if zero != 0:
        errors.append("zero_tick_frames_nonzero")
    if fight_zero != 0:
        errors.append("fight_zero_tick_frames_nonzero")
    recomputed_invariant = not errors
    recomputed_fight_invariant = (fight_video == fight_presentation and
                                  fight_logic <= logic and fight_zero == 0)
    passed = recomputed_invariant and recomputed_fight_invariant
    reported_invariant = probe.get("cadence_invariant")
    if reported_invariant is not None and not isinstance(reported_invariant, bool):
        errors.append("cadence_invariant_must_be_boolean")
        passed = False
    return {
        "status": "passed" if passed else "failed",
        "reason": "recomputed HCAD logic/presentation invariant and zero-tick count" if passed else "HCAD invariant failed",
        "source": probe.get("source_report", "manifest.cadence_probe"),
        "rom_sha256": rom_sha256,
        "probe": probe,
        "validation_errors": errors,
        "recomputed_invariants": {
            "cadence_invariant": recomputed_invariant,
            "fight_cadence_invariant": recomputed_fight_invariant,
        },
        "claim_limit": "measured game cadence for the observed HCAD window; not perceptual motion approval",
    }


def shared_runtime_anchor_from_manifest(manifest: dict[str, Any],
                                        video: dict[str, Any],
                                        audio: dict[str, Any],
                                        rom_sha256: str | None) -> dict[str, Any]:
    """Accept only a marker bound to runtime, video PTS and audio samples.

    ``capture_clock`` is intentionally not an anchor: it clocks the host-side
    recorder processes, not VDP scanout or an emulated presentation.  Keeping
    this contract in ingest makes a future instrumented capture additive while
    preserving the current honest ``needs_review`` result.
    """
    anchor = manifest.get("runtime_media_anchor")
    required = (
        "marker_id", "runtime_presentation_frame", "video_source_frame_index",
        "video_pts_seconds", "audio_sample_index", "audio_sample_rate_hz",
        "measured_event_sync_error_ms", "video_sha256", "audio_sha256",
        "rom_sha256", "evidence_refs",
    )
    base = {
        "status": "needs_review",
        "event_anchor": "not_available_without_shared_runtime_marker",
        "method": None,
        "required_fields": list(required),
        "rejected_host_clock": bool(manifest.get("capture_clock")),
        "measured_event_sync_error_ms": None,
        "evidence_refs": [],
        "reason": "runtime_media_anchor_missing_or_incomplete",
    }
    if not isinstance(anchor, dict):
        return base
    binding = manifest.get("runtime_media_anchor_binding")
    if isinstance(binding, dict) and binding.get("status") != "passed":
        base["reason"] = "runtime_media_anchor_binding_not_qualified"
        base["binding_status"] = binding.get("status")
        base["binding_errors"] = binding.get("errors", [])
        return base
    missing = [key for key in required if key not in anchor]
    refs = anchor.get("evidence_refs")
    if missing or not isinstance(refs, list) or not refs:
        base["missing_fields"] = missing
        base["reason"] = "runtime_media_anchor_missing_required_binding"
        return base
    if anchor.get("video_sha256") != video.get("sha256"):
        base["reason"] = "runtime_media_anchor_video_sha_mismatch"
        return base
    if anchor.get("audio_sha256") != audio.get("sha256"):
        base["reason"] = "runtime_media_anchor_audio_sha_mismatch"
        return base
    if anchor.get("rom_sha256") != rom_sha256:
        base["reason"] = "runtime_media_anchor_rom_sha_mismatch"
        return base
    try:
        numeric = (
            int(anchor["runtime_presentation_frame"]),
            int(anchor["video_source_frame_index"]),
            float(anchor["video_pts_seconds"]),
            int(anchor["audio_sample_index"]),
            int(anchor["audio_sample_rate_hz"]),
            float(anchor["measured_event_sync_error_ms"]),
        )
    except (TypeError, ValueError, OverflowError):
        base["reason"] = "runtime_media_anchor_numeric_binding_invalid"
        return base
    if (numeric[0] < 0 or numeric[1] < 0 or numeric[2] < 0 or numeric[3] < 0 or
            numeric[4] <= 0 or numeric[5] < 0 or not math.isfinite(numeric[2]) or
            not math.isfinite(numeric[5])):
        base["reason"] = "runtime_media_anchor_numeric_binding_invalid"
        return base
    base.update({
        "status": "passed",
        "event_anchor": "shared_runtime_marker_bound_to_video_pts_and_audio_sample",
        "method": anchor.get("method", "shared_runtime_marker"),
        "marker_id": anchor["marker_id"],
        "measured_event_sync_error_ms": numeric[5],
        "runtime_presentation_frame": numeric[0],
        "video_source_frame_index": numeric[1],
        "video_pts_seconds": numeric[2],
        "audio_sample_index": numeric[3],
        "audio_sample_rate_hz": numeric[4],
        "video_sha256": anchor["video_sha256"],
        "audio_sha256": anchor["audio_sha256"],
        "rom_sha256": anchor["rom_sha256"],
        "evidence_refs": refs,
        "reason": "shared runtime/video/audio marker and measured error present",
    })
    return base


def ingest(args: argparse.Namespace) -> int:
    bundle = Path(args.bundle).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(args.manifest).resolve() if args.manifest else bundle / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.is_file() else {}
    video = Path(args.video).resolve() if args.video else bundle / str(manifest.get("video") or "combat_window.mp4")
    audio = Path(args.audio).resolve() if args.audio else bundle / str(manifest.get("audio_wav") or "emulator_audio.wav")
    log = Path(args.video_log).resolve() if args.video_log else bundle / "video.log"
    region_hz = int(args.region_hz)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "tool_name": "audiovisual_review",
        "tool_version": TOOL_VERSION,
        "stage": "V1_ingest_integrity",
        "bundle": {"path": str(bundle), "present": bundle.is_dir(),
                   "manifest": file_record(manifest_path, bundle) if manifest_path.is_file() else None},
        "manifest": manifest,
        "artifacts": {},
        "claims": {"metadata_is_not_review": True, "video_fps_is_not_game_fps": True},
    }
    if video.is_file():
        report["artifacts"]["video"] = probe_video(video, log if log.is_file() else None, region_hz)
    else:
        report["artifacts"]["video"] = {"present": False, "path": str(video), "master_preserved": False}
    if audio.is_file():
        report["artifacts"]["audio"] = audio_metrics(audio)
        analyzer = load_audio_analyzer(Path(args.project).resolve()) if args.project else None
        if analyzer:
            try:
                report["artifacts"]["audio"]["signal_report"] = analyzer.analyze(audio, bundle.name)
            except Exception as exc:
                report["artifacts"]["audio"]["signal_report_error"] = str(exc)
    else:
        report["artifacts"]["audio"] = {"present": False, "path": str(audio), "master_preserved": False}
    video_report = report["artifacts"]["video"]
    audio_report = report["artifacts"]["audio"]
    video_duration = video_report.get("duration_seconds")
    audio_duration = audio_report.get("duration_seconds")
    rom_sha256 = sha256(bundle / "rom.bin") if (bundle / "rom.bin").is_file() else None
    anchor = shared_runtime_anchor_from_manifest(manifest, video_report, audio_report, rom_sha256)
    report["synchronization"] = {
        "video_duration_seconds": video_duration,
        "audio_duration_seconds": audio_duration,
        "duration_delta_seconds": (audio_duration - video_duration) if video_duration is not None and audio_duration is not None else None,
        "event_anchor": anchor["event_anchor"],
        "measured_event_sync_error_ms": anchor["measured_event_sync_error_ms"],
        "status": anchor["status"],
        "claim_status": anchor["status"],
        "reason": anchor["reason"],
        "anchor_contract": anchor,
    }
    report["artifact_identity"] = {
        "video": {"present": bool(video_report.get("master_preserved")),
                  "sha256": video_report.get("sha256"),
                  "master_preserved": bool(video_report.get("master_preserved"))},
        "audio": {"present": bool(audio_report.get("master_preserved")),
                  "sha256": audio_report.get("sha256"),
                  "master_preserved": bool(audio_report.get("master_preserved"))},
        "rom_identity_matches_bundle": (
            bool(manifest.get("rom_sha256")) and manifest.get("rom_sha256") == rom_sha256
        ),
        "manifest_rom_sha256": manifest.get("rom_sha256"),
        "bundle_rom_sha256": rom_sha256,
        "config_sha256_recorded": bool(manifest.get("config_sha256")),
        "status": "passed" if video_report.get("master_preserved") and
        manifest.get("rom_sha256") and manifest.get("rom_sha256") == rom_sha256 else "needs_review",
        "reason": "ROM/media hashes and master preservation only",
        "claim_name": "artifact_identity",
        "deprecated_alias": "capture_integrity",
        "claim_limit": "identity and preservation only; no temporal, sync, game-cadence or perceptual approval",
    }
    report["media_temporal_integrity"] = {
        "master_video_preserved": bool(video_report.get("master_preserved")),
        "master_audio_preserved": bool(audio_report.get("master_preserved")),
        "drop_count_from_encoder_log": video_report.get("encoder_log", {}).get("drop_count"),
        "duplicate_count_from_encoder_log": video_report.get("encoder_log", {}).get("dup_count"),
        "pts_gap_count": len(video_report.get("pts_audit", {}).get("gaps", [])),
        "non_monotonic_count": video_report.get("pts_audit", {}).get("non_monotonic_count"),
        "status": "failed" if video_report.get("encoder_log", {}).get("drop_count", 0) or
        video_report.get("pts_audit", {}).get("gaps") or
        video_report.get("pts_audit", {}).get("non_monotonic_count") else "passed",
        "reason": "media timestamp gap/drop detected; master retained" if (
            video_report.get("encoder_log", {}).get("drop_count", 0) or
            video_report.get("pts_audit", {}).get("gaps") or
            video_report.get("pts_audit", {}).get("non_monotonic_count")
        ) else "video PTS and encoder continuity passed",
        "claim_limit": "media PTS/encoder continuity only; not game logic cadence",
    }
    pts = video_report.get("pts_audit", {})
    report["media_temporal_integrity"]["pts_gaps"] = pts.get("gaps", [])
    report["game_cadence"] = game_cadence_from_manifest(manifest, manifest.get("rom_sha256"), hcad_from_bundle(bundle))
    frames_path = out / "frame_index.json"
    write_json(frames_path, {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "source_video_sha256": video_report.get("sha256"),
        "frames": video_report.get("frames", []),
        "frame_count": video_report.get("frame_count_with_valid_pts", 0),
        "note": "The master is unchanged. Frames with invalid PTS are retained in the audit and excluded from approval claims.",
    })
    ingest_path = out / "audiovisual_ingest_report.json"
    report["outputs"] = {"frame_index": str(frames_path), "ingest_report": str(ingest_path)}
    write_json(ingest_path, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def parse_roi(value: str) -> tuple[str, tuple[int, int, int, int]]:
    name, coords = value.split("=", 1)
    numbers = tuple(int(item) for item in coords.split(","))
    if len(numbers) != 4:
        raise ValueError("roi must be name=x,y,w,h")
    return name, numbers


def query_segment(pts: float | None, event_start: float, event_end: float) -> str:
    if isinstance(pts, (int, float)) and pts < event_start:
        return "pre_context"
    if isinstance(pts, (int, float)) and pts > event_end:
        return "post_context"
    return "event"


def _ffmpeg_select_expression(source_indices: list[int]) -> str:
    """Build a source-frame selector without asking ffmpeg to invent cadence.

    ``-ss`` is a seek hint and can start decoding at a nearby keyframe.  That
    is not sufficient for a hash-bound frame review because the resulting PNG
    ordinal can silently differ from the ffprobe source index.  Selecting by
    ``n`` keeps the source-frame identity explicit.  A contiguous interval is
    kept compact; sparse queries use an exact union of source indices.
    """
    if not source_indices:
        raise ValueError("source_indices must not be empty")
    ordered = sorted(set(source_indices))
    if ordered == list(range(ordered[0], ordered[-1] + 1)):
        return f"select=between(n\\,{ordered[0]}\\,{ordered[-1]})"
    terms = "+".join(f"eq(n\\,{index})" for index in ordered)
    return f"select={terms}"


def query(args: argparse.Namespace) -> int:
    report_path = Path(args.report).resolve()
    report = load_json(report_path)
    video = Path(report["artifacts"]["video"]["path"])
    event_start = float(args.start)
    event_end = float(args.end)
    pre_context = float(args.pre_context)
    post_context = float(args.post_context)
    if event_start < 0 or event_end <= event_start:
        raise ValueError("event interval must satisfy 0 <= start < end")
    if pre_context < 0 or post_context < 0:
        raise ValueError("pre/post context must be non-negative")
    start = max(0.0, event_start - pre_context)
    end = event_end + post_context
    event_id = args.event_id
    target = Path(args.out).resolve() / event_id
    target.mkdir(parents=True, exist_ok=True)
    if list(target.glob("frame_*.png")):
        raise RuntimeError("query_output_not_empty_choose_new_event_id")
    frames = [frame for frame in report["artifacts"]["video"].get("pts_audit", {}).get("gaps", [])]
    # Use ffprobe-derived PTS as the authority; the decoded images are paired
    # in order and are marked as limited evidence if ffmpeg returns a different
    # count. No CFR conversion or duplicate removal is performed.
    index_path = report.get("outputs", {}).get("frame_index")
    all_frames = []
    if index_path and Path(index_path).is_file():
        loaded = load_json(Path(index_path))
        all_frames = [item for item in loaded.get("frames", []) if "pts_seconds" in item]
    selected = [item for item in all_frames if start <= item["pts_seconds"] <= end]
    if not selected:
        # The compact report may not carry all frames; still perform the
        # extraction and expose the mismatch instead of inventing indices.
        selected = [{"frame_index": None, "pts_seconds": start}]
    duration = max(0.001, end - start)
    pattern = target / "frame_%06d.png"
    source_indices = [int(item["frame_index"]) for item in selected
                      if isinstance(item.get("frame_index"), int)]
    if not source_indices:
        raise RuntimeError("frame_query_has_no_source_indices")
    select_expression = _ffmpeg_select_expression(source_indices)
    command = ["ffmpeg", "-v", "error", "-i", str(video),
               "-vf", select_expression, "-fps_mode", "passthrough",
               "-start_number", "0", "-f", "image2", str(pattern)]
    result = sp.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"frame_query_failed:{result.stderr[-500:]}")
    images = sorted(target.glob("frame_*.png"))
    rois = dict(parse_roi(value) for value in args.roi)
    audio_path = Path(report.get("artifacts", {}).get("audio", {}).get("path", ""))
    audio_command = (["ffplay", "-autoexit", "-ss", str(start), "-t", str(duration), str(audio_path)]
                     if audio_path.is_file() else None)
    frame_records = []
    try:
        from PIL import Image
    except Exception:
        Image = None
    exact_source_binding = len(images) == len(selected)
    for image, source in zip(images, selected):
        pts = source.get("pts_seconds")
        segment = query_segment(pts, event_start, event_end)
        record = {"path": image.name, "sha256": sha256(image),
                  "frame_index": source.get("frame_index"),
                  "pts_seconds": pts,
                  "segment": segment,
                  "source_video_sha256": report["artifacts"]["video"].get("sha256"),
                  "pts_binding": ("ffprobe_source_index_exact" if exact_source_binding
                                  else "ordered_pair_unresolved_after_decoder_mismatch"),
                  "eligible_for_temporal_claim": source.get("eligible_for_temporal_claim", True)}
        if Image:
            with Image.open(image) as opened:
                for name, (x, y, width, height) in rois.items():
                    crop = opened.crop((x, y, x + width, y + height))
                    roi_path = target / f"{image.stem}_{name}.png"
                    crop.save(roi_path)
                    record.setdefault("rois", {})[name] = {"path": roi_path.name,
                        "sha256": sha256(roi_path), "x": x, "y": y, "w": width, "h": height}
        frame_records.append(record)
    # Materialize convenience clips without rewriting the masters or inventing
    # cadence. Stream copy keeps the source packets; the exact frame/PTS query
    # above remains authoritative because container clip boundaries can only be
    # nominal around keyframes.
    clips: dict[str, Any] = {
        "video": None,
        "audio": None,
        "synchronization": "not_asserted_without_shared_runtime_anchor",
        "claim_limit": "derived_context_clip_only; query_report_frames_and_source_PTS_are_authoritative",
    }
    video_clip = target / "event_video_clip.mkv"
    video_clip_command = ["ffmpeg", "-v", "error", "-i", str(video),
                          "-vf", select_expression, "-an", "-map", "0:v:0",
                          "-c:v", "ffv1", "-fps_mode", "passthrough",
                          "-frames:v", str(len(selected)), str(video_clip)]
    video_clip_result = sp.run(video_clip_command, capture_output=True, text=True, check=False)
    video_clip_probe = None
    if video_clip_result.returncode == 0 and video_clip.is_file():
        probe_result = sp.run(["ffprobe", "-v", "error", "-count_frames",
                               "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                               "-of", "json", str(video_clip)], capture_output=True, text=True, check=False)
        if probe_result.returncode == 0:
            try:
                video_clip_probe = json.loads(probe_result.stdout)
            except json.JSONDecodeError:
                video_clip_probe = None
        stream = (video_clip_probe or {}).get("streams", [{}])[0]
        frame_count = int(stream.get("nb_read_frames", -1)) if str(stream.get("nb_read_frames", "")).isdigit() else -1
        clips["video"] = {"path": video_clip.name, "sha256": sha256(video_clip),
                           "source_sha256": report["artifacts"]["video"].get("sha256"),
                           "nominal_start_seconds": start, "nominal_end_seconds": end,
                           "method": "ffmpeg_lossless_select_by_source_frame_index",
                           "source_frame_count": len(selected), "clip_frame_count": frame_count,
                           "status": "passed" if frame_count == len(selected) else "needs_review",
                           "command": video_clip_command,
                           "claim_limit": "derived_lossless_frame_clip; source query PTS remains authoritative"}
    else:
        clips["video"] = {"status": "needs_review", "method": "ffmpeg_lossless_select_by_source_frame_index",
                           "error": video_clip_result.stderr[-500:]}
    if audio_path.is_file():
        audio_clip = target / "event_audio_clip.wav"
        audio_clip_command = ["ffmpeg", "-v", "error", "-i", str(audio_path),
                              "-ss", str(start), "-t", str(duration),
                              "-map", "0:a:0", "-c:a", "copy", "-avoid_negative_ts", "disabled",
                              str(audio_clip)]
        audio_clip_result = sp.run(audio_clip_command, capture_output=True, text=True, check=False)
        if audio_clip_result.returncode == 0 and audio_clip.is_file():
            clips["audio"] = {"path": audio_clip.name, "sha256": sha256(audio_clip),
                               "source_sha256": report["artifacts"]["audio"].get("sha256"),
                               "nominal_start_seconds": start, "nominal_end_seconds": end,
                               "method": "ffmpeg_stream_copy_nominal_context_interval",
                               "command": audio_clip_command}
        else:
            clips["audio"] = {"status": "needs_review", "method": "ffmpeg_stream_copy_nominal_context_interval",
                               "error": audio_clip_result.stderr[-500:]}
    query_report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "tool_name": "audiovisual_review",
        "tool_version": TOOL_VERSION,
        "stage": "V2_query",
        "event_id": event_id,
        "source_video_sha256": report["artifacts"]["video"].get("sha256"),
        "interval": {"start_seconds": event_start, "end_seconds": event_end},
        "query_interval": {"start_seconds": start, "end_seconds": end},
        "pre_context_seconds": pre_context,
        "post_context_seconds": post_context,
        "requested_frame_count": len(selected),
        "decoded_frame_count": len(images),
        "event_frame_count": sum(record["segment"] == "event" for record in frame_records),
        "context_frame_counts": {
            "pre_context": sum(record["segment"] == "pre_context" for record in frame_records),
            "post_context": sum(record["segment"] == "post_context" for record in frame_records),
        },
        "frame_count_match": len(images) == len(selected),
        "source_frame_indices": source_indices,
        "source_frame_index_range": {"first": min(source_indices), "last": max(source_indices)},
        "extraction": {
            "method": "ffmpeg_select_by_source_frame_index",
            "filter": select_expression,
            "no_cfr": True,
            "no_interpolation": True,
            "no_duplicate_removal": True,
            "exact_source_binding": exact_source_binding,
            "claim_limit": "if frame_count_match is false, image-to-source binding is unresolved and cannot support a precise frame finding",
        },
        "frames": frame_records,
        "roi_definitions": {name: {"x": coords[0], "y": coords[1], "w": coords[2], "h": coords[3]}
                            for name, coords in rois.items()},
        "clips": clips,
        "player": {
            "video_command": (["ffplay", "-autoexit", str(target / clips["video"]["path"])]
                               if isinstance(clips.get("video"), dict) and clips["video"].get("path")
                               else ["ffplay", "-autoexit", "-ss", str(start), "-t", str(duration), str(video)]),
            "audio_command": (["ffplay", "-autoexit", str(target / clips["audio"]["path"])]
                              if isinstance(clips.get("audio"), dict) and clips["audio"].get("path")
                              else audio_command),
            "audio_note": "The WAV window uses the nominal interval only; it is not A/V synchronized without a measured shared anchor.",
        },
        "evidence_limit": "image_sequence_query_not_a_temporal_or_audio_approval",
    }
    write_json(target / "query_report.json", query_report)
    player = target / "play_event.sh"
    audio_hint = ("# Separate WAV context clip (nominal interval only; not synchronized):\n"
                  "# ffplay -autoexit '" + str(target / clips["audio"]["path"]) + "'\n"
                  if isinstance(clips.get("audio"), dict) and clips["audio"].get("path")
                  else "# No audio context clip was materialized.\n")
    video_player = (target / clips["video"]["path"]
                    if isinstance(clips.get("video"), dict) and clips["video"].get("path")
                    else video)
    player.write_text("#!/usr/bin/env bash\nset -eu\n" + audio_hint +
                      "exec ffplay -autoexit '" + str(video_player) + "'\n", encoding="utf-8")
    player.chmod(0o755)
    print(json.dumps(query_report, indent=2, ensure_ascii=False))
    return 0


def make_findings(args: argparse.Namespace) -> int:
    report = load_json(Path(args.report).resolve())
    out = Path(args.out).resolve()
    video = report["artifacts"]["video"]
    findings = []
    for number, gap in enumerate(video.get("pts_audit", {}).get("gaps", []), 1):
        findings.append({
            "id": f"capture-pts-gap-{number:02d}",
            "category": "media_temporal_integrity",
            "status": "candidate",
            "approval_status": "not_approved",
            "timestamp": {"start_seconds": gap["before_pts_seconds"], "end_seconds": gap["after_pts_seconds"]},
            "frame_context": {"before_frame_index": gap["before_frame_index"], "after_frame_index": gap["after_frame_index"],
                              "consecutive_frames_required": True},
            "media_sha256": video.get("sha256"),
            "rom_sha256": report.get("manifest", {}).get("rom_sha256"),
            "roi": {"x": 0, "y": 0, "w": video.get("stream", {}).get("width"), "h": video.get("stream", {}).get("height")},
            "confidence": 1.0,
            "hypothesis": "capture/encoder timestamp discontinuity; not a game-frame claim",
            "impact": "temporal claim cannot be released for this interval; spaced screenshots can miss the loss",
            "causal_test": "repeat same-ROM capture with passthrough timestamps, inspect encoder drop log and HCAD together",
            "runtime_context": {
                "input": None,
                "scene": report.get("manifest", {}).get("stage"),
                "combat_event": None,
                "emulated_frame": None,
                "logic_ticks": None,
                "presentation_commits": None,
                "dma": None,
                "correlation_status": "not_available_in_capture_bundle; do_not_infer_game_stall",
            },
            "evidence_refs": [str(args.report), str(report.get("outputs", {}).get("frame_index"))],
            "reviewer": "audiovisual_review_automatic_candidate",
            "method": "ffprobe_pts_audit_plus_encoder_log",
            "tools": ["ffprobe", "ffmpeg", "existing_capture_visual_ko.py"],
            "claim_limit": "candidate_only; does_not_approve_visual_temporal_or_audio_quality",
        })
    write_json(out, {"schema_version": SCHEMA_VERSION, "generated_at": now(),
                     "tool_name": "audiovisual_review", "tool_version": TOOL_VERSION,
                     "stage": "V3_findings", "findings": findings,
                     "coverage": {"unexamined_intervals": "all_intervals_without_query_or_review"},
                     "status": "candidate_only"})
    print(json.dumps({"findings": len(findings), "out": str(out)}, indent=2))
    return 0


def make_gameplay_finding(args: argparse.Namespace) -> int:
    report = load_json(Path(args.report).resolve())
    manifest = load_json(Path(args.manifest).resolve())
    query = load_json(Path(args.query).resolve())
    causal_compare = None
    causal_compare_arg = getattr(args, "causal_compare", None)
    causal_compare_path = Path(causal_compare_arg).resolve() if causal_compare_arg else None
    if causal_compare_path:
        causal_compare = load_json(causal_compare_path)
    hsem = load_json(Path(args.hsem).resolve()) if args.hsem else None
    hprb = load_json(Path(args.hprb).resolve()) if args.hprb else None
    hcad = load_json(Path(args.hcad).resolve()) if args.hcad else None
    hstr = load_json(Path(args.hstr).resolve()) if args.hstr else None
    hape = manifest.get("runtime_presentation_event")
    frames = query.get("frames", [])
    hprb_summary = None
    if hprb:
        hprb_summary = {key: hprb.get(key) for key in (
            "video_frame", "last_scene", "combat_total_events", "combat_total_hits",
            "combat_total_projectiles", "combat_total_ko", "max_dma_queued_bytes",
            "max_sprites_per_scanline", "decision")}
    hsem_summary = None
    if hsem:
        hsem_summary = {key: hsem.get(key) for key in (
            "video_frame", "samples", "last_x_p1", "last_x_p2", "last_state_p1",
            "last_state_p2", "attack_frames_p1", "fireball_frames_p1",
            "last_special_p1", "evidence_scope")}
    hstr_summary = None
    if hstr:
        records = hstr.get("records", [])
        trace_records = [record for record in records if
                         700 <= int(record.get("p1_state", 0)) <= 790 or
                         int(record.get("p1_fireball_active", 0)) != 0]
        capture_clock = manifest.get("capture_clock", {})
        video_start = capture_clock.get("video_started_monotonic_ns")
        event_capture = next((item for item in manifest.get("capture_timeline", [])
                              if item.get("capture") == "special_only_p1_try0_0.png"), None)
        alignment = {"status": "unavailable", "method": "none"}
        mapped_records = []
        if trace_records and video_start and event_capture and event_capture.get("monotonic_ns"):
            nominal_media_frame = round((event_capture["monotonic_ns"] - video_start) / 1_000_000_000 * 60.0)
            offset = int(trace_records[0]["presentation_frame"]) - nominal_media_frame
            query_first = int(frames[0].get("frame_index")) if frames else None
            query_last = int(frames[-1].get("frame_index")) if frames else None
            for record in trace_records:
                media_frame = int(record["presentation_frame"]) - offset
                if query_first is None or query_first <= media_frame <= query_last:
                    mapped = dict(record)
                    mapped["estimated_media_frame_index"] = media_frame
                    mapped_records.append(mapped)
            alignment = {
                "status": "estimated",
                "method": "monotonic_capture_timeline_to_nominal_60hz_media_frame",
                "anchor_capture": event_capture["capture"],
                "anchor_runtime_presentation_frame": trace_records[0]["presentation_frame"],
                "anchor_estimated_media_frame": nominal_media_frame,
                "runtime_minus_media_frame_offset": offset,
                "uncertainty": "host-clock/PTS mapping; not a VDP scanout timestamp",
            }
        hstr_summary = {
            "schema": hstr.get("schema"),
            "count": hstr.get("count"),
            "first_presentation_frame": hstr.get("first_presentation_frame"),
            "last_presentation_frame": hstr.get("last_presentation_frame"),
            "states": hstr.get("states"),
            "anim_frames": hstr.get("anim_frames"),
            "fireball_active_records": hstr.get("fireball_active_records"),
            "alignment": alignment,
            "records_in_query_interval": mapped_records,
            "evidence_scope": hstr.get("evidence_scope"),
        }
    cross_mode_state = None
    if isinstance(causal_compare, dict):
        runtime_context = causal_compare.get("runtime_context", {}).get("runtime_presentation_event", {})
        cross_mode_state = {
            "status": "same_runtime_state" if runtime_context.get("same_state_context") is True else "needs_review",
            "same_rom": causal_compare.get("comparison", {}).get("rom_sha256", {}).get("same") is True,
            "same_config": causal_compare.get("comparison", {}).get("config_sha256", {}).get("same") is True,
            "same_inputs": causal_compare.get("comparison", {}).get("requested_inputs", {}).get("same") is True,
            "runtime_context": runtime_context,
            "claim_limit": "same-state context across separate runs; no cross-run PTS or scanout binding",
        }
    finding = {
        "id": args.finding_id,
        "category": "gameplay_visual",
        "status": "candidate",
        "approval_status": "not_approved",
        "timestamp": query.get("interval"),
        "frame_context": {
            "first_frame_index": frames[0].get("frame_index") if frames else None,
            "last_frame_index": frames[-1].get("frame_index") if frames else None,
            "source_frame_first": frames[0].get("frame_index") if frames else None,
            "source_frame_last": frames[-1].get("frame_index") if frames else None,
            "source_query": str(Path(args.query).resolve()),
        },
        "media_sha256": report.get("artifacts", {}).get("video", {}).get("sha256"),
        "audio_sha256": report.get("artifacts", {}).get("audio", {}).get("sha256"),
        "rom_sha256": report.get("manifest", {}).get("rom_sha256"),
        "roi": query.get("roi_definitions", {}).get("gameplay") or query.get("roi_definitions", {}).get("full"),
        "confidence": float(args.confidence),
        "symptom": args.symptom,
        "hypothesis": args.hypothesis,
        "impact": args.impact,
        "causal_test": args.causal_test,
        "routing": {
            "owner": "gameplay_runtime_owner",
            "next_action": "execute_causal_test_before_code_change",
            "correction_claim": "do_not_patch_gameplay_from_image_only_candidate",
        },
        "state_correlation": {
            "scene": manifest.get("stage"),
            "input_trace": args.input_summary,
            "expected_state": args.expected_state,
            "special_sample_count": len(manifest.get("special_samples", [])),
            "hape": hape,
            "hsem": hsem_summary,
            "hprb": hprb_summary,
            "hcad": hcad,
            "hstr": hstr_summary,
            "cross_mode_capture": cross_mode_state,
            "correlation_limit": "HAPE is same-boundary runtime state context; HSTR/HSEM/HPRB remain diagnostic snapshots and do not provide video PTS, scanout timestamp or perceptual approval",
        },
        "evidence_refs": [str(Path(args.report).resolve()), str(Path(args.manifest).resolve()),
                          str(Path(args.query).resolve())] + ([str(causal_compare_path)] if causal_compare_path else []) + [str(Path(value).resolve()) for value in (args.hsem, args.hprb, args.hcad, args.hstr) if value] + [str(Path(value).resolve()) for value in args.visual_evidence],
        "visual_evidence_refs": [str(Path(value).resolve()) for value in args.visual_evidence],
        "reviewer": args.reviewer,
        "method": "hash_bound_event_query_plus_sequential_image_inspection_and_runtime_probe_decode",
        "tools": ["ffprobe", "ffmpeg", "view_image", "analyze_hape_probe.py", "analyze_hsem_probe.py", "analyze_hprb_probe.py", "analyze_hstr_probe.py", "audiovisual_review.py:causal-compare"],
        "claim_limit": "candidate gameplay finding; does not prove root cause or approve visual/motion/audio quality",
    }
    write_json(Path(args.out).resolve(), {"schema_version": SCHEMA_VERSION, "generated_at": now(),
                                          "tool_name": "audiovisual_review", "tool_version": TOOL_VERSION,
                                          "stage": "V3_findings", "status": "candidate_only",
                                          "findings": [finding]})
    print(json.dumps({"status": "candidate_only", "finding_id": args.finding_id,
                      "out": str(Path(args.out).resolve())}, indent=2))
    return 0


def _causal_frame_metrics(directory: Path, prefix: str,
                          roi: tuple[int, int, int, int]) -> dict[str, Any]:
    """Summarize paired screenshots without pretending ordinal frames are synced.

    This is deliberately a candidate generator.  A no-video run and a video
    run can execute the same input script at different wall-clock positions;
    therefore the output reports distributions and alignment limits instead
    of declaring a game defect from image differences alone.
    """
    try:
        from PIL import Image
    except Exception as exc:
        return {"status": "needs_review", "error": f"pillow_unavailable:{exc}", "frames": []}
    frames = sorted(directory.glob(f"{prefix}*.png"),
                    key=lambda path: int(path.stem.rsplit("_", 1)[-1])
                    if path.stem.rsplit("_", 1)[-1].isdigit() else path.name)
    x, y, width, height = roi
    records: list[dict[str, Any]] = []
    for path in frames:
        try:
            with Image.open(path) as opened:
                pixels = list(opened.convert("RGB").crop((x, y, x + width, y + height)).getdata())
            records.append({
                "path": str(path),
                "sha256": sha256(path),
                "frame_ordinal": int(path.stem.rsplit("_", 1)[-1])
                if path.stem.rsplit("_", 1)[-1].isdigit() else None,
                "red_candidate_pixels": sum(r > 150 and g < 115 and b < 115 for r, g, b in pixels),
                "white_candidate_pixels": sum(r > 190 and g > 190 and b > 190 for r, g, b in pixels),
            })
        except Exception as exc:
            records.append({"path": str(path), "status": "needs_review", "error": str(exc)})
    numeric_red = sorted(item["red_candidate_pixels"] for item in records
                         if isinstance(item.get("red_candidate_pixels"), int))
    numeric_white = sorted(item["white_candidate_pixels"] for item in records
                           if isinstance(item.get("white_candidate_pixels"), int))
    def distribution(values: list[int]) -> dict[str, Any]:
        if not values:
            return {"count": 0, "minimum": None, "median": None, "maximum": None}
        return {"count": len(values), "minimum": values[0],
                "median": values[len(values) // 2], "maximum": values[-1]}
    return {"status": "passed" if records and all("error" not in item for item in records) else "needs_review",
            "directory": str(directory), "frame_prefix": prefix, "frame_count": len(records),
            "roi": {"x": x, "y": y, "width": width, "height": height},
            "red_candidate_distribution": distribution(numeric_red),
            "white_candidate_distribution": distribution(numeric_white),
            "frames": records}


def _causal_hstr_summary(path: Path | None, expected_rom: str | None) -> dict[str, Any]:
    if path is None:
        return {"status": "not_provided"}
    if not path.is_file():
        return {"status": "needs_review", "path": str(path), "reason": "hstr_missing"}
    try:
        value = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "needs_review", "path": str(path), "reason": f"hstr_invalid:{exc}"}
    active = [item for item in value.get("records", [])
              if isinstance(item, dict) and int(item.get("p1_fireball_active", 0) or 0) != 0]
    return {
        "status": "context_only" if active and (not expected_rom or value.get("rom_sha256", expected_rom) == expected_rom) else "needs_review",
        "path": str(path), "sha256": sha256(path), "rom_sha256": value.get("rom_sha256", expected_rom),
        "active_record_count": len(active),
        "first_active_presentation_frame": active[0].get("presentation_frame") if active else None,
        "last_active_presentation_frame": active[-1].get("presentation_frame") if active else None,
        "claim_limit": "same-ROM runtime context; no screenshot timestamp binding unless a shared marker exists",
    }


def causal_compare(args: argparse.Namespace) -> int:
    with_manifest_path = Path(args.with_video_manifest).resolve()
    without_manifest_path = Path(args.without_video_manifest).resolve()
    with_manifest = load_json(with_manifest_path)
    without_manifest = load_json(without_manifest_path)
    with_rom = with_manifest.get("rom_sha256")
    without_rom = without_manifest.get("rom_sha256")
    comparisons = {
        "rom_sha256": {"with_video": with_rom, "without_video": without_rom,
                        "same": bool(with_rom and with_rom == without_rom)},
        "config_sha256": {"with_video": with_manifest.get("config_sha256"),
                           "without_video": without_manifest.get("config_sha256"),
                           "same": with_manifest.get("config_sha256") == without_manifest.get("config_sha256")},
        "scenario": {"with_video": with_manifest.get("scenario"),
                      "without_video": without_manifest.get("scenario"),
                      "same": with_manifest.get("scenario") == without_manifest.get("scenario")},
        "requested_inputs": {
            "with_video": [with_manifest.get("requested_p1"), with_manifest.get("requested_p2")],
            "without_video": [without_manifest.get("requested_p1"), without_manifest.get("requested_p2")],
            "same": ([with_manifest.get("requested_p1"), with_manifest.get("requested_p2")] ==
                     [without_manifest.get("requested_p1"), without_manifest.get("requested_p2")]),
        },
    }
    contract_same = all(item["same"] for item in comparisons.values())
    def hape_context(manifest: dict[str, Any]) -> dict[str, Any]:
        event = manifest.get("runtime_presentation_event")
        if not isinstance(event, dict):
            return {"status": "missing"}
        fields = ("marker_id", "scene", "logic_ticks", "gameplay_event",
                  "p1_state", "p1_anim_frame", "p1_anim_frame_total",
                  "p1_frame_time", "p1_frame_time_total", "p1_fireball_active",
                  "p1_fireball_x", "p1_fireball_y", "p1_input_bits",
                  "p1_attack_button", "p1_hit_pause", "active_sprites",
                  "used_vdp_sprites", "scanline_peak")
        return {"status": "present", **{field: event.get(field) for field in fields},
                "runtime_presentation_frame": event.get("runtime_presentation_frame"),
                "pre_sprite_dma_bytes": event.get("pre_sprite_dma_bytes"),
                "sprite_dma_delta_bytes": event.get("sprite_dma_delta_bytes")}
    hape_with = hape_context(with_manifest)
    hape_without = hape_context(without_manifest)
    comparable_hape_fields = ("scene", "logic_ticks", "gameplay_event", "p1_state",
                              "p1_anim_frame", "p1_anim_frame_total", "p1_frame_time",
                              "p1_frame_time_total", "p1_fireball_active", "p1_fireball_x",
                              "p1_fireball_y", "p1_input_bits", "p1_attack_button",
                              "p1_hit_pause", "active_sprites", "used_vdp_sprites",
                              "scanline_peak")
    hape_same_state = (hape_with.get("status") == "present" and
                       hape_without.get("status") == "present" and
                       all(hape_with.get(field) == hape_without.get(field)
                           for field in comparable_hape_fields))
    runtime_event_context = {
        "with_video": hape_with,
        "without_video": hape_without,
        "same_state_context": hape_same_state,
        "presentation_frame_delta": (hape_with.get("runtime_presentation_frame") -
                                      hape_without.get("runtime_presentation_frame")
                                      if hape_same_state else None),
        "dma_delta_capture_minus_baseline": (hape_with.get("sprite_dma_delta_bytes") -
                                              hape_without.get("sprite_dma_delta_bytes")
                                              if hape_same_state else None),
        "claim_limit": "HAPE compares game state at each run's marker boundary; presentation counters are not cross-run timestamps",
    }
    roi_values = tuple(int(value) for value in args.roi.split(","))
    if len(roi_values) != 4 or any(value < 0 for value in roi_values):
        raise ValueError("causal compare ROI must be x,y,width,height with non-negative values")
    with_frames = _causal_frame_metrics(Path(args.with_video_dir).resolve(), args.frame_prefix, roi_values)
    without_frames = _causal_frame_metrics(Path(args.without_video_dir).resolve(), args.frame_prefix, roi_values)
    query = load_json(Path(args.query).resolve()) if args.query else {}
    hstr_with = _causal_hstr_summary(Path(args.hstr_with_video).resolve() if args.hstr_with_video else None, with_rom)
    hstr_without = _causal_hstr_summary(Path(args.hstr_without_video).resolve() if args.hstr_without_video else None, without_rom)
    visual_difference = bool(
        with_frames.get("status") == "passed" and without_frames.get("status") == "passed" and
        (with_frames.get("red_candidate_distribution") != without_frames.get("red_candidate_distribution") or
         with_frames.get("white_candidate_distribution") != without_frames.get("white_candidate_distribution"))
    )
    finding = {
        "id": args.finding_id,
        "category": "capture_route_vs_gameplay",
        "status": "candidate",
        "approval_status": "not_approved",
        "timestamp": query.get("interval"),
        "frame_context": {
            "with_video_frame_ordinals": [item.get("frame_ordinal") for item in with_frames.get("frames", [])],
            "without_video_frame_ordinals": [item.get("frame_ordinal") for item in without_frames.get("frames", [])],
            "alignment": "ordinal_only; no shared screenshot/runtime timestamp",
        },
        "media_sha256": sha256(Path(args.with_video_dir).resolve() / str(with_manifest.get("video") or "combat_window.mp4"))
        if (Path(args.with_video_dir).resolve() / str(with_manifest.get("video") or "combat_window.mp4")).is_file() else None,
        "rom_sha256": with_rom,
        "roi": with_frames.get("roi"),
        "confidence": 0.7 if contract_same and visual_difference else 0.45,
        "symptom": "same-ROM special route produces different screenshot pixel distributions with and without video capture",
        "hypothesis": "capture-route timing or framebuffer acquisition changes the observed visual sequence; this is not a confirmed game root cause",
        "impact": "a spaced screenshot or recorded frame can mislead a reviewer about the special animation and hide the distinction between game output and recorder artifact",
        "causal_test": "repeat the same input route with a shared runtime marker in both modes and bind screenshots to presentation frames before changing gameplay code",
        "routing": {"owner": "capture_pipeline_owner", "next_action": "add shared marker binding to the no-video comparison; do not patch gameplay from this candidate"},
        "state_correlation": {"with_video_hstr": hstr_with, "without_video_hstr": hstr_without,
                              "runtime_presentation_event": runtime_event_context,
                              "runtime_marker": with_manifest.get("runtime_media_marker"),
                              "correlation_limit": "HAPE proves matching special state at each run's marker boundary; it does not bind the two runs to one video PTS"},
        "evidence_refs": [str(with_manifest_path), str(without_manifest_path), str(Path(args.query).resolve()) if args.query else None,
                          str(Path(args.hstr_with_video).resolve()) if args.hstr_with_video else None,
                          str(Path(args.hstr_without_video).resolve()) if args.hstr_without_video else None],
        "claim_limit": "candidate-only causal comparison; no visual, motion, audio or game-root-cause approval",
    }
    finding["evidence_refs"] = [value for value in finding["evidence_refs"] if value]
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "tool_name": "audiovisual_review",
        "tool_version": TOOL_VERSION,
        "stage": "V3_findings",
        "status": "candidate_only",
        "comparison": comparisons,
        "contract_same": contract_same,
        "visual_difference_candidate": visual_difference,
        "with_video": {"manifest": str(with_manifest_path), "frames": with_frames},
        "without_video": {"manifest": str(without_manifest_path), "frames": without_frames},
        "runtime_context": {"with_video_hstr": hstr_with, "without_video_hstr": hstr_without,
                            "runtime_presentation_event": runtime_event_context},
        "findings": [finding],
        "finding": finding,
        "claim_limit": "same-ROM capture-route comparison only; ordinal frame metrics are not runtime/PTS synchronization",
    }
    write_json(Path(args.out).resolve(), report)
    print(json.dumps({"status": report["status"], "finding_id": args.finding_id,
                      "contract_same": contract_same, "visual_difference_candidate": visual_difference,
                      "out": str(Path(args.out).resolve())}, indent=2))
    return 0


def status_item(status: str, reason: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"status": status, "reason": reason, "evidence": evidence or [],
            "approval": status == "passed"}


def _merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[list[float]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def _interval_duration(intervals: list[tuple[float, float]]) -> float:
    return sum(end - start for start, end in _merge_intervals(intervals))


def _parse_declared_interval(value: Any, total: float | None, label: str) -> tuple[float, float] | None:
    """Parse a declared unexamined interval without trusting its spelling.

    Review packets historically used strings such as ``0.000-10.200``.  Keep
    that interchange format, but normalize it before comparing it with the
    complement of the intervals actually seen.  An invalid declaration must
    not turn into complete coverage merely because it is a non-empty list.
    """
    start: Any = None
    end: Any = None
    if isinstance(value, dict):
        start = value.get("start_seconds")
        end = value.get("end_seconds")
    elif isinstance(value, str):
        match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*[-–]\s*([0-9]+(?:\.[0-9]+)?)\s*", value)
        if match:
            start, end = match.groups()
    if start is None or end is None:
        return None
    try:
        start_f = float(start)
        end_f = float(end)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(start_f) or not math.isfinite(end_f):
        return None
    if start_f < 0 or end_f <= start_f or (total is not None and end_f > total + 0.000001):
        return None
    return (start_f, end_f)


def _complement_intervals(total: float | None, observed: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if total is None or total <= 0:
        return []
    complement: list[tuple[float, float]] = []
    cursor = 0.0
    for start, end in _merge_intervals(observed):
        if start > cursor + 0.000001:
            complement.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < total - 0.000001:
        complement.append((cursor, total))
    return complement


def _same_intervals(left: list[tuple[float, float]], right: list[tuple[float, float]]) -> bool:
    left_m = _merge_intervals(left)
    right_m = _merge_intervals(right)
    if len(left_m) != len(right_m):
        return False
    return all(abs(a - c) <= 0.000001 and abs(b - d) <= 0.000001
               for (a, b), (c, d) in zip(left_m, right_m))


def _review_evidence_root(review: dict[str, Any]) -> Path | None:
    value = review.get("evidence_root")
    if not isinstance(value, str) or not value.strip():
        return None
    root = Path(value)
    if not root.is_absolute():
        manifest_dir = review.get("_manifest_dir")
        root = Path(manifest_dir) / root if isinstance(manifest_dir, str) and manifest_dir else Path.cwd() / root
    return root.resolve()


def _validate_evidence_refs(review: dict[str, Any], refs: Any, label: str,
                            errors: list[str]) -> None:
    if not isinstance(refs, list) or not refs:
        return
    root = _review_evidence_root(review)
    if root is None or not root.is_dir():
        return
    manifest_dir = review.get("_manifest_dir")
    base = Path(manifest_dir).resolve() if isinstance(manifest_dir, str) and manifest_dir else root
    for index, ref in enumerate(refs):
        if not isinstance(ref, str) or not ref.strip():
            continue
        path = Path(ref)
        resolved = path.resolve() if path.is_absolute() else (base / path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            errors.append(f"{label}_evidence_ref_{index}_outside_root")
            continue
        if not resolved.is_file():
            errors.append(f"{label}_evidence_ref_{index}_missing")


def validate_review(report: dict[str, Any], review: dict[str, Any] | None) -> dict[str, Any]:
    """Validate a reviewer packet without deciding its perceptual verdicts."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"qualified": False, "errors": ["review_manifest_missing"],
                "observed_intervals": [], "coverage": {"complete": False}}
    if not isinstance(review.get("schema_version"), str) or not re.fullmatch(r"\d+\.\d+\.\d+", review.get("schema_version", "")):
        errors.append("review_schema_version_missing_or_invalid")
    if review.get("tool_name") != "audiovisual_review":
        errors.append("review_tool_name_missing_or_invalid")
    if not isinstance(review.get("tool_version"), str) or not review.get("tool_version", "").strip():
        errors.append("review_tool_version_missing_or_invalid")
    if not isinstance(review.get("reviewer"), str) or not review.get("reviewer", "").strip():
        errors.append("reviewer_missing")
    if not isinstance(review.get("method"), str) or not review.get("method", "").strip():
        errors.append("method_missing")
    evidence_root = _review_evidence_root(review)
    if evidence_root is None:
        errors.append("evidence_root_missing_or_invalid")
    elif not evidence_root.is_dir():
        errors.append("evidence_root_not_found")
    tools_used = review.get("tools")
    if not isinstance(tools_used, list) or not tools_used or not all(isinstance(item, str) and item.strip() for item in tools_used):
        errors.append("tools_missing_or_invalid")
    capabilities = review.get("method_capabilities")
    if not isinstance(capabilities, dict):
        errors.append("method_capabilities_missing")
        capabilities = {}
    for capability in ("video_playback", "audio_audition"):
        if not isinstance(capabilities.get(capability), bool):
            errors.append(f"method_capability_{capability}_missing_or_invalid")
    source = review.get("source_media")
    if not isinstance(source, dict):
        errors.append("source_media_hashes_missing")
        source = {}
    expected_video = report.get("artifacts", {}).get("video", {}).get("sha256")
    expected_audio = report.get("artifacts", {}).get("audio", {}).get("sha256")
    expected_rom = report.get("manifest", {}).get("rom_sha256")
    if source.get("video_sha256") != expected_video:
        errors.append("video_sha256_mismatch")
    if expected_audio and source.get("audio_sha256") != expected_audio:
        errors.append("audio_sha256_mismatch")
    if source.get("rom_sha256") != expected_rom:
        errors.append("rom_sha256_mismatch")

    total = report.get("artifacts", {}).get("video", {}).get("duration_seconds")
    try:
        total = float(total)
    except (TypeError, ValueError):
        total = None
        errors.append("video_duration_missing")
    intervals_raw = review.get("observed_intervals")
    observed: list[tuple[float, float]] = []
    normalized_observed: list[dict[str, Any]] = []
    if not isinstance(intervals_raw, list) or not intervals_raw:
        errors.append("observed_intervals_missing_or_empty")
        intervals_raw = []
    for index, item in enumerate(intervals_raw):
        if not isinstance(item, dict):
            errors.append(f"observed_interval_{index}_not_object")
            continue
        try:
            start = float(item["start_seconds"])
            end = float(item["end_seconds"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"observed_interval_{index}_invalid_bounds")
            continue
        valid_bounds = start >= 0 and end > start and (total is None or end <= total)
        evidence_refs = item.get("evidence_refs")
        if not valid_bounds:
            errors.append(f"observed_interval_{index}_out_of_bounds")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            errors.append(f"observed_interval_{index}_evidence_missing")
        _validate_evidence_refs(review, evidence_refs, f"observed_interval_{index}", errors)
        if item.get("actually_seen") is not True:
            errors.append(f"observed_interval_{index}_not_confirmed_seen")
        if valid_bounds:
            observed.append((start, end))
            normalized_observed.append({"event_id": item.get("event_id"), "start_seconds": start,
                                        "end_seconds": end, "evidence_refs": evidence_refs})

    coverage = review.get("coverage")
    if not isinstance(coverage, dict):
        errors.append("coverage_missing")
        coverage = {}
    unexamined = coverage.get("unexamined_intervals")
    if not isinstance(unexamined, list):
        errors.append("unexamined_intervals_must_be_list")
        unexamined = None
    observed_union = _merge_intervals(observed)
    observed_duration = _interval_duration(observed_union)
    complete = bool(total is not None and observed_union and observed_union[0][0] <= 0.000001 and
                    observed_union[-1][1] >= total - 0.000001 and
                    sum(1 for left, right in zip(observed_union, observed_union[1:]) if right[0] > left[1] + 0.000001) == 0)
    declared_unexamined: list[tuple[float, float]] = []
    if isinstance(unexamined, list):
        for index, item in enumerate(unexamined):
            parsed = _parse_declared_interval(item, total, f"unexamined_intervals_{index}")
            if parsed is None:
                errors.append(f"unexamined_interval_{index}_invalid")
            else:
                declared_unexamined.append(parsed)
        expected_unexamined = _complement_intervals(total, observed_union)
        if not _same_intervals(declared_unexamined, expected_unexamined):
            errors.append("unexamined_intervals_do_not_match_observed_complement")
    if unexamined == [] and not complete:
        errors.append("empty_unexamined_but_observed_intervals_do_not_cover_video")
    declared_ratio = coverage.get("coverage_ratio")
    computed_ratio = (observed_duration / total) if total and total > 0 else 0.0
    if declared_ratio is not None:
        try:
            if abs(float(declared_ratio) - computed_ratio) > 0.001:
                errors.append("coverage_ratio_mismatch")
        except (TypeError, ValueError):
            errors.append("coverage_ratio_invalid")

    verdicts = review.get("verdicts")
    if not isinstance(verdicts, dict):
        errors.append("verdicts_missing")
        verdicts = {}
    for axis in ("event_observed", "visual_legibility", "visual_quality",
                 "motion_quality", "audio_quality"):
        verdict = verdicts.get(axis)
        if not isinstance(verdict, dict) or verdict.get("status") not in ("passed", "failed", "needs_review"):
            errors.append(f"verdict_{axis}_missing_or_invalid")
        elif not isinstance(verdict.get("evidence_refs"), list) or not verdict.get("evidence_refs"):
            errors.append(f"verdict_{axis}_evidence_missing")
        else:
            _validate_evidence_refs(review, verdict.get("evidence_refs"), f"verdict_{axis}", errors)
            if axis == "visual_quality" and verdict.get("status") == "passed":
                criteria = verdict.get("criteria_checked")
                comparison = verdict.get("reference_comparison")
                if not isinstance(criteria, list) or not criteria or not all(isinstance(item, str) and item.strip() for item in criteria):
                    errors.append("verdict_visual_quality_criteria_missing")
                if not isinstance(comparison, dict) or comparison.get("status") != "passed":
                    errors.append("verdict_visual_quality_reference_comparison_missing")
                elif not isinstance(comparison.get("evidence_refs"), list) or not comparison.get("evidence_refs"):
                    errors.append("verdict_visual_quality_reference_evidence_missing")
                else:
                    _validate_evidence_refs(review, comparison.get("evidence_refs"), "verdict_visual_quality_reference", errors)
    qualified = not errors
    return {
        "qualified": qualified,
        "errors": errors,
        "reviewer": review.get("reviewer"),
        "method": review.get("method"),
        "evidence_root": str(evidence_root) if evidence_root else None,
        "tools": tools_used,
        "claim_scope": review.get("claim_scope", "unspecified"),
        "capabilities": capabilities,
        "source_media": source,
        "observed_intervals": normalized_observed,
        "observed_union": [{"start_seconds": start, "end_seconds": end} for start, end in observed_union],
        "coverage": {"total_seconds": total, "observed_seconds": observed_duration,
                     "coverage_ratio": computed_ratio, "complete": complete,
                     "unexamined_intervals": unexamined,
                     "unexamined_union": [{"start_seconds": start, "end_seconds": end}
                                          for start, end in _merge_intervals(declared_unexamined)]},
        "verdicts": verdicts,
    }


def evaluate_gate(report: dict[str, Any], review: dict[str, Any] | None = None) -> dict[str, Any]:
    video = report.get("artifacts", {}).get("video", {})
    audio = report.get("artifacts", {}).get("audio", {})
    identity = report.get("artifact_identity", {})
    temporal = report.get("media_temporal_integrity", {})
    sync = report.get("synchronization", {})
    game_cadence = report.get("game_cadence", {})
    review_check = validate_review(report, review)
    verdicts = review_check.get("verdicts", {})
    capabilities = review_check.get("capabilities", {})
    axes: dict[str, Any] = {}
    identity_ok = identity.get("status") == "passed"
    axes["artifact_identity"] = status_item(
        "passed" if identity_ok else "needs_review",
        "ROM/media hashes and master preservation only" if identity_ok else "missing or mismatched ROM/media identity")
    temporal_ok = temporal.get("status") == "passed"
    axes["media_temporal_integrity"] = status_item(
        "passed" if temporal_ok else "failed",
        "PTS monotonic and no encoder drop/gap observed" if temporal_ok else "media timestamp gap/drop detected; master retained")
    sync_ok = sync.get("status") == "passed" and sync.get("measured_event_sync_error_ms") is not None
    axes["av_sync"] = status_item(
        "passed" if sync_ok else "needs_review",
        "shared event anchor and measured sync error present" if sync_ok else "duration delta is not event synchronization")
    axes["game_cadence"] = status_item(
        game_cadence.get("status", "unsupported"),
        game_cadence.get("reason", "game cadence unavailable"))

    event_verdict = verdicts.get("event_observed", {}).get("status")
    event_allowed = (review_check["qualified"] and event_verdict == "passed" and
                      bool(verdicts.get("event_observed", {}).get("evidence_refs")))
    axes["event_observed"] = status_item(
        "passed" if event_allowed else ("failed" if event_verdict == "failed" else "needs_review"),
        "qualified review observed the declared event interval" if event_allowed else
        "qualified event observation/evidence not present")

    legibility_verdict = verdicts.get("visual_legibility", {}).get("status")
    legibility_allowed = (review_check["qualified"] and legibility_verdict == "passed" and
                          bool(verdicts.get("visual_legibility", {}).get("evidence_refs")))
    axes["visual_legibility"] = status_item(
        "passed" if legibility_allowed else ("failed" if legibility_verdict == "failed" else "needs_review"),
        "qualified bounded visual-legibility review with evidence" if legibility_allowed else
        "qualified visual-legibility verdict/evidence not present")

    visual_verdict = verdicts.get("visual_quality", {}).get("status")
    visual_packet = verdicts.get("visual_quality", {})
    quality_criteria = visual_packet.get("criteria_checked")
    quality_reference = visual_packet.get("reference_comparison")
    quality_allowed = (review_check["qualified"] and visual_verdict == "passed" and
                       bool(visual_packet.get("evidence_refs")) and
                       isinstance(quality_criteria, list) and bool(quality_criteria) and
                       isinstance(quality_reference, dict) and quality_reference.get("status") == "passed" and
                       bool(quality_reference.get("evidence_refs")))
    axes["visual_quality"] = status_item(
        "passed" if quality_allowed else ("failed" if visual_verdict == "failed" else "needs_review"),
        "qualified artistic criteria and reference comparison with evidence" if quality_allowed else
        "observation/legibility does not substitute for artistic quality criteria and reference comparison")

    motion_verdict = verdicts.get("motion_quality", {}).get("status")
    motion_allowed = (review_check["qualified"] and motion_verdict == "passed" and
                      capabilities.get("video_playback") is True and temporal_ok and
                      game_cadence.get("status") == "passed" and
                      bool(verdicts.get("motion_quality", {}).get("evidence_refs")))
    axes["motion_quality"] = status_item(
        "passed" if motion_allowed else ("failed" if motion_verdict == "failed" else "needs_review"),
        "qualified playback review with media and game cadence support" if motion_allowed else "playback-qualified motion verdict or cadence support missing")

    audio_verdict = verdicts.get("audio_quality", {}).get("status")
    audio_allowed = (review_check["qualified"] and audio_verdict == "passed" and
                     capabilities.get("audio_audition") is True and sync_ok and
                     bool(audio.get("master_preserved")) and
                     bool(verdicts.get("audio_quality", {}).get("evidence_refs")))
    axes["audio_quality"] = status_item(
        "passed" if audio_allowed else ("failed" if audio_verdict == "failed" else "needs_review"),
        "qualified audition, sync and hash-bound audio evidence" if audio_allowed else "audition-qualified audio verdict, sync or evidence missing")

    coverage_complete = review_check["qualified"] and review_check.get("coverage", {}).get("complete") is True
    axes["coverage"] = status_item(
        "passed" if coverage_complete else "needs_review",
        "computed observed intervals cover the complete media" if coverage_complete else
        "coverage is incomplete, invalid or lacks a qualified reviewer")
    claims = {
        "artifact_identity": "released" if axes["artifact_identity"]["status"] == "passed" else "blocked",
        "media_temporal_integrity": "released" if axes["media_temporal_integrity"]["status"] == "passed" else "blocked",
        "av_sync": "released" if axes["av_sync"]["status"] == "passed" else "blocked",
        "game_cadence": "released" if axes["game_cadence"]["status"] == "passed" else "blocked",
        "event_observed": "released" if axes["event_observed"]["status"] == "passed" else "blocked",
        "visual_legibility": "released" if axes["visual_legibility"]["status"] == "passed" else "blocked",
        "visual_approval": "released" if axes["visual_quality"]["status"] == "passed" else "blocked",
        "temporal_motion_approval": "released" if axes["motion_quality"]["status"] == "passed" else "blocked",
        "audio_approval": "released" if axes["audio_quality"]["status"] == "passed" else "blocked",
        "coverage_complete": "released" if axes["coverage"]["status"] == "passed" else "blocked",
    }
    claim_scopes = {
        "artifact_identity": "ROM/media hash identity and master preservation only",
        "media_temporal_integrity": "video PTS and encoder continuity only",
        "av_sync": "shared runtime/video/audio marker only",
        "game_cadence": game_cadence.get("claim_limit", "hash-bound HCAD window only"),
        "event_observed": ("declared event was observed over the qualified interval"
                           if axes["event_observed"]["status"] == "passed" else "none"),
        "visual_legibility": ("bounded visual-legibility review over the qualified interval"
                               if axes["visual_legibility"]["status"] == "passed" else "none"),
        "visual_approval": (review_check.get("claim_scope", "unspecified")
                             if axes["visual_quality"]["status"] == "passed"
                             else "none"),
        "temporal_motion_approval": ("continuous playback over the qualified review scope"
                                     if axes["motion_quality"]["status"] == "passed" else "none"),
        "audio_approval": ("audition and measured sync over the qualified review scope"
                           if axes["audio_quality"]["status"] == "passed" else "none"),
        "coverage_complete": ("complete media review by qualified reviewer"
                              if axes["coverage"]["status"] == "passed" else "none"),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "tool_name": "audiovisual_review",
        "tool_version": TOOL_VERSION,
        "stage": "V4_gate",
        "status": ("passed" if all(value == "released" for value in claims.values()) else
                   "blocked" if any(value == "blocked" for value in claims.values()) else "needs_review"),
        "axes": axes,
        "claims": claims,
        "claim_scopes": claim_scopes,
        "review_validation": review_check,
        "non_substitution_rule": "No axis result substitutes for another axis.",
    }


def gate(args: argparse.Namespace) -> int:
    report = load_json(Path(args.report).resolve())
    review = None
    if args.review:
        review_path = Path(args.review).resolve()
        review = load_json(review_path)
        review["_manifest_dir"] = str(review_path.parent)
    result = evaluate_gate(report, review)
    write_json(Path(args.out).resolve(), result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "needs_review" else 2


def end_to_end(args: argparse.Namespace) -> int:
    """Consume V0-V4 outputs and emit one hash-bound V5 execution receipt.

    The receipt distinguishes pipeline execution from claims.  A complete
    execution can therefore be ``status=blocked`` when the captured media has
    PTS gaps or the reviewer only had image capability; that is the intended
    result, not a failed attempt hidden behind a green pipeline status.
    """
    paths = {
        "freeze": Path(args.freeze).resolve(),
        "capture_manifest": Path(args.capture_manifest).resolve(),
        "ingest": Path(args.ingest).resolve(),
        "query": Path(args.query).resolve(),
        "finding": Path(args.finding).resolve(),
        "review": Path(args.review).resolve(),
        "gate": Path(args.gate).resolve(),
    }
    overhead_arg = getattr(args, "overhead", None)
    if overhead_arg:
        paths["overhead"] = Path(overhead_arg).resolve()
    errors: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}
    for name, path in paths.items():
        if not path.is_file():
            errors.append(f"{name}_missing")
            continue
        try:
            loaded[name] = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{name}_invalid:{exc}")

    stages = {
        "freeze": "V0_freeze",
        "ingest": "V1_ingest_integrity",
        "query": "V2_query",
        "finding": "V3_findings",
        "gate": "V4_gate",
    }
    steps: dict[str, Any] = {}
    for name, expected in stages.items():
        actual = loaded.get(name, {}).get("stage")
        passed = actual == expected
        steps[name] = {"status": "passed" if passed else "failed",
                       "expected_stage": expected, "actual_stage": actual,
                       "path": str(paths[name])}
        if not passed:
            errors.append(f"{name}_stage_mismatch")

    freeze = loaded.get("freeze", {})
    capture = loaded.get("capture_manifest", {})
    ingest_report = loaded.get("ingest", {})
    query_report = loaded.get("query", {})
    finding_report = loaded.get("finding", {})
    review = loaded.get("review", {})
    gate_report = loaded.get("gate", {})
    video = ingest_report.get("artifacts", {}).get("video", {})
    audio = ingest_report.get("artifacts", {}).get("audio", {})
    ingest_manifest = ingest_report.get("manifest", {})
    capture_bundle = paths["capture_manifest"].parent

    # A historical capture manifest used ``capture_integrity=released`` for
    # identity/preservation.  That name is intentionally rejected here: it
    # can be misread as temporal or audiovisual approval.  The canonical
    # identity axis is artifact_identity and has no authority over the other
    # axes.
    legacy_capture_claim = capture.get("capture_integrity")
    legacy_semantics_ok = legacy_capture_claim is None
    steps["capture_identity_semantics"] = {
        "status": "passed" if legacy_semantics_ok else "failed",
        "claim_name": "artifact_identity",
        "deprecated_alias": "capture_integrity",
        "legacy_value_present": not legacy_semantics_ok,
        "reason": "capture manifest does not expose a broad capture_integrity claim" if legacy_semantics_ok
        else "legacy capture_integrity claim cannot be consumed as audiovisual approval",
        "path": str(paths["capture_manifest"]),
    }
    if not legacy_semantics_ok:
        errors.append("deprecated_capture_integrity_claim_present")

    # Verify the actual capture files named by the capture manifest, not merely
    # the strings in downstream reports.
    capture_video_path = capture_bundle / str(capture.get("video") or "combat_window.mp4")
    audio_declared = capture.get("audio_wav")
    audio_not_captured = audio_declared in (None, "") and str(capture.get("audio", "")).startswith("not_captured")
    capture_audio_path = (capture_bundle / str(audio_declared)
                          if isinstance(audio_declared, str) and audio_declared.strip()
                          else None)
    capture_artifacts: dict[str, Any] = {}
    for kind, path in (("video", capture_video_path), ("audio", capture_audio_path)):
        if path is None and kind == "audio" and audio_not_captured:
            capture_artifacts[kind] = {"present": False, "optional": True,
                                       "reason": "capture_manifest_declares_audio_not_captured"}
            continue
        if path is not None and path.is_file():
            capture_artifacts[kind] = {"path": str(path), "sha256": sha256(path),
                                       "size_bytes": path.stat().st_size}
        else:
            capture_artifacts[kind] = {"path": str(path) if path is not None else None, "present": False}
            errors.append(f"capture_{kind}_missing")
    capture_rom_path = capture_bundle / "rom.bin"
    if capture_rom_path.is_file():
        capture_artifacts["rom"] = {"path": str(capture_rom_path), "sha256": sha256(capture_rom_path),
                                     "size_bytes": capture_rom_path.stat().st_size}
    else:
        capture_artifacts["rom"] = {"path": str(capture_rom_path), "present": False}
        errors.append("capture_rom_missing")

    hashes = {
        "rom": {
            "freeze": freeze.get("rom", {}).get("sha256"),
            "frozen_copy": freeze.get("frozen_rom", {}).get("sha256"),
            "capture_manifest": capture.get("rom_sha256"),
            "capture_file": capture_artifacts.get("rom", {}).get("sha256"),
            "ingest_manifest": ingest_manifest.get("rom_sha256"),
            "review": review.get("source_media", {}).get("rom_sha256"),
        },
        "video": {
            "capture_file": capture_artifacts.get("video", {}).get("sha256"),
            "ingest": video.get("sha256"),
            "query": query_report.get("source_video_sha256"),
            "review": review.get("source_media", {}).get("video_sha256"),
            "finding": (finding_report.get("findings") or [{}])[0].get("media_sha256"),
        },
        "audio": {
            "capture_file": capture_artifacts.get("audio", {}).get("sha256"),
            "ingest": audio.get("sha256"),
            "review": review.get("source_media", {}).get("audio_sha256"),
            "finding": (finding_report.get("findings") or [{}])[0].get("audio_sha256"),
        },
    }
    hash_checks: dict[str, Any] = {}
    for kind, values in hashes.items():
        present = [value for value in values.values() if isinstance(value, str) and value]
        audio_absent = kind == "audio" and not present and audio_not_captured
        same = bool(present) and len(set(present)) == 1 and len(present) == len(values)
        hash_checks[kind] = {"status": "not_present" if audio_absent else ("passed" if same else "failed"),
                             "values": values, "claim_limit": "audio axis remains blocked when not captured"
                             if audio_absent else None}
        if not same and not audio_absent:
            errors.append(f"{kind}_hash_chain_mismatch_or_missing")

    query_ok = bool(query_report.get("frame_count_match") is True and
                    query_report.get("extraction", {}).get("exact_source_binding") is True and
                    query_report.get("extraction", {}).get("no_cfr") is True and
                    query_report.get("extraction", {}).get("no_interpolation") is True and
                    query_report.get("extraction", {}).get("no_duplicate_removal") is True)
    steps["query_integrity"] = {
        "status": "passed" if query_ok else "failed",
        "requested_frame_count": query_report.get("requested_frame_count"),
        "decoded_frame_count": query_report.get("decoded_frame_count"),
        "frame_count_match": query_report.get("frame_count_match"),
        "source_frame_index_range": query_report.get("source_frame_index_range"),
        "path": str(paths["query"]),
    }
    if not query_ok:
        errors.append("query_not_exact_or_frame_count_mismatch")

    findings = finding_report.get("findings")
    candidate_ok = bool(isinstance(findings, list) and findings and any(
        item.get("status") == "candidate" and item.get("approval_status") == "not_approved"
        and item.get("timestamp") and item.get("confidence") is not None
        and item.get("hypothesis") and item.get("impact") and item.get("causal_test")
        and item.get("routing", {}).get("owner") and item.get("routing", {}).get("next_action")
        for item in findings if isinstance(item, dict)))
    steps["finding_integrity"] = {
        "status": "passed" if candidate_ok else "failed",
        "candidate_count": len(findings) if isinstance(findings, list) else 0,
        "path": str(paths["finding"]),
    }
    if not candidate_ok:
        errors.append("finding_missing_required_candidate_context")

    candidate = next((item for item in findings if isinstance(item, dict) and
                      item.get("status") == "candidate"), {}) if isinstance(findings, list) else {}
    frame_context = candidate.get("frame_context", {}) if isinstance(candidate, dict) else {}
    source_query_value = frame_context.get("source_query") if isinstance(frame_context, dict) else None
    source_query_path = None
    if isinstance(source_query_value, str) and source_query_value.strip():
        source_query_path = Path(source_query_value)
        if not source_query_path.is_absolute():
            source_query_path = paths["finding"].parent / source_query_path
        source_query_path = source_query_path.resolve()
    query_range = query_report.get("source_frame_index_range", {})
    query_interval = query_report.get("interval", {})
    extracted_interval = query_report.get("query_interval") or query_interval
    first_frame = frame_context.get("source_frame_first") if isinstance(frame_context, dict) else None
    last_frame = frame_context.get("source_frame_last") if isinstance(frame_context, dict) else None
    finding_timestamp = candidate.get("timestamp", {}) if isinstance(candidate, dict) else {}
    binding_ok = bool(source_query_path and source_query_path == paths["query"].resolve() and
                      source_query_path.is_file())
    if isinstance(first_frame, int) and isinstance(last_frame, int):
        binding_ok = binding_ok and first_frame <= last_frame and first_frame >= int(query_range.get("first", first_frame)) and last_frame <= int(query_range.get("last", last_frame))
    else:
        binding_ok = False
    try:
        timestamp_ok = (float(finding_timestamp["start_seconds"]) >= float(extracted_interval["start_seconds"])
                        and float(finding_timestamp["end_seconds"]) <= float(extracted_interval["end_seconds"])
                        and float(finding_timestamp["end_seconds"]) > float(finding_timestamp["start_seconds"]))
    except (KeyError, TypeError, ValueError):
        timestamp_ok = False
    binding_ok = binding_ok and timestamp_ok
    steps["finding_query_binding"] = {
        "status": "passed" if binding_ok else "failed",
        "finding_source_query": str(source_query_path) if source_query_path else source_query_value,
        "query_path": str(paths["query"]),
        "source_frame_first": first_frame,
        "source_frame_last": last_frame,
        "query_source_frame_index_range": query_range,
        "finding_timestamp": finding_timestamp,
        "query_interval": query_interval,
        "extracted_interval": extracted_interval,
    }
    if not binding_ok:
        errors.append("finding_query_binding_missing_or_out_of_range")

    overhead_report = loaded.get("overhead")
    overhead_path = paths.get("overhead")
    overhead_ok = False
    overhead_reason = "capture overhead report missing"
    overhead_rom_hashes: list[str] = []
    if isinstance(overhead_report, dict):
        observed_overhead = overhead_report.get("observed_overhead", {})
        phase_medians = observed_overhead.get("phase_medians", {})
        required_phases = ("boot_ms", "capture_ms", "finalization_ms", "total_ms")
        phases_ok = all(isinstance(phase_medians.get(phase, {}).get("delta_median_ms"), (int, float))
                        for phase in required_phases)
        pairs = overhead_report.get("successful_pairs")
        pair_count = len(pairs) if isinstance(pairs, list) else 0
        # ``same_rom_sha256`` is an assertion made by the producer.  V5 must
        # also bind the report to the ROM actually present in this capture;
        # otherwise a valid overhead report from another build can be reused.
        def collect_overhead_rom_hashes(value: Any) -> None:
            if isinstance(value, dict):
                rom_hash = value.get("rom_sha256")
                if isinstance(rom_hash, str) and rom_hash:
                    overhead_rom_hashes.append(rom_hash)
                for nested in value.values():
                    collect_overhead_rom_hashes(nested)
            elif isinstance(value, list):
                for nested in value:
                    collect_overhead_rom_hashes(nested)

        collect_overhead_rom_hashes(overhead_report.get("cases", []))
        collect_overhead_rom_hashes(overhead_report.get("successful_pairs", []))
        expected_overhead_rom_sha = capture_artifacts.get("rom", {}).get("sha256")
        overhead_rom_binding_ok = bool(
            isinstance(expected_overhead_rom_sha, str) and expected_overhead_rom_sha and
            overhead_rom_hashes and all(value == expected_overhead_rom_sha for value in overhead_rom_hashes)
        )
        overhead_ok = bool(overhead_report.get("status") == "measured" and
                           overhead_report.get("same_rom_sha256") is True and
                           overhead_rom_binding_ok and
                           observed_overhead.get("cadence_telemetry_complete") is True and
                           pair_count >= 2 and phases_ok)
        overhead_reason = ("paired baseline/capture overhead with HCAD telemetry and phase medians"
                           if overhead_ok else
                           "overhead report lacks comparable repetitions, HCAD telemetry, phase medians or ROM binding")
    steps["capture_overhead"] = {
        "status": "passed" if overhead_ok else "failed",
        "reason": overhead_reason,
        "path": str(overhead_path) if overhead_path else None,
        "capture_rom_sha256": capture_artifacts.get("rom", {}).get("sha256"),
        "report_rom_sha256_values": sorted(set(overhead_rom_hashes)),
        "rom_binding": bool(overhead_rom_hashes) and all(
            value == capture_artifacts.get("rom", {}).get("sha256") for value in overhead_rom_hashes
        ),
        "claim_limit": "paired host-phase overhead only; never FPS, game cadence or perceptual motion",
    }
    if not overhead_ok:
        errors.append("capture_overhead_missing_or_not_comparable")
        if not overhead_rom_hashes or not steps["capture_overhead"]["rom_binding"]:
            errors.append("capture_overhead_rom_hash_mismatch_or_missing")

    review_for_validation = dict(review)
    review_for_validation["_manifest_dir"] = str(paths["review"].parent)
    review_validation = validate_review(ingest_report, review_for_validation)
    steps["qualified_review"] = {
        "status": "passed" if review_validation.get("qualified") else "failed",
        "qualified": review_validation.get("qualified", False),
        "reviewer": review_validation.get("reviewer"),
        "method": review_validation.get("method"),
        "capabilities": review_validation.get("capabilities", {}),
        "coverage": review_validation.get("coverage", {}),
        "errors": review_validation.get("errors", []),
        "path": str(paths["review"]),
    }
    if not review_validation.get("qualified"):
        errors.append("qualified_review_missing_or_invalid")

    recomputed_gate = evaluate_gate(ingest_report, review_for_validation)
    gate_consistent = (gate_report.get("status") == recomputed_gate.get("status") and
                       gate_report.get("claims") == recomputed_gate.get("claims") and
                       gate_report.get("claim_scopes") == recomputed_gate.get("claim_scopes"))
    steps["gate_consumption"] = {
        "status": "passed" if gate_consistent else "failed",
        "stored_status": gate_report.get("status"),
        "recomputed_status": recomputed_gate.get("status"),
        "stored_claims": gate_report.get("claims", {}),
        "claim_scopes": gate_report.get("claim_scopes", {}),
        "path": str(paths["gate"]),
    }
    if not gate_consistent:
        errors.append("stored_gate_does_not_match_consumed_review")

    capture_cadence = capture.get("cadence_probe")
    steps["capture_cadence_telemetry"] = {
        "status": "passed" if isinstance(capture_cadence, dict) else "needs_review",
        "source": "capture_manifest.cadence_probe" if isinstance(capture_cadence, dict) else None,
        "claim_limit": "absence in this manifest never releases game cadence; ingest HCAD is evaluated separately",
    }
    pipeline_ok = not errors
    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "tool_name": "audiovisual_review",
        "tool_version": TOOL_VERSION,
        "stage": "V5_end_to_end",
        "status": gate_report.get("status") if pipeline_ok else "blocked",
        "execution_status": "passed" if pipeline_ok else "failed",
        "pipeline_claim": "V0-V4 outputs were consumed and cross-checked; claim scopes remain those emitted by V4",
        "steps": steps,
        "hash_chain": hash_checks,
        "capture_artifacts": capture_artifacts,
        "capture_overhead": overhead_report if isinstance(overhead_report, dict) else None,
        "review_validation": review_validation,
        "claims": gate_report.get("claims", {}) if pipeline_ok else {},
        "claim_scopes": gate_report.get("claim_scopes", {}) if pipeline_ok else {},
        "blocking_errors": errors,
        "non_substitution_rule": "A successful V5 execution never converts a blocked axis into approval.",
    }
    write_json(Path(args.out).resolve(), result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if pipeline_ok else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("preflight"); p.add_argument("--out", type=Path)
    p = sub.add_parser("freeze"); p.add_argument("--project", required=True); p.add_argument("--out", required=True); p.add_argument("--rom"); p.add_argument("--route")
    p = sub.add_parser("ingest"); p.add_argument("--bundle", required=True); p.add_argument("--out", required=True); p.add_argument("--project"); p.add_argument("--manifest"); p.add_argument("--video"); p.add_argument("--audio"); p.add_argument("--video-log"); p.add_argument("--region-hz", type=int, default=60)
    p = sub.add_parser("query"); p.add_argument("--report", required=True); p.add_argument("--out", required=True); p.add_argument("--event-id", required=True); p.add_argument("--start", required=True); p.add_argument("--end", required=True); p.add_argument("--pre-context", type=float, default=0.5); p.add_argument("--post-context", type=float, default=0.5); p.add_argument("--roi", action="append", default=[])
    p = sub.add_parser("findings"); p.add_argument("--report", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("gameplay-finding")
    for name in ("report", "manifest", "query", "out", "finding-id", "symptom", "hypothesis", "impact", "causal-test", "input-summary", "expected-state"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--hsem"); p.add_argument("--hprb"); p.add_argument("--hcad"); p.add_argument("--hstr")
    p.add_argument("--causal-compare")
    p.add_argument("--visual-evidence", action="append", default=[])
    p.add_argument("--confidence", type=float, default=0.75); p.add_argument("--reviewer", default="Codex")
    p = sub.add_parser("causal-compare")
    p.add_argument("--with-video-manifest", required=True)
    p.add_argument("--without-video-manifest", required=True)
    p.add_argument("--with-video-dir", required=True)
    p.add_argument("--without-video-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--query")
    p.add_argument("--hstr-with-video")
    p.add_argument("--hstr-without-video")
    p.add_argument("--finding-id", default="capture-route-special-overlay-001")
    p.add_argument("--frame-prefix", default="special_only_p1_try0_")
    p.add_argument("--roi", default="128,80,384,280")
    p = sub.add_parser("gate"); p.add_argument("--report", required=True); p.add_argument("--review"); p.add_argument("--out", required=True)
    p = sub.add_parser("end-to-end")
    for name in ("freeze", "capture-manifest", "ingest", "query", "finding", "review", "gate", "out"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--overhead", required=True,
                   help="paired capture-overhead report with persisted HCAD telemetry")
    args = parser.parse_args()
    if args.command == "preflight":
        result = preflight(); print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.out: write_json(args.out.resolve(), result)
        return 0 if not result["blockers"] else 2
    if args.command == "freeze": return freeze(args)
    if args.command == "ingest": return ingest(args)
    if args.command == "query": return query(args)
    if args.command == "findings": return make_findings(args)
    if args.command == "gameplay-finding": return make_gameplay_finding(args)
    if args.command == "causal-compare": return causal_compare(args)
    if args.command == "gate": return gate(args)
    if args.command == "end-to-end": return end_to_end(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
