"""Le as metricas de desempenho da save.sram de uma captura BlastEm do Mugenesis.

Uso: read_sram_metrics.py <pasta de captura> [symbol.txt]

- MDRT (sonda canonica): over_budget com denominador pos-warmup ([30]),
  pico de sprites e de PIXELS por linha ([20]/[21]/[22]).
- PCHS (so ROM com -DMG_PCPROF): histograma de PC por H-Int, agregado por simbolo
  com o symbol.txt do mesmo build; e o histograma so dos quadros acima do orcamento.
"""
import bisect
import collections
import glob
import json
import os
import struct
import sys


def _session(path):
    if os.path.exists(os.path.join(path, "save.sram")):
        return path
    return sorted(glob.glob(os.path.join(path, "*/")))[-1]


def mdrt(raw):
    i = raw.find(b"MDRT")
    n = struct.unpack(">H", raw[i + 8:i + 10])[0]
    w = struct.unpack(">%dH" % n, raw[i + 10:i + 10 + 2 * n])
    measured = w[30]
    return {
        "scene_id": w[5],
        "scene_frames": w[8],
        "measured_post_warmup": measured,
        "over_budget": w[10],
        "over_budget_pct_post_warmup": round(100 * w[10] / measured, 1) if measured else None,
        "max_cpu": w[11],
        "max_line_sprites": w[14],
        "frames_line_sprites_gt20": w[22],
        "max_line_px": w[20],
        "frames_line_px_gt_screen": w[21],
    }


def _by_symbol(hist, bucket, symfile):
    syms = sorted((int(a, 16), n) for a, t, n in
                  (l.split() for l in open(symfile) if len(l.split()) == 3) if t in "tT")
    addrs = [a for a, _ in syms]
    out = collections.Counter()
    for b, n in enumerate(hist):
        if not n:
            continue
        lo, hi = b * bucket, (b + 1) * bucket
        j = bisect.bisect_right(addrs, lo) - 1
        while j < len(syms) and (j < 0 or syms[j][0] < hi):
            s = max(lo, syms[j][0] if j >= 0 else 0)
            e = min(hi, syms[j + 1][0] if j + 1 < len(syms) else hi)
            if e > s:
                out[syms[j][1] if j >= 0 else "?"] += n * (e - s) / bucket
            j += 1
    total = sum(hist) or 1
    return [(name, round(100 * v / total, 1)) for name, v in out.most_common(25)]


def pchs(raw, symfile):
    i = raw.find(b"PCHS")
    if i < 0:
        return None
    base = i - 0x2000
    hist = struct.unpack(">4096H", raw[i + 4:i + 4 + 8192])
    frames, spikes = struct.unpack(">HH", raw[base + 0x4004:base + 0x4008])
    spike_hist = struct.unpack(">2048H", raw[base + 0x4008:base + 0x4008 + 4096])
    return {
        "samples": sum(hist),
        "all_frames": _by_symbol(hist, 64, symfile),
        "frames": frames,
        "over_budget_frames": spikes,
        "over_budget_only": _by_symbol(spike_hist, 128, symfile),
    }


def main(argv):
    d = _session(argv[1])
    raw = open(os.path.join(d, "save.sram"), "rb").read()
    out = {"session": d, "mdrt": mdrt(raw)}
    if len(argv) > 2:
        out["pc_profile"] = pchs(raw, argv[2])
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv)
