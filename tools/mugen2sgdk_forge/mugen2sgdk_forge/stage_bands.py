"""Viewport analysis for a one-layer-per-scanline-band Mega Drive plane.

This is an offline source-pattern and streaming estimate. It does not emit SGDK
assets, prove a VDP layout, or emulate MUGEN's subpixel rasterizer.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

from .stage_measure import _canon


def _round_pixel(value: float) -> int:
    """Match stage_measure's explicit nearest-integer projection policy."""
    return round(value)


def _effective_delta(layer, sprite, sprite_y: int) -> float:
    base = layer.delta[0]
    if layer.type != "parallax":
        return base
    scale = layer.xscale or (1.0, 1.0)
    # Elecbyte's 1.0 specification defines a linear top-to-bottom interpolation.
    # The last source scanline is used as the bottom endpoint in this estimate.
    t = sprite_y / max(1, sprite.height - 1)
    return base * (scale[0] + (scale[1] - scale[0]) * t)


def _camera_offset(camera_from_left: int, left_camera: float, delta: float) -> int:
    # Difference between the rounded left-bound and current camera projections.
    return _round_pixel(left_camera * delta) - _round_pixel((left_camera - camera_from_left) * delta)


def _ceil8(value: int) -> int:
    return (value + 7) // 8 * 8


def _palette_hash(palette) -> str:
    payload = bytes(component for rgb in palette for component in rgb)
    return hashlib.sha256(payload).hexdigest()


