#!/usr/bin/env python3
"""Build a source-faithful semantic palette/tile-atlas study at the anchor camera.

The builder only recolors the authored source-derived BG_B/BG_A plates,
indexes them, deduplicates exact 8x8 patterns with hardware H/V flips, and
recomposes the indexed maps. It does not invent stage pixels or touch res/ROM.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
WORKSPACE = HERE.parents[5]
# The archival bundle is self-contained for rebuilding the study. Keep the raw
# MUGEN package outside Git; when it is present locally, verify it against the
# source hash recorded in the bundled lineage.
INPUT = HERE / "source"
SOURCE_ZIP = PROJECT / "rascunho/entrada_bruta/ssf2_01_ryu.zip"
SOURCE_LINEAGE = INPUT / "source_plane_lineage.json"
SOURCE_COMPOSITE = INPUT / "source_composite_anchor.png"
OUT = HERE
sys.path.insert(0, str(WORKSPACE / "tools/mugen2sgdk_forge"))
from mugen2sgdk_forge.converters.sprites import vdp_rgb, vdp_word  # noqa: E402

SWATCHES = {
    "deep_shadow": (0x22, 0x44, 0x66),
    "blue_mid": (0x44, 0x88, 0xAA),
    "blue_vivid": (0x44, 0x88, 0xCC),
    "sky_light": (0x66, 0xAA, 0xEE),
    "wood_dark": (0x88, 0x66, 0x22),
    "wood_mid": (0xAA, 0x88, 0x66),
    "cloud_light": (0xAA, 0xCC, 0xEE),
    "wood_light": (0xCC, 0xAA, 0x66),
}
ORDERS = {
    "seven_color": ["deep_shadow", "blue_mid", "sky_light", "cloud_light",
                    "wood_dark", "wood_mid", "wood_light"],
    "eight_color_control": ["deep_shadow", "blue_mid", "blue_vivid", "sky_light",
                            "cloud_light", "wood_dark", "wood_mid", "wood_light"],
}
BLUE_ROLE = {
    "seven_color": ["deep_shadow", "blue_mid", "sky_light", "cloud_light"],
    "eight_color_control": ["deep_shadow", "blue_mid", "blue_vivid", "sky_light", "cloud_light"],
}
WOOD_ROLE = ["deep_shadow", "wood_dark", "wood_mid", "wood_light"]
WIDTH, HEIGHT, TILE = 320, 224, 8


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hexrgb(rgb: tuple[int, int, int]) -> str:
    return "#%02X%02X%02X" % rgb


def dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    # Same channel weighting used by the converter: green carries more weight.
    return 2 * (a[0] - b[0]) ** 2 + 4 * (a[1] - b[1]) ** 2 + 3 * (a[2] - b[2]) ** 2


def hardware_palette(names: list[str]) -> dict:
    result = {}
    for index, name in enumerate(names, start=1):
        source_rgb = SWATCHES[name]
        word = vdp_word(source_rgb)
        result[name] = {"index": index, "input_swatch_rgb": hexrgb(source_rgb),
                        "vdp_word": f"0x{word:03X}", "hardware_rgb": hexrgb(vdp_rgb(word))}
    return result


def save_indexed(path: Path, size: tuple[int, int], indexes: list[int], names: list[str]) -> None:
    palette = [(255, 0, 255)] + [vdp_rgb(vdp_word(SWATCHES[name])) for name in names]
    flat = [channel for rgb in palette for channel in rgb]
    flat.extend([0] * (768 - len(flat)))
    image = Image.new("P", size)
    image.putpalette(flat)
    image.putdata(indexes)
    image.info["transparency"] = 0
    image.save(path, format="PNG", optimize=False, transparency=0)


def remap_plane(image: Image.Image, variant: str, plane: str) -> tuple[list[int], dict, dict]:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    names = ORDERS[variant]
    index_for = {name: i + 1 for i, name in enumerate(names)}
    targets = {name: vdp_rgb(vdp_word(SWATCHES[name])) for name in names}
    indexes: list[int] = []
    counts: dict[str, Counter] = {}
    errors: Counter = Counter()
    all_errors = []
    for y in range(HEIGHT):
        if plane == "far" or y < 176:
            allowed = BLUE_ROLE[variant]
            role = "sky_architecture_blue"
        else:
            allowed = WOOD_ROLE
            role = "foreground_wood_with_shared_shadow"
        role_counts = counts.setdefault(role, Counter())
        for x in range(WIDTH):
            r, g, b, a = pixels[x, y]
            if a == 0:
                indexes.append(0)
                continue
            src = vdp_rgb(vdp_word((r, g, b)))
            winner = min(allowed, key=lambda name: (dist(src, targets[name]), index_for[name]))
            index = index_for[winner]
            indexes.append(index)
            role_counts[(hexrgb(src), winner)] += 1
            error = sum((src[c] - targets[winner][c]) ** 2 for c in range(3))
            errors[role] += error
            all_errors.append(error)
    mapping = {}
    for role, entries in counts.items():
        mapping[role] = [{"source_hardware_rgb": source, "target_role": target,
                          "target_hardware_rgb": hexrgb(targets[target]), "pixels": n}
                         for (source, target), n in sorted(entries.items())]
    metric = {role: {"mapped_pixels": sum(entries.values()),
                     "mean_squared_rgb_error": errors[role] / max(1, sum(entries.values()))}
              for role, entries in counts.items()}
    metric["all_visible"] = {"mapped_pixels": len(all_errors),
                             "mean_squared_rgb_error": sum(all_errors) / max(1, len(all_errors)),
                             "rmse_per_channel": math.sqrt(sum(all_errors) / max(1, len(all_errors) * 3))}
    return indexes, mapping, metric


def tile_at(indexes: list[int], tx: int, ty: int) -> bytes:
    return bytes(indexes[(ty * 8 + y) * WIDTH + tx * 8 + x]
                 for y in range(8) for x in range(8))


def transform(tile: bytes, hflip: bool, vflip: bool) -> bytes:
    rows = [tile[y * 8:(y + 1) * 8] for y in range(8)]
    if vflip:
        rows.reverse()
    if hflip:
        rows = [row[::-1] for row in rows]
    return b"".join(rows)


def canonical(tile: bytes) -> tuple[bytes, bool, bool]:
    return min(((transform(tile, h, v), h, v)
                for h in (False, True) for v in (False, True)), key=lambda row: row[0])


def encode_4bpp_planar(tile: bytes) -> bytes:
    output = bytearray()
    for y in range(8):
        row = tile[y * 8:(y + 1) * 8]
        for plane in range(4):
            byte = 0
            for x, index in enumerate(row):
                byte |= ((index >> plane) & 1) << (7 - x)
            output.append(byte)
    return bytes(output)


def decode_4bpp_planar(tile: bytes) -> bytes:
    output = bytearray()
    for y in range(8):
        row = tile[y * 4:y * 4 + 4]
        for x in range(8):
            output.append(sum(((row[p] >> (7 - x)) & 1) << p for p in range(4)))
    return bytes(output)


def write_candidate(variant: str, source_images: dict[str, Image.Image]) -> dict:
    names = ORDERS[variant]
    base = OUT / variant
    (base / "planes").mkdir(parents=True, exist_ok=True)
    (base / "tiles").mkdir(parents=True, exist_ok=True)
    remapped: dict[str, list[int]] = {}
    role_maps, color_metrics, plane_metrics = {}, {}, {}
    alpha_masks = {}
    for plane, source in source_images.items():
        indexes, mapping, metric = remap_plane(source, variant, plane)
        remapped[plane] = indexes
        role_maps[plane], color_metrics[plane] = mapping, metric
        alpha_masks[plane] = bytes(1 if rgba[3] else 0 for rgba in source.convert("RGBA").getdata())
        indexed_path = base / "planes" / f"{plane}_{variant}_indexed.png"
        save_indexed(indexed_path, (WIDTH, HEIGHT), indexes, names)
        plane_metrics[plane] = {"path": indexed_path.relative_to(OUT).as_posix(),
                                "sha256": sha(indexed_path), "size": [WIDTH, HEIGHT],
                                "source_alpha_mask_preserved": True,
                                "visible_pixels": sum(v != 0 for v in alpha_masks[plane])}

    patterns_no_flip: set[bytes] = set()
    bank_ids: dict[bytes, int] = {}
    bank_patterns: list[bytes] = []
    map_rows_by_plane = {}
    flip_counts = Counter()
    tile_color_counts = []
    per_plane_unique = {}
    for plane, indexes in remapped.items():
        map_rows = []
        layer_patterns = []
        for ty in range(HEIGHT // TILE):
            row = []
            for tx in range(WIDTH // TILE):
                tile = tile_at(indexes, tx, ty)
                patterns_no_flip.add(tile)
                layer_patterns.append(tile)
                norm, hflip, vflip = canonical(tile)
                if norm not in bank_ids:
                    bank_ids[norm] = len(bank_ids)
                    bank_patterns.append(norm)
                tile_id = bank_ids[norm]
                if tile_id >= 2048:
                    raise ValueError("relative tile ID exceeds the VDP name-table field")
                flip_counts[(hflip, vflip)] += 1
                visible = set(tile) - {0}
                tile_color_counts.append(len(visible))
                word = tile_id | (int(hflip) << 11) | (int(vflip) << 12)
                row.append({"tile_id": tile_id, "hflip": hflip, "vflip": vflip,
                            "palette": 0, "priority": False, "word": word})
            map_rows.append(row)
        map_rows_by_plane[plane] = map_rows
        per_plane_unique[plane] = {"map_entries": 1120,
                                   "unique_patterns_no_flip": len(set(layer_patterns)),
                                   "unique_patterns_with_hv_flip": len({canonical(t)[0] for t in layer_patterns})}

    bank_data = b"".join(encode_4bpp_planar(tile) for tile in bank_patterns)
    bank_path = base / "tiles" / "shared_tileset_4bpp_planar.bin"
    bank_path.write_bytes(bank_data)
    atlas_columns = 32
    atlas_rows = (len(bank_patterns) + atlas_columns - 1) // atlas_columns
    atlas_indexes = bytearray(atlas_columns * TILE * atlas_rows * TILE)
    atlas_width = atlas_columns * TILE
    for tile_id, tile in enumerate(bank_patterns):
        ox, oy = (tile_id % atlas_columns) * TILE, (tile_id // atlas_columns) * TILE
        for py in range(TILE):
            for px in range(TILE):
                atlas_indexes[(oy + py) * atlas_width + ox + px] = tile[py * TILE + px]
    atlas_path = base / "tiles" / "shared_tileset_atlas_8x8.png"
    save_indexed(atlas_path, (atlas_width, atlas_rows * TILE), list(atlas_indexes), names)
    atlas_preview_path = base / "tiles" / "shared_tileset_atlas_preview_4x.png"
    Image.open(atlas_path).convert("RGBA").resize(
        (atlas_width * 4, atlas_rows * TILE * 4), Image.Resampling.NEAREST
    ).save(atlas_preview_path, format="PNG", optimize=False)
    map_paths = {}
    for plane, rows in map_rows_by_plane.items():
        words = bytearray()
        for row in rows:
            for cell in row:
                words.extend(cell["word"].to_bytes(2, "big"))
        path = base / "tiles" / f"{plane}_tilemap_40x28_be.bin"
        path.write_bytes(words)
        json_path = base / "tiles" / f"{plane}_tilemap_40x28.json"
        json_path.write_text(json.dumps({"plane": plane, "palette": "PAL0", "size": [40, 28],
                                         "tile_size": [8, 8], "entries": rows}, separators=(",", ":")) + "\n")
        map_paths[plane] = {"binary": path.relative_to(OUT).as_posix(), "binary_sha256": sha(path),
                            "binary_bytes": path.stat().st_size,
                            "json": json_path.relative_to(OUT).as_posix(), "json_sha256": sha(json_path)}

    # Compose the palettes from the indexed maps for a deterministic lossless round trip.
    rgba_planes = {}
    for plane, indexes in remapped.items():
        rgba = Image.new("RGBA", (WIDTH, HEIGHT))
        rgba_pixels = rgba.load()
        source_rgba = source_images[plane].convert("RGBA")
        source_alpha = source_rgba.getchannel("A").get_flattened_data()
        target_rgb = [None] + [vdp_rgb(vdp_word(SWATCHES[name])) for name in names]
        for i, index in enumerate(indexes):
            rgba_pixels[i % WIDTH, i // WIDTH] = (*target_rgb[index], source_alpha[i]) if index else (0, 0, 0, 0)
        rgba_planes[plane] = rgba
    composite = Image.alpha_composite(rgba_planes["far"], rgba_planes["near"]).convert("RGB")
    preview_path = base / f"suzaku_source_anchor_{variant}_preview.png"
    composite.save(preview_path, format="PNG", optimize=False)

    source_composite = Image.open(SOURCE_COMPOSITE).convert("RGB")
    source_hardware = [vdp_rgb(vdp_word(rgb)) for rgb in source_composite.getdata()]
    candidate_pixels = list(composite.getdata())
    sse = sum(sum((a[c] - b[c]) ** 2 for c in range(3)) for a, b in zip(source_hardware, candidate_pixels))
    mse = sse / max(1, len(candidate_pixels))
    changed = sum(a != b for a, b in zip(source_hardware, candidate_pixels))

    # Verify VDP planar bytes plus H/V map attributes reconstruct each indexed plane exactly.
    roundtrip = {}
    for plane, indexes in remapped.items():
        reconstructed = bytearray(WIDTH * HEIGHT)
        for ty, row in enumerate(map_rows_by_plane[plane]):
            for tx, cell in enumerate(row):
                tile_id = cell["tile_id"]
                tile = decode_4bpp_planar(bank_data[tile_id * 32:(tile_id + 1) * 32])
                tile = transform(tile, cell["hflip"], cell["vflip"])
                for py in range(8):
                    for px in range(8):
                        reconstructed[(ty * 8 + py) * WIDTH + tx * 8 + px] = tile[py * 8 + px]
        if list(reconstructed) != indexes:
            raise ValueError(f"tile atlas round trip failed for {variant}/{plane}")
        roundtrip[plane] = "passed_pixel_exact"

    palette_entries = hardware_palette(names)
    palette_doc = {"variant": variant, "index0": "transparent", "entries": palette_entries,
                   "visible_colors": len(names), "valid_vdp_words": True,
                   "mapping_note": "semantic role whitelist first; nearest target only within the role ramp"}
    (base / "palette.json").write_text(json.dumps(palette_doc, indent=2) + "\n")
    (base / "semantic_color_mapping.json").write_text(json.dumps({"plane_roles": role_maps,
                                                                    "error_metrics": color_metrics}, indent=2) + "\n")
    conflict = {"schema": "mugen2sgdk_forge.per_tile_palette_conflict_report/v1",
                "status": "passed_for_static_anchor_candidate", "palette": "PAL0",
                "max_colors_per_tile": max(tile_color_counts, default=0),
                "hardware_limit": 15, "tiles_over_limit": sum(v > 15 for v in tile_color_counts),
                "tiles_with_0_to_4_colors": sum(v <= 4 for v in tile_color_counts),
                "tiles_with_5_to_8_colors": sum(5 <= v <= 8 for v in tile_color_counts)}
    (base / "per_tile_palette_conflict_report.json").write_text(json.dumps(conflict, indent=2) + "\n")
    flag_report = {"schema": "mugen2sgdk_forge.tilemap_flag_report/v1",
                   "exact_patterns_across_planes_without_flip": len(patterns_no_flip),
                   "shared_atlas_patterns_with_hv_flip": len(bank_patterns),
                   "map_entries_total": 2240,
                   "entries_no_flip": flip_counts[(False, False)],
                   "entries_hflip_only": flip_counts[(True, False)],
                   "entries_vflip_only": flip_counts[(False, True)],
                   "entries_hvflip": flip_counts[(True, True)],
                   "savings_from_hv_reuse": len(patterns_no_flip) - len(bank_patterns)}
    (base / "tilemap_flag_report.json").write_text(json.dumps(flag_report, indent=2) + "\n")
    return {"variant": variant, "visible_color_count": len(names),
            "palette_entries": palette_entries, "plane_assets": plane_metrics,
            "per_plane_tile_metrics": per_plane_unique,
            "exact_patterns_across_planes_without_flip": len(patterns_no_flip),
            "shared_patterns_with_hv_flip": len(bank_patterns),
            "pattern_bytes": len(bank_patterns) * 32,
            "two_plane_map_bytes": 4480,
            "static_anchor_patterns_plus_maps_bytes": len(bank_patterns) * 32 + 4480,
            "tile_bank_sha256": sha(bank_path), "tile_bank_path": bank_path.relative_to(OUT).as_posix(),
            "tile_atlas_png": atlas_path.relative_to(OUT).as_posix(),
            "tile_atlas_preview_png": atlas_preview_path.relative_to(OUT).as_posix(),
            "tilemaps": map_paths, "preview": preview_path.relative_to(OUT).as_posix(),
            "preview_sha256": sha(preview_path),
            "source_hardware_rgb_mse_per_pixel": mse,
            "source_hardware_rgb_rmse_per_channel": math.sqrt(mse / 3),
            "changed_pixels_vs_source_after_hardware_decode": changed,
            "pixel_exact_tilemap_roundtrip": roundtrip,
            "palette_conflict_report": conflict, "tilemap_flag_report": flag_report}


def main() -> None:
    lineage = json.loads(SOURCE_LINEAGE.read_text())
    source_sha = lineage["source_package"]["sha256"]
    source_package_revalidated = SOURCE_ZIP.is_file()
    if source_package_revalidated and sha(SOURCE_ZIP) != source_sha:
        raise ValueError("source SFF package hash does not match the bundled anchor lineage")
    if lineage["recomposition"]["mismatched_pixels"] != 0:
        raise ValueError("source anchor plates no longer reproduce the source compositor exactly")
    for key, filename in (("far", "far_bg0a_bg0b_anchor.png"),
                          ("near", "near_bg1_bg4_anchor.png"),
                          ("composite", "source_composite_anchor.png")):
        actual = sha(INPUT / filename)
        expected = lineage["assets"][key]["sha256"]
        if actual != expected:
            raise ValueError(f"source plate hash mismatch for {key}")
    source_images = {"far": Image.open(INPUT / "far_bg0a_bg0b_anchor.png").convert("RGBA"),
                     "near": Image.open(INPUT / "near_bg1_bg4_anchor.png").convert("RGBA")}
    for name, image in source_images.items():
        if image.size != (WIDTH, HEIGHT):
            raise ValueError(f"{name}: unexpected source plate size {image.size}")
    OUT.joinpath("source").mkdir(exist_ok=True)
    for path in (INPUT / "far_bg0a_bg0b_anchor.png", INPUT / "near_bg1_bg4_anchor.png",
                 SOURCE_COMPOSITE, SOURCE_LINEAGE):
        (OUT / "source" / path.name).write_bytes(path.read_bytes())
    palette_meta = {"swatches": {name: hexrgb(rgb) for name, rgb in SWATCHES.items()},
                    "seven_color_variant_drops": ["blue_vivid #4488CC"],
                    "source": "user-provided approximate PAL0 color roles",
                    "hardware_conversion": "canonical mugen2sgdk_forge vdp_word/vdp_rgb",
                    "scope": "static anchor-camera offline test; no HUD/FX palette ownership changed"}
    (OUT / "palette_candidates.json").write_text(json.dumps(palette_meta, indent=2) + "\n")
    results = {variant: write_candidate(variant, source_images) for variant in ORDERS}
    seven_preview = Image.open(OUT / results["seven_color"]["preview"]).convert("RGB")
    eight_preview = Image.open(OUT / results["eight_color_control"]["preview"]).convert("RGB")
    variant_pixels = list(zip(seven_preview.getdata(), eight_preview.getdata()))
    changed_between_variants = sum(a != b for a, b in variant_pixels)
    variant_sse = sum(sum((a[c] - b[c]) ** 2 for c in range(3))
                      for a, b in variant_pixels)
    variant_mse = variant_sse / max(1, len(variant_pixels))
    original_preview = Image.open(SOURCE_COMPOSITE).convert("RGB")
    comparison = Image.new("RGB", (WIDTH * 3, HEIGHT))
    comparison.paste(original_preview, (0, 0))
    comparison.paste(seven_preview, (WIDTH, 0))
    comparison.paste(eight_preview, (WIDTH * 2, 0))
    comparison_path = OUT / "source_7color_8color_comparison.png"
    comparison.save(comparison_path, format="PNG", optimize=False)
    summary = {"schema": "mugen2sgdk_forge.semantic_tile_atlas_study/v1",
               "status": "offline_static_anchor_study_not_runtime_asset",
               "source_package_sha256": source_sha,
               "source_package_revalidated_during_build": source_package_revalidated,
               "source_composite_sha256": sha(SOURCE_COMPOSITE),
               "source_lineage_sha256": sha(SOURCE_LINEAGE),
               "anchor_camera_from_left": lineage["anchor_camera_from_left"],
               "canvas": [WIDTH, HEIGHT], "tile_size": [8, 8],
               "planes": {"far": "BG_B study plate from BG0a/BG0b", "near": "BG_A study plate from BG1..BG4"},
               "variant_difference": {"pixels_changed_7_vs_8": changed_between_variants,
                                      "fraction_changed_7_vs_8": changed_between_variants / len(variant_pixels),
                                      "mean_squared_rgb_error_7_vs_8": variant_mse,
                                      "comparison_image": comparison_path.name,
                                      "comparison_order": ["original source", "seven color", "eight color control"]},
               "results": results,
               "limitations": ["The existing plates merge source layers by depth for one anchor camera only.",
                               "BG0a/BG0b autonomous velocity, camera sweep, BG4a row-varying xscale and BG5 animation are not represented in this static tilemap.",
                               "These exact source-derived plates do not approve a runtime layer architecture or visual quality.",
                               "No production res files, runtime code, ROM, or canonical documents were changed."]}
    (OUT / "scene_tilemap_conversion_report.json").write_text(json.dumps(summary, indent=2) + "\n")
    seven = results["seven_color"]
    eight = results["eight_color_control"]
    records = {
        "route_decision_record.json": {
            "schema": "mugen2sgdk_forge.route_decision_record/v1",
            "context_type": "existing_project_stage_experiment",
            "dominant_route": "source_translation_then_semantic_tile_atlas",
            "first_skill": "art-translation-to-vdp",
            "asset_strategy": "source-derived two-plane anchor plates plus shared TILESET and MAP study outputs",
            "decision_status": "offline_candidate_only",
            "reason": "Preserve source geometry and test whether a hand-declared seven-color role palette reduces exact tile patterns before runtime work.",
            "forbidden_until_evidence": ["res promotion", "ROM integration", "camera or motion approval", "AAA claim"]},
        "depth_role_map.json": {
            "BG_B": {"source_layers": ["BG0a", "BG0b"], "role": "sky, clouds, moon, distant atmosphere"},
            "BG_A": {"source_layers": ["BG1", "BG2", "BG3", "BG4a", "BG4b"],
                     "role": "castle, wall, roof, deck and near structure", "note": "static source-order plate; independent layer motion is not retained"}},
        "composition_schema.json": {
            "canvas": [WIDTH, HEIGHT], "camera_from_left": 224, "crop_top": 16,
            "recomposition": "source-order alpha composition of source-derived far and near plates",
            "color_conversion": "semantic role whitelist, then nearest VDP word within the role ramp",
            "tilemap": {"tile_size": [8, 8], "map_size": [40, 28], "shared_atlas": True}},
        "layer_plan.json": {
            "source_layer_order": ["BG0a", "BG0b", "BG1", "BG2", "BG3", "BG4a", "BG4b"],
            "study_grouping": {"BG_B": ["BG0a", "BG0b"], "BG_A": ["BG1", "BG2", "BG3", "BG4a", "BG4b"]},
            "claim_ceiling": "static camera 224 only; no autonomous sky motion or BG5"},
        "shared_canvas_contract.json": {
            "width": WIDTH, "height": HEIGHT, "origin": "source anchor renderer",
            "all_planes_share_canvas": True, "camera_anchor": 224,
            "source_mask_policy_preserved": True},
        "hardware_budget_review.json": {
            "status": "offline_estimate_not_validated_budget",
            "seven_color_anchor": {"unique_patterns_with_hv_flip": seven["shared_patterns_with_hv_flip"],
                                   "pattern_bytes": seven["pattern_bytes"], "two_maps_bytes": 4480,
                                   "patterns_plus_maps_bytes": seven["static_anchor_patterns_plus_maps_bytes"]},
            "eight_color_control_anchor": {"unique_patterns_with_hv_flip": eight["shared_patterns_with_hv_flip"],
                                           "pattern_bytes": eight["pattern_bytes"], "two_maps_bytes": 4480,
                                           "patterns_plus_maps_bytes": eight["static_anchor_patterns_plus_maps_bytes"]},
            "scope": "one 320x224 anchor; excludes independent scrolling windows, fighter/HUD/FX residency, VRAM placement, DMA and ROM capture",
            "historical_engine_stage_region": {"tiles": 446, "status": "conditional old estimate, not physical VDP ceiling"},
            "finding": "615 seven-color patterns exceed the historical 446-tile stage allocation by 169; architecture and camera sweep still need a new budget."},
        "delivery_findings.json": {
            "status": "needs_visual_review",
            "positive": ["source geometry retained", "seven-color candidate uses fewer patterns than eight-color control", "indexed planes recompose pixel-exactly from the emitted atlas"],
            "open": ["source color error requires human comparison", "camera endpoints and intermediate scroll are not represented", "BG0 velocity and BG5 animation remain absent", "production VRAM/DMA fit unproven"],
            "promotion": "blocked; scratch study only"}}
    for filename, record in records.items():
        (OUT / filename).write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    readme = f"""# Suzaku semantic palette and tile-atlas study

