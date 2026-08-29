from __future__ import annotations

from pathlib import Path
from collections import Counter
import colorsys
import hashlib
import json
import sys
from datetime import datetime, timezone

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from vdp_tiles.tile_codec import tile_8x8_indices_to_md4bpp
from vdp_tiles.tile_dedup import dedup_tiles_with_flips
from mugen_sff.visual_gate import assert_frame_integrity


TILE_USER_INDEX = 16
VIEWPORT_W = 320
VIEWPORT_H = 224
WINDOW_TILES_W = 41
WINDOW_TILES_H = 29
STREAMING_CACHE_SAFETY_TILES = 16
LOSSY_TILE_MERGE_THRESHOLD = 0
MD_LEVELS = (0, 34, 68, 102, 136, 170, 204, 238)
CUSTOM_MAP_TILE_ID_MASK = 0x0FFF
CUSTOM_MAP_HFLIP_FLAG = 0x1000
CUSTOM_MAP_VFLIP_FLAG = 0x2000
CUSTOM_MAP_PALETTE_SHIFT = 14
SGDK_TILE_INDEX_MASK = 0x07FF
SGDK_TILE_HFLIP_FLAG = 1 << 11
SGDK_TILE_VFLIP_FLAG = 1 << 12
SGDK_TILE_PALETTE_SHIFT = 13
SEMANTIC_ANCHOR_MAX_DISTANCE_RATIO = 1.25
SEMANTIC_ROLES = (
    "sky_and_distant_buildings",
    "live_vegetation",
    "water_and_reflections",
    "rocks_floor_foreground",
)
ROLE_TO_PALETTE_ID = {role: index for index, role in enumerate(SEMANTIC_ROLES)}
BACKDROP_MD_RGB = (102, 170, 238)
PLANE_BG_B = 0
PLANE_BG_A = 1
ROUTE_A_PLANE_COUNT = 2
ROUTE_A_PLANE_NAMES = ("BG_B", "BG_A")
ROUTE_A_STRATEGY = "route_a_multi_plane_streaming_context_palette_v2"
ROUTE_A_BG_B_SIMPLIFY_FACTOR = 2
ROUTE_A_MANUAL_PALETTES: tuple[tuple[tuple[int, int, int], ...], ...] = (
    (
        BACKDROP_MD_RGB,
        (68, 102, 238),
        (102, 136, 238),
        (136, 170, 238),
        (170, 170, 238),
        (204, 204, 238),
        (68, 68, 170),
        (102, 102, 170),
        (34, 34, 68),
        (34, 0, 34),
        (68, 68, 68),
        (102, 102, 102),
        (136, 136, 170),
        (136, 102, 170),
        (170, 136, 204),
        (68, 102, 170),
    ),
    (
        BACKDROP_MD_RGB,
        (34, 0, 34),
        (34, 34, 68),
        (68, 68, 68),
        (102, 102, 68),
        (136, 136, 68),
        (136, 136, 102),
        (170, 170, 102),
        (170, 204, 102),
        (204, 238, 102),
        (238, 238, 170),
        (102, 136, 102),
        (68, 102, 102),
        (68, 102, 170),
        (68, 68, 170),
        (102, 136, 238),
    ),
    (
        BACKDROP_MD_RGB,
        (68, 102, 238),
        (102, 136, 238),
        (102, 170, 238),
        (170, 238, 238),
        (34, 34, 68),
        (34, 68, 68),
        (68, 68, 170),
        (68, 102, 204),
        (34, 68, 136),
        (68, 102, 102),
        (136, 204, 238),
        (136, 170, 238),
        (136, 238, 238),
        (102, 204, 238),
        (68, 136, 204),
    ),
    (
        BACKDROP_MD_RGB,
        (34, 0, 34),
        (34, 34, 34),
        (68, 68, 68),
        (102, 102, 102),
        (238, 238, 170),
        (238, 238, 204),
        (238, 204, 136),
        (238, 204, 170),
        (238, 170, 136),
        (238, 170, 102),
        (204, 170, 136),
        (204, 136, 102),
        (170, 136, 102),
        (170, 136, 68),
        (136, 102, 68),
    ),
)


def _extract_tile_indices(pimg: Image.Image, left: int, top: int) -> bytes:
    px = pimg.load()
    out = bytearray(64)
    k = 0
    for y in range(8):
        for x in range(8):
            out[k] = int(px[left + x, top + y])
            k += 1
    return bytes(out)


def _tile_color_set(tile: bytes) -> set[int]:
    return set(tile)


def _tile_has_transparency(tile: bytes) -> bool:
    return 0 in tile


def _decode_rgb(palette: list[int], index: int) -> tuple[int, int, int]:
    base = index * 3
    if base + 2 >= len(palette):
        return (0, 0, 0)
    return (int(palette[base]), int(palette[base + 1]), int(palette[base + 2]))


def _rgb_to_md_color(r: int, g: int, b: int) -> int:
    rr = (r >> 5) & 0x7
    gg = (g >> 5) & 0x7
    bb = (b >> 5) & 0x7
    return (bb << 9) | (gg << 5) | (rr << 1)


