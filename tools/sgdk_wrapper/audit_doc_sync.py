#!/usr/bin/env python3
"""Audit active memory/changelog/report claims against the current ROM identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SHA_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def first_hash(text: str) -> str | None:
    match = SHA_RE.search(text)
    return match.group(0).lower() if match else None


def labeled_line_hash(text: str, label: str) -> str | None:
    for line in text.splitlines():
        if label.lower() in line.lower():
            value = first_hash(line)
            if value:
                return value
    return None


def json_hash(data: dict[str, Any] | None) -> str | None:
    if not data:
        return None
    direct = data.get("rom_sha256")
    if isinstance(direct, str) and SHA_RE.fullmatch(direct):
        return direct.lower()
    rom = data.get("rom")
    if isinstance(rom, dict):
        nested = rom.get("sha256")
        if isinstance(nested, str) and SHA_RE.fullmatch(nested):
            return nested.lower()
    return None


def audit(project: Path) -> dict[str, Any]:
    blockers: list[str] = []
    observations: list[dict[str, Any]] = []
    superseded: list[dict[str, Any]] = []
    rom_path = project / "out/rom.bin"
    current_hash = sha256(rom_path) if rom_path.is_file() else None
    if not current_hash:
        blockers.append("doc_sync_current_rom_missing")

    memory_path = project / "doc/10-memory-bank.md"
    changelog_path = project / "doc/changelog/changelog.md"
    memory = memory_path.read_text(encoding="utf-8-sig") if memory_path.is_file() else ""
    changelog = changelog_path.read_text(encoding="utf-8-sig") if changelog_path.is_file() else ""
    generated_match = re.search(r"<!-- SGDK GENERATED STATUS START -->(.*?)<!-- SGDK GENERATED STATUS END -->", memory, re.S)
    generated = generated_match.group(1) if generated_match else ""
    narrative = memory[generated_match.end():] if generated_match else memory

    doc_sources = {
        "memory_generated": labeled_line_hash(generated, "ROM vigente"),
        "memory_narrative": labeled_line_hash(narrative, "ROM vigente"),
        "changelog_latest": (SHA_RE.findall(changelog)[-1].lower() if SHA_RE.findall(changelog) else None),
    }
    for name, observed_hash in doc_sources.items():
        observations.append({"source": name, "rom_sha256": observed_hash, "active": True})
        if observed_hash is None:
            blockers.append(f"doc_sync_rom_identity_missing:{name}")
        elif current_hash and observed_hash != current_hash:
            blockers.append(f"doc_sync_rom_identity_mismatch:{name}")

    active_reports = {
        "emulator_session": project / "out/logs/emulator_session.json",
        "blastem_evidence": project / "out/logs/blastem_evidence.json",
        "runtime_metrics": project / "out/logs/runtime_metrics.json",
        "performance_capture": project / "out/logs/performance_capture_report.json",
        "claim_reconciliation": project / "out/logs/claim_reconciliation_report.json",
    }
    for name, path in active_reports.items():
        data = read_json(path)
        observed_hash = json_hash(data)
        observations.append({"source": name, "path": str(path.relative_to(project)), "rom_sha256": observed_hash, "active": True})
        if observed_hash is None:
            blockers.append(f"doc_sync_rom_identity_missing:{name}")
        elif current_hash and observed_hash != current_hash:
            blockers.append(f"doc_sync_rom_identity_mismatch:{name}")

    claim = read_json(active_reports["claim_reconciliation"]) or {}
    resolved = claim.get("resolved_claims") or {}
    generated_ready = bool(re.search(r"ready_for_aaa\s*[=:]\s*true", generated, re.I))
    narrative_ready = bool(re.search(r"ready_for_aaa\s*[=:]\s*true", narrative, re.I))
    if (generated_ready or narrative_ready) and resolved.get("ready_for_aaa") is not True:
        blockers.append("doc_sync_strong_status_contradiction:ready_for_aaa")
    generated_performance_stable = bool(re.search(r"performance\s*[=:].*estavel", generated, re.I))
    metrics = read_json(active_reports["runtime_metrics"]) or {}
    if generated_performance_stable and metrics.get("capture_status") != "ok":
        blockers.append("doc_sync_strong_status_contradiction:performance_partial")

    for path in sorted((project / "out/logs").glob("*.json")):
        if path in active_reports.values():
            continue
        data = read_json(path)
        observed_hash = json_hash(data)
        if observed_hash and current_hash and observed_hash != current_hash:
            superseded.append({"path": str(path.relative_to(project)), "rom_sha256": observed_hash, "active_claim": False})

    unique_blockers = list(dict.fromkeys(blockers))
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "audit_doc_sync",
        "tool_version": "1.0.0",
        "status": "ok" if not unique_blockers else "blocked",
        "policy": "current_rom_and_lowest_proven_status_win",
        "current_rom_sha256": current_hash,
        "active_sources": observations,
        "superseded_reports": superseded,
        "resolved_claims": resolved,
        "blockers": unique_blockers,
        "claim_limit": "Historical reports remain auditable but cannot act as current claims when their ROM differs.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    project = args.project_root.resolve()
    output = args.output if args.output.is_absolute() else project / args.output
    report = audit(project)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "blockers": report["blockers"], "superseded": len(report["superseded_reports"])}))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
