from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "data" / "processed" / "celestial_chase_v001" / "source_baked_pixel_art_candidates_v001"
OUT_DIR = SOURCE_DIR / "runtime_animation_validation_v005"
PROJECT = ROOT / "SGDK_projects" / "Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]"
RES_DUST = PROJECT / "res" / "sprites" / "chase" / "pursuer_impact_dust_fx_64x32_strip_v005.png"

FRAME_W = 64
FRAME_H = 32
FRAME_COUNT = 6

# Mega Drive-native intensity steps, with index 0 reserved for transparency.
PALETTE = [
    (238, 0, 238),     # transparent key
    (0, 0, 34),        # cold outline
    (34, 0, 68),       # purple deep shadow
    (68, 68, 68),      # smoke dark
    (102, 102, 102),   # smoke mid
    (170, 170, 136),   # smoke light
    (238, 170, 34),    # impact gold
    (238, 238, 170),   # ivory hot core
    (136, 102, 68),    # road dust brown
    (204, 136, 34),    # warm dust
    (68, 34, 68),      # ember purple
    (238, 204, 102),   # gold highlight
    (34, 34, 34),      # dark ground cut
    (102, 68, 34),     # low dirt
    (170, 102, 34),    # orange debris
    (238, 238, 238),   # white spark
]


def set_px(img: Image.Image, x: int, y: int, color: int) -> None:
    if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
        img.putpixel((x, y), color)


def draw_slope(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: int, width: int = 1) -> None:
    if len(points) > 1:
        draw.line(points, fill=color, width=width)


def draw_puff(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, color: int, outline: int = 3) -> None:
    draw.rectangle((x + 2, y, x + w - 3, y + h - 1), fill=color)
    draw.rectangle((x, y + 2, x + w - 1, y + h - 3), fill=color)
    draw.line((x + 1, y + 1, x + w - 2, y + 1), fill=outline)
    draw.line((x + 1, y + h - 2, x + w - 2, y + h - 2), fill=outline)


