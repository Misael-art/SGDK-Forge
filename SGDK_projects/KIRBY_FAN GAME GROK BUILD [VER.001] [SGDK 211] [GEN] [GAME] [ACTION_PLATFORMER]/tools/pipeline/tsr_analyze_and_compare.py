#!/usr/bin/env python3
"""Analyze reference sheets + compare metrics vs our R6 Kirby (lab only).

Outputs:
  data/reference_archive/compare/metrics_v001.json
  data/reference_archive/compare/*_panel.png
  data/reference_archive/premises/PREMISES_DRAFT.md
  data/reference_archive/versions/v003_md_quantized/*

Does not write to res/.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "data" / "reference_archive"
RAW = ARCHIVE / "raw"
COMPARE = ARCHIVE / "compare"
PREMISES = ARCHIVE / "premises"
V003 = ARCHIVE / "versions" / "v003_md_quantized"
OURS = ROOT / "res" / "sprites" / "ph_kirby.png"

LATTICE = np.array([0, 36, 73, 109, 146, 182, 219, 255], dtype=np.int16)


def snap_rgb(rgb: np.ndarray) -> np.ndarray:
    out = rgb.astype(np.int16)
    for c in range(3):
        d = np.abs(out[..., c : c + 1] - LATTICE[None, None, :])
        out[..., c] = LATTICE[d.argmin(-1)]
    return out.astype(np.uint8)


def is_key(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0].astype(np.int16), rgb[..., 1].astype(np.int16), rgb[..., 2].astype(np.int16)
    # magenta / near-magenta / pure green chroma keys common on TSR
    mag = (r >= 200) & (b >= 200) & (g <= 80)
    black = (r <= 8) & (g <= 8) & (b <= 8)
    lime = (g >= 200) & (r <= 80) & (b <= 80)
    return mag | black | lime


def load_rgb(path: Path) -> np.ndarray:
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    rgb = a[..., :3].copy()
    alpha = a[..., 3]
    # transparent → magenta key for analysis
    rgb[alpha < 16] = (255, 0, 255)
    return rgb


def body_stats(rgb: np.ndarray) -> dict:
    key = is_key(rgb)
    body = ~key
    if not body.any():
        return {"opaque_pct": 0.0, "unique_colors": 0, "pink_ramp": 0, "mean_lum": 0.0}
    pix = rgb[body]
    # unique colors (capped)
    uniq = {tuple(p) for p in pix.reshape(-1, 3)}
    # pink-ish: high R, mid B, lower G relative
    pinks = [
        c
        for c in uniq
        if c[0] >= 146 and c[0] >= c[1] and c[2] >= 73 and (c[0] - c[1]) >= 20
    ]
    lum = 0.2126 * pix[:, 0] + 0.7152 * pix[:, 1] + 0.0722 * pix[:, 2]
    return {
        "opaque_pct": float(body.mean() * 100),
        "unique_colors": len(uniq),
        "pink_ramp": len(pinks),
        "mean_lum": float(lum.mean()),
        "lum_p10": float(np.percentile(lum, 10)),
        "lum_p90": float(np.percentile(lum, 90)),
        "lum_delta": float(np.percentile(lum, 90) - np.percentile(lum, 10)),
        "size": list(rgb.shape[:2]),
    }


def quantize_sheet(rgb: np.ndarray, max_colors: int = 15) -> Image.Image:
    """Lab quantize: snap lattice then reduce — absolute palette stamp 0..15."""
    snapped = snap_rgb(rgb)
    key = is_key(snapped)
    work = snapped.copy()
    work[key] = (255, 0, 255)
    # PIL adaptive quantize
    im = Image.fromarray(work, mode="RGB")
    q = im.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    # force index 0 = key: remap nearest to magenta
    pal = q.getpalette() or []
    # convert to P with magenta as 0
    arr = np.array(q)
    # find palette entry closest to magenta
    cols = []
    for i in range(max_colors):
        cols.append((pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2]))
    mag_i = min(range(len(cols)), key=lambda i: abs(cols[i][0] - 255) + abs(cols[i][1] - 0) + abs(cols[i][2] - 255))
    # swap mag_i with 0
    if mag_i != 0:
        arr2 = arr.copy()
        arr2[arr == 0] = mag_i
        arr2[arr == mag_i] = 0
        arr = arr2
        cols[0], cols[mag_i] = cols[mag_i], cols[0]
    # pad to 16
    while len(cols) < 16:
        cols.append((0, 0, 0))
    cols[0] = (255, 0, 255)
    out = Image.fromarray(arr.astype(np.uint8), mode="P")
    flat: list[int] = []
    for c in cols[:16]:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - 16))
    out.putpalette(flat[:768])
    return out


def panel_compare(ours_path: Path, ref_paths: list[Path], out_path: Path) -> None:
    imgs = []
    labels = []
    if ours_path.exists():
        imgs.append(Image.open(ours_path).convert("RGB"))
        labels.append("OURS_R6")
    for p in ref_paths:
        if not p.exists():
            continue
        im = Image.open(p).convert("RGB")
        # scale ref to height 64 for panel strip if huge
        if im.height > 128:
            scale = 128 / im.height
            im = im.resize((max(1, int(im.width * scale)), 128), Image.Resampling.NEAREST)
        imgs.append(im)
        labels.append(p.stem[:24])
    if not imgs:
        return
    h = max(im.height for im in imgs) + 20
    w = sum(im.width for im in imgs) + 8 * len(imgs)
    board = Image.new("RGB", (w, h), (30, 30, 34))
    x = 4
    for im, lab in zip(imgs, labels):
        board.paste(im, (x, 18))
        # label is optional; skip font dependency
        x += im.width + 8
    board.save(out_path)


def main() -> int:
    COMPARE.mkdir(parents=True, exist_ok=True)
    PREMISES.mkdir(parents=True, exist_ok=True)
    V003.mkdir(parents=True, exist_ok=True)

    metrics: dict = {"ship_allowed": False, "fan_study_allowed": True, "files": {}}

    raw_files = sorted(RAW.rglob("*.png")) + sorted(RAW.rglob("*.gif"))
    for path in raw_files:
        rel = str(path.relative_to(ARCHIVE))
        try:
            rgb = load_rgb(path)
        except Exception as e:
            metrics["files"][rel] = {"error": str(e)}
            continue
        st = body_stats(rgb)
        metrics["files"][rel] = st
        # quantize lab copy
        q = quantize_sheet(rgb)
        out = V003 / path.relative_to(RAW)
        out.parent.mkdir(parents=True, exist_ok=True)
        # gif → png
        out = out.with_suffix(".png")
        q.save(out)
        print(f"{rel}: colors={st['unique_colors']} pinks={st['pink_ramp']} lumΔ={st['lum_delta']:.1f}")

    # ours
    if OURS.exists():
        our = load_rgb(OURS)
        metrics["ours_r6"] = body_stats(our)
        print("ours_r6", metrics["ours_r6"])

    # compare panel: ours vs SNES vs GBA vs NES
    refs = [
        RAW / "snes_kirby_super_star" / "52859_kirby.png",
        RAW / "gba_nightmare_dreamland" / "32130_kirby.png",
        RAW / "nes_kirby_adventure" / "49192_kirby.png",
    ]
    panel_compare(OURS, refs, COMPARE / "ours_r6_vs_ref_kirby_panel.png")

    (COMPARE / "metrics_v001.json").write_text(json.dumps(metrics, indent=2) + "\n")

    # draft premises from numbers
    ours = metrics.get("ours_r6", {})
    snes_key = next((k for k in metrics["files"] if "52859" in k), None)
    snes = metrics["files"].get(snes_key or "", {})
    premises = f"""# PREMISES DRAFT — extraídas do arquivo de referência (lab)

