import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'audio-tools'))
import psg_score
import vgm_to_xgm2


class ScoreTests(unittest.TestCase):
    def test_invalid_scores(self):
        psg_score.self_check()

    def test_official_converter_ntsc_pal(self):
        for region in ('ntsc', 'pal'):
            with self.subTest(region=region), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                score = {'schema_version': '1.0.0', 'region': region,
                         'frames': 120, 'loop_frame': 30, 'notes': [
                             {'channel': 0, 'frame': 30, 'duration': 30, 'midi': 69},
                             {'channel': 0, 'frame': 60, 'duration': 30, 'midi': 72},
                             {'channel': 1, 'frame': 30, 'duration': 90, 'midi': 57}]}
                vgm = root / 'authored.vgm'
                data = psg_score.compile_score(score)
                vgm.write_bytes(data)
                # Independently decode the emitted command stream.
                cursor, samples = 0x40, 0
                loop_offset = int.from_bytes(data[0x1c:0x20], 'little') + 0x1c
                loop_samples = None
                while data[cursor] != 0x66:
                    if cursor == loop_offset:
                        loop_samples = samples
                    command = data[cursor]
                    if command == 0x50:
                        cursor += 2
                    elif command in (0x62, 0x63):
                        samples += 735 if command == 0x62 else 882
                        cursor += 1
                    else:
                        self.fail(f'Unknown command {command:x}')
                self.assertEqual(samples, int.from_bytes(data[0x18:0x1c], 'little'))
                self.assertEqual(samples - loop_samples, int.from_bytes(data[0x20:0x24], 'little'))
                report = vgm_to_xgm2.convert(vgm, root / 'authored.xgm', False, 'auto', True)
                self.assertEqual(report['xgm2']['magic'], 'XGM2')
                self.assertEqual(report['xgm2']['format']['ntsc_vs_pal'], region.upper())
                self.assertGreater(report['xgm2']['psg_block_bytes'], 0)


if __name__ == '__main__':
    unittest.main()
