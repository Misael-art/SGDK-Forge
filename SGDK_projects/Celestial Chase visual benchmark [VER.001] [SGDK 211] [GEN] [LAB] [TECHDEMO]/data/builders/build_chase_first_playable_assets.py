"""Build the Celestial Chase first-playable visual candidate.

The builder preserves the approved source-baked character strips. It translates
the curated v007 scene pair into a tile-aware runtime candidate and derives
gameplay props from the project-local source boards.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter, OrderedDict
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT = Path(__file__).resolve().parents[2]
LEGACY_SOURCE = PROJECT / "rascunho" / "entrada_bruta" / "legacy_megadrive_dev" / "source_art" / "celestial_chase_v001"
LEGACY_PROCESSED = (
    PROJECT
    / "rascunho"
    / "processado"
    / "legacy_megadrive_dev"
    / "processed"
    / "celestial_chase_v001"
)
V007 = LEGACY_PROCESSED / "elite_split_scene" / "runtime_split_candidates_v007"
DEFAULT_FONT_SOURCE = PROJECT.parents[1] / "sdk" / "sgdk-2.11" / "res" / "image" / "font_default.png"

SOURCE_ROOT = PROJECT / "data" / "source_art" / "chase_first_playable"
PROCESSED_ROOT = PROJECT / "data" / "processed" / "chase_first_playable"
REVIEW_ROOT = PROCESSED_ROOT / "review"
RES_GFX = PROJECT / "res" / "gfx" / "chase"
RES_SPRITES = PROJECT / "res" / "sprites" / "chase"
CASE_ROOT = PROJECT / "doc" / "source_cases" / "chase_first_playable"
LOG_ROOT = PROJECT / "out" / "logs"
MOTION_ROOT = PROJECT / "out" / "evidence" / "motion"

BG_B_SOURCE = V007 / "chase_bg_b_atmosphere_runtime_v007.png"
BG_A_SOURCE = V007 / "chase_bg_a_road_overlay_runtime_floor_y144.png"
COMPOSITE_SOURCE = V007 / "chase_runtime_split_composite_direct_floor_y144.png"
PROPS_SOURCE = LEGACY_SOURCE / "props" / "chase_obstacle_props_candidate_v001.png"
FX_SOURCE = LEGACY_SOURCE / "fx" / "chase_fx_sheet_candidate_v001.png"
PURSUER_PALETTE_SOURCE = PROJECT / "res" / "sprites" / "chase" / "pursuer_3q_front_mid_96x80_zloop_strip_v003.png"

BG_B_BASIC = PROCESSED_ROOT / "basic" / "chase_bg_b_basic.png"
BG_A_BASIC = PROCESSED_ROOT / "basic" / "chase_bg_a_basic.png"
BG_B_ELITE = PROCESSED_ROOT / "elite" / "chase_bg_b_elite.png"
BG_A_ELITE = PROCESSED_ROOT / "elite" / "chase_bg_a_elite.png"

RUNTIME_BG_B = RES_GFX / "chase_bg_b_elite.png"
RUNTIME_BG_A = RES_GFX / "chase_bg_a_elite.png"
V009_ROOT = PROCESSED_ROOT / "v009"
V009_REVIEW = V009_ROOT / "review"
V009_BG_B = RES_GFX / "chase_bg_b_v009.png"
V009_BG_A = RES_GFX / "chase_bg_a_v009.png"

HERO_SOURCE = RES_SPRITES / "hero_run_toward_64x80_strip_v003.png"
PURSUER_BODY_SOURCE = RES_SPRITES / "pursuer_3q_front_mid_96x80_zloop_strip_v003.png"
PURSUER_HEAD_SOURCE = RES_SPRITES / "pursuer_head_horns_112x64_zloop_strip_v003.png"
PURSUER_CLAW_SOURCE = RES_SPRITES / "pursuer_attack_hoof_96x64_zloop_strip_v003.png"
STAR_SOURCE = RES_SPRITES / "chase_energy_star_32x32.png"
PULSE_SOURCE = RES_SPRITES / "chase_pulse_impact_64x48.png"

V009_HERO = RES_SPRITES / "hero_run_toward_64x80_strip_v009.png"
V009_HERO_GHOST = RES_SPRITES / "hero_ghost_64x80_strip_v009.png"
V009_PURSUER_TORSO = RES_SPRITES / "pursuer_torso_96x80_strip_v009.png"
V009_PURSUER_HEAD = RES_SPRITES / "pursuer_head_80x64_strip_v009.png"
V009_PURSUER_CLAW = RES_SPRITES / "pursuer_claw_64x64_strip_v009.png"
V009_STAR = RES_SPRITES / "chase_energy_star_32x32_strip_v009.png"
V009_PULSE = RES_SPRITES / "chase_pulse_impact_64x48_strip_v009.png"
V009_CLOUD = RES_SPRITES / "chase_cloud_64x32_strip_v009.png"
V009_LETTERBOX = RES_GFX / "chase_letterbox_tile_v009.png"
V011_ROOT = PROCESSED_ROOT / "v011"
V011_REVIEW = V011_ROOT / "review"
V011_BG_B = RES_GFX / "chase_bg_b_v011.png"
V011_BG_A = RES_GFX / "chase_bg_a_v011.png"
V011_BOULDER = RES_SPRITES / "chase_obstacle_boulder_64x48_strip_v011.png"
V011_BRAND = RES_SPRITES / "chase_obstacle_brand_64x48_strip_v011.png"
V011_PURSUER_TORSO = RES_SPRITES / "pursuer_torso_96x80_strip_v011.png"
V011_CONTACT_SHADOW = RES_SPRITES / "chase_contact_shadow_16x8_strip_v011.png"
V011_HUD_FONT = RES_GFX / "chase_hud_font_v011.png"


def ensure_dirs() -> None:
    for path in (
        SOURCE_ROOT / "background",
        SOURCE_ROOT / "props",
        SOURCE_ROOT / "fx",
        BG_B_BASIC.parent,
        BG_B_ELITE.parent,
        REVIEW_ROOT,
        V009_REVIEW,
        V011_REVIEW,
        RES_GFX,
        RES_SPRITES,
        CASE_ROOT,
        LOG_ROOT,
        MOTION_ROOT,
    ):
        path.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")


def copy_source(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def palette16(image: Image.Image) -> list[int]:
    palette = list(image.getpalette() or [])
    palette = palette[: 16 * 3]
    palette += [0] * ((16 * 3) - len(palette))
    return palette


def normalize_indexed(image: Image.Image, transparent: bool = False) -> Image.Image:
    if image.mode != "P":
        image = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)

    source_palette = list(image.getpalette() or [])
    used = sorted(set(image.getdata()))
    if transparent and 0 not in used:
        used.insert(0, 0)
    if len(used) > 16:
        raise ValueError(f"Expected <=16 used palette indexes, found {len(used)}")

    mapping = {old: new for new, old in enumerate(used)}
    pixels = bytes(mapping[value] for value in image.getdata())
    normalized = Image.frombytes("P", image.size, pixels)

    compact_palette: list[int] = []
    for old in used:
        base = old * 3
        compact_palette.extend(source_palette[base : base + 3])
    compact_palette += [0] * ((16 * 3) - len(compact_palette))
    normalized.putpalette(compact_palette)
    if transparent:
        normalized.info["transparency"] = mapping.get(0, 0)
    return normalized


def save_indexed(image: Image.Image, path: Path, transparent: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"bits": 4, "optimize": True}
    if transparent:
        kwargs["transparency"] = 0
    image.save(path, **kwargs)


def snap_md_channel(value: int) -> int:
    return max(0, min(238, round(value / 34) * 34))


def snap_palette_to_md(image: Image.Image) -> Image.Image:
    result = image.copy()
    palette = list(result.getpalette() or [])
    palette += [0] * (768 - len(palette))
    for index in range(16 * 3):
        palette[index] = snap_md_channel(palette[index])
    result.putpalette(palette)
    return result


def ensure_transparent_zero(image: Image.Image) -> Image.Image:
    result = image.copy()
    corners = (
        result.getpixel((0, 0)),
        result.getpixel((result.width - 1, 0)),
        result.getpixel((0, result.height - 1)),
        result.getpixel((result.width - 1, result.height - 1)),
    )
    background_index = max(set(corners), key=corners.count)
    if background_index != 0:
        pixels = bytes(
            0 if value == background_index else background_index if value == 0 else value
            for value in result.getdata()
        )
        result = Image.frombytes("P", result.size, pixels)
        palette = list(image.getpalette() or [])
        palette += [0] * (768 - len(palette))
        old_zero = palette[0:3]
        background = palette[background_index * 3 : background_index * 3 + 3]
        palette[0:3] = background
        palette[background_index * 3 : background_index * 3 + 3] = old_zero
        result.putpalette(palette)
    result.info["transparency"] = 0
    return result


def reserve_backdrop_zero(image: Image.Image, backdrop: tuple[int, int, int]) -> Image.Image:
    result = image.copy()
    palette = list(result.getpalette() or [])
    palette += [0] * (768 - len(palette))
    old_zero = tuple(palette[:3])
    used_nonzero = sorted(set(result.getdata()) - {0})
    nearest_index = min(
        used_nonzero,
        key=lambda index: sum(
            (old_zero[channel] - palette[index * 3 + channel]) ** 2
            for channel in range(3)
        ),
    )
    pixels = bytes(nearest_index if value == 0 else value for value in result.getdata())
    result = Image.frombytes("P", result.size, pixels)
    palette[0:3] = list(backdrop)
    result.putpalette(palette)
    return result


def remaster_v009_palette(image: Image.Image, role: str) -> Image.Image:
    result = image.copy()
    palette = list(result.getpalette() or [])
    palette += [0] * (768 - len(palette))
    if role == "sky":
        colors = {
            0: (0, 0, 0),
            1: (170, 136, 102),
            2: (136, 136, 136),
            3: (102, 136, 136),
            4: (102, 68, 136),
            5: (68, 68, 136),
            6: (68, 68, 68),
            7: (34, 68, 136),
            9: (34, 34, 136),
            10: (34, 34, 102),
            11: (34, 34, 34),
            12: (0, 34, 102),
            13: (0, 34, 68),
            14: (0, 0, 102),
            15: (0, 0, 34),
        }
    else:
        colors = {
            1: (238, 204, 136),
            2: (170, 170, 170),
            3: (102, 102, 102),
            4: (68, 68, 136),
            5: (34, 68, 136),
            6: (34, 34, 136),
            7: (34, 34, 102),
            8: (0, 34, 102),
            9: (0, 0, 102),
            10: (0, 0, 34),
        }
    for index, color in colors.items():
        palette[index * 3 : index * 3 + 3] = color
    result.putpalette(palette)
    return result


def road_edges_for_y(y: int, width: int, horizon_y: int = 92) -> tuple[int, int]:
    """Perspective road boundaries in the active 320px staging space."""
    center = width // 2
    if y <= horizon_y:
        return center - 4, center + 4
    t = min(1.0, (y - horizon_y) / max(1, 223 - horizon_y))
    half_width = int(6 + (width * 0.49) * (t * t))
    return max(0, center - half_width), min(width - 1, center + half_width)


def local_mode(values: list[int], fallback: int) -> tuple[int, int]:
    if not values:
        return fallback, 0
    mode, count = Counter(values).most_common(1)[0]
    return mode, count


def reduce_road_micro_noise(
    image: Image.Image,
    transparent: bool,
    y_min: int = 104,
    passes: int = 1,
) -> Image.Image:
    """Remove singleton pixel noise while preserving indexed 4bpp hard edges."""
    result = image.copy()
    for _ in range(passes):
        source = result.copy()
        source_pixels = source.load()
        target_pixels = result.load()
        for y in range(max(1, y_min), result.height - 1):
            for x in range(1, result.width - 1):
                current = source_pixels[x, y]
                if transparent and current == 0:
                    continue
                neighbors: list[int] = []
                visible_neighbors = 0
                same_neighbors = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        value = source_pixels[x + dx, y + dy]
                        if transparent and value == 0:
                            continue
                        visible_neighbors += 1
                        if value == current:
                            same_neighbors += 1
                        neighbors.append(value)

                if transparent and current != 0 and visible_neighbors <= 1:
                    target_pixels[x, y] = 0
                    continue

                mode, mode_count = local_mode(neighbors, current)
                if mode != current and mode_count >= 5 and same_neighbors <= 1:
                    target_pixels[x, y] = mode

        # Horizontal hard-pixel cleanup: reduce one-pixel speckles inside rows.
        source = result.copy()
        source_pixels = source.load()
        target_pixels = result.load()
        for y in range(max(1, y_min), result.height - 1):
            for x in range(1, result.width - 1):
                current = source_pixels[x, y]
                if transparent and current == 0:
                    continue
                left = source_pixels[x - 1, y]
                right = source_pixels[x + 1, y]
                if left == right and left != current and not (transparent and left == 0):
                    target_pixels[x, y] = left
    if transparent:
        result.info["transparency"] = 0
    return result


def draw_index_line(
    image: Image.Image,
    start: tuple[int, int],
    end: tuple[int, int],
    color_index: int,
    pattern: int = 1,
) -> None:
    pixels = image.load()
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    step = 0
    while True:
        if 0 <= x0 < image.width and 0 <= y0 < image.height and (pattern <= 1 or (step % pattern) != 0):
            pixels[x0, y0] = color_index
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
        step += 1


def reinforce_road_perspective_overlay(image: Image.Image) -> Image.Image:
    """Add mockup-like vanishing lines and stone rows to the transparent BG_A layer."""
    result = image.copy()
    result.info["transparency"] = 0
    pixels = result.load()
    width = result.width
    center = width // 2
    horizon_y = 92
    dark = 10
    deep = 9
    shadow = 8
    mid = 6
    blue = 5
    light = 1

    for y in range(horizon_y, result.height):
        left, right = road_edges_for_y(y, width, horizon_y)
        t_num = y - horizon_y
        edge_width = 1 + (1 if y > 154 else 0) + (1 if y > 198 else 0)
        for offset in range(edge_width):
            if left + offset < width:
                pixels[left + offset, y] = dark
            if right - offset >= 0:
                pixels[right - offset, y] = dark
        if (y & 3) == 0:
            if left + edge_width + 1 < width:
                pixels[left + edge_width + 1, y] = blue
            if right - edge_width - 1 >= 0:
                pixels[right - edge_width - 1, y] = blue
        if t_num > 36 and (y & 7) == 0:
            inner_left = min(width - 1, left + edge_width + 4)
            inner_right = max(0, right - edge_width - 4)
            if inner_left < inner_right:
                pixels[inner_left, y] = light
                pixels[inner_right, y] = light

    row_y = horizon_y + 8
    row_gap = 4
    row_index = 0
    while row_y < result.height:
        left, right = road_edges_for_y(row_y, width, horizon_y)
        left = min(width - 1, left + 5)
        right = max(0, right - 5)
        if left < right:
            row_color = deep if row_y > 198 else shadow
            for x in range(left, right + 1):
                # Broken rows read as stone slabs, not as a full debug ruler.
                if ((x >> 3) + row_index) % 5 == 0 or ((x + row_index) & 1) == 0:
                    continue
                pixels[x, row_y] = row_color
                if row_y + 1 < result.height and row_y > 150 and ((x + row_index) & 7) == 0:
                    pixels[x, row_y + 1] = mid
        row_y += row_gap
        row_gap = min(18, row_gap + (2 if row_y < 168 else 3))
        row_index += 1

    for target_x in (center - 76, center - 34, center + 34, center + 76):
        draw_index_line(result, (center, horizon_y), (target_x, result.height - 1), dark, pattern=7)
    return result


def add_road_material_dither(image: Image.Image) -> Image.Image:
    """Add controlled 2x2 stone texture so the road reads as material, not noise."""
    result = image.copy()
    result.info["transparency"] = 0
    pixels = result.load()
    width = result.width
    for y in range(132, result.height):
        left, right = road_edges_for_y(y, width)
        left = max(0, left + 10)
        right = min(width - 1, right - 10)
        if left >= right:
            continue
        for x in range(left, right + 1):
            value = pixels[x, y]
            if value not in (4, 5, 6, 7, 8):
                continue
            # Coarse clustered dither: visible on CRT scale, but avoids salt.
            if ((x >> 1) + (y >> 1)) % 11 == 0:
                pixels[x, y] = 5 if value >= 7 else 6
            elif y > 184 and ((x >> 2) + y) % 17 == 0:
                pixels[x, y] = 8
    return result


def polish_chase_road_layers(bg_b: Image.Image, bg_a: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Cinematic v014 road pass: reduce noisy tiling and restore mockup-like perspective."""
    polished_b = reduce_road_micro_noise(bg_b, transparent=False, y_min=106, passes=1)
    polished_a = reduce_road_micro_noise(bg_a, transparent=True, y_min=96, passes=2)
    polished_a = reinforce_road_perspective_overlay(polished_a)
    polished_a = add_road_material_dither(polished_a)
    return polished_b, polished_a


