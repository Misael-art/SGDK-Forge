#!/usr/bin/env python3
"""Thirty-six checks for the main-compatible learning evidence-binding guard."""
from __future__ import annotations
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".agent" / "scripts" / "learning_evidence_binding.py"
spec = importlib.util.spec_from_file_location("binding", SCRIPT)
binding = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(binding)
SHA_A, SHA_B = "a" * 64, "b" * 64
passed = total = 0

def check(name: str, actual, expected) -> None:
    global passed, total
    total += 1
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")
    passed += 1
    print(f"[PASS] {name}")

def run_case(name: str, manifest, gates, expected_status, expected_grade, expected_gap, expected_mismatch, expected_failed) -> None:
    report = binding.evaluate(manifest, gates)
    check(f"{name}: status", report["status"], expected_status)
    check(f"{name}: grade", report["evidence_grade"], expected_grade)
    check(f"{name}: gap", expected_gap in report["binding_gaps"], expected_gap is not None)
    check(f"{name}: mismatch count", len(report["mismatches"]), expected_mismatch)
    check(f"{name}: failed count", len(report["failed_gates"]), expected_failed)
    check(f"{name}: hash echo", report["rom_sha256"], str(manifest.get("rom_sha256", "")).lower() or None)

def main() -> int:
    run_case("sealed_matching", {"status": "sealed", "rom_sha256": SHA_A}, [{"gate_id": "runtime", "status": "passed", "rom_sha256": SHA_A}], "fresh", "E4_budget_and_regression", None, 0, 0)
    run_case("unsealed", {"status": "open", "rom_sha256": SHA_A}, [{"gate_id": "runtime", "status": "passed", "rom_sha256": SHA_A}], "stale", "E3_blastem", "evidence_bundle_not_sealed", 0, 0)
    run_case("invalid_hash", {"status": "sealed", "rom_sha256": "invalid"}, [{"gate_id": "runtime", "status": "passed", "rom_sha256": "invalid"}], "stale", "E3_blastem", "rom_sha256_invalid", 0, 0)
    run_case("missing_gate", {"status": "sealed", "rom_sha256": SHA_A}, [], "stale", "E3_blastem", "gate_report_reference_missing", 0, 0)
    run_case("hash_mismatch", {"status": "sealed", "rom_sha256": SHA_A}, [{"gate_id": "runtime", "status": "passed", "rom_sha256": SHA_B}], "stale", "E3_blastem", "gate_report_rom_hash_mismatch", 1, 0)
    run_case("failed_gate", {"status": "sealed", "rom_sha256": SHA_A}, [{"gate_id": "runtime", "status": "failed", "rom_sha256": SHA_A}], "stale", "E3_blastem", "referenced_gate_not_passed", 0, 1)
    print(f"{passed}/{total} passed")
    return 0 if passed == total == 36 else 1

if __name__ == "__main__": raise SystemExit(main())
