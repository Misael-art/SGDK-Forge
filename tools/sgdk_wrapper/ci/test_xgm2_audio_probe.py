#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "extract_xgm2_audio_probe.py"
SPEC = importlib.util.spec_from_file_location("extract_xgm2_audio_probe", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def fixture(values: tuple[int, ...], magic: bytes = b"AUD2") -> bytes:
    data = bytearray(0x1000)
    offset = MODULE.AUD2_OFFSET
    data[offset:offset + 4] = magic
    struct.pack_into(">HH", data, offset + 4, 1, MODULE.AUD2_TOTAL_BYTES)
    struct.pack_into(">" + ("H" * MODULE.AUD2_WORDS), data, offset + 8, *values)
    return bytes(data)


class Xgm2AudioProbeTests(unittest.TestCase):
    def test_good_simultaneous_session_passes(self) -> None:
        values = (4, 2, 1, 4, 300, 42, 3, 0, 8, 5, 5, 1200, 60)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "save.sram"
            path.write_bytes(fixture(values))
            report = MODULE.build_report(path, "fixture-good")
        self.assertEqual("passed", report["status"])
        self.assertTrue(report["checks"]["simultaneous_music_sfx_observed"])

    def test_missing_simultaneous_playback_blocks(self) -> None:
        values = (4, 2, 1, 0, 300, 42, 3, 0, 0, 0, 0, 1200, 60)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "save.sram"
            path.write_bytes(fixture(values))
            report = MODULE.build_report(path)
        self.assertEqual("blocked", report["status"])
        self.assertIn("simultaneous_music_sfx_observed", report["blockers"])

    def test_session_that_stops_after_simultaneous_playback_retains_proof(self) -> None:
        values = (4, 5, 0, 0, 450, 92, 0, 1, 8, 5, 5, 2083, 60)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "save.sram"
            path.write_bytes(fixture(values))
            report = MODULE.build_report(path, "fixture-ended")
        self.assertEqual("passed", report["status"])
        self.assertTrue(report["checks"]["music_runtime_observed"])
        self.assertIn("xgm2_missed_frames_observed", report["warnings"])

    def test_missing_signature_is_rejected(self) -> None:
        values = (0,) * MODULE.AUD2_WORDS
        with self.assertRaisesRegex(ValueError, "AUD2 signature missing"):
            MODULE.parse_aud2(fixture(values, magic=b"NOPE"))


if __name__ == "__main__":
    unittest.main()