def select_frames(
    strip: Image.Image,
    frame_size: tuple[int, int],
    frame_indices: tuple[int, ...],
) -> Image.Image:
    frame_width, frame_height = frame_size
    result = Image.new("P", (frame_width * len(frame_indices), frame_height), 0)
    result.putpalette(palette16(strip))
    for output_index, source_index in enumerate(frame_indices):
        frame = strip.crop(
            (
                source_index * frame_width,
                0,
                (source_index + 1) * frame_width,
                frame_height,
            )
        )
        result.paste(frame, (output_index * frame_width, 0))
    result.info["transparency"] = 0
    return result


HERO_VELOCITY_PALETTE = [
    (255, 0, 255),
    (0, 0, 34),
    (0, 34, 68),
    (0, 68, 136),
    (34, 102, 204),
    (68, 34, 0),
    (136, 68, 34),
    (238, 136, 34),
    (170, 102, 68),
    (238, 170, 102),
    (238, 204, 136),
    (34, 34, 34),
    (68, 68, 102),
    (102, 136, 238),
    (170, 204, 238),
    (238, 238, 204),
]

HERO_VELOCITY_REMAP = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 8,
    10: 9,
    11: 5,
    12: 7,
    13: 12,
    14: 10,
    15: 11,
}


def hero_velocity_palette16() -> list[int]:
    palette: list[int] = []
    for color in HERO_VELOCITY_PALETTE:
        palette.extend(color)
    palette += [0] * ((16 * 3) - len(palette))
    return palette


