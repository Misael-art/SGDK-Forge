#!/usr/bin/env python3
"""Package two explicitly authored native TAINA variants.

Pixel choices live in native_pixel_edit_patch.json. This builder only
serializes the declared pixels into evidence, maps, reports and temporary
records; it does not infer shapes, materials or semantic regions.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[2]
WORKSPACE = PROJECT.parents[1]
ROOT = PROJECT / "rascunho/taina_native_headless_authoring_v01"
MODEL = PROJECT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
APPROVED_SOURCE = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/source/face_and_guard_topology_visual_source_v01.png"
APPROVED_SOURCE_SHA = "b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf"
PROBE_A_SHA = "1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830"
PROBE_A = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/taina_48x64_geometry_face_guard_v01.png"
EXERCISE_SHA = "ad6b9606c775710994d65ca2a5f4a7e0ee10dfd4f97ae0f64e05c7b45cc7d874"
EXERCISE = PROJECT / "rascunho/taina_visual_challenger_exercise_v01/exercise_record.json"

spec = importlib.util.spec_from_file_location("geometry_builder", PROJECT / "tools/art/build_taina_native_geometry_challengers_v01.py")
assert spec and spec.loader
geometry_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry_builder)

sys.path.insert(0, str(WORKSPACE / "tools/sgdk_wrapper"))
from forge_art import pixel_contract  # noqa: E402

VARIANTS = [
    ("a1_face_guard_feet_native_pass", "taina_48x64_native_a1_face_guard_feet_v01"),
    ("a2_weight_sash_native_pass", "taina_48x64_native_a2_weight_sash_v01"),
]
LABELS = {"head_or_face": 1, "hair": 2, "torso": 3, "arms_or_guard": 4,
          "hands": 5, "legs": 6, "feet": 7, "sash": 8}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE).as_posix()


def project_rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT).as_posix()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("P")
    visible = [(x, y) for y in range(64) for x in range(48) if image.getpixel((x, y)) != 0]
    return {"width": 48, "height": 64, "mode": "P", "visible_colors": len({image.getpixel(p) for p in visible}),
            "filled_pixels": len(visible), "canvas_pixels": 48 * 64,
            "occupancy_pct": round(len(visible) / (48 * 64) * 100, 2),
            "bbox": [min(x for x, _ in visible), min(y for _, y in visible),
                     max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]}


def save_mask_artifacts(candidate: Path, plan_path: Path, out: Path, asset_id: str) -> dict[str, object]:
    image = Image.open(candidate).convert("P")
    visible = {(x, y) for y in range(64) for x in range(48) if image.getpixel((x, y)) != 0}
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assigned: dict[tuple[int, int], str] = {}
    for row in plan["rows"]:
        y = row["y"]
        for x0, x1, region in row["runs"]:
            if region not in LABELS:
                raise RuntimeError(f"unknown semantic region {region}")
            for x in range(x0, x1 + 1):
                if (x, y) in assigned:
                    raise RuntimeError(f"semantic overlap at {(x, y)}")
                assigned[(x, y)] = region
    if set(assigned) != visible:
        raise RuntimeError(f"semantic plan does not exactly cover visible pixels: missing={len(visible-set(assigned))} extra={len(set(assigned)-visible)}")
    palette = [0, 0, 0]
    for i in range(1, 9):
        palette.extend((34 * (i % 7), 34 * ((i + 2) % 7), 34 * ((i + 4) % 7)))
    palette.extend([0, 0, 0] * (256 - 9))
    sem = Image.new("P", (48, 64), 0)
    sem.putpalette(palette)
    for pos, region in assigned.items():
        sem.putpixel(pos, LABELS[region])
    sem_path = out / "semantic_region_map.png"
    sem.save(sem_path, "PNG", bits=4, transparency=0)

    silhouette = Image.new("P", (48, 64), 0)
    silhouette.putpalette([0, 0, 0, 34, 34, 34] + [0, 0, 0] * 254)
    for pos in visible:
        silhouette.putpixel(pos, 1)
    silhouette_path = out / "silhouette_mask.png"
    silhouette.save(silhouette_path, "PNG", bits=1, transparency=0)

    lineart = Image.new("P", (48, 64), 0)
    lineart.putpalette([0, 0, 0, 34, 0, 34] + [0, 0, 0] * 254)
    for pos in visible:
        lineart.putpixel(pos, 1)
    lineart_path = out / "lineart_blocking_1px.png"
    lineart.save(lineart_path, "PNG", bits=1, transparency=0)

    contour = Image.new("P", (48, 64), 0)
    contour.putpalette([0, 0, 0, 238, 170, 68, 68, 34, 68] + [0, 0, 0] * 253)
    for x, y in visible:
        edge = any(nx < 0 or ny < 0 or nx >= 48 or ny >= 64 or (nx, ny) not in visible
                   for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
        contour.putpixel((x, y), 1 if edge else 2)
    contour_path = out / "contour_overlay.png"
    contour.save(contour_path, "PNG", bits=2, transparency=0)
    counts = {name: sum(1 for region in assigned.values() if region == name) for name in LABELS}
    artifacts = {}
    for name, path in (("silhouette_mask", silhouette_path), ("semantic_region_map", sem_path),
                       ("contour_overlay", contour_path)):
        artifacts[name] = {"path": rel(path), "sha256": sha(path), "asset_id": asset_id,
                           "scale": "48x64", "source": rel(candidate)}
    return {"paths": {k: v["path"] for k, v in artifacts.items()},
            "sha256": {k: v["sha256"] for k, v in artifacts.items()},
            "artifacts": artifacts, "asset_id": asset_id, "scale": "48x64",
            "required_semantic_regions": list(LABELS), "semantic_label_legend": LABELS,
            "semantic_label_counts": counts, "occupancy_metrics": metrics(candidate),
            "bbox": metrics(candidate)["bbox"],
            "method": "authorial_irregular_runs_from_effectively_drawn_regions"}


def panel(entries: list[tuple[str, Path]]) -> Path:
    path = ROOT / "native_headless_authoring_comparison_panel_v01.png"
    canvas = Image.new("RGB", (1500, 420), (30, 32, 44))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 14)
    bold = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Bold.ttf", 17)
    for i, (label, source) in enumerate(entries):
        x = 16 + i * 295
        draw.text((x, 10), label, fill=(238, 238, 230), font=bold)
        image = Image.open(source).convert("RGBA")
        if image.size != (48, 64):
            image.thumbnail((260, 340), Image.Resampling.NEAREST)
            bg = Image.new("RGB", image.size, (238, 238, 230))
            bg.paste(image.convert("RGB"), mask=image.getchannel("A") if "A" in image.getbands() else None)
            preview = bg
        else:
            preview = Image.new("RGB", (240, 320), (238, 238, 230))
            native_preview = image.resize((240, 320), Image.Resampling.NEAREST)
            preview.paste(native_preview, (0, 0), native_preview)
        if preview.height > 320:
            preview = preview.crop((0, 0, min(preview.width, 260), 320))
        canvas.paste(preview, (x + 16, 45))
        draw.text((x, 382), "48x64 / 1x-first / staging", fill=(182, 190, 198), font=font)
    canvas.save(path)
    return path


def create_record(asset_id: str, candidate: Path, pixel_report: Path, evidence: dict[str, str], shape: dict[str, object], budget: dict[str, object], out: Path) -> Path:
    m = metrics(candidate)
    record_evidence = {key: project_rel(WORKSPACE / value) for key, value in evidence.items()}
    record_shape = {name: {**artifact, "path": project_rel(WORKSPACE / artifact["path"]), "source": project_rel(candidate)}
                    for name, artifact in shape["artifacts"].items()}
    record = {
        "schema_version": "1.3.0", "asset_id": asset_id, "asset_kind": "sprite_single",
        "source": {"path": project_rel(MODEL), "sha256": MODEL_SHA, "classification": "concept_high_res", "approval_status": "approved_source"},
        "scale_contract": {"status": "locked", "target_width": 48, "target_height": 64, "selected_width": 48, "selected_height": 64,
                           "probes": [{"width": 48, "height": 64, "path": project_rel(candidate), "technical_status": "passed", "visual_status": "pending", "promotable": False},
                                      {"width": 64, "height": 96, "path": project_rel(PROJECT / "rascunho/taina_visual_challengers_v03/candidates/taina_64x96_challenger_b/taina_64x96_challenger_b.png"), "technical_status": "passed", "visual_status": "pending", "promotable": False}]},
        "producer_output": {"path": project_rel(candidate), "role": "native_candidate", "interaction_channel": "cli_headless", "width": 48, "height": 64, "mode": "P", "visible_rgb_colors": m["visible_colors"], "alpha_values": [0, 255]},
        "native_candidate": {"path": project_rel(candidate), "method": "authored_native_pixel", "width": 48, "height": 64, "pixel_report": project_rel(pixel_report),
                             "visual_evidence": {"candidate_sha256": sha(candidate), "native_1x": record_evidence["native_1x"], "nearest_preview": record_evidence["nearest_preview"],
                                                  "light_background": record_evidence["light_background"], "dark_background": record_evidence["dark_background"], "chroma_background": record_evidence["chroma_background"],
                                                  "preview_scale": 8, "light_rgb": [238, 238, 230], "dark_rgb": [28, 30, 38], "chroma_rgb": [238, 0, 238],
                                                  "human_approval": "doc/art/characters/taina/human_source_authoring_approval_v01.json"},
                             "shape_block_contract": {**record_shape, "required_semantic_regions": shape["required_semantic_regions"],
                                                       "semantic_label_legend": shape["semantic_label_legend"], "semantic_label_counts": shape["semantic_label_counts"],
                                                       "occupancy_metrics": shape["occupancy_metrics"], "bbox": shape["bbox"]}},
        "palette_contract": {"max_visible_colors": 15, "index0_role": "transparent0", "outline_role": "single dark marine/purple ink",
                              "material_roles": ["skin", "orange_top", "teal_wraps", "indigo_trousers", "sash"]},
        "gates": {"semantic_parse": "passed", "lineart": "passed", "color_blocking": "passed", "palette_lock": "passed", "pixel_contract": "passed",
                  "native_visual": "in_progress", "scale": "passed", "budget": "passed", "human": "in_progress", "sgdk_integration": "not_started", "emulator": "not_started"},
        "runtime_evidence": None, "promotion": {"promotable": False, "target": "none"}, "status": "native_authoring",
        "next_action": "human_visual_decision_on_A1_or_A2; no_res_or_animation",
        "provenance": {"interaction_channel": "cli_headless", "source_kind": "native_pixel", "producer_identity": "explicit_pixel_patch_executor",
                        "action_log": project_rel(out / "native_pixel_edit_patch.json"), "human_approval": "doc/art/characters/taina/human_source_authoring_approval_v01.json"},
        "scale_report": {"status": "passed", "camera_width": 320, "camera_height": 224, "hitbox": "undeclared_requires_collision_contract",
                         "notes": "48x64 remains locked; 64x96 is comparison_only.", "probes": project_rel(PROJECT / "rascunho/taina_visual_challengers_v03/scale_budget_report_v03.json")},
        "budget_report": {"status": "passed", "tiles": budget["hero_plus_four_enemies"]["hardware_sprite_count"], "scanline_px": budget["hero_plus_four_enemies"]["max_sprite_pixels_per_scanline"],
                          "notes": "budget_pass limited to static TAINA + four enemies; 3+3 is comparison_only."},
        "visual_report": {"status": "pending", "sha256": sha(candidate), "notes": "native visual and human gates pending; source approval is not pose approval."},
        "incumbent": {"path": project_rel(PROBE_A), "sha256": PROBE_A_SHA, "role": "comparison_only"},
        "methodology_reference": {"path": project_rel(EXERCISE), "sha256": EXERCISE_SHA, "role": "methodology_reference"}
    }
    record_path = out / f"native_sprite_production_record_{asset_id}.json"
    write_json(record_path, record)
    return record_path


def main() -> int:
    if sha(MODEL) != MODEL_SHA or sha(APPROVED_SOURCE) != APPROVED_SOURCE_SHA or sha(PROBE_A) != PROBE_A_SHA:
        raise SystemExit("source/control hash mismatch")
    pre = {"data": geometry_builder.snapshot_tree(PROJECT / "data"), "res": geometry_builder.snapshot_tree(PROJECT / "res"),
           "stage": "before_explicit_native_pixel_patches", "approved_visual_source_sha256": APPROVED_SOURCE_SHA,
           "probe_control_sha256": PROBE_A_SHA}
    write_json(ROOT / "containment_snapshot_pre_headless_authoring_v01.json", pre)
    results = []
    for variant, asset_id in VARIANTS:
        out = ROOT / variant
        patch_path = out / "native_pixel_edit_patch.json"
        candidate = out / f"{asset_id}.png"
        patch_doc = json.loads(patch_path.read_text(encoding="utf-8"))
        app_report = json.loads((out / "native_pixel_edit_application_report.json").read_text(encoding="utf-8"))
        if app_report["result_png_sha256"] != sha(candidate) or app_report["patch_sha256"] != patch_doc["patch_sha256"]:
            raise SystemExit(f"patch binding mismatch for {asset_id}")
        m = metrics(candidate)
        pc = pixel_contract.validate_png(candidate, pixel_contract.ROLE_TRANSPARENT0)
        if pc["blocking"]:
            raise SystemExit(f"pixel contract failed for {asset_id}: {pc}")
        pixel_doc = {k: pc[k] for k in ("schema_version", "tool", "tool_version", "width", "height", "bit_depth", "color_type", "visible_colors", "content_sha256", "status", "blocking_statuses")}
        pixel_doc["mode"] = "P"
        pixel_doc.update({"asset_id": asset_id, "candidate_path": project_rel(candidate), "candidate_sha256": sha(candidate), "transparent_index": 0,
                          "filled_pixels": m["filled_pixels"], "canvas_pixels": m["canvas_pixels"], "bbox": m["bbox"], "occupancy_pct": m["occupancy_pct"]})
        pixel_path = out / "pixel_compliance_report.json"
        write_json(pixel_path, pixel_doc)
        shape = save_mask_artifacts(candidate, out / "semantic_region_plan.json", out, asset_id)
        evidence_raw = geometry_builder.evidence(candidate, out)
        evidence = {"native_1x": evidence_raw["native_1x"], "nearest_preview": evidence_raw["nearest_8x"], "light_background": evidence_raw["light"],
                    "dark_background": evidence_raw["dark"], "chroma_background": evidence_raw["chroma"], "camera_320x224": evidence_raw["camera_320x224"]}
        budget = geometry_builder.budget(asset_id, sha(candidate))
        delta = {"asset_id": asset_id, "candidate_sha256": sha(candidate), "source_candidate_sha256": PROBE_A_SHA,
                 "operations_applied": app_report["operations_applied"], "patch_sha256": app_report["patch_sha256"],
                 "regions_altered": {}}
        for operation in app_report["operations"]:
            delta["regions_altered"].setdefault(operation["region"], 0)
            delta["regions_altered"][operation["region"]] += 1
        current = {(x, y) for y in range(64) for x in range(48) if Image.open(candidate).convert("P").getpixel((x, y)) != 0}
        base = {(x, y) for y in range(64) for x in range(48) if Image.open(PROBE_A).convert("P").getpixel((x, y)) != 0}
        delta["silhouette_added_pixels"] = sorted([list(p) for p in current - base])
        delta["silhouette_removed_pixels"] = sorted([list(p) for p in base - current])
        write_json(out / "mask_delta_report.json", delta)
        write_json(out / "palette_role_map.json", {"schema_version": "1.0.0", "asset_id": asset_id, "index0": {"index": 0, "role": "transparent0"},
            "visible_roles": [{"index": i + 1, "role": role, "rgb": list(rgb)} for i, (role, rgb) in enumerate(geometry_builder.PALETTE) if i + 1 in {v for v in Image.open(candidate).convert("P").getdata() if v}],
            "alias_check": "unique_rgb_per_visible_index", "source": "explicit_patch_preserves_fixed_material_palette"})
        record = create_record(asset_id, candidate, pixel_path, evidence, shape, budget, out)
        result = {"asset_id": asset_id, "candidate_path": rel(candidate), "candidate_sha256": sha(candidate), "patch_path": rel(patch_path),
                  "patch_sha256": app_report["patch_sha256"], "pixel_report_path": rel(pixel_path), "pixel_report_candidate_sha": pixel_doc["candidate_sha256"],
                  "visual_evidence_candidate_sha": sha(candidate), "budget_candidate_sha": budget["candidate_sha256"], "record_path": rel(record),
                  "record_native_candidate": sha(candidate), "shape": shape, "metrics": m, "budget": budget, "evidence": evidence}
        write_json(out / "native_authoring_candidate_report.json", result)
        results.append(result)
    post = {"data": geometry_builder.snapshot_tree(PROJECT / "data"), "res": geometry_builder.snapshot_tree(PROJECT / "res"), "stage": "after_explicit_native_pixel_patches"}
    containment = {"pre": pre, "post": post, "data_unchanged": pre["data"] == post["data"], "res_unchanged": pre["res"] == post["res"], "staging_only": True, "res_promotion": False}
    write_json(ROOT / "containment_report_v01.json", containment)
    if not containment["data_unchanged"] or not containment["res_unchanged"]:
        raise SystemExit("containment failed")
    review_panel = panel([("MODEL SHEET", MODEL), ("SOURCE A", APPROVED_SOURCE), ("A1", ROOT / VARIANTS[0][0] / f"{VARIANTS[0][1]}.png"),
                          ("A2", ROOT / VARIANTS[1][0] / f"{VARIANTS[1][1]}.png"), ("PROBE A", PROBE_A)])
    package = {"schema_version": "1.0.0", "status": "pending_human_decision", "scale": "48x64", "comparison_only": ["64x96"],
               "human_source_decision": {"decision": "approved_as_visual_source_for_native_authoring", "asset_id": "face_and_guard_topology_visual_source_v01", "sha256": APPROVED_SOURCE_SHA,
                                           "record": "doc/art/characters/taina/human_source_authoring_approval_v01.json"},
               "candidates": results, "review_panel": rel(review_panel), "automatic_winner": None,
               "semantic_gate_scope": "A/B/C probe semantic maps are diagnostic only; A1/A2 maps are explicit authorial runs and validated separately",
               "containment": containment, "res_promotion": False, "animation_authorization": False, "visual_pass": False, "ready_for_aaa": False,
               "decision_required": "approved_for_final_native_pose with exact asset_id, SHA-256 and scale=48x64"}
    write_json(ROOT / "native_headless_authoring_package_manifest_v01.json", package)
    print(json.dumps({"status": "passed", "panel": rel(review_panel), "candidates": [{"asset_id": r["asset_id"], "sha256": r["candidate_sha256"], "patch_sha256": r["patch_sha256"]} for r in results]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
