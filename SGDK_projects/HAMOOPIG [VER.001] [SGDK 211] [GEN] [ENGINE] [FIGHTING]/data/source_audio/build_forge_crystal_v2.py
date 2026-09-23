#!/usr/bin/env python3
"""Compile the authorial Forge Crystal BGM for the Mega Drive PSG.

The arrangement is deliberately small enough for the XGM1 driver but has four
independent parts: a lead motif, a moving bass, a bright counter/arpeggio and
an SN76489 noise percussion voice.  Timing is expressed in NTSC video frames
so the loop is deterministic and does not depend on a host MIDI renderer.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "res/music/mus_forge_brand.vgm"
REPORT = ROOT / "rascunho/forge_crystal_v2_build_report.json"

FPS = 60
BPM = 150
BEATS = 32                 # eight 4/4 bars
FRAMES_PER_BEAT = FPS * 60 // BPM
EIGHTH = FRAMES_PER_BEAT // 2
LOOP_FRAMES = BEATS * FRAMES_PER_BEAT
PSG_CLOCK = 3579545


def psg(value: int) -> bytes:
    return bytes((0x50, value & 0xFF))


def tone(ch: int, hz: float, attenuation: int) -> bytes:
    """Return a latched PSG tone period and volume."""
    period = max(1, min(0x3FF, int(round(PSG_CLOCK / (32.0 * hz)))))
    return psg(0x80 | ((ch & 3) << 5) | (period & 0x0F)) + psg((period >> 4) & 0x3F) \
        + psg(0x90 | ((ch & 3) << 5) | (max(0, min(15, attenuation)) & 0x0F))


def tone_off(ch: int) -> bytes:
    return psg(0x90 | ((ch & 3) << 5) | 0x0F)


def noise(mode: int, attenuation: int) -> bytes:
    return psg(0xE0 | (mode & 0x07)) + psg(0xF0 | (max(0, min(15, attenuation)) & 0x0F))


def note_events() -> dict[int, list[tuple[str, int, float, int]]]:
    events: dict[int, list[tuple[str, int, float, int]]] = {}

    def add_note(ch: int, start_beat: float, length_beats: float, midi: int, att: int) -> None:
        start = int(round(start_beat * FRAMES_PER_BEAT))
        end = min(LOOP_FRAMES, start + max(1, int(round(length_beats * FRAMES_PER_BEAT))))
        hz = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        events.setdefault(start, []).append(("on", ch, hz, att))
        events.setdefault(end, []).append(("off", ch, 0.0, 0))

    # A minor / A harmonic minor color.  The second half raises the leading
    # tone and opens the register so the loop has a real arc instead of a flat
    # eight-bar repetition.
    lead_bars = [
        [76, 79, 81, 84, 81, 79, 76, 74],
        [76, 79, 81, 86, 84, 81, 79, 76],
        [74, 76, 79, 81, 79, 76, 74, 72],
        [76, 79, 81, 84, 86, 84, 81, 79],
        [76, 79, 81, 84, 81, 79, 76, 74],
        [76, 79, 81, 88, 86, 84, 81, 79],
        [81, 84, 86, 88, 86, 84, 81, 79],
        [76, 74, 72, 74, 76, 79, 81, 76],
    ]
    for bar, notes in enumerate(lead_bars):
        base = bar * 4.0
        for i, midi in enumerate(notes):
            length = 0.5 if i not in (3, 7) else 0.75
            add_note(0, base + i * 0.5, length, midi, 1 + (i % 3))

    bass_roots = [45, 45, 41, 43, 45, 45, 41, 43]
    for bar in range(8):
        root = bass_roots[bar]
        fifth = root + 7
        base = bar * 4.0
        add_note(1, base, 1.75, root, 5)
        add_note(1, base + 2.0, 1.25, fifth, 6)
        add_note(1, base + 3.5, 0.35, root + 12, 7)

    # Crystal counterline: arpeggio is sparse on bars 1--4, then answers the
    # lead in bars 5--8.  It uses the third PSG voice and leaves the fourth for
    # percussion, keeping the spectral roles separated on real hardware.
    arp = [[69, 72, 76, 79], [67, 71, 74, 79], [65, 69, 72, 76], [64, 67, 71, 76]]
    for bar in range(8):
        chord = arp[bar % 4]
        base = bar * 4.0
        for i in range(8):
            midi = chord[i % 4] + (12 if bar >= 4 and i in (2, 3, 6, 7) else 0)
            add_note(2, base + i * 0.5, 0.32, midi, 8 + (i & 1))

    return events


def percussion_events() -> dict[int, list[tuple[int, int]]]:
    events: dict[int, list[tuple[int, int]]] = {}
    for beat in range(BEATS):
        frame = beat * FRAMES_PER_BEAT
        # Metallic downbeat/accent.  The alternating noise modes produce a
        # crisp forge pulse without turning the BGM into a sample wall.
        events.setdefault(frame, []).append((0x07, 7 if beat % 4 == 0 else 9))
        if beat % 4 in (1, 3):
            events.setdefault(frame + EIGHTH, []).append((0x05, 11))
    # A short pickup before the last bar gives the loop a controlled return.
    events.setdefault(LOOP_FRAMES - EIGHTH, []).append((0x03, 10))
    return events


def build() -> dict:
    body = bytearray()
    body += noise(0x07, 15) + tone_off(0) + tone_off(1) + tone_off(2)
    loop_point = len(body)
    melodic = note_events()
    percussion = percussion_events()
    for frame in range(LOOP_FRAMES):
        for kind, ch, hz, att in melodic.get(frame, []):
            body += tone(ch, hz, att) if kind == "on" else tone_off(ch)
        for mode, att in percussion.get(frame, []):
            body += noise(mode, att)
        body.append(0x62)
    body += tone_off(0) + tone_off(1) + tone_off(2) + noise(0x07, 15)
    body.append(0x66)

    header = bytearray(0x100)
    header[0:4] = b"Vgm "
    struct.pack_into("<I", header, 0x04, 0x100 + len(body) - 4)
    struct.pack_into("<I", header, 0x08, 0x00000150)
    struct.pack_into("<I", header, 0x10, PSG_CLOCK)
    struct.pack_into("<I", header, 0x18, LOOP_FRAMES * 735)
    loop_abs = 0x100 + loop_point
    struct.pack_into("<I", header, 0x1C, loop_abs - 0x1C)
    struct.pack_into("<I", header, 0x20, LOOP_FRAMES * 735)
    struct.pack_into("<I", header, 0x24, FPS)
    struct.pack_into("<H", header, 0x28, 0x0009)
    header[0x2A] = 16
    struct.pack_into("<I", header, 0x34, 0xCC)
    OUT.write_bytes(bytes(header) + body)
    report = {
        "schema_version": "2.0.0",
        "title": "Forge Crystal",
        "source_score": "data/source_audio/forge_crystal_score.json",
        "source_score_sha256": hashlib.sha256((ROOT / "data/source_audio/forge_crystal_score.json").read_bytes()).hexdigest(),
        "output": "res/music/mus_forge_brand.vgm",
        "output_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "driver": "XGM1",
        "chips": ["SN76489"],
        "voices": {"lead": 0, "bass": 1, "crystal_counterline": 2, "forge_noise": 3},
        "tempo_bpm": BPM,
        "meter": "4/4",
        "tonal_center": "A minor",
        "bars": 8,
        "loop_frames_ntsc": LOOP_FRAMES,
        "loop_seconds_ntsc": LOOP_FRAMES / FPS,
        "pcm_in_bgm": False,
        "sfx_pcm_channels_reserved": [3, 4],
        "status": "candidate_until_human_listening",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    build()