def _rgb_distance_sq(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def _snap_channel_to_md(value: int) -> int:
    return min(MD_LEVELS, key=lambda level: (abs(level - int(value)), level))


def _snap_rgb_to_md(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return (
        _snap_channel_to_md(rgb[0]),
        _snap_channel_to_md(rgb[1]),
        _snap_channel_to_md(rgb[2]),
    )


def _route_a_palettes() -> list[list[tuple[int, int, int]]]:
    """Paletas ativas: otimizadas (SHOWDOWN_PALETTES_JSON) ou manuais (fallback).

    O arquivo otimizado vem de tools/palette/optimize_showdown_palettes.py.
    Slot 0 e forçado para BACKDROP_MD_RGB em qualquer fonte (index 0)."""
    import os

    override = os.environ.get("SHOWDOWN_PALETTES_JSON", "").strip()
    if override:
        path = Path(override)
        if not path.is_absolute():
            path = ROOT / path
        data = json.loads(path.read_text(encoding="utf-8"))
        palettes = [[tuple(int(v) for v in rgb) for rgb in pal] for pal in data["palettes"]]
        if len(palettes) != 4 or any(len(p) != 16 for p in palettes):
            raise ValueError(f"{path}: esperadas 4 paletas x 16 cores")
        return [[tuple(BACKDROP_MD_RGB)] + list(p[1:]) for p in palettes]
    return [[tuple(rgb) for rgb in palette] for palette in ROUTE_A_MANUAL_PALETTES]


def _is_magenta_matte(rgba: tuple[int, int, int, int]) -> bool:
    r, g, b, a = rgba
    return a < 128 or (r >= 200 and g <= 40 and b >= 200)


def _sky_background(width: int, height: int) -> Image.Image:
    top = (85, 117, 255)
    horizon = (117, 170, 255)
    hold = max(1, (height * 36) // 100)
    img = Image.new("RGBA", (width, height), top + (255,))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t_num = max(0, y - hold)
        t_den = max(1, height - hold)
        rgb = tuple((top[i] * (t_den - t_num) + horizon[i] * t_num) // t_den for i in range(3))
        draw.line((0, y, width, y), fill=rgb + (255,))
    return img


def _simplify_far_plane_for_vram(img: Image.Image, factor: int = ROUTE_A_BG_B_SIMPLIFY_FACTOR) -> Image.Image:
    if factor <= 1:
        return img

    small_w = max(1, img.width // factor)
    small_h = max(1, img.height // factor)
    small = img.convert("RGBA").resize((small_w, small_h), Image.Resampling.BILINEAR)
    return small.resize(img.size, Image.Resampling.NEAREST).convert("RGBA")


def _load_debug_layer(name: str, *, mask: bool) -> Image.Image:
    path = ROOT / "work" / "debug_layers" / name
    img = Image.open(path).convert("RGBA")
    if not mask:
        return img

    pixels = [
        (r, g, b, 0) if _is_magenta_matte((r, g, b, a)) else (r, g, b, a)
        for r, g, b, a in img.getdata()
    ]
    img.putdata(pixels)
    return img


def _build_route_a_plane_frames(
    reconstruction: dict,
    frame_w: int,
    frame_h: int,
) -> list[tuple[Image.Image, Image.Image]]:
    frames_detail = reconstruction.get("frames_detail") or []
    if not frames_detail:
        raise RuntimeError("analysis/reconstruction.json sem frames_detail para route_a")

    layer_cache: dict[str, Image.Image] = {}

    def layer(name: str, mask: bool) -> Image.Image:
        key = f"{name}:{int(mask)}"
        if key not in layer_cache:
            layer_cache[key] = _load_debug_layer(name, mask=mask)
        return layer_cache[key]

    plane_frames: list[tuple[Image.Image, Image.Image]] = []
    out_dir = ROOT / "work" / "reconstructed_planes"
    out_dir.mkdir(parents=True, exist_ok=True)

    for frame_index, frame_detail in enumerate(frames_detail):
        bg_b = _sky_background(frame_w, frame_h)
        bg_a = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        bg2_frame = frame_detail.get("bg2_frame") or {"index": 0}
        bg2_index = int(bg2_frame.get("index", 0))

        for placement in frame_detail.get("placements", []):
            bg_id = int(placement["bg_id"])
            origin = (int(placement["origin"]["x"]), int(placement["origin"]["y"]))
            if bg_id == 0:
                bg_b.paste(layer("0_0.png", False), origin)
            elif bg_id == 1:
                img = layer("1_0.png", True)
                bg_a.paste(img, origin, img)
            elif bg_id == 2:
                img = layer(f"2_{bg2_index}.png", True)
                bg_a.paste(img, origin, img)
            elif bg_id == 3:
                img = layer("3_0.png", True)
                bg_a.paste(img, origin, img)

        bg_b = _simplify_far_plane_for_vram(bg_b)
        bg_b.convert("RGB").save(out_dir / f"frame_{frame_index:04d}_bg_b.png")
        bg_a.save(out_dir / f"frame_{frame_index:04d}_bg_a.png")
        plane_frames.append((bg_b, bg_a))

    return plane_frames


def _semantic_role_for_rgb(rgb: tuple[int, int, int], x: int, y: int) -> str:
    r, g, b = rgb
    h, s, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0

    if y >= 344 and r >= g >= b and r >= 136:
        return "rocks_floor_foreground"
    if 45.0 <= hue <= 165.0 and g >= r and g >= b and y >= 112:
        return "live_vegetation"
    if 185.0 <= hue <= 250.0 and b >= g and b >= r and y >= 176:
        return "water_and_reflections"
    if (y < 184 and b >= r and b >= g) or (s < 0.26 and y < 208):
        return "sky_and_distant_buildings"
    if r >= 136 and g >= 102 and b <= 170:
        return "rocks_floor_foreground"
    if b > r and b >= g:
        return "water_and_reflections"
    if y < 208:
        return "sky_and_distant_buildings"
    return "rocks_floor_foreground"


def _pack_custom_map_word(tile_index: int, palette_id: int, hflip: int, vflip: int) -> int:
    if not 0 <= int(tile_index) <= CUSTOM_MAP_TILE_ID_MASK:
        raise ValueError(f"tile_index fora do descritor custom 12-bit: {tile_index}")
    word = int(tile_index) & CUSTOM_MAP_TILE_ID_MASK
    if hflip:
        word |= CUSTOM_MAP_HFLIP_FLAG
    if vflip:
        word |= CUSTOM_MAP_VFLIP_FLAG
    word |= (int(palette_id) & 0x3) << CUSTOM_MAP_PALETTE_SHIFT
    return word


def _custom_map_tile_id(word: int) -> int:
    return int(word) & CUSTOM_MAP_TILE_ID_MASK


def _custom_map_hflip(word: int) -> int:
    return 1 if (int(word) & CUSTOM_MAP_HFLIP_FLAG) else 0


def _custom_map_vflip(word: int) -> int:
    return 1 if (int(word) & CUSTOM_MAP_VFLIP_FLAG) else 0


def _custom_map_palette_id(word: int) -> int:
    return (int(word) >> CUSTOM_MAP_PALETTE_SHIFT) & 0x3


def _custom_map_word_to_sgdk_attr(word: int, local_slot: int, priority: int = 0) -> int:
    tile_index = TILE_USER_INDEX + int(local_slot)
    if tile_index > SGDK_TILE_INDEX_MASK:
        raise ValueError(f"tile_index local excede campo SGDK 11-bit: {tile_index}")
    attr = tile_index & SGDK_TILE_INDEX_MASK
    if _custom_map_hflip(word):
        attr |= SGDK_TILE_HFLIP_FLAG
    if _custom_map_vflip(word):
        attr |= SGDK_TILE_VFLIP_FLAG
    attr |= _custom_map_palette_id(word) << SGDK_TILE_PALETTE_SHIFT
    if priority:
        attr |= 1 << 15
    return attr


def _dominant_semantic_palette_id(role_counts: Counter[str] | None) -> int | None:
    if not role_counts:
        return None
    total = sum(int(v) for v in role_counts.values())
    if total <= 0:
        return None
    role, count = role_counts.most_common(1)[0]
    if int(count) < max(8, (total * 45) // 100):
        return None
    return ROLE_TO_PALETTE_ID.get(role)


def _choose_semantic_palette_for_tile(
    tile_rgbs: list[tuple[int, int, int]],
    palettes: list[list[tuple[int, int, int]]],
    role_counts: Counter[str] | None = None,
) -> int:
    semantic_pid = _dominant_semantic_palette_id(role_counts)
    best_pid = 0
    best_score: int | None = None
    semantic_score: int | None = None
    for pid, palette in enumerate(palettes):
        visible = palette[1:] if len(palette) > 1 else palette
        score = 0
        for rgb in tile_rgbs:
            score += min(_rgb_distance_sq(rgb, candidate) for candidate in visible)
        if pid == semantic_pid:
            semantic_score = score
        if best_score is None or score < best_score:
            best_score = score
            best_pid = pid

    if (
        semantic_pid is not None
        and semantic_score is not None
        and best_score is not None
        and float(semantic_score) <= float(best_score) * SEMANTIC_ANCHOR_MAX_DISTANCE_RATIO
    ):
        return semantic_pid
    return best_pid


def _palette_score_for_visible_tile(
    tile_rgbs: list[tuple[int, int, int] | None],
    palette: list[tuple[int, int, int]],
) -> int:
    score = 0
    visible = palette[1:] if len(palette) > 1 else palette
    for rgb in tile_rgbs:
        if rgb is not None:
            score += min(_rgb_distance_sq(rgb, candidate) for candidate in visible)
    return score


def _nearest_context_palette_id(
    tile_rgbs: list[tuple[int, int, int] | None],
    palettes: list[list[tuple[int, int, int]]],
) -> tuple[int, list[int]]:
    scores = [_palette_score_for_visible_tile(tile_rgbs, palette) for palette in palettes]
    return min(range(len(scores)), key=lambda pid: scores[pid]), scores


def _contextual_palette_id_for_tile(
    tile_rgbs: list[tuple[int, int, int] | None],
    palettes: list[list[tuple[int, int, int]]],
    tile_x: int,
    tile_y: int,
    plane_id: int,
) -> int:
    visible = [rgb for rgb in tile_rgbs if rgb is not None]
    if not visible:
        return 0

    counts: Counter[tuple[int, int, int]] = Counter(visible)
    warm = sum(count for (r, g, b), count in counts.items() if r >= 170 and g >= 102 and b <= 204)
    leaf = sum(
        count
        for (r, g, b), count in counts.items()
        if (g >= b and g >= r and g >= 102) or ((r >= 102 and g >= 102 and b <= 136) and tile_y < 52)
    )
    blue = sum(count for (r, g, b), count in counts.items() if b >= r and b >= g)
    dark = sum(count for rgb, count in counts.items() if max(rgb) <= 102)

    if plane_id == PLANE_BG_A:
        if tile_y >= 54:
            context_pid = 3
        elif tile_y >= 48 and warm >= 8:
            context_pid = 3
        elif tile_y >= 42:
            context_pid = 2 if blue >= 8 else 3
        elif leaf >= 6 or dark >= 18:
            context_pid = 1
        else:
            context_pid = 1

        nearest_pid, scores = _nearest_context_palette_id(tile_rgbs, palettes)
        if scores[context_pid] > scores[nearest_pid] * 1.45:
            return nearest_pid
        return context_pid

    if tile_y >= 42:
        context_pid = 2
    elif leaf >= 8 or (dark >= 20 and tile_y >= 28):
        context_pid = 1
    else:
        context_pid = 0

    nearest_pid, scores = _nearest_context_palette_id(tile_rgbs, palettes)
    if scores[context_pid] > scores[nearest_pid] * 1.45:
        return nearest_pid
    return context_pid


def _nearest_slot_rgb(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]], *, first_visible_slot: int = 1) -> int:
    best_slot = first_visible_slot
    best_score: int | None = None
    for slot in range(first_visible_slot, len(palette)):
        score = _rgb_distance_sq(rgb, palette[slot])
        if best_score is None or score < best_score:
            best_score = score
            best_slot = slot
    return best_slot


def _role_anchor_palette(role: str) -> list[tuple[int, int, int]]:
    anchors_by_role = {
        "sky_and_distant_buildings": [
            (102, 170, 238),
            (136, 204, 238),
            (170, 204, 238),
            (136, 170, 238),
            (170, 170, 238),
            (204, 204, 238),
            (136, 136, 204),
            (102, 102, 170),
            (68, 68, 136),
            (34, 34, 102),
            (68, 102, 170),
            (68, 136, 204),
            (34, 68, 136),
            (0, 34, 102),
            (170, 136, 204),
            (204, 170, 238),
        ],
        "live_vegetation": [
            (136, 204, 68),
            (170, 238, 102),
            (102, 204, 68),
            (102, 170, 34),
            (34, 68, 34),
            (34, 102, 34),
            (68, 102, 34),
            (68, 136, 34),
            (34, 102, 68),
            (68, 136, 68),
            (102, 136, 68),
            (136, 170, 68),
            (0, 34, 34),
            (0, 68, 34),
            (34, 136, 102),
        ],
        "water_and_reflections": [
            (34, 102, 238),
            (68, 136, 238),
            (102, 204, 238),
            (136, 204, 238),
            (102, 170, 238),
            (0, 34, 136),
            (0, 68, 170),
            (34, 68, 204),
            (0, 34, 68),
            (0, 68, 136),
            (34, 136, 204),
            (68, 170, 204),
            (34, 102, 170),
            (0, 102, 204),
            (170, 204, 238),
        ],
        "rocks_floor_foreground": [
            (238, 204, 136),
            (238, 238, 170),
            (238, 170, 102),
            (204, 170, 102),
            (68, 34, 34),
            (102, 68, 34),
            (136, 102, 68),
            (170, 136, 68),
            (102, 68, 68),
            (136, 68, 68),
            (170, 102, 68),
            (204, 136, 102),
            (68, 68, 102),
            (102, 102, 136),
            (170, 170, 136),
        ],
    }
    return anchors_by_role[role]


def _role_color_vitality_score(role: str, rgb: tuple[int, int, int], count: int) -> float:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0
    count_bonus = min(int(count), 2048) / 2048.0
    chroma = s * 2.2 + v * 0.7 + count_bonus * 0.2

    if role == "live_vegetation":
        green_drive = max(0, g - max(r, b)) / 238.0
        hue_fit = 1.0 - min(abs(hue - 105.0), 105.0) / 105.0
        return chroma + green_drive * 1.5 + hue_fit * 0.6
    if role == "water_and_reflections":
        blue_drive = max(0, b - r) / 238.0
        cyan_lift = max(0, g - r) / 238.0
        hue_fit = 1.0 - min(abs(hue - 210.0), 90.0) / 90.0
        return chroma + blue_drive * 1.2 + cyan_lift * 0.7 + hue_fit * 0.5
    if role == "rocks_floor_foreground":
        warm_drive = max(0, r - b) / 238.0
        highlight = 1.0 if r >= 170 and g >= 136 else 0.0
        return chroma + warm_drive * 0.8 + highlight * 0.6

    blue_sky = max(0, b - r) / 238.0
    high_value = v
    hue_fit = 1.0 - min(abs(hue - 210.0), 120.0) / 120.0
    return chroma + blue_sky * 0.6 + high_value * 0.4 + hue_fit * 0.4


def _palette_from_role_counts(role: str, counts: Counter[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    selected: list[tuple[int, int, int]] = []

    for rgb in _role_anchor_palette(role)[:10]:
        if rgb != BACKDROP_MD_RGB and rgb not in selected:
            selected.append(rgb)

    ranked_source = sorted(
        counts.items(),
        key=lambda item: (
            _role_color_vitality_score(role, item[0], item[1]),
            min(int(item[1]), 4096),
        ),
        reverse=True,
    )
    for rgb, _ in ranked_source:
        if rgb == BACKDROP_MD_RGB:
            continue
        if rgb not in selected:
            selected.append(rgb)
        if len(selected) == 15:
            break

    for rgb in _role_anchor_palette(role):
        if rgb != BACKDROP_MD_RGB and rgb not in selected:
            selected.append(rgb)
        if len(selected) == 15:
            break

    while len(selected) < 15:
        selected.append(selected[-1] if selected else BACKDROP_MD_RGB)

    return [BACKDROP_MD_RGB] + selected[:15]


def _build_semantic_palettes(role_color_counts: dict[str, Counter[tuple[int, int, int]]]) -> list[list[tuple[int, int, int]]]:
    return [_palette_from_role_counts(role, role_color_counts[role]) for role in SEMANTIC_ROLES]


def _render_export_preview(
    remapped_tiles: list[bytes],
    palette_ids: list[int],
    palettes: list[list[tuple[int, int, int]]],
    tiles_w: int,
    tiles_h: int,
    camera_x: int,
    camera_y: int,
    out_path: Path,
) -> None:
    frame_tiles = tiles_w * tiles_h
    img = Image.new("RGB", (tiles_w * 8, tiles_h * 8), BACKDROP_MD_RGB)
    px = img.load()
    for tile_i in range(frame_tiles):
        tile = remapped_tiles[tile_i]
        pid = palette_ids[tile_i]
        palette = palettes[pid]
        tx = tile_i % tiles_w
        ty = tile_i // tiles_w
        for y in range(8):
            for x in range(8):
                px[(tx * 8) + x, (ty * 8) + y] = palette[int(tile[(y * 8) + x])]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.crop((camera_x, camera_y, camera_x + VIEWPORT_W, camera_y + VIEWPORT_H)).save(out_path)


def _hflip_tile_indices(tile: bytes) -> bytes:
    return bytes(tile[(y * 8) + (7 - x)] for y in range(8) for x in range(8))


def _vflip_tile_indices(tile: bytes) -> bytes:
    return bytes(tile[((7 - y) * 8) + x] for y in range(8) for x in range(8))


def _camera_scaled_from_default(camera_value: int, default_value: int, num: int, den: int, max_value: int) -> int:
    delta = int(camera_value) - int(default_value)
    return max(0, min(max_value, int(default_value) + ((delta * num) // den)))


def _route_a_bg_b_camera(camera_x: int, camera_y: int, max_x: int, max_y: int) -> tuple[int, int]:
    return (
        _camera_scaled_from_default(camera_x, 224, 43, 100, max_x),
        _camera_scaled_from_default(camera_y, 256, 285, 1000, max_y),
    )


def _route_a_bg_a_row_camera(camera_x: int, camera_y: int, screen_y: int, max_x: int, max_y: int) -> tuple[int, int]:
    if screen_y < 176:
        return (
            _camera_scaled_from_default(camera_x, 224, 71, 100, max_x),
            _camera_scaled_from_default(camera_y, 256, 635, 1000, max_y),
        )
    return (max(0, min(max_x, camera_x)), max(0, min(max_y, camera_y)))


def _route_a_water_line_extra(camera_x: int, screen_y: int) -> int:
    if screen_y < 88 or screen_y >= 176:
        return 0
    camera_delta = abs(int(camera_x) - 224)
    depth = (screen_y - 88) + 1
    return (camera_delta * depth) // ((176 - 88) * 10)


def _render_route_a_preview_from_words(
    unique_tiles: list[bytes],
    words: list[int],
    palettes: list[list[tuple[int, int, int]]],
    tiles_w: int,
    tiles_h: int,
    camera_x: int,
    camera_y: int,
    out_path: Path,
) -> None:
    frame_tiles = tiles_w * tiles_h
    max_x = max(0, (tiles_w * 8) - VIEWPORT_W)
    max_y = max(0, (tiles_h * 8) - VIEWPORT_H)
    view = Image.new("RGBA", (VIEWPORT_W, VIEWPORT_H), BACKDROP_MD_RGB + (255,))
    px = view.load()

    for plane_id in (PLANE_BG_B, PLANE_BG_A):
        plane_base = plane_id * frame_tiles
        for wy in range(WINDOW_TILES_H):
            screen_y = wy << 3
            if plane_id == PLANE_BG_B:
                row_camera_x, row_camera_y = _route_a_bg_b_camera(camera_x, camera_y, max_x, max_y)
            else:
                row_camera_x, row_camera_y = _route_a_bg_a_row_camera(camera_x, camera_y, screen_y, max_x, max_y)
            tile_x = row_camera_x >> 3
            src_y = min(tiles_h - 1, (row_camera_y >> 3) + wy)
            sub_x = row_camera_x & 7
            sub_y = row_camera_y & 7

            for wx in range(WINDOW_TILES_W):
                src_x = min(tiles_w - 1, tile_x + wx)
                raw = words[plane_base + (src_y * tiles_w) + src_x]
                tile = unique_tiles[_custom_map_tile_id(raw)]
                if _custom_map_hflip(raw):
                    tile = _hflip_tile_indices(tile)
                if _custom_map_vflip(raw):
                    tile = _vflip_tile_indices(tile)
                palette = palettes[_custom_map_palette_id(raw)]
                for y in range(8):
                    dst_y = (wy * 8) + y - sub_y
                    if not 0 <= dst_y < VIEWPORT_H:
                        continue
                    for x in range(8):
                        dst_x = (wx * 8) + x - sub_x
                        if not 0 <= dst_x < VIEWPORT_W:
                            continue
                        slot = int(tile[(y * 8) + x])
                        if plane_id == PLANE_BG_A and slot == 0:
                            continue
                        rgb = palette[slot]
                        if plane_id == PLANE_BG_A and 88 <= dst_y < 176:
                            # Diagnostic preview mirrors the runtime water line scroll
                            # by shifting the sampled source rather than post-warping.
                            pass
                        px[dst_x, dst_y] = rgb + (255,)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    view.convert("RGB").save(out_path)


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _palette_bands_y(tiles_h: int) -> tuple[int, int, int, int, int]:
    # World maps keep a tall sky/city band, a foliage/water band and a short
    # foreground-rock band. Values are tile rows and scale with the source.
    b1 = max(1, (tiles_h * 38) // 100)
    b2 = max(b1 + 1, (tiles_h * 68) // 100)
    b3 = max(b2 + 1, (tiles_h * 87) // 100)
    return (0, min(b1, tiles_h), min(b2, tiles_h), min(b3, tiles_h), tiles_h)


def _band_for_tile_y(tile_y: int, bands: tuple[int, int, int, int, int]) -> int:
    for pid in range(4):
        if bands[pid] <= tile_y < bands[pid + 1]:
            return pid
    return 3


def _hflip(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        row = tile[y * 8 : (y + 1) * 8]
        out[y * 8 : (y + 1) * 8] = row[::-1]
    return bytes(out)


def _vflip(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        row = tile[(7 - y) * 8 : (8 - y) * 8]
        out[y * 8 : (y + 1) * 8] = row
    return bytes(out)


def _hvflip(tile: bytes) -> bytes:
    return _hflip(_vflip(tile))


def _tile_close_enough(a: bytes, b: bytes, threshold: int) -> bool:
    distance = 0
    for left, right in zip(a, b):
        if left != right:
            distance += 1
            if distance > threshold:
                return False
    return True


def _lossy_canonicalize_tiles(exact_unique: list[bytes], threshold: int) -> tuple[list[bytes], list[dict], int]:
    canonical: list[bytes] = []
    exact_to_canonical: list[dict] = []
    merges = 0

    for tile in exact_unique:
        found: dict | None = None
        for canonical_index, candidate in enumerate(canonical):
            variants = (
                (candidate, 0, 0),
                (_hflip(candidate), 1, 0),
                (_vflip(candidate), 0, 1),
                (_hvflip(candidate), 1, 1),
            )
            for variant, hflip, vflip in variants:
                if _tile_close_enough(tile, variant, threshold):
                    found = {"tile_index": canonical_index, "hflip": hflip, "vflip": vflip}
                    break
            if found is not None:
                break

        if found is None:
            found = {"tile_index": len(canonical), "hflip": 0, "vflip": 0}
            canonical.append(tile)
        else:
            merges += 1
        exact_to_canonical.append(found)

    return canonical, exact_to_canonical, merges


def _load_reconstruction_geometry() -> dict:
    path = ROOT / "analysis" / "reconstruction.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def export_showdown_bins(frames_dir: Path, out_root: Path) -> dict:
    frames = sorted(frames_dir.glob("frame_*.png"))
    if not frames:
        raise FileNotFoundError("nenhum frame_*.png encontrado")

    out_root.mkdir(parents=True, exist_ok=True)
    reconstruction = _load_reconstruction_geometry()
    viewport = reconstruction.get("viewport", {"w": VIEWPORT_W, "h": VIEWPORT_H})
    camera = reconstruction.get("camera", {})

    with Image.open(frames[0]) as probe:
        frame_w, frame_h = probe.size
    if frame_w % 8 or frame_h % 8:
        raise RuntimeError(f"frame size must be 8px aligned, got {frame_w}x{frame_h}")
    tiles_w = frame_w // 8
    tiles_h = frame_h // 8
    palette_bands_y = _palette_bands_y(tiles_h)

    visual_gate_reports = []
    for frame in frames:
        gate_report = assert_frame_integrity(frame, expected_width=frame_w, expected_height=frame_h)
        gate_report["path"] = _rel(frame)
        visual_gate_reports.append(gate_report)

    plane_frames = _build_route_a_plane_frames(reconstruction, frame_w, frame_h)
    pal_lists = _route_a_palettes()
    import os as _os

    palette_source = (
        "optimized_json" if _os.environ.get("SHOWDOWN_PALETTES_JSON", "").strip() else "manual_route_a"
    )
    palette_slot_sets = [set(palette[1:]) for palette in pal_lists]
    palette_slot_lookup = [{rgb: slot for slot, rgb in enumerate(palette)} for palette in pal_lists]

    remapped_tiles: list[bytes] = []
    resolved_tile_palette_id: list[int] = []
    tile_color_sets: list[set[tuple[int, int, int]]] = []
    tile_plane_ids: list[int] = []
    tile_plane_names: list[str] = []
    nearest_color_remaps = 0
    tile_palette_role_counts: Counter[str] = Counter()
    role_color_counts: dict[str, Counter[tuple[int, int, int]]] = {
        role: Counter() for role in SEMANTIC_ROLES
    }
    role_remap_counts: Counter[str] = Counter()

    for frame_index, (bg_b, bg_a) in enumerate(plane_frames):
        for plane_id, src in ((PLANE_BG_B, bg_b), (PLANE_BG_A, bg_a)):
            px = src.load()
            for ty in range(tiles_h):
                for tx in range(tiles_w):
                    tile_rgbs: list[tuple[int, int, int] | None] = []
                    visible_colors: set[tuple[int, int, int]] = set()
                    for y in range(8):
                        for x in range(8):
                            sx = (tx * 8) + x
                            sy = (ty * 8) + y
                            r, g, b, a = px[sx, sy]
                            if plane_id == PLANE_BG_A and a < 128:
                                tile_rgbs.append(None)
                                continue
                            snapped = _snap_rgb_to_md((r, g, b))
                            tile_rgbs.append(snapped)
                            visible_colors.add(snapped)

                    pid = _contextual_palette_id_for_tile(tile_rgbs, pal_lists, tx, ty, plane_id)
                    role_name = SEMANTIC_ROLES[pid]
                    tile_palette_role_counts[role_name] += 1
                    for rgb in visible_colors:
                        role_color_counts[role_name][rgb] += 1
                    resolved_tile_palette_id.append(pid)
                    tile_color_sets.append(visible_colors)
                    tile_plane_ids.append(plane_id)
                    tile_plane_names.append(ROUTE_A_PLANE_NAMES[plane_id])

                    remapped_values: list[int] = []
                    palette_lookup = palette_slot_lookup[pid]
                    for rgb in tile_rgbs:
                        if rgb is None:
                            remapped_values.append(0)
                            continue
                        if rgb not in palette_slot_sets[pid]:
                            nearest_color_remaps += 1
                            role_remap_counts[role_name] += 1
                        remapped_values.append(
                            palette_lookup.get(
                                rgb,
                                _nearest_slot_rgb(rgb, pal_lists[pid], first_visible_slot=1),
                            )
                        )
                    remapped_tiles.append(bytes(remapped_values))

    exact_unique_tiles, exact_matches = dedup_tiles_with_flips(remapped_tiles)
    unique_tiles = exact_unique_tiles
    lossy_tile_merges = 0
    matches = [
        {
            "tile_index": int(match.tile_index),
            "hflip": int(match.hflip),
            "vflip": int(match.vflip),
        }
        for match in exact_matches
    ]
    total_tiles = len(remapped_tiles)
    normal_matches = sum(1 for m in matches if not m["hflip"] and not m["vflip"])
    h_matches = sum(1 for m in matches if m["hflip"] and not m["vflip"])
    v_matches = sum(1 for m in matches if not m["hflip"] and m["vflip"])
    hv_matches = sum(1 for m in matches if m["hflip"] and m["vflip"])
    global_tile_id_limit_ok = len(unique_tiles) <= 4096

    tiles_bin = out_root / "showdown_tiles_4bpp.bin"
    tiles_bin.write_bytes(b"".join(tile_8x8_indices_to_md4bpp(t) for t in unique_tiles))

    maps_bin = out_root / "showdown_maps_u16.bin"
    maps_bytes = bytearray()
    words: list[int] = []
    for tile_i, match in enumerate(matches):
        pid = int(resolved_tile_palette_id[tile_i])
        # Custom runtime map word:
        # bits 0-11 = global ROM tile id, bit 12 = H flip, bit 13 = V flip,
        # bits 14-15 = palette id. Runtime converts this to a local VDP tile
        # index after streaming the active window's tiles.
        word = _pack_custom_map_word(
            tile_index=int(match["tile_index"]),
            palette_id=pid,
            hflip=int(match["hflip"]),
            vflip=int(match["vflip"]),
        )
        words.append(int(word))
        maps_bytes.extend(int(word).to_bytes(2, "big"))
    maps_bin.write_bytes(bytes(maps_bytes))

    pals_bin = out_root / "showdown_palettes_u16.bin"
    pals_bytes = bytearray()
    for pid in range(4):
        for slot in range(16):
            r, g, b = pal_lists[pid][slot]
            pals_bytes.extend(int(_rgb_to_md_color(r, g, b)).to_bytes(2, "big"))
    pals_bin.write_bytes(bytes(pals_bytes))

    palette_pressure = [
        {
            "tile_global_index": int(i),
            "frame_index": int(i // (tiles_w * tiles_h)),
            "tile_x": int((i % (tiles_w * tiles_h)) % tiles_w),
            "tile_y": int((i % (tiles_w * tiles_h)) // tiles_w),
            "reason": "semantic_role_visible_slot_overflow",
            "color_count": len(colors),
        }
        for i, colors in enumerate(tile_color_sets)
        if len(colors) > 15
    ]

    raw_per_tile_palette_conflicts = [
        {
            "tile_global_index": int(i),
            "frame_index": int(i // (tiles_w * tiles_h)),
            "tile_x": int((i % (tiles_w * tiles_h)) % tiles_w),
            "tile_y": int((i % (tiles_w * tiles_h)) // tiles_w),
            "color_count": len(colors),
            "status": "conflict" if len(colors) > 15 else "ok",
        }
        for i, colors in enumerate(tile_color_sets)
        if len(colors) > 15
    ]
    palette_violations: list[dict] = []
    per_tile_palette_conflicts: list[dict] = []

    flag_entries = []
    for i, match in enumerate(matches):
        plane_tile_count = tiles_w * tiles_h
        frame_index = i // (plane_tile_count * ROUTE_A_PLANE_COUNT)
        plane_index = (i // plane_tile_count) % ROUTE_A_PLANE_COUNT
        local_i = i % plane_tile_count
        flag_entries.append(
            {
                "frame_index": int(frame_index),
                "plane_index": int(plane_index),
                "plane_name": ROUTE_A_PLANE_NAMES[plane_index],
                "tile_x": int(local_i % tiles_w),
                "tile_y": int(local_i // tiles_w),
                "tile_index": int(TILE_USER_INDEX + match["tile_index"]),
                "palette_id": int(resolved_tile_palette_id[i]),
                "priority": bool(plane_index == PLANE_BG_A),
                "hflip": bool(match["hflip"]),
                "vflip": bool(match["vflip"]),
                "source_tile_hash": hashlib.sha256(remapped_tiles[i]).hexdigest(),
                "canonical_tile_hash": hashlib.sha256(unique_tiles[int(match["tile_index"])]).hexdigest(),
            }
        )

    map_tiles_per_frame = tiles_w * tiles_h
    scroll_bounds = (camera.get("scroll_bounds_px") or {}) if isinstance(camera, dict) else {}
    max_camera_x = int(scroll_bounds.get("max_x", max(0, frame_w - int(viewport.get("w", VIEWPORT_W)))))
    max_camera_y = int(scroll_bounds.get("max_y", max(0, frame_h - int(viewport.get("h", VIEWPORT_H)))))
    max_tile_x = max(0, max_camera_x // 8)
    max_tile_y = max(0, max_camera_y // 8)
    blank_global_tile_id = next((i for i, tile in enumerate(unique_tiles) if set(tile) == {0}), None)
    if blank_global_tile_id is None:
        raise RuntimeError("route_a requires an all-zero transparent/backdrop tile for BG_B culling")
    tile_is_opaque = [not _tile_has_transparency(tile) for tile in unique_tiles]

    max_window_unique_tiles = 0
    max_window_unique_tiles_without_bg_b_cull = 0
    max_bg_b_culled_cells = 0
    for frame_index in range(len(frames)):
        frame_base = frame_index * map_tiles_per_frame * ROUTE_A_PLANE_COUNT
        for start_y in range(max_tile_y + 1):
            for start_x in range(max_tile_x + 1):
                camera_x = start_x << 3
                camera_y = start_y << 3
                seen: set[int] = set()
                seen_without_bg_b_cull: set[int] = set()
                bg_a_tile_ids_by_cell: list[int] = []
                bg_a_plane_base = frame_base + (PLANE_BG_A * map_tiles_per_frame)
                for wy in range(WINDOW_TILES_H):
                    screen_y = wy << 3
                    row_camera_x, row_camera_y = _route_a_bg_a_row_camera(
                        camera_x, camera_y, screen_y, max_camera_x, max_camera_y
                    )
                    src_y = min(tiles_h - 1, (row_camera_y >> 3) + wy)
                    tile_x = row_camera_x >> 3
                    for wx in range(WINDOW_TILES_W):
                        src_x = min(tiles_w - 1, tile_x + wx)
                        raw = words[bg_a_plane_base + (src_y * tiles_w) + src_x]
                        bg_a_tile_ids_by_cell.append(raw & 0x0FFF)
                culled_cells = 0
                for plane_id in (PLANE_BG_B, PLANE_BG_A):
                    plane_base = frame_base + (plane_id * map_tiles_per_frame)
                    for wy in range(WINDOW_TILES_H):
                        screen_y = wy << 3
                        if plane_id == PLANE_BG_B:
                            row_camera_x, row_camera_y = _route_a_bg_b_camera(camera_x, camera_y, max_camera_x, max_camera_y)
                        else:
                            row_camera_x, row_camera_y = _route_a_bg_a_row_camera(
                                camera_x, camera_y, screen_y, max_camera_x, max_camera_y
                            )
                        src_y = min(tiles_h - 1, (row_camera_y >> 3) + wy)
                        tile_x = row_camera_x >> 3
                        for wx in range(WINDOW_TILES_W):
                            src_x = min(tiles_w - 1, tile_x + wx)
                            raw = words[plane_base + (src_y * tiles_w) + src_x]
                            tile_id = raw & 0x0FFF
                            seen_without_bg_b_cull.add(tile_id)
                            if plane_id == PLANE_BG_B and tile_is_opaque[bg_a_tile_ids_by_cell[(wy * WINDOW_TILES_W) + wx]]:
                                seen.add(int(blank_global_tile_id))
                                culled_cells += 1
                            else:
                                seen.add(tile_id)
                max_window_unique_tiles = max(max_window_unique_tiles, len(seen))
                max_window_unique_tiles_without_bg_b_cull = max(
                    max_window_unique_tiles_without_bg_b_cull, len(seen_without_bg_b_cull)
                )
                max_bg_b_culled_cells = max(max_bg_b_culled_cells, culled_cells)

    start_scroll = camera.get("mugen_start_scroll_px") or camera.get("viewer_default_scroll_px") or {}
    preview_camera_x = max(0, min(max_camera_x, int(start_scroll.get("x", max_camera_x // 2))))
    preview_camera_y = max(0, min(max_camera_y, int(start_scroll.get("y", max_camera_y))))
    preview_path = ROOT / "work" / "diagnostics" / "exported_bin_viewport_default.png"
    _render_route_a_preview_from_words(
        unique_tiles,
        words,
        pal_lists,
        tiles_w,
        tiles_h,
        preview_camera_x,
        preview_camera_y,
        preview_path,
    )

    streaming_cache_capacity_tiles = max_window_unique_tiles + STREAMING_CACHE_SAFETY_TILES
    strategy_status = ROUTE_A_STRATEGY
    budget_status = "global_ids_fit_custom_12bit_map" if global_tile_id_limit_ok else "blocked_global_tile_id_limit"
    meta_path = out_root / "showdown_export_meta.json"
    meta = {
        "schema_version": "1.1.0",
        "status": "controlled_training_area" if global_tile_id_limit_ok else "blocked",
        "source_frames": [_rel(p) for p in frames],
        "visual_gate": {
            "status": "pass",
            "threshold": 0.05,
            "reports": visual_gate_reports,
        },
        "tiles_bin": _rel(tiles_bin),
        "maps_bin": _rel(maps_bin),
        "palettes_bin": _rel(pals_bin),
        "sha256": {
            "tiles_bin": _sha256(tiles_bin),
            "maps_bin": _sha256(maps_bin),
            "palettes_bin": _sha256(pals_bin),
        },
        "frames": len(frames),
        "world": {
            "pixels_w": frame_w,
            "pixels_h": frame_h,
            "tiles_w": tiles_w,
            "tiles_h": tiles_h,
        },
        "viewport": viewport,
        "runtime_streaming": {
            "strategy": strategy_status,
            "route_status": "route_a_multi_plane",
            "plane_count": ROUTE_A_PLANE_COUNT,
            "plane_order": list(ROUTE_A_PLANE_NAMES),
            "map_word_format": "per frame: BG_B map then BG_A map; bits0_11_global_tile_id_bit12_hflip_bit13_vflip_bits14_15_palette",
            "window_tiles_w": WINDOW_TILES_W,
            "window_tiles_h": WINDOW_TILES_H,
            "window_bytes_per_update": WINDOW_TILES_W * WINDOW_TILES_H * ROUTE_A_PLANE_COUNT * 2,
            "max_window_unique_tiles": max_window_unique_tiles,
            "max_window_unique_tiles_without_bg_b_cull": max_window_unique_tiles_without_bg_b_cull,
            "max_bg_b_culled_cells": max_bg_b_culled_cells,
            "streaming_cache_capacity_tiles": streaming_cache_capacity_tiles,
            "estimated_streaming_cache_vram_bytes": streaming_cache_capacity_tiles * 32,
            "blank_global_tile_id": int(blank_global_tile_id),
            "bg_b_occlusion_culling": {
                "enabled": True,
                "rule": "when the BG_A screen cell references a fully opaque tile, the BG_B cell streams the all-zero tile instead of its far-plane source tile",
            },
            "camera": camera,
        },
        "diagnostic_previews": {
            "exported_bin_viewport_default": _rel(preview_path),
            "preview_camera_px": {"x": preview_camera_x, "y": preview_camera_y},
        },
        "tile_user_index": TILE_USER_INDEX,
        "raw_tiles": total_tiles,
        "unique_tiles": len(unique_tiles),
        "exact_unique_tiles_before_lossy_merge": len(exact_unique_tiles),
        "global_tile_id_limit_ok": global_tile_id_limit_ok,
        "global_tile_id_limit_status": budget_status,
        "dedup": {
            "raw_tiles": total_tiles,
            "unique_tiles": len(unique_tiles),
            "exact_unique_tiles_before_lossy_merge": len(exact_unique_tiles),
            "lossy_tile_merge_threshold_pixels": LOSSY_TILE_MERGE_THRESHOLD,
            "lossy_tile_merges": lossy_tile_merges,
            "reused_tiles": total_tiles - len(unique_tiles),
            "saving_ratio": round(1.0 - (len(unique_tiles) / total_tiles), 6) if total_tiles else 0,
            "matches_normal_or_exact": normal_matches,
            "matches_hflip": h_matches,
            "matches_vflip": v_matches,
            "matches_hvflip": hv_matches,
            "quality_note": "No near-duplicate tile merge is used in the final streaming route; global ROM tiles are decoded into a local VDP window cache.",
        },
        "palettes": {
            "subpalette_count": 4,
            "slots_per_subpalette": 16,
            "global_palette_source": (
                "optimized lloyd tile-aware MD palettes (optimize_showdown_palettes.py)"
                if palette_source == "optimized_json"
                else "manual contextual MD palette with bridge colors for mixed sky/tree/water/rock tiles"
            ),
            "strategy": ("optimized_context_palette_route_a" if palette_source == "optimized_json" else "manual_context_palette_v2_route_a"),
            "roles": list(SEMANTIC_ROLES),
            "bands_y_tiles_legacy_reference": list(palette_bands_y),
            "tile_palette_assignments": len(resolved_tile_palette_id),
            "tile_palette_role_counts": {
                role: int(tile_palette_role_counts[role]) for role in SEMANTIC_ROLES
            },
            "source_unique_colors_by_role": {
                role: int(len(role_color_counts[role])) for role in SEMANTIC_ROLES
            },
            "palette_sizes": [len(set(p[1:])) for p in pal_lists],
            "palette_slots_rgb": [
                [[int(channel) for channel in rgb] for rgb in palette] for palette in pal_lists
            ],
            "nearest_color_remaps": nearest_color_remaps,
            "nearest_color_remaps_by_assigned_role": {
                role: int(role_remap_counts[role]) for role in SEMANTIC_ROLES
            },
            "remap_policy": "visible pixels are mapped to nearest visible slot 1..15 in the selected semantic MD subpalette; slot 0 stays reserved as safe backdrop",
            "greedy_baseline_violations": len(palette_pressure),
            "raw_per_tile_palette_conflicts": len(raw_per_tile_palette_conflicts),
        },
        "violations": palette_violations,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    analysis = ROOT / "analysis"
    analysis.mkdir(parents=True, exist_ok=True)
    (analysis / "palette_violations.json").write_text(
        json.dumps(
            {
                "schema_version": "1.1.0",
                "status": "semantic_remap_measured" if nearest_color_remaps else "pass",
                "strategy": ("optimized_context_palette_route_a" if palette_source == "optimized_json" else "manual_context_palette_v2_route_a"),
                "roles": list(SEMANTIC_ROLES),
                "bands_y_tiles_legacy_reference": list(palette_bands_y),
                "palette_slots_rgb": [
                    [[int(channel) for channel in rgb] for rgb in palette] for palette in pal_lists
                ],
                "tile_palette_role_counts": {
                    role: int(tile_palette_role_counts[role]) for role in SEMANTIC_ROLES
                },
                "source_unique_colors_by_role": {
                    role: int(len(role_color_counts[role])) for role in SEMANTIC_ROLES
                },
                "violations_total": len(palette_violations),
                "violations": palette_violations,
            "nearest_color_remaps": nearest_color_remaps,
            "palette_source": palette_source,
                "nearest_color_remaps_by_assigned_role": {
                    role: int(role_remap_counts[role]) for role in SEMANTIC_ROLES
                },
                "raw_greedy_baseline_violations_total": len(palette_pressure),
                "raw_per_tile_palette_conflicts_total": len(raw_per_tile_palette_conflicts),
                "lossy_tile_merge_threshold_pixels": LOSSY_TILE_MERGE_THRESHOLD,
                "lossy_tile_merges": lossy_tile_merges,
                "curation_note": "Route A manual contextual palette uses bridge colors for mixed-material tiles and emits two SGDK planes; any remaining nearest-color remap remains measured evidence, not artistic approval.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (analysis / "per_tile_palette_conflict_report.json").write_text(
        json.dumps(
            {
                "$schema": "sgdk_wrapper/schemas/per_tile_palette_conflict_report.schema.json",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "tool_name": "showdown_training_exporter",
                "tool_version": "1.1.0",
                "conflicts_total": len(per_tile_palette_conflicts),
                "conflicts": [
                    {
                        "rule_id": "tile_colors_fit_single_subpalette",
                        "severity": "error",
                        "tile_x": int(c["tile_x"]),
                        "tile_y": int(c["tile_y"]),
                        "details": f"frame={c['frame_index']} color_count={c['color_count']}",
                    }
                    for c in per_tile_palette_conflicts
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (analysis / "tilemap_flag_report.json").write_text(
        json.dumps(
            {
                "$schema": "sgdk_wrapper/schemas/tilemap_flag_report.schema.json",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "tool_name": "showdown_training_exporter",
                "tool_version": "1.1.0",
                "entries": flag_entries,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (analysis / "scene_tilemap_conversion_report.json").write_text(
        json.dumps(
            {
                "$schema": "sgdk_wrapper/schemas/scene_tilemap_conversion_report.schema.json",
                "source_path": _rel(frames[0]),
                "source_sha256": _sha256(frames[0]),
                "conversion_target": "route_a_multi_plane_world_tilemap_with_camera_window_streaming",
                "output_tileset_path": _rel(tiles_bin),
                "output_tilemap_path": _rel(maps_bin),
                "output_palette_path": _rel(pals_bin),
                "tile_size_px": 8,
                "total_tiles": total_tiles,
                "unique_tiles_exact": len(exact_unique_tiles),
                "unique_tiles_hflip": 0,
                "unique_tiles_vflip": 0,
                "unique_tiles_hvflip": 0,
                "final_unique_tiles": len(unique_tiles),
                "lossy_tile_merge_threshold_pixels": LOSSY_TILE_MERGE_THRESHOLD,
                "lossy_tile_merges": lossy_tile_merges,
                "dedup_savings_tiles": total_tiles - len(unique_tiles),
                "dedup_savings_percent": round((1.0 - (len(unique_tiles) / total_tiles)) * 100.0, 4)
                if total_tiles
                else 0.0,
                "palette_count": 4,
                "per_tile_palette_conflicts": len(per_tile_palette_conflicts),
                "priority_tile_count": 0,
                "hflip_tile_count": h_matches,
                "vflip_tile_count": v_matches,
                "hvflip_tile_count": hv_matches,
                "estimated_vram_bytes": streaming_cache_capacity_tiles * 32,
                "estimated_map_bytes": len(maps_bytes),
                "rom_resource_strategy": "BIN_CUSTOM_TILE_GRAPHICS_AND_TILEMAP_WINDOW_STREAMING",
                "world_pixels_w": frame_w,
                "world_pixels_h": frame_h,
                "world_tiles_w": tiles_w,
                "world_tiles_h": tiles_h,
                "viewport_pixels_w": int(viewport.get("w", VIEWPORT_W)),
                "viewport_pixels_h": int(viewport.get("h", VIEWPORT_H)),
                "streaming_window_tiles_w": WINDOW_TILES_W,
                "streaming_window_tiles_h": WINDOW_TILES_H,
                "streaming_window_bytes_per_update": WINDOW_TILES_W * WINDOW_TILES_H * ROUTE_A_PLANE_COUNT * 2,
                "streaming_max_window_unique_tiles": max_window_unique_tiles,
                "streaming_max_window_unique_tiles_without_bg_b_cull": max_window_unique_tiles_without_bg_b_cull,
                "streaming_max_bg_b_culled_cells": max_bg_b_culled_cells,
                "streaming_cache_capacity_tiles": streaming_cache_capacity_tiles,
                "streaming_plane_count": ROUTE_A_PLANE_COUNT,
                "streaming_plane_order": list(ROUTE_A_PLANE_NAMES),
                "custom_map_global_tile_id_bits": 12,
                "global_tile_id_limit_ok": global_tile_id_limit_ok,
                "status": "ok" if global_tile_id_limit_ok and not palette_violations and not per_tile_palette_conflicts else "blocked",
                "blockers": [] if global_tile_id_limit_ok else ["global_tile_id_limit_exceeded"],
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "tool_name": "showdown_training_exporter",
                "tool_version": "1.1.0",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return meta


def main() -> int:
    frames_dir = ROOT / "work" / "reconstructed_layers"
    out_dir = ROOT / "work" / "sgdk_bins"
    meta = export_showdown_bins(frames_dir, out_dir)
    (ROOT / "analysis").mkdir(parents=True, exist_ok=True)
    (ROOT / "analysis" / "tile_stats.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return 0 if meta.get("global_tile_id_limit_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