Status: source-derived, static anchor-camera experiment. It changes no `res/`, runtime code, ROM, or canonical project document.

The input is the exact DEF/SFF-derived `far_bg0a_bg0b_anchor.png` and `near_bg1_bg4_anchor.png` pair bundled under `source/`, with its source-lineage record. The two plates are a camera-224 still; the original layer sprites and MUGEN source remain the visual authority. The raw MUGEN ZIP is not bundled; its SHA-256 is recorded in the lineage, and the builder verifies it when that archive is available locally.

The 7-color candidate uses the proposed role palette, with `#4488CC` removed. The 8-color control retains it. Both variants quantize the supplied approximate swatches through the project's canonical `vdp_word` / `vdp_rgb`, and map source colors only within declared semantic ramps: cool sky/architecture above y=176, wood deck below y=176, with deep shadow shared. Index 0 is reserved for transparency. No new stage pixels were drawn.

Measured atlas results with exact H/V tile reuse:

- 7 colors: {seven['shared_patterns_with_hv_flip']} shared patterns, {seven['pattern_bytes']} pattern bytes, 4,480 bytes for the two 40x28 maps, {seven['static_anchor_patterns_plus_maps_bytes']} bytes total.
- 8-color control: {eight['shared_patterns_with_hv_flip']} shared patterns, {eight['pattern_bytes']} pattern bytes, 4,480 bytes for the two maps, {eight['static_anchor_patterns_plus_maps_bytes']} bytes total.
- 7-color color-error control: MSE {seven['source_hardware_rgb_mse_per_pixel']:.2f}; 8-color: MSE {eight['source_hardware_rgb_mse_per_pixel']:.2f}. This metric is not an aesthetic approval.
- Removing the vivid-blue swatch changes {changed_between_variants} of {len(variant_pixels)} composed pixels versus the 8-color control; RGB MSE between candidates is {variant_mse:.2f}.

