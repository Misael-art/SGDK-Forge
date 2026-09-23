#!/usr/bin/env python3
"""Backfill HPRB JSON reports for already captured P10 probe bundles."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "doc/engine/p10_qa_matrix.json"
DECODER = ROOT / "tests/analyze_hprb_probe.py"


def main() -> int:
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    rom = ROOT / "out/rom.bin"
    rom_sha = hashlib.sha256(rom.read_bytes()).hexdigest()
    failures = []
    decoded = 0
    for case in data["cases"]:
        bundle_value = case.get("bundle")
        if not bundle_value or case.get("runtime_status") != "probe_passed":
            continue
        bundle = ROOT / bundle_value
        sram = bundle / "userdata/blastem/rom/save.sram"
        report = bundle / "hprb_probe_report.json"
        if not sram.is_file():
            failures.append((case["id"], "SRAM missing"))
            continue
        result = subprocess.run(
            [sys.executable, str(DECODER), str(sram), "--rom", str(bundle / "rom.bin"), "--out", str(report)],
            cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode != 0:
            failures.append((case["id"], result.stderr[-800:]))
            continue
        case["hprb_report"] = str(report.relative_to(ROOT))
        case["rom_sha256"] = rom_sha
        decoded += 1
    MATRIX.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decoded": decoded, "failures": failures, "rom_sha256": rom_sha}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
