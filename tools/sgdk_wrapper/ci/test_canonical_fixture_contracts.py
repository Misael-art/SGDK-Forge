#!/usr/bin/env python3
"""Regression suite for the seven canonical neutral fixture contracts."""

from __future__ import annotations

import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path


WRAPPER_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = WRAPPER_ROOT / "canonical_fixture_gate.py"
spec = importlib.util.spec_from_file_location("canonical_fixture_gate", TOOL_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to import {TOOL_PATH}")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


HASH_A = "a" * 64
HASH_B = "b" * 64


class CanonicalFixtureContractTests(unittest.TestCase):
    def test_zero_sample_denominator_never_passes(self) -> None:
        required = gate.evaluate_sampled_gate({"sample_count": 0, "violation_count": 0})
        contextual = gate.evaluate_sampled_gate(
            {"sample_count": 0, "violation_count": 0, "required": False}
        )
        self.assertEqual(required["status"], "failed")
        self.assertEqual(contextual["status"], "warning")
        self.assertNotEqual(contextual["status"], "passed")

    def test_versioned_telemetry_skips_missing_optional_field(self) -> None:
        report = gate.evaluate_telemetry(
            {
                "required_fields": ["scene_id"],
                "optional_fields": ["playtest_step"],
                "block": {"schema_version": "1.0.0", "total_words": 4, "scene_id": 2},
            }
        )
        self.assertEqual(report["status"], "warning")
        self.assertEqual(report["code"], "telemetry_optional_fields_skipped")
        self.assertEqual(report["observations"]["missing_optional_fields"], ["playtest_step"])

    def test_versioned_telemetry_fails_closed_on_required_field(self) -> None:
        report = gate.evaluate_telemetry(
            {
                "required_fields": ["scene_id"],
                "block": {"schema_version": "1.0.0", "total_words": 3},
            }
        )
        self.assertEqual(report["status"], "failed")

    def test_rom_playtest_counts_observed_states_not_requested_states(self) -> None:
        failed = gate.evaluate_rom_playtest(
            {"requested_mask": 0b111, "observed_mask": 0b011, "required_mask": 0b111, "completed": True}
        )
        passed = gate.evaluate_rom_playtest(
            {"requested_mask": 0b111, "observed_mask": 0b111, "required_mask": 0b111, "completed": True}
        )
        self.assertEqual(failed["status"], "failed")
        self.assertEqual(passed["status"], "passed")

    def test_raster_screenshot_color_count_is_informational(self) -> None:
        report = gate.evaluate_raster_color(
            {
                "cram_entries_used": 58,
                "illegal_cram_entries": 0,
                "screenshot_unique_colors": 270,
                "mid_frame_palette_updates": 12,
            }
        )
        self.assertEqual(report["status"], "passed")
        self.assertTrue(report["observations"]["screenshot_color_count_informational"])

    def test_static_table_must_not_be_rebuilt_or_uploaded(self) -> None:
        passed = gate.evaluate_identical_work(
            {
                "camera_delta": 0,
                "table_hash_before": HASH_A,
                "table_hash_after": HASH_A,
                "rebuild_count": 0,
                "dma_bytes": 0,
            }
        )
        failed = gate.evaluate_identical_work(
            {
                "camera_delta": 0,
                "table_hash_before": HASH_A,
                "table_hash_after": HASH_A,
                "rebuild_count": 1,
                "dma_bytes": 896,
            }
        )
        self.assertEqual(passed["status"], "passed")
        self.assertEqual(failed["status"], "failed")

    def test_evidence_bundle_and_gate_must_share_rom_hash(self) -> None:
        common = {
            "manifest": {"status": "sealed", "rom_sha256": HASH_A},
            "gate_reports": [{"gate_id": "runtime", "status": "passed", "rom_sha256": HASH_A}],
        }
        self.assertEqual(gate.evaluate_evidence_binding(common)["status"], "passed")
        common["gate_reports"][0]["rom_sha256"] = HASH_B
        self.assertEqual(gate.evaluate_evidence_binding(common)["status"], "failed")

    def test_static_contract_cannot_claim_feature_readiness(self) -> None:
        overclaim = gate.evaluate_scope(
            {
                "declared_scope": "static_contract",
                "claimed_scope": "feature_readiness",
                "source_status": "passed",
            }
        )
        bounded = gate.evaluate_scope(
            {
                "declared_scope": "static_contract",
                "claimed_scope": "static_contract",
                "source_status": "passed",
            }
        )
        self.assertEqual(overclaim["status"], "failed")
        self.assertEqual(bounded["status"], "passed")

    def test_neutral_fixture_closes_all_seven_without_aaa_claim(self) -> None:
        fixture = {
            "fixture_id": "forge_reference_neutral_v1",
            "contracts": [
                {"type": "sampled_gate_non_vacuity", "sample_count": 8, "violation_count": 0},
                {
                    "type": "versioned_telemetry",
                    "required_fields": ["scene_id"],
                    "optional_fields": ["playtest_step"],
                    "block": {
                        "schema_version": "1.0.0",
                        "total_words": 5,
                        "scene_id": 1,
                        "playtest_step": 3,
                        "future_field": 99,
                    },
                },
                {
                    "type": "rom_side_playtest",
                    "requested_mask": 7,
                    "observed_mask": 7,
                    "required_mask": 7,
                    "completed": True,
                },
                {
                    "type": "raster_color_truth",
                    "cram_entries_used": 24,
                    "illegal_cram_entries": 0,
                    "screenshot_unique_colors": 96,
                    "mid_frame_palette_updates": 8,
                },
                {
                    "type": "identical_work_elision",
                    "camera_delta": 0,
                    "table_hash_before": HASH_A,
                    "table_hash_after": HASH_A,
                    "rebuild_count": 0,
                    "dma_bytes": 0,
                },
                {
                    "type": "evidence_binding",
                    "manifest": {"status": "sealed", "rom_sha256": HASH_A},
                    "gate_reports": [
                        {"gate_id": "runtime", "status": "passed", "rom_sha256": HASH_A}
                    ],
                },
                {
                    "type": "gate_scope",
                    "declared_scope": "static_contract",
                    "claimed_scope": "static_contract",
                    "source_status": "passed",
                },
            ],
        }
        report = gate.evaluate_fixture(fixture)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["results"]), 7)
        self.assertFalse(report["ready_for_aaa"])

    def test_fref_binary_parser_preserves_rom_observed_contracts(self) -> None:
        words = [0] * 20
        words[0:4] = [7, 7, 7, 1]
        words[4:10] = [32, 0, 32, 4, 0, 0]
        words[10:14] = [0x1234, 0x5678, 0x1234, 0x5678]
        words[14:18] = [16, 0, 0, 3]
        words[18:20] = [0, 240]
        raw = bytearray(0x1800)
        raw.extend(b"FREF")
        raw.extend(struct.pack(">HH", 1, len(words)))
        raw.extend(struct.pack(f">{len(words)}H", *words))
        with tempfile.TemporaryDirectory(prefix="forge_fref_") as temp_dir:
            sram = Path(temp_dir) / "save.sram"
            sram.write_bytes(raw)
            fixture = gate.fixture_from_fref(sram)
        report = gate.evaluate_fixture(fixture)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(len(report["results"]), 6)
        self.assertEqual(report["results"][2]["code"], "rom_observed_coverage_complete")


if __name__ == "__main__":
    unittest.main(verbosity=2)
