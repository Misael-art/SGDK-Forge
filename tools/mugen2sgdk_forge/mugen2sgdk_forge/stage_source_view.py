"""Static MUGEN stage source compositor for inspection, not SGDK asset output."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

from .stage_bands import _camera_offset, _effective_delta, _round_pixel


def render(st, sprites: list, camera_from_left: int, crop_top: int = 16,
           width: int = 320, height: int = 224,
           speed_remap_by_scanline: dict[int, dict[str, float]] | None = None) -> dict:
    sprite_map = {(sprite.group, sprite.image): sprite for sprite in sprites}
    layers = []
    palette = None
    unsupported = []
    for order, layer in enumerate(st.layers):
        if layer.type == "anim":
            continue
        if not layer.spriteno:
            continue
        if layer.trans != "none" or layer.window is not None or layer.tile[1] != 0:
            unsupported.append({"layer": layer.name, "trans": layer.trans,
                                "window": layer.window, "tile_y": layer.tile[1]})
            continue
        sprite = sprite_map.get(tuple(layer.spriteno))
        if sprite is None:
            unsupported.append({"layer": layer.name, "missing_sprite": list(layer.spriteno)})
            continue
        if palette is None:
            palette = sprite.palette
        elif sprite.palette != palette:
            raise ValueError("source view requires one shared SFF palette")
        layers.append((order, layer, sprite))
    if unsupported:
        raise ValueError("static source renderer does not support these layer features: " + repr(unsupported))
    if palette is None:
        raise ValueError("stage contains no static source layers")

    pixels = bytearray(width * height)
    owners = [-1] * (width * height)
    row_deltas: list[dict[str, float]] = [dict() for _ in range(height)]
    center = int(st.localcoord[0]) // 2
    left_camera = -st.camera["boundleft"]
    for layer_index, (_, layer, sprite) in enumerate(layers):
        source_y0 = int(layer.start[1]) - sprite.axis_y - crop_top
        if layer.tile[0] == 0:
            tile_indices = (0,)
        else:
            tile_indices = range(-3, 4) if layer.tile[0] == 1 else range(int(layer.tile[0]))
        tile_step = sprite.width + int(layer.tilespacing[0])
        for screen_y in range(height):
            sy = screen_y - source_y0
            if not 0 <= sy < sprite.height:
                continue
            delta = _effective_delta(layer, sprite, sy)
            if speed_remap_by_scanline is not None:
                remap = speed_remap_by_scanline.get(screen_y, {})
                delta = float(remap.get(str(round(delta, 9)), delta))
            camera_shift = _camera_offset(camera_from_left, left_camera, delta)
            left_x = center + int(layer.start[0]) - sprite.axis_x + _round_pixel(left_camera * delta) - camera_shift
            row_deltas[screen_y][layer.name] = delta
            source_start = sy * sprite.width
            source_row = sprite.pixels[source_start:source_start + sprite.width]
            for tile_index in tile_indices:
                copy_x = left_x + tile_index * tile_step
                for source_x, pixel in enumerate(source_row):
                    screen_x = copy_x + source_x
                    if not 0 <= screen_x < width:
                        continue
                    if layer.mask and pixel == 0:
                        continue
                    pos = screen_y * width + screen_x
                    pixels[pos] = pixel
                    owners[pos] = layer_index

    visible = {layer.name: 0 for _, layer, _ in layers}
    visible_index0 = {layer.name: 0 for _, layer, _ in layers}
    per_row = []
    for y in range(height):
        counts = {layer.name: 0 for _, layer, _ in layers}
        zero_counts = {layer.name: 0 for _, layer, _ in layers}
        base = y * width
        for x in range(width):
            pos = base + x
            owner = owners[pos]
            if owner >= 0:
                name = layers[owner][1].name
                counts[name] += 1
                if pixels[pos] == 0:
                    zero_counts[name] += 1
        for name, count in counts.items():
            visible[name] += count
            visible_index0[name] += zero_counts[name]
        nonempty = [name for name, count in counts.items() if count]
        visible_deltas = sorted({round(row_deltas[y][name], 9) for name in nonempty})
        per_row.append({"screen_y": y,
                        "visible_pixels_by_layer": {name: count for name, count in counts.items() if count},
                        "visible_source_index0_pixels_by_layer": {name: count for name, count in zero_counts.items() if count},
                        "visible_layers": nonempty,
                        "horizontal_delta_by_layer": {name: round(row_deltas[y][name], 9)
                                                       for name in nonempty},
                        "horizontal_deltas": visible_deltas,
                        "one_scroll_group_needed_per_visible_delta": len(visible_deltas)})
    return {"pixels": bytes(pixels), "palette": palette, "visible_pixels_by_layer": visible,
            "visible_source_index0_pixels_by_layer": visible_index0,
            "scanlines": per_row,
            "source_layers": [{"name": layer.name, "layerno": layer.layerno, "mask": layer.mask,
                               "delta": list(layer.delta), "xscale": list(layer.xscale) if layer.xscale else None,
                               "velocity": list(layer.velocity), "source_sprite": list(layer.spriteno)}
                              for _, layer, _ in layers],
            "animated_layers_skipped": [layer.name for layer in st.layers if layer.type == "anim"]}


def aggregate_camera_sweep(samples, anchor: int) -> dict:
    """Aggregate visible source-speed evidence without retaining every raster."""
    cameras = []
    accumulators = None
    for raw_camera, view in samples:
        camera = int(raw_camera)
        if camera in cameras:
            raise ValueError("camera sweep positions must be unique")
        cameras.append(camera)
        rows = view.get("scanlines", [])
        if accumulators is None:
            accumulators = [{"groups": {}, "total": 0} for _ in rows]
        elif len(rows) != len(accumulators):
            raise ValueError("all camera sweep samples must have the same scanline count")
        distance = abs(camera - anchor) if isinstance(anchor, int) and not isinstance(anchor, bool) else 0
        for y, row in enumerate(rows):
            groups = accumulators[y]["groups"]
            counts = row.get("visible_pixels_by_layer", {})
            deltas = row.get("horizontal_delta_by_layer", {})
            if set(counts) != set(deltas):
                raise ValueError("source-view scanline must map every visible layer to a horizontal delta")
            for layer, count in counts.items():
                speed = round(float(deltas[layer]), 9)
                count = int(count)
                group = groups.setdefault(speed, {"speed": speed, "visible_pixels": 0,
                                                  "distance_weighted_pixels": 0,
                                                  "max_camera_distance": 0,
                                                  "max_camera_from_left": None,
                                                  "layers": []})
                group["visible_pixels"] += count
                group["distance_weighted_pixels"] += count * distance
                accumulators[y]["total"] += count
                if count > 0 and (distance > group["max_camera_distance"]):
                    group["max_camera_distance"] = distance
                    group["max_camera_from_left"] = camera
                if layer not in group["layers"]:
                    group["layers"].append(layer)
    if not cameras or accumulators is None:
        raise ValueError("camera sweep requires at least one rendered camera sample")
    if not isinstance(anchor, int) or isinstance(anchor, bool) or not min(cameras) <= anchor <= max(cameras):
        raise ValueError("camera sweep anchor must be an integer inside sampled bounds")
    scanlines = [{"screen_y": y, "total_visible_pixel_samples": row["total"],
                  "source_speed_groups": [row["groups"][speed] for speed in sorted(row["groups"])]}
                 for y, row in enumerate(accumulators)]
    total_samples = sum(row["total"] for row in accumulators)
    return {"schema": "mugen2sgdk_forge.stage_camera_sweep_profile/v1",
            "camera_positions_from_left": cameras,
            "sample_count": len(cameras),
            "reference_camera_from_left": anchor,
            "total_visible_pixel_samples": total_samples,
            "scanlines": scanlines,
            "method": "Exact source compositor visibility counts and speed groups aggregated for each requested integer camera sample; no raster copies retained.",
            "limitations": ["source renderer semantics and pixel rounding have not been compared with MUGEN runtime",
                            "static layers only; animated BG and BGCtrl are omitted",
                            "camera sweep weights are not Plane A/B ownership, palette, tilemap, or hardware budget"],
            "claim_ceiling": "source_composition_camera_coverage_only"}


def analyze(st, sprites: list, source_sha256: str, output_dir: Path,
            crop_top: int = 16, width: int = 320, height: int = 224,
            sweep_camera_step: int | None = None) -> dict:
    span = st.camera["boundright"] - st.camera["boundleft"]
    if not float(span).is_integer():
        raise ValueError("camera span must be integral for source-view samples")
    camera_positions = sorted({0, int(span) // 2, int(span)})
    output_dir.mkdir(parents=True, exist_ok=True)
    views, previews = [], []
    for camera in camera_positions:
        view = render(st, sprites, camera, crop_top, width, height)
        image = Image.frombytes("P", (width, height), view["pixels"])
        rgb_palette = [component for rgb in view["palette"] for component in rgb]
        image.putpalette(rgb_palette + [0] * (768 - len(rgb_palette)))
        path = output_dir / f"mugen_static_camera_{camera:04d}.png"
        image.save(path, format="PNG", bits=8, optimize=False)
        scanlines = view["scanlines"]
        multi_delta = [row for row in scanlines if row["one_scroll_group_needed_per_visible_delta"] > 1]
        over_two = [row for row in scanlines if row["one_scroll_group_needed_per_visible_delta"] > 2]
        views.append({"camera_from_left": camera,
                      "visible_pixels_by_layer": view["visible_pixels_by_layer"],
                      "visible_source_index0_pixels_by_layer": view["visible_source_index0_pixels_by_layer"],
                      "multi_delta_scanline_count": len(multi_delta),
                      "scanlines_over_two_plane_capacity_count": len(over_two),
                      "max_distinct_scroll_groups_in_scanline": max(
                          row["one_scroll_group_needed_per_visible_delta"] for row in scanlines),
                      "multi_delta_scanlines": multi_delta,
                      "scanlines_over_two_plane_capacity": over_two,
                      "scanlines": scanlines})
        previews.append({"camera_from_left": camera, "path": path.name,
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "status": "static_source_composite_not_game_asset"})
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
            "status": "static_source_composite_only",
            "source_sha256": source_sha256,
            "source_stage": st.name,
            "viewport": {"width": width, "height": height, "crop_top": crop_top},
            "camera_samples_from_left_bound": camera_positions,
            "layer_order": "source DEF order; layerno metadata retained",
            "semantic_limits": ["animated BG and BGCtrl are omitted",
                                "non-none trans, window and vertical tiling are unsupported",
                                "pixel rounding has not been compared with MUGEN runtime",
                                "each scanline can use one horizontal delta per VDP plane; assignment of layers to A/B is not modeled",
                                "MUGEN mask=false source index0 may need remapping to a visible MD color",
                                "not a Mega Drive plane composition or visual approval"],
            "views": views, "previews": previews,
            "claim_ceiling": "source_composition_analysis_only"}
    if sweep_camera_step is not None:
        if not isinstance(sweep_camera_step, int) or isinstance(sweep_camera_step, bool) or sweep_camera_step <= 0:
            raise ValueError("sweep camera step must be a positive integer")
        sweep_positions = list(range(0, int(span) + 1, sweep_camera_step))
        if sweep_positions[-1] != int(span):
            sweep_positions.append(int(span))
        anchor = int(span) // 2
        report["camera_sweep_profile"] = aggregate_camera_sweep(
            ((camera, render(st, sprites, camera, crop_top, width, height))
             for camera in sweep_positions), anchor)
    return report


def analyze_files(package: Path, def_name: str, sff_name: str, output_dir: Path,
                  report_path: Path, crop_top: int = 16,
                  sweep_camera_step: int | None = None) -> dict:
    from .stage_bands import load_source

    st, sprites = load_source(package, def_name, sff_name)
    report = analyze(st, sprites, hashlib.sha256(package.read_bytes()).hexdigest(), output_dir,
                     crop_top=crop_top, sweep_camera_step=sweep_camera_step)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
