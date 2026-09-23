#!/usr/bin/env python3
"""Summarize per-case HPRB probes without collapsing visual/audio status."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "doc/engine/p10_qa_matrix.json"
OUT = ROOT / "out/logs/p10_matrix_hprb_summary.json"


def main() -> int:
    matrix = json.loads(MATRIX.read_text())
    rom_sha = hashlib.sha256((ROOT / "out/rom.bin").read_bytes()).hexdigest()
    rows = []
    for case in matrix["cases"]:
        if case.get("runtime_status") not in {"probe_passed", "passed"}:
            continue
        report_path = case.get("probe_report") or case.get("hprb_report")
        if not report_path:
            continue
        report = json.loads((ROOT / report_path).read_text())
        if report.get("rom_sha256") != rom_sha:
            raise SystemExit(f"ROM mismatch in {case['id']}")
        rows.append({
            "id": case["id"],
            "stage": case["stage"],
            "region": case["region"],
            "video_frame": report.get("video_frame"),
            "peak_dma_queued_bytes": report.get("max_dma_queued_bytes"),
            "peak_active_sprites": report.get("max_active_sprites"),
            "peak_vdp_sprites": report.get("max_vdp_sprites"),
            "peak_sprites_per_scanline": report.get("max_sprites_per_scanline"),
            "combat_total_events": report.get("combat_total_events"),
            "combat_total_hits": report.get("combat_total_hits"),
            "warnings": report.get("warnings", []),
        })
    numeric = ("peak_dma_queued_bytes", "peak_active_sprites", "peak_vdp_sprites", "peak_sprites_per_scanline")
    maxima = {key: max((row[key] for row in rows if row[key] is not None), default=None) for key in numeric}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "schema_version": "1.0.0",
        "rom_sha256": rom_sha,
        "cases_decoded": len(rows),
        "maxima": maxima,
        "cases": rows,
        "claim_limit": "HPRB runtime probe only; no visual/audio/sensory approval",
    }, indent=2) + "\n")
    print(json.dumps({"cases_decoded": len(rows), "maxima": maxima, "rom_sha256": rom_sha}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
