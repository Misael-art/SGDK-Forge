#!/usr/bin/env python3
"""Render a deterministic nearest-neighbour GIF from the canonical VBlank timing."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from animation_validation_common import load_object, resolve_inside, sha256_file


TOOL_VERSION = "1.0.0"


def render(contract: dict, project_root: Path, output: Path, scale: int) -> dict:
    artifact = contract["artifact"]
    source_path = resolve_inside(project_root, artifact["path"])
    if sha256_file(source_path) != artifact["sha256"]:
        raise ValueError("strip_artifact_sha_mismatch")
    timing = contract["timing_contract"]
    holds = timing["frame_holds_vblank"]
    if len(holds) != len(contract["frames"]):
        raise ValueError("runtime_timing_contract_mismatch")
    hz = float(timing["vblank_hz"])
    with Image.open(source_path) as source:
        source.load()
        frames = []
        for frame in contract["frames"]:
            crop = source.crop((frame["x"], frame["y"], frame["x"] + frame["w"], frame["y"] + frame["h"]))
            if scale != 1:
                crop = crop.resize((crop.width * scale, crop.height * scale), Image.Resampling.NEAREST)
            frames.append(crop)
    durations = [max(10, round(value * 1000.0 / hz / 10.0) * 10) for value in holds]
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=durations,
                   loop=0 if timing.get("loop") else 1, disposal=2,
                   transparency=int(artifact.get("transparent_index", 0)))
    return {
        "tool_name": "render_animation_evidence",
        "tool_version": TOOL_VERSION,
        "status": "rendered",
        "output": output.as_posix(),
        "output_sha256": sha256_file(output),
        "frame_holds_vblank": holds,
        "gif_durations_ms": durations,
        "scale": scale,
    }


def self_check() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        strip = Image.new("P", (32, 16), 0)
        strip.putpalette([0, 0, 0, 255, 255, 255] + [0, 0, 0] * 254)
        draw = ImageDraw.Draw(strip)
        draw.rectangle((3, 3, 10, 12), outline=1)
        draw.rectangle((20, 2, 28, 12), outline=1)
        strip_path = root / "strip.png"
        strip.save(strip_path, bits=4, transparency=0)
        contract = {
            "artifact": {"path": "strip.png", "sha256": sha256_file(strip_path), "transparent_index": 0},
            "frames": [
                {"x": 0, "y": 0, "w": 16, "h": 16},
                {"x": 16, "y": 0, "w": 16, "h": 16},
            ],
            "timing_contract": {"vblank_hz": 60, "loop": True, "frame_holds_vblank": [6, 12]},
        }
        output = root / "preview.gif"
        report = render(contract, root, output, 2)
        with Image.open(output) as gif:
            durations = []
            for index in range(gif.n_frames):
                gif.seek(index)
                durations.append(int(gif.info.get("duration", 0)))
    if report["gif_durations_ms"] != [100, 200] or durations != [100, 200]:
        print(f"self-check failed: deterministic timing mismatch: {report} actual={durations}", file=sys.stderr)
        return 1
    print("render_animation_evidence self-check passed (nearest scale, canonical VBlank timing)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if not args.contract or not args.project_root or not args.output:
        parser.error("--contract, --project-root and --output are required")
    if args.scale < 1:
        parser.error("--scale must be >= 1")
    try:
        report = render(load_object(args.contract), args.project_root.resolve(), args.output.resolve(), args.scale)
    except (KeyError, ValueError, OSError) as exc:
        print(json.dumps({"status": "error", "blocker": str(exc)}), file=sys.stderr)
        return 1
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
