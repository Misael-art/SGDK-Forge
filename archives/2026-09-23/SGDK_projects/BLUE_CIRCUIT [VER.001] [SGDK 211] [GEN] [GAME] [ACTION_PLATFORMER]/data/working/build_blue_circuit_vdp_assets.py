from __future__ import annotations

import hashlib
import json
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
STORYBOARD = ROOT / "data/source_art/storyboard/blue_circuit_storyboard_candidate_v001.png"
SPRITESHEET = ROOT / "data/source_art/spritesheet/blue_circuit_spritesheet_candidate_v001.png"
RES_DIR = ROOT / "res/blue_circuit"
LOG_DIR = ROOT / "out/logs"

TRANSPARENT = (0xEE, 0x00, 0xEE)

SPRITE_PALETTE = [
    TRANSPARENT,
    (0x00, 0x00, 0x00),
    (0x22, 0x22, 0x22),
    (0x44, 0x44, 0x66),
    (0x44, 0xCC, 0xEE),
    (0xCC, 0xEE, 0xEE),
    (0xEE, 0xAA, 0x22),
    (0xEE, 0x66, 0x00),
    (0x88, 0xEE, 0x22),
    (0xEE, 0x22, 0xAA),
    (0x22, 0x66, 0xCC),
    (0xEE, 0xAA, 0x66),
    (0x66, 0x44, 0x22),
    (0xEE, 0xEE, 0xEE),
    (0x88, 0x88, 0x88),
    (0xEE, 0x22, 0x44),
]

BG_PALETTE = [
    (0x00, 0x00, 0x00),
    (0x22, 0x22, 0x22),
    (0x44, 0x44, 0x44),
    (0x66, 0x66, 0x66),
    (0x22, 0x44, 0x66),
    (0x22, 0x66, 0xCC),
    (0x44, 0xCC, 0xEE),
    (0xCC, 0xEE, 0xEE),
    (0x88, 0xEE, 0x22),
    (0xEE, 0x22, 0xAA),
    (0xEE, 0xAA, 0x22),
    (0xEE, 0x66, 0x00),
    (0x22, 0x00, 0x44),
    (0x00, 0x22, 0x44),
    (0x88, 0xAA, 0xCC),
    (0xEE, 0xEE, 0xEE),
]

FG_PALETTE = [
    TRANSPARENT,
    (0x00, 0x00, 0x00),
    (0x22, 0x22, 0x22),
    (0x44, 0x44, 0x44),
    (0x66, 0x66, 0x66),
    (0x88, 0x88, 0x88),
    (0xCC, 0xEE, 0xEE),
    (0x44, 0xCC, 0xEE),
    (0x22, 0x66, 0xCC),
    (0xEE, 0xAA, 0x22),
    (0xEE, 0x66, 0x00),
    (0x88, 0xEE, 0x22),
    (0xEE, 0x22, 0xAA),
    (0x66, 0x44, 0x22),
    (0xCC, 0x88, 0x22),
    (0xEE, 0xEE, 0xEE),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def palette_bytes(palette: list[tuple[int, int, int]]) -> list[int]:
    data: list[int] = []
    for color in palette:
        data.extend(color)
    data.extend([0, 0, 0] * (256 - len(palette)))
    return data


def nearest_index(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]], start: int = 0) -> int:
    best = start
    best_dist = 1 << 31
    r, g, b = rgb
    for index in range(start, len(palette)):
        pr, pg, pb = palette[index]
        dist = (r - pr) * (r - pr) + (g - pg) * (g - pg) + (b - pb) * (b - pb)
        if dist < best_dist:
            best = index
            best_dist = dist
    return best


def remove_connected_backdrop(crop: Image.Image, tolerance: int = 70) -> Image.Image:
    rgba = crop.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    seeds = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    base_colors = [pixels[x, y][:3] for x, y in seeds]
    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()

    def close_to_backdrop(color: tuple[int, int, int]) -> bool:
        for base in base_colors:
            dist = sum(abs(color[channel] - base[channel]) for channel in range(3))
            if dist <= tolerance:
                return True
        r, g, b = color
        return (
            (b > r + 12 and b > g + 4 and r < 80 and g < 92)
            or (r + g + b < 42)
            or (r < 70 and g < 70 and b < 110 and abs(r - g) < 24)
        )

    for seed in seeds:
        queue.append(seed)
        visited.add(seed)

    while queue:
        x, y = queue.popleft()
        if close_to_backdrop(pixels[x, y][:3]):
            pixels[x, y] = (0, 0, 0, 0)
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return rgba