> Gerado automaticamente a partir de métricas. Revisão humana obrigatória antes de
> virar checklist de geração. **Não copiar pixels de rip.**

## Fonte

- Arquivo: `data/reference_archive/`
- Compare: `compare/ours_r6_vs_ref_kirby_panel.png`
- Métricas: `compare/metrics_v001.json`

## Personagem (Kirby)

| Premissa | Ref SNES (se ok) | Nosso R6 | Ação de geração |
|---|---|---|---|
| Tons de rosa no corpo (aprox) | {snes.get('pink_ramp', '?')} cores pink-like | {ours.get('pink_ramp', '?')} | Gerador deve manter **≥5** faixas (1–5 + outline) |
| Delta luminância p90−p10 | {snes.get('lum_delta', 0):.1f} | {ours.get('lum_delta', 0):.1f} | Alvo: delta ≥ 80 (volume legível a 32px) |
| Contorno escuro | presente nos rips | idx 6 | Sempre anel de contorno 1px |
| Pés contrastantes | castanho/vermelho | idx 7/8 | Nunca rosa do corpo nos pés |
| Olhos | alto contraste | 9/10 | Preto + brilho branco |
| Set de poses mínimo | idle, walk, jump, float, inhale, hurt | 8 frames R6 | Manter taxonomia do `kirby.c` |

## Cenário (Vegetable Valley NES)

- Estágios 2637–2640: estudar **densidade de tile** (grama, terra, arbusto) vs nosso R5.
- Premissa de tile: **não flat fill** — microdetalhe em ≥30% da área opaca de terra.
- Montanha: faces claras/escuras sólidas (já em R5); ref NES é mais “bloco”; ref SNES é alvo AAA.

## Pipeline MD (aprendizado de conversão)

1. Key color → index 0 (nunca corpo).
2. Reduzir cores **antes** de snap RGB333 (PALETTES.md).
3. Stamp 0..15 absoluto no PNG (L-011).
4. Sheet personagem: células uniformes, sem divisórias.
5. Comparar **métricas**, não bitmap do rip.

## Critério de sucesso do aprendizado

1. Geração original atinge pink_ramp ≥ ref e lum_delta ≥ 0.85× ref SNES (quando medido).
2. Critico cego: hesitação entre original e ref **painel de métricas** (não pixel-perfect).
3. Zero bytes de `raw/` em `res/` (hash gate).

## Próximo

- [ ] Revisão humana deste draft → `PREMISES.md` final
- [ ] Atualizar `build_kirby_procedural.py` com checklist de premissas
- [ ] Imagine prompts ancorados em premissas (sem “copy this sheet”)
- [ ] Critico cego R4: nosso gen vs SNES ref (métricas no relatório)
"""
    (PREMISES / "PREMISES_DRAFT.md").write_text(premises)
    print("wrote", COMPARE / "metrics_v001.json")
    print("wrote", PREMISES / "PREMISES_DRAFT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
