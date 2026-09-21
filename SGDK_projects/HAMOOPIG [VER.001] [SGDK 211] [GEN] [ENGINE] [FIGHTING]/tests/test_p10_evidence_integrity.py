#!/usr/bin/env python3
"""Fresh P10 cases must point to readable manifests from the current ROM."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
matrix = json.loads((ROOT / "doc/engine/p10_qa_matrix.json").read_text())
rom_sha = hashlib.sha256((ROOT / "out/rom.bin").read_bytes()).hexdigest()
observed = 0
for case in matrix["cases"]:
    if case.get("runtime_status") not in {"selection_passed", "probe_passed", "passed"}:
        continue
    observed += 1
    bundle = ROOT / case["bundle"]
    manifest = bundle / "manifest.json"
    data = json.loads(manifest.read_text())
    assert data["rom_sha256"] == rom_sha, case["id"]
    assert data["requested_p1"] == case["p1"], case["id"]
    assert data["requested_p2"] == case["p2"], case["id"]
    if case.get("runtime_status") == "probe_passed":
        report = ROOT / (case.get("probe_report") or case["hprb_report"])
        decoded = json.loads(report.read_text())
        assert decoded["rom_sha256"] == rom_sha, case["id"]
assert observed >= 1
summary = ROOT / "out/logs/p10_matrix_hprb_summary.json"
summary_data = json.loads(summary.read_text())
assert summary_data["cases_decoded"] == 36
assert summary_data["rom_sha256"] == rom_sha
print(f"PASS: {observed} P10 cases have current-ROM manifest evidence")
