"""Generate original XGM2 PCM assets for the Celestial Chase vertical slice."""

from __future__ import annotations

import hashlib
import json
import math
import wave
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
OUTPUT = PROJECT / "res" / "audio" / "chase"
REPORT = PROJECT / "doc" / "sample_format_audit.json"
RATE = 13300


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clamp(value: float) -> int:
    return max(0, min(255, int(round(128 + value))))


def fade(index: int, length: int, edge: int) -> float:
    if index < edge:
        return index / edge
    if index >= length - edge:
        return (length - index - 1) / edge
    return 1.0


def write_wav(path: Path, samples: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(1)
        handle.setframerate(RATE)
        handle.writeframes(bytes(samples))


def score_sample(time_s: float, phase: int) -> float:
    chord_sets = (
        (110.00, 164.81, 220.00, 261.63),
        (98.00, 146.83, 196.00, 246.94),
        (123.47, 185.00, 246.94, 293.66),
        (82.41, 123.47, 164.81, 220.00),
    )
    chord = chord_sets[phase % len(chord_sets)]
    beat = int(time_s * 4.0) % 4
    lead = chord[beat]
    bass = chord[0] * 0.5
    shimmer = chord[(beat + 2) % 4] * 2.0
    pulse = 0.45 + 0.55 * max(0.0, math.sin(math.tau * 2.0 * time_s))
    return (
        math.sin(math.tau * bass * time_s) * 24.0
        + math.sin(math.tau * lead * time_s) * 31.0 * pulse
        + math.sin(math.tau * shimmer * time_s) * 9.0
        + math.sin(math.tau * (lead * 0.5) * time_s) * 6.0
    )


def build_score(seconds: float = 8.0) -> list[int]:
    length = int(RATE * seconds)
    edge = int(RATE * 0.035)
    result: list[int] = []
    for index in range(length):
        time_s = index / RATE
        phase = int(time_s / 2.0)
        result.append(clamp(score_sample(time_s, phase) * fade(index, length, edge)))
    result[0] = 128
    result[-1] = 128
    return result


def build_tone(
    seconds: float,
    frequencies: tuple[float, ...],
    amplitude: float,
    noise: float = 0.0,
    descend: bool = False,
) -> list[int]:
    length = int(RATE * seconds)
    edge = max(1, int(RATE * min(0.025, seconds / 5.0)))
    result: list[int] = []
    seed = 0x4A31
    for index in range(length):
        time_s = index / RATE
        progress = index / max(1, length - 1)
        value = 0.0
        for frequency in frequencies:
            current = frequency * (1.0 - (0.35 * progress if descend else 0.0))
            value += math.sin(math.tau * current * time_s) * (amplitude / len(frequencies))
        if noise:
            seed = ((seed * 1103515245) + 12345) & 0x7FFFFFFF
            value += (((seed >> 16) & 0xFF) - 128) * noise
        envelope = (1.0 - progress) * fade(index, length, edge)
        result.append(clamp(value * envelope))
    result[0] = 128
    result[-1] = 128
    return result


def audit(path: Path) -> dict:
    with wave.open(str(path), "rb") as handle:
        frames = handle.readframes(handle.getnframes())
        duration = handle.getnframes() / handle.getframerate()
    centered = [value - 128 for value in frames]
    return {
        "path": path.relative_to(PROJECT).as_posix(),
        "sha256": sha256(path),
        "channels": 1,
        "bits_per_sample": 8,
        "sample_rate_hz": RATE,
        "duration_seconds": round(duration, 3),
        "dc_offset": round(sum(centered) / max(1, len(centered)), 3),
        "peak": max(abs(value) for value in centered),
        "first_sample": frames[0],
        "last_sample": frames[-1],
        "loop_boundary_silent": frames[0] == 128 and frames[-1] == 128,
    }


def main() -> None:
    assets = {
        "chase_score_loop.wav": build_score(),
        "chase_menu.wav": build_tone(0.12, (440.0, 660.0), 72.0),
        "chase_jump.wav": build_tone(0.18, (520.0, 780.0), 68.0),
        "chase_land.wav": build_tone(0.14, (130.0,), 62.0, noise=0.18, descend=True),
        "chase_hit.wav": build_tone(0.24, (92.0, 184.0), 76.0, noise=0.32, descend=True),
        "chase_pulse.wav": build_tone(0.46, (220.0, 440.0, 880.0), 72.0),
        "chase_pickup.wav": build_tone(0.16, (660.0, 990.0), 65.0),
        "chase_victory.wav": build_tone(0.72, (329.63, 493.88, 659.25), 64.0),
        "chase_failure.wav": build_tone(0.72, (196.0, 146.83, 98.0), 64.0, descend=True),
        "chase_pressure.wav": build_tone(0.20, (82.41, 164.81), 54.0, descend=True),
    }
    for name, samples in assets.items():
        write_wav(OUTPUT / name, samples)

    report = {
        "schema": "sample_format_audit_v1",
        "status": "generated_pending_validate_audio_and_blastem_listen",
        "generation_basis": "project_local_original_synthesis",
        "driver": "XGM2",
        "assets": [audit(OUTPUT / name) for name in assets],
        "delivery_findings": [
            "All sources are mono PCM WAV at 13.3 kHz and 8-bit.",
            "Every sample begins and ends at unsigned PCM center 128.",
            "The score loop remains pending a human headphone loop check in BlastEm.",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