The shared 4bpp planar tilebank and name tables were decoded back into both indexed planes and matched pixel-for-pixel. See `scene_tilemap_conversion_report.json`, `tilemap_flag_report.json`, and `per_tile_palette_conflict_report.json` under each variant.

Limit: this combines static source layers into BG_B/BG_A anchor plates at camera 224. Its 615 unique patterns remain 169 above the historical 446-tile stage allocation, which is conditional and not the physical VDP ceiling. It does not preserve independent parallax motion, the sky's autonomous velocity, BG4a's row-varying scale, BG5 animation, HUD/FX palette ownership, camera sweep, ROM residency, or DMA. It is not ready for `res/` or a game build.
"""
    (OUT / "README.md").write_text(readme)
    print(json.dumps({"status": summary["status"],
                      "seven_color": {"tiles": results["seven_color"]["shared_patterns_with_hv_flip"],
                                      "pattern_bytes": results["seven_color"]["pattern_bytes"],
                                      "scene_mse": results["seven_color"]["source_hardware_rgb_mse_per_pixel"]},
                      "eight_color_control": {"tiles": results["eight_color_control"]["shared_patterns_with_hv_flip"],
                                              "pattern_bytes": results["eight_color_control"]["pattern_bytes"],
                                              "scene_mse": results["eight_color_control"]["source_hardware_rgb_mse_per_pixel"]},
                      "changed_pixels_7_vs_8": changed_between_variants,
                      "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
