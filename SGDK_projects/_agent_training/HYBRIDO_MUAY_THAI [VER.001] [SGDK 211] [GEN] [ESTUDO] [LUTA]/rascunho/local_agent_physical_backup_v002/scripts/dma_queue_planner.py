#!/usr/bin/env python3
"""Plan and validate conservative VBlank DMA queues.

Input: JSON object with ops array. Each op needs bytes and timing. Valid timing
values are vblank, preload, loading, and active_frame. Active frame DMA is
blocked because MegaDrive_DEV only treats DMA as safe in VBlank or honest load.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.0.0"
DEFAULT_VBLANK_BYTE_BUDGET = 7168


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def plan(data: dict[str, Any]) -> dict[str, Any]:
    budget = _int(data.get("vblank_byte_budget"), DEFAULT_VBLANK_BYTE_BUDGET)
    ops = data.get("ops") or []
    bytes_by_frame: dict[int, int] = defaultdict(int)
    blockers: list[str] = []
    warnings: list[str] = []
    planned_ops: list[dict[str, Any]] = []

    for index, op in enumerate(ops):
        if not isinstance(op, dict):
            blockers.append(f"invalid_dma_op:{index}")
            continue
        timing = op.get("timing")
        size = _int(op.get("bytes"))
        frame = _int(op.get("frame"), 0)
        if timing == "active_frame":
            blockers.append(f"dma_outside_vblank:{index}")
        elif timing not in {"vblank", "preload", "loading"}:
            blockers.append(f"unknown_dma_timing:{index}")

        if timing == "vblank":
            bytes_by_frame[frame] += size
        planned_ops.append(
            {
                "index": index,
                "frame": frame,
                "bytes": size,
                "timing": timing,
                "target": op.get("target", "unknown")
            }
        )

    over_budget_frames = [
        {"frame": frame, "bytes": count, "budget": budget}
        for frame, count in sorted(bytes_by_frame.items())
        if count > budget
    ]
    if over_budget_frames:
        blockers.append("vblank_dma_bytes_over_budget")

    near_budget_frames = [
        {"frame": frame, "bytes": count, "budget": budget}
        for frame, count in sorted(bytes_by_frame.items())
        if budget * 0.85 <= count <= budget
    ]
    if near_budget_frames:
        warnings.append("vblank_dma_near_budget")

    return {
        "tool_name": "dma_queue_planner",
        "tool_version": TOOL_VERSION,
        "status": "ok" if not blockers else "error",
        "vblank_byte_budget": budget,
        "ops": planned_ops,
        "bytes_by_frame": dict(sorted(bytes_by_frame.items())),
        "over_budget_frames": over_budget_frames,
        "near_budget_frames": near_budget_frames,
        "blockers": blockers,
        "warnings": warnings,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def self_check() -> int:
    ok = plan({"ops": [{"frame": 0, "timing": "vblank", "bytes": 1024, "target": "tiles"}]})
    bad = plan({"ops": [{"frame": 0, "timing": "active_frame", "bytes": 32, "target": "cram"}]})
    if ok["status"] != "ok":
        print("self-check failed: valid DMA queue rejected", file=sys.stderr)
        return 1
    if bad["status"] != "error" or "dma_outside_vblank:0" not in bad["blockers"]:
        print("self-check failed: unsafe DMA was not blocked", file=sys.stderr)
        return 1
    print("dma_queue_planner self-check passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if not args.input:
        parser.error("--input is required unless --self-check is used")
    report = plan(load_json(args.input))
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
