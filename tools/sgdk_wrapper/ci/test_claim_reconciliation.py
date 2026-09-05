#!/usr/bin/env python3
"""Regression tests for lowest-proven-status claim reconciliation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


WRAPPER_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = WRAPPER_ROOT / "reconcile_claims.py"
spec = importlib.util.spec_from_file_location("reconcile_claims", TOOL_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to import {TOOL_PATH}")
claims = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claims)


class ClaimReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="sgdk_claim_reconciliation_")
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, payload: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_blocked_gate_overrides_positive_ready_claims(self) -> None:
        rom_hash = "a" * 64
        self.write("out/logs/visual_delivery_gate_report.json", {
            "ready_for_aaa": True,
            "technical_ready": True,
            "creative_ready": True,
            "blocking_status": "none",
            "rom_sha256": rom_hash,
            "session_id": "session-1",
        })
        self.write("doc/contracts/runtime_admission_report.json", {
            "status": "blocked_pending_vdp_conversion",
            "runtime_admitted": False,
            "blocking_statuses": ["blocked_no_vdp_conversion"],
            "forbidden_claims": ["ready_for_aaa"],
        })
        report = claims.reconcile(self.root, include_validation_report=False)
        self.assertFalse(report["resolved_claims"]["ready_for_aaa"])
        self.assertIn("report_status_conflict", report["blocking_statuses"])

    def test_partial_capture_and_zero_perceptual_metrics_lower_claims(self) -> None:
        self.write("out/logs/visual_delivery_gate_report.json", {
            "ready_for_aaa": True,
            "technical_ready": True,
            "creative_ready": True,
            "blocking_status": "none",
            "rom_sha256": "a" * 64,
            "session_id": "session-1",
        })
        self.write("out/logs/runtime_metrics.json", {
            "capture_status": "partial",
            "performance": "estavel",
            "perceptual_check": {"fluidez": 0, "leitura": 0, "naturalidade": 0, "impacto": 0},
            "rom_sha256": "a" * 64,
            "session_id": "session-1",
        })
        report = claims.reconcile(self.root, include_validation_report=False)
        self.assertEqual(report["resolved_claims"]["performance"], "unproven")
        self.assertFalse(report["resolved_claims"]["creative_ready"])
        self.assertIn("runtime_capture_partial", report["blocking_statuses"])
        self.assertIn("perceptual_metrics_zero", report["blocking_statuses"])
        self.assertIn("report_status_conflict", report["blocking_statuses"])

    def test_identity_mismatch_is_explicit_conflict(self) -> None:
        self.write("out/logs/visual_delivery_gate_report.json", {
            "ready_for_aaa": True,
            "technical_ready": True,
            "creative_ready": True,
            "rom_sha256": "a" * 64,
            "session_id": "session-1",
        })
        self.write("out/logs/emulator_session.json", {
            "performance": "estavel",
            "rom_sha256": "b" * 64,
            "session_id": "session-2",
        })
        report = claims.reconcile(self.root, include_validation_report=False)
        self.assertIn("report_rom_identity_mismatch", report["blocking_statuses"])
        self.assertIn("report_evidence_session_mismatch", report["blocking_statuses"])
        self.assertIn("report_status_conflict", report["blocking_statuses"])
        self.assertFalse(report["identity_reconciliation"]["same_rom"])
        self.assertFalse(report["identity_reconciliation"]["same_evidence_session"])

    def test_consistent_full_evidence_can_preserve_positive_claims(self) -> None:
        common = {"rom_sha256": "c" * 64, "session_id": "session-clean"}
        self.write("out/logs/visual_delivery_gate_report.json", {
            **common,
            "ready_for_aaa": True,
            "technical_ready": True,
            "creative_ready": True,
            "blocking_status": "none",
        })
        self.write("out/logs/runtime_metrics.json", {
            **common,
            "capture_status": "complete",
            "performance": "estavel",
            "perceptual_check": {"fluidez": 4, "leitura": 4, "naturalidade": 3, "impacto": 4},
        })
        self.write("out/logs/emulator_session.json", {**common, "performance": "estavel"})
        report = claims.reconcile(self.root, include_validation_report=False)
        self.assertEqual(report["blocking_statuses"], [])
        self.assertTrue(report["resolved_claims"]["ready_for_aaa"])
        self.assertEqual(report["resolved_claims"]["performance"], "stable")
        self.assertTrue(report["identity_reconciliation"]["same_rom"])
        self.assertTrue(report["identity_reconciliation"]["same_evidence_session"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
