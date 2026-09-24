#!/usr/bin/env python3
"""Decode the HCAD logic-to-video presentation ledger from save.sram."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

SCHEMA = {1: 40}
FIELDS = (
    "video_frames", "logic_ticks", "zero_tick_frames", "one_tick_frames",
    "two_tick_frames", "max_ticks_per_frame", "presentation_commits",
    "presentation_without_logic", "fight_video_frames", "fight_logic_ticks",
    "fight_presentation_commits", "fight_zero_tick_frames", "last_logic_ticks",
    "last_scene", "region_hz", "timing_profile",
)


def decode(path: Path) -> dict:
    raw = path.read_bytes()
    offset = raw.find(b"HCAD")
    if offset < 0:
        raise ValueError("HCAD block missing")
    schema, total_bytes = struct.unpack_from(">HH", raw, offset + 4)
    if schema not in SCHEMA or total_bytes != SCHEMA[schema]:
        raise ValueError(f"unsupported HCAD schema/size: {schema}/{total_bytes}")
    words = struct.unpack_from(">16H", raw, offset + 8)
    report = {name: value for name, value in zip(FIELDS, words)}
    report["schema"] = schema
    report["cadence_invariant"] = (
        report["video_frames"] == report["presentation_commits"]
        and report["logic_ticks"] == (
            report["zero_tick_frames"] * 0
            + report["one_tick_frames"]
            + report["two_tick_frames"] * 2
        )
    )
    report["fight_cadence_invariant"] = (
        report["fight_video_frames"] == report["fight_presentation_commits"]
        and report["fight_logic_ticks"] <= report["logic_ticks"]
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sram", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = decode(args.sram)
    text = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["cadence_invariant"] and report["fight_cadence_invariant"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
