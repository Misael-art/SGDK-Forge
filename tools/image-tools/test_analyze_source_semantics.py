#!/usr/bin/env python3
"""
Testes sinteticos do analyze_source_semantics.py.
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

from analyze_source_semantics import build_report, save_json  # noqa: E402

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
    with tempfile.TemporaryDirectory(prefix="md_source_semantics_") as temp_dir:
        root = Path(temp_dir)
        source = root / "source.png"
        target = root / "target.png"
        manifest_path = root / "case.json"

        image = Image.new("RGBA", (320, 224), (24, 24, 24, 255))
        pixels = image.load()
        for y in range(0, 80):
            for x in range(0, 320):
                pixels[x, y] = (200, 80, 40, 255)
        for y in range(80, 180):
            for x in range(0, 320):
                pixels[x, y] = (80, 80, 80, 255)
        for y in range(180, 224):
            for x in range(0, 320):
                pixels[x, y] = (30, 30, 30, 255)
        image.save(source)
        Image.new("RGBA", (320, 224), (10, 20, 30, 255)).save(target)

        manifest = {
            "case_id": "synthetic_scene_board",
            "source_image": str(source),
            "scene_truth_kind": "supervised_training_truth",
            "layout_complexity": "medium",
            "reports_dir": str(root / "reports"),
            "source_inventory": {
                "includes": ["scene_planes", "author_credits"],
            },
            "drop_policy": {
                "drop_classes": ["author_credits"],
            },
            "composition_schema": {
                "kind": "scene_layers",
                "roles": [
                    {"region_id": "bg_b", "composition_role": "scene_plane_bg_b", "order": 0},
                    {"region_id": "bg_a", "composition_role": "scene_plane_bg_a", "order": 1},
                    {"region_id": "front", "composition_role": "scene_plane_foreground_composition", "order": 2},
                ],
            },
            "semantic_parse_report": {
                "source_layout_type": "editorial_board",
                "semantic_regions": [
                    {"id": "bg_b", "classification": "scene_plane_bg_b", "bbox": [0, 0, 320, 80]},
                    {"id": "bg_a", "classification": "scene_plane_bg_a", "bbox": [0, 80, 320, 180]},
                    {"id": "front", "classification": "scene_plane_foreground_composition", "bbox": [0, 180, 320, 224]},
                ],
                "drop_regions": [
                    {"id": "credits", "classification": "author_credits", "bbox": [200, 180, 320, 224], "action": "drop"},
                ],
                "animation_ranges": [],
                "final_scene_hypothesis": {
                    "summary": "Cena sintetica recomposta em tres planos.",
                    "reference_image": str(target),
                },
            },
        }
        save_json(manifest_path, manifest)
        report = build_report(manifest_path, manifest)

        assert_true(
            "Relatorio supervisionado valida caso sem erros",
            report["validation"]["ok"],
            json.dumps(report["validation"], ensure_ascii=False),
        )
        assert_true(
            "Gera painel semantico humano",
            Path(report["outputs"]["human_semantic_panel"]).is_file(),
            str(report["outputs"]),
        )
        assert_true(
            "Gera painel de composicao inferida",
            Path(report["outputs"]["inferred_composition_panel"]).is_file(),
            str(report["outputs"]),
        )
        assert_true(
            "Gera recomposed_scene quando existe referencia supervisionada",
            Path(report["outputs"]["recomposed_scene"]).is_file(),
            str(report["outputs"]),
        )

        inferred = {
            "layout_type": "editorial_board",
            "export_mode": "final",
            "review_required": False,
            "recomposition_visual_score": 0.98,
            "visual_failures": [],
            "recomposition_pass": True,
            "conflicts": [],
            "blocked_reasons": [],
            "delivery_findings": [
                {
                    "type": "shared_canvas_sparse_alpha_expected",
                    "severity": "info",
                    "target": "bg_b_pred",
                    "message": "Layer ocupa apenas parte do canvas comum.",
                }
            ],
            "regions": [
                {
                    "id": "bg_b_pred",
                    "classification": "scene_plane_bg_b",
                    "bbox": [0, 0, 320, 80],
                    "action": "keep",
                    "compositional_role": "scene_plane_bg_b",
                    "engine_affordance": "scene_layer_continuous",
                    "confidence_bbox": 0.95,
                    "confidence_classification": 0.92,
                    "confidence_composition": 0.93,
                    "confidence_engine_affordance": 0.91,
                },
                {
                    "id": "bg_a_pred",
                    "classification": "scene_plane_bg_a",
                    "bbox": [0, 80, 320, 180],
                    "action": "keep",
                    "compositional_role": "scene_plane_bg_a",
                    "engine_affordance": "scene_layer_continuous",
                    "confidence_bbox": 0.95,
                    "confidence_classification": 0.92,
                    "confidence_composition": 0.93,
                    "confidence_engine_affordance": 0.91,
                },
                {
                    "id": "front_pred",
                    "classification": "scene_plane_foreground_composition",
                    "bbox": [0, 180, 320, 224],
                    "action": "keep",
                    "compositional_role": "scene_plane_foreground_composition",
                    "engine_affordance": "scene_layer_continuous",
                    "confidence_bbox": 0.95,
                    "confidence_classification": 0.92,
                    "confidence_composition": 0.93,
                    "confidence_engine_affordance": 0.91,
                },
                {
                    "id": "credits_pred",
                    "classification": "author_credits",
                    "bbox": [200, 180, 320, 224],
                    "action": "drop",
                    "engine_affordance": "editorial_noise",
                    "confidence_bbox": 0.95,
                    "confidence_classification": 0.92,
                    "confidence_composition": 0.08,
                    "confidence_engine_affordance": 0.97,
                },
            ],
        }
        audited_report = build_report(manifest_path, manifest, inferred)
        assert_true(
            "Auditoria supervisionada reconhece inferencia alinhada",
            audited_report["audit"]["ok"],
            json.dumps(audited_report["audit"], ensure_ascii=False),
        )
        assert_true(
            "Auditoria supervisionada expõe acuracia por dimensao",
            audited_report["audit"]["composition_accuracy"] >= 1.0 and audited_report["audit"]["engine_affordance_accuracy"] >= 1.0,
            json.dumps(audited_report["audit"], ensure_ascii=False),
        )
        assert_true(
            "Auditoria supervisionada carrega delivery_findings",
            audited_report["audit"]["delivery_finding_count"] == 1,
            json.dumps(audited_report["audit"], ensure_ascii=False),
        )

    print(f"\nResultado: {PASSED} passou/passaram, {FAILED} falhou/falharam.")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
