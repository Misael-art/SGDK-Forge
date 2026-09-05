#!/usr/bin/env python3
"""Write deterministic objective metrics for a PCM WAV emulator capture."""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dbfs(value: float) -> float | None:
    if value <= 0:
        return None
    return 20.0 * math.log10(value / 32768.0)


def analyze(path: Path, session_id: str | None) -> dict:
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        sample_width = source.getsampwidth()
        sample_rate = source.getframerate()
        frame_count = source.getnframes()
        compression = source.getcomptype()
        raw = source.readframes(frame_count)

    if channels < 1 or sample_width != 2 or compression != "NONE":
        raise ValueError("expected uncompressed 16-bit PCM WAV")

    samples = array.array("h")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    if len(samples) != frame_count * channels:
        raise ValueError("WAV sample count does not match its frame metadata")

    threshold = int(round(32768.0 * (10.0 ** (-60.0 / 20.0))))
    peak = 0
    sum_squares = 0
    active_frames = 0
    channel_peaks = [0] * channels
    channel_sum_squares = [0] * channels
    identical_stereo_frames = 0

    for frame in range(frame_count):
        frame_active = False
        base = frame * channels
        if channels == 2 and samples[base] == samples[base + 1]:
            identical_stereo_frames += 1
        for channel in range(channels):
            value = int(samples[base + channel])
            magnitude = abs(value)
            peak = max(peak, magnitude)
            channel_peaks[channel] = max(channel_peaks[channel], magnitude)
            square = value * value
            sum_squares += square
            channel_sum_squares[channel] += square
            if magnitude > threshold:
                frame_active = True
        if frame_active:
            active_frames += 1

    total_samples = len(samples)
    rms = math.sqrt(sum_squares / total_samples) if total_samples else 0.0
    duration = frame_count / sample_rate if sample_rate else 0.0
    channel_metrics = []
    for channel in range(channels):
        channel_rms = (
            math.sqrt(channel_sum_squares[channel] / frame_count)
            if frame_count
            else 0.0
        )
        channel_metrics.append(
            {
                "channel": channel + 1,
                "peak_dbfs": dbfs(channel_peaks[channel]),
                "rms_dbfs": dbfs(channel_rms),
            }
        )

    checks = {
        "duration_at_least_10_seconds": duration >= 10.0,
        "non_silent_signal_present": peak > threshold and active_frames > 0,
        "no_digital_clipping": peak < 32767,
    }
    blockers = [name for name, passed in checks.items() if not passed]
    return {
        "schema_version": "1.0.0",
        "report_type": "emulator_audio_capture_analysis",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "source": {
            "path": str(path),
            "sha256": file_sha256(path),
            "size_bytes": path.stat().st_size,
        },
        "format": {
            "codec": "pcm_s16le",
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "frames": frame_count,
            "duration_seconds": round(duration, 6),
        },
        "metrics": {
            "peak_dbfs": dbfs(peak),
            "rms_dbfs": dbfs(rms),
            "active_frame_ratio_above_minus_60_dbfs": (
                active_frames / frame_count if frame_count else 0.0
            ),
            "identical_stereo_frame_ratio": (
                identical_stereo_frames / frame_count
                if channels == 2 and frame_count
                else None
            ),
            "channels": channel_metrics,
        },
        "checks": checks,
        "blockers": blockers,
        "status": "passed" if not blockers else "blocked",
        "claim_limit": (
            "objective_signal_integrity_only; does_not_prove_composition_quality_or_"
            "human_auditory_acceptance"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--session-id")
    args = parser.parse_args()

    try:
        report = analyze(args.wav.resolve(), args.session_id)
    except (OSError, ValueError, wave.Error) as exc:
        print(f"[BLOCKED] {exc}")
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
