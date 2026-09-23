#!/usr/bin/env python3
"""Build the TAINA comparison panel and measured review report."""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_simulator(root: Path):
    path = root / "tools" / "sgdk_wrapper" / ".agent" / "scripts" / "vdp_scanline_simulator.py"
    spec = importlib.util.spec_from_file_location("vdp_scanline_simulator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def fit(img: Image.Image, box: tuple[int, int], resample=Image.Resampling.NEAREST) -> Image.Image:
    copy = img.copy()
    copy.thumbnail(box, resample=resample)
    return copy


def paste_center(dst: Image.Image, img: Image.Image, box: tuple[int, int, int, int], resample=Image.Resampling.NEAREST):
    x, y, w, h = box
    fitted = fit(img, (w, h), resample)
    px = x + (w - fitted.width) // 2
    py = y + (h - fitted.height) // 2
    if fitted.mode == "RGBA":
        dst.alpha_composite(fitted.convert("RGBA"), (px, py))
    else:
        dst.paste(fitted, (px, py))
    return (px, py, fitted.width, fitted.height)


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill=(235, 230, 198)):
    draw.text(xy, text, fill=fill, font=ImageFont.load_default())


def visible_stats(path: Path) -> tuple[int, int, int, int]:
    with Image.open(path) as img:
        indices = list(img.tobytes())
        visible = [(i % img.width, i // img.width) for i, idx in enumerate(indices) if idx != 0]
        bbox = [min(x for x, _ in visible), min(y for _, y in visible),
                max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]
        peak = max(sum(1 for x in range(img.width) if indices[y * img.width + x] != 0)
                   for y in range(img.height))
        return len(visible), bbox[2] - bbox[0], bbox[3] - bbox[1], peak


def tile_stats(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        raw = list(img.tobytes())
        tiles = []
        for ty in range(0, img.height, 8):
            for tx in range(0, img.width, 8):
                tiles.append(tuple(raw[(ty + y) * img.width + tx + x]
                                   for y in range(8) for x in range(8)))
        return len(tiles), len(set(tiles))


def budget_for(path: Path, scale: str, sim) -> dict:
    with Image.open(path) as img:
        w, h = img.size
    filled, visible_w, visible_h, peak = visible_stats(path)
    raw_tiles, unique_tiles = tile_stats(path)
    entries = math.ceil(w / 32) * math.ceil(h / 32)
    # Scene contract worst case: hero plus four medium enemies sharing a
    # 32px-high overlap band. The simulator measures both VDP limits.
    scene = [{"name": "taina", "x": 120, "y": 96, "w": w, "h": h}]
    for i in range(4):
        scene.append({"name": f"enemy_{i+1}", "x": 104 + i * 28, "y": 112,
                      "w": 32, "h": 48})
    pressure = sim.simulate({"display_mode": "h40", "sprites": scene,
                             "headroom_justification": "close-combat composition measured for TAINA review"})
    return {
        "scale": scale, "width": w, "height": h,
        "visible_pixels": filled, "visible_bbox_width": visible_w,
        "visible_bbox_height": visible_h, "worst_pose_scanline_peak_px": peak,
        "raw_tiles": raw_tiles, "unique_tiles": unique_tiles,
        "vram_raw_bytes": raw_tiles * 32, "vram_unique_bytes": unique_tiles * 32,
        "dma_upload_upper_bound_bytes": unique_tiles * 32,
        "metasprite_entries_32px_cells": entries,
        "coexistence_scene": {"hero_plus_four_enemies": pressure},
        "camera": {"width": 320, "height": 224, "ground_y": 192,
                   "cell_footprint": [120, 96, w, h],
                   "hitbox": {"status": "undeclared_requires_collision_contract"}},
    }


def camera_view(path: Path, bg=(20, 28, 39)) -> Image.Image:
    with Image.open(path) as img:
        sprite = img.convert("RGBA")
    canvas = Image.new("RGBA", (320, 224), bg + (255,))
    x = (320 - sprite.width) // 2
    y = 192 - sprite.height
    canvas.alpha_composite(sprite, (x, y))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((x, y, x + sprite.width - 1, y + sprite.height - 1), outline=(236, 196, 72, 255), width=1)
    draw.line((x + sprite.width // 2, y + sprite.height - 8,
               x + sprite.width // 2, y + sprite.height), fill=(77, 209, 195, 255), width=1)
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--package-root", type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root.resolve()
    package = args.package_root.resolve()
    manifest = json.loads((package / "candidates" / "challenger_package_manifest.json").read_text(encoding="utf-8"))
    sim = load_simulator(Path(__file__).resolve().parents[2])
    budget = []
    for item in manifest["candidates"]:
        path = root / item["candidate_path"]
        budget.append(budget_for(path, item["scale"], sim))
    budget_doc = {"schema_version": "1.0.0", "status": "measured_review_only",
                  "source": "exact_resolution_candidate_pngs", "res_touched": False,
                  "scales": budget}
    (package / "scale_budget_report.json").write_text(json.dumps(budget_doc, indent=2) + "\n", encoding="utf-8")

    panel = Image.new("RGBA", (1600, 1540), (13, 18, 28, 255))
    draw = ImageDraw.Draw(panel)
    label(draw, (24, 18), "TAINA - VISUAL CHALLENGER PANEL v02", (252, 218, 118))
    label(draw, (24, 40), "review-only | model sheet + incumbent cells + 1x/8x/light/dark/camera + footprint", (185, 198, 210))
    model = root / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
    incumbent = root / "data/processed/characters/taina/lineart/taina_lineart_basic_48x64_v01.png"
    paste_center(panel, Image.open(model).convert("RGBA"), (24, 72, 390, 270), Image.Resampling.LANCZOS)
    label(draw, (24, 348), "APPROVED MODEL SHEET (source of truth)", (252, 218, 118))
    inc = Image.open(incumbent).convert("RGBA")
    label(draw, (450, 72), "INCUMBENT — split by 48x64 cell", (252, 218, 118))
    for i in range(4):
        cell = inc.crop((i * 48, 0, (i + 1) * 48, 64))
        paste_center(panel, cell, (450 + i * 105, 96, 96, 128), Image.Resampling.NEAREST)
        label(draw, (468 + i * 105, 232), f"cell {i+1}", (185, 198, 210))
    label(draw, (450, 270), "incumbent is comparison_only; never a generation source", (140, 160, 176))

    card_w, card_h = 760, 540
    start_y = 390
    for idx, item in enumerate(manifest["candidates"]):
        col, row = idx % 2, idx // 2
        x0, y0 = 24 + col * (card_w + 16), start_y + row * (card_h + 16)
        draw.rectangle((x0, y0, x0 + card_w, y0 + card_h), outline=(67, 95, 119), width=2)
        label(draw, (x0 + 16, y0 + 12), f"{item['asset_id']}  [{item['scale']}]", (252, 218, 118))
        candidate = root / item["candidate_path"]
        evidence = root / Path(item["native_1x_path"]).parent
        images = [
            ("1x (shown 4x)", candidate, Image.Resampling.NEAREST),
            ("8x nearest", evidence / "nearest_8x.png", Image.Resampling.NEAREST),
            ("light", evidence / "light_background.png", Image.Resampling.NEAREST),
            ("dark", evidence / "dark_background.png", Image.Resampling.NEAREST),
            ("chroma", evidence / "chroma_background.png", Image.Resampling.NEAREST),
        ]
        for j, (name, image_path, sampling) in enumerate(images):
            ix = x0 + 16 + (j % 5) * 142
            iy = y0 + 48
            with Image.open(image_path) as im:
                paste_center(panel, im.convert("RGBA"), (ix, iy, 132, 250), sampling)
            label(draw, (ix + 8, y0 + 310), name, (185, 198, 210))
        cam = camera_view(candidate)
        paste_center(panel, cam, (x0 + 16, y0 + 342, 230, 160), Image.Resampling.NEAREST)
        label(draw, (x0 + 260, y0 + 356), "camera 320x224", (185, 198, 210))
        label(draw, (x0 + 260, y0 + 380), f"footprint {item['width']}x{item['height']}", (185, 198, 210))
        label(draw, (x0 + 260, y0 + 404), "yellow = cell footprint (hitbox undeclared)", (236, 196, 72))
        label(draw, (x0 + 260, y0 + 428), "cyan = pivot/ground cue", (77, 209, 195))

    panel_path = package / "taina_visual_comparison_panel.png"
    panel.convert("RGB").save(panel_path, "PNG")

    review = {
        "schema_version": "1.0.0", "status": "human_gate_pending",
        "panel": str(panel_path.relative_to(root)), "budget_report": str((package / "scale_budget_report.json").relative_to(root)),
        "source_of_truth": str(model.relative_to(root)), "incumbent_cells": 4,
        "assistant_scores": None,
        "score_status": "not_measured_requires_human_visual_decision",
        "decision_rule": "perceptual_win AND system_win",
        "recommendation": {"target_scale": None, "candidate": None,
                           "reason": "no candidate is recommended until matte, semantic regions, corrected scanline budget and human visual comparison all pass",
                           "perceptual_win": False, "system_win": False, "requires_human_approval": True},
        "notes": ["No unmeasured numeric aesthetic score is emitted.",
                  "No challenger is promoted; no res/ file is changed.",
                  "64x96 remains a valid visual challenger and is not discarded before the human gate."]
    }
    review_path = package / "taina_visual_review_report.json"
    review_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"panel": str(panel_path), "budget": str(package / "scale_budget_report.json"),
                      "review": str(review_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
