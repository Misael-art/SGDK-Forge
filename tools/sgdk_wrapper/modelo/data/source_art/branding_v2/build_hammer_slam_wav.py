#!/usr/bin/env python3
"""Synthesize a 13.3 kHz unsigned-8 PCM hammer slam for XGM2.

Authored for the modelo brand, not a ripped sample. Transient + inharmonic
clang + low thump + short ring. Declared placeholder until a recorded hit
replaces it.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

RATE = 13300
DUR = 0.42
OUT = Path(__file__).resolve().parents[3] / "res" / "audio" / "branding" / "hammer_slam.wav"


def main() -> None:
    n = int(RATE * DUR)
    samples = []
    for i in range(n):
        t = i / RATE
        env_click = math.exp(-t * 220.0)
        env_clang = math.exp(-t * 18.0)
        env_thump = math.exp(-t * 9.0)
        env_ring = math.exp(-t * 7.5)
        env_noise = math.exp(-t * 55.0)

        click = math.sin(2 * math.pi * 2100 * t) * env_click * 0.55
        clang = (
            math.sin(2 * math.pi * 187 * t)
            + 0.55 * math.sin(2 * math.pi * 341 * t)
            + 0.35 * math.sin(2 * math.pi * 512 * t)
            + 0.22 * math.sin(2 * math.pi * 903 * t)
            + 0.12 * math.sin(2 * math.pi * 1481 * t)
        ) * env_clang * 0.28
        thump = math.sin(2 * math.pi * 58 * t) * env_thump * 0.62
        ring = math.sin(2 * math.pi * 1180 * t + 0.7 * math.sin(2 * math.pi * 6 * t)) * env_ring * 0.12
        # deterministic noise, not random: hashed saw
        noise = (((i * 1103515245 + 12345) >> 16) & 0xFF) / 127.5 - 1.0
        grit = noise * env_noise * 0.22

        acc = click + clang + thump + ring + grit
        if acc > 1.0:
            acc = 1.0
        elif acc < -1.0:
            acc = -1.0
        # leave 8 counts of headroom (XGM2 hates 0x00/0xFF clip)
        samples.append(int(128 + acc * 112))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as fh:
        fh.setnchannels(1)
        fh.setsampwidth(1)
        fh.setframerate(RATE)
        fh.writeframes(struct.pack("B" * len(samples), *samples))
    print(f"wrote {OUT} frames={n} dur={DUR:.3f}s")


if __name__ == "__main__":
    main()
