#!/usr/bin/env python3
"""Decode the hash-bound HDBG runtime state snapshot/trace."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

OFFSET = 0x600
FIELDS = (
    "scene", "clock_l", "clock_r", "clock_tick", "p1_energy", "p2_energy",
    "p1_state", "p2_state", "result_timer", "pause_ko", "frames_lo",
    "frames_hi", "p1_anim_frame", "p1_anim_frame_total", "p1_frame_time",
    "p1_frame_time_total", "p1_fireball_active", "p1_fireball_x",
    "p1_fireball_y", "p1_attack_button", "p1_down_input", "p1_right_input",
    "p1_x_input", "presentation_frame",
)


def decode(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < OFFSET + 8 or raw[OFFSET:OFFSET + 4] != b"HDBG":
        raise ValueError("HDBG block missing")
    schema, size = struct.unpack_from(">HH", raw, OFFSET + 4)
    if schema != 2 or size != 56:
        raise ValueError(f"unsupported HDBG schema/size: {schema}/{size}")
    if len(raw) < OFFSET + size:
        raise ValueError("truncated HDBG block")
    values = struct.unpack_from(">24H", raw, OFFSET + 8)
    result = dict(zip(FIELDS, values))
    result["frames"] = (result.pop("frames_hi") << 16) | result.pop("frames_lo")
    result["schema"] = schema
    result["declared_size"] = size
    result["evidence_scope"] = "HDBG live special-frame state snapshot from BlastEm; diagnostic only"
    return result


def self_check() -> int:
    values = list(range(24))
    blob = bytearray(OFFSET + 56)
    blob[OFFSET:OFFSET + 4] = b"HDBG"
    struct.pack_into(">HH", blob, OFFSET + 4, 2, 56)
    struct.pack_into(">24H", blob, OFFSET + 8, *values)
    path = Path("/tmp/hamoopig_hdbg_self_check.sram")
    path.write_bytes(blob)
    decoded = decode(path)
    if decoded["frames"] != (11 << 16) | 10 or decoded["p1_anim_frame"] != 12:
        print("FAIL: HDBG fields do not round-trip")
        return 1
    print("PASS: HDBG decoder self-check")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sram", nargs="?", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check or args.sram is None:
        return self_check()
    result = decode(args.sram)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
