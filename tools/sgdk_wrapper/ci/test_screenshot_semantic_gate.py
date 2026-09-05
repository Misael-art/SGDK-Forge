#!/usr/bin/env python3
"""Regression tests for the canonical screenshot semantic gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


WRAPPER_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WRAPPER_ROOT.parents[1]
TOOL_PATH = WRAPPER_ROOT / "screenshot_semantic_gate.py"

spec = importlib.util.spec_from_file_location("screenshot_semantic_gate", TOOL_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to import {TOOL_PATH}")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class ScreenshotSemanticGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="sgdk_semantic_fixture_")
        root = Path(self.temp.name)
        self.low_information = root / "low_information.png"
        self.rich_dark = root / "rich_dark.png"
        self.rich_gameplay = root / "rich_gameplay.png"

        Image.new("RGB", (320, 224), (250, 250, 250)).save(self.low_information)

        dark = Image.new("RGB", (320, 224), (8, 12, 24))
        draw = ImageDraw.Draw(dark)
        for y in range(0, 224, 8):
            for x in range(0, 320, 8):
                color = (28, 72, 112) if (x // 8 + y // 8) % 2 else (6, 20, 42)
                draw.rectangle((x, y, x + 7, y + 7), fill=color)
        dark.save(self.rich_dark)

        gameplay = Image.new("RGB", (320, 224), (22, 36, 58))
        draw = ImageDraw.Draw(gameplay)
        for y in range(0, 224, 8):
            for x in range(0, 320, 8):
                color = (18, 42, 74) if (x // 8 + y // 8) % 2 else (8, 20, 38)
                draw.rectangle((x, y, x + 7, y + 7), fill=color)
        for x in range(0, 320, 16):
            draw.rectangle((x, 144 + (x // 16) % 3 * 8, x + 15, 223), fill=(30, 94, 68))
        for x in range(24, 300, 40):
            draw.rectangle((x, 88, x + 15, 135), fill=(216, 176, 70))
        draw.rectangle((130, 96, 157, 143), fill=(76, 170, 224))
        gameplay.save(self.rich_gameplay)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_low_information_capture_is_rejected(self) -> None:
        report = gate.analyze_screenshot(self.low_information)
        expected_hash = hashlib.sha256(self.low_information.read_bytes()).hexdigest()
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["semantic_capture_valid"])
        self.assertEqual(report["blocker_code"], "blank_or_low_information_capture")
        self.assertEqual(report["screenshot_sha256"], expected_hash)
        self.assertEqual(report["claim_impacts"]["visual"], "unproven")
        self.assertEqual(report["claim_impacts"]["gameplay"], "unproven")
        self.assertEqual(report["claim_impacts"]["performance"], "unproven")
        self.assertLess(report["edge_density"], 0.04)
        self.assertGreater(report["dominant_ratio"], 0.90)
        self.assertGreater(report["width"], 0)
        self.assertGreater(report["height"], 0)

    def test_dark_and_gameplay_controls_are_accepted(self) -> None:
        for fixture in (self.rich_dark, self.rich_gameplay):
            with self.subTest(fixture=fixture):
                report = gate.analyze_screenshot(fixture)
                self.assertEqual(report["status"], "passed")
                self.assertTrue(report["semantic_capture_valid"])
                self.assertIsNone(report["blocker_code"])
                self.assertGreaterEqual(report["edge_density"], 0.04)
                self.assertRegex(report["screenshot_sha256"], r"^[0-9a-f]{64}$")

    def test_cli_writes_report_and_uses_blocking_exit_code(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sgdk_screenshot_gate_") as temp_dir:
            output_path = Path(temp_dir) / "semantic_capture_report.json"
            process = subprocess.run(
                [
                    sys.executable,
                    str(TOOL_PATH),
                    "--path",
                    str(self.low_information),
                    "--output",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(process.returncode, 1, process.stderr)
            report = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(report["decision"], "rejected_low_information")


if __name__ == "__main__":
    unittest.main(verbosity=2)