def _tile_cost(rows: list[bytearray], width: int, height: int, line_info: dict,
               camera_positions: list[int], camera_frame_step: int) -> dict:
    map_width = len(rows[0])
    tile_patterns = {}
    for tile_row in range((height + 7) // 8):
        for tile_col in range(map_width // 8):
            tile_patterns[(tile_row, tile_col)] = _canon(
                tuple(tuple(rows[y][tile_col * 8 + x] for x in range(8))
                      for y in range(tile_row * 8, min(tile_row * 8 + 8, height))))
    visible_sets, camera_rows = [], []
    for camera_index, camera in enumerate(camera_positions):
        keys, cells = set(), set()
        for y in range(height):
            offset = line_info[y]["offsets"][camera_index]
            tile_row = y // 8
            first = offset // 8
            last = (offset + width - 1) // 8
            for col in range(first, last + 1):
                cells.add((tile_row, col))
                keys.add(tile_patterns[(tile_row, col)])
        visible_sets.append(keys)
        camera_rows.append({"camera_from_left": camera, "visible_unique_source_tiles_with_flip": len(keys),
                            "visible_tile_cells": len(cells)})
    counts = [row["visible_unique_source_tiles_with_flip"] for row in camera_rows]
    peak = max(counts)
    camera_to_index = {camera: index for index, camera in enumerate(camera_positions)}
    transitions = []
    max_entering = 0
    for index, camera in enumerate(camera_positions):
        target_index = camera_to_index.get(camera + camera_frame_step)
        if target_index is None:
            continue
        entering = visible_sets[target_index] - visible_sets[index]
        leaving = visible_sets[index] - visible_sets[target_index]
        max_entering = max(max_entering, len(entering))
        transitions.append({"from_camera": camera, "to_camera": camera_positions[target_index],
                            "minimum_new_unique_patterns": len(entering),
                            "patterns_no_longer_visible": len(leaving),
                            "new_pattern_bytes_lower_bound": len(entering) * 32})
    return {"minimum_unique_source_tiles_with_flip": min(counts),
            "maximum_unique_source_tiles_with_flip": peak,
            "peak_camera_positions": [row["camera_from_left"] for row in camera_rows
                                      if row["visible_unique_source_tiles_with_flip"] == peak],
            "union_visible_patterns_over_all_sampled_cameras": len(set().union(*visible_sets)),
            "max_visible_tile_cells": max(row["visible_tile_cells"] for row in camera_rows),
            "camera_positions": camera_rows,
            "streaming_lower_bound_per_camera_frame_step": {
                "camera_frame_step": camera_frame_step,
                "max_new_unique_patterns": max_entering,
                "max_new_pattern_bytes": max_entering * 32,
                "warning": "ideal set difference only; excludes tilemap writes, DMA setup, cache pinning, alignment and VBlank competition",
                "transitions": transitions}}


def analyze(st, sprites: list, contract: dict, source_sha256: str,
            output_dir: Path | None = None, palette_candidate: dict | None = None) -> dict:
    """Build sampled per-row strips and measure visible source tile patterns.

    Contract bands must be sorted, disjoint, and cover the complete viewport.
    One static source layer owns each band. Parallax xscale is translated into
    per-line horizontal offsets, matching the documented MUGEN meaning.
    """
    width = int(contract["viewport_width"])
    height = int(contract["viewport_height"])
    crop_top = int(contract["crop_top"])
    if width <= 0 or width % 8 or height <= 0 or height % 8:
        raise ValueError("viewport width and height must be positive and tile-aligned")
    bands = contract.get("bands", [])
    if not bands:
        raise ValueError("contract requires at least one band")
    ordered = sorted(bands, key=lambda b: (int(b["y0"]), int(b["y1"])))
    cursor = 0
    for band in ordered:
        y0, y1 = int(band["y0"]), int(band["y1"])
        if y0 != cursor or y1 <= y0 or y1 > height:
            raise ValueError(f"bands must cover [0,{height}) exactly without overlap; gap/overlap at {cursor}")
        cursor = y1
    if cursor != height:
        raise ValueError(f"bands end at {cursor}; expected {height}")

    sprite_map = {(s.group, s.image): s for s in sprites}
    layer_map = {layer.name: layer for layer in st.layers}
    palette = None
    prepared = []
    for band in ordered:
        name = band["layer"]
        layer = layer_map.get(name)
        if not layer or not layer.spriteno:
            raise ValueError(f"{name}: band requires a static source layer")
        if layer.type not in ("normal", "parallax"):
            raise ValueError(f"{name}: unsupported layer type {layer.type}")
        if layer.trans != "none":
            raise ValueError(f"{name}: blend mode {layer.trans} requires a separate compositor")
        if layer.tile != (0, 0):
            raise ValueError(f"{name}: source tiling requires an explicit tiling compositor")
        sprite = sprite_map.get(tuple(layer.spriteno))
        if sprite is None:
            raise ValueError(f"{name}: missing SFF sprite {layer.spriteno}")
        if palette is None:
            palette = sprite.palette
        elif sprite.palette != palette:
            raise ValueError("bands use different SFF palettes; explicit palette remapping is required")
        source_y0 = int(layer.start[1]) - sprite.axis_y - crop_top
        source_rows = []
        for y in range(int(band["y0"]), int(band["y1"])):
            sy = y - source_y0
            if 0 <= sy < sprite.height:
                source_rows.append((y, sy, _effective_delta(layer, sprite, sy)))
            else:
                raise ValueError(f"{name}: band row {y} maps outside source sprite (source y={sy})")
        prepared.append({"contract": band, "layer": layer, "sprite": sprite,
                         "source_rows": source_rows, "source_y0": source_y0})

    span = st.camera["boundright"] - st.camera["boundleft"]
    left_camera = -st.camera["boundleft"]
    if not float(span).is_integer():
        raise ValueError("camera span must be integral for exhaustive integer-camera sampling")
    sample = contract.get("camera_sampling", {})
    step = int(sample.get("step", 1))
    camera_frame_step = int(sample.get("camera_frame_step", step))
    if step <= 0:
        raise ValueError("camera sampling step must be positive")
    if camera_frame_step <= 0:
        raise ValueError("camera frame step must be positive")
    if camera_frame_step < step or camera_frame_step % step:
        raise ValueError("camera frame step must be a positive multiple of the camera sample step")
    camera_positions = list(range(0, int(span) + 1, step))
    if camera_positions[-1] != int(span):
        camera_positions.append(int(span))

    line_info = {}
    maximum_extent = width
    for item in prepared:
        for y, sy, delta in item["source_rows"]:
            offsets = [_camera_offset(c, left_camera, delta) for c in camera_positions]
            maximum_extent = max(maximum_extent, max(offsets, default=0) + width)
            line_info[y] = {"source_y": sy, "delta": delta, "offsets": offsets,
                            "layer": item["layer"], "sprite": item["sprite"]}
    map_width = _ceil8(maximum_extent)
    rows = [bytearray(map_width) for _ in range(height)]
    coverage_rows = [bytearray(map_width) for _ in range(height)]
    opaque_zero_rows = [bytearray(map_width) for _ in range(height)]
    screen_center = int(st.localcoord[0]) // 2
    for y, info in line_info.items():
        sy = info["source_y"]
        if sy is None:
            continue
        layer, sprite, delta = info["layer"], info["sprite"], info["delta"]
        left_x = screen_center + int(layer.start[0]) - sprite.axis_x + _round_pixel(left_camera * delta)
        src_start = sy * sprite.width
        for sx, pixel in enumerate(sprite.pixels[src_start:src_start + sprite.width]):
            dx = left_x + sx
            if 0 <= dx < map_width:
                coverage_rows[y][dx] = 1
                rows[y][dx] = pixel
                if not layer.mask and pixel == 0:
                    opaque_zero_rows[y][dx] = 1

    palette_key = _palette_hash(palette)
    pattern_rows = [[256 if opaque_zero_rows[y][x] else rows[y][x]
                     for x in range(map_width)] for y in range(height)]
    source_cost = _tile_cost(pattern_rows, width, height, line_info, camera_positions, camera_frame_step)
    opaque_zero_by_camera = []
    for camera_index, camera in enumerate(camera_positions):
        per_layer = {item["layer"].name: 0 for item in prepared}
        for y in range(height):
            info = line_info[y]
            if info["layer"].mask:
                continue
            offset = info["offsets"][camera_index]
            per_layer[info["layer"].name] += sum(opaque_zero_rows[y][offset:offset + width])
        opaque_zero_by_camera.append({"camera_from_left": camera,
                                      "visible_opaque_index0_pixels_by_layer": per_layer,
                                      "total_visible_opaque_index0_pixels": sum(per_layer.values())})
    opaque_zero_visible = any(row["total_visible_opaque_index0_pixels"] for row in opaque_zero_by_camera)
    candidate_cost = None
    candidate_zero_index = None
    if palette_candidate is not None:
        from .converters.sprites import vdp_rgb, vdp_word

        words = [int(word, 0) for word in palette_candidate["palette_words"]]
        if len(words) != 16 or words[0] != 0:
            raise ValueError("palette candidate must contain the 16 CRAM words from stage-candidate")
        target_rgb = [vdp_rgb(word) for word in words[1:9]]
        index_map = [0] * 256
        for index, rgb in enumerate(palette):
            if index == 0:
                continue
            source_rgb = vdp_rgb(vdp_word(rgb))
            winner = min(range(len(target_rgb)),
                         key=lambda target: sum((source_rgb[c] - target_rgb[target][c]) ** 2 for c in range(3)))
            index_map[index] = winner + 1
        source_zero_rgb = vdp_rgb(vdp_word(palette[0]))
        candidate_zero_target = min(range(len(target_rgb)),
                                    key=lambda target: sum((source_zero_rgb[c] - target_rgb[target][c]) ** 2
                                                          for c in range(3))) + 1
        candidate_zero_index = candidate_zero_target if opaque_zero_visible else 0
        mapped_rows = [bytearray(candidate_zero_target if opaque_zero_rows[y][x] else index_map[rows[y][x]]
                                  for x in range(map_width)) for y in range(height)]
        candidate_cost = _tile_cost(mapped_rows, width, height, line_info, camera_positions, camera_frame_step)

    source_layers = []
    for item in prepared:
        layer = item["layer"]
        source_layers.append({"band": item["contract"]["name"], "layer": layer.name,
                              "y0": int(item["contract"]["y0"]), "y1": int(item["contract"]["y1"]),
                              "delta": list(layer.delta), "xscale": list(layer.xscale) if layer.xscale else None,
                              "mask": layer.mask, "trans": layer.trans,
                              "axis": [item["sprite"].axis_x, item["sprite"].axis_y],
                              "source_sprite": list(layer.spriteno)})

    previews = []
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        sample_cameras = sorted({camera_positions[0], camera_positions[len(camera_positions) // 2], camera_positions[-1]})
        for camera in sample_cameras:
            ci = camera_positions.index(camera)
            rgba = bytearray(width * height * 4)
            for y in range(height):
                offset = line_info[y]["offsets"][ci]
                info = line_info[y]
                layer = info["layer"]
                for x in range(width):
                    map_x = offset + x
                    out_i = (y * width + x) * 4
                    if map_x >= map_width or not coverage_rows[y][map_x]:
                        continue
                    index = rows[y][map_x]
                    color = palette[index]
                    rgba[out_i:out_i + 4] = bytes((*color, 0 if layer.mask and index == 0 else 255))
            im = Image.frombytes("RGBA", (width, height), bytes(rgba))
            encoded_path = output_dir / f"source_band_camera_{camera:04d}.png"
            im.save(encoded_path, format="PNG", bits=8, optimize=False)
            previews.append({"camera_from_left": camera, "path": encoded_path.name,
                             "sha256": hashlib.sha256(encoded_path.read_bytes()).hexdigest(),
                             "status": "source_preview_not_runtime_or_visual_approval"})

    masked_bands = [item["layer"].name for item in prepared if item["layer"].mask]
    report = {
        "schema": "mugen2sgdk_forge.stage_bands_report/v1",
        "status": "analysis_only_opaque_index0_remap_required" if opaque_zero_visible else "analysis_only",
        "source_sha256": source_sha256,
        "source_palette_sha256": palette_key,
        "source_stage": st.name,
        "contract_sha256": hashlib.sha256((json.dumps(contract, sort_keys=True, separators=(",", ":"))).encode()).hexdigest(),
        "viewport": {"width": width, "height": height, "crop_top": crop_top},
        "camera_sampling": {"start_from_left_bound": 0, "end_from_left_bound": int(span),
                            "step": step, "positions": len(camera_positions),
                            "camera_frame_step": camera_frame_step,
                            "integer_camera_exhaustive": step == 1},
        "projection": {"camera_rounding": "Python round() nearest-even; emulator parity unverified",
                       "parallax_xscale": "base_delta times linearly interpolated top-to-bottom xscale",
                       "basis": "Elecbyte MUGEN 1.0 Background/Stage Documentation, Parallaxing background elements",
                       "limitations": ["subpixel MUGEN rasterization not compared against a running MUGEN reference",
                                       "source-index tiles are not ResComp output or a final palette measurement"]},
        "source_layers": source_layers,
        "line_scroll_profile": [
            {"screen_y": y, "layer": line_info[y]["layer"].name,
             "source_y": line_info[y]["source_y"], "camera_delta_per_pixel": line_info[y]["delta"],
             "offsets_at_first_middle_last_camera_sample": [
                 line_info[y]["offsets"][0], line_info[y]["offsets"][len(camera_positions) // 2],
                 line_info[y]["offsets"][-1]]}
            for y in range(height)],
        "map": {"width_pixels_for_full_camera_span": map_width,
                "width_tiles": map_width // 8,
                "fits_64_column_plane": map_width <= 512,
                "fits_128_column_plane": map_width <= 1024,
                "plane_map_bytes_64x32": 64 * 32 * 2,
                "plane_map_bytes_128x32": 128 * 32 * 2},
        "viewport_pattern_cost": source_cost,
        "candidate_palette_pattern_cost": ({
            "status": ("unapproved_candidate_with_opaque_zero_remap" if opaque_zero_visible
                       else "unapproved_palette_sensitivity_only"),
            "candidate_palette_sha256": hashlib.sha256(json.dumps(palette_candidate["palette_words"],
                                                                    separators=(",", ":")).encode()).hexdigest(),
            "candidate_palette_report_sha256": palette_candidate.get("_report_sha256"),
            "palette_approved": False,
            "opaque_source_zero_target_index": candidate_zero_index,
            "maximum_unique_tiles_with_flip": candidate_cost["maximum_unique_source_tiles_with_flip"],
            "peak_camera_positions": candidate_cost["peak_camera_positions"],
            "union_visible_patterns_over_all_sampled_cameras": candidate_cost["union_visible_patterns_over_all_sampled_cameras"],
            "max_new_patterns_per_camera_frame_step": candidate_cost["streaming_lower_bound_per_camera_frame_step"]["max_new_unique_patterns"],
            "max_new_pattern_bytes_lower_bound": candidate_cost["streaming_lower_bound_per_camera_frame_step"]["max_new_pattern_bytes"]
        } if candidate_cost is not None else {"status": "not_measured"}),
        "source_zero_semantics": {"mugen_mask_true_zero_maps_to_md_transparent_zero": True,
                                  "mugen_mask_false_visible_zero_requires_nonzero_md_index": True,
                                  "visible_opaque_index0_pixels_by_camera": opaque_zero_by_camera,
                                  "opaque_zero_remap_required": opaque_zero_visible,
                                  "source_index0_hardware_pattern_sentinel": 256},
        "semantic_gates": {"mugen_mask_layers": masked_bands,
                           "genesis_scroll_plane_color0_is_transparent": True,
                           "layer_assignment_across_bg_a_bg_b": "not_modeled",
                           "palette_approval": "pending",
                           "rescomp_and_rom_measurement": "pending",
                           "visual_approval": "pending"},
        "previews": previews,
        "claim_ceiling": "source_derived_analysis_only",
    }
    return report


def load_source(package: Path, def_name: str, sff_name: str):
    import zipfile

    from .parsers import sff, stage

    with zipfile.ZipFile(package) as archive:
        parsed = stage.parse(archive.read(def_name).decode("latin-1"), def_name)
        sprites, warnings = sff.parse(archive.read(sff_name))
    if parsed.warnings or warnings:
        raise ValueError("source parser warnings require adjudication: " + repr(parsed.warnings + warnings))
    return parsed, sprites


def analyze_files(package: Path, def_name: str, sff_name: str, contract_path: Path,
                  output_dir: Path | None = None, palette_candidate_path: Path | None = None) -> dict:
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    st, sprites = load_source(package, def_name, sff_name)
    palette_candidate = None
    if palette_candidate_path is not None:
        candidate_bytes = palette_candidate_path.read_bytes()
        palette_candidate = json.loads(candidate_bytes)
        if palette_candidate.get("source_sha256") != hashlib.sha256(package.read_bytes()).hexdigest():
            raise ValueError("palette candidate source SHA-256 does not match the stage package")
        palette_candidate["_report_sha256"] = hashlib.sha256(candidate_bytes).hexdigest()
    report = analyze(st, sprites, contract, hashlib.sha256(package.read_bytes()).hexdigest(),
                     output_dir, palette_candidate)
    report["contract_source_sha256"] = hashlib.sha256(contract_bytes).hexdigest()
    if palette_candidate_path is not None:
        report["palette_candidate_source"] = str(palette_candidate_path)
    return report
