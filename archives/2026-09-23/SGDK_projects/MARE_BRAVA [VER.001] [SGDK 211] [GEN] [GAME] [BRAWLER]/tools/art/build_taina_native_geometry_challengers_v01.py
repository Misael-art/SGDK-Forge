#!/usr/bin/env python3
"""Stage three independent TAINA geometry challengers.

The producer outputs are the only visual inputs.  This builder performs only
auditable operations: border-connected matte extraction, NEAREST fitting,
fixed material-role colour mapping, indexing, evidence composition and
measurement.  It never reads a rejected candidate as an image source.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT.parents[1]
OUT = PROJECT / "rascunho/taina_native_geometry_challengers_v01"
MODEL = PROJECT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
CONTROL_B = PROJECT / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b/taina_48x64_challenger_b.png"
CONTROL_B_SHA = "d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa"
CONTROL_ELITE = PROJECT / "rascunho/taina_native_refinement_v01/taina_48x64_refined_elite_v01.png"
CONTROL_ELITE_SHA = "0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13"
ROUTES = {
    "face_and_guard_topology": {
        "asset_id": "taina_48x64_geometry_face_guard_v01",
        "hypothesis": "FACE_AND_GUARD_TOPOLOGY",
        "source": "face_and_guard_topology/source/face_and_guard_topology_visual_source_v01.png",
    },
    "silhouette_and_weight": {
        "asset_id": "taina_48x64_geometry_silhouette_weight_v01",
        "hypothesis": "SILHOUETTE_AND_WEIGHT",
        "source": "silhouette_and_weight/source/silhouette_and_weight_visual_source_v01.png",
    },
    "integrated_native_redraw": {
        "asset_id": "taina_48x64_geometry_integrated_redraw_v01",
        "hypothesis": "INTEGRATED_NATIVE_REDRAW",
        "source": "integrated_native_redraw/source/integrated_native_redraw_visual_source_v01.png",
    },
}

# One deliberate, unique VDP colour per role. Index 0 is transparent.
PALETTE = [
    ("outline_deep", (34, 0, 34)),
    ("hair_highlight", (102, 68, 68)),
    ("skin_shadow", (136, 68, 34)),
    ("skin_base", (204, 136, 68)),
    ("skin_highlight", (238, 170, 102)),
    ("orange_shadow", (170, 34, 0)),
    ("orange_base", (238, 102, 0)),
    ("orange_highlight", (238, 170, 68)),
    ("teal_shadow", (0, 68, 68)),
    ("teal_base", (34, 136, 136)),
    ("teal_highlight", (102, 204, 170)),
    ("indigo_shadow", (34, 34, 68)),
    ("indigo_base", (68, 68, 136)),
    ("indigo_highlight", (102, 102, 170)),
]

sys.path.insert(0, str(WORKSPACE / "tools/sgdk_wrapper"))
from forge_art import foreground_matte, pixel_contract  # noqa: E402

SIM_PATH = WORKSPACE / "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py"
spec = importlib.util.spec_from_file_location("vdp_sim", SIM_PATH)
assert spec and spec.loader
vdp_sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vdp_sim)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE).as_posix()


def snapshot_tree(directory: Path) -> list[dict[str, object]]:
    return [{"path": rel(p), "sha256": sha(p), "bytes": p.stat().st_size}
            for p in sorted(directory.rglob("*")) if p.is_file()]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_mask(source: Path) -> tuple[Image.Image, dict[str, object]]:
    rgba = Image.open(source).convert("RGBA")
    alpha_values = set(rgba.getchannel("A").getdata())
    if alpha_values != {255}:
        mask = rgba.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
        report = {
            "status": "passed",
            "method": "source_alpha_binary_thresholded_for_native_translation",
            "source_alpha_values": sorted(alpha_values),
            "binary_native_mask": True,
            "blockers": [],
        }
    else:
        mask, report = foreground_matte.extract_foreground_mask(rgba.convert("RGB"))
        report["method_role"] = "border_connected_only_for_opaque_source"
    if not mask.getbbox() or report.get("status") != "passed":
        raise RuntimeError(f"matte failed for {source}: {report}")
    return mask, report


def material_palette_image(rgba: Image.Image) -> Image.Image:
    """Map visible pixels to fixed material ramps; no adaptive quantizer.

    The material decision is a declared spatial/hue block, not a statistical
    recolour: torso/limbs/feet, teal wraps/sash, indigo trousers and dark hair
    use separate fixed ramps so the native translation does not collapse the
    identity materials into one dark cluster.
    """
    colours = [rgb for _, rgb in PALETTE]
    out = Image.new("P", rgba.size, 0)
    flat = [0, 0, 0]
    for _, rgb in PALETTE:
        flat.extend(rgb)
    flat.extend([0, 0, 0] * (16 - len(PALETTE) - 1))
    out.putpalette(flat)
    rgb = rgba.convert("RGB")
    alpha = rgba.getchannel("A")
    role_index = {role: i + 1 for i, (role, _) in enumerate(PALETTE)}

    def choose_role(px: tuple[int, int, int], x: int, y: int) -> str:
        r, g, b = px
        nx, ny = x / 48, y / 64
        lum = (r * 3 + g * 6 + b) / 10
        warm = r > b * 1.25 and r > g * 1.08
        indigo = b > r * 1.12 and b > g * 1.10
        teal = g >= r * 0.82 and b >= r * 0.82 and g + b > r * 1.55 and not indigo
        # The face gets a semantic slot before the general hair rule. This
        # preserves eye/cheek separation at 1x without inventing pixels.
        if 0.20 <= ny < 0.36 and 0.38 <= nx <= 0.70 and not teal and not indigo:
            if lum < 90:
                return "outline_deep"
            return "skin_highlight" if lum > 165 else "skin_base" if lum > 82 else "skin_shadow"
        if ny < 0.30 and lum < 125:
            return "outline_deep" if lum < 78 else "hair_highlight"
        if ny >= 0.56 and not teal and not warm:
            return "indigo_highlight" if lum > 150 else "indigo_base" if lum > 75 else "indigo_shadow"
        if teal:
            return "teal_highlight" if lum > 145 else "teal_base" if lum > 70 else "teal_shadow"
        if ny >= 0.34 and ny < 0.58 and 0.33 < nx < 0.70 and warm:
            return "orange_highlight" if lum > 165 else "orange_base" if lum > 82 else "orange_shadow"
        if indigo:
            return "indigo_highlight" if lum > 150 else "indigo_base" if lum > 75 else "indigo_shadow"
        return "skin_highlight" if lum > 170 else "skin_base" if lum > 92 else "skin_shadow"

    values: list[int] = []
    for y in range(rgba.height):
        for x in range(rgba.width):
            if alpha.getpixel((x, y)) < 128:
                values.append(0)
                continue
            values.append(role_index[choose_role(rgb.getpixel((x, y)), x, y)])
    out.putdata(values)
    out.info["transparency"] = 0
    return out


def fit_native(source: Path) -> tuple[Image.Image, dict[str, object]]:
    src = Image.open(source).convert("RGBA")
    mask, matte = source_mask(source)
    bbox = mask.getbbox()
    assert bbox
    src = src.crop(bbox)
    mask = mask.crop(bbox)
    target_w, target_h = 44, 59
    scale = min(target_w / src.width, target_h / src.height)
    dst_w = max(1, round(src.width * scale))
    dst_h = max(1, round(src.height * scale))
    pixel_contract.assert_nearest_resample("NEAREST")
    art = src.resize((dst_w, dst_h), Image.Resampling.NEAREST)
    alpha = mask.resize((dst_w, dst_h), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (48, 64), (0, 0, 0, 0))
    x = (48 - dst_w) // 2
    y = 2  # visible bottom is locked to ground_y=60
    canvas.paste(art, (x, y), alpha)
    return material_palette_image(canvas), matte


def tile_metrics(image: Image.Image) -> dict[str, object]:
    tiles = [tuple(image.getpixel((x, y)) for y in range(ty, ty + 8) for x in range(tx, tx + 8))
             for ty in range(0, 64, 8) for tx in range(0, 48, 8)]
    visible = [(x, y) for y in range(64) for x in range(48) if image.getpixel((x, y)) != 0]
    bbox = [min(x for x, _ in visible), min(y for _, y in visible), max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]
    return {"raw_tiles": 48, "unique_tiles": len(set(tiles)), "vram_unique_bytes": len(set(tiles)) * 32,
            "dma_upper_bound_bytes": len(set(tiles)) * 32, "visible_pixels": len(visible), "bbox": bbox}


def evidence(candidate: Path, root: Path) -> dict[str, str]:
    ev = root / "evidence"
    ev.mkdir(parents=True, exist_ok=True)
    native = ev / "native_1x.png"
    shutil.copy2(candidate, native)
    image = Image.open(candidate).convert("P")
    nearest = ev / "nearest_8x.png"
    image.resize((384, 512), Image.Resampling.NEAREST).save(nearest, "PNG", bits=4, transparency=0)
    rgba = image.convert("RGBA")
    for name, colour in (("light", (238, 238, 230)), ("dark", (28, 30, 38)), ("chroma", (238, 0, 238))):
        bg = Image.new("RGBA", image.size, colour + (255,))
        bg.alpha_composite(rgba)
        bg.convert("RGB").save(ev / f"{name}_background.png")
    camera = Image.new("RGB", (320, 224), (238, 238, 230))
    x, y = 136, 128
    camera.paste(rgba, (x, y), rgba)
    draw = ImageDraw.Draw(camera)
    draw.line((0, 192, 319, 192), fill=(198, 82, 46), width=1)
    draw.line((160, 128, 160, 223), fill=(72, 128, 140), width=1)
    draw.text((4, 4), "TAÍNA 320x224 / ground_y=192", fill=(28, 30, 38), font=ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 12))
    camera.save(ev / "camera_320x224.png")
    return {"native_1x": rel(native), "nearest_8x": rel(nearest),
            "light": rel(ev / "light_background.png"), "dark": rel(ev / "dark_background.png"),
            "chroma": rel(ev / "chroma_background.png"), "camera_320x224": rel(ev / "camera_320x224.png")}


def shape_block(candidate: Path, root: Path, asset_id: str) -> dict[str, object]:
    shape = root / "shape_block"
    shape.mkdir(parents=True, exist_ok=True)
    image = Image.open(candidate).convert("P")
    alpha = image.convert("RGBA").getchannel("A")
    silhouette = Image.new("P", (48, 64), 0)
    silhouette.putpalette([0, 0, 0, 34, 34, 34] + [0, 0, 0] * 254)
    sem = Image.new("P", (48, 64), 0)
    sem.putpalette([0, 0, 0] + [v for i in range(1, 9) for v in (34 * (i % 7), 34 * ((i + 2) % 7), 34 * ((i + 4) % 7))] + [0, 0, 0] * 247)
    labels = {"head_or_face": 1, "hair": 2, "torso": 3, "arms_or_guard": 4, "hands": 5, "legs": 6, "feet": 7, "sash": 8}
    counts = {key: 0 for key in labels}
    for y in range(64):
        for x in range(48):
            if alpha.getpixel((x, y)) < 128:
                continue
            silhouette.putpixel((x, y), 1)
            nx, ny = x / 48, y / 64
            if ny < .20 and (nx < .32 or nx > .68): name = "hair"
            elif ny < .30: name = "head_or_face"
            elif ny < .46 and (nx < .30 or nx > .70): name = "hands" if ny < .38 else "arms_or_guard"
            elif ny < .58: name = "torso"
            elif ny >= .88: name = "feet"
            elif nx > .60 and .42 < ny < .86: name = "sash"
            else: name = "legs"
            sem.putpixel((x, y), labels[name]); counts[name] += 1
    silhouette.save(shape / "silhouette_mask.png", "PNG", bits=1, transparency=0)
    sem.save(shape / "semantic_region_map.png", "PNG", bits=4, transparency=0)
    contour = Image.new("P", (48, 64), 0)
    contour.putpalette([0, 0, 0, 238, 170, 68, 68, 34, 68] + [0, 0, 0] * 253)
    for y in range(64):
        for x in range(48):
            if alpha.getpixel((x, y)) < 128: continue
            edge = any(nx < 0 or ny < 0 or nx >= 48 or ny >= 64 or alpha.getpixel((nx, ny)) < 128
                       for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
            contour.putpixel((x, y), 1 if edge else 2)
    contour.save(shape / "contour_overlay.png", "PNG", bits=2, transparency=0)
    return {"paths": {name: rel(shape / f"{name}.png") for name in ("silhouette_mask", "semantic_region_map", "contour_overlay")},
            "sha256": {name: sha(shape / f"{name}.png") for name in ("silhouette_mask", "semantic_region_map", "contour_overlay")},
            "asset_id": asset_id, "scale": "48x64", "counts": counts, "method": "candidate_derived_semantic_diagnostic_annotation"}


def compare_masks(candidate: Path) -> dict[str, object]:
    def mask(path: Path) -> set[tuple[int, int]]:
        img = Image.open(path).convert("P")
        return {(x, y) for y in range(64) for x in range(48) if img.getpixel((x, y)) != 0}
    current = mask(candidate)
    comparisons = {}
    for name, path, expected in (("challenger_b", CONTROL_B, CONTROL_B_SHA), ("elite_control", CONTROL_ELITE, CONTROL_ELITE_SHA)):
        if sha(path) != expected: raise RuntimeError(f"control hash mismatch: {path}")
        other = mask(path)
        comparisons[name] = {"control_sha256": expected, "changed_mask_pixels": len(current ^ other),
                             "intersection_pixels": len(current & other), "candidate_only_pixels": len(current - other),
                             "control_only_pixels": len(other - current)}
    return comparisons


def budget(asset_id: str, candidate_sha: str) -> dict[str, object]:
    def sprite(name: str, x: int, y: int, w: int, h: int) -> dict[str, int | str]:
        return {"name": name, "x": x, "y": y, "w": w, "h": h}
    def scene(enemies: int) -> dict[str, object]:
        sprites = [sprite("taina", 136, 128, 48, 64)]
        for i in range(enemies // 2): sprites.append(sprite(f"cria_{i+1}", 32 + i * 28, 128, 44, 64))
        for i in range(enemies - enemies // 2): sprites.append(sprite(f"estivador_{i+1}", 168 + i * 56, 128, 56, 64))
        return vdp_sim.simulate({"display_mode": "h40", "headroom_justification": "static geometry challenger budget; no runtime claim", "sprites": sprites})
    return {"asset_id": asset_id, "candidate_sha256": candidate_sha, "scale": "48x64", "hardware_cells": {"count": 4, "decomposition": "2x2 <=32x32 VDP cells"},
            "hero_plus_four_enemies": scene(4), "next_3_plus_3_comparison_only": scene(6), "measurement_level": "measured"}


def main() -> int:
    if sha(MODEL) != MODEL_SHA: raise SystemExit("approved model sheet hash mismatch")
    pre = {"data": snapshot_tree(PROJECT / "data"), "res": snapshot_tree(PROJECT / "res"), "model_sheet_sha256": MODEL_SHA,
           "controls_read_only": {"challenger_b": CONTROL_B_SHA, "elite": CONTROL_ELITE_SHA}, "stage": "pre_native_translation"}
    write_json(OUT / "containment_snapshot_pre_native_translation_v01.json", pre)
    candidates = []
    for route, spec_data in ROUTES.items():
        root = OUT / route
        source = OUT / spec_data["source"]
        candidate = root / f"{spec_data['asset_id']}.png"
        native, matte = fit_native(source)
        native.save(candidate, "PNG", bits=4, transparency=0)
        pc = pixel_contract.validate_png(candidate, pixel_contract.ROLE_TRANSPARENT0)
        if pc["blocking"]: raise RuntimeError(f"pixel contract failed: {pc}")
        visible = sorted({i for i in Image.open(candidate).convert("P").getdata() if i})
        palette_roles = [{"index": i + 1, "role": role, "rgb": list(rgb)} for i, (role, rgb) in enumerate(PALETTE) if i + 1 in visible]
        write_json(root / "foreground_matte_report.json", {**matte, "input_source_path": rel(source), "input_source_sha256": sha(source), "candidate_sha256": sha(candidate), "alpha_contract": "binary_index0_transparent", "blockers": []})
        write_json(root / "pixel_compliance_report.json", {"schema_version": "1.0.0", "asset_id": spec_data["asset_id"], "candidate_sha256": sha(candidate), "tool": pc["tool"], "tool_version": pc["tool_version"], "status": pc["status"], "blocking_statuses": pc.get("blocking_statuses", []), "width": 48, "height": 64, "visible_colors": len(visible), "transparent_index": 0, "translation": "NEAREST_plus_fixed_material_role_map_no_statistical_quantization"})
        write_json(root / "palette_role_map.json", {"schema_version": "1.0.0", "asset_id": spec_data["asset_id"], "index0": {"index": 0, "role": "transparent0"}, "visible_roles": palette_roles, "alias_check": "unique_rgb_per_visible_index", "source": "fixed_material_palette"})
        ev = evidence(candidate, root)
        shape = shape_block(candidate, root, spec_data["asset_id"])
        item = {"route": route, "asset_id": spec_data["asset_id"], "hypothesis": spec_data["hypothesis"], "scale": "48x64", "source": {"path": rel(source), "sha256": sha(source), "role": "visual_producer_output_from_approved_model_sheet_only", "source_kind": "ai_generated_high_res", "producer": "imagegen_builtin"}, "candidate": {"path": rel(candidate), "sha256": sha(candidate), "method": "assisted_native_translation_with_native_material_cluster_curation", "source_of_pixels": "route_source_only"}, "evidence": ev, "shape_block": shape, "palette_role_map": rel(root / "palette_role_map.json"), "foreground_matte_report": rel(root / "foreground_matte_report.json"), "pixel_compliance_report": rel(root / "pixel_compliance_report.json"), "tile_metrics": tile_metrics(Image.open(candidate).convert("P")), "geometry_comparison": compare_masks(candidate), "budget": budget(spec_data["asset_id"], sha(candidate)), "review": "pending_human_decision"}
        candidates.append(item)
    post = {"data": snapshot_tree(PROJECT / "data"), "res": snapshot_tree(PROJECT / "res"), "stage": "post_native_translation"}
    containment = {"pre": pre, "post": post, "data_unchanged": pre["data"] == post["data"], "res_unchanged": pre["res"] == post["res"], "staging_only": True, "res_promotion": False}
    write_json(OUT / "containment_report_v01.json", containment)
    if not containment["data_unchanged"] or not containment["res_unchanged"]: raise SystemExit("containment failed: data/ or res/ changed")
    manifest = {"schema_version": "1.0.0", "status": "pending_human_decision", "round": "native_geometry_refinement_v01", "identity_source": {"path": rel(MODEL), "sha256": MODEL_SHA, "role": "approved_model_sheet_visual_source_of_truth"}, "forbidden_sources": ["rejected_basic", "rejected_elite", "challenger_b_as_pixel_source"], "scale_contract": {"status": "locked", "selected": "48x64", "comparison_only": ["64x96"]}, "candidates": candidates, "controls": {"challenger_b": {"path": rel(CONTROL_B), "sha256": CONTROL_B_SHA, "role": "comparison_only"}, "elite": {"path": rel(CONTROL_ELITE), "sha256": CONTROL_ELITE_SHA, "role": "best_technical_control_comparison_only"}}, "containment_report": rel(OUT / "containment_report_v01.json"), "decision_required": "proposed_for_final_native_pose with exact asset_id, SHA-256 and scale=48x64", "decision_candidates": [{"decision": "proposed_for_final_native_pose", "asset_id": c["asset_id"], "sha256": c["candidate"]["sha256"], "scale": "48x64"} for c in candidates], "discarded_attempts": [{"attempt": "initial_global_nearest_palette_translation", "symptom": "skin_hair_and_indigo_collapsed_into_dark_or_teal_clusters_at_1x", "cause": "global_colour_mapping_was_not_material_native", "sha256_observed": {"face_guard": "976f2b763d64ba2adade353a631a19dd81a6f7d51170055d2137a9d4a7679195", "silhouette_weight": "07a414bb7f7909eb3302f6adc687f98b3aacbc8dc588338e6709db70ccd6fe0e", "integrated_redraw": "031c7cd1276851297af6c7966fa5f44dce964567ac9d87294a87bcf8af321250"}, "disposition": "discarded_from_review; no res_or_runtime_use"}], "promotable": False, "res_promotion": False, "animation_authorization": False, "visual_pass": False, "ready_for_aaa": False}
    write_json(OUT / "native_geometry_challengers_manifest_v01.json", manifest)
    print(json.dumps({"manifest": rel(OUT / "native_geometry_challengers_manifest_v01.json"), "candidates": [{"asset_id": x["asset_id"], "sha256": x["candidate"]["sha256"], "visible_colors": len([r for r in x["palette_role_map"]])} for x in candidates], "containment": containment}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
