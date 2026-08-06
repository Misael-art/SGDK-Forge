#!/usr/bin/env python3
"""Ten regression tests for the seven neutral fixture contracts."""
from __future__ import annotations
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "canonical_fixture_gate.py"
spec = importlib.util.spec_from_file_location("fixture_gate", TOOL)
gate = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(gate)
HASH_A, HASH_B = "a" * 64, "b" * 64

class FixtureContractTests(unittest.TestCase):
    def test_01_zero_sample_never_passes(self):
        self.assertEqual(gate.evaluate_sampled_gate({"sample_count": 0, "violation_count": 0})["status"], "failed")
    def test_02_optional_missing_warns(self):
        self.assertEqual(gate.evaluate_telemetry({"required_fields": ["scene"], "optional_fields": ["future"], "block": {"scene": 1}})["status"], "warning")
    def test_03_required_missing_fails(self):
        self.assertEqual(gate.evaluate_telemetry({"required_fields": ["scene"], "block": {}})["status"], "failed")
    def test_04_playtest_uses_observed_mask(self):
        self.assertEqual(gate.evaluate_rom_playtest({"requested_mask": 7, "observed_mask": 3, "required_mask": 7, "completed": True})["status"], "failed")
    def test_05_playtest_complete_passes(self):
        self.assertEqual(gate.evaluate_rom_playtest({"requested_mask": 7, "observed_mask": 7, "required_mask": 7, "completed": True})["status"], "passed")
    def test_06_raster_color_count_is_informational(self):
        self.assertTrue(gate.evaluate_raster_color({"cram_entries_used": 58, "illegal_cram_entries": 0, "mid_frame_palette_updates": 4})["observations"]["screenshot_color_count_informational"])
    def test_07_static_table_must_be_elided(self):
        self.assertEqual(gate.evaluate_identical_work({"camera_delta": 0, "table_hash_before": HASH_A, "table_hash_after": HASH_A, "rebuild_count": 1, "dma_bytes": 0})["status"], "failed")
    def test_08_evidence_hashes_must_match(self):
        report = gate.evaluate_evidence_binding({"manifest": {"status": "sealed", "rom_sha256": HASH_A}, "gate_reports": [{"status": "passed", "rom_sha256": HASH_B}]})
        self.assertEqual(report["status"], "failed")
    def test_09_static_contract_cannot_overclaim(self):
        self.assertEqual(gate.evaluate_scope({"declared_scope": "static_contract", "claimed_scope": "feature_readiness", "source_status": "passed"})["status"], "failed")
    def test_10_fref_parser_preserves_runtime_observation(self):
        words = [7, 7, 7, 1, 32, 0, 0, 0, 0, 0, 0x1234, 0x5678, 0x1234, 0x5678, 16, 0, 0, 0, 0, 240]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "save.sram"; path.write_bytes(b"\0" * 64 + b"FREF" + struct.pack(">HH", 1, len(words)) + struct.pack(">20H", *words))
            self.assertEqual(gate.evaluate_fixture(gate.fixture_from_fref(path))["status"], "passed")

if __name__ == "__main__": unittest.main(verbosity=1)
