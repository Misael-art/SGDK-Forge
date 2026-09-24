#!/usr/bin/env python3
"""Decode the HSTR special-state trace exported by the ROM."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

OFFSET = 0x700
CAPACITY = 128
RECORD_WORDS = 16
SIZE = 8 + 8 + CAPACITY * (2 + RECORD_WORDS * 2)
FIELDS = (
    "presentation_frame", "probe_frame", "game_frame", "scene", "logic_ticks",
    "p1_state", "p1_anim_frame", "p1_anim_frame_total", "p1_frame_time",
    "p1_frame_time_total", "p1_fireball_active", "p1_fireball_x",
    "p1_fireball_y", "p1_input_bits", "p1_attack_button", "p1_hit_pause",
)


def decode(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) < OFFSET + 8 or raw[OFFSET:OFFSET + 4] != b"HSTR":
        raise ValueError("HSTR block missing")
    schema, declared = struct.unpack_from(">HH", raw, OFFSET + 4)
    if schema != 1 or declared != SIZE:
        raise ValueError(f"unsupported HSTR schema/size: {schema}/{declared}")
    if len(raw) < OFFSET + declared:
        raise ValueError("truncated HSTR block")
    count, write_index, record_words, capacity = struct.unpack_from(">4H", raw, OFFSET + 8)
    if record_words != RECORD_WORDS or capacity != CAPACITY or count > CAPACITY:
        raise ValueError("invalid HSTR dimensions")
    cursor = OFFSET + 16
    records = []
    for _ in range(CAPACITY):
        record_index = struct.unpack_from(">H", raw, cursor)[0]
        cursor += 2
        values = struct.unpack_from(">16H", raw, cursor)
        cursor += 32
        if record_index == 0xFFFF:
            continue
        record = dict(zip(FIELDS, values))
        record["record_index"] = record_index
        records.append(record)
    if len(records) != count:
        raise ValueError(f"HSTR count mismatch: header={count}, records={len(records)}")
    return {
        "schema": schema,
        "declared_size": declared,
        "count": count,
        "write_index": write_index,
        "records": records,
        "first_presentation_frame": records[0]["presentation_frame"] if records else None,
        "last_presentation_frame": records[-1]["presentation_frame"] if records else None,
        "states": sorted({record["p1_state"] for record in records}),
        "anim_frames": sorted({record["p1_anim_frame"] for record in records}),
        "fireball_active_records": sum(record["p1_fireball_active"] != 0 for record in records),
        "evidence_scope": "HSTR special-state ring from same-ROM BlastEm SRAM; diagnostic correlation only",
    }


def self_check() -> int:
    blob = bytearray(OFFSET + SIZE)
    blob[OFFSET:OFFSET + 4] = b"HSTR"
    struct.pack_into(">HH", blob, OFFSET + 4, 1, SIZE)
    struct.pack_into(">4H", blob, OFFSET + 8, 1, 1, RECORD_WORDS, CAPACITY)
    cursor = OFFSET + 16
    for index in range(1, CAPACITY):
        blank = cursor + index * (2 + RECORD_WORDS * 2)
        struct.pack_into(">H", blob, blank, 0xFFFF)
    struct.pack_into(">H", blob, cursor, 0)
    struct.pack_into(">16H", blob, cursor + 2, 77, 77, 12, 10, 1, 700, 4, 12, 1, 5, 1, 200, 100, 3, 0, 0)
    path = Path("/tmp/hamoopig_hstr_self_check.sram")
    path.write_bytes(blob)
    decoded = decode(path)
    if decoded["count"] != 1 or decoded["records"][0]["p1_state"] != 700:
        print("FAIL: HSTR did not round-trip")
        return 1
    print("PASS: HSTR decoder self-check")
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