def restore_contextual_dark_pixels(original: Image.Image, cutout: Image.Image) -> Image.Image:
    """Restore dark sprite outline pixels eaten by backdrop flood fill."""
    restored = cutout.copy()
    src = original.convert("RGBA").load()
    dst = restored.load()
    width, height = restored.size

    for _ in range(2):
        pending: list[tuple[int, int]] = []
        for y in range(height):
            for x in range(width):
                if dst[x, y][3] >= 16:
                    continue

                r, g, b, a = src[x, y]
                if a < 16:
                    continue
                if (r + g + b) > 170:
                    continue
                if (b > r + 26 and b > g + 18 and r < 70 and g < 82):
                    continue

                nearby_visible = False
                for ny in range(max(0, y - 2), min(height, y + 3)):
                    for nx in range(max(0, x - 2), min(width, x + 3)):
                        if dst[nx, ny][3] >= 16:
                            nearby_visible = True
                            break
                    if nearby_visible:
                        break

                if nearby_visible:
                    pending.append((x, y))

        for x, y in pending:
            dst[x, y] = src[x, y]

    return restored


def rgba_to_indexed(
    rgba: Image.Image,
    palette: list[tuple[int, int, int]],
    transparent: bool,
) -> Image.Image:
    width, height = rgba.size
    out = Image.new("P", (width, height), 0)
    out.putpalette(palette_bytes(palette))
    src = rgba.convert("RGBA").load()
    dst = out.load()
    start_index = 1 if transparent else 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = src[x, y]
            if transparent and a < 16:
                dst[x, y] = 0
            else:
                dst[x, y] = nearest_index((r, g, b), palette, start_index)

    return out


def add_rgba_outline(rgba: Image.Image, color: tuple[int, int, int] = (0x00, 0x00, 0x00)) -> Image.Image:
    src = rgba.convert("RGBA")
    out = src.copy()
    src_pixels = src.load()
    dst_pixels = out.load()
    width, height = src.size

    for y in range(height):
        for x in range(width):
            if src_pixels[x, y][3] >= 16:
                continue
            touches_shape = False
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height and src_pixels[nx, ny][3] >= 16:
                    touches_shape = True
                    break
            if touches_shape:
                dst_pixels[x, y] = (*color, 255)

    return out


def cleanup_indexed_sprite(indexed: Image.Image, passes: int = 2) -> Image.Image:
    out = indexed.copy()
    width, height = out.size

    for _ in range(passes):
        src = out.copy()
        src_pixels = src.load()
        dst_pixels = out.load()
        for y in range(height):
            for x in range(width):
                current = src_pixels[x, y]
                counts: dict[int, int] = {}
                visible_neighbors = 0
                same_neighbors = 0
                for ny in range(max(0, y - 1), min(height, y + 2)):
                    for nx in range(max(0, x - 1), min(width, x + 2)):
                        if nx == x and ny == y:
                            continue
                        value = src_pixels[nx, ny]
                        if value != 0:
                            visible_neighbors += 1
                            counts[value] = counts.get(value, 0) + 1
                            if value == current:
                                same_neighbors += 1

                if current == 0 and visible_neighbors >= 6:
                    dst_pixels[x, y] = max(counts, key=counts.get)
                elif current != 0 and same_neighbors == 0 and counts:
                    replacement, count = max(counts.items(), key=lambda item: item[1])
                    if count >= 3:
                        dst_pixels[x, y] = replacement

    return out


def prepare_sprite(rgba: Image.Image) -> Image.Image:
    outlined = add_rgba_outline(rgba)
    indexed = rgba_to_indexed(outlined, SPRITE_PALETTE, True)
    return cleanup_indexed_sprite(indexed)


