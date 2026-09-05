#!/usr/bin/env python3
"""Validate a physical Mega Drive or FPGA evidence session without inventing attestation."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_PROOFS = {"boot", "input", "audio", "gameplay"}
FINAL_STATUSES = {"captured", "accepted", "rejected"}
PASS_DECISIONS = {"pass", "accepted_with_known_issue"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate(project_root: Path, manifest_path: Path, rom_path: Path) -> dict[str, Any]:
    blockers: list[str] = []
    manifest: dict[str, Any] = {}
    try:
        manifest = load_json(manifest_path)
    except FileNotFoundError:
        blockers.append("hardware_session_manifest_missing")
    except (OSError, json.JSONDecodeError):
        blockers.append("hardware_session_manifest_unreadable")

    actual_rom_sha = file_sha256(rom_path) if rom_path.is_file() else None
    if actual_rom_sha is None:
        blockers.append("hardware_test_rom_missing")

    if manifest:
        status = manifest.get("status")
        if status not in FINAL_STATUSES:
            blockers.append("hardware_test_pending_external_execution")
        if status == "rejected":
            blockers.append("hardware_test_rejected")

        device = manifest.get("device") or {}
        for field in ("kind", "manufacturer", "model", "revision", "video_standard"):
            if not device.get(field):
                blockers.append(f"hardware_device_field_missing:{field}")
        if device.get("kind") not in {"original_console", "fpga"}:
            blockers.append("hardware_device_kind_invalid")
        if not manifest.get("region"):
            blockers.append("hardware_region_missing")

        load_method = manifest.get("load_method") or {}
        for field in ("kind", "device", "firmware"):
            if not load_method.get(field):
                blockers.append(f"hardware_load_method_field_missing:{field}")

        declared_rom = manifest.get("rom") or {}
        declared_sha = str(declared_rom.get("sha256") or "").lower()
        if actual_rom_sha and declared_sha != actual_rom_sha:
            blockers.append("hardware_rom_hash_mismatch_current_rom")
        if actual_rom_sha and declared_rom.get("size_bytes") != rom_path.stat().st_size:
            blockers.append("hardware_rom_size_mismatch")

        blastem_manifest_path = project_root / "out/evidence/blastem/evidence_manifest.json"
        try:
            blastem_sha = str(load_json(blastem_manifest_path).get("rom_sha256") or "").lower()
            if declared_sha != blastem_sha:
                blockers.append("hardware_rom_hash_mismatch_blastem_bundle")
        except (OSError, json.JSONDecodeError):
            blockers.append("approved_blastem_manifest_missing_or_unreadable")

        observed_proofs: set[str] = set()
        captures = manifest.get("captures") or []
        if not captures:
            blockers.append("hardware_capture_missing")
        for index, capture in enumerate(captures):
            capture_path = project_root / str(capture.get("path") or "")
            if not capture_path.is_file() or capture_path.stat().st_size == 0:
                blockers.append(f"hardware_capture_file_missing_or_empty:{index}")
                continue
            actual_capture_sha = file_sha256(capture_path)
            if actual_capture_sha != str(capture.get("sha256") or "").lower():
                blockers.append(f"hardware_capture_hash_mismatch:{index}")
            observed_proofs.update(str(value) for value in capture.get("proves") or [])
        for proof in sorted(REQUIRED_PROOFS - observed_proofs):
            blockers.append(f"hardware_capture_proof_missing:{proof}")

        observations = manifest.get("observations") or {}
        for field in ("boot", "input", "audio", "gameplay"):
            if observations.get(field) != "pass":
                blockers.append(f"hardware_observation_not_passed:{field}")
        for field in ("timing_decision", "audio_decision"):
            if observations.get(field) not in PASS_DECISIONS:
                blockers.append(f"hardware_decision_not_accepted:{field}")

        attestation = manifest.get("tester_attestation") or {}
        if not attestation.get("performed_by") or not attestation.get("performed_at"):
            blockers.append("hardware_tester_identity_or_time_missing")
        if attestation.get("truthful") is not True:
            blockers.append("hardware_tester_attestation_missing")

    unique_blockers = list(dict.fromkeys(blockers))
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "validate_hardware_session",
        "tool_version": "1.0.0",
        "status": "ok" if not unique_blockers else "blocked",
        "session_id": manifest.get("session_id") if manifest else None,
        "manifest_status": manifest.get("status") if manifest else None,
        "rom_sha256": actual_rom_sha,
        "capture_count": len(manifest.get("captures") or []) if manifest else 0,
        "blockers": unique_blockers,
        "claim_limit": "Only an externally performed, attested session with matching ROM and capture can pass this gate.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    manifest_path = args.manifest if args.manifest.is_absolute() else project_root / args.manifest
    rom_path = args.rom if args.rom.is_absolute() else project_root / args.rom
    output_path = args.output if args.output.is_absolute() else project_root / args.output
    report = validate(project_root, manifest_path.resolve(), rom_path.resolve())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "blockers": report["blockers"]}))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
