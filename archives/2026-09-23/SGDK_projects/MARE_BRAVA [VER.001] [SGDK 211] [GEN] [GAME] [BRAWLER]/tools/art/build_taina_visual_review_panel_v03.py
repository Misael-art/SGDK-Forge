#!/usr/bin/env python3
"""Build the v03 human review board from persisted evidence only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "rascunho/taina_visual_challengers_v03"
CANDIDATES = BASE / "candidates"
REPORT = BASE / "scale_budget_report_v03.json"
MANIFEST = CANDIDATES / "challenger_package_manifest.json"
OUT = BASE / "taina_visual_comparison_panel_v03.png"
FONT = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 14)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paste_fit(dst: Image.Image, src: Image.Image, box: tuple[int, int, int, int], resample=Image.Resampling.NEAREST) -> None:
    x, y, w, h = box
    image = src.copy()
    image.thumbnail((w, h), resample)
    px = x + (w - image.width) // 2
    py = y + (h - image.height) // 2
    if image.mode in ("RGBA", "LA"):
        dst.paste(image, (px, py), image)
    else:
        dst.paste(image, (px, py))


def camera_card(candidate: Path, width: int, height: int, out: Path) -> None:
    canvas = Image.new("RGB", (320, 224), (238, 238, 230))
    draw = ImageDraw.Draw(canvas)
    native = Image.open(candidate).convert("RGBA")
    x, y = (320 - width) // 2, 192 - height
    canvas.paste(native, (x, y), native)
    draw.rectangle((x, y, x + width - 1, y + height - 1), outline=(78, 92, 110), width=1)
    draw.line((0, 192, 319, 192), fill=(198, 82, 46), width=1)
    draw.line((x + width // 2, y, x + width // 2, 223), fill=(72, 128, 140), width=1)
    draw.text((4, 4), "320x224 camera", fill=(28, 30, 38), font=FONT)
    draw.text((4, 212), "ground_y=192  pivot=(center, ground)", fill=(28, 30, 38), font=FONT)
    canvas.save(out, optimize=True)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    budget = json.loads(REPORT.read_text(encoding="utf-8"))
    by_id = {item["asset_id"]: item for item in manifest["candidates"]}
    budget_by_id = {item["asset_id"]: item for item in budget["scales"]}

    # Board is a diagnostic artifact. Candidate pixels come only from the
    # already persisted evidence files; no image interpolation is performed.
    panel = Image.new("RGB", (1680, 1780), (28, 30, 38))
    draw = ImageDraw.Draw(panel)
    draw.text((28, 20), "TAÍNA — VISUAL CHALLENGERS v03", fill=(255, 220, 120), font=FONT)
    draw.text((28, 44), "REVIEW ONLY · no automatic winner · human decision required by asset_id + SHA-256", fill=(220, 225, 232), font=FONT)
    draw.text((28, 68), "Matte: border-connected / passed · Candidates: native 1x + NEAREST 8x · res/: untouched", fill=(180, 190, 202), font=FONT)

    # Model sheet and incumbent are explicitly comparison-only, never sources.
    model = ROOT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
    incumbent = ROOT / "data/processed/characters/taina/lineart/taina_lineart_basic_48x64_v01.png"
    draw.text((28, 104), "MODEL SHEET — approved source of identity (concept; not native asset)", fill=(255, 255, 255), font=FONT)
    paste_fit(panel, Image.open(model).convert("RGB"), (28, 122, 520, 300), Image.Resampling.LANCZOS)
    draw.rectangle((28, 122, 548, 422), outline=(110, 120, 135), width=2)
    draw.text((580, 104), "INCUMBENT — comparison_only (not a pixel source)", fill=(255, 255, 255), font=FONT)
    paste_fit(panel, Image.open(incumbent).convert("RGBA"), (580, 122, 260, 300), Image.Resampling.NEAREST)
    draw.rectangle((580, 122, 840, 422), outline=(110, 120, 135), width=2)
    draw.text((880, 122), "Human preference prior: challenger B (preliminary only)", fill=(255, 220, 120), font=FONT)
    draw.text((880, 148), "This is not approval, not a score, and not a recommendation.", fill=(220, 225, 232), font=FONT)
    draw.text((880, 182), "Footprint is visual placement only; hitbox remains", fill=(220, 225, 232), font=FONT)
    draw.text((880, 198), "undeclared_requires_collision_contract.", fill=(255, 160, 130), font=FONT)

    card_w, card_h = 800, 640
    positions = [(28, 470), (852, 470), (28, 1130), (852, 1130)]
    for (asset_id, item), (cx, cy) in zip(by_id.items(), positions):
        width, height = item["width"], item["height"]
        metrics = budget_by_id[asset_id]
        tiles = metrics["tile_metrics"]
        panel_box = (cx, cy, card_w, card_h)
        draw.rectangle((cx, cy, cx + card_w - 1, cy + card_h - 1), outline=(110, 120, 135), width=2)
        draw.text((cx + 18, cy + 14), f"{asset_id} · {width}x{height}", fill=(255, 220, 120), font=FONT)
        draw.text((cx + 18, cy + 34), f"SHA-256 {item['candidate_sha256']}", fill=(180, 190, 202), font=FONT)
        evidence = CANDIDATES / asset_id / "evidence"
        # Four views are all distinct persisted derivatives. The camera view
        # is generated below as diagnostic composition, never as an asset.
        views = [("native_1x", evidence / "native_1x.png"),
                 ("nearest_8x", evidence / "nearest_8x.png"),
                 ("light", evidence / "light_background.png"),
                 ("dark", evidence / "dark_background.png"),
                 ("chroma", evidence / "chroma_background.png")]
        for i, (label, path) in enumerate(views):
            vx = cx + 18 + i * 150
            vy = cy + 66
            draw.text((vx, vy), label, fill=(220, 225, 232), font=FONT)
            bg = Image.new("RGB", (136, 190), (238, 238, 230) if label == "light" else (28, 30, 38) if label == "dark" else (238, 0, 238) if label == "chroma" else (48, 52, 64))
            paste_fit(bg, Image.open(path).convert("RGBA"), (4, 20, 128, 166), Image.Resampling.NEAREST)
            panel.paste(bg, (vx, vy + 18))
            draw.rectangle((vx, vy + 18, vx + 135, vy + 207), outline=(110, 120, 135), width=1)
        draw.text((cx + 18, cy + 300), "camera 320x224 / pivot + ground cue", fill=(220, 225, 232), font=FONT)
        cam = evidence / "camera_320x224.png"
        camera_card(CANDIDATES / asset_id / f"{asset_id}.png", width, height, cam)
        paste_fit(panel, Image.open(cam).convert("RGB"), (cx + 18, cy + 320, 320, 224), Image.Resampling.NEAREST)
        draw.rectangle((cx + 18, cy + 320, cx + 338, cy + 544), outline=(110, 120, 135), width=1)
        draw.text((cx + 370, cy + 322), f"cell footprint: {metrics['hardware_cells']['cell_decomposition']}", fill=(220, 225, 232), font=FONT)
        draw.text((cx + 370, cy + 342), f"raw / unique tiles: {tiles['raw_tiles']} / {tiles['unique_tiles']}", fill=(220, 225, 232), font=FONT)
        draw.text((cx + 370, cy + 362), f"VRAM unique: {tiles['vram_unique_bytes']} B", fill=(220, 225, 232), font=FONT)
        draw.text((cx + 370, cy + 382), f"DMA upper bound: {tiles['dma_upload_upper_bound_bytes']} B", fill=(220, 225, 232), font=FONT)
        scene = metrics["scenarios"]["hero_plus_four_enemies"]
        nxt = metrics["scenarios"]["next_ambitious_step_6_enemies"]
        draw.text((cx + 370, cy + 420), f"TAÍNA + 4: {scene['total_sprite_links']} links total", fill=(160, 230, 170), font=FONT)
        draw.text((cx + 370, cy + 440), f"peak: {scene['max_sprites_per_scanline']} sprites / {scene['max_sprite_pixels_per_scanline']} px", fill=(160, 230, 170), font=FONT)
        draw.text((cx + 370, cy + 478), f"next 3+3: {nxt['total_sprite_links']} links", fill=(255, 160, 130), font=FONT)
        draw.text((cx + 370, cy + 498), f"peak: {nxt['max_sprites_per_scanline']} sprites / {nxt['max_sprite_pixels_per_scanline']} px", fill=(255, 160, 130), font=FONT)
        draw.text((cx + 370, cy + 536), "visual_pass=false · promotable=false · human=not_started", fill=(255, 220, 120), font=FONT)

    panel.save(OUT, optimize=True)
    # Register camera evidence hashes in the manifest without changing any
    # candidate or source bytes.
    for item in manifest["candidates"]:
        cam = CANDIDATES / item["asset_id"] / "evidence/camera_320x224.png"
        item["camera_evidence"] = {"path": str(cam.relative_to(ROOT)), "sha256": sha(cam),
                                    "role": "diagnostic_only", "footprint": [120, 192 - item["height"], item["width"], item["height"]],
                                    "pivot": [120 + item["width"] // 2, 192], "ground_y": 192}
    manifest["review_panel"] = {"path": str(OUT.relative_to(ROOT)), "sha256": sha(OUT),
                                 "status": "human_gate_pending", "automatic_scoring": False,
                                 "human_preference_prior": "challenger_b_preliminary_only"}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
