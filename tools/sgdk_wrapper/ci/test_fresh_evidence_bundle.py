#!/usr/bin/env python3
"""Regression tests for same-session BlastEm evidence sealing."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import struct
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image


WRAPPER_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = WRAPPER_ROOT / "seal_fresh_evidence_bundle.py"
spec = importlib.util.spec_from_file_location("seal_fresh_evidence_bundle", TOOL_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to import {TOOL_PATH}")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class FreshEvidenceBundleTests(unittest.TestCase):
    def make_fixture(self, root: Path, *, white: bool = False) -> dict[str, object]:
        rom = root / "rom.bin"
        screenshot = root / "screenshot.png"
        sram = root / "save.sram"
        rom.write_bytes(b"SEGA" + bytes(range(256)) * 8)
        image = Image.new("RGB", (320, 224), (255, 255, 255) if white else (0, 0, 24))
        if not white:
            for y in range(0, 224, 8):
                for x in range(0, 320, 8):
                    image.paste(((x * 3) % 256, (y * 5) % 256, ((x + y) * 2) % 256), (x, y, x + 8, y + 8))
        image.save(screenshot)
        metric_words = [1, 0, 300, 320, 224, 64, 32, 3, 0, 0, 0, 0, 0, 0, 0, 22, 180, 35, 0, 8, 6, 0, 0, 60]
        palette_words = list(range(64))
        payload = b"VLAB" + struct.pack(">HH", 1, 8 + (len(metric_words) + len(palette_words)) * 2)
        payload += struct.pack(f">{len(metric_words) + len(palette_words)}H", *(metric_words + palette_words))
        sram.write_bytes(payload + bytes(32768 - len(payload)))
        now = datetime.now(timezone.utc)
        return {
            "session_root": root,
            "session_id": "fresh-bundle-test",
            "rom_path": rom,
            "screenshot_path": screenshot,
            "sram_path": sram,
            "expected_rom_sha256": hashlib.sha256(rom.read_bytes()).hexdigest(),
            "started_at": (now - timedelta(seconds=2)).isoformat(),
            "completed_at": (now + timedelta(seconds=2)).isoformat(),
            "emulator_ref": "app/com.retrodev.blastem/x86_64/stable",
            "emulator_commit": "c1f3f4435e9d009fa001322e26e73e785fe443fcedfae1f3187836685c602221",
            "window_title": "Fixture - BlastEm - 60.0 fps",
        }

    def test_complete_same_session_bundle_is_sealed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sgdk_fresh_bundle_") as temp:
            fixture = self.make_fixture(Path(temp))
            result = tool.seal_bundle(**fixture)
            self.assertTrue(result["sealed"])
            self.assertEqual(result["freshness"]["artifact_count"], 5)
            self.assertEqual({item["session_id"] for item in result["manifest"]["artifacts"]}, {"fresh-bundle-test"})
            self.assertTrue(all(len(item["sha256"]) == 64 for item in result["manifest"]["artifacts"]))
            metrics = __import__("json").loads((Path(temp) / "runtime_metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics["vlab"]["over_budget_frames"], 35)
            self.assertEqual(metrics["vlab"]["max_cpu_load"], 0)
            self.assertEqual(metrics["vlab"]["target_fps"], 60)

    def test_different_rom_identity_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sgdk_fresh_bundle_") as temp:
            fixture = self.make_fixture(Path(temp))
            fixture["expected_rom_sha256"] = "0" * 64
            result = tool.seal_bundle(**fixture)
            self.assertFalse(result["sealed"])
            self.assertIn("rom_identity_mismatch", result["freshness"]["blockers"])

    def test_stale_artifact_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sgdk_fresh_bundle_") as temp:
            fixture = self.make_fixture(Path(temp))
            stale = datetime.now(timezone.utc).timestamp() - 86400
            os.utime(fixture["rom_path"], (stale, stale))
            result = tool.seal_bundle(**fixture)
            self.assertFalse(result["sealed"])
            self.assertIn("artifact_stale:rom", result["freshness"]["blockers"])

    def test_blank_screenshot_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sgdk_fresh_bundle_") as temp:
            fixture = self.make_fixture(Path(temp), white=True)
            result = tool.seal_bundle(**fixture)
            self.assertFalse(result["sealed"])
            self.assertIn("blank_or_low_information_capture", result["freshness"]["blockers"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