def remap_hero_velocity_palette(frame: Image.Image) -> Image.Image:
    pixels = bytes(HERO_VELOCITY_REMAP.get(value, 0) for value in frame.getdata())
    result = Image.frombytes("P", frame.size, pixels)
    result.putpalette(hero_velocity_palette16())
    result.info["transparency"] = 0
    return result


def denoise_hero_frame(frame: Image.Image, passes: int = 2) -> Image.Image:
    result = frame.copy()
    width, height = result.size
    for _ in range(passes):
        pixels = result.load()
        changes: list[tuple[int, int, int]] = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                value = pixels[x, y]
                if value == 0:
                    continue
                neighbors = (
                    pixels[x - 1, y],
                    pixels[x + 1, y],
                    pixels[x, y - 1],
                    pixels[x, y + 1],
                )
                if sum(1 for neighbor in neighbors if neighbor == value) > 0:
                    continue
                visible = [neighbor for neighbor in neighbors if neighbor != 0]
                if visible:
                    changes.append((x, y, max(set(visible), key=visible.count)))
        for x, y, value in changes:
            pixels[x, y] = value
    return result


def visible_bbox(frame: Image.Image) -> tuple[int, int, int, int] | None:
    coords = [
        (x, y)
        for y in range(frame.height)
        for x in range(frame.width)
        if frame.getpixel((x, y)) != 0
    ]
    if not coords:
        return None
    xs = [coord[0] for coord in coords]
    ys = [coord[1] for coord in coords]
    return min(xs), min(ys), max(xs), max(ys)


def add_hero_velocity_mantle(frame: Image.Image, phase: int) -> Image.Image:
    result = frame.copy()
    source = frame.load()
    pixels = result.load()
    bbox = visible_bbox(frame)
    if bbox is None:
        result.info["transparency"] = 0
        return result

    min_x, min_y, max_x, max_y = bbox
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            value = source[x, y]
            if value == 0:
                continue
            if value in (2, 3, 4, 12) and ((x + (2 * y) + (phase * 3)) & 15) == 0:
                pixels[x, y] = 13
            elif value in (5, 6, 7, 8, 9, 10) and ((x + y + phase) & 31) == 0:
                pixels[x, y] = 10

    # Acentos externos so podem existir colados na silhueta. Nunca preencher
    # canvas transparente inteiro: isso foi a origem da capsula opaca da v022.
    rim_pixels: list[tuple[int, int, int]] = []
    for y in range(max(4, min_y - 1), min(76, max_y + 2)):
        for x in range(max(4, min_x - 1), min(60, max_x + 2)):
            if source[x, y] != 0:
                continue
            neighbors = (
                source[x - 1, y],
                source[x + 1, y],
                source[x, y - 1],
                source[x, y + 1],
            )
            if sum(1 for neighbor in neighbors if neighbor != 0) < 2:
                continue
            if ((x * 3) + y + phase) & 7:
                continue
            rim_pixels.append((x, y, 3 if y < 52 else 2))
    for x, y, color in rim_pixels:
        pixels[x, y] = color

    result.info["transparency"] = 0
    return result


