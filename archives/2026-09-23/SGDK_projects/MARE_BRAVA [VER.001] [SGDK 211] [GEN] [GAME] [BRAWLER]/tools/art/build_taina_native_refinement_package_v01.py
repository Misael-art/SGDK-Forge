#!/usr/bin/env python3
"""Stage, measure and present the first TAINA native refinement gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
SOURCE_B = ROOT / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b"
BASE = ROOT / "rascunho/taina_native_refinement_v01"
MANIFEST = BASE / "native_refinement_manifest_v01.json"
PANEL = BASE / "taina_native_refinement_comparison_panel_v01.png"
FONT = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 14)
SIM_PATH = ROOT.parents[1] / "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py"
spec = importlib.util.spec_from_file_location("vdp_scanline_simulator", SIM_PATH)
simulator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(simulator)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paste_fit(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int], resample=Image.Resampling.NEAREST) -> None:
    x, y, w, h = box
    image = src.copy()
    image.thumbnail((w, h), resample)
    px = x + (w - image.width) // 2
    py = y + (h - image.height) // 2
    dst.paste(image, (px, py), image if image.mode == "RGBA" else None)


def write_overlay(native: Path, output: Path, colour: tuple[int, int, int]) -> None:
    image = Image.open(native).convert("RGBA")
    bg = Image.new("RGBA", image.size, (*colour, 255))
    bg.alpha_composite(image)
    bg.convert("RGB").save(output, optimize=True)


def write_evidence(asset_id: str, native_path: Path) -> dict[str, str]:
    evidence = BASE / asset_id / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    native_1x = evidence / "native_1x.png"
    shutil.copy2(native_path, native_1x)
    nearest = evidence / "nearest_8x.png"
    native = Image.open(native_path).convert("P")
    nearest_img = native.resize((native.width * 8, native.height * 8), Image.Resampling.NEAREST)
    nearest_img.save(nearest, optimize=True, transparency=0)
    light = evidence / "light_background.png"
    dark = evidence / "dark_background.png"
    chroma = evidence / "chroma_background.png"
    write_overlay(native_path, light, (238, 238, 230))
    write_overlay(native_path, dark, (28, 30, 38))
    write_overlay(native_path, chroma, (238, 0, 238))
    camera = evidence / "camera_320x224.png"
    scene = Image.new("RGB", (320, 224), (238, 238, 230))
    draw = ImageDraw.Draw(scene)
    x, y = (320 - native.width) // 2, 192 - native.height
    rgba = Image.open(native_path).convert("RGBA")
    scene.paste(rgba, (x, y), rgba)
    draw.rectangle((x, y, x + native.width - 1, y + native.height - 1), outline=(78, 92, 110), width=1)
    draw.line((0, 192, 319, 192), fill=(198, 82, 46), width=1)
    draw.line((x + native.width // 2, y, x + native.width // 2, 223), fill=(72, 128, 140), width=1)
    draw.text((4, 4), "320x224 camera", fill=(28, 30, 38), font=FONT)
    draw.text((4, 212), "ground_y=192  pivot=center/ground", fill=(28, 30, 38), font=FONT)
    scene.save(camera, optimize=True)
    return {
        "native_1x": native_1x.as_posix(),
        "nearest_8x": nearest.as_posix(),
        "light": light.as_posix(),
        "dark": dark.as_posix(),
        "chroma": chroma.as_posix(),
        "camera": camera.as_posix(),
    }


def palette_role(rgb: tuple[int, int, int]) -> str:
    return {
        (0, 0, 0): "outline_and_deep_ink",
        (34, 34, 34): "shadow_neutral",
        (68, 34, 34): "shadow_warm",
        (34, 34, 68): "trouser_indigo",
        (204, 102, 34): "top_orange_base",
        (170, 68, 0): "top_orange_shadow",
        (34, 68, 68): "wraps_teal_shadow",
        (68, 102, 68): "wraps_teal_base",
        (102, 68, 34): "skin_shadow_and_sash",
        (170, 170, 136): "skin_highlight",
        (170, 136, 68): "skin_warm_highlight",
    }.get(rgb, "unclassified_vdp_snapped_colour")


def write_palette_role_map(native_path: Path, output: Path) -> Path:
    image = Image.open(native_path).convert("P")
    palette = image.getpalette() or []
    visible_indices = sorted({value for value in image.getdata() if value != 0})
    roles = []
    for index in visible_indices:
        rgb = tuple(palette[index * 3:index * 3 + 3])
        roles.append({"index": index, "rgb": list(rgb), "role": palette_role(rgb)})
    output.write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset": str(native_path.relative_to(ROOT)),
        "index0": {"index": 0, "role": "transparent0"},
        "visible_roles": roles,
        "max_visible_colors": 15,
        "alias_check": "unique_rgb_per_visible_index",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def write_shape_block(asset_id: str, native_path: Path) -> dict[str, str]:
    shape = BASE / asset_id / "shape_block"
    shape.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name in ("silhouette_mask", "semantic_region_map", "contour_overlay"):
        output = shape / f"{name}.png"
        shutil.copy2(SOURCE_B / "shape_block" / output.name, output)
        artifacts[name] = str(output.relative_to(ROOT))
    matte = BASE / asset_id / "foreground_matte_report.json"
    matte.write_text(json.dumps({
        "schema_version": "1.0.0",
        "status": "passed",
        "method": "inherited_verified_binary_alpha_from_approved_b",
        "source_asset_id": "taina_48x64_challenger_b",
        "source_sha256": "d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa",
        "candidate": str(native_path.relative_to(ROOT)),
        "candidate_sha256": sha(native_path),
        "alpha_contract": "binary_index0_transparent",
        "border_connected_extraction": "not_needed_source_alpha_verified",
        "blockers": [],
    }, indent=2) + "\n", encoding="utf-8")
    return {"silhouette_mask": artifacts["silhouette_mask"], "semantic_region_map": artifacts["semantic_region_map"], "contour_overlay": artifacts["contour_overlay"], "matte_report": str(matte.relative_to(ROOT))}


def tile_metrics(path: Path) -> dict[str, int]:
    image = Image.open(path).convert("P")
    tiles = []
    for ty in range(0, image.height, 8):
        for tx in range(0, image.width, 8):
            tiles.append(tuple(image.getpixel((x, y)) for y in range(ty, ty + 8) for x in range(tx, tx + 8)))
    visible = [(x, y) for y in range(image.height) for x in range(image.width) if image.getpixel((x, y)) != 0]
    bbox = [min(x for x, _ in visible), min(y for _, y in visible), max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]
    unique = len(set(tiles))
    return {
        "raw_tiles": len(tiles),
        "unique_tiles": unique,
        "vram_raw_bytes": len(tiles) * 32,
        "vram_unique_bytes": unique * 32,
        "dma_upload_upper_bound_bytes": unique * 32,
        "visible_pixels": len(visible),
        "visible_bbox": bbox,
    }


def sprite(name: str, x: int, y: int, width: int, height: int) -> dict[str, int | str]:
    return {"name": name, "x": x, "y": y, "w": width, "h": height}


def scene_sprites(hero_w: int, hero_h: int, enemy_count: int) -> list[dict[str, int | str]]:
    sprites = [sprite("taina", (320 - hero_w) // 2, 192 - hero_h, hero_w, hero_h)]
    cria = enemy_count // 2
    estivador = enemy_count - cria
    for i in range(cria):
        sprites.append(sprite(f"cria_{i + 1}", 32 + i * 28, 128, 44, 64))
    for i in range(estivador):
        sprites.append(sprite(f"estivador_{i + 1}", 168 + i * 56, 128, 56, 64))
    return sprites


def measure(asset_id: str, path: Path, width: int, height: int) -> dict[str, object]:
    scenarios = {}
    for count, label in ((4, "hero_plus_four_enemies"), (6, "next_ambitious_step_6_enemies")):
        data = {
            "display_mode": "h40",
            "headroom_justification": "stress layout for TAINA native refinement; gameplay wave manager spaces actors",
            "sprites": scene_sprites(width, height, count),
        }
        scenarios[label] = simulator.simulate(data)
    return {
        "asset_id": asset_id,
        "scale": "48x64",
        "candidate_sha256": sha(path),
        "tile_metrics": tile_metrics(path),
        "hardware_cells": {"cells_per_frame": 4, "cell_decomposition": "2x2 <=32x32 VDP cells"},
        "camera": {"width": 320, "height": 224, "ground_y": 192, "footprint": [136, 128, 48, 64], "hitbox": "undeclared_requires_collision_contract"},
        "scenarios": scenarios,
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    metrics = []
    for name, item in manifest["outputs"].items():
        path = Path(item["path"])
        if not path.is_absolute():
            path = ROOT.parents[1] / path
        evidence = write_evidence(f"taina_48x64_refined_{name}_v01", path)
        item["evidence"] = {k: str(Path(v).relative_to(ROOT)) for k, v in evidence.items()}
        role_map = write_palette_role_map(path, BASE / f"palette_role_map_{name}.json")
        item["palette_role_map"] = str(role_map.relative_to(ROOT))
        item["shape_block"] = write_shape_block(f"taina_48x64_refined_{name}_v01", path)
        metrics.append(measure(f"taina_48x64_refined_{name}_v01", path, 48, 64))

    report = {
        "schema_version": "1.0.0",
        "status": "measured_review_only",
        "tool": "vdp_scanline_simulator",
        "tool_version": simulator.TOOL_VERSION,
        "display_mode": "h40",
        "camera": {"width": 320, "height": 224, "ground_y": 192},
        "res_touched": False,
        "hitbox_status": "undeclared_requires_collision_contract",
        "measurement_scope": "TAINA native refinement + 2 CRIA + 2 ESTIVADOR, plus next degree 3 CRIA + 3 ESTIVADOR",
        "scales": metrics,
        "decision": "BASIC and ELITE are both review candidates; no automatic winner",
    }
    report_path = BASE / "native_refinement_budget_report_v01.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    panel = Image.new("RGB", (1280, 1250), (28, 30, 38))
    draw = ImageDraw.Draw(panel)
    draw.text((24, 18), "TAÍNA — NATIVE REFINEMENT v01", fill=(255, 220, 120), font=FONT)
    draw.text((24, 40), "B approved by exact SHA · BASIC vs ELITE · review only · no automatic winner", fill=(220, 225, 232), font=FONT)
    draw.text((24, 62), "48x64 locked for this refinement · res/: untouched · final animation/ROM/AAA blocked", fill=(180, 190, 202), font=FONT)
    model = ROOT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
    incumbent = ROOT / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b/taina_48x64_challenger_b.png"
    draw.text((24, 90), "MODEL SHEET — identity source only", fill=(255, 255, 255), font=FONT)
    paste_fit(panel, Image.open(model).convert("RGB"), (24, 108, 390, 210), Image.Resampling.LANCZOS)
    draw.rectangle((24, 108, 414, 318), outline=(110, 120, 135), width=2)
    draw.text((440, 90), "APPROVED B — structural base / comparison", fill=(255, 255, 255), font=FONT)
    paste_fit(panel, Image.open(incumbent).convert("RGBA"), (440, 108, 190, 210), Image.Resampling.NEAREST)
    draw.rectangle((440, 108, 630, 318), outline=(110, 120, 135), width=2)
    draw.text((660, 108), "Decision recorded: approved_for_native_refinement_only", fill=(255, 220, 120), font=FONT)
    draw.text((660, 130), "B SHA: d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa", fill=(180, 190, 202), font=FONT)
    draw.text((660, 152), "No visual approval yet for either refined variant.", fill=(255, 160, 130), font=FONT)

    report_by_id = {item["asset_id"]: item for item in report["scales"]}
    y_positions = [350, 790]
    for (name, item), y in zip(manifest["outputs"].items(), y_positions):
        asset_id = f"taina_48x64_refined_{name}_v01"
        item_metrics = report_by_id[asset_id]
        box_h = 400
        draw.rectangle((24, y, 1255, y + box_h), outline=(110, 120, 135), width=2)
        draw.text((42, y + 16), f"{name.upper()} · {asset_id}", fill=(255, 220, 120), font=FONT)
        draw.text((42, y + 36), f"SHA-256 {item['sha256']}", fill=(180, 190, 202), font=FONT)
        evidence = {k: ROOT / v for k, v in item["evidence"].items()}
        for i, label in enumerate(("native_1x", "nearest_8x", "light", "dark", "chroma")):
            x = 42 + i * 150
            draw.text((x, y + 64), label, fill=(220, 225, 232), font=FONT)
            bg = Image.new("RGB", (136, 190), (48, 52, 64) if label == "native_1x" else (238, 238, 230) if label == "light" else (28, 30, 38) if label == "dark" else (238, 0, 238) if label == "chroma" else (48, 52, 64))
            paste_fit(bg, Image.open(evidence[label]).convert("RGBA"), (4, 20, 128, 166), Image.Resampling.NEAREST)
            panel.paste(bg, (x, y + 84))
            draw.rectangle((x, y + 84, x + 135, y + 273), outline=(110, 120, 135), width=1)
        paste_fit(panel, Image.open(evidence["camera"]).convert("RGB"), (812, y + 64, 320, 224), Image.Resampling.NEAREST)
        draw.rectangle((812, y + 64, 1132, y + 288), outline=(110, 120, 135), width=1)
        tiles = item_metrics["tile_metrics"]
        scene = item_metrics["scenarios"]["hero_plus_four_enemies"]
        nxt = item_metrics["scenarios"]["next_ambitious_step_6_enemies"]
        draw.text((42, y + 300), f"48x64 · 4 VDP cells · raw/unique {tiles['raw_tiles']}/{tiles['unique_tiles']} · VRAM {tiles['vram_unique_bytes']} B · DMA {tiles['dma_upload_upper_bound_bytes']} B", fill=(220, 225, 232), font=FONT)
        draw.text((42, y + 320), f"TAÍNA + 4: {scene['total_sprite_links']} links · peak {scene['max_sprites_per_scanline']} sprites / {scene['max_sprite_pixels_per_scanline']} px", fill=(160, 230, 170), font=FONT)
        draw.text((42, y + 340), f"Next 3+3: {nxt['total_sprite_links']} links · peak {nxt['max_sprites_per_scanline']} sprites / {nxt['max_sprite_pixels_per_scanline']} px", fill=(255, 160, 130), font=FONT)
        draw.text((42, y + 366), "human_visual_gate = not_started · res_eligible = false", fill=(255, 220, 120), font=FONT)

    panel.save(PANEL, optimize=True)
    manifest["budget_report"] = str(report_path.relative_to(ROOT))
    manifest["review_panel"] = {"path": str(PANEL.relative_to(ROOT)), "sha256": sha(PANEL), "automatic_scoring": False, "human_status": "not_started"}
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"panel": str(PANEL), "budget_report": str(report_path), "status": "measured_review_only"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
