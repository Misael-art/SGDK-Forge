#!/usr/bin/env python3
"""Adversarial gate for native lineart blocking challengers.

The fixtures assert semantic claims and provenance. They deliberately do not
assign an aesthetic score and never treat a technical counter as visual pass.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

W, H = 56, 80
LAB = Path(__file__).resolve().parent.parent
STAGE = LAB / "native_lineart_blocking_v03"
MANIFEST = STAGE / "native_lineart_blocking_manifest_v01.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_semantic_flattening(case: dict) -> bool:
    return case["acceptance_status"] != "visual_challenger" and case["internal_drawing_preserved"] is False


def reject_nonindependent_owner_annotation(case: dict) -> bool:
    return case["source_classification"] != "independent_artistic_segmentation"


def reject_near_duplicate(case: dict) -> bool:
    return case["difference_ratio"] < 0.02 or len(case["affected_regions"]) < 3


def reject_lineart_loss(case: dict) -> bool:
    return not all(case["features"].values())


def reject_gate_without_alternatives(case: dict) -> bool:
    return not case["meaningful_visual_alternatives"]


def technical_report(manifest: dict) -> dict:
    candidates = {}
    for code, entry in manifest["candidates"].items():
        png = Path(entry["path"])
        with Image.open(png) as im:
            indexed = im.convert("P")
            values = list(indexed.getdata())
            palette = im.getpalette() or []
            alpha = im.info.get("transparency")
            candidates[code] = {
                "asset_id": entry["asset_id"],
                "path": str(png),
                "sha256": sha(png),
                "sha_matches_manifest": sha(png) == entry["sha256"],
                "size": list(im.size),
                "mode": im.mode,
                "bit_depth": im.info.get("bits", 4),
                "index0_transparent": alpha == 0,
                "visible_indices": sorted(set(v for v in values if v != 0)),
                "palette_entries": len(palette) // 3,
                "grid_8x8": im.size[0] % 8 == 0 and im.size[1] % 8 == 0,
                "report_has_identity_gate": bool(entry.get("identity_report")),
            }
    return candidates


def make_delta(manifest: dict) -> str:
    a_path = Path(manifest["candidates"]["A"]["path"])
    b_path = Path(manifest["candidates"]["B"]["path"])
    with Image.open(a_path) as a, Image.open(b_path) as b:
        ap = list(a.convert("P").getdata())
        bp = list(b.convert("P").getdata())
        delta = Image.new("RGB", (W, H), (8, 8, 12))
        pixels = []
        for x, y in ((i % W, i // W) for i in range(W * H)):
            if ap[y * W + x] != 0 or bp[y * W + x] != 0:
                pixels.append((x, y, (240, 64, 160) if ap[y * W + x] != bp[y * W + x] else (92, 92, 104)))
        for x, y, color in pixels:
            delta.putpixel((x, y), color)
        out = STAGE / "delta_overlay_a_vs_b.png"
        delta.resize((W * 8, H * 8), Image.Resampling.NEAREST).save(out)
    return str(out)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    technical = technical_report(manifest)
    for code, result in technical.items():
        assert result["sha_matches_manifest"]
        assert result["size"] == [W, H]
        assert result["mode"] == "P"
        assert result["index0_transparent"]
        assert len(result["visible_indices"]) <= 15
        assert result["grid_8x8"]

    fixtures = [
        ("rejects_semantic_flattening_as_visual_challenger", reject_semantic_flattening, {"acceptance_status": "visual_lab_control", "internal_drawing_preserved": False}),
        ("rejects_nonindependent_owner_annotation", reject_nonindependent_owner_annotation, {"source_classification": "derived_diagnostic_annotation_from_legacy_seed"}),
        ("rejects_near_duplicate_challengers", reject_near_duplicate, {"difference_ratio": 0.001, "affected_regions": ["face", "hair"]}),
        ("rejects_lineart_loss", reject_lineart_loss, {"features": {"eye_and_gaze": False, "hair_face_separation": True}}),
        ("rejects_human_gate_without_meaningful_visual_alternatives", reject_gate_without_alternatives, {"meaningful_visual_alternatives": False}),
    ]
    fixture_results = []
    for name, fn, case in fixtures:
        result = bool(fn(case))
        assert result, name
        fixture_results.append({"name": name, "result": "passed"})

    report = {
        "schema_version": "taina_native_lineart_gate.v1",
        "stage": manifest["stage"],
        "human_visual_gate": manifest["human_gate_status"],
        "technical_candidates": technical,
        "comparison": manifest["comparison"],
        "adversarial_fixtures": fixture_results,
        "fixture_summary": {"passed": len(fixture_results), "total": len(fixture_results)},
        "delta_overlay": make_delta(manifest),
        "visual_decision": "pending_human_decision",
        "visual_pass": False,
        "promotable": False,
        "res_promotion": False,
        "animation_authorization": False,
        "rom_authorization": False,
        "ready_for_aaa": False,
    }
    out = STAGE / "native_lineart_validation_report_v01.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "native_lineart_gate_checked", "report": str(out), "fixtures": report["fixture_summary"], "delta_overlay": report["delta_overlay"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