def sprite_canvas_contract_report(
    strip: Image.Image,
    frame_size: tuple[int, int],
    *,
    edge: int = 4,
) -> list[dict]:
    frame_width, frame_height = frame_size
    reports: list[dict] = []
    for frame_index in range(strip.width // frame_width):
        frame = strip.crop(
            (
                frame_index * frame_width,
                0,
                (frame_index + 1) * frame_width,
                frame_height,
            )
        )
        visible = [(x, y) for y in range(frame_height) for x in range(frame_width) if frame.getpixel((x, y)) != 0]
        edge_nonzero = sum(
            1
            for x, y in visible
            if x < edge or x >= frame_width - edge or y < edge or y >= frame_height - edge
        )
        bbox = visible_bbox(frame)
        touches_full_width = bool(bbox and bbox[0] == 0 and bbox[2] == frame_width - 1)
        reports.append(
            {
                "frame": frame_index,
                "visible_pixels": len(visible),
                "visible_ratio": round(len(visible) / (frame_width * frame_height), 4),
                "edge_nonzero_pixels": edge_nonzero,
                "edge_nonzero_ratio": round(edge_nonzero / max(1, len(visible)), 4),
                "bbox": list(bbox) if bbox else None,
                "touches_full_width": touches_full_width,
            }
        )
    return reports


def validate_sprite_canvas_contract(
    strip: Image.Image,
    frame_size: tuple[int, int],
    asset_id: str,
    *,
    max_visible_ratio: float = 0.58,
    max_edge_nonzero: int = 160,
) -> dict:
    palette = list(strip.getpalette() or [])
    palette += [0] * (768 - len(palette))
    report = {
        "asset_id": asset_id,
        "status": "passed",
        "transparent_index": strip.info.get("transparency"),
        "index0_rgb": palette[:3],
        "frame_size": list(frame_size),
        "frames": sprite_canvas_contract_report(strip, frame_size),
        "issues": [],
    }
    if strip.mode != "P":
        report["issues"].append({"code": "SPRITE_NOT_INDEXED", "severity": "critical"})
    if strip.info.get("transparency") != 0:
        report["issues"].append({"code": "TRANSPARENCY_INDEX_NOT_ZERO", "severity": "critical"})
    if palette[:3] != [255, 0, 255]:
        report["issues"].append({"code": "INDEX0_NOT_MAGENTA_CANVAS", "severity": "warning"})
    for frame_report in report["frames"]:
        if frame_report["visible_ratio"] > max_visible_ratio:
            report["issues"].append(
                {
                    "code": "OPAQUE_FRAME_CAPSULE_RISK",
                    "severity": "critical",
                    "frame": frame_report["frame"],
                    "visible_ratio": frame_report["visible_ratio"],
                }
            )
        if frame_report["edge_nonzero_pixels"] > max_edge_nonzero:
            report["issues"].append(
                {
                    "code": "NON_INDEX0_BACKGROUND_MATTE",
                    "severity": "critical",
                    "frame": frame_report["frame"],
                    "edge_nonzero_pixels": frame_report["edge_nonzero_pixels"],
                }
            )
        if frame_report["touches_full_width"]:
            report["issues"].append(
                {
                    "code": "SPRITE_CANVAS_TOUCHES_FULL_WIDTH",
                    "severity": "critical",
                    "frame": frame_report["frame"],
                    "bbox": frame_report["bbox"],
                }
            )
    if report["issues"]:
        report["status"] = "blocked"
        raise ValueError(f"{asset_id} failed sprite canvas contract: {report['issues']}")
    return report


def remaster_hero_run_strip(
    strip: Image.Image,
    frame_size: tuple[int, int],
    frame_indices: tuple[int, ...],
) -> Image.Image:
    frame_width, frame_height = frame_size
    result = Image.new("P", (frame_width * len(frame_indices), frame_height), 0)
    result.putpalette(hero_velocity_palette16())
    for output_index, source_index in enumerate(frame_indices):
        source_frame = strip.crop(
            (
                source_index * frame_width,
                0,
                (source_index + 1) * frame_width,
                frame_height,
            )
        )
        frame = remap_hero_velocity_palette(source_frame)
        frame = denoise_hero_frame(frame)
        frame = add_hero_velocity_mantle(frame, output_index)
        result.paste(frame, (output_index * frame_width, 0))
    result.info["transparency"] = 0
    return result


def derive_ghost_strip(strip: Image.Image, frame_size: tuple[int, int]) -> Image.Image:
    frame_width, frame_height = frame_size
    result = Image.new("P", strip.size, 0)
    result.putpalette(hero_velocity_palette16())
    for frame_index in range(strip.width // frame_width):
        frame = strip.crop(
            (
                frame_index * frame_width,
                0,
                (frame_index + 1) * frame_width,
                frame_height,
            )
        )
        source = frame.load()
        ghost = Image.new("P", frame_size, 0)
        ghost.putpalette(hero_velocity_palette16())
        pixels = ghost.load()
        for y in range(frame_height):
            for x in range(frame_width):
                value = source[x, y]
                if value == 0:
                    continue
                if value in (1, 11):
                    color = 1
                elif value in (5, 6, 7, 8, 9, 10):
                    color = 13
                elif value in (2, 3, 12):
                    color = 3
                else:
                    color = 4
                pixels[x, y] = color
        for y in range(4, frame_height - 4):
            for x in range(3, frame_width - 3):
                if pixels[x, y] != 0 and ((x + (2 * y) + frame_index) & 31) == 0:
                    pixels[x, y] = 14
        result.paste(ghost, (frame_index * frame_width, 0))
    result.info["transparency"] = 0
    return result


def derive_torso_strip(strip: Image.Image, frame_size: tuple[int, int]) -> Image.Image:
    result = strip.copy()
    frame_width, frame_height = frame_size
    pixels = result.load()
    for frame in range(result.width // frame_width):
        origin_x = frame * frame_width
        for y in range(frame_height):
            for x in range(frame_width):
                keep_shoulders = 29 <= y < 54 and 24 <= x < 72
                keep_core = 54 <= y and 32 <= x < 64
                if not (keep_shoulders or keep_core):
                    pixels[origin_x + x, y] = 0
    result.info["transparency"] = 0
    return result


def derive_v011_torso_strip(strip: Image.Image, frame_size: tuple[int, int]) -> Image.Image:
    result = strip.copy()
    frame_width, frame_height = frame_size
    pixels = result.load()
    for frame in range(result.width // frame_width):
        origin_x = frame * frame_width
        for y in range(frame_height):
            for x in range(frame_width):
                keep_collar = 23 <= y < 29 and 34 <= x < 62
                keep_shoulders = 27 <= y < 55 and 22 <= x < 74
                keep_rear_body = 54 <= y and 28 <= x < 68
                if not (keep_collar or keep_shoulders or keep_rear_body):
                    pixels[origin_x + x, y] = 0
    result.info["transparency"] = 0
    return result


def crop_strip(
    strip: Image.Image,
    source_frame_size: tuple[int, int],
    crop: tuple[int, int, int, int],
) -> Image.Image:
    source_width, source_height = source_frame_size
    crop_width = crop[2] - crop[0]
    crop_height = crop[3] - crop[1]
    frame_count = strip.width // source_width
    result = Image.new("P", (crop_width * frame_count, crop_height), 0)
    result.putpalette(palette16(strip))
    for frame in range(frame_count):
        frame_image = strip.crop(
            (
                frame * source_width + crop[0],
                crop[1],
                frame * source_width + crop[2],
                crop[3],
            )
        )
        result.paste(frame_image, (frame * crop_width, 0))
    result.info["transparency"] = 0
    return result


def derive_twinkle_strip(image: Image.Image) -> Image.Image:
    source = ensure_transparent_zero(image)
    frames: list[Image.Image] = []
    center_x = source.width // 2
    center_y = source.height // 2
    for phase in range(4):
        frame = source.copy()
        pixels = frame.load()
        for y in range(frame.height):
            for x in range(frame.width):
                if pixels[x, y] == 0:
                    continue
                distance = abs(x - center_x) + abs(y - center_y)
                if distance > 12 and ((x + y + phase) & 3) != 0:
                    pixels[x, y] = 0
        frames.append(frame)
    result = Image.new("P", (source.width * len(frames), source.height), 0)
    result.putpalette(palette16(source))
    for index, frame in enumerate(frames):
        result.paste(frame, (index * source.width, 0))
    result.info["transparency"] = 0
    return result


def derive_expansion_strip(image: Image.Image) -> Image.Image:
    source = ensure_transparent_zero(image)
    factors = (0.34, 0.52, 0.72, 1.0, 0.82, 0.58)
    result = Image.new("P", (source.width * len(factors), source.height), 0)
    result.putpalette(palette16(source))
    for index, factor in enumerate(factors):
        width = max(8, int(source.width * factor) // 2 * 2)
        height = max(8, int(source.height * factor) // 2 * 2)
        frame = source.resize((width, height), Image.Resampling.NEAREST)
        x = index * source.width + (source.width - width) // 2
        y = (source.height - height) // 2
        result.paste(frame, (x, y))
    result.info["transparency"] = 0
    return result


def extend_canvas_with_mirrored_gutters(image: Image.Image, gutter_px: int = 96) -> Image.Image:
    if image.width != 320:
        raise ValueError(f"Expected a 320px source canvas, found {image.width}px")
    if gutter_px % 8 != 0:
        raise ValueError("Gutter must remain tile aligned")

    result = Image.new("P", (image.width + gutter_px * 2, image.height), 0)
    result.putpalette(palette16(image))
    left = image.crop((0, 0, gutter_px, image.height)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    right = image.crop(
        (image.width - gutter_px, 0, image.width, image.height)
    ).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    result.paste(left, (0, 0))
    result.paste(image, (gutter_px, 0))
    result.paste(right, (gutter_px + image.width, 0))
    if image.info.get("transparency") == 0:
        result.info["transparency"] = 0
    return result


def derive_contact_scaled_strip(image: Image.Image) -> Image.Image:
    source = ensure_transparent_zero(image)
    factors = (0.50, 0.66, 0.82, 1.00)
    content_box = source.getbbox()
    if content_box is None:
        raise ValueError("Cannot derive depth stages from an empty sprite")
    content = source.crop(content_box)
    result = Image.new("P", (source.width * len(factors), source.height), 0)
    result.putpalette(palette16(source))
    for index, factor in enumerate(factors):
        width = max(8, int(content.width * factor) // 2 * 2)
        height = max(8, int(content.height * factor) // 2 * 2)
        frame = content.resize((width, height), Image.Resampling.NEAREST)
        x = index * source.width + (source.width - width) // 2
        y = source.height - height
        result.paste(frame, (x, y))
    result.info["transparency"] = 0
    return result


def derive_contact_shadow_strip(palette_source: Image.Image) -> Image.Image:
    widths = (6, 11, 16)
    result = Image.new("P", (16 * len(widths), 8), 0)
    result.putpalette(palette16(palette_source))
    pixels = result.load()
    for frame, width in enumerate(widths):
        radius_x = width / 2
        radius_y = 3.5
        for y in range(8):
            for x in range(16):
                dx = (x - 7.5) / radius_x
                dy = (y - 3.5) / radius_y
                distance = dx * dx + dy * dy
                if distance <= 0.46:
                    pixels[frame * 16 + x, y] = 10
                elif distance <= 0.78 and ((x + y + frame) & 1) == 0:
                    pixels[frame * 16 + x, y] = 9
                elif distance <= 1.0 and ((x + (y << 1) + frame) & 3) == 0:
                    pixels[frame * 16 + x, y] = 8
    result.info["transparency"] = 0
    return result


def derive_hud_font(default_font: Image.Image, palette_source: Image.Image) -> Image.Image:
    if default_font.size != (128, 48):
        raise ValueError(f"Expected SGDK 96-glyph font sheet, found {default_font.size}")

    source = default_font.convert("P")
    result = Image.new("P", source.size, 0)
    result.putpalette(palette16(palette_source))
    source_pixels = source.load()
    target_pixels = result.load()

    for tile_y in range(0, source.height, 8):
        for tile_x in range(0, source.width, 8):
            for y in range(8):
                for x in range(8):
                    if source_pixels[tile_x + x, tile_y + y] == 0:
                        continue
                    if x + 1 < 8 and y + 1 < 8:
                        target_pixels[tile_x + x + 1, tile_y + y + 1] = 10
            for y in range(8):
                for x in range(8):
                    if source_pixels[tile_x + x, tile_y + y] != 0:
                        target_pixels[tile_x + x, tile_y + y] = 15
    return result


def derive_cloud_strip(bg_b: Image.Image) -> Image.Image:
    crops = ((0, 48, 64, 80), (256, 48, 320, 80))
    result = Image.new("P", (128, 32), 0)
    result.putpalette(palette16(bg_b))
    for frame_index, box in enumerate(crops):
        frame = bg_b.crop(box)
        pixels = frame.load()
        for y in range(frame.height):
            for x in range(frame.width):
                if pixels[x, y] >= 10:
                    pixels[x, y] = 0
        result.paste(frame, (frame_index * 64, 0))
    result.info["transparency"] = 0
    return result


def save_strip_gif(
    strip: Image.Image,
    frame_size: tuple[int, int],
    path: Path,
    duration_ms: int,
) -> None:
    frame_width, frame_height = frame_size
    frames = [
        strip.crop((x, 0, x + frame_width, frame_height)).convert("RGBA")
        for x in range(0, strip.width, frame_width)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
    )


def save_strip_webp(
    strip: Image.Image,
    frame_size: tuple[int, int],
    path: Path,
    duration_ms: int,
) -> None:
    frame_width, frame_height = frame_size
    frames = [
        strip.crop((x, 0, x + frame_width, frame_height)).convert("RGBA")
        for x in range(0, strip.width, frame_width)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        lossless=True,
        quality=100,
    )


def tile_signature(tile: Image.Image, block: int, transparent: bool) -> tuple[int, ...]:
    pixels = tile.load()
    signature: list[int] = []
    for block_y in range(0, 8, block):
        for block_x in range(0, 8, block):
            values = [
                pixels[x, y]
                for y in range(block_y, block_y + block)
                for x in range(block_x, block_x + block)
            ]
            if transparent and values.count(0) >= ((block * block + 1) // 2):
                signature.append(0)
                continue
            visible = [value for value in values if not (transparent and value == 0)] or [0]
            signature.append(round(sum(visible) / len(visible)))
    return tuple(signature)


def tile_aware_translate(image: Image.Image, block: int, transparent: bool = False) -> Image.Image:
    result = image.copy()
    representatives: OrderedDict[tuple[int, ...], Image.Image] = OrderedDict()
    for y in range(0, image.height, 8):
        for x in range(0, image.width, 8):
            tile = image.crop((x, y, x + 8, y + 8))
            signature = tile_signature(tile, block, transparent)
            if signature not in representatives:
                representatives[signature] = tile.copy()
            result.paste(representatives[signature], (x, y))
    return result


def unique_tiles(image: Image.Image, ignore_empty: bool = False) -> list[Image.Image]:
    result: OrderedDict[bytes, Image.Image] = OrderedDict()
    for y in range(0, image.height, 8):
        for x in range(0, image.width, 8):
            tile = image.crop((x, y, x + 8, y + 8))
            payload = tile.tobytes()
            if ignore_empty and not any(payload):
                continue
            result.setdefault(payload, tile)
    return list(result.values())


def tile_count(image: Image.Image, ignore_empty: bool = False) -> int:
    return len(unique_tiles(image, ignore_empty))


def tile_count_with_flips(image: Image.Image, ignore_empty: bool = False) -> int:
    result: set[bytes] = set()
    for y in range(0, image.height, 8):
        for x in range(0, image.width, 8):
            tile = image.crop((x, y, x + 8, y + 8))
            payload = tile.tobytes()
            if ignore_empty and not any(payload):
                continue
            variants = (
                payload,
                tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(),
                tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes(),
                tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                .transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                .tobytes(),
            )
            result.add(min(variants))
    return len(result)


def frame_region_variant_count(
    strip: Image.Image,
    frame_size: tuple[int, int],
    region: tuple[int, int, int, int],
) -> int:
    frame_width, frame_height = frame_size
    if region[2] > frame_width or region[3] > frame_height:
        raise ValueError("Region exceeds frame bounds")
    variants = {
        strip.crop(
            (
                frame * frame_width + region[0],
                region[1],
                frame * frame_width + region[2],
                region[3],
            )
        ).tobytes()
        for frame in range(strip.width // frame_width)
    }
    return len(variants)


def save_palette_strip(image: Image.Image, path: Path) -> None:
    palette = palette16(image)
    strip = Image.new("RGB", (16 * 16, 24), (0, 0, 0))
    draw = ImageDraw.Draw(strip)
    for index in range(16):
        color = tuple(palette[index * 3 : index * 3 + 3])
        draw.rectangle((index * 16, 0, index * 16 + 15, 23), fill=color)
    strip.save(path)


def save_tileset_sheet(image: Image.Image, path: Path, ignore_empty: bool = False) -> None:
    tiles = unique_tiles(image, ignore_empty)
    columns = 32
    rows = max(1, (len(tiles) + columns - 1) // columns)
    sheet = Image.new("P", (columns * 8, rows * 8), 0)
    sheet.putpalette(palette16(image))
    for index, tile in enumerate(tiles):
        sheet.paste(tile, ((index % columns) * 8, (index // columns) * 8))
    save_indexed(sheet, path, False)


def composite(bg_b: Image.Image, bg_a: Image.Image) -> Image.Image:
    result = bg_b.convert("RGBA")
    result.alpha_composite(bg_a.convert("RGBA"))
    return result.convert("RGB")


def border_average(image: Image.Image) -> tuple[int, int, int]:
    rgb = image.convert("RGB")
    samples: list[tuple[int, int, int]] = []
    for x in range(rgb.width):
        samples.append(rgb.getpixel((x, 0)))
        samples.append(rgb.getpixel((x, rgb.height - 1)))
    for y in range(rgb.height):
        samples.append(rgb.getpixel((0, y)))
        samples.append(rgb.getpixel((rgb.width - 1, y)))
    count = len(samples)
    return tuple(sum(sample[channel] for sample in samples) // count for channel in range(3))


def isolate_board_crop(source: Image.Image, crop: tuple[int, int, int, int]) -> Image.Image:
    region = source.convert("RGB").crop(crop)
    background = border_average(region)
    rgba = Image.new("RGBA", region.size, (0, 0, 0, 0))
    source_pixels = region.load()
    target_pixels = rgba.load()

    for y in range(region.height):
        for x in range(region.width):
            red, green, blue = source_pixels[x, y]
            distance = abs(red - background[0]) + abs(green - background[1]) + abs(blue - background[2])
            spread = max(red, green, blue) - min(red, green, blue)
            dark_mass = (red + green + blue) < 245
            alpha = 255 if (distance > 46 or spread > 34 or dark_mass) else 0
            target_pixels[x, y] = (red, green, blue, alpha)
    return rgba


def remap_rgba_to_palette(image: Image.Image, target_palette: list[int]) -> Image.Image:
    colors = [
        tuple(target_palette[index * 3 : index * 3 + 3])
        for index in range(16)
    ]
    result = Image.new("P", image.size, 0)
    result.putpalette(target_palette)
    source_pixels = image.convert("RGBA").load()
    target_pixels = result.load()
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = source_pixels[x, y]
            if alpha < 80:
                target_pixels[x, y] = 0
                continue
            best_index = 1
            best_distance = 1 << 30
            for index in range(1, 16):
                target_red, target_green, target_blue = colors[index]
                distance = (
                    (red - target_red) * (red - target_red)
                    + (green - target_green) * (green - target_green)
                    + (blue - target_blue) * (blue - target_blue)
                )
                if distance < best_distance:
                    best_index = index
                    best_distance = distance
            target_pixels[x, y] = best_index
    result.info["transparency"] = 0
    return result


def build_sprite(
    board: Image.Image,
    crop: tuple[int, int, int, int],
    size: tuple[int, int],
    target_palette: list[int],
    output: Path,
) -> dict:
    isolated = isolate_board_crop(board, crop)
    translated = isolated.resize(size, Image.Resampling.BOX)
    indexed = remap_rgba_to_palette(translated, target_palette)
    save_indexed(indexed, output, True)
    return {
        "path": output.relative_to(PROJECT).as_posix(),
        "size": list(size),
        "unique_tiles": tile_count(indexed, True),
        "sha256": sha256(output),
    }


def build_backgrounds() -> dict:
    bg_b_source = normalize_indexed(Image.open(BG_B_SOURCE), False)
    bg_a_source = normalize_indexed(Image.open(BG_A_SOURCE), True)

    save_indexed(bg_b_source, BG_B_BASIC, False)
    save_indexed(bg_a_source, BG_A_BASIC, True)

    # BG_B uses a coarse tile signature to reduce unique atmospheric tiles.
    # BG_A keeps twice the local detail because it owns the playable road.
    bg_b_elite = tile_aware_translate(bg_b_source, 4, False)
    bg_a_elite = tile_aware_translate(bg_a_source, 2, True)
    save_indexed(bg_b_elite, BG_B_ELITE, False)
    save_indexed(bg_a_elite, BG_A_ELITE, True)
    save_indexed(bg_b_elite, RUNTIME_BG_B, False)
    save_indexed(bg_a_elite, RUNTIME_BG_A, True)

    composite(bg_b_source, bg_a_source).save(REVIEW_ROOT / "basic_composite.png")
    composite(bg_b_elite, bg_a_elite).save(REVIEW_ROOT / "elite_composite.png")

    original = Image.open(COMPOSITE_SOURCE).convert("RGB")
    board = Image.new("RGB", (320 * 3, 224 + 24), (0, 0, 0))
    board.paste(original, (0, 24))
    board.paste(composite(bg_b_source, bg_a_source), (320, 24))
    board.paste(composite(bg_b_elite, bg_a_elite), (640, 24))
    labels = ImageDraw.Draw(board)
    labels.text((4, 4), "ORIGINAL", fill=(238, 238, 238))
    labels.text((324, 4), "BASIC", fill=(238, 238, 238))
    labels.text((644, 4), "ELITE", fill=(238, 238, 238))
    board.save(REVIEW_ROOT / "original_basic_elite_board.png")

    for label, image, transparent in (
        ("bg_b_basic", bg_b_source, False),
        ("bg_a_basic", bg_a_source, True),
        ("bg_b_elite", bg_b_elite, False),
        ("bg_a_elite", bg_a_elite, True),
    ):
        save_palette_strip(image, REVIEW_ROOT / f"{label}_palette_strip.png")
        save_tileset_sheet(image, REVIEW_ROOT / f"{label}_tileset_sheet.png", transparent)

    return {
        "basic": {
            "bg_b_unique_tiles": tile_count(bg_b_source),
            "bg_a_unique_tiles": tile_count(bg_a_source, True),
            "total_unique_tiles": tile_count(bg_b_source) + tile_count(bg_a_source, True),
        },
        "elite": {
            "bg_b_unique_tiles": tile_count(bg_b_elite),
            "bg_a_unique_tiles": tile_count(bg_a_elite, True),
            "total_unique_tiles": tile_count(bg_b_elite) + tile_count(bg_a_elite, True),
        },
    }


def build_gameplay_sprites() -> list[dict]:
    target_palette = palette16(Image.open(PURSUER_PALETTE_SOURCE))
    props = Image.open(PROPS_SOURCE)
    fx = Image.open(FX_SOURCE)
    specs = [
        ("chase_obstacle_boulder_64x48.png", props, (42, 28, 326, 216), (64, 48)),
        ("chase_obstacle_brand_64x48.png", props, (36, 220, 340, 405), (64, 48)),
        ("chase_energy_star_32x32.png", fx, (270, 188, 374, 288), (32, 32)),
        ("chase_pulse_impact_64x48.png", fx, (258, 660, 535, 825), (64, 48)),
    ]
    return [
        {
            "symbol": name.removesuffix(".png"),
            **build_sprite(board, crop, size, target_palette, RES_SPRITES / name),
        }
        for name, board, crop, size in specs
    ]


def v009_asset_stats(path: Path, frame_size: tuple[int, int] | None = None) -> dict:
    image = Image.open(path)
    used = sorted(set(image.getdata()))
    return {
        "path": path.relative_to(PROJECT).as_posix(),
        "size": list(image.size),
        "frame_size": list(frame_size) if frame_size else None,
        "frame_count": (image.width // frame_size[0]) if frame_size else 1,
        "transparent_index": image.info.get("transparency"),
        "index_zero_pixels": sum(1 for value in image.getdata() if value == 0),
        "used_indices": used,
        "unique_tiles": tile_count(image, image.info.get("transparency") == 0),
        "sha256": sha256(path),
    }


def build_v009_assets() -> dict:
    bg_b_source = remaster_v009_palette(
        reserve_backdrop_zero(snap_palette_to_md(Image.open(RUNTIME_BG_B)), (0, 0, 0)),
        "sky",
    )
    bg_a_source = remaster_v009_palette(
        ensure_transparent_zero(snap_palette_to_md(Image.open(RUNTIME_BG_A))),
        "road",
    )
    bg_b_source, bg_a_source = polish_chase_road_layers(bg_b_source, bg_a_source)
    bg_b = tile_aware_translate(bg_b_source, 4, False)
    bg_a = tile_aware_translate(bg_a_source, 4, True)
    save_indexed(bg_b, V009_BG_B, False)
    save_indexed(bg_a, V009_BG_A, True)

    hero = remaster_hero_run_strip(ensure_transparent_zero(Image.open(HERO_SOURCE)), (64, 80), (0, 3, 4, 7))
    hero_ghost = derive_ghost_strip(hero, (64, 80))
    sprite_gate_report = {
        "schema_version": "1.0.0",
        "status": "passed",
        "scope": "critical_chase_sprite_transparency_gate",
        "reports": [
            validate_sprite_canvas_contract(hero, (64, 80), "spr_chase_hero_run_v009"),
            validate_sprite_canvas_contract(hero_ghost, (64, 80), "spr_chase_hero_ghost_v009"),
        ],
    }
    write_json(LOG_ROOT / "sprite_transparency_gate_report.json", sprite_gate_report)
    torso = derive_torso_strip(ensure_transparent_zero(Image.open(PURSUER_BODY_SOURCE)), (96, 80))
    head = crop_strip(ensure_transparent_zero(Image.open(PURSUER_HEAD_SOURCE)), (112, 64), (16, 0, 96, 64))
    claw = crop_strip(ensure_transparent_zero(Image.open(PURSUER_CLAW_SOURCE)), (96, 64), (16, 0, 80, 64))
    star = derive_twinkle_strip(Image.open(STAR_SOURCE))
    pulse = derive_expansion_strip(Image.open(PULSE_SOURCE))
    cloud = derive_cloud_strip(bg_b)

    for image, path in (
        (hero, V009_HERO),
        (hero_ghost, V009_HERO_GHOST),
        (torso, V009_PURSUER_TORSO),
        (head, V009_PURSUER_HEAD),
        (claw, V009_PURSUER_CLAW),
        (star, V009_STAR),
        (pulse, V009_PULSE),
        (cloud, V009_CLOUD),
    ):
        save_indexed(image, path, True)

    letterbox = Image.new("P", (8, 8), 10)
    letterbox.putpalette(palette16(bg_a))
    save_indexed(letterbox, V009_LETTERBOX, False)

    save_strip_gif(hero, (64, 80), V009_REVIEW / "hero_run_v009.gif", 90)
    save_strip_gif(hero_ghost, (64, 80), V009_REVIEW / "hero_ghost_v009.gif", 90)
    save_strip_gif(hero, (64, 80), MOTION_ROOT / "chase_hero_silhouette_velocity_v013.gif", 90)
    save_strip_webp(hero, (64, 80), MOTION_ROOT / "chase_hero_silhouette_velocity_v013.webp", 90)
    save_strip_gif(hero_ghost, (64, 80), MOTION_ROOT / "chase_hero_ghost_silhouette_velocity_v013.gif", 90)
    save_strip_webp(hero_ghost, (64, 80), MOTION_ROOT / "chase_hero_ghost_silhouette_velocity_v013.webp", 90)
    save_strip_gif(star, (32, 32), V009_REVIEW / "energy_star_v009.gif", 80)
    save_strip_gif(pulse, (64, 48), V009_REVIEW / "pulse_impact_v009.gif", 55)

    composite(bg_b, bg_a).save(V009_REVIEW / "v009_background_composite.png")
    save_palette_strip(bg_b, V009_REVIEW / "bg_b_v009_palette_strip.png")
    save_palette_strip(bg_a, V009_REVIEW / "bg_a_v009_palette_strip.png")
    save_tileset_sheet(bg_b, V009_REVIEW / "bg_b_v009_tileset_sheet.png", False)
    save_tileset_sheet(bg_a, V009_REVIEW / "bg_a_v009_tileset_sheet.png", True)

    assets = [
        v009_asset_stats(V009_BG_B),
        v009_asset_stats(V009_BG_A),
        v009_asset_stats(V009_HERO, (64, 80)),
        v009_asset_stats(V009_HERO_GHOST, (64, 80)),
        v009_asset_stats(V009_PURSUER_TORSO, (96, 80)),
        v009_asset_stats(V009_PURSUER_HEAD, (80, 64)),
        v009_asset_stats(V009_PURSUER_CLAW, (64, 64)),
        v009_asset_stats(V009_STAR, (32, 32)),
        v009_asset_stats(V009_PULSE, (64, 48)),
        v009_asset_stats(V009_CLOUD, (64, 32)),
        v009_asset_stats(V009_LETTERBOX),
    ]
    report = {
        "schema": "chase_v009_translation_report_v1",
        "status": "source_derived_runtime_candidate_pending_blastem_and_human_review",
        "problem_class": "asset_palette_runtime_composition_and_scene_architecture",
        "hero_frame_policy": {
            "source_frame_count": 8,
            "selected_source_frames_zero_based": [0, 3, 4, 7],
            "rejected_source_frames_zero_based": [1, 2, 5, 6],
            "reason": "Reject reported anatomy and face-palette defects rather than hiding them with timing.",
        },
        "palette_policy": {
            "index_zero": "deep black backdrop on BG_B; transparent on BG_A and sprites",
            "grid": "Mega Drive 9-bit",
            "contrast": "deep navy, saturated indigo, ivory and gold separation",
        },
        "pursuer_modular_policy": {
            "parts": ["torso", "head", "claw_shared_hflip"],
            "runtime_required": True,
            "monolithic_body_runtime_rejected": True,
        },
        "fx_policy": {
            "energy_star_frames": 4,
            "pulse_expansion_frames": 6,
            "opaque_matte_rejected": True,
        },
        "assets": assets,
        "delivery_findings": [
            "All v009 critical sprite assets reserve index 0 for transparency.",
            "BG_B no longer uses palette index 0 for visible beige pixels.",
            "BG_A road overlay receives the v014 cinematic polish before tile dedup: singleton noise is reduced and perspective rows/vanishing lines are explicit.",
            "The corrected hero loop intentionally uses fewer frames rather than preserving broken anatomy.",
            "No human visual approval is inferred by the builder.",
        ],
    }
    write_json(CASE_ROOT / "v009_translation_report.json", report)
    return report


def build_v011_assets() -> dict:
    bg_b = extend_canvas_with_mirrored_gutters(Image.open(V009_BG_B))
    bg_a = extend_canvas_with_mirrored_gutters(Image.open(V009_BG_A))
    boulder = derive_contact_scaled_strip(Image.open(RES_SPRITES / "chase_obstacle_boulder_64x48.png"))
    brand = derive_contact_scaled_strip(Image.open(RES_SPRITES / "chase_obstacle_brand_64x48.png"))
    torso = derive_v011_torso_strip(
        ensure_transparent_zero(Image.open(PURSUER_BODY_SOURCE)),
        (96, 80),
    )
    contact_shadow = derive_contact_shadow_strip(bg_a)
    hud_font = derive_hud_font(Image.open(DEFAULT_FONT_SOURCE), torso)

    for image, path, transparent in (
        (bg_b, V011_BG_B, False),
        (bg_a, V011_BG_A, True),
        (boulder, V011_BOULDER, True),
        (brand, V011_BRAND, True),
        (torso, V011_PURSUER_TORSO, True),
        (contact_shadow, V011_CONTACT_SHADOW, True),
        (hud_font, V011_HUD_FONT, False),
    ):
        save_indexed(image, path, transparent)

    visible_bg_b = bg_b.crop((96, 0, 416, 224))
    visible_bg_a = bg_a.crop((96, 0, 416, 224))
    composite(visible_bg_b, visible_bg_a).save(V011_REVIEW / "v011_background_composite.png")
    save_strip_gif(boulder, (64, 48), V011_REVIEW / "boulder_depth_stages_v011.gif", 140)
    save_strip_gif(brand, (64, 48), V011_REVIEW / "brand_depth_stages_v011.gif", 140)
    save_strip_gif(torso, (96, 80), V011_REVIEW / "pursuer_torso_rear_cycle_v011.gif", 100)

    assets = [
        v009_asset_stats(V011_BG_B),
        v009_asset_stats(V011_BG_A),
        v009_asset_stats(V011_BOULDER, (64, 48)),
        v009_asset_stats(V011_BRAND, (64, 48)),
        v009_asset_stats(V011_PURSUER_TORSO, (96, 80)),
        v009_asset_stats(V011_CONTACT_SHADOW, (16, 8)),
        v009_asset_stats(V011_HUD_FONT),
    ]
    report = {
        "schema": "chase_v011_translation_report_v1",
        "status": "source_derived_runtime_candidate_pending_rescomp_blastem_and_human_review",
        "background_gutter_policy": {
            "source_width_px": 320,
            "runtime_width_px": 512,
            "gutter_px_each_side": 96,
            "method": "tile_aligned_horizontal_mirror",
            "bg_b_flip_aware_unique_tiles": tile_count_with_flips(bg_b),
            "bg_a_flip_aware_unique_tiles": tile_count_with_flips(bg_a, True),
        },
        "obstacle_depth_policy": {
            "frame_count": 4,
            "frame_size": [64, 48],
            "scale_factors": [0.50, 0.66, 0.82, 1.00],
            "contact_anchor": "bottom_center",
            "runtime_rule": "switch frames only at shared obstacle Z thresholds",
        },
        "pursuer_torso_policy": {
            "collar_overlap_margin_px": 6,
            "rear_body_region": [28, 54, 68, 80],
            "rear_body_frame_variants": frame_region_variant_count(torso, (96, 80), (28, 54, 68, 80)),
            "runtime_rule": "head swing and bob remain inside the source-baked collar overlap",
        },
        "contact_shadow_policy": {
            "frame_count": 3,
            "frame_size": [16, 8],
            "palette": "PAL3 road dark index with transparent dithering",
            "estimated_resident_sprite_tiles": 10,
            "owners": ["chase_player", "chase_obstacles", "chase_pursuer"],
        },
        "hud_font_policy": {
            "source": DEFAULT_FONT_SOURCE.relative_to(PROJECT.parents[1]).as_posix(),
            "glyph_count": 96,
            "vram_route": "replace_reserved_font_tiles",
            "palette_indices": {"shadow": 10, "face": 15},
            "status": "source_derived_candidate_pending_human_review",
        },
        "assets": assets,
        "delivery_findings": [
            "The visible 320px background composition carries the v014 road polish from the v009 source pass.",
            "Mirrored gutters remain tile aligned so ResComp can reuse flipped tiles.",
            "Obstacle scale stages reuse one resident VRAM slot per obstacle.",
            "No human visual approval is inferred by the builder.",
        ],
    }
    write_json(CASE_ROOT / "v011_translation_report.json", report)
    return report


def main() -> None:
    ensure_dirs()
    copied_sources = [
        (BG_B_SOURCE, SOURCE_ROOT / "background" / BG_B_SOURCE.name),
        (BG_A_SOURCE, SOURCE_ROOT / "background" / BG_A_SOURCE.name),
        (COMPOSITE_SOURCE, SOURCE_ROOT / "background" / COMPOSITE_SOURCE.name),
        (PROPS_SOURCE, SOURCE_ROOT / "props" / PROPS_SOURCE.name),
        (FX_SOURCE, SOURCE_ROOT / "fx" / FX_SOURCE.name),
    ]
    for source, destination in copied_sources:
        copy_source(source, destination)

    background_stats = build_backgrounds()
    sprite_stats = build_gameplay_sprites()
    v009_report = build_v009_assets()
    v011_report = build_v011_assets()

    source_inventory = [
        {
            "path": destination.relative_to(PROJECT).as_posix(),
            "sha256": sha256(destination),
            "source_path": source.relative_to(PROJECT).as_posix(),
        }
        for source, destination in copied_sources
    ]

    write_json(
        SOURCE_ROOT / "premium_source_manifest.json",
        {
            "schema": "premium_source_manifest_v1",
            "asset_family": "chase_first_playable",
            "source_validity": True,
            "authoriality_basis": "project_local_celestial_chase_source_package",
            "accepted_as_premium_source": False,
            "human_approval_status": "pending_for_background_props_and_fx",
            "protected_source_baked_character_pixels": True,
            "sources": source_inventory,
        },
    )

    write_json(
        CASE_ROOT / "semantic_parse_report.json",
        {
            "schema": "semantic_parse_report_v1",
            "translation_target": "scene_slice_and_gameplay_sprites",
            "layout_classification": {
                "background_pair": "paired_bg_scene_slice",
                "props": "editorial_object_board",
                "fx": "editorial_fx_board",
            },
            "usable_regions": [
                "v007 BG_B atmosphere",
                "v007 BG_A road overlay",
                "boulder, astral brand and obelisk prop regions",
                "energy star and pulse impact FX regions",
            ],
            "drop_policy": [
                "board backgrounds",
                "unused scale variants",
                "metadata-free editorial spacing",
            ],
            "must_keep": [
                "celestial horizon",
                "gold road focal line",
                "navy-indigo-gold material hierarchy",
                "telegraph silhouette readability",
            ],
        },
    )
    write_json(
        CASE_ROOT / "observed_ir.json",
        {
            "schema": "observed_ir_v1",
            "facts": [
                "BG_B and BG_A share a 320x224 canvas.",
                "BG_A uses palette index 0 as structural transparency.",
                "The direct pair exceeds the scene-local background target.",
                "Props and FX boards contain multiple scale variants on editorial backgrounds.",
            ],
        },
    )
    write_json(
        CASE_ROOT / "derived_structure_ir.json",
        {
            "schema": "derived_structure_ir_v1",
            "confidence": "high",
            "structure": {
                "BG_B": "atmosphere, horizon and under-road continuity",
                "BG_A": "playable road and near foreground",
                "sprites": "hazards, pickup and pulse feedback",
            },
            "resource_model": "scene_local_preload",
            "fallback": "existing tile-light background if runtime budget or perception fails",
        },
    )
    write_json(
        CASE_ROOT / "translation_report.json",
        {
            "schema": "art_translation_report_v1",
            "status": "runtime_candidate_pending_rescomp_blastem_and_human_review",
            "basic": background_stats["basic"],
            "elite": background_stats["elite"],
            "elite_method": {
                "BG_B": "tile representative reuse with 4x4 signature blocks",
                "BG_A": "tile representative reuse with 2x2 signature blocks",
                "global_downscale": False,
                "source_baked_character_pixels_modified": False,
            },
            "runtime_sprites": sprite_stats,
            "dominant_problem_class": "erro_de_budget",
            "delivery_findings": [
                "Elite preserves the v007 focal road while reducing resident background tiles.",
                "Translated props and FX remain perceptual candidates until seen at gameplay speed.",
                "No human approval is inferred by this builder.",
            ],
        },
    )
    write_json(
        CASE_ROOT / "source_to_rom_asset_map.json",
        {
            "schema": "source_to_rom_asset_map_v1",
            "status": "candidate",
            "assets": [
                {
                    "source": "data/source_art/chase_first_playable/background",
                    "runtime": RUNTIME_BG_B.relative_to(PROJECT).as_posix(),
                    "sha256": sha256(RUNTIME_BG_B),
                },
                {
                    "source": "data/source_art/chase_first_playable/background",
                    "runtime": RUNTIME_BG_A.relative_to(PROJECT).as_posix(),
                    "sha256": sha256(RUNTIME_BG_A),
                },
                *[
                    {
                        "source": "data/source_art/chase_first_playable/props_or_fx",
                        "runtime": sprite["path"],
                        "sha256": sprite["sha256"],
                    }
                    for sprite in sprite_stats
                ],
            ],
        },
    )
    write_json(
        CASE_ROOT / "hardware_budget_review.json",
        {
            "schema": "hardware_budget_review_v1",
            "technical_verdict": "cabe_com_recuo",
            "perceptual_verdict": "nao_perceptivel_ainda",
            "sprite_reserve_tiles": 420,
            "background_target_tiles": 1004,
            "basic_background_tiles": background_stats["basic"]["total_unique_tiles"],
            "elite_background_tiles": background_stats["elite"]["total_unique_tiles"],
            "elite_headroom_tiles": 1004 - background_stats["elite"]["total_unique_tiles"],
            "load_time_dma": "scene_enter_only",
            "per_frame_dma": "none_for_background_pair",
            "required_next_evidence": [
                "ResComp tile counts",
                "sprite scanline pressure",
                "BlastEm screenshot",
                "runtime perceptual review",
            ],
        },
    )

    print(
        json.dumps(
            {
                "backgrounds": background_stats,
                "sprites": sprite_stats,
                "v009_assets": len(v009_report["assets"]),
                "v011_assets": len(v011_report["assets"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
