#!/usr/bin/env python3
"""
Testes sinteticos da curadoria de budget do analyze_translation_case.py.

Uso:
  python tools/image-tools/test_analyze_translation_case.py
"""

from __future__ import annotations

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

from analyze_translation_case import (  # noqa: E402
    apply_case_penalties,
    build_semantic_stage_review,
    build_hardware_budget_review,
    editorial_sheet_contamination,
    tile_budget_stats,
)

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


def make_unique_grid(path: Path, width_tiles: int, height_tiles: int) -> None:
    image = Image.new("RGBA", (width_tiles * 8, height_tiles * 8), (0, 0, 0, 0))
    px = image.load()
    for ty in range(height_tiles):
        for tx in range(width_tiles):
            tile_id = (ty * width_tiles) + tx + 1
            for y in range(8):
                for x in range(8):
                    bit_index = y * 8 + x
                    on = (tile_id >> (bit_index % 11)) & 1
                    accent = (tile_id * (bit_index + 3)) % 256
                    if on:
                        color = (accent, (accent * 5) % 256, (accent * 9) % 256, 255)
                    else:
                        color = ((accent * 13) % 256, (accent * 7) % 256, (accent * 3) % 256, 255)
                    px[(tx * 8) + x, (ty * 8) + y] = color
    image.save(path, "PNG")


def make_repeated_grid(path: Path, width_tiles: int, height_tiles: int) -> None:
    image = Image.new("RGBA", (width_tiles * 8, height_tiles * 8), (0, 0, 0, 0))
    px = image.load()
    colors = [
        (32, 96, 160, 255),
        (64, 128, 192, 255),
        (96, 160, 224, 255),
        (16, 48, 80, 255),
    ]
    for ty in range(height_tiles):
        for tx in range(width_tiles):
            c1 = colors[(tx + ty) % len(colors)]
            c2 = colors[(tx * 2 + ty) % len(colors)]
            for y in range(8):
                for x in range(8):
                    px[(tx * 8) + x, (ty * 8) + y] = c1 if x < 4 else c2
    image.save(path, "PNG")


