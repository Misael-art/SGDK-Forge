#!/usr/bin/env python3
"""
Ferramenta generica: redimensiona PNGs de producao e (opcional) boards conforme
um spec JSON e gera contrapartes BMP indexadas (ate 16 cores).

Serve para qualquer projeto que precise de lote com dimensoes exatas e PNG + BMP
indexado (ex.: Mega Drive / SGDK).

Uso:
  python batch_resize_index.py --spec <spec.json> --batch-root <dir>
  python batch_resize_index.py --batch-root <dir>   # usa --spec default se existir

Spec JSON:
  {
    "production": [
      {
        "name": "id",
        "png_rel": "production/arquivo.png",
        "w": 32, "h": 32,
        "bmp_rel": "indexed/arquivo.bmp",
        "bmp_w": 32, "bmp_h": 32,
        "transparency": true
      }
    ],
    "boards": [
      { "rel": "boards/cena.png", "w": 320, "h": 224 }
    ]
  }

Requisito: pip install Pillow
"""

import argparse
import json
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def _resample():
    return Image.Resampling.LANCZOS


def resize_and_save(img: Image.Image, path: str, w: int, h: int) -> None:
    if img.size != (w, h):
        img = img.resize((w, h), _resample())
    img.save(path, "PNG")


def quantize_to_16_colors(img: Image.Image, need_transparency: bool, max_colors: int = 16) -> Image.Image:
    """Reduz a imagem a no maximo max_colors; se need_transparency, reserva uma cor transparente."""
    if not need_transparency:
        rgb = img.convert("RGB")
        return rgb.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT).convert("P")
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.split()[-1]
    rgb = img.convert("RGB")
    n = max_colors - 1
    quantized_rgb = rgb.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    palette_rgb = quantized_rgb.getpalette()[: n * 3]
    full_palette = [(0, 0, 0)] + [
        (palette_rgb[i * 3], palette_rgb[i * 3 + 1], palette_rgb[i * 3 + 2]) for i in range(n)
    ]
    out = Image.new("P", img.size)
    out.putpalette([c for p in full_palette for c in p])
    out.info["transparency"] = 0
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if alpha.getpixel((x, y)) < 128:
                out.putpixel((x, y), 0)
            else:
                out.putpixel((x, y), 1 + quantized_rgb.getpixel((x, y)))
    return out


def to_indexed_bmp(img: Image.Image, path: str, max_colors: int = 16) -> None:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    indexed = img.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    indexed.save(path, "BMP")


def run_batch(
    root: str,
    production_specs: list,
    board_specs: list,
    max_colors: int = 16,
) -> list:
    """Executa redimensionamento e indexacao. Retorna lista de mensagens de erro (vazia se ok)."""
    errors = []
    sep = os.sep

    for spec in production_specs:
        png_path = os.path.join(root, spec["png_rel"].replace("/", sep))
        bmp_path = os.path.join(root, spec["bmp_rel"].replace("/", sep))
        if not os.path.isfile(png_path):
            errors.append(f"Falta: {spec['png_rel']}")
            continue
        try:
            img = Image.open(png_path).convert("RGBA")
            w, h = spec["w"], spec["h"]
            img_resized = img.resize((w, h), _resample()) if img.size != (w, h) else img
            img_quantized = quantize_to_16_colors(
                img_resized, spec.get("transparency", False), max_colors=max_colors
            )
            if spec.get("transparency", False):
                rgba_out = Image.new("RGBA", img_quantized.size)
                pal = img_quantized.getpalette()
                for y in range(img_quantized.size[1]):
                    for x in range(img_quantized.size[0]):
                        idx = img_quantized.getpixel((x, y))
                        if idx == 0:
                            rgba_out.putpixel((x, y), (0, 0, 0, 0))
                        else:
                            r, g, b = pal[idx * 3 : idx * 3 + 3]
                            rgba_out.putpixel((x, y), (r, g, b, 255))
                if not any(
                    rgba_out.getpixel((x, y))[3] < 255
                    for y in range(rgba_out.size[1])
                    for x in range(rgba_out.size[0])
                ):
                    rgba_out.putpixel((0, 0), (0, 0, 0, 0))
                rgba_out.save(png_path, "PNG")
            else:
                img_quantized.save(png_path, "PNG")
            bmp_w, bmp_h = spec["bmp_w"], spec["bmp_h"]
            img_bmp = (
                img_quantized.resize((bmp_w, bmp_h), Image.Resampling.NEAREST)
                if (w, h) != (bmp_w, bmp_h)
                else img_quantized
            )
            os.makedirs(os.path.dirname(bmp_path), exist_ok=True)
            if img_bmp.mode == "P":
                img_bmp.save(bmp_path, "BMP")
            else:
                to_indexed_bmp(img_bmp, bmp_path, max_colors=max_colors)
        except Exception as e:
            errors.append(f"{spec.get('name', spec['png_rel'])}: {e}")

    for spec in board_specs:
        path = os.path.join(root, spec["rel"].replace("/", sep))
        if not os.path.isfile(path):
            errors.append(f"Falta board: {spec['rel']}")
            continue
        try:
            img = Image.open(path).convert("RGB")
            resize_and_save(img, path, spec["w"], spec["h"])
        except Exception as e:
            errors.append(f"Board {spec['rel']}: {e}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Redimensiona e indexa lote de imagens conforme spec JSON (uso generico)."
    )
    parser.add_argument(
        "--spec",
        default=None,
        help="Caminho para o arquivo JSON de spec (production + boards).",
    )
    parser.add_argument(
        "--batch-root",
        required=True,
        help="Diretorio raiz do lote (contem production/, indexed/, boards/).",
    )
    parser.add_argument(
        "--max-colors",
        type=int,
        default=16,
        help="Numero maximo de cores para quantizacao (default: 16).",
    )
    args = parser.parse_args()
    root = os.path.abspath(args.batch_root)
    if not os.path.isdir(root):
        print(f"Erro: diretorio nao encontrado: {root}", file=sys.stderr)
        return 1

    spec_path = args.spec
    if not spec_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_spec = os.path.join(script_dir, "specs", "pequeno_principe_v2.json")
        if os.path.isfile(default_spec):
            spec_path = default_spec
    if not spec_path or not os.path.isfile(spec_path):
        print("Erro: indique --spec <arquivo.json> ou coloque specs/pequeno_principe_v2.json em tools/image-tools.", file=sys.stderr)
        return 1

    with open(spec_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    production_specs = data.get("production", [])
    board_specs = data.get("boards", [])

    errors = run_batch(root, production_specs, board_specs, max_colors=args.max_colors)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("Lote redimensionado e indexado com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
