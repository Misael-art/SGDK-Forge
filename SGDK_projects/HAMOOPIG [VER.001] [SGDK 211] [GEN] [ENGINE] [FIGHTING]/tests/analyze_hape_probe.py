#!/usr/bin/env python3
"""Decode HAMOOPIG's hash-bound presentation-event SRAM record.

HAPE is state context written at the same presentation boundary as HANC.  It
does not convert the runtime counter into a video PTS or approve perception.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

OFFSET = 0x1920
SIGNATURE = b"HAPE"
SCHEMA = 1
BYTES = 60


def decode(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < OFFSET + BYTES or raw[OFFSET:OFFSET + 4] != SIGNATURE:
        raise ValueError("HAPE block missing")
    schema, declared = struct.unpack_from(">HH", raw, OFFSET + 4)
    if schema != SCHEMA or declared != BYTES:
        raise ValueError(f"unsupported HAPE schema/size: {schema}/{declared}")
    words = struct.unpack_from(">26H", raw, OFFSET + 8)

    def u32(index: int) -> int:
        return (words[index] << 16) | words[index + 1]

    return {
        "schema": schema,
        "bytes": declared,
        "marker_id": words[0],
        "runtime_presentation_frame": u32(1),
        "probe_frame": u32(3),
        "game_frame": u32(5),
        "scene": words[7],
        "logic_ticks": words[8],
        "gameplay_event": bool(words[9]),
        "p1_state": words[10],
        "p1_anim_frame": words[11],
        "p1_anim_frame_total": words[12],
        "p1_frame_time": words[13],
        "p1_frame_time_total": words[14],
        "p1_fireball_active": bool(words[15]),
        "p1_fireball_x": words[16],
        "p1_fireball_y": words[17],
        "p1_input_bits": words[18],
        "p1_attack_button": words[19],
        "p1_hit_pause": words[20],
        "pre_sprite_dma_bytes": words[21],
        "sprite_dma_delta_bytes": words[22],
        "active_sprites": words[23],
        "used_vdp_sprites": words[24],
        "scanline_peak": words[25],
        "evidence_scope": "same-boundary runtime state context; not video PTS, scanout timestamp or perceptual approval",
    }


def self_check() -> int:
    raw = bytearray(OFFSET + BYTES)
    raw[OFFSET:OFFSET + 4] = SIGNATURE
    struct.pack_into(">HH", raw, OFFSET + 4, SCHEMA, BYTES)
    words = [0] * 26
    words[0] = 0x8001
    words[1] = 0
    words[2] = 2288
    words[7] = 10
    words[8] = 1
    words[9] = 1
    words[10] = 700
    words[15] = 1
    struct.pack_into(">26H", raw, OFFSET + 8, *words)
    path = Path("/tmp/hamoopig_hape_self_check.sram")
    path.write_bytes(raw)
    value = decode(path)
    assert value["runtime_presentation_frame"] == 2288
    assert value["p1_state"] == 700 and value["p1_fireball_active"]
    print("PASS: HAPE decoder self-check")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sram", nargs="?", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        return self_check()
    if args.sram is None:
        parser.error("sram is required unless --self-check is used")
    print(json.dumps(decode(args.sram.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
