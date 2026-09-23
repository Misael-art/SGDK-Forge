from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from sgdk_export import export_showdown_bins as exporter


VIEW_W = 320
VIEW_H = 224
WORLD_TILES_W = 96
WORLD_TILES_H = 60
WINDOW_TILES_W = 41
WINDOW_TILES_H = 29


def read_u16be_words(path: Path) -> list[int]:
    data = path.read_bytes()
    if len(data) % 2:
        raise ValueError(f"u16 bin with odd byte length: {path}")
    return [int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2)]


def decode_tile_4bpp(tile_bytes: bytes) -> bytes:
    if len(tile_bytes) != 32:
        raise ValueError("tile must be exactly 32 bytes")
    out = bytearray(64)
    dst = 0
    for byte in tile_bytes:
        out[dst] = (byte >> 4) & 0x0F
        out[dst + 1] = byte & 0x0F
        dst += 2
    return bytes(out)


def palette_word_to_components(word: int) -> tuple[int, int, int]:
    return ((word >> 1) & 0x7, (word >> 5) & 0x7, (word >> 9) & 0x7)


def components_to_rgb32(components: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(component * 32 for component in components)


def components_to_rgb34(components: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(component * 34 for component in components)


def render_default_view_from_bins(
    maps: list[int],
    tiles: list[bytes],
    palettes_rgb: list[list[tuple[int, int, int]]],
    plane_count: int,
    camera_x: int,
    camera_y: int,
    out_path: Path,
) -> Image.Image:
    frame_words = maps[: WORLD_TILES_W * WORLD_TILES_H * plane_count]
    exporter._render_route_a_preview_from_words(
        tiles,
        frame_words,
        palettes_rgb,
        WORLD_TILES_W,
        WORLD_TILES_H,
        camera_x,
        camera_y,
        out_path,
    )
    view = Image.open(out_path).convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    return view


def image_diff_count(left: Image.Image, right: Image.Image) -> int:
    left_px = list(left.convert("RGB").getdata())
    right_px = list(right.convert("RGB").getdata())
    return sum(1 for a, b in zip(left_px, right_px) if a != b)


def main() -> int:
    bins_dir = ROOT / "work" / "sgdk_bins"
    diagnostics_dir = ROOT / "work" / "diagnostics"
    analysis_dir = ROOT / "analysis"

    meta = json.loads((bins_dir / "showdown_export_meta.json").read_text(encoding="utf-8"))
    palette_words = read_u16be_words(bins_dir / "showdown_palettes_u16.bin")
    map_words = read_u16be_words(bins_dir / "showdown_maps_u16.bin")
    tile_data = (bins_dir / "showdown_tiles_4bpp.bin").read_bytes()
    tiles = [decode_tile_4bpp(tile_data[i : i + 32]) for i in range(0, len(tile_data), 32)]
    runtime = meta["runtime_streaming"]
    plane_count = int(runtime.get("plane_count", 1))

    palette_components = [palette_word_to_components(word) for word in palette_words]
    palettes_rgb32 = [
        [components_to_rgb32(palette_components[(pid * 16) + slot]) for slot in range(16)]
        for pid in range(4)
    ]
    palettes_rgb34 = [
        [components_to_rgb34(palette_components[(pid * 16) + slot]) for slot in range(16)]
        for pid in range(4)
    ]

    tile_index_counter = Counter(exporter._custom_map_tile_id(word) for word in map_words)
    palette_id_counter = Counter(exporter._custom_map_palette_id(word) for word in map_words)
    hflip_count = sum(exporter._custom_map_hflip(word) for word in map_words)
    vflip_count = sum(exporter._custom_map_vflip(word) for word in map_words)
    high_11bit_tile_refs = sum(1 for word in map_words if exporter._custom_map_tile_id(word) > 0x07FF)
    invalid_cram_words = [word for word in palette_words if word & ~0x0EEE]
    invalid_tile_nibbles = [
        tile_id for tile_id, tile in enumerate(tiles) if any(index > 15 for index in tile)
    ]

    camera = meta["runtime_streaming"]["camera"]["viewer_default_scroll_px"]
    bin_preview_path = diagnostics_dir / "exported_bin_viewport_from_bins.png"
    bin_preview = render_default_view_from_bins(
        map_words,
        tiles,
        palettes_rgb34,
        plane_count,
        int(camera["x"]),
        int(camera["y"]),
        bin_preview_path,
    )
    export_preview_path = diagnostics_dir / "exported_bin_viewport_default.png"
    export_preview = Image.open(export_preview_path).convert("RGB")
    diff_pixels = image_diff_count(bin_preview, export_preview)

    tile_data_start = exporter.TILE_USER_INDEX * 32
    tile_data_end = tile_data_start + (int(runtime["streaming_cache_capacity_tiles"]) * 32)
    first_tilemap_vram = 0xC000
    vram_layout_status = "pass" if tile_data_end <= first_tilemap_vram else "blocked"

    report = {
        "schema_version": "1.0.0",
        "status": "pass"
        if not invalid_cram_words and not invalid_tile_nibbles and diff_pixels == 0 and vram_layout_status == "pass"
        else "blocked",
        "pipeline_kind": "custom_bin_tiles_palettes_and_custom_12bit_map_words",
        "not_rescomp_png_image_route": True,
        "palette_contract": {
            "cram_words": len(palette_words),
            "subpalettes": 4,
            "slots_per_subpalette": 16,
            "invalid_cram_word_count": len(invalid_cram_words),
            "hardware_components_0_to_7": [
                palette_components[(pid * 16) : ((pid + 1) * 16)] for pid in range(4)
            ],
            "rgb32_preview_equivalent": palettes_rgb32,
            "rgb34_display_preview_equivalent": palettes_rgb34,
        },
        "tile_contract": {
            "tile_count_from_bin": len(tiles),
            "tile_count_from_meta": int(meta["unique_tiles"]),
            "invalid_tile_nibble_count": len(invalid_tile_nibbles),
            "tile_bin_sha256": hashlib.sha256((bins_dir / "showdown_tiles_4bpp.bin").read_bytes()).hexdigest(),
        },
        "map_contract": {
            "word_count": len(map_words),
            "plane_count": plane_count,
            "plane_order": runtime.get("plane_order", ["BG_A"]),
            "tile_id_min": min(tile_index_counter) if tile_index_counter else 0,
            "tile_id_max": max(tile_index_counter) if tile_index_counter else 0,
            "palette_id_counts": {str(key): int(value) for key, value in sorted(palette_id_counter.items())},
            "hflip_refs": int(hflip_count),
            "vflip_refs": int(vflip_count),
            "tile_refs_above_sgdk_11bit_attr_index": int(high_11bit_tile_refs),
            "custom_descriptor_reason": "global tile ids may exceed SGDK tile attr 11-bit field; runtime remaps active window to local VRAM slots before writing SGDK attrs",
            "maps_bin_sha256": hashlib.sha256((bins_dir / "showdown_maps_u16.bin").read_bytes()).hexdigest(),
        },
        "active_window_budget": {
            "max_window_unique_tiles": int(runtime["max_window_unique_tiles"]),
            "max_window_unique_tiles_without_bg_b_cull": int(runtime.get("max_window_unique_tiles_without_bg_b_cull", runtime["max_window_unique_tiles"])),
            "max_bg_b_culled_cells": int(runtime.get("max_bg_b_culled_cells", 0)),
            "streaming_cache_capacity_tiles": int(runtime["streaming_cache_capacity_tiles"]),
            "max_local_sgdk_tile_index": exporter.TILE_USER_INDEX + int(runtime["streaming_cache_capacity_tiles"]) - 1,
            "sgdk_attr_tile_index_limit": 0x07FF,
            "tile_data_vram_start": tile_data_start,
            "tile_data_vram_end_exclusive": tile_data_end,
            "first_tilemap_vram": first_tilemap_vram,
            "vram_layout_status": vram_layout_status,
            "bg_b_occlusion_culling": runtime.get("bg_b_occlusion_culling", {"enabled": False}),
        },
        "bin_preview_roundtrip": {
            "export_preview": export_preview_path.relative_to(ROOT).as_posix(),
            "bin_preview": bin_preview_path.relative_to(ROOT).as_posix(),
            "diff_pixels": int(diff_pixels),
        },
        "claim_limits": [
            "This audit proves explicit CRAM/tile/map consistency for the custom BIN route.",
            "It does not prove VDP residency without visual_vdp_dump.bin or equivalent runtime telemetry.",
            "Route A uses BG_B and BG_A map words in one custom map bin; runtime culls BG_B under fully opaque BG_A cells before streaming.",
        ],
    }

    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "showdown_vdp_contract_audit_v001.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], "diff_pixels": diff_pixels, "tile_count": len(tiles)}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
