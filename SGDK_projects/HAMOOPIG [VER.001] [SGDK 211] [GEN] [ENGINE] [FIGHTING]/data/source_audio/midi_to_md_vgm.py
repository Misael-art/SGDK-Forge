#!/usr/bin/env python3
"""Transcribe the Ken-stage MIDI to a compact NTSC VGM (YM2612 + PSG noise).

The MIDI itself never enters the ROM. Lead/harmony/bass become three FM
channels; GM drums become SN76489 noise. Loop is the shortest repeating
melody period (8-16 bars). No PCM samples — minimum cart weight, FM timbre
on MD. Driver remains XGM1 (HAMOOPIG already uses XGM_* / Z80_DRIVER_XGM).
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIDI = ROOT / "data/source_audio/ssf2_ken_stage_vgmusic.mid"
OUT_VGM = ROOT / "res/music/ken_stage.vgm"
REPORT = ROOT / "rascunho/ken_stage_vgm_report.json"

YM_CLOCK = 7670453
PSG_CLOCK = 3579545
FPS = 60
MIN_STEM_NOTES = 200
PERC_CHANNEL = 9
DRUM_FRAMES = 2


def _vlq(data, i):
    v = 0
    while True:
        b = data[i]
        i += 1
        v = (v << 7) | (b & 0x7F)
        if not b & 0x80:
            return v, i


def parse_midi(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b"MThd"
    tpqn = struct.unpack(">H", raw[12:14])[0]
    tempo_us = 500000
    stems = {}
    perc = []
    i = 14
    trk = -1
    while i < len(raw):
        chunk = raw[i:i + 4]
        ln = struct.unpack(">I", raw[i + 4:i + 8])[0]
        body = raw[i + 8:i + 8 + ln]
        i += 8 + ln
        if chunk != b"MTrk":
            continue
        trk += 1
        j = 0
        tick = 0
        run = None
        active = {}
        while j < len(body):
            d, j = _vlq(body, j)
            tick += d
            st = body[j]
            if st & 0x80:
                j += 1
                run = st
            else:
                st = run
            hi = st & 0xF0
            ch = st & 0x0F
            if hi in (0x90, 0x80):
                note, vel = body[j], body[j + 1]
                j += 2
                key = (ch, note)
                if hi == 0x90 and vel > 0:
                    active.setdefault(key, []).append((tick, vel))
                else:
                    if active.get(key):
                        on_tick, on_vel = active[key].pop(0)
                        if ch == PERC_CHANNEL:
                            perc.append((on_tick, note, on_vel))
                        else:
                            stems.setdefault((trk, ch), []).append(
                                (on_tick, tick, note, on_vel))
            elif hi in (0xA0, 0xB0, 0xE0):
                j += 2
            elif hi in (0xC0, 0xD0):
                j += 1
            elif st == 0xFF:
                mt = body[j]
                j += 1
                ln2, j = _vlq(body, j)
                if mt == 0x51 and ln2 == 3:
                    tempo_us = int.from_bytes(body[j:j + 3], "big")
                j = len(body) if mt == 0x2F else j + ln2
            elif st in (0xF0, 0xF7):
                ln2, j = _vlq(body, j)
                j += ln2
            else:
                j += 1
    return tpqn, tempo_us, stems, perc


def midi_to_block_fnum(note: int) -> tuple[int, int]:
    freq = 440.0 * (2 ** ((note - 69) / 12.0))
    block = max(1, min(7, (note // 12) - 1))
    # F-Number = (144 * freq * 2^20 / clock) / 2^(block-1)
    fnum = int(round((144.0 * freq * (1 << 20) / YM_CLOCK) / (1 << (block - 1))))
    while fnum > 2047 and block < 7:
        fnum //= 2
        block += 1
    while fnum < 256 and block > 1:
        fnum *= 2
        block -= 1
    fnum = max(1, min(2047, fnum))
    return block, fnum


def fm_patch(ch: int, kind: str) -> list[tuple[int, int]]:
    op = [0x00, 0x08, 0x04, 0x0C]
    base = ch
    if kind == "lead":
        mul, tl, ar, dr, slrr, fb_alg = (1, 18, 0x1F, 0x09, 0x25, 0x34)
    elif kind == "bass":
        mul, tl, ar, dr, slrr, fb_alg = (1, 10, 0x1F, 0x06, 0x18, 0x32)
    else:
        mul, tl, ar, dr, slrr, fb_alg = (2, 28, 0x18, 0x0A, 0x47, 0x24)
    regs = [(0xB0 + base, fb_alg), (0xB4 + base, 0xC0)]
    for i, off in enumerate(op):
        tl_i = tl if i == 3 or kind != "lead" else tl + 8
        regs += [
            (0x30 + off + base, (0 << 4) | mul),
            (0x40 + off + base, tl_i),
            (0x50 + off + base, ar),
            (0x60 + off + base, dr),
            (0x70 + off + base, 0x00),
            (0x80 + off + base, slrr),
            (0x90 + off + base, 0x00),
        ]
    return regs


def vgm_write_ym(buf: bytearray, reg: int, val: int) -> None:
    buf += bytes((0x52, reg & 0xFF, val & 0xFF))


def vgm_write_psg(buf: bytearray, val: int) -> None:
    buf += bytes((0x50, val & 0xFF))


def vgm_wait_frame(buf: bytearray) -> None:
    buf.append(0x62)


def build() -> dict:
    tpqn, tempo_us, stems, perc = parse_midi(MIDI)
    bpm = 60_000_000.0 / tempo_us
    fpt = FPS * tempo_us / (1_000_000.0 * tpqn)
    bar_ticks = tpqn * 4
    big = {k: ns for k, ns in stems.items() if len(ns) >= MIN_STEM_NOTES}
    if not big:
        big = stems

    def avg_pitch(k):
        ns = stems[k]
        return sum(n for _, _, n, _ in ns) / max(1, len(ns))

    melody = max(big, key=avg_pitch)
    bass = min(big, key=avg_pitch)
    rest = [k for k in big if k not in (melody, bass)]
    harmony = max(rest, key=lambda k: len(stems[k])) if rest else None
    mel = sorted(stems[melody])
    bas = sorted(stems[bass])
    har = sorted(stems[harmony]) if harmony else []

    sig = {}
    for on, off, n, v in mel:
        sig.setdefault(on // bar_ticks, set()).add((on % bar_ticks, n))
    start_bar = min(sig)
    filled = tuple(frozenset(sig[b]) for b in sorted(sig))
    period = len(filled)
    for p in range(1, len(filled) // 2 + 1):
        if all(filled[i] == filled[i % p] for i in range(len(filled))):
            period = p
            break
    bars_n = min(max(period, 8), 16)
    start_tick = start_bar * bar_ticks
    window = start_tick + bars_n * bar_ticks
    frames_n = max(1, int(round(bars_n * bar_ticks * fpt)))

    body = bytearray()
    for reg, val in fm_patch(0, "lead") + fm_patch(1, "bass") + fm_patch(2, "harm"):
        vgm_write_ym(body, reg, val)
    vgm_write_psg(body, 0xE7)
    vgm_write_psg(body, 0xFF)
    loop_point = len(body)

    def events_for(notes, ch):
        ev = {}
        for on, off, n, v in notes:
            if not (start_tick <= on < window):
                continue
            f = int(round((on - start_tick) * fpt))
            end_f = int(round((off - start_tick) * fpt))
            ev.setdefault(f, []).append(("on", ch, n, v))
            if end_f > f:
                ev.setdefault(min(end_f, frames_n - 1), []).append(("off", ch, n, v))
        return ev

    ev = {}
    for src, ch in ((mel, 0), (bas, 1), (har, 2)):
        for f, items in events_for(src, ch).items():
            ev.setdefault(f, []).extend(items)
    for t, n, v in perc:
        if start_tick <= t < window:
            f = int(round((t - start_tick) * fpt))
            ev.setdefault(f, []).append(("drum", 0, n, v))

    drum_off = -1
    for f in range(frames_n):
        for kind, ch, n, v in ev.get(f, []):
            if kind == "on":
                block, fnum = midi_to_block_fnum(n)
                vgm_write_ym(body, 0xA4 + ch, ((block & 7) << 3) | ((fnum >> 8) & 7))
                vgm_write_ym(body, 0xA0 + ch, fnum & 0xFF)
                vgm_write_ym(body, 0x28, 0xF0 | ch)
            elif kind == "off":
                vgm_write_ym(body, 0x28, ch)
            elif kind == "drum":
                mode = 0x04 if n < 42 else 0x03
                att = max(0, min(14, 3 + (127 - v) // 32))
                vgm_write_psg(body, 0xE0 | mode)
                vgm_write_psg(body, 0xF0 | att)
                drum_off = f + DRUM_FRAMES
        if f == drum_off:
            vgm_write_psg(body, 0xF0 | 15)
        vgm_wait_frame(body)
    body.append(0x66)

    header = bytearray(256)
    header[0:4] = b"Vgm "
    eof = 256 + len(body) - 4
    data_offset_from_34 = 256 - 0x34
    loop_file_off = 256 + loop_point
    struct.pack_into("<I", header, 4, eof)
    struct.pack_into("<I", header, 8, 0x00000161)
    struct.pack_into("<I", header, 0x0C, YM_CLOCK)
    struct.pack_into("<I", header, 0x10, PSG_CLOCK)
    struct.pack_into("<I", header, 0x18, frames_n * 735)
    struct.pack_into("<I", header, 0x1C, loop_file_off - 0x1C)
    struct.pack_into("<I", header, 0x20, frames_n * 735)
    struct.pack_into("<I", header, 0x24, 60)
    struct.pack_into("<H", header, 0x28, 0x0009)
    header[0x2A] = 16
    header[0x2B] = 0
    struct.pack_into("<I", header, 0x34, data_offset_from_34)
    OUT_VGM.parent.mkdir(parents=True, exist_ok=True)
    OUT_VGM.write_bytes(bytes(header) + bytes(body))
    info = {
        "midi": str(MIDI),
        "midi_sha256": hashlib_sha(MIDI),
        "vgm": str(OUT_VGM),
        "bytes": OUT_VGM.stat().st_size,
        "bpm": round(bpm, 2),
        "bars": bars_n,
        "period_bars": period,
        "frames": frames_n,
        "loop_point_body": loop_point,
        "stems": {"melody": str(melody), "bass": str(bass), "harmony": str(harmony)},
        "no_pcm": True,
        "midi_not_in_rom": True,
        "driver": "XGM1",
        "chips": ["YM2612", "SN76489"],
        "composition_scope": "core_loop_10m",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(info, indent=2))
    return info


def hashlib_sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    build()
