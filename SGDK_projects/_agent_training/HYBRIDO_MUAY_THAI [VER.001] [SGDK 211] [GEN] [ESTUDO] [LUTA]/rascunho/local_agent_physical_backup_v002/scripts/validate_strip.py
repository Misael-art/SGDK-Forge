#!/usr/bin/env python3
"""Validate one-action Mega Drive animation strip contracts.

Input: JSON matching tools/sgdk_wrapper/schemas/animation_strip_contract.schema.json.
Output: JSON report with status, blockers, warnings, and measured drift.

This validator is intentionally conservative. It blocks metadata-only assets,
multi-action sheets, non-horizontal frame order, pivot drift, bbox drift, and
palette drift when the strip contract forbids it.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.0.0"


@dataclass
class StripCheck:
    status: str
    blockers: list[str]
    warnings: list[str]
    metrics: dict[str, Any]


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def validate_strip(data: dict[str, Any]) -> StripCheck:
    blockers: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}

    if data.get("asset_kind") != "animation_strip":
        blockers.append("asset_kind_not_animation_strip")

    if data.get("metadata_only") is True:
        blockers.append("metadata_only_asset_not_approved")

    if data.get("strip_layout") != "horizontal_single_action":
        blockers.append("strip_not_horizontal_single_action")

    action = data.get("action")
    actions = data.get("actions")
    if not isinstance(action, str) or not action.strip():
        blockers.append("missing_single_action")
    if isinstance(actions, list) and len(actions) != 1:
        blockers.append("multi_action_sheet")

    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        blockers.append("missing_frames")
        return StripCheck("error", blockers, warnings, metrics)

    declared_count = _as_int(data.get("frame_count"), -1)
    if declared_count != len(frames):
        blockers.append("frame_count_mismatch")

    thresholds = data.get("drift_thresholds") or {}
    pivot_limit = _as_int(thresholds.get("pivot_px"), 0)
    bbox_limit = _as_int(thresholds.get("bbox_px"), 0)
    palette_change_allowed = bool(thresholds.get("palette_changed_allowed", False))

    first = frames[0]
    base_y = _as_int(first.get("y"))
    base_w = _as_int(first.get("w"))
    base_h = _as_int(first.get("h"))
    base_pivot_x = _as_int(first.get("pivot_x"))
    base_pivot_y = _as_int(first.get("pivot_y"))

    max_pivot_drift = 0
    max_bbox_drift = 0
    last_x = -1
    seen_indexes: set[int] = set()

    for expected_index, frame in enumerate(frames):
        index = _as_int(frame.get("index"), -1)
        x = _as_int(frame.get("x"), -1)
        y = _as_int(frame.get("y"), -1)
        w = _as_int(frame.get("w"), -1)
        h = _as_int(frame.get("h"), -1)
        pivot_x = _as_int(frame.get("pivot_x"), 0)
        pivot_y = _as_int(frame.get("pivot_y"), 0)

        if index in seen_indexes:
            blockers.append(f"duplicate_frame_index:{index}")
        seen_indexes.add(index)

        if index != expected_index:
            warnings.append(f"non_sequential_frame_index:{index}")

        if x <= last_x:
            blockers.append(f"frame_x_not_increasing:{index}")
        last_x = x

        if y != base_y:
            blockers.append(f"frame_y_drift:{index}")

        pivot_drift = max(abs(pivot_x - base_pivot_x), abs(pivot_y - base_pivot_y))
        bbox_drift = max(abs(w - base_w), abs(h - base_h))
        max_pivot_drift = max(max_pivot_drift, pivot_drift)
        max_bbox_drift = max(max_bbox_drift, bbox_drift)

        if not frame.get("phase"):
            blockers.append(f"missing_motion_phase:{index}")

    if max_pivot_drift > pivot_limit:
        blockers.append("pivot_drift_over_threshold")
    if max_bbox_drift > bbox_limit:
        blockers.append("bbox_drift_over_threshold")

    palette_hash = data.get("palette_hash")
    frame_palette_hashes = {
        frame.get("palette_hash")
        for frame in frames
        if isinstance(frame, dict) and frame.get("palette_hash")
    }
    if palette_hash and frame_palette_hashes and frame_palette_hashes != {palette_hash}:
        if palette_change_allowed:
            warnings.append("palette_changed_but_allowed")
        else:
            blockers.append("palette_drift_over_threshold")

    metrics.update(
        {
            "frame_count": len(frames),
            "max_pivot_drift_px": max_pivot_drift,
            "max_bbox_drift_px": max_bbox_drift,
            "horizontal_order": "ok" if "frame_x_not_increasing" not in blockers else "error",
        }
    )

    return StripCheck("ok" if not blockers else "error", blockers, warnings, metrics)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def self_check() -> int:
    valid = {
        "schema_version": "1.0.0",
        "asset_id": "hero_idle",
        "asset_kind": "animation_strip",
        "action": "idle",
        "strip_layout": "horizontal_single_action",
        "frame_count": 2,
        "visual_dna_manifest": "visual_dna_manifest.example.json",
        "motion_phase_map": "motion_phase_map.md",
        "pivot_policy": "bottom_center_feet",
        "drift_thresholds": {
            "pivot_px": 0,
            "bbox_px": 0,
            "palette_changed_allowed": False,
            "scale_percent": 0
        },
        "approval_status": "approved_for_sheet",
        "frames": [
            {"index": 0, "x": 0, "y": 0, "w": 32, "h": 48, "pivot_x": 16, "pivot_y": 47, "phase": "hold"},
            {"index": 1, "x": 32, "y": 0, "w": 32, "h": 48, "pivot_x": 16, "pivot_y": 47, "phase": "settle"}
        ]
    }
    invalid = dict(valid)
    invalid["actions"] = ["idle", "run"]
    invalid["metadata_only"] = True

    valid_report = validate_strip(valid)
    invalid_report = validate_strip(invalid)
    if valid_report.status != "ok":
        print("self-check failed: valid sample rejected", file=sys.stderr)
        return 1
    if invalid_report.status != "error" or "multi_action_sheet" not in invalid_report.blockers:
        print("self-check failed: invalid sample was not blocked", file=sys.stderr)
        return 1
    print("validate_strip self-check passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="animation strip contract JSON")
    parser.add_argument("--output", type=Path, help="optional report output path")
    parser.add_argument("--self-check", action="store_true", help="run built-in self-check")
    args = parser.parse_args(argv)

    if args.self_check:
        return self_check()
    if not args.input:
        parser.error("--input is required unless --self-check is used")

    report = validate_strip(load_json(args.input))
    payload = {
        "tool_name": "validate_strip",
        "tool_version": TOOL_VERSION,
        "status": report.status,
        "blockers": report.blockers,
        "warnings": report.warnings,
        "metrics": report.metrics,
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
