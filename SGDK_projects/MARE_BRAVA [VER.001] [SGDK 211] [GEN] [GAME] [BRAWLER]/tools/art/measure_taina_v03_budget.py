#!/usr/bin/env python3
"""Measure the TAINA v03 scale alternatives with the corrected VDP model."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "rascunho/taina_visual_challengers_v03"
CANDIDATES = BASE / "candidates"
SIM_PATH = ROOT.parents[1] / "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py"
spec = importlib.util.spec_from_file_location("vdp_scanline_simulator", SIM_PATH)
simulator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(simulator)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tile_metrics(path: Path) -> dict:
    image = Image.open(path).convert("P")
    width, height = image.size
    pixels = image.load()
    tiles = []
    for ty in range(0, height, 8):
        for tx in range(0, width, 8):
            tile = tuple(pixels[x, y] for y in range(ty, min(ty + 8, height))
                         for x in range(tx, min(tx + 8, width)))
            tiles.append(tile)
    visible = [(x, y) for y in range(height) for x in range(width) if pixels[x, y] != 0]
    bbox = [min(x for x, _ in visible), min(y for _, y in visible),
            max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]
    return {
        "raw_tiles": len(tiles),
        "unique_tiles": len(set(tiles)),
        "vram_raw_bytes": len(tiles) * 32,
        "vram_unique_bytes": len(set(tiles)) * 32,
        "dma_upload_upper_bound_bytes": len(set(tiles)) * 32,
        "visible_pixels": len(visible),
        "visible_bbox": bbox,
        "visible_bbox_width": bbox[2] - bbox[0],
        "visible_bbox_height": bbox[3] - bbox[1],
    }


def sprite(name: str, x: int, y: int, width: int, height: int) -> dict:
    return {"name": name, "x": x, "y": y, "w": width, "h": height}


def scene_sprites(hero_w: int, hero_h: int, enemy_count: int) -> list[dict]:
    sprites = [sprite("taina", (320 - hero_w) // 2, 192 - hero_h, hero_w, hero_h)]
    # Deliberately collocated on the fight lane to test the hardware ceiling.
    # This is a stress layout, not a recommendation for wave choreography.
    cria = enemy_count // 2
    estivador = enemy_count - cria
    for i in range(cria):
        sprites.append(sprite(f"cria_{i + 1}", 32 + i * 28, 128, 44, 64))
    for i in range(estivador):
        sprites.append(sprite(f"estivador_{i + 1}", 168 + i * 56, 128, 56, 64))
    return sprites


def measure_scale(asset_id: str, width: int, height: int) -> dict:
    candidate = CANDIDATES / asset_id / f"{asset_id}.png"
    metrics = tile_metrics(candidate)
    scenarios = {}
    inputs = {}
    for enemy_count, label in ((4, "hero_plus_four_enemies"), (6, "next_ambitious_step_6_enemies")):
        data = {
            "display_mode": "h40",
            "headroom_justification": "stress layout for TAINA scale gate; gameplay wave manager spaces actors",
            "sprites": scene_sprites(width, height, enemy_count),
        }
        input_path = BASE / "budget" / f"vdp_input_{asset_id}_{enemy_count}enemies.json"
        input_path.parent.mkdir(parents=True, exist_ok=True)
        input_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        inputs[label] = str(input_path.relative_to(ROOT))
        scenarios[label] = simulator.simulate(data)
    return {
        "asset_id": asset_id,
        "scale": f"{width}x{height}",
        "width": width,
        "height": height,
        "candidate_sha256": sha(candidate),
        "tile_metrics": metrics,
        "hardware_cells": {
            "cells_per_frame": math.ceil(width / 32) * math.ceil(height / 32),
            "cell_decomposition": f"{math.ceil(width / 32)}x{math.ceil(height / 32)} <=32x32 VDP cells",
        },
        "camera": {"width": 320, "height": 224, "ground_y": 192,
                   "footprint": [120, 192 - height, width, height],
                   "hitbox": "undeclared_requires_collision_contract"},
        "enemy_model": {
            "cria": {"declared_footprint": [44, 64], "cell_count": 4, "tile_measurement": "not_available_for_v03_scale_gate"},
            "estivador": {"declared_footprint": [56, 64], "cell_count": 4, "tile_measurement": "not_available_for_v03_scale_gate"},
            "layout_note": "2 CRIA + 2 ESTIVADOR for required case; 3 + 3 is the next measured degree",
        },
        "vdp_inputs": inputs,
        "scenarios": scenarios,
    }


def main() -> int:
    scales = []
    for asset_id, width, height in (
        ("taina_48x64_challenger_a", 48, 64),
        ("taina_48x64_challenger_b", 48, 64),
        ("taina_64x96_challenger_a", 64, 96),
        ("taina_64x96_challenger_b", 64, 96),
    ):
        scales.append(measure_scale(asset_id, width, height))
    report = {
        "schema_version": "1.0.0",
        "status": "measured_review_only",
        "tool": "vdp_scanline_simulator",
        "tool_version": simulator.TOOL_VERSION,
        "display_mode": "h40",
        "camera": {"width": 320, "height": 224, "ground_y": 192},
        "res_touched": False,
        "hitbox_status": "undeclared_requires_collision_contract",
        "measurement_scope": "TAINA candidate + 2 CRIA + 2 ESTIVADOR, plus next degree 3 CRIA + 3 ESTIVADOR",
        "scales": scales,
        "decision": {
            "48x64": "technically less expensive; visual decision pending human gate",
            "64x96": "reopened and measured; visual/camera/gameplay decision pending human gate",
            "next_degree": "6 enemies is measured and intentionally stresses the 320-pixel scanline limit",
        },
    }
    out = BASE / "scale_budget_report_v03.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(out), "status": report["status"], "tool_version": simulator.TOOL_VERSION}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
