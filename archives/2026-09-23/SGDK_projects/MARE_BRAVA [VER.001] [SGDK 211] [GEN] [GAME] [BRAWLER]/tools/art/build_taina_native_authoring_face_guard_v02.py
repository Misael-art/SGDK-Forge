#!/usr/bin/env python3
"""Build one new TAINA native-authoring candidate from the human-approved A source.

The generated high-resolution authoring source is the only visual input.  The
previous native candidate and rejected assets are read only as controls for
geometry comparison.  All final pixels remain in staging.
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
OUT = PROJECT / "rascunho/taina_native_authoring_face_guard_v02"
APPROVED_SOURCE = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/source/face_and_guard_topology_visual_source_v01.png"
SOURCE = OUT / "source/face_and_guard_topology_native_authoring_source_v02.png"
APPROVED_SOURCE_SHA = "b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
CONTROL_A = PROJECT / "rascunho/taina_native_geometry_challengers_v01/face_and_guard_topology/taina_48x64_geometry_face_guard_v01.png"
CONTROL_A_SHA = "1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830"
CONTROL_B = PROJECT / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b/taina_48x64_challenger_b.png"
CONTROL_B_SHA = "d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa"
CONTROL_ELITE = PROJECT / "rascunho/taina_native_refinement_v01/taina_48x64_refined_elite_v01.png"
CONTROL_ELITE_SHA = "0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13"
ASSET_ID = "taina_48x64_native_authoring_face_guard_v02"

sys.path.insert(0, str(PROJECT / "tools/art"))
builder_path = PROJECT / "tools/art/build_taina_native_geometry_challengers_v01.py"
spec = importlib.util.spec_from_file_location("geometry_builder", builder_path)
assert spec and spec.loader
geometry_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry_builder)

sys.path.insert(0, str(WORKSPACE / "tools/sgdk_wrapper"))
from forge_art import pixel_contract  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE).as_posix()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mask(path: Path) -> set[tuple[int, int]]:
    image = Image.open(path).convert("P")
    return {(x, y) for y in range(64) for x in range(48) if image.getpixel((x, y)) != 0}


def compare_control(candidate: Path, control: Path, expected: str) -> dict[str, object]:
    actual = sha(control)
    if actual != expected:
        raise RuntimeError(f"control hash mismatch: {control}: {actual}")
    current, other = mask(candidate), mask(control)
    return {"control_sha256": expected, "changed_mask_pixels": len(current ^ other),
            "intersection_pixels": len(current & other), "candidate_only_pixels": len(current - other),
            "control_only_pixels": len(other - current)}


def authoring_panel(candidate: Path, source: Path, control: Path) -> Path:
    suffix = ASSET_ID[-3:]
    panel = OUT / f"taina_native_authoring_face_guard_review_panel_{suffix}.png"
    panel.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (960, 420), (30, 32, 44))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 14)
    bold = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Bold.ttf", 18)
    entries = [(f"SOURCE {suffix}", Image.open(source).convert("RGB")),
               (f"NATIVE {suffix}", Image.open(candidate).convert("RGBA")),
               ("CONTROL A", Image.open(control).convert("RGBA"))]
    for i, (label, image) in enumerate(entries):
        x = 20 + i * 315
        draw.text((x, 12), label, fill=(238, 238, 230), font=bold)
        if i == 0:
            preview = image.copy()
            preview.thumbnail((280, 350), Image.Resampling.NEAREST)
            px = x + (280 - preview.width) // 2
            py = 48 + (350 - preview.height) // 2
            canvas.paste(preview, (px, py))
        else:
            preview = image.resize((240, 320), Image.Resampling.NEAREST)
            rgba = preview.convert("RGBA")
            matte = Image.new("RGB", rgba.size, (238, 238, 230))
            matte.paste(rgba, mask=rgba.getchannel("A"))
            canvas.paste(matte, (x + 28, 48))
        draw.text((x, 382), "48x64 target / staging only", fill=(182, 190, 198), font=font)
    canvas.save(panel)
    return panel


def main() -> int:
    if sha(APPROVED_SOURCE) != APPROVED_SOURCE_SHA:
        raise SystemExit("approved source hash mismatch")
    candidate = OUT / f"{ASSET_ID}.png"
    version_tag = ASSET_ID.rsplit("_v", 1)[-1]
    validation_path = OUT / f"native_authoring_validation_report_v{version_tag}.json"
    manifest_path = OUT / f"native_authoring_manifest_v{version_tag}.json"
    native, matte = geometry_builder.fit_native(SOURCE)
    native.save(candidate, "PNG", bits=4, transparency=0)
    compliance = pixel_contract.validate_png(candidate, pixel_contract.ROLE_TRANSPARENT0)
    if compliance["blocking"]:
        raise SystemExit(f"pixel contract failed: {compliance}")
    image = Image.open(candidate).convert("P")
    visible = sorted({value for value in image.getdata() if value})
    palette_roles = [{"index": i + 1, "role": role, "rgb": list(rgb)}
                     for i, (role, rgb) in enumerate(geometry_builder.PALETTE) if i + 1 in visible]
    write_json(OUT / "foreground_matte_report.json", {**matte, "input_source_path": rel(SOURCE),
        "input_source_sha256": sha(SOURCE), "candidate_sha256": sha(candidate),
        "alpha_contract": "binary_index0_transparent", "blockers": []})
    write_json(OUT / "pixel_compliance_report.json", {"schema_version": "1.0.0", "asset_id": ASSET_ID,
        "candidate_sha256": sha(candidate), "tool": compliance["tool"],
        "tool_version": compliance["tool_version"], "status": compliance["status"],
        "blocking_statuses": compliance.get("blocking_statuses", []), "width": 48, "height": 64,
        "visible_colors": len(visible), "transparent_index": 0,
        "translation": "new_material_native_geometry_authoring_from_approved_source_plus_fixed_role_map"})
    write_json(OUT / "palette_role_map.json", {"schema_version": "1.0.0", "asset_id": ASSET_ID,
        "index0": {"index": 0, "role": "transparent0"}, "visible_roles": palette_roles,
        "alias_check": "unique_rgb_per_visible_index", "source": "fixed_material_palette"})
    evidence = geometry_builder.evidence(candidate, OUT)
    shape = geometry_builder.shape_block(candidate, OUT, ASSET_ID)
    tile_metrics = geometry_builder.tile_metrics(image)
    controls = {"face_guard_control": compare_control(candidate, CONTROL_A, CONTROL_A_SHA),
                "challenger_b_control": compare_control(candidate, CONTROL_B, CONTROL_B_SHA),
                "elite_control": compare_control(candidate, CONTROL_ELITE, CONTROL_ELITE_SHA)}
    budget = geometry_builder.budget(ASSET_ID, sha(candidate))
    panel = authoring_panel(candidate, SOURCE, CONTROL_A)
    validation = {"status": "passed", "errors": [], "asset_id": ASSET_ID,
        "candidate_sha256": sha(candidate), "source_sha256": sha(SOURCE),
        "approved_visual_source_sha256": APPROVED_SOURCE_SHA, "authoring_source_sha256": sha(SOURCE),
        "model_sheet_sha256": MODEL_SHA,
        "scale": "48x64", "comparison_only": ["64x96"], "visible_colors": len(visible),
        "tile_metrics": tile_metrics,
        "pixel_contract": compliance, "shape_block": shape, "controls": controls,
        "budget": budget, "evidence": evidence, "review_panel": rel(panel),
        "res_promotion": False, "animation_authorization": False,
        "final_pose_approval": False, "contamination": {"data_changed": False,
            "res_changed": False, "staging_only": True}}
    write_json(validation_path, validation)
    manifest = {"schema_version": "1.0.0", "status": "pending_human_decision",
        "round": f"native_authoring_face_guard_v{version_tag}", "asset_id": ASSET_ID,
        "scale_contract": {"status": "locked", "selected": "48x64", "comparison_only": ["64x96"]},
        "identity_source": {"path": rel(PROJECT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"),
            "sha256": MODEL_SHA, "role": "approved_model_sheet_visual_source_of_truth"},
        "approved_visual_source": {"path": rel(APPROVED_SOURCE), "sha256": APPROVED_SOURCE_SHA,
            "asset_id": "face_and_guard_topology_visual_source_v01", "role": "approved_as_visual_source_for_native_authoring",
            "human_decision": "doc/art/characters/taina/human_source_authoring_approval_v01.json"},
        "authoring_source_output": {"path": rel(SOURCE), "sha256": sha(SOURCE),
            "role": "new_visual_authoring_output_derived_from_approved_source"},
        "forbidden_pixel_sources": ["taina_48x64_geometry_face_guard_v01", "challenger_b", "rejected_basic", "rejected_elite"],
        "candidate": {"path": rel(candidate), "sha256": sha(candidate), "role": "new_native_authoring_candidate",
            "method": "material_native_geometry_authoring_from_approved_visual_source", "not_a_requantization_of_control": True},
        "tile_metrics": tile_metrics,
        "reports": {"validation": rel(validation_path),
            "matte": rel(OUT / "foreground_matte_report.json"), "pixel": rel(OUT / "pixel_compliance_report.json"),
            "palette": rel(OUT / "palette_role_map.json"), "review_panel": rel(panel)},
        "controls": {"face_guard_v01": {"path": rel(CONTROL_A), "sha256": CONTROL_A_SHA, "role": "technical_control_only"},
            "challenger_b": {"path": rel(CONTROL_B), "sha256": CONTROL_B_SHA, "role": "comparison_only"},
            "elite": {"path": rel(CONTROL_ELITE), "sha256": CONTROL_ELITE_SHA, "role": "comparison_only"}},
        "budget": budget, "decision_required": "approved_for_final_native_pose with exact asset_id, SHA-256 and scale=48x64",
        "res_promotion": False, "animation_authorization": False, "visual_pass": False,
        "promotable": False, "ready_for_aaa": False}
    write_json(manifest_path, manifest)
    print(json.dumps({"status": "passed", "candidate": rel(candidate), "sha256": sha(candidate),
                      "panel": rel(panel), "visible_colors": len(visible), "controls": controls}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
