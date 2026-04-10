#!/usr/bin/env python3
"""
Testes sinteticos do infer_source_structure.py.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

try:
    from PIL import Image
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from infer_source_structure import build_inference, group_frames_from_components  # noqa: E402

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


def build_stage_board(path: Path) -> None:
    image = Image.new("RGBA", (320, 224), (136, 136, 224, 255))
    pixels = np.array(image)
    pixels[10:90, 20:260, :3] = (160, 120, 80)
    pixels[95:120, 20:300, :3] = (210, 210, 220)
    pixels[125:170, 20:300, :3] = (96, 192, 255)
    for x in range(20, 260, 20):
        pixels[175:205, x:x + 6, :3] = (180, 60, 150)
    pixels[208:220, 40:260, :3] = (220, 90, 80)
    Image.fromarray(pixels, "RGBA").save(path)


def build_tile_object_sheet(path: Path) -> None:
    image = Image.new("RGBA", (256, 192), (255, 0, 255, 255))
    pixels = np.array(image)
    pixels[0:58, 0:256, :3] = (80, 20, 40)
    pixels[70:120, 10:60, :3] = (120, 70, 130)
    pixels[70:120, 70:120, :3] = (120, 70, 130)
    pixels[70:120, 130:180, :3] = (120, 70, 130)
    pixels[135:185, 10:60, :3] = (140, 50, 90)
    pixels[135:185, 70:120, :3] = (140, 50, 90)
    pixels[145:180, 78:112, :3] = (0, 0, 0)
    pixels[135:185, 130:180, :3] = (140, 50, 90)
    pixels[140:184, 136:176, :3] = (0, 0, 0)
    Image.fromarray(pixels, "RGBA").save(path)


def build_sprite_spill_components() -> tuple[list[int], list[dict[str, int | list[int]]]]:
    band_bbox = [0, 100, 220, 190]
    components = [
        {"bbox": [10, 106, 53, 187], "area": 1000, "width": 43, "height": 81},
        {"bbox": [65, 102, 115, 187], "area": 1000, "width": 50, "height": 85},
        {"bbox": [123, 100, 190, 187], "area": 1000, "width": 67, "height": 87},
        {"bbox": [198, 177, 220, 289], "area": 1000, "width": 22, "height": 112},
    ]
    return (band_bbox, components)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="md_infer_structure_") as temp_dir:
        root = Path(temp_dir)

        stage_path = root / "stage.png"
        build_stage_board(stage_path)
        observed_stage, derived_stage = build_inference(stage_path, "stage_board")

        assert_true("Infere stage board", derived_stage["layout_type"] == "stage_board", str(derived_stage["layout_type"]))
        keep_stage = [region for region in derived_stage["regions"] if region["action"] == "keep"]
        assert_true("Stage board gera ao menos 3 regioes uteis", len(keep_stage) >= 3, str(keep_stage))
        assert_true(
            "Observed IR e separado da derived IR",
            "regions" in observed_stage and "observed_support" not in derived_stage,
            str({"observed_keys": list(observed_stage.keys()), "derived_keys": list(derived_stage.keys())}),
        )
        assert_true(
            "Stage board usa confianca por dimensao",
            all("confidence_bbox" in region and "confidence_classification" in region and "confidence_engine_affordance" in region for region in derived_stage["regions"]),
            str(derived_stage["regions"]),
        )

        tile_path = root / "tile_sheet.png"
        build_tile_object_sheet(tile_path)
        observed_tile, derived_tile = build_inference(tile_path, "tile_object_sheet")
        tile_classes = {region["classification"] for region in derived_tile["regions"]}
        assert_true("Tile/object detecta corrompido", "corrupted_region" in tile_classes, str(tile_classes))
        assert_true("Tile/object detecta objeto animado", "object_animation_sequence" in tile_classes, str(tile_classes))
        assert_true("Tile/object detecta base e overlay", {"tile_cluster", "overlay_cluster"}.issubset(tile_classes), str(tile_classes))
        assert_true(
            "Tile/object registra conflitos engine-aware quando faltar split",
            "conflicts" in derived_tile,
            str(derived_tile),
        )

        band_bbox, spill_components = build_sprite_spill_components()
        grouped_frames = group_frames_from_components(band_bbox, spill_components)
        assert_true(
            "Sprite band ignora spillover vertical de frame da linha vizinha",
            len(grouped_frames) == 3,
            str(grouped_frames),
        )
        assert_true(
            "Sprite band preserva frames validos da propria linha",
            grouped_frames[-1][3] <= band_bbox[3],
            str(grouped_frames),
        )

    print(f"\nResultado: {PASSED} passou/passaram, {FAILED} falhou/falharam.")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
