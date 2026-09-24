#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


AUDITOR = Path(__file__).resolve().parents[1] / "audit_doc_sync.py"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def fixture(root: Path, doc_hash: str | None = None, ready: bool = False, partial: bool = False) -> str:
    rom = root / "out/rom.bin"
    rom.parent.mkdir(parents=True, exist_ok=True)
    rom.write_bytes(b"DOC-SYNC-ROM")
    rom_hash = hashlib.sha256(rom.read_bytes()).hexdigest()
    shown_hash = doc_hash or rom_hash
    memory = root / "doc/10-memory-bank.md"
    memory.parent.mkdir(parents=True)
    memory.write_text(
        "<!-- SGDK GENERATED STATUS START -->\n"
        f"- ROM vigente: `{shown_hash}`\n"
        f"- ready_for_aaa={'true' if ready else 'false'}\n"
        "- performance=estavel\n"
        "<!-- SGDK GENERATED STATUS END -->\n"
        f"- ROM vigente: SHA-256 `{shown_hash}`\n",
        encoding="utf-8",
    )
    changelog = root / "doc/changelog/changelog.md"
    changelog.parent.mkdir(parents=True)
    changelog.write_text(f"- ROM: {shown_hash}\n", encoding="utf-8")
    session = "fixture-session"
    write_json(root / "out/logs/emulator_session.json", {"rom_sha256": rom_hash})
    write_json(root / "out/logs/blastem_evidence.json", {"rom_sha256": rom_hash})
    write_json(root / "out/logs/runtime_metrics.json", {"rom_sha256": rom_hash, "capture_status": "partial" if partial else "ok"})
    write_json(root / "out/logs/performance_capture_report.json", {"rom_sha256": rom_hash})
    write_json(root / "out/logs/claim_reconciliation_report.json", {"rom_sha256": rom_hash, "resolved_claims": {"ready_for_aaa": False, "performance": "stable"}})
    write_json(root / "out/logs/old_report.json", {"rom_sha256": "a" * 64, "status": "ok"})
    return rom_hash


def run(root: Path, expected: int) -> dict:
    output = root / "out/logs/doc_sync_report.json"
    result = subprocess.run([sys.executable, str(AUDITOR), "--project-root", str(root), "--output", str(output)], capture_output=True, text=True, check=False)
    assert result.returncode == expected, result.stdout + result.stderr
    return json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="doc_sync_") as temp:
        base = Path(temp)
        coherent = base / "coherent"
        fixture(coherent)
        report = run(coherent, 0)
        assert report["status"] == "ok" and len(report["superseded_reports"]) == 1

        mismatch = base / "mismatch"
        fixture(mismatch, doc_hash="b" * 64)
        assert "doc_sync_rom_identity_mismatch:memory_generated" in run(mismatch, 1)["blockers"]

        contradiction = base / "contradiction"
        fixture(contradiction, ready=True)
        assert "doc_sync_strong_status_contradiction:ready_for_aaa" in run(contradiction, 1)["blockers"]

        partial = base / "partial"
        fixture(partial, partial=True)
        assert "doc_sync_strong_status_contradiction:performance_partial" in run(partial, 1)["blockers"]

    print("doc_sync_audit: 4 cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