def draw_frame(frame_index: int) -> Image.Image:
    img = Image.new("P", (FRAME_W, FRAME_H), 0)
    draw = ImageDraw.Draw(img)

    if frame_index == 0:
        draw_slope(draw, [(18, 24), (29, 22), (39, 23), (52, 25)], 5)
        draw_slope(draw, [(22, 26), (40, 26), (56, 27)], 8)
        draw.rectangle((29, 21, 37, 23), fill=6)
        draw.point([(28, 20), (38, 20), (41, 22)], fill=11)
    elif frame_index == 1:
        draw_puff(draw, 8, 20, 16, 7, 4)
        draw_puff(draw, 42, 20, 17, 7, 4)
        draw_slope(draw, [(4, 24), (18, 21), (30, 20)], 5, 2)
        draw_slope(draw, [(34, 20), (48, 21), (62, 24)], 5, 2)
        draw.polygon([(26, 18), (34, 15), (42, 19), (36, 24), (27, 23)], fill=6)
        draw.line([(26, 18), (34, 15), (42, 19), (36, 24), (27, 23), (26, 18)], fill=1)
        draw.line((27, 20, 40, 20), fill=11)
        for p in [(14, 16), (19, 14), (45, 14), (51, 16), (56, 19)]:
            set_px(img, p[0], p[1], 14)
    elif frame_index == 2:
        draw_puff(draw, 4, 18, 20, 9, 4)
        draw_puff(draw, 24, 20, 14, 7, 5)
        draw_puff(draw, 42, 18, 20, 9, 4)
        draw_slope(draw, [(1, 27), (15, 24), (31, 23), (48, 24), (63, 27)], 3, 1)
        draw.polygon([(21, 20), (32, 16), (45, 21), (36, 27), (22, 25)], fill=9)
        draw.line([(21, 20), (32, 16), (45, 21), (36, 27), (22, 25), (21, 20)], fill=1)
        draw.line((23, 22, 43, 22), fill=7)
        draw.line((10, 17, 3, 14), fill=10)
        draw.line((54, 17, 62, 14), fill=10)
    elif frame_index == 3:
        draw_puff(draw, 2, 20, 18, 7, 3)
        draw_puff(draw, 19, 21, 14, 6, 4)
        draw_puff(draw, 37, 21, 14, 6, 4)
        draw_puff(draw, 50, 20, 13, 7, 3)
        draw_slope(draw, [(4, 25), (18, 23), (30, 24)], 5)
        draw_slope(draw, [(34, 24), (48, 23), (62, 25)], 5)
        draw.line((23, 18, 34, 21), fill=6)
        draw.line((33, 20, 45, 18), fill=11)
        for p in [(9, 16), (15, 15), (48, 15), (56, 16)]:
            set_px(img, p[0], p[1], 10)
    elif frame_index == 4:
        draw_slope(draw, [(2, 24), (14, 22), (24, 23)], 4)
        draw_slope(draw, [(40, 23), (52, 22), (63, 24)], 4)
        draw.rectangle((10, 26, 24, 27), fill=13)
        draw.rectangle((39, 26, 56, 27), fill=13)
        draw.line((23, 19, 31, 21), fill=5)
        draw.line((37, 21, 47, 19), fill=5)
        for p in [(12, 19), (19, 17), (45, 17), (55, 19)]:
            set_px(img, p[0], p[1], 3)
    else:
        # Deliberately blank settle frame. The runtime hides after the visible burst.
        pass

    img.putpalette([component for rgb in PALETTE for component in rgb])
    img.info["transparency"] = 0
    return img


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RES_DUST.parent.mkdir(parents=True, exist_ok=True)

    frames = [draw_frame(i) for i in range(FRAME_COUNT)]
    strip = Image.new("P", (FRAME_W * FRAME_COUNT, FRAME_H), 0)
    strip.putpalette(frames[0].getpalette()[:48])
    strip.info["transparency"] = 0
    for i, frame in enumerate(frames):
        strip.paste(frame, (i * FRAME_W, 0))

    processed_strip = OUT_DIR / "pursuer_impact_dust_fx_64x32_strip_v005.png"
    strip.save(processed_strip, optimize=True, transparency=0, bits=4)
    strip.save(RES_DUST, optimize=True, transparency=0, bits=4)

    zoom = Image.new("RGBA", (FRAME_W * FRAME_COUNT * 4, FRAME_H * 4 + 18), (18, 18, 26, 255))
    draw = ImageDraw.Draw(zoom)
    for i, frame in enumerate(frames):
        crop = frame.convert("RGBA").resize((FRAME_W * 4, FRAME_H * 4), Image.Resampling.NEAREST)
        x = i * FRAME_W * 4
        zoom.alpha_composite(crop, (x, 0))
        draw.text((x + 4, FRAME_H * 4 + 2), f"D{i}", fill=(245, 245, 245, 255))
    zoom_path = OUT_DIR / "pursuer_impact_dust_fx_64x32_strip_v005_zoom4.png"
    zoom.save(zoom_path)

    report = {
        "schema": "celestial_chase_impact_fx_v005",
        "status": "generated_source_baked_pixel_fx",
        "standard": "Source_Baked_Pixel_Art_Standard",
        "asset": str(processed_strip),
        "promoted_asset": str(RES_DUST),
        "zoom_board": str(zoom_path),
        "frame_size": [FRAME_W, FRAME_H],
        "frame_count": FRAME_COUNT,
        "visible_frames": ["D0", "D1", "D2", "D3", "D4"],
        "blank_settle_frame": "D5",
        "palette_entries": len(PALETTE),
        "sha256": sha256(processed_strip),
        "runtime_intent": "short impact burst triggered on boss B3; dust animates independently instead of freezing on a single frame",
    }
    report_path = OUT_DIR / "pursuer_impact_dust_fx_v005_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": "ok", "asset": str(processed_strip), "promoted_asset": str(RES_DUST), "report": str(report_path)}, indent=2))


if __name__ == "__main__":
    main()