def make_editorial_sheet(path: Path) -> None:
    image = Image.new("RGBA", (320, 224), (0, 0, 0, 255))
    draw = image.load()
    panels = [
        (8, 8, 120, 56, (238, 102, 0, 255)),
        (18, 70, 180, 140, (102, 102, 68, 255)),
        (210, 78, 300, 132, (136, 34, 34, 255)),
        (16, 160, 180, 212, (68, 34, 34, 255)),
        (220, 170, 300, 212, (204, 170, 136, 255)),
    ]
    for left, top, right, bottom, color in panels:
        for y in range(top, bottom):
            for x in range(left, right):
                draw[x, y] = color if ((x + y) & 1) == 0 else (color[0] // 2, color[1] // 2, color[2] // 2, 255)
    image.save(path, "PNG")


def make_clean_scene(path: Path) -> None:
    image = Image.new("RGBA", (320, 224), (34, 0, 34, 255))
    draw = image.load()
    for y in range(224):
        for x in range(320):
            if y < 96:
                draw[x, y] = (136, 34 + (y // 4), 34, 255)
            elif y < 176:
                draw[x, y] = (68, 34, 34, 255) if ((x // 16) + (y // 8)) % 2 == 0 else (102, 68, 34, 255)
            else:
                draw[x, y] = (34, 34, 34, 255) if ((x + y) & 7) < 4 else (68, 34, 34, 255)
    image.save(path, "PNG")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="md_translation_budget_") as temp_dir:
        root = Path(temp_dir)
        bg_a = root / "bg_a.png"
        bg_b = root / "bg_b.png"
        sprite = root / "sprite.png"
        repeated = root / "repeated.png"
        editorial = root / "editorial.png"
        clean_scene = root / "clean_scene.png"

        make_unique_grid(bg_a, 40, 28)
        make_unique_grid(bg_b, 40, 28)
        make_unique_grid(sprite, 16, 8)
        make_repeated_grid(repeated, 16, 16)
        make_editorial_sheet(editorial)
        make_clean_scene(clean_scene)

        repeated_stats = tile_budget_stats(repeated)
        assert_true(
            "Repeated grid gera reuso real",
            repeated_stats["unique_non_empty_tiles"] < repeated_stats["non_empty_tiles"],
            str(repeated_stats),
        )

        variants = {
            "basic": {
                "units": [
                    {"name": "bg_b", "role": "bg_b", "tile_budget": tile_budget_stats(bg_b)},
                    {"name": "mid", "role": "midground_layer", "tile_budget": tile_budget_stats(bg_a)},
                    {"name": "front", "role": "foreground_layer", "tile_budget": tile_budget_stats(sprite)},
                ]
            },
            "elite": {
                "units": [
                    {"name": "bg_b", "role": "bg_b", "tile_budget": tile_budget_stats(bg_b)},
                    {"name": "mid", "role": "midground_layer", "tile_budget": tile_budget_stats(bg_a)},
                    {"name": "front", "role": "foreground_layer", "tile_budget": tile_budget_stats(sprite)},
                ]
            },
        }

        review = build_hardware_budget_review("scene_slice", variants)
        codes = {item["code"] for item in review["recommendations"]}

        assert_true(
            "Detecta compare_flat candidate quando backgrounds estouram teto pratico",
            "COMPARE_FLAT_CANDIDATE" in codes,
            str(review),
        )
        assert_true(
            "Detecta candidate de reparticao manual de VRAM",
            "MANUAL_VRAM_PARTITION_CANDIDATE" in codes,
            str(review),
        )
        assert_true(
            "Detecta risco de conversao de imagem inteira",
            "WHOLE_IMAGE_CONVERSION_RISK" in codes,
            str(review),
        )

        editorial_penalty, editorial_details = editorial_sheet_contamination(editorial)
        clean_penalty, clean_details = editorial_sheet_contamination(clean_scene)

        assert_true(
            "Detecta contaminacao editorial em sheet multipainel",
            editorial_penalty > 0,
            str(editorial_details),
        )
        assert_true(
            "Nao penaliza cena limpa como sheet editorial",
            clean_penalty == 0,
            str(clean_details),
        )

        exempt_analysis = {
            "metrics": {
                "reference_alignment": 0.8,
                "visual_excellence_score": 0.8,
            },
            "issues": [],
            "recommendations": [],
            "status": "elite_ready",
        }
        exempt_result = apply_case_penalties(
            exempt_analysis,
            editorial,
            "scene_slice",
            "foreground_layer",
        )
        penalty_sources = {item["source"] for item in exempt_result.get("case_penalties", [])}
        issue_codes = {item["code"] for item in exempt_result.get("issues", [])}
        assert_true(
            "Foreground layer semantica nao recebe falso positivo editorial",
            "semantic_layer_exemption" in penalty_sources and "EDITORIAL_SHEET_CONTAMINATION" not in issue_codes,
            str(exempt_result),
        )

        semantic_manifest = {
            "translation_target": "scene_slice",
            "scene_truth_kind": "supervised_training_truth",
            "layout_complexity": "high",
            "source_inventory": {"includes": ["scene_planes", "author_credits"]},
            "drop_policy": {"drop_classes": ["author_credits"]},
            "composition_schema": {
                "roles": [
                    {"region_id": "bg", "composition_role": "scene_plane_bg_b", "order": 0},
                    {"region_id": "credits", "composition_role": "mockup_preview", "order": 1},
                ]
            },
            "semantic_parse_report": {
                "source_layout_type": "editorial_board",
                "semantic_regions": [
                    {"id": "bg", "classification": "scene_plane_bg_b", "bbox": [0, 0, 64, 64]},
                ],
                "drop_regions": [
                    {"id": "credits", "classification": "author_credits", "bbox": [64, 0, 96, 32], "action": "drop"},
                ],
            },
        }
        semantic_variants = {
            "basic": {
                "units": [
                    {"name": "bg", "role": "bg_b", "semantic_region_id": "bg"},
                    {"name": "credits_promoted", "role": "bg_a", "semantic_region_id": "credits"},
                ]
            },
            "elite": {
                "units": [
                    {"name": "bg", "role": "bg_b", "semantic_region_id": "bg"},
                ]
            },
        }
        semantic_review = build_semantic_stage_review(semantic_manifest, semantic_variants)
        semantic_codes = {item["code"] for item in semantic_review["issues"]}
        assert_true(
            "Detecta promocao indevida de regiao descartada",
            "DROP_REGION_PROMOTED_TO_SCENE" in semantic_codes,
            str(semantic_review),
        )

        missing_semantic_manifest = {
            "translation_target": "scene_slice",
            "layout_complexity": "high",
            "scene_truth_kind": "inferred",
            "source_inventory": {},
            "drop_policy": {},
            "composition_schema": {},
            "source_semantic_map": {
                "source_layout_type": "editorial_board",
            },
        }
        missing_review = build_semantic_stage_review(missing_semantic_manifest, {"basic": {"units": []}, "elite": {"units": []}})
        missing_codes = {item["code"] for item in missing_review["issues"]}
        assert_true(
            "Detecta ausencia de semantic_parse_report em source complexo",
            "MISSING_SEMANTIC_PARSE_REPORT" in missing_codes and "MISSING_COMPOSITION_SCHEMA" in missing_codes,
            str(missing_review),
        )

    print(f"\nResultado: {PASSED} passou/passaram, {FAILED} falhou/falharam.")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