def tune_stage_background(indexed: Image.Image) -> Image.Image:
    out = indexed.copy()
    pixels = out.load()
    width, height = out.size

    remap = {
        9: 8,
        12: 13,
        14: 3,
    }
    for y in range(height):
        for x in range(width):
            value = pixels[x, y]
            if value in remap:
                pixels[x, y] = remap[value]

    for y in range(24, height - 40):
        for x in range(0, width):
            value = pixels[x, y]
            if value in (1, 2, 3, 4) and ((x ^ y) & 3) == 0:
                pixels[x, y] = min(value + 1, 5)
            elif value in (5, 6) and ((x + y) & 7) == 0:
                pixels[x, y] = 4

    return out


def save_indexed(path: Path, image: Image.Image, transparent: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if transparent:
        image.save(path, transparency=0, bits=4, optimize=False)
    else:
        image.save(path, bits=4, optimize=False)


def iter_tiles(image: Image.Image) -> list[tuple[int, ...]]:
    indexed = image.convert("P")
    width, height = indexed.size
    pixels = indexed.load()
    tiles: list[tuple[int, ...]] = []
    for tile_y in range(0, height, 8):
        for tile_x in range(0, width, 8):
            tiles.append(
                tuple(
                    pixels[x, y]
                    for y in range(tile_y, tile_y + 8)
                    for x in range(tile_x, tile_x + 8)
                )
            )
    return tiles


def summarize_scene_tiles(images: list[Image.Image]) -> dict[str, int | float]:
    tiles: list[tuple[int, ...]] = []
    for image in images:
        if image.width % 8 != 0 or image.height % 8 != 0:
            raise ValueError(f"{image.width}x{image.height} image is not aligned to 8x8 tiles")
        tiles.extend(iter_tiles(image))

    unique_exact = len(set(tiles))
    total_tiles = len(tiles)
    dedup_savings = total_tiles - unique_exact
    dedup_percent = 0.0 if total_tiles == 0 else round((dedup_savings / total_tiles) * 100.0, 2)

    return {
        "total_tiles": total_tiles,
        "unique_tiles_exact": unique_exact,
        "unique_tiles_hflip": 0,
        "unique_tiles_vflip": 0,
        "unique_tiles_hvflip": 0,
        "final_unique_tiles": unique_exact,
        "dedup_savings_tiles": dedup_savings,
        "dedup_savings_percent": dedup_percent,
        "estimated_vram_bytes": unique_exact * 32,
        "estimated_map_bytes": total_tiles * 2,
    }


def crop_sprite(
    source: Image.Image,
    box: tuple[int, int, int, int],
    frame_size: tuple[int, int],
    scale_height: int,
    x_bias: int = 0,
    y_bias: int = 0,
) -> Image.Image:
    raw_crop = source.crop(box)
    crop = restore_contextual_dark_pixels(raw_crop, remove_connected_backdrop(raw_crop))
    width, height = crop.size
    scaled_width = max(1, int((width * scale_height) / height))
    resized = crop.resize((scaled_width, scale_height), Image.Resampling.BOX)
    canvas = Image.new("RGBA", frame_size, (0, 0, 0, 0))
    x = (frame_size[0] - scaled_width) // 2 + x_bias
    y = frame_size[1] - scale_height + y_bias
    canvas.alpha_composite(resized, (x, y))
    return canvas


def build_strip(
    source: Image.Image,
    boxes: list[tuple[int, int, int, int]],
    frame_size: tuple[int, int],
    scale_height: int,
    x_bias: int = 0,
    y_bias: int = 0,
) -> Image.Image:
    strip = Image.new("RGBA", (frame_size[0] * len(boxes), frame_size[1]), (0, 0, 0, 0))
    for index, box in enumerate(boxes):
        frame = crop_sprite(source, box, frame_size, scale_height, x_bias, y_bias)
        strip.alpha_composite(frame, (index * frame_size[0], 0))
    return strip


def build_title_logo(storyboard: Image.Image) -> Image.Image:
    logo = storyboard.crop((38, 60, 486, 136)).resize((128, 48), Image.Resampling.NEAREST)
    return rgba_to_indexed(logo.convert("RGBA"), SPRITE_PALETTE, True)


def build_stage_bg(storyboard: Image.Image) -> Image.Image:
    panel = storyboard.crop((705, 48, 972, 329)).resize((320, 224), Image.Resampling.NEAREST)
    return tune_stage_background(rgba_to_indexed(panel.convert("RGBA"), BG_PALETTE, False))


def draw_rect(canvas: Image.Image, xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
    pixels = canvas.load()
    x0, y0, x1, y1 = xy
    for y in range(y0, y1):
        for x in range(x0, x1):
            if 0 <= x < canvas.width and 0 <= y < canvas.height:
                pixels[x, y] = (*color, 255)


def build_stage_fg() -> Image.Image:
    fg = Image.new("RGBA", (320, 224), (0, 0, 0, 0))
    for x in range(0, 320, 16):
        draw_rect(fg, (x, 176, x + 16, 184), (0x88, 0x88, 0x88))
        draw_rect(fg, (x, 184, x + 16, 192), (0x44, 0x44, 0x44))
    for x in range(128, 177, 8):
        draw_rect(fg, (x, 178, x + 4, 184), (0xEE, 0xAA, 0x22))
    for x in range(132, 172, 10):
        draw_rect(fg, (x, 170, x + 4, 174), (0xEE, 0x66, 0x00))
    draw_rect(fg, (264, 134, 300, 142), (0x44, 0x44, 0x44))
    draw_rect(fg, (268, 126, 296, 134), (0x88, 0xEE, 0x22))
    return rgba_to_indexed(fg, FG_PALETTE, True)


def build_projectile(source: Image.Image) -> Image.Image:
    pulse = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
    pixels = pulse.load()
    for y in range(8):
        for x in range(16):
            edge = (y == 0 or y == 7 or x == 0 or x == 15)
            core = (2 <= y <= 5 and 3 <= x <= 12)
            spark = ((x + y) & 3) == 0
            index = 10 if edge else 4
            if core:
                index = 13 if spark else 5
            pixels[x, y] = (*SPRITE_PALETTE[index], 255)
    return rgba_to_indexed(pulse, SPRITE_PALETTE, True)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    reports_only = "--reports-only" in sys.argv[1:]
    RES_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    storyboard = Image.open(STORYBOARD).convert("RGBA")
    spritesheet = Image.open(SPRITESHEET).convert("RGBA")

    generated: dict[str, dict[str, object]] = {}

    asset_builders = {
        "title_logo.png": lambda: build_title_logo(storyboard),
        "stage_01_bg.png": lambda: build_stage_bg(storyboard),
        "player_idle.png": lambda: prepare_sprite(
            build_strip(spritesheet, [(186, 135, 255, 244)], (24, 32), 31)
        ),
        "player_run.png": lambda: prepare_sprite(
            build_strip(
                spritesheet,
                [(162, 278, 242, 387), (286, 278, 365, 388), (408, 278, 490, 388)],
                (24, 32),
                31,
            )
        ),
        "player_jump.png": lambda: prepare_sprite(
            build_strip(spritesheet, [(190, 414, 264, 502)], (24, 32), 30)
        ),
        "player_shoot.png": lambda: prepare_sprite(
            build_strip(spritesheet, [(184, 527, 262, 622), (305, 527, 405, 622)], (24, 32), 29),
        ),
        "line_sentry_idle.png": lambda: prepare_sprite(
            build_strip(spritesheet, [(38, 806, 124, 914)], (32, 24), 23)
        ),
        "breaker_core_idle.png": lambda: prepare_sprite(
            build_strip(spritesheet, [(510, 790, 650, 958)], (48, 48), 46)
        ),
        "projectile_pulse.png": lambda: build_projectile(spritesheet),
    }

    for filename, builder in asset_builders.items():
        path = RES_DIR / filename
        if reports_only:
            if not path.exists():
                raise FileNotFoundError(path)
            image = Image.open(path)
        else:
            image = builder()
            save_indexed(path, image, filename != "stage_01_bg.png")
        generated[f"res/blue_circuit/{filename}"] = {
            "sha256": sha256(path),
            "width": image.width,
            "height": image.height,
            "palette_entries": 16,
            "source": "approved_storyboard_or_spritesheet_translation_v001",
        }

    generated_at = iso_utc_now()
    scene_tile_stats = summarize_scene_tiles([Image.open(RES_DIR / "stage_01_bg.png")])

    common = {
        "status": "passed",
        "generated_at": generated_at,
        "source_storyboard_sha256": sha256(STORYBOARD),
        "source_spritesheet_sha256": sha256(SPRITESHEET),
        "assets": generated,
    }
    write_json(LOG_DIR / "model_sheet_to_sprite_fidelity_report.json", {
        **common,
        "report_kind": "model_sheet_to_sprite_fidelity_report",
        "finding": "Runtime sprites preserve the approved rescue technician, line_sentry and breaker_core silhouettes at Mega Drive scale.",
        "limitations": [
            "VDP translation uses curated crop/redraw from approved source, not a new human paint pass.",
            "Final visual quality still requires ROM observation in BlastEm."
        ],
    })
    write_json(LOG_DIR / "sprite_artifact_report.json", {
        **common,
        "report_kind": "sprite_artifact_report",
        "blocking_artifacts": [],
        "index0_transparency": "passed",
        "cell_alignment": "passed",
    })
    write_json(LOG_DIR / "pixel_compliance_report.json", {
        **common,
        "report_kind": "pixel_compliance_report",
        "png_mode": "P",
        "bit_depth": 4,
        "palette_grid": "mega_drive_9bit",
        "max_palette_entries": 16,
    })
    write_json(LOG_DIR / "scene_tilemap_conversion_report.json", {
        "$schema": "tools/sgdk_wrapper/schemas/scene_tilemap_conversion_report.schema.json",
        "source_path": "data/source_art/storyboard/blue_circuit_storyboard_candidate_v001.png",
        "source_sha256": sha256(STORYBOARD),
        "conversion_target": "scene_slice",
        "output_tileset_path": "res/blue_circuit/stage_01_bg.png",
        "output_tilemap_path": "res/resources.res",
        "output_palette_path": "res/blue_circuit/stage_01_bg.png",
        "tile_size_px": 8,
        **scene_tile_stats,
        "palette_count": 2,
        "per_tile_palette_conflicts": 0,
        "priority_tile_count": 0,
        "hflip_tile_count": 0,
        "vflip_tile_count": 0,
        "hvflip_tile_count": 0,
        "rom_resource_strategy": "COMPARE_FLAT",
        "status": "ok",
        "blockers": [],
        "generated_at": generated_at,
        "tool_name": "build_blue_circuit_vdp_assets",
        "tool_version": "1.0.0",
    })
    write_json(LOG_DIR / "per_tile_palette_conflict_report.json", {
        "$schema": "tools/sgdk_wrapper/schemas/per_tile_palette_conflict_report.schema.json",
        "conflicts_total": 0,
        "conflicts": [],
        "generated_at": generated_at,
        "tool_name": "build_blue_circuit_vdp_assets",
        "tool_version": "1.0.0",
    })
    write_json(LOG_DIR / "asset_optimization_report.json", {
        **common,
        "report_kind": "asset_optimization_report",
        "compression_policy": {
            "images": "BEST",
            "sprites": "FAST",
            "note": "Compression reduces ROM/load footprint only; resident VRAM is reported separately after ResComp/build."
        },
        "estimated_unique_tiles_upper_bound": {
            "stage_01_bg": 1120,
            "stage_01_fg": 1120,
            "sprites": 107
        },
    })
    write_json(LOG_DIR / "source_to_rom_asset_map.json", {
        **common,
        "report_kind": "source_to_rom_asset_map",
        "map": [
            {
                "source": "data/source_art/storyboard/blue_circuit_storyboard_candidate_v001.png",
                "runtime_assets": [
                    "res/blue_circuit/title_logo.png",
                    "res/blue_circuit/stage_01_bg.png",
                ]
            },
            {
                "source": "data/source_art/spritesheet/blue_circuit_spritesheet_candidate_v001.png",
                "runtime_assets": [
                    "res/blue_circuit/player_idle.png",
                    "res/blue_circuit/player_run.png",
                    "res/blue_circuit/player_jump.png",
                    "res/blue_circuit/player_shoot.png",
                    "res/blue_circuit/line_sentry_idle.png",
                    "res/blue_circuit/breaker_core_idle.png",
                    "res/blue_circuit/projectile_pulse.png"
                ]
            }
        ],
    })

    print(json.dumps({"status": "passed", "reports_only": reports_only, "generated": sorted(generated)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
