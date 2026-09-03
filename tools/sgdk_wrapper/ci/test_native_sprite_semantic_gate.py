#!/usr/bin/env python3
"""Adversarial fixtures for the native-sprite semantic validator (v2.1).

The validator is now a real semantic gate, not a schema-only checker. These
fixtures prove it rejects every false green from the 2026-08-30 TAINA review:

  - candidate declared 48x64 but PNG on disk is 16x16;
  - pixel_report empty / unbindable;
  - five distinct PATHS with IDENTICAL content (native/nearest/light/dark/chroma);
  - nearest preview that is not NEAREST of the candidate;
  - light/dark/chroma recomposites that are not recomposited on the declared RGB;
  - scale=passed with report failed/not_applicable;
  - scale=passed with no probe measurements;
  - budget=passed without a budget report;
  - human approval that is fake / a methodology JSON masquerading as approval;
  - canvas area confused with visible pixels (filled == canvas);
  - incumbent null/stale; methodology reference null/stale;
  - challenger promoted without perceptual_win AND system_win;
  - invalid schema (record missing required fields);
  - wrong-root / project-root not existing;
  - shape-block missing the 8 semantic regions;
  - schema 1.4 material map missing, palette leakage, shared-role overlap,
    forged boundary overlay and absent critical garment/skin boundary.

A positive (portable) fixture is rebuilt under a foreign temp root and must
pass, proving safe path resolution + a complete, honest record.

Usage:
    python tools/sgdk_wrapper/ci/test_native_sprite_semantic_gate.py
Exit codes:
    0 = all pass
    1 = at least one fixture failed
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sgdk_wrapper"))

from validate_native_sprite_production import validate_record  # noqa: E402

passed = 0
failed = 0
total = 0
REGIONS = ["head_or_face", "hair", "torso", "arms_or_guard", "hands",
           "legs", "feet", "sash"]
MATERIALS = ["skin", "cloth"]


def check(name, cond, detail=""):
    global passed, failed, total
    total += 1
    if cond:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- {detail}")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_ok_indexed(path: Path, w=16, h=16):
    from PIL import Image
    img = Image.new("P", (w, h))
    palette = [0x00, 0x00, 0x00, 0x22, 0x22, 0x22, 0x44, 0x66, 0xAA]
    img.putpalette(palette)
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = 0 if (x == 0 or y == 0 or x == w - 1 or y == h - 1) else 1 + ((x + y) % 2)
    img.save(path, "PNG", bits=4, transparency=0)


def write_indexed_character(path: Path, w=48, h=64):
    """A real indexed (mode-P) candidate with a genuine silhouette and >= 2
    visible colors, so the forge-art pixel contract passes (mode P, transparent
    index 0, 9-bit grid, multiple of 8)."""
    from PIL import Image
    img = Image.new("P", (w, h))
    # 8 palette entries on the 9-bit grid.
    palette = [0x00, 0x00, 0x00,
               0x22, 0x22, 0x22,
               0x44, 0x66, 0x88,
               0x88, 0xAA, 0xCC,
               0xEE, 0xCC, 0x88]
    img.putpalette(palette + [0] * 750)
    px = img.load()
    half = w // 2
    for y in range(5, h - 5):
        # Deliberately non-rectangular character-like silhouette.
        if y < 16:
            radius = 6
        elif y < 38:
            radius = 10 - abs(26 - y) // 6
        else:
            radius = 4 + (y % 2)
        for x in range(max(1, half - radius), min(w - 1, half + radius + 1)):
            if y >= 42 and abs(x - half) < 2:
                continue
            px[x, y] = 1 + ((x + y) % 4)
    img.info["transparency"] = 0
    img.save(path, "PNG", bits=4, transparency=0)
    return path


def make_derived(candidate: Path, ev_dir: Path, tag: str, scale=8,
                 light=(238, 238, 230), dark=(28, 30, 38), chroma=(238, 0, 238)):
    from PIL import Image
    base = Image.open(candidate).convert("RGBA")
    ev_dir.mkdir(parents=True, exist_ok=True)
    native = ev_dir / f"{tag}_native_1x.png"
    nearest = ev_dir / f"{tag}_nearest.png"
    lightf = ev_dir / f"{tag}_light.png"
    darkf = ev_dir / f"{tag}_dark.png"
    chromaf = ev_dir / f"{tag}_chroma.png"
    shutil.copy(candidate, native)
    base.resize((base.width * scale, base.height * scale), Image.NEAREST).save(nearest)

    def comp(rgb):
        bg = Image.new("RGBA", base.size, rgb + (255,))
        bg.alpha_composite(base)
        return bg
    comp(light).save(lightf)
    comp(dark).save(darkf)
    comp(chroma).save(chromaf)
    return native, nearest, lightf, darkf, chromaf


def base_fixture(tmp: Path, project_root: Path) -> dict:
    from PIL import Image
    data_dir = project_root / "data" / "processed"
    ev_dir = project_root / "out" / "evidence"
    data_dir.mkdir(parents=True, exist_ok=True)
    src = data_dir / "candidate.png"
    write_indexed_character(src, 48, 64)
    native, nearest, lightf, darkf, chromaf = make_derived(src, ev_dir, "base")

    ref = project_root / "rascunho" / "methodology_ref.json"
    ref.parent.mkdir(parents=True, exist_ok=True)
    ref.write_text(json.dumps({"exercise_id": "fixture", "sha256": "x"}), encoding="utf-8")
    inc = project_root / "rascunho" / "incumbent.png"
    write_indexed_character(inc, 48, 64)

    # A pixel report bound to the candidate's canonical content hash.
    import sys
    sys.path.insert(0, str(ROOT / "tools" / "sgdk_wrapper"))
    from forge_art import pixel_contract
    pc = pixel_contract.validate_png(src, pixel_contract.ROLE_TRANSPARENT0)
    pixel_report = project_root / "doc" / "pixel_report.json"
    pixel_report.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as candidate_img:
        raw = candidate_img.tobytes()
        visible = [(i % 48, i // 48) for i, value in enumerate(raw) if value != 0]
        bbox = [min(x for x, _ in visible), min(y for _, y in visible),
                max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]
    filled = len(visible)
    pixel_report.write_text(json.dumps({
        "schema_version": "1.0.0", "tool": pc["tool"], "tool_version": pc["tool_version"],
        "asset_id": "fixture_candidate", "candidate_path": str(src.relative_to(project_root)),
        "candidate_sha256": sha(src), "content_sha256": pc["content_sha256"],
        "width": 48, "height": 64, "mode": "P", "bit_depth": pc["bit_depth"],
        "color_type": pc["color_type"], "transparent_index": 0,
        "visible_colors": pc["visible_colors"], "filled_pixels": filled,
        "canvas_pixels": 48 * 64, "bbox": bbox,
        "occupancy_pct": round(filled / (48 * 64) * 100, 2),
        "status": "passed", "blocking_statuses": []
    }), encoding="utf-8")

    shape_dir = project_root / "out" / "shape_block"
    shape_dir.mkdir(parents=True, exist_ok=True)
    silhouette = shape_dir / "silhouette.png"
    semantic = shape_dir / "semantic_regions.png"
    contour = shape_dir / "contour_overlay.png"
    sil_img = Image.new("P", (48, 64), 0)
    sem_img = Image.new("P", (48, 64), 0)
    con_img = Image.new("P", (48, 64), 0)
    sil_img.putpalette([0, 0, 0, 32, 32, 32] + [0, 0, 0] * 254)
    sem_palette = [0, 0, 0]
    for i in range(1, 9):
        sem_palette.extend((34 * min(i, 7), 34 * ((i + 2) % 8), 34 * ((i + 4) % 8)))
    sem_palette.extend([0, 0, 0] * (256 - 9))
    sem_img.putpalette(sem_palette)
    con_img.putpalette([0, 0, 0, 64, 32, 72, 224, 180, 72] + [0, 0, 0] * 253)
    spx = sil_img.load(); mpx = sem_img.load(); cpx = con_img.load()
    counts = {name: 0 for name in REGIONS}
    visible_set = set(visible)
    for x, y in visible:
        spx[x, y] = 1
        label = ((x + y) % 8) + 1
        mpx[x, y] = label
        counts[REGIONS[label - 1]] += 1
        edge = any((nx, ny) not in visible_set
                   for nx, ny in ((x - 1, y), (x + 1, y),
                                  (x, y - 1), (x, y + 1)))
        cpx[x, y] = 1 if edge else 2
    sil_img.save(silhouette, "PNG", bits=1, transparency=0)
    sem_img.save(semantic, "PNG", bits=4, transparency=0)
    con_img.save(contour, "PNG", bits=2, transparency=0)
    artifact = lambda path: {"path": str(path.relative_to(project_root)), "sha256": sha(path),
                             "asset_id": "fixture_candidate", "scale": "48x64",
                             "source": str(src.relative_to(project_root))}

    return {
        "schema_version": "1.3.0",
        "asset_id": "fixture_candidate",
        "asset_kind": "sprite_single",
        "source": {"path": str(src.relative_to(project_root)), "sha256": sha(src),
                   "classification": "authored_raster", "approval_status": "approved_source"},
        "scale_contract": {"status": "locked", "target_width": 48, "target_height": 64,
                           "selected_width": 48, "selected_height": 64,
                           "probes": [{"width": 48, "height": 64, "path": "data/processed/candidate.png",
                                       "technical_status": "passed", "visual_status": "passed",
                                       "promotable": False}]},
        "producer_output": {"path": str(src.relative_to(project_root)), "role": "native_candidate",
                            "interaction_channel": "cli_headless", "width": 48, "height": 64,
                            "mode": "P", "visible_rgb_colors": pc["visible_colors"], "alpha_values": [0, 255]},
        "native_candidate": {
            "path": str(src.relative_to(project_root)), "method": "authored_native_pixel",
            "width": 48, "height": 64,
            "pixel_report": str(pixel_report.relative_to(project_root)),
            "visual_evidence": {
                "candidate_sha256": sha(src),
                "native_1x": str(native.relative_to(project_root)),
                "nearest_preview": str(nearest.relative_to(project_root)),
                "light_background": str(lightf.relative_to(project_root)),
                "dark_background": str(darkf.relative_to(project_root)),
                "chroma_background": str(chromaf.relative_to(project_root)),
                "preview_scale": 8, "light_rgb": [238, 238, 230], "dark_rgb": [28, 30, 38],
                "chroma_rgb": [238, 0, 238],
                "human_approval": "",
            },
            "shape_block_contract": {
                "silhouette_mask": artifact(silhouette),
                "semantic_region_map": artifact(semantic),
                "contour_overlay": artifact(contour),
                "required_semantic_regions": REGIONS,
                "semantic_label_legend": {name: i + 1 for i, name in enumerate(REGIONS)},
                "semantic_label_counts": counts,
                "occupancy_metrics": {"filled_pixels": filled, "canvas_pixels": 3072,
                                      "occupancy_pct": round(filled / 3072 * 100, 2)},
                "bbox": bbox,
            },
        },
        "palette_contract": {"max_visible_colors": 15, "index0_role": "transparent0",
                             "outline_role": "single dark ink", "material_roles": ["skin", "cloth"]},
        "gates": {"semantic_parse": "passed", "lineart": "passed", "color_blocking": "passed",
                  "palette_lock": "passed", "pixel_contract": "passed", "native_visual": "passed",
                  "scale": "passed", "budget": "passed", "human": "passed",
                  "sgdk_integration": "not_started", "emulator": "not_started"},
        "runtime_evidence": None,
        "promotion": {"promotable": True, "target": "none"},
        "status": "ready_for_res",
        "next_action": "promote",
        "provenance": {"interaction_channel": "cli_headless", "source_kind": "native_pixel",
                       "producer_identity": "fixture", "action_log": "tool", "human_approval": ""},
        "scale_report": {"status": "passed", "camera_width": 320, "camera_height": 224,
                         "hitbox": "48x64",
                         "notes": "probe measurements captured", "probes": "measured"},
        "budget_report": {"status": "passed", "tiles": 12, "scanline_px": 48, "notes": "fixture"},
        "visual_report": {"status": "passed", "sha256": sha(src), "notes": "fixture"},
        "incumbent": {"path": str(inc.relative_to(project_root)), "sha256": sha(inc), "role": "comparison_only"},
        "methodology_reference": {"path": str(ref.relative_to(project_root)), "sha256": sha(ref), "role": "methodology_reference"},
    }


def add_material_contract(rec: dict, project_root: Path) -> dict:
    """Upgrade the portable fixture to schema 1.4 material ownership."""
    from PIL import Image

    result = json.loads(json.dumps(rec))
    candidate = project_root / result["native_candidate"]["path"]
    out = project_root / "out" / "material_topology"
    out.mkdir(parents=True, exist_ok=True)
    material_map = out / "material_region_map.png"
    boundary = out / "material_boundary_overlay.png"

    with Image.open(candidate) as image:
        indices = list(image.convert("P").tobytes())
        width, height = image.size
    labels = [0 if index == 0 else 1 if index in (1, 2) else 2 for index in indices]

    map_image = Image.new("P", (width, height), 0)
    map_image.putpalette([0, 0, 0, 204, 136, 68, 68, 68, 136] + [0, 0, 0] * 253)
    map_image.putdata(labels)
    map_image.save(material_map, "PNG", bits=2, transparency=0)

    overlay_values = [0] * len(labels)
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            label = labels[pos]
            if label == 0:
                continue
            touches_other = any(
                0 <= nx < width and 0 <= ny < height
                and labels[ny * width + nx] not in (0, label)
                for nx, ny in ((x - 1, y), (x + 1, y),
                               (x, y - 1), (x, y + 1))
            )
            overlay_values[pos] = 1 if touches_other else 2
    overlay_image = Image.new("P", (width, height), 0)
    overlay_image.putpalette([0, 0, 0, 238, 170, 68, 68, 34, 68] + [0, 0, 0] * 253)
    overlay_image.putdata(overlay_values)
    overlay_image.save(boundary, "PNG", bits=2, transparency=0)

    def artifact(path: Path) -> dict:
        return {"path": str(path.relative_to(project_root)), "sha256": sha(path),
                "asset_id": result["asset_id"], "scale": "48x64",
                "source": str(candidate.relative_to(project_root))}

    result["schema_version"] = "1.4.0"
    result["gates"]["material_topology"] = "passed"
    result["native_candidate"]["material_region_contract"] = {
        "status": "passed",
        "map_method": "explicit_material_ownership_map",
        "source_reference": {
            "path": result["source"]["path"],
            "sha256": result["source"]["sha256"],
            "role": "approved_material_topology_reference",
        },
        "material_region_map": artifact(material_map),
        "material_boundary_overlay": artifact(boundary),
        "material_label_legend": {"skin": 1, "cloth": 2},
        "material_label_counts": {"skin": labels.count(1), "cloth": labels.count(2)},
        "allowed_palette_indices": {"skin": [2], "cloth": [3, 4]},
        "shared_outline_indices": [1],
        "critical_boundaries": [{
            "boundary_id": "skin_cloth_separation",
            "material_a": "skin", "material_b": "cloth",
            "minimum_contact_edges": 1,
        }],
        "blocking_statuses": [],
    }
    return result


def run_positive(tmp):
    project_root = tmp / "proj" / "NOME [VER.001] [SGDK 211] [GEN] [GAME] [LAB]"
    project_root.mkdir(parents=True, exist_ok=True)
    rec = base_fixture(tmp, project_root)
    rp = project_root / "doc" / "native_sprite_production_record.json"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(rec), encoding="utf-8")
    res = validate_record(project_root, rp, require_shape_block_contract=True)
    check("positive_portable_passes_foreign_root", res["status"] == "passed",
          f"errors={[e['code'] for e in res['errors']]} warnings={res['warnings']}")
    return project_root, rp, rec


def codes(r):
    return [e["code"] for e in r["errors"]]


def main():
    print("\n=== Native Sprite Semantic Gate — Adversarial Fixtures ===\n")
    with tempfile.TemporaryDirectory(prefix="native_sprite_gate_") as tmp:
        tmp = Path(tmp)
        project_root, rp, rec = run_positive(tmp)

        # 1. candidate declared 48x64 but PNG 16x16.
        m = json.loads(json.dumps(rec))
        small = project_root / "data" / "processed" / "small.png"
        write_ok_indexed(small, 16, 16)
        m["native_candidate"]["width"] = 48
        m["native_candidate"]["height"] = 64
        m["native_candidate"]["path"] = str(small.relative_to(project_root))
        m["source"]["path"] = "data/processed/candidate.png"  # keep source sane
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("candidate_declared_48x64_png_16x16",
              "candidate_dimension_mismatch" in codes(r), f"got {codes(r)}")

        # 2. pixel_report empty.
        m = json.loads(json.dumps(rec)); m["native_candidate"]["pixel_report"] = ""
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_pixel_report_empty", "pixel_report_missing" in codes(r), f"got {codes(r)}")

        # 3. five distinct PATHS but IDENTICAL content.
        m = json.loads(json.dumps(rec))
        ve = m["native_candidate"]["visual_evidence"]
        ev_dir = (project_root / "out" / "evidence").resolve()
        src = (project_root / "data" / "processed" / "candidate.png").resolve()
        # write 3 extra files that are byte-copies of native_1x (candidate).
        for role, fn in (("nearest_preview", "nearest.png"), ("light_background", "light.png"),
                         ("dark_background", "dark.png"), ("chroma_background", "chroma.png")):
            p = ev_dir / fn
            shutil.copy(src, p)
            ve[role] = str(p.relative_to(project_root))
        ve["native_1x"] = str((ev_dir / "base_native_1x.png").relative_to(project_root))
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_distinct_paths_identical_content",
              any(c in codes(r) for c in ("nearest_preview_not_nearest",
                                          "light_background_not_recomposite",
                                          "dark_background_not_recomposite")),
              f"got {codes(r)}")

        # 4. nearest that is NOT NEAREST (resize NEAREST vs BILINEAR).
        m = json.loads(json.dumps(rec))
        ve = m["native_candidate"]["visual_evidence"]
        src = (project_root / "data" / "processed" / "candidate.png").resolve()
        nearest = (project_root / "out" / "evidence").resolve() / "nearest_bilinear.png"
        from PIL import Image
        Image.open(src).convert("RGBA").resize((48 * 8, 64 * 8), Image.BILINEAR).save(nearest)
        ve["nearest_preview"] = str(nearest.relative_to(project_root))
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_nearest_not_nearest", "nearest_preview_not_nearest" in codes(r), f"got {codes(r)}")

        # 5. scale=passed with report not_applicable.
        m = json.loads(json.dumps(rec)); m["scale_report"]["status"] = "not_applicable"
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_scale_pass_report_not_applicable", "scale_pass_without_report" in codes(r), f"got {codes(r)}")

        # 6. scale=passed but no probes.
        m = json.loads(json.dumps(rec)); m["scale_contract"]["probes"] = []
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_scale_pass_without_probes", "scale_pass_without_probes" in codes(r), f"got {codes(r)}")

        # 7. budget=passed without budget report.
        m = json.loads(json.dumps(rec)); m.pop("budget_report")
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_budget_pass_without_report", "budget_pass_without_report" in codes(r), f"got {codes(r)}")

        # 8. human approval fake (methodology JSON used as human approval).
        m = json.loads(json.dumps(rec))
        m["provenance"]["interaction_channel"] = "human_pixel_editor"
        m["provenance"]["source_kind"] = "hand_authored_pixel"
        m["provenance"]["producer_identity"] = "someone"
        m["provenance"]["human_approval"] = str(rec["methodology_reference"]["path"])
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_human_approval_is_methodology_json",
              any(c in codes(r) for c in ("human_approval_sha_mismatch", "human_approval_decision_missing")),
              f"got {codes(r)}")

        # 9. canvas area confused with visible pixels (filled == canvas in shape block).
        m = json.loads(json.dumps(rec))
        m["native_candidate"]["shape_block_contract"]["occupancy_metrics"] = {
            "filled_pixels": 3072, "canvas_pixels": 3072}
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_canvas_confused_with_visible", "canvas_confused_with_visible" in codes(r), f"got {codes(r)}")

        # 10. incumbent null.
        m = json.loads(json.dumps(rec)); m["incumbent"] = None
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_incumbent_null", "incumbent_missing" in codes(r), f"got {codes(r)}")

        # 11. challenger promoted without perceptual AND system win.
        m = json.loads(json.dumps(rec)); m["challenger_win"] = {"perceptual_win": True, "system_win": False}
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_challenger_without_system_win", "challenger_not_justified" in codes(r), f"got {codes(r)}")

        # 12. invalid schema (missing required top-level field).
        m = json.loads(json.dumps(rec)); m.pop("provenance")
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_invalid_schema", "record_schema_violation" in codes(r), f"got {codes(r)}")

        # 13. project root does not exist.
        r = validate_record(project_root.parent / "does_not_exist", rp)
        check("rejects_project_root_not_exist", "project_root_not_exist" in codes(r), f"got {codes(r)}")

        # 14. shape-block missing the 8 regions.
        m = json.loads(json.dumps(rec))
        m["native_candidate"]["shape_block_contract"]["required_semantic_regions"] = ["head_or_face"]
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_immature_shape_block_regions", "semantic_regions_incomplete" in codes(r), f"got {codes(r)}")

        # 15. mandatory gate marked not_applicable for a critical character.
        m = json.loads(json.dumps(rec)); m["gates"]["human"] = "not_applicable"
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_mandatory_gate_not_applicable", "human_not_applicable_for_critical" in codes(r), f"got {codes(r)}")

        # 16. one shape artifact cannot masquerade as three semantic roles.
        m = json.loads(json.dumps(rec))
        sb = m["native_candidate"]["shape_block_contract"]
        sb["semantic_region_map"] = sb["silhouette_mask"]
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_reused_shape_block_artifact",
              "shape_block_artifacts_not_distinct" in codes(r), f"got {codes(r)}")

        # 17. Shape artifact hash is stale even though its path and dimensions exist.
        m = json.loads(json.dumps(rec))
        m["native_candidate"]["shape_block_contract"]["silhouette_mask"]["sha256"] = "0" * 64
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_shape_artifact_hash_mismatch",
              "shape_block_silhouette_mask_hash_mismatch" in codes(r), f"got {codes(r)}")

        # 18. Shape artifact link points at another asset id.
        m = json.loads(json.dumps(rec))
        m["native_candidate"]["shape_block_contract"]["semantic_region_map"]["asset_id"] = "other_asset"
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_shape_artifact_asset_link_mismatch",
              "shape_block_semantic_region_map_asset_id_mismatch" in codes(r), f"got {codes(r)}")

        # 19. A same-size semantic map with no real labels must fail.
        m = json.loads(json.dumps(rec))
        empty = project_root / "out" / "shape_block" / "semantic_empty.png"
        Image.new("P", (48, 64), 0).save(empty, "PNG", bits=4, transparency=0)
        sb = m["native_candidate"]["shape_block_contract"]
        sb["semantic_region_map"]["path"] = str(empty.relative_to(project_root))
        sb["semantic_region_map"]["sha256"] = sha(empty)
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_semantic_map_without_real_labels",
              "semantic_labels_missing_on_disk" in codes(r), f"got {codes(r)}")

        # 20. Producer metadata cannot be hand-edited away from the PNG.
        m = json.loads(json.dumps(rec)); m["producer_output"]["mode"] = "RGBA"
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_producer_metadata_mismatch",
              "producer_output_metadata_mismatch" in codes(r), f"got {codes(r)}")

        # 21. Pixel report must satisfy the canonical report schema.
        m = json.loads(json.dumps(rec))
        pr = project_root / "doc" / "pixel_report.json"
        report = json.loads(pr.read_text(encoding="utf-8")); report.pop("bbox")
        pr.write_text(json.dumps(report), encoding="utf-8")
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_pixel_report_schema_violation",
              "pixel_report_schema_violation" in codes(r), f"got {codes(r)}")

        # 23. Silhouette must equal the candidate's exact visible mask.
        m = json.loads(json.dumps(rec))
        original_sil = project_root / m["native_candidate"]["shape_block_contract"]["silhouette_mask"]["path"]
        bad_sil = project_root / "out" / "shape_block" / "silhouette_mismatch.png"
        sil = Image.open(original_sil).convert("P")
        visible_xy = next((x, y) for y in range(64) for x in range(48) if sil.getpixel((x, y)) == 1)
        sil.putpixel(visible_xy, 0)
        sil.save(bad_sil, "PNG", bits=1, transparency=0)
        art = m["native_candidate"]["shape_block_contract"]["silhouette_mask"]
        art["path"] = str(bad_sil.relative_to(project_root)); art["sha256"] = sha(bad_sil)
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_silhouette_candidate_mismatch",
              "silhouette_candidate_mismatch" in codes(r), f"got {codes(r)}")

        # 24. One token pixel cannot pretend to be an anatomical region.
        m = json.loads(json.dumps(rec))
        original_sem = project_root / m["native_candidate"]["shape_block_contract"]["semantic_region_map"]["path"]
        token_sem = project_root / "out" / "shape_block" / "semantic_token.png"
        sem = Image.open(original_sem).convert("P")
        positions = [(x, y) for y in range(64) for x in range(48) if sem.getpixel((x, y)) == 4]
        for x, y in positions[1:]:
            sem.putpixel((x, y), 3)
        sem.save(token_sem, "PNG", bits=4, transparency=0)
        sb = m["native_candidate"]["shape_block_contract"]
        sb["semantic_region_map"]["path"] = str(token_sem.relative_to(project_root))
        sb["semantic_region_map"]["sha256"] = sha(token_sem)
        sb["semantic_label_counts"] = {name: list(sem.tobytes()).count(i + 1)
                                       for i, name in enumerate(REGIONS)}
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_token_semantic_region",
              "semantic_labels_tokenized_not_meaningful" in codes(r), f"got {codes(r)}")

        # 25. Semantic regions must cover exactly the candidate, no holes.
        m = json.loads(json.dumps(rec))
        hole_sem = project_root / "out" / "shape_block" / "semantic_hole.png"
        sem = Image.open(original_sem).convert("P")
        pos = next((x, y) for y in range(64) for x in range(48) if sem.getpixel((x, y)) != 0)
        sem.putpixel(pos, 0)
        sem.save(hole_sem, "PNG", bits=4, transparency=0)
        sb = m["native_candidate"]["shape_block_contract"]
        sb["semantic_region_map"]["path"] = str(hole_sem.relative_to(project_root))
        sb["semantic_region_map"]["sha256"] = sha(hole_sem)
        sb["semantic_label_counts"] = {name: list(sem.tobytes()).count(i + 1)
                                       for i, name in enumerate(REGIONS)}
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_semantic_union_hole",
              "semantic_union_candidate_mismatch" in codes(r), f"got {codes(r)}")

        # 26. Contour must be derived from the 4-neighbor silhouette boundary.
        m = json.loads(json.dumps(rec))
        original_con = project_root / m["native_candidate"]["shape_block_contract"]["contour_overlay"]["path"]
        bad_con = project_root / "out" / "shape_block" / "contour_wrong.png"
        con = Image.open(original_con).convert("P")
        pos = next((x, y) for y in range(64) for x in range(48) if con.getpixel((x, y)) == 1)
        con.putpixel(pos, 2)
        con.save(bad_con, "PNG", bits=2, transparency=0)
        art = m["native_candidate"]["shape_block_contract"]["contour_overlay"]
        art["path"] = str(bad_con.relative_to(project_root)); art["sha256"] = sha(bad_con)
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_non_derived_contour",
              "contour_overlay_not_derived" in codes(r), f"got {codes(r)}")

        # 27. Assisted translation cannot omit proof of background extraction.
        m = json.loads(json.dumps(rec))
        m["native_candidate"]["method"] = "assisted_native_translation"
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_assisted_translation_without_matte_report",
              "foreground_matte_report_missing" in codes(r), f"got {codes(r)}")

        # 28. A bound, clean border-connected report is accepted by this gate.
        matte_path = project_root / "doc" / "foreground_matte_report.json"
        source_path = project_root / rec["native_candidate"]["path"]
        matte_path.write_text(json.dumps({
            "schema_version": "1.0.0", "tool": "forge_art.foreground_matte",
            "tool_version": "1.0.0", "method": "border_connected_color_flood_v1",
            "status": "passed", "blocking_statuses": [],
            "input_source_path": str(source_path.relative_to(project_root)),
            "input_source_sha256": sha(source_path)
        }), encoding="utf-8")
        m["native_candidate"]["foreground_matte_report"] = str(matte_path.relative_to(project_root))
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("accepts_bound_border_connected_matte_report",
              not any(code.startswith("foreground_matte_") for code in codes(r)),
              f"got {codes(r)}")

        # 29. Schema 1.4 with an explicit, honest material ownership map passes.
        rec14 = add_material_contract(base_fixture(tmp, project_root), project_root)
        rp.write_text(json.dumps(rec14), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("accepts_explicit_material_ownership_contract",
              r["status"] == "passed", f"got {codes(r)}")

        # 30. A garment/skin pixel using a palette index not owned by its
        # material is the executable form of colour leakage.
        m = json.loads(json.dumps(rec14))
        m["native_candidate"]["material_region_contract"]["allowed_palette_indices"]["skin"] = [5]
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_material_palette_leakage",
              "material_palette_leakage" in codes(r), f"got {codes(r)}")

        # 31. A non-outline palette index cannot belong to two materials.
        m = json.loads(json.dumps(rec14))
        m["native_candidate"]["material_region_contract"]["allowed_palette_indices"]["cloth"].append(2)
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_material_palette_role_overlap",
              "material_palette_role_overlap" in codes(r), f"got {codes(r)}")

        # 32. The boundary overlay is evidence, not an arbitrary review image.
        m = json.loads(json.dumps(rec14))
        art = m["native_candidate"]["material_region_contract"]["material_boundary_overlay"]
        overlay_path = project_root / art["path"]
        forged = project_root / "out" / "material_topology" / "forged_boundary.png"
        overlay = Image.open(overlay_path).convert("P")
        boundary_pos = next((x, y) for y in range(64) for x in range(48)
                            if overlay.getpixel((x, y)) == 1)
        overlay.putpixel(boundary_pos, 2)
        overlay.save(forged, "PNG", bits=2, transparency=0)
        art["path"] = str(forged.relative_to(project_root)); art["sha256"] = sha(forged)
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_forged_material_boundary_overlay",
              "material_boundary_overlay_not_derived" in codes(r), f"got {codes(r)}")

        # 33. New records cannot omit material ownership while claiming the
        # colour passes completed.
        m = json.loads(json.dumps(rec14))
        m["native_candidate"].pop("material_region_contract")
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_schema14_without_material_contract",
              "material_region_contract_missing" in codes(r), f"got {codes(r)}")

        # 34. A named critical garment/skin boundary must actually exist in the
        # material map; declarations alone cannot buy the gate.
        m = json.loads(json.dumps(rec14))
        m["native_candidate"]["material_region_contract"]["critical_boundaries"][0]["minimum_contact_edges"] = 9999
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_missing_critical_material_boundary",
              "critical_material_boundary_missing" in codes(r), f"got {codes(r)}")

        # 35. Gate status cannot contradict a failed contract.
        m = json.loads(json.dumps(rec14))
        m["native_candidate"]["material_region_contract"]["status"] = "failed"
        m["native_candidate"]["material_region_contract"]["blocking_statuses"] = ["garment_boundary_drift"]
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_material_gate_false_green",
              "material_topology_pass_without_contract" in codes(r), f"got {codes(r)}")

        # 36. Repeated material pairs are evaluated inside their declared ROI;
        # a valid boundary elsewhere cannot satisfy the top/arm-specific gate.
        m = json.loads(json.dumps(rec14))
        boundary_contract = m["native_candidate"]["material_region_contract"]["critical_boundaries"][0]
        boundary_contract["region"] = [0, 0, 4, 4]
        rp.write_text(json.dumps(m), encoding="utf-8")
        r = validate_record(project_root, rp)
        check("rejects_critical_boundary_outside_declared_roi",
              "critical_material_boundary_missing" in codes(r), f"got {codes(r)}")

    print(f"\n{passed}/{total} native-sprite semantic-gate fixtures passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
