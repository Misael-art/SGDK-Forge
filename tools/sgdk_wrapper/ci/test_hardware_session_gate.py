#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "validate_hardware_session.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_case(project: Path, manifest: dict, expected: int) -> dict:
    manifest_path = project / "doc/hardware_session_manifest.json"
    output = project / "out/logs/hardware_test_gate_report.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--project-root", str(project), "--manifest", "doc/hardware_session_manifest.json", "--rom", "out/rom.bin", "--output", "out/logs/hardware_test_gate_report.json"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == expected, result.stdout + result.stderr
    return json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hardware_gate_") as temp:
        project = Path(temp)
        rom = project / "out/rom.bin"
        rom.parent.mkdir(parents=True)
        rom.write_bytes(b"ROM-FIXTURE")
        rom_sha = sha(rom)
        evidence = project / "out/evidence/blastem/evidence_manifest.json"
        evidence.parent.mkdir(parents=True)
        evidence.write_text(json.dumps({"rom_sha256": rom_sha}), encoding="utf-8")
        capture = project / "out/evidence/hardware/session/video.bin"
        capture.parent.mkdir(parents=True)
        capture.write_bytes(b"VIDEO-FIXTURE")

        valid = {
            "schema_version": "1.0.0",
            "session_id": "hardware-fixture",
            "status": "accepted",
            "device": {"kind": "fpga", "manufacturer": "fixture", "model": "fixture", "revision": "1", "video_standard": "NTSC_60HZ"},
            "region": "U",
            "load_method": {"kind": "fpga_sd", "device": "fixture", "firmware": "1.0"},
            "rom": {"path": "out/rom.bin", "sha256": rom_sha, "size_bytes": rom.stat().st_size},
            "captures": [{"kind": "video", "path": "out/evidence/hardware/session/video.bin", "sha256": sha(capture), "proves": ["boot", "input", "audio", "gameplay"]}],
            "observations": {"boot": "pass", "input": "pass", "audio": "pass", "gameplay": "pass", "timing_decision": "pass", "audio_decision": "pass", "issues": []},
            "tester_attestation": {"performed_by": "fixture", "performed_at": "2026-07-20T00:00:00Z", "truthful": True},
        }
        assert run_case(project, valid, 0)["status"] == "ok"

        pending = json.loads(json.dumps(valid))
        pending["status"] = "pending_external_test"
        pending["captures"] = []
        pending["tester_attestation"] = {"performed_by": None, "performed_at": None, "truthful": False}
        pending_report = run_case(project, pending, 1)
        assert "hardware_test_pending_external_execution" in pending_report["blockers"]
        assert "hardware_capture_missing" in pending_report["blockers"]

        mismatch = json.loads(json.dumps(valid))
        mismatch["rom"]["sha256"] = "0" * 64
        mismatch_report = run_case(project, mismatch, 1)
        assert "hardware_rom_hash_mismatch_current_rom" in mismatch_report["blockers"]
        assert "hardware_rom_hash_mismatch_blastem_bundle" in mismatch_report["blockers"]

    print("hardware_session_gate: 3 cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
