#!/usr/bin/env python3
"""Write an original NTSC VGM forge bed for XGM2.

Not a rip. Four bars at 100 BPM: FM bass, metallic bell, pad, PSG pulse.
Loop is the whole file. Lab composition_scope=core_loop_10m candidate —
status remains placeholder until a human composer replaces it.
"""
from __future__ import annotations

import struct
from pathlib import Path

OUT = Path(__file__).resolve().parents[3] / "res" / "music" / "forge_brand_loop.vgm"

YM2612 = 7670454
SN76489 = 3579545
FRAME = 735  # NTSC
BPM = 100
FRAMES_PER_BEAT = int(round((44100 * 60 / BPM) / FRAME))  # 26
BEATS = 16  # 4 bars


def u32(n: int) -> bytes:
    return struct.pack("<I", n)


def ym0(reg: int, val: int) -> bytes:
    return bytes((0x52, reg & 0xFF, val & 0xFF))


def ym1(reg: int, val: int) -> bytes:
    return bytes((0x53, reg & 0xFF, val & 0xFF))


def psg(val: int) -> bytes:
    return bytes((0x50, val & 0xFF))


def wait_frames(n: int) -> bytes:
    return bytes((0x62,)) * n


def key(ch: int, on: bool) -> bytes:
    slots = 0xF0 if on else 0x00
    return ym0(0x28, slots | (ch & 7))


def fnum_block(hz: float) -> tuple[int, int]:
    block = 4
    while hz < 200 and block > 0:
        hz *= 2
        block -= 1
    while hz > 800 and block < 7:
        hz /= 2
        block += 1
    fnum = int(round((hz * 144 * (1 << (20 - block))) / YM2612))
    fnum = max(1, min(0x7FF, fnum))
    return fnum, block


def set_freq(ch: int, hz: float) -> bytes:
    fnum, block = fnum_block(hz)
    if ch < 3:
        return ym0(0xA4 + ch, ((block & 7) << 3) | ((fnum >> 8) & 7)) + ym0(0xA0 + ch, fnum & 0xFF)
    off = ch - 3
    return ym1(0xA4 + off, ((block & 7) << 3) | ((fnum >> 8) & 7)) + ym1(0xA0 + off, fnum & 0xFF)


def write_op(port_fn, ch_off: int, op: int, dtmul: int, tl: int, rsar: int, amd1: int, d2: int, d1lrr: int) -> bytes:
    # op 0..3 -> register offsets 0, 8, 4, 12 for ops 1,3,2,4
    op_off = (0, 8, 4, 12)[op]
    base = ch_off + op_off
    return (
        port_fn(0x30 + base, dtmul)
        + port_fn(0x40 + base, tl)
        + port_fn(0x50 + base, rsar)
        + port_fn(0x60 + base, amd1)
        + port_fn(0x70 + base, d2)
        + port_fn(0x80 + base, d1lrr)
        + port_fn(0x90 + base, 0)
    )


def patch_bass() -> bytes:
    # CH0 port0, alg 4, fb 5 — tight low FM
    body = ym0(0xB0, (5 << 3) | 4) + ym0(0xB4, 0xC0)
    body += write_op(ym0, 0, 0, 0x01, 0x1A, 0x1F, 0x07, 0x07, 0x18)
    body += write_op(ym0, 0, 1, 0x01, 0x12, 0x1F, 0x09, 0x08, 0x28)
    body += write_op(ym0, 0, 2, 0x01, 0x24, 0x1F, 0x05, 0x05, 0x18)
    body += write_op(ym0, 0, 3, 0x01, 0x08, 0x1F, 0x04, 0x04, 0x48)
    return body


def patch_bell() -> bytes:
    # CH1 metallic clang
    body = ym0(0xB0 + 1, (4 << 3) | 5) + ym0(0xB4 + 1, 0xC0)
    body += write_op(ym0, 1, 0, 0x01, 0x1C, 0x1F, 0x12, 0x08, 0x27)
    body += write_op(ym0, 1, 1, 0x03, 0x22, 0x1F, 0x0F, 0x09, 0x27)
    body += write_op(ym0, 1, 2, 0x05, 0x28, 0x1F, 0x11, 0x0A, 0x37)
    body += write_op(ym0, 1, 3, 0x07, 0x14, 0x1F, 0x08, 0x08, 0x47)
    return body


