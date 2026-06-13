from __future__ import annotations

from pathlib import Path
from collections import Counter
import hashlib
import json
import sys
from datetime import datetime, timezone

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from vdp_tiles.palette_plan import plan_4palettes_for_tiles
from vdp_tiles.tile_codec import tile_8x8_indices_to_md4bpp
from vdp_tiles.tile_dedup import dedup_tiles_with_flips
from mugen_sff.visual_gate import assert_frame_integrity


TILE_USER_INDEX = 16
VIEWPORT_W = 320
VIEWPORT_H = 224
WINDOW_TILES_W = 42
WINDOW_TILES_H = 30
LOSSY_TILE_MERGE_THRESHOLD = 0


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

    with Image.open(frames[0]) as base_img:
        master = base_img.convert("RGB").quantize(colors=64, dither=Image.Dither.NONE).convert("P")

    master_palette = master.getpalette() or []

    all_tiles: list[bytes] = []
    tile_color_sets: list[set[int]] = []

    for frame_path in frames:
        with Image.open(frame_path) as src:
            rgb = src.convert("RGB")
        pimg = rgb.quantize(palette=master, dither=Image.Dither.NONE).convert("P")
        for ty in range(tiles_h):
            for tx in range(tiles_w):
                t = _extract_tile_indices(pimg, tx * 8, ty * 8)
                all_tiles.append(t)
                tile_color_sets.append(_tile_color_set(t))

    greedy_plan = plan_4palettes_for_tiles(tile_color_sets)

    pal_lists: list[list[int]] = []
    pal_maps: list[dict[int, int]] = []
    band_counts: list[Counter[int]] = [Counter() for _ in range(4)]
    for tile_i, tile in enumerate(all_tiles):
        local_i = tile_i % (tiles_w * tiles_h)
        tile_y = local_i // tiles_w
        pid = _band_for_tile_y(tile_y, palette_bands_y)
        band_counts[pid].update(int(px) for px in tile)

    for pid in range(4):
        lst = [idx for idx, _ in band_counts[pid].most_common(16)]
        while len(lst) < 16:
            lst.append(0)
        pal_lists.append(lst)
        pal_maps.append({global_idx: local_idx for local_idx, global_idx in enumerate(lst)})

    max_palette_index = max((max(p) for p in pal_lists if p), default=0)
    rgb_cache = {global_idx: _decode_rgb(master_palette, global_idx) for global_idx in range(max_palette_index + 1)}

    def nearest_slot(pid: int, global_idx: int) -> int:
        mapping = pal_maps[pid]
        if global_idx in mapping:
            return int(mapping[global_idx])
        src_rgb = rgb_cache.get(global_idx, _decode_rgb(master_palette, global_idx))
        best_slot = 0
        best_score = None
        for slot, candidate_idx in enumerate(pal_lists[pid]):
            candidate_rgb = rgb_cache.get(candidate_idx, _decode_rgb(master_palette, candidate_idx))
            score = _rgb_distance_sq(src_rgb, candidate_rgb)
            if best_score is None or score < best_score:
                best_score = score
                best_slot = int(slot)
        return best_slot

    remapped_tiles: list[bytes] = []
    resolved_tile_palette_id: list[int] = []
    nearest_color_remaps = 0
    for tile_i, tile in enumerate(all_tiles):
        local_i = tile_i % (tiles_w * tiles_h)
        pid = _band_for_tile_y(local_i // tiles_w, palette_bands_y)
        resolved_tile_palette_id.append(pid)
        remapped_values = []
        for px in tile:
            global_idx = int(px)
            if global_idx not in pal_maps[pid]:
                nearest_color_remaps += 1
            remapped_values.append(nearest_slot(pid, global_idx))
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
        word = int(match["tile_index"]) & 0x0FFF
        if int(match["hflip"]):
            word |= 1 << 12
        if int(match["vflip"]):
            word |= 1 << 13
        word |= (pid & 0x3) << 14
        words.append(int(word))
        maps_bytes.extend(int(word).to_bytes(2, "big"))
    maps_bin.write_bytes(bytes(maps_bytes))

    pals_bin = out_root / "showdown_palettes_u16.bin"
    pals_bytes = bytearray()
    for pid in range(4):
        for slot in range(16):
            gidx = int(pal_lists[pid][slot])
            r, g, b = _decode_rgb(master_palette, gidx)
            pals_bytes.extend(int(_rgb_to_md_color(r, g, b)).to_bytes(2, "big"))
    pals_bin.write_bytes(bytes(pals_bytes))

    palette_pressure = [
        {
            "tile_global_index": int(tile_index),
            "frame_index": int(tile_index // (tiles_w * tiles_h)),
            "tile_x": int((tile_index % (tiles_w * tiles_h)) % tiles_w),
            "tile_y": int((tile_index % (tiles_w * tiles_h)) // tiles_w),
            "reason": int(v.get("reason", 0)),
            "color_count": int(v.get("color_count", 0)),
        }
        for tile_index, v in ((int(v.get("tile_index", -1)), v) for v in greedy_plan.violations)
    ]

    raw_per_tile_palette_conflicts = [
        {
            "tile_global_index": int(i),
            "frame_index": int(i // (tiles_w * tiles_h)),
            "tile_x": int((i % (tiles_w * tiles_h)) % tiles_w),
            "tile_y": int((i % (tiles_w * tiles_h)) // tiles_w),
            "color_count": len(colors),
            "status": "conflict" if len(colors) > 16 else "ok",
        }
        for i, colors in enumerate(tile_color_sets)
        if len(colors) > 16
    ]
    palette_violations: list[dict] = []
    per_tile_palette_conflicts: list[dict] = []

    flag_entries = []
    for i, match in enumerate(matches):
        local_i = i % (tiles_w * tiles_h)
        flag_entries.append(
            {
                "frame_index": int(i // (tiles_w * tiles_h)),
                "tile_x": int(local_i % tiles_w),
                "tile_y": int(local_i // tiles_w),
                "tile_index": int(TILE_USER_INDEX + match["tile_index"]),
                "palette_id": int(resolved_tile_palette_id[i]),
                "priority": False,
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
    max_window_unique_tiles = 0
    for frame_index in range(len(frames)):
        frame_base = frame_index * map_tiles_per_frame
        for start_y in range(max_tile_y + 1):
            for start_x in range(max_tile_x + 1):
                seen: set[int] = set()
                for wy in range(WINDOW_TILES_H):
                    src_y = min(tiles_h - 1, start_y + wy)
                    for wx in range(WINDOW_TILES_W):
                        src_x = min(tiles_w - 1, start_x + wx)
                        raw = words[frame_base + (src_y * tiles_w) + src_x]
                        seen.add(raw & 0x0FFF)
                max_window_unique_tiles = max(max_window_unique_tiles, len(seen))

    streaming_cache_capacity_tiles = max_window_unique_tiles + 64
    strategy_status = "tile_graphics_and_tilemap_window_streaming"
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
            "map_word_format": "bits0_11_global_tile_id_bit12_hflip_bit13_vflip_bits14_15_palette",
            "window_tiles_w": WINDOW_TILES_W,
            "window_tiles_h": WINDOW_TILES_H,
            "window_bytes_per_update": WINDOW_TILES_W * WINDOW_TILES_H * 2,
            "max_window_unique_tiles": max_window_unique_tiles,
            "streaming_cache_capacity_tiles": streaming_cache_capacity_tiles,
            "estimated_streaming_cache_vram_bytes": streaming_cache_capacity_tiles * 32,
            "camera": camera,
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
            "global_palette_source": "first reconstructed world frame quantized to 64 colors",
            "strategy": "banded_palette_v1_world",
            "bands_y_tiles": list(palette_bands_y),
            "tile_palette_assignments": len(resolved_tile_palette_id),
            "palette_sizes": [len([slot for slot in p if slot != 0]) for p in pal_lists],
            "nearest_color_remaps": nearest_color_remaps,
            "remap_policy": "missing global colors are mapped to the nearest RGB color in the selected MD subpalette instead of slot 0",
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
                "status": "pass_with_degradation" if nearest_color_remaps else "pass",
                "strategy": "banded_palette_v1_world",
                "bands_y_tiles": list(palette_bands_y),
                "violations_total": len(palette_violations),
                "violations": palette_violations,
                "nearest_color_remaps": nearest_color_remaps,
                "raw_greedy_baseline_violations_total": len(palette_pressure),
                "raw_per_tile_palette_conflicts_total": len(raw_per_tile_palette_conflicts),
                "lossy_tile_merge_threshold_pixels": LOSSY_TILE_MERGE_THRESHOLD,
                "lossy_tile_merges": lossy_tile_merges,
                "curation_note": "Final exported world tiles fit one of four banded subpalettes, but source colors were approximated; tile graphics are streamed per camera window to preserve world extent without lossy tile merging.",
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
                "conversion_target": "world_tilemap_with_camera_window_streaming",
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
                "streaming_window_bytes_per_update": WINDOW_TILES_W * WINDOW_TILES_H * 2,
                "streaming_max_window_unique_tiles": max_window_unique_tiles,
                "streaming_cache_capacity_tiles": streaming_cache_capacity_tiles,
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
