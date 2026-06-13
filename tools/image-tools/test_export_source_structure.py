#!/usr/bin/env python3
"""
Testes sinteticos do export_source_structure.py.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from export_source_structure import export_structure  # noqa: E402
from infer_source_structure import save_json  # noqa: E402

PASSED = 0
FAILED = 0


def ok(label: str) -> None:
    global PASSED
    PASSED += 1
    print(f"[PASS] {label}")


def fail(label: str, detail: str) -> None:
    global FAILED
    FAILED += 1
    print(f"[FAIL] {label} - {detail}")


def assert_true(label: str, condition: bool, detail: str) -> None:
    if condition:
        ok(label)
    else:
        fail(label, detail)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="md_export_structure_") as temp_dir:
        root = Path(temp_dir)
        source_path = root / "source.png"
        image = Image.new("RGBA", (320, 224), (136, 136, 224, 255))
        pixels = image.load()
        for y in range(10, 80):
            for x in range(20, 280):
                pixels[x, y] = (160, 120, 80, 255)
        for y in range(85, 120):
            for x in range(20, 300):
                pixels[x, y] = (210, 210, 220, 255)
        for y in range(125, 170):
            for x in range(20, 300):
                pixels[x, y] = (96, 192, 255, 255)
        image.save(source_path)

        derived_ir = {
            "case_id": "synthetic_export_case",
            "source_image": str(source_path),
            "layout_type": "stage_board",
            "background_key_color": [136, 136, 224],
            "shared_canvas": {"width": 320, "height": 224, "space": "source_canvas"},
            "regions": [
                {
                    "id": "sky_strip",
                    "bbox": [20, 125, 300, 170],
                    "action": "keep",
                    "classification": "scene_plane_sky",
                    "system_role": "scene_layer",
                    "candidate_asset_kind": "scene_layer",
                    "compositional_role": "scene_plane_bg_b",
                    "engine_affordance": "scene_layer_continuous",
                    "confidence_bbox": 0.9,
                    "confidence_classification": 0.9,
                    "confidence_composition": 0.9,
                    "confidence_engine_affordance": 0.9,
                    "review_required": False,
                },
                {
                    "id": "architecture_panel",
                    "bbox": [20, 10, 280, 80],
                    "action": "keep",
                    "classification": "scene_plane_architecture",
                    "system_role": "scene_layer",
                    "candidate_asset_kind": "scene_layer",
                    "compositional_role": "scene_plane_bg_a",
                    "engine_affordance": "scene_layer_continuous",
                    "confidence_bbox": 0.9,
                    "confidence_classification": 0.9,
                    "confidence_composition": 0.9,
                    "confidence_engine_affordance": 0.9,
                    "review_required": False,
                },
                {
                    "id": "ground_perspective_strip",
                    "bbox": [20, 85, 300, 120],
                    "action": "keep",
                    "classification": "scene_plane_ground",
                    "system_role": "scene_layer",
                    "candidate_asset_kind": "scene_layer",
                    "compositional_role": "scene_plane_bg_a",
                    "engine_affordance": "scene_layer_continuous",
                    "confidence_bbox": 0.9,
                    "confidence_classification": 0.9,
                    "confidence_composition": 0.9,
                    "confidence_engine_affordance": 0.9,
                    "review_required": False,
                },
                {
                    "id": "actor_strip_01",
                    "bbox": [20, 180, 300, 220],
                    "action": "drop",
                    "classification": "actor_sprite_sheet",
                    "system_role": "editorial_noise",
                    "candidate_asset_kind": "editorial_noise",
                    "compositional_role": None,
                    "engine_affordance": "editorial_noise",
                    "confidence_bbox": 0.9,
                    "confidence_classification": 0.9,
                    "confidence_composition": 0.1,
                    "confidence_engine_affordance": 0.95,
                    "review_required": False,
                },
            ],
            "sequences": [],
            "conflicts": [],
            "review_required": False,
            "blocked_reasons": [],
        }
        ir_path = root / "derived_structure_ir.json"
        save_json(ir_path, derived_ir)

        outputs = export_structure(ir_path, root / "reports")
        validation_report = Path(outputs["validation_report"])
        assert_true("Export gera validation_report", validation_report.is_file(), str(outputs))

        report = json.loads(validation_report.read_text(encoding="utf-8"))
        assert_true("Export final quando estrutura segura", report["export_mode"] == "final", str(report))
        assert_true("Export gera recomposed_scene", Path(outputs["recomposed_scene"]).is_file(), str(outputs))
        assert_true("Export registra resumo por regiao", len(report["region_confidence_summary"]) == 3, str(report))
        assert_true(
            "Export preserva referencias drop para inspecao",
            (root / "reports" / "extracts" / "final" / "drops" / "actor_strip_01.png").is_file(),
            str(outputs),
        )

        metadata = json.loads(Path(outputs["structural_metadata"]).read_text(encoding="utf-8"))
        assert_true(
            "Metadata explica canvas RGBA de review para scene layers",
            metadata.get("scene_layer_canvas_policy", {}).get("kind") == "shared_canvas_rgba_review_asset",
            json.dumps(metadata, ensure_ascii=False),
        )
        assert_true(
            "Validation report expõe delivery_findings",
            any(item.get("type") == "notable_drop_region" for item in report.get("delivery_findings", [])),
            json.dumps(report, ensure_ascii=False),
        )
        assert_true(
            "Scene layer gera tight preview para leitura humana",
            (root / "reports" / "extracts" / "final" / "layer_previews" / "architecture_panel_tight.png").is_file(),
            str(outputs),
        )

        derived_ir["regions"][0]["confidence_composition"] = 0.4
        save_json(ir_path, derived_ir)
        outputs = export_structure(ir_path, root / "reports_low_conf")
        report = json.loads(Path(outputs["validation_report"]).read_text(encoding="utf-8"))
        assert_true("Export cai para provisional quando confianca e baixa", report["export_mode"] == "provisional", str(report))

        derived_ir["regions"][0]["confidence_composition"] = 0.9
        derived_ir["conflicts"] = [{"type": "synthetic_conflict", "blocks_final_export": True}]
        save_json(ir_path, derived_ir)
        outputs = export_structure(ir_path, root / "reports_conflict")
        report = json.loads(Path(outputs["validation_report"]).read_text(encoding="utf-8"))
        assert_true("Conflito estrutural bloqueia export final", report["export_mode"] == "provisional", str(report))

    print(f"\nResultado: {PASSED} passou/passaram, {FAILED} falhou/falharam.")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
