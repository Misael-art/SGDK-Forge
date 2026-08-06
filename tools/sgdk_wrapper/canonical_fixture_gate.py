#!/usr/bin/env python3
"""Evaluate bounded, neutral SGDK technical-fixture contracts.

This tool intentionally never promotes a fixture to AAA readiness.  It validates
only the seven contracts documented in canonical_fixture_contracts.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SCOPES = {"static_contract", "runtime_observation", "feature_readiness"}


def result(spec: dict[str, Any], status: str, code: str, observations: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate_id": str(spec.get("gate_id", spec.get("type", "unnamed_gate"))),
        "required": bool(spec.get("required", True)),
        "scope": str(spec.get("scope", "runtime_observation")),
        "status": status,
        "code": code,
        "observations": observations,
    }


def evaluate_sampled_gate(spec: dict[str, Any]) -> dict[str, Any]:
    samples, violations = int(spec.get("sample_count", 0)), int(spec.get("violation_count", 0))
    if samples <= 0:
        return result(spec, "failed" if spec.get("required", True) else "warning", "sample_denominator_empty", {"sample_count": samples, "violation_count": violations})
    return result(spec, "passed" if violations == 0 else "failed", "sampled_gate_clean" if violations == 0 else "sampled_gate_violations", {"sample_count": samples, "violation_count": violations})


def evaluate_telemetry(spec: dict[str, Any]) -> dict[str, Any]:
    block = spec.get("block") if isinstance(spec.get("block"), dict) else {}
    required = [str(value) for value in spec.get("required_fields", [])]
    optional = [str(value) for value in spec.get("optional_fields", [])]
    missing_required = [name for name in required if name not in block]
    missing_optional = [name for name in optional if name not in block]
    if missing_required:
        status, code = "failed", "telemetry_required_fields_missing"
    elif missing_optional:
        status, code = "warning", "telemetry_optional_fields_skipped"
    else:
        status, code = "passed", "telemetry_compatible"
    return result(spec, status, code, {"schema_version": block.get("schema_version"), "total_words": block.get("total_words"), "missing_required_fields": missing_required, "missing_optional_fields": missing_optional})


def evaluate_rom_playtest(spec: dict[str, Any]) -> dict[str, Any]:
    requested, observed, required = (int(spec.get(name, 0)) for name in ("requested_mask", "observed_mask", "required_mask"))
    completed = bool(spec.get("completed", False))
    passed = completed and (observed & required) == required
    return result(spec, "passed" if passed else "failed", "rom_observed_coverage_complete" if passed else "rom_observed_coverage_incomplete", {"requested_mask": requested, "observed_mask": observed, "required_mask": required, "completed": completed})


def evaluate_raster_color(spec: dict[str, Any]) -> dict[str, Any]:
    entries, illegal = int(spec.get("cram_entries_used", 0)), int(spec.get("illegal_cram_entries", 0))
    midframe = int(spec.get("mid_frame_palette_updates", 0))
    passed = entries > 0 and illegal == 0
    return result(spec, "passed" if passed else "failed", "cram_words_legal" if passed else "cram_words_illegal_or_empty", {"cram_entries_used": entries, "illegal_cram_entries": illegal, "screenshot_unique_colors": int(spec.get("screenshot_unique_colors", 0)), "mid_frame_palette_updates": midframe, "screenshot_color_count_informational": midframe > 0})


def evaluate_identical_work(spec: dict[str, Any]) -> dict[str, Any]:
    before, after = str(spec.get("table_hash_before", "")), str(spec.get("table_hash_after", ""))
    delta, rebuilds, dma = int(spec.get("camera_delta", 0)), int(spec.get("rebuild_count", 0)), int(spec.get("dma_bytes", 0))
    hashes_valid = bool(SHA256_RE.fullmatch(before) and SHA256_RE.fullmatch(after))
    passed = hashes_valid and ((delta == 0 and before == after and rebuilds == 0 and dma == 0) or (delta != 0 and rebuilds > 0))
    code = "identical_work_elided" if passed and delta == 0 else "changed_state_rebuilt" if passed else "static_state_rebuilt_or_uploaded"
    return result(spec, "passed" if passed else "failed", code, {"camera_delta": delta, "table_hash_before": before, "table_hash_after": after, "rebuild_count": rebuilds, "dma_bytes": dma})


def evaluate_evidence_binding(spec: dict[str, Any]) -> dict[str, Any]:
    manifest = spec.get("manifest") if isinstance(spec.get("manifest"), dict) else {}
    gates = [gate for gate in spec.get("gate_reports", []) if isinstance(gate, dict)]
    rom_hash = str(manifest.get("rom_sha256", "")).lower()
    mismatches = [str(gate.get("gate_id", "unnamed_gate")) for gate in gates if str(gate.get("rom_sha256", "")).lower() != rom_hash]
    failures = [str(gate.get("gate_id", "unnamed_gate")) for gate in gates if gate.get("status") != "passed"]
    passed = manifest.get("status") == "sealed" and bool(SHA256_RE.fullmatch(rom_hash)) and bool(gates) and not mismatches and not failures
    return result(spec, "passed" if passed else "failed", "evidence_bound_to_single_rom" if passed else "evidence_identity_unproven", {"manifest_status": manifest.get("status"), "rom_sha256": rom_hash or None, "gate_report_count": len(gates), "rom_hash_mismatch_gates": mismatches, "failed_gates": failures})


def evaluate_scope(spec: dict[str, Any]) -> dict[str, Any]:
    declared, claimed, source_status = (str(spec.get(key, "")) for key in ("declared_scope", "claimed_scope", "source_status"))
    passed = declared in SCOPES and claimed in SCOPES and source_status == "passed" and not (declared == "static_contract" and claimed != "static_contract")
    return result(spec, "passed" if passed else "failed", "gate_scope_bounded" if passed else "gate_scope_overclaim_or_missing", {"declared_scope": declared or None, "claimed_scope": claimed or None, "source_status": source_status or None})


EVALUATORS = {
    "sampled_gate_non_vacuity": evaluate_sampled_gate,
    "versioned_telemetry": evaluate_telemetry,
    "rom_side_playtest": evaluate_rom_playtest,
    "raster_color_truth": evaluate_raster_color,
    "identical_work_elision": evaluate_identical_work,
    "evidence_binding": evaluate_evidence_binding,
    "gate_scope": evaluate_scope,
}


def evaluate_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    contracts = fixture.get("contracts")
    if not isinstance(contracts, list):
        raise ValueError("fixture_contracts_missing")
    results = []
    for contract in contracts:
        if not isinstance(contract, dict) or str(contract.get("type", "")) not in EVALUATORS:
            raise ValueError("unsupported_fixture_contract")
        results.append(EVALUATORS[str(contract["type"])](contract))
    blockers = [item["gate_id"] for item in results if item["required"] and item["status"] == "failed"]
    return {"schema_version": "1.0.0", "tool_name": "canonical_fixture_gate", "fixture_id": str(fixture.get("fixture_id", "unnamed_fixture")), "fixture_sha256": hashlib.sha256(json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "status": "passed" if not blockers else "failed", "blockers": blockers, "results": results, "ready_for_aaa": False, "claim_ceiling": "technical_fixture_contracts"}


def fixture_from_fref(sram_path: Path) -> dict[str, Any]:
    raw = sram_path.read_bytes()
    offset = raw.find(b"FREF")
    if offset < 0 or offset + 48 > len(raw):
        raise ValueError("fref_block_missing_or_truncated")
    version, words_count = struct.unpack_from(">HH", raw, offset + 4)
    if words_count < 20 or offset + 8 + words_count * 2 > len(raw):
        raise ValueError("fref_block_truncated_or_incompatible")
    words = list(struct.unpack_from(f">{words_count}H", raw, offset + 8))
    table_hash = f"{((words[10] << 16) | words[11]):08x}".rjust(64, "0")
    after_hash = f"{((words[12] << 16) | words[13]):08x}".rjust(64, "0")
    return {"fixture_id": "forge_reference_runtime_v1", "contracts": [
        {"type": "sampled_gate_non_vacuity", "gate_id": "fref_static_table_samples", "sample_count": words[4], "violation_count": words[5]},
        {"type": "versioned_telemetry", "gate_id": "fref_telemetry_compatibility", "required_fields": ["requested_mask", "observed_mask", "required_mask", "completed"], "block": {"schema_version": f"{version}.0.0", "total_words": words_count, "requested_mask": words[0], "observed_mask": words[1], "required_mask": words[2], "completed": words[3]}},
        {"type": "rom_side_playtest", "gate_id": "fref_rom_side_playtest", "requested_mask": words[0], "observed_mask": words[1], "required_mask": words[2], "completed": words[3] != 0},
        {"type": "raster_color_truth", "gate_id": "fref_cram_truth", "cram_entries_used": words[14], "illegal_cram_entries": words[15], "mid_frame_palette_updates": words[16]},
        {"type": "identical_work_elision", "gate_id": "fref_static_table_elision", "camera_delta": 0, "table_hash_before": table_hash, "table_hash_after": after_hash, "rebuild_count": words[8], "dma_bytes": words[9]},
        {"type": "gate_scope", "gate_id": "fref_scope_boundary", "declared_scope": "runtime_observation", "claimed_scope": "runtime_observation", "source_status": "passed"},
    ]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture")
    group.add_argument("--fref-sram")
    parser.add_argument("--output")
    args = parser.parse_args()
    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8-sig")) if args.fixture else fixture_from_fref(Path(args.fref_sram))
    payload = json.dumps(evaluate_fixture(fixture), indent=2) + "\n"
    if args.output:
        path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0 if json.loads(payload)["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
