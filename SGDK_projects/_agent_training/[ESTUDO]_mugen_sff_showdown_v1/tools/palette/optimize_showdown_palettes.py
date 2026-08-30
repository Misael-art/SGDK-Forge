#!/usr/bin/env python3
"""Otimizador global de subpaletas Mega Drive para o stage Showdown.

Substitui os slots manuais (ROUTE_A_MANUAL_PALETTES) por slots derivados
da distribuicao REAL de pixels visiveis do mundo reconstruido, respeitando:

- espaco de cor 9-bit (canais em MD_LEVELS);
- decisao de subpaleta por tile EXATAMENTE como o exporter resolve
  (_contextual_palette_id_for_tile) — a semantica de composicao nao muda;
- slot 0 fixo = BACKDROP_MD_RGB (index 0 / convencao de transparencia).

Desempenho: os pixels sao lidos UMA unica vez e reduzidos a registros
compactos por tile (contador de cores + linha + plano). As iteracoes E/M
redecidem pids e refitam slots sobre esses registros — sem reler PNG.

Deterministico: zero aleatoriedade. Semente inicial = paletas manuais.

Saida: analysis/optimized_palettes_v002.json + metricas estimadas.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "sgdk_export"))

from export_showdown_bins import (  # noqa: E402
    BACKDROP_MD_RGB,
    MD_LEVELS,
    PLANE_BG_A,
    PLANE_BG_B,
    _build_route_a_plane_frames,
    _contextual_palette_id_for_tile,
    _load_reconstruction_geometry,
    _rgb_distance_sq,
    _route_a_palettes,
)

MD_LEVELS_LIST = list(MD_LEVELS)

OUT_PATH = ROOT / "analysis" / "optimized_palettes_v002.json"
K_SLOTS = 15
OUTER_ITERS = 3
INNER_KMEANS_ITERS = 12


def build_tile_records():
    """Leitura UNICA dos planos -> [(ty, plane_id, Counter_cores_visiveis)]."""
    reconstruction = _load_reconstruction_geometry()
    frames_dir = ROOT / "work" / "reconstructed_layers"
    frames = sorted(frames_dir.glob("frame_*.png"))
    if not frames:
        raise FileNotFoundError("work/reconstructed_layers sem frame_*.png")

    from PIL import Image

    with Image.open(frames[0]) as probe:
        frame_w, frame_h = probe.size
    tiles_w, tiles_h = frame_w // 8, frame_h // 8
    plane_frames = _build_route_a_plane_frames(reconstruction, frame_w, frame_h)

    records: list[tuple[int, int, Counter]] = []
    for bg_b, bg_a in plane_frames:
        for plane_id, src in ((PLANE_BG_B, bg_b), (PLANE_BG_A, bg_a)):
            px = src.load()
            for ty in range(tiles_h):
                for tx in range(tiles_w):
                    cnt: Counter[tuple[int, int, int]] = Counter()
                    for y in range(8):
                        for x in range(8):
                            r, g, b, a = px[tx * 8 + x, ty * 8 + y]
                            if plane_id == PLANE_BG_A and a < 128:
                                continue
                            rr = (int(r) >> 5) & 0x7
                            gg = (int(g) >> 5) & 0x7
                            bb = (int(b) >> 5) & 0x7
                            cnt[(rr * 34, gg * 34, bb * 34)] += 1
                    if cnt:
                        records.append((ty, plane_id, cnt))
    return records


def assign_histograms(records, palettes):
    """E-step: pid por tile com a MESMA funcao do exporter."""
    hists: list[Counter] = [Counter() for _ in palettes]
    for ty, plane_id, cnt in records:
        # replica exatamente as bandas/contextos do exporter via a funcao original,
        # alimentada com uma lista fake ordenada por contador (a funcao so usa Counter)
        fake_rgbs = [rgb for rgb, w in cnt.items() for _ in range(min(w, 64))]
        pid = _contextual_palette_id_for_tile(fake_rgbs, palettes, 0, ty, plane_id)
        hists[pid].update(cnt)
    return hists


def fit_slots(hist: Counter, init_slots: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    colors = list(hist.keys())
    if not colors:
        return [tuple(s) for s in init_slots]

    def snap(c):
        return tuple(min(MD_LEVELS_LIST, key=lambda lv: (abs(lv - int(v)), lv)) for v in c)

    slots = []
    for c in init_slots[:K_SLOTS]:
        slots.append(snap(c))
    slots = _dedupe_pad(slots, hist)

    assign: dict = {}
    for _ in range(INNER_KMEANS_ITERS):
        moved = False
        dist = [[_rgb_distance_sq(c, s) for s in slots] for c in colors]
        new_assign = {}
        for i, c in enumerate(colors):
            best = min(range(K_SLOTS), key=lambda j: (dist[i][j], j))
            new_assign[c] = best
            if assign.get(c) != best:
                moved = True
        assign = new_assign
        if not moved:
            break
        for j in range(K_SLOTS):
            members = [(c, hist[c]) for c in colors if assign[c] == j]
            if not members:
                continue
            wsum = sum(w for _, w in members)
            slots[j] = snap(tuple(
                sum(c[k] * w for c, w in members) / wsum for k in range(3)
            ))
        slots = _dedupe_pad(slots, hist)
    return slots


def _dedupe_pad(slots, hist):
    seen: list = []
    for s in slots:
        if s not in seen:
            seen.append(s)
    if len(seen) >= K_SLOTS:
        return seen[:K_SLOTS]
    remaining = sorted(
        (c for c in hist.keys() if c not in seen),
        key=lambda c: (-hist[c], c),
    )
    return (seen + remaining)[:K_SLOTS]


def objective(palettes, hists):
    remapped = 0
    sq = 0
    for pid, hist in enumerate(hists):
        visible = palettes[pid][1:]
        for rgb, w in hist.items():
            d = min(_rgb_distance_sq(rgb, cand) for cand in visible)
            sq += d * w
            if d > 0:
                remapped += w
    return remapped, sq


def main() -> int:
    t0 = time.time()
    base = _route_a_palettes()
    palettes = [list(p) for p in base]

    print("[1/4] leitura unica dos planos...", flush=True)
    records = build_tile_records()
    total_px = sum(sum(c.values()) for _, _, c in records)
    print(f"      tiles={len(records)} pixels_visiveis={total_px} ({time.time()-t0:.0f}s)", flush=True)

    print("[2/4] baseline manual...", flush=True)
    hists = assign_histograms(records, palettes)
    base_remapped, base_sq = objective(palettes, hists)
    print(f"      manual: remaps~{base_remapped} ({base_remapped/max(total_px,1):.2%})", flush=True)

    print("[3/4] iteracoes Lloyd tile-aware...", flush=True)
    for outer in range(OUTER_ITERS):
        t_it = time.time()
        for pid in range(len(palettes)):
            slots = fit_slots(hists[pid], [tuple(p) for p in palettes[pid][1:]])
            palettes[pid] = [tuple(BACKDROP_MD_RGB)] + slots
        hists = assign_histograms(records, palettes)
        remapped, sq = objective(palettes, hists)
        print(f"      iter {outer+1}: remaps~{remapped} ({remapped/max(total_px,1):.2%}) ({time.time()-t_it:.0f}s)", flush=True)

    final_remapped, final_sq = objective(palettes, hists)

    report = {
        "schema_version": "1.0.0",
        "generator": "optimize_showdown_palettes.py",
        "method": "lloyd_tile_aware_kmeans_md9bit_index0_backdrop_singlepass",
        "k_slots": K_SLOTS,
        "outer_iterations": OUTER_ITERS,
        "deterministic": True,
        "metrics": {
            "total_visible_pixels": total_px,
            "baseline_manual_remapped": base_remapped,
            "optimized_remapped_estimate": final_remapped,
            "improvement_ratio": round(1 - (final_remapped / max(base_remapped, 1)), 4),
            "weighted_mean_dist_baseline": round((base_sq / max(total_px, 1)) ** 0.5, 3),
            "weighted_mean_dist_optimized": round((final_sq / max(total_px, 1)) ** 0.5, 3),
        },
        "palettes": [[[int(v) for v in rgb] for rgb in pal] for pal in palettes],
    }
    OUT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[4/4] OK -> {OUT_PATH.relative_to(ROOT)} | melhoria: {report['metrics']['improvement_ratio']:.2%}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
