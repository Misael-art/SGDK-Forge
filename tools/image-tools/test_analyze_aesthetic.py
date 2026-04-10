#!/usr/bin/env python3
"""
Testes sinteticos do juiz estetico.

Uso:
  python tools/image-tools/test_analyze_aesthetic.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


SCRIPT = Path(__file__).resolve().parent / "analyze_aesthetic.py"
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


def run_case(asset: Path, role: str, profile: str, paired_bg: Path | None = None, critical: bool = False) -> dict:
    output = asset.parent / f"{asset.stem}_report.json"
    command = [
        sys.executable,
        str(SCRIPT),
        "--asset",
        str(asset),
        "--role",
        role,
        "--reference-profile",
        profile,
        "--output",
        str(output)
    ]
    if paired_bg:
        command.extend(["--paired-bg", str(paired_bg)])
    if critical:
        command.append("--critical-visual")

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(output.read_text(encoding="utf-8"))


def make_sprite_good(path: Path) -> None:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    for y in range(6, 26):
        for x in range(8, 24):
            px[x, y] = (68, 136, 204, 255)
    for y in range(8, 24):
        for x in range(10, 22):
            px[x, y] = (136, 204, 238, 255)
    for y in range(10, 22):
        for x in range(12, 20):
            px[x, y] = (34, 68, 136, 255)
    for x in range(8, 24):
        px[x, 6] = (0, 0, 0, 255)
        px[x, 25] = (0, 0, 0, 255)
    for y in range(6, 26):
        px[8, y] = (0, 0, 0, 255)
        px[23, y] = (0, 0, 0, 255)
    img.save(path, "PNG")


def make_low_separation_sprite(path: Path) -> None:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    for y in range(6, 26):
        for x in range(8, 24):
            px[x, y] = (92, 124, 160, 255)
    for y in range(10, 22):
        for x in range(11, 21):
            px[x, y] = (102, 136, 172, 255)
    for y in range(13, 19):
        for x in range(13, 19):
            px[x, y] = (78, 108, 144, 255)
    img.save(path, "PNG")


def make_palette_waste(path: Path) -> None:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    tones = [(80 + i, 80 + i, 80 + i, 255) for i in range(12)]
    for y in range(8, 24):
        for x in range(8, 24):
            px[x, y] = tones[(x + y) % len(tones)]
    img.save(path, "PNG")


def make_sparse_sprite(path: Path) -> None:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    for y in range(4, 8):
        for x in range(4, 8):
            px[x, y] = (238, 170, 34, 255)
    img.save(path, "PNG")


def make_noisy_bg(path: Path) -> None:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
    px = img.load()
    palette = [
        (34, 34, 34, 255),
        (68, 68, 68, 255),
        (102, 102, 102, 255),
        (136, 136, 136, 255),
        (170, 170, 170, 255),
        (204, 204, 204, 255)
    ]
    for y in range(32):
        for x in range(32):
            px[x, y] = palette[(x * 3 + y * 5) % len(palette)]
    img.save(path, "PNG")


def make_flat_bg(path: Path) -> None:
    img = Image.new("RGBA", (32, 32), (102, 102, 102, 255))
    img.save(path, "PNG")


def make_similar_bg(path: Path) -> None:
    img = Image.new("RGBA", (32, 32), (70, 140, 206, 255))
    img.save(path, "PNG")


def has_issue(report: dict, code: str) -> bool:
    return any(issue["code"] == code for issue in report["issues"])


def main() -> int:
    if not SCRIPT.exists():
        print(f"Erro: script nao encontrado: {SCRIPT}")
        return 1

    with tempfile.TemporaryDirectory(prefix="md_aesthetic_") as temp_dir:
        root = Path(temp_dir)

        good = root / "good_sprite.png"
        low_sep = root / "low_separation_sprite.png"
        palette_waste = root / "palette_waste.png"
        sparse = root / "sparse.png"
        noisy_bg = root / "noisy_bg.png"
        flat_bg = root / "flat_bg.png"
        similar_bg = root / "similar_bg.png"

        make_sprite_good(good)
        make_low_separation_sprite(low_sep)
        make_palette_waste(palette_waste)
        make_sparse_sprite(sparse)
        make_noisy_bg(noisy_bg)
        make_flat_bg(flat_bg)
        make_similar_bg(similar_bg)

        good_report = run_case(good, "sprite", "generic-megadrive-elite")
        assert_true("Sprite base fica ao menos em review", good_report["status"] in {"elite_ready", "needs_review"}, good_report["status"])

        palette_report = run_case(palette_waste, "sprite", "generic-megadrive-elite")
        assert_true("Detecta desperdicio de paleta", has_issue(palette_report, "PALETTE_WASTE"), json.dumps(palette_report["issues"], ensure_ascii=False))

        sparse_report = run_case(sparse, "sprite", "generic-megadrive-elite")
        assert_true("Detecta excesso de vazio", has_issue(sparse_report, "OVER_EMPTY_TILES"), json.dumps(sparse_report["issues"], ensure_ascii=False))

        noisy_report = run_case(noisy_bg, "bg_a", "earthworm-jim")
        assert_true("Detecta textura ruidosa", has_issue(noisy_report, "NOISY_TEXTURE"), json.dumps(noisy_report["issues"], ensure_ascii=False))

        flat_report = run_case(flat_bg, "bg_a", "generic-megadrive-elite")
        assert_true("Detecta falta de dithering em BG_A", has_issue(flat_report, "MISSING_DITHERING_FOR_MATERIAL"), json.dumps(flat_report["issues"], ensure_ascii=False))

        layer_report = run_case(low_sep, "sprite", "shinobi-iii", paired_bg=similar_bg)
        assert_true("Detecta separacao de plano baixa", has_issue(layer_report, "LOW_LAYER_SEPARATION"), json.dumps(layer_report["issues"], ensure_ascii=False))

    print(f"\nResultado: {PASSED} passou/passaram, {FAILED} falhou/falharam.")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
