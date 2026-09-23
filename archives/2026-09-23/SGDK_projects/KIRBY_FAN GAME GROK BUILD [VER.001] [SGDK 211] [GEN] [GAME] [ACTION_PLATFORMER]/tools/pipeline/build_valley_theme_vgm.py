#!/usr/bin/env python3
"""Vegetable Valley theme — richer procedural VGM for XGM2 (YM2612 + PSG).

Not a Furnace composition. Goals vs previous placeholder:
  - FM1 bass (aggressive), FM2 pad, FM3 lead, FM4 arpeggio
  - PSG1 lead sparkle, PSG noise hi-hat
  - Longer phrase (8 bars), clearer cadence, G major dream-land energy
  - Loop marked for continuous stage play

Usage:
  python3 tools/pipeline/build_valley_theme_vgm.py --install
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "res" / "audio" / "mus_stage_valley.vgm"
SRC = ROOT / "res" / "audio" / "source" / "mus_stage_valley_r2.vgm"

YM_CLOCK = 7670454
SN_CLOCK = 3579545
FRAME_SAMPLES = 735  # 44100/60


class Vgm:
    def __init__(self) -> None:
        self.data = bytearray()
        self.frames = 0
        self.loop_at: int | None = None

    def ym0(self, reg: int, val: int) -> None:
        self.data += bytes((0x52, reg & 0xFF, val & 0xFF))

    def ym1(self, reg: int, val: int) -> None:
        self.data += bytes((0x53, reg & 0xFF, val & 0xFF))

    def psg(self, val: int) -> None:
        self.data += bytes((0x50, val & 0xFF))

    def wait_frame(self, n: int = 1) -> None:
        for _ in range(n):
            self.data += bytes((0x62,))
        self.frames += n

    def mark_loop(self) -> None:
        self.loop_at = len(self.data)

    def build(self) -> bytes:
        body = bytes(self.data) + bytes((0x66,))
        header = bytearray(0x100)
        header[0x00:0x04] = b"Vgm "
        struct.pack_into("<I", header, 0x08, 0x00000150)
        struct.pack_into("<I", header, 0x0C, SN_CLOCK)
        struct.pack_into("<I", header, 0x2C, YM_CLOCK)
        struct.pack_into("<I", header, 0x24, 60)
        total = self.frames * FRAME_SAMPLES
        struct.pack_into("<I", header, 0x18, total)
        struct.pack_into("<I", header, 0x34, 0x100 - 0x34)
        if self.loop_at is not None:
            loop_abs = 0x100 + self.loop_at
            struct.pack_into("<I", header, 0x1C, loop_abs - 0x1C)
            struct.pack_into("<I", header, 0x20, total)
        struct.pack_into("<I", header, 0x04, (0x100 + len(body)) - 0x04)
        return bytes(header) + body


OP = (0x00, 0x08, 0x04, 0x0C)


def patch(v: Vgm, ch: int, algo: int, feedback: int, ops: list[tuple]) -> None:
    write = v.ym0 if ch < 3 else v.ym1
    base = ch % 3
    for i, (mul, tl, ar, d1r, d2r, rr, sl) in enumerate(ops):
        o = OP[i]
        write(0x30 + o + base, mul & 0x0F)
        write(0x40 + o + base, tl & 0x7F)
        write(0x50 + o + base, ar & 0x1F)
        write(0x60 + o + base, d1r & 0x1F)
        write(0x70 + o + base, d2r & 0x1F)
        write(0x80 + o + base, ((sl & 0x0F) << 4) | (rr & 0x0F))
    write(0xB0 + base, ((feedback & 7) << 3) | (algo & 7))
    write(0xB4 + base, 0xC0)


def ym_note(midi: int) -> tuple[int, int]:
    freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    block = 4
    while freq < 262.0 and block > 0:
        freq *= 2.0
        block -= 1
    while freq >= 524.0 and block < 7:
        freq /= 2.0
        block += 1
    fnum = int(round((freq * 144.0 * (1 << 21)) / YM_CLOCK)) >> block
    fnum = max(0, min(2047, fnum))
    return block, fnum


def note_on(v: Vgm, ch: int, midi: int) -> None:
    write = v.ym0 if ch < 3 else v.ym1
    base = ch % 3
    block, fnum = ym_note(midi)
    write(0xA4 + base, ((block & 7) << 3) | ((fnum >> 8) & 3))
    write(0xA0 + base, fnum & 0xFF)
    key = 0xF0 | (base + (4 if ch >= 3 else 0))
    v.ym0(0x28, key)


def note_off(v: Vgm, ch: int) -> None:
    base = ch % 3
    v.ym0(0x28, base + (4 if ch >= 3 else 0))


def psg_note(v: Vgm, ch: int, midi: int, atten: int) -> None:
    freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
    n = int(round(SN_CLOCK / (32.0 * freq)))
    n = max(1, min(1023, n))
    v.psg(0x80 | (ch << 5) | (n & 0x0F))
    v.psg((n >> 4) & 0x3F)
    v.psg(0x90 | (ch << 5) | (atten & 0x0F))


def psg_off(v: Vgm, ch: int) -> None:
    v.psg(0x90 | (ch << 5) | 0x0F)


def psg_noise(v: Vgm, atten: int, mode: int = 0x04) -> None:
    """mode: 0x04 periodic, 0x07 white-ish; register 0xE? / 0xF?"""
    v.psg(0xE0 | (mode & 0x07))
    v.psg(0xF0 | (atten & 0x0F))


def silence_all(v: Vgm) -> None:
    for ch in range(4):
        v.psg(0x90 | (ch << 5) | 0x0F)
    for c in range(3):
        v.ym0(0x28, c)
        v.ym0(0x28, c + 4)


def build_theme() -> bytes:
    v = Vgm()
    v.ym0(0x22, 0x00)
    v.ym0(0x27, 0x00)
    v.ym0(0x2B, 0x00)
    silence_all(v)

    # FM0 bass — aggressive short punch (algo 4)
    patch(
        v,
        0,
        algo=4,
        feedback=6,
        ops=[
            (1, 28, 31, 10, 5, 7, 2),
            (1, 16, 31, 8, 4, 7, 2),
            (2, 36, 31, 12, 6, 8, 3),
            (1, 12, 31, 10, 5, 8, 2),
        ],
    )
    # FM1 pad — soft strings (algo 7 stacked)
    patch(
        v,
        1,
        algo=5,
        feedback=2,
        ops=[
            (1, 42, 18, 8, 4, 6, 3),
            (1, 40, 16, 8, 4, 6, 3),
            (1, 38, 16, 8, 4, 6, 3),
            (1, 34, 14, 6, 3, 6, 2),
        ],
    )
    # FM2 lead — bright dream-land whistle
    patch(
        v,
        2,
        algo=2,
        feedback=5,
        ops=[
            (3, 34, 31, 8, 3, 6, 1),
            (1, 22, 31, 7, 3, 6, 1),
            (2, 30, 31, 8, 3, 6, 1),
            (1, 10, 31, 6, 2, 6, 1),
        ],
    )
    # FM3 (port1 ch0) arpeggio bell
    patch(
        v,
        3,
        algo=4,
        feedback=3,
        ops=[
            (4, 38, 31, 12, 8, 9, 2),
            (2, 28, 31, 10, 6, 8, 2),
            (1, 40, 31, 12, 8, 9, 3),
            (1, 20, 31, 10, 6, 9, 2),
        ],
    )

    # Tempo ~132 BPM: eighth ≈ 14 frames @ 60Hz
    E = 14
    # Scale G major midis
    # bass root motion
    bass_pat = [
        [43, 43, 50, 50, 45, 45, 47, 47],  # G2 G2 D3 D3 A2 A2 B2 B2
        [43, 43, 50, 50, 48, 48, 47, 45],
        [41, 41, 48, 48, 43, 43, 45, 45],  # F
        [43, 43, 50, 47, 45, 43, 42, 40],
    ]
    lead_pat = [
        [67, 71, 74, 71, 67, 74, 71, 67],  # G4 B4 D5 ...
        [69, 71, 72, 74, 76, 74, 72, 71],
        [67, 65, 64, 62, 64, 65, 67, 69],
        [71, 72, 74, 76, 79, 76, 74, 71],
    ]
    arp_pat = [
        [55, 59, 62, 67, 62, 59, 55, 59],
        [57, 60, 64, 69, 64, 60, 57, 60],
        [53, 57, 60, 65, 60, 57, 53, 57],
        [55, 59, 62, 67, 71, 67, 62, 59],
    ]
    pad_pat = [55, 57, 53, 55]  # whole-bar pads G Am F G

    # short intro (2 bars) before loop
    for i in range(8):
        note_on(v, 0, bass_pat[0][i] - 12)
        if i % 2 == 0:
            note_on(v, 2, lead_pat[0][i])
        psg_noise(v, 12 if i % 2 == 0 else 15, 0x07)
        v.wait_frame(E // 2)
        note_off(v, 0)
        note_off(v, 2)
        psg_noise(v, 15, 0x07)
        v.wait_frame(E // 2)

    v.mark_loop()
    for bar in range(8):
        bi = bar % 4
        # pad whole bar
        note_on(v, 1, pad_pat[bi])
        for i in range(8):
            # bass
            note_on(v, 0, bass_pat[bi][i])
            # lead
            note_on(v, 2, lead_pat[bi][i])
            # arpeggio
            note_on(v, 3, arp_pat[bi][i])
            # PSG sparkle octave up, quieter
            psg_note(v, 0, lead_pat[bi][i] + 12, 10 if i % 2 == 0 else 12)
            # hat
            psg_noise(v, 11 if i % 2 == 0 else 14, 0x07)
            v.wait_frame(E - 4)
            note_off(v, 0)
            note_off(v, 2)
            note_off(v, 3)
            psg_off(v, 0)
            psg_noise(v, 15, 0x07)
            v.wait_frame(4)
        note_off(v, 1)

    return v.build()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()
    data = build_theme()
    SRC.parent.mkdir(parents=True, exist_ok=True)
    SRC.write_bytes(data)
    print(f"wrote {SRC} ({len(data)} bytes, ~{len(data)/44100:.1f}s raw upper bound)")
    if args.install:
        # backup old
        bak = OUT.with_suffix(".vgm.bak")
        if OUT.exists() and not bak.exists():
            bak.write_bytes(OUT.read_bytes())
        OUT.write_bytes(data)
        print(f"installed {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
