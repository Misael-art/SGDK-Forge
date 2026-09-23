#!/usr/bin/env python3
"""Build the runtime jab strip from only the three non-idle raster frames."""

from pathlib import Path
import hashlib
import json

from PIL import Image


PROJECT = Path(__file__).resolve().parents[2]
SOURCE = (
    PROJECT
    / "rascunho/taina_combo_hit_1_jab_v01"
    / "taina_combo_hit_1_jab_native_64x64_v01.png"
)
PROCESSED = (
    PROJECT
    / "data/processed/characters/taina/animation"
    / "taina_combo_hit_1_jab_runtime_unique_64x64_v02.png"
)
RUNTIME = (
    PROJECT
    / "res/sprites/characters/taina"
    / "taina_combo_hit_1_jab_runtime_unique_64x64_v02.png"
)
REPORT = (
    PROJECT
    / "doc/art/characters/taina/animation"
    / "taina_combo_hit_1_jab_runtime_unique_build_v02.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = Image.open(SOURCE)
    if source.mode != "P" or source.size != (320, 64):
        raise SystemExit(f"unexpected source contract: mode={source.mode} size={source.size}")

    # Physical frames 1..3 are launch, active contact and recoil. Logical
    # anticipation/recovery reuse the already resident idle definition.
    unique = source.crop((64, 0, 256, 64))
    unique.putpalette(source.getpalette())
    unique.info["transparency"] = 0

    for destination in (PROCESSED, RUNTIME):
        destination.parent.mkdir(parents=True, exist_ok=True)
        unique.save(destination, optimize=False, bits=4, transparency=0)

    report = {
        "schema_version": "1.0.0",
        "report_id": "taina_combo_hit_1_jab_runtime_unique_build_v02",
        "generated_at": "2026-07-29",
        "status": "built",
        "source": str(SOURCE.relative_to(PROJECT)),
        "source_sha256": sha256(SOURCE),
        "output": str(RUNTIME.relative_to(PROJECT)),
        "output_sha256": sha256(RUNTIME),
        "geometry_px": [192, 64],
        "cell_px": [64, 64],
        "physical_frame_count": 3,
        "physical_frames": ["launch", "active_contact", "follow_through_recoil"],
        "logical_phase_count": 5,
        "idle_reuse": {
            "anticipation": "spr_taina_idle_guard frame 0",
            "recovery_bridge": "spr_taina_idle_guard frame 0",
        },
        "removed_duplicate_cells": [
            "old jab frame 0 duplicated idle_guard frame 0",
            "old jab frame 4 duplicated old jab frame 0",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
