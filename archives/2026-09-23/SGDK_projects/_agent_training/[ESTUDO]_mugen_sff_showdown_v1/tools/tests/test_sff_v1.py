import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from mugen_sff.sff_v1 import iter_sff_v1_entries, read_sff_v1_header


class TestSffV1(unittest.TestCase):
    def test_showdown_header(self) -> None:
        sff = ROOT / "rascunho" / "inputs" / "showdown.sff"
        header = read_sff_v1_header(sff)
        self.assertEqual(header.version, (1, 0, 1, 0))
        self.assertEqual(header.groups, 4)
        self.assertEqual(header.images, 6)
        self.assertEqual(header.first_offset, 512)
        self.assertEqual(header.subheader_size, 32)

    def test_showdown_entries_count(self) -> None:
        sff = ROOT / "rascunho" / "inputs" / "showdown.sff"
        entries = list(iter_sff_v1_entries(sff))
        self.assertEqual(len(entries), 6)


if __name__ == "__main__":
    unittest.main()
