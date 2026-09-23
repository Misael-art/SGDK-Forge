#!/usr/bin/env python3
"""Le o bloco TSTR da SRAM de evidencia do Showdown e emite report medido.

Uso:
  python3 read_tile_stream_stats.py <save.sram> <saida.json> [--capacity N]

Bloco (SRAM offset 0x300): magic "TSTR", u16 schema, u16 total_bytes,
8 contadores u32 big-endian:
  [0] tiles pedidos ao cache (acquires com sucesso)
  [1] tiles efetivamente enviados por DMA/VDP_loadTileData
  [2] chamadas de upload
  [3] eventos de overflow (pedido acima da capacidade)
  [4] pico de tiles residentes num unico passe de camera
  [5] CACHE_TILE_CAPACITY compilado na ROM
  [6] GLOBAL_UNIQUE_TILES compilado na ROM
  [7] magic interno 0x54533130 ("TS10")
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

TSTR_OFFSET = 0x300


def parse(sram_path: Path) -> dict:
    raw = sram_path.read_bytes()
    off = raw.find(b"TSTR", TSTR_OFFSET - 16)
    if off < 0:
        raise ValueError("tstr_block_missing")
    schema, total = struct.unpack_from(">HH", raw, off + 4)
    if schema not in (1, 2):
        raise ValueError(f"tstr_layout_unexpected schema={schema} total={total}")
    words = struct.unpack_from(">16H", raw, off + 8)
    stats = [(words[i * 2] << 16) | words[i * 2 + 1] for i in range(8)]
    rep = {
        "schema_version": "1.0.0",
        "tstr_schema": schema,
        "source": str(sram_path),
        "counters": {
            "tiles_requested_total": stats[0],
            "tiles_dma_uploaded_total": stats[1],
            "upload_calls_total": stats[2],
            "overflow_events_total": stats[3],
            "max_resident_single_pass": stats[4],
            "cache_capacity_compiled": stats[5],
            "global_unique_tiles_compiled": stats[6],
            "magic": f"0x{stats[7]:08X}",
        },
    }
    if schema >= 2:
        sw = struct.unpack_from(">11H", raw, off + 8 + 32)
        stop_names = ["center", "nw", "ne", "sw", "se"]
        stops = {}
        for i, name in enumerate(stop_names):
            stops[name] = {
                "peak_resident": sw[i],
                "tiles_requested": sw[5 + i],
                "recorded": bool(sw[10] & (1 << i)),
            }
        rep["corner_sweep"] = {"stops_done_mask": sw[10], "stops": stops}
    return rep


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    sram_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    capacity_override = None
    if "--capacity" in sys.argv:
        capacity_override = int(sys.argv[sys.argv.index("--capacity") + 1])

    rep = parse(sram_path)
    c = rep["counters"]
    cap = capacity_override or c["cache_capacity_compiled"]
    peak = c["max_resident_single_pass"]
    c["margin_tiles"] = cap - peak if cap else None
    c["margin_ratio"] = round((cap - peak) / cap, 4) if cap and cap > 0 else None
    c["overflow_consistent"] = (
        (c["overflow_events_total"] == 0) if peak and cap and peak <= cap else (c["overflow_events_total"] > 0)
    )
    verdict = {
        "code_loaded_tiles_measured": True,
        "peak_within_capacity": bool(cap and peak <= cap),
        "dma_bytes_total": c["tiles_dma_uploaded_total"] * 32,
    }
    sweep = rep.get("corner_sweep")
    if sweep and all(s["recorded"] for s in sweep["stops"].values()):
        worst_name, worst = max(
            sweep["stops"].items(), key=lambda kv: kv[1]["peak_resident"]
        )
        sweep["worst_stop"] = {
            "name": worst_name,
            "peak_resident": worst["peak_resident"],
            "margin_tiles": cap - worst["peak_resident"] if cap else None,
            "margin_ratio": round((cap - worst["peak_resident"]) / cap, 4) if cap else None,
        }
        verdict["sweep_all_within_capacity"] = bool(
            cap and all(s["peak_resident"] <= cap for s in sweep["stops"].values())
        )
        verdict["worst_margin_tiles"] = sweep["worst_stop"]["margin_tiles"]
    rep["verdict"] = verdict
    out_path.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep["counters"], indent=2))
    if sweep:
        print("corner_sweep:", json.dumps(sweep, indent=2))
    print("verdict:", json.dumps(verdict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
