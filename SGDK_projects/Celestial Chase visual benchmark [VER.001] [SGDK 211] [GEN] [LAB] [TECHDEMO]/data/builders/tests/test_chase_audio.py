from __future__ import annotations

import struct
import unittest

from data.builders.build_chase_audio import (
    SN76489_CLOCK,
    VGM_WAIT_SAMPLES,
    YM2612_CLOCK,
    audit_vgm_bytes,
    build_chase_vgm,
)


class ChaseAudioVgmTests(unittest.TestCase):
    def test_original_score_has_fm_psg_and_ntsc_loop(self) -> None:
        data = build_chase_vgm()
        audit = audit_vgm_bytes(data)

        self.assertEqual(b"Vgm ", data[:4])
        self.assertEqual(0x00000150, struct.unpack_from("<I", data, 0x08)[0])
        self.assertEqual(SN76489_CLOCK, audit["sn76489_clock_hz"])
        self.assertEqual(YM2612_CLOCK, audit["ym2612_clock_hz"])
        self.assertEqual(60, audit["rate_hz"])
        self.assertTrue(audit["uses_fm"])
        self.assertTrue(audit["uses_psg"])
        self.assertEqual(480, audit["wait_60hz_commands"])
        self.assertEqual(480 * VGM_WAIT_SAMPLES, audit["total_samples"])
        self.assertEqual(audit["total_samples"], audit["loop_samples"])

    def test_header_offsets_and_end_command_are_consistent(self) -> None:
        data = build_chase_vgm()
        eof_offset = struct.unpack_from("<I", data, 0x04)[0]
        data_offset = 0x34 + struct.unpack_from("<I", data, 0x34)[0]
        loop_offset = 0x1C + struct.unpack_from("<I", data, 0x1C)[0]

        self.assertEqual(len(data), eof_offset + 4)
        self.assertEqual(0x40, data_offset)
        self.assertGreaterEqual(loop_offset, data_offset)
        self.assertLess(loop_offset, len(data))
        self.assertEqual(0x66, data[-1])


if __name__ == "__main__":
    unittest.main()
