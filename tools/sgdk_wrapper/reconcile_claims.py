#!/usr/bin/env python3
"""Resolve delivery claims using the lowest status proven by canonical reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.0.0"


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as exc:
        return None, str(exc)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _first(data: dict[str, Any], paths: tuple[tuple[str, ...], ...]) -> Any:
    for path in paths:
        value = _nested(data, *path)
        if value is not None:
            return value
    return None


def _as_bool(value: Any) -> bool | None:
    return value if isinstance(value, bool) else None


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _is_blocked_status(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    if normalized in {"", "none", "ok", "passed", "pass", "sealed", "accepted"}:
        return False
    return any(token in normalized for token in ("block", "error", "fail", "reject", "stale", "invalid", "missing"))


def _perceptual_zero(data: dict[str, Any]) -> bool:
    candidate = _first(
        data,
        (
            ("perceptual_check",),
            ("runtime_metrics", "perceptual_check"),
            ("metrics", "perceptual_check"),
        ),
    )
    if not isinstance(candidate, dict) or not candidate:
        return False
    values = [value for value in candidate.values() if isinstance(value, (int, float)) and not isinstance(value, bool)]
    return bool(values) and all(float(value) <= 0.0 for value in values)


def _candidate_paths(project_root: Path, include_validation_report: bool) -> list[tuple[str, Path]]:
    candidates = [
        ("visual_delivery_gate_runtime", project_root / "out/logs/visual_delivery_gate_report.json"),
        ("visual_delivery_gate_contract", project_root / "doc/contracts/visual_delivery_gate_report.json"),
        ("runtime_admission", project_root / "doc/contracts/runtime_admission_report.json"),
        ("runtime_metrics", project_root / "out/logs/runtime_metrics.json"),
        ("emulator_session", project_root / "out/logs/emulator_session.json"),
        ("screenshot_semantic_gate", project_root / "out/logs/screenshot_semantic_gate_report.json"),
        ("evidence_closeout", project_root / "out/logs/evidence_closeout_report.json"),
    ]
    if include_validation_report:
        candidates.insert(0, ("validation_report", project_root / "out/logs/validation_report.json"))
    return candidates


def reconcile(project_root: str | Path, include_validation_report: bool = True) -> dict[str, Any]:
    root = Path(project_root).expanduser().resolve()
    report_entries: list[dict[str, Any]] = []
    blockers: list[str] = []
    conflict_reasons: list[str] = []
    ready_values: list[bool] = []
    technical_values: list[bool] = []
    creative_values: list[bool] = []
    performance_values: list[str] = []
    rom_identities: dict[str, str] = {}
    session_identities: dict[str, str] = {}
    strong_claim_present = False
    blocked_report_present = False
    partial_capture = False
    perceptual_zero = False

    for name, path in _candidate_paths(root, include_validation_report):
        if not path.is_file():
            continue
        data, error = _read_json(path)
        entry: dict[str, Any] = {
            "name": name,
            "path": str(path),
            "sha256": _sha256(path),
            "readable": error is None,
            "read_error": error,
        }
        if data is None:
            blockers.append("claim_source_report_unreadable")
            blocked_report_present = True
            report_entries.append(entry)
            continue

        ready = _as_bool(_first(data, (("ready_for_aaa",), ("status_panel", "ready_for_aaa"))))
        technical = _as_bool(_first(data, (("technical_ready",), ("status_panel", "technical_ready"))))
        creative = _as_bool(_first(data, (("creative_ready",), ("status_panel", "creative_ready"))))
        performance = _first(data, (("performance",), ("qa_axes", "performance")))
        capture_status = _first(data, (("capture_status",), ("runtime_capture", "capture_status")))
        blocking_values = []
        for field_path in (
            ("blocking_statuses",),
            ("creative_blocking_statuses",),
            ("status_panel", "closing_blockers"),
        ):
            blocking_values.extend(_strings(_nested(data, *field_path)))
        blocking_status = _first(data, (("blocking_status",), ("status",), ("seal_status",)))
        runtime_admitted = _as_bool(data.get("runtime_admitted"))
        semantic_valid = _as_bool(data.get("semantic_capture_valid"))

        entry_blocked = bool(blocking_values) or _is_blocked_status(blocking_status)
        if runtime_admitted is False and _strings(data.get("forbidden_claims")):
            entry_blocked = True
        if semantic_valid is False:
            entry_blocked = True
        if ready is True or technical is True or creative is True or str(performance).lower() in {"estavel", "stable", "ok"}:
            strong_claim_present = True
        if entry_blocked:
            blocked_report_present = True

        if ready is not None:
            ready_values.append(ready)
        if technical is not None:
            technical_values.append(technical)
        if creative is not None:
            creative_values.append(creative)
        if isinstance(performance, str) and performance.strip():
            performance_values.append(performance.strip().lower())

        is_partial = isinstance(capture_status, str) and capture_status.strip().lower() in {"partial", "incomplete", "truncated"}
        partial_capture = partial_capture or is_partial
        entry_perceptual_zero = _perceptual_zero(data)
        perceptual_zero = perceptual_zero or entry_perceptual_zero

        rom_sha256 = _first(
            data,
            (
                ("rom_sha256",),
                ("current_rom_sha256",),
                ("captured_rom_sha256",),
                ("evidence", "rom_sha256"),
                ("rom", "sha256"),
            ),
        )
        session_id = _first(
            data,
            (
                ("session_id",),
                ("evidence_session_id",),
                ("emulator_session_id",),
                ("evidence", "emulator_session_id"),
            ),
        )
        if isinstance(rom_sha256, str) and len(rom_sha256.strip()) == 64:
            rom_identities[name] = rom_sha256.strip().lower()
        if isinstance(session_id, str) and session_id.strip():
            session_identities[name] = session_id.strip()

        entry.update(
            {
                "ready_for_aaa": ready,
                "technical_ready": technical,
                "creative_ready": creative,
                "performance": performance,
                "capture_status": capture_status,
                "perceptual_metrics_zero": entry_perceptual_zero,
                "blocked": entry_blocked,
                "blocking_statuses": blocking_values,
                "rom_sha256": rom_identities.get(name),
                "session_id": session_identities.get(name),
            }
        )
        report_entries.append(entry)

    if not report_entries:
        blockers.append("claim_sources_missing")

    if partial_capture:
        blockers.append("runtime_capture_partial")
        if any(value in {"estavel", "stable", "ok"} for value in performance_values):
            conflict_reasons.append("partial_capture_conflicts_with_stable_performance")
    if perceptual_zero:
        blockers.append("perceptual_metrics_zero")
        if True in creative_values:
            conflict_reasons.append("zero_perceptual_metrics_conflict_with_creative_ready")
    if blocked_report_present and (True in ready_values or True in technical_values or True in creative_values):
        conflict_reasons.append("blocked_report_conflicts_with_positive_ready_claim")
    if len(set(ready_values)) > 1 or len(set(technical_values)) > 1 or len(set(creative_values)) > 1:
        conflict_reasons.append("ready_claims_diverge_between_reports")

    unique_roms = sorted(set(rom_identities.values()))
    unique_sessions = sorted(set(session_identities.values()))
    identity_reports = [entry for entry in report_entries if entry["name"] in {
        "visual_delivery_gate_runtime",
        "visual_delivery_gate_contract",
        "runtime_metrics",
        "emulator_session",
        "screenshot_semantic_gate",
        "evidence_closeout",
    }]
    missing_rom_reports = [entry["name"] for entry in identity_reports if not entry.get("rom_sha256")]
    missing_session_reports = [entry["name"] for entry in identity_reports if not entry.get("session_id")]
    if len(unique_roms) > 1:
        blockers.append("report_rom_identity_mismatch")
        conflict_reasons.append("reports_reference_different_roms")
    if len(unique_sessions) > 1:
        blockers.append("report_evidence_session_mismatch")
        conflict_reasons.append("reports_reference_different_evidence_sessions")
    if strong_claim_present and missing_rom_reports:
        blockers.append("report_rom_identity_missing")
        conflict_reasons.append("positive_claim_report_set_lacks_rom_identity")
    if strong_claim_present and missing_session_reports:
        blockers.append("report_evidence_session_missing")
        conflict_reasons.append("positive_claim_report_set_lacks_evidence_session")
    if conflict_reasons:
        blockers.append("report_status_conflict")

    blockers = list(dict.fromkeys(blockers))
    conflict_reasons = list(dict.fromkeys(conflict_reasons))
    performance_resolved = "unproven"
    if not partial_capture and performance_values and all(value in {"estavel", "stable", "ok"} for value in performance_values):
        performance_resolved = "stable"
    creative_resolved = bool(creative_values) and all(creative_values) and not perceptual_zero and not blocked_report_present
    technical_resolved = bool(technical_values) and all(technical_values) and not partial_capture and not blocked_report_present
    ready_resolved = bool(ready_values) and all(ready_values) and technical_resolved and creative_resolved and not blockers

    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "reconcile_claims",
        "tool_version": TOOL_VERSION,
        "project_root": str(root),
        "status": "passed" if not blockers else "blocked",
        "policy": "lowest_proven_status_wins",
        "include_validation_report": include_validation_report,
        "blocking_statuses": blockers,
        "conflict_reasons": conflict_reasons,
        "resolved_claims": {
            "ready_for_aaa": ready_resolved,
            "technical_ready": technical_resolved,
            "creative_ready": creative_resolved,
            "performance": performance_resolved,
        },
        "observations": {
            "partial_capture": partial_capture,
            "perceptual_metrics_zero": perceptual_zero,
            "blocked_report_present": blocked_report_present,
            "strong_claim_present": strong_claim_present,
        },
        "identity_reconciliation": {
            "rom_sha256_values": unique_roms,
            "session_id_values": unique_sessions,
            "missing_rom_identity_reports": missing_rom_reports,
            "missing_session_id_reports": missing_session_reports,
            "same_rom": len(unique_roms) == 1 and not missing_rom_reports,
            "same_evidence_session": len(unique_sessions) == 1 and not missing_session_reports,
        },
        "reports": report_entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--exclude-validation-report", action="store_true")
    args = parser.parse_args()
    report = reconcile(args.project_root, include_validation_report=not args.exclude_validation_report)
    destination = Path(args.output).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
