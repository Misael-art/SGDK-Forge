#!/usr/bin/env python3
"""Validate YM2612 patch ranges and obvious DAC/FM ownership hazards.

Input: JSON object with one patch or a patches array. Output: JSON report.
The validator checks operator ranges, algorithm/feedback ranges, and obvious
clipping risk signals. It does not replace emulator listening tests.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.0.0"

RANGES = {
    "detune": (0, 7),
    "multiple": (0, 15),
    "total_level": (0, 127),
    "rate_scaling": (0, 3),
    "attack_rate": (0, 31),
    "decay_rate": (0, 31),
    "sustain_rate": (0, 31),
    "release_rate": (0, 15),
    "sustain_level": (0, 15),
}


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _validate_patch(patch: dict[str, Any], index: int) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []

    algorithm = _int(patch.get("algorithm"), -1)
    feedback = _int(patch.get("feedback"), -1)
    if not 0 <= algorithm <= 7:
        blockers.append(f"patch_{index}_algorithm_out_of_range")
    if not 0 <= feedback <= 7:
        blockers.append(f"patch_{index}_feedback_out_of_range")

    operators = patch.get("operators")
    if not isinstance(operators, list) or len(operators) != 4:
        blockers.append(f"patch_{index}_operator_count_not_4")
        return blockers, warnings

    loud_ops = 0
    for op_index, op in enumerate(operators):
        if not isinstance(op, dict):
            blockers.append(f"patch_{index}_operator_{op_index}_invalid")
            continue
        for field, (minimum, maximum) in RANGES.items():
            value = _int(op.get(field), minimum)
            if not minimum <= value <= maximum:
                blockers.append(f"patch_{index}_operator_{op_index}_{field}_out_of_range")
        if _int(op.get("total_level"), 127) <= 4:
            loud_ops += 1

    if loud_ops >= 3:
        warnings.append(f"patch_{index}_clipping_risk_many_loud_operators")

    if patch.get("uses_dac") is True and patch.get("channel") not in {"FM_CH6_DAC", "CH6"}:
        blockers.append(f"patch_{index}_dac_not_on_channel_6")

    return blockers, warnings


def validate(data: dict[str, Any]) -> dict[str, Any]:
    patches = data.get("patches")
    if patches is None:
        patches = [data]
    blockers: list[str] = []
    warnings: list[str] = []
    for index, patch in enumerate(patches):
        if not isinstance(patch, dict):
            blockers.append(f"patch_{index}_invalid")
            continue
        b, w = _validate_patch(patch, index)
        blockers.extend(b)
        warnings.extend(w)
    return {
        "tool_name": "ym2612_patch_validator",
        "tool_version": TOOL_VERSION,
        "status": "ok" if not blockers else "error",
        "patch_count": len(patches),
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
    op = {
        "detune": 0,
        "multiple": 1,
        "total_level": 24,
        "rate_scaling": 0,
        "attack_rate": 31,
        "decay_rate": 12,
        "sustain_rate": 4,
        "release_rate": 7,
        "sustain_level": 3
    }
    ok = validate({"algorithm": 4, "feedback": 2, "channel": "FM_CH1", "operators": [op, op, op, op]})
    bad_op = dict(op)
    bad_op["attack_rate"] = 99
    bad = validate({"algorithm": 9, "feedback": 2, "channel": "FM_CH1", "operators": [bad_op, op, op, op]})
    if ok["status"] != "ok":
        print("self-check failed: valid patch rejected", file=sys.stderr)
        return 1
    if bad["status"] != "error":
        print("self-check failed: invalid patch not rejected", file=sys.stderr)
        return 1
    print("ym2612_patch_validator self-check passed")
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
    report = validate(load_json(args.input))
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
