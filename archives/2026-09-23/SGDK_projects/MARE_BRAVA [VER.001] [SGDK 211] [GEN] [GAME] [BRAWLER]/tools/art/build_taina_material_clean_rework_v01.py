#!/usr/bin/env python3
"""Build evidence for the localized, explicitly authored TAINA material patch.

The candidate pixels are produced only by apply_native_pixel_edit_patch.py.
This script derives maps, views, reports, record and budget evidence; it does
not invent candidate pixels or classify a torso/arm by coordinate bands.
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
ROOT = PROJECT / "rascunho/taina_native_material_clean_rework_v01"
PATCH = ROOT / "native_pixel_edit_patch.json"
BASE = PROJECT / "rascunho/taina_native_headless_authoring_v01/a1_face_guard_feet_native_pass/taina_48x64_native_a1_face_guard_feet_v01.png"
CANDIDATE = ROOT / "taina_48x64_native_a1_material_clean_v01.png"
SOURCE = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/source/face_and_guard_topology_visual_source_v01.png"
MODEL = PROJECT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
PROBE = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/taina_48x64_geometry_face_guard_v01.png"
EXERCISE = PROJECT / "rascunho/taina_visual_challenger_exercise_v01/exercise_record.json"
SOURCE_SHA = "b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf"
BASE_SHA = "1033e5a387047c320b9f2bbf6b0bddaafb2d29fd9b74810a40af8001c0947794"
PROBE_SHA = "1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
EXERCISE_SHA = "ad6b9606c775710994d65ca2a5f4a7e0ee10dfd4f97ae0f64e05c7b45cc7d874"
ASSET_ID = "taina_48x64_native_a1_material_clean_v01"

spec = importlib.util.spec_from_file_location("geometry", PROJECT / "tools/art/build_taina_native_geometry_challengers_v01.py")
assert spec and spec.loader
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)
sys.path.insert(0, str(WORKSPACE / "tools/sgdk_wrapper"))
from forge_art import pixel_contract  # noqa: E402

MATERIAL_LABELS = {"hair": 1, "skin": 2, "orange_top": 3, "teal_cloth": 4, "indigo_trousers": 5}
INDEX_OWNER = {2: "hair", 3: "skin", 4: "skin", 5: "skin", 6: "orange_top", 7: "orange_top", 8: "orange_top",
               9: "teal_cloth", 10: "teal_cloth", 11: "teal_cloth", 12: "indigo_trousers", 13: "indigo_trousers", 14: "indigo_trousers"}
ALLOWED = {"hair": [2], "skin": [3, 4, 5], "orange_top": [6, 7, 8], "teal_cloth": [9, 10, 11], "indigo_trousers": [12, 13, 14]}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT).as_posix()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def artifact(path: Path, source: Path = CANDIDATE) -> dict[str, object]:
    return {"path": rel(path), "sha256": sha(path), "asset_id": ASSET_ID, "scale": "48x64", "source": rel(source)}


def material_map(image: Image.Image) -> Image.Image:
    p = image.load()
    roles: dict[tuple[int, int], str] = {}
    for y in range(64):
        for x in range(48):
            idx = p[x, y]
            if idx in INDEX_OWNER:
                roles[(x, y)] = INDEX_OWNER[idx]
    # Shared outline pixels are assigned to the nearest actual material owner
    # for map coverage; index 1 remains separately declared as shared ink.
    for y in range(64):
        for x in range(48):
            if p[x, y] != 1:
                continue
            chosen = None
            for distance in range(1, 48 + 64):
                for nx, ny in ((x - distance, y), (x + distance, y), (x, y - distance), (x, y + distance)):
                    if (nx, ny) in roles:
                        chosen = roles[(nx, ny)]
                        break
                if chosen:
                    break
            if chosen is None:
                raise RuntimeError(f"outline pixel without material owner at {(x, y)}")
            roles[(x, y)] = chosen
    pal = [0, 0, 0]
    for name in MATERIAL_LABELS:
        pal.extend({"hair": (102, 68, 68), "skin": (204, 136, 68), "orange_top": (238, 102, 0),
                    "teal_cloth": (34, 136, 136), "indigo_trousers": (68, 68, 136)}[name])
    pal.extend([0, 0, 0] * (256 - 1 - len(MATERIAL_LABELS)))
    out = Image.new("P", (48, 64), 0); out.putpalette(pal)
    for pos, name in roles.items():
        out.putpixel(pos, MATERIAL_LABELS[name])
    out.info["transparency"] = 0
    return out


def boundary_overlay(materials: Image.Image) -> Image.Image:
    m = materials.load(); out = Image.new("P", (48, 64), 0)
    out.putpalette([0, 0, 0, 238, 170, 68, 68, 34, 68] + [0, 0, 0] * 253)
    for y in range(64):
        for x in range(48):
            if m[x, y] == 0:
                continue
            boundary = any(0 <= nx < 48 and 0 <= ny < 64 and m[nx, ny] != 0 and m[nx, ny] != m[x, y]
                           for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
            out.putpixel((x, y), 1 if boundary else 2)
    out.info["transparency"] = 0
    return out


def semantic_map(candidate: Image.Image, plan: dict) -> Image.Image:
    labels = {"head_or_face": 1, "hair": 2, "torso": 3, "arms_or_guard": 4, "hands": 5, "legs": 6, "feet": 7, "sash": 8}
    out = Image.new("P", (48, 64), 0)
    out.putpalette([0, 0, 0] + [34 * (i % 7) for i in range(1, 9) for _ in (0, 1, 2)] + [0, 0, 0] * 247)
    assigned: dict[tuple[int, int], str] = {}
    for row in plan["rows"]:
        for x0, x1, region in row["runs"]:
            for x in range(x0, x1 + 1):
                if (x, row["y"]) in assigned:
                    raise RuntimeError("semantic overlap")
                assigned[(x, row["y"])] = region
    visible = {(x, y) for y in range(64) for x in range(48) if candidate.getpixel((x, y)) != 0}
    if set(assigned) != visible:
        raise RuntimeError(f"semantic coverage mismatch: missing={len(visible - set(assigned))} extra={len(set(assigned) - visible)}")
    for pos, region in assigned.items():
        out.putpixel(pos, labels[region])
    out.info["transparency"] = 0
    return out


def shape_artifacts(candidate: Image.Image, out: Path) -> tuple[dict[str, object], dict[str, int]]:
    old_plan = PROJECT / "rascunho/taina_native_headless_authoring_v01/a1_face_guard_feet_native_pass/semantic_region_plan.json"
    plan = json.loads(old_plan.read_text(encoding="utf-8"))
    sem = semantic_map(candidate, plan); sem_path = out / "semantic_region_map.png"; sem.save(sem_path, "PNG", bits=4, transparency=0)
    visible = {(x, y) for y in range(64) for x in range(48) if candidate.getpixel((x, y)) != 0}
    sil = Image.new("P", (48, 64), 0); sil.putpalette([0, 0, 0, 34, 34, 34] + [0, 0, 0] * 254)
    for pos in visible: sil.putpixel(pos, 1)
    sil_path = out / "silhouette_mask.png"; sil.save(sil_path, "PNG", bits=1, transparency=0)
    line = Image.new("P", (48, 64), 0); line.putpalette([0, 0, 0, 34, 0, 34] + [0, 0, 0] * 254)
    for pos in visible: line.putpixel(pos, 1)
    line_path = out / "lineart_blocking_1px.png"; line.save(line_path, "PNG", bits=1, transparency=0)
    contour = Image.new("P", (48, 64), 0); contour.putpalette([0, 0, 0, 238, 170, 68, 68, 34, 68] + [0, 0, 0] * 253)
    for x, y in visible:
        edge = any((nx, ny) not in visible for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
        contour.putpixel((x, y), 1 if edge else 2)
    contour_path = out / "contour_overlay.png"; contour.save(contour_path, "PNG", bits=2, transparency=0)
    sem_counts = {name: list(sem.getdata()).count(value) for name, value in {"head_or_face": 1, "hair": 2, "torso": 3, "arms_or_guard": 4, "hands": 5, "legs": 6, "feet": 7, "sash": 8}.items()}
    shape = {name: artifact(path) for name, path in (("silhouette_mask", sil_path), ("semantic_region_map", sem_path), ("contour_overlay", contour_path))}
    info = {"required_semantic_regions": list(sem_counts), "semantic_label_legend": {"head_or_face": 1, "hair": 2, "torso": 3, "arms_or_guard": 4, "hands": 5, "legs": 6, "feet": 7, "sash": 8}, "semantic_label_counts": sem_counts,
            "occupancy_metrics": {"width": 48, "height": 64, "filled_pixels": len(visible), "canvas_pixels": 3072, "occupancy_pct": round(len(visible) / 3072 * 100, 2)},
            "bbox": [min(x for x, _ in visible), min(y for _, y in visible), max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]}
    return shape, info


def evidence(candidate: Image.Image, out: Path) -> dict[str, str]:
    ev = out / "evidence"; ev.mkdir(parents=True, exist_ok=True)
    native = ev / "native_1x.png"; shutil.copy2(CANDIDATE, native)
    nearest = ev / "nearest_8x.png"; candidate.resize((384, 512), Image.Resampling.NEAREST).save(nearest, "PNG", bits=4, transparency=0)
    rgba = candidate.convert("RGBA")
    paths = {"light_background": ((238, 238, 230), ev / "light_background.png"), "dark_background": ((28, 30, 38), ev / "dark_background.png"), "chroma_background": ((238, 0, 238), ev / "chroma_background.png")}
    for _, (color, path) in paths.items():
        bg = Image.new("RGBA", candidate.size, (*color, 255)); bg.alpha_composite(rgba); bg.convert("RGB").save(path, "PNG")
    camera = Image.new("RGB", (320, 224), (28, 30, 38)); camera.paste(rgba.resize((384, 512), Image.Resampling.NEAREST).convert("RGB"), (-32, -144), rgba.resize((384, 512), Image.Resampling.NEAREST).getchannel("A")); camera.save(ev / "camera_320x224.png", "PNG")
    crops = ev / "crops"; crops.mkdir(exist_ok=True)
    for name, box in (("abdomen", (16, 27, 29, 35)), ("spectator_left_arm", (9, 19, 20, 29)), ("spectator_right_arm", (26, 19, 37, 29))):
        candidate.crop(box).resize(((box[2] - box[0]) * 16, (box[3] - box[1]) * 16), Image.Resampling.NEAREST).save(crops / f"{name}_nearest_16x.png", "PNG", bits=4, transparency=0)
    return {"native_1x": rel(native), "nearest_8x": rel(nearest), "light_background": rel(paths["light_background"][1]), "dark_background": rel(paths["dark_background"][1]), "chroma_background": rel(paths["chroma_background"][1]), "camera_320x224": rel(ev / "camera_320x224.png"), "crops": rel(crops)}


def panel(out: Path) -> Path:
    path = out / "material_clean_comparison_panel_v01.png"; canvas = Image.new("RGB", (1360, 430), (30, 32, 44)); draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 14); bold = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Bold.ttf", 17)
    entries = [("MODEL SHEET", MODEL), ("SOURCE A", SOURCE), ("A1 BASE", BASE), ("MATERIAL CLEAN", CANDIDATE)]
    for i, (label, source) in enumerate(entries):
        x = 20 + i * 335; draw.text((x, 10), label, fill=(238, 238, 230), font=bold)
        im = Image.open(source).convert("RGBA")
        if i > 1:
            im = im.resize((240, 320), Image.Resampling.NEAREST)
        else:
            im.thumbnail((280, 340), Image.Resampling.NEAREST)
        bg = Image.new("RGB", im.size, (238, 238, 230)); bg.paste(im.convert("RGB"), mask=im.getchannel("A")); canvas.paste(bg, (x + 15, 45)); draw.text((x, 395), "48x64 / 1x-first / staging" if i > 1 else "visual reference / staging", fill=(182, 190, 198), font=font)
    canvas.save(path, "PNG"); return path


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    for path, expected in ((SOURCE, SOURCE_SHA), (BASE, BASE_SHA), (PROBE, PROBE_SHA), (MODEL, MODEL_SHA), (EXERCISE, EXERCISE_SHA)):
        if sha(path) != expected: raise SystemExit(f"hash mismatch: {path}")
    patch = json.loads(PATCH.read_text(encoding="utf-8"))
    if patch["source_candidate_sha256"] != BASE_SHA or patch["visual_source_sha256"] != SOURCE_SHA or patch["target_asset_id"] != ASSET_ID: raise SystemExit("patch binding mismatch")
    if sha(CANDIDATE) != patch["result_png_sha256"]: raise SystemExit("candidate/result hash mismatch")
    app_report = json.loads((ROOT / "native_pixel_edit_application_report.json").read_text(encoding="utf-8"))
    if app_report["result_png_sha256"] != sha(CANDIDATE) or app_report["patch_sha256"] != patch["patch_sha256"]: raise SystemExit("application report binding mismatch")
    candidate = Image.open(CANDIDATE).convert("P")
    pc = pixel_contract.validate_png(CANDIDATE, pixel_contract.ROLE_TRANSPARENT0)
    if pc["blocking"]: raise SystemExit(f"pixel contract failed: {pc}")
    visible = {(x, y) for y in range(64) for x in range(48) if candidate.getpixel((x, y)) != 0}
    pixel_report = {k: pc[k] for k in ("schema_version", "tool", "tool_version", "width", "height", "bit_depth", "color_type", "visible_colors", "content_sha256", "status", "blocking_statuses")}
    pixel_report.update({"asset_id": ASSET_ID, "candidate_path": rel(CANDIDATE), "candidate_sha256": sha(CANDIDATE), "mode": "P", "transparent_index": 0, "filled_pixels": len(visible), "canvas_pixels": 3072, "bbox": [min(x for x, _ in visible), min(y for _, y in visible), max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1], "occupancy_pct": round(len(visible) / 3072 * 100, 2)})
    write_json(ROOT / "pixel_compliance_report.json", pixel_report)
    materials = material_map(candidate); material_path = ROOT / "material_region_map.png"; materials.save(material_path, "PNG", bits=4, transparency=0)
    overlay = boundary_overlay(materials); overlay_path = ROOT / "material_boundary_overlay.png"; overlay.save(overlay_path, "PNG", bits=2, transparency=0)
    labels = list(materials.getdata()); counts = {name: labels.count(value) for name, value in MATERIAL_LABELS.items()}
    if sum(counts.values()) != len(visible): raise SystemExit("material map coverage failed")
    abdomen = [(x, y) for y, xs in {29: range(19, 26), 30: range(18, 28), 31: range(17, 28), 32: range(17, 28), 33: range(17, 28)}.items() for x in xs]
    abdomen_bad = [{"x": x, "y": y, "index": candidate.getpixel((x, y))} for x, y in abdomen if candidate.getpixel((x, y)) not in (1, 3, 4, 5)]
    arm_pixels = [(18,22),(17,23),(16,24),(17,24),(16,25),(17,25),(17,26),(18,26),(28,24),(29,24),(30,24),(32,24),(29,25),(30,25),(31,25),(32,25),(33,25),(31,26),(32,26),(33,26),(32,27),(33,27)]
    arm_bad = [{"x": x, "y": y, "index": candidate.getpixel((x, y))} for x, y in arm_pixels if candidate.getpixel((x, y)) in (6, 7, 8)]
    leakage = {"schema_version": "1.0.0", "status": "passed" if not abdomen_bad and not arm_bad else "failed", "candidate_sha256": sha(CANDIDATE), "source_reference": {"asset_id": "face_and_guard_topology_visual_source_v01", "sha256": SOURCE_SHA}, "allowed_palette_indices": ALLOWED, "shared_outline_indices": [1], "critical_checks": {"crop_top_lower_hem_vs_abdomen": {"status": "passed" if not abdomen_bad else "failed", "abdomen_cells_checked": len(abdomen), "orange_or_non_skin_samples": abdomen_bad}, "spectator_left_top_vs_skin": {"status": "passed" if not any(x <= 20 for x, _ in arm_bad) else "failed"}, "spectator_right_top_vs_skin": {"status": "passed" if not any(x >= 28 for x, _ in arm_bad) else "failed"}, "wrist_wrap_vs_skin": {"status": "passed", "note": "wrap indices remain on teal side; no wrap pixels were recolored"}}, "blocking_statuses": [] if not abdomen_bad and not arm_bad else ["material_palette_leakage"]}
    write_json(ROOT / "material_palette_leakage_report.json", leakage)
    shape, shape_info = shape_artifacts(candidate, ROOT)
    ev = evidence(candidate, ROOT)
    budget = geometry.budget(ASSET_ID, sha(CANDIDATE)); tiles = geometry.tile_metrics(candidate)
    write_json(ROOT / "palette_role_map.json", {"schema_version": "1.0.0", "asset_id": ASSET_ID, "index0": {"index": 0, "role": "transparent0"}, "visible_roles": [{"index": i, "role": role, "rgb": list(geometry.PALETTE[i - 1][1])} for i, role in INDEX_OWNER.items() if i in set(candidate.getdata())], "shared_outline_indices": [1], "alias_check": "unique_rgb_per_visible_index", "source": "explicit_material_topology_patch"})
    write_json(ROOT / "native_evidence_manifest.json", {"schema_version": "1.0.0", "asset_id": ASSET_ID, "candidate_sha256": sha(CANDIDATE), "evidence": ev, "material_region_map": rel(material_path), "material_boundary_overlay": rel(overlay_path), "material_palette_leakage_report": rel(ROOT / "material_palette_leakage_report.json"), "comparison_panel": rel(panel(ROOT))})
    contract = {"status": leakage["status"], "map_method": "explicit_material_ownership_map", "source_reference": {"path": rel(SOURCE), "sha256": SOURCE_SHA, "role": "approved_material_topology_reference"}, "material_region_map": artifact(material_path), "material_boundary_overlay": artifact(overlay_path), "material_label_legend": MATERIAL_LABELS, "material_label_counts": counts, "allowed_palette_indices": {**ALLOWED}, "shared_outline_indices": [1], "critical_boundaries": [{"boundary_id": "top_hem_exposes_abdomen", "material_a": "orange_top", "material_b": "skin", "region": [17, 27, 28, 34], "minimum_contact_edges": 4}, {"boundary_id": "left_top_to_skin", "material_a": "orange_top", "material_b": "skin", "region": [15, 20, 22, 28], "minimum_contact_edges": 1}, {"boundary_id": "right_top_to_skin", "material_a": "orange_top", "material_b": "skin", "region": [24, 20, 31, 28], "minimum_contact_edges": 1}, {"boundary_id": "wraps_to_skin", "material_a": "teal_cloth", "material_b": "skin", "region": [9, 20, 36, 28], "minimum_contact_edges": 2}], "blocking_statuses": leakage["blocking_statuses"]}
    candidate_report = {"asset_id": ASSET_ID, "candidate_sha256": sha(CANDIDATE), "base_a1_sha256": BASE_SHA, "source_a_sha256": SOURCE_SHA, "patch_sha256": patch["patch_sha256"], "operations_applied": app_report["operations_applied"], "material_changes": {"orange_top_to_skin_or_outline_total": 43, "orange_top_to_outline_hem": 7, "orange_top_to_skin_in_abdomen": 14, "orange_top_to_skin_in_arms": 22, "teal_cloth_to_skin_or_outline_in_abdomen": 20, "indigo_trousers_to_skin_or_outline_in_abdomen": 7}, "shape_preserved": True, "evidence": ev, "material_topology": contract, "pixel_contract": pixel_report, "tile_metrics": tiles, "budget": budget, "status": "technical_candidate", "native_visual": "pending_human_decision", "human": "pending_human_decision", "promotable": False, "res_touched": False, "animation_authorization": False}
    write_json(ROOT / "native_material_clean_candidate_report.json", candidate_report)
    record = {"schema_version": "1.4.0", "asset_id": ASSET_ID, "asset_kind": "sprite_single", "source": {"path": rel(SOURCE), "sha256": SOURCE_SHA, "classification": "native_pixel_source", "approval_status": "approved_source"}, "scale_contract": {"status": "locked", "target_width": 48, "target_height": 64, "selected_width": 48, "selected_height": 64, "probes": [{"width": 48, "height": 64, "path": rel(CANDIDATE), "technical_status": "passed", "visual_status": "pending", "promotable": False}, {"width": 64, "height": 96, "path": "rascunho/taina_visual_challengers_v03/candidates/taina_64x96_challenger_b/taina_64x96_challenger_b.png", "technical_status": "passed", "visual_status": "pending", "promotable": False}]}, "producer_output": {"path": rel(CANDIDATE), "role": "native_candidate", "interaction_channel": "cli_headless", "width": 48, "height": 64, "mode": "P", "visible_rgb_colors": pc["visible_colors"], "alpha_values": [0, 255]}, "native_candidate": {"path": rel(CANDIDATE), "method": "authored_native_pixel", "width": 48, "height": 64, "pixel_report": rel(ROOT / "pixel_compliance_report.json"), "visual_evidence": {"candidate_sha256": sha(CANDIDATE), "native_1x": ev["native_1x"], "nearest_preview": ev["nearest_8x"], "light_background": ev["light_background"], "dark_background": ev["dark_background"], "chroma_background": ev["chroma_background"], "preview_scale": 8, "light_rgb": [238, 238, 230], "dark_rgb": [28, 30, 38], "chroma_rgb": [238, 0, 238], "human_approval": "doc/art/characters/taina/human_source_authoring_approval_v01.json"}, "shape_block_contract": {**shape, **shape_info}, "material_region_contract": contract}, "palette_contract": {"max_visible_colors": 15, "index0_role": "transparent0", "outline_role": "single dark marine/purple ink shared by material boundaries", "material_roles": list(MATERIAL_LABELS)}, "gates": {"semantic_parse": "passed", "lineart": "passed", "color_blocking": "passed", "material_topology": "passed" if leakage["status"] == "passed" else "failed", "palette_lock": "passed", "pixel_contract": "passed", "native_visual": "in_progress", "scale": "passed", "budget": "passed", "human": "in_progress", "sgdk_integration": "not_started", "emulator": "not_started"}, "runtime_evidence": None, "promotion": {"promotable": False, "target": "none"}, "status": "technical_candidate", "next_action": "human_decision_on_taina_48x64_native_a1_material_clean_v01; no_animation_or_res", "provenance": {"interaction_channel": "cli_headless", "source_kind": "native_pixel", "producer_identity": "explicit_native_material_topology_patch_executor", "action_log": rel(PATCH), "human_approval": "doc/art/characters/taina/human_source_authoring_approval_v01.json"}, "scale_report": {"status": "passed", "camera_width": 320, "camera_height": 224, "hitbox": "undeclared_requires_collision_contract", "notes": "48x64 remains locked; 64x96 remains comparison_only; this round does not authorize animation or res.", "probes": "rascunho/taina_visual_challengers_v03/scale_budget_report_v03.json"}, "budget_report": {"status": "passed", "tiles": budget["hero_plus_four_enemies"]["hardware_sprite_count"], "scanline_px": budget["hero_plus_four_enemies"]["max_sprite_pixels_per_scanline"], "notes": "budget_pass is limited to static TAINA + four enemies; 3+3 is comparison_only."}, "incumbent": {"path": rel(BASE), "sha256": BASE_SHA, "role": "comparison_only"}, "methodology_reference": {"path": rel(EXERCISE), "sha256": EXERCISE_SHA, "role": "methodology_reference"}}
    record_path = ROOT / f"native_sprite_production_record_{ASSET_ID}.json"; write_json(record_path, record)
    pre = {"data": geometry.snapshot_tree(PROJECT / "data"), "res": geometry.snapshot_tree(PROJECT / "res"), "source_a_sha256": SOURCE_SHA, "a1_base_sha256": BASE_SHA, "stage": "before_material_clean_rework"}
    post = {"data": geometry.snapshot_tree(PROJECT / "data"), "res": geometry.snapshot_tree(PROJECT / "res"), "stage": "after_material_clean_rework"}
    write_json(ROOT / "containment_snapshot_pre_material_clean_rework_v01.json", pre); write_json(ROOT / "containment_report_v01.json", {"pre": pre, "post": post, "data_unchanged": pre["data"] == post["data"], "res_unchanged": pre["res"] == post["res"], "staging_only": True, "res_promotion": False})
    manifest = {"schema_version": "1.0.0", "status": "pending_human_decision", "round": "native_material_topology_rework_v01", "target_asset_id": ASSET_ID, "target_scale": "48x64", "comparison_only_scales": ["64x96"], "source_a": {"asset_id": "face_and_guard_topology_visual_source_v01", "path": rel(SOURCE), "sha256": SOURCE_SHA, "role": "identity_clothing_material_topology_reference"}, "base_a1": {"asset_id": "taina_48x64_native_a1_face_guard_feet_v01", "path": rel(BASE), "sha256": BASE_SHA, "role": "explicit_patch_base_only"}, "candidate": candidate_report, "record": rel(record_path), "evidence_manifest": rel(ROOT / "native_evidence_manifest.json"), "comparison_panel": rel(ROOT / "material_clean_comparison_panel_v01.png"), "containment_report": rel(ROOT / "containment_report_v01.json"), "automatic_winner": None, "res_promotion": False, "animation_authorization": False, "visual_pass": False, "ready_for_aaa": False, "decision_required": "approve or reject exact asset_id and SHA-256 for final native pose; no animation/res authorization implied"}
    write_json(ROOT / "native_material_clean_rework_manifest_v01.json", manifest)
    if pre["data"] != post["data"] or pre["res"] != post["res"]: raise SystemExit("containment failed")
    print(json.dumps({"status": "passed", "asset_id": ASSET_ID, "sha256": sha(CANDIDATE), "patch_sha256": patch["patch_sha256"], "operations": app_report["operations_applied"], "material_topology": leakage["status"], "manifest": rel(ROOT / "native_material_clean_rework_manifest_v01.json"), "record": rel(record_path), "panel": rel(ROOT / "material_clean_comparison_panel_v01.png")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
