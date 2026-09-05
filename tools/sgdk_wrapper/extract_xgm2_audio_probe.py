#!/usr/bin/env python3
"""Extract the AUD2 XGM2 telemetry block from a BlastEm SRAM image."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


AUD2_MAGIC = b"AUD2"
AUD2_SCHEMA_VERSION = 1
AUD2_OFFSET = 0x800
AUD2_WORDS = 13
AUD2_TOTAL_BYTES = 8 + (AUD2_WORDS * 2)
FIELD_NAMES = (
    "scene_id",
    "music_state",
    "music_playing",
    "pcm_channel_mask",
    "samples_recorded",
    "max_xgm2_cpu_load",
    "max_xgm2_dma_wait",
    "max_xgm2_missed_frames",
    "simultaneous_music_sfx_samples",
    "sfx_requests",
    "sfx_accepted",
    "xgm2_driver_frame_counter",
    "target_fps",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_aud2(data: bytes, offset: int = AUD2_OFFSET) -> dict:
    if len(data) < offset + 8:
        raise ValueError("SRAM shorter than AUD2 header offset")
    if data[offset:offset + 4] != AUD2_MAGIC:
        actual = data[offset:offset + 4].decode("ascii", errors="replace")
        raise ValueError(f"AUD2 signature missing at 0x{offset:X} (found {actual!r})")

    version, length = struct.unpack_from(">HH", data, offset + 4)
    if version != AUD2_SCHEMA_VERSION:
        raise ValueError(f"unsupported AUD2 schema {version}")
    if length != AUD2_TOTAL_BYTES:
        raise ValueError(f"invalid AUD2 length {length}; expected {AUD2_TOTAL_BYTES}")
    if len(data) < offset + length:
        raise ValueError("SRAM does not contain the complete AUD2 payload")

    values = struct.unpack_from(">" + ("H" * AUD2_WORDS), data, offset + 8)
    metrics = dict(zip(FIELD_NAMES, values, strict=True))
    metrics["music_playing"] = bool(metrics["music_playing"])
    return metrics


def build_report(sram_path: Path, session_id: str | None = None) -> dict:
    metrics = parse_aud2(sram_path.read_bytes())
    checks = {
        "music_runtime_observed": bool(
            metrics["xgm2_driver_frame_counter"] > 0
            and (
                metrics["music_playing"]
                or metrics["simultaneous_music_sfx_samples"] > 0
            )
        ),
        "simultaneous_music_sfx_observed": metrics["simultaneous_music_sfx_samples"] > 0,
        "sfx_accepted": metrics["sfx_accepted"] > 0,
        "no_xgm2_missed_frames": metrics["max_xgm2_missed_frames"] == 0,
        "telemetry_window_present": metrics["samples_recorded"] > 0,
    }
    required_checks = (
        "music_runtime_observed",
        "simultaneous_music_sfx_observed",
        "sfx_accepted",
        "telemetry_window_present",
    )
    blockers = [name for name in required_checks if not checks[name]]
    warnings = []
    if not checks["no_xgm2_missed_frames"]:
        warnings.append("xgm2_missed_frames_observed")
    return {
        "schema_version": "1.0.0",
        "report_type": "xgm2_audio_runtime_metrics",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "source_sram": {
            "path": str(sram_path),
            "sha256": sha256(sram_path),
            "size_bytes": sram_path.stat().st_size,
            "aud2_offset": AUD2_OFFSET,
        },
        "metrics": metrics,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "status": "passed" if not blockers else "blocked",
        "claim_limit": (
            "objective_xgm2_runtime_telemetry_only; human_audio_review_still_required"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sram", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--session-id")
    args = parser.parse_args()

    try:
        report = build_report(args.sram.resolve(), args.session_id)
    except (OSError, ValueError) as exc:
        print(f"[BLOCKED] {exc}")
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
