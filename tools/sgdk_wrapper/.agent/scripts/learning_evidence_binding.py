#!/usr/bin/env python3
"""Small, dependency-free evidence-binding primitive for local learning records."""
from __future__ import annotations
import re
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

def evaluate(manifest: dict[str, Any], gates: list[dict[str, Any]]) -> dict[str, Any]:
    rom = str(manifest.get("rom_sha256", "")).lower()
    sealed = manifest.get("status") == "sealed"
    valid = bool(SHA256_RE.fullmatch(rom))
    mismatches = [str(gate.get("gate_id", "unnamed_gate")) for gate in gates if str(gate.get("rom_sha256", "")).lower() != rom]
    failed = [str(gate.get("gate_id", "unnamed_gate")) for gate in gates if gate.get("status") != "passed"]
    fresh = sealed and valid and bool(gates) and not mismatches and not failed
    return {
        "status": "fresh" if fresh else "stale",
        "evidence_grade": "E4_budget_and_regression" if fresh else "E3_blastem",
        "rom_sha256": rom or None,
        "binding_gaps": (["evidence_bundle_not_sealed"] if not sealed else []) + (["rom_sha256_invalid"] if not valid else []) + (["gate_report_reference_missing"] if not gates else []) + (["gate_report_rom_hash_mismatch"] if mismatches else []) + (["referenced_gate_not_passed"] if failed else []),
        "mismatches": mismatches,
        "failed_gates": failed,
    }
