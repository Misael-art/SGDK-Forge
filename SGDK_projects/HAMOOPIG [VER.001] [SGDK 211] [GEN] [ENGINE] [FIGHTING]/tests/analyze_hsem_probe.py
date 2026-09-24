#!/usr/bin/env python3
"""Decode the semantic combat-state block exported by the ROM.

HSEM is diagnostic telemetry, not a gameplay approval.  It complements HPRB
with aggregate distance/state/input observations while preserving HPRB's byte
layout for older evidence bundles.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

HSEM_OFFSET = 0x580
SIGNATURE = b"HSEM"
SCHEMA_SIZE = {1: (54, 23)}
FIELDS = (
    "frame_hi", "frame_lo", "samples", "min_distance", "max_distance",
    "guard_frames_p1", "guard_frames_p2", "attack_frames_p1",
    "attack_frames_p2", "fireball_frames_p1", "fireball_frames_p2",
    "throw_frames_p1", "throw_frames_p2", "last_x_p1", "last_x_p2",
    "last_state_p1", "last_state_p2", "last_guard_p1", "last_guard_p2",
    "last_attack_button_p1", "last_attack_button_p2", "last_special_p1",
    "last_special_p2",
)


class HsemError(Exception):
    pass


def decode(data: bytes) -> dict:
    if len(data) < HSEM_OFFSET + 8:
        raise HsemError(f"too short for header: {len(data)} bytes")
    if data[HSEM_OFFSET:HSEM_OFFSET + 4] != SIGNATURE:
        raise HsemError("HSEM signature missing")
    schema, size = struct.unpack_from(">HH", data, HSEM_OFFSET + 4)
    if schema not in SCHEMA_SIZE:
        raise HsemError(f"unsupported HSEM schema {schema}")
    expected, words = SCHEMA_SIZE[schema]
    if size != expected:
        raise HsemError(f"schema {schema} declares size {size}, expected {expected}")
    need = HSEM_OFFSET + size
    if len(data) < need:
        raise HsemError(f"truncated HSEM block: {len(data)} bytes, need {need}")
    values = struct.unpack_from(f">{words}H", data, HSEM_OFFSET + 8)
    result = dict(zip(FIELDS, values))
    result["video_frame"] = (result.pop("frame_hi") << 16) | result.pop("frame_lo")
    result["schema"] = schema
    result["declared_size"] = size
    result["words"] = words
    result["evidence_scope"] = "HSEM SRAM snapshot from BlastEm; diagnostic only"
    return result


def _block(values=None, *, signature=SIGNATURE, schema=1, size=54):
    values = list(values or [])
    values += [0] * (23 - len(values))
    return (b"\0" * HSEM_OFFSET + signature + struct.pack(">HH", schema, size)
            + struct.pack(">23H", *values[:23]))


def self_check() -> int:
    failures = []
    valid = decode(_block([0, 123, 123, 0, 160, 0, 7, 40, 10]))
    if valid["video_frame"] != 123 or valid["guard_frames_p2"] != 7:
        failures.append("fixture válida não decodificou campos básicos")
    for name, blob in (
        ("signature", _block(signature=b"BAD!")),
        ("schema", _block(schema=2, size=56)),
        ("size", _block(size=52)),
        ("truncated", _block()[:-1]),
    ):
        try:
            decode(blob)
        except HsemError:
            continue
        failures.append(f"entrada inválida {name} aceita")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: HSEM decoder self-check")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sram", nargs="?", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check or args.sram is None:
        return self_check()
    result = decode(args.sram.read_bytes())
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
