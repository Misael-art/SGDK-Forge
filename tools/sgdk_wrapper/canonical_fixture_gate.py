#!/usr/bin/env python3
"""Evaluate reusable SGDK fixture contracts without inferring broad claims.

The evaluator is intentionally project-agnostic.  Projects provide measured
values; this module decides only whether those values support the declared
scope.  A green static contract is never promoted to gameplay or AAA proof.
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


TOOL_VERSION = "1.0.0"
SCOPES = {
    "static_contract",
    "runtime_observation",
    "visual_semantic",
    "hardware_state",
    "feature_readiness",
}
PASSING = {"passed", "warning", "not_applicable"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _result(
    gate_id: str,
    scope: str,
    status: str,
    code: str,
    *,
    required: bool = True,
    observations: dict[str, Any] | None = None,
    claim_limit: str,
) -> dict[str, Any]:
    if scope not in SCOPES:
        raise ValueError(f"unsupported_gate_scope:{scope}")
    return {
        "gate_id": gate_id,
        "scope": scope,
        "required": required,
        "status": status,
        "code": code,
        "observations": observations or {},
        "claim_limit": claim_limit,
    }


def evaluate_sampled_gate(spec: dict[str, Any]) -> dict[str, Any]:
    samples = int(spec.get("sample_count", 0))
    violations = int(spec.get("violation_count", 0))
    required = bool(spec.get("required", True))
    if samples <= 0:
        status = "failed" if required else "warning"
        return _result(
            str(spec.get("gate_id", "sampled_gate")),
            str(spec.get("scope", "runtime_observation")),
            status,
            "zero_sample_denominator",
            required=required,
            observations={"sample_count": samples, "violation_count": violations},
            claim_limit="Zero samples are vacuous and can never produce PASS.",
        )
    status = "passed" if violations == 0 else "failed"
    return _result(
        str(spec.get("gate_id", "sampled_gate")),
        str(spec.get("scope", "runtime_observation")),
        status,
        "sampled_gate_clean" if status == "passed" else "sampled_gate_violations",
        required=required,
        observations={"sample_count": samples, "violation_count": violations},
        claim_limit="The result covers only the sampled interval and declared scope.",
    )


def evaluate_telemetry(spec: dict[str, Any]) -> dict[str, Any]:
    block = spec.get("block") if isinstance(spec.get("block"), dict) else {}
    schema_version = str(block.get("schema_version", ""))
    total_words = block.get("total_words")
    required_fields = [str(value) for value in spec.get("required_fields", [])]
    optional_fields = [str(value) for value in spec.get("optional_fields", [])]
    missing_required = [field for field in required_fields if field not in block]
    missing_optional = [field for field in optional_fields if field not in block]
    version_valid = bool(re.fullmatch(r"[0-9]+(?:\.[0-9]+){0,2}", schema_version))
    length_valid = isinstance(total_words, int) and total_words >= len(block) - 2

    if not version_valid or not length_valid or missing_required:
        return _result(
            str(spec.get("gate_id", "telemetry_contract")),
            "static_contract",
            "failed",
            "telemetry_contract_incompatible",
            observations={
                "schema_version": schema_version or None,
                "total_words": total_words,
                "missing_required_fields": missing_required,
                "missing_optional_fields": missing_optional,
            },
            claim_limit="Malformed version/length or absent required fields block the consumer.",
        )
    return _result(
        str(spec.get("gate_id", "telemetry_contract")),
        "static_contract",
        "warning" if missing_optional else "passed",
        "telemetry_optional_fields_skipped" if missing_optional else "telemetry_compatible",
        observations={
            "schema_version": schema_version,
            "total_words": total_words,
            "missing_required_fields": [],
            "missing_optional_fields": missing_optional,
            "unknown_fields_tolerated": sorted(
                set(block) - {"schema_version", "total_words", *required_fields, *optional_fields}
            ),
        },
        claim_limit="Missing optional fields degrade to warning/SKIP; they never crash the report.",
    )


def evaluate_rom_playtest(spec: dict[str, Any]) -> dict[str, Any]:
    requested = int(spec.get("requested_mask", 0))
    observed = int(spec.get("observed_mask", 0))
    required_mask = int(spec.get("required_mask", 0))
    completed = bool(spec.get("completed", False))
    missing = required_mask & ~observed
    passed = completed and required_mask != 0 and missing == 0
    return _result(
        str(spec.get("gate_id", "rom_side_playtest")),
        "runtime_observation",
        "passed" if passed else "failed",
        "rom_observed_coverage_complete" if passed else "rom_observed_coverage_incomplete",
        observations={
            "requested_mask": requested,
            "observed_mask": observed,
            "required_mask": required_mask,
            "missing_observed_mask": missing,
            "completed": completed,
            "requested_is_not_evidence": True,
        },
        claim_limit="Only states observed by ROM-side logic count; requested input is informational.",
    )


def evaluate_raster_color(spec: dict[str, Any]) -> dict[str, Any]:
    cram_entries = int(spec.get("cram_entries_used", 0))
    illegal = int(spec.get("illegal_cram_entries", 0))
    screenshot_colors = int(spec.get("screenshot_unique_colors", 0))
    raster_updates = int(spec.get("mid_frame_palette_updates", 0))
    passed = 0 <= cram_entries <= 64 and illegal == 0
    return _result(
        str(spec.get("gate_id", "raster_color_truth")),
        "hardware_state",
        "passed" if passed else "failed",
        "cram_budget_valid" if passed else "cram_budget_invalid",
        observations={
            "cram_entries_used": cram_entries,
            "illegal_cram_entries": illegal,
            "screenshot_unique_colors": screenshot_colors,
            "mid_frame_palette_updates": raster_updates,
            "screenshot_color_count_informational": raster_updates > 0,
        },
        claim_limit=(
            "With mid-frame palette updates, screenshot color count cannot prove CRAM occupancy "
            "or RGB333 legality."
        ),
    )


def evaluate_identical_work(spec: dict[str, Any]) -> dict[str, Any]:
    camera_delta = int(spec.get("camera_delta", 0))
    before = str(spec.get("table_hash_before", ""))
    after = str(spec.get("table_hash_after", ""))
    rebuilds = int(spec.get("rebuild_count", 0))
    dma_bytes = int(spec.get("dma_bytes", 0))
    valid_hashes = bool(SHA256_RE.fullmatch(before) and SHA256_RE.fullmatch(after))
    if camera_delta == 0:
        passed = valid_hashes and before == after and rebuilds == 0 and dma_bytes == 0
        code = "identical_work_elided" if passed else "static_state_rebuilt_or_uploaded"
    else:
        passed = valid_hashes and rebuilds > 0
        code = "changed_state_rebuilt" if passed else "changed_state_not_rebuilt"
    return _result(
        str(spec.get("gate_id", "identical_work_elision")),
        "runtime_observation",
        "passed" if passed else "failed",
        code,
        observations={
            "camera_delta": camera_delta,
            "table_hash_before": before,
            "table_hash_after": after,
            "rebuild_count": rebuilds,
            "dma_bytes": dma_bytes,
        },
        claim_limit="This proves work elision only; it does not authorize visual degradation.",
    )


def evaluate_evidence_binding(spec: dict[str, Any]) -> dict[str, Any]:
    manifest = spec.get("manifest") if isinstance(spec.get("manifest"), dict) else {}
    gates = [item for item in spec.get("gate_reports", []) if isinstance(item, dict)]
    rom_hash = str(manifest.get("rom_sha256", "")).lower()
    sealed = manifest.get("status") == "sealed"
    valid_hash = bool(SHA256_RE.fullmatch(rom_hash))
    mismatches = [
        str(gate.get("gate_id", "unnamed_gate"))
        for gate in gates
        if str(gate.get("rom_sha256", "")).lower() != rom_hash
    ]
    failed_gates = [
        str(gate.get("gate_id", "unnamed_gate"))
        for gate in gates
        if gate.get("status") != "passed"
    ]
    passed = sealed and valid_hash and bool(gates) and not mismatches and not failed_gates
    return _result(
        str(spec.get("gate_id", "evidence_binding")),
        "feature_readiness",
        "passed" if passed else "failed",
        "evidence_bound_to_single_rom" if passed else "evidence_identity_unproven",
        observations={
            "manifest_status": manifest.get("status"),
            "rom_sha256": rom_hash or None,
            "gate_report_count": len(gates),
            "rom_hash_mismatch_gates": mismatches,
            "failed_gates": failed_gates,
        },
        claim_limit="Identity binding proves provenance, not gameplay, performance, audio or AAA quality.",
    )


def evaluate_scope(spec: dict[str, Any]) -> dict[str, Any]:
    declared = str(spec.get("declared_scope", ""))
    claimed = str(spec.get("claimed_scope", ""))
    source_status = str(spec.get("source_status", ""))
    valid = declared in SCOPES and claimed in SCOPES
    overclaim = declared == "static_contract" and claimed != "static_contract"
    passed = valid and source_status == "passed" and not overclaim
    return _result(
        str(spec.get("gate_id", "gate_scope")),
        "static_contract",
        "passed" if passed else "failed",
        "gate_scope_bounded" if passed else "gate_scope_overclaim_or_missing",
        observations={
            "declared_scope": declared or None,
            "claimed_scope": claimed or None,
            "source_status": source_status or None,
        },
        claim_limit="A static contract cannot become feature readiness by aggregation or naming.",
    )


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
    results: list[dict[str, Any]] = []
    for contract in contracts:
        if not isinstance(contract, dict):
            raise ValueError("fixture_contract_not_object")
        contract_type = str(contract.get("type", ""))
        evaluator = EVALUATORS.get(contract_type)
        if evaluator is None:
            raise ValueError(f"unsupported_fixture_contract:{contract_type}")
        results.append(evaluator(contract))

    blockers = [item["gate_id"] for item in results if item["required"] and item["status"] == "failed"]
    warnings = [item["gate_id"] for item in results if item["status"] == "warning"]
    report = {
        "schema_version": "1.0.0",
        "tool_name": "canonical_fixture_gate",
        "tool_version": TOOL_VERSION,
        "fixture_id": str(fixture.get("fixture_id", "unnamed_fixture")),
        "evidence_kind": str(fixture.get("evidence_kind", "runtime_or_unspecified")),
        "fixture_sha256": hashlib.sha256(
            json.dumps(fixture, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "status": "passed" if not blockers else "failed",
        "blockers": blockers,
        "warnings": warnings,
        "results": results,
        "ready_for_aaa": False,
        "claim_ceiling": "technical_fixture_contracts",
    }
    return report


def fixture_from_fref(
    sram_path: Path,
    *,
    rom_path: Path | None = None,
    evidence_manifest: Path | None = None,
    bound_gate_report: Path | None = None,
) -> dict[str, Any]:
    raw = sram_path.read_bytes()
    offset = raw.find(b"FREF")
    if offset < 0 or offset + 8 > len(raw):
        raise ValueError("fref_block_missing")
    schema_version, total_words = struct.unpack_from(">HH", raw, offset + 4)
    payload_end = offset + 8 + total_words * 2
    if total_words < 20 or payload_end > len(raw):
        raise ValueError("fref_block_truncated_or_incompatible")
    words = list(struct.unpack_from(f">{total_words}H", raw, offset + 8))
    cram_entries = words[14]
    illegal_cram_entries = words[15]
    vlab_offset = raw.find(b"VLAB")
    if vlab_offset >= 0 and vlab_offset + 8 <= len(raw):
        _, vlab_total_bytes = struct.unpack_from(">HH", raw, vlab_offset + 4)
        if vlab_total_bytes >= 8 + ((24 + 64) * 2) and vlab_offset + vlab_total_bytes <= len(raw):
            palette_offset = vlab_offset + 8 + (24 * 2)
            palette = struct.unpack_from(">64H", raw, palette_offset)
            cram_entries = 64
            illegal_cram_entries = sum(1 for value in palette if value & ~0x0EEE)
    before_hash = f"{((words[10] << 16) | words[11]):08x}".rjust(64, "0")
    after_hash = f"{((words[12] << 16) | words[13]):08x}".rjust(64, "0")
    contracts: list[dict[str, Any]] = [
        {
            "type": "sampled_gate_non_vacuity",
            "gate_id": "fref_static_table_samples",
            "scope": "runtime_observation",
            "sample_count": words[4],
            "violation_count": words[5],
        },
        {
            "type": "versioned_telemetry",
            "gate_id": "fref_telemetry_compatibility",
            "required_fields": ["requested_mask", "observed_mask", "required_mask", "completed"],
            "optional_fields": ["future_optional_word"],
            "block": {
                "schema_version": f"{schema_version}.0.0",
                "total_words": total_words,
                "requested_mask": words[0],
                "observed_mask": words[1],
                "required_mask": words[2],
                "completed": words[3],
            },
        },
        {
            "type": "rom_side_playtest",
            "gate_id": "fref_rom_side_playtest",
            "requested_mask": words[0],
            "observed_mask": words[1],
            "required_mask": words[2],
            "completed": words[3] != 0,
        },
        {
            "type": "raster_color_truth",
            "gate_id": "fref_cram_truth",
            "cram_entries_used": cram_entries,
            "illegal_cram_entries": illegal_cram_entries,
            "screenshot_unique_colors": 0,
            "mid_frame_palette_updates": words[16],
        },
        {
            "type": "identical_work_elision",
            "gate_id": "fref_static_table_elision",
            "camera_delta": 0,
            "table_hash_before": before_hash,
            "table_hash_after": after_hash,
            "rebuild_count": words[8],
            "dma_bytes": words[9],
        },
        {
            "type": "gate_scope",
            "gate_id": "fref_scope_boundary",
            "declared_scope": "runtime_observation",
            "claimed_scope": "runtime_observation",
            "source_status": "passed",
        },
    ]
    if evidence_manifest and bound_gate_report:
        contracts.append(
            {
                "type": "evidence_binding",
                "gate_id": "fref_evidence_binding",
                "manifest": json.loads(evidence_manifest.read_text(encoding="utf-8-sig")),
                "gate_reports": [json.loads(bound_gate_report.read_text(encoding="utf-8-sig"))],
            }
        )
    rom_sha256 = hashlib.sha256(rom_path.read_bytes()).hexdigest() if rom_path else None
    return {
        "fixture_id": "forge_reference_runtime_v1",
        "source": {
            "sram_path": str(sram_path),
            "fref_offset": offset,
            "rom_sha256": rom_sha256,
            "frame": (words[18] << 16) | words[19],
        },
        "contracts": contracts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fixture")
    source.add_argument("--fref-sram")
    parser.add_argument("--rom-path")
    parser.add_argument("--evidence-manifest")
    parser.add_argument("--bound-gate-report")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.fixture:
        fixture_path = Path(args.fixture).expanduser().resolve()
        fixture = json.loads(fixture_path.read_text(encoding="utf-8-sig"))
    else:
        fixture = fixture_from_fref(
            Path(args.fref_sram).expanduser().resolve(),
            rom_path=Path(args.rom_path).expanduser().resolve() if args.rom_path else None,
            evidence_manifest=Path(args.evidence_manifest).expanduser().resolve()
            if args.evidence_manifest
            else None,
            bound_gate_report=Path(args.bound_gate_report).expanduser().resolve()
            if args.bound_gate_report
            else None,
        )
    report = evaluate_fixture(fixture)
    if isinstance(fixture.get("source"), dict):
        report["source"] = fixture["source"]
        report["rom_sha256"] = fixture["source"].get("rom_sha256")
    payload = json.dumps(report, ensure_ascii=True, indent=2) + "\n"
    if args.output:
        destination = Path(args.output).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