def patch_pad() -> bytes:
    # CH2 slow heat
    body = ym0(0xB0 + 2, (3 << 3) | 4) + ym0(0xB4 + 2, 0xC0)
    body += write_op(ym0, 2, 0, 0x01, 0x28, 0x0C, 0x04, 0x04, 0xA8)
    body += write_op(ym0, 2, 1, 0x02, 0x30, 0x0A, 0x05, 0x05, 0xA8)
    body += write_op(ym0, 2, 2, 0x01, 0x2C, 0x0B, 0x04, 0x04, 0x98)
    body += write_op(ym0, 2, 3, 0x01, 0x1A, 0x08, 0x03, 0x03, 0xA8)
    return body


def psg_tone(ch: int, freq: int, vol: int) -> bytes:
    # SN76489: latch tone
    lat = 0x80 | ((ch & 3) << 5) | (freq & 0x0F)
    data = (freq >> 4) & 0x3F
    att = 0x90 | ((ch & 3) << 5) | (vol & 0x0F)
    return psg(lat) + psg(data) + psg(att)


def psg_off(ch: int) -> bytes:
    return psg(0x90 | ((ch & 3) << 5) | 0x0F)


def main() -> None:
    data = bytearray()
    data += ym0(0x22, 0x00)
    data += ym0(0x27, 0x00)
    data += ym0(0x2B, 0x00)
    for ch in range(6):
        data += key(ch, False)
    data += patch_bass() + patch_bell() + patch_pad()

    # note plan in Hz, 16 beats
    bass = [73.4, 73.4, 65.4, 73.4, 82.4, 73.4, 65.4, 55.0,
            73.4, 73.4, 98.0, 87.3, 73.4, 65.4, 55.0, 73.4]
    bell = [293.7, 0, 0, 349.2, 0, 0, 293.7, 0,
            392.0, 0, 0, 349.2, 0, 293.7, 0, 220.0]
    pad = 146.8

    data += set_freq(2, pad) + key(2, True)

    loop_start = 0
    for i, hz in enumerate(bass):
        data += set_freq(0, hz) + key(0, True)
        if bell[i]:
            data += set_freq(1, bell[i]) + key(1, True)
        # PSG ember pulse on beats 0,4,8,12
        if i % 4 == 0:
            data += psg_tone(0, 0x1C0, 8)
        else:
            data += psg_off(0)
        data += wait_frames(4)
        data += key(0, False)
        if bell[i]:
            data += key(1, False)
        data += wait_frames(FRAMES_PER_BEAT - 4)

    data += psg_off(0)
    loop_end = len(data)
    data += bytes((0x66,))

    header = bytearray(0x100)
    header[0:4] = b"Vgm "
    header[0x08:0x0C] = u32(0x00000170)
    header[0x0C:0x10] = u32(SN76489)
    header[0x2C:0x30] = u32(YM2612)
    header[0x34:0x38] = u32(0x100 - 0x34)
    header[0x24:0x28] = u32((BEATS * FRAMES_PER_BEAT) * FRAME)  # loop samples
    header[0x1C:0x20] = u32((BEATS * FRAMES_PER_BEAT) * FRAME)  # total samples
    # loop offset: relative to 0x1C, points at loop_start in data
    # VGM loop offset is relative to 0x1C
    loop_abs = 0x100 + loop_start
    header[0x20:0x24] = u32(loop_abs - 0x1C)
    eof = 0x100 + len(data) - 4
    header[0x04:0x08] = u32(eof)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(bytes(header) + bytes(data))
    print(f"wrote {OUT} bytes={OUT.stat().st_size} loop_frames={BEATS * FRAMES_PER_BEAT} unused_tail={len(data)-loop_end}")


if __name__ == "__main__":
    main()
